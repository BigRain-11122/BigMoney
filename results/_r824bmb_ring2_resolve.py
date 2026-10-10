# r824 bm-b ring-2 rebase resolver (rebase onto refreshed origin/main after claw block)
# Skill: bigmoney-conflict-resolve. Recipes:
#  - snapshot faces: take-ours (HEAD side ts 08:12:5x > pick side 08:04-08:05, R208/R216)
#  - rolling-ledger faces: union history rows zero-loss (r188/R208), scalars take-ours
#  - append-ledger-md queue face: union both machines' consumption records in commit-ts
#    order (r823 @08:10:21 then r947 @08:22:34, R208 law)
# Parse-verify before write (r185). No marker bytes in output. Zero-loss assertions inline.
import io, json, re, subprocess

def stage_bytes(n, p):
    return subprocess.run(["git", "show", ":%d:%s" % (n, p)], capture_output=True).stdout

def rowkey(r):
    return json.dumps(r, sort_keys=True, ensure_ascii=False)

SNAPSHOT_TAKE_OURS = [
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/update_status.json",
]
LEDGER_FACES = {
    "results/compute_audit.json": ["history"],
    "results/regime_state.json": ["triggers", "transitions", "history"],
}
receipt = {"round": "r824-ring2", "faces": {}, "law": "skill bigmoney-conflict-resolve r188/R208/R216/R208-ledger-md"}

for p in SNAPSHOT_TAKE_OURS:
    b = stage_bytes(2, p)
    assert b"<<<<<<<" not in b, "ours side has markers: " + p
    d = json.loads(b.decode("utf-8"))  # r185
    io.open(p, "wb").write(b)
    receipt["faces"][p] = {"recipe": "take-ours (ts 08:12:5x > 08:04-05)", "bytes": len(b)}

for p, keys in LEDGER_FACES.items():
    ours = json.loads(stage_bytes(2, p).decode("utf-8"))
    theirs = json.loads(stage_bytes(3, p).decode("utf-8"))
    doc = dict(ours)  # scalars = ours (newest)
    counts = {}
    for k in keys:
        seen, out = set(), []
        for src in (ours, theirs):
            for r in (src.get(k) or []):
                kk = rowkey(r)
                if kk not in seen:
                    seen.add(kk)
                    out.append(r)
        if out and all(isinstance(r, dict) and "ts" in r for r in out):
            out.sort(key=lambda r: str(r.get("ts")))
        doc[k] = out
        counts[k] = {"ours": len(ours.get(k) or []), "theirs": len(theirs.get(k) or []),
                     "union": len(out)}
        assert len(out) >= max(len(ours.get(k) or []), len(theirs.get(k) or [])), "union loss: " + k
    blob = json.dumps(doc, ensure_ascii=False, indent=1) + "\n"
    json.loads(blob)  # r185
    assert "<<<" not in blob
    io.open(p, "w", encoding="utf-8", newline="\n").write(blob)
    receipt["faces"][p] = {"recipe": "ledger union both sides, scalars take-ours", "counts": counts}

# queue md: single hunk, keep both records in commit-ts order (r823 then r947)
p = "state/queue/explore.md"
text = io.open(p, "r", encoding="utf-8", newline="").read()
lines = text.split("\n")
def find(pred, start=0):
    return next((k for k in range(start, len(lines)) if pred(lines[k])), None)
i = find(lambda l: l.rstrip("\r").startswith("<<<<<<<"))
j = find(lambda l: l.rstrip("\r") == "=======", i + 1)
m = find(lambda l: l.rstrip("\r").startswith(">>>>>>>"), j + 1)
assert None not in (i, j, m), "queue hunk not found"
pre, ours_seg, theirs_seg, post = lines[:i], lines[i+1:j], lines[j+1:m], lines[m+1:]
# ours side (HEAD) = r947 record; theirs side (pick) = r823 record
r947 = [l for l in ours_seg if l.strip()]
r823 = [l for l in theirs_seg if l.strip()]
eol = "\r\n" if any("\r" in l for l in lines[:i]) else "\n"
merged = pre + r823 + [""] + r947 + post
blob = eol.join(merged)
assert "<<<" not in blob and ">>>" not in blob
io.open(p, "w", encoding="utf-8", newline="").write(blob)
receipt["faces"][p] = {"recipe": "append-ledger-md union, r823(08:10:21) then r947(08:22:34)",
                      "kept_lines": {"r823": len(r823), "r947": len(r947)}}

with io.open("results/_r824bmb_ring2_resolve.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("resolved:", len(receipt["faces"]), "faces")
for k, v in receipt["faces"].items():
    print(" ", k, "->", v.get("recipe", ""))
