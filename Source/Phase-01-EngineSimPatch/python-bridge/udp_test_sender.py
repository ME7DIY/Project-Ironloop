#!/usr/bin/env python3
"""
Emit schema-valid UDP engine state packets for bridge smoke testing.

Usage:
  python udp_test_sender.py
  python udp_test_sender.py --hz 50 --duration 10
  python udp_test_sender.py --rpm-min 800 --rpm-max 4200 --throttle-min 0.05 --throttle-max 0.9
"""

import argparse
import json
import math
import socket
import time


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(value, hi))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def wave_0_1(seconds: float, period: float) -> float:
    if period <= 0:
        return 0.0
    phase = (seconds % period) / period
    return (math.sin(phase * 2.0 * math.pi) + 1.0) * 0.5


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send synthetic engine-sim UDP packets.")
    parser.add_argument("--host", default="127.0.0.1", help="Target host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5555, help="Target UDP port (default: 5555)")
    parser.add_argument("--hz", type=float, default=60.0, help="Packet rate in Hz (default: 60)")
    parser.add_argument("--duration", type=float, default=0.0, help="Seconds to run; 0 means infinite")
    parser.add_argument("--rpm-min", type=float, default=800.0, help="Minimum RPM (default: 800)")
    parser.add_argument("--rpm-max", type=float, default=4200.0, help="Maximum RPM (default: 4200)")
    parser.add_argument("--throttle-min", type=float, default=0.05, help="Minimum throttle ratio (default: 0.05)")
    parser.add_argument("--throttle-max", type=float, default=0.90, help="Maximum throttle ratio (default: 0.90)")
    parser.add_argument("--map-kpa-min", type=float, default=30.0, help="Minimum MAP kPa (default: 30)")
    parser.add_argument("--map-kpa-max", type=float, default=190.0, help="Maximum MAP kPa (default: 190)")
    parser.add_argument("--afr-rich", type=float, default=12.2, help="Rich AFR endpoint (default: 12.2)")
    parser.add_argument("--afr-lean", type=float, default=15.8, help="Lean AFR endpoint (default: 15.8)")
    parser.add_argument("--ect-min", type=float, default=75.0, help="Minimum coolant temp C (default: 75)")
    parser.add_argument("--ect-max", type=float, default=102.0, help="Maximum coolant temp C (default: 102)")
    parser.add_argument("--iat-min", type=float, default=18.0, help="Minimum intake temp C (default: 18)")
    parser.add_argument("--iat-max", type=float, default=48.0, help="Maximum intake temp C (default: 48)")
    parser.add_argument("--print-every", type=int, default=30, help="Print every N packets (default: 30)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    hz = max(args.hz, 1.0)
    interval = 1.0 / hz
    duration = max(args.duration, 0.0)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start = time.monotonic()
    frame = 0

    print(f"[udp-test-sender] target=udp://{args.host}:{args.port} hz={hz:.1f} duration={duration:.1f}s")

    while True:
        now = time.monotonic()
        elapsed = now - start
        if duration > 0 and elapsed >= duration:
            break

        # Smooth engine profile waveforms for repeatable tests.
        throttle_t = wave_0_1(elapsed, 6.0)
        rpm_t = wave_0_1(elapsed, 5.0)
        map_t = wave_0_1(elapsed, 4.0)
        afr_t = wave_0_1(elapsed + 0.8, 7.0)
        ect_t = wave_0_1(elapsed, 18.0)
        iat_t = wave_0_1(elapsed + 1.2, 10.0)

        throttle = clamp(lerp(args.throttle_min, args.throttle_max, throttle_t), 0.0, 1.0)
        rpm = max(0.0, lerp(args.rpm_min, args.rpm_max, rpm_t))
        map_pa = max(0.0, lerp(args.map_kpa_min, args.map_kpa_max, map_t) * 1000.0)
        intake_afr = max(1.0, lerp(args.afr_rich, args.afr_lean, afr_t))
        exhaust_o2 = clamp((intake_afr - 14.7) * 0.02, -0.2, 0.2)
        ect_c = lerp(args.ect_min, args.ect_max, ect_t)
        iat_c = lerp(args.iat_min, args.iat_max, iat_t)

        payload = {
            "schema_version": 1,
            "timestamp_ms": int(time.time() * 1000),
            "frame": frame,
            "engine": {
                "rpm": round(rpm, 3),
                "throttle": round(throttle, 6),
                "manifold_pressure": round(map_pa, 3),
                "intake_afr": round(intake_afr, 3),
                "exhaust_o2": round(exhaust_o2, 6),
                "combustion_temp_c": round(ect_c, 3),
                "intake_temp_c": round(iat_c, 3),
            },
        }

        text = json.dumps(payload, separators=(",", ":"))
        sock.sendto(text.encode("utf-8"), (args.host, args.port))

        if args.print_every > 0 and (frame % args.print_every == 0):
            print(
                f"[udp-test-sender] frame={frame} rpm={rpm:.1f} "
                f"thr={throttle:.2f} map_kpa={map_pa / 1000.0:.1f} "
                f"afr={intake_afr:.2f} ect={ect_c:.1f} iat={iat_c:.1f}"
            )

        frame += 1
        time.sleep(interval)

    print(f"[udp-test-sender] done sent_frames={frame}")


if __name__ == "__main__":
    main()
