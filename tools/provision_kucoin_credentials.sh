#!/bin/bash

# Securely provision KuCoin credentials for IBIS and optionally restart service.

set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$BASE_DIR/ibis/keys.env"
SERVICE_NAME="ibis-agent.service"

mkdir -p "$(dirname "$ENV_FILE")"
umask 077

echo "Provisioning KuCoin credentials for IBIS."
echo "Target file: $ENV_FILE"
echo ""

read -r -s -p "KUCOIN_API_KEY: " KUCOIN_API_KEY
echo ""
read -r -s -p "KUCOIN_API_SECRET: " KUCOIN_API_SECRET
echo ""
read -r -s -p "KUCOIN_API_PASSPHRASE: " KUCOIN_API_PASSPHRASE
echo ""
read -r -p "PAPER_TRADING [false]: " PAPER_TRADING
read -r -p "KUCOIN_IS_SANDBOX [false]: " KUCOIN_IS_SANDBOX

PAPER_TRADING="${PAPER_TRADING:-false}"
KUCOIN_IS_SANDBOX="${KUCOIN_IS_SANDBOX:-false}"

if [ -z "$KUCOIN_API_KEY" ] || [ -z "$KUCOIN_API_SECRET" ] || [ -z "$KUCOIN_API_PASSPHRASE" ]; then
    echo "ERROR: all three KuCoin values are required."
    exit 1
fi

cat > "$ENV_FILE" <<EOF
KUCOIN_API_KEY=$KUCOIN_API_KEY
KUCOIN_API_SECRET=$KUCOIN_API_SECRET
KUCOIN_API_PASSPHRASE=$KUCOIN_API_PASSPHRASE
PAPER_TRADING=$PAPER_TRADING
KUCOIN_IS_SANDBOX=$KUCOIN_IS_SANDBOX
EOF

chmod 600 "$ENV_FILE"
echo "Wrote credential file with mode 600."

echo ""
read -r -p "Restart $SERVICE_NAME now? [Y/n]: " RESTART_NOW
if [ "${RESTART_NOW:-Y}" = "n" ] || [ "${RESTART_NOW:-Y}" = "N" ]; then
    echo "Skipped restart."
    exit 0
fi

sudo systemctl restart "$SERVICE_NAME"
sudo systemctl status "$SERVICE_NAME" --no-pager
