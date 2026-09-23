# Worker node start script (Windows).
# Usage: .\scripts\start_worker.ps1 -MasterTsIp 100.x.x.x
param(
    [string]$MasterTsIp = $env:QUANT_MASTER_TS_IP,
    [int]$Port = 6379
)

if (-not $MasterTsIp) {
    Write-Host "ERROR: pass -MasterTsIp or set QUANT_MASTER_TS_IP env var" -ForegroundColor Red
    exit 1
}

$env:QUANT_MASTER_TS_IP = $MasterTsIp
Write-Host "Connecting to Redis at $MasterTsIp`:$Port over Tailscale" -ForegroundColor Cyan

celery -A tasks.celery_app worker --loglevel=info -Q backtest_queue `
    -b "redis://${MasterTsIp}:${Port}/0"
