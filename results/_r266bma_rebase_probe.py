"""r266 rebase pre-probe: origin/main faces for conflict surfaces (read-only)."""
import json
import re
import subprocess


def ob(p):
    return subprocess.run(["git", "show", "origin/main:" + p], capture_output=True).stdout


t = ob("fleet/tasks/T-2026-09-26-83-P1.json").decode("utf-8")
print("origin T-83 has r266 row:", "progress_r266" in t)
print("origin T-83 has r270 row:", "progress_r270" in t)
keys = [l.split(":")[0].strip().strip('"') for l in t.splitlines() if "progress_r2" in l]
print("origin T-83 progress keys:", keys)

pr = ob("Tools/iteration_prompt.txt").decode("utf-8")
print("origin prompt has quarterly leg:", "每季首轮加跑治理法熵审视" in pr)

c = json.loads(ob("results/post_review_criteria.json").decode("utf-8-sig"))
print("origin criteria items:", len(c["items"]), "| last ids:", [e["id"] for e in c["items"]][-6:])
print("origin _reconciled tail:", c["_reconciled"][-220:])

o = json.loads(ob("results/strategy_scorecard.json").decode("utf-8"))
print("origin scorecard profile sha:", o.get("profile_cards", {}).get("prereg_sha256_16"),
      "| landing:", o.get("landing_hooks", {}).get("prereg_sha256_16"))

s = ob("scripts/strategy_scorecard.py").decode("utf-8")
print("origin has _prereg_sha16:", "_prereg_sha16" in s)
for m in re.finditer(r"def (_?[a-z0-9_]*sha[a-z0-9_]*)\(", s):
    print("origin sha helper:", m.group(1))
i = s.find("lf-normal")
print("origin mentions lf-normalize near sha:", "normalize" in s.lower() and "sha" in s)
m = re.search(r"def [a-z0-9_]*sha[a-z0-9_]*\(.*?\n(?:.*?\n){0,6}", s)
print(m.group(0)[:400] if m else "(no helper block)")
