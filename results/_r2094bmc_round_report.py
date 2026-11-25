import io, os
row = ("2026-11-25T17:3x+08:00 | r2094 | bm-c | **PRODUCT（新文件面·竞争窗轮）**："
       "竞争探针 rc=3 CONTENTION（对端交互宿主 pid=93460，15:54 起，17:27 仍持 33 张共享面含本机心跳）"
       "→ 按 r1907 只落新增文件面（state/心跳/S6/冒烟均未碰）。产出＝**r2093 只判了择时的 delta，"
       "从没印过水平**：同一张表上常驻 carry 在三把尺子上是 IC 2.76/9.65/9.68%、IM 5.74/11.96/11.50%，"
       "跳 5.9-6.9pp，比它要判的 delta（0-6pp）还宽。新面把一手按每把尺子折成元并记现金腿："
       "一手 IC 只锁 144,580 元保证金（首档的 12.80%），其余 984,985 元照旧吃息 17,503 元/年，"
       "故净超额=carry 减去被锁保证金的机会利息，不是一个除法。最差尺子下 IC 仍 +2.72%、IM +5.45% 资本；"
       "最好尺子 10.10%/11.59%。**现金是叠加不是替代**——除以全额首档会低估，拿 carry 比停车收益率会高估，"
       "两种旧读法都错。IM 的择时在 strictest 下相对常驻 **-2,174 元/年**（常驻赢择时）。"
       "判词 PAYS_ON_ITS_WORST_RULER_BUT_THE_RATE_IS_RULER_BOUND：指令活、年化不活——"
       "carry 到底算不算展期日这个定义之争未决前禁报单点数字。"
       " | selftest 10/10 · check CHECK_OK · 负控 6/6（cash 30%/清零→翻负、缺面拒、手改被抓 STALE、单尺子 6.92pp 误）"
       " | 记账：本行 1 处（state/心跳由对端写，本窗未改）"
       " | 下轮=(a) 裁决展期日算不算 carry（定义面，不是统计面）；(b) 一手以上容量未测；"
       "(c) 14 条内联腿仍无独立命令\n")
p = "round_reports-bm-c.md"
raw = open(p, "rb").read()
assert raw.endswith(b"\n"), "ledger tail lacks newline"
with open(p, "a", encoding="utf-8", newline="") as fh:
    fh.write(row)
print("appended")
