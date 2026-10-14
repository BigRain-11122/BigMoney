# r997 bm-a rebase conflict resolve: all 15 UU = same-day regenerated runtime
# faces, MINE (replayed r997, 19:43-19:46) newer than BASE (19:24-19:28) per
# triage results/_r997bma_conflict_triage.txt -> live-wins take --theirs (mine).
# Then continue rebase + push. Writers stay paused? No - they were re-enabled;
# rebase-continue path is short (2 addenda picks); residual face churn gets
# committed post-rebase if needed.
$git = "C:\Program Files\Git\cmd\git.exe"
Set-Location "C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
$files = @(
  "docs/daily_report/REPORT-2026-10-14.json",
  "docs/daily_report/REPORT-2026-10-14.md",
  "docs/live_usage/LIVE-2026-10-14.json",
  "docs/live_usage/LIVE-2026-10-14.md",
  "docs/live_usage/LIVE-latest.json",
  "docs/live_usage/LIVE-latest.md",
  "results/_attrition_guard_scan.json",
  "results/_r686bmb_d19_check.json",
  "results/compute_audit.json",
  "results/fundamental_b_layer_filter.json",
  "results/futures_update_status.json",
  "results/lhb_update_status.json",
  "results/regime_state.json",
  "results/token_usage.json",
  "results/update_status.json"
)
foreach ($f in $files) {
  & $git checkout --theirs -- $f
  if ($LASTEXITCODE -ne 0) { Write-Output "THEIRS-FAIL: $f"; exit 1 }
  & $git add -- $f
}
Write-Output "RESOLVED 15 faces (live-wins mine)"
# verify zero conflict markers in staged faces
$markers = & $git diff --cached --name-only -G "<<<<<<<|>>>>>>> "
if ($markers) { Write-Output "MARKER-ALERT: $markers"; exit 1 }
Write-Output "MARKER-FREE ok"
$cont = & $git rebase --continue 2>&1 | Select-Object -Last 3
Write-Output "CONTINUE: $cont"
