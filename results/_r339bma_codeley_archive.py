# _r339bma_codeley_archive.py -- v3: 23rd-batch in-window archival, TWO entries folded.
# v2 left CODELY at 10330B (over 10KB by 90B -- single pointer too fat). Per same-hour fold
# precedent (r90 folded r338bma's fresh entry), r91 bm-c's full entry (17:2x, 40min old) joins
# the 23rd batch verbatim; CODELY keeps two pointers. Worktrees are CRLF-uniform (r338 law).
import sys

FULL_R339 = ('- [2026-09-27 17:4x r339 bm-a] 坑律：**共享 JSON 面字节级拼接编辑（b[:-N] 接头式）取侧与去尾字节数必须按 '
             'blob 尾态计算——autocrlf 工作树 CRLF 是假象（blob 常=纯 LF）**。r339 实弹：fleet 票件 blob=LF 无尾换行、'
             '工作树=CRLF；v1 从工作树字节 b[:-2] 去 \\n} 漏去 \\r → 接头留裸 CR + git diff 整件假 churn（20 行假重写·'
             'r338 律「写后 --stat 核 churn」当场捕获）；v2 正典=git show HEAD:<path> 取 blob 定 EOL/尾换行→从 blob '
             '字节重建（LF 尾=去 2 字节 \\n}、CRLF 尾=去 3 字节 \\r\\n}）→JSON 校验→落盘→--stat 核 churn≈目标行数。'
             '指针=results/_r339bma_ticket_note.py（v1 病灶+v2 修正双版本在档）+commit r339。')
POINTER_R339 = ('- [2026-09-27 17:4x r339 bm-a] 坑律（二十三批外迁·指针）：共享 JSON 字节拼接编辑取侧/去尾字节必按 '
                'blob 尾态（autocrlf 工作树 CRLF 假象·v1 b[:-2] 留裸 CR+整件假 churn；正典=blob 字节重建+写后 --stat '
                '核 churn）——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十三批』节。')
POINTER_R91 = ('- [2026-09-27 17:2x r91 bm-c] 坑律（二十三批外迁·指针）：S0 pull 共享滚动台账 stash→pop 必 UU——resolver '
               '定侧源=git show HEAD:<path>+stash@{N}:<path>（:2:/:3: 经任何 git add 即灭）；解完才 add 且赶 :X0:02 tick '
               '前；PS 引 stash@{0} 必单引号——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 '
               '二十三批』节。')
HEADER = ('## 坑律归档 2026-09-27 二十三批（r339 bm-a·水位律当窗整编：r339 新坑律 append 后超 ≤10KB 硬线·'
          'r91 bmc+ r339 bma 两全文外迁·行级零丢失）')


def crlf(s):
    return s.replace('\n', '\r\n').encode('utf-8')


cp = 'CODELY.md'
ap = 'research/memory-archive/202609.md'
c = open(cp, 'rb').read()
a = open(ap, 'rb').read()
assert c.endswith(b'\r\n') and a.endswith(b'\r\n'), 'CRLF worktrees expected'

# --- extract r91 full line from CODELY (second-to-last line; last = r339 pointer from v2) ---
clines = c.decode('utf-8').split('\r\n')
assert clines[-1] == '', 'must end with CRLF'
body = clines[:-1]
assert body[-1].startswith('- [2026-09-27 17:4x r339 bm-a] 坑律（二十三批外迁·指针）'), 'v2 pointer expected last'
r91_idx = [i for i, l in enumerate(body) if l.startswith('- [2026-09-27 17:2x r91 bm-c] 坑律：**S0 pull')]
assert len(r91_idx) == 1, 'r91 full line not found uniquely'
R91_FULL = body[r91_idx[0]]
assert 'commit r91。' in R91_FULL and len(R91_FULL) > 300, 'r91 full line sanity'

# --- rebuild CODELY: drop r91 full + drop v2 pointer, append both pointers ---
nb = [l for i, l in enumerate(body) if i != r91_idx[0]]
nb = [l for l in nb if not l.startswith('- [2026-09-27 17:4x r339 bm-a] 坑律（二十三批外迁·指针）')]
nb.append(POINTER_R91)
nb.append(POINTER_R339)
c2 = crlf('\r\n'.join(nb) + '\n')

# --- rebuild archive 23rd section: header + r91 full + blank + r339 full ---
prefix = '## 坑律归档 2026-09-27 二十三批'
hidx = a.find(prefix.encode('utf-8'))
assert hidx > 0, 'v2 section prefix not found in archive'
a2 = a[:hidx] + crlf(HEADER + '\n\n' + R91_FULL + '\n\n' + FULL_R339 + '\n')

open(cp, 'wb').write(c2)
open(ap, 'wb').write(a2)
print('CODELY : %d -> %d (limit 10240, %s)' % (len(c), len(c2), 'OK' if len(c2) <= 10240 else 'OVER'))
print('archive: %d -> %d' % (len(a), len(a2)))
assert R91_FULL.encode('utf-8') in open(ap, 'rb').read(), 'r91 verbatim loss'
assert FULL_R339.encode('utf-8') in open(ap, 'rb').read(), 'r339 verbatim loss'
assert R91_FULL not in open(cp, 'rb').read().decode('utf-8'), 'r91 full must be gone from CODELY'
print('two-entry verbatim + dual-pointer checks PASS')
