# py Architecture & Design Document

This document explains the design decisions, system architecture, and implementation details of the `py` tool.

---

## Design Philosophy

### Core Principles

1. **Single File Distribution**
   - No installation complexity (no pip/poetry/setup.py)
   - Easy to audit and verify
   - Simple to update (download new version, replace)
   - Portable across machines

2. **Zero External Dependencies**
   - Only Python 3.8+ stdlib
   - No pip, poetry, or third-party packages needed
   - Faster startup, smaller attack surface
   - Works in isolated environments

3. **Project Isolation**
   - Each project gets a completely isolated `.venv`
   - No global state pollution
   - Multiple projects can coexist
   - Easy cleanup: just remove the project directory

4. **Transparent State**
   - All state stored in plain JSON (not binary)
   - Uses standard `pyproject.toml` format
   - Human-readable lock files
   - Easy debugging: inspect files with `cat`/`jq`

5. **Minimal API Surface**
   - 17 commands total (vs. poetry's 40+)
   - Each command does one thing well
   - Follows Unix philosophy
   - Easy to remember and discover

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────┐
│  User Shell                                         │
│  $ py add flask                                     │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  py Script (Main Dispatcher)                        │
│  • Parse arguments (argparse)                       │
│  • Route to cmd_* handler                           │
│  • Handle signals (SIGINT, SIGTERM)                 │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────┼──────────┬──────────┐
        ▼          ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
   │cmd_add │ │cmd_run │ │cmd_fix │ │cmd_...  │
   └────┬───┘ └────┬───┘ └────┬───┘ └────────┘
        │          │          │
        │          │          │
        ▼          ▼          ▼
   ┌─────────────────────────────────────────┐
   │  State Management Layer                 │
   │  • .py.state.json (declared deps)       │
   │  • .py.lock.json (exact versions)       │
   │  • .py-snapshots/ (env snapshots)       │
   │  • ~/.cache/py/ (global wheel cache)    │
   └─────────────────────────────────────────┘
        │
        ▼
   ┌─────────────────────────────────────────┐
   │  pip & venv (stdlib subprocess calls)   │
   │  • Creates .venv                        │
   │  • Installs packages                    │
   │  • Queries PyPI                         │
   └─────────────────────────────────────────┘
```

### State Layers

#### Layer 1: Declared Dependencies (`.py.state.json`)
```json
{
  "dependencies": [
    "requests>=2.28",
    "flask>=3.0"
  ],
  "python_version": "3.8"
}
```
**What:** Packages you explicitly want  
**Purpose:** Source of truth for project requirements  
**Managed by:** `cmd_add`, `cmd_remove`, `cmd_purge`  
**Versioning:** Git-friendly (human-readable)

#### Layer 2: Locked Versions (`.py.lock.json`)
```json
{
  "dependencies": {
    "requests": "2.32.5",
    "flask": "3.1.3",
    "werkzeug": "3.1.2",
    "click": "8.1.7",
    "itsdangerous": "2.1.2",
    "jinja2": "3.1.4"
  }
}
```
**What:** Exact versions of ALL packages (including transitive deps)  
**Purpose:** Reproducible installs  
**Managed by:** `cmd_add` (auto-generated), `cmd_upgrade`  
**Versioning:** Git-friendly (like requirements.lock)

#### Layer 3: Environment Snapshots (`.py-snapshots/<name>.json`)
```json
{
  "timestamp": "2026-03-15T14:23:45.123456",
  "python_version": "3.13.12",
  "dependencies": ["requests>=2.28", "flask>=3.0"],
  "installed": {
    "requests": "2.32.5",
    "flask": "3.1.3",
    "werkzeug": "3.1.2"
  }
}
```
**What:** Point-in-time capture of env state + metadata  
**Purpose:** CI reproducibility, debugging, rollback  
**Managed by:** `cmd_snapshot`  
**Use case:** Export snapshot to archive, compare in CI

#### Layer 4: Global Cache (`~/.cache/py/`)
```
~/.cache/py/
├── wheels/
│   ├── requests-2.32.5-py3-none-any.whl
│   ├── flask-3.1.3-py3-none-any.whl
│   └── ...
└── metadata
```
**What:** Global pool of downloaded wheels  
**Purpose:** Speed up installs across projects  
**Managed by:** `cmd_cache` (info, prune)  
**Benefit:** Avoid re-downloading flask v3.1.3 for every project

---

## Execution Flow

### Typical Workflow

```
py init
  │
  ├─ Create .venv (python3 -m venv)
  ├─ Initialize .py.state.json (empty deps)
  ├─ Create .gitignore (.venv, .py.lock.json, etc.)
  └─ Print success

py add requests flask
  │
  ├─ Parse dependencies
  ├─ Check for conflicts (cmd_check logic)
  ├─ pip install requests flask --find-links ~/.cache/py
  ├─ Query pip freeze → exact versions
  ├─ Save .py.state.json (update dependencies list)
  ├─ Save .py.lock.json (locked versions)
  └─ Print success

py run main.py --arg
  │
  ├─ Check if state/lock exist
  ├─ Verify .venv matches lock file (skip if matches)
  ├─ Spawn subprocess with VIRTUAL_ENV set
  ├─ Run main.py inside subprocess
  └─ Exit with subprocess's exit code
```

### State Transitions

```
                  ┌─────────┐
                  │  init   │
                  └────┬────┘
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
    ┌──────────┐            ┌──────────┐
    │ add pkg  │            │ shell    │
    │ depends  │            │ (manual) │
    └────┬─────┘            └──────────┘
         │                       
         ▼                       
    ┌──────────┐
    │ upgrade  │
    │ remove   │
    └──────────┘
         │
         ▼
    ┌──────────┐
    │  audit   │──┐
    │  search  │  │
    │  doctor  │  │
    │  check   │  │ (read-only)
    │  list    │  │
    └──────────┘──┘
         │
         ▼
    ┌──────────┐
    │ snapshot │
    │ save     │
    └──────────┘
```

---

## Key Algorithms

### 1. Dependency Conflict Detection

```python
def check_dependency_conflicts(dependencies):
    """
    Find packages with multiple conflicting version specs.
    
    Example:
        ['flask>=3.0', 'flask==2.0']  → conflict!
        ['requests>=2.28', 'requests>=2.30']  → OK (both >=)
    """
    by_package = defaultdict(list)
    
    for dep in dependencies:
        pkg, spec = parse_dep_spec(dep)
        pkg_lower = pkg.lower()
        by_package[pkg_lower].append((pkg, spec))
    
    conflicts = [
        specs for specs in by_package.values()
        if len(specs) > 1
    ]
    
    return conflicts
```

**Time complexity:** O(n) where n = number of dependencies  
**Space complexity:** O(n)  
**When called:** `py add` (before install), `py check` command

### 2. Lock File Validation

```python
def verify_lock_matches(installed, locked):
    """
    Compare installed packages against lock file.
    Returns difference summary.
    """
    missing = set(locked.keys()) - set(installed.keys())
    extra = set(installed.keys()) - set(locked.keys())
    version_diff = {
        pkg: (installed[pkg], locked[pkg])
        for pkg in set(installed.keys()) & set(locked.keys())
        if installed[pkg] != locked[pkg]
    }
    
    return {
        'missing': missing,
        'extra': extra,
        'version_diff': version_diff
    }
```

**Time complexity:** O(n) where n = total packages  
**When called:** `py run` (before each run), `py lock-diff` command

### 3. Environment Comparison (Snapshots)

```python
def compare_snapshot(current_installed, snapshot):
    """
    Compare current environment against saved snapshot.
    """
    added = set(current_installed.keys()) - set(snapshot['installed'].keys())
    removed = set(snapshot['installed'].keys()) - set(current_installed.keys())
    
    changed = {
        pkg: (current_installed[pkg], snapshot['installed'][pkg])
        for pkg in set(current_installed.keys()) & set(snapshot['installed'].keys())
        if current_installed[pkg] != snapshot['installed'][pkg]
    }
    
    return {
        'added': added,
        'removed': removed,
        'changed': changed
    }
```

**Time complexity:** O(n)  
**When called:** `py snapshot compare` command

---

## Error Handling Strategy

### Error Recovery Levels

#### Level 1: Warnings (don't crash)
```python
# Example: outdated lock file
if lock_outdated:
    print("⚠ Lock file is outdated", file=sys.stderr)
    # Continue execution anyway
```

#### Level 2: Self-Healing (auto-fix)
```python
# Example: missing gitignore
if not os.path.exists('.gitignore'):
    auto_fix_gitignore()
    print("✓ Created .gitignore")
```

#### Level 3: Manual Recovery (ask user)
```python
# Example: corrupted state file
try:
    state = load_state()
except json.JSONDecodeError:
    print("✗ Corrupted .py.state.json", file=sys.stderr)
    print("Run 'py fix' to attempt recovery", file=sys.stderr)
    return 1
```

#### Level 4: Hard Failure (exit)
```python
# Example: no Python 3.8+
if sys.version_info < (3, 8):
    print("✗ py requires Python 3.8+", file=sys.stderr)
    sys.exit(1)
```

### Signal Handling

```python
def signal_handler(signum, frame):
    """Handle SIGINT (Ctrl+C) gracefully"""
    print("\n✗ Interrupted by user (SIGINT)", file=sys.stderr)
    sys.exit(130)  # Standard POSIX exit code for SIGINT

signal.signal(signal.SIGINT, signal_handler)
```

**Exit codes:**
- `0`: Success
- `1`: Generic error
- `130`: SIGINT (Ctrl+C)
- `143`: SIGTERM

---

## Performance Optimizations

### 1. Lock File Reuse
```python
# If lock file matches declared deps, don't reinstall
if lock_up_to_date(declared, locked):
    print("✓ Dependencies already installed")
    return 0
```
**Impact:** `py run` is instant (no reinstall)

### 2. Global Wheel Cache
```bash
pip install --find-links ~/.cache/py flask
```
**Impact:** Reusing packages across projects is instant

### 3. Lazy State Loading
```python
# Only load state if command needs it
if needs_state:
    state = load_state()
```
**Impact:** Fast `py run` (skip JSON parsing if possible)

### 4. No Subprocess Calls in Loops
```python
# ❌ Bad: subprocess per package
for pkg in packages:
    subprocess.run(['pip', 'show', pkg])

# ✓ Good: single subprocess call
output = subprocess.run(['pip', 'list', '--format=json'])
```
**Impact:** Significant speedup for many packages

---

## Testing Strategy

### Test Categories

#### 1. Unit Tests (Functions)
- Parse dependency spec correctly
- Detect conflicts in lists
- Compare versions

#### 2. Integration Tests (Commands)
- `py init` → creates all files
- `py add` → installs + saves state + saves lock
- `py run` → executes script in venv
- `py doctor` → detects issues

#### 3. Regression Tests
- Old projects still work
- State format backward compatible
- Existing scripts run unchanged

#### 4. Edge Cases
- Empty dependencies
- Special characters in package names
- Very long dependency lists (100+ packages)
- Network timeouts during install
- Corrupted state files

### Test Infrastructure

```bash
# Comprehensive test script
bash test.sh

# Manual test in isolation
mkdir /tmp/test_py_manual && cd /tmp/test_py_manual
python3 ~/py init
python3 ~/py add requests  # Should work, no cleanup
```

---

## Security Considerations

### 1. Virtual Environment Isolation
- Each project's packages are isolated
- No global package pollution
- Safe to run untrusted code in isolated projects

### 2. Subprocess Security
```python
# ✓ Safe: shell=False (default)
subprocess.run(['pip', 'install', pkg])

# ❌ Dangerous: shell=True
subprocess.run(f'pip install {pkg}', shell=True)
```

### 3. File Permissions
```python
# Create lock file with standard permissions
with open(lock_path, 'w') as f:
    json.dump(...)
# File is readable by owner, not world-readable
```

### 4. No External URLs (except PyPI)
- No auto-update from internet
- Manual download/installation only
- Transparent dependency sourcing

---

## Extensibility Points

### Adding Custom Commands

Insert handler + argparse registration:

```python
def cmd_custom(args):
    """My custom command"""
    print("Custom logic here")
    return 0

# In argparse setup:
custom_parser = subparsers.add_parser('custom')
custom_parser.set_defaults(func=cmd_custom)

# In commands dict:
'custom': cmd_custom
```

### Adding Custom Checks to `py doctor`

```python
# In cmd_doctor():
checks = [
    check_venv(),
    check_lock_file(),
    check_my_custom_check(),  # Add here
]
```

### Adding Custom Auto-Fixes to `py fix`

```python
# In cmd_fix():
fixes = [
    auto_fix_gitignore(),
    auto_fix_toml(),
    auto_fix_my_custom_issue(),  # Add here
]
```

---

## Known Limitations

### 1. No Transitive Dependency Control
- Can't pin transitive deps (only direct deps)
- Workaround: use `pip-tools` or specify explicilty

### 2. No Python Version Changing
- Always uses system Python
- Workaround: use `pyenv` or `conda`

### 3. No Configuration File Support
- Settings only via command-line flags
- Workaround: create shell aliases

### 4. No GUI
- CLI only
- Workaround: use web frontend (future)

### 5. No Workspace Support
- One project per directory
- Workaround: use monorepo structure + multiple dirs

---

## Future Enhancements

### Phase 3: Configuration
- `~/.pyrc` for global settings
- `[tool.py]` section in `pyproject.toml`
- Per-project overrides

### Phase 4: Intelligence
- Transitive dependency tracking
- Conflict resolution suggestions
- Auto-upgrade recommendations

### Phase 5: Integration
- GitHub Actions plugin
- Pre-commit hook support
- Devcontainer integration

### Phase 6: Distribution
- Publish to PyPI (ironically)
- Package managers (brew, apt, etc.)
- Standalone binaries (PyInstaller)

---

## Glossary

| Term | Definition |
|------|-----------|
| **venv** | Virtual environment (`.venv`) isolated Python |
| **Lock file** | `.py.lock.json` with exact versions |
| **State** | `.py.state.json` with declared dependencies |
| **Snapshot** | Point-in-time capture for CI reproducibility |
| **Cache** | `~/.cache/py` with global wheel pool |
| **pyproject.toml** | Standard Python project metadata file |
| **Transitive** | Indirect dependencies (flask → werkzeug) |
| **Conflict** | Same package with incompatible version specs |

---

## References

- Python docs: [venv](https://docs.python.org/3/library/venv.html), [subprocess](https://docs.python.org/3/library/subprocess.html)
- [pyproject.toml spec](https://packaging.python.org/en/latest/specifications/)
- [Semantic Versioning](https://semver.org/)
- [PEP 427: Wheel Format](https://www.python.org/dev/peps/pep-0427/)
