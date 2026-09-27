# Installs/refreshes the pre-commit conflict-marker claw (D-20260927-05 item-iii)
# from the versioned canonical copy Tools\git-hooks\pre-commit into .git\hooks\.
# .git\hooks is machine-local (never synced by git) - each machine runs this once;
# the loop S7 self-heal line re-runs it on drift. Idempotent by design (-Force copy).
# CRLF->LF normalized on install (autocrlf smudge safety, r331 pitlaw): sh.exe must
# not see CR. PATH-AGNOSTIC. Pure ASCII. Zero-token.
$Project = Split-Path -Parent $PSScriptRoot
$src = Join-Path $Project 'Tools\git-hooks\pre-commit'
if (-not (Test-Path $src)) { Write-Output "FATAL: $src missing"; exit 1 }
$dst = Join-Path $Project '.git\hooks\pre-commit'
$raw = Get-Content -Raw -LiteralPath $src
Copy-Item -LiteralPath $src -Destination $dst -Force
$bytes = [System.IO.File]::ReadAllBytes($dst)
# strip CR bytes (0x0D) so the hook is pure LF regardless of autocrlf checkout
$clean = New-Object System.Collections.Generic.List[byte]
foreach ($b in $bytes) { if ($b -ne 13) { $clean.Add($b) } }
[System.IO.File]::WriteAllBytes($dst, $clean.ToArray())
if ((Test-Path $dst) -and -not ((Get-Content -Raw $dst).Contains("`r"))) {
    Write-Output "pre-commit claw installed -> $dst (LF-normalized)"
} else {
    Write-Output "FATAL: claw install/verify failed"; exit 1
}
