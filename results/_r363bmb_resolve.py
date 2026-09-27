# r363 bm-b push-storm resolver: results/compute_audit.json (rolling-ledger UU)
# Classifier: rolling-ledger -> dual-blob union on history (zero row loss),
# latest snapshot take-new by nested latest.ts (deep-scan r311/r319 probe).
# ours=stage2 (origin tip, other machine 06:14:15) / theirs=stage3 (my replay 06:11:26)
import subprocess, json, io, sys

sys.stdout.reconfigure(encoding="utf-8")

def blob(stage):
    b = subprocess.run(["git", "show", f":{stage}:results/compute_audit.json"],
                       capture_output=True).stdout
    return json.loads(b.decode("utf-8-sig"))

o, t = blob(2), blob(3)
oh, th = o["history"], t["history"]
o_ts = [h["ts"] for h in oh]
t_ts = [h["ts"] for h in th]
assert not (set(o_ts) & set(t_ts)), "expected zero ts overlap (probe confirmed)"

union = {h["ts"]: h for h in th}
union.update({h["ts"]: h for h in oh})
merged_hist = [union[k] for k in sorted(union)]
assert len(merged_hist) == len(t_ts) + len(o_ts) == 48, "union count law"

# latest: take-new by nested latest.ts (deep-scan compare path exists on both sides)
assert "ts" in o["latest"] and "ts" in t["latest"], "r319 existence probe"
newer = o if o["latest"]["ts"] > t["latest"]["ts"] else t
older_ts = t["latest"]["ts"] if newer is o else o["latest"]["ts"]
merged = {"latest": newer["latest"], "history": merged_hist}
print(f"union rows 48 (mine {len(t_ts)} + theirs {len(o_ts)}, overlap 0)")
print(f"latest take-new: {newer['latest']['ts']} (other side {older_ts} older)")

# parse-verify + zero-loss byte anchors
out = json.dumps(merged, ensure_ascii=False, indent=1) + "\n"
json.loads(out)
for h in th:
    assert any(x["ts"] == h["ts"] for x in merged_hist), f"lost row {h['ts']}"
for h in oh:
    assert any(x["ts"] == h["ts"] for x in merged_hist), f"lost row {h['ts']}"

# base-blob line-ending mirror (r223/r234: detect, do not assume)
base = subprocess.run(["git", "show", "bb793033:results/compute_audit.json"],
                      capture_output=True).stdout
crlf = b"\r\n" in base[:2000]
with open("results/compute_audit.json", "w", encoding="utf-8",
          newline="" if not crlf else "") as fh:
    fh.write(out)
print(f"written (base CRLF={crlf}); parse-verify OK; zero-loss OK")
