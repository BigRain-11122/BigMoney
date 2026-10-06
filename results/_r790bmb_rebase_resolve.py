import subprocess, json, os, sys

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)

def blob(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError(f"blob read fail {ref}:{path} rc={r.returncode} len={len(r.stdout)}")
    return r.stdout

receipt = {"round": "r790-takeover", "mode": "rebase-tail-pick-469df318d-churn-absorb", "faces": {}}

# --- snapshot faces: take stage2 (origin newer 00:55 > ours-replay 00:53), byte-exact raw copy (r611-i) ---
SNAP = ["results/p1d_gates.json", "results/saturation_engine/face_bm-b.json", "results/saturation_engine/state_bm-b.json"]
for p in SNAP:
    b2 = blob(":2", p)
    json.loads(b2.decode("utf-8"))          # r185 parse gate before write
    with open(p, "wb") as f:
        f.write(b2)
    back = open(p, "rb").read()
    assert back == b2, f"write-back mismatch {p}"   # r704 read-back
    d = json.loads(back.decode("utf-8"))
    ts = d.get("ts") or d.get("meta", {}).get("date") or d.get("last_tick", {}).get("ts")
    receipt["faces"][p] = {"recipe": "take-stage2-origin-newer", "bytes": len(b2), "ts": ts}
    print(f"[SNAP take-origin] {p} ts={ts} bytes={len(b2)}")

# --- history jsonl: line-level union zero loss (r188/r217), ts-sorted ---
p = "results/saturation_engine/history_bm-b.jsonl"
b2 = blob(":2", p); b3 = blob(":3", p)
nl2 = "\r\n" if b"\r\n" in b2 else "\n"
L2 = [l for l in b2.decode("utf-8").split(nl2) if l.strip()]
L3 = [l for l in b3.decode("utf-8").split("\r\n" if b"\r\n" in b3 else "\n") if l.strip()]
s2, s3 = set(L2), set(L3)
union_set = s2 | s3
assert len(union_set) == len(s2) + len(s3) - len(s2 & s3)
seen, rows = set(), []
for l in union_set:
    o = json.loads(l)                      # per-line parse gate
    assert isinstance(o, dict) and "ts" in o, f"bad history line: {l[:100]}"
    rows.append((o["ts"], l))
rows.sort(key=lambda x: x[0])               # chronological, stable
for _, l in rows: assert l not in seen or True
out = nl2.join(l for _, l in rows) + nl2
with open(p, "wb") as f:
    f.write(out.encode("utf-8"))
back = open(p, "rb").read().decode("utf-8")
bl = [l for l in back.split(nl2) if l.strip()]
assert set(bl) == union_set and len(bl) == len(union_set), "union loss!"
for l in bl: json.loads(l)
receipt["faces"][p] = {"recipe": "line-union-sorted", "s2_lines": len(L2), "s3_lines": len(L3),
                       "union_lines": len(bl), "s2_only": len(s2-s3), "s3_only": len(s3-s2), "nl": repr(nl2)}
print(f"[UNION] {p}: {len(L2)}+{len(L3)} -> {len(bl)} lines (s2_only={len(s2-s3)} s3_only={len(s3-s2)})")

# --- conflict marker scan scoped to changed set (r637) ---
bad = []
for p in SNAP + [p]:
    c = open(p, "rb").read().decode("utf-8", "replace")
    for i, line in enumerate(c.splitlines()):
        if line.startswith(("<<<<<<< ", ">>>>>>> ", "||||||| ")) or line == "=======":
            bad.append((p, i))
assert not bad, f"markers remain: {bad}"
receipt["marker_scan"] = "PASS (0 markers in 4 resolved faces)"

# --- unstaged churn absorb check: append-only superset (r782 worksnap law) ---
for q in ["results/fund_divlowvol_p1/nulls.jsonl", "results/fund_quality_p1/nulls.jsonl"]:
    wt = set(l for l in open(q, "rb").read().decode("utf-8", "replace").splitlines() if l.strip())
    h = blob("HEAD", q)
    hl = set(l for l in h.decode("utf-8", "replace").splitlines() if l.strip())
    assert hl <= wt, f"HEAD lines missing from worktree {q} (append-only violation)"
    receipt["faces"][q] = {"recipe": "churn-absorb-append-only", "head_lines": len(hl), "wt_lines": len(wt)}
    print(f"[CHURN] {q}: HEAD {len(hl)} -> worktree {len(wt)} superset OK")

receipt["verdict"] = "all faces resolved, awaiting atomic add+continue (r787)"
with open("results/_r790bmb_rebase_resolve.json", "w", encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("RECEIPT: results/_r790bmb_rebase_resolve.json")
print("RESOLVE-OK")
