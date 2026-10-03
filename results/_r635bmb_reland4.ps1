# r635 bm-b reland pass 4: cherry-pick current main onto latest origin/main (iterative
# convergence under 3-machine push race). Dynamic pick sha, fresh iso each run.
# ASCII-only comments (PS5.1 GBK law).
$iso = "$env:TEMP\bmb-iso-r635d"
Set-Location "C:\Fluxgroup\FluxGroup\quant\bigmoney"
$pick = git rev-parse main
Write-Host "[0] pick=$pick (current main)"

git worktree remove $iso --force 2>$null
git worktree remove "$env:TEMP\bmb-iso-r635c" --force 2>$null
git worktree prune
git fetch origin 2>$null
$base = git rev-parse origin/main
Write-Host "[1] base(origin/main)=$base"

git worktree add $iso $base *> $null
if ($LASTEXITCODE -ne 0) { throw "worktree add failed" }
git -C $iso cherry-pick $pick *> $null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[2] cherry-pick CLEAN (zero conflicts)"
} else {
    $uu = @(git -C $iso status --porcelain | Select-String -Pattern "^(UU|AA|AU|UA|DU|UD|DD)")
    Write-Host "[2] UU count: $($uu.Count)"
    $uu | ForEach-Object { Write-Host "    $_" }
    python results\_r635bmb_resolve2.py $iso
    if ($LASTEXITCODE -ne 0) { throw "resolver failed rc=$LASTEXITCODE" }
}

git -C $iso add -A
$uu2 = @(git -C $iso status --porcelain | Select-String -Pattern "^(UU|AA|AU|UA|DU|UD|DD)")
if ($uu2.Count -gt 0) { throw "UNRESOLVED UU remains: $($uu2 -join ',')" }
$dels = @(git -C $iso diff --cached --name-status HEAD | Select-String -Pattern "^D")
if ($dels.Count -gt 0) { throw "STAGED DELETION SET non-empty: $($dels -join ',')" }
Step3Msg = "zero UU + zero deletions"
Write-Host "[3] $Step3Msg"

git -C $iso grep --cached -l -E "^<<<<<<< |^=======$|^>>>>>>> " 2>$null
if ($LASTEXITCODE -eq 0) { throw "markers present in staged tree" }
Write-Host "[4] staged tree marker-clean"

git -C $iso cherry-pick --continue --no-edit *> $null
if ($LASTEXITCODE -ne 0) { throw "cherry-pick continue failed rc=$LASTEXITCODE" }
$newtip = git -C $iso rev-parse HEAD
if ($newtip -eq $base) { throw "cherry-pick did not advance" }
Write-Host "[5] newtip=$newtip"

git update-ref refs/heads/main $newtip
Write-Host "[6] main moved to newtip"

git push origin main:main 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "[7] PUSH REJECTED again - iterate"; exit 2 }
Write-Host "[7] push OK"

git reset --mixed *> $null
git worktree remove $iso --force 2>$null
git worktree prune
Write-Host "[8] index resynced, iso cleaned"
git log --oneline -2
