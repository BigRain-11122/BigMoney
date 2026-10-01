"""r510 bm-a rebase resolver: shared derive/report faces, ts-newer-wins.

Law: r294 (jsonl union domain = conflict lines only), r500 (deep-probe
bytes-parse before compare), r509 closeout precedent (ts newer wins for
full-rewrite regen faces; md twin follows json twin side).
"""
import json
import os
import subprocess
import sys

FILES = [
    "docs/daily_report/REPORT-2026-10-01.json",
    "docs/daily_report/REPORT-2026-10-01.md",
    "docs/live_usage/LIVE-2026-10-01.json",
    "docs/live_usage/LIVE-2026-10-01.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/pool_core_samples.jsonl",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

TS_KEYS = ("ts", "generated", "generated_at", "asof", "written_at",
           "updated_at", "epoch")


def side(blob: bytes):
    """Deep-parse bytes for the newest ts-ish scalar (r500 law: parse,
    never str-compare raw)."""
    best = None
    try:
        txt = blob.decode("utf-8", errors="replace")
    except Exception:
        return None
    try:
        obj = json.loads(txt)
        stack = [obj]
        while stack:
            o = stack.pop()
            if isinstance(o, dict):
                for k, v in o.items():
                    if any(t in str(k).lower() for t in TS_KEYS) \
                            and isinstance(v, (str, int, float)):
                        s = str(v)
                        if best is None or s > best:
                            best = s
                    elif isinstance(v, (dict, list)):
                        stack.append(v)
            elif isinstance(o, list):
                stack.extend(o)
    except Exception:
        # non-json (md/js): probe first 2k for a date/epoch marker
        for line in txt.splitlines()[:40]:
            for t in TS_KEYS:
                i = line.find(t)
                if i >= 0:
                    seg = line[i:i + 40].strip('"\' ,}')
                    s = seg.split(":", 1)[-1].strip(' "\'}')
                    if len(s) >= 8 and (best is None or s > best):
                        best = s
    return best


def main():
    report = {}
    twins = {  # md/js twin -> json primary (twin follows primary side)
        "docs/daily_report/REPORT-2026-10-01.md":
            "docs/daily_report/REPORT-2026-10-01.json",
        "docs/live_usage/LIVE-2026-10-01.md":
            "docs/live_usage/LIVE-2026-10-01.json",
        "docs/live_usage/LIVE-latest.md":
            "docs/live_usage/LIVE-latest.json",
        "results/dashboard_status.js": "results/dashboard_status.json",
    }
    for f in FILES:
        if f in twins:
            continue                     # resolved after its primary
        stage2 = subprocess.check_output(
            ["git", "show", f":2:{f}"])   # ours = origin/main (new base)
        stage3 = subprocess.check_output(
            ["git", "show", f":3:{f}"])   # theirs = my replayed commit
        if f.endswith(".jsonl"):
            # r294 union domain: conflict blob lines, dedup keep both-parent
            a = {ln for ln in stage2.decode("utf-8").splitlines() if ln}
            b = {ln for ln in stage3.decode("utf-8").splitlines() if ln}
            union = sorted(a | b)
            with open(f, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("\n".join(union) + "\n")
            report[f] = f"union {len(a)}|{len(b)}->{len(union)}"
            continue
        sa, sb = side(stage2), side(stage3)
        if sa is None and sb is None:
            pick = 3                      # no probe: keep mine (regen face)
            why = "no-ts-both->mine"
        elif sb is None:
            pick = 2
            why = f"mine-no-ts origin={sa}"
        elif sa is None:
            pick = 3
            why = f"origin-no-ts mine={sb}"
        elif sb >= sa:                    # mine newer-or-equal
            pick = 3
            why = f"mine {sb} >= origin {sa}"
        else:
            pick = 2
            why = f"origin {sa} > mine {sb}"
        with open(f, "wb") as fh:
            fh.write(stage2 if pick == 2 else stage3)
        report[f] = f"pick {'origin' if pick == 2 else 'mine'} ({why})"
    # twins follow their primary's recorded side
    for twin, primary in twins.items():
        pick2 = "pick origin" in report.get(primary, "")
        blob = subprocess.check_output(
            ["git", "show", f":2:{twin}" if pick2 else f":3:{twin}"])
        with open(twin, "wb") as fh:
            fh.write(blob)
        report[twin] = f"twin-follows-json ({'origin' if pick2 else 'mine'})"
    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.exit(main())
