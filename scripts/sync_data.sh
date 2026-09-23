#!/usr/bin/env bash
# Worker-side: pull latest data from Master over Tailscale.
# Run via cron every 6 hours:
#   0 */6 * * * /path/to/sync_data.sh
set -e

MASTER_TS_IP="${QUANT_MASTER_TS_IP:?set QUANT_MASTER_TS_IP}"
MASTER_USER="${QUANT_MASTER_USER:-$USER}"
MASTER_DIR="${QUANT_MASTER_DIR:-/quant_system}"
LOCAL_DIR="$(cd "$(dirname "$0")/.." && pwd)/data"

echo "[$(date)] syncing from ${MASTER_USER}@${MASTER_TS_IP}:${MASTER_DIR}/data/ -> ${LOCAL_DIR}"
rsync -avz --delete \
    "${MASTER_USER}@${MASTER_TS_IP}:${MASTER_DIR}/data/" \
    "${LOCAL_DIR}/"

# Push results back to Master
mkdir -p "${LOCAL_DIR}/../results"
rsync -avz "${LOCAL_DIR}/../results/" \
    "${MASTER_USER}@${MASTER_TS_IP}:${MASTER_DIR}/results/"
echo "[$(date)] sync done."
