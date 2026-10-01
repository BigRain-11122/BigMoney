$g='git'
& $g fetch origin *>&1 | Out-Null
$parent = (& $g rev-parse origin/main).Trim()
Write-Host "parent=$parent"

$idx = Join-Path $env:TEMP 'fg-r530close-idx'
if(Test-Path $idx){ Remove-Item $idx -Force }
$env:GIT_INDEX_FILE = $idx
& $g read-tree $parent 2>&1 | Out-Null

# payload: round-close faces (state/heartbeat/round-report/CODELY/tools)
# + local lane files (engine ledger superset -- local-authority face).
# Shared daemon-written faces (p1d_gates/pool_core_samples/autofill_state/
# update_status/token_usage/runnable_pool/pool_claims) stay OUT of payload
# (concurrent multi-writer: origin side wins, local daemon rewrites next tick).
$payload = @(
  "state.json",
  "fleet/machines/bm-b.json",
  "logs/iteration-loop/round_reports.md",
  "CODELY.md",
  "results/saturation_engine/ledger_bm-b.jsonl",
  "results/saturation_engine/history_bm-b.jsonl",
  "results/saturation_engine/state_bm-b.json",
  "results/saturation_engine/face_bm-b.json",
  "results/_r530bmb_pool_ram_probe.py",
  "results/_r530bmb_s7_state.py",
  "results/_r530bmb_s7_reports.py",
  "results/_r530bmb_push_w38_final.ps1"
)
foreach($f in $payload){
  if(-not (Test-Path $f)){ Write-Host "MISSING $f -- skip"; continue }
  $blob = (& $g hash-object -w $f).Trim()
  & $g update-index --add --cacheinfo "100644,$blob,$f"
  if($LASTEXITCODE -ne 0){ Write-Host "update-index FAILED $f"; Remove-Item Env:GIT_INDEX_FILE; exit 1 }
}
$tree = (& $g write-tree).Trim()
$sha = (& $g commit-tree $tree -p $parent -F "$env:TEMP\w38fin-msg2.txt").Trim()
Write-Host "newcommit=$sha"

# audit legs
$del = & $g diff --name-only --diff-filter=D $parent $sha
if($del){ Write-Host "DELETION DETECTED: $del -- ABORT (r525)"; Remove-Item Env:GIT_INDEX_FILE; exit 1 }
Write-Host "deletion-set empty PASS"
$w38res = (& $g ls-tree $sha results/perpetual_faces/n1_w38_results.json --name-only | Measure-Object).Count
$n38 = (& $g ls-tree $sha results/p2cal_ext/n1_w38/ --name-only | Measure-Object -Line).Lines
Write-Host "audit: w38res=$w38res w38shards=$n38"
if(-not($w38res -eq 1 -and $n38 -eq 12)){ Write-Host "AUDIT FAIL -- ABORT"; Remove-Item Env:GIT_INDEX_FILE; exit 1 }

& $g push origin "${sha}:refs/heads/main" 2>&1 | Select-Object -Last 2
if($LASTEXITCODE -eq 0){
  & $g update-ref refs/heads/main $sha $parent 2>&1 | Out-Null
  Write-Host "local main aligned"
}
Write-Host "PUSHED_SHA=$sha"
Remove-Item Env:GIT_INDEX_FILE -ErrorAction SilentlyContinue
