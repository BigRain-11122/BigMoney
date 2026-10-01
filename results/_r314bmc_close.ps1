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
# fresh machine metrics (in-process cmdlets + one hidden nvidia-smi)
$os = Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average
$cpu = [math]::Round($os.Average, 1)
$ram = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB, 1)
$g = Run-Hidden 'nvidia-smi' '--query-gpu=memory.free --format=csv,noheader,nounits' $repo
$gpu = 0
if ($g.rc -eq 0 -and $g.out.Trim() -ne '') { $gpu = [int]$g.out.Trim() }
Write-Output ('metrics: cpu=' + $cpu + ' ram_free_gb=' + $ram + ' gpu_free_mib=' + $gpu)
$r = Run-Hidden 'python' ('K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r314bmc_close_files.py ' + $cpu + ' ' + $ram + ' ' + $gpu) $repo
Write-Output $r.out
if ($r.err) { Write-Output ('PY_ERR: ' + $r.err) }
if ($r.rc -ne 0) { Write-Output 'CLOSE-FILES FAILED'; exit 1 }
# heartbeat epoch int self-check (smoke F7 law)
$hb = Get-Content (Join-Path $repo 'fleet\machines\bm-c.json') -Raw | ConvertFrom-Json
if ($hb.heartbeat_epoch_utc -is [int]) { Write-Output ('epoch int check: OK ' + $hb.heartbeat_epoch_utc) } else { Write-Output 'EPOCH NOT INT - FIX' ; exit 1 }
# targeted add: all current M + my untracked scripts (all are this round's products)
Write-Output '--- add round outputs ---'
& $sg -GitArgs 'add -A' -Cwd $repo
Write-Output '--- staged stat ---'
& $sg -GitArgs 'diff --cached --stat' -Cwd $repo
Write-Output '--- commit ---'
& $sg -GitArgs 'commit -m "round 314: triple-crash adoption + CAS cherry-pick fleet integration + W8 products 4 files to origin (5/12) + wild_route adoption-verified (393-cell byte identity) + monthly trio fresh-base refresh + S6 35 legs rc0"' -Cwd $repo
Write-Output ('commit rc=' + $LASTEXITCODE)
Write-Output '--- push ---'
& $sg -GitArgs 'push origin main' -Cwd $repo
Write-Output ('push rc=' + $LASTEXITCODE)
if ($LASTEXITCODE -ne 0) {
  & $sg -GitArgs 'fetch origin' -Cwd $repo
  & $sg -GitArgs 'push origin main' -Cwd $repo
  Write-Output ('push retry rc=' + $LASTEXITCODE)
}
Write-Output '--- 送达核验: fetch + rev-list + ls-tree ---'
& $sg -GitArgs 'fetch origin' -Cwd $repo
& $sg -GitArgs 'rev-list --left-right --count origin/main...HEAD' -Cwd $repo
& $sg -GitArgs 'ls-tree --name-only origin/main results/briefings/' -Cwd $repo
& $sg -GitArgs 'ls-tree --name-only origin/main results/p2cal_ext/n1_w8/ | wc -l' -Cwd $repo
Write-Output '--- final status ---'
& $sg -GitArgs 'status --porcelain' -Cwd $repo
Write-Output ('NOW: ' + (Get-Date -Format 'HH:mm:ss'))
Write-Output '=== r314 close done ==='
