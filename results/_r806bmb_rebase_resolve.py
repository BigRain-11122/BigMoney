"""r806 bm-b rebase resolve: 12 UU from replay of r805 (22d58d45c) onto origin ebf8ce3aa.

Recipes (bigmoney-conflict-resolve SKILL):
- 11 snapshot faces: take-ours (origin side newer by deep ts probe, see _r806bmb_conflict_probe.py output)
  - REPORT-2026-10-07.{json,md} ours 14:48:53 vs theirs 14:32:32 (twins same side, r98/r99/r100)
  - LIVE-* x4 ours 14:48:54 vs theirs 14:32:32 (all twins same side, r439bmb)
  - fundamental_b_layer_filter ours 14:47:51 vs 14:32:11 (R216)
  - futures_update_status ours 14:47:46 vs 14:31:19 (R208)
  - lhb_update_status ours 14:47:46 vs 14:31:19 (R208)
  - token_usage ours 14:48:54 vs 14:32:33 (R216)
  - _attrition_guard_scan ours 14:51:56 vs 14:34:48 (UNKNOWN->manual: per-run scan verdict snapshot, ts+files+active_loss+rc, no ledger key, regenerable evidence face)
- compute_audit.json rolling-ledger: history union zero-loss (r188/R208) + latest take-new by deep ts (r311 deep-scan; ours 14:47:30 > theirs 14:30:35)
"""
import subprocess, json, sys

TAKE_OURS = [
    "docs/daily_report/REPORT-2026-10-07.json",
    "docs/daily_report/REPORT-2026-10-07.md",
    "docs/live_usage/LIVE-2026-10-07.json",
    "docs/live_usage/LIVE-2026-10-07.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/_attrition_guard_scan.json",
]

def run(args):
    r = subprocess.run(args, capture_output=True)
    if r.returncode != 0:
        print("CMD FAIL", args, r.stderr.decode("utf-8", "replace")[:300])
        sys.exit(1)
    return r.stdout

def blob(stage, path):
    return run(["git", "show", f":{stage}:{path}"])

# 1) snapshot faces: take-ours via git checkout --ours (byte-exact from git object, no encoding risk)
for p in TAKE_OURS:
    run(["git", "checkout", "--ours", "--", p])
    print(f"take-ours: {p}")

# 2) compute_audit.json union
o_raw = blob(2, "results/compute_audit.json")
t_raw = blob(3, "results/compute_audit.json")
o = json.loads(o_raw.decode("utf-8"))
t = json.loads(t_raw.decode("utf-8"))

def row_key(r):
    return json.dumps(r, sort_keys=True, ensure_ascii=False)

o_rows = {row_key(r): r for r in o["history"]}
t_rows = {row_key(r): r for r in t["history"]}
union = dict(o_rows)
union.update(t_rows)
merged = sorted(union.values(), key=lambda r: r.get("ts", ""))
expected = len(o_rows) + len(set(t_rows) - set(o_rows))
assert len(merged) == expected, f"union count {len(merged)} != expected {expected}"

latest = o["latest"] if o["latest"].get("ts", "") >= t["latest"].get("ts", "") else t["latest"]
merged_doc = {"latest": latest, "history": merged}

# newline/encoding mirror from base blob (r223/r234 law)
crlf = b"\r\n" in o_raw[:2000]
body = json.dumps(merged_doc, ensure_ascii=False, indent=1)
if crlf:
    body = body.replace("\n", "\r\n")
tail = "\r\n" if crlf else "\n"
if not body.endswith(tail):
    body += tail
enc = "utf-8-sig" if o_raw.startswith(b"\xef\xbb\xbf") else "utf-8"
with open("results/compute_audit.json", "w", encoding=enc, newline="") as f:
    f.write(body)

# 3) parse-validation gate before add (r185 law)
json.loads(open("results/compute_audit.json", "rb").read().decode("utf-8-sig" if enc == "utf-8-sig" else "utf-8"))
print(f"compute_audit union: {len(o['history'])} ours + {len(t['history'])} theirs -> {len(merged)} rows (zero-loss assert PASS)")
print(f"compute_audit latest take-new: ts={latest.get('ts')}")
print("RESOLVE OK")
