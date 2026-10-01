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
$r = Run-Hidden 'python' 'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r314bmc_resolve_pick2.py' $repo
Write-Output $r.out
if ($r.err) { Write-Output ('PY_ERR: ' + $r.err) }
if ($r.rc -ne 0) { Write-Output 'RESOLVE FAILED -- STOP'; exit 1 }
& $sg -GitArgs 'add CODELY.md results/pool_core_samples.jsonl' -Cwd $repo
& $sg -GitArgs 'commit -C ea71e0aa1' -Cwd $repo
Write-Output ('commit rc=' + $LASTEXITCODE)
Write-Output '--- new stack ---'
& $sg -GitArgs 'log --oneline -4' -Cwd $repo
$newSha = (& "K:\Fluxgroup\FluxGroup\quant\.codely-cli\scratch\silent-git.ps1" -GitArgs 'rev-parse HEAD' -Cwd $repo) | Select-Object -Last 1
$newSha = $newSha.Trim()
Write-Output ('newSha=' + $newSha)
Write-Output '--- CAS update-ref main (expected-old ea71e0aa19c6e6ed9449c59f3c1161d6c3f31763) ---'
& $sg -GitArgs ('update-ref refs/heads/main ' + $newSha + ' ea71e0aa19c6e6ed9449c59f3c1161d6c3f31763') -Cwd $repo
Write-Output ('update-ref rc=' + $LASTEXITCODE)
if ($LASTEXITCODE -ne 0) { Write-Output 'CAS FAILED -- daemon moved main -- STOP'; exit 1 }
& $sg -GitArgs 'checkout main' -Cwd $repo
Write-Output ('checkout rc=' + $LASTEXITCODE)
Write-Output '--- ahead/behind after integration (expect 0 behind / 2 ahead) ---'
& $sg -GitArgs 'rev-list --left-right --count origin/main...HEAD' -Cwd $repo
Write-Output '--- push ---'
& $sg -GitArgs 'push origin main' -Cwd $repo
Write-Output ('push rc=' + $LASTEXITCODE)
if ($LASTEXITCODE -ne 0) {
  Write-Output '--- push rejected: fetch + retry once ---'
  & $sg -GitArgs 'fetch origin' -Cwd $repo
  & $sg -GitArgs 'push origin main' -Cwd $repo
  Write-Output ('push retry rc=' + $LASTEXITCODE)
}
Write-Output '--- 送达核验: fetch + ls-tree carried files + rev-list ---'
& $sg -GitArgs 'fetch origin' -Cwd $repo
& $sg -GitArgs 'ls-tree --name-only origin/main results/p2cal_ext/n1_w8/' -Cwd $repo
& $sg -GitArgs 'rev-list --left-right --count origin/main...HEAD' -Cwd $repo
Write-Output '=== done integration ==='
