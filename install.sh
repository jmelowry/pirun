#!/bin/bash
# PiRun installer - Simple curl | bash installation
# Usage: curl -sSL https://raw.githubusercontent.com/jmelowry/pirun/main/install.sh | bash

set -e

INSTALL_DIR="${PIRUN_INSTALL_DIR:-$HOME/.pirun}"
REPO_URL="https://github.com/jmelowry/pirun"
BRANCH="${PIRUN_BRANCH:-main}"

echo "======================================"
echo "  PiRun Installer"
echo "======================================"
echo ""
echo "Installing to: $INSTALL_DIR"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Found Python $PYTHON_VERSION"

# Check pip
if ! python3 -m pip --version &> /dev/null; then
    echo "Error: pip is required but not found"
    exit 1
fi

echo "✓ Found pip"

# Create install directory
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Download files
echo ""
echo "Downloading PiRun..."

download_file() {
    local file=$1
    local url="https://raw.githubusercontent.com/jmelowry/pirun/$BRANCH/$file"

    if command -v curl &> /dev/null; then
        curl -sSL -o "$file" "$url"
    elif command -v wget &> /dev/null; then
        wget -q -O "$file" "$url"
    else
        echo "Error: Neither curl nor wget found"
        exit 1
    fi
}

# Create directory structure
mkdir -p services static

# Download main files
echo "  - pirun.py"
download_file "pirun.py"
chmod +x pirun.py

echo "  - server.py"
download_file "server.py"

echo "  - requirements.txt"
download_file "requirements.txt"

# Download services
echo "  - services/"
download_file "services/__init__.py"
download_file "services/config.py"
download_file "services/file_service.py"
download_file "services/exec_service.py"

# Download static files
echo "  - static/"
download_file "static/index.html"
download_file "static/style.css"
download_file "static/app.js"

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
python3 -m pip install -q -r requirements.txt

echo ""
echo "======================================"
echo "  Installation Complete!"
echo "======================================"
echo ""
echo "PiRun installed to: $INSTALL_DIR"
echo ""
echo "Add to PATH by running:"
echo "  export PATH=\"\$PATH:$INSTALL_DIR\""
echo ""
echo "Or add this to your ~/.bashrc or ~/.zshrc:"
echo "  export PATH=\"\$PATH:$INSTALL_DIR\""
echo ""
echo "Quick start:"
echo "  $INSTALL_DIR/pirun.py init ~/myproject"
echo "  $INSTALL_DIR/pirun.py serve ~/myproject"
echo ""
echo "Or with PATH configured:"
echo "  pirun.py init ~/myproject"
echo "  pirun.py serve ~/myproject"
echo ""
