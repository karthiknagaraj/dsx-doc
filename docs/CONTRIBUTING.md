# Contributing Guide

Welcome! This guide will help you contribute to the DSX Documentation Assistant project.

---

## Code of Conduct

- Be respectful and inclusive
- Welcome diverse perspectives
- Focus on constructive feedback
- Report issues privately if necessary

---

## Getting Started

### 1. Set Up Development Environment

```powershell
# Clone repository
git clone https://github.com/YOUR-USERNAME/dsx-doc-assistant.git
cd dsx-doc-assistant

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies (includes dev tools)
pip install -r requirements.txt
pip install pytest pytest-mock

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

**Branch naming convention:**
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

---

## Development Workflow

### Running Tests

```powershell
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_doc_format.py

# Run with coverage
pip install pytest-cov
pytest --cov=. tests/

# View coverage report
pytest --cov=. --cov-report=html tests/
# Open htmlcov/index.html in browser
```

### Code Style

We follow **PEP 8** guidelines:

```powershell
# Install linter
pip install pylint flake8

# Check code style
pylint *.py
flake8 *.py --max-line-length=100

# Auto-format (optional)
pip install black
black *.py
```

**Key style points:**
- Max line length: 100 characters
- Use type hints for functions
- Document functions with docstrings
- Use meaningful variable names

### Testing New Code

```powershell
# Example: Testing a new feature
pytest -v tests/test_new_feature.py

# With coverage threshold
pip install pytest-cov
pytest --cov=. --cov-fail-under=80 tests/
```

Create test file at `tests/test_your_feature.py`:

```python
"""Tests for feature description."""

import pytest
from your_module import your_function


def test_basic_functionality(monkeypatch):
    """Test that feature works correctly."""
    # Arrange
    input_data = {"key": "value"}
    
    # Act
    result = your_function(input_data)
    
    # Assert
    assert result is not None
    assert "expected" in result


def test_error_handling():
    """Test error cases."""
    with pytest.raises(ValueError):
        your_function(invalid_input)
```

---

## Feature Development

### 1. Identify an Issue

- Check [GitHub Issues](https://github.com/YOUR-USERNAME/dsx-doc-assistant/issues)
- Create new issue if feature doesn't exist
- Discuss approach with maintainers

### 2. Implement Feature

**Example structure:**

```python
"""Module: New feature for DSX assistant.

This module provides functionality to [describe what it does].

Examples:
    Basic usage:
    
    >>> from new_module import new_function
    >>> result = new_function(input_data)
    >>> print(result)
"""

from typing import Dict, Any, List


def new_function(data: Dict[str, Any]) -> str:
    """Generate output from input data.
    
    Args:
        data: Input dictionary with keys 'x' and 'y'
    
    Returns:
        Formatted string output
    
    Raises:
        ValueError: If required keys missing
    
    Examples:
        >>> new_function({'x': 1, 'y': 2})
        'Result: 3'
    """
    if 'x' not in data or 'y' not in data:
        raise ValueError("Missing required keys: 'x' or 'y'")
    
    result = data['x'] + data['y']
    return f"Result: {result}"
```

### 3. Write Tests

```python
"""Tests for new_module."""

import pytest
from new_module import new_function


def test_new_function_basic():
    """Test basic functionality."""
    result = new_function({'x': 1, 'y': 2})
    assert result == "Result: 3"


def test_new_function_missing_key():
    """Test missing key error."""
    with pytest.raises(ValueError, match="Missing required keys"):
        new_function({'x': 1})
```

### 4. Document Feature

Add docstring and examples to:
- Function docstrings (see example above)
- [USAGE.md](docs/USAGE.md) - User-facing documentation
- [API_REFERENCE.md](docs/API_REFERENCE.md) - Technical reference
- Update [README.md](README.md) if appropriate

### 5. Create Pull Request

```bash
# Commit changes
git add .
git commit -m "feat: Add new feature for X functionality"

# Push branch
git push origin feature/your-feature-name

# Create PR on GitHub with:
# - Description of changes
# - Related issue number (fixes #123)
# - Testing information
# - Screenshots if UI changes
```

---

## Commit Message Convention

Follow these patterns:

```
feat: Add new feature
bugfix: Fix specific issue
docs: Update documentation
refactor: Improve code structure
test: Add or update tests
chore: Update dependencies
```

Examples:

```
feat: Add batch processing with multiple workers
bugfix: Fix API timeout issue when generating large docs
docs: Add installation guide
refactor: Extract LLM logic to separate module
```

---

## Pull Request Process

### Before Submitting

- [ ] Tests pass: `pytest tests/`
- [ ] Code style checked: `flake8 *.py`
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] Branch is up-to-date with main: `git pull origin main`

### PR Template

```markdown
## Description
Briefly describe your changes and why.

## Related Issue
Closes #123

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Testing
Describe tests added/modified:
- [ ] Unit tests added
- [ ] Integration tests passed
- [ ] Manual testing completed

## Screenshots (if UI changes)
[Add screenshots]

## Checklist
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No new warnings generated
```

---

## Areas for Contribution

### Documentation Improvements
- Clarify existing docs
- Add missing examples
- Fix typos
- Expand troubleshooting guides

### Feature Requests
- New DSX element types
- Additional output formats (PDF, HTML)
- Enhanced semantic search
- Integration with other tools

### Bug Fixes
- Report with minimal reproduction
- Propose fix if you have one
- Test fixes thoroughly

### Performance
- Identify bottlenecks
- Optimize parsing/generation
- Reduce memory usage
- Cache improvements

### Testing
- Add missing test coverage
- Create integration tests
- Test edge cases
- Test error scenarios

---

## Development Tips

### Quick Test Run

```powershell
# Create test DSX file
$testDsx = "tests/sample.dsx"

# Test parsing
python -c "
from dsx_to_canonical import parse_dsx_file
data = parse_dsx_file('$testDsx')
print(f'Jobs: {len(data[\"jobs\"])}')
"

# Test documentation
python -c "
from doc_generator import generate_job_docs, load_chat_config
from dsx_to_canonical import parse_dsx_file
cfg = load_chat_config()
data = parse_dsx_file('$testDsx')
md, meta = generate_job_docs(data, '', cfg)
print(f'Generated {len(md)} chars, used {meta[\"tokens_used\"]} tokens')
"
```

### Debug Mode

```python
# Enable verbose logging
import os
os.environ['DEBUG'] = '1'

# Add debug prints
def my_function(x):
    print(f"DEBUG: Input = {x}")
    result = process(x)
    print(f"DEBUG: Output = {result}")
    return result
```

### IDE Setup (VSCode)

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestPath": "${workspaceFolder}/venv/bin/pytest",
    "[python]": {
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    }
}
```

---

## Release Process

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- Major.Minor.Patch (e.g., 1.2.3)
- Major: Breaking changes
- Minor: New features
- Patch: Bug fixes

### Creating a Release

1. Update version in files:
   - `README.md`
   - `setup.py` (if exists)
   - Top of main modules

2. Update `CHANGELOG.md`:
   ```markdown
   ## [1.2.0] - 2025-03-24
   ### Added
   - New feature X
   - New feature Y
   
   ### Fixed
   - Bug fix A
   - Bug fix B
   ```

3. Create Git tag:
   ```bash
   git tag -a v1.2.0 -m "Release version 1.2.0"
   git push origin v1.2.0
   ```

4. Create GitHub Release with release notes

---

## Getting Help

- **Questions**: Create a discussion in GitHub Discussions
- **Bugs**: Open an issue with reproduction steps
- **Features**: Open issue to discuss before implementing
- **Code Review**: Comment on PR with specific feedback

---

## Recognition

Contributors are recognized in:
- [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Release notes
- GitHub contributors page

Thank you for contributing! 🎉

