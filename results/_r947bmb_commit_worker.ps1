# r947 bm-b commit worker (ASCII-only per PS5.1 GBK pit law)
# Detached: commits r947 products via temp-index plumbing (avoids restore-worker's index.lock),
# pushes with protocol fallback (main -> machine/bm-b-r947). Bounded git calls, full logging.
$ErrorActionPreference = 'Continue'
$bm = 'C:\Fluxgroup\FluxGroup\quant\bigmoney'
$log = "$bm\results\_r947bmb_commit_worker.log"
function W([string]$m) { Add-Content -Path $log -Value ("{0} {1}" -f (Get-Date -Format s), $m) -Encoding UTF8 }
function RunGit([string[]]$argv, [int]$secs) {
    $p = Start-Process -FilePath git -ArgumentList $argv -WorkingDirectory $bm -PassThru -WindowStyle Hidden -RedirectStandardOutput "$env:TEMP\cw_out.txt" -RedirectStandardError "$env:TEMP\cw_err.txt"
    if ($p.WaitForExit($secs * 1000)) { return $p.ExitCode } else { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue; return 999 }
}

W "commit worker start pid=$PID"

# 1. fetch delta (retry x2, 90s each)
$rc = RunGit @('fetch','origin','+refs/heads/main:refs/remotes/origin/main') 90
if ($rc -ne 0) { W "fetch attempt1 rc=$rc retrying"; $rc = RunGit @('fetch','origin','+refs/heads/main:refs/remotes/origin/main') 90 }
W ("fetch rc={0} origin/main={1}" -f $rc, (git -C $bm rev-parse --short refs/remotes/origin/main 2>&1))

# 2. temp-index plumbing commit
$env:GIT_INDEX_FILE = "$bm\.git\tmp-index-r947"
$null = RunGit @('read-tree','refs/remotes/origin/main') 60
$null = RunGit @('update-index','--add','state.json','logs/iteration-loop/round_reports.md','results/_r947bmb_gitloss_forensics.json','results/_r947bmb_restore_worker.ps1','results/_r947bmb_closeout.py','results/_r947bmb_restore_worker.log','fleet/inbox/MSG-20261014-2015-bmb.md') 120
$tree = git -C $bm write-tree 2>&1
W "tree=$tree"
Remove-Item Env:\GIT_INDEX_FILE -ErrorAction SilentlyContinue
if ($tree -notmatch '^[0-9a-f]{40}$') { W "write-tree FAILED ($tree) - aborting, r948 manual commit"; exit 1 }

$commit = git -C $bm commit-tree $tree -p refs/remotes/origin/main -m "round 947: git-loss recovery v2 (lean fetch rebuild ebf8a644 + detached restore worker + forensics/MSG) [via bm-b]" 2>&1
W "commit=$commit"
if ($commit -notmatch '^[0-9a-f]{40}$') { W "commit-tree FAILED ($commit) - aborting"; exit 1 }

$null = git -C $bm update-ref refs/heads/main $commit 2>&1
W "main updated to $commit"

# 3. push main, fallback machine branch
$rc = RunGit @('push','origin','main') 120
W "push main rc=$rc"
if ($rc -ne 0) {
    W "push main failed -> protocol fallback branch"
    $rc2 = RunGit @('push','origin',("HEAD:refs/heads/machine/bm-b-r947")) 120
    W "push machine/bm-b-r947 rc=$rc2"
}

# 4. verify + cleanup
$remote = git -C $bm ls-remote origin main 2>&1
W "ls-remote main: $remote"
Remove-Item "$bm\.git\tmp-index-r947" -Force -ErrorAction SilentlyContinue
W "commit worker done"
