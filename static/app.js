// PiRun Web UI
class PiRunApp {
    constructor() {
        this.currentPath = '';
        this.currentFile = null;
        this.currentRunId = null;
        this.pollInterval = null;

        this.init();
    }

    init() {
        this.setupTabs();
        this.setupFileView();
        this.setupRunnerView();
        this.loadFiles('/');
    }

    // Tab switching
    setupTabs() {
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const viewName = tab.dataset.view;
                this.switchView(viewName);
            });
        });
    }

    switchView(viewName) {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));

        document.querySelector(`[data-view="${viewName}"]`).classList.add('active');
        document.getElementById(`${viewName}-view`).classList.add('active');
    }

    // File View
    setupFileView() {
        document.getElementById('save-btn').addEventListener('click', () => this.saveFile());
        document.getElementById('close-btn').addEventListener('click', () => this.closeFile());
    }

    async loadFiles(path) {
        try {
            const response = await fetch(`/api/files?path=${encodeURIComponent(path)}`);
            const data = await response.json();

            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }

            this.currentPath = path;
            this.renderFileList(data.entries);
        } catch (error) {
            alert('Failed to load files: ' + error.message);
        }
    }

    renderFileList(entries) {
        const fileList = document.getElementById('file-list');
        const pathBar = document.getElementById('current-path');

        pathBar.textContent = '/' + this.currentPath;
        fileList.innerHTML = '';

        // Add parent directory link if not at root
        if (this.currentPath) {
            const parentItem = this.createFileItem({
                name: '..',
                type: 'dir'
            });
            fileList.appendChild(parentItem);
        }

        // Add all entries
        entries.forEach(entry => {
            const item = this.createFileItem(entry);
            fileList.appendChild(item);
        });
    }

    createFileItem(entry) {
        const div = document.createElement('div');
        div.className = 'file-item';
        if (entry.type === 'dir') div.classList.add('dir');

        const icon = document.createElement('span');
        icon.className = 'file-icon';
        icon.textContent = entry.type === 'dir' ? '📁' : '📄';

        const name = document.createElement('span');
        name.className = 'file-name';
        name.textContent = entry.name;

        div.appendChild(icon);
        div.appendChild(name);

        div.addEventListener('click', () => {
            if (entry.type === 'dir') {
                const newPath = entry.name === '..'
                    ? this.currentPath.split('/').slice(0, -1).join('/')
                    : this.currentPath ? `${this.currentPath}/${entry.name}` : entry.name;
                this.loadFiles(newPath);
            } else {
                const filePath = this.currentPath ? `${this.currentPath}/${entry.name}` : entry.name;
                this.openFile(filePath);
            }
        });

        return div;
    }

    async openFile(path) {
        try {
            const response = await fetch(`/api/file?path=${encodeURIComponent(path)}`);
            const data = await response.json();

            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }

            this.currentFile = path;
            document.getElementById('editor-empty').classList.add('hidden');
            document.getElementById('editor-container').classList.remove('hidden');
            document.getElementById('editor-filename').textContent = path;
            document.getElementById('editor').value = data.content;

            // Highlight selected file
            document.querySelectorAll('.file-item').forEach(item => {
                item.classList.remove('selected');
                if (item.querySelector('.file-name')?.textContent === path.split('/').pop()) {
                    item.classList.add('selected');
                }
            });
        } catch (error) {
            alert('Failed to open file: ' + error.message);
        }
    }

    async saveFile() {
        if (!this.currentFile) return;

        try {
            const content = document.getElementById('editor').value;
            const response = await fetch(`/api/file?path=${encodeURIComponent(this.currentFile)}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            });

            const data = await response.json();
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                // Visual feedback
                const saveBtn = document.getElementById('save-btn');
                saveBtn.textContent = 'Saved!';
                setTimeout(() => saveBtn.textContent = 'Save', 1000);
            }
        } catch (error) {
            alert('Failed to save file: ' + error.message);
        }
    }

    closeFile() {
        this.currentFile = null;
        document.getElementById('editor-container').classList.add('hidden');
        document.getElementById('editor-empty').classList.remove('hidden');
        document.querySelectorAll('.file-item').forEach(item => item.classList.remove('selected'));
    }

    // Runner View
    setupRunnerView() {
        document.getElementById('run-btn').addEventListener('click', () => this.runScript());
    }

    async runScript() {
        const scriptPath = document.getElementById('script-path').value.trim();
        if (!scriptPath) {
            alert('Please enter a script path');
            return;
        }

        const argsInput = document.getElementById('script-args').value.trim();
        const args = argsInput ? argsInput.split(/\s+/) : [];

        try {
            const response = await fetch('/api/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: scriptPath, args })
            });

            const data = await response.json();
            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }

            this.currentRunId = data.run_id;
            this.updateRunStatus('running', 'Running...');
            document.getElementById('output-log').textContent = 'Starting execution...\n';

            // Start polling for updates
            this.startPolling();
        } catch (error) {
            alert('Failed to start run: ' + error.message);
        }
    }

    startPolling() {
        if (this.pollInterval) clearInterval(this.pollInterval);

        this.pollInterval = setInterval(async () => {
            await this.checkRunStatus();
        }, 1000);
    }

    async checkRunStatus() {
        if (!this.currentRunId) return;

        try {
            // Get status
            const statusResponse = await fetch(`/api/run/status?run_id=${this.currentRunId}`);
            const statusData = await statusResponse.json();

            // Get log
            const logResponse = await fetch(`/api/run/log?run_id=${this.currentRunId}`);
            const logData = await logResponse.json();

            // Update UI
            document.getElementById('output-log').textContent = logData.log || 'No output yet...';

            const elapsed = statusData.ended_at
                ? statusData.ended_at - statusData.started_at
                : Date.now() / 1000 - statusData.started_at;
            document.getElementById('run-time').textContent = `${elapsed.toFixed(1)}s`;

            // Check if finished
            if (statusData.state !== 'running') {
                clearInterval(this.pollInterval);
                this.pollInterval = null;

                const statusText = statusData.state === 'succeeded'
                    ? `Completed (exit code: ${statusData.exit_code})`
                    : `Failed (${statusData.state})`;

                this.updateRunStatus(statusData.state, statusText);
            }
        } catch (error) {
            console.error('Failed to check run status:', error);
        }
    }

    updateRunStatus(state, text) {
        const statusEl = document.getElementById('run-status');
        statusEl.textContent = text;
        statusEl.className = '';
        if (state === 'running') statusEl.classList.add('running');
        else if (state === 'succeeded') statusEl.classList.add('success');
        else statusEl.classList.add('error');
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new PiRunApp();
});
