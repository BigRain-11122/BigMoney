# One-command machine bootstrap for fleet expansion (O-20260924-1655 sec.2).
#   powershell -NoProfile -ExecutionPolicy Bypass -File Tools\bootstrap-machine.ps1 -Roles bigmoney
# Wraps the actual in-repo paths (no new logic, see fleet/EXPANSION_ACCEPTANCE.md sec.1):
#   1. python bootstrap.py            (deps + Tsinghua mirror fallback + smoke + dashboard data)
#   2. Tools\register_loop_task.ps1    (Bigmoney-IterationLoop, idempotent -Force)
#   3. Tools\register_watchdog_task.ps1 (Bigmoney-LoopWatchdog, idempotent -Force)
#   4. identity guidance              (dual-role template copy ONLY if fleet\machine.json missing)
# PATH-AGNOSTIC. Pure ASCII. Zero-token. Existing machines are safe: identity file
# is never touched when present, register scripts are -Force idempotent.
param(
    [string]$Roles = "bigmoney",
    [switch]$DryRun
)
$Project = Split-Path -Parent $PSScriptRoot
if ($Roles -ne "bigmoney") {
    Write-Output "FATAL: unsupported role '$Roles' (only 'bigmoney' exists today)"
    exit 1
}
$py = "python"
if ($null -ne (Get-Command python -ErrorAction SilentlyContinue)) { } else {
    Write-Output "FATAL: python not on PATH (install Python >= 3.10 first)"
    exit 1
}
$steps = @(
    @{ name = "[1/4] bootstrap.py (deps+mirror fallback+smoke+dashboard)"; cmd = $py;        arg = "bootstrap.py" },
    @{ name = "[2/4] register iteration loop task";                       cmd = "powershell"; arg = "-NoProfile -ExecutionPolicy Bypass -File Tools\register_loop_task.ps1" },
    @{ name = "[3/4] register watchdog task (30min)";                     cmd = "powershell"; arg = "-NoProfile -ExecutionPolicy Bypass -File Tools\register_watchdog_task.ps1" },
    @{ name = "[4/4] identity guidance (template copy only if missing)";  cmd = "";           arg = "" }
)
$rc = 0
foreach ($s in $steps) {
    Write-Output $s.name
    if ($DryRun) { continue }
    if ($s.name.StartsWith("[4/4]")) {
        $idFile = Join-Path $Project "fleet\machine.json"
        $tplDual = Join-Path $Project "fleet\_machine.dual-role.template"
        $tplSingle = Join-Path $Project "fleet\_machine.json.template"
        if (Test-Path $idFile) {
            Write-Output "  fleet\machine.json already present - kept untouched (existing machine)"
        } else {
            $tpl = if (Test-Path $tplDual) { $tplDual } else { $tplSingle }
            Copy-Item $tpl $idFile
            Write-Output "  copied $(Split-Path -Leaf $tpl) -> fleet\machine.json"
            Write-Output "  EDIT fleet\machine.json now: machine_id (BigMoney side: next free bm-d/bm-e) + main_owner (dual-role machines keep Biggame primary)"
        }
        continue
    }
    Push-Location $Project
    & $s.cmd $s.arg.Split(' ') | ForEach-Object { Write-Output "  $_" }
    if ($LASTEXITCODE -ne 0) { Write-Output "FAIL at step: $($s.name) (exit $LASTEXITCODE)"; $rc = 1; Pop-Location; break }
    Pop-Location
}
if ($DryRun) {
    Write-Output "DRY-RUN: no commands executed, no files written"
    exit 0
}
if ($rc -eq 0) {
    Write-Output ""
    Write-Output "MACHINE READY. Next steps per fleet\EXPANSION_ACCEPTANCE.md:"
    Write-Output "  1. write first heartbeat fleet\machines\<machine_id>.json (last_seen/epoch_utc/clock_read same-instant, P-33)"
    Write-Output "  2. take first-job shard: sec.4 J-1 (T-22 PROSPECT beat-rate, --shard/--shards native)"
    Write-Output "  3. S6 maintenance chain runs with the loop - report exit codes honestly"
}
exit $rc
