#!/usr/bin/env python3
"""
Raspberry Pi hardware backend skeleton for Phase 02.

Supports:
- MCP4728 DAC output (TPS/MAP/O2 channels)
- MCP4131 digital potentiometer skeleton path

Falls back to mock mode when dependencies/hardware are unavailable.
"""

from dataclasses import dataclass
from typing import Any, Dict


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(value, hi))


@dataclass
class PiHardwareStatus:
    mode: str  # "real" or "mock"
    reason: str


class PiHardwareInterface:
    def __init__(self, config: Dict[str, Any]) -> None:
        hw_cfg = config.get("hardware", {})
        self.mock_on_missing = bool(hw_cfg.get("mock_on_missing", True))
        self.force_mock = bool(hw_cfg.get("force_mock", False))

        self.status = PiHardwareStatus(mode="mock", reason="not initialized")
        self._mcp = None
        self._spi = None

        if self.force_mock:
            self.status = PiHardwareStatus(mode="mock", reason="force_mock=true")
            return

        try:
            # Optional imports: available only on Pi env with proper packages.
            import board  # type: ignore
            import busio  # type: ignore
            import adafruit_mcp4728  # type: ignore
            import spidev  # type: ignore
        except Exception as exc:  # pragma: no cover
            if self.mock_on_missing:
                self.status = PiHardwareStatus(mode="mock", reason=f"missing deps: {exc}")
                return
            raise

        try:
            i2c_bus = int(hw_cfg.get("mcp4728", {}).get("i2c_bus", 1))
            address = int(hw_cfg.get("mcp4728", {}).get("address", 96))

            # board.I2C() typically maps to /dev/i2c-1 on Pi.
            i2c = board.I2C() if i2c_bus == 1 else busio.I2C(board.SCL, board.SDA)
            self._mcp = adafruit_mcp4728.MCP4728(i2c, address=address)

            spi_bus = int(hw_cfg.get("mcp4131", {}).get("spi_bus", 0))
            spi_device = int(hw_cfg.get("mcp4131", {}).get("spi_device", 0))
            max_speed_hz = int(hw_cfg.get("mcp4131", {}).get("max_speed_hz", 1_000_000))

            spi = spidev.SpiDev()
            spi.open(spi_bus, spi_device)
            spi.max_speed_hz = max_speed_hz
            self._spi = spi

            self.status = PiHardwareStatus(mode="real", reason="hardware initialized")
        except Exception as exc:  # pragma: no cover
            if self.mock_on_missing:
                self.status = PiHardwareStatus(mode="mock", reason=f"init failed: {exc}")
                self._mcp = None
                self._spi = None
                return
            raise

    def _set_dac_channel(self, channel_obj: Any, volts: float) -> None:
        normalized = clamp(volts / 5.0, 0.0, 1.0)
        raw_16 = int(normalized * 65535.0)

        # Adafruit lib variants expose either `value` or `normalized_value`.
        if hasattr(channel_obj, "value"):
            channel_obj.value = raw_16
            return
        if hasattr(channel_obj, "normalized_value"):
            channel_obj.normalized_value = normalized
            return

        raise RuntimeError("Unsupported MCP4728 channel API")

    def set_dac_voltages(self, tps_v: float, map_v: float, o2_v: float) -> None:
        if self.status.mode == "mock" or self._mcp is None:
            return

        # Convention:
        # channel_a -> TPS, channel_b -> MAP, channel_c -> O2
        self._set_dac_channel(self._mcp.channel_a, tps_v)
        self._set_dac_channel(self._mcp.channel_b, map_v)
        self._set_dac_channel(self._mcp.channel_c, o2_v)

    def set_digital_pot_raw(self, value_0_255: int) -> None:
        if self.status.mode == "mock" or self._spi is None:
            return

        value = int(clamp(value_0_255, 0, 255))
        # MCP4131 write command to pot0.
        self._spi.xfer2([0x00, value])

    def close(self) -> None:
        if self._spi is not None:
            try:
                self._spi.close()
            except Exception:
                pass
            self._spi = None

