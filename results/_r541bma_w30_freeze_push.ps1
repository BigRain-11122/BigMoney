$ErrorActionPreference = "Stop"
# r541 W30 surgical freeze push (r512 clean route: temp index on origin/main,
# zero stash, zero rebase, zero working-tree touch). Parent rev-parsed live
# per r519 law (daemon 1-min fetch makes pre-stored shas stale).
$repo = "C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
$env:GIT_INDEX_FILE = "$repo\.git\_r541_tmp_index"
try {
  git -C $repo fetch origin 2>&1 | Out-Null
  $parent = (git -C $repo rev-parse origin/main).Trim()
  Write-Host "parent=$parent"
  # r511 table-tail lock re-check: no W30 row on origin at push time
  $canon = git -C $repo show "origin/main:research/PERPETUAL_FACES.md"
  $txt = $canon -join "`n"
  if ($txt -match "N1 波30") { throw "r511 lock: W30 row already on origin" }
  git -C $repo read-tree $parent
  $files = @(
    "research/PERPETUAL_FACES.md",
    "research/PERPETUAL_N1_W30_PREREG.md",
    "results/_r541bma_w30_band_gate.py",
    "scripts/perpetual_faces.py",
    "scripts/perpetual_faces_n1.py"
  )
  foreach ($f in $files) {
    $sha = (git -C $repo hash-object -w $f).Trim()
    git -C $repo update-index --add --cacheinfo "100644,$sha,$f"
  }
  $tree = (git -C $repo write-tree).Trim()
  $commit = (git -C $repo commit-tree $tree -p $parent -F "$repo\results\_r541bma_w30_msg.txt").Trim()
  Write-Host "commit=$commit"
  git -C $repo push origin "${commit}:refs/heads/main" 2>&1 | Out-Host
  Write-Host "PUSH_OK"
} finally {
  Remove-Item env:GIT_INDEX_FILE -ErrorAction SilentlyContinue
  Remove-Item "$repo\.git\_r541_tmp_index" -Force -ErrorAction SilentlyContinue
}
