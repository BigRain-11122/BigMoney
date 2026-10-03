"""r646 bm-a rebase-conflict resolver (bigmoney-conflict-resolve skill; r645 resolver
with the space-vs-T normalization fix from the r645 post-run honesty note).

Faces handled here (manual recipes):
  twin-regen-md: REPORT/LIVE dated + LIVE-latest json+md (twin-side coupling r327/r329:
    json deep-ts probe decides side, md byte-copied from the SAME side blob)
  js-wrapper-snapshot: dashboard_status.json decides side, .js byte-copied same side
    whole bytes (producer format, never json.dumps re-emit, R209)
  snapshot take-new: scorecard_v1 / strategy_scorecard / fundamental_b_layer_filter /
    _attrition_guard_scan (per-run evidence snapshot, classified UNKNOWN by classifier
    -> manual adjudication = take-new by deep ts probe, regenerated every round)

ALL_FACES union faces are resolved by scripts/merge_lane_views.py resolve (separately).

Stage law (r351): :2: = new base side (origin / other machine), :3: = replayed side (ours).
ts compare: normalize " " -> "T" before lexicographic compare (r645 honesty note).
"""
import json
import re
import subprocess

TS_KEY_HINTS = ("generated_at", "generated", "ts", "clock_read", "scan_ts", "asof", "updated")
TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def stage_bytes(stage: str, path: str) -> bytes:
    r = subprocess.run(["git", "show", f"{stage}{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"stage read fail {stage}:{path}: {r.stderr.decode()[:200]}")
    return r.stdout


def norm_ts(v: str) -> str:
    return v.replace(" ", "T")


def deep_ts(obj, probe_path=None):
    best = (None, None)
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and TS_RE.match(v) and any(h in k for h in TS_KEY_HINTS):
                if best[0] is None or norm_ts(v) > norm_ts(best[0]):
                    best = (v, f"{probe_path}.{k}" if probe_path else k)
            sub = deep_ts(v, f"{probe_path}.{k}" if probe_path else k)
            if sub[0] is not None and (best[0] is None or norm_ts(sub[0]) > norm_ts(best[0])):
                best = sub
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            sub = deep_ts(v, f"{probe_path}[{i}]" if probe_path else f"[{i}]")
            if sub[0] is not None and (best[0] is None or norm_ts(sub[0]) > norm_ts(best[0])):
                best = sub
    return best


def resolve_snapshot(path: str, label: str):
    b2, b3 = stage_bytes(":2:", path), stage_bytes(":3:", path)
    j2, j3 = json.loads(b2.decode("utf-8")), json.loads(b3.decode("utf-8"))
    t2, t3 = deep_ts(j2), deep_ts(j3)
    print(f"[{label}] :2: {t2} | :3: {t3}")
    if t3[0] is not None and (t2[0] is None or norm_ts(t3[0]) >= norm_ts(t2[0])):
        winner, wb, side, stage = j3, b3, ":3: (ours bm-a)", ":3:"
    else:
        winner, wb, side, stage = j2, b2, ":2: (origin)", ":2:"
    with open(path, "wb") as f:
        f.write(wb)
    json.loads(open(path, "rb").read().decode("utf-8"))  # parse-verify before add (r185)
    print(f"[{label}] took {side}")
    return stage


def resolve_twin(json_path: str, md_path: str, label: str):
    stage = resolve_snapshot(json_path, label + ".json")
    wb = stage_bytes(stage, md_path)
    with open(md_path, "wb") as f:
        f.write(wb)
    print(f"[{label}.md] byte-copied from same side {stage}")


if __name__ == "__main__":
    resolve_twin("docs/daily_report/REPORT-2026-10-03.json",
                 "docs/daily_report/REPORT-2026-10-03.md", "REPORT-2026-10-03")
    live_stage = resolve_snapshot("docs/live_usage/LIVE-2026-10-03.json", "LIVE-2026-10-03.json")
    for jp, mp in [("docs/live_usage/LIVE-2026-10-03.md", None),
                   ("docs/live_usage/LIVE-latest.json", None),
                   ("docs/live_usage/LIVE-latest.md", None)]:
        wb = stage_bytes(live_stage, jp)
        with open(jp, "wb") as f:
            f.write(wb)
        if jp.endswith(".json"):
            json.loads(wb.decode("utf-8"))
        print(f"[{jp}] byte-copied from {live_stage} (LIVE twins same-side law r439)")
    dash_stage = resolve_snapshot("results/dashboard_status.json", "dashboard_status.json")
    wb = stage_bytes(dash_stage, "results/dashboard_status.js")
    with open("results/dashboard_status.js", "wb") as f:
        f.write(wb)
    print(f"[dashboard_status.js] whole-byte from {dash_stage} (js-wrapper R209, same side)")
    resolve_snapshot("results/scorecard_v1.json", "scorecard_v1")
    resolve_snapshot("results/strategy_scorecard.json", "strategy_scorecard")
    resolve_snapshot("results/fundamental_b_layer_filter.json", "b_layer_filter")
    resolve_snapshot("results/_attrition_guard_scan.json", "attrition_guard_scan")
    print("RESOLVED 12 files -- ALL_FACES go via merge_lane_views.py resolve next")
