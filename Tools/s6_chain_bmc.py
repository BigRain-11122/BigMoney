"""bm-c S6 chain runner (reusable).

Runs the 43 S6 data/panel maintenance legs in the order fixed by the round
prompt, records {leg, rc, elapsed} for each into
results/_r<round>bmc_s6_chain.json and prints a compact tail summary.

Usage: python Tools\\s6_chain_bmc.py <round_no>
Exit 0 always (legs are recorded; non-zero legs are reported, not fatal) --
the round report must surface any rc!=0 leg verbatim.

Why a shared runner: the per-round chain used to be an ad-hoc script rebuilt
every window (r1179..r1182 clones) which cost most of the round's wall time in
generation rather than measurement.
"""
import json
import subprocess
import sys
import time
from datetime import datetime

LEGS = [
    ("dualrun", ["python", "scripts/pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", ["python", "scripts/compute_audit.py"]),
    ("py_watermark", ["python", "scripts/py_watermark.py", "probe"]),
    ("update_daily", ["python", "scripts/update_daily.py"]),
    # The official exchange calendar, so "no new bar" stops being ambiguous: on
    # 2026-10-26 every panel leg printed no-op while the market had closed and the
    # feed had simply not published. The audit reads the sina trading-day list
    # (one request, then local for the rest of the year) and names the verdict.
    ("cal_audit", ["python", "scripts/exchange_calendar_audit.py", "run"]),
    ("market_regime", ["python", "scripts/market_regime.py"]),
    ("scorecard", ["python", "scripts/strategy_scorecard.py"]),
    ("market_clock", ["python", "scripts/market_clock_call.py", "run"]),
    ("update_lhb", ["python", "scripts/update_lhb.py"]),
    ("update_zt_pool", ["python", "scripts/update_zt_pool.py"]),
    ("update_heat", ["python", "scripts/update_heat.py"]),
    ("update_futures", ["python", "scripts/update_futures.py"]),
    ("update_repo", ["python", "scripts/update_repo.py"]),
    ("update_options", ["python", "scripts/update_options.py"]),
    ("update_moneyflow", ["python", "scripts/update_moneyflow.py"]),
    ("update_sina_mf", ["python", "scripts/update_sina_mf.py"]),
    # Both panel lanes are bm-b's (R31 lane law). bm-b's heartbeat has been silent
    # for days while these legs ran, so the chain passes the standing --takeover
    # consent r1276 established: the flag is only half the gate -- each script still
    # refuses unless the owner heartbeat is stale by >= TAKEOVER_STALE_MIN, so a
    # healthy bm-b keeps ownership and this machine just prints its honest no-op.
    ("update_astock_daily", ["python", "scripts/update_astock_daily.py",
                             "--takeover"]),
    ("update_etf_daily", ["python", "scripts/update_etf_daily.py", "--takeover"]),
    # The wide panel (1,724 files) is the price universe of every ETF study and of
    # the production book, but its refresh leg was never wired in: r1257 pulled it
    # once by hand and the panel then sat frozen at that Friday while every
    # downstream face kept computing on it. Runs after the five-member leg because
    # it is the wider face of the same session.
    ("update_etf_wide", ["python", "scripts/update_etf_wide.py", "run"]),
    # The production book's two live faces ride right behind the panel leg they read.
    # etf_book_forward appends one mark per new bar (idempotent; exit 3 freezes the
    # ledger instead of rewriting history) and etf_book_order re-emits the executable
    # ticket. Both were hand-run only until r1275, so the accrual depended on a session
    # remembering to call them -- r1267, r1269 and r1273 each named that as owed.
    ("etf_book_forward", ["python", "scripts/etf_book_forward.py"]),
    # The card is the headline face and the ticket the executable one; both are sold as
    # "the production book". r1290 found the card stranded a full refresh behind (priced
    # 2026-10-23/stale_feed while this ticket was already 2026-10-26/current) because only
    # the ticket was on this chain -- the same orphan-face class as r1257's panel. Card
    # first, ticket second: the ticket's card_agreement block reads the card back.
    # r1310: the question a funder asks before the capacity one -- after the four liquid
    # exposures an account could just hold (gold / Nasdaq QDII / CSI300 / bond), does the
    # book still have an intercept? Regresses the published book's daily returns on those
    # four, with an IS/OOS walk-forward column, and prints the span arms' own risk beside it
    # so a raw-CAGR contest cannot credit the benchmark for taking more risk. Rides the
    # chain for the same reason the capacity face does: a hand-run audit is a face that
    # silently ages (r1257/r1290/r1291/r1293/r1295 class). ~90s, no network.
    ("etf_book_spanning", ["python", "scripts/etf_book_spanning.py"]),
    ("etf_book_production", ["python", "scripts/etf_book_production.py"]),
    ("etf_book_order", ["python", "scripts/etf_book_order.py", "run"]),
    # The width face prices the disagreement BETWEEN those two faces ("what does the
    # ticket's 5 names cost against the card's 12"), and it was hand-run only: r1291 found
    # it sitting on 2026-10-23 while both faces above had moved to 2026-10-26 -- third
    # instance of the orphan-face class after r1257 (wide panel) and r1290 (the card).
    # ~70s on the same panel the two legs above already warmed.
    ("etf_book_width_audit", ["python", "scripts/etf_book_width_audit.py", "run"]),
    # The capacity face answers the money question the NAV ladder cannot: at a given
    # participation cap, how much capital can this book hold and what does it earn per
    # year THERE. Hand-run until r1295 -- the same orphan-face class as r1257 (wide
    # panel), r1290 (card) and r1291 (width face) -- so it rides the chain behind the
    # panel those legs already warmed (~110s, no network, no judge).
    ("etf_book_capacity_rule", ["python", "scripts/etf_book_capacity_rule.py", "run"]),
    # r1293: the register of every live book face. The legs above each refresh ONE
    # face; nothing listed them together, so a face could be added, go stale, or sit
    # outside the chain with no single place to notice (r1290 and r1291 were both that
    # class). Every row is derived from its own artefact, so it also catches a pointer
    # that still names a file which no longer exists. <1s, no network, no judge.
    ("etf_book_registry", ["python", "scripts/etf_book_registry.py", "run"]),
    # Fifth instance of the same class, one layer up: every face above is machine-shaped,
    # so the one thing a human can actually read about the only money-making structure we
    # have did not exist. docs/live_book/<date>.md is a pure mirror (order, money split,
    # forward nav, backtest band, next rebalance) with zero new judgement; single writer
    # = bm-a, other hosts print an honest no-op. <1s, no network.
    ("etf_book_ceo_page", ["python", "scripts/etf_book_ceo_page.py", "run"]),
    # Fourth instance of the orphan-face class, and the worst-placed one: the staggered
    # 5+5 book is the config this firm calls its production book, but its accrual ran only
    # off a scheduled task that no longer exists on this host (schtasks: not found), so the
    # ledger sat at 2026-10-23 while the panel had already printed 2026-10-26 -- a stale
    # track record on the face with the best measured numbers (Sharpe 1.32). The ledger is
    # idempotent per signal date (re-running a date replaces that row), so riding the chain
    # cannot double-count a bar; the scheduled task, if it ever returns, is harmless too.
    ("etf_paper_signal", ["python", "scripts/etf_paper_signal.py"]),
    ("regime_thermo", ["python", "scripts/regime_thermo_build.py"]),
    ("regime_dualarm", ["python", "scripts/regime_gate_dualarm.py", "run"]),
    ("rev_osc_export", ["python", "scripts/rev_osc_signal_export.py", "run"]),
    ("minute_feed", ["python", "scripts/update_minute_feed.py"]),
    ("ths_panel", ["python", "scripts/update_ths_panel.py"]),
    ("ah_panel", ["python", "scripts/ah_panel_puller.py"]),
    ("fund_premium", ["python", "scripts/update_fund_premium.py", "snapshot"]),
    ("fundamental", ["python", "scripts/update_fundamental.py"]),
    ("b_layer", ["python", "-m", "firm.risk.b_layer_filter"]),
    ("fund_statements", ["python", "scripts/update_fund_statements.py"]),
    ("t24_paper", ["python", "scripts/t24_prospect_paper.py", "run"]),
    ("t24_promote", ["python", "scripts/t24_prospect_promotion.py", "run"]),
    ("aggr_paper", ["python", "scripts/aggressive_lab.py", "paper"]),
    ("alloc_paper", ["python", "scripts/alloc_paper.py", "run"]),
    ("grid_paper", ["python", "scripts/grid_paper.py", "run"]),
    ("system_v1", ["python", "scripts/system_v1_paper.py", "run"]),
    # r1129: the marks lane feeds the T-35 fill verifier, and a session that was
    # never captured looks identical to one that is merely late. Classify every
    # trading day (captured / permanent hole / still pending) so the verifier's
    # rc=1 can be read as "unrecoverable" instead of "retry tomorrow".
    ("marks_coverage", ["python", "scripts/marks_coverage.py"]),
    ("t35_export", ["python", "scripts/t35_paper_export.py", "run"]),
    ("scorecard_daily", ["python", "scripts/daily_scorecard.py"]),
    ("daily_report", ["python", "scripts/daily_report.py", "run"]),
    ("ceo_live_usage", ["python", "scripts/ceo_live_usage.py"]),
    ("build_status", ["python", "-m", "monitor.build_status"]),
    ("token_meter", ["python", "scripts/token_meter.py"]),
    # O-20261026-0810-bm-a 4 handed this side the fix: the heartbeat carried 25 GPU
    # keys from a dozen per-round closeouts, disagreeing by up to 13 GB, with
    # gpu_util_pct pinned to a literal 0 -- a fleet audit was reading a random
    # round's snapshot. gpu_face re-probes once and rewrites every alias from that
    # one reading, so the face is consistent without a session remembering to do it.
    ("gpu_face", ["python", "Tools/gpu_face.py", "apply"]),
    # r1133: the group repo's tip landed with a tree of 2 files (3,492 deleted)
    # because its closeout wrote the commit from a partial index. A commit-tree
    # bypasses every hook, so the only defence is a tree-count comparison; it
    # runs on this repo and on the group tree when the machine carries one.
    ("tree_shrink", ["python", "Tools/tree_shrink_guard.py", "check",
                     "--repo", ".", "--commits", "20"]),
    ("tree_shrink_group", ["python", "Tools/tree_shrink_guard.py", "check_group"]),
    # r1134: r1133 could only DETECT the wipe, after the fact. A commit-tree
    # cannot be hooked, but the push can: both repos now carry a pre-push
    # tree-shrink gate (group face: the gap was that it had no pre-push at all).
    # This leg proves the gates are installed and identical to the committed
    # source, so a machine that "has the file" but never installed it shows red.
    ("tree_shrink_gates", ["python", "Tools/tree_shrink_guard.py", "check_gates"]),
]


def main():
    args = [a for a in sys.argv[1:]]
    only = None
    for a in list(args):
        if a.startswith("--only"):
            only = a.split("=", 1)[1] if "=" in a else None
            args.remove(a)
            if only is None:
                only = args.pop(0) if args else ""
    round_no = args[0] if args else "0"
    legs = LEGS
    if only is not None:
        want = [w.strip() for w in only.split(",") if w.strip()]
        legs = [(n, c) for n, c in LEGS if n in want]
        missing = sorted(set(want) - {n for n, _ in legs})
        if missing:
            print(f"unknown leg(s): {missing}; known={[n for n, _ in LEGS]}")
            sys.exit(2)
    out = []
    for name, cmd in legs:
        t0 = time.time()
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=900)
            rc = r.returncode
            tail = (r.stdout or "").strip().splitlines()[-1:] or [""]
        except subprocess.TimeoutExpired:
            rc = 124
            tail = ["TIMEOUT"]
        el = round(time.time() - t0, 1)
        out.append({"leg": name, "rc": rc, "elapsed_sec": el,
                    "tail": tail[0][:220]})
        print(f"{rc:3d} {name:18s} {el:7.1f}s {tail[0][:120]}", flush=True)

    path = f"results/_r{round_no}bmc_s6_chain.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    bad = [o for o in out if o["rc"] != 0]
    print(f"chain: {len(out)-len(bad)}/{len(out)} rc0 -> {path} "
          f"({datetime.now().isoformat(timespec='seconds')})")
    if bad:
        print("NONZERO: " + ", ".join(f"{o['leg']}={o['rc']}" for o in bad))


if __name__ == "__main__":
    main()