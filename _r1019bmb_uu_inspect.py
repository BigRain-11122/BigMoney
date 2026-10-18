# r1019 UU inspect: HEAD (origin tip after FF) vs stash side (my local churn)
# ASCII only. Read-only.
import subprocess, json, re

def side(rev, path):
    r = subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True)
    return r.stdout.decode('utf-8', errors='replace')

def sniff(txt, label):
    m = re.search(r'"ts"\s*:\s*"([^"]+)"', txt)
    ts = m.group(1) if m else 'NO-TS'
    try:
        obj = json.loads(txt)
        keys = list(obj.keys())[:8]
        info = json.dumps({k: (type(obj[k]).__name__ if not isinstance(obj[k], dict)
                               else 'dict:' + ','.join(list(obj[k].keys())[:4]))
                           for k in keys})
    except Exception as e:
        return f'{label}: ts={ts} PARSE-FAIL {e}'
    return f'{label}: ts={ts} keys={info}'

for path in ['fleet/machine-health.json', 'results/futures_update_status.json',
             'results/lhb_update_status.json', 'results/watermark_red.json',
             'results/token_usage.json']:
    print('== ' + path)
    print('  ' + sniff(side('HEAD', path), 'HEAD-origin'))
    print('  ' + sniff(side('stash@{0}', path), 'stash-local'))
