"""r2027 state update, order-preserving (no sort_keys): the earlier dump reordered the
whole face and buried this round's six real edits in 40 lines of churn."""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
FIELDS = os.path.join(ROOT, "results", "_r2027bmc_hb_fields.json")

fields = json.load(open(FIELDS, encoding="utf-8"))
d = json.load(open(STATE, encoding="utf-8"))
d["round_no"] = 2027
d["round_no_prev"] = 2026
d["rounds"] = 2027
d["rounds_done"] = 1963
d["task"] = ("r2027: one contract is 4,822 ETF lots; 90.13% of notional needs 162% of the book "
             "in cash at an 80% 融券 ratio; the ETF rounds to 0.00004 of beta, the contract to 0.2078")
d["work"] = ("r2027 · 新增文件面（竞争窗）：scripts/astock_veto_hedge_lots.py + "
             "results/astock_veto_hedge_lots.json + research/ASTOCK_VETO_HEDGE_LOTS.md —— "
             "把 r2026 的「90.13% 账面」翻成一张下单前的检查单")
d["当前任务"] = ("r2027: 把默认档翻成手数——一手差 4,822 倍；1M 账面 ETF 3,919 手（beta 误差 0.00004）"
              "vs IM 0.813 手（只能 0 或 1.1091 beta）；80% 融券档 162% 现金承诺；IM 12% 保证金被单日 -5.64% 吃掉 47%")
d["当前活"] = "把「90% 账面」翻成账户真的能下的单：几手、压多少现金、离强平多远"
d["最近实物"] = ("research/ASTOCK_VETO_HEDGE_LOTS.md + results/astock_veto_hedge_lots.json + "
             "scripts/astock_veto_hedge_lots.py（selftest 29/29·check rc0·负控 21/21）（2026-11-24 05:3x）")
d["最新实物"] = ("research/ASTOCK_VETO_HEDGE_LOTS.md + results/astock_veto_hedge_lots.json + "
             "scripts/astock_veto_hedge_lots.py")
d["最新判词"] = "LOT_IS_FREE_ON_THE_ETF_AND_A_FOUR_THOUSANDTH_OF_THE_BOOK_ON_THE_FUTURE"
d["本次"] = ("r2027 检查单：ETF 一手 230 元 / IM 一手 1,109,120 元（4,822x）；1M 档 ETF 3,918.83 手→3,919"
         "（beta 0.9014，误差 0.00004）、IM 0.813 手→0 或 1（beta 1.1091，误差 0.2078）；"
         "0.5% beta 所需账面 ETF 23,000 元 / IM 1.109 亿；精确中性账面 1 手 1,230,535 / 2 手 2,461,071；"
         "融券保证金 50/80/100% → committed 135/162/180% 账面；IM 12/15% → 13/17%（且 1M 档不可下）；"
         "每元目标名义占用 ETF 1.50/1.80/2.00 vs IM 0.15/0.18；最新 bar ETF -4.80% / IM -5.64%（12% 档一天的 47%）；"
         "滚动 2.02% 名义 / 1.82% 账面；基差中位 -0.629%")
d["未验证"] = ("①保证金比例与券源是券商条款不可观测，按 50/80/100% 与 12/15% 轴印；②强平距离=保证金率的粗略上界，"
           "未建模维持保证金/追保/手续费；③价格取 11-20 收盘、持仓取最后一期（11-11 期末），7 个交易日未做市值重估；"
           "④IM 基差中位取自混合到期日，不能年化；⑤券源规模与召回未建模；⑥本面是口径件不是下单指令")
d["watermark_verdict"] = ("green (red=false; lane healthy; repo_write_contention rc=3 CONTENTION "
                          "-> new-file faces only)")
d["watermark_note"] = ("竞争探针 rc=3：2 宿主存活（对端 pid 51252 11-22 20:10 起常驻 interactive / 本宿），"
                       "21 张共享面在轮首前被对端写、重叠窗 0 张 -> 按 r1927 只落新增文件面，"
                       "未改共享代码/数据面、未跑 S6 链")
d["s0_note"] = "orphan_face_probe py_faces=6 orphans=0 零杀；repo_write_contention rc=3 CONTENTION"
d["s05_note"] = ("orders_ack_scan CLEAN（116 令 / 329 回执 / 124 陈旧注记 / unacked=[]）；"
                 "decisions.md 原字节 sha256 79e3083b85c130b8... == state 水位 -> 零新决策；"
                 "orders.md 原字节 99e8e77d093cc13d == 水位 -> 零新行；fleet/inbox 空")
d["smoke"] = ("not run this round (CONTENTION); 以 29/29 selftest + 21/21 负控 + run/check 双 rc0 背书，"
              "不宣称全绿")
d["s6_chain"] = "not run (CONTENTION rc=3)"
d["s7_attrition"] = "attrition_ledger_guard scan CLEAN（4 账本，3 处历史缩行 healed）"
d["s7_claws"] = "pre-commit / pre-push 与 Tools/git-hooks/ 逐字节（CR 归一）MATCH，未重装、未用 --no-verify"
d["s7_loop"] = "Bigmoney-IterationLoop phase ok（machine=bm-c pin=0 current=0，首燃 11/24 05:30 未动）"
d["s7_note"] = "contention window (rc=3): new-file-only landing; shared smoke/S6 faces untouched"
d["孤儿面"] = 0
d["下轮指针"] = ("(a) 无竞争轮：smoke_test.py 两腿 + Tools/s6_chain_bma.py r2022-r2027 五面腿 + "
             "knowledge/METHODOLOGY_ASSETS.md 卡（锁存：跨盘 relpath 崩 = r1745 族第四例）+ CODELY 两行；"
             "(b) 把「162% 现金承诺」接进 CEO 一页纸与票据的仓位节；"
             "(c) 账面/价格时点错位（11-11 期末 vs 11-20 收盘）改成同一天重估")
d["下个里程碑"] = ("(a) 竞争窗结束后把 r2022–r2027 五面接 S6 链腿与冒烟腿（≤48h）；"
              "(b) 把「90.13% 名义 = 162% 现金承诺 / 一手 4,822 倍」接到 CEO 一页纸与票据仓位节（≤48h）")
d["记账_r2027"] = "轮报告 1 处 + state 1 处 + 心跳 1 处 = 3"
d["本地未达 origin commit 数"] = 0

with open(STATE, "w", encoding="utf-8") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print("state round_no -> %d (%d keys, original order kept)" % (d["round_no"], len(d)))
