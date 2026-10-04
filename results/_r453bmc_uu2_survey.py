"""r453 bm-c UU2 survey: print head + max-ts of :2:/:3: stages for regen faces."""
import re
import subprocess

FACES = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.json",
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/update_status.json",
]
TSRE = re.compile(r"20\d\d-\d\d-\d\d[T ]\d\d:\d\d:\d\d")


def show(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else f"<SHOW_FAIL {r.returncode}>"


for p in FACES:
    o, t = show(2, p), show(3, p)
    mo, mt = TSRE.findall(o), TSRE.findall(t)
    ho = " | ".join(o.strip().splitlines()[:3])[:150]
    ht = " | ".join(t.strip().splitlines()[:3])[:150]
    print(f"SURV| {p}")
    print(f"  OURS ts={max(mo) if mo else 'NONE'} head={ho}")
    print(f"  THRS ts={max(mt) if mt else 'NONE'} head={ht}")
