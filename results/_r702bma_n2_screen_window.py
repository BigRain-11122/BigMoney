# r702 bm-a -- N2-W15 screen-finalize WINDOW probe (MSG-2215 seat; 12/12
# trigger met: SHARD-2 landed 23:44:03 by bm-a daemon). READ-ONLY finalize-
# window audit per r685 law (dup probe re-runs IN the window, post-merge):
# import faces, freeze gate, idempotent guard, checkpoint tiling/pairing/
# dup/poison across ALL 12 shards, full coverage == 1154/1154 zero missing.
# NO ledger append, NO survivor math (no result-preview bias), NO writes
# except this receipt JSON. (Successor of _r700bma_n2_screen_rehearsal.py
# whose WAIT-face assertion (missing==SHARD-2 block) is now vacuously RED;
# this r702 form asserts the TRIGGER face: zero missing.)
import json
import os
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, REPO)

receipt = {"batch": "PERPETUAL-N2-W15", "stage": "screen-finalize-window-probe",
           "machine": "bm-a", "round": "r702",
           "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
           "note": "r685 finalize-window leg; supersedes the r700 "
                   "rehearsal WAIT-face for this window"}
problems = []

import perpetual_faces_n2 as n2e  # noqa: E402
import trial_labor_w1 as tl1      # noqa: E402
import trial_labor_w2 as tl2      # noqa: E402
import trial_labor_w6 as tl6      # noqa: E402
import science_gates as sg        # noqa: E402

faces = ["_cell_list_n2", "_load_screen_rows_n2", "_freeze_gate",
         "_ckpt_path", "NSHARDS", "K_NULLS", "CANDIDATES_FILE",
         "SCREEN_FILE", "BATCH_SCREEN", "CUTOFF"]
missing_attrs = [f for f in faces if not hasattr(n2e, f)]
for mod, fn in ((tl6, "finalize_already_landed"), (tl2, "_finalize_math"),
                (tl1, "append_ledger"), (tl1, "NULL_P_REGIMES"),
                (sg, "cutoff_meta")):
    if not hasattr(mod, fn):
        missing_attrs.append(f"{mod.__name__}.{fn}")
receipt["import_faces"] = {"n_checked": len(faces) + 5,
                           "missing": missing_attrs}
if missing_attrs:
    problems.append(f"import faces missing: {missing_attrs}")

rc = n2e._freeze_gate("screen-finalize")
receipt["freeze_gate_rc"] = rc
if rc != 0:
    problems.append("freeze gate refused (bands not registered)")
landed = tl6.finalize_already_landed(n2e.BATCH_SCREEN, n2e.SCREEN_FILE)
receipt["finalize_already_landed"] = landed is not None
if landed is not None:
    problems.append("screen already landed -- seat is stale, no finalize")

cells = n2e._cell_list_n2()
nshards, knulls = n2e.NSHARDS, n2e.K_NULLS
n_null_cells = sum(1 for c in cells if c["kind"] == "null")
expected = {sh: {c["cell_id"] for i, c in enumerate(cells)
                if i % nshards == sh} for sh in range(nshards)}
receipt["cells"] = {"n_total": len(cells), "n_nulls": n_null_cells,
                    "k_nulls_const": knulls,
                    "per_shard_counts": {str(s): len(v)
                                          for s, v in expected.items()}}
if n_null_cells != knulls:
    problems.append(f"null cell count {n_null_cells} != K_NULLS {knulls}")

per_shard, union_rows = {}, {}
total_dups = 0
for sh in range(nshards):
    ck = n2e._ckpt_path(sh, nshards)
    st = {"exists": os.path.exists(ck), "rows": 0, "nonempty_ok": 0,
          "poison_empty": 0, "outside_stride": [], "dup_in_shard": []}
    if st["exists"]:
        with open(ck, encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    r = json.loads(ln)
                except Exception:
                    st["poison_empty"] += 1
                    continue
                st["rows"] += 1
                ok = (r.get("cell_id") and "beat6m_n" in r
                      and r.get("family"))
                if not ok:
                    st["poison_empty"] += 1
                    continue
                st["nonempty_ok"] += 1
                cid = r["cell_id"]
                if cid not in expected[sh]:
                    st["outside_stride"].append(cid)
                if cid in union_rows:
                    st["dup_in_shard"].append(cid)
                else:
                    union_rows[cid] = sh
    total_dups += len(st["dup_in_shard"])
    per_shard[str(sh)] = st
    if st["outside_stride"]:
        problems.append(f"shard {sh}: {len(st['outside_stride'])} rows "
                        "outside its stride (r670 pairing violation)")
    if st["dup_in_shard"]:
        problems.append(f"shard {sh}: dup ids "
                        f"{st['dup_in_shard'][:3]} (r482 law)")
    if st["poison_empty"]:
        problems.append(f"shard {sh}: {st['poison_empty']} empty/poison "
                        "rows (r670 non-empty-payload law)")
    if not st["exists"]:
        problems.append(f"shard {sh}: checkpoint file missing")
receipt["per_shard"] = per_shard

missing_all = [c["cell_id"] for c in cells if c["cell_id"] not in union_rows]
receipt["coverage"] = {
    "landed_union": len(union_rows), "expected_total": len(cells),
    "missing_total": len(missing_all), "total_dups": total_dups}
if missing_all:
    problems.append(f"{len(missing_all)} missing cells (trigger NOT met)")
if len(union_rows) != len(cells):
    problems.append(f"landed {len(union_rows)} != expected {len(cells)}")

receipt["verdict"] = "GREEN_TRIGGER_MET" if not problems else "RED"
receipt["problems"] = problems
out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "_r702bma_n2_screen_window.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(receipt, fh, ensure_ascii=False, indent=1)
print(f"verdict={receipt['verdict']} landed={len(union_rows)}/"
      f"{len(cells)} missing={len(missing_all)} dups={total_dups} "
      f"problems={len(problems)}")
for p in problems:
    print("  PROBLEM:", p)
sys.exit(0 if not problems else 1)
