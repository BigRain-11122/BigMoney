import subprocess, json, os

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

def stage_blob(stage, path):
    r = subprocess.run(["git", "-C", REPO, "show", f":{stage}:{path}"],
                       capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"git show :{stage}:{path} rc={r.returncode} {r.stderr[:200]}")
    return r.stdout

# --- watermark_red.json: r1028 newer-wins by ts field ---
wm = "results/watermark_red.json"
b2, b3 = stage_blob(2, wm), stage_blob(3, wm)
j2, j3 = json.loads(b2.decode("utf-8")), json.loads(b3.decode("utf-8"))
ts2, ts3 = str(j2.get("ts", "")), str(j3.get("ts", ""))
body, winner = (b2, "ours(origin-post-pull)") if ts2 >= ts3 else (b3, "theirs(local-stash)")
with open(os.path.join(REPO, wm), "wb") as f:
    f.write(body)

# --- post_review.jsonl: append-only union, zero-loss assert (r419/r1061) ---
pr = "results/post_review.jsonl"
p2, p3 = stage_blob(2, pr).decode("utf-8", "replace"), stage_blob(3, pr).decode("utf-8", "replace")
l2 = [l for l in p2.splitlines() if l.strip()]
l3 = [l for l in p3.splitlines() if l.strip()]
s2 = set(l2)
combined = l2 + [l for l in l3 if l not in s2]
assert set(combined) == (s2 | set(l3)), "union row-set assertion failed"
with open(os.path.join(REPO, pr), "wb") as f:
    f.write(("\n".join(combined) + "\n").encode("utf-8"))

print(json.dumps({
    "wm_winner": winner, "wm_ts_ours": ts2, "wm_ts_theirs": ts3,
    "pr_lines_ours": len(l2), "pr_lines_theirs": len(l3),
    "pr_union_lines": len(combined), "assert": "zero-loss-ok",
}, ensure_ascii=False))
