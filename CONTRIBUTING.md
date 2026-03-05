# Contributing to IRONLOOP

Thank you for your interest in contributing to Project IRONLOOP! This document outlines guidelines and best practices for contributing to the project.

## Code of Conduct

- Be respectful and inclusive of all contributors
- Provide constructive feedback
- Focus on ideas and code, not individuals
- Help others learn and grow

## Ways to Contribute

### 1. **Bug Reports & Feature Requests**
- Open an issue with a clear title and description
- Include steps to reproduce for bugs
- Suggest use cases for feature requests
- Label issues appropriately (`bug`, `enhancement`, `documentation`, etc.)

### 2. **Code Contributions**
- **Embedded Systems / MicroPython** — Pico firmware, PIO assembly, signal generation
- **Python (Signal Bridge)** — DAC/pot control, K-Line communication, data exchange
- **C++ (engine-sim fork)** — Socket broadcasting, state serialization
- **Control Systems** — Feedback loop tuning, PID optimization
- **Machine Learning** — RL environment design, model training frameworks

### 3. **Documentation**
- Tutorials and guides for each phase
- Wiring diagrams and schematics
- Troubleshooting guides
- API documentation
- Research notes and references

### 4. **Testing & Validation**
- Hardware testing on different configurations
- Signal timing verification with logic analyzers
- ECU compatibility testing
- RL training result documentation

### 5. **Research & Knowledge Base**
- Datasheets and technical papers
- ME7 reverse engineering notes
- Automotive signal standards documentation
- Tuning methodology guides

## Development Workflow

### Setting Up Your Environment

```bash
# 1. Fork the repository on GitHub
# https://github.com/ME7DIY/Project-Ironloop/fork

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/Project-Ironloop.git
cd Project-Ironloop

# 3. Add upstream remote
git remote add upstream https://github.com/ME7DIY/Project-Ironloop.git

# 4. Create a feature branch
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b fix/issue-description
```

### Making Changes

- **Keep commits atomic** — One logical change per commit
- **Write clear commit messages:**
  ```
  [Phase-XX] Brief description of change
  
  Longer explanation if needed. Reference issues with #123.
  ```
- **Test your changes** before pushing
- **Keep code style consistent** — Follow existing patterns in the codebase

### Submitting a Pull Request

1. **Update your fork with latest upstream:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push your feature branch:**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request on GitHub:**
   - Provide a clear title and description
   - Reference related issues with `Fixes #123` or `Related to #456`
   - Include screenshots/videos if applicable (signal captures, test results)
   - List any breaking changes or new dependencies

4. **Respond to review feedback:**
   - Be open to suggestions
   - Discuss design decisions
   - Update your PR accordingly

## Coding Standards

### Python
```python
# Follow PEP 8
# Use type hints for clarity
def read_sensor(adc_pin: int) -> float:
    """Read analog value from ADC pin."""
    pass

# Docstrings for classes and functions
class DACSynth:
    """Synthesizes analog signals via MCP4728 DAC."""
    pass
```

### MicroPython (Pico)
```python
# Concise, efficient code
# Document PIO assembly with comments
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW)
def crank_60_2():
    wrap_target()
    set(pins, 1).side(1)[15]  # tooth high
    set(pins, 0).side(0)[15]  # gap low
    wrap()
```

### C++
```cpp
// Clear, readable code
// Use CMake for builds
class EngineSimBridge {
public:
    void broadcastState(const EngineState& state);
private:
    struct EngineState { /* ... */ };
};
```

## Testing

### Hardware Testing Checklist
- [ ] DAC outputs verified with multimeter
- [ ] Digital pot resistance ranges correct
- [ ] Pico signal timing verified with logic analyzer
- [ ] K-Line communication stable
- [ ] ECU boots and reads sensors
- [ ] Full closed-loop stability test

### Software Testing Checklist
- [ ] Unit tests pass (where applicable)
- [ ] Integration tests with hardware
- [ ] No python syntax errors (`python -m py_compile`)
- [ ] Code follows PEP 8 style (`pylint`, `black`)

## Documentation

### For Code Changes
- Add docstrings to new functions/classes
- Include inline comments for complex logic
- Update README if adding major features

### For Research Materials
- Organize under relevant phase in `Research/`
- Name files descriptively
- Include source references and timestamps
- Add summary comments if submitting PDFs

### For Tutorials
- Place in `docs/` directory
- Use clear step-by-step format
- Include wiring diagrams and code examples
- Test instructions on fresh setup

## Issue Labels

- `bug` — Something isn't working
- `enhancement` — New feature or improvement
- `documentation` — docs, guides, README updates
- `hardware` — Physical components, wiring, PCB design
- `software` — Code, firmware, algorithms
- `research` — Theory, datasheets, reference materials
- `question` — Help or clarification needed
- `Phase-01` / `Phase-02` etc. — Related to specific phases
- `good first issue` — Ideal for new contributors

## Getting Help

- **GitHub Discussions** — Ask questions, brainstorm ideas
- **Issues** — Report bugs, request features
- **Example Code** — Check the `Research/` and `Software/` directories
- **Community** — Reach out to maintainers and contributors

## Recognition

Contributors will be recognized in:
- Project README contributors list
- Commit history
- Release notes (for significant contributions)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping make IRONLOOP better!** 🚀

Questions? Open an issue or start a discussion on GitHub.
