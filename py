#!/usr/bin/env python3
"""
py - Python project management without the friction.

A single-file tool that handles environments, dependencies, and execution
the way it should work: invisibly.
"""

import os
import sys
import subprocess
import json
import argparse
import signal
from pathlib import Path
import shutil

# Try to use real TOML parser (Python 3.11+), fallback to manual
try:
    import tomllib
    HAS_TOMLLIB = True
except ImportError:
    HAS_TOMLLIB = False

# Try to use tomlkit for writing (preserves formatting), fallback to manual
try:
    import tomlkit
    HAS_TOMLKIT = True
except ImportError:
    HAS_TOMLKIT = False

VENV_DIR = ".venv"
CONFIG_FILE = "pyproject.toml"
STATE_FILE = ".py.state.json"
LOCK_FILE = ".py.lock.json"

class Colors:
    """Terminal colors for output."""
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    DIM = "\033[2m"

def color(text, color_code):
    """Apply color to text if terminal supports it."""
    if sys.stdout.isatty():
        return f"{color_code}{text}{Colors.RESET}"
    return text

def success(text):
    return color(f"✓ {text}", Colors.GREEN)

def error(text):
    return color(f"✗ {text}", Colors.RED)

def warn(text):
    return color(f"⚠ {text}", Colors.YELLOW)

def dim(text):
    return color(text, Colors.DIM)

def get_venv_path():
    return Path(VENV_DIR).resolve()

def venv_exists():
    venv_path = get_venv_path()
    python_exe = venv_path / "bin" / "python" if os.name != 'nt' else venv_path / "Scripts" / "python.exe"
    return python_exe.exists()

def create_venv():
    print(f"Creating virtual environment in {VENV_DIR}...")
    try:
        subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True, capture_output=True)
        print(success("Virtual environment created"))
        return True
    except subprocess.CalledProcessError as e:
        print(error(f"Failed to create virtual environment: {e}"))
        return False

def get_venv_python():
    venv_path = get_venv_path()
    if os.name == 'nt':
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"

def get_venv_pip():
    venv_path = get_venv_path()
    if os.name == 'nt':
        return venv_path / "Scripts" / "pip.exe"
    return venv_path / "bin" / "pip"

def read_dependencies():
    """Read dependencies using tomllib if available, else manual parsing."""
    if not os.path.exists(CONFIG_FILE):
        return []

    if HAS_TOMLLIB:
        try:
            with open(CONFIG_FILE, 'rb') as f:
                data = tomllib.load(f)
            deps = data.get('project', {}).get('dependencies', [])
            return deps
        except Exception as e:
            print(warn(f"TOML parse failed ({e}), falling back to manual parsing"))
            return _read_dependencies_manual()
    else:
        return _read_dependencies_manual()

def _read_dependencies_manual():
    """Fallback manual TOML parsing for older Python versions."""
    deps = []
    with open(CONFIG_FILE, 'r') as f:
        content = f.read()

    in_deps_section = False
    for line in content.split('\n'):
        line = line.strip()
        if '[project.dependencies]' in line or ('dependencies' in line and '=' in line and '[' in line):
            in_deps_section = True
            continue

        if in_deps_section:
            if line.startswith('[') and 'dependencies' not in line:
                break
            if line.startswith(']') or (line.startswith('[') and not line.startswith('["')):
                break

            if '"' in line or "'" in line:
                line = line.split('#')[0].rstrip(',').strip()
                for quote in ['"', "'"]:
                    if quote in line:
                        parts = line.split(quote)
                        if len(parts) >= 3:
                            dep = parts[1]
                            if dep and not dep.startswith('#'):
                                deps.append(dep)
                            break

    return deps

def write_dependency(package):
    """Add a dependency to pyproject.toml, preserving formatting if possible.

    Handles version specifiers by comparing base names when checking
    for existing entries.
    """
    # base name used for duplicate checks
    base = package.split("[" if "[" in package else "=")[0].strip().lower()

    if HAS_TOMLKIT and HAS_TOMLLIB:
        # when using tomlkit we can inspect existing names easily
        try:
            with open(CONFIG_FILE, 'r') as f:
                doc = tomlkit.parse(f.read())

            if 'project' not in doc:
                doc['project'] = tomlkit.table()
            if 'dependencies' not in doc['project']:
                doc['project']['dependencies'] = tomlkit.array()

            deps = doc['project']['dependencies']
            # preserve duplicates logic by comparing base names
            existing = [d.split("[" if "[" in d else "=")[0].strip().lower() for d in deps]
            if base not in existing:
                deps.append(package)
                with open(CONFIG_FILE, 'w') as f:
                    f.write(tomlkit.dumps(doc))
                return True
            return False
        except Exception:
            pass  # Fall through to manual method

    # Manual TOML editing (fallback)
    with open(CONFIG_FILE, 'r') as f:
        content = f.read()

    lines = content.split('\n')
    new_lines = []
    in_deps = False
    added = False

    for line in lines:
        if 'dependencies' in line and '=' in line and '[' in line:
            in_deps = True
            new_lines.append(line)
            # avoid duplicates by base name
            if base not in content.lower():
                new_lines.append(f'  "{package}",')
                added = True
            continue

        if in_deps and line.strip().startswith(']'):
            in_deps = False

        new_lines.append(line)

    if added:
        with open(CONFIG_FILE, 'w') as f:
            f.write('\n'.join(new_lines))
        return True
    return False

def get_installed_packages(pip_exe):
    """Get dict of {package: version} currently installed in venv."""
    try:
        result = subprocess.run(
            [str(pip_exe), "list", "--format", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        packages = json.loads(result.stdout)
        return {pkg["name"].lower(): pkg["version"] for pkg in packages}
    except Exception:
        return {}

def save_state(deps):
    state = {
        "dependencies": deps,
        "python_version": sys.version,
        "venv_dir": str(get_venv_path())
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def save_lock(installed):
    """Persist a mapping of installed package versions."""
    try:
        with open(LOCK_FILE, 'w') as f:
            json.dump(installed, f, indent=2)
    except Exception:
        pass

def load_lock():
    if not os.path.exists(LOCK_FILE):
        return None
    try:
        with open(LOCK_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return None

def load_state():
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None

def install_dependencies(force=False):
    """Install dependencies, only updating if needed (like pip-sync).

    Compares against both the saved state and the lock file to avoid
    unnecessary pip invocations.  When force is True the checks are skipped.
    """
    deps = read_dependencies()

    if not deps:
        print("No dependencies found in pyproject.toml")
        return True

    if not force:
        state = load_state()
        lock = load_lock()
        if state and state.get("dependencies") == deps and lock:
            # check installed packages against lock file too
            pip = get_venv_pip()
            installed = get_installed_packages(pip)
            if installed == lock:
                print(dim("Dependencies already up to date (lock)"))
                return True
        elif state and state.get("dependencies") == deps:
            print(dim("Dependencies already up to date"))
            return True

    pip = get_venv_pip()

    # Check what's already installed
    installed = get_installed_packages(pip)

    # See which packages need to be installed/updated
    to_install = []
    for dep in deps:
        # Extract base package name (before version specifiers)
        pkg_name = dep.split("[" if "[" in dep else "=")[0].strip().lower()

        # If not installed or has version specifier, install
        if pkg_name not in installed or any(op in dep for op in ["==", "<", ">", "~", "!"]):
            to_install.append(dep)

    if not to_install:
        print(dim("✓ All dependencies already installed"))
        save_state(deps)
        return True

    print(f"Installing {len(to_install)} package(s): {', '.join(to_install)}")

    try:
        subprocess.run([str(pip), "install", "--upgrade", "pip"],
                      capture_output=True, check=False)

        cmd = [str(pip), "install", "--upgrade", "--upgrade-strategy=only-if-needed"] + to_install
        result = subprocess.run(cmd, check=True)

        # refresh installed list and lock file
        installed = get_installed_packages(pip)
        save_state(deps)
        save_lock(installed)
        print(success("Dependencies installed"))
        return True
    except subprocess.CalledProcessError as e:
        print(error(f"Failed to install dependencies: {e}"))
        return False


def ensure_environment():
    """Ensure venv exists and dependencies are installed."""
    if not venv_exists():
        if not create_venv():
            return False

    return install_dependencies()

def exec_command(args):
    """Execute command, replacing current process (Unix) or spawning (Windows)."""
    if not ensure_environment():
        sys.exit(1)

    python = get_venv_python()
    cmd = [str(python)] + args

    # On Unix, replace current process for clean signal handling
    if os.name != 'nt' and hasattr(os, 'execvp'):
        # Reset signal handlers before exec
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        os.execvp(cmd[0], cmd)
    else:
        # Windows: spawn and wait
        try:
            result = subprocess.run(cmd)
            sys.exit(result.returncode)
        except KeyboardInterrupt:
            sys.exit(130)


def query_pypi(package_name, timeout=5):
    """Query PyPI JSON API for package info. Returns dict or None on error."""
    import urllib.request
    import urllib.error
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return json.loads(response.read().decode('utf-8'))
    except (urllib.error.HTTPError, urllib.error.URLError, Exception):
        return None


def search_pypi(query, limit=10, timeout=5):
    """Search PyPI by querying exact package."""
    try:
        result = query_pypi(query, timeout=timeout)
        if result:
            return [(result["info"]["name"], result["info"]["version"], result["info"]["summary"])]
        return []
    except Exception:
        return []


def get_outdated_packages(installed_dict):
    """Check which installed packages have newer versions on PyPI."""
    outdated = []
    for pkg_name, version in installed_dict.items():
        data = query_pypi(pkg_name, timeout=3)
        if data:
            latest = data["info"]["version"]
            if latest != version:
                outdated.append((pkg_name, version, latest))
    return outdated


def validate_toml_syntax():
    """Check if pyproject.toml is valid TOML. Returns (is_valid, error_msg)."""
    if not os.path.exists(CONFIG_FILE):
        return (True, None)
    try:
        if HAS_TOMLLIB:
            with open(CONFIG_FILE, 'rb') as f:
                tomllib.load(f)
        else:
            with open(CONFIG_FILE, 'r') as f:
                content = f.read()
                if '[project]' not in content:
                    return (False, "Missing [project] section")
        return (True, None)
    except Exception as e:
        return (False, str(e))


def check_python_version_constraint():
    """Extract requires-python from pyproject.toml and check if current Python matches."""
    try:
        if not os.path.exists(CONFIG_FILE):
            return (True, sys.version.split()[0], None)
        if HAS_TOMLLIB:
            with open(CONFIG_FILE, 'rb') as f:
                data = tomllib.load(f)
                spec = data.get('project', {}).get('requires-python')
                if spec:
                    return (check_version_spec(sys.version_info, spec), sys.version.split()[0], spec)
        return (True, sys.version.split()[0], None)
    except Exception:
        return (True, sys.version.split()[0], None)


def check_version_spec(version_info, spec):
    """Simple version spec checker. Supports >=, <=, ==, ~=, !=."""
    import re
    current = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    for clause in spec.split(','):
        clause = clause.strip()
        match = re.match(r'^([><=!~]+)([0-9.]+)$', clause)
        if not match:
            continue
        op, ver = match.groups()
        current_tuple = tuple(map(int, current.split('.')[:2]))
        ver_tuple = tuple(map(int, ver.split('.')[:2]))
        if op == '>=' and current_tuple < ver_tuple:
            return False
        elif op == '<=' and current_tuple > ver_tuple:
            return False
        elif op == '==' and current_tuple != ver_tuple:
            return False
        elif op == '<' and current_tuple >= ver_tuple:
            return False
        elif op == '>' and current_tuple <= ver_tuple:
            return False
    return True


def format_search_results(results):
    """Format search results as a nice table."""
    if not results:
        return "No packages found."
    lines = ["\nResults:"]
    for pkg_name, version, summary in results:
        summary_short = (summary[:60] + '...') if len(summary) > 60 else summary
        lines.append(f"  {pkg_name:<30} {version:<15} {summary_short}")
    return "\n".join(lines)


def get_cache_dir():
    """Get or create ~/.cache/py directory."""
    cache_dir = os.path.expanduser("~/.cache/py")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir

def cmd_cache(args):
    """Manage global wheel cache."""
    cache_dir = get_cache_dir()
    if hasattr(args, 'action') and args.action == 'prune':
        now = __import__('time').time()
        thirty_days = 30 * 24 * 60 * 60
        removed = 0
        for fname in os.listdir(cache_dir):
            fpath = os.path.join(cache_dir, fname)
            if os.path.isfile(fpath) and fpath.endswith('.whl'):
                if now - os.path.getmtime(fpath) > thirty_days:
                    os.remove(fpath)
                    removed += 1
        print(success(f"Pruned {removed} old wheels"))
    else:
        wheels = [f for f in os.listdir(cache_dir) if f.endswith('.whl')]
        if wheels:
            total_size = sum(os.path.getsize(os.path.join(cache_dir, f)) for f in wheels)
            size_mb = total_size / (1024 * 1024)
            print(f"Cache directory: {cache_dir}")
            print(f"Wheels cached: {len(wheels)}")
            print(f"Total size: {size_mb:.2f} MB")
        else:
            print("Cache is empty")


def parse_dep_spec(dep_str):
    """Parse dependency string into (package_name, version_spec)."""
    import re
    dep = dep_str.split('[')[0]
    match = re.match(r'^([a-zA-Z0-9_-]+)(.*)', dep)
    if match:
        pkg_name = match.group(1).lower()
        version_spec = match.group(2).strip() or None
        return (pkg_name, version_spec)
    return (dep.lower(), None)

def check_dependency_conflicts(deps_list):
    """Check for conflicting dependency specifications."""
    from collections import defaultdict
    conflicts = defaultdict(set)
    
    for dep in deps_list:
        pkg_name, version_spec = parse_dep_spec(dep)
        if version_spec:
            conflicts[pkg_name].add(version_spec)
    
    result = []
    for pkg, specs in conflicts.items():
        if len(specs) > 1:
            result.append((pkg, list(specs)))
    
    return result

def cmd_check(args):
    """Enhanced dependency checking with conflict detection."""
    print("Analyzing dependencies...\n")
    
    deps = read_dependencies()
    if not deps:
        print("No dependencies declared")
        return
    
    conflicts = check_dependency_conflicts(deps)
    if conflicts:
        print(warn("Dependency conflicts found:"))
        for pkg, specs in conflicts:
            print(f"  {pkg}: {', '.join(specs)}")
        print()
    
    valid_ops = ['>=', '<=', '==', '!=', '~=', '>', '<']
    for dep in deps:
        pkg, spec = parse_dep_spec(dep)
        if spec and not any(op in spec for op in valid_ops):
            print(warn(f"Invalid version spec: {dep}"))
    
    if not conflicts:
        print(success("No dependency conflicts detected"))


def auto_fix_gitignore():
    """Auto-create or fix .gitignore if missing required entries."""
    required = [VENV_DIR, STATE_FILE, "__pycache__/", "*.pyc", LOCK_FILE]
    
    if os.path.exists(".gitignore"):
        with open(".gitignore", 'r') as f:
            content = f.read()
        missing = [r for r in required if r not in content]
        if missing:
            with open(".gitignore", 'a') as f:
                f.write("\n# Added by py auto-fix\n")
                for item in missing:
                    f.write(f"{item}\n")
            print(success(f"Fixed .gitignore (added {len(missing)} entries)"))
            return True
    else:
        with open(".gitignore", 'w') as f:
            for item in required:
                f.write(f"{item}\n")
        print(success("Created .gitignore"))
        return True
    
    return False

def auto_fix_toml():
    """Try to auto-fix common TOML issues."""
    if not os.path.exists(CONFIG_FILE):
        return False
    
    valid, error_msg = validate_toml_syntax()
    if valid:
        return False
    
    with open(CONFIG_FILE, 'r') as f:
        content = f.read()
    
    if '[project]' not in content:
        content = '[project]\nname = "default"\n\n' + content
        print(warn("Added missing [project] section"))
    
    if 'dependencies' not in content:
        if '[project]' in content:
            idx = content.find('[project]')
            end_idx = content.find('\n', idx) + 1
            content = content[:end_idx] + "dependencies = []\n\n" + content[end_idx:]
            print(warn("Added missing dependencies list"))
    
    try:
        with open(CONFIG_FILE, 'w') as f:
            f.write(content)
        valid, _ = validate_toml_syntax()
        if valid:
            print(success("TOML fixed"))
            return True
    except Exception:
        pass
    
    return False

def cmd_fix(args):
    """Auto-fix common project issues."""
    print("Scanning for issues...\n")
    
    fixed = 0
    
    if auto_fix_gitignore():
        fixed += 1
    
    if auto_fix_toml():
        fixed += 1
    
    if os.path.exists(CONFIG_FILE):
        if not os.path.exists(STATE_FILE):
            save_state(read_dependencies())
            print(success("Recreated state file"))
            fixed += 1
        
        if not os.path.exists(LOCK_FILE) and venv_exists():
            pip = get_venv_pip()
            installed = get_installed_packages(pip)
            save_lock(installed)
            print(success("Recreated lock file"))
            fixed += 1
    
    if fixed == 0:
        print("No issues found")
    else:
        print(f"\n{success(f'Fixed {fixed} issue(s)')}")


SNAPSHOT_DIR = ".py-snapshots"

def get_snapshot_path(name):
    """Get path to named snapshot."""
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    return os.path.join(SNAPSHOT_DIR, f"{name}.json")

def cmd_snapshot(args):
    """Manage environment snapshots for CI/reproducibility."""
    if not hasattr(args, 'snapshot_cmd'):
        print("Usage: py snapshot [save|compare|list]")
        return
    
    if args.snapshot_cmd == 'save':
        if not venv_exists():
            print(warn("No venv found; run 'py init' first"))
            return
        
        pip = get_venv_pip()
        installed = get_installed_packages(pip)
        deps = read_dependencies()
        
        snapshot = {
            "timestamp": __import__('time').time(),
            "python_version": sys.version.split()[0],
            "dependencies": deps,
            "installed": installed,
        }
        
        snapshot_name = args.name if hasattr(args, 'name') and args.name else "latest"
        snap_path = get_snapshot_path(snapshot_name)
        
        with open(snap_path, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        print(success(f"Snapshot saved: {snap_path}"))
    
    elif args.snapshot_cmd == 'compare':
        if not venv_exists():
            print(warn("No venv found"))
            return
        
        snapshot_name = args.name if hasattr(args, 'name') and args.name else "latest"
        snap_path = get_snapshot_path(snapshot_name)
        
        if not os.path.exists(snap_path):
            print(error(f"Snapshot '{snapshot_name}' not found"))
            return
        
        with open(snap_path, 'r') as f:
            snapshot = json.load(f)
        
        pip = get_venv_pip()
        current_installed = get_installed_packages(pip)
        saved_installed = snapshot.get('installed', {})
        
        print(f"Comparing against snapshot '{snapshot_name}'...\n")
        
        added = set(current_installed.keys()) - set(saved_installed.keys())
        removed = set(saved_installed.keys()) - set(current_installed.keys())
        changed = [p for p in set(current_installed.keys()) & set(saved_installed.keys())
                   if current_installed[p] != saved_installed[p]]
        
        has_diff = bool(added or removed or changed)
        
        if added:
            print(warn(f"Added ({len(added)}):"))
            for pkg in sorted(added):
                print(f"  + {pkg} {current_installed[pkg]}")
        
        if removed:
            print(warn(f"Removed ({len(removed)}):"))
            for pkg in sorted(removed):
                print(f"  - {pkg} {saved_installed[pkg]}")
        
        if changed:
            print(warn(f"Updated ({len(changed)}):"))
            for pkg in sorted(changed):
                print(f"  {pkg}: {saved_installed[pkg]} → {current_installed[pkg]}")
        
        if not has_diff:
            print(success("No differences from snapshot"))
    
    elif args.snapshot_cmd == 'list':
        if os.path.exists(SNAPSHOT_DIR):
            snaps = [f.replace('.json', '') for f in os.listdir(SNAPSHOT_DIR) if f.endswith('.json')]
            if snaps:
                print("Saved snapshots:")
                for snap in sorted(snaps):
                    print(f"  • {snap}")
            else:
                print("No snapshots saved")
        else:
            print("No snapshots saved")



def cmd_init(args):
    if os.path.exists(CONFIG_FILE):
        print(f"{CONFIG_FILE} already exists")
        return

    project_name = Path.cwd().name

    toml_content = f"""[project]
name = "{project_name}"
version = "0.1.0"
description = "Add your description here"
requires-python = ">=3.8"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""

    with open(CONFIG_FILE, 'w') as f:
        f.write(toml_content)

    print(success(f"Created {CONFIG_FILE}"))

    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        with open(gitignore_path, 'w') as f:
            f.write(f"{VENV_DIR}/\n{STATE_FILE}\n__pycache__/\n*.pyc\n*.egg-info/\ndist/\nbuild/\n")
        print(success("Created .gitignore"))

def cmd_add(args):
    if not args.packages:
        print("Usage: py add <package> [package2 ...]")
        return

    if not os.path.exists(CONFIG_FILE):
        cmd_init(args)

    added_any = False
    for package in args.packages:
        if write_dependency(package):
            print(success(f"Added {package}"))
            added_any = True
        else:
            print(f"{package} already in dependencies")

    if added_any:
        if venv_exists() or create_venv():
            install_dependencies(force=True)

def cmd_run(args):
    if not args.script:
        print("Usage: py run <script.py> [args...]")
        return

    if not Path(args.script).exists():
        print(error(f"Script '{args.script}' not found"))
        sys.exit(1)

    script_args = [args.script] + (args.args or [])

    if args.verbose:
        python = get_venv_python()
        print(dim(f"Using: {python}"))

    exec_command(script_args)

def cmd_shell(args):
    if not ensure_environment():
        return

    venv_path = get_venv_path()

    if os.name == 'nt':
        activate = venv_path / "Scripts" / "activate.bat"
        print(f"Run: {activate}")
        subprocess.run(["cmd", "/k", str(activate)])
    else:
        shell = os.environ.get('SHELL', '/bin/bash')
        print(f"Entering project environment ({VENV_DIR})")
        print(dim("Type 'exit' to leave"))

        env = os.environ.copy()
        env['VIRTUAL_ENV'] = str(venv_path)
        env['PATH'] = str(venv_path / "bin") + os.pathsep + env.get('PATH', '')
        env['PS1'] = f"({VENV_DIR}) $ "

        subprocess.run([shell], env=env)

def _modify_dependencies(modifier):
    """Utility that reads pyproject, lets modifier(list) edit deps, and writes back."""
    if not os.path.exists(CONFIG_FILE):
        return False
    try:
        if HAS_TOMLLIB:
            with open(CONFIG_FILE, 'rb') as f:
                data = tomllib.load(f)
            deps = data.get('project', {}).get('dependencies', [])
            new_deps = modifier(deps[:])  # copy
            if new_deps != deps:
                data.setdefault('project', {})['dependencies'] = new_deps
                if HAS_TOMLKIT:
                    # round-trip using tomlkit to preserve formatting
                    with open(CONFIG_FILE, 'r') as f:
                        text = f.read()
                    doc = tomlkit.parse(text)
                    doc['project']['dependencies'] = tomlkit.array(new_deps)
                    with open(CONFIG_FILE, 'w') as f:
                        f.write(tomlkit.dumps(doc))
                else:
                    # simple rewrite
                    with open(CONFIG_FILE, 'w') as f:
                        toml_content = """[project]
"""
                        # naive rewrite if needed; but since tomllib can't dump we use manual
                        f.write(f"[project]\ndependencies = {new_deps}\n")
                return True
            return False
        else:
            # fallback simple text manipulation
            with open(CONFIG_FILE, 'r') as f:
                lines = f.readlines()
            out_lines = []
            in_deps = False
            old_deps = []
            for line in lines:
                if 'dependencies' in line and '=' in line and '[' in line:
                    in_deps = True
                    out_lines.append(line)
                    continue
                if in_deps and line.strip().startswith(']'):
                    in_deps = False
                    continue
                if in_deps and ('"' in line or "'" in line):
                    dep = line.strip().strip(',').strip().strip('"').strip("'")
                    old_deps.append(dep)
                    continue
                out_lines.append(line)
            new_deps = modifier(old_deps[:])
            if new_deps != old_deps:
                # simple rewrite: replace entire section
                start = False
                for line in lines:
                    if not start and 'dependencies' in line and '=' in line and '[' in line:
                        out_lines = []
                        out_lines.append(line)
                        for d in new_deps:
                            out_lines.append(f'  "{d}",\n')
                        out_lines.append(']\n')
                        start = True
                        continue
                with open(CONFIG_FILE, 'w') as f:
                    f.writelines(out_lines)
                return True
            return False
    except Exception:
        return False


def cmd_list(args):
    """List installed dependencies."""
    deps = read_dependencies()
    if not deps:
        print("No dependencies configured")
        return

    print("Dependencies:")
    for dep in deps:
        print(f"  • {dep}")

    if venv_exists():
        pip = get_venv_pip()
        try:
            result = subprocess.run([str(pip), "list", "--format=freeze"],
                                  capture_output=True, text=True, check=True)
            installed = result.stdout.strip().split('\n')
            print(f"\n{dim(f'Installed ({len(installed)} packages)')}")
        except subprocess.CalledProcessError:
            pass

    # show lock info if available
    lock = load_lock()
    if lock is not None:
        print(dim(f"Lock records {len(lock)} packages"))

def cmd_doctor(args):
    """Run diagnostics on the project environment with enhanced checks."""
    ok = True
    print("Examining project...\n")
    
    # Check TOML syntax
    is_valid, error_msg = validate_toml_syntax()
    if not is_valid:
        print(warn(f"TOML syntax error: {error_msg}"))
        ok = False
    else:
        print(success("pyproject.toml syntax OK"))
    
    # Check Python version constraint
    py_ok, current_py, req_spec = check_python_version_constraint()
    if not py_ok:
        print(warn(f"Python {current_py} does not meet requirement: {req_spec}"))
        ok = False
    else:
        if req_spec:
            print(success(f"Python {current_py} meets requirement: {req_spec}"))
        else:
            print(f"Python version: {current_py}")
    
    # Check venv
    if not venv_exists():
        print(warn("virtual environment is missing"))
        ok = False
    else:
        print(success("virtual environment exists"))

    # Check dependencies
    deps = read_dependencies()
    if deps:
        print(f"{len(deps)} dependencies declared in {CONFIG_FILE}")
        if venv_exists():
            pip = get_venv_pip()
            installed = get_installed_packages(pip)
            for dep in deps:
                pkg = dep.split("[" if "[" in dep else "=")[0].strip().lower()
                if pkg not in installed:
                    print(warn(f"{pkg} is not installed"))
                    ok = False
            lock = load_lock()
            if lock is None:
                print(warn("no lock file present"))
                ok = False
            elif installed != lock:
                print(warn("installed packages differ from lock file"))
                ok = False
            else:
                print(success("lock file matches installed packages"))
    else:
        print("no dependencies declared")

    # Check .gitignore
    if os.path.exists(".gitignore"):
        with open(".gitignore", 'r') as f:
            gitignore_content = f.read()
            if VENV_DIR in gitignore_content and LOCK_FILE in gitignore_content:
                print(success(".gitignore is properly configured"))
            else:
                print(warn(".gitignore missing venv or lock file entry"))
                ok = False
    else:
        print(warn(".gitignore not found"))
        ok = False

    state = load_state()
    if state is None:
        print(warn("no state file present"))
        ok = False
    else:
        print(success("state file present"))

    print()
    if ok:
        print(success("everything looks healthy"))
    else:
        print(warn("some issues detected"))

def cmd_remove(args):
    """Remove one or more packages from project and environment."""
    if not args.packages:
        print("Usage: py remove <pkg> [pkg2 ...]")
        return
    removed_any = False
    for pkg in args.packages:
        base = pkg.split("[" if "[" in pkg else "=")[0].strip().lower()
        def modifier(deps):
            return [d for d in deps if not d.lower().startswith(base)]
        if _modify_dependencies(modifier):
            print(success(f"Removed {pkg} from {CONFIG_FILE}"))
            removed_any = True
        else:
            print(f"{pkg} not found in {CONFIG_FILE}")
    if removed_any and venv_exists():
        pip = get_venv_pip()
        subprocess.run([str(pip), "uninstall", "-y"] + args.packages)
        install_dependencies(force=True)


def cmd_upgrade(args):
    """Upgrade packages in the environment; adds to pyproject if missing."""
    if not args.packages:
        print("Usage: py upgrade <pkg> [pkg2 ...]")
        return
    if not venv_exists() and not create_venv():
        return
    pip = get_venv_pip()
    subprocess.run([str(pip), "install", "--upgrade"] + args.packages)
    # ensure they're in project file
    for pkg in args.packages:
        write_dependency(pkg)
    install_dependencies(force=True)


def cmd_purge(args):
    """Remove all dependencies and uninstall everything from venv."""
    if os.path.exists(CONFIG_FILE):
        def modifier(deps):
            return []
        _modify_dependencies(modifier)
        print(success(f"Cleared dependencies in {CONFIG_FILE}"))
    if venv_exists():
        # simply remove the whole virtualenv directory; easier and avoids
        # uninstalling pip itself which leaves the env broken.
        try:
            shutil.rmtree(VENV_DIR)
            print(success("Removed virtual environment"))
        except Exception:
            print(warn("Failed to remove virtual environment, continuing"))
    save_lock({})
    save_state([])
    print(success("Environment purged"))


def cmd_audit(args):
    """Audit dependencies for outdated packages."""
    if not venv_exists():
        print(warn("virtual environment not found; run 'py init' first"))
        return
    
    pip = get_venv_pip()
    installed = get_installed_packages(pip)
    
    if not installed:
        print("No packages installed")
        return
    
    print(f"Checking {len(installed)} packages for updates...")
    outdated = get_outdated_packages(installed)
    
    if outdated:
        print(warn(f"Found {len(outdated)} outdated package(s):\n"))
        for pkg, current, latest in outdated:
            print(f"  {pkg:<25} {current:<15} → {latest}")
        print(f"\nRun 'py upgrade {outdated[0][0]}' to update a package")
    else:
        print(success("All packages are up to date"))


def cmd_lock_diff(args):
    """Show differences between lock file and installed packages."""
    if not venv_exists():
        print(warn("virtual environment not found"))
        return
    
    lock = load_lock()
    if lock is None:
        print(warn("No lock file present"))
        return
    
    pip = get_venv_pip()
    installed = get_installed_packages(pip)
    
    print("Comparing lock file to installed packages...\n")
    
    # Find differences
    in_lock_only = set(lock.keys()) - set(installed.keys())
    in_installed_only = set(installed.keys()) - set(lock.keys())
    version_mismatches = []
    
    for pkg in set(lock.keys()) & set(installed.keys()):
        if lock[pkg] != installed[pkg]:
            version_mismatches.append((pkg, lock[pkg], installed[pkg]))
    
    has_diff = bool(in_lock_only or in_installed_only or version_mismatches)
    
    if in_lock_only:
        print(warn(f"In lock file but not installed ({len(in_lock_only)}):"))
        for pkg in sorted(in_lock_only):
            print(f"  - {pkg} {lock[pkg]}")
        print()
    
    if in_installed_only:
        print(warn(f"Installed but not in lock file ({len(in_installed_only)}):"))
        for pkg in sorted(in_installed_only):
            print(f"  + {pkg} {installed[pkg]}")
        print()
    
    if version_mismatches:
        print(warn(f"Version mismatches ({len(version_mismatches)}):"))
        for pkg, lock_ver, inst_ver in version_mismatches:
            print(f"  {pkg:<25} lock: {lock_ver:<15} installed: {inst_ver}")
        print()
    
    if not has_diff:
        print(success("Lock file and installed packages match"))
    else:
        print("Run 'py install --force' to sync to dependencies")


def cmd_search(args):
    """Search PyPI for a package name using the JSON API."""
    if not args.query:
        print("Usage: py search <term>")
        return
    print(f"Searching PyPI for '{args.query}'...")
    results = search_pypi(args.query)
    if results:
        print(format_search_results(results))
        for pkg_name, version, summary in results:
            print(f"\nTo add: py add {pkg_name}")
    else:
        print(warn(f"No packages found matching '{args.query}'"))


def main():
    # CRITICAL: Check for direct script execution BEFORE argparse to avoid "invalid choice" errors
    if len(sys.argv) > 1:
        first_arg = sys.argv[1]
        
        # Handle help flags
        if first_arg in ['-h', '--help', 'help']:
            # Fall through to normal argparse help below
            pass
        # Handle direct .py execution
        elif first_arg.endswith('.py'):
            if not Path(first_arg).exists():
                print(error(f"Script '{first_arg}' not found"))
                sys.exit(1)

            # Build args object and run directly
            class DirectArgs:
                script = first_arg
                args = sys.argv[2:]
                verbose = '-v' in sys.argv or '--verbose' in sys.argv

            cmd_run(DirectArgs())
            return

    parser = argparse.ArgumentParser(
        description='py - Python project management without the friction',
        prog='py',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  py init                 # Initialize new project
  py add requests flask   # Add dependencies
  py main.py              # Run script (auto-detected)
  py run main.py -v       # Run with verbose output
  py shell                # Enter project environment
  py list                 # Show dependencies
  py doctor               # Diagnose environment
  py remove pkg           # Remove dependency
  py upgrade pkg          # Upgrade a package
  py purge                # Cleans environment
  py search requests      # Search PyPI
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # init
    subparsers.add_parser('init', help='Initialize a new project')

    # add
    add_parser = subparsers.add_parser('add', help='Add dependencies')
    add_parser.add_argument('packages', nargs='+', help='Package names')

    # run
    run_parser = subparsers.add_parser('run', help='Run a Python script')
    run_parser.add_argument('script', help='Script to run')
    run_parser.add_argument('args', nargs=argparse.REMAINDER, help='Arguments')
    run_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose')

    # shell
    subparsers.add_parser('shell', help='Open shell in environment')

    # list
    subparsers.add_parser('list', help='List dependencies')

    # doctor
    subparsers.add_parser('doctor', help='Diagnose project environment')

    # remove
    rem = subparsers.add_parser('remove', help='Remove dependencies')
    rem.add_argument('packages', nargs='+', help='Package names')

    # upgrade
    upg = subparsers.add_parser('upgrade', help='Upgrade packages')
    upg.add_argument('packages', nargs='+', help='Package names')

    # purge
    subparsers.add_parser('purge', help='Remove all dependencies and clear environment')

    # search
    search_parser = subparsers.add_parser('search', help='Search PyPI')
    search_parser.add_argument('query', help='Search term')

    # audit
    subparsers.add_parser('audit', help='Check for outdated packages')

    # lock-diff
    subparsers.add_parser('lock-diff', help='Show lock file differences')

    # cache
    cache_parser = subparsers.add_parser('cache', help='Manage global wheel cache')
    cache_parser.add_argument('action', nargs='?', default='info', choices=['info', 'prune'], help='Cache action')

    # check
    subparsers.add_parser('check', help='Check for dependency conflicts')

    # fix
    subparsers.add_parser('fix', help='Auto-fix common project issues')

    # snapshot
    snap_parser = subparsers.add_parser('snapshot', help='Manage environment snapshots')
    snap_parser.add_argument('snapshot_cmd', nargs='?', default='list', choices=['save', 'compare', 'list'])
    snap_parser.add_argument('name', nargs='?', default='latest', help='Snapshot name')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        'init': cmd_init,
        'add': cmd_add,
        'run': cmd_run,
        'shell': cmd_shell,
        'list': cmd_list,
        'doctor': cmd_doctor,
        'remove': cmd_remove,
        'upgrade': cmd_upgrade,
        'purge': cmd_purge,
        'search': cmd_search,
        'audit': cmd_audit,
        'lock-diff': cmd_lock_diff,
        'cache': cmd_cache,
        'check': cmd_check,
        'fix': cmd_fix,
        'snapshot': cmd_snapshot,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
