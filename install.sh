#!/bin/bash
#
# py - Python Project Management Tool
# Installation script
#
# Usage:
#   curl https://raw.githubusercontent.com/Antonymwangi20/py/main/install.sh | bash
#   OR
#   bash install.sh
#
# This script installs py to ~/.local/bin/py and ensures it's in PATH

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RESET='\033[0m'

# Configuration
REPO_URL="${REPO_URL:-https://raw.githubusercontent.com/Antonymwangi20/py/main}"
INSTALL_DIR="$HOME/.local/bin"
INSTALL_PATH="$INSTALL_DIR/py"
VERSION="1.0"

# Helper functions
log_info() {
    echo -e "${GREEN}✓${RESET} $1"
}

log_error() {
    echo -e "${RED}✗${RESET} $1" >&2
}

log_warn() {
    echo -e "${YELLOW}⚠${RESET} $1"
}

# Check prerequisites
check_prerequisites() {
    echo "Checking prerequisites..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        log_error "python3 not found. Please install Python 3.8+"
        exit 1
    fi
    
    local py_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if [[ $(echo "$py_version < 3.8" | bc -l) -eq 1 ]]; then
        log_error "Python 3.8+ required (found $py_version)"
        exit 1
    fi
    
    log_info "Python $py_version"
    
    # Check if venv module is available
    if ! python3 -m venv --help &> /dev/null; then
        log_error "Python venv module not found"
        log_info "Install with:"
        log_info "  Ubuntu/Debian: sudo apt install python3-venv"
        log_info "  Fedora: sudo dnf install python3-venv"
        exit 1
    fi
    
    log_info "venv module available"
}

# Create install directory
create_install_dir() {
    if [[ ! -d "$INSTALL_DIR" ]]; then
        log_info "Creating $INSTALL_DIR"
        mkdir -p "$INSTALL_DIR" || {
            log_error "Failed to create $INSTALL_DIR"
            exit 1
        }
    fi
}

# Download or use local py script
install_py() {
    echo "Installing py..."
    
    if [[ -f "./py" ]]; then
        # Use local py script
        log_info "Using local py script"
        cp ./py "$INSTALL_PATH"
    else
        # Download from repository
        log_info "Downloading py from $REPO_URL/py"
        
        if command -v curl &> /dev/null; then
            curl -fsSL "$REPO_URL/py" -o "$INSTALL_PATH" || {
                log_error "Failed to download py"
                exit 1
            }
        elif command -v wget &> /dev/null; then
            wget -q "$REPO_URL/py" -O "$INSTALL_PATH" || {
                log_error "Failed to download py"
                exit 1
            }
        else
            log_error "curl or wget required to download py"
            exit 1
        fi
    fi
    
    # Make executable
    chmod +x "$INSTALL_PATH" || {
        log_error "Failed to make $INSTALL_PATH executable"
        exit 1
    }
    
    log_info "Installed to $INSTALL_PATH"
}

# Verify installation
verify_installation() {
    echo "Verifying installation..."
    
    if [[ ! -f "$INSTALL_PATH" ]]; then
        log_error "Installation failed: $INSTALL_PATH not found"
        exit 1
    fi
    
    if [[ ! -x "$INSTALL_PATH" ]]; then
        log_error "Installation failed: $INSTALL_PATH not executable"
        exit 1
    fi
    
    # Test execution
    if ! "$INSTALL_PATH" --version &> /dev/null; then
        log_error "Installation verification failed: py doesn't work"
        exit 1
    fi
    
    log_info "Installation verified"
}

# Add to PATH if needed
setup_path() {
    echo "Setting up PATH..."
    
    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" == *":$INSTALL_DIR:"* ]]; then
        log_info "$INSTALL_DIR already in PATH"
        return
    fi
    
    log_warn "$INSTALL_DIR not in PATH"
    
    # Detect shell config file
    if [[ -n "$ZSH_VERSION" ]]; then
        shell_config="$HOME/.zshrc"
    elif [[ -n "$BASH_VERSION" ]]; then
        shell_config="$HOME/.bashrc"
    else
        shell_config="$HOME/.profile"
    fi
    
    # Add to PATH
    if [[ -f "$shell_config" ]]; then
        if grep -q "local/bin" "$shell_config"; then
            log_info "PATH already configured in $shell_config"
        else
            echo "" >> "$shell_config"
            echo "# Add ~/.local/bin to PATH for py" >> "$shell_config"
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$shell_config"
            log_info "Added to $shell_config"
            log_warn "Run: source $shell_config"
        fi
    else
        log_warn "Could not find shell config file"
        log_info "Add this line to your shell config:"
        log_info 'export PATH="$HOME/.local/bin:$PATH"'
    fi
}

# Show next steps
show_next_steps() {
    echo ""
    echo "=== Installation Complete ==="
    echo ""
    log_info "py $VERSION installed to $INSTALL_PATH"
    echo ""
    echo "Quick start:"
    echo "  mkdir my-project"
    echo "  cd my-project"
    echo "  py init"
    echo "  py add requests"
    echo "  py doctor"
    echo ""
    echo "For help:"
    echo "  py --help"
    echo ""
    echo "Documentation:"
    echo "  https://github.com/Antonymwangi20/py#readme"
    echo ""
}

# Main installation flow
main() {
    echo "╔════════════════════════════════════╗"
    echo "║  py - Python Project Management    ║"
    echo "║  Installation Script               ║"
    echo "╚════════════════════════════════════╝"
    echo ""
    
    check_prerequisites
    echo ""
    
    create_install_dir
    echo ""
    
    install_py
    echo ""
    
    verify_installation
    echo ""
    
    setup_path
    echo ""
    
    show_next_steps
}

# Run installation
main "$@"
