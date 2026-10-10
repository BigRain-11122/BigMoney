# -*- coding: utf-8 -*-
# r839 bm-c: fix report path -- append proper line to ROOT round_reports-bm-c.md, remove bogus fleet/ copy
import subprocess, datetime

iso = '2026-10-10T21:2x+08:00'
line = ('2026-10-10T21:2x+08:00 | r839 | dept:工程/舰队（pit-protocol 协议域 sub-split ceremony 债销账轮+S6 39 腿+S7 收口） | '
        '本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） | '
        'WM-VERDICT: 绿（red=false·lane=healthy·池 4 ready 全 claimed 0 unclaimed·板 open 0/inflight 0·bandit 0·satengine 队空·supply_gap 旗=fleet 级 W17-drain/W18-draft 等待面非本机违令） | '
        '孤儿面=0 | '
        'r839: ①S0.5 双 delta：DEC 34cf2538 恒等零动作·ORD e20de2d6→1cd22364 变更（CEO 物理件区扫=O-2006 全员 resume 广播〔bm-c 无 pause 旗=零动作〕+O-2015 游戏域不涉本司·水位键更新）；'
        '②**pit-protocol.md sub-split ceremony 债全销**（r838 指针②·31,433B>30,720B r859 起欠账）：r529/r583/r645 state 簿记族 3 条 2,034B verbatim 迁 pit-protocol-lane.md'
        '（主件 31→28 条·lane 18→21 条·主件头部执法面同步改道 lane 件·字节恒等 31,433-2,034+73=29,472<=30KB）·'
        'TREASURE §2 迁移仪式三件齐（prescan rc3 命中 4 件留痕=fail-closed 面 r441 交集裁定·零丢失 verbatim 非删除类+登记册出入行+零丢失断言）·receipt=results/_r839bmc_pit_protocol_lanesplit.json；'
        '③S4 新律入主件=Python text-mode 换行翻译坑（r838 EOL 律机械腿·open() newline=None 翻译 CRLF→LF=探针零命中假象·主件 30,510B）；'
        '④CODELY.md 协议域指针行 r839 仪式注记+TREASURE_REGISTRY r839 出入行（42,406B）；'
        '⑤队列面=tech/explore 队头全闭合或让渡（T23=bm-b r840 声明·W18=drain-gated）·无可认领新头·本轮主产=ceremony（上轮指针②承接）；'
        '⑥S6 39 腿 rc0（dualrun ZERO-DRIFT streak 13·周末数据腿诚实 no-op·market_clock ORANGE_COOL·REPORT/LIVE-2026-10-10 续鲜·token 0）+'
        'S7 四件绿（pin=5 no-op·watchdog 活·双爪 CR 归一恒等）+attrition 4 台账 CLEAN+d19 NOOP+orders 水位更新+smoke 49/49 | '
        '下轮指针: r840 ①D-05 写腿=10-11 00:00 常务轮首位 ②W17-JUDGE drain 观察+W18 berth 门复核（drain-gated）③T-182 co-sign 待 bm-a runner（10-16 窗）④10-14 政体验证窗 v1.1 re-cut ⑤CODELY.md 主件余量 210B=下窗 append 大概率再触发 mini-split（设计循环）\n')

p = 'round_reports-bm-c.md'
b = open(p, 'rb').read()
# EOL probe per r838 law
crlf = b.count(b'\r\n'); lf = b.count(b'\n') - crlf
sep = b'\r\n' if crlf >= lf else b'\n'
if not b.endswith(sep):
    # file ends with the other EOL; match tail
    sep_out = b'\r\n' if b.endswith(b'\r\n') else b'\n'
else:
    sep_out = sep
nb = b + line.encode('utf-8') + sep_out if b.endswith(b'\r\n') or b.endswith(b'\n') else b + sep_out + line.encode('utf-8')
open(p, 'wb').write(nb)
print('root report appended, crlf=%d lf=%d, tail sep matched' % (crlf, lf))

r = subprocess.run(['git', 'rm', '-q', 'fleet/round_reports-bm-c.md'], capture_output=True)
print('git rm bogus:', r.returncode, r.stderr.decode('utf-8', 'replace')[:80])
