import json
d=json.load(open('results/update_status.json',encoding='utf-8')); print('update_status.updated=',d['updated'])
c=json.load(open('results/compute_audit.json',encoding='utf-8')); print('ca latest.ts=',c['latest']['ts'],'history n=',len(c['history']))
r=json.load(open('results/regime_state.json',encoding='utf-8')); print('regime updated=',r['updated'])
print('x2 lines=',sum(1 for _ in open('results/x2_watch_log.jsonl',encoding='utf-8')))
p=json.load(open('results/prospect_paper/_summary.json',encoding='utf-8')); print('prospect gen=',p['generated'],'mode=',p.get('regime_guard_mode'))
ds=json.load(open('results/daily_scorecard.json',encoding='utf-8')); print('scorecard cutoff=',ds.get('cutoff') or ds.get('meta',{}).get('cutoff'))
js=open('results/dashboard_status.js','rb').read(); print('dash.js wrapper ok=',js.startswith(b'window.DASH_DATA = ') and js.rstrip().endswith(b';'))
