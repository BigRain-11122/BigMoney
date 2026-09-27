# _r336bmb_codeley_archive.py -- 25th-batch in-window hot/cold archival (r336 bm-b).
# Trigger: fold landing left CODELY.md at 13400B > <=10KB hard line (O-20260927-0230 group order:
# append-over-line = same-window archival, never wait for monthly). Mechanism = 24th-batch
# pattern (r339bma v3): CRLF-uniform worktrees, moved lines preserved VERBATIM in archive
# 25th-batch section, CODELY keeps pointers; removals are either (a) already-archived fulls
# (verified by distinctive substring before removal) or (b) strict-subset duplicate rows whose
# superset/verbatim survives elsewhere; line-level zero-loss asserted per move.
import io

CP = 'CODELY.md'
AP = 'research/memory-archive/202609.md'
c = open(CP, 'rb').read()
a = open(AP, 'rb').read()


def eol_of(b):
    crlf = b.count(b'\r\n')
    return '\r\n' if crlf and crlf >= (b.count(b'\n') - crlf) else '\n'


EOL_C, EOL_A = eol_of(c), eol_of(a)      # r339 law: mirror per-file tail-state, worktree EOL is illusory
assert c.endswith(EOL_C.encode()) and a.endswith(EOL_A.encode()), 'uniform-EOL expected per file'
clines = c.decode('utf-8').split(EOL_C)
assert clines[-1] == ''
body = clines[:-1]
orig_size = len(c)

# (prefix, action, verify-substring-or-None)  action: move|remove
MOVES = [
    ('- [2026-09-27 17:5x r335 bm-b] 坑律：**tick git 集成的 add/stash 腿', 'move', None),
    ('- [2026-09-27 17:3x r334 bm-b] 坑律：**rolling-ledger union', 'remove-if-archived', 'asof 行 4 条同键全塌缩'),
    ('- 坑律正典全量归档（2026-09-27 集团令', 'move', None),
    ('- [2026-09-27 17:2x r91 bm-c] 坑律（二十三批外迁·指针）：S0 stash→pop 共享滚动台账必 UU', 'move', None),
    ('- [2026-09-27 16:2x r335 bm-a] 坑律（二十一批外迁·指针）：PowerShell ConvertFrom-Json 假红', 'move', None),
    ('- 十六批外迁（r330 bm-b）：九条坑律行级外迁', 'move', None),
    ('- 十七批外迁（r88 bm-c）：两条目 FULL', 'move', None),
    ('- 十九批外迁（r89 bm-c）：五条目 FULL', 'move', None),
    ('- 十六批外迁（r330 bm-b·14:5x 当窗超线整编）', 'move', None),
]
POINTER_R335 = ('- [2026-09-27 17:5x r335 bm-b] 坑律（二十五批外迁·指针）：tick add/stash 腿不受 r201 mid-rebase 护栏管辖'
                '（r335 三连击实弹；正典=动态 sides 正典重建+原子 add-continue-push+行锚定终验+危险窗后 reflog 定谳）'
                '——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十五批』节。'
                '指针=results/_r335bmb_resolve.py+_r335bmb_probe_race.py。')
HEADER = ('## 坑律归档 2026-09-27 二十五批（r336 bm-b·水位律当窗整编：fold 落链后 CODELY 13400B>≤10KB 硬线'
          '·9 行外迁去重·行级零丢失）')

moved, removed = [], []
nb = []
for l in body:
    hit = next((m for m in MOVES if l.startswith(m[0])), None)
    if not hit:
        nb.append(l)
        continue
    prefix, action, probe = hit
    if action == 'remove-if-archived':
        assert probe and probe in a.decode('utf-8'), 'r334 full NOT found in archive 23rd section -- refuse removal'
        removed.append(l)
    else:
        moved.append(l)
assert len(moved) == 8 and len(removed) == 1, f'move/remove count mismatch: {len(moved)}/{len(removed)}'

# r91 short-pointer carried the sole 指针= field (_r91bmc_resolve_autofill.py) -- merge into kept long pointer (r329 bidirectional field law)
kept_r91 = [l for l in nb if l.startswith('- [2026-09-27 17:2x r91 bm-c] 坑律（二十三批外迁·指针）：S0 pull 共享滚动台账')]
assert len(kept_r91) == 1, 'r91 long pointer not found uniquely'
if '指针=results/_r91bmc_resolve_autofill.py' not in kept_r91[0]:
    nb[nb.index(kept_r91[0])] = kept_r91[0] + '指针=results/_r91bmc_resolve_autofill.py。'
# kept PS pointer must be the superset (r335 bm-a 二十批 long form) for the moved subset row
assert any(l.startswith('- [2026-09-27 16:2x r335 bm-a] 坑律（二十批外迁·指针）：PowerShell ConvertFrom-Json') for l in nb), 'PS superset pointer must survive'
nb.append(POINTER_R335)

# collapse fold-recovery blank-line runs (2+ consecutive empties -> 1) inside Reference region only
out, run = [], 0
for l in nb:
    if l == '':
        run += 1
        if run > 1:
            continue
    else:
        run = 0
    out.append(l)
while out and out[-1] == '':
    out.pop()
c2 = (EOL_C.join(out) + EOL_C).encode('utf-8')

# archive: insert 25th section verbatim before the FIRST batch section header
ap_txt = a.decode('utf-8')
hidx = ap_txt.find('## 坑律归档 2026-09-27')
assert hidx > 0, 'first batch header not found in archive'
section = HEADER + '\n\n' + '\n\n'.join(moved + removed) + '\n\n'
a2 = (ap_txt[:hidx] + section + ap_txt[hidx:]).encode('utf-8')

open(CP, 'wb').write(c2)
open(AP, 'wb').write(a2)
chk_a = open(AP, 'rb').read().decode('utf-8')
for l in moved + removed:
    assert l in chk_a, 'verbatim loss: ' + l[:40]
assert all(l not in open(CP, 'rb').read().decode('utf-8') for l in moved + removed), 'moved/removed rows must be gone from CODELY'
print('CODELY : %d -> %d (limit 10240, %s)' % (orig_size, len(c2), 'OK' if len(c2) <= 10240 else 'OVER'))
print('archive: %d -> %d (+%d moved+%d removed-verbatim, 25th section)' % (len(a), len(a2), len(moved), len(removed)))
assert len(c2) <= 10240, 'hard line violated'
print('25th-batch verbatim + pointer + subset-dedup self-verify PASS')
