# PiRun Quick Start

A minimal, sandboxed Python project manager with a dark-mode web UI.

## Installation

### Quick Install (from GitHub)

```bash
curl -sSL https://raw.githubusercontent.com/jmelowry/pirun/main/install.sh | bash
export PATH="$PATH:$HOME/.pirun"
```

### Manual Install

```bash
git clone https://github.com/jmelowry/pirun.git
cd pirun
pip install -r requirements.txt
export PATH="$PATH:$(pwd)"
```

## Usage

### Initialize a new project

```bash
./pirun.py init /path/to/myproject --name "My Project"
```

This creates:
- `.pirun.yaml` - Configuration file
- `.venv/` - Python virtual environment
- `scripts/` - Directory for your Python scripts
- `var/logs/` - Execution logs
- `scripts/hello.py` - Example script

### Start the web server

```bash
./pirun.py serve /path/to/myproject
```

Then open http://127.0.0.1:8080 in your browser.

The web UI provides:
- **Files Tab**: Browse, view, and edit files in your project
- **Run Tab**: Execute Python scripts with arguments and view live output

### Run scripts from CLI

```bash
./pirun.py run /path/to/myproject scripts/hello.py --arg1 value
```

## Features

### Security & Sandboxing
- All file operations confined to project directory
- No path traversal allowed
- Python-only execution via project venv
- No shell access

### Web UI
- Clean, minimal dark-mode interface
- File browser with text editor
- Script runner with live output
- Auto-refresh during execution

### Configuration

Edit `.pirun.yaml` in your project directory:

```yaml
name: my-project
base_dir: /path/to/myproject
venv_python: .venv/bin/python
server:
  addr: 127.0.0.1:8080
  run_timeout_ms: 30000
  max_upload_bytes: 5000000
```

## Example: Creating a Simple Project

```bash
# Initialize
./pirun.py init ~/pirun-demo

# Create a script
cat > ~/pirun-demo/scripts/greet.py << 'EOF'
import sys
name = sys.argv[1] if len(sys.argv) > 1 else "World"
print(f"Hello, {name}!")
EOF

# Run it
./pirun.py run ~/pirun-demo scripts/greet.py Alice

# Or start the web UI
./pirun.py serve ~/pirun-demo
```

## API Endpoints

- `GET /api/files?path=<path>` - List directory contents
- `GET /api/file?path=<path>` - Read file
- `PUT /api/file?path=<path>` - Write file (JSON body: `{content: "..."}`)
- `DELETE /api/file?path=<path>` - Delete file
- `POST /api/run` - Execute script (JSON body: `{path: "...", args: [...]}`)
- `GET /api/run/status?run_id=<id>` - Get execution status
- `GET /api/run/log?run_id=<id>` - Get execution log

## System Requirements

- Python 3.7+
- Works on Linux (including Raspberry Pi), macOS, and Windows
- Minimal memory footprint (~20-30MB)

## Tips

- The UI auto-saves are not enabled - click "Save" after editing
- Script output updates every second during execution
- Logs are stored in `var/logs/<run_id>.log`
- Hidden files and `.venv` are hidden in the file browser
