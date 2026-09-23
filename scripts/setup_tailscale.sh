#!/usr/bin/env bash
# Install Tailscale on Linux Worker (Debian/Ubuntu).
set -e

echo "=== Tailscale setup (Linux) ==="
if ! command -v tailscale &>/dev/null; then
    echo "[1/3] Installing Tailscale..."
    curl -fsSL https://tailscale.com/install.sh | sh
else
    echo "[1/3] Tailscale already installed."
fi

echo "[2/3] Bringing up (browser will open for login)..."
sudo tailscale up

echo "[3/3] Status:"
tailscale ip -4
tailscale status
