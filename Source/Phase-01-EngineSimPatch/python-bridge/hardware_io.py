#!/usr/bin/env python3
"""
Hardware output sinks for the Phase 02 bridge scaffold.

`stub` simulates DAC writes and is the default until real hardware drivers
are integrated.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Protocol
import csv

from pi_hardware import PiHardwareInterface


@dataclass
class SensorTargets:
    tps_voltage_v: float
    map_voltage_v: float
    lambda_value: float
    o2_narrowband_v: float
    ect_temp_c: float
    iat_temp_c: float
    ect_resistance_ohm: float
    iat_resistance_ohm: float
    rpm: float


class HardwareSink(Protocol):
    def apply(self, targets: SensorTargets, frame: Optional[int]) -> None:
        ...


class ConsoleSink:
    def apply(self, targets: SensorTargets, frame: Optional[int]) -> None:
        print(
            f"{datetime.now().strftime('%H:%M:%S')} "
            f"frame={frame} "
            f"tps_v={targets.tps_voltage_v:.3f} "
            f"map_v={targets.map_voltage_v:.3f} "
            f"lambda={targets.lambda_value:.3f} "
            f"o2_v={targets.o2_narrowband_v:.3f} "
            f"ect_c={targets.ect_temp_c:.1f} "
            f"iat_c={targets.iat_temp_c:.1f} "
            f"rpm={targets.rpm:.1f}"
        )


class StubMe7HardwareSink:
    """
    Phase 02 placeholder sink.
    Simulates hardware channel writes to DAC outputs.
    """

    def __init__(self) -> None:
        self.dac_channels = {
            "tps": 0.0,
            "map": 0.0,
            "o2": 0.0,
        }

    def _write_dac(self, channel: str, volts: float) -> None:
        self.dac_channels[channel] = volts

    def apply(self, targets: SensorTargets, frame: Optional[int]) -> None:
        self._write_dac("tps", targets.tps_voltage_v)
        self._write_dac("map", targets.map_voltage_v)
        self._write_dac("o2", targets.o2_narrowband_v)

        print(
            f"{datetime.now().strftime('%H:%M:%S')} "
            f"frame={frame} "
            f"dac[tps]={self.dac_channels['tps']:.3f}V "
            f"dac[map]={self.dac_channels['map']:.3f}V "
            f"dac[o2]={self.dac_channels['o2']:.3f}V "
            f"r_ect={targets.ect_resistance_ohm:.0f}ohm "
            f"r_iat={targets.iat_resistance_ohm:.0f}ohm "
            f"lambda={targets.lambda_value:.3f} "
            f"rpm={targets.rpm:.1f}"
        )


class CsvSink:
    def __init__(self, csv_path: str) -> None:
        self.path = Path(csv_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.path.open("a", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)
        if self._file.tell() == 0:
            self._writer.writerow([
                "timestamp",
                "frame",
                "tps_voltage_v",
                "map_voltage_v",
                "lambda_value",
                "o2_narrowband_v",
                "ect_temp_c",
                "iat_temp_c",
                "ect_resistance_ohm",
                "iat_resistance_ohm",
                "rpm",
            ])
            self._file.flush()

    def apply(self, targets: SensorTargets, frame: Optional[int]) -> None:
        self._writer.writerow([
            datetime.now().isoformat(timespec="milliseconds"),
            frame,
            f"{targets.tps_voltage_v:.6f}",
            f"{targets.map_voltage_v:.6f}",
            f"{targets.lambda_value:.6f}",
            f"{targets.o2_narrowband_v:.6f}",
            f"{targets.ect_temp_c:.6f}",
            f"{targets.iat_temp_c:.6f}",
            f"{targets.ect_resistance_ohm:.6f}",
            f"{targets.iat_resistance_ohm:.6f}",
            f"{targets.rpm:.6f}",
        ])
        self._file.flush()

    def __del__(self) -> None:
        try:
            self._file.close()
        except Exception:
            pass


class PiMe7HardwareSink:
    """
    Hardware sink that targets Pi-attached MCP4728/MCP4131.
    Falls back to mock behavior automatically if configured or unavailable.
    """

    def __init__(self, config: dict) -> None:
        self.hw = PiHardwareInterface(config)
        print(f"[hardware] pi sink mode={self.hw.status.mode} ({self.hw.status.reason})")

    def apply(self, targets: SensorTargets, frame: Optional[int]) -> None:
        # DAC channel outputs (Phase 02 core path).
        self.hw.set_dac_voltages(
            tps_v=targets.tps_voltage_v,
            map_v=targets.map_voltage_v,
            o2_v=targets.o2_narrowband_v,
        )

        # MCP4131 uses one wiper value; use ECT proxy for now.
        pot_raw = int(max(0, min(255, (targets.ect_resistance_ohm / 10000.0) * 255.0)))
        self.hw.set_digital_pot_raw(pot_raw)

        print(
            f"{datetime.now().strftime('%H:%M:%S')} "
            f"frame={frame} "
            f"pi[{self.hw.status.mode}] "
            f"tps_v={targets.tps_voltage_v:.3f} "
            f"map_v={targets.map_voltage_v:.3f} "
            f"o2_v={targets.o2_narrowband_v:.3f} "
            f"r_ect={targets.ect_resistance_ohm:.0f}ohm "
            f"lambda={targets.lambda_value:.3f} "
            f"rpm={targets.rpm:.1f}"
        )


def create_sink(
    name: str,
    csv_path: str = "logs/signal_targets.csv",
    config: Optional[dict] = None
) -> HardwareSink:
    normalized = name.strip().lower()
    if normalized == "console":
        return ConsoleSink()
    if normalized == "stub":
        return StubMe7HardwareSink()
    if normalized == "csv":
        return CsvSink(csv_path)
    if normalized == "pi":
        return PiMe7HardwareSink(config or {})

    raise ValueError(f"Unknown sink: {name}")
