"""r133 bm-c S0 rebase-land resolver: snapshot-family take-fresher (deep-ts
probe, tie->origin per r140). ALL_FACES lanes already resolved via
merge_lane_views.py resolve (r377 canon). Precedent: r132 _r132bmc_storm_resolve
(same recipes, this rebase's 4 conflicted snapshot faces only).
Prints per-file decision evidence; parse-verifies JSON faces; zero conflict
markers left.
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
    "results/prospect_promotion/_summary.json",
]


def stage_blob(path: str, stage: int) -> bytes:
    return subprocess.check_output(["git", "show", f":{stage}:{path}"])


def probe_max_ts(text: str):
    hits = TS_RE.findall(text)
    return max(hits) if hits else ""


def main() -> int:
    for path in SNAPSHOTS:
        s2 = stage_blob(path, 2)  # origin (rebase base) side
        s3 = stage_blob(path, 3)  # replay (bm-c r132) side
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
    for path in SNAPSHOTS:
        body = open(path, "rb").read().decode("utf-8", "replace")
        assert "<<<<<<<" not in body and ">>>>>>>" not in body, f"markers left in {path}"
    print("resolver done: 4 snapshots take-fresher, parse-verified, zero markers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
