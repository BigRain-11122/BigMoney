"""r821 bm-b S6 chain driver (replicates r818 38-leg structure verbatim).

Chain A: pool_dualrun -> fund_statements (28 legs, fixed order).
Chain B: paper/report lanes; the new-bar trigger quad
(live_paper / t35_open_fill_verify / t24_prospect_paper /
 t24_prospect_promotion) runs ONLY when update_daily landed a new bar
(BIGMONEY_REGIME_GUARD=enforce for live_paper per O-1136), else skipped
with an honest note (weekend rounds: r818/r820 precedent).

Per-leg 600s timeout jacket (r806 spirit); capture utf-8 replace (encoding
law); log -> results/_r821bmb_s6_log.txt; exit = number of non-zero legs.
"""
import datetime as dt
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "_r821bmb_s6_log.txt")
PANEL = os.path.join(ROOT, "data", "daily", "sh510300.csv")
TIMEOUT_S = 600

CHAIN_A = [
    ("pool_dualrun", ["python", "scripts\\pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", ["python", "scripts\\compute_audit.py"]),
    ("py_watermark", ["python", "scripts\\py_watermark.py", "probe"]),
    ("update_daily", ["python", "scripts\\update_daily.py"]),
    ("market_regime", ["python", "scripts\\market_regime.py"]),
    ("strategy_scorecard", ["python", "scripts\\strategy_scorecard.py"]),
    ("market_clock_call", ["python", "scripts\\market_clock_call.py", "run"]),
    ("update_lhb", ["python", "scripts\\update_lhb.py"]),
    ("update_zt_pool", ["python", "scripts\\update_zt_pool.py"]),
    ("zt_pool_crosscheck", ["python", "scripts\\zt_pool_crosscheck.py"]),
    ("update_heat", ["python", "scripts\\update_heat.py"]),
    ("update_futures", ["python", "scripts\\update_futures.py"]),
    ("update_repo", ["python", "scripts\\update_repo.py"]),
    ("update_options", ["python", "scripts\\update_options.py"]),
    ("update_moneyflow", ["python", "scripts\\update_moneyflow.py"]),
    ("update_sina_mf", ["python", "scripts\\update_sina_mf.py"]),
    ("update_astock_daily", ["python", "scripts\\update_astock_daily.py"]),
    ("update_etf_daily", ["python", "scripts\\update_etf_daily.py"]),
    ("regime_thermo_build", ["python", "scripts\\regime_thermo_build.py"]),
    ("regime_gate_dualarm", ["python", "scripts\\regime_gate_dualarm.py",
                             "run"]),
    ("rev_osc_export", ["python", "scripts\\rev_osc_signal_export.py",
                        "run"]),
    ("update_minute_feed", ["python", "scripts\\update_minute_feed.py"]),
    ("update_ths_panel", ["python", "scripts\\update_ths_panel.py"]),
    ("ah_panel_puller", ["python", "scripts\\ah_panel_puller.py"]),
    ("update_fund_premium", ["python", "scripts\\update_fund_premium.py",
                             "snapshot"]),
    ("update_fundamental", ["python", "scripts\\update_fundamental.py"]),
    ("b_layer_filter", ["python", "-m", "firm.risk.b_layer_filter"]),
    ("update_fund_statements",
     ["python", "scripts\\update_fund_statements.py"]),
]

CHAIN_B = [
    ("aggressive_lab", ["python", "scripts\\aggressive_lab.py", "paper"]),
    ("alloc_paper", ["python", "scripts\\alloc_paper.py", "run"]),
    ("grid_paper", ["python", "scripts\\grid_paper.py", "run"]),
    ("system_v1_paper", ["python", "scripts\\system_v1_paper.py", "run"]),
    ("t35_paper_export", ["python", "scripts\\t35_paper_export.py", "run"]),
    ("daily_scorecard", ["python", "scripts\\daily_scorecard.py"]),
    ("daily_report", ["python", "scripts\\daily_report.py", "run"]),
    ("ceo_live_usage", ["python", "scripts\\ceo_live_usage.py"]),
    ("build_status", ["python", "-m", "monitor.build_status"]),
    ("token_meter", ["python", "scripts\\token_meter.py"]),
]

QUAD = [
    ("live_paper", ["python", "-m", "live.paper"]),
    ("t35_open_fill_verify", ["python", "scripts\\t35_open_fill_verify.py"]),
    ("t24_prospect_paper", ["python", "scripts\\t24_prospect_paper.py",
                            "run"]),
    ("t24_prospect_promotion",
     ["python", "scripts\\t24_prospect_promotion.py", "run"]),
]


def panel_tail():
    try:
        with open(PANEL, "rb") as f:
            data = f.read().decode("utf-8", errors="replace")
        lines = [ln for ln in data.splitlines() if ln.strip()]
        return lines[-1].split(",")[0] if lines else None
    except Exception:
        return None


def run_leg(name, cmd, env_extra=None, log=None):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    try:
        r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True,
                           timeout=TIMEOUT_S)
        rc = r.returncode
        out = (r.stdout or b"").decode("utf-8", errors="replace")
        err = (r.stderr or b"").decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        rc, out, err = "TIMEOUT", "", ""
    except Exception as e:
        rc, out, err = "FAULT", "", "%s: %s" % (type(e).__name__, str(e)[:200])
    lines = [ln for ln in (out + "\n" + err).splitlines() if ln.strip()]
    last = lines[-1][:500] if lines else "(no output)"
    line = "LEG %s rc=%s last=%s" % (name, rc, last)
    # console print must be GBK-safe (pit-encoding console family);
    # the log file keeps the full utf-8 text.
    try:
        print(line.encode("ascii", "replace").decode("ascii"))
    except Exception:
        print("LEG %s rc=%s (console print sanitized)" % (name, rc))
    if log:
        log.write(line + "\n")
        log.flush()
    return rc


def main():
    tail_before = panel_tail()
    nbad = 0
    nlegs = 0
    with open(LOG, "w", encoding="utf-8") as log:
        log.write("r821 bm-b S6 chain %s (new-bar quad gated)\n"
                  % dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        for name, cmd in CHAIN_A:
            rc = run_leg(name, cmd, log=log)
            nlegs += 1
            if rc != 0:
                nbad += 1
        tail_after = panel_tail()
        new_bar = (tail_before is not None
                   and tail_after is not None
                   and tail_before != tail_after)
        log.write("new_bar detect: before=%s after=%s new_bar=%s\n"
                  % (tail_before, tail_after, new_bar))
        if new_bar:
            log.write("--- new-bar trigger quad: RUNNING "
                      "(REGIME_GUARD=enforce for live_paper) ---\n")
            for name, cmd in QUAD:
                extra = {"BIGMONEY_REGIME_GUARD": "enforce"} \
                    if name == "live_paper" else None
                rc = run_leg(name, cmd, env_extra=extra, log=log)
                nlegs += 1
                if rc != 0:
                    nbad += 1
        else:
            log.write("--- chain B: paper/report lanes (new-bar trigger "
                      "quad skipped: live_paper/t35_open_fill_verify/"
                      "t24_prospect_paper/t24_prospect_promotion) ---\n")
        for name, cmd in CHAIN_B:
            rc = run_leg(name, cmd, log=log)
            nlegs += 1
            if rc != 0:
                nbad += 1
        log.write("CHAIN_DONE legs=%d bad=%d new_bar=%s\n"
                  % (nlegs, nbad, new_bar))
    print("CHAIN_DONE legs=%d bad=%d new_bar=%s -> %s"
          % (nlegs, nbad, new_bar, LOG))
    return nbad


if __name__ == "__main__":
    sys_exit = __import__("sys").exit
    sys_exit(main())
