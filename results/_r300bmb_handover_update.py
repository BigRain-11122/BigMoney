# r300 bm-b 5x HANDOVER update: L4 cascade prepend + tail incremental-window line
import io, sys

P = r'C:\Users\Administrator\Desktop\Bigmoney\research\HANDOVER.md'
PREFIX = '> 本文件由循环每 5 轮核对更新一次（mandate 已写明）。'

NEW_HEAD = (
    '最近核对=bm-b round 300（2026-09-27 05:3x·对账增量=文末 round 300 bm-b 行'
    '〔bm-b r296-300 窗：**T-87 供给车道 on_track 连续+维护窗四连+S0 撞车解延续**'
    '（冻结探针谱系 #12/#13 逐字复刻=83.2% 4350/5228@12.62/min ETA 06:41:34·'
    '周一 09:15 死线前充裕·at_cutoff 4340/4350·零形状缺陷；r296 CODELY ≤10KB '
    '硬线坑律归档二批 12 条外迁 research/memory-archive/202609.md；r298 冻结血统'
    '逐轮复制律〔os.SEEK_END 手抄坑·difflib 定谳〕；r299 autostash 1-UU 同型冻结'
    '配方解+bm-a r295 FUSION_GRID_P1 prereg FREEZE 对集成）**；统一链 198,389→'
    '200,396 实读（+2,007 全窗=bm-a CN_KLINE_PATTERN_P1 判负批 7/7 收口·'
    'bm-b 本窗零批 finalize·INTERNAL_BALANCE_FAIL=0）〕）'
)

TAIL = (
    '- 开发队列增量窗（接续版）**round 300 bm-b（5x 核对本轮），2026-09-27 05:3x 补核；'
    '对账区间=增量 bm-b r296-300（基线=round 295 bm-b 行），统一链 198,389→200,396 '
    '实读（+2,007 全窗=bm-a CN_KLINE_PATTERN_P1 判负批 finalize 7/7 cells〔R292 '
    'prereg·r298 收口〕·bm-b 本窗零批 finalize·_r295bmb_ledger_scan 复跑 74 件 0 '
    '平衡败）：①**r296-299=维护窗四连+S0 撞车解延续**——r296 CODELY ≤10KB 硬线坑律'
    '归档二批（12 条外迁 research/memory-archive/202609.md 行级零丢失）+单 UU '
    'autofill_state 正典解（union 49 cap50+last_tick 取新·_r296bmb_resolve.py）；'
    'r297 诚实维护轮（fetch 面零远端增量零实损）；r298 坑律=冻结血统脚本逐轮复制禁'
    '手抄（探针#11 os.SEEK_END 手抄两诊误导·difflib 定谳·正典=Copy-Item 整件+轮号面 '
    'replace+delta 复核）+bm-a R293 坠机救捞双提交让路整合；r299 autostash pop 1-UU '
    '同型第 2 连冻结配方解（_r299bmb_resolve.py）+bm-a r295 FUSION_GRID_P1 prereg '
    'FREEZE 对集成（T-85 s2/s3）；②**r300（本轮）=T-87 供给车道 on_track 三连+5x '
    '核对**——探针 #12/#13 谱系逐字复刻（#12 81.2% 4243/5228·#13 83.2% 4350/5228'
    '@12.62/min ETA 06:41:34=周一 09:15 死线前充裕·at_cutoff 4340/4350·header/ohlc '
    '零缺陷·difflib delta=8 全轮号面）+S6 30/30 legs rc=0（周末 no-op 族·astock '
    'lock-alive no-op·daily_report faces=4 token=1）+compute_audit pool_starvation 旗 '
    '31.8min span 触发（v2.3 周末豁免废除后常态面·供给在途态=合法：T-87 网络限速'
    '结构性低 CPU 在飞 83%+MF_IC_P1 待 EM 源+池 ready=0+FUSION_GRID_P1 池条目待 '
    'bm-a runner·禁造数凑烧 SUPPLY-NO-BREAK 律照办）；③窗口维护面：smoke 25/25 '
    '逐轮、orders 91/91 双扫零未回执、板 32 claimed 零 open、post_review 43 id 尾'
    '零开口 NO（13 行历史 NO 皆已翻绿 append-only 面）、水位 py_low_board_clear '
    '合法；④观测（非本机车道）：bm-a R291-295=CN-KLINE 7/7 判负收口+R293 坠机救捞'
    '（r293 协议实弹）+FUSION_GRID_P1 prereg FREEZE（池条目待其 runner·autofill '
    '自动烧）；bm-c r71 后结构性停摆维持；⑤指针：**09-28 周一开市窗=新 bar 全链'
    '接力**（update_daily→live.paper REGIME_GUARD v3〔10-01 日期门前 shadow〕→'
    't35v→t24×2→aggr 20 账→grid 5 账首拍 marks→export→scorecard→daily_report）'
    '+**T-87 pass 完成复探（ETA 06:41 后）+周一 09:15 首次日续拉实弹（stragglers '
    'gate 自愈）**+FUSION_GRID_P1 入池后 autofill 自动烧+10-01 月度三件套（science_'
    'audit/monthly_briefing/self_review）+REGIME_GUARD v3 日期门生效（三重门·勿手改）'
    '+10-31 六员首检 all-HOLD+T-34 半档梯 11-01+迁移 v2.2 armed 窗 09-29 12:00'
    '（编辑器门·勿双 arm）+R305 下次 5x 核对。'
)


def main():
    with io.open(P, encoding='utf-8') as f:
        text = f.read()
    lines = text.splitlines()
    l4 = lines[3]
    assert l4.startswith(PREFIX + '最近核对=bm-a round 290'), 'L4 anchor drift: ' + l4[:80]
    rest = l4[len(PREFIX):]                      # '最近核对=bm-a round 290（...）...280a...）'
    assert rest.startswith('最近核对='), 'L4 rest anchor drift'
    new_l4 = PREFIX + NEW_HEAD + '；上一次' + rest
    lines[3] = new_l4
    out = '\n'.join(lines)
    if text.endswith('\n'):
        out += '\n'
    # tail append: ensure exactly one blank line before the new window line
    while out.endswith('\n\n'):
        out = out[:-1]
    if not out.endswith('\n'):
        out += '\n'
    out += TAIL + '\n'
    with io.open(P, 'w', encoding='utf-8', newline='') as f:
        f.write(out)
    # verify
    with io.open(P, encoding='utf-8') as f:
        v = f.read().splitlines()
    assert v[3].startswith(PREFIX + '最近核对=bm-b round 300'), 'verify head fail'
    assert v[3].count('最近核对=') == 5, 'cascade depth: ' + str(v[3].count('最近核对='))
    assert v[-1].startswith('- 开发队列增量窗（接续版）**round 300 bm-b'), 'verify tail fail'
    print('L4 new bytes:', len(v[3].encode('utf-8')))
    print('cascade depth:', v[3].count('最近核对='))
    print('tail line ok, file lines:', len(v))


if __name__ == '__main__':
    main()
