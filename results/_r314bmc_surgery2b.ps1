# r314 bm-c surgery part2b -- abort empty pick, restore daemon-rewritten lane file, detach, real pick
$ErrorActionPreference = 'Continue'
$repo = 'K:\Fluxgroup\FluxGroup\quant\bigmoney'
$sg   = 'K:\Fluxgroup\FluxGroup\quant\.codely-cli\scratch\silent-git.ps1'
Write-Output ('NOW: ' + (Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz'))
& $sg -GitArgs 'cherry-pick --abort' -Cwd $repo
Write-Output ('abort rc=' + $LASTEXITCODE)
& $sg -GitArgs 'checkout -- results/autofill_state.bm-c.json' -Cwd $repo
Write-Output '--- status after abort+restore (expect only untracked scripts) ---'
& $sg -GitArgs 'status --porcelain' -Cwd $repo
Write-Output '--- detach at origin/main (retry) ---'
& $sg -GitArgs 'checkout --detach origin/main' -Cwd $repo
Write-Output ('detach rc=' + $LASTEXITCODE)
Write-Output '--- HEAD now ---'
& $sg -GitArgs 'log --oneline -1' -Cwd $repo
Write-Output '--- cherry-pick 936da95cb (real, onto origin tip) ---'
& $sg -GitArgs 'cherry-pick 936da95cb' -Cwd $repo
Write-Output ('pick1 rc=' + $LASTEXITCODE)
Write-Output '--- unmerged ---'
& $sg -GitArgs 'diff --name-only --diff-filter=U' -Cwd $repo
Write-Output '--- status short ---'
& $sg -GitArgs 'status --porcelain' -Cwd $repo
Write-Output '=== done part2b ==='
