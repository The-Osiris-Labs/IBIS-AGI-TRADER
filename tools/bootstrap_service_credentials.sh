#!/bin/bash

# Configure systemd service to load KuCoin credentials from a persistent env file.
# This script does not print secrets.

set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_NAME="ibis-agent.service"
ENV_FILE_DEFAULT="$BASE_DIR/ibis/keys.env"
ENV_FILE="${1:-$ENV_FILE_DEFAULT}"
DROPIN_DIR="/etc/systemd/system/${SERVICE_NAME}.d"
DROPIN_FILE="${DROPIN_DIR}/credentials.conf"

if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: env file not found: $ENV_FILE"
    exit 1
fi

if ! rg -q "^\s*KUCOIN_API_KEY\s*=" "$ENV_FILE"; then
    echo "ERROR: KUCOIN_API_KEY missing in $ENV_FILE"
    exit 1
fi
if ! rg -q "^\s*KUCOIN_API_SECRET\s*=" "$ENV_FILE"; then
    echo "ERROR: KUCOIN_API_SECRET missing in $ENV_FILE"
    exit 1
fi
if ! rg -q "^\s*KUCOIN_API_PASSPHRASE\s*=" "$ENV_FILE"; then
    echo "ERROR: KUCOIN_API_PASSPHRASE missing in $ENV_FILE"
    exit 1
fi

sudo mkdir -p "$DROPIN_DIR"
sudo bash -c "cat > '$DROPIN_FILE' <<EOF
[Service]
EnvironmentFile=$ENV_FILE
EOF"

sudo systemctl daemon-reload

echo "Configured $SERVICE_NAME credential source:"
echo "- drop-in: $DROPIN_FILE"
echo "- env file: $ENV_FILE"
echo ""
echo "Next step (manual): sudo systemctl restart $SERVICE_NAME"
