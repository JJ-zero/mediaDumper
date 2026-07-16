#!/bin/bash

# Media Dumper Service Generator
# This script fills the service template and writes the result for manual review.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_TEMPLATE_DIR="$SCRIPT_DIR/service_template"
SERVICE_NAME="mediaDumper"
SERVICE_FILE_NAME="${SERVICE_NAME}.service"
GENERATED_SERVICE_FILE_NAME="${SERVICE_NAME}.generated.service"
GENERATED_SERVICE_FILE="$SERVICE_TEMPLATE_DIR/$GENERATED_SERVICE_FILE_NAME"

echo -e "${GREEN}Media Dumper Service Generator${NC}"
echo "================================"
echo ""

# Detect Python executable
if [[ -f "$SCRIPT_DIR/venv/bin/python" ]]; then
    PYTHON_EXECUTABLE="$SCRIPT_DIR/venv/bin/python"
    echo -e "${GREEN}✓${NC} Detected virtual environment"
else
    echo -e "${RED}⚠ No virtual environment detected. Aborting.${NC}"
    exit 1
fi

# Detect service user
# Priority: explicit env var -> sudo caller -> current user
if [[ -n "${SERVICE_USER:-}" ]]; then
    echo -e "${GREEN}✓${NC} Service user: $SERVICE_USER (from environment)"
elif [[ -n "${SUDO_USER:-}" && "$SUDO_USER" != "root" ]]; then
    SERVICE_USER="$SUDO_USER"
    echo -e "${GREEN}✓${NC} Service user: $SERVICE_USER (from sudo)"
else
    SERVICE_USER="$(whoami)"
    echo -e "${GREEN}✓${NC} Service user: $SERVICE_USER"
fi

if [[ "$SERVICE_USER" == "root" ]]; then
    echo -e "${RED}Error: Refusing to generate a service that runs as root${NC}"
    echo "Set SERVICE_USER explicitly, for example:"
    echo "  SERVICE_USER=your-linux-user bash service_template/generate_service.sh"
    exit 1
fi

# Validate template exists
if [[ ! -f "$SERVICE_TEMPLATE_DIR/$SERVICE_FILE_NAME" ]]; then
    echo -e "${RED}Error: Template not found at $SERVICE_TEMPLATE_DIR/$SERVICE_FILE_NAME${NC}"
    exit 1
fi

echo "- Project Directory: $SCRIPT_DIR"
echo "- Python Executable: $PYTHON_EXECUTABLE"
echo ""

# Create generated service file with replacements
sed \
    -e "s|{{SCRIPT_DIR}}|$SCRIPT_DIR|g" \
    -e "s|{{SERVICE_USER}}|$SERVICE_USER|g" \
    -e "s|{{PYTHON_EXECUTABLE}}|$PYTHON_EXECUTABLE|g" \
    "$SERVICE_TEMPLATE_DIR/$SERVICE_FILE_NAME" > "$GENERATED_SERVICE_FILE"

# Verify replacements
if grep -q "{{" "$GENERATED_SERVICE_FILE"; then
    echo -e "${RED}Error: Not all placeholders were replaced${NC}"
    rm -f "$GENERATED_SERVICE_FILE"
    exit 1
fi

echo -e "${GREEN}✓${NC} Service file generated at \n$GENERATED_SERVICE_FILE"

echo ""
echo -e "${GREEN}Generation Complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Review generated file: $GENERATED_SERVICE_FILE"
echo "  2. Install and start service: sudo bash service_template/install_service.sh"
echo "  3. Check status: sudo systemctl status $SERVICE_NAME"
echo ""
