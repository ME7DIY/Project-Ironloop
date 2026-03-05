#!/usr/bin/env python3
"""
Phase 02 bridge scaffold:
Receives Phase 01 UDP state packets and converts them into preliminary
sensor output targets for ME7 signal emulation.
"""

import argparse
import json
import math
import socket
from pathlib import Path
from typing import Dict, Any, Tuple

from hardware_io import SensorTargets, create_sink


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(value, hi))


DEFAULT_CONFIG: Dict[str, Any] = {
    "tps": {"v_min": 0.5, "v_max": 4.5},
    "map": {"kpa_min": 20.0, "kpa_max": 250.0, "v_min": 0.5, "v_max": 4.5},
    "lambda": {"stoich_afr": 14.7, "min": 0.7, "max": 1.4},
    "o2_narrowband": {
        "model": "sigmoid",
        "rich_voltage": 0.85,
        "lean_voltage": 0.15,
        "switch_lambda": 1.0,
        "sigmoid_gain": 45.0
    },
    "ntc": {"r0_ohm": 2500.0, "t0_c": 25.0, "beta": 3950.0, "min_ohm": 100.0, "max_ohm": 100000.0},
    "sensor_temp_limits": {"ect_c_min": -40.0, "ect_c_max": 115.0, "iat_c_min": -40.0, "iat_c_max": 80.0},
    "ect_remap": {"enabled": True, "in_min_c": 200.0, "in_max_c": 2400.0, "out_min_c": 75.0, "out_max_c": 110.0},
    "iat_remap": {"enabled": True, "in_min_c": 20.0, "in_max_c": 160.0, "out_min_c": 20.0, "out_max_c": 60.0},
    "schema": {"version": 1},
    "smoothing": {"enabled": True, "alpha": 0.35},
}


class ExponentialSmoother:
    def __init__(self, alpha: float) -> None:
        self.alpha = clamp(alpha, 0.01, 1.0)
        self._state: Dict[str, float] = {}

    def step(self, key: str, value: float) -> float:
        if key not in self._state:
            self._state[key] = value
            return value
        smoothed = self.alpha * value + (1.0 - self.alpha) * self._state[key]
        self._state[key] = smoothed
        return smoothed


def load_config(config_path: Path) -> Dict[str, Any]:
    config = json.loads(json.dumps(DEFAULT_CONFIG))
    if not config_path.exists():
        return config
    try:
        with config_path.open("r", encoding="utf-8") as f:
            user_cfg = json.load(f)
    except Exception:
        return config

    # shallow merge for current simple structure
    for section, values in user_cfg.items():
        if isinstance(values, dict) and section in config:
            config[section].update(values)
        else:
            config[section] = values
    return config


def throttle_to_tps_voltage(throttle_ratio: float, cfg: Dict[str, Any]) -> float:
    v_min = float(cfg["tps"]["v_min"])
    v_max = float(cfg["tps"]["v_max"])
    return v_min + clamp(throttle_ratio, 0.0, 1.0) * (v_max - v_min)


def map_pa_to_voltage(map_pa: float, cfg: Dict[str, Any]) -> float:
    kpa = map_pa / 1000.0
    kpa_min = float(cfg["map"]["kpa_min"])
    kpa_max = float(cfg["map"]["kpa_max"])
    v_min = float(cfg["map"]["v_min"])
    v_max = float(cfg["map"]["v_max"])
    normalized = (kpa - kpa_min) / (kpa_max - kpa_min)
    return v_min + clamp(normalized, 0.0, 1.0) * (v_max - v_min)


def afr_to_lambda(afr: float, cfg: Dict[str, Any]) -> float:
    if afr <= 0:
        return 1.0
    stoich = float(cfg["lambda"]["stoich_afr"])
    lam_min = float(cfg["lambda"]["min"])
    lam_max = float(cfg["lambda"]["max"])
    return clamp(afr / stoich, lam_min, lam_max)


def lambda_to_narrowband_voltage(lambda_value: float, cfg: Dict[str, Any]) -> float:
    nb_cfg = cfg["o2_narrowband"]
    rich = float(nb_cfg["rich_voltage"])
    lean = float(nb_cfg["lean_voltage"])
    model = str(nb_cfg.get("model", "step")).lower()

    if model == "step":
        switch_lambda = float(nb_cfg.get("switch_lambda", 1.0))
        return rich if lambda_value < switch_lambda else lean

    # Sigmoid model produces a narrowband-like transition around lambda=1.
    switch_lambda = float(nb_cfg.get("switch_lambda", 1.0))
    gain = float(nb_cfg.get("sigmoid_gain", 45.0))
    transition = 1.0 / (1.0 + math.exp(gain * (lambda_value - switch_lambda)))
    return clamp(lean + (rich - lean) * transition, min(rich, lean), max(rich, lean))


def temp_c_to_ntc_ohms(temp_c: float, cfg: Dict[str, Any]) -> float:
    # Beta model:
    # R = R0 * exp(B * (1/T - 1/T0))
    ntc = cfg["ntc"]
    r0 = float(ntc["r0_ohm"])
    t0_k = float(ntc["t0_c"]) + 273.15
    beta = float(ntc["beta"])
    min_ohm = float(ntc["min_ohm"])
    max_ohm = float(ntc["max_ohm"])

    t_k = temp_c + 273.15
    if t_k <= 0:
        return max_ohm

    resistance = r0 * math.exp(beta * ((1.0 / t_k) - (1.0 / t0_k)))
    return clamp(resistance, min_ohm, max_ohm)


def remap_value(value: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    if in_max <= in_min:
        return out_min
    normalized = clamp((value - in_min) / (in_max - in_min), 0.0, 1.0)
    return out_min + (out_max - out_min) * normalized


def map_sensor_temp(raw_temp_c: float, cfg: Dict[str, Any], sensor: str) -> float:
    if sensor not in ("ect", "iat"):
        return raw_temp_c

    remap_cfg = cfg.get(f"{sensor}_remap", {})
    mapped = raw_temp_c
    if bool(remap_cfg.get("enabled", False)):
        mapped = remap_value(
            raw_temp_c,
            float(remap_cfg.get("in_min_c", -40.0)),
            float(remap_cfg.get("in_max_c", 120.0)),
            float(remap_cfg.get("out_min_c", -40.0)),
            float(remap_cfg.get("out_max_c", 120.0)),
        )

    limits = cfg.get("sensor_temp_limits", {})
    min_c = float(limits.get(f"{sensor}_c_min", -40.0))
    max_c = float(limits.get(f"{sensor}_c_max", 120.0))
    return clamp(mapped, min_c, max_c)


def validate_payload(msg: Dict[str, Any], cfg: Dict[str, Any]) -> Tuple[bool, str]:
    expected_version = int(cfg["schema"]["version"])
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


def convert_engine_state(msg: dict, cfg: Dict[str, Any]) -> SensorTargets:
    engine = msg.get("engine", {})
    throttle = float(engine.get("throttle", 0.0))
    map_pa = float(engine.get("manifold_pressure", 101325.0))
    afr = float(engine.get("intake_afr", 14.7))
    raw_ect_temp_c = float(engine.get("combustion_temp_c", 90.0))
    raw_iat_temp_c = float(engine.get("intake_temp_c", 25.0))
    ect_temp_c = map_sensor_temp(raw_ect_temp_c, cfg, "ect")
    iat_temp_c = map_sensor_temp(raw_iat_temp_c, cfg, "iat")
    rpm = float(engine.get("rpm", 0.0))

    lambda_value = afr_to_lambda(afr, cfg)
    return SensorTargets(
        tps_voltage_v=throttle_to_tps_voltage(throttle, cfg),
        map_voltage_v=map_pa_to_voltage(map_pa, cfg),
        lambda_value=lambda_value,
        o2_narrowband_v=lambda_to_narrowband_voltage(lambda_value, cfg),
        ect_temp_c=ect_temp_c,
        iat_temp_c=iat_temp_c,
        ect_resistance_ohm=temp_c_to_ntc_ohms(ect_temp_c, cfg),
        iat_resistance_ohm=temp_c_to_ntc_ohms(iat_temp_c, cfg),
        rpm=rpm,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert engine UDP state to sensor targets.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5555, help="Bind UDP port (default: 5555)")
    parser.add_argument(
        "--sink",
        default="stub",
        choices=["stub", "console", "csv", "pi"],
        help="Output sink backend (default: stub)",
    )
    parser.add_argument("--csv-path", default="logs/signal_targets.csv", help="CSV path when --sink csv")
    parser.add_argument(
        "--config",
        default=str(Path(__file__).with_name("bridge_config.json")),
        help="Path to bridge mapping config JSON",
    )
    parser.add_argument("--print-input", action="store_true", help="Also print incoming engine payload")
    parser.add_argument("--no-schema-check", action="store_true", help="Disable schema/version validation")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(Path(args.config))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.host, args.port))
    sink = create_sink(args.sink, args.csv_path, config)
    smoothing_cfg = config.get("smoothing", {})
    smoothing_enabled = bool(smoothing_cfg.get("enabled", True))
    smoother = ExponentialSmoother(float(smoothing_cfg.get("alpha", 0.35)))

    print(f"[signal-generator] listening on udp://{args.host}:{args.port}")
    print(f"[signal-generator] sink={args.sink}")

    while True:
        payload, _ = sock.recvfrom(65535)
        text = payload.decode("utf-8", errors="replace")

        try:
            msg = json.loads(text)
        except json.JSONDecodeError:
            print(f"[signal-generator] invalid json: {text}")
            continue

        if args.print_input:
            print(f"[input] {text}")

        if not args.no_schema_check:
            valid, reason = validate_payload(msg, config)
            if not valid:
                print(f"[signal-generator] schema check failed: {reason}")
                continue

        targets = convert_engine_state(msg, config)
        if smoothing_enabled:
            ect_temp_c = smoother.step("ect_c", targets.ect_temp_c)
            iat_temp_c = smoother.step("iat_c", targets.iat_temp_c)
            targets = SensorTargets(
                tps_voltage_v=smoother.step("tps", targets.tps_voltage_v),
                map_voltage_v=smoother.step("map", targets.map_voltage_v),
                lambda_value=smoother.step("lambda", targets.lambda_value),
                o2_narrowband_v=smoother.step("o2", targets.o2_narrowband_v),
                ect_temp_c=ect_temp_c,
                iat_temp_c=iat_temp_c,
                ect_resistance_ohm=temp_c_to_ntc_ohms(ect_temp_c, config),
                iat_resistance_ohm=temp_c_to_ntc_ohms(iat_temp_c, config),
                rpm=smoother.step("rpm", targets.rpm),
            )
        sink.apply(targets, msg.get("frame"))


if __name__ == "__main__":
    main()
