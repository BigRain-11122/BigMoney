# -*- coding: utf-8 -*-
"""R258 bm-a: CODELY.md memory append (S4, four-question gate passed:
E1 pit / no restatement / lesson-first / single item <1.5KB)."""
import io

ENTRY = (
    "\n- [2026-09-26 17:2x] 坑律（bm-a R258·T-73 s2 slice-D·size 因子 cap 构造面·"
    "E1 判定前自捕零外泄）：**单位/换算类文档 lore 与运营缓存面可能分裂——"
    "TURNOVER_DERIVATION 文档「688 volume 列=100×真实股数」描述的是 raw bars 源，"
    "P1C 运营缓存 volume 列已归一（决定性锚：amount/volume≈close，2025+ 中位 ×1.0007、"
    "2019-2021 ×1.0014；turnover_derived[688]=真换手量级）——从文档 lore 直接派生 "
    "/100 板修=双修正，617 只 688 股流通市值缩小 100×（中位 71M 假值）污染 size 截面"
    "排名**；正律=①消费运营缓存前，任何单位/换算 lore 必须用独立锚实测裁定"
    "（amount/volume vs close、量级 sanity），文档纪=raw 源面≠缓存面；②派生面板"
    "构造必须带 sanity 披露腿（同数量级校验）使病在判定前自捕（本轮 cap_sanity 腿"
    "当场红）；③缺陷面数字废弃+修正重算+runs log/defect_disclosure 留痕+消费掉的"
    "试验照计入 N（终产物 10 面、消费 13 次 IC 计算如实分列）；缺陷稳健性注记="
    "污染面 OOS −0.0546 vs 修正 −0.0566 方向不变（病不翻案但必须修）。指针="
    "scripts/t73_s2_factor_history.py build_size_signal R258 修正段+头注 AMENDMENT+"
    "results/_r258bma_688_probe.py+results/_r258bma_sliceD_reset.py\n")

with io.open("CODELY.md", "a", encoding="utf-8", newline="") as fh:
    fh.write(ENTRY)
print("appended bytes:", len(ENTRY.encode("utf-8")))
