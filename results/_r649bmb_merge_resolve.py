# -*- coding: utf-8 -*-
"""r649 bm-b merge resolver (origin/main bm-a r659/r660/r660b push-race closeout).

Canonical recipes per r642 lineage + bigmoney-conflict-resolve SKILL:
- results/compute_audit.json: rolling-ledger ts-key union (r188/R208),
  producer cap semantics [-200:]+append -> keep 201 newest, latest=newer side
  (ours 05:26:19 > theirs 05:12:43).
- results/token_usage.json: take-ours -- ours is the direct successor in the
  same append series (ours.delta_vs_prev.prev_generated == theirs.generated
  05:15:10; all append-only faces identical: crash_fuse sigs 63=63,
  refusals 1539=1539; machines dict identical except 'default' report_bytes
  ours 1728527 > theirs 1725236 = fresher read). Zero-loss take-ours.
- results/dashboard_status.js: derive snapshot take-new-by-ts
  (ours generated_at 05:28:11 > theirs 05:06:22) -> take-ours.

Post-resolve verification: every face json.loads-clean (js face DASH_DATA
json-parse); zero conflict markers in index (git grep --cached, r644 law).
"""
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


def sh(*args):
    r = subprocess.run(args, capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"FAIL {args}: {r.stderr.decode('utf-8', 'r')[:400]}")
    return r.stdout


def blob(side, path):
    r = subprocess.run(["git", "show", f":{side}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"FAIL blob {side}:{path}: "
                         f"{r.stderr.decode('utf-8', 'r')[:200]}")
    return r.stdout


# ---- phase 1: compute_audit.json rolling-ledger union (cap 201) ----
print("== phase 1: compute_audit.json rolling-ledger union (cap 201)")
p = "results/compute_audit.json"
ours, theirs = json.loads(blob(2, p)), json.loads(blob(3, p))
ha = {e["ts"]: e for e in ours["history"]}
hb = {e["ts"]: e for e in theirs["history"]}
assert len(ha) == 201, f"ours history len {len(ha)}"
assert len(hb) == 201, f"theirs history len {len(hb)}"
union = dict(ha)
union.update(hb)
keys = sorted(union)                              # ts strings sort lexically
kept = keys[-201:]                                # producer cap: newest 201
merged_hist = [union[k] for k in kept]
ours_newest = max(ha)
theirs_newest = max(hb)
assert ours_newest in kept, "our own audit entry lost"
assert theirs_newest in kept, "bm-a audit entry lost (zero-loss)"
merged = {"latest": ours["latest"], "history": merged_hist}
assert merged["latest"]["ts"] > theirs["latest"]["ts"], "latest must be newer side"
json.loads(json.dumps(merged))                     # round-trip sanity
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(merged, fh, indent=1, ensure_ascii=False)
    fh.write("\n")
sh("git", "add", "--", p)
print(f"  union ok: {len(ha)}|{len(hb)} -> {len(merged_hist)} "
      f"(dropped oldest common, kept ours {ours_newest} + theirs {theirs_newest})")

# ---- phase 2: token_usage.json take-ours (chain-suffix proof) ----
print("== phase 2: token_usage.json take-ours (successor-in-chain proof)")
p = "results/token_usage.json"
ours_b, theirs_b = blob(2, p), blob(3, p)
O, T = json.loads(ours_b), json.loads(theirs_b)
assert O["delta_vs_prev"]["prev_generated"] == T["generated"], \
    "ours not chained on theirs -- recipe premise broken"
assert O["l2_local_llm"]["crash_fuse"]["sigs"] == T["l2_local_llm"]["crash_fuse"]["sigs"], \
    "append face diverges -- take-ours unsafe"
assert O["l2_local_llm"]["crash_fuse"]["refusals"] == T["l2_local_llm"]["crash_fuse"]["refusals"]
assert O["generated"] > T["generated"]
with open(p, "wb") as fh:
    fh.write(ours_b)
sh("git", "add", "--", p)
print(f"  take-ours ok: generated {O['generated']} chained on {T['generated']}")

# ---- phase 3: dashboard_status.js take-ours (take-new-by-ts) ----
print("== phase 3: dashboard_status.js take-new-by-ts")
p = "results/dashboard_status.js"
ours_b, theirs_b = blob(2, p), blob(3, p)
o_ts = json.loads(ours_b.decode("utf-8", errors="replace")
                  .split("=", 1)[1].strip().rstrip(";"))["meta"]["generated_at"]
t_ts = json.loads(theirs_b.decode("utf-8", errors="replace")
                  .split("=", 1)[1].strip().rstrip(";"))["meta"]["generated_at"]
assert o_ts > t_ts, f"ours not newer: {o_ts} vs {t_ts}"
with open(p, "wb") as fh:
    fh.write(ours_b)
sh("git", "add", "--", p)
print(f"  take-ours ok: {o_ts} > {t_ts}")

# ---- phase 4: zero-marker + zero-UU verification (r644/r657 laws) ----
print("== phase 4: verification")
r = subprocess.run(["git", "grep", "--cached", "-l", "-E", r"^(<<<<<<<|=======$|>>>>>>>)"],
                   capture_output=True)
assert r.returncode == 1, f"conflict markers in index: {r.stdout.decode()[:300]}"
out = subprocess.run(["git", "status", "--porcelain"],
                      capture_output=True).stdout.decode("utf-8", "r")
uu = [l for l in out.splitlines() if l.startswith(("UU", "AA", "DD"))]
assert not uu, f"remaining conflicts: {uu}"
json.load(open("results/compute_audit.json", encoding="utf-8"))
json.load(open("results/token_usage.json", encoding="utf-8"))
print("RESOLVE_OK")
