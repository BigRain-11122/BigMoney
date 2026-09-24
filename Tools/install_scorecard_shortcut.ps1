# T-29 v0.2: 量化战绩 desktop shortcut (CEO direct access, O-1718 s2 + O-2045 s3).
# Creates/refreshes 量化战绩.lnk on the current user's desktop pointing at
# results/daily_scorecard.html. Idempotent; run on the CEO machine (bm-a)
# immediately -- other machines get it via fleet order when they pull.
# FluxVerse install-desktop-shortcut precedent (group reuse per T-29 spec s2).
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$target = Join-Path $root 'results\daily_scorecard.html'
if (-not (Test-Path $target)) {
    Write-Error "scorecard html missing: $target (run scripts\daily_scorecard.py first)"
    exit 1
}
$desktop = [Environment]::GetFolderPath('Desktop')
$lnk = Join-Path $desktop '量化战绩.lnk'
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut($lnk)
$s.TargetPath = $target
$s.WorkingDirectory = $root
$s.Description = 'BigMoney 量化战绩直达（T-29 · O-1718/O-2045 s3）'
$s.IconLocation = "$env:WINDIR\System32\shell32.dll,13"
$s.Save()
Write-Output "shortcut: $lnk -> $target"
