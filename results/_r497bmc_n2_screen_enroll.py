"""r497 bm-c: PERPETUAL-N2-W15-SCREEN 12-shard pool enrollment per
research/PERPETUAL_N2_W15_PREREG.md FROZEN (bm-c r492 commit 1ff613cbe).
Supply-materialization step 2 (seat: MSG-2026-10-04-2100 sec.3.3 declared
+ MSG-2026-10-04-2115 window; bounds from ACTUAL rows r670 tiling + r481
recipe). Raw-text surgical insert per r678 law. Anti-double-enroll gate.
Runner three-call claim on verified done (r496 canon). Evidence ->
results/_r497bmc_n2_screen_enroll.json."""
import datetime
import difflib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
EVID = os.path.join(ROOT, "results", "_r497bmc_n2_screen_enroll.json")

now_dt = datetime.datetime.now().astimezone()
now = now_dt.strftime("%Y-%m-%d %H:%M:%S")
now_iso = now_dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")

sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from science_gates import SEED_REGISTRY  # noqa: E402
import perpetual_faces_n2 as n2  # noqa: E402

# --- freeze-state + product facts (live reads, zero hand-copy) ---
bands = {k: SEED_REGISTRY.get(k) for k in
         ("perpetual_n2_w15_gen", "perpetual_n2_w15_scrnull",
          "perpetual_n2_w15_unc")}
assert bands["perpetual_n2_w15_gen"] == 541500, bands
assert bands["perpetual_n2_w15_scrnull"] == 542000, bands
assert bands["perpetual_n2_w15_unc"] == 542500, bands
assert os.path.exists(n2.CANDIDATES_FILE), "candidates absent"
assert os.path.exists(n2.PREP_FILE), "prep state absent"
cells = n2._cell_list_n2()
n_cells = len(cells)
assert n_cells == 1154, n_cells
sizes = []
for s in range(12):
    mine = [c for i, c in enumerate(cells) if i % 12 == s]
    sizes.append(len(mine))
assert sizes == [97, 97] + [96] * 10, sizes
seen = []
for s in range(12):
    seen.extend(c["cell_id"] for i, c in enumerate(cells) if i % 12 == s)
assert sorted(seen) == sorted(c["cell_id"] for c in cells), "tiling union"
assert len(set(c["cell_id"] for c in cells)) == n_cells, "dup cell_id"

# --- pool state + anti-double-enroll gate ---
raw = open(POOL, encoding="utf-8", newline="").read()
data = json.loads(raw)
entries = data["entries"]
n_before = len(entries)
new_ids = [f"PERPETUAL-N2-W15-SHARD-{i}" for i in range(12)]
have = {str(e.get("id", "")) for e in entries}
for nid in new_ids:
    assert nid not in have, "already enrolled: " + nid
try:
    rt = json.dumps(data, indent=1, ensure_ascii=False)
    roundtrip_stable = (rt + ("\n" if raw.endswith("\n") else "")) == raw
except Exception:
    roundtrip_stable = False

ticket = ("T-2026-09-30-133 s2 perpetual-supply N2 line (O-2026-09-30-2340 CEO "
          "standing-supply order, prereg sec.0 authorization face; seat = "
          "MSG-2026-10-04-2100 sec.3.3 declared + MSG-2026-10-04-2115 "
          "declaration window honored; bm-b review right per MSG-1845 clause 2)")
prereg = ("research/PERPETUAL_N2_W15_PREREG.md FROZEN r492 commit 1ff613cbe "
          "(sec.3 screen stage: bounds from ACTUAL rows n=1,154 = 954 "
          "candidates + 200 scrnull nulls, r670 tiling i%12==shard sizes "
          "97/97/96x10 union-exactly-once machine-checked; survival line = "
          "beat6m_rate > null-family p95 tl2._finalize_math same-face + "
          "n_entries>=1 honest leg; single-axis 6m base full leg-L backtest, "
          "EW48 passive beat-rate, V1 13.041bp cost always on; evidence_cutoff "
          "2026-09-22 sec.2; scrnull band 542_000; screen-finalize = ledger "
          "PERPETUAL-N2-W15-SCREEN, separate owner after all 12 done)")
ckpt_note = ("results/n2_w15/checkpoint/n2_screen_shard_%dof12.jsonl "
             "(append-per-cell kill-safe resume, r670 scanner pairing "
             "non-empty payload law)")

entries_new = []
for i in range(12):
    entries_new.append({
        "id": f"PERPETUAL-N2-W15-SHARD-{i}",
        "ticket_ref": ticket,
        "prereg_ref": prereg,
        "runner": "scripts/perpetual_faces_n2.py",
        "runner_args": ["run", "--shard", str(i), "--shards", "12"],
        "lane_owner": None,
        "priority": 1,
        "status": "ready",
        "entered_at": now_iso,
        "workers_plan": {
            "workers": 8,
            "priority": "BelowNormal",
            "note": ("per-cell single-axis 6m full-history backtest "
                     "(W14 same engine face ~2.25s/cell probe-caliber); "
                     "~%d cells this shard; ProcessPool state-shared "
                     "initializer; in-runner RAM gate three-sample >=4GB "
                     "r354 (honest refuse rc2 -> pool retry when RAM "
                     "frees; trio-locked machines refuse honestly by "
                     "design); CEO 10%% CPU reserve law = BelowNormal"
                     % sizes[i]),
        },
        "data_gates": ("in-runner fail-closed exit 2: (a) FREEZE-GATE "
                       "SEED_REGISTRY trio == 541500/542000/542500; "
                       "(b) RUN-GATE prep state + candidates file "
                       "present; (c) RAM gate r354; (d) post-burn "
                       "missing-cells = honest refuse NO pool claim "
                       "(checkpoint retained for resume). deps all "
                       "in-repo: core48 panel + b_layer_mask + frozen "
                       "grammar sha16 a231bf10940e7878"),
        "data_deps": ["data/daily/", "data/fundamental/b_layer_mask.csv",
                      "results/n2_w15/n2_w15_candidates.json",
                      "results/n2_w15/n2_w15_prep_state.json"],
        "shards": [{
            "key": f"n2w15-{i}of12",
            "status": "ready",
            "checkpoint": ckpt_note % i,
            "note": ("bounds: cells i%%12==%d over 1,154 (97/97/96x10 "
                     "tiling); runner r496 three-call claim on verified "
                     "done (claim file results/pool_claims/"
                     "PERPETUAL-N2-W15-SHARD-%d/); done-flip duty = "
                     "burner-side settle per r244 landed-marker law + "
                     "r668 post-finalize pool recheck law" % (i, i)),
        }],
        "entered_by": "bm-c r497",
        "worker_class": "self-contained",
    })

# --- raw-text surgical insert (r678 law) ---
tail_probe = raw[-200:]
eol = "\r\n" if "\r\n" in tail_probe else "\n"
tail_marker = eol + " ]" + eol + "}"
idx = raw.rfind(tail_marker)
assert idx != -1, "tail marker not found"
pre = raw[:idx]
assert pre.endswith(eol + "  }"), \
    "last entry close shape unexpected: %r" % pre[-10:]


def ser(e):
    t = json.dumps(e, indent=1, ensure_ascii=False)
    return "  " + "\n  ".join(t.split("\n"))


insertion = "," + eol + ("," + eol).join(ser(e) for e in entries_new)
new_raw = pre + insertion + raw[idx:]

lines = new_raw.splitlines(True)
ua_idx = [k for k, ln in enumerate(lines)
          if ln.startswith(' "updated_at":')]
assert len(ua_idx) == 1, "updated_at line count=%d" % len(ua_idx)
lines[ua_idx[0]] = ' "updated_at": "%s",%s' % (now_iso, eol)
sn_idx = [k for k, ln in enumerate(lines)
          if ln.startswith(' "_stamp_note":')]
assert len(sn_idx) == 1, "stamp_note line count=%d" % len(sn_idx)
stamp = ("r497 bm-c N2-W15 SCREEN enrollment: +12 entries "
         "PERPETUAL-N2-W15-SHARD-0..11 (supply step 2; prereg FROZEN "
         "1ff613cbe; bounds from actual 1,154 rows r670 tiling 97/97/96x10; "
         "runner three-call claim; seat MSG-2115 window honored)")
stamp_json = json.dumps(stamp, ensure_ascii=False)
lines[sn_idx[0]] = ' "_stamp_note": %s,%s' % (stamp_json, eol)
new_raw = "".join(lines)

# --- post-surgery assertions ---
data2 = json.loads(new_raw)
ids2 = [str(e.get("id", "")) for e in data2["entries"]]
assert len(ids2) == n_before + 12, len(ids2)
for nid in new_ids:
    assert ids2.count(nid) == 1, nid
old_ids = [str(e.get("id", "")) for e in entries]
assert all(ids2.count(i) == 1 for i in old_ids), "old entry lost/duplicated"
for i, nid in enumerate(new_ids):
    e2 = next(x for x in data2["entries"] if x.get("id") == nid)
    assert e2["runner_args"] == ["run", "--shard", str(i), "--shards", "12"]
    assert e2["status"] == "ready" and e2["shards"][0]["status"] == "ready"
    assert e2["shards"][0]["key"] == f"n2w15-{i}of12"
diff = list(difflib.unified_diff(raw.splitlines(), new_raw.splitlines(),
                                 lineterm="", n=0))
added = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
removed = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
assert removed == 2, "expected exactly 2 replaced top-level lines, got %d" % removed

with open(POOL, "w", encoding="utf-8", newline="") as f:
    f.write(new_raw)
data3 = json.loads(open(POOL, encoding="utf-8", newline="").read())
assert len(data3["entries"]) == n_before + 12

ev = {
    "round": "r497 bm-c", "ts": now_iso, "bands": bands,
    "n_cells": n_cells, "sizes": sizes,
    "pool_entries_before": n_before, "pool_entries_after": n_before + 12,
    "new_ids": new_ids, "roundtrip_stable": roundtrip_stable,
    "diff_added_lines": added, "diff_removed_lines": removed,
    "eol_detected": repr(eol),
    "prereg": "research/PERPETUAL_N2_W15_PREREG.md FROZEN r492 1ff613cbe",
    "seat_msg": "fleet/inbox/MSG-2026-10-04-2115-bmc-ALL.md",
    "declared_msg": "fleet/inbox/MSG-2026-10-04-2100-bmc-ALL.md sec.3.3",
}
with open(EVID, "w", encoding="utf-8") as f:
    json.dump(ev, f, ensure_ascii=False, indent=1)
print("ENROLL OK: +12 PERPETUAL-N2-W15-SHARD-0..11, pool %d->%d, "
      "added=%d removed=%d, sizes=%s, eol=%r"
      % (n_before, n_before + 12, added, removed, sizes, eol))
