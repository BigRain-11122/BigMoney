# -*- coding: utf-8 -*-
# r305 bm-b 5x HANDOVER update: L4 cascade prepend + tail incremental-window line
# (r300bm-b pattern verbatim: PREFIX cascade + one-line window ledger)
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = r'C:\Users\Administrator\Desktop\Bigmoney\research\HANDOVER.md'
PREFIX = '> 本文件由循环每 5 轮核对更新一次（mandate 已写明）。'

NEW_HEAD = (
    '最近核对=bm-b round 305（2026-09-27 06:5x·对账增量=文末 round 305 bm-b 行'
    '〔bm-b r301-305 窗：**T-87 供给车道首拉收口+settle 律缺口三修+py_watermark '
    '锁面修复+维护窗连营**（r301 POSTHUMOUS 补闭 S7 push 撞头 27-UU 典解·r302 '
    'wrap 钟面 astimezone 自证门·r303/304 探针#16/#17 连营·r305=完成态探针 '
    'pass_complete 5217/5228〔quarantined 11 三振=000019 停牌+新股相·settled 12 '
    '停牌短尾面〕·settle 律缺口=fetch 成功股 attempts.pop→quarantine 永不可达→'
    'complete 结构性不可达+gate 30min 无限 spawn 环，三修=suspended-settle 面'
    '〔同 cutoff≥3 周期离 todo·新 cutoff 重臂=复牌股自愈〕+load_progress 白名单'
    '携带修〔settle 计数每周期归1实弹〕+bytes-cutoff 优先·manual cycles 3-8 收口'
    '·06:52 稳态=complete true/cutoff 2026-09-24/gate no-op 零网络·py_watermark '
    'local_batch_running 锁面修复=网络限速 detached pass 0.36 核<0.5 CPU 阈恒漏检'
    '→py_low_board_clear 假 idle 实况 T-87 在飞，修=锁面纳入+selftest 23 腿）〕）'
)

TAIL = (
    '- 开发队列增量窗（接续版）**round 305 bm-b（5x 核对本轮），2026-09-27 06:5x 补核；'
    '对账区间=增量 bm-b r301-305（基线=round 300 bm-b 行），统一链 200,396→202,441 '
    '实读（+2,045 全窗=bm-a FUSION_GRID_P1 判负批 45 cells+2000 nulls finalize'
    '〔r296-298 窗·r303/304 收编〕·bm-b 本窗零批 finalize·_r295bmb_ledger_scan 复跑 '
    '75 件 INTERNAL_BALANCE_FAIL=0·HEAD=FUSION_GRID_P1 202,441）：'
    '①**r301-304=维护窗四连+S0 撞车解延续**（r301 POSTHUMOUS 补闭 bm-a r296 同窗 '
    '27-UU bigmoney-conflict-resolve 分类器 11 GREEN+16 UNKNOWN 手工定谳·r302 wrap '
    '件 naive iso 无偏移=F7 红线面自证门当场拦后同轮修复三面零外泄+autofill_state '
    '单 UU 典解·r303/304 探针#16/#17 on_track 93.9%/96.0%+lineage_copy 器=冻结血统 '
    'Copy-Item+轮号面 replace+difflib delta 复核 r298 坑律正典化）；'
    '②**r305（本轮）=T-87 首拉收口+双补丁**——完成态探针新面（_r305bmb_astock_'
    'completion_probe.py 三态设计）·06:40:11 pass ended 5217/5228·11 股三振 '
    'quarantine+12 股停牌短尾 settle·**settle 律缺口三修**=suspended-settle 面+'
    'load_progress 携带修+bytes-cutoff 优先（selftest 腿齐全过）·manual cycles 3-8'
    '（操作员周期越过 30min gate 节流·~60 请求·披露）·06:52 稳态=complete true/'
    'cutoff 2026-09-24/gate no-op 零网络·**py_watermark 锁面修复**（CPU 阈 0.5 核恒'
    '漏检网络限速 pass→假 idle py_low_board_clear·修=data/*/_refresh.lock 活 pid 纳入'
    '+refresh_lock_lanes 披露+selftest 21→23 腿·活探针 06:36:31 honest=py_low_with_'
    'work_cands）+post_review 开放负判定 per-id 解析器=0 开口（13 历史 NO 皆同 id '
    '后续 YES 翻绿）+orders 双向全差集器 91/91 零 ghost；③窗口维护面：smoke 25/25 '
    '逐轮（双补丁后复跑 25/25）·orders 91/91 双扫零未回执·板 32 票 claimed 零 '
    'open·池 56/56 done 零可认领·audit v2.3 CLEAN 零旗·S6 30/30 rc=0 逐轮；'
    '④观测（非本机车道）：bm-a R296-298=FUSION_GRID_P1 runner 崩窝修复+烧批落地 '
    '0/45 G1\'v2 NEGATIVE=config-family no-increment（member-alpha 未证伪）+prereg '
    's7/s8 单次定稿（P3 magnitude-MISS=精确 v3 政体份额 ORANGE+RED 10% 非 61%·预测'
    '前提面可精算必先精算坑律入册）+28-UU rebase-window addendum+CN_SOE runner '
    'pooled 待 autofill；bm-c r71 后结构性停摆维持；⑤指针：**09-28 周一开市窗=新 '
    'bar 全链接力**（update_daily→live.paper REGIME_GUARD v3〔10-01 日期门前 shadow〕'
    '→t35v→t24×2→aggr→grid 5 账首拍 marks→export→scorecard→daily_report）+'
    '**T-87 周一 15:30 后首次日续拉实弹=全宇宙分离 fetch ~3.5h 家族 by-design 成本'
    '诚实披露**（settled 12 股新 cutoff 重臂·复牌自愈）+10-01 月度三件套（science_'
    'audit/monthly_briefing/self_review）+REGIME_GUARD v3 日期门生效（三重门·勿手改）'
    '+10-31 六员首检 all-HOLD+T-34 半档梯 11-01+迁移 v2.2 armed 窗 09-29 12:00'
    '（编辑器门·勿双 arm）+R310 下次 5x 核对。'
)


def main():
    with io.open(P, encoding='utf-8') as f:
        text = f.read()
    lines = text.splitlines()
    l4 = lines[3]
    assert l4.startswith(PREFIX + '最近核对=bm-b round 300'), \
        'L4 anchor drift: ' + l4[:80]
    rest = l4[len(PREFIX):]
    assert rest.startswith('最近核对='), 'L4 rest anchor drift'
    new_l4 = PREFIX + NEW_HEAD + '；上一次' + rest
    lines[3] = new_l4
    out = '\n'.join(lines)
    if text.endswith('\n'):
        out += '\n'
    while out.endswith('\n\n'):
        out = out[:-1]
    if not out.endswith('\n'):
        out += '\n'
    out += TAIL + '\n'
    with io.open(P, 'w', encoding='utf-8', newline='') as f:
        f.write(out)
    with io.open(P, encoding='utf-8') as f:
        v = f.read().splitlines()
    assert v[3].startswith(PREFIX + '最近核对=bm-b round 305'), 'verify head fail'
    assert v[3].count('最近核对=') == 6, 'cascade depth: ' + str(v[3].count('最近核对='))
    assert v[-1].startswith('- 开发队列增量窗（接续版）**round 305 bm-b'), 'verify tail fail'
    print('L4 new bytes:', len(v[3].encode('utf-8')))
    print('cascade depth:', v[3].count('最近核对='))
    print('tail line ok, file lines:', len(v))


if __name__ == '__main__':
    main()
