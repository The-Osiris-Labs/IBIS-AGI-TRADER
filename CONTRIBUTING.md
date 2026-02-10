# Contributing to IBIS

Thank you for your interest in contributing to IBIS! The following guide will help you get started.

## Development Philosophy

IBIS is built on several core principles:

1. **Intelligent Decision-Making**: Every trade must be justified by strong analysis
2. **Risk Management**: Never risk more capital than is appropriate
3. **Continuous Learning**: The agent must improve from every market cycle
4. **Transparent Code**: Logic should be clear and well-documented
5. **Production Reliability**: Code must be robust and handle edge cases

## Getting Started

### Prerequisites

- Python 3.8+
- KuCoin API account (for testing)
- Virtual environment (recommended)

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/ibis-trader.git
cd ibis-trader

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up API keys
cp ibis/keys.env.example ibis/keys.env
# Edit ibis/keys.env with your KuCoin API keys
```

### Testing Your Changes

```bash
# Paper trading mode (no real money risked)
PAPER_TRADING=true python3 ibis_true_agent.py

# Debug mode with verbose output
DEBUG=true VERBOSE=true python3 ibis_true_agent.py

# Run test suite
python3 -m pytest tests/

# Run specific diagnostic
python3 tests/diagnostics/check_system.py
```

## Code Guidelines

### Style

- Follow PEP 8
- Use type hints for functions
- Write docstrings for public APIs
- Use clear, descriptive variable names
- Keep functions focused and single-purpose

### Trading Logic Changes

When modifying trading logic:

1. **Do not change core parameters** without discussion:
   - Stop loss (5%)
   - Take profit (1.5%)
   - Position limits (5 concurrent)
   - Risk allocation percentages

2. **Preserve learning**: The agent's learned strategies must be maintained

3. **Test thoroughly**:
   - Paper trading for at least 10 cycles
   - Verify position management
   - Check state persistence
   - Validate learning system

4. **Document reasoning**: Explain why the change improves IBIS

### Adding Features

Before adding a feature:

1. Discuss in an issue (feature request)
2. Design the change to fit IBIS philosophy
3. Write tests for new functionality
4. Update documentation
5. Submit PR with clear description

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes with clear commits
3. Test thoroughly (paper trading mode)
4. Update documentation as needed
5. Submit PR with:
   - Clear title and description
   - Link to relevant issue
   - Testing instructions
   - Screenshots/logs if helpful

## Reporting Issues

### Bug Reports

Include:
- Description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System info (OS, Python version, etc.)
- Relevant logs

### Feature Requests

Include:
- Clear description of the feature
- Use cases/benefits
- How it fits IBIS philosophy
- Potential concerns

## Code of Conduct

- Be respectful to all contributors
- Welcome diverse perspectives
- Focus on ideas, not individuals
- Help others learn and improve

## Questions?

- Check existing issues/discussions
- Review documentation in `/docs`
- Look at examples in `/examples`
- Check QUICKREF.md for common tasks

## Acknowledgments

Contributors will be recognized in the project's contributors list and release notes.

Thank you for helping make IBIS better! 🦅
