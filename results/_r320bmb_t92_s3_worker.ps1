# Audio queue worker: polls E:\Minigame\Tools\audio-queue\incoming for work-order
# JSONs, renders each through the X989 mastered chain (audio_render_order.py),
# then moves each order to done\ or failed\. T-92 s3 idle-window lane face:
# callers must respect the fleet envelope law (RAM<4GB -> no new heavy jobs,
# full silent, zero popup; this lane uses CPU only, GPU stays with the 7b serve
# per P-19). Submitters drop JSON work orders into incoming\ and never run
# piper/ffmpeg themselves. PURE ASCII (PS5.1 GBK rule).
param(
    [string]$QueueDir = 'E:\Minigame\Tools\audio-queue',
    [int]$LockMaxAgeMinutes = 30
)
$ErrorActionPreference = 'Continue'
$in = Join-Path $QueueDir 'incoming'
$done = Join-Path $QueueDir 'done'
$fail = Join-Path $QueueDir 'failed'
foreach ($d in @($in, $done, $fail)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }
$lock = Join-Path $QueueDir 'worker.lock'
if (Test-Path $lock) {
    $age = ((Get-Date) - (Get-Item $lock).LastWriteTime).TotalMinutes
    if ($age -lt $LockMaxAgeMinutes) { exit 0 }
}
Set-Content -Path $lock -Value (Get-Date -Format s) -Encoding ASCII
try {
    $reqs = @(Get-ChildItem $in -Filter *.json -ErrorAction SilentlyContinue)
    if ($reqs.Count -eq 0) { exit 0 }
    foreach ($r in $reqs) {
        $log = Join-Path $QueueDir ('run_' + $r.BaseName + '.log')
        & python (Join-Path $QueueDir 'audio_render_order.py') $r.FullName 2>&1 | Out-File $log -Encoding utf8
        if ($LASTEXITCODE -eq 0) {
            Move-Item $r.FullName (Join-Path $done $r.Name) -Force
            Add-Content (Join-Path $QueueDir 'worker.log') ("{0} OK {1}" -f (Get-Date -Format s), $r.Name)
        } else {
            Move-Item $r.FullName (Join-Path $fail $r.Name) -Force
            Add-Content (Join-Path $QueueDir 'worker.log') ("{0} FAIL {1} exit={2}" -f (Get-Date -Format s), $r.Name, $LASTEXITCODE)
        }
    }
}
finally {
    Remove-Item $lock -Force -ErrorAction SilentlyContinue
}
