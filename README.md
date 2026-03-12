# py - Python Project Management Without Friction

A single-file Python tool for managing virtual environments, dependencies, and script execution. Designed to feel natural and get out of your way.

**Latest Version:** 1.0

---

## Quick Start

```bash
# Initialize a new project
py init

# Add dependencies
py add requests flask

# Run a script
py main.py

# Enter the project environment
py shell

# List dependencies
py list

# Check project health
py doctor
```

---

## Installation

Copy `py` to your PATH:

```bash
curl https://example.com/py -o ~/.local/bin/py
chmod +x ~/.local/bin/py
```

Or download directly:

```bash
wget https://example.com/py -O ~/.local/bin/py
chmod +x ~/.local/bin/py
```

**Requirements:**
- Python 3.8+
- No external dependencies (uses only stdlib)

---

## Core Commands

### `py init`
Initialize a new project with `pyproject.toml`, `.gitignore`, and `.venv` setup.

```bash
$ py init
✓ Created pyproject.toml
✓ Created .gitignore
```

### `py add <package> [package2 ...]`
Add dependencies and automatically install them.

```bash
$ py add requests flask
✓ Added requests
✓ Added flask
✓ Virtual environment created
✓ Dependencies installed
```

### `py run <script.py> [args...]`
Run a Python script in the project environment. Can be abbreviated to just `py script.py`.

```bash
$ py run main.py --port 8000
# OR
$ py main.py --port 8000
```

**Flags:**
- `-v, --verbose` - Show which Python interpreter is being used

### `py shell`
Drop into an interactive shell with the project environment activated.

```bash
$ py shell
Entering project environment (.venv)
Type 'exit' to leave
(.venv) $ python --version
```

### `py list`
Show declared dependencies and installed packages.

```bash
$ py list
Dependencies:
  • requests
  • flask

Installed (13 packages)
Lock records 13 packages
```

### `py remove <pkg> [pkg2 ...]`
Remove packages from dependencies and uninstall them.

```bash
$ py remove requests
✓ Removed requests from pyproject.toml
Found existing installation: requests 2.32.5
Successfully uninstalled requests-2.32.5
```

### `py upgrade <pkg> [pkg2 ...]`
Upgrade packages to the latest available versions.

```bash
$ py upgrade flask
Requirement already satisfied: flask in ./.venv/lib/python3.13/site-packages (3.1.3)
```

### `py purge`
Completely clear the project environment and dependencies.

```bash
$ py purge
✓ Cleared dependencies in pyproject.toml
✓ Removed virtual environment
✓ Environment purged
```

---

## Diagnostic & Analysis Commands

### `py doctor`
Run comprehensive diagnostics on the project environment.

Checks:
- ✅ `pyproject.toml` syntax validity
- ✅ Python version constraint compatibility
- ✅ Virtual environment presence
- ✅ Dependency installation status
- ✅ Lock file vs. installed sync
- ✅ `.gitignore` configuration
- ✅ State file presence

```bash
$ py doctor
Examining project...

✓ pyproject.toml syntax OK
✓ Python 3.13.12 meets requirement: >=3.8
✓ virtual environment exists
2 dependencies declared in pyproject.toml
✓ lock file matches installed packages
✓ .gitignore is properly configured
✓ state file present

✓ everything looks healthy
```

### `py check`
Check for dependency conflicts and invalid version specifications.

```bash
$ py check
Analyzing dependencies...

✓ No dependency conflicts detected
```

**Detects:**
- Multiple conflicting version specs for the same package
- Invalid version operators (only `>=`, `<=`, `==`, `!=`, `~=`, `>`, `<` are valid)

### `py audit`
Check which packages have newer versions available on PyPI.

```bash
$ py audit
Checking 13 packages for updates...
✓ All packages are up to date
```

Or with outdated packages:

```bash
Found 2 outdated package(s):
  requests      2.30.0          → 2.32.5
  flask         3.0.0           → 3.1.3

Run 'py upgrade requests' to update a package
```

### `py search <term>`
Search PyPI for packages using the modern JSON API (no `pip search` deprecation).

```bash
$ py search flask
Searching PyPI for 'flask'...

Results:
  flask                         3.1.3           Web development, one drop at a time

To add: py add flask
```

### `py lock-diff`
Compare lock file with currently installed packages to detect divergences.

```bash
$ py lock-diff
Comparing lock file to installed packages...

✓ Lock file and installed packages match
```

Or when differences exist:

```
In lock file but not installed (1):
  - deprecated-pkg 1.0.0

Installed but not in lock file (2):
  + new-pkg 2.0.0

Version mismatches (1):
  requests     lock: 2.30.0    installed: 2.32.5

Run 'py install --force' to sync to dependencies
```

---

## Project Recovery Commands

### `py fix`
Auto-fix common project issues.

Auto-repairs:
- ✅ Missing or incomplete `.gitignore`
- ✅ Malformed `pyproject.toml` (missing `[project]` section, dependencies list)
- ✅ Missing state files
- ✅ Missing lock files

```bash
$ py fix
Scanning for issues...

✓ pyproject.toml syntax OK
✓ Fixed .gitignore (added 2 entries)

✓ Fixed 1 issue(s)
```

---

## Performance & Caching

### `py cache`
Manage the global wheel cache at `~/.cache/py/`.

**Show cache info:**
```bash
$ py cache info
Cache directory: /home/user/.cache/py
Wheels cached: 42
Total size: 156.32 MB
```

**Prune old wheels** (older than 30 days):
```bash
$ py cache prune
✓ Pruned 5 old wheels
```

**Benefit:** Wheels are cached globally, so reinstalling the same versions across projects is instant.

---

## CI & Environment Snapshots

### `py snapshot save [name]`
Save a snapshot of the current environment (dependencies + installed versions).

```bash
$ py snapshot save production
✓ Snapshot saved: .py-snapshots/production.json
```

**Use cases:**
- Save before making changes for easy rollback
- Archive known-good environments for CI
- Document dependency state at release time

### `py snapshot compare [name]`
Compare current environment against a saved snapshot.

```bash
$ py snapshot compare production
Comparing against snapshot 'production'...

Updated (2):
  requests     lock: 2.30.0    installed: 2.32.5
  flask        lock: 3.0.0     installed: 3.1.3
```

**Shows:**
- Packages added since snapshot
- Packages removed since snapshot
- Version changes

### `py snapshot list`
List all saved snapshots in `.py-snapshots/`.

```bash
$ py snapshot list
Saved snapshots:
  • dev
  • production
  • testing
```

---

## Project Structure

After `py init`, your project looks like:

```
my-project/
├── .venv/                    # Auto-created virtual environment
├── pyproject.toml            # Project metadata & dependencies
├── .gitignore                # Venv + cache exclusions
├── .py.state.json            # Internal state tracking
├── .py.lock.json             # Lock file (like requirements.lock)
└── .py-snapshots/            # Environment snapshots (optional)
    ├── latest.json
    ├── production.json
    └── testing.json
```

**Files created by py:**
- `.venv/` – Virtual environment (gitignored)
- `.py.state.json` – Tracks declared dependencies (gitignored)
- `.py.lock.json` – Lock file with exact versions (gitignored)
- `.py-snapshots/` – Environment snapshots directory

---

## Configuration

### `pyproject.toml`

Minimal example:

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "My awesome project"
requires-python = ">=3.8"
dependencies = [
    "requests>=2.28",
    "flask>=3.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**py respects:**
- `dependencies` – List of packages to install
- `requires-python` – Validated by `py doctor`
- `project.name` – Used in initialization

---

## Advanced Usage

### Global Wheel Cache
Wheels are automatically cached in `~/.cache/py/`. This speeds up reinstalling common dependencies across projects:

```bash
$ py add numpy
# First time: Downloads and caches wheel

$ cd ../another-project && py add numpy
# Second time: Instant install from cache
```

Check cache usage:

```bash
$ py cache info
Wheels cached: 156
Total size: 2.34 GB

$ py cache prune  # Remove wheels older than 30 days
```

### Lock Files

py automatically handles lock files:

1. **On `py add`:** Downloads and records exact versions in `.py.lock.json`
2. **On `py run`:** Skips reinstall if lock matches declared deps
3. **On `py audit`:** Compares lock against PyPI for available updates

Manual lock management:

```bash
$ py lock-diff           # See what's out of sync
$ py snapshot save ci    # Archive current state
$ py snapshot compare ci # Verify reproducibility
```

### CI/CD Integration

**GitHub Actions example:**

```yaml
- name: Setup Python project
  run: |
    pip install .../py
    py fix  # Auto-create missing files
    py doctor  # Verify health
    py snapshot save ci-run

- name: Run tests
  run: |
    py pytest tests/

- name: Check for regressions
  run: |
    py snapshot compare ci-run  # Ensure no surprise installs
```

### Dependency Analysis

Check for conflicts before committing:

```bash
$ py check
Analyzing dependencies...

✓ No dependency conflicts detected
```

Audit before deploying:

```bash
$ py audit
Checking 42 packages for updates...

Found 3 outdated package(s):
  [list of upgradeable packages]
```

---

## Tips & Tricks

### Quick Script Execution
Skip the `run` verb—just use the script name:

```bash
# These are equivalent:
py main.py
py run main.py
```

### Verbose Mode
See which Python interpreter is being used:

```bash
$ py run main.py -v
Using: /path/to/.venv/bin/python
```

### Environment Isolation
Each project gets its own `.venv`:

```bash
$ cd project-a && py add flask
$ cd ../project-b && py add flask
# project-b gets its own Flask installation, no conflicts
```

### Auto-Recovery
Broken project state is auto-detected:

```bash
$ py doctor
⚠ .gitignore missing venv or lock file entry

$ py fix
✓ Fixed .gitignore (added 1 entries)
```

---

## Troubleshooting

### "Module not found" errors

Run doctor to diagnose:

```bash
$ py doctor
⚠ pkg is not installed

$ py fix
✓ Recreated lock file

$ py run script.py  # Try again
```

### Virtual environment is broken

Recreate it:

```bash
$ py purge
$ py init
$ py add ...  # Re-add dependencies
```

### Lock file is out of sync

Force reinstall:

```bash
$ py lock-diff  # See what's different
$ py add ...    # Add new package
# (This auto-syncs the lock file)
```

### `pip search` doesn't work

Use `py search` instead (uses PyPI JSON API):

```bash
$ py search requests
# Modern, faster, works offline
```

---

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| `py init` | 2-5s | Creates venv + basic files |
| `py add` (first) | 10-60s | Downloads wheels, depends on package size |
| `py add` (cached) | <1s | Uses global cache, instant |
| `py run` | <1s | Reuses lock file, no reinstall |
| `py doctor` | 1-2s | Local checks only (no network) |
| `py audit` | 5-30s | Checks PyPI for each package |
| `py search` | 1-3s | One PyPI API call |
| `py snapshot save` | <1s | Writes JSON file |

---

## Compatibility

- **Python versions:** 3.8+
- **Operating systems:** Linux, macOS, Windows (with git bash)
- **pip versions:** 20.0+
- **Dependencies:** None (stdlib only)

---

## FAQ

**Q: Is this a replacement for poetry/pipenv?**  
A: Not exactly. It's simpler and faster for small projects. Good for scripts, prototypes, and CI. Poetry is better for complex multi-package projects.

**Q: Will my `.venv` be portable?**  
A: No, virtualenvs are platform/Python-specific. Use `py snapshot` + CI for reproducibility.

**Q: Can I use `py` for production?**  
A: Yes, with snapshots. Save a snapshot, version it, and compare in CI.

**Q: What about private packages?**  
A: Use `pip`'s standard authentication. py passes everything to pip.

**Q: Does `py` lock dependencies recursively?**  
A: Yes, via `pip`. The lock file records exact versions of all transitive dependencies.

---

## Contributing & Issues

Found a bug? Create a snapshot, check logs, and report:

```bash
$ py doctor
$ py snapshot save latest
$ py cache info
```

---

## License

MIT 

---
