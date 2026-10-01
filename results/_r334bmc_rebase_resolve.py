"""r334 bm-c rebase conflict resolver: 27 same-day idempotent derive faces
(r505 wall-clock-newer law) + x2_watch_log.jsonl conflict-zone union (r294
domain law). Diff3 five-marker aware (r312: never cut on '=======').
Raw bytes, no PS transcoding (r292). Zero-marker assertion before write.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES_JSON_SIDE_PICK = [
    "docs/daily_report/REPORT-2026-10-01.json",
    "docs/daily_report/REPORT-2026-10-01.md",
    "docs/live_usage/LIVE-2026-10-01.json",
    "docs/live_usage/LIVE-2026-10-01.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.js",
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
    "results/paper_export/export-2026-09-30.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/update_status.json",
]
FILES_UNION = [
    "results/x2_watch_log.jsonl",   # append-only ledger: zone union (r294)
]

TS_RE = re.compile(
    r'"(?:ts|generated|generated_at|updated|updated_at|asof|stamp|'
    r'date|time|written_at|last_seen|updated_at)"\s*:\s*"'
    r'(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(?::\d{2})?)"')
TS_RE2 = re.compile(r'(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})')


def _max_ts(text):
    cands = TS_RE.findall(text) or TS_RE2.findall(text)
    return max(cands) if cands else ""


def split_conflicts(text):
    """Segments: ('plain', s) | ('conflict', ours, base, theirs).
    Diff3-aware; base section may be absent (2-way)."""
    segs = []
    lines = text.splitlines(keepends=True)
    cur, ours, base, theirs = [], [], [], []
    state = 0
    for ln in lines:
        stripped = ln.rstrip("\r\n")
        if state == 0:
            if ln.startswith("<<<<<<< "):
                segs.append(("plain", "".join(cur)))
                cur, ours, base, theirs = [], [], [], []
                state = 1
            else:
                cur.append(ln)
        elif state == 1:
            if ln.startswith("||||||| "):
                state = 2
            elif stripped == "=======":
                state = 3
            else:
                ours.append(ln)
        elif state == 2:
            if stripped == "=======":
                state = 3
            else:
                base.append(ln)
        elif state == 3:
            if ln.startswith(">>>>>>> "):
                segs.append(("conflict", "".join(ours), "".join(base),
                             "".join(theirs)))
                cur, ours, base, theirs = [], [], [], []
                state = 0
            else:
                theirs.append(ln)
    segs.append(("plain", "".join(cur)))
    return segs


def resolve_side_pick(text):
    """Whole-file wall-clock pick: newest internal ts side wins every hunk
    (r505: same-day idempotent re-derive, no semantic merge space)."""
    segs = split_conflicts(text)
    ours_all = "".join(s[1] for s in segs if s[0] == "conflict")
    theirs_all = "".join(s[3] for s in segs if s[0] == "conflict")
    t_ours, t_theirs = _max_ts(ours_all), _max_ts(theirs_all)
    if t_ours and (not t_theirs or t_ours >= t_theirs):
        winner = "ours(origin)"
    else:
        winner = "theirs(bm-c-r334)"
    out = []
    for s in segs:
        if s[0] == "plain":
            out.append(s[1])
        else:
            out.append(s[1] if winner.startswith("ours") else s[3])
    return "".join(out), winner, t_ours, t_theirs


def resolve_union(text):
    """Conflict-zone line union: ours + theirs-not-in-ours, full-line key
    (deterministic twins collapse; domain = zone only, r294 law)."""
    segs = split_conflicts(text)
    out = []
    stats = []
    for s in segs:
        if s[0] == "plain":
            out.append(s[1])
            continue
        ours_lines = s[1].splitlines(keepends=True)
        theirs_lines = s[3].splitlines(keepends=True)
        ours_keys = set(x.rstrip("\r\n") for x in ours_lines)
        kept = [x for x in theirs_lines
                if x.rstrip("\r\n") not in ours_keys and x.strip()]
        stats.append((len(ours_lines), len(theirs_lines), len(kept)))
        out.append("".join(ours_lines))
        out.append("".join(kept))
    return "".join(out), "union", stats, None


def main():
    report = []
    for rel in FILES_JSON_SIDE_PICK + FILES_UNION:
        path = os.path.join(ROOT, rel.replace("/", os.sep))
        raw = open(path, "rb").read()
        text = raw.decode("utf-8", errors="strict")
        if "<<<<<<< " not in text:
            report.append(f"SKIP(no markers) {rel}")
            continue
        if rel in FILES_UNION:
            merged, policy, a, b = resolve_union(text)
        else:
            merged, policy, a, b = resolve_side_pick(text)
        # zero-marker assertion (claw-compatible)
        for mk in ("<<<<<<< ", ">>>>>>> ", "||||||| "):
            assert mk not in merged, f"marker leftover {mk!r} in {rel}"
        # stray '=======' lone lines that came from markers
        bad = [ln for ln in merged.splitlines()
               if ln.rstrip("\r\n") == "======="]
        assert not bad, f"lone ======= leftover in {rel}"
        # JSON parse validation (r504 law) for .json faces
        if rel.endswith(".json"):
            json.loads(merged)
        new_raw = merged.encode("utf-8")
        if new_raw != raw:
            open(path, "wb").write(new_raw)
        if policy == "union":
            report.append(f"UNION {rel}: per-zone (ours,theirs,kept)={a}")
        else:
            report.append(f"SIDE {rel}: winner={policy} "
                          f"ts_ours={a} ts_theirs={b}")
    print("\n".join(report))
    print(f"RESOLVED {len(report)} files OK")


if __name__ == "__main__":
    main()
