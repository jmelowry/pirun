# Installation Guide

## Quick Install (Recommended)

Install PiRun directly from GitHub:

```bash
curl -sSL https://raw.githubusercontent.com/jmelowry/pirun/main/install.sh | bash
```

This will:
- Download PiRun to `~/.pirun/`
- Install Python dependencies
- Make `pirun.py` executable

Add to your PATH:

```bash
export PATH="$PATH:$HOME/.pirun"
```

Make it permanent by adding to your `~/.bashrc` or `~/.zshrc`:

```bash
echo 'export PATH="$PATH:$HOME/.pirun"' >> ~/.bashrc
source ~/.bashrc
```

## Custom Install Location

```bash
export PIRUN_INSTALL_DIR=/opt/pirun
curl -sSL https://raw.githubusercontent.com/jmelowry/pirun/main/install.sh | bash
export PATH="$PATH:/opt/pirun"
```

## Manual Installation

### 1. Clone the repository

```bash
git clone https://github.com/jmelowry/pirun.git
cd pirun
```

### 2. Install dependencies

```bash
pip3 install -r requirements.txt
```

Or using a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Make executable

```bash
chmod +x pirun.py
```

### 4. Test it

```bash
./pirun.py --help
```

### 5. Add to PATH (optional)

```bash
export PATH="$PATH:$(pwd)"
# Or create a symlink
sudo ln -s $(pwd)/pirun.py /usr/local/bin/pirun
```

## Requirements

- Python 3.7 or higher
- pip
- virtualenv (installed automatically)

## Platform Support

- **Raspberry Pi**: All models with Python 3.7+ (Zero W, 2, 3, 4, 5)
- **Linux**: Any distribution with Python 3.7+
- **macOS**: 10.15+ recommended
- **Windows**: WSL2 or native with Python 3.7+

## Verification

Verify the installation:

```bash
pirun --help
```

You should see:

```
Usage: pirun [OPTIONS] COMMAND [ARGS]...

  PiRun - Sandboxed Python project manager.

Commands:
  init   Initialize a new PiRun project.
  run    Execute a Python script in the project's venv.
  serve  Start the web server for a project.
```

## Updating

### Quick install method:

```bash
rm -rf ~/.pirun
curl -sSL https://raw.githubusercontent.com/jmelowry/pirun/main/install.sh | bash
```

### Manual method:

```bash
cd /path/to/pirun
git pull
pip install -r requirements.txt
```

## Uninstallation

### Quick install method:

```bash
rm -rf ~/.pirun
# Remove from PATH in ~/.bashrc or ~/.zshrc
```

### Manual method:

```bash
rm -rf /path/to/pirun
# Remove any symlinks you created
```

## Troubleshooting

### "python3: command not found"

Install Python 3:

```bash
# Debian/Ubuntu/Raspberry Pi OS
sudo apt update && sudo apt install python3 python3-pip

# macOS
brew install python3

# Fedora/RHEL
sudo dnf install python3 python3-pip
```

### "pip: command not found"

Install pip:

```bash
# Debian/Ubuntu/Raspberry Pi OS
sudo apt install python3-pip

# macOS
python3 -m ensurepip

# Fedora/RHEL
sudo dnf install python3-pip
```

### Permission errors

Try using `--user` flag:

```bash
pip3 install --user -r requirements.txt
```

### virtualenv not found

It should be installed automatically, but if needed:

```bash
pip3 install virtualenv
```
