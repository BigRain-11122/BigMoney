"""r709 bm-a rebase-step2 resolver: bm-a saturation_engine faces (3 UU)

Recipe chain:
- face_bm-a.json / state_bm-a.json : snapshot class, deep-ts probe newer-wins.
  S2(origin)=03:51:04 > S3(local)=03:48:04 -> take :2: verbatim (origin side is
  this machine's own daemon self-commit push, r290 lineage; live daemon keeps writing).
- history_bm-a.jsonl : rolling-ledger 120-cap producer window (r85 law). Two windows
  are complementary (L3 lacks 01:35-01:5x old lines; L2 lacks 03:33-03:48 lines).
  Union (136) then keep newest 120 by embedded ts = zero information loss under
  producer cap semantics; oldest 16 dropped are exactly the union's oldest lines.
  Zero ts-collisions verified pre-write (r140 same-tie n/a). EOL mirror = LF.
All three faces rc0 (reproducible-artifact, treasure_guard passed).
"""
import subprocess, json, sys

def blob(rev):
    r = subprocess.run(["git", "show", rev], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"git show {rev} failed: {r.stderr[:200]!r}")
    return r.stdout

# --- snapshot faces: take :2: (newer ts, origin side) ---
for p in ["results/saturation_engine/face_bm-a.json",
          "results/saturation_engine/state_bm-a.json"]:
    s2 = blob(f":2:{p}")
    d = json.loads(s2)  # parse-verify (r185)
    open(p, "wb").write(s2)
    rb = open(p, "rb").read()
    assert rb == s2, f"readback mismatch {p}"
    print(f"[resolve:{p}] take :2: origin-side (newer ts 03:51:04), parse-verified")

# --- history: union + newest-120 cap by ts ---
p = "results/saturation_engine/history_bm-a.jsonl"
s2 = blob(f":2:{p}").decode("utf-8")
s3 = blob(f":3:{p}").decode("utf-8")
L2 = [l for l in s2.splitlines() if l.strip()]
L3 = [l for l in s3.splitlines() if l.strip()]
set2, set3 = set(L2), set(L3)
union = set2 | set3
assert len(union) == 136, f"unexpected union size {len(union)}"
def ts_of(l):
    return json.loads(l)["ts"]
# collision check (same ts diff content) pre-write
seen = {}
for l in union:
    t = ts_of(l)
    if t in seen and seen[t] != l:
        sys.exit(f"ts-collision at {t}: different content")
    seen[t] = l
out = sorted(union, key=ts_of)[-120:]  # newest 120 by ts (producer cap)
payload = ("\n".join(out) + "\n").encode("utf-8")
# assertions: newest data from BOTH sides survives
assert set(l for l in set3 - set2 if ts_of(l) >= "2026-10-05T03:00") <= set(out), "L3-newest lost"
assert set(l for l in set2 - set3 if ts_of(l) >= "2026-10-05T03:45") <= set(out), "L2-newest lost"
assert all(json.loads(l) for l in out)
with open(p, "wb") as f:
    f.write(payload)
rb = open(p, "rb").read().decode("utf-8")
rbl = [l for l in rb.splitlines() if l.strip()]
assert set(rbl) == set(out) and len(rbl) == 120, "readback mismatch"
assert "\r" not in rb, "EOL violation"
print(f"[resolve:{p}] union {len(union)} -> newest-120 cap (dropped 16 oldest), "
      f"window {ts_of(out[0])} -> {ts_of(out[-1])}, parse-verified")
