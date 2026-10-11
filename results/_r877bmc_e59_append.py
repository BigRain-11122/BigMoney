# -*- coding: utf-8 -*-
# r877 bm-c: append E59 methodology card (capture law O-20261002-2100 closeout step)
import io

CARD = u"""
- **E59 事件窗归因切片法（episode x regime-at-ignition 分桶）+「无日流件在盘」宣判前必先 grep 定位（sleeve-daily-series 伴生件）**：proven·研究面。事件驱动面（题材批 episodes.csv）无连续日流时归因单位=事件窗——按点火日（ignition_date）查 REGIME-5 标签分桶（恐慌日优先入 PANIC 桶·桶统计=逐集 sys_net/bh_net 分布：中位/p25/p75/正份额/超 BH 份额/超额中位·12 月滚动机械不适用因窗长=事件长非 252 日）；另一切教训：切片 v1 §4「超跌反弹无独立日流件在盘」宣判当日即被推翻——results/rev_osc/daily_series_FY_BG_TP8.json（DECISION_CHAIN_V2_P1 两路 sleeve gate 的伴生 sleeve-daily-series 件·judged 冻结配置零 RNG）一直在盘——「无 X 件在盘」类缺口行宣判前必先 grep results/ 找决策链/陪审批伴生日流件。
- 2026-10-11 14:5x·bm-c r877·P0 矩阵切片二收口步（捕获律 O-20261002-2100 依法生成·事件窗归因法 live 实证=TJ-FULL BULL 主场成立（中位 +3.7%/集·超 BH 57.5%）+dip_rebound BEAR 自declared 主场失守（12 月中位 −3.1%/x2 −9.0%·gate_off）双实锚·scripts/regime_p0_slice2.py selftest 11/11）：
"""

path = r'knowledge\METHODOLOGY_ASSETS.md'
with io.open(path, 'r', encoding='utf-8') as fh:
    t = fh.read()
assert u'E59 ' not in t, 'E59 already present'
with io.open(path, 'a', encoding='utf-8', newline='') as fh:
    fh.write(CARD)
with io.open(path, 'r', encoding='utf-8') as fh:
    t2 = fh.read()
assert u'E59 ' in t2 and t2.startswith(t[:200]), 'append verify fail'
print('E59 appended OK; total bytes', len(t2.encode('utf-8')))
