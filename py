#!/usr/bin/env python3
import os
import sys
import subprocess
import json
import argparse
from pathlib import Path

VENV_DIR = ".venv"
CONFIG_FILE = "pyproject.toml"
STATE_FILE = ".py.state.json"

def get_venv_path():
    return Path(VENV_DIR).resolve()

def venv_exists():
    venv_path = get_venv_path()
    python_exe = venv_path / "bin" / "python" if os.name != 'nt' else venv_path / "Scripts" / "python.exe"
    return python_exe.exists()

def create_venv():
    print(f"Creating virtual environment in {VENV_DIR}...")
    try:
        subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)
        print("✓ Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create virtual environment: {e}")
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
    deps = []
    if not os.path.exists(CONFIG_FILE):
        return deps
    
    with open(CONFIG_FILE, 'r') as f:
        content = f.read()
    
    in_deps_section = False
    for line in content.split('\n'):
        line = line.strip()
        if '[project.dependencies]' in line or 'dependencies = [' in line:
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

def save_state(deps):
    state = {
        "dependencies": deps,
        "python_version": sys.version
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def load_state():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def install_dependencies(force=False):
    deps = read_dependencies()
    
    if not deps:
        print("No dependencies found in pyproject.toml")
        return True
    
    if not force:
        state = load_state()
        if state and state.get("dependencies") == deps:
            print("Dependencies already up to date")
            return True
    
    print(f"Installing dependencies: {', '.join(deps)}")
    pip = get_venv_pip()
    
    try:
        subprocess.run([str(pip), "install", "--upgrade", "pip"], 
                      capture_output=True, check=False)
        
        cmd = [str(pip), "install"] + deps
        result = subprocess.run(cmd, check=True)
        
        save_state(deps)
        print("✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False

def ensure_environment():
    if not venv_exists():
        if not create_venv():
            return False
    
    return install_dependencies()

def run_command(args, verbose=False):
    if not ensure_environment():
        sys.exit(1)
    
    python = get_venv_python()
    
    if verbose:
        print(f"Running with: {python}")
    
    cmd = [str(python)] + args
    try:
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        sys.exit(130)

def cmd_init(args):
    if os.path.exists(CONFIG_FILE):
        print(f"{CONFIG_FILE} already exists")
        return
    
    project_name = Path.cwd().name
    
    toml_content = f'''[project]
name = "{project_name}"
version = "0.1.0"
description = "Add your description here"
requires-python = ">=3.8"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
'''
    
    with open(CONFIG_FILE, 'w') as f:
        f.write(toml_content)
    
    print(f"✓ Created {CONFIG_FILE}")
    
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        with open(gitignore_path, 'w') as f:
            f.write(f"{VENV_DIR}/\n{STATE_FILE}\n__pycache__/\n*.pyc\n")
        print("✓ Created .gitignore")

def cmd_add(args):
    if not args.packages:
        print("Usage: py add <package> [package2 ...]")
        return
    
    if not os.path.exists(CONFIG_FILE):
        cmd_init(args)
    
    with open(CONFIG_FILE, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    in_deps = False
    deps_added = False
    
    for line in lines:
        if 'dependencies' in line and '=' in line and '[' in line:
            in_deps = True
            new_lines.append(line)
            for pkg in args.packages:
                if f'"{pkg}"' not in content and f"'{pkg}'" not in content:
                    new_lines.append(f'  "{pkg}",')
                    deps_added = True
            continue
        
        if in_deps and line.strip().startswith(']'):
            in_deps = False
        
        new_lines.append(line)
    
    if deps_added:
        with open(CONFIG_FILE, 'w') as f:
            f.write('\n'.join(new_lines))
        print(f"✓ Added {', '.join(args.packages)} to dependencies")
        
        if venv_exists() or create_venv():
            install_dependencies(force=True)
    else:
        print("Dependencies already present or could not be added")

def cmd_run(args):
    if not args.script:
        print("Usage: py run <script.py> [args...]")
        return
    
    # Check if script exists
    if not Path(args.script).exists():
        print(f"Error: script '{args.script}' not found")
        sys.exit(1)
    
    verbose = args.verbose if hasattr(args, 'verbose') else False
    run_command([args.script] + (args.args or []), verbose=verbose)

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
        print("Type 'exit' to leave.")
        print(f"Virtual env: {venv_path}")
        
        env = os.environ.copy()
        env['VIRTUAL_ENV'] = str(venv_path)
        env['PATH'] = str(venv_path / "bin") + os.pathsep + env.get('PATH', '')
        env['PS1'] = f"({VENV_DIR}) $ "
        
        subprocess.run([shell], env=env)

def main():
    parser = argparse.ArgumentParser(
        description='py - Python project management without the friction',
        prog='py'
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    init_parser = subparsers.add_parser('init', help='Initialize a new project')
    
    add_parser = subparsers.add_parser('add', help='Add dependencies')
    add_parser.add_argument('packages', nargs='+', help='Package names to add')
    
    run_parser = subparsers.add_parser('run', help='Run a Python script')
    run_parser.add_argument('script', help='Python script to run')
    run_parser.add_argument('args', nargs=argparse.REMAINDER, help='Arguments to pass to script')
    run_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    shell_parser = subparsers.add_parser('shell', help='Open shell in virtual environment')
    
    args = parser.parse_args()
    
    # Handle direct script execution: py main.py -> py run main.py
    if not args.command and len(sys.argv) > 1 and sys.argv[1].endswith('.py'):
        # Simulate args for run command
        class DirectArgs:
            script = sys.argv[1]
            args = sys.argv[2:]
            verbose = False
        cmd_run(DirectArgs())
        return
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    commands = {
        'init': cmd_init,
        'add': cmd_add,
        'run': cmd_run,
        'shell': cmd_shell,
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
