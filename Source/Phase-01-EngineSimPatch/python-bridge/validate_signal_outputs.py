#!/usr/bin/env python3
"""
Validate bridge CSV output against profile-based ranges and rate limits.

Example:
  python validate_signal_outputs.py \
    --csv ../logs/signal_targets.csv \
    --config bridge_config.json \
    --profile phase2_minimum
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from signal_generator import load_config


@dataclass
class Violation:
    kind: str
    field: str
    frame: str
    timestamp: str
    detail: str


@dataclass
class Row:
    timestamp: str
    frame: str
    values: Dict[str, float]


NUMERIC_FIELDS: List[str] = [
    "tps_voltage_v",
    "map_voltage_v",
    "lambda_value",
    "o2_narrowband_v",
    "ect_temp_c",
    "iat_temp_c",
    "ect_resistance_ohm",
    "iat_resistance_ohm",
    "rpm",
]

DEFAULT_RATE_LIMITS: Dict[str, float] = {
    # Conservative defaults (units per second) if config has no slew limits.
    "tps_voltage_v": 12.0,
    "map_voltage_v": 15.0,
    "lambda_value": 2.0,
    "o2_narrowband_v": 8.0,
    "ect_temp_c": 6.0,
    "iat_temp_c": 6.0,
    "rpm": 7000.0,
}

SLEW_LIMIT_FIELD_MAP: Dict[str, str] = {
    "tps_voltage_v": "tps_voltage_v_per_s",
    "map_voltage_v": "map_voltage_v_per_s",
    "lambda_value": "lambda_per_s",
    "o2_narrowband_v": "o2_narrowband_v_per_s",
    "ect_temp_c": "temp_c_per_s",
    "iat_temp_c": "temp_c_per_s",
    "rpm": "rpm_per_s",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate bridge output CSV.")
    parser.add_argument(
        "--csv",
        required=True,
        help="Path to CSV file produced by signal_generator --sink csv",
    )
    parser.add_argument(
        "--config",
        default=str(Path(__file__).with_name("bridge_config.json")),
        help="Path to bridge config json",
    )
    parser.add_argument(
        "--profile",
        default=None,
        help="Optional config profile (for example: phase2_minimum)",
    )
    parser.add_argument(
        "--max-print",
        type=int,
        default=20,
        help="Max violations printed in summary (default: 20)",
    )
    parser.add_argument(
        "--rpm-max",
        type=float,
        default=9000.0,
        help="Absolute upper bound for rpm range check (default: 9000)",
    )
    parser.add_argument(
        "--rate-min-dt",
        type=float,
        default=0.003,
        help="Ignore rate checks for intervals below this dt seconds (default: 0.003)",
    )
    parser.add_argument(
        "--rate-tolerance",
        type=float,
        default=0.10,
        help="Relative tolerance for rate checks (default: 0.10 = 10%%)",
    )
    parser.add_argument(
        "--rate-source",
        choices=["max", "default", "config"],
        default="max",
        help=(
            "Rate limit source: "
            "'default' uses built-in limits, "
            "'config' prefers profile slew_limits, "
            "'max' uses the larger of default/config per field (default)"
        ),
    )
    return parser.parse_args()


def _float_or_none(value: str) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_timestamp_seconds(ts: str) -> Optional[float]:
    try:
        dt = datetime.fromisoformat(ts)
    except ValueError:
        return None
    return dt.timestamp()


def load_rows(csv_path: Path) -> Tuple[List[Row], List[str], List[str]]:
    rows: List[Row] = []
    warnings: List[str] = []
    available_fields: List[str] = []

    with csv_path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        required_base = ["timestamp", "frame"]
        missing_base = [f for f in required_base if f not in fieldnames]
        if missing_base:
            raise ValueError(f"CSV missing required base columns: {', '.join(missing_base)}")

        available_fields = [f for f in NUMERIC_FIELDS if f in fieldnames]
        if not available_fields:
            raise ValueError("CSV contains no known numeric signal columns")

        unavailable = [f for f in NUMERIC_FIELDS if f not in fieldnames]
        if unavailable:
            warnings.append(
                "skipping unavailable columns from validation: " + ", ".join(unavailable)
            )

        for idx, raw in enumerate(reader, start=2):
            values: Dict[str, float] = {}
            bad_fields: List[str] = []
            for field in available_fields:
                value = _float_or_none(raw.get(field, ""))
                if value is None:
                    bad_fields.append(field)
                else:
                    values[field] = value

            if bad_fields:
                warnings.append(
                    f"line {idx}: skipped due to non-numeric fields: {', '.join(bad_fields)}"
                )
                continue

            rows.append(
                Row(
                    timestamp=raw.get("timestamp", ""),
                    frame=raw.get("frame", ""),
                    values=values,
                )
            )

    return rows, warnings, available_fields


def build_ranges(cfg: Dict[str, object], rpm_max: float, available_fields: List[str]) -> Dict[str, Tuple[float, float]]:
    tps_cfg = cfg.get("tps", {})
    map_cfg = cfg.get("map", {})
    lambda_cfg = cfg.get("lambda", {})
    o2_cfg = cfg.get("o2_narrowband", {})
    temp_limits = cfg.get("sensor_temp_limits", {})
    ntc_cfg = cfg.get("ntc", {})

    rich = float(o2_cfg.get("rich_voltage", 0.85))
    lean = float(o2_cfg.get("lean_voltage", 0.15))
    o2_min = min(rich, lean)
    o2_max = max(rich, lean)

    ranges = {
        "tps_voltage_v": (float(tps_cfg.get("v_min", 0.0)), float(tps_cfg.get("v_max", 5.0))),
        "map_voltage_v": (float(map_cfg.get("v_min", 0.0)), float(map_cfg.get("v_max", 5.0))),
        "lambda_value": (float(lambda_cfg.get("min", 0.0)), float(lambda_cfg.get("max", 2.0))),
        "o2_narrowband_v": (o2_min, o2_max),
        "ect_temp_c": (
            float(temp_limits.get("ect_c_min", -40.0)),
            float(temp_limits.get("ect_c_max", 140.0)),
        ),
        "iat_temp_c": (
            float(temp_limits.get("iat_c_min", -40.0)),
            float(temp_limits.get("iat_c_max", 140.0)),
        ),
        "ect_resistance_ohm": (
            float(ntc_cfg.get("min_ohm", 50.0)),
            float(ntc_cfg.get("max_ohm", 200000.0)),
        ),
        "iat_resistance_ohm": (
            float(ntc_cfg.get("min_ohm", 50.0)),
            float(ntc_cfg.get("max_ohm", 200000.0)),
        ),
        "rpm": (0.0, float(rpm_max)),
    }
    return {k: v for k, v in ranges.items() if k in available_fields}


def build_rate_limits(
    cfg: Dict[str, object],
    available_fields: List[str],
    warnings: List[str],
    rate_source: str,
) -> Dict[str, float]:
    defaults = dict(DEFAULT_RATE_LIMITS)
    config_limits: Dict[str, float] = {}
    slew_cfg = cfg.get("slew_limits", {})
    if isinstance(slew_cfg, dict) and bool(slew_cfg.get("enabled", False)):
        for field, cfg_key in SLEW_LIMIT_FIELD_MAP.items():
            if field not in defaults:
                continue
            raw = slew_cfg.get(cfg_key)
            if raw is None:
                continue
            try:
                parsed = float(raw)
            except (TypeError, ValueError):
                warnings.append(
                    f"invalid slew limit '{cfg_key}={raw}' in config; using default for {field}"
                )
                continue
            if parsed > 0:
                config_limits[field] = parsed

    limits = dict(defaults)
    if rate_source == "config":
        for field, value in config_limits.items():
            limits[field] = value
    elif rate_source == "max":
        for field, value in config_limits.items():
            limits[field] = max(defaults.get(field, value), value)

    return {k: v for k, v in limits.items() if k in available_fields}


def validate_rows(
    rows: List[Row],
    ranges: Dict[str, Tuple[float, float]],
    rate_limits: Dict[str, float],
    rate_min_dt: float,
    rate_tolerance: float,
) -> Tuple[List[Violation], int]:
    violations: List[Violation] = []
    eps = 1e-9
    skipped_short_dt = 0

    for row in rows:
        for field, (lo, hi) in ranges.items():
            value = row.values[field]
            if value < lo - eps or value > hi + eps:
                violations.append(
                    Violation(
                        kind="range",
                        field=field,
                        frame=row.frame,
                        timestamp=row.timestamp,
                        detail=f"value={value:.6f} outside [{lo:.6f}, {hi:.6f}]",
                    )
                )

    prev: Optional[Row] = None
    for row in rows:
        if prev is None:
            prev = row
            continue

        t0 = _parse_timestamp_seconds(prev.timestamp)
        t1 = _parse_timestamp_seconds(row.timestamp)
        if t0 is None or t1 is None:
            prev = row
            continue

        dt = t1 - t0
        if dt <= 0:
            prev = row
            continue

        if dt < rate_min_dt:
            skipped_short_dt += 1
            prev = row
            continue

        for field, max_rate in rate_limits.items():
            current = row.values[field]
            prior = prev.values[field]
            rate = abs(current - prior) / dt
            limit = max_rate * (1.0 + rate_tolerance)
            if rate > limit:
                violations.append(
                    Violation(
                        kind="rate",
                        field=field,
                        frame=row.frame,
                        timestamp=row.timestamp,
                        detail=(
                            f"rate={rate:.3f}/s exceeds {limit:.3f}/s "
                            f"(base={max_rate:.3f}/s tol={rate_tolerance:.1%}, dt={dt:.4f}s)"
                        ),
                    )
                )

        prev = row

    return violations, skipped_short_dt


def summarize(
    rows: List[Row],
    violations: List[Violation],
    warnings: List[str],
    max_print: int,
    skipped_short_dt: int,
) -> int:
    print(f"[validator] rows={len(rows)}")
    if rows:
        print(f"[validator] frame_range={rows[0].frame}..{rows[-1].frame}")
        print(f"[validator] time_range={rows[0].timestamp} -> {rows[-1].timestamp}")
    if skipped_short_dt:
        print(f"[validator] skipped_short_dt_intervals={skipped_short_dt}")

    if warnings:
        print(f"[validator] warnings={len(warnings)}")
        for warning in warnings[:5]:
            print(f"  - {warning}")
        if len(warnings) > 5:
            print(f"  - ... and {len(warnings) - 5} more")

    if not violations:
        print("[validator] PASS: no range/rate violations detected")
        return 0

    range_count = sum(1 for v in violations if v.kind == "range")
    rate_count = sum(1 for v in violations if v.kind == "rate")
    print(f"[validator] FAIL: violations={len(violations)} range={range_count} rate={rate_count}")
    for violation in violations[:max_print]:
        print(
            f"  - [{violation.kind}] field={violation.field} frame={violation.frame} "
            f"time={violation.timestamp} {violation.detail}"
        )
    if len(violations) > max_print:
        print(f"  - ... and {len(violations) - max_print} more")
    return 1


def main() -> int:
    args = parse_args()
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"[validator] error: csv not found: {csv_path}")
        return 2

    config_path = Path(args.config)
    cfg, active_profile = load_config(config_path, args.profile)
    print(f"[validator] config={config_path}")
    print(f"[validator] profile={active_profile}")
    print(
        "[validator] "
        f"rate_source={args.rate_source} "
        f"rate_min_dt={args.rate_min_dt:.4f}s "
        f"rate_tolerance={args.rate_tolerance:.1%}"
    )

    rows, warnings, available_fields = load_rows(csv_path)
    if not rows:
        print("[validator] error: no valid rows found in csv")
        return 2

    ranges = build_ranges(cfg, args.rpm_max, available_fields)
    rate_limits = build_rate_limits(cfg, available_fields, warnings, args.rate_source)
    violations, skipped_short_dt = validate_rows(
        rows,
        ranges,
        rate_limits,
        rate_min_dt=max(0.0, float(args.rate_min_dt)),
        rate_tolerance=max(0.0, float(args.rate_tolerance)),
    )
    return summarize(rows, violations, warnings, args.max_print, skipped_short_dt)


if __name__ == "__main__":
    raise SystemExit(main())
