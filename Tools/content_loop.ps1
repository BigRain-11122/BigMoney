# CONTENT-LOOP v0.1 driver -- drama line, bm-b host (O-20261018-2144 sec.2.1,
# O-20261018-2236 10-min idle SLA family). One round per fire:
#   python Tools\content_loop_step.py round   (locked queue scan -> claim ->
#   run station -> regenerate QUEUE.md -> book round row)
# Activity gate v0.1 = schtasks ExecutionTimeLimit 35min hard cap; the
# iteration_loop v2 silent-gate (25min zero-output) lands in v0.2 together
# with the runner registry expansion. Zero-window: task runs via wscript
# InvisibleRunner hidden chain + S4U (see register_content_loop_task.ps1).
# bm-b-only carrier: honest stdout no-op on other machines.
# ENCODING: this file is pure ASCII (loop ENCODING RULE).
$Project = Split-Path -Parent $PSScriptRoot
$mid = ''
try {
    $mid = (Get-Content (Join-Path $Project 'fleet\machine.json') -Raw -ErrorAction Stop | ConvertFrom-Json).machine_id
} catch {}
if ($mid -ne 'bm-b') {
    Write-Output ("CONTENT-LOOP carrier is bm-b-hosted; machine=" + $mid + " -> honest no-op")
    exit 0
}
$log = Join-Path $Project 'results\content_loop_driver.log'
$ts = Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz'
try {
    $out = & python (Join-Path $Project 'Tools\content_loop_step.py') 'round' 2>&1 | Out-String
    Add-Content -Path $log -Value ($ts + ' | ' + ($out -replace "`r`n", ' ').Trim())
    Write-Output $out
} catch {
    Add-Content -Path $log -Value ($ts + ' | DRIVER-ERROR ' + $_.Exception.Message)
    Write-Output ('DRIVER-ERROR: ' + $_.Exception.Message)
    exit 1
}
