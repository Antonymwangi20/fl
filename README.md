# fl - Python Project Management Without Friction

A single-file Python tool for managing virtual environments, dependencies, and script execution. Designed to feel natural and get out of your way.

**Latest Version:** 1.0

---

## Quick Start

```bash
# Initialize a new project
fl init

# Add dependencies
fl add requests flask

# Add from requirements.txt
fl add req

# Run a script
fl main.py

# Enter the project environment
fl shell

# List dependencies
fl list

# Check project health
fl doctor
```

---

## Installation

Copy `fl` to your PATH:

```bash
curl -fsSL https://raw.githubusercontent.com/Antonymwangi20/fl/main/fl -o ~/.local/bin/fl
chmod +x ~/.local/bin/fl
```

Or download directly:

```bash
wget https://example.com/fl -O ~/.local/bin/fl
chmod +x ~/.local/bin/fl
```

**Requirements:**
- Python 3.8+
- No external dependencies (uses only stdlib)

---

## Core Commands

### `fl init`
Initialize a new project with `pyproject.toml`, `.gitignore`, and `.venv` setup.

```bash
$ fl init
✓ Created pyproject.toml
✓ Created .gitignore
```

### `fl add <package> [package2 ...]`
Add dependencies and automatically install them.

```bash
$ fl add requests flask
✓ Added requests
✓ Added flask
✓ Virtual environment created
✓ Dependencies installed
```

**Add from requirements.txt:**
```bash
$ fl add req
✓ Added 5 packages from requirements.txt
✓ Dependencies installed
```

### `fl run <script.py> [args...]`
Run a Python script in the project environment. Can be abbreviated to just `fl script.py`.

```bash
$ fl run main.py --port 8000
# OR
$ fl main.py --port 8000
```

**Flags:**
- `-v, --verbose` - Show which Python interpreter is being used

### `fl shell`
Drop into an interactive shell with the project environment activated.

```bash
$ fl shell
Entering project environment (.venv)
Type 'exit' to leave
(.venv) $ python --version
```

### `fl list`
Show declared dependencies and installed packages.

```bash
$ fl list
Dependencies:
  • requests
  • flask

Installed (13 packages)
Lock records 13 packages
```

### `fl remove <pkg> [pkg2 ...]`
Remove packages from dependencies and uninstall them.

```bash
$ fl remove requests
✓ Removed requests from pyproject.toml
Found existing installation: requests 2.32.5
Successfully uninstalled requests-2.32.5
```

### `fl upgrade <pkg> [pkg2 ...]`
Upgrade packages to the latest available versions.

```bash
$ fl upgrade flask
Requirement already satisfied: flask in ./.venv/lib/python3.13/site-packages (3.1.3)
```

### `fl purge`
Completely clear the project environment and dependencies.

```bash
$ fl purge
✓ Cleared dependencies in pyproject.toml
✓ Removed virtual environment
✓ Environment purged
```

---

## Diagnostic & Analysis Commands

### `fl doctor`
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
$ fl doctor
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

### `fl check`
Check for dependency conflicts and invalid version specifications.

```bash
$ fl check
Analyzing dependencies...

✓ No dependency conflicts detected
```

**Detects:**
- Multiple conflicting version specs for the same package
- Invalid version operators (only `>=`, `<=`, `==`, `!=`, `~=`, `>`, `<` are valid)

### `fl audit`
Check which packages have newer versions available on PyPI.

```bash
$ fl audit
Checking 13 packages for updates...
✓ All packages are up to date
```

Or with outdated packages:

```bash
Found 2 outdated package(s):
  requests      2.30.0          → 2.32.5
  flask         3.0.0           → 3.1.3

Run 'fl upgrade requests' to update a package
```

### `fl search <term>`
Search PyPI for packages using the modern JSON API (no `pip search` deprecation).

```bash
$ fl search flask
Searching PyPI for 'flask'...

Results:
  flask                         3.1.3           Web development, one drop at a time

To add: fl add flask
```

### `fl lock-diff`
Compare lock file with currently installed packages to detect divergences.

```bash
$ fl lock-diff
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

Run 'fl install --force' to sync to dependencies
```

---

## Project Recovery Commands

### `fl fix`
Auto-fix common project issues.

Auto-repairs:
- ✅ Missing or incomplete `.gitignore`
- ✅ Malformed `pyproject.toml` (missing `[project]` section, dependencies list)
- ✅ Missing state files
- ✅ Missing lock files

```bash
$ fl fix
Scanning for issues...

✓ pyproject.toml syntax OK
✓ Fixed .gitignore (added 2 entries)

✓ Fixed 1 issue(s)
```

---

## Performance & Caching

### `fl cache`
Manage the global wheel cache at `~/.cache/fl/`.

**Show cache info:**
```bash
$ fl cache info
Cache directory: /home/user/.cache/fl
Wheels cached: 42
Total size: 156.32 MB
```

**Prune old wheels** (older than 30 days):
```bash
$ fl cache prune
✓ Pruned 5 old wheels
```

**Benefit:** Wheels are cached globally, so reinstalling the same versions across projects is instant.

---

## CI & Environment Snapshots

### `fl snapshot save [name]`
Save a snapshot of the current environment (dependencies + installed versions).

```bash
$ fl snapshot save production
✓ Snapshot saved: .fl-snapshots/production.json
```

**Use cases:**
- Save before making changes for easy rollback
- Archive known-good environments for CI
- Document dependency state at release time

### `fl snapshot compare [name]`
Compare current environment against a saved snapshot.

```bash
$ fl snapshot compare production
Comparing against snapshot 'production'...

Updated (2):
  requests     lock: 2.30.0    installed: 2.32.5
  flask        lock: 3.0.0     installed: 3.1.3
```

**Shows:**
- Packages added since snapshot
- Packages removed since snapshot
- Version changes

### `fl snapshot list`
List all saved snapshots in `.fl-snapshots/`.

```bash
$ fl snapshot list
Saved snapshots:
  • dev
  • production
  • testing
```

---

## Project Structure

After `fl init`, your project looks like:

```
my-project/
├── .venv/                    # Auto-created virtual environment
├── pyproject.toml            # Project metadata & dependencies
├── .gitignore                # Venv + cache exclusions
├── .fl.state.json            # Internal state tracking
├── .fl.lock.json             # Lock file (like requirements.lock)
└── .fl-snapshots/            # Environment snapshots (optional)
    ├── latest.json
    ├── production.json
    └── testing.json
```

**Files created by fl:**
- `.venv/` – Virtual environment (gitignored)
- `.fl.state.json` – Tracks declared dependencies (gitignored)
- `.fl.lock.json` – Lock file with exact versions (gitignored)
- `.fl-snapshots/` – Environment snapshots directory

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

**fl respects:**
- `dependencies` – List of packages to install
- `requires-python` – Validated by `fl doctor`
- `project.name` – Used in initialization

---

## Advanced Usage

### Global Wheel Cache
Wheels are automatically cached in `~/.cache/fl/`. This speeds up reinstalling common dependencies across projects:

```bash
$ fl add numpy
# First time: Downloads and caches wheel

$ cd ../another-project && fl add numpy
# Second time: Instant install from cache
```

Check cache usage:

```bash
$ fl cache info
Wheels cached: 156
Total size: 2.34 GB

$ fl cache prune  # Remove wheels older than 30 days
```

### Lock Files

fl automatically handles lock files:

1. **On `fl add`:** Downloads and records exact versions in `.fl.lock.json`
2. **On `fl run`:** Skips reinstall if lock matches declared deps
3. **On `fl audit`:** Compares lock against PyPI for available updates

Manual lock management:

```bash
$ fl lock-diff           # See what's out of sync
$ fl snapshot save ci    # Archive current state
$ fl snapshot compare ci # Verify reproducibility
```

### CI/CD Integration

**GitHub Actions example:**

```yaml
- name: Setup Python project
  run: |
    pip install .../fl
    fl fix  # Auto-create missing files
    fl doctor  # Verify health
    fl snapshot save ci-run

- name: Run tests
  run: |
    fl pytest tests/

- name: Check for regressions
  run: |
    fl snapshot compare ci-run  # Ensure no surprise installs
```

### Dependency Analysis

Check for conflicts before committing:

```bash
$ fl check
Analyzing dependencies...

✓ No dependency conflicts detected
```

Audit before deploying:

```bash
$ fl audit
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
fl main.py
fl run main.py
```

### Verbose Mode
See which Python interpreter is being used:

```bash
$ fl run main.py -v
Using: /path/to/.venv/bin/python
```

### Environment Isolation
Each project gets its own `.venv`:

```bash
$ cd project-a && fl add flask
$ cd ../project-b && fl add flask
# project-b gets its own Flask installation, no conflicts
```

### Auto-Recovery
Broken project state is auto-detected:

```bash
$ fl doctor
⚠ .gitignore missing venv or lock file entry

$ fl fix
✓ Fixed .gitignore (added 1 entries)
```

---

## Troubleshooting

### "Module not found" errors

Run doctor to diagnose:

```bash
$ fl doctor
⚠ pkg is not installed

$ fl fix
✓ Recreated lock file

$ fl run script.py  # Try again
```

### Virtual environment is broken

Recreate it:

```bash
$ fl purge
$ fl init
$ fl add ...  # Re-add dependencies
```

### Lock file is out of sync

Force reinstall:

```bash
$ fl lock-diff  # See what's different
$ fl add ...    # Add new package
# (This auto-syncs the lock file)
```

### `pip search` doesn't work

Use `fl search` instead (uses PyPI JSON API):

```bash
$ fl search requests
# Modern, faster, works offline
```

---

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| `fl init` | 2-5s | Creates venv + basic files |
| `fl add` (first) | 10-60s | Downloads wheels, depends on package size |
| `fl add` (cached) | <1s | Uses global cache, instant |
| `fl run` | <1s | Reuses lock file, no reinstall |
| `fl doctor` | 1-2s | Local checks only (no network) |
| `fl audit` | 5-30s | Checks PyPI for each package |
| `fl search` | 1-3s | One PyPI API call |
| `fl snapshot save` | <1s | Writes JSON file |

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
A: No, virtualenvs are platform/Python-specific. Use `fl snapshot` + CI for reproducibility.

**Q: Can I use `fl` for production?**  
A: Yes, with snapshots. Save a snapshot, version it, and compare in CI.

**Q: What about private packages?**  
A: Use `pip`'s standard authentication. fl passes everything to pip.

**Q: Does `fl` lock dependencies recursively?**  
A: Yes, via `pip`. The lock file records exact versions of all transitive dependencies.

**Q: Can I import from requirements.txt?**  
A: Yes! Use `fl add req` to read `requirements.txt` and add all packages to your project. Each package gets added to `pyproject.toml` and installed.

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
