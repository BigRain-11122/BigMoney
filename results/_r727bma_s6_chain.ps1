# r727 bm-a S6 chain driver (38 legs, literal invocations per r657 law, bare-run per r460 law)
$ErrorActionPreference = 'Continue'
$log = 'results\_r727bma_s6_chain.txt'
"=== r727 S6 chain start $(Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz') ===" | Out-File $log -Encoding utf8
$fail = @()
python scripts\pool_dualrun_reconcile.py run *>> $log; "RC=$LASTEXITCODE pool_dualrun_reconcile run" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "pool_dualrun_reconcile run rc=$LASTEXITCODE" }
python scripts\compute_audit.py *>> $log; "RC=$LASTEXITCODE compute_audit" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "compute_audit rc=$LASTEXITCODE" }
python scripts\py_watermark.py probe *>> $log; "RC=$LASTEXITCODE py_watermark probe" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "py_watermark probe rc=$LASTEXITCODE" }
python scripts\update_daily.py *>> $log; "RC=$LASTEXITCODE update_daily" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "update_daily rc=$LASTEXITCODE" }
python scripts\market_regime.py *>> $log; "RC=$LASTEXITCODE market_regime" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "market_regime rc=$LASTEXITCODE" }
python scripts\strategy_scorecard.py *>> $log; "RC=$LASTEXITCODE strategy_scorecard" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "strategy_scorecard rc=$LASTEXITCODE" }
python scripts\market_clock_call.py run *>> $log; "RC=$LASTEXITCODE market_clock_call" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "market_clock_call rc=$LASTEXITCODE" }
python scripts\update_lhb.py *>> $log; "RC=$LASTEXITCODE update_lhb" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "update_lhb rc=$LASTEXITCODE" }
python scripts\update_heat.py *>> $log; "RC=$LASTEXITCODE update_heat" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "update_heat rc=$LASTEXITCODE" }
python scripts\update_futures.py *>> $log; "RC=$LASTEXITCODE update_futures" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "update_futures rc=$LASTEXITCODE" }
python scripts\update_repo.py *>> $log; "RC=$LASTEXITCODE update_repo" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "update_repo rc=$LASTEXITCODE" }
python scripts\update_options.py *>> $log; "RC=$LASTEXITCODE update_options" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "update_options rc=$LASTEXITCODE" }
python scripts\update_moneyflow.py *>> $log; "RC=$LASTEXITCODE update_moneyflow" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "update_moneyflow rc=$LASTEXITCODE" }
python scripts\update_sina_mf.py *>> $log; "RC=$LASTEXITCODE update_sina_mf" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "update_sina_mf rc=$LASTEXITCODE" }
python scripts\update_astock_daily.py *>> $log; "RC=$LASTEXITCODE update_astock_daily (bm-b lane, expect no-op)" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "update_astock_daily rc=$LASTEXITCODE" }
python scripts\update_etf_daily.py *>> $log; "RC=$LASTEXITCODE update_etf_daily (bm-b lane, expect no-op)" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "update_etf_daily rc=$LASTEXITCODE" }
python scripts\rev_osc_signal_export.py run *>> $log; "RC=$LASTEXITCODE rev_osc_signal_export (bm-b lane, expect no-op)" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "rev_osc_signal_export rc=$LASTEXITCODE" }
python scripts\update_minute_feed.py *>> $log; "RC=$LASTEXITCODE update_minute_feed (bm-b lane, expect no-op)" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "update_minute_feed rc=$LASTEXITCODE" }
python scripts\update_ths_panel.py *>> $log; "RC=$LASTEXITCODE update_ths_panel" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "update_ths_panel rc=$LASTEXITCODE" }
python scripts\ah_panel_puller.py *>> $log; "RC=$LASTEXITCODE ah_panel_puller" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "ah_panel_puller rc=$LASTEXITCODE" }
python scripts\update_fund_premium.py snapshot *>> $log; "RC=$LASTEXITCODE update_fund_premium snapshot (bm-c lane, expect no-op)" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "update_fund_premium rc=$LASTEXITCODE" }
python scripts\update_fundamental.py *>> $log; "RC=$LASTEXITCODE update_fundamental" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "update_fundamental rc=$LASTEXITCODE" }
python -m firm.risk.b_layer_filter *>> $log; "RC=$LASTEXITCODE b_layer_filter" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "b_layer_filter rc=$LASTEXITCODE" }
python scripts\update_fund_statements.py *>> $log; "RC=$LASTEXITCODE update_fund_statements" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "update_fund_statements rc=$LASTEXITCODE" }
# paper cluster legs skipped: no new bar this round (golden-week holiday 10-05, market reopens 10-08; last bar day 2026-10-02, panels unchanged)
python scripts\daily_scorecard.py *>> $log; "RC=$LASTEXITCODE daily_scorecard (host=bm-a)" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "daily_scorecard rc=$LASTEXITCODE" }
python scripts\daily_report.py run *>> $log; "RC=$LASTEXITCODE daily_report" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "daily_report rc=$LASTEXITCODE" }
python scripts\ceo_live_usage.py *>> $log; "RC=$LASTEXITCODE ceo_live_usage" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "ceo_live_usage rc=$LASTEXITCODE" }
python -m monitor.build_status *>> $log; "RC=$LASTEXITCODE build_status (host=bm-a)" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "build_status rc=$LASTEXITCODE" }
python scripts\token_meter.py *>> $log; "RC=$LASTEXITCODE token_meter" | Out-File $log -Append -Encoding utf8
if ($LASTEXITCODE -ne 0) { $fail += "token_meter rc=$LASTEXITCODE" }
"=== r727 S6 chain end $(Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz') ===" | Out-File $log -Append -Encoding utf8
"FAILS: $($fail.Count)" | Out-File $log -Append -Encoding utf8
$fail | Out-File $log -Append -Encoding utf8
Write-Host "S6 DONE fails=$($fail.Count)"
$fail

