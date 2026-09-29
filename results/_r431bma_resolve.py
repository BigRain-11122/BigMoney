"""r431 bm-a push-storm manual resolver: snapshot / twin-regen / js-wrapper faces (11 files).

Probes take the genuinely newer side per file (stage blobs, deep-ts, R350);
json+md twins byte-copied from the SAME side as their json probe (r329);
js wrapper whole-byte take-side (R209), side decided by its .json twin probe.
"""
import json
import re
import subprocess

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


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
    # snapshot faces (take-new, no twins)
    for p in ("results/fundamental_b_layer_filter.json",
              "results/scorecard_v1.json",
              "results/strategy_scorecard.json"):
        take_newer_json(p)
    # twin pairs: json probe decides, md byte-copy same side
    w = take_newer_json("docs/daily_report/REPORT-2026-09-29.json")
    byte_copy("docs/daily_report/REPORT-2026-09-29.md", w)
    w = take_newer_json("docs/live_usage/LIVE-2026-09-29.json")
    byte_copy("docs/live_usage/LIVE-2026-09-29.md", w)
    byte_copy("docs/live_usage/LIVE-latest.json", w)
    byte_copy("docs/live_usage/LIVE-latest.md", w)
    # dashboard json probe -> js whole-byte same-side decision via its own probe
    w = take_newer_json("results/dashboard_status.json")
    b2, b3 = blob("2", "results/dashboard_status.js"), blob("3", "results/dashboard_status.js")
    jw = w  # same producer run; keep side coupled with the json twin
    side = b2 if jw == "2" else b3
    write_bytes("results/dashboard_status.js", side)
    print(f"[js-wrapper:dashboard_status.js] side :{jw}: coupled with .json twin ({len(side)}B)")
    # parse-verify all written jsons (r185)
    for p in ("results/fundamental_b_layer_filter.json", "results/scorecard_v1.json",
              "results/strategy_scorecard.json", "docs/daily_report/REPORT-2026-09-29.json",
              "docs/live_usage/LIVE-2026-09-29.json", "docs/live_usage/LIVE-latest.json",
              "results/dashboard_status.json"):
        json.loads(open(p, "rb").read().decode("utf-8"))
    js = open("results/dashboard_status.js", "rb").read().decode("utf-8")
    json.loads(js.split("=", 1)[1].rsplit(";", 1)[0].strip())
    print("[verify] all faces parse-verified OK")


if __name__ == "__main__":
    main()
