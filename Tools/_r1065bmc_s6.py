"""r1065 bm-c S6 chain driver (canon clone of r1064): standing-leg canon clone (r838 canon lineage; r871/r936/r1037/r1045/r1052/r1055/r1056/r1057/r1058/r1059/r1060/r1061/r1063/r1064 canon clone -- identical leg list, leg count derived at runtime honest count). Full log to results/_r1065bmc_s6_log.txt. MUST run under the SYSTEM python (Python313): embedded ComfyUI python has no pandas/akshare (r516 lesson). Every leg subprocess passes CREATE_NO_WINDOW (U060 silence law). Saturday 10:3x run -- bars 10-16 landed and consumed by r1055 (papers fired there); next trading day Monday 10-19 15:30 => update_daily/papers legs expected honest weekend no-ops (cutoff 10-16 current); bm-a/bm-b-owned lanes honest no-op on this machine per R31 lane guards. r1065 window = 55th-gen absorb continuation: dead r1065 window estate (frozen-face extract 09:27 + needle probe + S0.5 ord analysis + derive script authored 10:09, prereg NOT emitted) absorbed THIS window; product = W260 PREREG FREEZE 0f33f9abc (derive ALL GATES PASS after 1 disclosed gate-heal [line-591 prior-label expect 3->0, W259-lineage mirror]; banned_direction_gate ADMIT rc0; bands A 587_301..589_300 NINTH A-hop / B 589_301..589_500 TENTH above-own-A); D-19 dual advance THIS window (ORD 29a77086->dbf28fba incl 09:0x V5-reburn dispatch + 09:45 meme + 09:5x CEO lane + 09:5x-10:0x CEO double + 10:1x report + 10:2x MV-V5-refine CEO order / DEC 881b6dcb->7f12de36 incl D-20261017-01/02/03 all interactive-window-executed governance); splice = next window FIRST ACTION."""

import datetime
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "_r1065bmc_s6_log.txt")
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
        log.write("r1065 bm-c S6 chain run %s legs=%d\n" % (started, len(LEGS)))
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
