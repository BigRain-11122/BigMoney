"""r222 bm-c push-window resolver: 18-UU same-day derive-face batch.

Rebase replay of my r222 commit onto origin/main (bm-a r432 S6 14:2x faces).
Stage orientation r351: :2: = origin (bm-a r432) side, :3: = local (bm-c r222 14:29) side.
Recipes: ALL_FACES x6 via merge_lane_views.py resolve (skill canon, no hand-union);
snapshot faces via storm-proven r431 deep-ts probe (R350: time-of-day value gate);
twins byte-copied from json-probe side (r329); js-wrapper whole-byte coupled (R209).
Lineage: _r432bma_s0resolve.py copied whole, face list trimmed to this UU set.
"""
import json
import re
import subprocess

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")

ALL_FACES = [
    "results/compute_audit.json",
    "results/regime_state.json",
    "results/update_status.json",
    "results/lhb_update_status.json",
    "results/futures_update_status.json",
    "results/token_usage.json",
]

TAKE_NEW = [
    "results/fundamental_b_layer_filter.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/prospect_promotion/_summary.json",
]


def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"git show :{stage}:{path} failed: {r.stderr.decode()[:200]}")
    return r.stdout


def deep_ts(obj, best=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            kn = str(k).replace("_", "").replace("-", "").lower()
            if isinstance(v, str) and TS_RE.match(v) and any(p in kn for p in ("generated", "updated", "ts", "asof", "date")):
                if v > best:
                    best = v
            elif isinstance(v, (dict, list)):
                best = deep_ts(v, best)
    elif isinstance(obj, list):
        for it in obj:
            best = deep_ts(it, best)
    return best


def write_bytes(path, side):
    with open(path, "wb") as f:
        f.write(side)


def take_newer_json(path):
    b2, b3 = blob("2", path), blob("3", path)
    t2, t3 = deep_ts(json.loads(b2)), deep_ts(json.loads(b3))
    if not t2 and not t3:
        raise SystemExit(f"{path}: no ts probe either side, refuse blind pick")
    winner, side = ("2", b2) if t2 >= t3 else ("3", b3)
    write_bytes(path, side)
    print(f"[take-new:{path}] :2:={t2!r} :3:={t3!r} -> :{winner}: ({len(side)}B)")
    return winner


def byte_copy(path, winner):
    side = blob("2", path) if winner == "2" else blob("3", path)
    write_bytes(path, side)
    print(f"[twin-copy:{path}] from :{winner}: ({len(side)}B)")


def main():
    # 1. ALL_FACES: canon union resolver (reads rebase stages itself)
    for p in ALL_FACES:
        r = subprocess.run(["python", "scripts/merge_lane_views.py", "resolve", p],
                           capture_output=True, text=True)
        print(f"[all-faces:{p}] rc={r.returncode} {r.stdout.strip()[:160]}{r.stderr.strip()[:160]}")
        if r.returncode != 0:
            raise SystemExit(f"merge_lane_views resolve failed for {p}")

    # 2. snapshot faces: take-new whole doc by deep-ts probe
    for p in TAKE_NEW:
        take_newer_json(p)

    # 3. twin pairs: json probe decides side, md byte-copy same side (r329)
    w = take_newer_json("docs/daily_report/REPORT-2026-09-29.json")
    byte_copy("docs/daily_report/REPORT-2026-09-29.md", w)
    w = take_newer_json("docs/live_usage/LIVE-2026-09-29.json")
    byte_copy("docs/live_usage/LIVE-2026-09-29.md", w)
    byte_copy("docs/live_usage/LIVE-latest.json", w)
    byte_copy("docs/live_usage/LIVE-latest.md", w)

    # 4. dashboard json probe -> js whole-byte coupled (R209: never json.dumps direct-write)
    w = take_newer_json("results/dashboard_status.json")
    side = blob("2", "results/dashboard_status.js") if w == "2" else blob("3", "results/dashboard_status.js")
    write_bytes("results/dashboard_status.js", side)
    print(f"[js-wrapper:dashboard_status.js] side :{w}: coupled with .json twin ({len(side)}B)")

    # 5. parse-verify every written json face (r185) + js wrapper payload
    for p in TAKE_NEW + ALL_FACES + [
        "docs/daily_report/REPORT-2026-09-29.json",
        "docs/live_usage/LIVE-2026-09-29.json",
        "docs/live_usage/LIVE-latest.json",
        "results/dashboard_status.json",
    ]:
        json.loads(open(p, "rb").read().decode("utf-8"))
    js = open("results/dashboard_status.js", "rb").read().decode("utf-8")
    json.loads(js.split("=", 1)[1].rsplit(";", 1)[0].strip())
    print("[verify] all 18 faces parse-verified OK")


if __name__ == "__main__":
    main()
