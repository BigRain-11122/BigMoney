# -*- coding: utf-8 -*-
"""r686 bm-a pool entry add: MASS-TRIAL-W3-JUDGE-SHARD-{0..3} (4 shards).

Mirror of the bm-c r481 surgical-splice pattern (_r481bmc_w3_screen_enroll.py)
per r678 law (runnable_pool.json json round-trip NOT byte-stable -> raw-text
surgical insert + updated_at/_stamp_note line surgery). Every existing entry
asserted preserved; refuses if entries already present (idempotent guard).

Entry status: ready if w3_judge_state.json already landed (W2 r424 precedent
"NO waiting gate -- prep artifact committed"), else waiting with flip deps
documented (W1-JUDGE r346 precedent).
"""
import difflib
import hashlib
import json
import os
import time

POOL = "results/runnable_pool.json"
MT = "results/mass_trial"
STATE = os.path.join(MT, "w3_judge_state.json")
EVID = "results/_r686bma_w3j_enroll.json"
NOW = time.strftime("%Y-%m-%d %H:%M:%S")
NSH = 4

raw = open(POOL, encoding="utf-8", newline="").read()
data = json.loads(raw)
entries = data["entries"]
n_before = len(entries)
assert not any(str(e.get("id", "")).startswith("MASS-TRIAL-W3-JUDGE")
               for e in entries), "W3-JUDGE already enrolled (anti-double gate)"

prep_landed = os.path.exists(STATE)
if prep_landed:
    st = json.load(open(STATE, encoding="utf-8"))
    n_judge = int(st["n_judge_cells"])
    n_surv = int(st["n_stage1_survivors"])
    n_elim = len(st["collapse"]["eliminated"])
    status = "ready"
else:
    n_judge = n_surv = n_elim = None
    status = "waiting"

sha = hashlib.sha256(open(os.path.join(MT, "w3_candidates.json"), "rb")
                     .read()).hexdigest()[:16]
assert sha == "d0fc84b31113d572", "candidates sha drift"

ticket = ("T-2026-10-03-158 W3 s3 full-judgment slice (O-20261002-2115 sec.1 "
          "thousand-trial standing line + O-20261004-1440 sec.3 supply "
          "pre-position CEO order + O-20261009 anchor sec.9; s3 judge face "
          "sec.9.1 FROZEN bm-a r686 commit fe94c9e R99 freeze-before-burn; "
          "seat MSG-2026-10-04-1655-bma-ALL; 785 stage-1 survivors -> "
          "|corr|>=0.999 leg-L collapse -> N_judge live-read at entry time)")
prereg = ("research/MASS_TRIAL_W3_PREREG.md sec.9.1 FROZEN bm-a r686 commit "
          "fe94c9e (grid = p5c FROZEN_CENSUS dual-leg L 1253/1127/875 + D "
          "3104/2978/2726 x windows {126,252,504} x cost {x1, x2=CostPatch"
          "(2.0)} x regime segs bear/bull/chop+na x dual nulls B=2000 "
          "block=20 circular + P=2000 sign-flip; seed mass_trial_w3_judge="
          "20287000 rng([20287000, cell_idx]) registered same freeze commit "
          "R250; candidates sha16 d0fc84b31113d572; N_eff cross-wave "
          "no-reset live-head; evidence_cutoff 2026-09-22 D2 lockbox)")
if prep_landed:
    data_gates = ("in-runner fail-closed exit 2: w3_judge_state.json required "
                  "(landed r686 detached prep), candidates sha anchor "
                  "d0fc84b31113d572, dual-leg census == p5c FROZEN_CENSUS "
                  "abort, t18 deep manifest PASS, per-cell jsonl checkpoint "
                  "cross-kill resume; finalize single-shot ledger guard + "
                  "MASS_TRIAL_W3_JUDGE_REFINALIZE byte-stable redo override "
                  "(w1 r259 pattern)")
else:
    data_gates = ("WAITING DEPS (flip to ready upon landing, W1-JUDGE r346 "
                  "precedent): judge-prep --wave 3 (spawned detached bm-a "
                  "r686 BelowNormal) -> w3_judge_state.json (t18 manifest "
                  "PASS + dual-leg census == FROZEN_CENSUS + collapse/kept "
                  "audit) then flip executor = any healthy machine round; "
                  "IN-RUNNER fail-closed exit 2: w3_judge_state.json "
                  "absent, candidates sha anchor d0fc84b31113d572, census "
                  "abort, t18 manifest gate; per-cell jsonl checkpoint "
                  "cross-kill resume; finalize single-shot ledger guard + "
                  "MASS_TRIAL_W3_JUDGE_REFINALIZE redo override")

def shard_note(i):
    return ("cells i%%%d==%d of sorted collapsed survivors; "
            "multi-machine shard-claim legal (ticket lock holds "
            "science face only); stale-owner takeover >20min per fleet "
            "law; wave-level finalize = separate round work "
            "(judge-finalize --wave 3 after all %d shards done + "
            "completeness probe)" % (NSH, i, NSH))

if prep_landed:
    wp_note = ("~%d judged cells/shard x ~10s/cell w1-real-fire measured "
               "(dual-leg dual-cost full curves + sliced window grids + "
               "dual nulls) -> worker_cap() pool BelowNormal; worker RAM "
               "~500-700MB (ctx_L+ctx_D panels); NO waiting gate -- prep "
               "artifact landed r686; claim-time host gate = t18 deep cache "
               "48 parquets (prep verified locally); runner lacks "
               "worker-side pool_claims handshake (w1 r351 precedent, "
               "zero-touch frozen face) -- done-flip duty = burner-side "
               "session adopts checkpoint rows and lands shard+entry done "
               "per r488/r489 two-layer law; idempotent resume (done-set "
               "cell_id skip) makes stale-owner takeover safe; "
               "deterministic runner = duplicate rows byte-identical, "
               "finalize dedups by cell_id" % max(n_judge // NSH, 1))
else:
    wp_note = ("judge-prep detached in flight on bm-a r686 (spawn 16:5x, "
               "BelowNormal); per-cell cost w1-real-fire measured ~10s/cell "
               "(dual-leg dual-cost full curves + sliced window grids + "
               "dual nulls); worker_cap() pool BelowNormal; worker RAM "
               "~500-700MB; stale-owner takeover >20min per fleet law; "
               "burn in-flight anchor <=2026-10-12 (sec.9)")

new_entries = []
for i in range(NSH):
    new_entries.append({
        "id": "MASS-TRIAL-W3-JUDGE-SHARD-%d" % i,
        "host_gates": [{"kind": "dir_nonempty",
                        "path": "Money02/data/cache/t18_deep_panel/ohlcv",
                        "pattern": "*.parquet"}],
        "ticket_ref": ticket,
        "prereg_ref": prereg,
        "runner": "scripts/mass_trial_w1.py",
        "runner_args": ["judge", "--wave", "3", "--shard", str(i),
                        "--shards", str(NSH)],
        "lane_owner": None,
        "priority": 1,
        "workers_plan": {"workers": "worker_cap() pool BelowNormal",
                         "priority": "BelowNormal", "note": wp_note},
        "data_gates": data_gates,
        "entered_at": NOW,
        "status": status,
        "worker_class": "self-contained",
        "shards": [{
            "key": "w3-judge-%dof%d" % (i, NSH),
            "status": status,
            "checkpoint": ("results/mass_trial/w3_judge_shard_%dof%d.jsonl "
                           "(row-level cell_id done-set resume)"
                           % (i, NSH)),
            "note": shard_note(i),
        }],
        "entered_by": "bm-a r686",
    })

# --- raw-text surgical insert (r678 law, r481 recipe) ---
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

lines = new_raw.splitlines(True)
ua_idx = [k for k, ln in enumerate(lines) if ln.startswith(' "updated_at":')]
assert len(ua_idx) == 1, "updated_at line count=%d" % len(ua_idx)
lines[ua_idx[0]] = ' "updated_at": "%s",%s' % (NOW, eol)
sn_idx = [k for k, ln in enumerate(lines) if ln.startswith(' "_stamp_note":')]
assert len(sn_idx) == 1, "stamp_note line count=%d" % len(sn_idx)
lines[sn_idx[0]] = (' "_stamp_note": "r686 bm-a enroll MASS-TRIAL-W3-JUDGE x4 '
                    '(%s, sec.9.1 freeze fe94c9e)",%s' % (status, eol))
new_raw = "".join(lines)

with open(POOL, "w", encoding="utf-8", newline="") as f:
    f.write(new_raw)

data3 = json.loads(open(POOL, encoding="utf-8").read())
assert len(data3["entries"]) == n_before + NSH
ids3 = [str(e.get("id", "")) for e in data3["entries"]]
old_ids = [str(e.get("id", "")) for e in entries]
assert all(ids3.count(i) == 1 for i in old_ids), "old entry lost/duplicated"
for i in range(NSH):
    e = next(x for x in data3["entries"]
             if x.get("id") == "MASS-TRIAL-W3-JUDGE-SHARD-%d" % i)
    assert e["status"] == status and e["shards"][0]["status"] == status
    assert e["runner_args"] == ["judge", "--wave", "3", "--shard", str(i),
                                "--shards", str(NSH)]

diff = list(difflib.unified_diff(raw.splitlines(), new_raw.splitlines(),
                                 lineterm="", n=0))
added = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
removed = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
assert removed == 2, "expected exactly 2 replaced top-level lines, got %d" % removed

ev = {
    "round": "r686 bm-a", "ts": NOW, "prep_landed": prep_landed,
    "status": status, "n_judge": n_judge, "n_survivors": n_surv,
    "n_collapse_eliminated": n_elim,
    "candidates_sha256_16": sha,
    "pool_entries_before": n_before, "pool_entries_after": n_before + NSH,
    "new_ids": ["MASS-TRIAL-W3-JUDGE-SHARD-%d" % i for i in range(NSH)],
    "diff_added_lines": added, "diff_removed_lines": removed,
    "eol_detected": repr(eol),
    "prereg": "research/MASS_TRIAL_W3_PREREG.md sec.9.1 frozen fe94c9e",
    "seed": "mass_trial_w3_judge=20287000 band 20287000..20287499",
}
with open(EVID, "w", encoding="utf-8") as f:
    json.dump(ev, f, ensure_ascii=False, indent=1)
print("ENROLL OK: +%d W3-JUDGE shards status=%s prep_landed=%s n_judge=%s, "
      "pool %d->%d, added=%d removed=%d"
      % (NSH, status, prep_landed, n_judge, n_before, n_before + NSH,
         added, removed))
