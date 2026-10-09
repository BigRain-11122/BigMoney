# -*- coding: utf-8 -*-
"""Append THEME_DEEPEN_P1 treasure-registry line (capture law, fresh append)."""
p = "knowledge/TREASURE_REGISTRY.md"
src = open(p, encoding="utf-8").read()
line = (
    "- 2026-10-06 13:5x bm-a r776 THEME_DEEPEN_P1 判决批收口窗（题材深化批·CEO 直令 "
    "O-20261006-1207·T-2026-10-06-173-P1）：**新宝藏=波位分层跟随测量法 E37 卡**"
    "（首波唯一正读数 +19.2%/73%·p=0.0165；二/三波+成本后判负=「首波吃肉二波喝汤」"
    "数值化定谳；注意力点火签名=著名题材共同特征·慢热配置型引入零触发=E25 幸存者基线"
    "机制面新发现）；账本 741,411→750,812（+9,401·measurement）；证据="
    "results/theme_deepen_p1/ 五件+research/THEME_DEEPEN_P1_PREREG.md（冻结 66d5ec5d4）"
    "+docs/theme_report/THEME-DEEPEN-R1-20261006.md（48h 首版报告提前交付）。\n"
)
open(p, "w", encoding="utf-8").write(src + line)
print("registry line appended")
