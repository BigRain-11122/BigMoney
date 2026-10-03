r"""r660 S0 merge UU resolver: per-face latest-scan-wins (r638/r644 precedent).

Reads stage2(ours)/stage3(theirs) blobs per UU face, extracts freshness key,
resolves checkout --ours/--theirs, verifies zero conflict markers remain.
Bytes-safe strict JSON read; md faces keyed by content hash equality fallback.
"""
import json
import re
import subprocess
import sys

FACES = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

KEYS = ("generated", "generated_at", "updated", "updated_at", "ts", "asof", "date", "cutoff")


def blob(rev, path):
    return subprocess.run(
        ["git", "show", f"{rev}:{path}"], capture_output=True
    ).stdout


def freshness(data_bytes, path):
    if path.endswith((".json", ".js")):
        try:
            d = json.loads(data_bytes.decode("utf-8"))
        except Exception:
            return None
        if isinstance(d, dict):
            for k in KEYS:
                v = d.get(k)
                if isinstance(v, str) and len(v) >= 8:
                    return v
            # nested scan ts
            for k in ("scan", "last_scan", "meta"):
                v = d.get(k)
                if isinstance(v, dict):
                    for kk in KEYS:
                        vv = v.get(kk)
                        if isinstance(vv, str) and len(vv) >= 8:
                            return vv
        return None
    m = re.search(rb"20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?", data_bytes)
    return m.group(0).decode() if m else None


def main():
    verdicts = []
    for f in FACES:
        ours = blob(":2", f)
        theirs = blob(":3", f)
        fo, ft = freshness(ours, f), freshness(theirs, f)
        if fo is None and ft is None:
            side = "ours"
            why = "no-ts-fallback-ours"
        elif ft is None:
            side, why = "ours", "theirs-no-ts"
        elif fo is None:
            side, why = "theirs", "ours-no-ts"
        elif fo >= ft:
            side, why = "ours", f"ours={fo} >= theirs={ft}"
        else:
            side, why = "theirs", f"theirs={ft} > ours={fo}"
        r = subprocess.run(
            ["git", "checkout", f"--{side}", "--", f], capture_output=True
        )
        if r.returncode != 0:
            verdicts.append((f, "ERROR", r.stderr.decode()[:120]))
            continue
        subprocess.run(["git", "add", "--", f], check=True)
        verdicts.append((f, side, why))
    for f, s, w in verdicts:
        print(f"{s:6} {f}  # {w}")
    # marker sweep assertion on all faces (r630/r657 law)
    bad = []
    for f in FACES:
        b = open(f, "rb").read()
        for mk in (b"<<<<<<<", b">>>>>>>", b"======="):
            # '=======' legal inside md? check only marker-with-newline pattern
            if mk == b"=======":
                if re.search(rb"^=======$", b, re.M):
                    bad.append(f)
                    break
            elif mk in b:
                bad.append(f)
                break
    print("MARKER-SWEEP:", "CLEAN" if not bad else f"DIRTY {bad}")
    return 0 if not bad else 2


if __name__ == "__main__":
    sys.exit(main())
