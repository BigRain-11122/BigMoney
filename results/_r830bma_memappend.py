# -*- coding: utf-8 -*-
"""r830 bm-a S4 memory append: METHODOLOGY_ASSETS E41 card (freeze-buildgen
method, proven this window) + CODELY.md one-line entry (four-question gate
passed: reusable every future freeze / not in any ledger yet / lesson-first
/ single-item under 1.5KB)."""
import io
import os

# ---- 1. METHODOLOGY_ASSETS.md E41 card -----------------------------------
ap = "knowledge/METHODOLOGY_ASSETS.md"
t = io.open(ap, encoding="utf-8").read()
assert "E41" not in t, "E41 already present"
card = (
    "- **E41 冻结手术 buildgen 法（AST 抽前代 pairs+有序事实 vmap+物理转储计数预验+干跑/首活 selftest 双闸）**："
    "proven：r830 bm-a 实弹（W175 freeze 面探针四转储→buildgen AST 抽 r826 全部 173 对 old 侧=物理面计数全验后才发射→"
    "干跑两迭代拦 12 处陈旧 token/针缺失零写入→首活 n1 selftest 拦 own-key 滚动缺（WAVE_CONFIGS[174] 自断言未滚 [175]）→"
    "净回滚→复合序修→再活→双 selftest 全绿→引擎两 tick 内自燃实证）；方法论=冻结类大手术件不再手抄 43KB——"
    "①前代同构件 AST 解析抽 pairs（old/new 全为字面量+NL 连接，迷你求值器足够）②本代事实=有序复合串映射"
    "（会话/sha/带位串/词级瀑布 W175→W176→W174→W175→W173→W174→W172→W173/序数词/裸号滚动）③old 侧=前代 new 侧"
    "原样即物理面（r776 律计数预验）④特例对（parity 链 append、镜像键 vs 自键同形异代）显式构造"
    "⑤词级瀑布会吞短复合——短键复合（'174: {\"batch\"' 形态）须级联不可见；值复合（== 397_604 == 397_603 + 1 形态）"
    "会先吞全串复合的目标——全串复合须排值复合之前（本窗两迭代坑律）；"
    "receipt=results/_r830bma_w175_freeze_buildgen.py + _r830bma_w175_freeze_edits.py（f3fca4055 已上 origin）；"
    "O-20261002-2100 捕获律 live 实证（E40 后续卡）\n"
)
with io.open(ap, "a", encoding="utf-8", newline="") as f:
    f.write(card)
print("E41 card appended, new len:", os.path.getsize(ap))

# ---- 2. CODELY.md one-line entry ------------------------------------------
cp = "CODELY.md"
t2 = io.open(cp, encoding="utf-8").read()
size_before = os.path.getsize(cp)
line = (
    "\n- [2026-10-07 15:3x r830 bm-a] **冻结手术 buildgen 法首用（E41·方法论资产卡已入 knowledge/METHODOLOGY_ASSETS.md）**："
    "W175 FREEZE 全链一窗交付（面探针→AST 抽 r826 173 对→S74 事实 vmap→干跑两迭代拦 12 处零写入→首活 selftest 拦 own-key 滚缺→"
    "净回滚→复合序修→再活双绿→冻结 f3fca4055 上 origin→引擎自燃 n1w175 2/12+9 队列实证）；坑律=词级瀑布吞短复合（短键须级联不可见形）"
    "+值复合吞全串复合（全串须排值前）——后续 W176+ 冻结窗禁手抄 43KB 一律走 buildgen 血统；执法面=pit-engine-freeze-editor.md 域。"
    "How to apply：下波冻结窗先读 E41 卡+本行；buildgen 前必跑面探针（r773 leg1）；首活 selftest 红即净回滚重来勿带病续。\n"
)
if "r830 bm-a] **冻结手术 buildgen 法首用" not in t2:
    with io.open(cp, "a", encoding="utf-8", newline="") as f:
        f.write(line)
print("CODELY.md appended:", size_before, "->", os.path.getsize(cp),
      "(>50KB trigger:", os.path.getsize(cp) > 50 * 1024, ")")
