# r917 resolver 2: 4 UU faces from absorb-commit replay (e02578ec5 onto 4437368d4)
# 1. fleet/machine-health.json          -> deep max-date scan ts-newer-wins (mine 23:11 vs origin 22:36)
# 2. results/saturation_engine/face_bm-b.json  -> ts-newer-wins (daemon live face, r825 priority)
# 3. results/saturation_engine/state_bm-b.json -> ts-newer-wins (daemon live face, r825 priority)
# 4. results/saturation_engine/history_bm-b.jsonl -> append-only line-union (r756: :2:-order + :3:-only appended, count assert)
import json, subprocess, re

GIT = r"C:\Program Files\Git\cmd\git.exe"

def blob(rev):
    r = subprocess.run([GIT, "show", rev], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show {rev} rc={r.returncode}: {r.stderr[:200]}")
    if len(r.stdout) < 100:
        raise RuntimeError(f"git show {rev} returned {len(r.stdout)}B (<100) = missing stage, refusing write (r710 law)")
    return r.stdout

def scan_ts(data):
    try:
        d = json.loads(data.decode("utf-8"))
    except Exception as e:
        return None, f"JSONDecodeFail:{e}"
    for k in ("scanned_at", "ts", "timestamp", "generated_at", "updated_at", "tick_at", "now"):
        if isinstance(d, dict) and k in d:
            return d[k], None
    return None, "no-ts-key:" + ",".join(list(d.keys())[:8]) if isinstance(d, dict) else "not-dict"

def max_date(text):
    m = re.findall(r"2026-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?", text)
    return max(m) if m else None

# --- ts-newer-wins faces ---
for path in ("fleet/machine-health.json",
             "results/saturation_engine/face_bm-b.json",
             "results/saturation_engine/state_bm-b.json"):
    b2 = blob(f":2:{path}")
    b3 = blob(f":3:{path}")
    t2, e2 = scan_ts(b2)
    t3, e3 = scan_ts(b3)
    winner = ":3:"
    if t2 and t3 and str(t2) > str(t3):
        winner = ":2:"
    if t2 is None and t3 is None:
        # fallback: deep max-date scan (r967 orders_fresh pattern)
        d2, d3 = max_date(b2.decode("utf-8", "replace")), max_date(b3.decode("utf-8", "replace"))
        if d2 and d3 and d2 > d3:
            winner = ":2:"
        t2, t3 = d2, d3
    data = b3 if winner == ":3:" else b2
    with open(path, "wb") as f:
        f.write(data)
    chk = open(path, "rb").read()
    assert chk == data, "write-back mismatch"
    assert b"<<<<<<<" not in chk, "marker residue"
    json.loads(chk.decode("utf-8"))  # reparse self-verify (r609)
    print(f"{path}: base={t2 or e2} mine={t3 or e3} -> {winner} ({len(data)}B) reparse-OK")

# --- append-only jsonl line-union (r756 recipe) ---
path = "results/saturation_engine/history_bm-b.jsonl"
o = blob(f":2:{path}").decode("utf-8", "replace").splitlines()
t = blob(f":3:{path}").decode("utf-8", "replace").splitlines()
tset = set(t)
oset = set(o)
theirs_only = [ln for ln in t if ln not in oset]
res = list(o) + theirs_only  # ours-order traversal + theirs-only appended
assert len(res) == len(o) + len(theirs_only), "union count assertion failed"
for ln in res:
    if ln.strip():
        json.loads(ln)  # per-line json validity (r611 jsonl tolerance law: every line must parse)
with open(path, "wb") as f:
    f.write(("\n".join(res) + "\n").encode("utf-8"))
chk = open(path, "rb").read()
assert b"<<<<<<<" not in chk and b">>>>>>>" not in chk, "marker residue"
print(f"{path}: ours={len(o)} theirs={len(t)} theirs_only={len(theirs_only)} -> union={len(res)} lines, per-line-json-OK")
print("RESOLVE2-DONE")
