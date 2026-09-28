"""r386 bm-b stash-pop UU batch resolver (26 files, classifier GREEN 26/0).

Skill canon: bigmoney-conflict-resolve. Sides in stash-pop UU state:
  :2: (ours)   = HEAD post-rebase = upstream face (origin fresh writes)
  :3: (theirs) = stashed content = this machine's 13:40-44 S6 chain outputs
Recipes per classifier output; probes read STAGED blobs only (r100 law).

Classes:
  snapshot       -> take-new via hardened deep-ts probe (tie -> HEAD side, r140)
  rolling-ledger -> union history/launches arrays zero-loss + newest snapshot fields
  append-log     -> line-level union zero-loss
  REPORT twins   -> probe .json side once, BOTH files take that side
  js-wrapper     -> whole bytes from the SAME side as its .json twin
"""
import json
import re
import subprocess
import sys

TS_HEAD = re.compile(r"^20\d{2}-")
TOD = re.compile(r"[T ]\d{2}:\d{2}")
KEY_PREFIXES = ("generated", "updated", "asof", "lastseen", "clockread", "ts")


def git_show(spec):
    r = subprocess.run(["git", "show", spec], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def side_bytes(path, stage):
    return git_show(f":{stage}:{path}")


def deep_ts(o):
    """Hardened probe (r100/R350): key normalized (strip _- lowercase) prefix
    match on wall-clock families; value must be ts-shaped WITH time-of-day;
    date-only values never feed the max; no key-exclusion lists."""
    best = None

    def rec(x):
        nonlocal best
        if isinstance(x, dict):
            for k, v in x.items():
                nk = re.sub(r"[_\-]", "", str(k)).lower()
                if isinstance(v, str) and TS_HEAD.match(v) and TOD.search(v):
                    if any(nk.startswith(p) for p in KEY_PREFIXES):
                        if best is None or v > best:
                            best = v
                rec(v)
        elif isinstance(x, list):
            for it in x:
                rec(it)

    rec(o)
    return best


def load_side(path, stage):
    raw = side_bytes(path, stage)
    if raw is None:
        return None
    return json.loads(raw.decode("utf-8-sig"))


def canon(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True)


def resolve_snapshot(path):
    a = load_side(path, 2)   # upstream/HEAD
    b = load_side(path, 3)   # stash/mine
    if a is None and b is None:
        return "both-missing", None
    if a is None:
        return "stash-only", side_bytes(path, 3)
    if b is None:
        return "head-only", side_bytes(path, 2)
    ta, tb = deep_ts(a), deep_ts(b)
    if ta is None and tb is None:
        return "tie-nots->HEAD", side_bytes(path, 2)
    if tb is None or (ta is not None and ta >= tb):
        return f"HEAD({ta} >= {tb})", side_bytes(path, 2)
    return f"STASH({tb} > {ta})", side_bytes(path, 3)


def resolve_union_rows(path, keys):
    a = load_side(path, 2)
    b = load_side(path, 3)
    if a is None:
        return "head-only", side_bytes(path, 2) if a is None and b is None else None
    out = dict(a) if isinstance(a, dict) else a
    for k in keys:
        rows_a = (a or {}).get(k) if isinstance(a, dict) else None
        rows_b = (b or {}).get(k) if isinstance(b, dict) else None
        if rows_a is None and rows_b is None:
            continue
        seen, merged = set(), []
        for r in (rows_a or []) + (rows_b or []):
            c = canon(r)
            if c not in seen:
                seen.add(c)
                merged.append(r)
        if merged and (rows_a is not None or rows_b is not None):
            out[k] = merged
    # newest snapshot fields from the newer side
    ta, tb = deep_ts(a), deep_ts(b)
    newer = b if (ta is None or (tb is not None and tb > ta)) else a
    if isinstance(out, dict) and isinstance(newer, dict):
        for k, v in newer.items():
            if k not in keys:
                out[k] = v
    return f"union+new({ta} vs {tb})", json.dumps(out, ensure_ascii=False, indent=1).encode()


def resolve_append_log(path):
    a = (side_bytes(path, 2) or b"").decode("utf-8-sig", "replace").splitlines()
    b = (side_bytes(path, 3) or b"").decode("utf-8-sig", "replace").splitlines()
    seen, merged = set(), []
    for line in a + b:
        if line not in seen:
            seen.add(line)
            merged.append(line)
    return f"union {len(a)}+{len(b)}->{len(merged)}", ("\n".join(merged) + "\n").encode()


SNAPSHOTS = [
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-24.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/update_status.json",
]

report = []
for p in SNAPSHOTS:
    note, data = resolve_snapshot(p)
    if data is not None:
        json.loads(data.decode("utf-8-sig"))  # parse-verify before write (r185)
    with open(p, "wb") as f:
        f.write(data or b"")
    report.append((p, note))

# REPORT twins: probe json side, both take that side
note, data = resolve_snapshot("docs/daily_report/REPORT-2026-09-28.json")
with open("docs/daily_report/REPORT-2026-09-28.json", "wb") as f:
    f.write(data or b"")
side = "HEAD" if "HEAD" in note else "STASH"
for ext in ("md", "json"):
    p = f"docs/daily_report/REPORT-2026-09-28.{ext}"
    stage = 2 if "HEAD" in note else 3
    d = side_bytes(p, stage)
    with open(p, "wb") as f:
        f.write(d or b"")
report.append((f"docs/daily_report/REPORT-2026-09-28.md+json", f"twins {note} -> {side}"))

# js-wrapper: same side as its .json twin
note_js, data_js = resolve_snapshot("results/dashboard_status.json")
stage = 2 if "HEAD" in note_js else 3
with open("results/dashboard_status.js", "wb") as f:
    f.write(side_bytes("results/dashboard_status.js", stage) or b"")
report.append(("results/dashboard_status.js", f"same-side-as-json ({side})"))

# rolling ledgers
for p, keys in [("results/compute_audit.json", ("history", "launches")),
                ("results/regime_state.json", ("history", "transitions"))]:
    note, data = resolve_union_rows(p, keys)
    if data is not None:
        json.loads(data.decode("utf-8-sig"))
        with open(p, "wb") as f:
            f.write(data)
        report.append((p, note))

# append log
note, data = resolve_append_log("results/x2_watch_log.jsonl")
with open("results/x2_watch_log.jsonl", "wb") as f:
    f.write(data)
report.append(("results/x2_watch_log.jsonl", note))

for p, note in report:
    print(f"[resolved] {p}: {note}")
print(f"TOTAL {len(report)} files resolved")
