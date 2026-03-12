# Contributing to py

Thank you for interest in improving py! This guide walks through the architecture, development setup, and contribution process.

---

## Development Setup

### 1. Clone/Download the Tool

```bash
git clone https://github.com/Antonymwangi20/py.git
cd py
```

### 2. Verify it Works

```bash
python3 py --help
python3 -m py_compile py  # Syntax check
```

### 3. Run Tests

```bash
bash test.sh  # Runs comprehensive test suite
```

---

## Architecture Overview

### Design Philosophy

- **Single file:** No installation complexity, easy to distribute and update
- **Stdlib only:** No dependencies besides Python 3.8+ (fast, portable)
- **Stateless by default:** Uses `.py.state.json`, `.py.lock.json`, and `.py-snapshots/` for state tracking
- **Shell-friendly:** All commands integrate well with bash, zsh, etc.

### File Structure (the `py` script)

```
py (single Python file, ~1500 lines)
├─ Imports (stdlib only)
├─ Constants & config
│  ├─ DEFAULT_PYTHON = "3.8"
│  ├─ PY_STATE_FILE = ".py.state.json"
│  ├─ PY_LOCK_FILE = ".py.lock.json"
│  ├─ CACHE_DIR = "~/.cache/py"
│  └─ SNAPSHOTS_DIR = ".py-snapshots"
├─ Utility functions (25+)
│  ├─ get_venv_path()
│  ├─ get_lock_path()
│  ├─ get_state_path()
│  ├─ ensure_venv()
│  ├─ load_state() / save_state()
│  ├─ load_lock() / save_lock()
│  ├─ get_cache_dir()
│  ├─ parse_dep_spec()
│  ├─ check_dependency_conflicts()
│  ├─ auto_fix_gitignore()
│  ├─ auto_fix_toml()
│  ├─ get_snapshot_path()
│  └─ ... and more
├─ Command handlers (17)
│  ├─ cmd_init()
│  ├─ cmd_add()
│  ├─ cmd_run()
│  ├─ cmd_shell()
│  ├─ cmd_list()
│  ├─ cmd_doctor()
│  ├─ cmd_check()
│  ├─ cmd_audit()
│  ├─ cmd_search()
│  ├─ cmd_lock_diff()
│  ├─ cmd_cache()
│  ├─ cmd_fix()
│  ├─ cmd_snapshot()
│  └─ (plus remove, upgrade, purge)
├─ Main entry point
│  ├─ Argument parsing (argparse)
│  ├─ Signal handling
│  └─ Command dispatch
```

### Data Files

Each project creates:

**`.py.state.json`** – Tracks declared dependencies
```json
{
  "dependencies": ["requests", "flask>=3.0"],
  "python_version": "3.13.12"
}
```

**`.py.lock.json`** – Exact installed versions (like `requirements.txt`)
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

**`.py-snapshots/<name>.json`** – Environment snapshot
```json
{
  "timestamp": "2026-03-15T14:23:45",
  "python_version": "3.13.12",
  "dependencies": ["requests", "flask>=3.0"],
  "installed": {
    "requests": "2.32.5",
    "flask": "3.1.3",
    "werkzeug": "3.1.2"
  }
}
```

---

## Command Handler Pattern

All commands follow this pattern:

```python
def cmd_example(args):
    """Description of what this command does.
    
    Args:
        args: argparse Namespace with parsed arguments
    
    Returns:
        0 on success, 1 on error
    """
    try:
        # 1. Validate input
        if not os.path.exists('.py.state.json'):
            print("✗ Not initialized. Run 'py init' first.", file=sys.stderr)
            return 1
        
        # 2. Load state if needed
        state = load_state()
        
        # 3. Execute logic
        result = do_something()
        
        # 4. Save state if modified
        if state_changed:
            save_state(state)
        
        # 5. Print results
        print("✓ Success")
        return 0
        
    except KeyboardInterrupt:
        print("\n✗ Interrupted", file=sys.stderr)
        return 130  # Standard SIGINT exit code
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1
```

---

## Key Functions

### State Management

```python
def load_state():
    """Load .py.state.json"""
    with open(get_state_path()) as f:
        return json.load(f)

def save_state(state):
    """Save .py.state.json"""
    with open(get_state_path(), 'w') as f:
        json.dump(state, f, indent=2)
```

### Virtual Environment

```python
def ensure_venv():
    """Create .venv if it doesn't exist"""
    venv_path = get_venv_path()
    if not os.path.exists(venv_path):
        subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)
```

### Dependency Parsing

```python
def parse_dep_spec(spec):
    """Parse 'requests>=2.28' → ('requests', '>=2.28')"""
    import re
    match = re.match(r'([a-zA-Z0-9_-]+)(.*)', spec)
    if match:
        return match.group(1), match.group(2)
    return spec, ''
```

### Conflict Detection

```python
def check_dependency_conflicts(dependencies):
    """Find same package with multiple specs"""
    conflicts = {}
    for dep in dependencies:
        pkg, spec = parse_dep_spec(dep)
        pkg_lower = pkg.lower()
        if pkg_lower not in conflicts:
            conflicts[pkg_lower] = []
        conflicts[pkg_lower].append((pkg, spec))
    
    return [specs for specs in conflicts.values() if len(specs) > 1]
```

---

## Testing

### Running the Test Suite

```bash
# Comprehensive test in isolated directory
bash test.sh

# Manual test commands
mkdir /tmp/test_py && cd /tmp/test_py
python3 ~/path/to/py init          # Initialize
python3 ~/path/to/py add requests  # Add dep
python3 ~/path/to/py list          # List
python3 ~/path/to/py doctor        # Health check
```

### Test Coverage Areas

- ✅ Initialization: creates all required files
- ✅ Dependency management: add, remove, list, upgrade
- ✅ Execution: run scripts, enter shell
- ✅ State persistence: across commands
- ✅ Lock files: accurate tracking
- ✅ Diagnostics: doctor detects issues
- ✅ Conflict detection: check catches duplicates
- ✅ Auto-fix: repairs broken projects
- ✅ Snapshots: save/compare/list work
- ✅ Cache management: info, prune
- ✅ Error handling: graceful failures

### Adding a New Test

Edit `test.sh` and add a function:

```bash
test_my_feature() {
    echo "Testing my feature..."
    py my-command arg1 arg2 || return 1
    grep "expected string" .py.state.json || return 1
    echo "✓ test_my_feature passed"
}
```

Then call it in the main test loop.

---

## Adding a New Command

### Step 1: Implement the Handler

```python
def cmd_example(args):
    """Do something useful.
    
    Args:
        args: Namespace(option=value, ...)
    Returns:
        0 on success, 1 on error
    """
    try:
        # Your logic here
        print("✓ Done")
        return 0
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1
```

### Step 2: Register in Argparse

In the `if __name__ == "__main__":` block, add:

```python
# Create subparser
example_parser = subparsers.add_parser(
    'example',
    help='Do something useful'
)
example_parser.add_argument('option', help='Required option')
example_parser.add_argument('--flag', action='store_true', help='Optional flag')
example_parser.set_defaults(func=cmd_example)
```

### Step 3: Add to Commands Dict

```python
commands = {
    'init': cmd_init,
    'add': cmd_add,
    ...
    'example': cmd_example,  # Add here
}
```

### Step 4: Test It

```bash
python3 py example --help
python3 py example value
```

---

## Common Pitfalls

### 1. Forgetting to Save State

```python
# ❌ Wrong
state['dependencies'] = ['flask']
# Changes lost!

# ✓ Right
state['dependencies'] = ['flask']
save_state(state)
```

### 2. Not Handling Missing .venv

```python
# ❌ Wrong
subprocess.run([get_pip_path(), 'install', 'flask'], check=True)
# Fails if .venv doesn't exist

# ✓ Right
ensure_venv()
subprocess.run([get_pip_path(), 'install', 'flask'], check=True)
```

### 3. Hardcoding Paths

```python
# ❌ Wrong
lock_path = '.py.lock.json'

# ✓ Right
lock_path = get_lock_path()
```

### 4. Ignoring Subprocess Errors

```python
# ❌ Wrong
subprocess.run([...])  # What if it fails?

# ✓ Right
subprocess.run([...], check=True)  # Raises CalledProcessError
```

### 5. String Escaping Issues

In multi-line strings with many escape sequences, use raw strings or write to temp file:

```python
# ✓ Better
content = '{"key": "value"}'
```

---

## Code Style

### Naming Conventions
- Functions: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Paths: Use `os.path` functions (portable)
- Command handlers: `cmd_<name>`

### Comments
- Add docstrings to all functions
- Use `#` for inline explanations
- Avoid obvious comments

### Formatting

```python
# Good
if not os.path.exists(path):
    print(f"✗ {path} not found", file=sys.stderr)
    return 1

# Also good (with clear variable names)
state_file = get_state_path()
if not os.path.exists(state_file):
    raise FileNotFoundError(f"State file missing: {state_file}")
```

---

## Performance Considerations

### Network Calls
- `py audit` calls PyPI – cache results if possible
- `py search` uses JSON API – single call, fast
- Minimize subprocess calls in loops

### File I/O
- Load state once per command, save once at end
- Don't re-parse pyproject.toml repeatedly
- Cache venv path (doesn't change)

### Virtual Environments
- Creating venv can be slow (~2-5s)
- Reuse existing venv when possible
- Don't recreate on every run

---

## Debugging & Logging

### Verbose Output
Add to any command:

```python
def cmd_example(args):
    if getattr(args, 'verbose', False):
        print(f"DEBUG: state = {state}")
```

Usage:
```bash
python3 py example -v
```

### Print State
Quick debug:

```bash
cat .py.state.json | python3 -m json.tool
```

### Trace Execution
```bash
python3 -u py run main.py 2>&1 | head -50
```

---

## Submitting Changes

### Before Submitting

1. **Test locally:**
   ```bash
   bash test.sh
   ```

2. **Check syntax:**
   ```bash
   python3 -m py_compile py
   ```

3. **Verify backward compatibility:**
   - Old projects should still work
   - Existing state files should load
   - New fields should have defaults

### Commit Message Format

```
Add cache pruning feature

- Add --max-age flag to 'py cache prune'
- Default 30 days, configurable
- Respects .cache/py directory structure
- Fixes #42
```

### PR Description

```
## What
Brief description of changes

## Why
Problem being solved

## How
Implementation approach

## Tests
How to verify the fix works

## Checklist
- [ ] Syntax check passed
- [ ] test.sh passed
- [ ] Backward compatible
- [ ] Updated README if needed
```

---

## Future Directions

### Potential Features
- **Configuration file:** `~/.pyrc` or `pyproject.toml` [tool.py]` section
- **Plugin system:** Load user commands from `~/.py/plugins/`
- **Package templates:** `py new --template flask`
- **Publish to PyPI:** Integrated release commands
- **Python version switching:** `py use 3.11`
- **Dependency visualizer:** `py graph --show`

### Performance Improvements
- Cache PyPI queries locally
- Parallel package downloads
- Pre-built wheels for common packages
- Lazy loading of heavy utilities

### Integration
- GitHub Actions plugin
- IDE extensions (VSCode, PyCharm)
- Devcontainer support
- Kubernetes integration

---

## Questions?

- Check the [README](README.md) for usage
- See [examples](examples/) for real-world usage
- Open an issue with questions or suggestions

---

Happy contributing!
