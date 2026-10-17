import json, re, subprocess

def get(ref, path):
    r = subprocess.run(['git', 'show', ref + ':' + path], capture_output=True)
    return r.stdout.decode('utf-8', errors='replace')

for path in ['fleet/machine-health.json', 'results/watermark_red.json']:
    head = get('HEAD', path)
    stash = get('stash@{0}', path)
    def last_ts(s):
        m = re.findall(r'"ts"\s*:\s*"([^"]+)"', s)
        return m[-1] if m else 'NONE'
    def plain_ts(s):
        m = re.findall(r'20\d\d-\d\d-\d\d[T ][\d:.+]+', s)
        return m[-1] if m else 'NONE'
    print(path)
    print('  HEAD tail ts:', last_ts(head), '| plain:', plain_ts(head))
    print('  STASH tail ts:', last_ts(stash), '| plain:', plain_ts(stash))
