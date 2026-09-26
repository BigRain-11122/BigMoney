"""r298 bm-b rebase step 2/2 UU resolver pair (classifier GREEN):
- results/compute_audit.json : rolling-ledger (r188/R208) -- union both history
  blobs zero row loss (|A union B|), latest snapshot take-new by ts.
- results/token_usage.json : snapshot (R216) -- take-new by generated ts
  wholesale (meter re-derives whole doc from files each round).
Parse-verify before write-back (r185 law); byte-mirror write for take-side file.
"""
import io
import json
import subprocess


def blob(stage, path):
    return subprocess.run(["git", "show", f":{stage}:{path}"],
                           capture_output=True, check=True).stdout


def cano(row):
    return json.dumps(row, ensure_ascii=False, sort_keys=True)


# ---- compute_audit.json: rolling-ledger union + latest take-new -----------
P1 = "results/compute_audit.json"
b_ours, b_theirs = blob(2, P1), blob(3, P1)
ours = json.loads(b_ours.decode("utf-8-sig"))
theirs = json.loads(b_theirs.decode("utf-8-sig"))
ho, ht = ours["history"], theirs["history"]
so, st = {cano(r) for r in ho}, {cano(r) for r in ht}
union_rows = list(ht) + [r for r in ho if cano(r) not in st]
union_rows.sort(key=lambda r: r.get("ts", ""))          # ledger = ts ascending
assert len(union_rows) == len(so | st), (len(union_rows), len(so | st))
assert all(cano(r) in (so | st) for r in union_rows), "union row not from source"
lo, lt = ours["latest"], theirs["latest"]
assert lt.get("ts", "") >= lo.get("ts", ""), (lo.get("ts"), lt.get("ts"))
merged = {"latest": lt, "history": union_rows}
indent = 1 if b_theirs[:40].count(b'\n "') or b"\n \"" in b_theirs[:200] else 2
with io.open(P1, "w", encoding="utf-8", newline="") as f:
    json.dump(merged, f, ensure_ascii=False, indent=indent)
    if b_theirs.endswith(b"}\n"):
        f.write("\n")
chk = json.load(io.open(P1, encoding="utf-8-sig"))
assert len(chk["history"]) == len(so | st)
assert chk["latest"]["ts"] == lt["ts"]
print("compute_audit: history union %d rows (ours %d + theirs %d, overlap %d), "
      "latest take-new ts=%s" % (len(union_rows), len(ho), len(ht),
                                 len(so & st), lt["ts"]))

# ---- token_usage.json: snapshot take-new wholesale --------------------------
P2 = "results/token_usage.json"
b_o2, b_t2 = blob(2, P2), blob(3, P2)
o2 = json.loads(b_o2.decode("utf-8-sig"))
t2 = json.loads(b_t2.decode("utf-8-sig"))
assert t2["generated"] >= o2["generated"], (o2["generated"], t2["generated"])
with io.open(P2, "wb") as f:
    f.write(b_t2)                                        # byte-identical take-new
chk2 = json.load(io.open(P2, encoding="utf-8-sig"))
assert chk2["generated"] == t2["generated"]
print("token_usage: snapshot take-new generated=%s (>= upstream %s)"
      % (t2["generated"], o2["generated"]))
print("RESOLVED: 2/2 conflict files written, parse-verified, zero-loss held")
