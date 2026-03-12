# Installation & Setup Guide

Quick installation and first-time setup for the `py` tool.

---

## Prerequisites

- **Python 3.8+** (for running py and projects)
- **pip** (usually comes with Python)
- **git** (optional, for cloning)
- **Linux/macOS/Windows (WSL)** (py is designed for Unix-like environments)

### Check Prerequisites

```bash
python3 --version
# Output: Python 3.13.12

pip --version
# Output: pip 24.0 from ...

git --version
# Output: git version 2.44.0
```

---

## Installation Options

### Option 1: Download Directly (Recommended)

```bash
# Download to PATH
curl https://raw.githubusercontent.com/Antonymwangi20/py/main/py -o ~/.local/bin/py
chmod +x ~/.local/bin/py

# Verify
py --version
# Output: py 1.0
```

**Requirements:**
- Must have `~/.local/bin` in `$PATH`
- Check: `echo $PATH | grep ~/.local/bin`

### Option 2: Clone from GitHub

```bash
git clone https://github.com/Antonymwangi20/py.git
cd py

# Install to PATH
cp py ~/.local/bin/py
chmod +x ~/.local/bin/py

# Verify
py --version
```

### Option 3: Install to System Bin (Requires sudo)

```bash
sudo cp py /usr/local/bin/py
sudo chmod +x /usr/local/bin/py

# Verify
py --version
```

### Option 4: Standalone (No PATH Required)

```bash
# Download anywhere
curl https://example.com/py -o ~/py
chmod +x ~/py

# Use with explicit path
~/py init
~/py add requests
```

---

## First-Time Setup

### 1. Verify Installation

```bash
py --help
# Should show all available commands
```

### 2. Create a Test Project

```bash
mkdir ~/test-py && cd ~/test-py
py init

# Output should show:
# ✓ Created pyproject.toml
# ✓ Created .gitignore
```

### 3. Add Your First Dependency

```bash
py add requests

# Output:
# ✓ Added requests
# ✓ Virtual environment created
# ✓ Dependencies installed
```

### 4. Run a Simple Script

```bash
cat > hello.py << 'EOF'
import requests
print(f"requests version: {requests.__version__}")
EOF

py hello.py

# Output: requests version: 2.32.5
```

### 5. Check Project Health

```bash
py doctor

# Output:
# ✓ pyproject.toml syntax OK
# ✓ Python 3.13.12 meets requirement: >=3.8
# ✓ Virtual environment exists
# ✓ 1 dependencies declared
# ✓ All dependencies installed
# ✓ Lock file matches installed packages
# ✓ .gitignore is properly configured
# ✓ State file present
# 
# ✓ everything looks healthy
```

**Success!** Your `py` installation is working.

---

## Configuration

### PATH Setup

If `py --help` doesn't work, add `~/.local/bin` to your PATH:

**Bash/Zsh (~/.bashrc or ~/.zshrc):**
```bash
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc  # or ~/.zshrc
```

**Fish (~/.config/fish/config.fish):**
```fish
set -gx PATH $HOME/.local/bin $PATH
```

### Shell Aliases (Optional)

Add convenient shortcuts to your shell config:

```bash
# ~/.bashrc or ~/.zshrc

# Use 'p' as shorthand
alias p='py'

# Quick project creation
pynew() {
    mkdir "$1" && cd "$1" && py init
}

# Open venv shell
pyvenv() {
    py shell
}
```

Usage:
```bash
p init           # Same as 'py init'
pynew myproject  # Create and init new project
```

---

## Updating py

### Check Current Version

```bash
py --version
# py 1.0
```

### Update from Latest Release

```bash
# Download new version
curl https://raw.githubusercontent.com/Antonymwangi20/py/main/py -o ~/.local/bin/py.new

# Verify it works
python3 ~/.local/bin/py.new --version

# Backup old version (optional)
cp ~/.local/bin/py ~/.local/bin/py.backup

# Replace
mv ~/.local/bin/py.new ~/.local/bin/py

# Verify
py --version
```

---

## Uninstallation

### Remove py

```bash
# Remove executable
rm ~/.local/bin/py

# Or if installed to system:
sudo rm /usr/local/bin/py

# Remove global cache (optional)
rm -rf ~/.cache/py
```

### Keep Project Data

Your projects' files are untouched:
- `pyproject.toml` – Saved
- `.py.state.json` – Saved
- `.py.lock.json` – Saved
- `.venv/` – Remains in project

You can use these with `pip` or other tools afterward.

---

## Troubleshooting Setup

### "Command not found: py"

```bash
# Check if py is in PATH
which py        # Should show path

# If not found:
ls -la ~/.local/bin/py  # Verify file exists

# Add to PATH if missing
export PATH="$HOME/.local/bin:$PATH"
# Add to ~/.bashrc or ~/.zshrc permanently
```

### "Permission denied"

```bash
# Make executable
chmod +x ~/.local/bin/py

# Verify
py --help
```

### "Python 3.8+ not found"

```bash
# Check Python version
python3 --version

# If < 3.8, upgrade:
# Ubuntu/Debian:
sudo apt update && sudo apt install python3.11

# macOS (with brew):
brew install python@3.11

# Or use pyenv:
pyenv install 3.11.0
pyenv global 3.11.0
```

### "~/.local/bin doesn't exist"

```bash
# Create directory
mkdir -p ~/.local/bin

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Make permanent in ~/.bashrc:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### "Can't create .venv"

```bash
# Check if venv module is available
python3 -m venv --help

# If missing, install it:
# Ubuntu/Debian:
sudo apt install python3.11-venv

# Or reinstall Python with venv
```

---

## Verification Checklist

After installation, verify everything works:

```bash
# ✓ py executable found
which py

# ✓ Correct version
py --version

# ✓ Help works
py --help

# ✓ Create test project
mkdir /tmp/py-test && cd /tmp/py-test
py init

# ✓ Add dependency
py add requests

# ✓ Run script
python3 << 'EOF'
import sys
sys.path.insert(0, '.venv/lib/python3.11/site-packages')
import requests
print("✓ requests imported successfully")
EOF

# ✓ Health check
py doctor

# ✓ No lock file issues
py lock-diff

# Cleanup
cd ~ && rm -rf /tmp/py-test
```

If all checks pass: **Installation successful!**

---

## Next Steps

### Read the Documentation

1. **[README.md](README.md)** – Overview and quick start
2. **[COMMAND_REFERENCE.md](COMMAND_REFERENCE.md)** – All commands explained
3. **[EXAMPLES.md](EXAMPLES.md)** – Real-world workflows
4. **[ARCHITECTURE.md](ARCHITECTURE.md)** – How py works (for contributors)
5. **[CONTRIBUTING.md](CONTRIBUTING.md)** – How to contribute

### Start Your First Project

```bash
# Create a new project
mkdir my-project && cd my-project

# Initialize
py init

# Add dependencies for your use case
py add requests flask pandas  # Example

# Run your first script
py main.py

# Check health
py doctor
```

### Join the Community

- Report issues: [GitHub Issues](https://github.com/Antonymwangi20/py/issues)
- Ask questions: [GitHub Discussions](https://github.com/Antonymwangi20/py/discussions)
- Share projects: [GitHub Show & Tell](https://github.com/Antonymwangi20/py/discussions/categories/show-and-tell)

---

## Additional Resources

### Python Resources
- [Python Official Docs](https://docs.python.org/3/)
- [Virtual Environments Guide](https://docs.python.org/3/tutorial/venv.html)
- [PyPI Package Index](https://pypi.org/)

### Related Tools
- [Poetry](https://python-poetry.org/) – Full-featured dependency manager
- [pip-tools](https://github.com/jazzband/pip-tools) – Requirements file management  
- [pyenv](https://github.com/pyenv/pyenv) – Python version manager
- [pipx](https://pypa.github.io/pipx/) – Isolated Python tool installation

---

## FAQ

**Q: Is py a replacement for poetry?**  
A: Not exactly. py is simpler and faster for small projects. Poetry is better for complex multi-package projects.

**Q: Can I use py in CI/CD?**  
A: Yes! Use snapshots to ensure reproducibility. See [CI/CD Integration](EXAMPLES.md#cicd-integration).

**Q: Does py support multiple Python versions?**  
A: py uses the system Python. For multiple versions, use `pyenv` or `conda`.

**Q: Can I install py to a custom location?**  
A: Yes, download to anywhere and use the full path: `/path/to/py init`

**Q: Will updating py break my projects?**  
A: No. Projects store their state in standard formats (JSON, TOML). They'll work with any version of py or other tools.

**Q: How do I uninstall py?**  
A: Just delete the file: `rm ~/.local/bin/py` (your projects remain intact)

---

## Support

Having issues? 

1. Check [COMMAND_REFERENCE.md](COMMAND_REFERENCE.md#troubleshooting) for common problems
2. Run `py doctor` to diagnose project issues
3. Run `py fix` to auto-repair problems
4. Open an issue on GitHub with output from `py doctor`

---

**Happy coding! 🚀**
