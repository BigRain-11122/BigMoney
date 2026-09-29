# r415 bm-b: probe both staged blobs of UU files for freshness ts (read-only)
# Rebase semantics: :2: = ours = upstream (bm-c r203 / origin), :3: = theirs = replayed bm-b r414
import subprocess, json, sys

FILES = [
    "docs/daily_report/REPORT-2026-09-29.json",
    "docs/daily_report/REPORT-2026-09-29.md",
    "docs/live_usage/LIVE-2026-09-29.json",
    "docs/live_usage/LIVE-2026-09-29.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

def blob(path, stage):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def deep_ts(obj, best=None, path=""):
    # hardened deep scan: any key (normalized: strip _ -) matching asof/generated/updated/cutoff/ts
    # value must be ts-shaped ^20\d{2}- AND contain time-of-day for wall-clock compare (R350)
    import re
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = str(k).replace("_", "").replace("-", "").lower()
            if isinstance(v, str) and re.match(r"^20\d{2}-", v):
                has_tod = bool(re.search(r"[T ]\d{2}:\d{2}", v))
                is_ts_key = any(nk.startswith(p) for p in ("asof", "generated", "updated", "cutoff", "timestamp")) or nk in ("ts",)
                if is_ts_key and has_tod:
                    cand = v.replace("T", " ").replace("+", " +")
                    if best is None or cand > best[0]:
                        best = (cand, path + "/" + str(k))
            deep_ts(v, best if best is None else best, path + "/" + str(k)) if False else None
            b2 = deep_ts(v, None, path + "/" + str(k))
            if b2 and (best is None or b2[0] > best[0]):
                best = b2
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            b2 = deep_ts(v, None, path + "/%d" % i)
            if b2 and (best is None or b2[0] > best[0]):
                best = b2
    return best

def probe(path):
    out = {}
    for stage, tag in ((2, "origin(r203)"), (3, "bm-b(r414)")):
        raw = blob(path, stage)
        if raw is None:
            out[tag] = "MISSING"
            continue
        # try json
        ts = None
        txt = raw.decode("utf-8", "replace")
        try:
            j = json.loads(txt)
            ts = deep_ts(j)
        except Exception:
            # md / js: regex first ts-looking line
            import re
            m = re.search(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", txt)
            ts = (m.group(0), "regex") if m else None
        out[tag] = ts
    return out

for f in FILES:
    p = probe(f)
    o, b = p.get("origin(r203)"), p.get("bm-b(r414)")
    pick = "?"
    if isinstance(o, tuple) and isinstance(b, tuple):
        pick = "origin" if o[0] > b[0] else ("bm-b" if b[0] > o[0] else "TIE->origin(HEAD)")
    print("%-55s origin=%s bm-b=%s => %s" % (f, o, b, pick))
