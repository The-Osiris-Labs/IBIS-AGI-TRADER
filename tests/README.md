# Test Suite

Comprehensive testing infrastructure for IBIS.

## Directory Structure

- **unit/** - Unit tests for core components
- **diagnostics/** - Diagnostic and debugging scripts
- **sandbox/** - Experimental and testing scripts
- **integration/** - Integration tests

## Running Tests

```bash
# Run all tests
python3 -m pytest tests/

# Run unit tests only
python3 -m pytest tests/unit/

# Run specific diagnostic
python3 tests/diagnostics/check_system.py
```

## Writing Tests

Follow the existing patterns:
1. Use pytest for unit tests
2. Name diagnostic scripts clearly (check_*, verify_*, diagnose_*)
3. Document what each test validates
4. Keep tests isolated and reproducible
