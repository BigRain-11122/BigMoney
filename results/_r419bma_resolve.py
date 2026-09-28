"""r419 bm-a merge-back resolver — group B (ts-probe snapshots) + group C (twin pairs).

Canon: bigmoney-conflict-resolve skill 解后纪律 — ts 探针深扫嵌套层 (D-20260927-09),
比较路径先探存在 (r319), twin-side coupling (r327/r329): json face decides side by
deep-probed ts; md twin byte-copied from the SAME side blob (禁杂交孪生).
In a MERGE: stage 2 = ours (local main / HEAD), stage 3 = theirs (origin/main).
"""
import json
import subprocess
import sys

TS_KEYS = {"generated", "generated_at", "updated", "ts", "asof", "cutoff",
           "date", "last_seen", "run_ts"}


def stage_blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def deep_ts(obj, best=""):
    """Recursively locate freshest ts-like string; path-existence-first (r319)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and k in TS_KEYS and len(v) >= 8:
                if v > best:
                    best = v
            else:
                best = deep_ts(v, best)
    elif isinstance(obj, list):
        for it in obj:
            best = deep_ts(it, best)
    return best


def resolve_snapshot(path):
    b2 = stage_blob(2, path)
    b3 = stage_blob(3, path)
    if b2 is None and b3 is None:
        return "BOTH-ABSENT"
    if b2 is None:
        side = "theirs"
    elif b3 is None:
        side = "ours"
    else:
        t2 = deep_ts(json.loads(b2.decode("utf-8")))
        t3 = deep_ts(json.loads(b3.decode("utf-8")))
        if t2 == "" and t3 == "":
            side = "ours"  # no ts anywhere -> HEAD tie (r140)
        else:
            side = "ours" if t2 >= t3 else "theirs"
        print(f"  {path}: ts2={t2!r} ts3={t3!r} -> {side}")
    subprocess.run(["git", "checkout", f"--{side}", path], check=True)
    subprocess.run(["git", "add", path], check=True)
    return side


def resolve_twin(json_path, md_path):
    side = resolve_snapshot(json_path)
    if md_path:
        subprocess.run(["git", "checkout", f"--{side}", md_path], check=True)
        subprocess.run(["git", "add", md_path], check=True)
    return side


if __name__ == "__main__":
    jobs = [
        ("snapshot", "results/prospect_promotion/_summary.json", None),
        ("snapshot", "results/fundamental_b_layer_filter.json", None),
        ("twin", "docs/daily_report/REPORT-2026-09-29.json",
         "docs/daily_report/REPORT-2026-09-29.md"),
        ("twin", "docs/live_usage/LIVE-2026-09-29.json",
         "docs/live_usage/LIVE-2026-09-29.md"),
        ("twin", "docs/live_usage/LIVE-latest.json",
         "docs/live_usage/LIVE-latest.md"),
    ]
    for kind, jp, mp in jobs:
        side = resolve_twin(jp, mp) if kind == "twin" else resolve_snapshot(jp)
        print(f"[{kind}] {jp}" + (f" + {mp}" if mp else "") + f" -> {side}")
    print("group B+C done")
