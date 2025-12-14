---
paths:
  - "tests/**"
  - "src/**"
---
# Testing Rules

## Test Requirements
- All new features require tests
- Minimum 80% code coverage target
- Use pytest with `-v` flag

## Testing Patterns
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific domain
python -m pytest tests/ -v -k "swim"
python -m pytest tests/ -v -k "adhd"

# With coverage
python -m pytest tests/ --cov=src --cov-report=term
```

## Mock External Services
- Mock SwimCloud API for swim tests
- Mock Supabase for database tests
- Use fixtures for common test data

## Test Categories
- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- ADHD workflow tests: `tests/adhd/`
- Swim tracking tests: `tests/swim/`
