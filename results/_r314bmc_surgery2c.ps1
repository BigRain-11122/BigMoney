$ErrorActionPreference = 'Continue'
$repo = 'K:\Fluxgroup\FluxGroup\quant\bigmoney'
$sg   = 'K:\Fluxgroup\FluxGroup\quant\.codely-cli\scratch\silent-git.ps1'
Write-Output ('NOW: ' + (Get-Date -Format 'HH:mm:ss'))
& $sg -GitArgs 'checkout -- results/dispatcher_state.bm-c.json' -Cwd $repo
& $sg -GitArgs 'cherry-pick ea71e0aa1' -Cwd $repo
Write-Output ('pick2 rc=' + $LASTEXITCODE)
Write-Output '--- unmerged ---'
& $sg -GitArgs 'diff --name-only --diff-filter=U' -Cwd $repo
Write-Output '--- status short ---'
& $sg -GitArgs 'status --porcelain' -Cwd $repo
Write-Output '=== done pick2 ==='
