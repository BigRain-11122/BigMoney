# r314 bm-c tree surgery part 2 -- CAS cherry-pick integration onto origin/main
$ErrorActionPreference = 'Continue'
$repo = 'K:\Fluxgroup\FluxGroup\quant\bigmoney'
$sg   = 'K:\Fluxgroup\FluxGroup\quant\.codely-cli\scratch\silent-git.ps1'
Write-Output ('NOW: ' + (Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz'))
Write-Output '--- fresh fetch ---'
& $sg -GitArgs 'fetch origin' -Cwd $repo
Write-Output '--- old main (expected ea71e0aa1) ---'
& $sg -GitArgs 'rev-parse refs/heads/main' -Cwd $repo
Write-Output '--- detach at origin/main ---'
& $sg -GitArgs 'checkout --detach origin/main' -Cwd $repo
Write-Output '--- cherry-pick 936da95cb (HQ C-03 commit) ---'
& $sg -GitArgs 'cherry-pick 936da95cb' -Cwd $repo
Write-Output ('rc=' + $LASTEXITCODE)
Write-Output '--- state after pick1 ---'
& $sg -GitArgs 'status --porcelain' -Cwd $repo
Write-Output '--- unmerged files ---'
& $sg -GitArgs 'diff --name-only --diff-filter=U' -Cwd $repo
Write-Output '=== done part2-step1 ==='
