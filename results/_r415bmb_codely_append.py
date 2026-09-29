# r415 bm-b CODELY.md append (file-face; utf-8 no-FFFD assert)
import io

F = 'CODELY.md'
LINE = (
"- [2026-09-29 08:2x r415 bm-b] 坑律九十四批（收割前任 flip 脚本时 receipt assert 必须按源常量实值形态校验·basename≠全路径）+死会话 detach 存续第三例实证：前 r415 会话猝死后其 detached judge-finalize pid2432 存续并于 08:14:22 独立落地 w6_judge.json（r386 detach 律实证+1）——继任会话收割时前任 flip 脚本两失：①单面（漏 .bm-b.json lane 面=违 pit-89 双面律）②ledger-file assert 写死 basename 'w6_judge.json' 而源常量实值=全路径 'results/trial_labor_w6/w6_judge.json'（恒败断言）。修法=继任者按 W5 r407 先例重写双面脚本+endwith 宽容匹配+回执四断言前置。How to apply：收割/复用任何未经验证的前任脚本先跑 receipt 断言干跑再触池面；assert 对字符串常量一律 endswith/归一匹配勿写死等值。W6 判决定谳=四面 G1 全零 0/293（比 W5 单点更彻底）·E[FP]=14.65·账本 333432·intake 零面·48h CEO 钟起算 2026-10-01 08:14。\n"
)

with io.open(F, 'a', encoding='utf-8', newline='') as fh:
    fh.write(LINE)
with io.open(F, 'r', encoding='utf-8') as fh:
    tail = fh.read()[-len(LINE):]
assert '\ufffd' not in tail and tail.endswith('2026-10-01 08:14。\n')
import os
print('CODELY appended OK, size=', os.path.getsize(F), 'no-FFFD verified')
