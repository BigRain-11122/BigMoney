# -*- coding: utf-8 -*-
"""r239 ticket updates: T-74 progress_r239 insert; T-75 flip done + result_ref.
Text-level minimal-diff inserts per r230 law (indent/EOL preserved)."""
import io

# --- T-74: progress insert before ticket_lineage anchor
p74 = "fleet/tasks/T-2026-09-26-74-P1.json"
with io.open(p74, "r", encoding="utf-8", newline="") as f:
    raw = f.read()
eol = "\r\n" if "\r\n" in raw else "\n"
anchor = ' "ticket_lineage":'
assert anchor in raw and '"progress_r239"' not in raw
prog = (
    ' "progress_r239": "s0 DELIVERED: canonical 6-layer tree + s2 prereg frozen at research/MARKET_CLOCK_COMBO.md ('
    'Arm-A regime-only operative 4 cells; heat composite UNFROZEN per data-honesty audit -- popularity 3 snapshots only, freeze gate >=60 trading days; '
    'N_eff=8; gates G1_prime_v2/G2v2 shared lib; honest window: sector faces 2020+ per panel audit, deep-history regime arm via import-replay). '
    's1 DELIVERED: docs/market_call/CALL-20260926.md (ORANGE call, ladder 50%, defense-leaning sleeve, top-3 sector tilt 512800/159985/513100, '
    'fund-event distortion guard flagged for 512480/159995 r60). s2 NEXT SLICE: runner scripts/market_clock_replay.py -> hermetic selftest -> pool submit (CPU multi-core, D-20260926-02); '
    's2 prep first step = SW/sector name-audit table (public source) + fund-event guard leg",'
    + eol
)
raw = raw.replace(anchor, prog + anchor, 1)
with io.open(p74, "w", encoding="utf-8", newline="") as f:
    f.write(raw)
print("T-74 progress inserted")

# --- T-75: status claimed->done + result_ref
p75 = "fleet/tasks/T-2026-09-26-75-P1.json"
with io.open(p75, "r", encoding="utf-8", newline="") as f:
    raw = f.read()
anchor = ' "status": "claimed",'
assert anchor in raw
repl = (' "status": "done",' + eol
        + ' "result_ref": "scripts/daily_report.py (run/force/selftest, 4 faces COMBAT/R&D/DECISION/TOMORROW, selftest PASS; '
        '55 accounts aggregated; _-prefixed schema-foreign files skipped) + firm/DECISIONS.md canon (3 backfilled entries D-01..03) + '
        'first report docs/daily_report/REPORT-20260926.md(+json twin, force-channel bootstrap disclosed) + '
        'S6 chain wiring Tools/iteration_prompt.txt (byte-precise LF-preserved insert, fires workday>=15:45) + '
        'scorecard CEO-face pointer line (T-29 cite) + smoke zero-regression verified r239",')
raw = raw.replace(anchor, repl, 1)
with io.open(p75, "w", encoding="utf-8", newline="") as f:
    f.write(raw)
print("T-75 flipped done with result_ref")
