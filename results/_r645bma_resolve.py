"""r645 bm-a rebase-conflict resolver (bigmoney-conflict-resolve skill, snapshot/twin recipes).

Faces: twin-regen-md pairs (REPORT/LIVE json+md, twin-side coupling r327/r329:
json face deep-ts probe decides side, md face byte-copied from the SAME side blob --
md is not JSON, direct json.loads on it crashes) + snapshot class take-new by deep
recursive ts probe (r311/D-20260927-09 deep-scan law: top-level miss != no ts; probe
path existence first, r319; wall-clock values must match ^20\\d{2}-, R350).
Stage law (r351): in an interactive rebase replay, :2: = the new base side
(origin / other machine), :3: = the side being replayed (ours, bm-a r645).

POST-RUN HONESTY NOTE (r645): the deep_ts probe has a space-vs-T ranking blind
spot ("2026-10-03 22:28:47" < "2026-10-03T19:06:22" lexicographically because
" " < "T"), which made the REPORT json probe report a false tie at the nested
core_spread face; the tie-break took :3: which post-verification IS the
chronologically newer side (mine 22:28:47 vs bm-c 22:15:52, verified via
generated_at grep on both stage blobs). Future resolver: normalize the
separator before comparing ts strings.
"""
import json
import re
import subprocess
import sys

TS_KEY_HINTS = ("generated_at", "generated", "ts", "clock_read", "scan_ts", "asof")
TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def stage_bytes(stage: str, path: str) -> bytes:
    r = subprocess.run(["git", "show", f"{stage}{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"stage read fail {stage}:{path}: {r.stderr.decode()[:200]}")
    return r.stdout


def deep_ts(obj, probe_path=None):
    """Recursively locate newest-looking wall-clock ts. Returns (ts_str, path) or (None, None)."""
    best = (None, None)
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and TS_RE.match(v) and any(h in k for h in TS_KEY_HINTS):
                if best[0] is None or v > best[0]:
                    best = (v, f"{probe_path}.{k}" if probe_path else k)
            sub = deep_ts(v, f"{probe_path}.{k}" if probe_path else k)
            if sub[0] is not None and (best[0] is None or sub[0] > best[0]):
                best = sub
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            sub = deep_ts(v, f"{probe_path}[{i}]" if probe_path else f"[{i}]")
            if sub[0] is not None and (best[0] is None or sub[0] > best[0]):
                best = sub
    return best


def resolve_snapshot(path: str, label: str):
    b2 = stage_bytes(":2:", path)
    b3 = stage_bytes(":3:", path)
    j2 = json.loads(b2.decode("utf-8"))
    j3 = json.loads(b3.decode("utf-8"))
    t2 = deep_ts(j2)
    t3 = deep_ts(j3)
    print(f"[{label}] :2: ts={t2} | :3: ts={t3}")
    if t3[0] is not None and (t2[0] is None or t3[0] >= t2[0]):
        winner, wb, side = j3, b3, ":3: (ours bm-a)"
    else:
        winner, wb, side = j2, b2, ":2: (origin)"
    with open(path, "wb") as f:
        f.write(wb)
    json.loads(open(path, "rb").read().decode("utf-8"))  # parse-verify before add (r185)
    print(f"[{label}] took {side} ts={deep_ts(winner)}")
    return side


def resolve_twin(json_path: str, md_path: str, label: str):
    side = resolve_snapshot(json_path, label + ".json")
    stage = ":3:" if side.startswith(":3") else ":2:"
    wb = stage_bytes(stage, md_path)
    with open(md_path, "wb") as f:
        f.write(wb)
    head = wb[:60].decode("utf-8", errors="replace")
    print(f"[{label}.md] byte-copied from same side {stage} | head={head[:50]!r}")


if __name__ == "__main__":
    resolve_twin("docs/daily_report/REPORT-2026-10-03.json",
                 "docs/daily_report/REPORT-2026-10-03.md", "REPORT-2026-10-03")
    resolve_twin("docs/live_usage/LIVE-2026-10-03.json",
                 "docs/live_usage/LIVE-2026-10-03.md", "LIVE-2026-10-03")
    resolve_twin("docs/live_usage/LIVE-latest.json",
                 "docs/live_usage/LIVE-latest.md", "LIVE-latest")
    resolve_snapshot("results/fundamental_b_layer_filter.json", "b_layer_filter")
    resolve_snapshot("results/_attrition_guard_scan.json", "attrition_guard_scan")
    print("ALL RESOLVED (8 files) -- next: git add + rebase --continue + merge_lane_views reconcile")
