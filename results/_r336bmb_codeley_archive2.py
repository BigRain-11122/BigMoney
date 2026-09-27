# _r336bmb_codeley_archive2.py -- 25th-batch supplemental: two more flowing index rows moved
# verbatim (main script left CODELY at 10426B, still 186B over <=10KB). Idempotent-guarded:
# refuses to run if the two rows are already absent (double-apply protection).
import io

CP = 'CODELY.md'
AP = 'research/memory-archive/202609.md'
c = open(CP, 'rb').read()
a = open(AP, 'rb').read()


def eol_of(b):
    crlf = b.count(b'\r\n')
    return '\r\n' if crlf and crlf >= (b.count(b'\n') - crlf) else '\n'


EOL_C, EOL_A = eol_of(c), eol_of(a)
ct, at = c.decode('utf-8'), a.decode('utf-8')
MOVES = [
    '- 十六批外迁（r86 bm-c）：三条目 FULL=归档十六批节；索引行外迁=archive 202609.md『坑律归档 2026-09-27 二十三批』节。',
    '- 十七批外迁（r88 bm-c·2026-09-27·水位律当窗整编·行级零丢失）：r328 bm-a 腾讯双K线互证律/r330 bm-b ctor 探针律两条目外迁=归档十七批节（9652B+新条将破 ≤10KB 硬线=律触发当窗办）；连带=「坑律正典全量归档」指针行严格超集去重（短行⊂长行·删短行零信息损失·r331 entry-union 条目级双向核验律适用）。',
]
present = [l for l in MOVES if l in ct]
assert len(present) == 2, f'expected both rows still in CODELY, found {len(present)} (double-apply guard)'
HEADER = '## 坑律归档 2026-09-27 二十五批'
assert HEADER in at, '25th section must already exist'
lines = ct.split(EOL_C)
lines = [l for l in lines if l not in MOVES]
c2 = (EOL_C.join(lines)).encode('utf-8')
hidx = at.find(HEADER)
blank_after = at.find(EOL_A, hidx + len(HEADER))
ins = blank_after + len(EOL_A)
a2 = (at[:ins] + EOL_A.join(MOVES) + EOL_A + EOL_A + at[ins:]).encode('utf-8')

open(CP, 'wb').write(c2)
open(AP, 'wb').write(a2)
chk = open(AP, 'rb').read().decode('utf-8')
for l in MOVES:
    assert l in chk, 'verbatim loss: ' + l[:30]
assert all(l not in open(CP, 'rb').read().decode('utf-8') for l in MOVES), 'rows must be gone from CODELY'
print('CODELY : %d -> %d (limit 10240, %s)' % (len(c), len(c2), 'OK' if len(c2) <= 10240 else 'OVER'))
assert len(c2) <= 10240, 'hard line still violated'
print('supplemental 2-row move verbatim self-verify PASS (25th section)')
