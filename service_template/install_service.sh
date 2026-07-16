#!/bin/bash

set -e

SERVICE_NAME="mediaDumper"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_TEMPLATE_DIR="$SCRIPT_DIR/service_template"
SERVICE_FILE_NAME="${SERVICE_NAME}.service"
GENERATED_SERVICE_FILE_NAME="${SERVICE_NAME}.generated.service"
GENERATED_SERVICE_FILE="$SERVICE_TEMPLATE_DIR/$GENERATED_SERVICE_FILE_NAME"
SYSTEM_SERVICE_FILE="/etc/systemd/system/$SERVICE_FILE_NAME"

if [[ $EUID -ne 0 ]]; then
	echo "Error: This script must be run as root"
	echo "Use: sudo bash service_template/install_service.sh"
	exit 1
fi

if [[ ! -f "$GENERATED_SERVICE_FILE" ]]; then
	echo "Error: Generated service file not found: $GENERATED_SERVICE_FILE"
	echo "Run this first: bash service_template/generate_service.sh"
	exit 1
fi

if grep -q "{{" "$GENERATED_SERVICE_FILE"; then
	echo "Error: Generated service file contains unresolved placeholders"
	echo "Re-generate it with: bash service_template/generate_service.sh"
	exit 1
fi

# Copy to systemd directory
cp "$GENERATED_SERVICE_FILE" "$SYSTEM_SERVICE_FILE"
chmod 644 "$SYSTEM_SERVICE_FILE"

systemctl daemon-reload

systemctl enable "$SERVICE_NAME"

systemctl start "$SERVICE_NAME"

systemctl status "$SERVICE_NAME" --no-pager
