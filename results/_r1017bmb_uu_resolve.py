"""r1017 bm-b stash-pop UU resolver (3 daemon faces).
Laws: machine-health origin-wins (r1015 precedent, local rows re-land next daemon tick);
watermark_red ts-newer-wins (r1028); token_usage per-machine union (r1008).
Resolution leaves the faces UNSTAGED (daemon live-writer policy -- never committed by bm-b)."""
import io
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


def sh(args):
    r = subprocess.run(['git'] + args, capture_output=True)
    return r.stdout


def head_blob(path):
    return sh(['show', 'HEAD:' + path]).decode('utf-8', 'replace')


# 1) machine-health: origin-wins -> worktree = HEAD version, unstage
subprocess.run(['git', 'checkout', '--ours', '--', 'fleet/machine-health.json'], capture_output=True)
subprocess.run(['git', 'restore', '--staged', '--', 'fleet/machine-health.json'], capture_output=True)
print('machine-health: origin-wins (worktree=HEAD, unstaged)')

# 2) watermark_red: ts-newer-wins
wr_local = sh(['checkout', '--theirs', '--', 'results/watermark_red.json'])  # noop capture
# read stashed-local version from the stash itself? --theirs already wrote it to worktree pre-checkout.
# simpler: after checkout --theirs the worktree holds the local (stashed) version; compare with HEAD.
subprocess.run(['git', 'checkout', '--theirs', '--', 'results/watermark_red.json'], capture_output=True)
with io.open('results/watermark_red.json', encoding='utf-8') as f:
    local = json.load(f)
head = json.loads(head_blob('results/watermark_red.json'))
lt, ht = str(local.get('ts', '')), str(head.get('ts', ''))
winner = 'local' if lt >= ht else 'head'
final = local if winner == 'local' else head
with io.open('results/watermark_red.json', 'w', encoding='utf-8') as f:
    json.dump(final, f, ensure_ascii=False, indent=1)
subprocess.run(['git', 'restore', '--staged', '--', 'results/watermark_red.json'], capture_output=True)
print('watermark_red: %s wins (local ts=%s vs head ts=%s)' % (winner, lt, ht))

# 3) token_usage: per-machine union -- base=HEAD, overlay local bm-b rows
subprocess.run(['git', 'checkout', '--theirs', '--', 'results/token_usage.json'], capture_output=True)
with io.open('results/token_usage.json', encoding='utf-8') as f:
    local_tu = json.load(f)
head_tu = json.loads(head_blob('results/token_usage.json'))
changed = 0
if isinstance(local_tu.get('machines'), dict):
    head_tu.setdefault('machines', {})
    for k, v in local_tu['machines'].items():
        if k == 'bm-b' or k not in head_tu['machines']:
            if head_tu['machines'].get(k) != v:
                head_tu['machines'][k] = v
                changed += 1
if isinstance(local_tu.get('l2_local_llm'), dict):
    head_tu.setdefault('l2_local_llm', {})
    for k, v in local_tu['l2_local_llm'].items():
        if k == 'bm-b' and head_tu['l2_local_llm'].get(k) != v:
            head_tu['l2_local_llm'][k] = v
            changed += 1
with io.open('results/token_usage.json', 'w', encoding='utf-8') as f:
    json.dump(head_tu, f, ensure_ascii=False, indent=1)
subprocess.run(['git', 'restore', '--staged', '--', 'results/token_usage.json'], capture_output=True)
print('token_usage: per-machine union applied, overlaid rows=%d' % changed)

print('resolver done')
