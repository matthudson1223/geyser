# Contributing to Geyser

Thank you for your interest in contributing to Geyser! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Familiarity with financial analysis concepts

### Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/yourusername/geyser.git
   cd geyser
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

5. **Copy environment template**:
   ```bash
   cp .env.example .env
   ```

## Development Workflow

### Branching Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `hotfix/*`: Urgent fixes for production

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Write tests** for new functionality

4. **Run tests locally**:
   ```bash
   pytest tests/
   ```

5. **Check code quality**:
   ```bash
   black src/ tests/
   isort src/ tests/
   flake8 src/ tests/
   mypy src/
   ```

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: add DCF valuation model
fix: correct P/E ratio calculation for negative earnings
docs: update installation instructions
test: add tests for cache manager
```

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Maximum line length: 100 characters
- Use type hints for function signatures
- Write docstrings for all public functions and classes

### Code Organization

- Keep functions small and focused (< 50 lines)
- Use meaningful variable names
- Avoid deep nesting (max 3 levels)
- Extract complex logic into separate functions

### Documentation

- Add docstrings using Google style:
  ```python
  def calculate_ratio(numerator: float, denominator: float) -> float:
      """
      Calculate a financial ratio.

      Args:
          numerator: The numerator value
          denominator: The denominator value

      Returns:
          The calculated ratio

      Raises:
          ValueError: If denominator is zero
      """
      if denominator == 0:
          raise ValueError("Denominator cannot be zero")
      return numerator / denominator
  ```

## Testing

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use descriptive test names: `test_calculate_ratio_with_valid_inputs`
- Aim for 80%+ code coverage

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_validators.py

# Run specific test
pytest tests/test_validators.py::TestTickerValidation::test_valid_tickers
```

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure all tests pass** and coverage is maintained
4. **Update CHANGELOG.md** with your changes
5. **Create pull request** with clear description:
   - What changes were made
   - Why these changes were needed
   - How to test the changes
   - Any breaking changes

### PR Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows style guide
- [ ] All tests passing
- [ ] No linting errors
- [ ] CHANGELOG.md updated

## Types of Contributions

### Bug Reports

- Use GitHub Issues
- Include: Steps to reproduce, expected behavior, actual behavior
- Provide: Python version, OS, error messages

### Feature Requests

- Use GitHub Issues with "enhancement" label
- Describe: Use case, proposed solution, alternatives considered

### Code Contributions

Welcome contributions:
- Bug fixes
- New financial metrics
- Performance improvements
- Additional data sources
- Documentation improvements
- Test coverage improvements

## Code Review Process

- All PRs require at least one review
- Address review comments promptly
- Maintainers will merge once approved

## Community Guidelines

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Focus on the code, not the person

## Questions?

- Open an issue for questions
- Check existing issues/PRs first
- Be patient and respectful

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
