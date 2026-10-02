"""r565 bm-b rebase resolver (r505/r314 law): 15 UU shared faces.
- pool_core_samples.jsonl: append-only -> union of conflict region lines (dedupe, order-preserved).
- 14 regen/rewrite faces: take WALL-CLOCK NEWER side by embedded ts/generated field; fallback origin side if no ts (r505 take-new).
Prints a per-file decision table. Writes resolved content to worktree (git add done by caller).
"""
import subprocess, json, re, sys

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

def git(*args, data=None):
    r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, input=data)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} rc={r.returncode}: {r.stderr.decode('utf-8','replace')[:200]}")
    return r.stdout

UU = [
 "docs/daily_report/REPORT-2026-10-02.json",
 "docs/daily_report/REPORT-2026-10-02.md",
 "docs/live_usage/LIVE-2026-10-02.json",
 "docs/live_usage/LIVE-2026-10-02.md",
 "docs/live_usage/LIVE-latest.json",
 "docs/live_usage/LIVE-latest.md",
 "results/_attrition_guard_scan.json",
 "results/compute_audit.json",
 "results/fundamental_b_layer_filter.json",
 "results/futures_update_status.json",
 "results/lhb_update_status.json",
 "results/pool_core_samples.jsonl",
 "results/regime_state.json",
 "results/token_usage.json",
 "results/update_status.json",
]

def extract_ts(text):
    """Find newest ISO-ish timestamp or epoch in text as sortable string."""
    cands = re.findall(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[+-]\d{2}:\d{2})?", text)
    if cands:
        return max(cands)
    e = re.findall(r"\b1\d{9}\b", text)
    if e:
        return max(e)
    return ""

UNION = {"results/pool_core_samples.jsonl"}

for p in UU:
    ours = git("show", f":2:{p}").decode("utf-8", "replace")     # origin side (bm-a newest)
    theirs = git("show", f":3:{p}").decode("utf-8", "replace")  # my replayed pick2
    if p in UNION:
        o_lines = [l for l in ours.splitlines() if l.strip()]
        t_lines = [l for l in theirs.splitlines() if l.strip()]
        seen, merged = set(), []
        for l in o_lines + t_lines:
            if l not in seen:
                seen.add(l)
                merged.append(l)
        # newline handling: preserve CRLF if either side used it
        nl = "\r\n" if ("\r\n" in ours or "\r\n" in theirs) else "\n"
        out = nl.join(merged) + (nl if merged else "")
        side = f"union({len(o_lines)}+{len(t_lines)}->{len(merged)})"
    else:
        to, tt = extract_ts(ours), extract_ts(theirs)
        # newer ts wins; if mine newer -> theirs side; if origin newer or tie/no-ts -> ours (r505 take-new, origin preferred on tie)
        if tt and (not to or tt > to):
            out, side = theirs, f"take-mine(mine_ts={tt} > origin_ts={to})"
        else:
            out, side = ours, f"take-origin(origin_ts={to} >= mine_ts={tt})"
    with open(REPO + "\\" + p.replace("/", "\\"), "w", encoding="utf-8", newline="") as f:
        f.write(out)
    print(f"{p}: {side}")
print("RESOLVER_DONE")
