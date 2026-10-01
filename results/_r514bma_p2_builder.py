"""r514 bm-a: build scripts/lowamp_p2.py from lowamp_p1.py (T-140 action-4
next_steps (a) copy-adapt). Exact-string replacements with count assertions;
zero hand-edits beyond the declared diff (prereg sec.0.6 channel)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "scripts", "lowamp_p1.py")
DST = os.path.join(ROOT, "scripts", "lowamp_p2.py")
FREEZE = "c3c825c2a92e11e4fe44d9774894007619daf74f"

src = open(SRC, encoding="utf-8").read()
fails = []


def rep(old, new, want=1, tag=""):
    global src
    n = src.count(old)
    if n != want:
        fails.append(f"{tag}: count {n} != {want}")
        return
    src = src.replace(old, new)


# 1. header block (batch id + ticket + prereg/freeze lineage)
rep('''"""LOWAMP-P1 -- low-amplitude cross-sectional daily-rebalance family judged
batch (T-2026-09-30-132-P1 s2 runner + s3 judged burn).

Prereg (FROZEN, R99): research/LOWAMP-P1.md -- s1 frozen at 5074b5102
(bm-b r483) + 32c529f49 (bm-a r494 ADMIT face). Judgments live there;
this file implements them, never re-states a threshold.''',
    f'''"""LOWAMP-P2 -- low-amplitude cross-sectional daily-rebalance family judged
batch RE-ENTRY (T-2026-10-01-140 action-4 runner). The as-designed family
face re-enters supply via the exit-axis explicit gate FIRST application.

Prereg (FROZEN): research/LOWAMP-P2.md -- frozen at {FREEZE[:10]} (bm-a r514
adoption commit; banned_direction_gate ADMIT rc0 re-verified same round).
Judgments live there; this file implements them, never re-states a
threshold. LOWAMP-P1 verdict VOID-with-face-note (O-20261001-1108 sec.3);
this batch is a NEW batch, not a re-run (T-136 audit "Either way" line).''',
    tag="header")

# 2. execution semantics -> sec.0.6 exit-axis block
rep('''Execution semantics (prereg sec.3, engine canon, engine/ untouched):
  entry_signal = selected-today, exit_signal = entry<=0 (t22 _run_cell
  convention verbatim) -> engine.run_backtest (T+1, cost model, frozen exit
  priority). x2 face = CostPatch(2.0) multiplier (r82 fix face).''',
    '''Execution semantics (prereg sec.3 + sec.0.6 exit-axis, engine/ untouched):
  entry_signal = selected-today, exit_signal = entry<=0 (t22 _run_cell
  convention verbatim -- the ONLY exit: selection-rotation, the family's
  own mechanism). HOLD-THROUGH declared: the engine default exit stack is
  EXPLICITLY DISABLED key-by-key in run_cell_portfolio params (prereg
  sec.0.6 verbatim: take_profit_levels=(), trailing_stop_activate=1e12,
  initial_stop=-1.0, time_decay_period=1e9, loss_time_days=1e9,
  global_hard_limit=1e9) -- the same params channel the T-136 audit
  as-burned leg proved, used in reverse (r301 hybrid finding closed).
  x2 face = CostPatch(2.0) multiplier (r82 fix face).''',
    tag="semantics")

# 3. seed registry disclosure block
rep('''Seed registry disclosure: prereg sec.3 binds nulls to rng([20330500, k])
and sensitivity to rng([20330000, k]); SEED_REGISTRY rows added post-freeze
label 20330500 "lowamp_p1_starts" and 20331000 "lowamp_p1_nulls" -- the
20331000 row is NOT consumed by this batch (no random starts exist here;
full enumeration). Registry left untouched (historical), discrepancy
disclosed here and in the results audit block.''',
    '''Seed registry disclosure (P2 band, prereg sec.3 verbatim): nulls bound to
rng([20334500, k]); sensitivity param draws bound to rng([20333500, k]);
the lowamp_p2_starts=20334000 registry row is NOT consumed by this batch
(judged starts = T-22 deterministic full enumeration; sensitivity legs =
full-panel continuous runs) -- disclosed here and in the results audit
block.''',
    tag="seeds-doc")

# 4. usage lines
rep("python scripts/lowamp_p1.py ", "python scripts/lowamp_p2.py ", want=7,
    tag="usage")

# 5. constants
rep('TICKET = "T-2026-09-30-132"', 'TICKET = "T-2026-10-01-140"', tag="ticket")
rep('PREREG = os.path.join(ROOT, "research", "LOWAMP-P1.md")',
    'PREREG = os.path.join(ROOT, "research", "LOWAMP-P2.md")', tag="prereg")
rep('OUT_DIR = os.path.join(ROOT, "results", "lowamp_p1")',
    'OUT_DIR = os.path.join(ROOT, "results", "lowamp_p2")', tag="outdir")
rep('OUT_JSON = os.path.join(OUT_DIR, "lowamp_p1_results.json")',
    'OUT_JSON = os.path.join(OUT_DIR, "lowamp_p2_results.json")', tag="outjson")
rep('BATCH_NAME = "LOWAMP-P1"', 'BATCH_NAME = "LOWAMP-P2"', tag="batch")
rep("SEED_NULLS = 20330500                       # prereg sec.3 verbatim",
    "SEED_NULLS = 20334500                       # prereg sec.3 verbatim",
    tag="seed-nulls")
rep("SEED_SENS = 20330000                        # prereg sec.3 verbatim",
    "SEED_SENS = 20333500                        # prereg sec.3 verbatim",
    tag="seed-sens")

# 6. exit-axis params (the single semantic change, sec.0.6)
rep('''    params = {"position_size_pct": 1.0, "max_positions": 1,
              "sizing_mode": "fixed_initial", "report_num_entries": True}''',
    '''    params = {"position_size_pct": 1.0, "max_positions": 1,
              "sizing_mode": "fixed_initial", "report_num_entries": True,
              # sec.0.6 exit-axis: HOLD-THROUGH -- engine default exit
              # stack explicitly disabled key-by-key (prereg verbatim;
              # r301 default-stack x low-amp hybrid finding reversed via
              # the engine's own params channel -- engine/ untouched)
              "take_profit_levels": (),
              "trailing_stop_activate": 1e12,
              "initial_stop": -1.0,
              "time_decay_period": 10 ** 9,
              "loss_time_days": 10 ** 9,
              "global_hard_limit": 10 ** 9}''',
    tag="params")

# 7. pool entry identity (r495 registration face mirror)
rep('''    if getattr(args, "nulls", None):
        return ("LOWAMP-P1-NULLS", "lowamp-p1-nulls-0of1")
    if getattr(args, "sensitivity", None):
        return ("LOWAMP-P1-SENS", "lowamp-p1-sens-0of1")
    entry = ("LOWAMP-P1-CELL-" + args.cell.replace("-", "").upper()
             + "-" + args.axis.upper() + "-" + args.face.upper())''',
    '''    if getattr(args, "nulls", None):
        return ("LOWAMP-P2-NULLS", "lowamp-p2-nulls-0of1")
    if getattr(args, "sensitivity", None):
        return ("LOWAMP-P2-SENS", "lowamp-p2-sens-0of1")
    entry = ("LOWAMP-P2-CELL-" + args.cell.replace("-", "").upper()
             + "-" + args.axis.upper() + "-" + args.face.upper())''',
    tag="entry-of")

# 8. status dir string
rep('print("no results/lowamp_p1 yet")',
    'print("no results/lowamp_p2 yet")', tag="status-dir")

# 9. finalize refs
rep('"probe_ref": "results/lowamp_p1/probe.json"',
    '"probe_ref": "results/lowamp_p2/probe.json"', tag="probe-ref")
rep('file_name="results/lowamp_p1/lowamp_p1_results.json"',
    'file_name="results/lowamp_p2/lowamp_p2_results.json"', tag="ledger-file")

# 10. probe seed_disclosure note
rep('''        "note": "registry row lowamp_p1_nulls=20331000 NOT consumed by this "
                "batch; prereg sec.3 binds nulls to 20330500 (verbatim)."}''',
    '''        "note": "registry row lowamp_p2_starts=20334000 NOT consumed by "
                "this batch (T-22 full enumeration judged starts; "
                "full-panel continuous sensitivity); prereg sec.3 binds "
                "nulls to 20334500 and sens draws to 20333500 "
                "(verbatim)."}''',
    tag="seed-note")

# 11. argparse description
rep('argparse.ArgumentParser(description="LOWAMP-P1 judged batch runner")',
    'argparse.ArgumentParser(description='
    '"LOWAMP-P2 judged batch runner (exit-axis hold-through)")',
    tag="argparse")

if fails:
    print("BUILDER FAIL:")
    for f in fails:
        print(" -", f)
    sys.exit(2)

# residual scan: no P1 identifiers may survive (the intentional
# "LOWAMP-P1 verdict VOID" lineage mention in the header is the only
# allowed bare-P1 reference; entry ids / paths / old seeds must be gone)
resid = [t for t in ("LOWAMP-P1-", "lowamp_p1", "lowamp-p1", "20330500",
                     "20330000", "20331000") if t in src]
if resid:
    print("RESIDUAL P1 tokens:", resid)
    sys.exit(3)

open(DST, "w", encoding="utf-8", newline="\n").write(src)
print(f"wrote {DST} ({len(src.splitlines())} lines)")
print("exit-axis params block present:",
      '"take_profit_levels": ()' in src and '"global_hard_limit": 10 ** 9' in src)
