$pc = Get-Content .git\hooks\pre-commit -Raw -ErrorAction SilentlyContinue
$pcCanon = Get-Content Tools\git-hooks\pre-commit -Raw
$pp = Get-Content .git\hooks\pre-push -Raw -ErrorAction SilentlyContinue
$ppCanon = Get-Content Tools\git-hooks\pre-push -Raw
$pcN = ($pc -replace "`r", '')
$pcCN = ($pcCanon -replace "`r", '')
$ppN = ($pp -replace "`r", '')
$ppCN = ($ppCanon -replace "`r", '')
Write-Output ("pre-commit match: " + ($pcN -eq $pcCN))
Write-Output ("pre-push match: " + ($ppN -eq $ppCN))
