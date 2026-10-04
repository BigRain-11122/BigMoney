"""r705 bm-a: PERPETUAL-N2-W15-JUDGE-PREP done-flip (entry+shard double
layer, r489 law) + 12-shard judge enrollment (r497 enrollment pattern,
sec.9.1 FROZEN r702 bm-b; N_judge=281 fixed by judge-prep r705 bm-a
PASS 01:10:23, collapse eliminated 0).

Laws applied: raw-text surgical edits only (r509/r678), entry-region
anchored needles (r694-2 batch-prefix shard keys), host-EOL ser() (r485),
anti-double-enroll gate, post-surgery reparse + id-count + difflib
assertions, burn+flip atomic same-window (r489/r668 -- the prep product
landed this window; leaving pool ready = re-claim churn face).
"""
import datetime
import difflib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
EVID = os.path.join(ROOT, "results", "_r705bma_n2_judge_enroll.json")

now_dt = datetime.datetime.now().astimezone()
now = now_dt.strftime("%Y-%m-%d %H:%M:%S")
now_iso = now_dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")

sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from science_gates import SEED_REGISTRY  # noqa: E402

# --- freeze-state + product facts (live reads, zero hand-copy) ---
assert SEED_REGISTRY.get("perpetual_n2_w15_judge") == 545500, \
    SEED_REGISTRY.get("perpetual_n2_w15_judge")
st = json.load(open(os.path.join(ROOT, "results", "n2_w15",
                                 "n2_w15_judge_state.json"),
                    encoding="utf-8"))
kept = sorted(st["collapse"]["kept"])
elim = sorted(st["collapse"].get("eliminated", []))
n_cells = len(kept)
assert n_cells == 281 and len(elim) == 0, (n_cells, len(elim))
assert st["seed_judge"] == 545500, st["seed_judge"]
sizes = [sum(1 for i in range(n_cells) if i % 12 == s) for s in range(12)]
assert sizes == [24] * 5 + [23] * 7, sizes
assert sum(sizes) == n_cells

# --- pool state + anti-double-enroll gate ---
raw = open(POOL, encoding="utf-8", newline="").read()
data = json.loads(raw)
entries = data["entries"]
n_before = len(entries)
have = {str(e.get("id", "")) for e in entries}
new_ids = [f"PERPETUAL-N2-W15-JUDGE-SHARD-{i}" for i in range(12)]
for nid in new_ids:
    assert nid not in have, "already enrolled: " + nid
assert "PERPETUAL-N2-W15-JUDGE-PREP" in have
eol = "\r\n" if "\r\n" in raw[-300:] else "\n"

# --- STEP A: JUDGE-PREP entry+shard double done-flip (surgical) ---
epos = raw.find('"PERPETUAL-N2-W15-JUDGE-PREP"')
assert epos >= 0 and raw.count('"PERPETUAL-N2-W15-JUDGE-PREP"') == 1
region_end = raw.find('"id"', epos + 10)
if region_end == -1:
    region_end = len(raw)

needle_entry = ('   "status": "ready",' + eol
                + '   "entered_at": "2026-10-05 01:0x",')
hit = raw.find(needle_entry, epos, region_end)
assert hit != -1, "prep entry status anchor not found in entry region"
repl_entry = (
    '   "status": "done",' + eol
    + '   "done_by": "bm-a",' + eol
    + '   "done_at": "%s",' % now + eol
    + '   "result_ref": "results/n2_w15/n2_w15_judge_state.json '
    '(judge-prep PASS 2026-10-05 01:10:23 by bm-a r705 detached spawn '
    '188s: survivors 281 -> N_judge 281, collapse eliminated 0; census '
    'L/D == frozen; dual-leg starts/passive precomputed; seed_judge '
    '545_500; one-shot state-file gate armed)",' + eol
    + '   "entered_at": "2026-10-05 01:0x",')
raw_a = raw[:hit] + repl_entry + raw[hit + len(needle_entry):]

# shard flip (same entry region, post-A needles stay unique there)
epos_a = raw_a.find('"PERPETUAL-N2-W15-JUDGE-PREP"')
region_end_a = raw_a.find('"id"', epos_a + 10)
if region_end_a == -1:
    region_end_a = len(raw_a)
needle_shard = ('     "status": "ready",' + eol
                + '     "owner": "bm-a",')
hit2 = raw_a.find(needle_shard, epos_a, region_end_a)
assert hit2 != -1, "prep shard status anchor not found in entry region"
repl_shard = (
    '     "status": "done",' + eol
    + '     "done_at": "%s",' % now + eol
    + '     "harvested_by": "bm-a",' + eol
    + '     "owner": "bm-a",')
raw_b = raw_a[:hit2] + repl_shard + raw_a[hit2 + len(needle_shard):]

# STEP A post-checks (reparse + prep entry done both layers)
data_a = json.loads(raw_b)
prep = next(e for e in data_a["entries"]
           if e.get("id") == "PERPETUAL-N2-W15-JUDGE-PREP")
assert prep["status"] == "done" and prep["shards"][0]["status"] == "done"
assert prep["shards"][0]["owner"] == "bm-a"
assert len(data_a["entries"]) == n_before

# --- STEP B: 12-shard judge enrollment (r497 tail-marker pattern) ---
ticket = ("T-2026-09-30-133 s2 perpetual-supply N2 line (O-2026-09-30-2340 "
          "CEO standing-supply order, prereg sec.0 authorization face); "
          "judge stage per sec.9.1 FROZEN r702 bm-b freeze commit (berth "
          "545_500 ADMIT + banned gate exit 0 + runner slice-4 judge legs "
          "same commit); downstream division = MSG-2026-10-05-0100-bmb-ALL "
          "(any healthy machine); N_judge fixed by judge-prep r705 bm-a")
prereg = ("research/PERPETUAL_N2_W15_PREREG.md sec.9.1 FROZEN 2026-10-05 "
          "r702 bm-b (judge stage: judged cells = judge-prep kept 281 of "
          "screen survivors 281, collapse |corr|>=0.999 eliminated 0 "
          "(r705 bm-a live product read); face = FROZEN_CENSUS dual-leg "
          "full grid L 1253/1127/875 + D 3104/2978/2726 x windows "
          "{126,252,504} x cost {x1 V1 13.041bp, x2 CostPatch(2.0)} x "
          "regime 3-way bear/bull/chop+na + dual nulls B=2000 block=20 + "
          "P=2000 sign-flip; exit axis (3) template_default per design; "
          "D6 REG6 ew6 canon >=0.7 reject disclosed at finalize; G1'v2/"
          "G2/DSR shared lib no hand-copy; evidence_cutoff 2026-09-22; "
          "seed band 545_500..545_999 rng default_rng([545_500, cell_idx]) "
          "dual-nulls face only; r670 tiling i%12==shard sizes 24x5/23x7 "
          "union-exactly-once machine-checked; judge-finalize = ledger "
          "PERPETUAL-N2-W15-JUDGE, separate owner after all 12 done)")
ckpt_note = ("results/n2_w15/checkpoint/n2_w15_judge_shard_%dof12.jsonl "
             "(append-per-cell kill-safe resume, full judged payload "
             "done-set law = _judge_scan_done cell_id+legs+legL_daily_"
             "returns non-empty payload)")


def ser(e):
    # r485 law: line joins use the DETECTED host EOL (CRLF here) --
    # LF joins create a mixed-EOL block that churns at the next settle.
    t = json.dumps(e, indent=1, ensure_ascii=False)
    return eol.join(["  " + ln for ln in t.split("\n")])


entries_new = []
for i in range(12):
    entries_new.append({
        "id": f"PERPETUAL-N2-W15-JUDGE-SHARD-{i}",
        "ticket_ref": ticket,
        "prereg_ref": prereg,
        "runner": "scripts/perpetual_faces_n2.py",
        "runner_args": ["judge", "--shard", str(i), "--shards", "12"],
        "lane_owner": None,
        "priority": 1,
        "status": "ready",
        "entered_at": now_iso,
        "workers_plan": {
            "workers": 8,
            "priority": "BelowNormal",
            "note": ("per-cell judged burn = dual-leg {L,D} x windows "
                     "{126,252,504} x cost {x1,x2} full-grid replay + "
                     "dual nulls B=2000/P=2000 (seed 545_500 "
                     "cell-anchored) -- heaviest per-cell weight in N2 "
                     "lineage (~4-6x screen cell per W13 judge "
                     "precedent); ~%d cells this shard; ProcessPool "
                     "state-shared initializer; in-runner RAM gate "
                     "three-sample >=4GB r354 with r379/r691 bounded "
                     "in-place wait cap 2880min (trio-locked machines "
                     "wait honestly); CEO 10%% CPU reserve law = "
                     "BelowNormal" % sizes[i]),
        },
        "data_gates": ("in-runner fail-closed exit 2: (a) FREEZE-GATE "
                       "SEED_REGISTRY judge berth == 545500 (sec.9.1); "
                       "(b) RUN-GATE judge_state (N_judge 281 fixed "
                       "r705) + candidates file present; (c) RAM gate "
                       "r354 + bounded wait r379/r691; (d) census drift "
                       "fail-closed both legs (data moved under batch "
                       "= refuse); (e) post-burn missing-cells = honest "
                       "refuse NO pool claim (checkpoint retained for "
                       "resume). deps all in-repo: core48 panel + "
                       "b_layer_mask + judge_state + candidates"),
        "data_deps": ["data/daily/",
                      "data/fundamental/b_layer_mask.csv",
                      "results/n2_w15/n2_w15_candidates.json",
                      "results/n2_w15/n2_w15_judge_state.json"],
        "shards": [{
            "key": f"n2w15judge-{i}of12",
            "status": "ready",
            "checkpoint": ckpt_note % i,
            "note": ("bounds: kept cells i%%12==%d over 281 (24x5/23x7 "
                     "tiling); runner r496 three-call claim on verified "
                     "done (claim file results/pool_claims/"
                     "PERPETUAL-N2-W15-JUDGE-SHARD-%d/); done-flip duty "
                     "= burner-side settle per r244 landed-marker law + "
                     "r668 post-finalize pool recheck law" % (i, i)),
        }],
        "entered_by": "bm-a r705",
        "worker_class": "self-contained",
    })

tail_marker = eol + " ]" + eol + "}"
idx = raw_b.rfind(tail_marker)
assert idx != -1, "tail marker not found"
pre = raw_b[:idx]
assert pre.endswith(eol + "  }"), \
    "last entry close shape unexpected: %r" % pre[-10:]
insertion = "," + eol + ("," + eol).join(ser(e) for e in entries_new)
raw_c = pre + insertion + raw_b[idx:]

lines = raw_c.splitlines(True)
ua_idx = [k for k, ln in enumerate(lines)
          if ln.startswith(' "updated_at":')]
assert len(ua_idx) == 1, "updated_at line count=%d" % len(ua_idx)
lines[ua_idx[0]] = ' "updated_at": "%s",%s' % (now_iso, eol)
sn_idx = [k for k, ln in enumerate(lines)
          if ln.startswith(' "_stamp_note":')]
assert len(sn_idx) == 1, "stamp_note line count=%d" % len(sn_idx)
stamp = ("r705 bm-a N2-W15 JUDGE enrollment: +12 entries "
         "PERPETUAL-N2-W15-JUDGE-SHARD-0..11 (sec.9.1 FROZEN r702 bm-b; "
         "N_judge=281 fixed by judge-prep r705 bm-a 01:10:23 PASS; "
         "JUDGE-PREP entry+shard double done-flip same window r489 law)")
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
    assert e2["runner_args"] == ["judge", "--shard", str(i),
                                 "--shards", "12"]
    assert e2["status"] == "ready" and e2["shards"][0]["status"] == "ready"
    assert e2["shards"][0]["key"] == f"n2w15judge-{i}of12"
prep2 = next(e for e in data2["entries"]
             if e.get("id") == "PERPETUAL-N2-W15-JUDGE-PREP")
assert prep2["status"] == "done" and prep2["shards"][0]["status"] == "done"
diff = list(difflib.unified_diff(raw.splitlines(), new_raw.splitlines(),
                                 lineterm="", n=0))
added = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
removed = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
assert removed == 4, "expected 4 replaced lines (2 top-level + 2 status), got %d" % removed

with open(POOL, "w", encoding="utf-8", newline="") as f:
    f.write(new_raw)
data3 = json.loads(open(POOL, encoding="utf-8", newline="").read())
assert len(data3["entries"]) == n_before + 12

ev = {
    "round": "r705 bm-a", "ts": now_iso,
    "berth": SEED_REGISTRY.get("perpetual_n2_w15_judge"),
    "n_judge_cells": n_cells, "eliminated": len(elim), "sizes": sizes,
    "pool_entries_before": n_before,
    "pool_entries_after": n_before + 12,
    "prep_flip": "entry+shard double done (r489 law)",
    "new_ids": new_ids,
    "diff_added_lines": added, "diff_removed_lines": removed,
    "eol_detected": repr(eol),
    "prereg": "research/PERPETUAL_N2_W15_PREREG.md sec.9.1 FROZEN r702 bm-b",
    "division_msg": "fleet/inbox/MSG-2026-10-05-0100-bmb-ALL.md",
}
with open(EVID, "w", encoding="utf-8") as f:
    json.dump(ev, f, ensure_ascii=False, indent=1)
print("ENROLL OK: JUDGE-PREP double-flip done +12 "
      "PERPETUAL-N2-W15-JUDGE-SHARD-0..11, pool %d->%d, added=%d "
      "removed=%d, sizes=%s, eol=%r"
      % (n_before, n_before + 12, added, removed, sizes, eol))
