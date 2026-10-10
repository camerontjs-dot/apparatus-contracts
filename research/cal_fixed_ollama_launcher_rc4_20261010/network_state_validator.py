"""Pure Q08 network-state validator, independent of worker/runner imports.

Linux UAPI: /sys/class/net/<iface>/flags (IFF_UP=0x1, IFF_LOOPBACK=0x8,
IFF_RUNNING=0x40, IFF_LOWER_UP=0x10000), operstate in sysfs ABI.
This is a necessary condition for the bounded worker namespace, not an
arbitrary-traffic security proof. The runner separately verifies actual
same-worker positive socket, ENETUNREACH and ECONNREFUSED observations.
"""
from __future__ import annotations

import re

IFF_UP = 0x1
IFF_LOOPBACK = 0x8
IFF_RUNNING = 0x40
IFF_LOWER_UP = 0x10000
INACTIVE_STATES = frozenset({"down", "notpresent", "lowerlayerdown"})
IFACE_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,15}$")


class NetworkShapeError(ValueError):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


def require(cond: bool, reason: str) -> None:
    if not cond:
        raise NetworkShapeError(reason)


def validate(observation: dict) -> dict:
    require(type(observation) is dict, "OBSERVATION_NOT_OBJECT")
    interfaces = observation.get("interfaces")
    links = observation.get("link_state")
    require(type(interfaces) is list and len(interfaces) >= 1, "INTERFACE_INVENTORY_MISSING")
    require(type(links) is list and len(links) == len(interfaces), "LINK_INVENTORY_INCOMPLETE")
    require(all(type(row) is list and len(row) == 2 and
                type(row[0]) is int and row[0] > 0 and
                type(row[1]) is str and IFACE_RE.fullmatch(row[1])
                for row in interfaces), "INTERFACE_SHAPE_INVALID")
    observed = {item[1]: item[0] for item in interfaces}
    require(len(observed) == len(interfaces), "DUPLICATE_INTERFACE_NAMES")
    require("lo" in observed, "LOOPBACK_MISSING")

    checked = {}
    for row in links:
        require(type(row) is dict and set(row) == {"name", "index", "flags", "operstate"},
                "LINK_RECORD_SHAPE_INVALID")
        name, index, flags, state = (row[k] for k in ("name", "index", "flags", "operstate"))
        require(type(name) is str and name in observed, "LINK_UNLISTED_NAME")
        require(type(index) is int and index == observed[name], "LINK_IFINDEX_MISMATCH")
        require(type(flags) is int and flags >= 0, "LINK_FLAGS_INVALID")
        require(type(state) is str and bool(state), "OPERSTATE_MISSING")
        require(name not in checked, "DUPLICATE_LINK_RECORD")
        checked[name] = (flags, state)
    require(set(checked) == set(observed), "LINK_STATE_MISSING")

    lo_flags, lo_state = checked["lo"]
    require(lo_flags & IFF_UP and lo_flags & IFF_LOOPBACK, "LOOPBACK_NOT_ACTIVE")
    # Linux loopback often uses the documented UNKNOWN operational state.
    require(lo_state in {"unknown", "up"}, "LOOPBACK_STATE_INVALID")
    inactive = []
    for name, (flags, state) in checked.items():
        if name == "lo":
            continue
        require(not (flags & IFF_LOOPBACK), "UNEXPECTED_LOOPBACK_INTERFACE")
        require(not (flags & IFF_UP), "NONLOOPBACK_ADMIN_UP")
        require(not (flags & IFF_RUNNING), "NONLOOPBACK_RUNNING")
        require(not (flags & IFF_LOWER_UP), "NONLOOPBACK_LOWER_UP")
        require(state in INACTIVE_STATES, "NONLOOPBACK_OPERSTATE_UNKNOWN_OR_ACTIVE")
        inactive.append(name)

    # The proc IPv4 route table starts with a fixed header. A loopback-only
    # route is not an external interface, but any other interface is a stop.
    route_v4 = observation.get("route_v4")
    require(type(route_v4) is str and bool(route_v4.strip()), "IPV4_ROUTE_MISSING")
    rows_v4 = route_v4.strip().splitlines()
    header = rows_v4[0].split()
    require(len(header) >= 8 and header[0] == "Iface" and header[1] == "Destination",
            "IPV4_ROUTE_HEADER_INVALID")
    for line in rows_v4[1:]:
        fields = line.split()
        require(len(fields) >= 8, "IPV4_ROUTE_ROW_MALFORMED")
        require(fields[0] == "lo", "IPV4_NONLOOPBACK_ROUTE")

    route_v6 = observation.get("route_v6")
    require(type(route_v6) is str, "IPV6_ROUTE_MISSING")
    rows_v6 = [line.split() for line in route_v6.splitlines() if line.strip()]
    for fields in rows_v6:
        require(len(fields) >= 10, "IPV6_ROUTE_ROW_MALFORMED")
        require(fields[-1] == "lo", "IPV6_NONLOOPBACK_ROUTE")

    if_inet6 = observation.get("ipv6_ifaddr")
    require(type(if_inet6) is str, "IPV6_ADDRESS_OBSERVATION_MISSING")
    ipv6_rows = [line.split() for line in if_inet6.splitlines() if line.strip()]
    for fields in ipv6_rows:
        require(len(fields) == 6, "IPV6_ADDRESS_ROW_MALFORMED")
        require(fields[-1] == "lo", "IPV6_NONLOOPBACK_ADDRESS")
        require(fields[0] == "0" * 31 + "1", "IPV6_UNEXPECTED_LOOPBACK_ADDRESS")

    return {
        "status": "LINKS_INERT_AND_ROUTES_LOOPBACK_ONLY_BOUNDED",
        "loopback_ifindex": observed["lo"],
        "enumerated_interfaces": sorted(checked),
        "admin_down_nonloopback_interfaces": sorted(inactive),
        "ipv4_route_rows": len(rows_v4) - 1,
        "ipv6_route_rows": len(rows_v6),
        "ipv6_address_rows": len(ipv6_rows),
        "scope_limits": [
            "live snapshots can change after observation",
            "runner's actual connection probes are separate required evidence",
            "kernel/userspace host and provider remain trusted",
            "no arbitrary network traffic or all-protocol isolation proof",
        ],
    }
