# r1084-continuation bm-c: memory-governance piece-3b -- post-gate pollution sweep (canon KEEP + SIGS; NO identity injection, tuple already in place from piece-3 07:59 run)
# Context: union REPLACE-DOWN restore at 08:06:35 re-inflated L0 to 377,015B (pre-surgery face) between the dead-window
# piece-3 run (07:59, quarantine written) and this window's gate v2 enforcement (08:17, 377,015->97,121B/104 entries).
# The restored-then-gated face still carries SIGS-matched non-KEEP pollution (11 scan hits); this sweep removes them verbatim.
# Union hemostat THIS window: Tools/fleet-memory-sync.ps1 checked out to origin no-op face (bm-b precedent local stop-bleed).
import importlib.util
import io
import os

L0 = r'C:\Users\Dasheng\.codely-cli\CODELY.md'
GATE = r'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r1084bmc_gate_v2.py'
QUAR = r'C:\Users\Dasheng\memory\topics\cross-machine-quarantine.md'

spec = importlib.util.spec_from_file_location('gate_v2', GATE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
KEEP_RULES = gate.KEEP_RULES

SIGS = [
    'C:\\Users\\sjs20', 'C:\\Fluxgroup', 'C:\\Users\\Administrator',
    '[via bm-a]', '[via bm-b]', 'metis', 'gui-agent', 'BiuNiYiXa',
    'PhantomEscapeGo', 'HomeWreck', 'BiliAutoReply', 'U360', 'GimmeAll',
    'HMI 线已废止', 'Skyline 工程进行中',
]

EXPECTED_PRE = 97121  # post-gate face guard: abort if union re-inflated again before this sweep


def is_keep(text):
    for rule in KEEP_RULES:
        if all(s in text for s in rule):
            return True
    return False


with io.open(L0, 'r', encoding='utf-8') as f:
    lines = f.read().split('\n')

pre_bytes = os.path.getsize(L0)
if pre_bytes != EXPECTED_PRE:
    print('FACE-GUARD: pre_bytes=%d != expected %d -- L0 changed since gate run, ABORT (re-audit before sweep)' % (pre_bytes, EXPECTED_PRE))
    raise SystemExit(2)

pre_entries = sum(1 for l in lines if l.startswith('- ['))
migrated = []
out = []
for l in lines:
    if l.startswith('- [') and ('本机身份元组' in l):
        out.append(l)
        continue
    if l.startswith('- [') and not is_keep(l) and any(s in l for s in SIGS):
        migrated.append(l)
        continue
    out.append(l)

new_text = '\n'.join(out)
with io.open(L0, 'w', encoding='utf-8', newline='') as f:
    f.write(new_text)

with io.open(QUAR, 'a', encoding='utf-8', newline='') as f:
    if migrated:
        f.write('\n== bm-c L0 post-gate pollution sweep 2026-10-18 r1084-continuation (piece-3b; restore-face re-pollution removed; zero-loss archive) ==\n')
        for m in migrated:
            f.write(m + '\n')

post_bytes = os.path.getsize(L0)
post_entries = sum(1 for l in out if l.startswith('- ['))
print('L0 pre: %dB / %d entries -> post: %dB / %d entries; migrated=%d' % (pre_bytes, pre_entries, post_bytes, post_entries, len(migrated)))
for m in migrated:
    print('MIGRATED:', m[:110])
# residual SIGS lines (KEEP-protected mentions stay by canon law)
resid = [l[:80] for l in out if l.startswith('- [') and any(s in l for s in SIGS)]
print('residual SIGS-matched (KEEP-protected by canon): %d' % len(resid))
for r in resid:
    print('KEPT:', r)
