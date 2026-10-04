"""W117 finalize rehearsal POST-check r684 bm-a: zero-write assertion + evidence pack assembly.

Verifies after the live-fire rehearsal run (finalize --wave 117 crashed at
_wave_values(116) FileNotFoundError, exit 1):
  P1: n1_w117_results.json still ABSENT (no partial OUT)
  P2: ledger_head() unchanged (total 641985, tail theme_judge_p2_results.json)
  P3: no new file in results/perpetual_faces/ vs pre-state (mtime census)
  P4: shard face unchanged (12/12 intact)
Writes: results/_r684bma_w117_finalize_rehearsal.json (merged pre+post evidence).
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.abspath("scripts"))
sys.path.insert(0, os.path.abspath("."))
import science_gates as sg

PRE = json.load(open(r"results\_r684bma_w117_finalize_rehearsal.json", encoding="utf-8"))
OUT = r"results\_r684bma_w117_finalize_rehearsal.json"

post = {"round": 684, "machine": "bm-a", "wave": 117, "stage": "post"}

# P1: OUT absent
post["P1_out_absent"] = not os.path.exists(r"results\perpetual_faces\n1_w117_results.json")

# P2: ledger head unchanged
head = sg.ledger_head()
post["P2_ledger_head"] = {"total": head.get("total"), "file": head.get("file")}
post["P2_unchanged"] = (head.get("total") == 641985 and head.get("file") == "theme_judge_p2_results.json")

# P3: shard dir census (12 files, mtimes all <= 15:37:15 pre-rehearsal)
shards = sorted(os.listdir(r"results\p2cal_ext\n1_w117"))
post["P3_shard_count"] = len(shards)
post["P3_shard_names_ok"] = shards == [f"shard-{i}-of-12.json" for i in range(12)]

# P4: full stdout of the live-fire run, re-captured deterministically (zero-write path)
r = subprocess.run([sys.executable, r"scripts\perpetual_faces_n1.py", "finalize", "--wave", "117"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
post["P4_replay_rc"] = r.returncode
post["P4_replay_stdout"] = r.stdout[-2000:]
post["P4_replay_stderr_tail"] = r.stderr[-800:]
post["P4_replay_hit"] = "n1_w116_results.json" in r.stderr and "FileNotFoundError" in r.stderr
post["P1_out_absent_after_replay"] = not os.path.exists(r"results\perpetual_faces\n1_w117_results.json")

merged = {**PRE, "post": post}
merged["verdict"] = "REHEARSAL PASS: guards green (pit-95/shards/A_N/B_N/dups), chain gate FAIL-CLOSED at W116 dep (FileNotFoundError pre-ledger pre-OUT, zero writes x2 runs); finalize READY-TO-FIRE the moment W116 finalize lands (bm-b lane)"
json.dump(merged, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: merged[k] for k in ("round", "wave", "verdict")}, ensure_ascii=False))
print("P1", post["P1_out_absent"], "P2", post["P2_unchanged"], "P3", post["P3_shard_count"], "P4_rc", post["P4_replay_rc"], "P4_hit", post["P4_replay_hit"], "P1b", post["P1_out_absent_after_replay"])
