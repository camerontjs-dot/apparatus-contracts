"""Frozen controller-only probes, sent as Python -c bytes; never a model tool.

No DNS; network destinations are fixed public-synthetic controls in this file.
127.0.0.1 is the *worker's* namespace, never a host gateway address.
"""
import errno
import json
import os
from pathlib import Path
import socket
import sys
import time


def attempt(destination):
    # Blocking connect_ex, bounded by the external process timeout. In network
    # none the kernel must immediately report ENETUNREACH/ECONNREFUSED.
    # Do not convert a Python timeout into a purported kernel denial.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        start = time.time_ns()
        print(json.dumps({"connection_begin": {"destination": destination, "started_ns": start, "syscall": "connect_ex"}}), flush=True)
        code = client.connect_ex(tuple(destination))
        return {"attempted": True, "syscall": "connect_ex", "family": "AF_INET",
                "destination": destination, "started_ns": start, "ended_ns": time.time_ns(),
                "errno": code, "errname": errno.errorcode.get(code, "SUCCESS" if code == 0 else "UNKNOWN")}


def network():
    interfaces = socket.if_nameindex()
    # Linux sysfs ABI: flags is an IFF_* hexadecimal mask; operstate is
    # operational state. Names alone do not establish usable networking.
    link_state = []
    for ifindex, name in interfaces:
        root = Path('/sys/class/net') / name
        link_state.append({
            "name": name,
            "index": int((root / 'ifindex').read_text().strip()),
            "flags": int((root / 'flags').read_text().strip(), 0),
            "operstate": (root / 'operstate').read_text().strip(),
        })
    result = {"schema": "cal-network-observation/2", "pid": os.getpid(),
              "namespace": os.readlink('/proc/self/ns/net'),
              "interfaces": interfaces,
              "link_state": link_state,
              "route_v4": Path('/proc/net/route').read_text(),
              "route_v6": Path('/proc/net/ipv6_route').read_text(),
              "ipv6_ifaddr": Path('/proc/net/if_inet6').read_text()}
    # Same interpreter, same socket primitive, same worker, actual accept + data.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(('127.0.0.1', 0))
        listener.listen(1)
        listener.settimeout(2)
        destination = list(listener.getsockname())
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            start = time.time_ns()
            code = client.connect_ex(tuple(destination))
            result['positive'] = {"attempted": True, "syscall": "connect_ex", "family": "AF_INET",
                                  "destination": destination, "errno": code,
                                  "errname": errno.errorcode.get(code, 'SUCCESS' if code == 0 else 'UNKNOWN'),
                                  "started_ns": start, "ended_ns": time.time_ns()}
            if code != 0:
                raise RuntimeError('POSITIVE_SOCKET_INSTRUMENTATION_FAILED')
            client.settimeout(2)
            with listener.accept()[0] as peer:
                peer.sendall(b'CAL-PUBLIC-SYNTHETIC-SOCKET-CONTROL\n')
                peer.shutdown(socket.SHUT_WR)
                result['positive']['received'] = client.makefile('rb').read().decode('ascii')
    print(json.dumps({"positive_checkpoint": result}), flush=True)
    result['synthetic_egress'] = attempt(['192.0.2.1', 9])
    print(json.dumps({"egress_checkpoint": result['synthetic_egress']}), flush=True)
    if result['synthetic_egress']['errno'] != errno.ENETUNREACH:
        print(json.dumps(result), flush=True)
        return  # first discriminating failure: no later connection attempt
    result['controller_loopback_boundary'] = attempt(['127.0.0.1', 11434])
    print(json.dumps(result), flush=True)


def main():
    operation, *args = sys.argv[1:]
    if operation == 'network':
        network()
    elif operation == 'id':
        print(os.getuid())
    elif operation == 'cat':
        for path in args:
            sys.stdout.buffer.write(Path(path).read_bytes())
    elif operation == 'ls':
        for name in sorted(os.listdir(args[-1])):
            print(name)
    elif operation == 'test':
        sys.exit(0 if os.path.lexists(args[-1]) else 1)
    elif operation == 'touch':
        try:
            # O_WRONLY deliberately tests the read-only boundary even when the
            # existing file already has today's timestamp.
            fd = os.open(args[0], os.O_WRONLY | os.O_CREAT, 0o600)
            os.close(fd)
        except OSError as error:
            print(json.dumps({'errno': error.errno, 'errname': errno.errorcode.get(error.errno)}), file=sys.stderr)
            sys.exit(1)
    else:
        raise ValueError('UNKNOWN_FROZEN_CONTROL')


if __name__ == '__main__':
    main()
