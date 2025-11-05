"""Python execution service with venv support."""
import os
import subprocess
import uuid
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from threading import Thread, Lock


class ExecutionService:
    """Handles Python script execution via venv."""

    def __init__(self, base_dir: str, venv_python: str, default_timeout_ms: int = 30000):
        self.base_dir = Path(base_dir).resolve()
        self.venv_python = self.base_dir / venv_python
        self.default_timeout_ms = default_timeout_ms
        self.log_dir = self.base_dir / 'var' / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Track running executions
        self.runs: Dict[str, Dict[str, Any]] = {}
        self.runs_lock = Lock()

    def _validate_script_path(self, relative_path: str) -> Path:
        """Validate that the script is a .py file within base_dir."""
        if not relative_path.endswith('.py'):
            raise ValueError("Only .py files can be executed")

        script_path = (self.base_dir / relative_path).resolve()

        try:
            script_path.relative_to(self.base_dir)
        except ValueError:
            raise ValueError(f"Script path escapes base directory: {relative_path}")

        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {relative_path}")

        return script_path

    def start_run(self, script_path: str, args: List[str] = None) -> Dict[str, Any]:
        """Start a Python script execution.

        Returns:
            Dict with run_id, started_at, timeout_ms
        """
        if args is None:
            args = []

        validated_path = self._validate_script_path(script_path)

        run_id = str(uuid.uuid4())
        started_at = time.time()

        run_info = {
            'run_id': run_id,
            'script_path': script_path,
            'args': args,
            'started_at': started_at,
            'ended_at': None,
            'state': 'running',
            'exit_code': None,
            'log_file': self.log_dir / f"{run_id}.log"
        }

        with self.runs_lock:
            self.runs[run_id] = run_info

        # Start execution in background thread
        thread = Thread(target=self._execute, args=(run_id, validated_path, args))
        thread.daemon = True
        thread.start()

        return {
            'run_id': run_id,
            'started_at': int(started_at),
            'timeout_ms': self.default_timeout_ms
        }

    def _execute(self, run_id: str, script_path: Path, args: List[str]):
        """Execute the script (runs in background thread)."""
        run_info = self.runs[run_id]
        log_file = run_info['log_file']

        # Prepare command
        cmd = [str(self.venv_python), str(script_path)] + args

        # Prepare environment
        env = os.environ.copy()
        env['VIRTUAL_ENV'] = str(self.base_dir / '.venv')
        env['PATH'] = f"{self.base_dir / '.venv' / 'bin'}:{env.get('PATH', '')}"

        try:
            with open(log_file, 'w') as f:
                process = subprocess.Popen(
                    cmd,
                    cwd=str(self.base_dir),
                    env=env,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    text=True
                )

                # Wait with timeout
                timeout_sec = self.default_timeout_ms / 1000
                try:
                    exit_code = process.wait(timeout=timeout_sec)
                    state = 'succeeded' if exit_code == 0 else 'failed'
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                    exit_code = -1
                    state = 'killed'
                    f.write(f"\n\n[KILLED: Timeout after {timeout_sec}s]\n")

        except Exception as e:
            state = 'failed'
            exit_code = -1
            with open(log_file, 'w') as f:
                f.write(f"[ERROR: {str(e)}]\n")

        # Update run info
        with self.runs_lock:
            run_info['ended_at'] = time.time()
            run_info['state'] = state
            run_info['exit_code'] = exit_code

    def get_status(self, run_id: str) -> Dict[str, Any]:
        """Get the status of a run."""
        with self.runs_lock:
            if run_id not in self.runs:
                raise ValueError(f"Run not found: {run_id}")

            run_info = self.runs[run_id].copy()

        return {
            'run_id': run_id,
            'state': run_info['state'],
            'started_at': int(run_info['started_at']),
            'ended_at': int(run_info['ended_at']) if run_info['ended_at'] else None,
            'exit_code': run_info['exit_code']
        }

    def get_log(self, run_id: str, tail_kb: int = 64) -> str:
        """Get the log output for a run.

        Args:
            run_id: The run ID
            tail_kb: Number of KB to return from end of log

        Returns:
            Log contents (last N KB)
        """
        with self.runs_lock:
            if run_id not in self.runs:
                raise ValueError(f"Run not found: {run_id}")

            log_file = self.runs[run_id]['log_file']

        if not log_file.exists():
            return ""

        # Read last N KB
        max_bytes = tail_kb * 1024
        file_size = log_file.stat().st_size

        with open(log_file, 'r') as f:
            if file_size > max_bytes:
                f.seek(file_size - max_bytes)
                # Skip partial line
                f.readline()
            return f.read()
