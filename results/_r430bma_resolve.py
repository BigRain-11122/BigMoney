"""r430 bm-a rebase-conflict resolver (remaining 7 files after merge_lane_views ALL_FACES).

Classes per bigmoney-conflict-resolve SKILL.md:
- results/fundamental_b_layer_filter.json = snapshot take-new by deep-ts probe
  (merge_lane_views fail-closed: not in ALL_FACES list -- classifier recipe R350 probe).
- docs/daily_report/REPORT-2026-09-29.{json,md} = twin-regen-md: json face probes
  generated ts -> BOTH twins take the SAME side, md copied as bytes (r327/r329).
- docs/live_usage/LIVE-2026-09-29.{json,md} + LIVE-latest.{json,md} = same-day
  idempotent regen twins (r422/r423 manual-determined precedent) -> same law.

Stages in rebase: :2: = origin side (bm-c r219/r220), :3: = local side (bm-a r430).
Deep-ts probe per R350: recursive scan, key normalize strip '_/-', value must match
^20\\d{2}- AND contain a time-of-day (T or space+HH:MM).
"""
import json
import re
import subprocess
import sys

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
KEY_RE = re.compile(r"(generated|updated|written|asof|as_of|^ts$|_ts$|^ts_|stamp)", re.I)


def blob(revspec: str) -> bytes:
    p = subprocess.run(["git", "show", revspec], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git show {revspec} rc={p.returncode}")
    return p.stdout


def deep_ts(obj, best=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = str(k).strip("_-").lower()
            if isinstance(v, str) and TS_RE.match(v) and (KEY_RE.search(nk) or nk in ("ts", "time")):
                if v > best:
                    best = v
            else:
                best = deep_ts(v, best)
    elif isinstance(obj, list):
        for it in obj:
            best = deep_ts(it, best)
    return best


def side_ts(revspec: str):
    raw = blob(revspec)
    try:
        return deep_ts(json.loads(raw.decode("utf-8"))), raw
    except Exception as e:
        return "", raw


def main() -> int:
    repo = "results/_r430bma_resolve"

    def resolve_snapshot(path):
        t2, b2 = side_ts(f":2:{path}")
        t3, b3 = side_ts(f":3:{path}")
        pick = 3 if (t3 and (not t2 or t3 >= t2)) else 2
        ts = t3 if pick == 3 else t2
        raw = b3 if pick == 3 else b2
        json.loads(raw.decode("utf-8"))  # parse-verify before write (r185)
        open(path, "wb").write(raw)
        print(f"[snapshot] {path}: side{pick} (ts {ts!r} vs {t2!r}/{t3!r}) written+parsed OK")

    def resolve_twins(jpath, mpath):
        t2, b2 = side_ts(f":2:{jpath}")
        t3, b3 = side_ts(f":3:{jpath}")
        pick = 3 if (t3 and (not t2 or t3 >= t2)) else 2
        ts = t3 if pick == 3 else t2
        raw_j = b3 if pick == 3 else b2
        json.loads(raw_j.decode("utf-8"))
        open(jpath, "wb").write(raw_j)
        raw_m = blob(f":{pick}:{mpath}")
        open(mpath, "wb").write(raw_m)  # md twin: same side, byte copy (r329)
        print(f"[twin] {jpath}+{mpath}: side{pick} (json ts {ts!r} vs {t2!r}/{t3!r}) both written")

    resolve_snapshot("results/fundamental_b_layer_filter.json")
    resolve_twins("docs/daily_report/REPORT-2026-09-29.json", "docs/daily_report/REPORT-2026-09-29.md")
    resolve_twins("docs/live_usage/LIVE-2026-09-29.json", "docs/live_usage/LIVE-2026-09-29.md")
    resolve_twins("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md")

    print(f"{repo}: 7 files resolved; next: git add <paths> + rebase --continue (GIT_EDITOR=true r356) + merge_lane_views reconcile same-window")
    return 0


if __name__ == "__main__":
    sys.exit(main())
