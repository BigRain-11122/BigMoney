# r312 bm-c S0/S0.5 batched check -- zero-window (all native exes via CreateNoWindow)
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
  $oT = $p.StandardOutput.ReadToEndAsync()
  $e = $p.StandardError.ReadToEnd()
  $o = $oT.Result
  $p.WaitForExit()
  return @{ out = $o; err = $e; rc = $p.ExitCode }
}

Write-Output '=== S0: fetch + status + rebase state ==='
& $sg -GitArgs 'fetch origin' -Cwd $repo
Write-Output '--- status porcelain ---'
& $sg -GitArgs 'status --porcelain' -Cwd $repo
Write-Output '--- log -3 ---'
& $sg -GitArgs 'log --oneline -3' -Cwd $repo
Write-Output '--- ahead(left=behind-us? no: left=origin-only, right=us-only) ---'
& $sg -GitArgs 'rev-list --left-right --count origin/main...HEAD' -Cwd $repo
Write-Output '--- rebase/lock state files ---'
$rb = @()
foreach ($f in @('rebase-merge','rebase-apply','REBASE_HEAD','CHERRY_PICK_HEAD','MERGE_HEAD','index.lock')) {
  if (Test-Path (Join-Path $repo ('.git\' + $f))) { $rb += $f }
}
if ($rb.Count -gt 0) { Write-Output ('REBASE-STATE: ' + ($rb -join ',')) } else { Write-Output 'REBASE-STATE: clean' }

Write-Output '=== S0.5: D-19 fresh-read (group tree, zero-touch) ==='
& $sg -GitArgs 'fetch origin' -Cwd 'K:\Fluxgroup\FluxGroup'
$tmpy = 'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r312bmc_dec_check.py'
$pycode = @'
import hashlib, subprocess
raw = subprocess.check_output(['git','-C','K:/Fluxgroup/FluxGroup','show','origin/main:docs/decisions.md'])
print('DEC_SHA=' + hashlib.sha256(raw).hexdigest())
raw_o = subprocess.check_output(['git','-C','K:/Fluxgroup/FluxGroup','show','origin/main:docs/orders.md']).decode('utf-8','replace')
lines = raw_o.splitlines()
print('ORDERS_FILE_LINES=' + str(len(lines)))
ceo = [l for l in lines if 'bm-c' in l and ('\u5f85' in l or '\u7269\u7406' in l)]
print('CEO_PHYS_LINES_MATCHING_BMC=' + str(len(ceo)))
for l in ceo[-10:]:
    print('CEO_ROW: ' + l[:200])
'@
Set-Content -Path $tmpy -Value $pycode -Encoding UTF8
$r = Run-Hidden 'python' $tmpy $repo
Write-Output $r.out
if ($r.err) { Write-Output ('PY_ERR: ' + $r.err) }
Write-Output '=== done ==='
