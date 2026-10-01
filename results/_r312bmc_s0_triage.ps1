# r312 bm-c S0 triage batch 2 -- zero-window
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
Write-Output ('NOW: ' + (Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz'))
Write-Output '--- incoming 17 (origin/main not in HEAD) ---'
& $sg -GitArgs 'log --oneline -17 HEAD..origin/main' -Cwd $repo
Write-Output '--- our 1 unpushed commit ---'
& $sg -GitArgs 'log --oneline -3 origin/main..HEAD' -Cwd $repo
Write-Output '--- CODELY.md diff vs HEAD (stat) ---'
& $sg -GitArgs 'diff --stat HEAD -- CODELY.md' -Cwd $repo
Write-Output '--- W7 prereg diff vs HEAD (full) ---'
& $sg -GitArgs 'diff HEAD -- research/PERPETUAL_N1_W7_PREREG.md' -Cwd $repo
Write-Output '--- wild_route_lab.py: committed? (log -3) ---'
& $sg -GitArgs 'log --oneline -3 -- scripts/wild_route_lab.py' -Cwd $repo
& $sg -GitArgs 'diff --stat HEAD -- scripts/wild_route_lab.py' -Cwd $repo
Write-Output '--- n1_w8 shard products on origin? ---'
foreach ($n in 8..11) {
  $p = ('results/p2cal_ext/n1_w8/shard-' + $n + '-of-12.json')
  & $sg -GitArgs ('cat-file -e origin/main:' + $p) -Cwd $repo
  if ($LASTEXITCODE -eq 0) { Write-Output ($p + ' ON-ORIGIN') } else { Write-Output ($p + ' not-on-origin(local-only)') }
}
Write-Output '--- orders dir newest (post-fetch) ---'
$od = Get-ChildItem (Join-Path $repo 'fleet\orders') -Filter '*.md' | Sort-Object LastWriteTime -Descending | Select-Object -First 6
foreach ($f in $od) { Write-Output ($f.Name + ' | mtime ' + $f.LastWriteTime.ToString('MM-dd HH:mm')) }
Write-Output ('orders total: ' + (Get-ChildItem (Join-Path $repo 'fleet\orders') -Filter '*.md').Count)
Write-Output '--- inbox unprocessed ---'
$in = Join-Path $repo 'fleet\inbox'
if (Test-Path $in) {
  $msgs = Get-ChildItem $in -File | Sort-Object LastWriteTime -Descending | Select-Object -First 8
  foreach ($m in $msgs) { Write-Output ($m.Name + ' | ' + $m.LastWriteTime.ToString('MM-dd HH:mm')) }
} else { Write-Output 'no inbox dir' }
Write-Output '--- D-19: extract decisions rows >= 2026-10-01 09:00 to file ---'
$tmpy = 'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r312bmc_dec_rows.py'
$pycode = @'
import subprocess, io, sys
raw = subprocess.check_output(['git','-C','K:/Fluxgroup/FluxGroup','show','origin/main:docs/decisions.md'])
text = raw.decode('utf-8')
lines = text.splitlines()
out = []
capture = False
for l in lines:
    keep = ('2026-10-01' in l and ('09:' in l or '10:' in l or '11:' in l or '12:' in l)) or ('09-30' in l and ('2' in l))
    if keep:
        capture = True
    if capture:
        out.append(l)
open('K:/Fluxgroup/FluxGroup/quant/bigmoney/results/_r312bmc_dec_rows.txt','w',encoding='utf-8').write('\n'.join(out[-400:]))
print('ROWS_FILE_WRITTEN lines=' + str(len(out[-400:])))
print('TOTAL_DEC_LINES=' + str(len(lines)))
'@
Set-Content -Path $tmpy -Value $pycode -Encoding UTF8
$r = Run-Hidden 'python' $tmpy $repo
Write-Output $r.out
if ($r.err) { Write-Output ('PY_ERR: ' + $r.err) }
Write-Output '=== done ==='
