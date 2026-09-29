#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r253 bm-c rebase conflict resolution (r443/r446/r449 union-blob law).

Policy (per-side triage, evidence in _r253bmc_reconf_*.py outputs):
- 17 derived/aggregate faces: take ORIGIN (ours) -- origin carries post-r446
  company state (ledger 355083, W12 SCREEN faces); mine derived from pre-r446
  base with later wall-clock only. S6 chain this round re-derives them all.
- results/compute_audit.json: history union dedupe (entry-hash), ts-sorted;
  latest = chronologically last entry.
- CODELY.md: origin base + my r249 cold pointer (after r240 ptr) - origin's
  r249 hot entry (moved-to-archive intent) + my r252 lesson entry at tail.
- research/memory-archive/202609.md: origin + append my r252 batch section
  verbatim (bytes preserved).
"""
import json, subprocess, sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def git(*args):
    r = subprocess.run(["git"] + list(args), capture_output=True, cwd=ROOT)
    if r.returncode != 0:
        raise RuntimeError("git %s: %s" % (args[0], r.stderr.decode("utf-8", "replace")[:300]))
    return r.stdout

def blob(stage, path):
    return git("show", ":%d:%s" % (stage, path))

OURS = [
    "docs/daily_report/REPORT-2026-09-30.json",
    "docs/daily_report/REPORT-2026-09-30.md",
    "docs/live_usage/LIVE-2026-09-30.json",
    "docs/live_usage/LIVE-2026-09-30.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

for p in OURS:
    git("checkout", "--ours", "--", p)
    git("add", "--", p)
    print("OURS  %s" % p)

def unresolved(path):
    r = subprocess.run(["git", "ls-files", "-u", "--", path], capture_output=True, cwd=ROOT)
    return bool(r.stdout.strip())

# ---- compute_audit.json union ----
if unresolved("results/compute_audit.json"):
    o = json.loads(blob(2, "results/compute_audit.json").decode("utf-8"))
    t = json.loads(blob(3, "results/compute_audit.json").decode("utf-8"))
    seen, hist = set(), []
    for h in o.get("history", []) + t.get("history", []):
        k = json.dumps(h, sort_keys=True, ensure_ascii=False)
        if k in seen:
            continue
        seen.add(k)
        hist.append(h)
    hist.sort(key=lambda h: str(h.get("ts", "")))
    latest = max(o.get("latest", {}), t.get("latest", {}), key=lambda x: str(x.get("ts", "")))
    merged = {"latest": latest, "history": hist}
    with open(os.path.join(ROOT, "results/compute_audit.json"), "wb") as f:
        f.write(json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8"))
    git("add", "--", "results/compute_audit.json")
    print("UNION results/compute_audit.json history=%d latest.ts=%s" % (len(hist), latest.get("ts")))
else:
    print("SKIP  compute_audit.json already resolved")

# ---- CODELY.md semantic union (bytes-preserving) ----
if unresolved("CODELY.md"):
    ob = blob(2, "CODELY.md"); tb = blob(3, "CODELY.md")
    ol = ob.splitlines(keepends=True); tl = tb.splitlines(keepends=True)
    def dec(b):
        return b.decode("utf-8", "replace")
    def startswith_b(line, prefix):
        return dec(line).startswith(prefix)
    my_r249_ptr = [l for l in tl if startswith_b(l, "- 冷层指针：r249 pandas to_csv")]
    my_r252 = [l for l in tl if startswith_b(l, "- [2026-09-30 04:5x r252 bm-c] 泊位/冻结步开工前")]
    assert len(my_r249_ptr) == 1, "r249 ptr not found in theirs"
    assert len(my_r252) == 1, "r252 entry not found in theirs"
    out = []
    for l in ol:
        if startswith_b(l, "- [2026-09-30 03:2x r249 bm-c] pandas to_csv"):
            continue  # hot entry -> replaced by cold pointer (moved to archive verbatim)
        out.append(l)
        if startswith_b(l, "- 冷层指针：r240"):
            out.append(my_r249_ptr[0])
    out.append(my_r252[0])
    data = b"".join(out)
    if not data.endswith(b"\n"):
        data += b"\n"
    with open(os.path.join(ROOT, "CODELY.md"), "wb") as f:
        f.write(data)
    git("add", "--", "CODELY.md")
    print("MERGE CODELY.md %dB lines=%d" % (len(data), data.count(b"\n")))
else:
    print("SKIP  CODELY.md already resolved")

# ---- archive 202609.md: origin + my r252 section verbatim ----
if unresolved("research/memory-archive/202609.md"):
    ab_o = blob(2, "research/memory-archive/202609.md")
    ab_t = blob(3, "research/memory-archive/202609.md")
    marker = "## 热冷整编 2026-09-30 r252 bm-c 窗批".encode("utf-8")
    idx = ab_t.find(marker)
    assert idx >= 0, "my r252 section not found"
    my_sec = ab_t[idx:]
    merged_ab = ab_o
    if not merged_ab.endswith(b"\n"):
        merged_ab += b"\n"
    merged_ab += b"\n" + my_sec
    if not merged_ab.endswith(b"\n"):
        merged_ab += b"\n"
    with open(os.path.join(ROOT, "research/memory-archive/202609.md"), "wb") as f:
        f.write(merged_ab)
    git("add", "--", "research/memory-archive/202609.md")
    print("MERGE archive %dB (+my section %dB)" % (len(merged_ab), len(my_sec)))
else:
    print("SKIP  archive already resolved")

# ---- verify no unresolved left ----
r = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], capture_output=True, cwd=ROOT)
left = r.stdout.decode("utf-8").strip()
print("unresolved-left: %s" % (left if left else "NONE"))
