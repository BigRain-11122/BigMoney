"""r1081 bm-c S6 chain driver (canon clone of r1075; r838 canon lineage): standing-leg canon clone -- identical leg list, leg count derived at runtime honest count. Full log to results/_r1081bmc_s6_log.txt. MUST run under the SYSTEM python (Python313): embedded ComfyUI python has no pandas/akshare (r516 lesson). Every leg subprocess passes CREATE_NO_WINDOW (U060 silence law). Per-leg stdout progress line (5-min zero-output kill guard, r1032 pit family). Sunday 04:0x run -- bars cutoff 10-16 current (weekend honest: update_daily/papers legs expected no-ops until Monday 10-19 15:30); bm-a/bm-b-owned lanes honest no-op on this machine per R31 lane guards. r1081 window = recovery-order absorb continuation (O-20261018-0137): dead windows r1076-r1080 estate landed by recovery pre-absorbs c3313769b/9e8084b54; THIS window product = W265 PREREG FREEZE (bands A 598_301..600_300 / B 600_301..600_500 per seat ADMIT; 5 same-window heals disclosed in freeze commit) + O-0137 bm-c receipt (task-panel audit + heartbeat heal); CEO recovery order 00:46 standing (machine accident = session-level kills, task panel verified alive); S0.5: ORD 018ba8b2 / DEC 1d4741e4 dual FALSE hold (pinned-probe, zero rows owed); unacked=2 (O-20261017-2207 UU-remote order = bm-a executed+receipted 22:16, bm-c ack-only; O-20261018-0137 = executing THIS window); smoke 49/49; orphan face=0; satengine ALIVE (W264 dedup 12/12)."""

import datetime
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "_r1081bmc_s6_log.txt")
PY = sys.executable
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

LEGS = [
    ("pool_dualrun_reconcile", [PY, "scripts/pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", [PY, "scripts/compute_audit.py"]),
    ("py_watermark", [PY, "scripts/py_watermark.py", "probe"]),
    ("update_daily", [PY, "scripts/update_daily.py"]),
    ("market_regime", [PY, "scripts/market_regime.py"]),
    ("strategy_scorecard", [PY, "scripts/strategy_scorecard.py"]),
    ("market_clock_call", [PY, "scripts/market_clock_call.py", "run"]),
    ("update_lhb", [PY, "scripts/update_lhb.py"]),
    ("update_zt_pool", [PY, "scripts/update_zt_pool.py"]),
    ("zt_pool_crosscheck", [PY, "scripts/zt_pool_crosscheck.py"]),
    ("update_heat", [PY, "scripts/update_heat.py"]),
    ("update_futures", [PY, "scripts/update_futures.py"]),
    ("update_repo", [PY, "scripts/update_repo.py"]),
    ("update_options", [PY, "scripts/update_options.py"]),
    ("update_moneyflow", [PY, "scripts/update_moneyflow.py"]),
    ("update_sina_mf", [PY, "scripts/update_sina_mf.py"]),
    ("update_astock_daily", [PY, "scripts/update_astock_daily.py"]),
    ("update_etf_daily", [PY, "scripts/update_etf_daily.py"]),
    ("regime_thermo_build", [PY, "scripts/regime_thermo_build.py"]),
    ("regime_gate_evidence", [PY, "scripts/regime_gate_evidence.py", "run"]),
    ("rev_osc_signal_export", [PY, "scripts/rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", [PY, "scripts/update_minute_feed.py"]),
    ("update_ths_panel", [PY, "scripts/update_ths_panel.py"]),
    ("ah_panel_puller", [PY, "scripts/ah_panel_puller.py"]),
    ("update_fund_premium", [PY, "scripts/update_fund_premium.py", "snapshot"]),
    ("update_fundamental", [PY, "scripts/update_fundamental.py"]),
    ("b_layer_filter", [PY, "-m", "firm.risk.b_layer_filter"]),
    ("update_fund_statements", [PY, "scripts/update_fund_statements.py"]),
    ("live_paper", [PY, "-m", "live.paper"],
     {"BIGMONEY_REGIME_GUARD": "enforce"}),
    ("t35_open_fill_verify", [PY, "scripts/t35_open_fill_verify.py"]),
    ("t24_prospect_paper", [PY, "scripts/t24_prospect_paper.py", "run"]),
    ("t24_prospect_promotion", [PY, "scripts/t24_prospect_promotion.py", "run"]),
    ("aggressive_lab", [PY, "scripts/aggressive_lab.py", "paper"]),
    ("alloc_paper", [PY, "scripts/alloc_paper.py", "run"]),
    ("grid_paper", [PY, "scripts/grid_paper.py", "run"]),
    ("cta_p1_paper", [PY, "scripts/cta_p1_paper.py", "run"]),
    ("system_v1_paper", [PY, "scripts/system_v1_paper.py", "run"]),
    ("t35_paper_export", [PY, "scripts/t35_paper_export.py", "run"]),
    ("daily_scorecard", [PY, "scripts/daily_scorecard.py"]),
    ("daily_report", [PY, "scripts/daily_report.py", "run"]),
    ("ceo_live_usage", [PY, "scripts/ceo_live_usage.py"]),
    ("build_status", [PY, "-m", "monitor.build_status"]),
    ("token_meter", [PY, "scripts/token_meter.py"]),
]


def main():
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    started = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    results = []
    with open(LOG, "w", encoding="utf-8") as log:
        log.write("r1081 bm-c S6 chain run %s legs=%d\n" % (started, len(LEGS)))
        log.flush()
        print("r1081 S6 chain start %s legs=%d" % (started, len(LEGS)))
        for entry in LEGS:
            name, cmd = entry[0], entry[1]
            leg_env = env
            if len(entry) > 2 and entry[2]:
                leg_env = dict(env)
                leg_env.update(entry[2])
            log.write("\n===== %s =====\n$ %s\n" % (name, " ".join(cmd)))
            log.flush()
            p = subprocess.run(cmd, cwd=ROOT, env=leg_env,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               creationflags=CNW)
            out = p.stdout.decode("utf-8", "replace")
            log.write(out)
            results.append((name, p.returncode))
            log.write("\n[rc=%d]\n" % p.returncode)
            log.flush()
            print("leg %s rc=%d" % (name, p.returncode))
        log.write("\nDONE %s\n" % datetime.datetime.now().astimezone().isoformat(
            timespec="seconds"))
    bad = [(n, rc) for n, rc in results if rc != 0]
    print("S6 legs=%d rc0=%d nonzero=%d" % (len(results), len(results) - len(bad),
                                            len(bad)))
    for n, rc in results:
        print("%-26s rc=%d" % (n, rc))
    return 2 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
