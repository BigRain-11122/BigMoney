"""r694 bm-a: PERPETUAL-N2-W15-GENERATE pool enrollment per
research/PERPETUAL_N2_W15_PREREG.md FROZEN (bm-c r492 commit 1ff613cbe).
Supply-materialization step 1 (MSG-1955 downstream open face; seat MSG
2026-10-04-1943 bm-a). Raw-text surgical insert per r678 law (json
round-trip of runnable_pool.json is NOT byte-stable). Anti-double-enroll
gate. Single entry, single shard generate-0of1 (W2/W13 generate precedent:
autofill burn + next-round harvest flip per r244 landed-marker law).
Evidence -> results/_r694bma_n2_gen_enroll.json."""
import datetime
import difflib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
EVID = os.path.join(ROOT, "results", "_r694bma_n2_gen_enroll.json")

now_dt = datetime.datetime.now().astimezone()
now = now_dt.strftime("%Y-%m-%d %H:%M:%S")
now_iso = now_dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# --- freeze-state facts (live reads, zero hand-copy) ---
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from science_gates import SEED_REGISTRY  # noqa: E402

bands = {k: SEED_REGISTRY.get(k) for k in
         ("perpetual_n2_w15_gen", "perpetual_n2_w15_scrnull",
          "perpetual_n2_w15_unc")}
assert bands["perpetual_n2_w15_gen"] == 541500, bands
assert bands["perpetual_n2_w15_scrnull"] == 542000, bands
assert bands["perpetual_n2_w15_unc"] == 542500, bands
cand_path = os.path.join(ROOT, "results", "n2_w15", "n2_w15_candidates.json")
assert not os.path.exists(cand_path), \
    "candidates file already present -- one-shot gate would refuse; ABORT"

# --- pool state + anti-double-enroll gate ---
raw = open(POOL, encoding="utf-8", newline="").read()
data = json.loads(raw)
entries = data["entries"]
n_before = len(entries)
assert not any(str(e.get("id", "")) == "PERPETUAL-N2-W15-GENERATE"
               for e in entries), "N2-GENERATE already enrolled (anti-double gate)"
try:
    rt = json.dumps(data, indent=1, ensure_ascii=False)
    roundtrip_stable = (rt + ("\n" if raw.endswith("\n") else "")) == raw
except Exception:
    roundtrip_stable = False

ticket = ("T-2026-09-30-133 s2 perpetual-supply N2 line (O-2026-09-30-2340 CEO "
          "standing-supply order, no new signature needed per prereg sec.0; "
          "prereg FROZEN bm-c r492 commit 1ff613cbe with forced berth skip "
          "disclosure 541500/542000/542500 per r682 horizon gate; runner five-legs "
          "bm-a r692 selftest 17/17 + FREEZE-GATE rc2 proof; supply-materialization "
          "seat claimed per MSG-2026-10-04-1955 downstream open face, F-04 first "
          "MSG-2026-10-04-1943)")
prereg = ("research/PERPETUAL_N2_W15_PREREG.md FROZEN r492 commit 1ff613cbe "
          "(sec.3 raw 5000 = A500/B4500 random-subspace draws, 18-tuple grammar "
          "W1-W14 frozen library hermetic sha-pinned; tl14 28-source exclusion "
          "real-read 7,896 rows; T-84s3 fingerprint dedup on effective signal face; "
          "seeds perpetual_n2_w15_gen/scrnull/unc=541500/542000/542500 R250 "
          "registered; evidence_cutoff 2026-09-22 sec.2; zero engine cells in "
          "generate stage)")

entry = {
    "id": "PERPETUAL-N2-W15-GENERATE",
    "ticket_ref": ticket,
    "prereg_ref": prereg,
    "runner": "scripts/perpetual_faces_n2.py",
    "runner_args": ["generate"],
    "lane_owner": None,
    "priority": 1,
    "status": "ready",
    "entered_at": now_iso,
    "workers_plan": {
        "workers": 1,
        "priority": "BelowNormal",
        "note": ("LIGHT minutes-scale single-process (W2 generate precedent 635.4s "
                 "raw 5000 bm-c r138; N2 face = subspace draws + exclusion "
                 "real-read + fingerprint dedup, zero engine cells burned); "
                 "per-candidate masks dropped after use (W2 RAM law); peak "
                 "~1.5-2GB; in-runner RAM gate three-sample >=4GB r354 built-in "
                 "(honest refuse rc2 -> pool retry when RAM frees) = protection "
                 "layer, ready status safe; 58GB free at enrollment three-sample"),
    },
    "data_gates": ("in-runner fail-closed exit 2: (a) FREEZE-GATE: SEED_REGISTRY "
                   "trio == 541500/542000/542500 else refuse; (b) one-shot: "
                   "results/n2_w15/n2_w15_candidates.json exists -> refuse "
                   "(same-grammar rerun ban TRIAL_LABOR_LAW sec.4); (c) free RAM "
                   "three-sample < 4GB after 40s bounded wait -> honest refuse "
                   "(r354 law). deps all in-repo: core48 panel data/daily/ + "
                   "b_layer_mask data/fundamental/ + hermetic grammar "
                   "tl14.build_grammar_w14 sha-pinned FROZEN_GRAMMAR_SHA16"),
    "data_deps": ["data/daily/", "data/fundamental/b_layer_mask.csv"],
    "shards": [{
        "key": "generate-0of1",
        "status": "ready",
        "checkpoint": ("results/n2_w15/n2_w15_candidates.json (single-shot "
                       "product = completion marker; refuse-if-exists guard)"),
        "note": ("one-shot generate, zero engine cells; done-flip duty = "
                 "burner-side session next round per r244 landed-marker law "
                 "(W2 r138 harvest precedent); downstream after harvest = "
                 "screen-prep in-round + 12-shard SCREEN enrollment (bounds "
                 "from actual candidates rows, r670 tiling + r481 recipe)"),
    }],
    "entered_by": "bm-a r694",
    "worker_class": "self-contained",
}

# --- raw-text surgical insert (r678 law) ---
tail_probe = raw[-200:]
eol = "\r\n" if "\r\n" in tail_probe else "\n"
tail_marker = eol + " ]" + eol + "}"
idx = raw.rfind(tail_marker)
assert idx != -1, "tail marker not found"
pre = raw[:idx]
assert pre.endswith(eol + "  }"), "last entry close shape unexpected: %r" % pre[-10:]


def ser(e):
    t = json.dumps(e, indent=1, ensure_ascii=False)
    return "  " + "\n  ".join(t.split("\n"))


insertion = "," + eol + ser(entry)
new_raw = pre + insertion + raw[idx:]

# top-level bookkeeping lines (updated_at + _stamp_note) -- line surgery on
# keepends lines (CRLF-safe per r481: 1-space line head unique)
lines = new_raw.splitlines(True)
ua_idx = [k for k, ln in enumerate(lines)
          if ln.startswith(' "updated_at":')]
assert len(ua_idx) == 1, "updated_at line count=%d" % len(ua_idx)
lines[ua_idx[0]] = ' "updated_at": "%s",%s' % (now_iso, eol)
sn_idx = [k for k, ln in enumerate(lines)
          if ln.startswith(' "_stamp_note":')]
assert len(sn_idx) == 1, "stamp_note line count=%d" % len(sn_idx)
stamp = ("r694 bm-a N2-W15 GENERATE enrollment: +1 entry "
         "PERPETUAL-N2-W15-GENERATE (supply materialization step 1; "
         "prereg FROZEN 1ff613cbe; bands 541500/542000/542500; "
         "one-shot generate, autofill burn + next-round harvest)")
stamp_json = json.dumps(stamp, ensure_ascii=False)
lines[sn_idx[0]] = ' "_stamp_note": %s,%s' % (stamp_json, eol)
new_raw = "".join(lines)

# --- post-surgery assertions ---
data2 = json.loads(new_raw)
ids2 = [str(e.get("id", "")) for e in data2["entries"]]
assert len(ids2) == n_before + 1, len(ids2)
e2 = next(x for x in data2["entries"]
          if x.get("id") == "PERPETUAL-N2-W15-GENERATE")
assert e2["runner_args"] == ["generate"]
assert e2["status"] == "ready" and e2["shards"][0]["status"] == "ready"
assert e2["worker_class"] == "self-contained" and e2["lane_owner"] is None
old_ids = [str(e.get("id", "")) for e in entries]
assert all(ids2.count(i) == 1 for i in old_ids), "old entry lost/duplicated"
diff = list(difflib.unified_diff(raw.splitlines(), new_raw.splitlines(),
                                 lineterm="", n=0))
added = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
removed = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
assert removed == 2, "expected exactly 2 replaced top-level lines, got %d" % removed

with open(POOL, "w", encoding="utf-8", newline="") as f:
    f.write(new_raw)
data3 = json.loads(open(POOL, encoding="utf-8").read())
assert len(data3["entries"]) == n_before + 1

ev = {
    "round": "r694 bm-a",
    "ts": now_iso,
    "bands": bands,
    "candidates_absent": True,
    "pool_entries_before": n_before,
    "pool_entries_after": n_before + 1,
    "new_id": "PERPETUAL-N2-W15-GENERATE",
    "roundtrip_stable": roundtrip_stable,
    "diff_added_lines": added, "diff_removed_lines": removed,
    "eol_detected": repr(eol),
    "prereg": "research/PERPETUAL_N2_W15_PREREG.md FROZEN r492 1ff613cbe",
    "seat_msg": "fleet/inbox/MSG-2026-10-04-1943-bma-all.md",
}
with open(EVID, "w", encoding="utf-8") as f:
    json.dump(ev, f, ensure_ascii=False, indent=1)
print("ENROLL OK: +1 PERPETUAL-N2-W15-GENERATE, pool %d->%d, "
      "added=%d removed=%d, bands=%s, candidates_absent=True"
      % (n_before, n_before + 1, added, removed, bands))
