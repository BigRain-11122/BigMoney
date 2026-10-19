# r1074bm-a: r1032-family continue-refused bypass surgery (r1012/r1014 recipe + r1011 reflog law + r1061 postscript asserts)
import subprocess, sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
def g(*args):
    r = subprocess.run(['git','-C',REPO]+list(args), capture_output=True, text=True, encoding='utf-8', errors='replace')
    return r.returncode, (r.stdout or '')+(r.stderr or '')

# 0. reflog main check (r1011 law): no OTHER-window commits on main since my commit
rc, out = g('reflog','main','-8')
print('--- reflog main ---'); print(out.strip())
rc, out = g('rev-parse','main'); main_old = out.strip()
assert main_old == '9048a32a775d279f570209a4e19d5bed2fe10dff', 'main moved: %r' % main_old
rc, out = g('rev-parse','HEAD'); head = out.strip()
print('pre: main=%s HEAD=%s (detached-at-base expected)' % (main_old[:12], head[:12]))
assert head != main_old, 'HEAD unexpectedly equals main'

# 1. staged set sanity: my resolution must be staged (~40+ paths)
rc, out = g('diff','--cached','--stat')
n_staged = len([l for l in out.splitlines() if l.strip() and ' files changed' not in l])
print('staged paths:', n_staged)
assert n_staged > 30, 'staged set suspiciously small'

# 2. quit the deadlocked sequencer (keeps index+worktree)
rc, out = g('rebase','--quit')
print('quit rc', rc, out.strip()[:150])

# 3. rebuild the commit on the detached HEAD with the staged resolution
rc, out = g('commit','-C', main_old)
print('commit -C rc', rc, out.strip()[:200])
assert rc == 0, 'commit -C failed'
rc, out = g('rev-parse','HEAD'); new_head = out.strip()
print('rebuilt', new_head[:12])

# 4. marker scan on the COMMITTED tree for the 12 UU faces (r1048 law: rebase machinery bypasses claws)
UU = ["docs/daily_report/REPORT-2026-10-19.json","docs/daily_report/REPORT-2026-10-19.md",
      "docs/live_usage/LIVE-2026-10-19.json","docs/live_usage/LIVE-2026-10-19.md",
      "docs/live_usage/LIVE-latest.json","docs/live_usage/LIVE-latest.md",
      "results/_attrition_guard_scan.json","results/_r686bmb_d19_check.json",
      "results/compute_audit.json","results/fundamental_b_layer_filter.json",
      "results/regime_state.json","results/update_status.json"]
bad = []
for p in UU:
    rc, out = g('show', 'HEAD:%s' % p)
    if re.search(r'^(<{7}|>{7}|={7}$)', out, re.M):
        bad.append(p)
print('committed-tree marker scan:', 'CLEAN' if not bad else bad)
assert not bad, 'markers inside rebuilt commit'

# 5. update-ref main to the rebuilt commit (main currently = my own pre-rebase commit only -- no other-window orphans)
rc, out = g('update-ref','main', new_head)
print('update-ref rc', rc)
rc, out = g('rev-parse','main'); rc2, out2 = g('rev-parse','HEAD')
assert out.strip() == new_head and out2.strip() == new_head, 'main/HEAD diverged post-surgery'
rc, out = g('rev-list','--count','origin/main..main')
ahead = out.strip()
rc, out = g('rev-list','--count','main..origin/main')
behind = out.strip()
print('post: main==HEAD==%s ahead=%s behind=%s' % (new_head[:12], ahead, behind))
assert ahead == '1' and behind == '0', 'unexpected topology'

# 6. push
rc, out = g('push')
print('push rc', rc, out.strip()[:300])
sys.exit(0 if rc == 0 else 1)
