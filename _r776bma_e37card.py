# -*- coding: utf-8 -*-
"""Append E37 card to knowledge/METHODOLOGY_ASSETS.md (fresh read-append) +
fix prereg sec.8 E-number reference."""
p = "knowledge/METHODOLOGY_ASSETS.md"
src = open(p, encoding="utf-8").read()
assert "E37" not in src, "E37 already present"
card = (
    "\n- **E37 波位分层跟随测量法（wave-position stratified follow measurement）"
    "（proven·面件级）**：题材线的散户可执行判决范式——测量单位=波段（v0.2 冻结切分）·"
    "分组特征=波位 seq（决策时可测：先序波已发生）·跟随规则=波基点确认线入场"
    "（+20% 断线族·folk 数值化）+运行峰破线出场（−20%·同族）·T+1 收盘执行·成本双轨；"
    "主测量面=波内全起点逐日穷举分布（D-41 §1.3 事件型落地：9,356 起点·79% 右偏）——"
    "公平对照=波内穷举分布非 B&H（E25 律第三应用面）；判负=逐波位独立关线"
    "（CEO「不能一棒子打死」执法：W1 正面 +19.2%/73%（p=0.0165）·W2/W3+ 判负照报）；"
    "配律=M6 常数敏感性披露（四格摆幅真实）+E25 幸存者基线（注意力点火签名="
    "著名题材共同特征·慢热配置型引入零触发=「成名筛选」的机制面）。"
    "实证=THEME_DEEPEN_P1 r776（T-2026-10-06-173-P1·O-20261006-1207 CEO 直令题材深化批）·"
    "证据=results/theme_deepen_p1/ 五件+research/THEME_DEEPEN_P1_PREREG.md §7/§8"
    "（冻结 66d5ec5d4·账本 750,812 链头）。\n"
)
open(p, "w", encoding="utf-8").write(src + card)
print("E37 appended, new len:", len(src + card))

# fix the prereg sec.8 reference E26 -> E37
pp = "research/THEME_DEEPEN_P1_PREREG.md"
s = open(pp, encoding="utf-8").read()
assert "METHODOLOGY_ASSETS E26 卡" in s
s = s.replace("METHODOLOGY_ASSETS E26 卡", "METHODOLOGY_ASSETS E37 卡")
open(pp, "w", encoding="utf-8").write(s)
print("prereg E-number fixed")
