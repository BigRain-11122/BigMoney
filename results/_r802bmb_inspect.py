import subprocess, json, sys

FILES = ['results/compute_audit.json','results/regime_state.json','results/token_usage.json',
         'results/update_status.json','results/futures_update_status.json','results/lhb_update_status.json',
         'results/fundamental_b_layer_filter.json','results/_attrition_guard_scan.json',
         'docs/daily_report/REPORT-2026-10-07.json','docs/live_usage/LIVE-2026-10-07.json',
         'docs/live_usage/LIVE-latest.json']

def stages_of(path):
    out = subprocess.run(['git','ls-files','-u','--',path],capture_output=True,text=True).stdout
    res = {}
    for line in out.strip().split('\n'):
        if not line.strip():
            continue
        meta, _, fpath = line.partition('\t')
        parts = meta.split()
        # mode SP sha SP stage
        if len(parts) >= 3:
            res[parts[2]] = parts[1]
    return res

def blob(sha):
    return subprocess.run(['git','cat-file','-p',sha],capture_output=True).stdout

for f in FILES:
    st = stages_of(f)
    print(f'== {f} stages={sorted(st.keys())}')
    for s in sorted(st.keys()):
        raw = blob(st[s])
        try:
            j = json.loads(raw)
            if isinstance(j, dict):
                tskeys = [k for k in j if any(t in k.lower() for t in ('ts','time','date','generated','cutoff','epoch'))]
                print(f'  st{s}: topkeys={list(j.keys())[:10]}')
                for k in tskeys[:8]:
                    print(f'     {k}={str(j[k])[:60]}')
            else:
                print(f'  st{s}: type={type(j).__name__} len={len(j)}')
        except Exception as e:
            print(f'  st{s}: PARSE-ERR {str(e)[:60]} head={raw[:60]!r}')
