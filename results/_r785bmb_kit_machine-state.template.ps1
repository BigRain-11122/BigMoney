# machine-state.template.ps1 - CEO 用机让路律 single-machine switch (fleet kit template)
# LAW: resource-chain.md §六 CEO 用机让路律 (2026-10-06, council C-20261006-01 PASS).
# CEO standing order: whichever machine HEARS "wo yao da youxi / wo yao gongzuo" pauses
# THAT machine only (all other machines keep full-speed operation); "quanmian kaigong"
# (full mobilization) = local resume + broadcast fleet O-token -> every machine resumes.
# REFERENCE IMPLEMENTATION (field-tested): bm-c K:\Fluxgroup\.codely-cli\machine-state.ps1 v2.
# DEPLOY: copy this file + gamewin_cron_suspend.py into <Fluxgroup root>\.codely-cli\ as
# machine-state.ps1, then LOCALIZE the three blocks marked ##LOCALIZE below. Idempotent.
# Usage (in-process per U060 law, NO console spawn): & "<root>\.codely-cli\machine-state.ps1" -Mode pause|resume|status

param([Parameter(Mandatory=$true)][ValidateSet("pause","resume","status")][string]$Mode)

$ErrorActionPreference = "Continue"

##LOCALIZE-1: this machine's GPU production Task Scheduler task names (self-report list)
$tasks = @("<LOCALIZE: your GPU production task names>")

##LOCALIZE-2: this machine's LLM stack (comment out lines that do not apply; declare honestly)
$ollamaExe = "<LOCALIZE: ollama.exe full path>"
$pinModel  = "<LOCALIZE: resident model, e.g. qwen3-8b / qwen3.8:4b>"
$keepAliveTask = "<LOCALIZE: ComfyUI/keepalive task name>"

# Portable paths: this script lives at <Fluxgroup root>\.codely-cli\machine-state.ps1
$cronPy = Join-Path $PSScriptRoot "gamewin_cron_suspend.py"

function Kill-GpuHolders {
    # ollama parent + llama-server children (kill-parent-leaves-child pit, 3x proven 10-06)
    Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process llama-server -ErrorAction SilentlyContinue | Stop-Process -Force
    # ComfyUI python (match command line; harmless if this machine has no ComfyUI)
    Get-CimInstance Win32_Process -Filter "name='python.exe'" |
        Where-Object { $_.CommandLine -match "ComfyUI" } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
}

function Get-VramUsedMB {
    $line = nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits
    return [int]($line | Select-Object -First 1)
}

if ($Mode -eq "status") {
    $vram = Get-VramUsedMB
    $ollamaUp = $false
    try { Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 3 | Out-Null; $ollamaUp = $true } catch {}
    $comfyUp = $false
    try { Invoke-RestMethod -Uri "http://127.0.0.1:8188/system_stats" -TimeoutSec 3 | Out-Null; $comfyUp = $true } catch {}
    $taskState = (Get-ScheduledTask -TaskName $tasks -ErrorAction SilentlyContinue | ForEach-Object { $_.TaskName + "=" + $_.State }) -join " "
    Write-Output ("STATE: vramUsedMB={0} ollama={1} comfy={2} tasks[{3}]" -f $vram, $ollamaUp, $comfyUp, $taskState)
    try { Write-Output ("CRON: " + (& python $cronPy status)) } catch { Write-Output "CRON: unknown" }
    if (-not $ollamaUp -and -not $comfyUp) { Write-Output "MODE=pause" }
    elseif ($ollamaUp -and $vram -gt 10000) { Write-Output "MODE=resume" }
    else { Write-Output "MODE=mixed" }
    return
}

if ($Mode -eq "pause") {
    Write-Output "[pause] stopping ollama + llama-server + comfyui ..."
    Kill-GpuHolders
    foreach ($t in $tasks) { try { Disable-ScheduledTask -TaskName $t -ErrorAction Stop | Out-Null; Write-Output "[pause] disabled: $t" } catch { Write-Output "[pause] WARN disable ${t}: $($_.Exception.Message)" } }
    try { Write-Output ("[pause] cron: " + (& python $cronPy suspend)) } catch { Write-Output "[pause] WARN cron suspend: $($_.Exception.Message)" }
    Start-Sleep -Seconds 4
    # hard verification: OUR holders must be gone (process-face, not absolute vram -
    # gaming window keeps vram legitimately used by CEO's own apps)
    $residue = Get-Process llama-server,ollama -ErrorAction SilentlyContinue
    $comfyResidue = Get-CimInstance Win32_Process -Filter "name='python.exe'" | Where-Object { $_.CommandLine -match "ComfyUI" }
    $guard = 0
    while (($residue -or $comfyResidue) -and $guard -lt 3) {
        Get-Process llama-server,ollama -ErrorAction SilentlyContinue | Stop-Process -Force
        Get-CimInstance Win32_Process -Filter "name='python.exe'" | Where-Object { $_.CommandLine -match "ComfyUI" } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
        Start-Sleep -Seconds 4
        $residue = Get-Process llama-server,ollama -ErrorAction SilentlyContinue
        $comfyResidue = Get-CimInstance Win32_Process -Filter "name='python.exe'" | Where-Object { $_.CommandLine -match "ComfyUI" }
        $guard++
    }
    if ($residue -or $comfyResidue) { Write-Output "[pause] FAIL: production residue still alive - manual check"; exit 1 }
    $vram = Get-VramUsedMB
    Write-Output ("[pause] OK production-clean (vramUsedMB={0} = CEO desktop/gaming face, none ours)" -f $vram)
    return
}

if ($Mode -eq "resume") {
    Write-Output "[resume] enabling production tasks ..."
    foreach ($t in $tasks) { try { Enable-ScheduledTask -TaskName $t -ErrorAction Stop | Out-Null; Write-Output "[resume] enabled: $t" } catch { Write-Output "[resume] WARN enable ${t}: $($_.Exception.Message)" } }
    try { Write-Output ("[resume] cron: " + (& python $cronPy restore)) } catch { Write-Output "[resume] WARN cron restore: $($_.Exception.Message)" }
    if ($pinModel -and $pinModel -notmatch "^<") {
        $env:OLLAMA_HOST = "0.0.0.0"
        if (-not (Get-Process ollama -ErrorAction SilentlyContinue)) {
            Start-Process -FilePath $ollamaExe -ArgumentList "serve" -WindowStyle Hidden
            Write-Output "[resume] ollama serve started"
        }
        $ok = $false
        foreach ($i in 1..12) {
            Start-Sleep -Seconds 3
            try {
                $body = '{"model":"' + $pinModel + '","prompt":"ping","stream":false,"keep_alive":-1}'
                $r = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -ContentType "application/json" -Body $body -TimeoutSec 240
                if ($r.done) { $ok = $true; break }
            } catch {}
        }
        if ($ok) { Write-Output "[resume] resident model pinned: $pinModel keep_alive=forever" }
        else { Write-Output "[resume] WARN model pin pending (API not up yet) - retry next window" }
    }
    if ($keepAliveTask -and $keepAliveTask -notmatch "^<") {
        try { Start-ScheduledTask -TaskName $keepAliveTask -ErrorAction Stop; Write-Output "[resume] keepalive kicked" } catch { Write-Output "[resume] WARN keepalive kick: $($_.Exception.Message)" }
    }
    $vram = Get-VramUsedMB
    Write-Output ("[resume] OK vramUsedMB={0}" -f $vram)
    return
}
