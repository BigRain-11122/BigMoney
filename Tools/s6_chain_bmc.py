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
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime

LEGS = [
    ("dualrun", ["python", "scripts/pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", ["python", "scripts/compute_audit.py"]),
    # r1422: compute_audit has raised supply_floor (ready 0 < floor 3) for thirty
    # rounds and names fill_ladder as the remediation face -- but the ladder's own
    # report could not distinguish "22 of 23 catalog rows already burned" from "one
    # row is gated", because the id-idempotency skip drops spent rows silently. The
    # face below classifies every catalog row and joins the calendar verdict (r1421),
    # so the red carries both halves of its cause: nothing left to offer, and no
    # candidate passing its own calendar. Runs right after the audit that raises it.
    ("ladder_face", ["python", "Tools/fill_ladder.py", "explain"]),
    ("py_watermark", ["python", "scripts/py_watermark.py", "probe"]),
    ("update_daily", ["python", "scripts/update_daily.py"]),
    # The official exchange calendar, so "no new bar" stops being ambiguous: on
    # 2026-10-26 every panel leg printed no-op while the market had closed and the
    # feed had simply not published. The audit reads the sina trading-day list
    # (one request, then local for the rest of the year) and names the verdict.
    ("cal_audit", ["python", "scripts/exchange_calendar_audit.py", "run"]),
    # r1156: cal_audit gave ONE panel an independent reference and a verdict; every
    # other forward lane still judged "am I late?" from its own bytes, so a lane that
    # stops produces no error at all -- it just stops writing and its callers keep
    # reading yesterday's tail. Measured on 2026-10-30: popularity last wrote 10-20,
    # moneyflow 10-19 at a source block, repo 10-28, while every leg returned rc0.
    # The board re-judges every lane's declared tail against the same official
    # calendar (~0.2s, no network, no engine) and refuses to certify a tail whose
    # envelope does not name the machine that wrote it. It must run BEFORE
    # build_status (the dashboard renders it) -- r1290 class otherwise.
    ("data_lane_freshness", ["python", "scripts/data_lane_freshness.py", "run"]),
    # r1249 (bm-a): D-20261104-05 asks @BigMoney, by 2026-11-06 12:00, to name ONE host per lane
    # with evidence, or the 2026-11-08 task re-enable stays refused (a double-run on the money
    # side is worse than a stopped lane). The answer already exists but in two places that
    # disagree -- config/lane_hosts.json (the 2026-10-21 redline) and the `owner` defaults inside
    # data_lane_freshness.LANES -- and only the audit's private precedence knows which wins. This
    # leg writes the winner down once, with its authority. Reads the freshness face, so it goes
    # after it; its own gate compares ownership only (liveness stays the freshness face's).
    ("lane_ownership_declaration", ["python", "scripts/lane_ownership_declaration.py", "run"]),
    # r1205: every freshness face on this line reads the INSTANT -- "is the
    # newest heartbeat/round younger than N minutes" -- so a round that writes
    # its heartbeat right after a four-hour stall reads green and the stall
    # leaves no trace (2026-11-01: the lane sat dead from 08:0x to 12:5x with
    # the loop tasks Disabled, and no face said so). This leg measures the gaps
    # between consecutive rounds, subtracts the machine's declared quiet
    # windows, and judges the gap that is still open.
    # --heal (r1217 bm-a): the leg must not merely say the lane is switched off.
    # On 2026-11-01 the saturation engine (the compute lane's ignition face) was
    # missing from LANE_TASKS entirely, so a dead engine read as LANE_ENABLED; and a
    # Disabled task costs the whole lane while a re-enable costs nothing. The leg now
    # flips Disabled tasks back on and records the readback in the same face.
    ("lane_silence", ["python", "scripts/lane_silence_audit.py", "--heal"]),
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
    # r1140: the band leg above showed 86-92% of the sleeve's turnover is structural
    # (entries/exits/sign flips), so a no-trade band is a two-sided loss. This leg attacks
    # the flip itself: two damping mechanisms x two thetas x two lookbacks, each priced on
    # the full cost ladder at the book's published weight, with the exposure spread and a
    # fragility flag published beside the win. ~15s, no network, no judge, selects nothing.
    ("futures_overlay_fliprate", ["python", "scripts/futures_overlay_fliprate.py"]),
    # r1141: the flip-rate leg above found its win on ONE decision sequence, which is
    # exactly the shape r1325 recorded as unsafe (a single sequence can be a phase, not an
    # effect). This leg re-prices the same two arms across 13 paths -- era split, two
    # execution lags, and one leave-one-variety-out panel per variety -- against an
    # adoption rule frozen in the script, and the gate publishes ADOPT/REJECT per arm from
    # the measured cells. ~25s, no network, no judge; decides nothing by itself.
    ("futures_overlay_fliprate_paths", ["python",
                                        "scripts/futures_overlay_fliprate_paths.py"]),
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
    # r1404: right after the leg that WRITES the ledger, the one that asks whether the
    # file can be read at all. On 2026-11-07 the committed ledger was not valid JSON for
    # four hours (a line-level resolution spliced two documents together: one missing
    # comma, two repeated keys, a conflated run record) and every reader -- ticket, CEO
    # page, settle audit, re-derivation -- died at open while nothing went red. The guard
    # scans the published faces under results/ (scratch dumps excluded by the underscore
    # convention) for parse errors, repeated keys and non-UTF-8 encodings; ~45s, read-only,
    # exit 0 clean / 1 findings / 2 mechanism.
    ("json_face_guard", ["python", "Tools/json_face_guard.py"]),
    # r1366 (r1365's own owed item 2): when the forward leg freezes on a drift, the
    # next question is whether a PUBLISHED bar was rewritten or whether the newest
    # bar's panel was still filling -- and until now that question was answered by a
    # session, one or two rounds later, by hand. It rides directly behind the leg it
    # explains so a freeze is classified in the round it happens. Read-only by
    # construction: it never writes the ledger, never re-runs the engine, never touches
    # data/. ~2s. Exit 0 on all three verdicts (no_drift / provisional-only /
    # settled_bar_drift) because a classified freeze is an observation, not a fault;
    # `check` re-derives the stored verdict instead of trusting it.
    ("etf_book_settle_audit", ["python", "scripts/etf_book_forward_settle_audit.py", "run"]),
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
    # r1335 / E207: the book's six SIGNS are exactly this panel's full-sample IC signs, so
    # every number the legs below publish rests on a direction chosen after the fact. This leg
    # prices the honest arm (signs from already-realised windows only) so the caveat the card
    # now prints is re-derived with the panel instead of quoted from a hand run (r1290 class).
    # ~110s, offline. Ordered BEFORE production: the card reads its artifact.
    ("etf_sign_pit", ["python", "scripts/etf_sign_pit.py", "run"]),
    # r1336 / E208: the leg above says the signs were read off the sample; this one prices
    # HOW MUCH that reading is worth by running all 2^6 sign sets on the same panel -- the
    # production signs rank 6th of 64 against a median arm of -1.63%/yr. Same r1290 reason:
    # the number the card quotes has to be re-derived with the panel, not quoted from a hand
    # run. ~82s, offline, deterministic (one panel load, then one engine call per sign set).
    ("etf_sign_enum", ["python", "scripts/etf_sign_enum.py", "run"]),
    # r1337 / E220: the leg above ranks the 64 sign sets on ONE window; this one splits that
    # window and asks whether the ordering survives the split -- so "rank 6 of 64" cannot be
    # quoted without the transfer number beside it. ~100s, offline, deterministic (same panel
    # load, same engine; sub-period numbers read off the same trading path).
    ("etf_sign_stability", ["python", "scripts/etf_sign_stability.py", "run"]),
    # r1339 / E227: both legs above rank the 64 sign sets at ONE cell (R20 x 12 names), but
    # 20 and 12 were themselves picked on the sample -- the walk-forward on this line selects
    # among N3/5/8 x R10/20/40. This leg runs all 64 arms at three declared cells and asks
    # whether each factor's own direction survives the cell choice; it is what stops "rank 6
    # of 64" from being quoted as a property of the factors. ~180s, offline, deterministic.
    ("etf_sign_cells", ["python", "scripts/etf_sign_cells.py", "run"]),
    # r1341 / E229: the attribution above leaves two quotable directions; a reduced book
    # built from only them is the construction claim that has to be priced, across the full
    # 9-cell grid (two arms per cell). ~60s after the panel is warm, offline, deterministic.
    ("etf_lowvol_book", ["python", "scripts/etf_lowvol_book.py", "run"]),
    # r1345 / E236: the three sign legs above price a per-factor IC sign and all 64 vectors
    # on one window, but an operator picks ONE vector from history and runs it. This leg
    # prices that procedure (trailing-Sharpe re-selection, 3 reselect x 2 lookback x 2 cells)
    # against the equal-weight control, so "rank 6 of 64" cannot be quoted as if the ranking
    # were reachable live. ~150s, offline, deterministic (one panel load, 64 engine calls/cell).
    ("etf_sign_pit_combo", ["python", "scripts/etf_sign_pit_combo.py", "run"]),
    ("etf_book_production", ["python", "scripts/etf_book_production.py"]),
    # must run AFTER production (it reads the card + payload production writes) and before
    # the page that quotes the book: a face with no producer freezes on the card it was
    # written against, which is exactly how the r1220 mismatch verdict survived r1221's fix.
    ("etf_book_causal_headline", ["python", "scripts/etf_book_causal_headline.py", "run"]),
    # r1224 / E341: the rebuild face answers the question the card's reader actually has --
    # whether the 1.14pp one-bar price can be earned back by a causal rule. It reads the
    # card's two arms as controls, so it belongs after production; ~60s, offline, deterministic
    # (one panel load, 24 engine calls).
    ("etf_book_causal_rebuild", ["python", "scripts/etf_book_causal_rebuild.py", "run"]),
    # r1226 / E26: the rebuild closed the question of earning that price back, so the only
    # channel left is the one that exists between the decision close and the fill open -- the
    # overnight gap. Priced here, before the page that quotes the book reads it; ~150s,
    # offline, deterministic (one panel load, 24 engine calls).
    ("etf_book_overnight_gap", ["python", "scripts/etf_book_overnight_gap.py", "run"]),
    # r1227 / E27: information is exhausted (E25 rebuild, E26 gap), so the last candidate is
    # the fill mechanic -- the same delta through k consecutive opens. Deterministic, ~50s.
    ("etf_book_open_slicing", ["python", "scripts/etf_book_open_slicing.py", "run"]),
    # r1237 bm-a / E29: the gate is only on the way in. The ranking screens every name on a
    # 20-bar turnover gate and no face checked that same number on the sell bar, so the book
    # could be holding names it would not be allowed to buy. Reads the exit bar's own gate
    # reading for every position the declared arm holds, prices the wait to the first
    # qualifying bar (censored positions reported, never scored as zero). ~30s, offline.
    ("etf_book_exit_liquidity", ["python", "scripts/etf_book_exit_liquidity.py", "run"]),
    # r1238 bm-a: the sibling leg above prices the exits that waited for the gate to clear and
    # reports the ones that never did as outside_cap with no price attached (109 of 3,924).
    # This leg prices that tail -- first print after the exit, no gate, silent names kept as
    # open_at_end -- and refuses its verdict unless the imported census reproduces the totals
    # the sibling face published. Must run after exit_liquidity: it imports its rows. ~10s.
    ("etf_book_forced_hold", ["python", "scripts/etf_book_forced_hold.py", "run"]),
    # r1238 bm-a: every cost number on the shelf is a RATE per side (8bp + sqrt impact) and a
    # rate has no floor, while a real brokerage charge does (a 5 CNY minimum per trade on most
    # retail accounts). At this rule's trade sizes the floor is not negligible, so the published
    # return is unreachable below ~68k CNY -- and above ~217k the same 8bp model is 5.5bp/side
    # too expensive. Both halves are priced on the published weight path. ~2min, offline.
    ("etf_book_min_capital", ["python", "scripts/etf_book_min_capital.py", "run"]),
    # r1246 bm-a: the whole universe is chosen by one number (20-day median turnover
    # >= 20M) and until now that cut was assumed, never swept inside this book. This leg
    # prices the same panel/ranking/grid at six gates on the arm the card calls tradable,
    # with the 20M arm required to reproduce the published declared cell (control) or the
    # verdict is CANNOT_JUDGE. ~90s, offline, deterministic.
    ("etf_book_entry_gate", ["python", "scripts/etf_book_entry_gate.py", "run"]),
    # r1230 bm-a: depth and duration are different risks. Every other face prices the fall;
    # this one prices the wait (underwater episodes, per-entry recovery horizon with censored
    # entries kept, forward 1/2/3 calendar-year returns). ~80s, offline, deterministic -- it
    # runs the production cell through the production engine and must reproduce it to 5e-5.
    ("etf_book_underwater", ["python", "scripts/etf_book_underwater.py", "run"]),
    # r1366: the carry split answers "how much of the quoted return is repo interest",
    # and it must be priced on the same bar as the ticket it explains. Hand-run only
    # until now -- r1366 found it frozen on 2026-10-29 (base cell 11.33%) while that
    # day's ticket already read 11.19%, i.e. the same orphan-face class as r1257
    # (wide panel), r1290 (card), r1291 (width face) and r1295 (capacity): a face
    # refreshed by hand reads as current to every reader that only checks existence.
    # r1367: and it runs BEFORE the ticket, because the ticket now quotes the split --
    # behind it, every chain run would have the executable sheet reading yesterday's
    # decomposition of today's headline (the r1290 two-days-one-sheet class, moved into
    # the sheet itself). ~5s on the warmed panel, no network.
    ("etf_book_return_regime", ["python", "scripts/etf_book_return_regime.py", "run"]),
    # r1172: five tickers are not five bets. The ticket below quotes this face verbatim in
    # its limitations block, so the leg must run FIRST -- behind it, the executable sheet
    # would print the previous bar's concentration beside today's weights (the r1290 /
    # r1367 two-days-one-sheet class). ~1s, no network, single writer.
    ("etf_book_bets_face", ["python", "scripts/etf_book_bets_face.py", "run"]),
    # r1190 / E298: five tickers are not five bets -- and five names are not five sources of
    # return either. This face splits the book's own P&L by symbol (the replica must match the
    # engine's equity bit for bit or it refuses to publish) and re-prices the book with the top
    # names, then with their whole asset class, deleted from the universe. Cost is the panel
    # build (~30s) plus five book runs (~1s each), no network. Runs before the ticket so the
    # executable sheet can quote a same-bar concentration reading instead of a stale one.
    ("etf_book_concentration", ["python", "scripts/etf_book_concentration.py", "run"]),
    ("etf_book_order", ["python", "scripts/etf_book_order.py", "run"]),
    # r1333: the ticket above is a 5-name beta-overlay book while the card and the ledger
    # run 12 names at an 8% vol target -- two published books with one operator. This leg
    # issues the ticket FOR the card's own config (names, weights and scale read off the
    # card, nothing re-ranked), so the operator's sheet cannot drift into the other book.
    # ~1s, offline, idempotent.
    ("etf_book_order_card", ["python", "scripts/etf_book_order.py", "card"]),
    # r1398: the entry-friction face reads today's ticket and the session's spot board,
    # so it needs the ticket legs above it -- and it needs the DAILY gate rather than a
    # hand-run, because #97 (etf_premium_sentiment) will be built on this forward series.
    # The gate itself lives in the script (trading day + after 15:30 + once per session
    # + 30-min failure backoff), so a chain cycle that fires at 09:00, 12:00 and 22:00
    # writes exactly one snapshot per session and never files an intraday board as the
    # close. <1s when it no-ops; one spot-board pull when it fires.
    ("etf_premium", ["python", "scripts/etf_premium_face.py", "fetch"]),
    # r1175: the book publishes an annual return and a drawdown, and never what a bad
    # open costs. Two legs answer that, and the ORDER matters: the contamination face
    # runs first because the shock face quotes it (one reader, E270) -- behind it, the
    # shock face would disclose yesterday's clean worst day beside today's raw one.
    # ~35s + ~21s on the warmed panel, no network, single writer each.
    ("etf_book_flip_contamination", ["python", "scripts/etf_book_flip_contamination.py", "run"]),
    ("etf_book_shock_day", ["python", "scripts/etf_book_shock_day.py", "run"]),
    # r1366: the carry split answers "how much of the quoted return is repo interest",
    # and it must be priced on the same bar as the ticket it explains. Hand-run only
    # until now -- r1366 found it frozen on 2026-10-29 (base cell 11.33%) while that
    # day's ticket already read 11.19%, i.e. the same orphan-face class as r1257
    # (wide panel), r1290 (card), r1291 (width face) and r1295 (capacity): a face
    # refreshed by hand reads as current to every reader that only checks existence.
    # r1367: this leg now sits AHEAD of etf_book_order (above) so the executable sheet
    # never quotes yesterday's split next to today's headline.
    # r1314: the card and the forward ledger are two independent records of ONE frozen
    # decision, and nothing compared them. Every leg above refreshes a face; this one asks
    # whether the paper book actually owns the book the card sells (names, weights, scale,
    # cash, decision bar), re-derives the ledger's nav from those same weights (1e-10 today,
    # so a trade the book never published would show), and prices the drift the frozen
    # decision has accumulated plus what undoing it costs at the next decision. Rides the
    # chain for the r1257/r1290/r1291/r1293/r1295 reason: a hand-run comparison is a
    # comparison nobody makes. ~15s on the warmed panel, no network.
    ("etf_book_card_track", ["python", "scripts/etf_book_card_track.py", "run"]),
    # r1402: the supply line judges berths STANDALONE (against 510300) and the money line is
    # the book, so "zoo #96 failed" and "the book should not listen to it" were two different
    # sentences with only the first one measured. This leg keeps the join live for the same
    # reason every other book face rides the chain: a hand-run comparison is a comparison
    # nobody makes. ~150s (book panel already warm, plus the A-share panel for the volume
    # axis), no network, publishes a verdict rather than a judgement.
    ("etf_book_volgate", ["python", "scripts/etf_book_volgate.py"]),
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
    ("etf_book_cagr_reconcile", ["python", "scripts/etf_book_cagr_reconcile.py", "--check"],
     ["python", "scripts/etf_book_cagr_reconcile.py"]),
    # r1323: the book is turnover-bound, so "does it trade on noise" is a money question.
    # Re-deriving the six buffer arms costs the panel build (~80s), so the chain runs the
    # engine-free gate: the control arm must still reproduce the published cell, turnover
    # must stay non-increasing in the buffer, the census arithmetic must hold, and the face
    # must go RED the moment the production card advances past the bar it was priced on.
    # 0.1s, no network.
    ("etf_book_hysteresis", ["python", "scripts/etf_book_hysteresis.py", "--check"],
     ["python", "scripts/etf_book_hysteresis.py", "run"]),
    # r1325: r1324's buffer arm carried its own refutation in a caveat -- "a single better
    # arm can be one decision sequence". The adoption face re-priced the same k=0.05 arm on
    # 5 books x 4 decision phases (60 engine runs, ~3 min), so the chain runs the ENGINE-FREE
    # gate: frozen criteria must be echoed unchanged, the cell grid must be complete, the
    # phase signature must still be a real calendar, and the published verdict must be the
    # one the rule produces from the summary. 0.1s, no network.
    ("etf_book_buffer_adoption", ["python", "scripts/etf_book_buffer_adoption.py", "--check"],
     ["python", "scripts/etf_book_buffer_adoption.py", "run"]),
    # r1347: r1325 path-tested ONE buffer arm (k=0.05) and rejected it, while the published
    # hysteresis face still carries four more arms priced on a single decision sequence. This
    # face re-prices the whole arm grid on 5 books x 4 phases (100 engine runs) and adds the
    # per-cell breakeven cost. Heavy, so the chain runs the gate only: frozen rule echoed,
    # grid complete, phases still distinct, every verdict recomputed, control reproducing the
    # card -- and "behind the card" is the third state the runner pays a refresh for (r1346).
    ("etf_book_hysteresis_paths", ["python", "scripts/etf_book_hysteresis_paths.py", "--check"],
     ["python", "scripts/etf_book_hysteresis_paths.py", "run"]),
    # r1347: a breakeven quoted in bp/side is not a decision anyone can make -- the book pays
    # the impact model, not a flat cost. This face inverts the published sqrt cost law to the
    # capital at which each cell's saving covers its loss, and compares that crossing to the
    # size where the p90 trade already hits 1% of ADV. Two published faces, no engine: the
    # chain runs the gate, and "behind the card" is paid by a refresh (r1346).
    ("etf_book_buffer_price_of_size",
     ["python", "scripts/etf_book_buffer_price_of_size.py", "--check"],
     ["python", "scripts/etf_book_buffer_price_of_size.py", "run"]),
    # r1195 (bm-a): the sleeve-gate face answered "no gate earns adoption" on ONE decision
    # grid, and its own numbers named the vol gate as the closest arm. A rule that only
    # improves on one phase of the grid has not been measured (E188), so this face re-prices
    # that gate on 5 grids x 3 placebo schedules. The first version of it dropped the panel
    # prefix, which does NOT move an engine grid anchored at `start`, and published fifteen
    # identical paths; the gate below therefore refuses phases that are not distinct grids,
    # and refuses a face whose verdicts do not recompute from its own rows. Engine-free.
    # r1242 (bm-a): the paths face below is paired with results/etf_book_sleeve_gate.json and
    # the operator page prints "cannot verify" whenever the two sit on different bars -- but
    # only the paths leg was on this chain, so the sleeve section degraded to "cannot verify"
    # every day the panel advanced (measured 2026-11-02: gate 2026-10-30 vs paths 2026-11-02,
    # two smoke legs red). Producer before consumer, and the gate's own check now reads the
    # panel's last bar: behind it = "stale" -> rc2 -> this refresh re-prices the three arms.
    ("etf_book_sleeve_gate", ["python", "scripts/etf_book_sleeve_gate.py", "check"],
     ["python", "scripts/etf_book_sleeve_gate.py", "run"]),
    ("etf_book_sleeve_paths", ["python", "scripts/etf_book_sleeve_paths.py", "--check"],
     ["python", "scripts/etf_book_sleeve_paths.py", "run"]),
    # r1196 (bm-a): the card calls the 8% vol target "a drawdown tool, not an edge" while the
    # slot census says 87.3% of decisions were de-levered -- nobody had measured whether that
    # de-levering TIMES anything or is simply a smaller book. This face holds the same names
    # on the same grid at the book's own average exposure and permutes the engine's own scale
    # series (20 placebo paths) as the control. Engine-free: every arm is the engine's state
    # machine with one number replaced, and the identity arm must reproduce the engine's nav.
    ("etf_book_exposure_timing", ["python", "scripts/etf_book_exposure_timing.py", "--check"],
     ["python", "scripts/etf_book_exposure_timing.py", "run"]),
    # r1249 (bm-a): the ladder face existed only as a hand-run artifact -- it was not in this
    # table at all, so nothing checked it and nothing could rebuild it, and it sat on the
    # 2026-10-30 panel while the book priced 2026-11-03 (the r1248 pointer-3 finding). The
    # stamp gate now lives inside every book face's --check; a leg that is not in the table
    # can still never fire it.
    ("etf_book_exposure_ladder", ["python", "scripts/etf_book_exposure_ladder.py", "--check"],
     ["python", "scripts/etf_book_exposure_ladder.py", "run"]),
    # r1209 (bm-a) / E325: the card's extra bar was priced at 1.14pp/yr, which leaves the
    # operator's question unanswered -- is that lost information, or an unachievable fill?
    # This face prices the same signal at the only two fills a real order can get (the closing
    # auction of the decision bar, and the next open) and re-prices the close with an
    # extra-cost grid standing in for auction impact. Engine-free gate: the verdict must
    # recompute from the rows and the card/causal arms must reproduce the look-ahead audit to
    # 1e-6 pp, so a face quoting a different book cannot pass as evidence.
    ("etf_book_fill_venue", ["python", "scripts/etf_book_fill_venue.py", "--check"],
     ["python", "scripts/etf_book_fill_venue.py", "run"]),
    # r1203 (bm-a) / E24: the window axis of the vol target was swept once and sold as
    # "LOAD-BEARING" -- but every cell was priced on the SAME 20-bar decision grid, which is
    # the r1325 single-phase champion trap one level up. This face re-prices the window
    # ladder on four phases and asserts the shipped window against the production card's own
    # metrics; the gate recomputes the verdict from the published rows and refuses a face
    # whose criteria echo has drifted. Engine-free (one engine call per cell at run time).
    ("etf_book_vol_window_phase", ["python", "scripts/etf_book_vol_window_phase.py", "--check"],
     ["python", "scripts/etf_book_vol_window_phase.py", "run"]),
    # r1212 (bm-a) / E328: the face above ends on "the champion sits on the EDGE of the grid,
    # pushing further is the next face's job". This is that face: the same question carried
    # one grid lower (5/10/15/20/25 alongside the old 30 and the shipped 60), with the
    # adoption rule imported from the previous face rather than retyped. It also measures
    # which arms actually run the overlay, from the engine's own per-decision diag, because
    # windows below its minimum estimation history do not test a shorter estimate -- they
    # test the overlay switched off, and three of them would otherwise count as three grid
    # points. Engine-free at gate time (verdict and position recompute from the rows).
    ("etf_book_vol_window_edge", ["python", "scripts/etf_book_vol_window_edge.py", "--check"],
     ["python", "scripts/etf_book_vol_window_edge.py", "run"]),
    # r1348: every published number is one point estimate on ONE ordering of 1,651 days, and
    # the face that publishes the distribution (block bootstrap of the book's own return
    # path) can be re-judged from its stored resample rows without re-running the 2000
    # draw. The chain runs the gate only; the engine-free recompute re-derives every
    # percentile and share, so a hand-edited p50 is contradicted by the rows.
    ("etf_book_nav_envelope", ["python", "scripts/etf_book_nav_envelope.py", "--check"],
     ["python", "scripts/etf_book_nav_envelope.py", "run"]),
    # r1204 (bm-a) / E322: every published headline is a CAGR over all bars, which is
    # identical whether the growth is spread evenly or carried by ten days. This face prices
    # the tail on the book's own bars (drop-best 1/5/10 against a seeded random-drop placebo,
    # best month out) and, because two faces now publish the same book, measures the sibling
    # path bar-for-bar instead of assuming it is the same. Engine-free recompute of the
    # verdict from the stored bar returns (--check), so a hand-edited sentence is contradicted.
    ("etf_book_tail_dependence", ["python", "scripts/etf_book_tail_dependence.py", "--check"],
     ["python", "scripts/etf_book_tail_dependence.py", "run"]),
    # r1349: the block length was the one free parameter the envelope had to admit, so three
    # arms (week 5 / quarter 60 / year 250) were run against it. The comparison face quotes
    # numbers read off each arm, so the chain re-derives every quoted number from that arm's
    # own rows rather than trusting the summary.
    ("etf_book_block_length", ["python", "scripts/etf_book_nav_envelope.py", "blocks", "--check"],
     ["python", "scripts/etf_book_nav_envelope.py", "blocks"]),
    # r1350/E253: the card calls the 8% overlay "a drawdown tool" and every number behind
    # that sentence is a median or one path. Both books are now bootstrapped on the SAME
    # draw per resample, so the overlay's effect on the worst 1% is a measurement, not an
    # inference from two published bands. Gate re-derives every quoted delta from the
    # paired rows on disk (no 2,000-draw re-run).
    ("etf_book_voltarget_tail", ["python", "scripts/etf_book_nav_envelope.py", "voltail", "--check"],
     ["python", "scripts/etf_book_nav_envelope.py", "voltail"]),
    # r1349 / E255: every percentile in the block ladder carries its own sampling error, so
    # "arm A is calmer than arm B by 0.3pp" can be a description of the draw count rather
    # than of the market. This leg re-derives each interval, each permutation p and each
    # verdict from the arms' own rows (~1s; it reads NOISE rows, never a 2,000-draw re-run).
    ("etf_book_quantile_floor", ["python", "scripts/etf_book_quantile_floor.py", "--check"],
     ["python", "scripts/etf_book_quantile_floor.py", "run"]),
    # r1350 / E257: the production config is a cell in a 3x3 (names x cadence) grid chosen by
    # comparing single-calendar numbers, and r1325 showed that one calendar is not a level.
    # The atlas burns every decision origin inside one rebalance cycle for all 12 cells (280
    # engine runs, multicore, ~2 min), so the chain runs the ENGINE-FREE gate: the frozen cell
    # grid and criteria are echoed, every per-cell scalar and the grid's spread/band are
    # rebuilt from the 280 raw rows, and the verdict is the one the rule produces -- an edited
    # median or an edited verdict is red. 0.9s, no network, no panel build.
    ("etf_book_phase_atlas", ["python", "scripts/etf_book_phase_atlas.py", "--check"]),
    # r1351: the atlas measured ONE arm (the production toll). r1163 (bm-a) priced the three
    # stockable follow-ups as variants of the same grid -- buffer k=0.05, 5bp/side, 20bp/side --
    # and published the verdicts, but no leg anywhere read that face back: a published verdict
    # with nothing consuming it is the r1266 line ("a ruling that lives only in a receipt is
    # not a gate"). This leg re-derives the whole payload from the four arm faces and refuses a
    # face that disagrees with its own sources; "source moved" is stale (the chain pays the
    # refresh, which is one JSON re-read, not an engine), an edit that no source explains stays
    # red. 0.4s, no network, no engine.
    ("etf_book_phase_atlas_arms", ["python", "scripts/etf_book_phase_atlas_arms.py", "--check"],
     ["python", "scripts/etf_book_phase_atlas_arms.py", "run"]),
    # r1354: the arms face retires the buffer family on a DIRECTION ("inside the band at every
    # strength"). A direction is not a knapsack: this leg re-derives the floor face, which fits
    # the axis and answers in the knob's own units -- the k that would be needed for the ruler
    # to see it -- and refuses the face if the fit or the answer was edited. Engine-free, 0.1s.
    ("etf_book_buffer_floor",
     ["python", "scripts/etf_book_phase_atlas_arms.py", "--floor-check"],
     ["python", "scripts/etf_book_phase_atlas_arms.py", "--floor"]),
    # r1355: the floor answered with a k on ONE axis. This leg re-derives the width axis -- the
    # knob r1350 refused to quote -- and it tests the SIGNS of the rungs before it fits a slope,
    # because a line through a hill has a slope that means nothing. Engine-free, reads the
    # published baseline grid, 0.05s.
    ("etf_book_width_floor",
     ["python", "scripts/etf_book_phase_atlas_arms.py", "--width-check"],
     ["python", "scripts/etf_book_phase_atlas_arms.py", "--width"]),
    # r1355: the buffer floor extrapolates k=7.79 past its last arm. The pool harvested the row
    # stocked at k=0.30 (the midpoint of the widest fitted gap) during the same round, so this
    # leg re-derives the read-back: predicted vs observed, with the tolerance set to 3x the fit's
    # own largest in-sample residual. A fit that is never tested is a claim, not a fit. 0.05s.
    ("etf_book_buffer_readback",
     ["python", "scripts/etf_book_phase_atlas_arms.py", "--readback-check"],
     ["python", "scripts/etf_book_phase_atlas_arms.py", "--readback"]),
    # r1356: the ladder's rung was a difference of two medians, and the two faces an operator
    # actually holds (card 12 names, ticket 5 names) are two points on that same ladder. This leg
    # re-derives the paired comparison over one complete R20 cycle, the second engine's rung on
    # the same step, and the as-issued 2x2 -- then rebuilds the verdict from those numbers. A
    # face whose stored label no longer follows from its own deltas is red. Engine-free: it reads
    # three published faces (atlas rows, capacity rungs, the live ticket), 0.1s.
    ("etf_book_live_widths",
     ["python", "scripts/etf_book_phase_atlas_arms.py", "--live-widths-check"],
     ["python", "scripts/etf_book_phase_atlas_arms.py", "--live-widths"]),
    # r1352 / E261: the arms face publishes labels, and a label is only a measurement if it is
    # rare when the data has no effect. This leg re-simulates the labeler on those same 12 cells
    # with each delta replaced by zero-mean noise of that cell's own band: an effect-free panel
    # reads REJECT 96.5% of the time, so the published REJECTs (buffer k=0.05 and both cost arms)
    # carry almost nothing while the rare NOT-SEPARABLE branch is the informative one. Engine-free,
    # ~2s; the refresh is a re-simulation, not an engine run.
    ("etf_book_rule_null", ["python", "scripts/etf_book_rule_null.py", "--check"],
     ["python", "scripts/etf_book_rule_null.py", "run"]),
    # r1361: every reader of the toll-bracketing arms so far consumed them one arm at a time,
    # and the arms leg reads them for the BAND. The complementary question -- the atlas judges
    # its 12-cell ordering against each cell's own phase band, so at what toll does the ordering
    # stop clearing its own noise? -- had never been read as a ladder. This leg re-derives the
    # whole read-back from the published arm faces: rung membership comes off each face's audit
    # block (a face that moves two knobs is refused, not averaged in), the crossing is
    # interpolated, and the verdict must follow from its own numbers. Engine-free, reads six
    # JSONs, 0.1s.
    ("etf_book_atlas_toll_ladder",
     ["python", "scripts/etf_book_atlas_toll_ladder.py", "--check"],
     ["python", "scripts/etf_book_atlas_toll_ladder.py", "run"]),
    # r1188 bm-a: every published number for this book is one CAGR, and nothing said which part
    # of the day earns it -- the overnight leg the old book keeps while the order is pending, the
    # session leg the new book earns after the fill, the quiet bars, or the toll. This leg walks
    # the SAME Forward state machine with four log buckets (identity to Forward is a selftest leg,
    # so the attribution cannot drift from the engine) and the chain only recounts the published
    # arithmetic: buckets must sum to the total, per-bar x bars must reproduce each bucket, and the
    # two headline sentences (plain carry minus fill-bar drag) must equal that total. Reads one
    # JSON, ~0.1s; the run costs a ~20s panel build.
    ("etf_book_leg_attribution",
     ["python", "scripts/etf_book_leg_attribution.py", "--check"],
     ["python", "scripts/etf_book_leg_attribution.py", "run"]),
    # r1362: E275's one sign-stable direction (wider = better) was measured inside one grid on
    # one panel. This leg re-asks it on the E198 18-name cross and rebuilds the verdict from the
    # stored arm summaries, so a hand-edited verdict or a rung that never traded is red. It also
    # carries the seeded random-score control that separates a width sign from a volatility sign.
    # Gate-only in the chain (--check reads 20KB); the run costs ~4 min of panel build.
    #
    # r1168 bm-a: the leg is REGISTERED BUT NOT RUNNABLE -- `scripts/etf_book_width_cross.py`
    # has never existed in any commit (git log --all --diff-filter=D finds nothing), so listing
    # it makes the shared chain name a producer nobody wrote and turns every machine's
    # "chain runner is the shared leg list" leg red on a missing script (measured here
    # 2026-10-30 20:2x: missing_scripts=['etf_book_width_cross']). A leg whose script is absent
    # is not a leg; it is a reminder. Uncomment the block below in the same commit that lands
    # the script (bm-c r1362 owner), and the reminder disappears with it.
    # ("etf_book_width_cross",
    #  ["python", "scripts/etf_book_width_cross.py", "--check"],
    #  ["python", "scripts/etf_book_width_cross.py", "run"]),
    # r1327: the 8% sizing overlay is recomputed only at a decision and from a trailing
    # window, so it is late in two ways at once and the headline cannot tell them apart.
    # Re-deriving the four vol_window arms costs the panel build (~3 min), so the chain runs
    # the gate: frozen criteria echoed, control arm still reproducing the published cell,
    # the lag block still carrying measured slots, and the verdict still the one the rule
    # produces. 0.1s + one rebuild, no network.
    ("etf_book_voltarget_lag", ["python", "scripts/etf_book_voltarget_lag.py", "--check"],
     ["python", "scripts/etf_book_voltarget_lag.py", "run"]),
    # r1328: r1327's four-window face printed +1.60pp/yr for the 20-bar estimator -- on ONE
    # decision calendar, which is exactly the reading r1325 showed is not a level. Re-pricing
    # 4 windows x 4 phases costs 16 engine runs (~5 min), so the chain runs the ENGINE-FREE
    # gate: frozen criteria echoed, the cell grid complete (every window in every phase), the
    # phase calendars still distinct, the control still reproducing the published cell, and
    # the published verdict still the one the rule produces from the summary.
    # 0.1s, no network.
    ("etf_book_voltarget_phase", ["python", "scripts/etf_book_voltarget_phase.py", "--check"],
     ["python", "scripts/etf_book_voltarget_phase.py", "run"]),
    # Fifth instance of the same class, one layer up: every face above is machine-shaped,
    # so the one thing a human can actually read about the only money-making structure we
    # have did not exist. docs/live_book/<date>.md is a pure mirror (order, money split,
    # forward nav, backtest band, next rebalance) with zero new judgement; single writer
    # = bm-a, other hosts print an honest no-op. <1s, no network.
    # r1198: the 10 bp per side that every published number rests on is itself a measured
    # quantity, and until this leg it had no scheduled producer -- the page would have
    # quoted a stale tape (or the assumption) with nobody noticing. Runs BEFORE the page,
    # which formats it (r1318 ordering law).
    ("etf_book_cost_tape", ["python", "scripts/etf_book_cost_tape.py", "--check"],
     ["python", "scripts/etf_book_cost_tape.py", "run"]),
    # r1213: the expectation table's three rows are priced on two periods, two class
    # universes and two fill orderings, under one column. This leg prices each dial one at
    # a time on the book the operator holds (its own identity arms reproduce 12.78 / 9.60 /
    # 18.35), so the page can say which ruler made each number. Runs BEFORE the page, which
    # quotes it (r1318 ordering law). ~50s.
    ("etf_book_band_ruler", ["python", "scripts/etf_book_band_ruler.py", "check"],
     ["python", "scripts/etf_book_band_ruler.py", "run"]),
    # r1216: the band ruler said "three rows, three rulers" in a bullet under the table,
    # while row 1 kept printing the ticket's own 683-bar return under a 全窗 header. This
    # leg re-derives both windows of the operator's own book from the ruler's cells and
    # relabels that row; it runs BEFORE the page, which quotes it (r1318 ordering law). ~2s.
    ("etf_book_window_label", ["python", "scripts/etf_book_window_label.py", "check"],
     ["python", "scripts/etf_book_window_label.py", "run"]),
    # r1249: the page can only be priced on the last CLOSED panel bar, and the panel moves
    # one day behind the exchange while sina's daily endpoint catches up. So every evening
    # between the close and the panel taking the bar, the operator's page says the book is
    # worth what it was yesterday. This leg reads one snapshot quote per held name, proves
    # each quote's own previous close equals the panel's last bar close, and reports the
    # weighted move of the held leg -- no forecast, no ledger write, no ticket change.
    # bm-a is the writer; other hosts print an honest no-op.
    # r1251: it MUST sit ahead of the page that quotes it -- it was placed one slot after,
    # so the page kept printing yesterday's silence for a full round (r1318 ordering law).
    ("etf_book_live_quote", ["python", "scripts/etf_book_live_quote.py"]),
    ("etf_book_ceo_page", ["python", "scripts/etf_book_ceo_page.py", "run"]),
    # r1150: the four-tier ticket menu is the same book sold at four betas, and it
    # lived a full round with no scheduled producer -- the r1290 two-face class. bm-a
    # is the writer; other hosts print an honest no-op. ~2s warm / ~30s on a new bar.
    ("etf_book_beta_menu", ["python", "scripts/etf_book_beta_menu.py"]),
    ("etf_book_width_null_production", ["python", "scripts/etf_book_width_null_production.py"]),
    # Fourth instance of the orphan-face class, and the worst-placed one: the staggered
    # 5+5 book is the config this firm calls its production book, but its accrual ran only
    # off a scheduled task that no longer exists on this host (schtasks: not found), so the
    # ledger sat at 2026-10-23 while the panel had already printed 2026-10-26 -- a stale
    # track record on the face with the best measured numbers (Sharpe 1.32). The ledger is
    # idempotent per signal date (re-running a date replaces that row), so riding the chain
    # cannot double-count a bar; the scheduled task, if it ever returns, is harmless too.
    ("etf_paper_signal", ["python", "scripts/etf_paper_signal.py"]),
    # r1449: three rulers (denominator / window / universe) each priced on their own face,
    # and the cell they never shared -- graded universe x the common window -- is the one
    # that lands lowest (k 0.3931 vs the 0.4603 in force). This leg re-derives the desk
    # sentence from the receipt's own cells and the newest ticket (0.1s, no panel): a stale
    # receipt after a new ticket lands raises rc1 and the round re-runs the 73s table.
    ("etf_book_size_rulers", ["python", "scripts/etf_book_size_rulers_decision.py", "check"]),
    # r1450: the rulers table answers "how wide is the argument"; the desk has to answer
    # "may the weight in force stay" before the 2026-11-11 rebalance. This leg re-derives
    # the permission from the same receipt: circular (the ticket's own construction),
    # path (measured on decision bars) and static (a mix, not a path) readings are told
    # apart, and keeping the size is allowed only if a PATH reading reaches the money.
    # Live: every path reading is below the money, the only reading above it is the static
    # denominator mix -> size at k=0.393073 (CNY 392,616), a cut of CNY 67,180. `check`
    # form (0.1s, published JSON only) so a drifted receipt or a newer ticket turns red
    # instead of leaving a stale permission on disk (r1290 class).
    ("rebalance_permission",
     ["python", "scripts/etf_book_rebalance_permission.py", "check"]),
    # r1451: the permission says what the desk MAY hold; it says nothing about what the desk
    # will ORDER. The order path derives its own k from an expanding beta and reads no
    # permission, so this leg measures the gap between the two published surfaces and scans
    # the source tree for a consumer of the permission's numbers. Live: order 0.460253 vs
    # permission 0.393073 (CNY 67,180 over), zero readers -> the cut is refused on paper and
    # nothing trims it; the trim block prints the per-leg lots so obeying it is mechanical.
    # `check` form (0.1s, published JSON + source scan, no panel).
    ("cut_order_gap", ["python", "scripts/etf_book_cut_order_gap.py", "check"]),
    # r1453: cut_order_gap and cut_gate_pass answer two halves of the same 11-11 question --
    # what the desk must SELL, and whether obeying that sale moves the calendar gate. Neither
    # printed the other, so a desk had to hold two receipts at once. etf_book_decision_line
    # folds both plus the year gate into ONE row (size, trim in lots, the three prices of
    # obeying) and goes RED when the two receipts disagree on a shared number, so a hand-typed
    # figure cannot survive. `check` form re-derives from the same files (0.1s, no panel).
    ("cut_gate_pass", ["python", "scripts/etf_book_cut_gate_pass.py", "--check"]),
    ("decision_line", ["python", "scripts/etf_book_decision_line.py", "--check"]),
    # r1454: the decision row sized the order but asked nothing about the object being
    # judged. The year gate has always judged the book BEFORE the execution wrapper; the
    # desk runs the book AFTER it. etf_book_wrapper_year_gate prices all three arms on
    # identical bars (plain / book+beta-overlay+repo-cash / the ticket's own untargeted
    # construction) and hands them to the same frozen gate. Live: plain CONDITIONAL,
    # wrapped CONDITIONAL (no check moves), ticket construction ADMIT at top2 0.6752 --
    # and that pass comes from owning less (k 0.23-0.47), which the face prints as
    # compression_note instead of a clean bill of health. `--check` re-derives published
    # JSON only (1.7s warm, no panel).
    ("wrapper_year_gate", ["python", "scripts/etf_book_wrapper_year_gate.py", "--check"]),
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
    # r1170: the page prints the regime cap and the ticket prints the deployed book, and
    # nothing compared them. On the first RED day (cap 20%) three of six paper accounts
    # sat above it. Reads published faces only; changes no rule.
    # r1265 (bm-a): the freshness board is written near the TOP of this table, before the
    # lanes it judges update (update_zt_pool / update_heat / update_astock_daily /
    # fund_statements all run below it). Inside one chain cycle it therefore always names
    # the tail of the PREVIOUS cycle, and an update that lands outside the chain leaves it
    # a whole cycle behind: at 14:32 a `--takeover` heat snapshot wrote 2026-11-06 while
    # the 14:19 board still said 2026-11-05, so the smoke leg that compares the two faces
    # went red on a lane that was correct. Same producer-before-consumer rule as r1318:
    # the board is a CONSUMER of every lane face, so after the last lane producer
    # (fund_statements, above) and before the two human faces that quote it
    # (daily_report / ceo_live_usage) it is re-derived from the same lanes.
    # Idempotent derivation, ~0.2s, no network. The early leg stays: the ownership and
    # silence legs in between read its face.
    ("data_lane_freshness_close", ["python", "scripts/data_lane_freshness.py", "run"]),
    # r1171: ORDER MATTERS (r1318 class) -- the daily report (sec.1) and the CEO page
    # (sec.2) now QUOTE this verdict, so the producer has to run before both consumers
    # or two human faces print yesterday's sentence all round.
    ("regime_cap_vs_book", ["python", "scripts/regime_cap_vs_book.py", "run"]),
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
    # r1249 (bm-a): the panel prints the open-fill verdict and tier as one of its paper rows,
    # but the producer was not in this table at all -- it ran wherever a round happened to
    # call it, and on 2026-11-03 that was 22 SECONDS AFTER build_status (panel 23:03:09 read
    # tier=none / day 10-30 while the gate wrote daily_bar_open / 11-03 at 23:03:31). Same
    # producer-before-consumer rule as r1318 above; the smoke leg that compares the two faces
    # is the tripwire, and it went red on exactly this ordering.
    ("t35_open_fill_verify", ["python", "scripts/t35_open_fill_verify.py"]),
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
    ("premium_phases", ["python", "scripts/etf_book_premium_phases.py", "--check"],
     ["python", "scripts/etf_book_premium_phases.py", "run"]),
    # r1426: the check that refuses the desk's own book (Y4 top-2 year share) cannot
    # adjudicate 3 of its 4 arms, so the objection rested on a ruler nobody could trust.
    # The leg is the gate on that comparison: it re-derives which calibers are trusted and
    # what the composite word is FROM THE PUBLISHED ROWS (a JSON read, no repricing), and
    # fails if the face's trust list, primary caliber or composite word no longer follows
    # from its own cells -- the r1290 class, a reading left on disk describing older data.
    ("year_caliber", ["python", "scripts/etf_book_year_caliber.py", "check"],
     ["python", "scripts/etf_book_year_caliber.py", "run"]),
    # r1427: a refusal is only as good as the ruler behind it. The phase gate now re-reads
    # every book through the calibers r1426 proved self-adjudicable, and this face is the
    # operator sentence that says which refusals survive that re-read. It copies receipts
    # only (no repricing, milliseconds), so it is regenerated every round -- a reading left
    # on disk is the r1290 class: the pool stops being empty and the sentence still says
    # "no candidate passes its calendar".
    # r1435: the sentence "refused at years_for_half median 2" has been on the board for
    # thirty-nine rounds, always read as front-loading -- but the ruler sorts the year nets
    # descending and is order-free, so it never claimed a direction. This leg re-derives
    # every published sentence FROM ITS OWN YEAR TABLE before the face below consumes it
    # (pure JSON read, no repricing), so a stale receipt or a hand-typed "front-loaded"
    # turns red instead of feeding the operator sentence again.
    ("half_year_provenance",
     ["python", "scripts/etf_book_half_year_provenance.py", "check"]),
    # r1436: r1435 named the years that make up the half (2025 for all three refused
    # books), but nothing said whether that year is READABLE -- it is the newest full
    # year, a gold year, and the top-2 share moves with the decision phase. This leg
    # re-derives the verdict from its own receipt: 2025 net +43.0pp on the first phase
    # falls to 22.3pp on another (spread 20.7pp > 15 -> PHASE_FRAGILE), 3x toll still
    # leaves 39.3pp (cost is not the issue), and the commodity sleeve collected 18.56pp
    # of the 50.92pp its own equal-weight buy-and-hold would have paid (the book held
    # LESS gold beta than passive, not more). ~1s, reads only the published receipt.
    ("book_2025_repro", ["python", "scripts/etf_book_2025_repro.py", "check"]),
    # r1443: r1442 measured one flattering arm (flip drawdown_60, +87bp) on a single
    # decision phase and named a phase sweep as its own next step. This leg re-derives the
    # 5-book x 4-phase press from its receipt: the flip is up in 85% of 20 cells with a
    # median +1.25pp, but the control arm's own phase IQR is 2.54pp (3.35pp on the
    # production cell itself) -> PHASE_FRAGILE, i.e. not separable from the grid. Read-only
    # JSON plus a recompute of the frozen rule; the 44-cell repricing runs only with `run`
    # in its own round (~2 min).
    ("sign_flip_phase", ["python", "scripts/etf_sign_flip_phase_test.py", "--check"]),
    ("supply_calendar", ["python", "scripts/supply_calendar_face.py", "run"]),
    # r1440: forty rounds read the calendar and the order page as two separate
    # subjects. This leg puts them in one sentence from receipts only (no
    # repricing): today the ticket executes nobond_vt08_adopted at book_weight
    # 0.460 (CNY 459,796 in 5 names + GC001 cash) while the same desk's supply
    # calendar says CONDITIONAL (years_for_half median 2 vs line 3) -- and the
    # object the gate judged is the book BEFORE the beta 0.20 + cash wrapper.
    # `run` form on purpose: a leftover receipt goes stale when tomorrow's ticket
    # arrives (r1290 class); the leg is pure JSON reads, milliseconds.
    ("execution_admission_gap",
     ["python", "scripts/etf_book_execution_admission_gap.py", "run"]),
    # r1445: the year gate counts a partial year as a year on all four checks. That is
    # protective where the check asks for a booked loss (Y3) and a gift where it asks what
    # a typical year looks like (Y1/Y2/Y4) -- and in the published set the SAME artifact
    # both grants three ADMITs and denies one. `run` form (0.13s, pure JSON reads over four
    # receipts): every year block is republished as prices move, so a frozen receipt face
    # would go stale on its own (r1290 class). Nothing here is adopted; production is A.
    ("partial_year_caliber",
     ["python", "scripts/etf_book_partial_year_caliber.py", "run"]),
    # r1446: the two receipts above are true and a desk cannot hold both at once -- the
    # caliber dispute (r1445) says the gate is one decision away from disagreeing with
    # itself, the forward read (r1444) says the deciding check is decorative. This leg
    # answers the question that actually lands on 2026-11-11: the executed book's word is
    # INVARIANT (A/B/P all CONDITIONAL, 71.08% vs 72.78% against a 70% line), so the
    # caliber argument cannot move the money; meanwhile the construction the ticket prices
    # is one of four gift arms whose ADMIT exists only because a partial year counts as a
    # year. `run` form (0.01s, pure JSON reads): every input republishes as prices move
    # (r1290 class).
    ("supply_gate_decision",
     ["python", "scripts/etf_book_supply_gate_decision.py", "run"]),
    # r1447: r1446 left one question open -- is the weight in force (0.460253) even the
    # weight of a rule that was graded? This leg re-derives the published size-provenance
    # receipt from the ticket and its own inputs (same decision grid as the ticket, beta
    # rule repriced, graded book's vol rule repriced, five identity legs: k / names /
    # constant / priced bar / decision bar). `--check` form (0.2s, ticket + JSON only):
    # the 2-minute repricing runs only with `run` in its own round, and a drifted receipt
    # turns this leg red instead of leaving a stale gap on disk (r1290 class).
    ("live_size_provenance",
     ["python", "scripts/etf_book_live_size_provenance.py", "--check"]),
    # r1447: the horizontal question above ("is the running weight the graded rule's
    # weight") has a vertical twin -- DEFAULT_BETA is a literal, so the weight is
    # k = target/beta and the target could have been any point on a ladder. This leg
    # re-derives the published ladder receipt (9 targets, one engine, one panel) and
    # refuses a receipt whose verdict no longer follows from its own rows. `--check`
    # (0.2s, published JSON only); the 2.5-minute repricing runs with `run` in its round.
    ("weight_provenance",
     ["python", "scripts/etf_book_weight_provenance.py", "--check"]),
    # r1428: "refused" with no horizon is an observation, not a plan. This leg re-checks
    # the published ETA face (identity against the phase gate's phase 0, so a drifted
    # repricing turns the leg red instead of silently promising a date). Read-only JSON,
    # milliseconds; the expensive repricing runs only with `run` in its own round.
    ("admission_eta", ["python", "scripts/etf_book_admission_eta.py", "check"]),
    # r1429: the two certified rulers disagree on the held book, so "use the trusted ruler"
    # silently became a choice. This leg re-derives the fixture election and the witness
    # reading from the published face -- if a ruler or a fixture verdict moves, the leg goes
    # red instead of leaving a stated choice on disk describing an older table. Read-only
    # JSON, ~0.1s.
    ("ruler_election", ["python", "scripts/etf_book_admission_ruler_election.py", "check"]),
    # r1431: r1429's election named a ruler, but nothing was switched: replacing a gate's
    # refusal reason is an admission-rule change and needs its own round. This leg re-derives
    # the adoption verdict FROM the receipt's own five conditions and re-checks the year-table
    # identity against the published calibers, so a hand-edited verdict or a drifted series
    # turns red instead of leaving "the reason may be switched" on disk describing older data.
    ("refusal_caliber_adoption",
     ["python", "scripts/etf_book_admission_refusal_caliber_adoption.py", "check"]),
    # r1433: four rounds went into the RULER that refuses the book and none into the dial the
    # desk actually owns. The vol target was the obvious candidate ("make the book steadier and
    # it stops earning its money too early"), so the sweep was run and published instead of
    # assumed: six scalings x the frozen phase set x both trusted rulers, every arm refused.
    # This leg re-derives each arm word and the scale-invariance deltas FROM THE PUBLISHED
    # CELLS (JSON read, no repricing), so a stale sweep cannot keep claiming it was run and a
    # hand-typed verdict cannot pass.
    ("vol_target_gate", ["python", "scripts/etf_book_vol_target_gate.py", "check"]),
    # r1331: E196 answers the question E190 left open -- whether the month the
    # ladder-drop verdict rests on is knowable in advance. It is a ~1s JSON read of
    # the E186 month table (no panel, no network, no engine), and it belongs on the
    # chain rather than in a session's memory because a face nobody re-derives is the
    # r1290 class: the reading stays on disk describing a table that may have moved.
    # It pins the reading, not the upstream -- the WHERE face it reads is itself a
    # session artefact, and the leg says so instead of implying a fresh measurement.
    ("ladderdropcarrier", ["python", "scripts/e39_panel_census.py",
                            "tilt3ladderdropcarrier"]),
    # r1332: E196 could only name the month; it could not say whether the calendar
    # label is a market mechanism or just this family's naming. E198 tests the same
    # window on a panel the family never touched -- 17 declared ETFs against the
    # benchmark, same statistic, three window definitions. It reads local daily CSVs
    # only (no network, no engine) and is idempotent, so it rides the chain: a
    # negative verdict that is never re-derived is exactly the r1290 class.
    ("reviewwindowcross", ["python", "scripts/e39_panel_census.py",
                           "reviewwindowcross"]),
    # r1332: MSG-20261029-0510-bma found knowledge/METHODOLOGY_ASSETS.md at origin
    # holding only 66 lines (E195+E196) -- a writer published a file built from a
    # stale local copy and ate every earlier card, and unlike the attrition ledgers
    # this append-only face had no tripwire. This leg is that tripwire: it fails when
    # a card committed at HEAD is missing from the tree, or when a NEW duplicate
    # number appears; it only warns on the pre-existing disorder of the union-restored
    # history (7 descents / 11 dupes) because a permanently red gate gets "fixed" by
    # loosening the assertion (r1135). ~0.2s, git read only.
    ("card_ledger_guard", ["python", "Tools/card_ledger_guard.py", "check"]),
    # r1333: E198's verdict is a NEGATIVE, and a negative is only informative if the
    # test could have produced a positive. This leg republishes the detection floor
    # (minimum window/outside |gap| ratio at 80% power, from the EXACT permutation sd)
    # beside the observed ratio on the same rows, so the chain carries "this test was
    # blind below X" next to the "not found" it defends. ~4s, reads the same 20 daily
    # CSVs and never loads a panel.
    ("reviewwindowfloor", ["python", "scripts/e39_panel_census.py",
                           "reviewwindowfloor"]),
]


def run_leg(name, cmd, refresh=None, quiet=False):
    """Run one leg; pay the declared refresh ONLY when the probe says the face is stale.

    r1345: a check-only leg goes red the moment the panel advances past the bar its
    face was priced on, and stays red until somebody re-derives it by hand -- three
    legs sat red across two chain records (r1343/r1344) that reported NONZERO and
    moved on. A gate that is permanently red on inherited state is the r1135 trap
    (the cheap repair becomes loosening the assertion). So a leg may declare a
    refresh command, paid only when the probe itself says STALE -- never when it
    says INCONSISTENT, which stays red.
    """
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=900)
        rc = r.returncode
        text = (r.stdout or "") + (r.stderr or "")
        tail = (r.stdout or "").strip().splitlines()[-1:] or [""]
    except subprocess.TimeoutExpired:
        rc = 124
        text = ""
        tail = ["TIMEOUT"]
    refreshed = None
    if rc != 0 and refresh and "stale" in text.lower():
        tr = time.time()
        try:
            rr = subprocess.run(refresh, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=900)
            refresh_rc = rr.returncode
        except subprocess.TimeoutExpired:
            refresh_rc = 124
        refreshed = {"cmd": refresh, "rc": refresh_rc,
                     "elapsed_sec": round(time.time() - tr, 1)}
        try:
            r2 = subprocess.run(cmd, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=900)
            rc = r2.returncode
            tail = (r2.stdout or "").strip().splitlines()[-1:] or [""]
        except subprocess.TimeoutExpired:
            rc = 124
            tail = ["TIMEOUT"]
    rec = {"leg": name, "rc": rc,
           "elapsed_sec": round(time.time() - t0, 1), "tail": tail[0][:220]}
    if refreshed:
        rec["refreshed"] = refreshed
    if not quiet:
        note = (" +refresh(rc=%s,%ss)" % (refreshed["rc"], refreshed["elapsed_sec"])) if refreshed else ""
        print(f"{rc:3d} {name:18s} {rec['elapsed_sec']:7.1f}s {tail[0][:110]}{note}",
              flush=True)
    return rec


def selftest():
    """Prove the branch that matters: stale pays the refresh, inconsistent does not.

    Two fixtures, both rc=2 with a refresh declared. Only the one whose probe says
    "stale" may run its refresh; the other must stay red WITH the refresh unspent --
    otherwise the gate has become a machine for making red go away.
    """
    import tempfile
    py = sys.executable
    legs = []

    def _check(name, ok, detail=""):
        legs.append((name, ok, detail))

    with tempfile.TemporaryDirectory() as td:
        flag = os.path.join(td, "refreshed.flag")
        # The probe reads the marker file the refresh writes: red until refreshed.
        probe = [py, "-c",
                 "import os,sys;p=r'%s';done=os.path.exists(p);"
                 "print('ok' if done else 'face is stale: priced on 2026-10-28 while the card is on 2026-10-29');"
                 "sys.exit(0 if done else 2)" % flag]
        refresh_cmd = [py, "-c", "open(r'%s','w').write('1')" % flag]
        rec = run_leg("stale_fixture", probe, refresh_cmd, quiet=True)
        _check("a stale probe pays its refresh once and comes back green",
               rec["rc"] == 0 and rec.get("refreshed", {}).get("rc") == 0,
               "rec=%r" % (rec,))

        flag2 = os.path.join(td, "must_stay_unspent.flag")
        bad_probe = [py, "-c",
                     "import sys;print('face is inconsistent: control arm does not reproduce the cell');sys.exit(2)"]
        bad_refresh = [py, "-c", "open(r'%s','w').write('1')" % flag2]
        rec2 = run_leg("inconsistent_fixture", bad_probe, bad_refresh, quiet=True)
        _check("an inconsistent probe stays red with its refresh unspent",
               rec2["rc"] == 2 and "refreshed" not in rec2 and not os.path.exists(flag2),
               "rec=%r spent=%r" % (rec2, os.path.exists(flag2)))

        rec3 = run_leg("no_refresh_fixture", bad_probe, None, quiet=True)
        _check("a leg without a refresh declared is unaffected",
               rec3["rc"] == 2 and "refreshed" not in rec3, "rec=%r" % (rec3,))

    # The leg table must be structurally readable by the new unpacking, and every
    # declared refresh must be a real argument vector (not a bare string).
    _check("every leg is (name, cmd[, refresh]) with list commands",
           all(len(t) in (2, 3) and isinstance(t[0], str) and isinstance(t[1], list)
               and (len(t) == 2 or isinstance(t[2], list)) for t in LEGS),
           "bad=%r" % ([t[0] for t in LEGS if not (len(t) in (2, 3) and isinstance(t[1], list))],))
    n_refresh = sum(1 for t in LEGS if len(t) == 3)
    _check("the six check-only legs declare a refresh", n_refresh >= 6, "n=%d" % n_refresh)
    full = chain_record_path(1364)
    scoped = chain_record_path(1364, "fund_premium")
    _check("a --only record cannot overwrite the full-chain record",
           full == "results/_r1364bmc_s6_chain.json"
           and scoped == "results/_r1364bmc_s6_chain.only-fund_premium.json"
           and full != scoped, "full=%r scoped=%r" % (full, scoped))
    _check("a --only record name survives commas and odd characters",
           chain_record_path(1364, "a, b/c") == "results/_r1364bmc_s6_chain.only-a-b_c.json",
           "got=%r" % (chain_record_path(1364, "a, b/c"),))
    _long = ",".join(t[0] for t in LEGS[:23])
    _long_path = chain_record_path(1170, _long)
    _check("a long --only list still yields a writable record name",
           len(_long_path) + len(".tmp") < 120 and "+23-" in _long_path,
           "len=%d path=%r" % (len(_long_path), _long_path))
    _same_prefix = chain_record_path(1170, _long + ",union_one")
    _check("a capped name still separates two subsets sharing a prefix",
           _long_path != _same_prefix and "+24-" in _same_prefix,
           "a=%r b=%r" % (_long_path, _same_prefix))

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, detail in legs:
        print(("[PASS] " if ok else "[FAIL] ") + name + ("" if ok else " | " + detail))
    print("%d/%d PASS" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


# Windows refuses a path over MAX_PATH (260) with OSError [Errno 22]; the repo root alone
# eats ~50 chars on the shallowest machine, so the scope slug gets a fixed budget rather
# than the whole leg list.
ONLY_SLUG_MAX = 60


def chain_record_path(round_no, only=None) -> str:
    """Where a chain record goes: the run scope belongs in the name.

    r1364: `--only <leg>` wrote to the same path as a full-chain run and clobbered
    results/_r1361bmc_s6_chain.json (101 legs -> 1). An atomic replace (r1343)
    protects against a torn write, not against a smaller run wearing the big
    run's name -- the file has to say what it measured.
    """
    if only:
        names = sorted(w.strip() for w in str(only).split(",") if w.strip())
        raw = "-".join(names)
        slug = "".join(c if (c.isalnum() or c in "-_") else "_" for c in raw)
        # r1170: a 23-leg --only run produced a 208-char file name and the record write died
        # with OSError [Errno 22] *after* every leg had already returned rc0 -- the work was
        # real and the evidence was thrown away by the naming rule. Cap the readable prefix
        # and fingerprint the full list, so the name still says what it measured and two
        # different subsets can never share one file.
        if len(slug) > ONLY_SLUG_MAX:
            digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8]
            head = "".join(c if (c.isalnum() or c in "-_") else "_" for c in raw[:ONLY_SLUG_MAX - 22])
            slug = "%s+%d-%s" % (head.rstrip("-_"), len(names), digest)
        return f"results/_r{round_no}bmc_s6_chain.only-{slug}.json"
    return f"results/_r{round_no}bmc_s6_chain.json"


def main():
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    args = [a for a in sys.argv[1:]]
    only = None
    for a in list(args):
        if a.startswith("--only"):
            only = a.split("=", 1)[1] if "=" in a else None
            args.remove(a)
            if only is None:
                # r1428: `--only a,b --round 1` used to pop args[0], which is `--round`
                # when the flag is written first -- the run then died with "unknown
                # leg(s): ['--round']" and nothing said the flag form was the problem.
                only = args.pop(0) if args else ""
                if only.startswith("--"):
                    print("refusing: --only needs its leg list attached; write "
                          "--only=a,b (or put --only last). Got %r instead." % (only,))
                    sys.exit(2)
    # r1343: `--all` used to be swallowed as the round number, so a chain run that way
    # wrote results/_r--allbmc_s6_chain.json (three such junk names are committed:
    # _r--all, _r--round, and _rrun). A flag is not an identity: take the round from
    # --round N / the first bare number, and refuse to invent a filename for anything
    # else instead of guessing.
    round_no = "0"
    for a in list(args):
        if a.startswith("--round"):
            args.remove(a)
            round_no = a.split("=", 1)[1] if "=" in a else (args.pop(0) if args else "")
        elif a == "--all":
            args.remove(a)
    if args:
        round_no = args[0]
    if round_no == "0":
        # `--all` is a legitimate "run every leg" call, but it says nothing about which
        # round this is: name the record after this machine's own state instead of "0".
        try:
            with open("state-bm-c.json", encoding="utf-8") as f:
                round_no = str(json.load(f).get("round_no") or "0")
        except Exception:
            pass
    if not str(round_no).isdigit():
        print("refusing: round number must be numeric (got %r); "
              "use --round N --all/--only ... so the chain record is not named after a flag"
              % (round_no,))
        sys.exit(2)
    legs = LEGS
    if only is not None:
        want = [w.strip() for w in only.split(",") if w.strip()]
        legs = [t for t in LEGS if t[0] in want]
        missing = sorted(set(want) - {t[0] for t in legs})
        if missing:
            print(f"unknown leg(s): {missing}; known={[t[0] for t in LEGS]}")
            sys.exit(2)
    out = [run_leg(name, cmd, *rest) for name, cmd, *rest in legs]

    path = chain_record_path(round_no, only)
    # r1343: an interrupted json.dump leaves a one-byte record behind
    # (results/_r1314bmc_s6_chain.json carries 161 bytes from a one-leg run, and the
    # 12:47 record from r1337 is a three-leg fragment). Write beside the target and
    # rename, so a record on disk is either the whole chain or the previous one.
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    bad = [o for o in out if o["rc"] != 0]
    print(f"chain: {len(out)-len(bad)}/{len(out)} rc0 -> {path} "
          f"({datetime.now().isoformat(timespec='seconds')})")
    if bad:
        print("NONZERO: " + ", ".join(f"{o['leg']}={o['rc']}" for o in bad))


if __name__ == "__main__":
    main()