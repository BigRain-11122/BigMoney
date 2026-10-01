$ErrorActionPreference = 'Continue'
$repo = 'K:\Fluxgroup\FluxGroup\quant\bigmoney'
$sg   = 'K:\Fluxgroup\FluxGroup\quant\.codely-cli\scratch\silent-git.ps1'
function Run-Hidden([string]$exe, [string]$argline, [string]$cwd) {
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $exe; $psi.Arguments = $argline
  if ($cwd) { $psi.WorkingDirectory = $cwd }
  $psi.UseShellExecute = $false; $psi.CreateNoWindow = $true
  $psi.RedirectStandardOutput = $true; $psi.RedirectStandardError = $true
  $p = [System.Diagnostics.Process]::Start($psi)
  $oT = $p.StandardOutput.ReadToEndAsync(); $e = $p.StandardError.ReadToEnd()
  $o = $oT.Result; $p.WaitForExit()
  return @{ out = $o; err = $e; rc = $p.ExitCode }
}
Write-Output ('NOW: ' + (Get-Date -Format 'HH:mm:ss'))
$oldMain = (& $sg -GitArgs 'rev-parse refs/heads/main' -Cwd $repo | Select-Object -Last 1).Trim()
Write-Output ('oldMain=' + $oldMain)
Write-Output '--- incoming 11 ---'
& $sg -GitArgs 'log --oneline -11 HEAD..origin/main' -Cwd $repo
& $sg -GitArgs 'checkout --detach origin/main' -Cwd $repo
& $sg -GitArgs 'cherry-pick ae8615f54' -Cwd $repo
Write-Output ('pick rc=' + $LASTEXITCODE)
if ($LASTEXITCODE -eq 0) {
  Write-Output 'CLEAN PICK -- no conflicts'
} else {
  $un = (& $sg -GitArgs 'diff --name-only --diff-filter=U' -Cwd $repo) -join '|'
  Write-Output ('UNMERGED=' + $un)
  if ($un.Trim() -ne '') {
    $files = $un.Split('|') | Where-Object { $_.Trim() -ne '' }
    $argline = 'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r314bmc_resolver2.py ' + ($files -join ' ')
    $r = Run-Hidden 'python' $argline $repo
    Write-Output $r.out
    if ($r.err) { Write-Output ('PY_ERR: ' + $r.err) }
    if ($r.rc -ne 0) { Write-Output 'RESOLVER FAILED -- fallback needed'; exit 1 }
    & $sg -GitArgs ('add -- ' + ($files -join ' ')) -Cwd $repo
    & $sg -GitArgs 'commit -C ae8615f54' -Cwd $repo
    Write-Output ('resolve-commit rc=' + $LASTEXITCODE)
  }
}
$newSha = (& $sg -GitArgs 'rev-parse HEAD' -Cwd $repo | Select-Object -Last 1).Trim()
Write-Output ('newSha=' + $newSha)
& $sg -GitArgs ('update-ref refs/heads/main ' + $newSha + ' ' + $oldMain) -Cwd $repo
Write-Output ('CAS rc=' + $LASTEXITCODE)
if ($LASTEXITCODE -ne 0) { Write-Output 'CAS FAILED -- daemon moved main'; exit 1 }
& $sg -GitArgs 'checkout main' -Cwd $repo
& $sg -GitArgs 'push origin main' -Cwd $repo
Write-Output ('push rc=' + $LASTEXITCODE)
if ($LASTEXITCODE -ne 0) {
  & $sg -GitArgs 'fetch origin' -Cwd $repo
  & $sg -GitArgs 'push origin main' -Cwd $repo
  Write-Output ('push retry rc=' + $LASTEXITCODE)
  if ($LASTEXITCODE -ne 0) {
    & $sg -GitArgs 'push origin HEAD:refs/heads/machine/bm-c-r314' -Cwd $repo
    Write-Output ('FALLBACK branch push rc=' + $LASTEXITCODE)
  }
}
& $sg -GitArgs 'fetch origin' -Cwd $repo
Write-Output '--- rev-list (expect 0 0) ---'
& $sg -GitArgs 'rev-list --left-right --count origin/main...HEAD' -Cwd $repo
Write-Output '--- final status ---'
& $sg -GitArgs 'status --porcelain' -Cwd $repo
Write-Output ('NOW: ' + (Get-Date -Format 'HH:mm:ss'))
