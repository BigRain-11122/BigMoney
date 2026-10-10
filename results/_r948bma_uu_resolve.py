"""r948 bm-a rebase UU resolver: whole-file take-newer-by-ts for same-day regen faces.

Context: rebase of our r947 (c88571f39, commit 08:42:19) onto 085a293f7 (bm-b r824,
commit 08:40:49). 14 UU files, all deterministic same-day regeneration artifacts
(daily_report / live_usage twins / S6 status JSONs). Recipe per bigmoney-conflict-resolve
family: derived regen faces -> take the side whose own generated ts is newer; md+json
twins resolved as a pair from the json's ts; no content-level merge, zero hand edits.

Stage semantics during rebase: stage2 = ours = onto side (bm-b r824); stage3 = theirs =
replayed side (our r947). Script is stage-index driven, not name driven.
"""
import json
import re
import subprocess
import sys

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"

UU = [
    "docs/daily_report/REPORT-2026-10-10.json",
    "docs/daily_report/REPORT-2026-10-10.md",
    "docs/live_usage/LIVE-2026-10-10.json",
    "docs/live_usage/LIVE-2026-10-10.md",
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

# twins: md takes the same side as its json anchor
PAIR = {
    "docs/daily_report/REPORT-2026-10-10.md": "docs/daily_report/REPORT-2026-10-10.json",
    "docs/live_usage/LIVE-2026-10-10.md": "docs/live_usage/LIVE-2026-10-10.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
}

TS_KEYS = ["generated", "ts", "timestamp", "asof", "updated", "date"]
TS_RE = re.compile(r"(20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})")


def stage(path, n):
    p = subprocess.run([GIT, "show", f":{n}:{path}"], capture_output=True, cwd=ROOT)
    if p.returncode != 0:
        return None
    return p.stdout.decode("utf-8", errors="replace")


def ts_of(text):
    """Extract the best 'generation timestamp' from json or md text."""
    try:
        j = json.loads(text)
        for k in TS_KEYS:
            v = j.get(k) if isinstance(j, dict) else None
            if isinstance(v, str) and TS_RE.search(v):
                return TS_RE.search(v).group(1)
    except Exception:
        pass
    m = TS_RE.search(text[:4000])
    return m.group(1) if m else None


def main():
    decisions = {}
    for path in UU:
        if path in PAIR:
            continue
        s2, s3 = stage(path, 2), stage(path, 3)
        if s2 is None or s3 is None:
            print(f"MISSING-STAGE {path} s2={s2 is not None} s3={s3 is not None}")
            return 2
        t2, t3 = ts_of(s2), ts_of(s3)
        # take-newer; tie or unparseable -> take stage3 (our r947, newer commit 08:42:19)
        if t2 and t3:
            side = 3 if t3 >= t2 else 2
            why = f"ts {t3} vs {t2}"
        else:
            side = 3
            why = f"ts parse t2={t2} t3={t3} -> newer-commit fallback"
        decisions[path] = (side, why)
    for md, js in PAIR.items():
        side, why = decisions[js]
        decisions[md] = (side, f"twin-of {js} ({why})")
    for path in UU:
        side, why = decisions[path]
        r = subprocess.run(
            [GIT, "checkout", "--ours" if side == 2 else "--theirs", "--", path],
            capture_output=True, cwd=ROOT)
        if r.returncode != 0:
            print(f"CHECKOUT-FAIL {path}: {r.stderr.decode(errors='replace')}")
            return 2
        a = subprocess.run([GIT, "add", "--", path], capture_output=True, cwd=ROOT)
        if a.returncode != 0:
            print(f"ADD-FAIL {path}")
            return 2
        label = "ours(=bmb-r824)" if side == 2 else "theirs(=our-r947)"
        print(f"RESOLVED {path} -> {label} | {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
