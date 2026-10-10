"""Synthetic pressure controls for the pure Q08 network-state evaluator.

Tests intentionally contain a weak route-only baseline that accepts an
administratively UP extra link, while the subject checker must reject it.
No model, Docker container, network or G89 operation is used here.
"""
import copy
import unittest

from network_state_validator import NetworkShapeError, validate

V4_HEADER = (
    "Iface\tDestination\tGateway \tFlags\tRefCnt\tUse\tMetric\tMask\tMTU\tWindow\tIRTT\n"
)
V6_LOOPBACK_ROW = (
    "0" * 32 + " 00 " + "0" * 32 + " 00 " + "0" * 32 +
    " 00000000 00000002 00000000 80200001 lo\n"
)
V6_LOOPBACK_ADDRESS = ("0" * 31 + "1 01 80 10 80 lo\n")


def fixture():
    return {
        "interfaces": [[1, "lo"], [2, "tunl0"], [3, "gre0"]],
        "link_state": [
            {"name": "lo", "index": 1, "flags": 0x49, "operstate": "unknown"},
            {"name": "tunl0", "index": 2, "flags": 0x80, "operstate": "down"},
            {"name": "gre0", "index": 3, "flags": 0x80, "operstate": "down"},
        ],
        "route_v4": V4_HEADER,
        "route_v6": V6_LOOPBACK_ROW,
        "ipv6_ifaddr": V6_LOOPBACK_ADDRESS,
    }


class NetworkValidatorTests(unittest.TestCase):
    def case(self):
        return copy.deepcopy(fixture())

    def reject(self, data, reason):
        with self.assertRaises(NetworkShapeError) as failure:
            validate(data)
        self.assertEqual(failure.exception.reason, reason)

    def test_01_inert_tunnel_names_are_not_automatically_failure(self):
        result = validate(self.case())
        self.assertEqual(result["status"], "LINKS_INERT_AND_ROUTES_LOOPBACK_ONLY_BOUNDED")
        self.assertEqual(result["admin_down_nonloopback_interfaces"], ["gre0", "tunl0"])

    def test_02_nonloopback_admin_up_detected(self):
        data = self.case()
        data["link_state"][1]["flags"] |= 0x1
        self.reject(data, "NONLOOPBACK_ADMIN_UP")

    def test_03_nonloopback_running_detected(self):
        data = self.case()
        data["link_state"][1]["flags"] |= 0x40
        self.reject(data, "NONLOOPBACK_RUNNING")

    def test_04_nonloopback_carrier_detected(self):
        data = self.case()
        data["link_state"][1]["flags"] |= 0x10000
        self.reject(data, "NONLOOPBACK_LOWER_UP")

    def test_05_nonloopback_operstate_up_detected(self):
        data = self.case()
        data["link_state"][1]["operstate"] = "up"
        self.reject(data, "NONLOOPBACK_OPERSTATE_UNKNOWN_OR_ACTIVE")

    def test_06_unknown_nonloopback_operstate_fails_safe(self):
        data = self.case()
        data["link_state"][1]["operstate"] = "unknown"
        self.reject(data, "NONLOOPBACK_OPERSTATE_UNKNOWN_OR_ACTIVE")

    def test_07_ipv4_external_route_detected(self):
        data = self.case()
        data["route_v4"] += "tunl0\t00000000\t00000000\t0003\t0\t0\t0\t00000000\t0\t0\t0\n"
        self.reject(data, "IPV4_NONLOOPBACK_ROUTE")

    def test_08_ipv6_external_route_detected(self):
        data = self.case()
        data["route_v6"] = V6_LOOPBACK_ROW.replace(" lo\n", " tunl0\n")
        self.reject(data, "IPV6_NONLOOPBACK_ROUTE")

    def test_09_ipv6_nonloopback_address_detected(self):
        data = self.case()
        data["ipv6_ifaddr"] += "0" * 31 + "2 02 40 20 80 gre0\n"
        self.reject(data, "IPV6_NONLOOPBACK_ADDRESS")

    def test_10_missing_link_state_detected(self):
        data = self.case()
        data["link_state"].pop()
        self.reject(data, "LINK_INVENTORY_INCOMPLETE")

    def test_11_wrong_interface_identity_detected(self):
        data = self.case()
        data["link_state"][1]["index"] = 99
        self.reject(data, "LINK_IFINDEX_MISMATCH")

    def test_12_loopback_not_up_detected(self):
        data = self.case()
        data["link_state"][0]["flags"] &= ~0x1
        self.reject(data, "LOOPBACK_NOT_ACTIVE")

    def test_13_nonloopback_loopback_flag_detected(self):
        data = self.case()
        data["link_state"][1]["flags"] |= 0x8
        self.reject(data, "UNEXPECTED_LOOPBACK_INTERFACE")

    def test_14_unexpected_ipv6_loopback_address_detected(self):
        data = self.case()
        data["ipv6_ifaddr"] = "0" * 31 + "2 01 80 10 80 lo\n"
        self.reject(data, "IPV6_UNEXPECTED_LOOPBACK_ADDRESS")

    def test_15_malformed_ipv4_route_detected(self):
        data = self.case()
        data["route_v4"] = "not-a-proc-route-table\n"
        self.reject(data, "IPV4_ROUTE_HEADER_INVALID")

    def test_16_duplicate_link_record_detected(self):
        data = self.case()
        data["link_state"][2] = copy.deepcopy(data["link_state"][1])
        self.reject(data, "DUPLICATE_LINK_RECORD")

    def test_17_weak_route_only_baseline_fails_to_detect_active_link(self):
        data = self.case()
        data["link_state"][1]["flags"] |= 0x1
        weak_route_only_accepts = not data["route_v4"].strip().splitlines()[1:]
        self.assertTrue(weak_route_only_accepts)
        self.reject(data, "NONLOOPBACK_ADMIN_UP")


if __name__ == "__main__":
    unittest.main()
