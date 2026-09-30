# r473 bm-b rebase-collision forensic inspect: dump stage2(ours=bm-a r483) vs stage3(theirs=bm-b r472) evidence
import subprocess, json, io, sys, hashlib

UU = [
    "CODELY.md",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
    "Money02/data/lhb/chunks/2026Q3.parquet",
    "Money02/data/lhb/lhb_detail.parquet",
    "docs/daily_report/REPORT-2026-09-30.json",
    "docs/daily_report/REPORT-2026-09-30.md",
    "docs/live_usage/LIVE-2026-09-30.json",
    "docs/live_usage/LIVE-2026-09-30.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
]

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

TS_KEYS = ["generated", "generated_at", "updated", "updated_at", "ts", "timestamp",
           "asof", "as_of", "cutoff", "evidence_cutoff", "scan_time", "run_time", "time"]

def ts_probe(obj, depth=0):
    hits = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (str, int, float)) and k in TS_KEYS:
                hits[k] = v
            elif isinstance(v, dict) and depth < 2:
                for kk, vv in ts_probe(v, depth + 1).items():
                    hits[k + "." + kk] = vv
    return hits

out = {}
for p in UU:
    a, b = blob(2, p), blob(3, p)
    rec = {"ours_bytes": len(a) if a else None, "theirs_bytes": len(b) if b else None}
    rec["ours_sha12"] = hashlib.sha256(a).hexdigest()[:12] if a else None
    rec["theirs_sha12"] = hashlib.sha256(b).hexdigest()[:12] if b else None
    if p.endswith(".parquet"):
        import pandas as pd
        try:
            da = pd.read_parquet(io.BytesIO(a))
            db = pd.read_parquet(io.BytesIO(b))
            rec["rows"] = [len(da), len(db)]
            rec["cols"] = list(da.columns)[:8]
            datecol = None
            for c in da.columns:
                lc = str(c).lower()
                if "date" in lc or "日" in str(c) or "day" in lc:
                    datecol = c
                    break
            if datecol is not None:
                rec["maxdate"] = [str(da[datecol].max()), str(db[datecol].max())]
                rec["mindate"] = [str(da[datecol].min()), str(db[datecol].min())]
            ka = da.astype(str).apply("|".join, axis=1)
            kb = db.astype(str).apply("|".join, axis=1)
            rec["dup_rows"] = int(len(set(ka) & set(kb)))
            rec["ours_only"] = int(len(set(ka) - set(kb)))
            rec["theirs_only"] = int(len(set(kb) - set(ka)))
        except Exception as e:
            rec["parquet_err"] = repr(e)[:200]
    elif p.endswith(".json") or p.endswith(".js"):
        ja = jb = None
        try:
            ja = json.loads(a)
            rec["ours_ts"] = ts_probe(ja)
        except Exception as e:
            rec["ours_json_err"] = repr(e)[:120]
        try:
            jb = json.loads(b)
            rec["theirs_ts"] = ts_probe(jb)
        except Exception as e:
            rec["theirs_json_err"] = repr(e)[:120]
        for side, jj in (("ours", ja), ("theirs", jb)):
            if isinstance(jj, dict):
                led = [k for k, v in jj.items() if isinstance(v, list)]
                if led:
                    rec[side + "_listkeys_len"] = {k: len(jj[k]) for k in led}
    else:
        rec["ours_lines"] = len(a.decode("utf-8", "replace").splitlines()) if a else None
        rec["theirs_lines"] = len(b.decode("utf-8", "replace").splitlines()) if b else None
    out[p] = rec

print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
