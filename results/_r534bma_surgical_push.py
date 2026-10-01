"""r534 surgical push: replay local ride commit onto origin/main via temp index (r523/r519 net path)."""
import subprocess, sys, os

def run(args, env=None, capture=True):
    r = subprocess.run(args, capture_output=capture, env=env, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        print('FAIL:', ' '.join(args)); print(r.stdout); print(r.stderr); sys.exit(1)
    return r.stdout.strip()

repo = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
git = ['git', '-C', repo]
LOCAL_SHA = run(git + ['rev-parse', 'HEAD'])
run(git + ['fetch', 'origin'])
BASE = run(git + ['rev-parse', 'origin/main'])
print('local HEAD :', LOCAL_SHA)
print('origin/main:', BASE)

# files changed in my local commit (single commit ahead)
diff = run(git + ['diff-tree', '--no-commit-id', '--name-status', '-r', LOCAL_SHA])
print('payload:'); print(diff)

tmp_index = os.path.join(repo, '.git', '_r534_tmp_index')
if os.path.exists(tmp_index):
    os.remove(tmp_index)
env = dict(os.environ, GIT_INDEX_FILE=tmp_index)
run(git + ['read-tree', BASE], env=env)

for line in diff.splitlines():
    parts = line.split('\t')
    st, path = parts[0], parts[1]
    if st.startswith('A') or st.startswith('M'):
        blob = run(git + ['rev-parse', f'{LOCAL_SHA}:{path}'])
        run(git + ['update-index', '--add', '--cacheinfo', f'100644,{blob},{path}'], env=env)
    elif st.startswith('D'):
        run(git + ['update-index', '--force-remove', path], env=env)
    elif st.startswith('R'):
        # R100 old new
        old, new = parts[1], parts[2]
        blob = run(git + ['rev-parse', f'{LOCAL_SHA}:{new}'])
        run(git + ['update-index', '--add', '--cacheinfo', f'100644,{blob},{new}'], env=env)
        run(git + ['update-index', '--force-remove', old], env=env)
    else:
        print('UNKNOWN STATUS:', line); sys.exit(1)

tree = run(git + ['write-tree'], env=env)
msgfile = os.path.join(repo, '.git', '_r534_msg.txt')
with open(msgfile, 'w', encoding='utf-8') as f:
    f.write(open(os.path.join(repo, '.git', '_r534_msg_content.txt'), encoding='utf-8').read() if os.path.exists(os.path.join(repo, '.git', '_r534_msg_content.txt')) else 'r534 ride: W21 engine products 6-10 + engine lane rides + MSG-195x processed [surgical]')
new_sha = run(git + ['commit-tree', tree, '-p', BASE, '-F', msgfile])
print('surgical commit:', new_sha)

# assertion: new tree diff vs origin = exactly my payload
check = run(git + ['diff-tree', '--no-commit-id', '--name-status', '-r', BASE, new_sha])
assert check == diff, f'PAYLOAD MISMATCH:\n{check}\nvs\n{diff}'
print('payload assertion: MATCH', len(diff.splitlines()), 'entries')

r = subprocess.run(git + ['push', 'origin', new_sha + ':refs/heads/main'], capture_output=True, text=True, encoding='utf-8', errors='replace')
print('push rc:', r.returncode, r.stdout.strip(), r.stderr.strip())
sys.exit(r.returncode)
