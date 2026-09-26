# -*- coding: utf-8 -*-
"""R280 bm-a 5x HANDOVER check: header flip + append round row (CRLF mirror)."""
import io

p = 'research/HANDOVER.md'
raw = open(p, 'rb').read()
t = raw.decode('utf-8-sig')
lines = t.split('\r\n') if '\r\n' in t else t.split('\n')
old3 = lines[3]
assert old3.startswith('> 本文件由循环每 5 轮核对更新一次'), 'L3 anchor drift'
bm_b_full = old3[old3.find('最近核对=bm-b'):]
assert bm_b_full.startswith('最近核对=bm-b'), 'bm-b anchor'
bm_b_body = bm_b_full[len('最近核对=bm-b round 280（'):]
new3 = ('> 本文件由循环每 5 轮核对更新一次（mandate 已写明）。最近核对=bm-a round 280'
        '（2026-09-27 00:5x·对账增量=文末 round 280 bm-a 行〔bm-a R279-280 增量（R276-278 已并读于 round 280 bm-b 行）：'
        '**REV_OSC d6 崩-发双发射根因修（工程修零判定产物窗）+CN_TREND_ETF_P1 prereg 冻结（T-87 s2 队列#1 趋势跟踪批）+S0 autofill_state 双撞车 union 解**；'
        '统一链 187,845 平持=本窗零批 finalize（prereg 冻结面不计账·revosc 修后待 tick 重发）〕）；'
        '上一次最近核对=bm-b round 280（' + bm_b_body)
lines[3] = new3
newrow = ('- 开发队列增量窗（接续版）**round 280 bm-a（5x 核对本轮），2026-09-27 00:5x 核对；'
          '对账区间=bm-a R279-280 增量（基线=round 280 bm-b 行·R276-278 已并读），统一链 187,845 平持实读'
          '（本窗零批 finalize：REV_OSC judged cells 在档未判=批曾崩于 d6 段·修后待 tick 重发、CN_TREND_ETF_P1 prereg 冻结面不计账）**：'
          '①**bm-a R279=死轮收养+认领竞速裁定**（fusion-nav 23:50 认领+23:52 完成滞留本地未推→bm-b 00:00 陈旧面认领=void per 8effe41b 竞速裁定律）；'
          '**R280（本轮）=REV_OSC 崩根因修+趋势批 prereg 冻结**——revosc runner d6_block 崩-发双发射根因='
          'load_member_rets 元组未解包（logs/autofill_REV-OSC-STOCK-P1.log 同点双崩·工程修 bdd99072·selftest 15/15·r253 零判定产物窗律）'
          '+CN_TREND_ETF_P1（T-87 s2 队列#1 趋势跟踪·research/CN_TREND_ETF_PREREG.md 冻结 feb36786+R280 零跑修正案 D2 截断面语义·'
          '23 ETF 机械宇宙探针 results/cn_trend_probe.json·7 judged cells MA/DON/MA200 族·K=2000 nulls seed 20270201 注册·'
          'V2 x2 判面·F-04 MSG-20260927-0035 声明）+S0 autofill_state 双 rebase 撞车 union 解（results/_r280bma_resolve{,2}.py·双新 claim 零丢失）；'
          'R285 下次 5x 核对。')
lines.append(newrow)
out = '\r\n'.join(lines)
with io.open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(out)
chk = open(p, 'rb').read()
print('written KB:', round(len(chk) / 1024, 1),
      '| endswith CRLF:', chk.endswith(b'\r\n'),
      '| row appended:', 'round 280 bm-a' in chk.decode('utf-8-sig'))
