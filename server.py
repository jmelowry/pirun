"""Flask web server and API for PiRun."""
from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
import os

from services.config import Config
from services.file_service import FileService
from services.exec_service import ExecutionService


def create_app(base_dir: str):
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder='static')
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

    # Initialize services
    config = Config(base_dir)
    file_service = FileService(base_dir)
    exec_service = ExecutionService(
        base_dir,
        config.get('venv_python', '.venv/bin/python'),
        config.get('server.run_timeout_ms', 30000)
    )

    # Error handler
    def make_error(message: str, status: int = 400):
        return jsonify({'error': message}), status

    # Health check
    @app.route('/health')
    def health():
        return jsonify({'ok': True})

    # Serve UI
    @app.route('/')
    def index():
        return send_from_directory('static', 'index.html')

    # File listing
    @app.route('/api/files')
    def list_files():
        try:
            path = request.args.get('path', '')
            entries = file_service.list_files(path)
            return jsonify({'entries': entries})
        except FileNotFoundError as e:
            return make_error(str(e), 404)
        except ValueError as e:
            return make_error(str(e), 400)
        except Exception as e:
            return make_error(f"Internal error: {str(e)}", 500)

    # Read file
    @app.route('/api/file')
    def read_file():
        try:
            path = request.args.get('path')
            if not path:
                return make_error("Missing 'path' parameter", 400)

            content = file_service.read_file(path)
            return jsonify({'path': path, 'content': content})
        except FileNotFoundError as e:
            return make_error(str(e), 404)
        except ValueError as e:
            return make_error(str(e), 400)
        except Exception as e:
            return make_error(f"Internal error: {str(e)}", 500)

    # Write file
    @app.route('/api/file', methods=['PUT'])
    def write_file():
        try:
            path = request.args.get('path')
            if not path:
                return make_error("Missing 'path' parameter", 400)

            data = request.get_json()
            if not data or 'content' not in data:
                return make_error("Missing 'content' in request body", 400)

            file_service.write_file(path, data['content'])
            return jsonify({'path': path, 'success': True})
        except ValueError as e:
            return make_error(str(e), 400)
        except Exception as e:
            return make_error(f"Internal error: {str(e)}", 500)

    # Delete file
    @app.route('/api/file', methods=['DELETE'])
    def delete_file():
        try:
            path = request.args.get('path')
            if not path:
                return make_error("Missing 'path' parameter", 400)

            file_service.delete_file(path)
            return jsonify({'path': path, 'success': True})
        except FileNotFoundError as e:
            return make_error(str(e), 404)
        except ValueError as e:
            return make_error(str(e), 400)
        except Exception as e:
            return make_error(f"Internal error: {str(e)}", 500)

    # Start execution
    @app.route('/api/run', methods=['POST'])
    def start_run():
        try:
            data = request.get_json()
            if not data or 'path' not in data:
                return make_error("Missing 'path' in request body", 400)

            script_path = data['path']
            args = data.get('args', [])

            result = exec_service.start_run(script_path, args)
            return jsonify(result)
        except (ValueError, FileNotFoundError) as e:
            return make_error(str(e), 400)
        except Exception as e:
            return make_error(f"Internal error: {str(e)}", 500)

    # Get run status
    @app.route('/api/run/status')
    def run_status():
        try:
            run_id = request.args.get('run_id')
            if not run_id:
                return make_error("Missing 'run_id' parameter", 400)

            status = exec_service.get_status(run_id)
            return jsonify(status)
        except ValueError as e:
            return make_error(str(e), 404)
        except Exception as e:
            return make_error(f"Internal error: {str(e)}", 500)

    # Get run log
    @app.route('/api/run/log')
    def run_log():
        try:
            run_id = request.args.get('run_id')
            if not run_id:
                return make_error("Missing 'run_id' parameter", 400)

            tail_kb = int(request.args.get('tail_kb', 64))
            log = exec_service.get_log(run_id, tail_kb)
            return jsonify({'run_id': run_id, 'log': log})
        except ValueError as e:
            return make_error(str(e), 404)
        except Exception as e:
            return make_error(f"Internal error: {str(e)}", 500)

    return app


def run_server(base_dir: str, host: str = '127.0.0.1', port: int = 8080):
    """Run the Flask development server."""
    app = create_app(base_dir)
    print(f"Starting PiRun server at http://{host}:{port}")
    print(f"Project directory: {base_dir}")
    app.run(host=host, port=port, debug=False)
