# -*- coding: utf-8 -*-
# r839 bm-c addendum: push-race disclosure to round report + new pit law direct-write to rebase child
import time

# --- 1) round report addendum (root file, pure CRLF) ---
rp = 'round_reports-bm-c.md'
b = open(rp, 'rb').read()
assert b.endswith(b'\r\n')
ADDENDUM = ('2026-10-10T21:3x+08:00 | r839 addendum | 推送竞速实录补记（r838 同款披露）：首轮 push 被 pre-push 所有权爪拦'
            '（推程删除集报 _r842bmb_closeout.py+t23_random_grammar_census.py 两件〔bm-b r841/r842 轮中新增·我基座 1898576f7 早于其入场=「HEAD 缺件」形态误报 D·爪正常执法零放行〕'
            '+origin 同窗推进 6 commits 非快进）→pull --rebase 单发=14 UU 全共享再生成面'
            '（REPORT/LIVE 族+update_status/attrition/compute_audit/regime_state/token 族·全 checkout --theirs 取 origin 后写面·信息零损失·下轮 S6 自动续鲜）'
            '→r789 假冲突报第三发复发（ls-files -u 空而 continue 拒）→r789 原子化律 add -A+continue 一发治愈→push 通（a71d6ee5b..111328613）'
            '→fetch+ls-tree 送达自证：receipt/_r839bmc_pit_protocol_lanesplit.json+pit-protocol.md（blob c69b3a4b0）在 origin·bm-b 两件完好·未达=0'
            ' | stash（2 saturation face 中间态）已 drop 零损失 | 新坑律=rebase 在位窗禁 stash pop（直写 pit-git-resolver-rebase.md·r747 先例）\n')
open(rp, 'wb').write(b + ADDENDUM.encode('utf-8'))
print('report addendum appended')

# --- 2) pit law direct-write to rebase child (r747 precedent) ---
cp = 'research/pit-git-resolver-rebase.md'
b2 = open(cp, 'rb').read()
assert b2.endswith(b'\r\n')
assert len(b2) <= 30720 - 350, 'headroom check'
LAW = ('- [2026-10-10 21:3x r839 bm-c] rebase 在位窗禁 stash pop 坑（r839 push-race 实弹）：'
       'pull --rebase 冲突在位时 stash pop=二层冲突源——pop 自身再撞（stash 保留+工作树半应用态与 rebase UU 面叠加，'
       'ls-files -u 与 rebase --continue 判读互相矛盾=诊断迷雾·实弹 14 UU 面上叠 pop 冲突后续判读三轮）；'
       '正法=冲突窗内禁 pop，rebase --continue 完成后再处理 stash（或 add -A 吸收工作树现态后判 stash 面已被超越即 drop）；'
       '同窗 r789 假冲突报第三发复发=原子化 add+continue 一发治愈再证。\r\n')
nb = b2 + LAW.encode('utf-8')
open(cp, 'wb').write(nb)
print('rebase child appended:', len(b2), '->', len(nb), '| le_cap:', len(nb) <= 30720)
