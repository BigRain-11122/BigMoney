# r968 S0 rebase storm resolver: twin-regen faces (REPORT/LIVE same-side law r327/r329)
# + UNKNOWN manual-classified face (_r686bmb_d19_check.json = bm-b d19 probe evidence
# snapshot, newest ts wins; tie -> :2: per r140).
# Law: json face deep-probe generated ts -> pick side -> md twins byte-copied from
# SAME side blob (never hybrid twins). Byte reads via subprocess (no PS redirect, r209).
import json
import subprocess
import sys

GIT = r"C:\Program Files\Git\cmd\git.exe"


def stage_bytes(path: str, stage: str) -> bytes:
    r = subprocess.run([GIT, "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"stage read fail {path} {stage}: {r.stderr[:200]}")
    return r.stdout


def deep_probe_ts(obj, depth=0):
    """Deep-scan nested layers for the newest wall-clock value under ts-like keys
    (r311 law: top-level miss != no ts). Returns max ISO string found or None."""
    best = None
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and len(v) >= 19 and v[:4] == "2026" and (
                    k in ("generated", "generated_at", "ts", "updated", "asof_time", "written_at")):
                if best is None or v > best:
                    best = v
            else:
                sub = deep_probe_ts(v, depth + 1)
                if sub and (best is None or sub > best):
                    best = sub
    elif isinstance(obj, list):
        for v in obj:
            sub = deep_probe_ts(v, depth + 1)
            if sub and (best is None or sub > best):
                best = sub
    return best


def pick_side(json_path: str):
    b2 = stage_bytes(json_path, "2")
    b3 = stage_bytes(json_path, "3")
    j2 = json.loads(b2.decode("utf-8-sig"))
    j3 = json.loads(b3.decode("utf-8-sig"))
    t2 = deep_probe_ts(j2)
    t3 = deep_probe_ts(j3)
    # tie -> :2: (HEAD/origin side, r140 law)
    if t3 is not None and (t2 is None or t3 > t2):
        return 3, t2, t3
    return 2, t2, t3


GROUPS = [
    # (json probe face, [all twin files of the group - same side byte-copied])
    ("docs/daily_report/REPORT-2026-10-13.json",
     ["docs/daily_report/REPORT-2026-10-13.json",
      "docs/daily_report/REPORT-2026-10-13.md"]),
    ("docs/live_usage/LIVE-2026-10-13.json",
     ["docs/live_usage/LIVE-2026-10-13.json",
      "docs/live_usage/LIVE-2026-10-13.md",
      "docs/live_usage/LIVE-latest.json",
      "docs/live_usage/LIVE-latest.md"]),
    ("results/_r686bmb_d19_check.json",
     ["results/_r686bmb_d19_check.json"]),
]

log = []
for probe, twins in GROUPS:
    side, t2, t3 = pick_side(probe)
    for f in twins:
        data = stage_bytes(f, str(side))
        with open(f, "wb") as fh:
            fh.write(data)
        log.append({"file": f, "side": f":{side}:", "ts2": t2, "ts3": t3})
    print(f"[r968 resolve] {probe}: side=:{side}: (ts2={t2} ts3={t3}) -> {len(twins)} twins byte-copied")

with open(r"results\_r968_resolve.json", "w", encoding="utf-8") as fh:
    json.dump(log, fh, ensure_ascii=False, indent=1)
print("receipt -> results/_r968_resolve.json")
