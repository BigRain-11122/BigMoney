# r635 bm-b reland pass 3 (v2): robust error handling - explicit rc checks, no global Stop pref.
# ASCII-only comments (PS5.1 GBK law). Reuses iso if present.
$iso = "$env:TEMP\bmb-iso-r635c"
Set-Location "C:\Fluxgroup\FluxGroup\quant\bigmoney"

function Step($n, $t) { Write-Host "[$n] $t" }

if (Test-Path "$iso\.git") {
    Step 1 "iso exists - reusing current state"
} else {
    git worktree add $iso origin/main *> $null
    if ($LASTEXITCODE -ne 0) { throw "worktree add failed" }
    Step 1 "iso created at origin/main"
    git -C $iso cherry-pick 860f34199 *> $null
    if ($LASTEXITCODE -ne 0) { Step 2 "cherry-pick stopped (conflicts expected, rc=$LASTEXITCODE)" }
}

$uu = @(git -C $iso status --porcelain | Select-String -Pattern "^(UU|AA|AU|UA|DU|UD|DD)")
Step 2 "UU count: $($uu.Count)"
$uu | ForEach-Object { Write-Host "    $_" }

python results\_r635bmb_resolve2.py $iso
if ($LASTEXITCODE -ne 0) { throw "resolver failed rc=$LASTEXITCODE" }

git -C $iso add -A
$uu2 = @(git -C $iso status --porcelain | Select-String -Pattern "^(UU|AA|AU|UA|DU|UD|DD)")
if ($uu2.Count -gt 0) { throw "UNRESOLVED UU remains: $($uu2 -join ',')" }
Step 3 "zero UU remaining"

$dels = @(git -C $iso diff --cached --name-status HEAD | Select-String -Pattern "^D")
if ($dels.Count -gt 0) { throw "STAGED DELETION SET non-empty: $($dels -join ',')" }
Step 4 "zero staged deletions"

$mk = git -C $iso grep --cached -l -E "^<<<<<<< |^=======$|^>>>>>>> " 2>$null
if ($LASTEXITCODE -eq 0) { throw "markers present in staged tree: $mk" }
Step 5 "staged tree marker-clean"

git -C $iso cherry-pick --continue --no-edit *> $null
if ($LASTEXITCODE -ne 0) { throw "cherry-pick continue failed rc=$LASTEXITCODE" }
$newtip = git -C $iso rev-parse HEAD
$base = git rev-parse origin/main
if ($newtip -eq $base) { throw "cherry-pick did not advance (newtip==base)" }
Step 6 "newtip=$newtip"

$mainnow = git rev-parse main
Step 7 "main-before=$mainnow"
git update-ref "refs/backup/bmb-r635-watchdog-sweep" $mainnow 2>$null
git update-ref refs/heads/main $newtip
Step 8 "main moved to newtip"

git push origin main:main 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "[9] PUSH REJECTED - main left at newtip (ahead); iterate"; exit 2 }
Step 9 "push OK"

git reset --mixed *> $null
Step 10 "index resynced to new main (worktree untouched)"

git worktree remove $iso --force 2>$null
git worktree prune
Step 11 "iso cleaned"
git log --oneline -3
git status --porcelain
