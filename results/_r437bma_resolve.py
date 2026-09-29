"""r437 bm-a push-storm UU resolver -- twin/snapshot faces (non-ALL_FACES, manual recipes).

Skill: bigmoney-conflict-resolve (classifier 13 classified + 4 UNKNOWN manually
adjudicated as twin-regen-md). Stage law: :2: = base-side (origin, r351),
:3: = replay-side (my r437 commit). Hardened deep-ts probe per r100/R350:
key normalized (strip '_'/'-' before prefix match), value must be timestamp-
shaped (^20\\d{2}-) AND carry time-of-day to feed the max; date-only values
never feed the max; no key-EXCLUDE lists. Same-second tie -> HEAD (:2:) per
r140. Twin coupling: json face decides the side, .md twin copies BYTES from
the SAME side (r329: md is not JSON, json.loads on it crashes). dashboard_status.js
= js-wrapper-snapshot: whole-byte take of the side chosen by its .json twin
(NEVER json.dumps re-emit, R209).

Zero-loss law: every side decision prints side + probe value; parse-verify all
json outputs before write.
"""
import json
import re
import subprocess
import sys

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}")


def blob(stage: str, path: str) -> bytes:
    return subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True,
                          check=True).stdout


def probe_ts(doc) -> str | None:
    """Deep-scan all nested layers for wall-clock ts under generated/updated/asof-like
    keys (normalized). Returns max time-of-day-carrying value or None."""
    best = None

    def walk(x):
        nonlocal best
        if isinstance(x, dict):
            for k, v in x.items():
                nk = str(k).replace("_", "").replace("-", "").lower()
                if isinstance(v, str) and TS_RE.match(v) and any(
                        nk.startswith(p) for p in ("generated", "updated", "asof", "ts", "time", "written")):
                    if best is None or v > best:
                        best = v
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    walk(doc)
    return best


def resolve_snapshot(path: str, tie_side: str = "2") -> str:
    a = json.loads(blob("2", path))
    b = json.loads(blob("3", path))
    ta, tb = probe_ts(a), probe_ts(b)
    side = "2" if (ta or "") >= (tb or "") else "3"   # same-second tie -> :2: (r140)
    data = blob(side, path)
    with open(path, "wb") as f:
        f.write(data)
    json.loads(data)  # parse-verify
    print(f"[resolve] {path}: side=:{side}: ts2={ta} ts3={tb}")
    return side


def twin_md(side: str, md_path: str):
    data = blob(side, md_path)
    with open(md_path, "wb") as f:
        f.write(data)
    print(f"[resolve] {md_path}: byte-copy from :{side}: ({len(data)}B)")


def main() -> int:
    # REPORT twins (json decides, md byte-copies)
    s = resolve_snapshot("docs/daily_report/REPORT-2026-09-29.json")
    twin_md(s, "docs/daily_report/REPORT-2026-09-29.md")
    # LIVE twins (UNKNOWN -> manual twin-regen-md adjudication)
    s = resolve_snapshot("docs/live_usage/LIVE-2026-09-29.json")
    twin_md(s, "docs/live_usage/LIVE-2026-09-29.md")
    s2 = resolve_snapshot("docs/live_usage/LIVE-latest.json")
    twin_md(s2, "docs/live_usage/LIVE-latest.md")
    # dashboard twins: .json decides, .js whole-byte same side (R209 js-wrapper)
    s3 = resolve_snapshot("results/dashboard_status.json")
    js = blob(s3, "results/dashboard_status.js")
    with open("results/dashboard_status.js", "wb") as f:
        f.write(js)
    assert js.startswith(b"window.DASH_DATA"), "js wrapper prefix check"
    print(f"[resolve] results/dashboard_status.js: whole-byte :{s3}: ({len(js)}B, wrapper intact)")
    # plain snapshots
    for p in ("results/fundamental_b_layer_filter.json",
              "results/scorecard_v1.json",
              "results/strategy_scorecard.json"):
        resolve_snapshot(p)
    print("resolver done: 11 faces")
    return 0


if __name__ == "__main__":
    sys.exit(main())
