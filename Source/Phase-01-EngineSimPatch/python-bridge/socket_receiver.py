#!/usr/bin/env python3
"""
Phase 01 UDP receiver for engine-sim state output.

Usage:
  python socket_receiver.py
  python socket_receiver.py --host 127.0.0.1 --port 5555 --raw
"""

import argparse
import json
import socket
import time
from datetime import datetime
from typing import Dict, Any, Tuple


def validate_payload(msg: Dict[str, Any], expected_version: int) -> Tuple[bool, str]:
    if msg.get("schema_version") != expected_version:
        return False, f"schema_version mismatch (expected {expected_version}, got {msg.get('schema_version')})"

    engine = msg.get("engine")
    if not isinstance(engine, dict):
        return False, "engine object missing"

    required = [
        "rpm",
        "throttle",
        "manifold_pressure",
        "intake_afr",
        "exhaust_o2",
        "combustion_temp_c",
        "intake_temp_c",
    ]
    missing = [k for k in required if k not in engine]
    if missing:
        return False, f"missing engine fields: {', '.join(missing)}"

    return True, ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Listen for engine-sim UDP JSON state packets.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5555, help="Bind UDP port (default: 5555)")
    parser.add_argument("--raw", action="store_true", help="Print raw JSON payload instead of compact view")
    parser.add_argument(
        "--stats-interval",
        type=float,
        default=2.0,
        help="Print packet stats every N seconds (default: 2.0)",
    )
    parser.add_argument("--expected-schema-version", type=int, default=1, help="Expected schema_version value")
    parser.add_argument("--no-schema-check", action="store_true", help="Disable schema validation")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.host, args.port))

    print(f"[receiver] listening on udp://{args.host}:{args.port}")

    total_packets = 0
    dropped_frames = 0
    out_of_order_frames = 0
    invalid_json = 0
    invalid_schema = 0
    last_frame = None

    interval_packets = 0
    interval_start = time.monotonic()

    while True:
        payload, _ = sock.recvfrom(65535)
        text = payload.decode("utf-8", errors="replace")

        if args.raw:
            print(text)
            total_packets += 1
            interval_packets += 1
            continue

        try:
            msg = json.loads(text)
            engine = msg.get("engine", {})

            if not args.no_schema_check:
                valid, reason = validate_payload(msg, args.expected_schema_version)
                if not valid:
                    invalid_schema += 1
                    print(f"[receiver] schema check failed: {reason}")
                    continue

            frame = msg.get("frame")

            if isinstance(frame, int):
                if last_frame is not None:
                    if frame > last_frame + 1:
                        dropped_frames += frame - last_frame - 1
                    elif frame <= last_frame:
                        out_of_order_frames += 1
                last_frame = frame

            total_packets += 1
            interval_packets += 1

            line = (
                f"{datetime.now().strftime('%H:%M:%S')} "
                f"frame={msg.get('frame')} "
                f"rpm={engine.get('rpm')} "
                f"thr={engine.get('throttle')} "
                f"map_pa={engine.get('manifold_pressure')} "
                f"afr={engine.get('intake_afr')} "
                f"o2={engine.get('exhaust_o2')} "
                f"ect_c={engine.get('combustion_temp_c')} "
                f"iat_c={engine.get('intake_temp_c')}"
            )
            print(line)
        except json.JSONDecodeError:
            invalid_json += 1
            print(f"[receiver] invalid json: {text}")

        elapsed = time.monotonic() - interval_start
        if elapsed >= args.stats_interval:
            rate = interval_packets / elapsed if elapsed > 0 else 0.0
            print(
                "[stats] "
                f"rate={rate:.1f} pkt/s "
                f"total={total_packets} "
                f"dropped={dropped_frames} "
                f"out_of_order={out_of_order_frames} "
                f"invalid_json={invalid_json} "
                f"invalid_schema={invalid_schema}"
            )
            interval_start = time.monotonic()
            interval_packets = 0


if __name__ == "__main__":
    main()
