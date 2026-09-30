# r481 CODELY hot-cold reorg per O-20260927-0230 <=10KB hardline (append crossed 11.6KB + new pit line)
# Moves pointer/receipt rows verbatim to archive 202609.md, merges into compact pointers, appends r481 pit line.
import io, sys

CODELY = 'CODELY.md'
ARCH = 'research/memory-archive/202609.md'

raw = open(CODELY, 'rb').read()
crlf = raw.count(b'\r\n'); lf = raw.count(b'\n') - crlf
eol = '\r\n' if crlf >= lf else '\n'
text = raw.decode('utf-8')
lines = text.split(eol)

def startswith_any(l, prefixes):
    return any(l.startswith(p) for p in prefixes)

# rows to archive verbatim (pointer/receipt type, subsumed by merged pointers)
move_prefixes = [
    '- [2026-09-30 r472 bm-b] 冻结探针事实消费三坑',
    '- [2026-09-30 r473 bm-b] 同轮双 rebase 撞车窗三坑',
    '- [2026-09-30 18:2x r485 bm-a] sina ETF 日线面节前发布滞后坑',
    '- [2026-09-30 18:5x r486 bm-a] 脏树并发窗双同步坑律',
    '- 冷层指针（r475 合并',
    '- [2026-09-30 r492 bm-a] O-20260930-2054 机队 CPU 效率确保令已回执执行',
    '- [2026-09-30 r282 bm-c] SSH',
    '- [2026-09-30 r284 bm-c] aps',
    '- [2026-09-30 r285 bm-c] astock',
    '- [2026-09-30 r476 bm-b] rebase',
    '- [2026-09-30 r476 bm-b] 并发窗种子带撞号坑',
    '- [2026-09-30 r477 bm-b] 探针≠门覆盖面坑',
    '- [2026-09-30 r286 bm-c] inbox',
    '- [2026-09-30 r286 bm-c] 有新bar触发判读面坑',
]
moved = [l for l in lines if startswith_any(l, move_prefixes)]
kept = [l for l in lines if not startswith_any(l, move_prefixes)]

new_pit = '- [2026-09-30 22:4x r481 bm-b] bm-b 无集团树坑+D-19 新鲜读 temp partial clone 配方（r481 首例实弹）：本机无集团仓检出——bm-c r290 正典配方路径 K:\\Fluxgroup\\FluxGroup 在本机 fatal（C 盘迁移后 K: 门面不存在·bm-b 只有 BigMoney 仓），D-19 新鲜读正解=temp partial clone：git clone --depth 1 --filter=blob:none --no-checkout git@github.com:BigRain-11122/FluxGroup.git $env:TEMP\\fg-dec-bmb 后 git -C … show origin/main:docs/decisions.md 与 docs/orders.md（零树触碰·blob:none 只拉树对象·秒级）；首跑水位基线 last_decisions_sha=21B5C469…FAFDCB 已入 state.json。How to apply：bm-b 一切集团台账消费走此配方（git show 面），禁信本机任何「集团树工作树」（不存在）亦禁按他机 K:\\ 路径硬套。'
merged_ptr_1 = '- 冷层指针（r481 合并·指针合并归档 r444 范式）：r472/r473/r485/r486 四条 mem- 档案指针行+r475 冷层指针行+r492 O-2054 回执流水行+r282/r284/r285/r286×2/r476×2/r477 九条截断指针行——全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r481 bm-b 窗批』节；mem 全文另在 .codely-cli/memory/mem-20260930-q-002~005.md；原九条截断行所指内容另见 archive『热冷整编 2026-09-30 r491 bm-a 窗批』+『r492 bm-a 窗批』两节。'

# insert new pit after the r290 row (Project section, near end); append merged pointer after r493 row
out = []
inserted_pit = False
for l in kept:
    out.append(l)
    if l.startswith('- [2026-09-30 22:2x r493 bm-a] 普查批书写变体保守判律'):
        out.append(new_pit)
        out.append(merged_ptr_1)
        inserted_pit = True
if not inserted_pit:
    # fallback: append at end
    out.append(new_pit)
    out.append(merged_ptr_1)

new_text = eol.join(out)
if not new_text.endswith(eol):
    new_text += eol
open(CODELY, 'wb').write(new_text.encode('utf-8'))

# archive append: verbatim moved rows under new section
arch_raw = open(ARCH, 'rb').read()
arch_eol = '\r\n' if arch_raw.count(b'\r\n') >= (arch_raw.count(b'\n') - arch_raw.count(b'\r\n')) else '\n'
section_title = '## 热冷整编 2026-09-30 r481 bm-b 窗批（CODELY>10KB 硬线触发·指针/回执行全迁 verbatim·merged 指针行替代）'
block = [section_title, ''] + moved + ['']
with open(ARCH, 'ab') as f:
    f.write((arch_eol.join(block) + arch_eol).encode('utf-8'))

# verification: size + zero-loss
size = len(open(CODELY, 'rb').read())
arch_text = open(ARCH, encoding='utf-8').read()
lost = [l for l in moved if l not in arch_text]
print('moved_rows=', len(moved))
print('new_size=', size, 'limit=10240', 'PASS' if size <= 10240 else 'FAIL')
print('zero_loss=', 'PASS' if not lost else 'LOST:' + str(len(lost)))
