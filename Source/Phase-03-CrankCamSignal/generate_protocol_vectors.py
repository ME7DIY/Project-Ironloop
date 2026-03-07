#!/usr/bin/env python3
"""
Generate deterministic Pi<->Pico protocol command vectors for IRONLOOP.

This script emits JSON files containing:
- ordered host commands
- expected device responses
- expected device state after each command

Primary goal: validate parser/state-machine behavior before bench hardware.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

PROTO = "IRONLOOP-PICO-1"


@dataclass
class Step:
    index: int
    host_tx: str
    expected_rx: List[str]
    expected_state: Dict[str, object]


def _status_line(state: str, rpm: int, sync: int) -> str:
    return f"STATUS state={state} rpm={rpm} sync={sync} proto={PROTO}"


def build_smoke_sequence() -> List[Step]:
    steps: List[Step] = []
    state = "IDLE"
    rpm = 0
    sync = 0
    i = 1

    def add(host_tx: str, expected_rx: List[str]) -> None:
        nonlocal i
        steps.append(
            Step(
                index=i,
                host_tx=host_tx,
                expected_rx=expected_rx,
                expected_state={"state": state, "rpm": rpm, "sync": sync},
            )
        )
        i += 1

    add(
        "HELLO proto=IRONLOOP-PICO-1 client=pi5",
        [f"OK cmd=HELLO proto={PROTO} fw=<version> state=IDLE"],
    )

    rpm = 1200
    add("SET_RPM value=1200", ["OK cmd=SET_RPM value=1200"])

    state = "RUNNING"
    sync = 1
    add("START", ["OK cmd=START state=RUNNING"])

    add("STATUS", [_status_line(state, rpm, sync)])

    rpm = 3400
    add("SET_RPM value=3400", ["OK cmd=SET_RPM value=3400"])
    add("STATUS", [_status_line(state, rpm, sync)])

    add("SET_RPM value=99999", ["ERR code=BAD_VALUE msg=rpm_out_of_range"])
    add("SETRPM value=1400", ["ERR code=UNKNOWN_CMD msg=setrpm"])

    state = "IDLE"
    sync = 0
    add("STOP", ["OK cmd=STOP state=IDLE"])
    add("STATUS", [_status_line(state, rpm, sync)])

    add("PING t=1710000000000", ["OK cmd=PING t=1710000000000"])
    return steps


def to_payload(profile_name: str, steps: List[Step]) -> Dict[str, object]:
    return {
        "name": profile_name,
        "protocol": PROTO,
        "description": "Deterministic command/response smoke sequence for Pi<->Pico parser tests",
        "steps": [asdict(step) for step in steps],
    }


def parse_args() -> argparse.Namespace:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Generate protocol test vectors.")
    parser.add_argument(
        "--out",
        default=str(script_dir / "vectors" / "pi_pico_protocol_smoke_v1.json"),
        help="Output JSON path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    payload = to_payload("smoke_v1", build_smoke_sequence())
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"[vector-gen] wrote {out_path}")
    print(f"[vector-gen] steps={len(payload['steps'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
