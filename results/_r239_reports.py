# -*- coding: utf-8 -*-
"""R239: append round report line + CODELY.md entries (line-level, UTF-8, self-managed newlines).
CODELY gate: 50KB check after append (D-20260925-01④)."""
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-a.md")
line = ("R239 | 2026-09-26T10:0x | bm-a (dept:策略/总经办/工程·CEO 三连令执行轮) | WM verdict: py_low_with_work_cands=合法 "
        "(CPU 24-96% 被 T-70 C-arm LLM 推理批吃满, py 占比低; 三张 CEO 即时票=本轮同轮认领同轮开动) | "
        "S0.5 双扫: O-0932/O-0940/O-0947 三令全收 (轮首) 全回执 (收尾, orders_ack 逐令枚举) | "
        "T-74 (O-0932 市场时钟组合): s0 正典+预注册冻结 MARKET_CLOCK_COMBO.md v1.0 (L1=v3四态x热度复合8格, 热度=H_act>=rolling250d p80 且 H_net>0, "
        "LHB 2007-2026 26.6万行=热度回测面, 涨停/炸板采集器缺位如实披露, 前向面禁入回测; s2 判据冻结: >=200起点格+成本恒开+随机基线+N记录+vs EW-48/B_MAXDIV+D6 对 T-73 族 corr 检查) "
        "+ s1 当日判定一页 CALL-2026-09-24: 格=ORANGE_COOL (LHB 81行<96 p80, 净买+16.4亿; 板块 r20>0 宽度仅0.167, "
        "强势=513100纳指/512800银行/512200地产/511090国债, 弱势=512400有色-15.7%/515030/515790), 仓位帽50%, 袖=震荡军当值+红利低波底仓; "
        "scripts/market_clock_call.py selftest 4 例 PASS, S6 链接线 (market_regime 腿后) | "
        "T-75 (O-0940 战报): firm/DECISIONS.md 正典 (4 条回填) + scripts/daily_report.py v1 (selftest PASS: 四面+token行, 聚合面零新判据) "
        "+ 首报当日出 REPORT-2026-09-26.md+json (6交易员+27账户族+时钟格+24h吞吐539commits/88结果件/37digest+决策尾+队列26+token行) "
        "+ S6 链接线 (daily_scorecard 腿后, 字节精准单行插) + 修正: py_watermark.py verdict 原来只打 stdout 不落 jsonl -> 持久化进记录 (selftest 20/20) | "
        "T-77 (O-0947 本地分治): LOCAL_FIRST.md v2.0 落地 (路由表 L1/L2/L3+CEO 保留面正交+速度优先律+3b 崩-发卫士条款+3c GPU 因子线条款) "
        "+ token 行入战报=验收点 d 已活 | E1 自捕 P0 红项: aggressive_lab paper 腿崩 AttributeError -> science_gates.ledger_head "
        "对 results/ 共享面顶层 list 形态 JSON 未防御 (.get on list), 肇事件=T-70 C-arm 批新落盘 tasks/*/C/metrics.json (设计=list 形态), "
        "修=isinstance 守卫跳过+real-form 夹具腿 (science_gates selftest 35/35 PASS), aggressive_lab 复绿 exit 0 | "
        "S6 链 21 腿全绿 (smoke 25/25 二次复证; update_lhb/futures/options/sina_mf/ths 周末 no-op, moneyflow 30min 节流在途守卫, "
        "compute_audit FLAG:pool_starvation=池空待 T-74 s2 批入池, ah 首拉 29min 节流) | inbox: bm-b T-76 slice-1 认领通知已处理归档 (零冲突) | "
        "下轮指针: T-74 s2 全史回测批 (runner+入池, 按冻结判据), T-77 crash-fuse/L2 扩展/GPU 首单, T-75 周一 15:45 首个实盘日战报验证 | "
        "水位证据: results/watermark.jsonl 09:49:35 (verdict 已持久化), CPU 94% C-arm 在飞")
with io.open(RR, "a", encoding="utf-8", newline="") as f:
    f.write("\n" + line + "\n")
print("round report appended")

CM = os.path.join(ROOT, "CODELY.md")
entries = [
    ("- [2026-09-26 10:0x] 执行记录（bm-a R239·CEO 三连令同轮执行）：O-0932 市场时钟组合 T-74 s0 正典+预注册冻结"
     "（research/MARKET_CLOCK_COMBO.md v1.0·热度复合 v0=H_act≥rolling250d p80 且 H_net>0·LHB 2007 起为唯一热度回测面·前向面禁入）"
     "+s1 当日出 CALL-2026-09-24 格=ORANGE_COOL（scripts/market_clock_call.py·S6 链接线）；O-0940 战报 T-75 "
     "firm/DECISIONS.md+scripts/daily_report.py+首报 REPORT-2026-09-26+S6 接线；O-0947 T-77 LOCAL_FIRST.md v2.0 路由表"
     "+token 行入战报。三票 claimed，续点=票内 progress_r239。"),
    ("- [2026-09-26 10:0x] 坑律（bm-a R239·science_gates.ledger_head 崩溃面·r157/r221 家族新维·E1 生产首跑自捕）："
     "**共享库对 results/ 递归扫描必须容忍顶层非 dict 形态 JSON——json.load(fh).get() 遇 list 即 AttributeError 且 "
     "except 元组只接 OSError/ValueError/UnicodeDecodeError 不接 AttributeError=整链崩**（实弹：T-70 C-arm 批新落盘 "
     "tasks/*/C/metrics.json=设计上就是 per-round list 形态（pilot_c_client 明文 aggregate per-round），首个 S6 轮 "
     "aggressive_lab 即崩，连带 p5_random_entry import-time LEDGER_PREV 全链）；正律=①递归扫描器对任意顶层形态 "
     "isinstance 守卫后跳过（非 dict=非账本件，同 unparseable 待遇）②夹具腿用真实形态（C-arm list 件入 "
     "science_gates selftest）③新生产者家族入 results/ 时审查共享扫描器的形态假设面。"
     "指针=scripts/science_gates.py ledger_head+selftest r239 腿+results/_r239_find_listjson.py。"),
    ("- [2026-09-26 10:0x] 坑律（bm-a R239·py_watermark verdict 持久化面·消费链缺陷·E1 设计期自捕）：**probe 的 "
     "verdict/window 只打 stdout 不落 jsonl 记录=任何文件面消费者（T-75 战报、轮报告引用）读到 None**；正律=派生判定"
     "若属下游消费面，必须随采样记录一并持久化（追加记录先算后写：samples=旧序列+新样本并集再判，与写后读恒等）。"
     "指针=scripts/py_watermark.py run() 持久化段+selftest 20/20。"),
]
with io.open(CM, "a", encoding="utf-8", newline="") as f:
    for e in entries:
        f.write(e + "\n")
size_kb = os.path.getsize(CM) / 1024
print(f"CODELY.md appended; size now {size_kb:.1f} KB")
if size_kb > 50:
    print("WARN: >50KB -> hot-cold reorganization due this window (D-20260925-01(4))")
