# -*- coding: utf-8 -*-
"""r764 bm-a rebase-resolve: 2 snapshot scorecard twins (bm-b r767 S6 vs bm-a r763 S6 same-window).
Laws applied:
- r98/r99: same-family re-derivation snapshot -> take-new byte-verbatim by deep-ts probe.
- r100: normalize key stripping '_'/'-' before prefix match; candidate value must be ts-shaped (^20\\d{2}-) before max-compare.
- R350: key-EXCLUDE lists forbidden; wall-clock max requires time-of-day ([T ]HH:MM) in value; date-only values never feed the max.
- r756: normalize separator (space->T) + parse before compare; NEVER raw string compare (mixed T+08:00 vs space-no-offset faces).
- probe STAGED blobs (:2: base_side=origin, :3: replay_side=mine), never working tree.
Stage with -c core.autocrlf=false to preserve blob byte-face (r343 law)."""
import subprocess, json, re, sys
from datetime import datetime

FACES = ["results/scorecard_v1.json", "results/strategy_scorecard.json"]
TS_RE = re.compile(r"^20\d{2}-")
TS_PREFIX_KEYS = ("generated", "updated", "asof", "stateupdated", "ts", "asof")

def blob(stage_ref, path):
    r = subprocess.run(["git", "show", "%s:%s" % (stage_ref, path)], capture_output=True)
    if r.returncode != 0:
        sys.stderr.write("show %s:%s rc=%d %s" % (stage_ref, path, r.returncode, r.stderr[:200]))
    return r.stdout

def parse_ts(v):
    """Normalize space->T then isoformat parse; return None if not full wall-clock ts."""
    if not isinstance(v, str) or not TS_RE.match(v):
        return None
    s = v.strip().replace(" ", "T")
    # R350: wall-clock max requires time-of-day
    if "T" not in s or not re.search(r"\d{2}:\d{2}", s):
        return None
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        try:
            return datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return None

def deep_ts_probe(obj, best=None):
    """Recursively collect all ts-shaped wall-clock values under ts-prefix keys; return max datetime."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = re.sub(r"[_-]", "", str(k)).lower()
            if isinstance(v, str) and any(nk.startswith(p) for p in TS_PREFIX_KEYS):
                t = parse_ts(v)
                if t is not None and (best is None or t > best):
                    best = t
            best = deep_ts_probe(v, best)
    elif isinstance(obj, list):
        for it in obj:
            best = deep_ts_probe(it, best)
    return best

def stage(path, data):
    with open(path, "wb") as f:
        f.write(data)
    subprocess.run(["git", "-c", "core.autocrlf=false", "add", path], check=True)

receipt = {}
for p in FACES:
    a = blob(":2", p)  # origin/base side (":2" + ":" + path = :2:path)
    m = blob(":3", p)  # my replay side
    ja, jm = json.loads(a.decode("utf-8")), json.loads(m.decode("utf-8"))
    ta, tm = deep_ts_probe(ja), deep_ts_probe(jm)
    assert ta is not None and tm is not None, (p, "probe miss both sides")
    if tm >= ta:
        winner, side, blob_data = tm, "replay-side(mine bm-a)", m
    else:
        winner, side, blob_data = ta, "base-side(origin bm-b)", a
    stage(p, blob_data)
    json.loads(blob_data.decode("utf-8"))  # parse-verify r185
    receipt[p] = {"origin_max_ts": str(ta), "mine_max_ts": str(tm), "took": side}
    print("%s: origin max-ts %s | mine max-ts %s -> take %s" % (p, ta, tm, side))

with open("results/_r764bma_resolve_receipt.json", "w", encoding="utf-8") as f:
    json.dump({"round": "r764", "faces": receipt,
               "laws": "r98/r99/r100/R350/r756 deep-ts take-new, staged-blob probe"},
              f, ensure_ascii=False, indent=1)
print("receipt written results/_r764bma_resolve_receipt.json")
