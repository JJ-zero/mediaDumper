# Linux Service Template

> __DISCLAIMER:__ The template and helper scripts were mostly generated with AI. I have reviewed and tested them, but please use them at your own risk.

## Files

- **mediaDumper.service** - The systemd service template with placeholders
- **generate_service.sh** - Script to auto-fill the template and generate a reviewable service file
- **install_service.sh** - Script to install, enable, and start the generated service file

## Features

The service template includes:
- Automatic restart on failure
- Logging to system journal (`journalctl`)
- Resource limits (CPU and memory)
- Security hardening (isolated filesystem, no new privileges)
- Proper dependency management

## Installation

### Quick Start

```bash
bash service_template/generate_service.sh
# Review the generated file at service_template/mediaDumper.generated.service
sudo bash service_template/install_service.sh
```

The process will:
1. Detect your Python environment
2. Determine the appropriate system user
3. Generate `service_template/mediaDumper.generated.service`
4. Let you review the generated service file before installation
5. Install it to `/etc/systemd/system/mediaDumper.service`
6. Reload systemd daemon
7. Enable the service (start on boot)
8. Start the service immediately

If you need to override the service runtime user during generation:

```bash
SERVICE_USER=myuser bash service_template/generate_service.sh
```

Virtual environment is required for generation. The script intentionally aborts when `venv/bin/python` is missing.

### Manual Installation

If you prefer to do it manually:

1. Fill in the placeholders in mediaDumper.service:
    1. Replace {{SCRIPT_DIR}} with the absolute path to the project root
    2. Replace {{SERVICE_USER}} with your username
    3. Replace {{PYTHON_EXECUTABLE}} with the Python interpreter you want systemd to run

2. Copy the reviewed service file to the systemd directory:
```bash
sudo cp service_template/mediaDumper.generated.service /etc/systemd/system/mediaDumper.service
```
3. Reload daemon, enable and start service
```bash
sudo systemctl daemon-reload
sudo systemctl enable mediaDumper
sudo systemctl start mediaDumper
```

## Advanced Customization

Edit the generated service file before installation:

- `Restart=on-failure` - Change restart policy
- `RestartSec=10s` - Adjust delay between restarts
- `MemoryLimit=512M` - Adjust memory limit
- `CPUQuota=20%` - Adjust CPU limit
- `User=` - Change service user
- `ReadWritePaths=` -  Restrict writable paths for the service (Enable to whitelist only necessary directories)

## Security Notes

- The service runs with the specified user (defaults to current user)
- By default, `ProtectSystem=strict` and `ProtectHome=yes` are present in the template but commented out
    - If you enable `ProtectSystem`/`ProtectHome`, configure `ReadWritePaths=` so all required target directories remain writable
    - Do not forget to include the _mount_ directory. The service mounts connected drives to `/media/sd` and it needs the read/write access to that directory.
- No new privileges can be gained
- Resource limits prevent runaway processes
