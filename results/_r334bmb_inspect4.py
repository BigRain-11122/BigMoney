# -*- coding: utf-8 -*-
"""r334 bm-b ad-hoc: inspect 4-file conflict sides + my original CODELY additions."""
import json, subprocess


def show(stage, path):
    return subprocess.run(["git", "show", f"{stage}:{path}"],
                          capture_output=True).stdout


# my r333 session's genuine CODELY.md additions (original chain parent -> dcaa14ff)
diff = subprocess.run(
    ["git", "diff", "dcaa14ff^", "dcaa14ff", "--", "CODELY.md"],
    capture_output=True).stdout.decode("utf-8")
added = [l[1:] for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
print("MY r333 added lines (dcaa14ff diff):", len(added))
for l in added:
    print("  +", l[:150])

o = show(":2", "CODELY.md").decode("utf-8")
t = show(":3", "CODELY.md").decode("utf-8")
print("\nCODELY ours(:2) bytes:", len(o.encode()), "theirs(:3) bytes:", len(t.encode()))
print("ours head:", o[:400].replace("\n", "\\n"))
print("\nours contains my r333 marker:",
      "r333 bm-b" in o, "| theirs contains:", "r333 bm-b" in t)
print("ours sections:", [s for s in o.splitlines() if s.startswith("###")])

for p in ("results/compute_audit.json", "results/lhb_update_status.json"):
    jo = json.loads(show(":2", p))
    jt = json.loads(show(":3", p))
    print(f"\n{p}: ours ts-ish={json.dumps({k: jo.get(k) for k in list(jo)[:4]}, ensure_ascii=False)[:200]}")
    print(f"{p}: theirs ts-ish={json.dumps({k: jt.get(k) for k in list(jt)[:4]}, ensure_ascii=False)[:200]}")
    if "history" in jo or "history" in jt:
        print(f"  history ours={len(jo.get('history', []))} theirs={len(jt.get('history', []))}")

for stage, tag in ((":2", "ours"), (":3", "theirs")):
    x = show(stage, "results/x2_watch_log.jsonl").decode("utf-8").splitlines()
    print(f"\nx2_watch {tag}: n={len(x)} last2={x[-2:]}")
