#!/bin/bash
# Makefile-like build tasks for py
# Usage: bash tasks.sh <task> [args...]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
RESET='\033[0m'

echo_task() {
    echo -e "${BLUE}▶${RESET} $1"
}

echo_success() {
    echo -e "${GREEN}✓${RESET} $1"
}

echo_error() {
    echo -e "${RED}✗${RESET} $1" >&2
}

# Check syntax
task_check() {
    echo_task "Checking Python syntax..."
    python3 -m py_compile py
    echo_success "Syntax OK"
}

# Run tests
task_test() {
    echo_task "Running tests..."
    mkdir -p /tmp/py-test-$$
    cd /tmp/py-test-$$
    
    python3 "$SCRIPT_DIR/py" init || {
        echo_error "init failed"
        return 1
    }
    python3 "$SCRIPT_DIR/py" add requests || {
        echo_error "add failed"
        return 1
    }
    python3 "$SCRIPT_DIR/py" list || {
        echo_error "list failed"
        return 1
    }
    python3 "$SCRIPT_DIR/py" doctor || {
        echo_error "doctor failed"
        return 1
    }
    
    cd - > /dev/null
    rm -rf /tmp/py-test-$$
    echo_success "All tests passed"
}

# Build distribution
task_build() {
    echo_task "Building distribution..."
    pip install --quiet build
    python -m build
    echo_success "Built to dist/"
    ls -lh dist/
}

# Test installer locally
task_test_install() {
    echo_task "Testing local installation..."
    rm -rf /tmp/py-install-test
    mkdir /tmp/py-install-test
    cp py install.sh /tmp/py-install-test/
    cd /tmp/py-install-test
    
    bash install.sh || {
        echo_error "Installation failed"
        cd - > /dev/null
        return 1
    }
    
    # Check if installed
    if [[ -x ~/.local/bin/py ]]; then
        echo_success "Installed to ~/.local/bin/py"
        ~/.local/bin/py --version
    fi
    
    cd - > /dev/null
    rm -rf /tmp/py-install-test
}

# Create release
task_release() {
    local version="${1:?Version required: task_release v2.0.0}"
    
    echo_task "Creating release $version..."
    
    # Check if clean working tree
    if [[ -n $(git status -s) ]]; then
        echo_error "Working tree not clean. Commit changes first."
        return 1
    fi
    
    # Update version in setup.py
    sed -i "s/version='.*'/version='$version'/" setup.py
    
    # Commit version bump
    git add setup.py
    git commit -m "Bump version to $version"
    
    # Create tag
    git tag -a "$version" -m "Release $version"
    
    echo_success "Release $version created"
    echo "Next: git push origin main && git push origin --tags"
}

# Publish to PyPI
task_publish() {
    echo_task "Publishing to PyPI..."
    
    if [[ ! -d dist/ ]]; then
        echo_error "dist/ not found. Run: tasks.sh build"
        return 1
    fi
    
    pip install --quiet twine
    twine upload dist/*
    
    echo_success "Published to PyPI"
}

# Lint code
task_lint() {
    echo_task "Linting..."
    
    if command -v pylint &> /dev/null; then
        pylint py --disable=all --enable=syntax-error || true
    else
        echo_error "pylint not installed: pip install pylint"
    fi
    
    if command -v flake8 &> /dev/null; then
        flake8 py --max-line-length=120 || true
    else
        echo_error "flake8 not installed: pip install flake8"
    fi
}

# Format code
task_format() {
    echo_task "Formatting..."
    
    if command -v black &> /dev/null; then
        black py
        echo_success "Formatted with black"
    else
        echo_error "black not installed: pip install black"
    fi
}

# Clean build artifacts
task_clean() {
    echo_task "Cleaning..."
    rm -rf dist/ build/ *.egg-info
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    echo_success "Cleaned"
}

# Show help
task_help() {
    cat << 'EOF'
py Build Tasks

Usage: bash tasks.sh <task> [args...]

Tasks:
  check         - Check Python syntax
  test          - Run functional tests
  lint          - Lint code (pylint, flake8)
  format        - Format code (black)
  build         - Build distribution (wheel + sdist)
  test-install  - Test installer locally
  release       - Create release (requires version tag)
  publish       - Upload to PyPI
  clean         - Remove build artifacts
  help          - Show this help

Examples:
  bash tasks.sh check       # Verify syntax
  bash tasks.sh test        # Run tests
  bash tasks.sh build       # Build distribution
  bash tasks.sh release v1.0.0  # Create release tag

Full workflow:
  bash tasks.sh check
  bash tasks.sh lint
  bash tasks.sh test
  bash tasks.sh build
  bash tasks.sh release v1.1.0
  git push origin --all --tags
  bash tasks.sh publish
EOF
}

# Main
main() {
    local task="${1:-help}"
    
    case "$task" in
        check) task_check ;;
        test) task_test ;;
        lint) task_lint ;;
        format) task_format ;;
        build) task_build ;;
        test-install) task_test_install ;;
        release) task_release "$2" ;;
        publish) task_publish ;;
        clean) task_clean ;;
        help|--help|-h) task_help ;;
        *)
            echo_error "Unknown task: $task"
            task_help
            return 1
            ;;
    esac
}

main "$@"
