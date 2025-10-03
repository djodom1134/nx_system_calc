# Contributing to Nx System Calculator

Thank you for your interest in contributing to the Nx System Calculator! This document provides guidelines and instructions for contributing to this project.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing Requirements](#testing-requirements)
6. [Commit Guidelines](#commit-guidelines)
7. [Pull Request Process](#pull-request-process)
8. [Issue Reporting](#issue-reporting)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. We expect all participants to:

- Be respectful and considerate
- Accept constructive criticism gracefully
- Focus on what is best for the project
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling, insulting, or derogatory remarks
- Publishing others' private information
- Any conduct that would be inappropriate in a professional setting

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python 3.11+** installed
- **Node.js 20 LTS+** installed
- **Git** configured with your name and email
- **Docker** and Docker Compose (for testing)
- A **GitHub account**

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/nx_system_calc.git
   cd nx_system_calc
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/networkoptix/nx_system_calc.git
   ```

### Setup Development Environment

```bash
# Setup script handles everything
./run.sh setup

# Or manually:
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

---

## Development Workflow

### Branch Naming Convention

Use descriptive branch names following this pattern:

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Urgent production fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test additions/improvements

**Examples:**
```bash
git checkout -b feature/add-h265-codec-support
git checkout -b bugfix/fix-raid-calculation-error
git checkout -b docs/update-api-documentation
```

### Keep Your Fork Updated

```bash
# Fetch upstream changes
git fetch upstream

# Merge into your local main
git checkout main
git merge upstream/main

# Push to your fork
git push origin main
```

---

## Coding Standards

### Python (Backend)

**Style Guide:** PEP 8

**Tools:**
- **Formatter**: `black` (line length: 100)
- **Linter**: `flake8`
- **Type Checker**: `mypy`
- **Import Sorter**: `isort`

**Run before committing:**
```bash
cd backend
black app/
flake8 app/
mypy app/
isort app/
```

**Code Conventions:**
- Use type hints for all function signatures
- Write docstrings for all public functions/classes
- Keep functions focused and under 50 lines
- Use meaningful variable names
- Avoid magic numbers (use constants)

**Example:**
```python
from typing import List
from pydantic import BaseModel

def calculate_storage(
    cameras: int,
    bitrate_mbps: float,
    retention_days: int
) -> float:
    """
    Calculate total storage required in TB.
    
    Args:
        cameras: Number of cameras
        bitrate_mbps: Average bitrate per camera in Mbps
        retention_days: Retention period in days
    
    Returns:
        Total storage in terabytes
    """
    HOURS_PER_DAY = 24
    SECONDS_PER_HOUR = 3600
    BITS_TO_TB = 8 * 1024 * 1024 * 1024 * 1024
    
    total_bits = cameras * bitrate_mbps * retention_days * HOURS_PER_DAY * SECONDS_PER_HOUR
    return total_bits / BITS_TO_TB
```

### TypeScript/React (Frontend)

**Style Guide:** Airbnb JavaScript Style Guide

**Tools:**
- **Formatter**: Prettier
- **Linter**: ESLint
- **Type Checker**: TypeScript

**Run before committing:**
```bash
cd frontend
npm run lint
npm run format
npx tsc --noEmit
```

**Code Conventions:**
- Use functional components with hooks
- Prefer `const` over `let`, avoid `var`
- Use TypeScript interfaces for props
- Keep components under 200 lines
- Extract reusable logic into custom hooks

**Example:**
```typescript
interface CalculationResultsProps {
  servers: number;
  storage: number;
  bandwidth: number;
}

export const CalculationResults: React.FC<CalculationResultsProps> = ({
  servers,
  storage,
  bandwidth,
}) => {
  return (
    <div className="results-panel">
      <h2>Calculation Results</h2>
      <div>Servers Required: {servers}</div>
      <div>Total Storage: {storage.toFixed(2)} TB</div>
      <div>Bandwidth: {bandwidth.toFixed(1)} Mbps</div>
    </div>
  );
};
```

---

## Testing Requirements

### Backend Tests

**Minimum Requirements:**
- ✅ Test coverage ≥ 85%
- ✅ Mutation score ≥ 70%
- ✅ All tests pass
- ✅ No security vulnerabilities

**Run tests:**
```bash
cd backend
pytest --cov=app --cov-report=term-missing
pytest --cov=app --cov-report=html  # Generate HTML report
```

**Writing Tests:**
```python
import pytest
from app.services.calculations.storage import calculate_storage

def test_calculate_storage_basic():
    """Test basic storage calculation."""
    result = calculate_storage(
        cameras=100,
        bitrate_mbps=2.5,
        retention_days=30
    )
    assert result > 0
    assert isinstance(result, float)

def test_calculate_storage_zero_cameras():
    """Test storage calculation with zero cameras."""
    result = calculate_storage(
        cameras=0,
        bitrate_mbps=2.5,
        retention_days=30
    )
    assert result == 0

@pytest.mark.parametrize("cameras,expected_range", [
    (10, (0.5, 2.0)),
    (100, (5.0, 20.0)),
    (1000, (50.0, 200.0)),
])
def test_calculate_storage_ranges(cameras, expected_range):
    """Test storage calculation ranges."""
    result = calculate_storage(cameras, 2.5, 30)
    assert expected_range[0] <= result <= expected_range[1]
```

### Frontend Tests

**Run tests:**
```bash
cd frontend
npm test
npm run test:coverage
```

**Writing Tests:**
```typescript
import { render, screen } from '@testing-library/react';
import { CalculationResults } from './CalculationResults';

describe('CalculationResults', () => {
  it('renders server count correctly', () => {
    render(<CalculationResults servers={2} storage={10.5} bandwidth={245.3} />);
    expect(screen.getByText(/Servers Required: 2/i)).toBeInTheDocument();
  });

  it('formats storage with 2 decimal places', () => {
    render(<CalculationResults servers={2} storage={10.567} bandwidth={245.3} />);
    expect(screen.getByText(/Total Storage: 10.57 TB/i)).toBeInTheDocument();
  });
});
```

---

## Commit Guidelines

### Commit Message Format

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(calculator): add H.265 codec support

Implement H.265 codec calculations with improved compression ratios.
Includes updated bitrate formulas and test coverage.

Closes #123
```

```
fix(storage): correct RAID 6 overhead calculation

RAID 6 overhead was incorrectly calculated at 33% instead of 50%.
Updated formula and added regression tests.

Fixes #456
```

### Pre-commit Hooks

Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

This automatically runs:
- Code formatting
- Linting
- Type checking
- Test suite

---

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass locally
- [ ] Test coverage ≥ 85%
- [ ] Documentation updated (if needed)
- [ ] Commit messages follow convention
- [ ] Branch is up-to-date with main

### Submitting a Pull Request

1. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request** on GitHub:
   - Use a clear, descriptive title
   - Reference related issues
   - Describe changes in detail
   - Add screenshots for UI changes

3. **PR Template:**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Related Issues
   Closes #123
   
   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Integration tests pass
   - [ ] Manual testing completed
   
   ## Screenshots (if applicable)
   [Add screenshots here]
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Comments added for complex code
   - [ ] Documentation updated
   - [ ] No new warnings generated
   - [ ] Tests added and passing
   ```

### Review Process

1. **Automated Checks**: CI pipeline must pass
2. **Code Review**: At least one approval required
3. **Testing**: QA team may test changes
4. **Approval**: Maintainer approves and merges

### After Merge

- Delete your feature branch
- Update your local main branch
- Close related issues

---

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Describe the bug**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen

**Screenshots**
If applicable, add screenshots

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Browser: [e.g., Chrome 120]
- Version: [e.g., 1.0.0]

**Additional context**
Any other relevant information
```

### Feature Requests

Use the feature request template:

```markdown
**Is your feature request related to a problem?**
Description of the problem

**Describe the solution you'd like**
Clear description of desired functionality

**Describe alternatives you've considered**
Alternative solutions or features

**Additional context**
Mockups, examples, or references
```

---

## Questions?

- **Email**: dev@networkoptix.com
- **Slack**: #nx-calculator-dev
- **GitHub Discussions**: https://github.com/networkoptix/nx_system_calc/discussions

---

**Thank you for contributing to Nx System Calculator!** 🎉

