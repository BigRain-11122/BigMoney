"""r485 bm-c: W3 judge 4-shard pool enrollment per MASS_TRIAL_W3_PREREG.md
sec.9.1 (FROZEN r484 commit 2b41a3958). Adoption of judge-prep artifact
w3_judge_state.json (committed r485 150f36fb4, prep PASS 1028s detached).
Raw-text surgical per r678 law (pool json round-trip NOT byte-stable ->
tail-marker insert + line surgery + reparse/difflib assertions), mirroring
the proven r481 screen-enrollment pattern. Facts derive from committed
products (zero hand-copy). Anti-double-enroll gate. Serial-position gate:
all judge-family entries done at enroll time. Evidence ->
results/_r485bmc_w3_judge_enroll.json."""
import datetime
import difflib
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
EVID = os.path.join(ROOT, "results", "_r485bmc_w3_judge_enroll.json")
MT = os.path.join(ROOT, "results", "mass_trial")

now_dt = datetime.datetime.now().astimezone()
now = now_dt.strftime("%Y-%m-%d %H:%M:%S")
now_iso = now_dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# --- facts from committed prep artifact (authoritative, zero hand-copy) ---
state = json.load(open(os.path.join(MT, "w3_judge_state.json"), encoding="utf-8"))
assert state["batch"] == "MASS_TRIAL_W3_JUDGE"
assert state["wave"] == 3 and state["seed_judge"] == 20285600
kept = state["collapse"]["kept"]
n_judge = len(kept)
elim = state["collapse"]["eliminated"]
n_clusters = len(state["collapse"]["clusters"])
n_surv = state["n_stage1_survivors"]
assert n_judge == state["n_judge_cells"] == 777, n_judge
assert n_surv == 785 and len(elim) == 8, (n_surv, len(elim))
assert n_surv - len(elim) == n_judge
cand_sha16 = hashlib.sha256(
    open(os.path.join(MT, "w3_candidates.json"), "rb").read()).hexdigest()[:16]
assert cand_sha16 == state["candidates_sha256_16"] == "d0fc84b31113d572", cand_sha16
cenL = state["legs"]["L"]["census"]
cenD = state["legs"]["D"]["census"]
assert (cenL["6m"], cenL["12m"], cenL["24m"]) == (1253, 1127, 875)
assert (cenD["6m"], cenD["12m"], cenD["24m"]) == (3104, 2978, 2726)

# --- shard cell counts: i%4 routing over sorted kept (runner law) ---
NSH = 4
counts = [sum(1 for i in range(n_judge) if i % NSH == s) for s in range(NSH)]
assert counts == [195, 194, 194, 194] and sum(counts) == n_judge, counts

# --- pool state + gates ---
raw = open(POOL, encoding="utf-8", newline="").read()
data = json.loads(raw)
entries = data["entries"]
n_before = len(entries)
assert not any(str(e.get("id", "")).startswith("MASS-TRIAL-W3-JUDGE")
               for e in entries), "W3-JUDGE already enrolled (anti-double gate)"
judge_fam = [e for e in entries if "JUDGE" in str(e.get("id", ""))]
not_done = [e["id"] for e in judge_fam if e.get("status") != "done"]
assert not not_done, "serial-position gate: judge-family not done: %s" % not_done

ticket = ("T-2026-10-03-158 s3 full-judgment batch (O-20261002-2115 sec.1 line-3 CEO order "
          "wave-3 + O-2026-09-27-2250 standing law; ticket claimed bm-c r422; s3 judge face "
          "FROZEN bm-c r484 commit 2b41a3958 prereg sec.9.1 R99 freeze-before-burn; "
          "judge-prep landed N_judge=777 same round detached 1028s, manifest PASS; prep "
          "artifact adopted+committed r485 150f36fb4 this enrollment window)")
prereg = ("research/MASS_TRIAL_W3_PREREG.md sec.9.1 FROZEN 2026-10-04 r484 commit 2b41a3958 "
          "(%d stage-1 survivors -> |corr|>=0.999 leg-L collapse %d clusters (%d eliminated) "
          "-> N_judge=%d; candidates sha16 %s; grid = p5c FROZEN_CENSUS dual-leg L %d/%d/%d + "
          "D %d/%d/%d x windows {126,252,504} x cost {x1, x2=CostPatch(2.0)} x regime segs "
          "bear/bull/chop+na x dual nulls B=2000/P=2000 seed [20285600,i]; G1v2/G2 via "
          "science_gates shared lib; family PBO CSCV 11 modules; seed mass_trial_w3_judge="
          "20285600 registered r484 R250 one-step; N_eff cross-wave ledger-head read never "
          "reset; E[FP]=0.05*N_judge)"
          % (n_surv, n_clusters, len(elim), n_judge, cand_sha16,
             cenL["6m"], cenL["12m"], cenL["24m"],
             cenD["6m"], cenD["12m"], cenD["24m"]))

new_entries = []
for s in range(NSH):
    new_entries.append({
        "id": "MASS-TRIAL-W3-JUDGE-SHARD-%d" % s,
        "host_gates": [{
            "kind": "dir_nonempty",
            "path": "Money02/data/cache/t18_deep_panel/ohlcv",
            "pattern": "*.parquet",
        }],
        "ticket_ref": ticket,
        "prereg_ref": prereg,
        "runner": "scripts/mass_trial_w1.py",
        "runner_args": ["judge", "--wave", "3",
                        "--shard", str(s), "--shards", str(NSH)],
        "lane_owner": None,
        "priority": 1,
        "status": "ready",
        "entered_at": now_iso,
        "workers_plan": {
            "workers": ("worker_cap() pool BelowNormal (prereg sec.9.1 workers <= "
                        "floor(cores*0.8) + O-1136 CPU 10%% reserve law; 32-core box)"),
            "priority": "BelowNormal",
            "note": ("~%d judged cells/shard (%d/%d = %s) x ~10s/cell w1-real-fire "
                     "measured (dual-leg dual-cost full curves + sliced window grids + "
                     "dual nulls) -> ~%.0fmin serial/shard, ~3-8min at worker_cap() "
                     "workers; worker RAM ~500-700MB (ctx_L+ctx_D panels); NO waiting "
                     "gate -- prep artifact committed (r485 150f36fb4), claim-time host "
                     "gate = t18 deep cache 48 parquets (prep verified locally 1028s "
                     "PASS r484); runner lacks worker-side pool_claims handshake (w1 "
                     "r351 precedent, zero-touch frozen face) -- done-flip duty = "
                     "burner-side session adopts checkpoint rows (%d cells total) and "
                     "lands shard+entry done per r488/r489 two-layer law; idempotent "
                     "resume (done-set cell_id skip) makes stale-owner takeover safe; "
                     "deterministic runner = duplicate rows byte-identical, finalize "
                     "dedups by cell_id"
                     % (counts[s], n_judge, NSH, "/".join(str(c) for c in counts),
                        counts[s] * 10.0 / 60.0, n_judge)),
        },
        "data_gates": ("in-runner fail-closed exit 2: w3_judge_state.json required "
                       "(committed r485 150f36fb4), candidates sha anchor %s, dual-leg "
                       "census == p5c FROZEN_CENSUS abort, t18 deep manifest PASS, "
                       "per-cell jsonl checkpoint cross-kill resume; finalize single-shot "
                       "ledger guard + MASS_TRIAL_W3_JUDGE_REFINALIZE byte-stable redo "
                       "override (w1 r259 pattern); 48h CEO report clock starts at "
                       "judge-finalize" % cand_sha16),
        "data_deps": ["results/mass_trial/w3_judge_state.json",
                      "results/mass_trial/w3_candidates.json",
                      "Money02/data/cache/t18_deep_panel/ohlcv",
                      "data/daily/"],
        "shards": [{
            "key": "w3-judge-%dof%d" % (s, NSH),
            "status": "ready",
            "checkpoint": ("results/mass_trial/w3_judge_shard_%dof%d.jsonl "
                           "(row-level cell_id done-set resume)" % (s, NSH)),
            "note": ("cells i%%%d==%d of sorted %d collapsed survivors (%d cells); "
                      "multi-machine shard-claim legal (ticket lock holds science face "
                      "only); stale-owner takeover >20min per fleet law; wave-level "
                      "finalize = separate round work (judge-finalize --wave 3 after "
                      "all %d shards done + %d-cell completeness probe)"
                      % (NSH, s, n_judge, counts[s], NSH, n_judge)),
        }],
        "entered_by": "bm-c r485",
        "worker_class": "self-contained",
    })

# --- raw-text surgical insert (r678 law, r481 proven pattern) ---
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


insertion = "," + eol + (("," + eol).join(ser(e) for e in new_entries))
new_raw = pre + insertion + raw[idx:]

# top-level bookkeeping lines (updated_at + _stamp_note) -- line surgery
lines = new_raw.splitlines(True)
ua_idx = [k for k, ln in enumerate(lines) if ln.startswith(' "updated_at":')]
assert len(ua_idx) == 1, "updated_at line count=%d" % len(ua_idx)
lines[ua_idx[0]] = ' "updated_at": "%s",%s' % (now_iso, eol)
sn_idx = [k for k, ln in enumerate(lines) if ln.startswith(' "_stamp_note":')]
assert len(sn_idx) == 1, "stamp_note line count=%d" % len(sn_idx)
stamp = ('r485 bm-c W3 judge enrollment: +4 entries MASS-TRIAL-W3-JUDGE-SHARD-0..3 '
         '(N_judge 777 = 785 survivors - 8 collapsed via 6 clusters |corr|>=0.999; '
         'cells/shard %s i%%4 routing; seed 20285600; prereg sec.9.1 frozen 2b41a3958; '
         'prep artifact adopted 150f36fb4)'
         % "/".join(str(c) for c in counts))
stamp_json = json.dumps(stamp, ensure_ascii=False)
lines[sn_idx[0]] = ' "_stamp_note": %s,%s' % (stamp_json, eol)
new_raw = "".join(lines)

# --- post-surgery assertions ---
data2 = json.loads(new_raw)
ids2 = [str(e.get("id", "")) for e in data2["entries"]]
assert len(ids2) == n_before + 4, len(ids2)
for s in range(NSH):
    e = next(x for x in data2["entries"]
             if x.get("id") == "MASS-TRIAL-W3-JUDGE-SHARD-%d" % s)
    assert e["runner_args"] == ["judge", "--wave", "3",
                                "--shard", str(s), "--shards", str(NSH)]
    assert e["status"] == "ready" and e["shards"][0]["status"] == "ready"
    assert e["worker_class"] == "self-contained" and e["lane_owner"] is None
    assert e["host_gates"][0]["path"] == "Money02/data/cache/t18_deep_panel/ohlcv"
old_ids = [str(e.get("id", "")) for e in entries]
assert all(ids2.count(i) == 1 for i in old_ids), "old entry lost/duplicated"
assert all(ids2.count(i) == 1 for i in ids2), "new entry duplicated"
diff = list(difflib.unified_diff(raw.splitlines(), new_raw.splitlines(),
                                 lineterm="", n=0))
added = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
removed = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
assert removed == 2, "expected exactly 2 replaced top-level lines, got %d" % removed
assert added > 100, "suspiciously small insertion: %d lines" % added

with open(POOL, "w", encoding="utf-8", newline="") as f:
    f.write(new_raw)
data3 = json.loads(open(POOL, encoding="utf-8").read())
assert len(data3["entries"]) == n_before + 4

ev = {
    "round": "r485 bm-c",
    "ts": now_iso,
    "n_survivors": n_surv, "n_judge": n_judge,
    "n_eliminated": len(elim), "n_clusters": n_clusters,
    "eliminated": elim,
    "shard_counts": counts,
    "candidates_sha256_16": cand_sha16,
    "seed_judge": state["seed_judge"],
    "census_L": cenL, "census_D": cenD,
    "pool_entries_before": n_before, "pool_entries_after": n_before + 4,
    "new_ids": ["MASS-TRIAL-W3-JUDGE-SHARD-%d" % s for s in range(NSH)],
    "serial_position_gate": "all judge-family done at enroll",
    "diff_added_lines": added, "diff_removed_lines": removed,
    "eol_detected": repr(eol),
    "prep_artifact_commit": "150f36fb4",
    "prereg": "research/MASS_TRIAL_W3_PREREG.md sec.9.1 frozen r484 2b41a3958",
    "refinalize_env": "MASS_TRIAL_W3_JUDGE_REFINALIZE",
}
with open(EVID, "w", encoding="utf-8") as f:
    json.dump(ev, f, ensure_ascii=False, indent=1)
print("ENROLL OK: +4 W3-JUDGE shards, N_judge=%d (785-%d via %d clusters), "
      "cells/shard=%s, pool %d->%d, added=%d removed=%d"
      % (n_judge, len(elim), n_clusters, counts, n_before, n_before + 4,
         added, removed))
