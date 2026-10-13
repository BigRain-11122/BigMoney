# r963 bm-a S6 chain continuation (legs after update_futures; live-output mode)
$ErrorActionPreference = 'Continue'
Set-Location 'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
$env:PYTHONIOENCODING = 'utf-8'
$legsA = @(
  @{n='update_repo';            c={python scripts\update_repo.py}},
  @{n='update_options';         c={python scripts\update_options.py}},
  @{n='update_moneyflow';       c={python scripts\update_moneyflow.py}},
  @{n='update_sina_mf';         c={python scripts\update_sina_mf.py}},
  @{n='update_astock_daily';    c={python scripts\update_astock_daily.py}},
  @{n='update_etf_daily';       c={python scripts\update_etf_daily.py}},
  @{n='regime_thermo_build';    c={python scripts\regime_thermo_build.py}},
  @{n='regime_gate_dualarm';    c={python scripts\regime_gate_dualarm.py run}},
  @{n='rev_osc_signal_export';  c={python scripts\rev_osc_signal_export.py run}},
  @{n='update_minute_feed';     c={python scripts\update_minute_feed.py}},
  @{n='update_ths_panel';       c={python scripts\update_ths_panel.py}},
  @{n='ah_panel_puller';        c={python scripts\ah_panel_puller.py}},
  @{n='update_fund_premium';    c={python scripts\update_fund_premium.py snapshot}},
  @{n='update_fundamental';    c={python scripts\update_fundamental.py}},
  @{n='b_layer_filter';          c={python -m firm.risk.b_layer_filter}},
  @{n='update_fund_statements'; c={python scripts\update_fund_statements.py}}
)
$paper_legs = @(
  @{n='live_paper';              c={python -m live.paper}},
  @{n='t35_open_fill_verify';    c={python scripts\t35_open_fill_verify.py}},
  @{n='t24_prospect_paper';      c={python scripts\t24_prospect_paper.py run}},
  @{n='t24_prospect_promotion';  c={python scripts\t24_prospect_promotion.py run}},
  @{n='aggressive_lab_paper';   c={python scripts\aggressive_lab.py paper}},
  @{n='alloc_paper';             c={python scripts\alloc_paper.py run}},
  @{n='grid_paper';              c={python scripts\grid_paper.py run}},
  @{n='system_v1_paper';         c={python scripts\system_v1_paper.py run}},
  @{n='t35_paper_export';        c={python scripts\t35_paper_export.py run}}
)
$face_legs = @(
  @{n='daily_scorecard';         c={python scripts\daily_scorecard.py}},
  @{n='daily_report';            c={python scripts\daily_report.py run}},
  @{n='ceo_live_usage';          c={python scripts\ceo_live_usage.py}},
  @{n='build_status';            c={python -m monitor.build_status}},
  @{n='token_meter';             c={python scripts\token_meter.py}}
)
function Run-Chain($list) {
  foreach ($leg in $list) {
    $t0 = Get-Date
    $out = & ($leg.c) 2>&1
    $rc = $LASTEXITCODE
    if ($null -eq $rc) { $rc = 0 }
    $last = ($out | Select-Object -Last 1)
    if ($last -is [System.Array]) { $last = $last[-1] }
    $dur = [int]((Get-Date) - $t0).TotalSeconds
    Write-Output ("LEG {0} rc={1} {2}s | {3}" -f $leg.n, $rc, $dur, ($last -join ' '))
  }
}
Write-Output "=== S6 resume A2 $(Get-Date -Format HH:mm:ss)"
Run-Chain $legsA
Write-Output "=== S6 phase B (paper, REGIME_GUARD=enforce) $(Get-Date -Format HH:mm:ss)"
$env:BIGMONEY_REGIME_GUARD = 'enforce'
Run-Chain $paper_legs
Write-Output "=== S6 phase C (faces) $(Get-Date -Format HH:mm:ss)"
Run-Chain $face_legs
Write-Output "=== S6 resume DONE $(Get-Date -Format HH:mm:ss)"
