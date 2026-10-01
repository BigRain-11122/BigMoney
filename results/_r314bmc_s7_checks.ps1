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
Write-Output '--- watermark.jsonl last line ---'
$wm = Join-Path $repo 'results\watermark.jsonl'
if (Test-Path $wm) { Get-Content $wm -Tail 1 }
Write-Output '--- watermark_red.json ---'
$wr = Join-Path $repo 'results\watermark_red.json'
if (Test-Path $wr) { Get-Content $wr -Raw }
Write-Output '--- git status after chain ---'
& $sg -GitArgs 'status --porcelain' -Cwd $repo
Write-Output '--- schtasks: loop + watchdog (R49: schtasks /query authority) ---'
$r1 = Run-Hidden 'schtasks' '/query /tn Bigmoney-IterationLoop /fo LIST' $repo
Write-Output ($r1.out -split "`n" | Where-Object { $_ -match 'TaskName|Status|Next Run|Last Run|Last Result' } | ForEach-Object { $_.Trim() })
$r2 = Run-Hidden 'schtasks' '/query /tn Bigmoney-LoopWatchdog /fo LIST' $repo
Write-Output ($r2.out -split "`n" | Where-Object { $_ -match 'TaskName|Status|Next Run|Last Run|Last Result' } | ForEach-Object { $_.Trim() })
Write-Output '--- precommit claw compare (CR-normalized) ---'
$hook = Get-Content (Join-Path $repo '.git\hooks\pre-commit') -Raw -ErrorAction SilentlyContinue
$ref  = Get-Content (Join-Path $repo 'Tools\git-hooks\pre-commit') -Raw -ErrorAction SilentlyContinue
if ($null -ne $hook -and $null -ne $ref) {
  $h = $hook -replace "`r",""
  $r = $ref -replace "`r",""
  if ($h -eq $r) { Write-Output 'CLAW: identical' } else { Write-Output 'CLAW: DIFFERS from Tools reference' }
} else { Write-Output ('CLAW: hook exists=' + ($null -ne $hook) + ' ref exists=' + ($null -ne $ref)) }
Write-Output '--- move processed inbox msgs (addressed to bm-c / ALL) ---'
$inbox = Join-Path $repo 'fleet\inbox'
$proc  = Join-Path $repo 'fleet\inbox\processed'
if (-not (Test-Path $proc)) { New-Item -ItemType Directory -Path $proc | Out-Null }
foreach ($m in @('MSG-20261001-113x-bmb-ALL-t139-akshare-face.md','MSG-20261001-112x-bmc-bma-n2-yield.md')) {
  $src = Join-Path $inbox $m
  if (Test-Path $src) { Move-Item $src (Join-Path $proc $m) -Force; Write-Output ('moved: ' + $m) }
}
Write-Output '--- remaining inbox ---'
Get-ChildItem $inbox -File | ForEach-Object { Write-Output $_.Name }
Write-Output ('NOW: ' + (Get-Date -Format 'HH:mm:ss'))
