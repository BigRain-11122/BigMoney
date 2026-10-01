# r314 bm-c tree surgery part 1 -- validate W8 products + carry commit + derive-face restore
$ErrorActionPreference = 'Continue'
$repo = 'K:\Fluxgroup\FluxGroup\quant\bigmoney'
$sg   = 'K:\Fluxgroup\FluxGroup\quant\.codely-cli\scratch\silent-git.ps1'
function Run-Hidden([string]$exe, [string]$argline, [string]$cwd) {
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $exe; $psi.Arguments = $argline
  if ($cwd) { $psi.WorkingDirectory = $cwd }
  $psi.UseShellExecute = $false; $psi.CreateNoWindow = $true
  $psi.RedirectStandardOutput = $true; $psi.RedirectStandardError = $true
  $p = [System.Diagnostics.Process]::Start($psi)
  $oT = $p.StandardOutput.ReadToEndAsync(); $e = $p.StandardError.ReadToEnd()
  $o = $oT.Result; $p.WaitForExit()
  return @{ out = $o; err = $e; rc = $p.ExitCode }
}
Write-Output ('NOW: ' + (Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz'))
Write-Output '--- daemon activity check ---'
$ds = Get-Content (Join-Path $repo 'results\dispatcher_state.bm-c.json') -Raw | ConvertFrom-Json
Write-Output ('dispatcher keys: ' + (($ds.PSObject.Properties.Name | Select-Object -First 12) -join ','))
$alog = Join-Path $repo 'logs\autofill.log'
if (Test-Path $alog) { Get-Content $alog -Tail 4 | ForEach-Object { Write-Output ('af: ' + $_) } }
Write-Output '--- W8 product validation (json parse + size) ---'
$tmpy = 'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r314bmc_w8_validate.py'
$pycode = @'
import json, os
base = 'K:/Fluxgroup/FluxGroup/quant/bigmoney/results/p2cal_ext/n1_w8'
for n in (8, 9, 10, 11):
    p = os.path.join(base, f'shard-{n}-of-12.json')
    try:
        d = json.load(open(p, encoding='utf-8'))
        keys = list(d.keys())[:8]
        cells = d.get('cells')
        cn = (len(cells) if hasattr(cells, '__len__') else 'n/a')
        print(f'W8 shard-{n}: OK size={os.path.getsize(p)} toplevel={keys} cells_count_field={cn}')
    except Exception as ex:
        print(f'W8 shard-{n}: FAIL {ex}')
'@
Set-Content -Path $tmpy -Value $pycode -Encoding UTF8
$r = Run-Hidden 'python' $tmpy $repo
Write-Output $r.out
if ($r.err) { Write-Output ('PY_ERR: ' + $r.err) }
Write-Output '--- origin n1_w8 product count (ls-tree) ---'
& $sg -GitArgs 'ls-tree --name-only origin/main results/p2cal_ext/n1_w8/' -Cwd $repo
Write-Output '--- carry: git add (explicit set) ---'
$carry = @(
  'CODELY.md',
  'research/PERPETUAL_N1_W7_PREREG.md',
  'results/p2cal_ext/n1_w8/shard-8-of-12.json',
  'results/p2cal_ext/n1_w8/shard-9-of-12.json',
  'results/p2cal_ext/n1_w8/shard-10-of-12.json',
  'results/p2cal_ext/n1_w8/shard-11-of-12.json',
  'results/pool_core_samples.jsonl',
  'results/pool_dualrun.bm-c.jsonl',
  'results/x2_watch_log.jsonl',
  'results/autofill_state.bm-c.json',
  'results/dispatcher_state.bm-c.json',
  'results/fundamental_status.bm-c.json',
  'results/futures_update_status.bm-c.json',
  'results/lhb_update_status.bm-c.json',
  'results/regime_state.bm-c.json',
  'results/compute_audit.bm-c.json',
  'results/token_usage.bm-c.json',
  'results/update_status.bm-c.json',
  'results/paper/COMPOSITE-CE-01_paper.json',
  'results/paper/COMPOSITE-CE-02_paper.json',
  'results/paper/DROUGHT-CE-01_paper.json',
  'results/paper/ENGULF-CE-01_paper.json',
  'results/paper/NEEDLE-DE-01_paper.json',
  'results/paper/VOLATILITY-CE-01_paper.json',
  'results/paper_export/export-2026-09-30.json',
  'results/paper_export/latest.json',
  'results/_r312bmc_s0_check.ps1',
  'results/_r312bmc_s0_triage.ps1',
  'results/_r312bmc_liveness.ps1',
  'results/_r312bmc_dec_check.py',
  'results/_r312bmc_dec_rows.py',
  'results/_r312bmc_dec_rows.txt',
  'results/_r312bmc_dec_board.txt',
  'results/_r312bmc_dec_scan.txt',
  'results/_r312bmc_wr_assembly_check.py',
  'results/_r312bmc_wr_pool_smoke.py',
  'results/_r312bmc_pool_union_resolver.py',
  'results/_r312bmc_shard10_flip.py'
)
& $sg -GitArgs ('add -- ' + ($carry -join ' ')) -Cwd $repo
Write-Output '--- staged set (ownership check, r494 law) ---'
& $sg -GitArgs 'diff --cached --stat' -Cwd $repo
Write-Output '--- carry commit ---'
& $sg -GitArgs 'commit -m "r314 pre-rebase carry: adopt dead-session work (r312 CODELY pitlaw + r313 W7 s7/s8 backfill) + W8 shard products 8-11 (r310 hygiene, fleet finalize unblock) + bm-c lane states + append jsonl"' -Cwd $repo
Write-Output '--- new carry sha ---'
& $sg -GitArgs 'log --oneline -2' -Cwd $repo
Write-Output '--- restore pure-derive shared faces to HEAD (r296 law 3) ---'
$restore = @(
  'docs/daily_report/REPORT-2026-10-01.json',
  'docs/daily_report/REPORT-2026-10-01.md',
  'docs/live_usage/LIVE-2026-10-01.json',
  'docs/live_usage/LIVE-2026-10-01.md',
  'docs/live_usage/LIVE-latest.json',
  'docs/live_usage/LIVE-latest.md',
  'results/_attrition_guard_scan.json',
  'results/compute_audit.json',
  'results/daily_scorecard.json',
  'results/dashboard_status.js',
  'results/dashboard_status.json',
  'results/fund_premium_status.json',
  'results/fundamental_b_layer_filter.json',
  'results/fundamental_status.json',
  'results/futures_update_status.json',
  'results/lhb_update_status.json',
  'results/prospect_paper/_summary.json',
  'results/prospect_promotion/_summary.json',
  'results/regime_state.json',
  'results/scorecard_v1.json',
  'results/strategy_scorecard.json',
  'results/t35_open_fill_verify.json',
  'results/token_usage.json',
  'results/update_status.json'
)
& $sg -GitArgs ('checkout -- ' + ($restore -join ' ')) -Cwd $repo
Write-Output '--- post-surgery status (expect clean tree) ---'
& $sg -GitArgs 'status --porcelain' -Cwd $repo
Write-Output '=== done part1 ==='
