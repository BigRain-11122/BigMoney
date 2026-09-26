# r282 bm-a REV-OSC-STOCK-P1 harvest flip (r244 landed-marker law):
# results/rev_osc/p1_results.json carries the ledger block (total 189859,
# single count) + verdict faces + r282 defect disclosure -> the pool entry
# flips done. Byte-face preserved (CRLF / indent=1 / ensure_ascii=False /
# no trailing newline, probed before write; r255/r257 law family).
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
OUT = os.path.join(ROOT, "results", "rev_osc", "p1_results.json")

raw = open(POOL, "rb").read()
assert not raw.startswith(b"\xef\xbb\xbf"), "BOM face drifted"
crlf = b"\r\n" in raw
assert raw.count(b"\r\n") == raw.count(b"\n"), "mixed EOL face"
no_trailing_nl = not raw.endswith(b"\n")
pool = json.loads(raw.decode("utf-8"))

res = json.load(open(OUT, encoding="utf-8-sig"))
tl = res["trials_ledger"]
assert tl["total"] == 189859 and tl["batch_trials"] == 2014, "ledger face"
vs = res["virtual_starts"]["cells"]
assert all(0.0 <= c["beat_rate_6m"] <= 1.0 for c in vs.values()), \
    "beat face still degenerate (r282 fix not landed?)"
deep = [c["segments"]["deep_bear"]["beat_rate"] for c in vs.values()]
assert all(b > 0.4 for b in deep), "deep-bear beat degenerate"
g1 = {n: g["g1_prime_v2"]["pass_v2"] for n, g in res["gates"].items()}
assert not any(g1.values()), "verdict face drift (expected all-negative)"

hit = None
for e in pool["entries"]:
    if e["id"] == "REV-OSC-STOCK-P1":
        hit = e
assert hit is not None, "entry absent"
assert hit["status"] == "ready", f"unexpected status {hit['status']}"
assert hit["shards"][0]["key"] == "revosc-0of1"
assert hit["shards"][0]["owner"] == "bm-a", "owner face"
hit["status"] = "done"
hit["shards"][0]["status"] = "done"
hit["note"] = (
    "landed 2026-09-27 01:00-01:01 (48s wall; fill latency 29.1min vs "
    "O-2100 10min target -- claim push-reject starvation 00:30/00:40/00:50, "
    "root-fixed same round: autofill rebase-retry r282); judged-negative "
    "all 7 cells per prereg s4 (g1 line 13.5951 vs best sharpe ~0.38 x1, "
    "CI lower negative, DSR 0.012, family PBO 0.4) = slot closed + "
    "new-evidence reopen note (O-2325 s5); beat-rate face unit defect "
    "found+fixed+re-derived same round (pct percent-as-fractional, "
    "r282 disclosure block in p1_results.json; deep-bear beat 0.55-0.62 "
    "inside prereg s5 band 0.55-0.75, was 0.0 degenerate); refine "
    "variants route to REFINE_BENCH + out-of-window paper track per "
    "O-2335 (FY_BG_H10 best beat profile 0.4838); data channel: p1c "
    "cache in-place consumed, forward collector = bm-b T-87 supply lane")
pool["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

body = json.dumps(pool, ensure_ascii=False, indent=1)
if crlf:
    body = body.replace("\n", "\r\n")
data = body.encode("utf-8")
if no_trailing_nl and data.endswith(b"\n"):
    data = data[:-1]
assert not data.startswith(b"\xef\xbb\xbf")
with open(POOL + ".tmp", "wb") as fh:
    fh.write(data)
os.replace(POOL + ".tmp", POOL)

check = json.load(open(POOL, encoding="utf-8-sig"))
e2 = next(e for e in check["entries"] if e["id"] == "REV-OSC-STOCK-P1")
print("flip ok:", e2["status"], e2["shards"][0]["status"],
      "entries_done=", sum(1 for e in check["entries"]
                           if e["status"] == "done"))
