# r1084-continuation bm-c: memory-governance piece-3 -- L0 identity tuple injection + cross-machine pollution verbatim migration
# Law: CEO 2026-10-18 00:2x memory-governance direct order (fleet rollout four-piece), memory.md section 10 v2
# KEEP protection = gate v2 canonical KEEP_RULES imported live (zero transcription); migration = verbatim zero-loss to topics quarantine.
import importlib.util
import io
import os
import re

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

IDENTITY = '- [2026-10-18] **本机身份元组（memory.md §10 v2·L0 注入面唯一真值锚·CEO 记忆治理直令 2026-10-18 00:2x）**：machine_id=bm-c（Machine C·compute-node）·root=K:\\Fluxgroup ·用户=Dasheng ·tailnet=100.123.74.104 ·硬件=RTX 3070 16GB+RAM 24GB ·本 L0=bm-c 单机注入面——他机身份条目禁驻留（发现即 verbatim 迁主题层·联合回灌已拆除 worker v1.9）·守门=HQ-MemoryBudgetGate 周期执法（v2 执法 50KB/120·预警 35KB/80）'


def is_keep(text):
    for rule in KEEP_RULES:
        if all(s in text for s in rule):
            return True
    return False


with io.open(L0, 'r', encoding='utf-8') as f:
    lines = f.read().split('\n')

entries = [i for i, l in enumerate(lines) if l.startswith('- [')]
pre_bytes = os.path.getsize(L0)
pre_entries = len(entries)

migrated = []
kept_tuple = False
out = []
section_user_seen = False
for l in lines:
    if l.strip() == '### User' and not kept_tuple:
        out.append(l)
        out.append(IDENTITY)
        kept_tuple = True
        section_user_seen = True
        continue
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

os.makedirs(os.path.dirname(QUAR), exist_ok=True)
with io.open(QUAR, 'a', encoding='utf-8', newline='') as f:
    if migrated:
        f.write('\n== bm-c L0 cross-machine pollution verbatim migration 2026-10-18 r1084-continuation (CEO memory-governance four-piece piece-3; zero-loss archive) ==\n')
        for m in migrated:
            f.write(m + '\n')

post_bytes = os.path.getsize(L0)
post_entries = sum(1 for l in out if l.startswith('- ['))
print('L0 pre: %dB / %d entries -> post: %dB / %d entries; migrated=%d; tuple_injected=%s' % (pre_bytes, pre_entries, post_bytes, post_entries, len(migrated), kept_tuple))
print('quarantine file: %s (+%d lines)' % (QUAR, len(migrated)))
for m in migrated[:40]:
    print('MIGRATED:', m[:90])
