#!/usr/bin/env python3
"""Fake VESC, for testing the harness without hardware.

Listens on TCP and speaks the VESC packet protocol, so the harness attaches to
it exactly as it would to a VESC Tool window's server (which relays the same
bytes). Answers just enough to exercise every path the driver has:

    COMM_FW_VERSION (0)      -> firmware 7.0, hw "FAKE_ESC"  (makes isPortConnected true)
    COMM_LISP_REPL_CMD (138) -> COMM_LISP_PRINT echo of the expression
    COMM_LISP_GET_STATS (134)-> cpu/heap/mem/stack, no globals
    COMM_LISP_SET_RUNNING (133) -> ok
    COMM_LISP_ERASE/WRITE/READ_CODE (132/131/130) -> ok (no real flash)

Usage:
    python3 fake_vesc.py [port] [--nodes 1,2,3]   # port default 65199

It also plays the CAN bus: COMM_FORWARD_CAN (34) is dispatched to the addressed
node and the node's reply is sent back unwrapped, exactly as a real ESC relays
it. COMM_PING_CAN (62) returns --nodes, so `:can scan` works. Replies carry the
node id (`> node2:4f32`, cpu_use = 3 + node) so attribution can be asserted.

Run the harness against it:
    ./run.sh ask '(+ 1 2)' 127.0.0.1 65199

This is a test double, not an emulator: REPL replies are canned, stats are
constants, and nothing stateful is modelled. Extend a handler when a test
needs it; do not add realism you will not assert on.
"""

import socket
import struct
import sys
import threading

CMD_FW_VERSION = 0
CMD_FORWARD_CAN = 34
CMD_PING_CAN = 62
CMD_LISP_READ_CODE = 130
CMD_LISP_WRITE_CODE = 131
CMD_LISP_ERASE_CODE = 132
CMD_LISP_SET_RUNNING = 133
CMD_LISP_GET_STATS = 134
CMD_LISP_PRINT = 135
CMD_LISP_REPL_CMD = 138


def crc16(buf: bytes) -> int:
    crc = 0
    for b in buf:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if (crc & 0x8000) else (crc << 1)
            crc &= 0xFFFF
    return crc


def frame(payload: bytes) -> bytes:
    out = bytearray()
    n = len(payload)
    if n <= 255:
        out += bytes((2, n))
    else:
        out += bytes((3, (n >> 8) & 0xFF, n & 0xFF))
    out += payload
    c = crc16(payload)
    out += bytes((c >> 8, c & 0xFF, 3))
    return bytes(out)


class PacketDecoder:
    """Feeds bytes, yields payload frames. Mirrors Packet::processData."""

    def __init__(self):
        self.buf = bytearray()

    def feed(self, data: bytes):
        self.buf += data
        out = []
        while True:
            if not self.buf:
                break
            start = self.buf[0]
            if start == 2:
                if len(self.buf) < 4:
                    break
                n = self.buf[1]
                total = 2 + n + 3
            elif start == 3:
                if len(self.buf) < 5:
                    break
                n = (self.buf[1] << 8) | self.buf[2]
                total = 3 + n + 3
            else:
                # Garbage: resync at the next plausible start byte.
                self.buf = self.buf[1:]
                continue
            if len(self.buf) < total:
                break
            payload = bytes(self.buf[(total - n - 3) : (total - 3)])
            crc = (self.buf[total - 3] << 8) | self.buf[total - 2]
            if crc == crc16(payload):
                out.append(payload)
            self.buf = self.buf[total:]
        return out


def cstr(s: str) -> bytes:
    return s.encode() + b"\0"


def handle(payload: bytes, node: int = 0, nodes: list[int] | None = None) -> list:
    cmd = payload[0]
    replies = []
    nodes = nodes or []

    if cmd == CMD_PING_CAN:
        replies.append(bytes((CMD_PING_CAN,)) + bytes(nodes))
    elif cmd == CMD_FW_VERSION:
        # Every packet starts with its command id, replies included.
        # major, minor, hw name, uuid(12), paired, testfw, hwType, confNum,
        # phaseFilters, qmlHw, qmlApp — commands.cpp stops at whatever exists.
        replies.append(bytes((CMD_FW_VERSION, 7, 0)) + cstr("FAKE_ESC") +
                       b"\1" * 12 + bytes((0, 0, 0, 0, 0, 0)))
    elif cmd == CMD_LISP_REPL_CMD:
        expr = payload[1:].split(b"\0")[0].decode(errors="replace")
        print(f"  repl[{node}]: {expr}", file=sys.stderr)
        # Two lines, like the real console: the value, then the prompt. The node
        # id is in the value so a test can prove where the answer came from.
        who = "" if node == 0 else f"node{node}:"
        replies.append(bytes((CMD_LISP_PRINT,)) + cstr(f"> {who}4f32"))
        replies.append(bytes((CMD_LISP_PRINT,)) + cstr("> "))
    elif cmd == CMD_LISP_GET_STATS:
        # double16 x100, big endian: cpu 3.00%, heap 11.00%, mem 20.00%,
        # stack 5.00%; then done_ctx_r; globals would follow as (str, f32auto).
        # cpu_use carries the node id: 3.00% on the attached device, 3+n on node n.
        vals = [300 + node * 100, 1100, 2000, 500]
        body = bytes((CMD_LISP_GET_STATS,)) + b"".join(
            struct.pack(">h", v) for v in vals) + cstr("main")
        replies.append(body)
    elif cmd == CMD_LISP_SET_RUNNING:
        replies.append(bytes((CMD_LISP_SET_RUNNING, 1)))
    elif cmd in (CMD_LISP_ERASE_CODE, CMD_LISP_WRITE_CODE, CMD_LISP_READ_CODE):
        replies.append(bytes((cmd, 1)))
    else:
        print(f"  (ignored cmd {cmd})", file=sys.stderr)

    return replies


def client_loop(conn, peer, nodes):
    print(f"client {peer}", file=sys.stderr)
    dec = PacketDecoder()
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            for payload in dec.feed(data):
                if payload[0] == CMD_FORWARD_CAN and len(payload) >= 2:
                    node = payload[1]
                    print(f"rx {len(payload)}B fwd -> node {node}", file=sys.stderr)
                    if node not in nodes:
                        # A real bus would simply never answer.
                        continue
                    replies = handle(payload[2:], node, nodes)
                else:
                    print(f"rx {len(payload)}B cmd={payload[0]}", file=sys.stderr)
                    replies = handle(payload, 0, nodes)
                for r in replies:
                    conn.sendall(frame(r))
    except (ConnectionError, OSError):
        pass
    finally:
        print(f"client {peer} gone", file=sys.stderr)
        conn.close()


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    nodes: list[int] = [1, 2, 3]
    for a in sys.argv[1:]:
        if a.startswith("--nodes="):
            nodes = [int(x) for x in a.split("=", 1)[1].split(",") if x]
    port = int(argv[0]) if argv else 65199
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port))
    srv.listen(1)
    print(f"fake VESC on 127.0.0.1:{port}, can nodes {nodes}", file=sys.stderr)
    while True:
        conn, addr = srv.accept()
        threading.Thread(target=client_loop, args=(conn, addr, nodes), daemon=True).start()


if __name__ == "__main__":
    main()
