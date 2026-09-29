"""r430 bm-a rebase-replay manual resolver (batch 2): snapshot / twin-regen / js-wrapper faces.

Classifier output (bigmoney-conflict-resolve skill):
- fundamental_b_layer_filter.json  snapshot take-new by 'updated' (r216)
- prospect_promotion/_summary.json snapshot take-new deep-ts probe (r350/r103)
- dashboard_status.json            snapshot take-new (R208)
- dashboard_status.js              js-wrapper-snapshot take-side whole bytes (R209)
- REPORT-2026-09-29.json/.md       twin-regen-md: json probe decides, md byte-copy same side (r327/r329)
- LIVE-2026-09-29.json/.md + LIVE-latest.json/.md  twin faces, same producer -> same side as LIVE-0929 probe

Laws applied: stage blobs not working tree (R350); probe path existence first (r319);
deep-scan nested layers for ts (r311); json+md twins MUST take same side (r329);
resolver machine-suffixed name to avoid clobbering replayed commit's resolver (pit-106).
"""
import json
import re
import subprocess

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def blob(stage: str, path: str) -> bytes:
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"git show :{stage}:{path} failed: {r.stderr.decode()[:200]}")
    return r.stdout


def deep_ts(obj, best=""):
    """Deep-scan nested layers for wall-clock ts values (r311); time-of-day required (R350)."""
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
        raise SystemExit(f"{path}: no ts probe found either side, refuse blind pick")
    winner, side = ("2", b2) if t2 >= t3 else ("3", b3)
    write_bytes(path, side)
    print(f"[take-new:{path}] :2:ts={t2!r} :3:ts={t3!r} -> side :{winner}: ({len(side)}B)")
    return winner


def byte_copy(path, winner):
    side = blob("2", path) if winner == "2" else blob("3", path)
    write_bytes(path, side)
    print(f"[twin-copy:{path}] byte-copied from side :{winner}: ({len(side)}B)")


def main():
    jobs = [
        ("results/fundamental_b_layer_filter.json", None, None),
        ("results/prospect_promotion/_summary.json", None, None),
        ("docs/daily_report/REPORT-2026-09-29.json", "docs/daily_report/REPORT-2026-09-29.md", None),
        ("docs/live_usage/LIVE-2026-09-29.json", "docs/live_usage/LIVE-2026-09-29.md",
         ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md")),
    ]
    for jpath, md, latest in jobs:
        w = take_newer_json(jpath)
        if md:
            byte_copy(md, w)
        if latest:
            byte_copy(latest[0], w)
            byte_copy(latest[1], w)
    # js wrapper: whole-byte take-side (R209: never re-emit via json.dumps)
    b2, b3 = blob("2", "results/dashboard_status.js"), blob("3", "results/dashboard_status.js")
    t2 = deep_ts(b2.decode("utf-8", "replace").replace('"', ""))
    t3 = deep_ts(b3.decode("utf-8", "replace").replace('"', ""))
    jw = "2" if t2 >= t3 else "3"
    write_bytes("results/dashboard_status.js", b2 if jw == "2" else b3)
    print(f"[js-wrapper:dashboard_status.js] :2:ts={t2!r} :3:ts={t3!r} -> side :{jw}:")
    # dashboard_status.json take-new
    take_newer_json("results/dashboard_status.json")
    # parse-verify every written json (r185)
    for jpath, _, latest in jobs:
        json.loads(open(jpath, "rb").read().decode("utf-8"))
        if latest:
            json.loads(open(latest[0], "rb").read().decode("utf-8"))
    js_text = open("results/dashboard_status.js", "rb").read().decode("utf-8")
    json.loads(js_text.split("=", 1)[1].rsplit(";", 1)[0].strip())
    print("[verify] all written faces parse-verified OK")


if __name__ == "__main__":
    main()
