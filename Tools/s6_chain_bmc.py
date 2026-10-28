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
    # r1136: the futures TSMOM sleeve was measured on 10-27 (standalone Sharpe 0.27, but
    # 50/50 with the ETF book 1.059 vs 0.98 alone at a smaller drawdown) and there was no
    # daily face for it -- the "produced but never read" class this repo keeps recording
    # (r1108). It rides immediately behind the panel it reads so the target weights can
    # never be older than the futures bars. ~2s, no network, no judge, shadow only.
    ("futures_tsmom_signal", ["python", "scripts/futures_tsmom_signal.py", "run"]),
    # r1137: the sleeve face published ONE blend point (50/50). A single weight is a single
    # decision sequence (r1262), and a heavier sleeve weight also lowers total risk, so the
    # raw CAGR column alone reads as "worse" (r1291). This leg republishes the whole overlay
    # axis with an equal-risk reading beside it, straight off the panels the two legs above
    # already refreshed. ~10s, no network, no judge, selects nothing.
    ("futures_overlay_sweep", ["python", "scripts/futures_overlay_sweep.py"]),
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
    # r1314: the card and the forward ledger are two independent records of ONE frozen
    # decision, and nothing compared them. Every leg above refreshes a face; this one asks
    # whether the paper book actually owns the book the card sells (names, weights, scale,
    # cash, decision bar), re-derives the ledger's nav from those same weights (1e-10 today,
    # so a trade the book never published would show), and prices the drift the frozen
    # decision has accumulated plus what undoing it costs at the next decision. Rides the
    # chain for the r1257/r1290/r1291/r1293/r1295 reason: a hand-run comparison is a
    # comparison nobody makes. ~15s on the warmed panel, no network.
    ("etf_book_card_track", ["python", "scripts/etf_book_card_track.py", "run"]),
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
    # r1329: it runs LAST among the faces (see the tail of this list). Parked here it
    # read ceo_page and the staggered ledger from the PREVIOUS run, so the first chain
    # of every day published two rows a bar behind the rest with nothing red.
    # r1319: the faces above each answer "what does THIS vehicle earn". A capital
    # allocator does not hold a vehicle, it holds an account size -- and nobody had put
    # the book, the four-ETF basket and the futures sleeve on that axis. Pure reader of
    # the spanning / capacity / futures faces already refreshed above: it measures
    # nothing, so its only failure mode is a missing input, which it reports instead of
    # zeroing. <1s, no network, no judge.
    ("capital_placement", ["python", "scripts/capital_placement.py", "run"]),
    # r1320: capital_placement put the card's 9.62% next to the capacity ladder's 7.28%
    # and called the 2.34pp between them an unattributed "run diff". They are three
    # measured things: knobs (card -> executable ticket, +3.73pp), the universe the two
    # faces were priced on (-5.55pp) and impact (-0.52pp). Re-deriving the 12-cell grid
    # costs ~5 min (the panel build dominates), so the chain runs the ENGINE-FREE audit:
    # the face must stay internally consistent, and must go red the moment a source face
    # it reconciles is re-derived to a new headline. 0.1s, no network.
    ("etf_book_cagr_reconcile", ["python", "scripts/etf_book_cagr_reconcile.py", "--check"]),
    # r1323: the book is turnover-bound, so "does it trade on noise" is a money question.
    # Re-deriving the six buffer arms costs the panel build (~80s), so the chain runs the
    # engine-free gate: the control arm must still reproduce the published cell, turnover
    # must stay non-increasing in the buffer, the census arithmetic must hold, and the face
    # must go RED the moment the production card advances past the bar it was priced on.
    # 0.1s, no network.
    ("etf_book_hysteresis", ["python", "scripts/etf_book_hysteresis.py", "--check"]),
    # r1325: r1324's buffer arm carried its own refutation in a caveat -- "a single better
    # arm can be one decision sequence". The adoption face re-priced the same k=0.05 arm on
    # 5 books x 4 decision phases (60 engine runs, ~3 min), so the chain runs the ENGINE-FREE
    # gate: frozen criteria must be echoed unchanged, the cell grid must be complete, the
    # phase signature must still be a real calendar, and the published verdict must be the
    # one the rule produces from the summary. 0.1s, no network.
    ("etf_book_buffer_adoption", ["python", "scripts/etf_book_buffer_adoption.py", "--check"]),
    # r1327: the 8% sizing overlay is recomputed only at a decision and from a trailing
    # window, so it is late in two ways at once and the headline cannot tell them apart.
    # Re-deriving the four vol_window arms costs the panel build (~3 min), so the chain runs
    # the gate: frozen criteria echoed, control arm still reproducing the published cell,
    # the lag block still carrying measured slots, and the verdict still the one the rule
    # produces. 0.1s + one rebuild, no network.
    ("etf_book_voltarget_lag", ["python", "scripts/etf_book_voltarget_lag.py", "--check"]),
    # r1328: r1327's four-window face printed +1.60pp/yr for the 20-bar estimator -- on ONE
    # decision calendar, which is exactly the reading r1325 showed is not a level. Re-pricing
    # 4 windows x 4 phases costs 16 engine runs (~5 min), so the chain runs the ENGINE-FREE
    # gate: frozen criteria echoed, the cell grid complete (every window in every phase), the
    # phase calendars still distinct, the control still reproducing the published cell, and
    # the published verdict still the one the rule produces from the summary.
    # 0.1s, no network.
    ("etf_book_voltarget_phase", ["python", "scripts/etf_book_voltarget_phase.py", "--check"]),
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
    # r1329: the register summarises the faces, so it must be the LAST book leg. Until
    # this round it sat ~50 legs earlier, ahead of etf_book_ceo_page and etf_paper_signal,
    # and its rows for those two faces were therefore always one run old (as_of
    # 2026-10-27 against card/ticket/forward 2026-10-28, verdict still "ok" because a
    # stale row is not an error in its own schema). Every other face is written above, so
    # from here the register has nothing left to miss. <1s, no network, no judge.
    ("etf_book_registry", ["python", "scripts/etf_book_registry.py", "run"]),
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
    # ORDER MATTERS (r1318): the panel READS fleet/machine-health.json, and the
    # hourly oversight task independently writes that file with a thin row. When
    # these legs ran after build_status, the panel was built from the thinned face
    # and then the face was healed behind it -- so the payload a person reads
    # carried a stale verdict every round, deterministically, while `check` said
    # ok (the r1290 two-face class). Producer before consumer: refresh, judge,
    # then build the panel from the judged face.
    ("machine_health_write", ["python", "Tools/machine_health_face.py", "rebuild"]),
    ("machine_health_face", ["python", "Tools/machine_health_face.py", "check"]),
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
    # r1314: fleet/machine-health.json is written by three machines' oversight task and
    # read by the panel, and on 2026-10-28 one bad payload became a nesting generator
    # ({"value": [{"value": [...]}]}) that made build_status fail SOFT -- the panel showed
    # fewer machines instead of saying UNKNOWN. bm-b landed the reader contract
    # (Tools/machine_health_face.py) and asserted it in smoke, but a gate nobody runs on
    # a schedule is a receipt, not a gate: this leg runs that same module's fail-closed
    # check, so the face is judged every round (smoke only runs when a session runs it).
    # r1315: gating alone would go red every hour. The hourly oversight writer is a
    # SEPARATE code face that emits a partial row (no `cpu`, no `gpu.util`), so the
    # face is complete at the end of a round and thin by the next one -- the gate would
    # then report INCOMPLETE for a machine that is fine, and the "fix" would be to
    # loosen the gate again. So the chain REFRESHES first (derive every entry from that
    # machine's own heartbeat, heal thin foreign rows) and then judges. Write is local:
    # it never invents a reading, a machine with no heartbeat keeps its row and reports
    # the gap.
    # r1318: those two legs moved ABOVE build_status -- see the note there. Running
    # them here healed the face after the panel had already copied the thin verdict.
    # D-20261028-04 asked this firm to sweep every resident script for a `..\..`
    # climb or a pasted group-tree mirror. A sweep done once answers "was it clean
    # on 10-28"; the defect is reintroduced the next time somebody writes a script
    # in a hurry, so the census runs every round and goes red on a new offender
    # (r1266: a verdict only in a receipt is not a gate). Costs ~4s over 2,100 files.
    ("group_root_sweep", ["python", "scripts/group_root_sweep.py", "run"]),
    # D-20261028-11 added two shapes to that rule: PowerShell reading .Path off a
    # Get-Item result (an empty group root that still reports OK) and prereg freshness
    # gates hashing WORKTREE bytes on an autocrlf checkout. Both are measured every
    # round. The second is a census and not a verdict: a constant matching neither
    # digest means the artefact was amended after the freeze, which is not a dialect
    # bug -- the r1324 first cut printed a clean face because its fixture could not
    # tell the two states apart at all.
    # ~2s over 8.5k files, no network.
    ("group_root_dialect_census", ["python", "scripts/group_root_dialect_census.py"]),
    # r1319: the pool's survivorship face. Read-only over data/daily (~4s) and
    # deterministic, so the cost is a file walk, not a re-run. What it buys: the
    # standing "pure survivor pool" caveat gets a number every round, and a symbol
    # that stops printing (delisting, or a collector that silently gave up) is
    # named on the day it happens instead of being inherited from a memo.
    ("etf_pool_survival", ["python", "scripts/etf_pool_survival.py", "run"]),
    # r1321/r1322: reader text. r1320 caught a published caveat that read "13.5%% vol"
    # and fixed it with a gate on that one face's output; this census sweeps every
    # reader-facing face (~13k files, ~7s) and gates the two buckets a reader opens --
    # JSON live faces and markdown prose under docs/ -- while naming (not rewriting)
    # machine strings, frozen evidence and the append-only pool record. r1322 wired it:
    # the first cut printed a chain leg in its comments that did not exist, and its
    # markdown pass labelled every .md "doc-prose" then gated only live-face, so the
    # CEO page itself was never checked.
    ("reader_text_audit", ["python", "scripts/reader_text_audit.py", "run"]),
    # r1326: the card's headline (book beats its own static class mix by +6.36pp/yr) was
    # priced on ONE decision calendar, and r1325 had just shown on this same book why that
    # is not a decision -- an arm that improved everything on the production calendar
    # reversed on 70% of four phase-shifted ones. The face re-prices the premium across
    # four phases; the leg runs its gate (criteria echo + verdict recomputed + four
    # distinct decision signatures), which is a JSON read, not another engine run.
    ("premium_phases", ["python", "scripts/etf_book_premium_phases.py", "--check"]),
    # r1331: E196 answers the question E190 left open -- whether the month the
    # ladder-drop verdict rests on is knowable in advance. It is a ~1s JSON read of
    # the E186 month table (no panel, no network, no engine), and it belongs on the
    # chain rather than in a session's memory because a face nobody re-derives is the
    # r1290 class: the reading stays on disk describing a table that may have moved.
    # It pins the reading, not the upstream -- the WHERE face it reads is itself a
    # session artefact, and the leg says so instead of implying a fresh measurement.
    ("ladderdropcarrier", ["python", "scripts/e39_panel_census.py",
                            "tilt3ladderdropcarrier"]),
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