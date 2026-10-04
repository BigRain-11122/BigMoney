"""r505 bm-c rebase conflict resolver (16 UU, r501/r698 blood, r440 two-分法).
Rebase semantics: ours=origin tip, theirs=my aa0527104 patch.
Strategies:
- HQ-FEEDBACK.md: take OURS (origin canonical F-20261005-01 receipt row landed
  by bm-a r703 -> bm-b r704 adoption; my duplicate draft row yields per
  commit-time priority; yield documented in round report).
- take-side ts faces: whole-file take of the side with the newer max timestamp.
- dashboard_status.js: locked to the .json twin's verdict.
- compute_audit.json: history array union by (ts,machine) key, zero-loss.
- token_usage.json: per-key union (machines subdict merged per machine).
All resolved files written back; caller runs git add + rebase --continue.
Receipt -> results/_r505bmc_merge_resolve.json
"""
import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TS_RE = re.compile(r"2026-10-0[45][ T]\d\d:\d\d:\d\d")
CONFLICT_RE = re.compile(
    r"<<<<<<< HEAD\n(.*?)\|\|\|\|\|\|\| [^\n]*\n(.*?)=======\n(.*?)>>>>>>> [0-9a-f]+\n",
    re.S,
)

TAKE_SIDE = [
    "docs/daily_report/REPORT-2026-10-05.json",
    "docs/daily_report/REPORT-2026-10-05.md",
    "docs/live_usage/LIVE-2026-10-05.json",
    "docs/live_usage/LIVE-2026-10-05.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/update_status.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/fundamental_b_layer_filter.json",
    "results/dashboard_status.json",
]

receipt = {"round": "r505", "strategies": {}, "sides": {}}


def read(p):
    return io.open(os.path.join(ROOT, p), encoding="utf-8", errors="strict").read()


def max_ts(text):
    hits = TS_RE.findall(text)
    return max(hits) if hits else ""


def take_side(path):
    """Whole-file take: choose side by newer max timestamp inside conflict sides."""
    text = read(path)
    m = CONFLICT_RE.search(text)
    if not m:
        receipt["sides"][path] = "NO-MARKER (already clean?)"
        return None
    ours, base, theirs = m.group(1), m.group(2), m.group(3)
    o_ts, t_ts = max_ts(ours), max_ts(theirs)
    side = "ours" if o_ts > t_ts else "theirs"
    if o_ts == t_ts:
        side = "ours"  # identical ts: origin canonical
    receipt["sides"][path] = {"ours_ts": o_ts, "theirs_ts": t_ts, "take": side}
    return side


def strip_conflicts_keep(path, side):
    """Rebuild file replacing each conflict block with chosen side's text."""
    text = read(path)

    def repl(m):
        return m.group(1) if side == "ours" else m.group(3)

    return CONFLICT_RE.sub(repl, text)


def union_history(path):
    text = read(path)
    blocks = list(CONFLICT_RE.finditer(text))
    if not blocks:
        receipt["sides"][path] = "NO-MARKER"
        return text
    # Reconstruct ours-side and theirs-side full documents.
    ours_doc, theirs_doc = "", ""
    last = 0
    for m in blocks:
        ours_doc += text[last:m.start()] + m.group(1)
        theirs_doc += text[last:m.start()] + m.group(3)
        last = m.end()
    ours_doc += text[last:]
    theirs_doc += text[last:]
    o = json.loads(ours_doc)
    t = json.loads(theirs_doc)
    hist_o = o.get("history", [])
    hist_t = t.get("history", [])
    key = lambda r: (r.get("ts", ""), r.get("machine", ""))
    seen = {}
    for r in hist_o + hist_t:
        k = key(r)
        if k not in seen or str(r) > str(seen[k]):
            seen[k] = r
    merged = sorted(seen.values(), key=lambda r: r.get("ts", ""))
    base = t if max_ts(theirs_doc) > max_ts(ours_doc) else o
    base["history"] = merged
    receipt["sides"][path] = {
        "union": "history-union", "ours_rows": len(hist_o),
        "theirs_rows": len(hist_t), "merged_rows": len(merged),
        "top_from": "theirs" if max_ts(theirs_doc) > max_ts(ours_doc) else "ours",
    }
    return json.dumps(base, ensure_ascii=False, indent=1) + "\n"


def union_token(path):
    text = read(path)
    blocks = list(CONFLICT_RE.finditer(text))
    if not blocks:
        receipt["sides"][path] = "NO-MARKER"
        return text
    ours_doc, theirs_doc = "", ""
    last = 0
    for m in blocks:
        ours_doc += text[last:m.start()] + m.group(1)
        theirs_doc += text[last:m.start()] + m.group(3)
        last = m.end()
    ours_doc += text[last:]
    theirs_doc += text[last:]
    o = json.loads(ours_doc)
    t = json.loads(theirs_doc)

    def merge(a, b):
        if isinstance(a, dict) and isinstance(b, dict):
            out = dict(a)
            for k, v in b.items():
                out[k] = merge(out[k], v) if k in out else v
            return out
        # scalar / ts-bearing: newer side wins by contained ts
        return b if max_ts(str(b)) > max_ts(str(a)) else a

    merged = merge(o, t)
    receipt["sides"][path] = {"union": "per-key-union",
                              "top_from": "theirs" if max_ts(theirs_doc) > max_ts(ours_doc) else "ours"}
    return json.dumps(merged, ensure_ascii=False, indent=1) + "\n"


def main():
    # 1. HQ-FEEDBACK: ours (origin canonical receipt row; my dup yields)
    p = "HQ-FEEDBACK.md"
    text = read(p)
    resolved = CONFLICT_RE.sub(lambda m: m.group(1), text)
    io.open(os.path.join(ROOT, p), "w", encoding="utf-8", newline="\n").write(resolved)
    receipt["strategies"][p] = "ours-yield-dup-row (origin F-20261005-01 canonical per commit-time)"

    # 2. take-side faces
    verdicts = {}
    for p in TAKE_SIDE:
        side = take_side(p)
        if side:
            resolved = strip_conflicts_keep(p, side)
            io.open(os.path.join(ROOT, p), "w", encoding="utf-8", newline="\n").write(resolved)
            verdicts[p] = side
            receipt["strategies"][p] = "ts-newer-wins " + side

    # 3. dashboard_status.js locked to .json twin
    js = "results/dashboard_status.js"
    json_side = verdicts.get("results/dashboard_status.json")
    if json_side:
        resolved = strip_conflicts_keep(js, json_side)
        io.open(os.path.join(ROOT, js), "w", encoding="utf-8", newline="\n").write(resolved)
        receipt["strategies"][js] = "twin-locked-to-json " + json_side

    # 4. compute_audit history union
    p = "results/compute_audit.json"
    resolved = union_history(p)
    io.open(os.path.join(ROOT, p), "w", encoding="utf-8", newline="\n").write(resolved)
    receipt["strategies"][p] = "history-union zero-loss"

    # 5. token_usage per-key union
    p = "results/token_usage.json"
    resolved = union_token(p)
    io.open(os.path.join(ROOT, p), "w", encoding="utf-8", newline="\n").write(resolved)
    receipt["strategies"][p] = "per-key-union"

    out = os.path.join(ROOT, "results", "_r505bmc_merge_resolve.json")
    json.dump(receipt, io.open(out, "w", encoding="utf-8", newline="\n"),
              ensure_ascii=False, indent=1)
    print("RESOLVED", len(receipt["strategies"]), "files; receipt", out)
    for k, v in receipt["strategies"].items():
        print(" ", k, "->", v)


if __name__ == "__main__":
    main()
