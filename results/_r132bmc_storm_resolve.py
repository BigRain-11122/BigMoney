"""r132 bm-c push-storm resolver: snapshot-family take-fresher (deep-ts probe, tie->origin per r140)
+ x2_watch_log.jsonl line-union. ALL_FACES lanes already resolved via merge_lane_views.py resolve
(r377 canon). Precedent: bm-a r379 addendum (snapshots x12 deep-ts take-fresher) + r358 resolver.
Prints per-file decision evidence; parse-verifies JSON faces; zero conflict markers left.
"""
import json
import re
import subprocess
import sys

TS_RE = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")

SNAPSHOTS = [
    "docs/daily_report/REPORT-2026-09-28.json",
    "docs/daily_report/REPORT-2026-09-28.md",
    "results/fundamental_b_layer_filter.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-24.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/t35_open_fill_verify.json",
]
UNION_LINES = ["results/x2_watch_log.jsonl"]


def stage_blob(path: str, stage: int) -> bytes:
    return subprocess.check_output(["git", "show", f":{stage}:{path}"])


def probe_max_ts(text: str):
    hits = TS_RE.findall(text)
    return max(hits) if hits else ""


def main() -> int:
    for path in SNAPSHOTS:
        s2 = stage_blob(path, 2)  # origin (bm-a r379 side)
        s3 = stage_blob(path, 3)  # replay (bm-c r132 side)
        t2 = probe_max_ts(s2.decode("utf-8", "replace"))
        t3 = probe_max_ts(s3.decode("utf-8", "replace"))
        if t2 and (not t3 or t2 >= t3):  # tie or fresher -> origin (r140)
            pick, side = s2, ":2:origin"
        else:
            pick, side = s3, ":3:replay"
        with open(path, "wb") as f:
            f.write(pick)
        if path.endswith(".json"):
            json.loads(pick.decode("utf-8"))  # parse-verify
        print(f"{path}: take {side} (origin ts={t2!r} replay ts={t3!r})")
    for path in UNION_LINES:
        s2 = stage_blob(path, 2).decode("utf-8", "replace").splitlines()
        s3 = stage_blob(path, 3).decode("utf-8", "replace").splitlines()
        seen = set(s2)
        merged = list(s2) + [ln for ln in s3 if ln not in seen and ln not in s2]
        out = "\n".join(merged) + ("\n" if merged else "")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(out)
        print(f"{path}: line-union {len(s2)}+{len(s3)}->{len(merged)}")
    # zero conflict-marker guarantee
    for path in SNAPSHOTS + UNION_LINES:
        body = open(path, "rb").read().decode("utf-8", "replace")
        assert "<<<<<<<" not in body and ">>>>>>>" not in body, f"markers left in {path}"
    print("resolver done: 14 snapshots + 1 line-union, parse-verified, zero markers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
