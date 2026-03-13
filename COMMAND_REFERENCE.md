# Command Reference

Quick lookup for all `fl-tool` commands with examples and options.

---

## Command Index

| Command | Purpose | Phase |
|---------|---------|-------|
| `init` | Initialize new project | 1 |
| `add` | Add dependencies | 1 |
| `remove` | Remove dependencies | 1 |
| `upgrade` | Upgrade packages | 1 |
| `run` / inline | Execute scripts | 1 |
| `shell` | Interactive environment | 1 |
| `list` | Show dependencies | 1 |
| `purge` | Clear environment | 1 |
| `doctor` | Health diagnostics | 1 |
| `search` | Find packages on PyPI | 1 |
| `audit` | Check for updates | 1 |
| `lock-diff` | Compare state vs. installed | 1 |
| `cache` | Manage global wheel cache | 2 |
| `check` | Detect conflicts | 2 |
| `fix` | Auto-repair project | 2 |
| `snapshot` | Environment snapshots | 2 |

---

## Core Commands

### `fl init`

**Purpose:** Initialize a new project

**Usage:**
```bash
fl init
```

**Output:**
```
✓ Created pyproject.toml
✓ Created .gitignore
✓ Created virtual environment
✓ Project initialized
```

**Files created:**
- `pyproject.toml` – Project metadata
- `.gitignore` – Venv exclusions
- `.venv/` – Virtual environment
- `.fl.state.json` – Empty deps list
- `.fl.lock.json` – Empty lock

**Options:** None

**Notes:**
- Safe to run multiple times (won't overwrite existing)
- Must run before `fl add`

---

### `fl add <package> [package2 ...]`

**Purpose:** Add dependencies and install them

**Usage:**
```bash
fl add requests
fl add flask django
fl add "numpy>=1.20,<2.0"
```

**Output:**
```
✓ Added requests
✓ Added flask
✓ Added django
✓ Virtual environment created
✓ Dependencies installed
```

**What it does:**
1. Parses package specs
2. Checks for conflicts
3. Adds to `.fl.state.json`
4. Installs via pip
5. Saves lock file (`.fl.lock.json`)

**Options:**
- None (positional args are packages)

**Special cases:**
- Version specs: `requests>=2.28`, `flask==3.0`
- Extras: `sqlalchemy[postgresql]`
- Multiple can be added in one call

---

### `fl remove <package> [package2 ...]`

**Purpose:** Remove dependencies and uninstall

**Usage:**
```bash
fl remove requests
fl remove flask django
```

**Output:**
```
✓ Removed requests from pyproject.toml
Found existing installation: requests-2.32.5
Successfully uninstalled requests-2.32.5
```

**Notes:**
- Warns if package not found
- Updates lock file automatically

---

### `fl upgrade [package]`

**Purpose:** Upgrade packages to latest versions

**Usage:**
```bash
fl upgrade                # Upgrade all
fl upgrade requests       # Upgrade specific package
fl upgrade flask django   # Upgrade multiple
```

**Output (all up to date):**
```
✓ All packages are up to date
```

**Output (upgrades available):**
```
Requirement already satisfied: requests in ./venv (2.30.0)
Collecting requests
  Downloading requests-2.32.5-py3-none-any.whl
Installing collected packages: requests
Successfully installed requests-2.32.5
✓ Upgrade complete
```

---

### `fl run <script.py> [args...]` / `fl <script.py> [args...]`

**Purpose:** Execute a Python script in project environment

**Usage:**
```bash
# Full syntax
fl run main.py
fl run main.py --port 8000 --debug

# Shorthand (no 'run' verb)
fl main.py
fl main.py --port 8000
```

**Output:**
```
$ py main.py
Starting server on port 8000...
```

**Options:**
- `-v, --verbose` – Show which Python is being used

**Example output with -v:**
```
Using: /home/user/project/.venv/bin/python
Starting server on port 8000...
```

**Notes:**
- Arguments after script name are passed to script
- Exit code matches script's exit code
- Environment variables are preserved

---

### `fl shell`

**Purpose:** Enter interactive shell with project environment activated

**Usage:**
```bash
fl shell
```

**Output:**
```
Entering project environment (.venv)
Type 'exit' to leave
(.venv) $ 
```

**Inside the shell:**
```bash
(.venv) $ python --version
Python 3.13.12

(.venv) $ pip list
Package            Version
------------------ ---------
click              8.1.7
flask              3.1.3
itsdangerous       2.1.2
jinja2             3.1.4
requests           2.32.5
werkzeug           3.1.2

(.venv) $ exit
$
```

**Notes:**
- Full REPL access to project Python
- All dependencies available
- Type `exit` to leave

---

### `fl list`

**Purpose:** Show project dependencies and installed packages

**Usage:**
```bash
fl list
```

**Output:**
```
Dependencies:
  • requests>=2.28
  • flask>=3.0

Installed (13 packages):
  flask (3.1.3)
  werkzeug (3.1.2)
  jinja2 (3.1.4)
  click (8.1.7)
  itsdangerous (2.1.2)
  requests (2.32.5)
  certifi (2024.6.2)
  charset-normalizer (3.2.0)
  idna (3.3)
  urllib3 (2.0.7)
  + 3 more

Lock records 13 packages
```

---

### `fl purge`

**Purpose:** Completely clear project environment and dependencies

**Usage:**
```bash
fl purge
```

**Output:**
```
✓ Cleared dependencies in pyproject.toml
✓ Removed virtual environment
✓ Environment purged
```

**Warning:** This is irreversible! All packages uninstalled, `.venv` deleted.

---

## Diagnostic Commands

### `fl doctor`

**Purpose:** Run comprehensive project diagnostics

**Usage:**
```bash
fl doctor
```

**Healthy output:**
```
Examining project...

✓ pyproject.toml syntax OK
✓ Python 3.13.12 meets requirement: >=3.8
✓ Virtual environment exists
✓ 2 dependencies declared in pyproject.toml
✓ All dependencies installed
✓ Lock file matches installed packages
✓ .gitignore is properly configured
✓ State file present

✓ everything looks healthy
```

**With issues:**
```
Examining project...

✗ pyproject.toml has syntax error: Unexpected token
✓ Python 3.13.12 meets requirement: >=3.8
✗ Virtual environment missing
⚠ Lock file differs from declared dependencies

✗ Found 3 issue(s). Run 'py fix' to auto-repair.
```

**What it checks:**
- TOML syntax validity
- Python version compatibility
- Virtual environment presence
- Dependencies declared
- Dependencies installed
- Lock file synchronization
- `.gitignore` configuration
- State file presence

---

### `fl check`

**Purpose:** Check for dependency conflicts and invalid specs

**Usage:**
```bash
fl check
```

**Healthy output:**
```
Analyzing dependencies...

✓ No dependency conflicts detected
✓ All version specs are valid
```

**With conflicts:**
```
Analyzing dependencies...

✗ Dependency conflict found:
  flask
    - flask>=3.0
    - flask==2.0
  (can't satisfy both constraints)

✗ Found 1 conflict(s)
```

**Detects:**
- Multiple specs for same package
- Incompatible version constraints
- Invalid operators (only `>=`, `<=`, `==`, `!=`, `~=`, `>` valid)

---

### `fl audit`

**Purpose:** Check for available package updates on PyPI

**Usage:**
```bash
fl audit
```

**All up to date:**
```
Checking 13 packages for updates...

✓ All packages are up to date
```

**With outdated packages:**
```
Checking 13 packages for updates...

Found 2 outdated package(s):
  requests      2.30.0          → 2.32.5      (latest)
  flask         3.0.0           → 3.1.3       (latest)

Run 'py upgrade requests' to update a package
```

**Notes:**
- Queries PyPI JSON API
- Shows current vs. latest versions
- Suggests upgrade command

---

### `fl search <term>`

**Purpose:** Search PyPI for packages

**Usage:**
```bash
pfly search flask
fl search web framework
```

**Output:**
```
Searching PyPI for 'flask'...

Results (top 5):
  1. flask                               3.1.3
     Web development, one drop at a time.
     pip: pip install flask

  2. flask-restx                         0.5.1
     Automatically generated REST API extension for Flask
     pip: pip install flask-restx

  3. flask-cors                          4.0.0
     A Flask extension adding CORS support
     pip: pip install flask-cors
```

**Notes:**
- Modern API (uses PyPI JSON endpoint)
- No `pip search` deprecation issues
- Return top results
- Shows package name, version, description

---

### `fl lock-diff`

**Purpose:** Compare lock file against currently installed packages

**Usage:**
```bash
fl lock-diff
```

**In sync:**
```
Comparing lock file to installed packages...

✓ Lock file and installed packages match
```

**Out of sync:**
```
Comparing lock file to installed packages...

In lock file but not installed (1):
  - deprecated-pkg (1.0.0)

Installed but not in lock file (2):
  + new-pkg (2.0.0)
  + another-pkg (1.5.0)

Version mismatches (1):
  requests
    lock:      2.30.0
    installed: 2.32.5

Run 'fl add ...' to add packages to dependencies
Run 'fl install --force' to sync to dependencies
```

---

## Phase 2 Commands

### `fl cache`

**Purpose:** Manage global wheel cache at `~/.cache/py`

#### `fl cache info`

Show cache status:

```bash
$ fl cache info

Cache directory: /home/user/.cache/py
Wheels cached: 42
Total size: 156.32 MB
```

#### `fl cache prune`

Remove wheels older than 30 days:

```bash
$ fl cache prune

Searching for old wheels (>30 days)...
✓ Pruned 5 old wheels
Freed: 23.45 MB
Total remaining: 132.87 MB
```

**Options:**
- `--max-age <days>` – Customize age threshold (default: 30)

---

### `fl check`

Check for dependency conflicts (see [diagnostic commands](#py-check) above)

---

### `fl fix`

**Purpose:** Auto-repair common project issues

**Usage:**
```bash
fl fix
```

**Output:**
```
Scanning for issues...

✓ pyproject.toml syntax OK
✓ Fixed .gitignore (added 2 entries)
✓ Created missing lock file
✓ Fixed 2 issue(s)
```

**Auto-fixes:**
- ✅ Creates missing `.gitignore`
- ✅ Adds missing `.gitignore` entries
- ✅ Repairs malformed `pyproject.toml`
- ✅ Recreates missing state file
- ✅ Recreates missing lock file

**Safe:** Won't overwrite your changes (backs up before modifying)

---

### `fl snapshot`

**Purpose:** Save and compare environment snapshots for CI reproducibility

#### `fl snapshot save [name]`

Save current environment state:

```bash
$ fl snapshot save production
✓ Snapshot saved: .fl-snapshots/production.json

$ fl snapshot save latest
✓ Snapshot saved: .fl-snapshots/latest.json
```

**Without name:** Uses current timestamp

```bash
$ fl snapshot save
✓ Snapshot saved: .fl-snapshots/2026-03-15T14-23-45.json
```

**Snapshot contents:**
```json
{
  "timestamp": "2026-03-15T14:23:45",
  "python_version": "3.13.12",
  "dependencies": ["requests>=2.28", "flask>=3.0"],
  "installed": {
    "requests": "2.32.5",
    "flask": "3.1.3",
    "werkzeug": "3.1.2"
  }
}
```

#### `fl snapshot compare [name]`

Compare current environment against snapshot:

```bash
$ fl snapshot compare production

Comparing against snapshot 'production'...
```

**No changes:**
```
✓ No differences from snapshot
```

**With changes:**
```
Added (1):
  + beautifulsoup4 (4.12.2)

Removed (2):
  - lxml (4.9.0)
  - cssselect (1.2.0)

Updated (2):
  requests     locked: 2.30.0  installed: 2.32.5
  flask        locked: 3.0.0   installed: 3.1.3
```

#### `fl snapshot list`

List all saved snapshots:

```bash
$ fl snapshot list

Saved snapshots in .py-snapshots/:
  • production (2026-03-15T14:23:45)
  • dev (2026-03-14T10:12:00)
  • testing (2026-03-10T08:45:30)
```

---

## Global Help

```bash
fl --help
fl -h

usage: fl [-h] {init,add,run,shell,list,remove,upgrade,doctor,purge,search,audit,lock-diff,cache,check,fix,snapshot} ...

Python Project Management

positional arguments:
  {init,add,run,shell,list,remove,upgrade,doctor,purge,search,audit,lock-diff,cache,check,fix,snapshot}
    init              Initialize a new Python project
    add               Add dependencies
    run               Run a Python script
    shell             Enter interactive shell
    list              List dependencies
    remove            Remove dependencies
    upgrade           Upgrade dependencies
    doctor            Check project health
    purge             Clear environment
    search            Search PyPI
    audit             Check for updates
    lock-diff         Compare lock vs. installed
    cache             Manage wheel cache
    check             Check for conflicts
    fix               Auto-repair project
    snapshot          Manage environment snapshots

optional arguments:
  -h, --help          Show this help message
```

```bash
fl <command> --help
fl add --help

usage: fl add [-h] package [package ...]

positional arguments:
  package     Package(s) to add (e.g., requests, flask>=3.0)

optional arguments:
  -h, --help  Show this help message
```

---

## Common Workflow Examples

### Starting a new web project:

```bash
fl init                                    # Initialize
fl add flask flask-cors                    # Add dependencies
fl run web_server.py --port 8000          # Run server
```

### Checking project health:

```bash
fl doctor
fl check
fl audit
```

### CI/CD workflow:

```bash
fl snapshot save ci-baseline               # Save known-good state
# (run tests, skip errors)
fl snapshot compare ci-baseline            # Verify reproducibility
```

### Updating dependencies:

```bash
fl audit                                   # See what's outdated
fl upgrade requests flask                  # Upgrade specific packages
fl check                                   # Verify no conflicts
fl snapshot save upgraded-deps             # Archive new state
```

### Recovering from corruption:

```bash
fl doctor                                  # Identify issues
fl fix                                     # Auto-repair
fl run tests.py                            # Verify it works
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Generic error or command failed |
| `130` | SIGINT (Ctrl+C) |
| `143` | SIGTERM (terminated) |

---

## Tips

1. **Use `-v` for debugging:**
   ```bash
   fl run main.py -v
   ```

2. **Check state quickly:**
   ```bash
   cat .fl.state.json | python3 -m json.tool
   cat .fl.lock.json | python3 -m json.tool
   ```

3. **Save before big changes:**
   ```bash
   fl snapshot save backup
   fl add many-packages
   # If issues: restore manually or use snapshot metadata
   ```

4. **Audit regularly:**
   ```bash
   fl audit  # Check for security updates weekly
   ```

5. **Use snapshots in CI:**
   ```yaml
   - name: Verify environment stability
     run: fl snapshot compare ci-baseline
   ```
