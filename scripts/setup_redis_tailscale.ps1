# Master-only: configure Redis to listen on Tailscale IP only.
# Run on Master Windows after installing Redis.
#
# Find our Tailscale IP first:
#   tailscale ip -4
# Then set $env:QUANT_MASTER_TS_IP before starting Celery workers.

param(
    [Parameter(Mandatory=$true)][string]$TsIp
)

Write-Host "=== Redis bind config for Tailscale ===" -ForegroundColor Cyan
Write-Host "Master Tailscale IP: $TsIp"

# Assume redis.windows.conf is in Redis install dir. Adjust path if needed.
$redisConf = "C:\Program Files\Redis\redis.windows.conf"
if (Test-Path $redisConf) {
    (Get-Content $redisConf) `
        -replace '^\s*bind\s+.*', "bind $TsIp 127.0.0.1" `
        -replace '^\s*protected-mode\s+.*', "protected-mode yes" |
        Set-Content $redisConf
    Write-Host "Updated $redisConf"
} else {
    Write-Host "Redis config not found at $redisConf"
    Write-Host "Edit it manually: bind $TsIp 127.0.0.1"
}

# Firewall: allow only Tailscale range
Write-Host "Adding firewall rule (Tailscale range 100.64.0.0/10)..."
New-NetFirewallRule -DisplayName "Redis-Tailscale" `
    -Direction Inbound -Protocol TCP -LocalPort 6379 `
    -RemoteAddress 100.64.0.0/10 -Action Allow -ErrorAction SilentlyContinue | Out-Null

# Export env var for Celery
[Environment]::SetEnvironmentVariable("QUANT_MASTER_TS_IP", $TsIp, "User")
$env:QUANT_MASTER_TS_IP = $TsIp
Write-Host "Env QUANT_MASTER_TS_IP=$TsIp (persisted at User scope)" -ForegroundColor Green
Write-Host "Next: restart Redis, then start Celery workers with same env."
