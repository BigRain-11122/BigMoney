# r99 bm-c API push wave-2: advance machine/bm-c-r99 to addendum commit (CODELY.md pitlaw row + api_push evidence script)
# base = 8f79af01 (wave-1 remote machine branch head, tree 56f01475); expect final tree == local 98c80a95 (byte-identity proof)
import subprocess, json, io, os, base64

repo = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(repo)
OWNER_REPO = 'repos/BigRain-11122/bigmoney'
BASE = '8f79af01'
BASE_TREE = '56f014750d54e6c66910c43e02c7e5cffe673ab4'

def gh(*args):
    r = subprocess.run(['gh', 'api'] + list(args), capture_output=True, text=True, encoding='utf-8')
    if r.returncode != 0:
        raise RuntimeError('gh api failed: %s %s' % (args, r.stderr[:300]))
    return r.stdout

def gh_json(endpoint, body, verb='POST'):
    tmp = repo + r'\.codely-cli\scratch\_api_body2.json'
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    with io.open(tmp, 'w', encoding='utf-8') as f:
        json.dump(body, f, ensure_ascii=False)
    return json.loads(gh('-X', verb, endpoint, '--input', tmp))

tree_entries = []
for path in ['CODELY.md', 'results/_r099bmc_api_push.py']:
    r = subprocess.run(['git', 'show', 'HEAD:' + path], capture_output=True)
    assert r.returncode == 0, path
    blob = gh_json('/%s/git/blobs' % OWNER_REPO, {'content': base64.b64encode(r.stdout).decode('ascii'), 'encoding': 'base64'})
    tree_entries.append({'path': path, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
    print('blob ok', path, '->', blob['sha'][:8])

tree = gh_json('/%s/git/trees' % OWNER_REPO, {'base_tree': BASE_TREE, 'tree': tree_entries})
print('tree=%s (local expect 98c80a95...)' % tree['sha'])

msg = subprocess.run(['git', 'log', '-1', '--format=%B', 'HEAD'], capture_output=True, text=True, encoding='utf-8').stdout.strip()
commit = gh_json('/%s/git/commits' % OWNER_REPO, {'message': msg, 'tree': tree['sha'], 'parents': [BASE]})
print('commit=%s' % commit['sha'])

ref = gh_json('/%s/git/refs/heads/machine/bm-c-r99' % OWNER_REPO, {'sha': commit['sha'], 'force': False}, verb='PATCH')
print('ref advanced: %s -> %s' % (ref['ref'], ref['object']['sha']))

rb = json.loads(gh('/%s/commits/machine/bm-c-r99' % OWNER_REPO))
local_tree = subprocess.run(['git', 'rev-parse', 'HEAD^{tree}'], capture_output=True, text=True).stdout.strip()
print('readback tree=%s local tree=%s match=%s' % (rb['commit']['tree']['sha'], local_tree, rb['commit']['tree']['sha'] == local_tree))
print('WAVE2 DONE')
