# Phase 01 UDP Schema (MVP)

## Endpoint

- Transport: UDP
- Host: `127.0.0.1`
- Port: `5555`
- Message format: UTF-8 JSON object per datagram

Runtime overrides (environment variables):

- `ENGINE_SIM_UDP_ENABLED` (`1/0`, `true/false`, `on/off`)
- `ENGINE_SIM_UDP_HOST` (default `127.0.0.1`)
- `ENGINE_SIM_UDP_PORT` (default `5555`)

## Current Payload

```json
{
  "schema_version": 1,
  "timestamp_ms": 285247538,
  "frame": 16185,
  "engine": {
    "rpm": 0.0,
    "throttle": 1.0,
    "manifold_pressure": 101324.629,
    "intake_afr": 13.339,
    "exhaust_o2": 0.000032,
    "combustion_temp_c": 86.2,
    "intake_temp_c": 24.8
  }
}
```

## Field Definitions

- `schema_version` (`int`)
  - Current value: `1`.
  - Used by receivers for compatibility checks.
- `timestamp_ms` (`uint64`)
  - Monotonic timestamp from app process (`steady_clock` milliseconds).
- `frame` (`uint64`)
  - Broadcast frame counter incremented once per app frame.
- `engine.rpm` (`float`)
  - Engine speed in RPM.
- `engine.throttle` (`float`)
  - Throttle command/position ratio (`0.0` to `1.0` typical).
- `engine.manifold_pressure` (`float`)
  - Absolute intake manifold pressure in Pascals (Pa).
- `engine.intake_afr` (`float`)
  - Intake air-fuel ratio estimate from sim model.
- `engine.exhaust_o2` (`float`)
  - Exhaust oxygen mass fraction estimate (`0.0` to `1.0` typical).
- `engine.combustion_temp_c` (`float`)
  - Average combustion chamber gas temperature converted to Celsius.
- `engine.intake_temp_c` (`float`)
  - Average intake plenum gas temperature converted to Celsius.

## Notes

- UDP delivery is best-effort; packet loss is acceptable for this telemetry stage.
- No ordering guarantees beyond local receiver observation.
- Values may be zero while engine is not running.
- `exhaust_o2` can show tiny non-zero residual values at idle/transition due to simulation numerical settling.

## Receiver

Use:

```bash
python Source/Phase-01-EngineSimPatch/python-bridge/socket_receiver.py
python Source/Phase-01-EngineSimPatch/python-bridge/signal_generator.py --sink stub
python Source/Phase-01-EngineSimPatch/python-bridge/signal_generator.py --sink csv --csv-path logs/signal_targets.csv
python Source/Phase-01-EngineSimPatch/python-bridge/signal_generator.py --sink pi
```

Bridge mapping config:

- `Source/Phase-01-EngineSimPatch/python-bridge/bridge_config.json`
- Controls TPS/MAP voltage mapping, lambda limits, O2 narrowband voltages, and smoothing alpha.
- Also controls Pi hardware backend behavior (`mock_on_missing`, I2C/SPI params).
- Also controls NTC model used for ECT/IAT resistance targets.
