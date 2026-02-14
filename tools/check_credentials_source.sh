#!/bin/bash

# Verify whether KuCoin credentials have at least one persistent source.
# Does not print secrets.

set -u

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_NAME="ibis-agent.service"

has_env=0
has_file=0
has_service_env=0
service_query="unknown"

if [ -n "${KUCOIN_API_KEY:-}" ] && [ -n "${KUCOIN_API_SECRET:-}" ] && [ -n "${KUCOIN_API_PASSPHRASE:-}" ]; then
    has_env=1
fi

check_file_for_keys() {
    local f="$1"
    [ -f "$f" ] || return 1
    rg -q "^\s*KUCOIN_API_KEY\s*=\s*[^[:space:]#]+" "$f" || return 1
    rg -q "^\s*KUCOIN_API_SECRET\s*=\s*[^[:space:]#]+" "$f" || return 1
    rg -q "^\s*KUCOIN_API_PASSPHRASE\s*=\s*[^[:space:]#]+" "$f" || return 1
    return 0
}

for f in "$BASE_DIR/keys.env" "$BASE_DIR/ibis/keys.env" "$BASE_DIR/.env"; do
    if check_file_for_keys "$f"; then
        has_file=1
    fi
done

unit_tmp="$(mktemp /tmp/ibis_service_unit.XXXXXX)"
show_tmp="$(mktemp /tmp/ibis_service_show.XXXXXX)"
if systemctl cat "$SERVICE_NAME" >"$unit_tmp" 2>/dev/null; then
    service_query="ok"
    if rg -q "^\s*Environment(File)?=" "$unit_tmp"; then
        has_service_env=1
    fi

    # Also check resolved runtime properties from systemd.
    if systemctl show "$SERVICE_NAME" -p Environment -p EnvironmentFiles >"$show_tmp" 2>/dev/null; then
        if rg -q "Environment=(.*KUCOIN_API_KEY|.*KUCOIN_API_SECRET|.*KUCOIN_API_PASSPHRASE)" "$show_tmp"; then
            has_service_env=1
        fi
        if rg -q "EnvironmentFiles=.*keys\\.env|EnvironmentFiles=.*\\.env" "$show_tmp"; then
            has_service_env=1
        fi
    fi
else
    service_query="unavailable"
fi
rm -f "$unit_tmp" 2>/dev/null || true
rm -f "$show_tmp" 2>/dev/null || true

echo "Credentials source check:"
echo "- shell_env_present: $has_env"
echo "- local_file_present: $has_file"
echo "- service_env_declared: $has_service_env"
echo "- service_query: $service_query"

if [ "$has_env" -eq 1 ] || [ "$has_file" -eq 1 ]; then
    echo "RESULT=PASS"
    exit 0
fi

if [ "$service_query" = "unavailable" ]; then
    echo "RESULT=WARN_UNVERIFIED"
    exit 2
fi

echo "RESULT=FAIL"
exit 1
