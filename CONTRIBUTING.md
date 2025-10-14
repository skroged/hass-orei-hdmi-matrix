# Contributing to OREI HDMI Matrix Integration

Thank you for your interest in contributing to the OREI HDMI Matrix integration for Home Assistant!

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request, please open an issue on GitHub. When reporting bugs, please include:

- Home Assistant version
- Integration version
- Device model and firmware version
- Steps to reproduce the issue
- Relevant log entries

### Development Setup

1. Fork the repository
2. Clone your fork locally
3. Set up a development environment:

```bash
# Install development dependencies
pip install -r requirements_dev.txt

# Install pre-commit hooks (optional but recommended)
pre-commit install
```

### Code Style

This project follows the Home Assistant coding standards:

- Use `black` for code formatting
- Use `isort` for import sorting
- Use `flake8` for linting
- Use `mypy` for type checking

Run the formatters before committing:

```bash
black custom_components/orei_hdmi_matrix/ tests/
isort custom_components/orei_hdmi_matrix/ tests/
flake8 custom_components/orei_hdmi_matrix/ tests/
mypy custom_components/orei_hdmi_matrix/
```

### Testing

Run the test suite:

```bash
pytest
```

### Submitting Changes

1. Create a feature branch from `main`
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation if needed
6. Submit a pull request

### Pull Request Guidelines

- Keep PRs focused and small when possible
- Include a clear description of changes
- Reference any related issues
- Ensure CI checks pass
- Update CHANGELOG.md for user-facing changes

## Code of Conduct

This project follows the Home Assistant Code of Conduct. Please be respectful and constructive in all interactions.

## Questions?

Feel free to open an issue or discussion if you have questions about contributing!
