# Worker-side (Windows): pull data from Master over Tailscale.
# Run via Task Scheduler every 6 hours, or call manually.
param(
    [Parameter(Mandatory=$true)][string]$MasterTsIp,
    [string]$MasterUser = "Administrator",
    [string]$MasterDir = "C:/Users/Administrator/Doubao/chats/2026-09-22/new-chat-1/quant_system"
)

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $here
$localData = Join-Path $root "data"

Write-Host "Syncing from ${MasterUser}@${MasterTsIp}:${MasterDir}/data/ -> $localData"
# Uses scp (built into Windows 10+) or rsync via WSL.
scp -r "${MasterUser}@${MasterTsIp}:${MasterDir}/data/*" "$localData/"

$localResults = Join-Path $root "results"
scp -r "${localResults}/*" "${MasterUser}@${MasterTsIp}:${MasterDir}/results/"
Write-Host "Sync done."
