"""r689 bm-b merge resolver: 16 S6 regen faces (bm-a r692 + bm-c r492 wave vs
my 19:16-19:18 regen). Canon: git show HEAD:/MERGE_HEAD: raw bytes (r657-2),
ts-normalized newer-wins (r461/r505 — ts_norm before compare), md/js twins
aligned to json decision (r681), dashboard_status.json nested ts probe
(meta.generated_at), token_usage per-key machines union with side_pick assert
+ whole-face ts fallback (r456/r466). Receipt -> results/_r689bmb_merge_resolve.json.
Lineage: r686 resolver verified in-source (r682 law) + 4 new faces."""
import datetime
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git_bytes(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT,
                       capture_output=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(f"git show {rev}:{path} rc={r.returncode} "
                           f"{r.stderr.decode('utf-8', 'replace')[:200]}")
    return r.stdout


def ts_norm(v):
    if v is None:
        return ""
    s = str(v).replace("T", " ")
    return s[:19]


def face_ts(obj):
    for k in ("ts", "updated", "updated_at", "generated", "generated_at",
              "asof", "cutoff", "last_run", "scan_ts"):
        if isinstance(obj, dict) and k in obj and obj[k]:
            return ts_norm(obj[k]), k
    return "", None


def dash_ts(obj):
    # dashboard_status.json: ts nested at meta.generated_at
    try:
        m = obj.get("meta", {})
        for k in ("generated_at", "generated", "ts", "updated"):
            if isinstance(m, dict) and k in m and m[k]:
                return ts_norm(m[k]), "meta." + k
    except Exception:
        pass
    return "", None


TS_FACES = [
    ("docs/daily_report/REPORT-2026-10-04.json", face_ts),
    ("docs/live_usage/LIVE-2026-10-04.json", face_ts),
    ("docs/live_usage/LIVE-latest.json", face_ts),
    ("results/_attrition_guard_scan.json", face_ts),
    ("results/compute_audit.json", face_ts),
    ("results/dashboard_status.json", dash_ts),
    ("results/fundamental_b_layer_filter.json", face_ts),
    ("results/futures_update_status.json", face_ts),
    ("results/lhb_update_status.json", face_ts),
    ("results/regime_state.json", face_ts),
    ("results/scorecard_v1.json", face_ts),
    ("results/strategy_scorecard.json", face_ts),
    ("results/update_status.json", face_ts),
]
TWIN_MD = {
    "docs/daily_report/REPORT-2026-10-04.json": "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json": "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json": "docs/live_usage/LIVE-latest.md",
    "results/dashboard_status.json": "results/dashboard_status.js",
}
TOKEN = "results/token_usage.json"

# mid-merge sanity
assert subprocess.run(["git", "rev-parse", "--verify", "MERGE_HEAD"],
                      cwd=ROOT, capture_output=True).returncode == 0, "MERGE_HEAD absent"

receipt = {"resolver": "r689 bm-b merge", "faces": {}, "ts": datetime.datetime.now().isoformat(timespec="seconds")}
decisions = {}

for path, tsfn in TS_FACES:
    ours_b = git_bytes("HEAD", path)
    theirs_b = git_bytes("MERGE_HEAD", path)
    ours = json.loads(ours_b.decode("utf-8"))
    theirs = json.loads(theirs_b.decode("utf-8"))
    o_ts, o_k = tsfn(ours)
    t_ts, t_k = tsfn(theirs)
    if o_ts and t_ts:
        side = "ours" if o_ts > t_ts else "theirs"
    else:
        side = "theirs" if not o_ts else "ours"  # missing-ts fallback: keep the side that has ts
        if not o_ts and not t_ts:
            side = "theirs"  # regen face origin-presumption (r505)
    chosen = ours_b if side == "ours" else theirs_b
    open(os.path.join(ROOT, path), "wb").write(chosen)
    decisions[path] = side
    receipt["faces"][path] = {"side": side, "ours_ts": o_ts, "theirs_ts": t_ts,
                              "ts_key": o_k or t_k}
    twin = TWIN_MD.get(path)
    if twin:
        tb = git_bytes("HEAD", twin) if side == "ours" else git_bytes("MERGE_HEAD", twin)
        open(os.path.join(ROOT, twin), "wb").write(tb)
        decisions[twin] = side
        receipt["faces"][twin] = {"side": side, "aligned_to": path}

# token_usage.json: per-key machines union (r456) + top ts newer + side_pick assert
ours = json.loads(git_bytes("HEAD", TOKEN).decode("utf-8"))
theirs = json.loads(git_bytes("MERGE_HEAD", TOKEN).decode("utf-8"))
o_ts, _ = face_ts(ours)
t_ts, _ = face_ts(theirs)
base, other = (ours, theirs) if (o_ts or "0") > (t_ts or "0") else (theirs, ours)
merged = dict(base)
om = ours.get("machines", {})
tm = theirs.get("machines", {})
mm = dict(om)
picks = {"ours": 0, "theirs": 0}
for k, v in tm.items():
    if k in mm:
        ko_ts, _ = face_ts(mm[k])
        kt_ts, _ = face_ts(v)
        if kt_ts and (not ko_ts or kt_ts > ko_ts):
            mm[k] = v
            picks["theirs"] += 1
        else:
            picks["ours"] += 1
    else:
        mm[k] = v
        picks["theirs"] += 1
for k, v in om.items():
    if k not in mm:
        picks["ours"] += 1
merged["machines"] = mm
if picks["ours"] == 0 and picks["theirs"] == 0:
    # zero side-pick -> whole-face ts freshness fallback (r456 law)
    side = "ours" if (o_ts or "0") > (t_ts or "0") else "theirs"
    merged = json.loads((git_bytes("HEAD", TOKEN) if side == "ours"
                         else git_bytes("MERGE_HEAD", TOKEN)).decode("utf-8"))
    receipt["faces"][TOKEN] = {"side": f"whole-face-{side} (side_pick=0 fallback)",
                               "ours_ts": o_ts, "theirs_ts": t_ts}
else:
    receipt["faces"][TOKEN] = {"side": "per-key-union", "picks": picks,
                               "ours_ts": o_ts, "theirs_ts": t_ts,
                               "machine_keys": sorted(mm.keys())}
open(os.path.join(ROOT, TOKEN), "wb").write(
    (json.dumps(merged, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
decisions[TOKEN] = "union"

# verify: no markers in any resolved face, all json parse
bad = []
for path in list(decisions.keys()):
    data = open(os.path.join(ROOT, path), "rb").read()
    if b"<<<<<<<" in data or b">>>>>>>" in data:
        bad.append(path)
    if path.endswith(".json"):
        try:
            json.loads(data.decode("utf-8"))
        except Exception as exc:
            bad.append(f"{path} PARSE {exc}")
assert not bad, f"verification failed: {bad}"
receipt["verification"] = "markers-clean + all-json-parse OK"
open(os.path.join(ROOT, "results", "_r689bmb_merge_resolve.json"), "wb").write(
    (json.dumps(receipt, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
print(json.dumps({"decisions": decisions, "picks": receipt["faces"].get(TOKEN, {}).get("picks"),
                  "verification": "OK"}, ensure_ascii=False, indent=1))
