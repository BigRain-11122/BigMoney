$ErrorActionPreference = "Continue"
$log = "results\_r416bmb_s6_log.txt"
Remove-Item $log -ErrorAction SilentlyContinue
$legs = @(
    @{ n = "dualrun";    c = "python scripts\pool_dualrun_reconcile.py run" },
    @{ n = "comp_audit"; c = "python scripts\compute_audit.py" },
    @{ n = "py_wm";      c = "python scripts\py_watermark.py probe" },
    @{ n = "upd_daily";  c = "python scripts\update_daily.py" },
    @{ n = "regime";     c = "python scripts\market_regime.py" },
    @{ n = "scorecard";  c = "python scripts\strategy_scorecard.py" },
    @{ n = "mkt_clock";  c = "python scripts\market_clock_call.py run" },
    @{ n = "upd_lhb";    c = "python scripts\update_lhb.py" },
    @{ n = "upd_heat";   c = "python scripts\update_heat.py" },
    @{ n = "upd_fut";    c = "python scripts\update_futures.py" },
    @{ n = "upd_repo";   c = "python scripts\update_repo.py" },
    @{ n = "upd_opts";   c = "python scripts\update_options.py" },
    @{ n = "upd_mf";     c = "python scripts\update_moneyflow.py" },
    @{ n = "upd_sina_mf"; c = "python scripts\update_sina_mf.py" }
)
foreach ($l in $legs) {
    $start = Get-Date
    $out = Invoke-Expression $l.c 2>&1 | Out-String
    $rc = $LASTEXITCODE
    $tail = ($out -split "`n" | Where-Object { $_ -match '\S' } | Select-Object -Last 2) -join ' | '
    $line = "{0,-12} rc={1} [{2:mm\:ss}] {3}" -f $l.n, $rc, ((Get-Date) - $start), $tail
    Write-Output $line
    Add-Content $log "=== LEG $($l.n) rc=$rc ==="
    Add-Content $log $out
}
