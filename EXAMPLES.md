# Examples & Real-World Workflows

Practical examples of using `py` for common Python development scenarios.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Web Development](#web-development)
3. [Data Science](#data-science)
4. [CLI Tools](#cli-tools)
5. [CI/CD Integration](#cicd-integration)
6. [Complex Scenarios](#complex-scenarios)

---

## Quick Start

### One-Minute Setup

```bash
# Create a new project
mkdir my-project && cd my-project
py init

# Add a popular package
py add requests

# Create a simple script
cat > fetch.py << 'EOF'
import requests
resp = requests.get('https://api.github.com')
print(resp.status_code)
EOF

# Run it
py fetch.py
# Output: 200
```

### Script Execution Shorthand

```bash
# These are equivalent:
py run main.py arg1 arg2
py main.py arg1 arg2               # Shorthand (faster to type)
```

---

## Web Development

### Flask Web Server

```bash
# Initialize
py init

# Add Flask and extensions
py add flask flask-cors flask-sqlalchemy

# Create app.py
cat > app.py << 'EOF'
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/users')
def get_users():
    return jsonify([
        {'id': 1, 'name': 'Alice'},
        {'id': 2, 'name': 'Bob'},
    ])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
EOF

# Run the server
py app.py
```

**Output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Django Project Setup

```bash
# Initialize
py init

# Add Django and common extensions
py add django djangorestframework django-cors-headers python-env

# Create Django project
py django-admin startproject myproject .
py django-admin startapp myapp

# Run development server
py manage.py runserver 8000
```

### FastAPI Server

```bash
# Initialize
py init

# Add FastAPI and server
py add fastapi uvicorn

# Create main.py
cat > main.py << 'EOF'
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
EOF

# Run server
py -m uvicorn main:app --reload
```

### Testing with pytest

```bash
# Add pytest
py add pytest pytest-cov

# Create tests/test_app.py
mkdir tests
cat > tests/test_app.py << 'EOF'
def test_addition():
    assert 1 + 1 == 2

def test_string():
    assert "hello".upper() == "HELLO"
EOF

# Run tests
py -m pytest tests/ -v --cov

# Output:
# tests/test_app.py::test_addition PASSED
# tests/test_app.py::test_string PASSED
# ======================== 2 passed in 0.02s ========================
```

---

## Data Science

### Jupyter Notebooks

```bash
# Initialize
py init

# Add data science stack
py add jupyter pandas numpy scikit-learn matplotlib

# Start Jupyter
py -m jupyter notebook

# Now use in browser: http://localhost:8888
```

**Inside notebook:**
```python
import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('data.csv')
print(df.head())

# Analysis
print(df.describe())
```

### Pandas Data Pipeline

```bash
# Initialize
py init

# Add pandas, sqlalchemy
py add pandas sqlalchemy openpyxl

# Create pipeline.py
cat > pipeline.py << 'EOF'
import pandas as pd

# Read
df = pd.read_csv('raw_data.csv')

# Transform
df['name'] = df['name'].str.upper()
df['age'] = pd.to_numeric(df['age'], errors='coerce')
df = df.dropna()

# Write
df.to_csv('clean_data.csv', index=False)
print(f"Processed {len(df)} rows")
EOF

# Run
py pipeline.py
# Output: Processed 1000 rows
```

### Machine Learning Model

```bash
# Initialize
py init

# Add ML stack
py add scikit-learn pandas numpy matplotlib

# Create model.py
cat > train_model.py << 'EOF'
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle

# Load data
df = pd.read_csv('data.csv')
X = df.drop('target', axis=1)
y = df['target']

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Evaluate
pred = model.predict(X_test)
acc = accuracy_score(y_test, pred)
print(f"Accuracy: {acc:.2%}")

# Save
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)
EOF

# Run
py train_model.py
# Output: Accuracy: 92.34%
```

---

## CLI Tools

### Click-based CLI

```bash
# Initialize
py init

# Add Click
py add click

# Create cli.py
cat > cli.py << 'EOF'
import click

@click.group()
def cli():
    """My CLI tool"""
    pass

@cli.command()
@click.option('--name', prompt='Your name', help='Name to greet')
def hello(name):
    """Say hello"""
    click.echo(f"Hello {name}!")

@cli.command()
@click.argument('files', nargs=-1, required=True)
def count(files):
    """Count lines in files"""
    for f in files:
        with open(f) as fp:
            lines = len(fp.readlines())
            click.echo(f"{f}: {lines} lines")

if __name__ == '__main__':
    cli()
EOF

# Run
py cli.py hello --name Alice
# Output: Hello Alice!

py cli.py count file1.txt file2.txt
# Output:
# file1.txt: 42 lines
# file2.txt: 100 lines
```

### Argument Parser Tool

```bash
# Initialize
py init

# Create tool.py
cat > tool.py << 'EOF'
import argparse
import sys

parser = argparse.ArgumentParser(description='Image converter')
parser.add_argument('input', help='Input image file')
parser.add_argument('--format', choices=['png', 'jpg', 'webp'], default='png')
parser.add_argument('--quality', type=int, default=85)

args = parser.parse_args()
print(f"Converting {args.input} to {args.format} (quality: {args.quality})")
EOF

# Run
py tool.py image.jpg --format webp --quality 90
# Output: Converting image.jpg to webp (quality: 90)
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Test and Lint

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.11', '3.13']
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install py
        run: pip install .../py
      
      - name: Initialize project
        run: py init
      
      - name: Add dependencies
        run: py add pytest pytest-cov pylint mypy
      
      - name: Run tests
        run: py -m pytest tests/ --cov
      
      - name: Run linter
        run: py -m pylint src/
      
      - name: Type check
        run: py -m mypy src/
      
      - name: Save snapshot
        if: success()
        run: py snapshot save ci-run-${{ github.run_id }}
      
      - name: Check for regressions
        run: py snapshot compare ci-run-${{ github.run_id }}
```

### Reproducible Environments with Snapshots

```bash
# Before running tests, save baseline
py snapshot save test-baseline

# Run tests (might install new packages temporarily)
py -m pytest tests/

# Verify environment didn't change unexpectedly
py snapshot compare test-baseline
```

### Multi-Stage Build with Docker

```dockerfile
FROM python:3.11 AS base
WORKDIR /app
RUN pip install .../py

# Stage 1: Development
FROM base AS dev
COPY . .
RUN py init && py add -r requirements-dev.txt
CMD ['py', 'run', 'app.py']

# Stage 2: Production
FROM base AS prod
COPY . .
RUN py init && py add -r requirements.txt
RUN py cache prune  # Clean cache before image
CMD ['py', 'run', 'app.py']
```

---

## Complex Scenarios

### Recovering from Broken State

```bash
# Your project is broken somehow
$ py run main.py
✗ Module not found: flask

# Diagnose
$ py doctor
✗ pyproject.toml syntax error
✓ Virtual environment exists
⚠ Lock file differs from declared dependencies

# Auto-fix
$ py fix
✓ Fixed pyproject.toml
✓ Created lock file
✓ Fixed 2 issue(s)

# Verify
$ py doctor
✓ everything looks healthy

# Run again
$ py run main.py
# Success!
```

### Dependency Conflict Resolution

```bash
# You try to add conflicting packages
$ py add flask==2.0 flask>=3.0
✓ Added flask==2.0
✓ Added flask>=3.0

# But when you check:
$ py check
✗ Dependency conflict found:
  flask
    - flask==2.0
    - flask>=3.0
  (can't satisfy both constraints)

# Fix by removing one
$ py remove "flask==2.0"
✓ Removed flask==2.0

# Verify
$ py check
✓ No dependency conflicts detected

# Try again
$ py add flask>=3.0
✓ Added flask>=3.0
```

### Auditing Before Deployment

```bash
# Check what's outdated
$ py audit
Found 3 outdated package(s):
  requests      2.28.0         → 2.32.5
  flask         3.0.0          → 3.1.3
  click         8.1.0          → 8.1.7

# Decide: update critical packages only
$ py upgrade requests click

# Verify no new conflicts
$ py check
✓ No dependency conflicts detected

# Audit again to confirm
$ py audit
Found 1 outdated package(s):
  flask         3.0.0          → 3.1.3

# Decide to skip non-critical updates
$ py snapshot save production-ready

# Deploy with confidence
```

### Parallel Development Workflows

```bash
# Team member A: working on feature-auth
$ cd myproject-auth
$ py init
$ py add flask flask-jwt

# Team member B: working on feature-api
$ cd myproject-api
$ py init
$ py add flask flask-restx

# Each has isolated .venv, no conflicts
# Both can coexist on same machine

# Later: merge requirements
$ cd myproject
$ py init
$ py add flask flask-jwt flask-restx
$ py doctor
✓ everything looks healthy
```

### Progressive Dependency Upgrade

```bash
# Current state
$ py list
Dependencies:
  • requests==2.28.0
  • flask==3.0.0

# Snapshot before changes
$ py snapshot save before-upgrade

# Try upgrading one package
$ py upgrade requests
Successfully installed requests-2.32.5

# Test thoroughly
$ py -m pytest tests/ -v --cov

# All tests pass! Save new snapshot
$ py snapshot save requests-upgraded

# Next, try flask (riskier upgrade)
$ py upgrade flask
Successfully installed flask-3.1.3

# Test again
$ py -m pytest tests/ -v --cov

# If fails: rollback by re-running with old versions
$ py remove flask
$ py add flask==3.0.0  # Downgrade

# Investigate issue, then try again with intermediate version
```

### Development vs. Production Dependencies

**pyproject.toml:**
```toml
[project]
name = "myapp"
dependencies = [
    "flask>=3.0",
    "sqlalchemy>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-cov",
    "black",
    "pylint",
]
```

**Development setup:**
```bash
py init
py add flask sqlalchemy pytest pytest-cov black pylint
```

**Production setup:**
```bash
py init
py add flask sqlalchemy  # Only production deps
```

### CI Environment Snapshots

```bash
#!/bin/bash
# ci-setup.sh

# Initialize clean environment
py init
py add pytest coverage black

# Save baseline before running tests
py snapshot save ci-baseline

# Run tests
py -m pytest tests/ --cov

# Verify environment stability
# (no surprise packages installed during test)
py snapshot compare ci-baseline
```

**Usage in CI/CD:**
```yaml
- name: Setup CI
  run: bash ci-setup.sh

- name: Run Tests
  run: py -m pytest tests/

- name: Verify Environment
  run: py snapshot compare ci-baseline
```

---

## Tips & Best Practices

### 1. Always Initialize First
```bash
py init  # Required before anything else
```

### 2. Check Health Regularly
```bash
py doctor  # Before committing
py audit   # Weekly for security
py check   # Before deploying
```

### 3. Save Snapshots at Key Points
```bash
py snapshot save before-refactor
# ... make changes ...
py run tests.py
# If everything works:
py snapshot save after-refactor
```

### 4. Use Snapshots in CI
```yaml
- run: py snapshot save ci-baseline
- run: py -m pytest tests/
- run: py snapshot compare ci-baseline  # Ensure reproducibility
```

### 5. Keep Dependencies Minimal
```bash
# Add only what you need
py add flask              # ✓ Good
py add flask mysql-connector  # ✓ Only if you use MySQL

# Avoid over-specification
py add "flask"            # ✓ Let pip find compatible version
py add "flask==3.1.2"     # Only if you have specific reason
```

### 6. Audit Before Deploying
```bash
py audit                  # Check for outdated/vulnerable packages
py check                  # Check for conflicts
py doctor                 # Run full diagnostics
py snapshot save prod-checkpoint  # Archive state
```

### 7. Interactive Development
```bash
# Use shell for exploration
py shell
(.venv) $ python
>>> import requests
>>> requests.__version__
'2.32.5'
```

---

## Troubleshooting Examples

### "ModuleNotFoundError" When Running Script

```bash
$ py run myapp.py
Traceback (most recent call last):
  File "myapp.py", line 1, in <module>
    import requests
ModuleNotFoundError: No module named 'requests'

# Solution: add the dependency
$ py add requests

$ py run myapp.py
# Works now!
```

### "Permission Denied" on Script  

```bash
$ py myscript.py
/bin/sh: myscript.py: Permission denied

# Solution: use 'run' verb
$ py run myscript.py
# Or make it executable:
$ chmod +x myscript.py
$ py myscript.py
```

### "Lock File Out of Sync"

```bash
$ py lock-diff
In lock file but not installed (2):
  - old-pkg (1.0.0)

# Solution: update lock
$ py add ...           # Add new packages (auto-updates lock)
# Or manually resync:
$ py remove old-pkg    # if it's not needed
```

### Project Won't Initialize

```bash
$ py init
✗ Can't create .venv

# Solution: check Python version
$ python3 --version
Python 3.7.0

# Upgrade Python (3.8+ required)
$ pyenv install 3.13.0
$ eval "$(pyenv init -)"
$ py init
# Works now!
```

---

## More Examples?

For additional examples or to contribute your own, see:
- [GitHub Discussions](https://github.com/Antonymwangi20/py/discussions)
- [Examples Directory](https://github.com/Antonymwangi20/py/tree/main/examples)
