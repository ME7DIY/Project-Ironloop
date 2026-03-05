# Project IRONLOOP
## Hardware-in-the-Loop Engine Control Unit Simulation

> A DIY Hardware-in-the-Loop simulation rig bridging open-source combustion simulation to a real Bosch ME7.5 engine control unit via direct pin-level signal injection.

![Status](https://img.shields.io/badge/status-in%20development-yellow)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Hardware](https://img.shields.io/badge/hardware-Raspberry%20Pi%205%20%2F%20Pico-red)

---

## 🎯 The Vision

IRONLOOP is an open-source, budget-friendly Hardware-in-the-Loop (HIL) platform that lets you:

- **Run a virtual engine** in real-time using [engine-sim](https://github.com/ange-yaghi/engine-sim)
- **Feed simulated sensor signals** directly into a real Bosch ME7.5 ECU
- **Read back ECU decisions** (fuel timing, ignition advance) into the simulation
- **Create a closed-loop system** where the virtual engine behaves like a real car

Professional HIL rigs cost **$100k+**. This version costs under **$200**.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Hardware Stack](#hardware-stack)
- [Build Phases](#build-phases)
- [Getting Started](#getting-started)
- [Sensors & Signals](#sensors--signals)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [License](#license)

---

## 🔧 Project Overview

### The Loop

```
engine-sim (Virtual Engine)
    ↓ [RPM, Throttle, MAP, Temps, Lambda...]
Python Bridge (Pi 5)
    ↓ [Voltage Conversion]
Signal Boards (DAC + Digital Pot)
    ↓ [0–5V Analog + Resistance Values]
Pico PIO (60-2 Crank Generator)
    ↓ [Hard Real-Time Digital Pulses]
Bosch ME7.5 ECU (Real Hardware)
    ↓ [Fuel Timing, Ignition Advance, Idle Control...]
ECU Output Decoder (K-Line / GPIO)
    ↓ [Injector PW, Ignition Angle]
Back to engine-sim → Loop Closes ↻
```

The entire system runs at ~60 Hz, giving the ECU a live virtual engine to control.

---

## 💰 Hardware Stack

| Component | Part | Cost |
|-----------|------|------|
| **Main Processor** | Raspberry Pi 5 (8GB) | ~$80 |
| **Crank/Cam Generator** | Raspberry Pi Pico | ~$4 |
| **Quad DAC** | MCP4728 I2C Breakout | ~$10 |
| **Digital Pot** | MCP4131 SPI Breakout | ~$8 |
| **ECU Interface** | VAG-KKL 409.1 USB K-Line Cable | ~$8 |
| **ECU Harness** | ME7.5 121-pin Connector + Bench Wiring | ~$15 |
| **Test Equipment** | Pomona Minigrabber Clips + Logic Analyzers | ~$20 |
| **Power Supply** | Old ATX PSU + Bench Breakout | ~$10 |
| | **TOTAL** | **~$155** |

---

## 🏗️ Build Phases

### **Phase 01: Patch engine-sim — State Output** (1–2 Weekends)
- Fork engine-sim and add local UDP/TCP socket broadcast
- Emit engine state (RPM, throttle, MAP, temps, lambda) as JSON every frame
- Build Python test receiver to validate data stream

**Key Topics:** C++ socket programming, CMake builds, JSON serialization

---

### **Phase 02: Fake Easy Sensors — ECU Powers On** (2–3 Weekends)
- Wire MCP4728 DAC for TPS, MAP, MAF, O2 analog signals
- Wire MCP4131 digital pot for ECT/IAT NTC thermistor emulation
- Get ME7 to boot without sensor fault codes

**Key Topics:** I2C/SPI, analog signal conversion, ME7 pinout, NTC curves, K-Line diagnostics

---

### **Phase 03: Crank & Cam Signal — ECU Runs** (3–6 Weeks)
- Write MicroPython + PIO assembly on Raspberry Pi Pico
- Generate perfect 60-2 crank wheel signal and cam sync pulse at variable RPM
- Level shift 3.3V Pico output to 12V for ECU input
- Verify timing with logic analyzer and oscilloscope
- Get ME7 to actually fire injector drivers

**Key Topics:** Pico PIO, 60-2 tooth patterns, RPM calculations, signal level shifting, real-time constraints

---

### **Phase 04: Close the Loop — ECU Affects Simulation** (4–8 Weeks)
- Read injector pulse width and ignition advance from ME7
- Implement feedback model: ECU decisions → torque changes → RPM in engine-sim
- Tune control loop for stability (PID filtering)
- End-to-end test: blip throttle → RPM climbs → ECU responds → closed loop works

**Key Topics:** K-Line / KWP2000, ECU output decoding, feedback control, PID tuning, torque modeling

---

### **Phase 05: AI Tuning Layer** (Ongoing)
- Log full simulation runs to CSV data
- Build custom OpenAI Gym environment wrapping the HIL loop
- Train RL agent (PPO via stable-baselines3) to evolve fuel and ignition maps
- Export optimized maps as ME7 ROM for real-world flashing

**Key Topics:** Reinforcement learning, PPO algorithms, ME7 ROM format, Gym environments

---

## 📡 Sensors & Signals

| Signal | Type | Difficulty | Notes |
|--------|------|-----------|-------|
| **TPS** (Throttle) | 0–5V Analog | 🟢 Easy | DAC output |
| **MAP** (Manifold Pressure) | 0–5V Analog | 🟢 Easy | Linear curve |
| **MAF** (Air Flow) | 0–5V Analog | 🟢 Easy | From sim air mass |
| **ECT** (Coolant Temp) | NTC Resistance | 🟢 Easy | Digital pot emulation |
| **IAT** (Intake Temp) | NTC Resistance | 🟢 Easy | Digital pot emulation |
| **O2 / Lambda** | 0–1V Analog | 🟡 Medium | Narrowband behavior |
| **Cam Sync** | Digital Pulse | 🟡 Medium | 1 pulse/cam rev, phase-aligned |
| **Crank — 60-2** | Hard Real-Time Digital | 🔴 Hard | **Sub-millisecond precision; Pico PIO only** |

---

## 🏛️ Architecture

### Component Layout

```
┌─────────────────────────────────────────────────────┐
│  Windows/Linux PC                                   │
│  ├─ engine-sim (C++ Virtual Engine)                 │
│  └─ State JSON → UDP Broadcast :5555                │
└──────────────────┬──────────────────────────────────┘
                   │ UDP Socket
                   ↓
┌─────────────────────────────────────────────────────┐
│  Raspberry Pi 5                                     │
│  ├─ Python Bridge (State Receiver + Signal Gen)     │
│  ├─ I2C Bus → MCP4728 DAC                          │
│  ├─ SPI Bus → MCP4131 Digital Pot                  │
│  ├─ Serial → Pico (RPM commands)                    │
│  └─ K-Line (pyserial) ↔ ME7 Diagnostics            │
└──────────────────┬──────────────────────────────────┘
         │                  │
        I2C               SPI
         │                  │
         ↓                  ↓
    ┌────────────┐    ┌────────────┐
    │ MCP4728    │    │ MCP4131    │
    │ Quad DAC   │    │ Digital    │
    │            │    │ Potentiom. │
    └────────────┘    └────────────┘
         │                  │
    Analog 0–5V      Resistance Values
         │                  │
         └────────┬─────────┘
                  ↓
    ┌──────────────────────────┐
    │  ME7.5 ECU Bench Harness │
    │  (TPS, MAP, MAF,         │
    │   ECT, IAT, O2 pins...)  │
    └──────────────────────────┘
                  ↑
         K-Line Serial Link
                  ↑
    ┌──────────────────────────┐
    │ Pico (Crank/Cam Gen)     │
    │ PIO Assembly → 60-2      │
    │ + Level Shifter          │
    └──────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- **Raspberry Pi 5** (8GB recommended)
- **Raspberry Pi Pico** (or Pico W)
- **MCP4728 DAC breakout**
- **MCP4131 Digital Pot breakout**
- **VAG-KKL 409.1 K-Line USB cable**
- **ME7.5 ECU** + bench harness
- **Windows/Linux PC** running engine-sim
- **Logic Analyzer** & **Oscilloscope** (for debugging)

### Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/ME7DIY/Project-Ironloop.git
   cd Project-Ironloop
   ```

2. **Raspberry Pi 5 Setup:**
   ```bash
   # Enable I2C and SPI
   sudo raspi-config
   # → Interface Options → I2C/SPI → Enable
   
   # Install Python dependencies
   pip install -r requirements.txt
   ```

3. **Fork and Build engine-sim:**
   ```bash
   git clone https://github.com/ange-yaghi/engine-sim.git
   cd engine-sim
   # Patch socket broadcast (see Phase-01 docs)
   cmake . && make
   ```

4. **Flash Pico with MicroPython:**
   - Download [Pico MicroPython firmware](https://micropython.org/download/rp2-pico/)
   - Flash via USB boot mode
   - Install [Adafruit Ampy](https://github.com/adafruit/ampy) or Thonny IDE

5. **Hardware Wiring:**
   - Follow pinout diagrams in `Research/Phase-02-FakeSensors/me7-pinout-pinning/`
   - Connect DAC/Pot outputs to ME7 bench harness
   - Wire Pico 60-2 output through level shifter to ECU crank input

---

## 📂 Directory Structure

```
Project-Ironloop/
├── ME7-HIL-Project.html          # Interactive project overview
├── README.md                      # This file
├── Research/                      # Extensive research & references
│   ├── General-Reference/
│   ├── Phase-01-EngineSimPatch/
│   ├── Phase-02-FakeSensors/
│   ├── Phase-03-CrankCamSignal/
│   ├── Phase-04-CloseLoop/
│   └── Phase-05-AITuning/
├── Software/                      # Python, C++, MicroPython source (TBD)
│   ├── engine-sim-bridge/        # Python receiver & signal generator
│   ├── pico-firmware/            # PIO crank signal generator
│   └── me7-diagnostics/          # K-Line reader / ECU output decoder
├── Hardware/                      # Datasheets, schematics (TBD)
│   ├── schematics/
│   ├── pcb-layouts/
│   └── bom/
└── Docs/                         # Detailed guides & tutorials (TBD)
    ├── phase-guides/
    ├── troubleshooting/
    └── signal-reference/
```

---

## 🔬 Research & Documentation

Extensive research materials are organized by phase in the `Research/` directory:

- **General-Reference/** — ECU fundamentals, ME7 docs, automotive signal standards
- **Phase-01/** — engine-sim architecture, C++ socket programming, JSON serialization
- **Phase-02/** — DAC/pot datasheets, sensor voltage curves, K-Line protocol
- **Phase-03/** — Pico hardware specs, PIO assembly, 60-2 timing, level shifting
- **Phase-04/** — KWP2000, ECU output decoding, PID control, torque modeling
- **Phase-05/** — RL theory, PPO algorithms, stable-baselines3, ME7 ROM format

---

## 🤝 Contributing

We welcome contributions! Whether you're:
- **Fixing bugs** in the control loop
- **Expanding sensor support** (VVT, turbo pressure, knock, etc.)
- **Improving AI tuning algorithms**
- **Adding documentation & guides**
- **Testing hardware configurations**

Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit changes with clear messages
4. Push to your fork
5. Open a Pull Request with detailed description

---

## ⚠️ Safety & Disclaimer

**This is experimental hardware and firmware.** Testing should occur:
- ✅ On a workbench with the ECU isolated from any actual engine
- ✅ In a controlled lab environment
- ✅ With proper test equipment (logic analyzer, oscilloscope, power supplies)
- ✅ With full understanding of ECU timing and safety considerations

**Do not** attempt to use this system on a real running engine without extensive validation and professional guidance. Automotive safety is critical.

---

## 📚 References & Acknowledgments

- **engine-sim** by Ange Yaghi — [https://github.com/ange-yaghi/engine-sim](https://github.com/ange-yaghi/engine-sim)
- **Bosch ME7.5 Community** — nefmoto docs, MPPS, ME7 tuner forums
- **Raspberry Pi Foundation** — Pico PIO, MicroPython documentation
- **Stable Baselines 3** — [https://stable-baselines3.readthedocs.io](https://stable-baselines3.readthedocs.io)

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

**In summary:** You're free to use, modify, and distribute this project, provided you:
- Include the license and copyright notice
- State any changes made
- Don't hold us liable for damages or injuries

---

## 📞 Get Involved

- **GitHub Issues** — Report bugs, request features
- **Discussions** — Ask questions, share knowledge
- **Pull Requests** — Submit code improvements

---

## 🎓 Learning Outcomes

By working through IRONLOOP, you'll master:

✅ **Embedded Systems:**  Real-time signal generation, sensor interfacing, hardware protocols (I2C, SPI, K-Line)

✅ **Automotive Engineering:** ECU architecture, fuel/ignition mapping, sensor signal types, ME7 internals

✅ **Control Systems:** Feedback loops, PID tuning, signal processing, system stability

✅ **Machine Learning:** Reinforcement learning, policy optimization, RL environment design

✅ **Systems Integration:** Multi-process Python applications, inter-chip communication, real-time constraints

✅ **Open-Source Development:** Git workflows, documentation, collaborative engineering

---

**Made with 🔧 and ❤️ by the IRONLOOP Community**

*Last Updated: March 5, 2026*
