# -*- coding: utf-8 -*-
"""R252 bm-a: append one round-report line (fixed fields, byte-mirror)."""
P = "logs/iteration-loop/round_reports-bm-a.md"
raw = open(P, "rb").read()
crlf = b"\r\n" in raw
bom = raw[:3] == b"\xef\xbb\xbf"
t = raw.decode("utf-8-sig")
if not t.endswith("\n"):
    t += "\n"
line = (
    "2026-09-26 15:03 | R252 bm-a | watermark: GREEN (py_low_board_clear 14:39 sample, red=false; ROT batch ready→launched same round) | "
    "①修红：autofill tick 熔断饿死缺陷（_pick 单候选撞 fuse 拒发即 return→池头 T80 熔断饿死后续 ready 批；修=拒发即跳过 skip 循环+last_tick fuse_skipped 追溯+selftest S16e 新腿，26/26 全绿；实弹 tick 14:50:27 跳过 T80〔refusals=3〕发射 ROT 批 pid 43612）| "
    "②T-73 s3 slice-2 全弧：CN-DIV-LOWVOL-ROT-P1 落地 14:50:53（18.4s·65 units）→收割门 _r252bma_rot_harvest.py 十面重derive PASS→池翻 done+harvest_note（r244 律）→判负收线 0/4 过 G1'v2（最强 W252_bare 0.7371<线 0.9527·CI 下沿正；MA200 门格双轴恶化=§5.2 预测双 MISS 照登）→prereg §7/§8 回填+gate_attrition 第 44 行（runner 自落 entries 列表）+票 progress_r252 | "
    "③P0 断链发现与修复：五件族 runner 嵌 append_ledger 块于非正典键 ledger（扫描器唯一认 trials_ledger）+zoo 窄域 157/exit 30/t33 40 缺口=记录头 185798 缺 394→census _r252bma_ledger_census.py 全谱普查→修复 _r252bma_ledger_chain_repair.py（五件键正典化+真链重锚 head→186192·六 runner 码点同修·判定面字节零动·skill_line 4dp 复核不变 rot 0.9527/cn_rev 0.6147）→science_gates 35/35+smoke 25/25 复跑全绿 | "
    "④复审：注册行 T-73-CN-DIV-LOWVOL-ROT-P1+R252-BMA-LEDGER-CHAIN-REPAIR 同轮落册（r246 律）+CN-REV 行重锚→复审器 run 19 YES/0 NO | "
    "⑤S6 链全绿（update_daily 0 新行周末·market_clock ORANGE_COOL·LHB 0 超截·全 gate exit 0）；集团决策 D-09/10/11 均执行司=HQ 域零动作面 | "
    "验证证据：p1_results.json+pool harvest_note+post_review.jsonl 三行 YES+git diff 字段级（pool 5+/3-·ticket 2+/1-·registry 195+/4-）| "
    "下轮指针：T-73 s3 剩余三模型（CORE-SATELLITE 卫星缺位待 T-57 供给·REGIME-POLICY s2 先研·GRID-SLEEVE 组合 prereg 开放）+T80 anchor 裁决在 bm-b（已 MSG 委托·fuse 拒发计数可见勿重发）\n"
)
data = (t + line).encode("utf-8")
if crlf:
    data = data.replace(b"\n", b"\r\n")
if bom:
    data = b"\xef\xbb\xbf" + data
with open(P, "wb") as fh:
    fh.write(data)
print("round report appended; size:", len(data))
