# -*- coding: utf-8 -*-
"""r472 bm-b: fill_ladder_catalog TRIAL-LABOR-W14-GENERATE entry
runner_exists flip (bm-c SLOT-5 r249 precedent): runner field gets the
BUILT annotation; stale 'pending' note replaced by the landed face.
Gates now all pass: prereg_frozen (r471) + runner_exists (this round)
+ standing_no_judge_inflight (pool zero running).  Pool entry
enqueued same window (results/_r472bmb_w14_generate_pool_entry.py,
double-file law)."""
import json

P = "Tools/fill_ladder_catalog.json"
cat = json.load(open(P, encoding="utf-8"))
es = cat if isinstance(cat, list) else cat.get(
    "entries", cat.get("waves", []))
e = [x for x in es if x.get("id") == "TRIAL-LABOR-W14-GENERATE"][0]
assert "BUILT" not in e["runner"], "already flipped"
e["runner"] = (
    "scripts/trial_labor_w14.py (BUILT r472 bm-b, selftest 53/53: "
    "W13 runner paradigm verbatim-import chain tl1-tl13 + "
    "a158_tsgate_probe RESI/CNT frozen construction + eighteen-tuple "
    "grammar 1,693,052,928 combos sha16 a231bf10940e7878 pinned + "
    "G-RESI/G-CNT fail-closed runner doors vs three-probe closure "
    "facts (r470 + r471 supplement + bm-c r277 twin 39/39) + "
    "resi/cnt stream append zero disturbance + 28-source exclusion "
    "loader + mask/engine parity vs W9 + W13 baselines + screen CSV "
    "contract resi/cnt columns; three-command identity first-runs "
    "real-data honest rc=2 [screen-prep ALL gates PASS + "
    "candidates-absent tail refusal; screen-finalize generate-pending "
    "refusal; judge-prep screen-absent refusal] per r446 surgical pit "
    "law; dead r472-session Slice-A half-work adopted wholesale "
    "zero-redo per r471 attrition law; both enqueue gates now pass -> "
    "pool-enqueued same window)")
e["note"] = (
    "runner LANDED bm-b r472 (runner build slice complete per r446 "
    "three-command law); grammar sha16 pinned at w14_grammar.json "
    "serialization time; pool entry TRIAL-LABOR-W14-GENERATE "
    "status=ready enqueued results/runnable_pool.json + lane "
    "bm-b double-file (entries=140); burn = autofill (execution-face "
    "separation O-2100, lane_owner=None any healthy machine may "
    "claim); downstream SCREEN/JUDGE pool entries land on their "
    "physical deps per W3-W13 precedent")
dump = json.dumps(cat, ensure_ascii=False, indent=1)
with open(P, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dump)
print("catalog flip OK: TRIAL-LABOR-W14-GENERATE runner_exists TRUE "
      "(runner BUILT annotation + landed note)")
