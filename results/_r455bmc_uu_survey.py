# -*- coding: utf-8 -*-
"""r455 bm-c UU survey: per-face both-sides (index :2: ours / :3: theirs) ts
probe + JSON parseability + structure keys, to ground the resolve step.
Read-only (no writes, no resolution here)."""
import json
import re
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
FACES = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]


def blob(side, path):
    r = subprocess.run(
        ["git", "show", ":%s:%s" % (side, path)],
        capture_output=True, cwd=ROOT)
    return r.stdout


def ts_of(raw, hint):
    text = raw.decode("utf-8", "replace")
    m = re.search(r'"(ts|generated_at|generated|asof|probe_time|scan_ts)"\s*:\s*"([^"]+)"', text)
    if m:
        return "%s=%s" % (m.group(1), m.group(2))
    m = re.search(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?", text)
    if m:
        return "first-ts-like=%s" % m.group(0)
    return "(no ts)"


def main():
    for f in FACES:
        ours = blob("2", f)
        theirs = blob("3", f)
        line = "%s | OURS %dB %s | THEIRS %dB %s" % (
            f, len(ours), ts_of(ours, f), len(theirs), ts_of(theirs, f))
        if f.endswith(".json"):
            ok_o = ok_t = "parse:?"
            try:
                json.loads(ours)
                ok_o = "parse:OK"
            except Exception:
                ok_o = "parse:FAIL"
            try:
                json.loads(theirs)
                ok_t = "parse:OK"
            except Exception:
                ok_t = "parse:FAIL"
            line += " | %s / %s" % (ok_o, ok_t)
        print(line[:320])
    # structure peek for union faces
    for f in ("results/compute_audit.json", "results/token_usage.json"):
        for side in ("2", "3"):
            raw = blob(side, f)
            try:
                j = json.loads(raw)
                keys = list(j.keys())[:12]
                hist = j.get("history")
                hn = len(hist) if isinstance(hist, list) else "-"
                pm = j.get("per_machine")
                pmn = list(pm.keys()) if isinstance(pm, dict) else "-"
                print("STRUCT %s :%s: keys=%s hist_len=%s pm=%s" % (f, side, keys, hn, pmn))
            except Exception as e:
                print("STRUCT %s :%s: parse-fail %s" % (f, side, str(e)[:80]))
    print("SURVEY_DONE")


if __name__ == "__main__":
    main()
