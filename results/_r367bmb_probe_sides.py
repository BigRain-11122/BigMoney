"""r367 bm-b push-storm resolver: probe both sides of UU files (stage2=ours=origin/bm-a r391+bm-c r145, stage3=theirs=local r366)."""
import subprocess, json, sys, re

UU = [
 "docs/daily_report/REPORT-2026-09-28.json","docs/daily_report/REPORT-2026-09-28.md",
 "results/compute_audit.json","results/daily_scorecard.json","results/dashboard_status.js",
 "results/dashboard_status.json","results/fundamental_b_layer_filter.json","results/futures_update_status.json",
 "results/lhb_update_status.json","results/paper/COMPOSITE-CE-01_paper.json","results/paper/COMPOSITE-CE-02_paper.json",
 "results/paper/DROUGHT-CE-01_paper.json","results/paper/ENGULF-CE-01_paper.json","results/paper/NEEDLE-DE-01_paper.json",
 "results/paper/VOLATILITY-CE-01_paper.json","results/paper_export/export-2026-09-24.json","results/paper_export/latest.json",
 "results/prospect_paper/_summary.json","results/prospect_promotion/_summary.json","results/regime_state.json",
 "results/t35_open_fill_verify.json","results/token_usage.json","results/update_status.json","results/x2_watch_log.jsonl",
]

def blob(stage, path):
    r = subprocess.run(["git","show",":%d:%s"%(stage,path)],capture_output=True)
    return r.stdout if r.returncode==0 else None

TS_RE = re.compile(rb'"(generated|updated|asof|date|run_ts|ts|time|cutoff)"\s*:\s*"([^"]{4,40})"')

def tsfields(b, limit=6):
    if b is None: return "MISSING"
    hits = TS_RE.findall(b)[:limit]
    return "; ".join(k.decode()+"="+v.decode() for k,v in hits) or "-"

def summar(path):
    o, t = blob(2,path), blob(3,path)
    print("="*100)
    print("UU", path)
    print("  ours(stage2,origin r391/r145): %dB | %s" % (len(o) if o else -1, tsfields(o)))
    print("  theirs(stage3,local r366)  : %dB | %s" % (len(t) if t else -1, tsfields(t)))
    if o and t:
        if o == t: print("  IDENTICAL bytes")
        else:
            # for json, show top-level key diff
            try:
                jo, jt = json.loads(o), json.loads(t)
                if isinstance(jo,dict) and isinstance(jt,dict):
                    common = set(jo)&set(jt); diffk=[k for k in common if jo[k]!=jt[k]]
                    print("  dict-diff keys:", sorted(diffk)[:12], "| only-ours:", sorted(set(jo)-set(jt))[:8], "| only-theirs:", sorted(set(jt)-set(jo))[:8])
                    for k in sorted(diffk)[:3]:
                        so, st = json.dumps(jo[k],ensure_ascii=False), json.dumps(jt[k],ensure_ascii=False)
                        print("    [%s] ours=%s" % (k, so[:220]))
                        print("    [%s] thrs=%s" % (k, st[:220]))
            except Exception as e:
                print("  (not plain json both sides: %s)" % e)
                lo, lt = o.splitlines(), t.splitlines()
                print("  lines: ours=%d theirs=%d" % (len(lo),len(lt)))
                import difflib
                dl = [l for l in difflib.unified_diff([x.decode('utf-8','replace') for x in lo],[x.decode('utf-8','replace') for x in lt],lineterm='')][2:14]
                for l in dl: print("   ",l[:200])

for p in UU: summar(p)
