$env:GIT_EDITOR='true'
$git = "C:\Program Files\Git\cmd\git.exe"
for ($i = 0; $i -lt 12; $i++) {
  $uu = & $git ls-files -u 2>$null | ForEach-Object { ($_ -split "`t")[-1] } | Sort-Object -Unique
  if ($uu) {
    & $git checkout --ours -- @($uu) 2>$null
    if ($LASTEXITCODE -ne 0) { Write-Output "CHECKOUT-FAIL"; break }
    & $git add -A 2>$null
  }
  $out = & $git rebase --continue 2>&1 | Select-Object -First 3
  Write-Output "RING $i : $out"
  if (-not (& $git status --porcelain 2>$null | Select-String '^(UU|AA)')) {
    $st = (& $git status 2>$null | Select-Object -First 1)
    Write-Output "STATUS: $st"
    if ($st -notmatch 'interactive rebase in progress') { break }
  }
}
& $git log -5 --oneline
