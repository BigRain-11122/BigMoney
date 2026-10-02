# -*- coding: utf-8 -*-
# r595 bm-b: append one pit-law line to repo CODELY.md (bytes-in-bytes-out, r530 law).
import io

ENTRY = (
    u'- [2026-10-02 21:2x r595 bm-b] FF/reset 对齐后 D 面未清零→add -A 吞删除坑'
    u'（r594 unpushed 提交被 T-144 pre-push 爪首次实弹拦截定谳）：reset --mixed 到新基后'
    u'「基里新增而他盘缺席」的件（bm-a r593 领养工件 _r592bma_*/_r593bma_* 9 件）呈 " D"，'
    u'git add -A 把盘缺记成提交删除=推他机属主件删除集，爪按「删除集含非本机属主件」拦死；'
    u'另 origin 同窗前进=爪删除集按「origin 树−本地 HEAD 树」差集算出 r374 分叉伪影双害同拦。'
    u'修法=r589 撤-FF-重落环：reset --mixed HEAD~1→恢复 9 件→属主分面 checkout'
    u'（bm-b 白名单 19 面保留+其余 69 面取 origin 正典）→执行时 rev-parse update-ref+reset FF 重锚'
    u'→重 commit 重 push 直达；jsonl 两态=共享 append-only 面先探行集关系（本地独有 dict 行=union 保、'
    u'否则 origin verbatim），他机属主证据面 r381 origin verbatim。'
    u'铁律=一切整合/收口序列 add -A 前必扫 porcelain 全部 " D" 行——本机不属主 D 面=术后伪影必恢复禁提交'
    u'（正法=E-08 卡）。How to apply：FF/外科/reset --mixed 后 status 见陌生 D 面，'
    u'先 ls-tree 核 origin 在场性再定性，在场=恢复勿删。'
)

b = io.open('CODELY.md', 'rb').read()
eol = b'\r\n' if b.count(b'\r\n') * 2 > b.count(b'\n') else b'\n'
nb = b + ENTRY.encode('utf-8') + eol
io.open('CODELY.md', 'wb').write(nb)
print('appended 1 line; new size %d bytes' % len(nb))
