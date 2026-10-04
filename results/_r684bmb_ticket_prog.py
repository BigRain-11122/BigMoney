# r684 bm-b: append progress_r684_bmb to T-148 ticket (surgical JSON field add
# per r629 mirror law: comma discipline + reparse + key-count self-check).
import io, json

FP = r"fleet/tasks/T-2026-10-02-148-P1.json"
raw = io.open(FP, encoding="utf-8").read()
assert '"progress_r684_bmb"' not in raw, "already present"

PROG = (
    ' "progress_r684_bmb": "r684 bm-b slice-3 PENDING-LEGS MACHINERY LANDED '
    '+ LOWAMP-2 BURNED: (1) scripts/contest_ytd_legs.py new runner -- lowamp '
    'leg reuses lowamp_p3 continuous machinery verbatim (LA-EDGE W104/N2 '
    'deep axis, base/x2 faces) with full-run reuse-parity anchors vs '
    'published s1_evidence_extract deep_axis_faces (ret_full 0.604283 / '
    '0.554954 + sharpe/nav/trades/entries all reproduced exactly); revcensus '
    'leg = census _cell_job mirror with series retention, '
    'refine_bench_rev_census axis layer verbatim, census-stats parity '
    'anchors vs published shard rows (sharpe_full/ann_ret/max_dd/n_days + '
    'entries/unfillable/skips/exits, abort on drift), RAM floor 16GB exit 3 '
    '(census law, trio NULLS holds RAM), ProcessPool run_cells_parallel, '
    'idempotent checkpoint; selftest 9/9. (2) contest_ytd_p1.py assemble '
    'A1.5: pending-burn rows auto-merge (unknown/duplicate rows abort), '
    'census recounts, honesty line for the 176d-vs-181d lockbox-window '
    'mismatch (B_MAXDIV precedent), pending filter by landed rows; selftest '
    '12/12 ALL PASS. (3) lowamp-2 BURNED inline (deterministic ~1min): '
    'LX-LA-EDGE-deep-base ytd +0.49% / -x2 ytd +0.51%, window '
    '2026-01-05..09-22 176d, ranks #41/#43 of 185; assembly rerun '
    'byte-deterministic (table sha16 e70010c053da57a6), census 209 measured '
    '(185 ranked + 24 listed) + 10 pending RC; CONTEST-TABLE.md CEO face '
    'refreshed. (4) RC-10 pool unit CONTEST-YTD-P1-RC-0OF1 submitted via '
    'autofill contract (host_gates p1c cache dir + data_deps 4 paths, '
    'workers 4 BelowNormal, consumer_plan assembly A1.5) -- autofill '
    'claims when RAM floor clears (trio ETAs 10-06..10-08, deadline 10-08 '
    'covered both machines). NEXT: RC burn lands -> assemble rerun -> '
    'full-pool 219-measured table by 10-08."'
)

# find the closing brace of the last progress field + ticket object
needle = ' 12 pending-burn legs (rev-census-10 + lowamp-2) disclosed in-table, due before 10-08; assembly rerun auto-includes them. Pit: T-146 ytd_curves nav 8dp-rounded + paper-only max_dd entry-capital-anchored -> published summary metrics authoritative, curves only for scale-invariant derived fields (sharpe)."\n}'
assert raw.count(needle) == 1, "ticket tail needle != 1"
patched = raw.replace(needle, needle[:-2] + ',\n' + PROG + '\n}')
with io.open(FP, "w", encoding="utf-8", newline="") as f:
    f.write(patched)
doc = json.loads(io.open(FP, encoding="utf-8").read())
assert "progress_r684_bmb" in doc and doc["status"] == "claimed"
print("ticket patched: keys =", len(doc), "| progress_r684_bmb len =",
      len(doc["progress_r684_bmb"]))
