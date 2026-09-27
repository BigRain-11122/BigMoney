# r99 bm-c push via Git Data API direct-construct (SSH/HTTPS git data-plane both stalled, api.github.com verified alive):
# local f43df0c9 (rebased on 205b9e79) -> blobs -> tree(base_tree=205b9e79 tree) -> commit(parents=[205b9e79]) -> refs POST machine/bm-c-r99 (NO force, main untouched)
import subprocess, json, io, os, base64, sys

repo = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(repo)
OWNER_REPO = 'repos/BigRain-11122/bigmoney'
BASE_SHA = '205b9e79'  # full sha resolved below

def gh(*args, check=True):
    r = subprocess.run(['gh', 'api'] + list(args), capture_output=True, text=True, encoding='utf-8')
    if check and r.returncode != 0:
        raise RuntimeError('gh api failed: %s %s' % (args, r.stderr[:300]))
    return r.stdout

def gh_json(endpoint, body, method='-X', verb='POST'):
    tmp = repo + r'\.codely-cli\scratch\_api_body.json'
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    with io.open(tmp, 'w', encoding='utf-8') as f:
        json.dump(body, f, ensure_ascii=False)
    out = gh(method, verb, endpoint, '--input', tmp)
    return json.loads(out)

# 0) resolve full base sha + base tree
base_full = json.loads(gh('/%s/commits/%s' % (OWNER_REPO, BASE_SHA)))['sha']
base_tree = json.loads(gh('/%s/commits/%s' % (OWNER_REPO, BASE_SHA)))['commit']['tree']['sha']
print('base_full=%s base_tree=%s' % (base_full, base_tree))

# 1) changed files: local diff 205b9e79..HEAD (f43df0c9) -- all M/A, no D expected
dif = subprocess.run(['git', 'diff', '--name-status', BASE_SHA, 'HEAD'], capture_output=True, text=True, encoding='utf-8').stdout
entries_raw = [l.split('\t') for l in dif.splitlines() if l.strip()]
assert all(e[0] in ('M', 'A') for e in entries_raw), 'unexpected deletions in diff: %s' % dif
print('changed files:', len(entries_raw))

# 2) upload blobs (base64) + build tree entries
tree_entries = []
for st, path in entries_raw:
    r = subprocess.run(['git', 'show', 'HEAD:' + path.replace('\\', '/')], capture_output=True)
    assert r.returncode == 0, path
    content = base64.b64encode(r.stdout).decode('ascii')
    blob = gh_json('/%s/git/blobs' % OWNER_REPO, {'content': content, 'encoding': 'base64'})
    tree_entries.append({'path': path.replace('\\', '/'), 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
    print('blob ok %s -> %s' % (path, blob['sha'][:8]))

# 3) tree with base_tree
tree = gh_json('/%s/git/trees' % OWNER_REPO, {'base_tree': base_tree, 'tree': tree_entries})
print('tree=%s' % tree['sha'])

# 4) commit
msg = subprocess.run(['git', 'log', '-1', '--format=%B', 'HEAD'], capture_output=True, text=True, encoding='utf-8').stdout.strip()
commit = gh_json('/%s/git/commits' % OWNER_REPO, {'message': msg, 'tree': tree['sha'], 'parents': [base_full]})
print('commit=%s' % commit['sha'])

# 5) ref: machine/bm-c-r99 (POST new branch, no force)
ref = gh_json('/%s/git/refs' % OWNER_REPO, {'ref': 'refs/heads/machine/bm-c-r99', 'sha': commit['sha']})
print('ref created: %s -> %s' % (ref['ref'], ref['object']['sha']))

# 6) verify: remote branch tip content == local HEAD tree (tree sha compare via remote commit readback)
rb = json.loads(gh('/%s/commits/machine/bm-c-r99' % OWNER_REPO))
print('remote readback tree=%s (expect %s) match=%s' % (rb['commit']['tree']['sha'], tree['sha'], rb['commit']['tree']['sha'] == tree['sha']))
print('API PUSH DONE r99 bm-c machine branch')
