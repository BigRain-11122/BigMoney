"""_r454bmb_s6_chain_cont.py -- bm-b r454 S6 chain continuation (legs 8..38).

First driver run crashed printing leg-8 snippet (GBK console codec vs U+FFFD,
r236 family). Legs 1-7 landed rc=0 (see _r454bmb_s6_chain.log). This resumes
from update_lhb onward with stdout reconfigured to UTF-8.
"""
import subprocess
import sys
import os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

LEGS = [
    ["python", "scripts/update_lhb.py"],
    ["python", "scripts/update_heat.py"],
    ["python", "scripts/update_futures.py"],
    ["python", "scripts/update_repo.py"],
    ["python", "scripts/update_options.py"],
    ["python", "scripts/update_moneyflow.py"],
    ["python", "scripts/update_sina_mf.py"],
    ["python", "scripts/update_astock_daily.py"],
    ["python", "scripts/update_etf_daily.py"],
    ["python", "scripts/rev_osc_signal_export.py", "run"],
    ["python", "scripts/update_minute_feed.py"],
    ["python", "scripts/update_intraday_marks.py"],
    ["python", "scripts/update_ths_panel.py"],
    ["python", "scripts/ah_panel_puller.py"],
    ["python", "scripts/update_fund_premium.py", "snapshot"],
    ["python", "scripts/update_fundamental.py"],
    [sys.executable, "-m", "firm.risk.b_layer_filter"],
    ["python", "-m", "live.paper"],
    ["python", "scripts/t35_open_fill_verify.py"],
    ["python", "scripts/t24_prospect_paper.py", "run"],
    ["python", "scripts/t24_prospect_promotion.py", "run"],
    ["python", "scripts/aggressive_lab.py", "paper"],
    ["python", "scripts/alloc_paper.py", "run"],
    ["python", "scripts/grid_paper.py", "run"],
    ["python", "scripts/system_v1_paper.py", "run"],
    ["python", "scripts/t35_paper_export.py", "run"],
    ["python", "scripts/daily_scorecard.py"],
    ["python", "scripts/daily_report.py", "run"],
    ["python", "scripts/ceo_live_usage.py"],
    ["python", "-m", "monitor.build_status"],
    ["python", "scripts/token_meter.py"],
]

TIMEOUT = 900
ENV_LEGS = {"python -m live.paper": {"BIGMONEY_REGIME_GUARD": "enforce"}}


def main():
    rcs = {}
    for leg in LEGS:
        name = " ".join(leg[:3])
        env = None
        for k, extra in ENV_LEGS.items():
            if name == k:
                env = dict(os.environ)
                env.update(extra)
        try:
            p = subprocess.run(leg, capture_output=True, text=True,
                                timeout=TIMEOUT, encoding="utf-8", errors="replace", env=env)
            rc, out = p.returncode, (p.stdout or "") + (p.stderr or "")
        except subprocess.TimeoutExpired:
            rc, out = 99, "TIMEOUT"
        tail = [ln.strip() for ln in out.strip().splitlines() if ln.strip()]
        snip = (tail[-1][:150] if tail else "")
        snip = snip.encode("utf-8", "replace").decode("utf-8", "replace")
        rcs[name] = rc
        print(f"{name} | rc={rc} | {snip}", flush=True)
    bad = {k: v for k, v in rcs.items() if v not in (0, 1)}
    print("---")
    print("NON-GREEN LEGS:", bad if bad else "NONE (rc0/rc1 only)")


if __name__ == "__main__":
    main()
