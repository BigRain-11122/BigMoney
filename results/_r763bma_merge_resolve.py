# -*- coding: utf-8 -*-
"""r763 bm-a merge resolver: 18 regen-twin UU faces canonical resolve
(r758/r766 law): JSON regen twins = ts-newer-wins (deep ts field scan,
both forms T-sep + space-sep normalized per r756 law); append-only
jsonl (x2_watch_log.jsonl) = union dedupe + ts stable sort (r758 law).
Writes receipt results/_r763bma_merge_resolve.json."""
import json
import subprocess
import sys
from datetime import datetime

FILES_JSON = [
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/update_status.json",
]
X2_LOG = "results/x2_watch_log.jsonl"
TS_KEYS = ["ts", "generated", "updated", "generated_at", "asof",
           "last_updated", "timestamp", "cutoff"]


def git_show(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", errors="replace")


def norm_ts(s):
    if not isinstance(s, str):
        return None
    t = s.strip().replace(" ", "T")
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S",
               "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(t, fmt)
        except ValueError:
            continue
    return None


def deep_ts(obj, depth=0):
    best = None
    if depth > 4:
        return None
    if isinstance(obj, dict):
        for k in obj:
            if isinstance(k, str) and k.lower() in TS_KEYS:
                v = norm_ts(obj[k])
                if v and (best is None or v > best):
                    best = v
        for v in obj.values():
            t = deep_ts(v, depth + 1)
            if t and (best is None or t > best):
                best = t
    elif isinstance(obj, list):
        for v in obj:
            t = deep_ts(v, depth + 1)
            if t and (best is None or t > best):
                best = t
    return best


receipt = {"json_ts_newer_wins": {}, "x2_union": {}}
for f in FILES_JSON:
    ours = git_show(":2:" + f.replace("/", "\\").replace("\\", "/"), f)
    theirs = git_show(":3:" + f, f)
    to, tt = None, None
    try:
        to = deep_ts(json.loads(ours)) if ours else None
    except Exception:
        pass
    try:
        tt = deep_ts(json.loads(theirs)) if theirs else None
    except Exception:
        pass
    if tt is not None and (to is None or tt > to):
        side = "theirs"
    elif to is not None:
        side = "ours"
    else:
        side = "theirs"  # no parseable ts on either: origin-wins default (r758)
    subprocess.run(["git", "checkout", f"--{side}", f], check=True)
    subprocess.run(["git", "add", f], check=True)
    receipt["json_ts_newer_wins"][f] = {
        "ours_ts": str(to), "theirs_ts": str(tt), "winner": side}

# x2_watch_log.jsonl: union dedupe + ts stable sort (r758 law)
ours_lines = [l for l in (git_show(":2:" + X2_LOG, X2_LOG) or "").splitlines() if l]
theirs_lines = [l for l in (git_show(":3:" + X2_LOG, X2_LOG) or "").splitlines() if l]
rows = []
seen = set()
for line in ours_lines + theirs_lines:
    if line in seen:
        continue
    seen.add(line)
    try:
        d = json.loads(line)
        rows.append((norm_ts(d.get("ts")) or datetime.min, line))
    except Exception:
        rows.append((datetime.min, line))
rows.sort(key=lambda x: x[0])
with open(X2_LOG, "w", encoding="utf-8", newline="\n") as fh:
    for _, line in rows:
        fh.write(line + "\n")
subprocess.run(["git", "add", X2_LOG], check=True)
receipt["x2_union"] = {"ours_rows": len(ours_lines),
                       "theirs_rows": len(theirs_lines),
                       "union_rows": len(rows),
                       "dupe_dropped": len(ours_lines) + len(theirs_lines) - len(rows)}
with open("results/_r763bma_merge_resolve.json", "w", encoding="utf-8") as fh:
    json.dump(receipt, fh, ensure_ascii=False, indent=1, default=str)
subprocess.run(["git", "add", "results/_r763bma_merge_resolve.json"], check=True)
print(f"resolved {len(FILES_JSON)} json twins + x2 union "
      f"{receipt['x2_union']}")
for f, v in receipt["json_ts_newer_wins"].items():
    print(f"  {f}: {v['winner']} (ours={v['ours_ts']} theirs={v['theirs_ts']})")
