$h1 = Get-Content .git\hooks\pre-commit -Raw -ErrorAction SilentlyContinue
$r1 = Get-Content Tools\git-hooks\pre-commit -Raw
$h2 = Get-Content .git\hooks\pre-push -Raw -ErrorAction SilentlyContinue
$r2 = Get-Content Tools\git-hooks\pre-push -Raw
$precommit_match = ($h1 -replace "`r","") -eq ($r1 -replace "`r","")
$prepush_match = ($h2 -replace "`r","") -eq ($r2 -replace "`r","")
Write-Output ("precommit_match={0}" -f $precommit_match)
Write-Output ("prepush_match={0}" -f $prepush_match)
