# -*- coding: utf-8 -*-
"""r650 bm-c rebase resolver: 15 UU faces vs bm-a r806 closeout wave (03:23:48).
Per-face law (r440 two-split + r648 sha-channel + r642 guard):
  - daily regen faces: per-face embedded-ts newer-wins (origin S6 ran 03:23+ vs mine 03:21)
  - token_usage.json: per-key max-union (r516-3 law)
  - compute_audit.json: history ts-key union (r570/r773 law)
  - marker scan = HARD GATE on every side taken (r648 law; pollution -> take clean side)
All blob reads via ls-files -u sha -> cat-file (r648: :N: reads can return empty+rc0)."""
import json, os, re, subprocess, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def git(*args, **kw):
    return subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True, **kw)

def blob_sha(path, stage):
    r = git("ls-files", "-u", "--", path)
    out = r.stdout.decode("utf-8", "replace")
    for line in out.splitlines():
        parts = line.split("\t")
        meta = parts[0].split()
        # format: <mode> <sha1> <stage>\t<path>  -> meta[1]=sha, meta[2]=stage
        if len(parts) >= 2 and meta[2] == str(stage) and parts[1] == path:
            return meta[1]
    return None

def read_blob(sha):
    r = git("cat-file", "-p", sha)
    if r.returncode != 0 or not r.stdout:
        raise SystemExit("blob read failed for %s (rc=%s len=%d)" % (sha, r.returncode, len(r.stdout or b"")))
    return r.stdout

MARKER = re.compile(rb"^(<{7}|={7}|>{7}) ", re.M)

def marker_clean(b):
    return not MARKER.search(b)

def ts_of(obj):
    for k in ("ts", "asof", "generated", "generated_at", "updated_at", "written_at", "scan_ts"):
        v = obj.get(k) if isinstance(obj, dict) else None
        if isinstance(v, str) and v:
            return v
    return ""

FACES_TAKE_NEWER = [
    "docs/daily_report/REPORT-2026-10-07.json",
    "docs/daily_report/REPORT-2026-10-07.md",
    "docs/live_usage/LIVE-2026-10-07.json",
    "docs/live_usage/LIVE-2026-10-07.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/update_status.json",
]
FACE_UNION_TOKEN = "results/token_usage.json"
FACE_UNION_AUDIT = "results/compute_audit.json"

report = {"asof_policy": "origin-newer-wins for regen faces (bm-a r806 S6 03:23+ vs bm-c 03:21); token per-key max-union; audit history ts-union; marker hard-gate both sides", "faces": {}}

def side_obj(path, stage):
    sha = blob_sha(path, stage)
    if sha is None:
        return None, None
    b = read_blob(sha)
    return b, sha

def pick_newer(path):
    b2, s2 = side_obj(path, 2)   # origin (rebase onto-side)
    b3, s3 = side_obj(path, 3)   # mine (replayed commit)
    if b2 is None and b3 is None:
        report["faces"][path] = "both-missing skip"
        return None
    if b2 is None:
        report["faces"][path] = "origin-missing take-mine"
        return b3
    if b3 is None:
        report["faces"][path] = "mine-missing take-origin"
        return b2
    m2, m3 = marker_clean(b2), marker_clean(b3)
    # ts compare
    def ts_bytes(b):
        try:
            o = json.loads(b.decode("utf-8-sig"))
            t = ts_of(o) if isinstance(o, dict) else ""
            if not t and isinstance(o, dict):
                t = ts_of(o.get("latest") or {}) or ""
            return t
        except Exception:
            m = re.search(rb'"(?:ts|generated|asof|generated_at)"\s*:\s*"([^"]+)"', b)
            return m.group(1).decode() if m else ""
    t2, t3 = ts_bytes(b2), ts_bytes(b3)
    take_origin = None
    if m2 and m3:
        if t2 and t3:
            take_origin = t2 >= t3
        else:
            take_origin = True  # unparseable ts: origin (host chain) wins by default
    elif m2 and not m3:
        take_origin = True
    elif m3 and not m2:
        take_origin = False
    else:
        raise SystemExit("both sides marker-polluted: %s" % path)
    report["faces"][path] = ("origin" if take_origin else "mine") + " (t2=%s t3=%s m2=%s m3=%s)" % (t2, t3, m2, m3)
    return b2 if take_origin else b3

def union_token(path):
    b2, _ = side_obj(path, 2)
    b3, _ = side_obj(path, 3)
    o2 = json.loads(b2.decode("utf-8-sig"))
    o3 = json.loads(b3.decode("utf-8-sig"))
    # per-key max-union: top-level dict of machine keys -> per-key newer ts wins
    if isinstance(o2, dict) and isinstance(o3, dict) and all(isinstance(v, dict) for v in list(o2.values())[:2]):
        merged = dict(o2)
        for k, v in o3.items():
            if k not in merged:
                merged[k] = v
            elif isinstance(v, dict) and isinstance(merged[k], dict):
                tv, tm = ts_of(v), ts_of(merged[k])
                if tv and (not tm or tv >= tm):
                    merged[k] = v
        out = merged
    else:
        # scalar/container face: newer ts wins
        t2, t3 = ts_of(o2), ts_of(o3)
        out = o2 if (t2 and (not t3 or t2 >= t3)) else o3
    report["faces"][path] = "per-key max-union"
    return json.dumps(out, indent=1, ensure_ascii=False).encode("utf-8")

def union_audit(path):
    b2, _ = side_obj(path, 2)
    b3, _ = side_obj(path, 3)
    o2 = json.loads(b2.decode("utf-8-sig"))
    o3 = json.loads(b3.decode("utf-8-sig"))
    h2 = o2.get("history") or []
    h3 = o3.get("history") or []
    seen = {}
    for row in h2 + h3:
        key = row.get("ts")
        if key is None:
            continue
        if key not in seen or str(row) > str(seen[key]):
            seen[key] = row
    merged_hist = [seen[k] for k in sorted(seen)]
    out = dict(o2)
    # latest = newer ts of the two
    l2, l3 = ts_of(o2.get("latest") or {}), ts_of(o3.get("latest") or {})
    out["latest"] = (o2.get("latest") or {}) if (l2 and (not l3 or l2 >= l3)) else (o3.get("latest") or {})
    out["history"] = merged_hist
    report["faces"][path] = "history ts-union %d rows (latest %s)" % (len(merged_hist), "origin" if out["latest"] is (o2.get("latest") or {}) else "mine")
    return json.dumps(out, indent=1, ensure_ascii=False).encode("utf-8")

resolved = {}
for p in FACES_TAKE_NEWER:
    b = pick_newer(p)
    if b is not None:
        resolved[p] = b
resolved[FACE_UNION_TOKEN] = union_token(FACE_UNION_TOKEN)
resolved[FACE_UNION_AUDIT] = union_audit(FACE_UNION_AUDIT)

for p, b in resolved.items():
    full = os.path.join(ROOT, p.replace("/", os.sep))
    with open(full, "wb") as fh:
        fh.write(b)
    print("resolved:", p, len(b), "bytes")

with open(os.path.join(ROOT, "results", "_r650bmc_merge_resolve.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, indent=1, ensure_ascii=False)
print("receipt written")
print(json.dumps(report["faces"], ensure_ascii=False, indent=1))
