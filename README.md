# PiRun

> Minimal, sandboxed Python project manager with a dark-mode web UI

PiRun provides a lightweight, secure environment for managing and running Python scripts on Raspberry Pi and other systems. Perfect for IoT projects, automation scripts, and learning Python.

## ✨ Features

- **🔒 Sandboxed Execution** - All operations confined to project directory
- **🌐 Web UI** - Clean, minimal dark-mode interface for file editing and script execution
- **🐍 Python-Only** - Execute scripts via isolated virtual environments
- **📦 Zero Dependencies** - Single binary approach, minimal footprint (~20-30MB)
- **🍓 Pi-Optimized** - Designed for Raspberry Pi (Zero W, 2, 3, 4, 5)
- **⚡ Fast** - Built with Flask, simple REST API

## 🚀 Quick Start

### Install

```bash
curl -sSL https://raw.githubusercontent.com/jmelowry/pirun/main/install.sh | bash
export PATH="$PATH:$HOME/.pirun"
```

### Initialize a Project

```bash
pirun init ~/myproject
cd ~/myproject
```

### Start the Web UI

```bash
pirun serve ~/myproject
```

Open **http://127.0.0.1:8080** in your browser.

### Or Run Scripts from CLI

```bash
pirun run ~/myproject scripts/hello.py
```

## 📸 Screenshots

The web UI features:
- **Files Tab**: Browse, view, and edit files with a text editor
- **Run Tab**: Execute Python scripts with arguments and view live output
- Dark-mode aesthetic with clean, minimal design

## 🛠️ Use Cases

- **Raspberry Pi Projects**: Manage IoT scripts, sensors, automation
- **Learning Python**: Safe sandbox for experimenting
- **Script Repository**: Organize and run utility scripts
- **Remote Execution**: Web-based script runner accessible via browser
- **Cron Jobs**: Scheduled script execution with logging

## 📦 What's Included

When you initialize a project, PiRun creates:

```
myproject/
├── .pirun.yaml          # Configuration
├── .venv/               # Isolated Python environment
├── scripts/             # Your Python scripts
│   └── hello.py         # Example script
└── var/logs/            # Execution logs
```

## 🔐 Security

- **Path Sandboxing**: All file operations restricted to project directory
- **No Path Traversal**: Validates all paths to prevent escaping base directory
- **Python-Only Execution**: No arbitrary shell commands
- **Isolated Environments**: Each project has its own virtualenv
- **Local-First**: Binds to 127.0.0.1 by default

## 📚 Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Installation Guide](INSTALL.md)

## 🔧 Requirements

- Python 3.7 or higher
- pip
- 10-20MB disk space

## 🌍 Platform Support

- **Raspberry Pi OS** (all models)
- **Linux** (Debian, Ubuntu, Fedora, etc.)
- **macOS** 10.15+
- **Windows** (via WSL2 or native)

## 📖 Usage Examples

### Example 1: Data Collection Script

```bash
# Initialize project
pirun init ~/weather-station

# Create a sensor script
cat > ~/weather-station/scripts/read_sensor.py << 'EOF'
import time
temperature = read_temperature()  # Your sensor logic
print(f"Temperature: {temperature}°C")
EOF

# Run it
pirun run ~/weather-station scripts/read_sensor.py
```

### Example 2: Web-Based Script Management

```bash
# Start the server
pirun serve ~/weather-station

# Access via browser at http://127.0.0.1:8080
# Edit scripts in the Files tab
# Execute with arguments in the Run tab
```

### Example 3: Custom Configuration

Edit `.pirun.yaml`:

```yaml
name: weather-station
base_dir: /home/pi/weather-station
venv_python: .venv/bin/python
server:
  addr: 127.0.0.1:8080
  run_timeout_ms: 60000        # 60 second timeout
  max_upload_bytes: 10000000   # 10MB max file size
```

## 🔌 API Endpoints

PiRun exposes a REST API:

- `GET /api/files?path=<path>` - List directory
- `GET /api/file?path=<path>` - Read file
- `PUT /api/file?path=<path>` - Write file
- `DELETE /api/file?path=<path>` - Delete file
- `POST /api/run` - Execute script
- `GET /api/run/status?run_id=<id>` - Check status
- `GET /api/run/log?run_id=<id>` - Get output log

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built for the Raspberry Pi and maker communities. Inspired by the need for simple, secure script management on resource-constrained devices.

---

**Made with ❤️ for Raspberry Pi**
