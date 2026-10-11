# -*- coding: utf-8 -*-
"""r872 bm-b: append r494-recurrence pit entry to research/pit-engine.md
(direct-write per r666/r747 precedent; file headroom verified)."""
import os

ENTRY = (
    "- [2026-10-11 09:5x r872 bm-b] **克隆多行方法体禁读一眼过=r494 复犯实录"
    "（A14 runner dec 主重索引 .reindex(master_dates) 转录丢·前驱 r872 会话死因）**："
    "A13 克隆时 cmd_run 主重索引块 vals/close 行都 reindex(master_dates) 唯 dec 行漏——"
    "异质员史（510300 全史 3490 vs 五员交集 1428）在 RESID 相 pd.Series(dec, index=master) "
    "长度炸；冻结 selftest 16/16 合成面同长员测不出（异质员史洞）。正法=surgical heal"
    "（A13 verbatim .reindex(master).fillna(False) 恢复）+checkpoint 保全零重烧"
    "+selftest 16/16x2。How to apply：克隆多行方法体=逐行 diff 源本再冻结；"
    "selftest 合成面必含异质长度员史腿。\n"
)

p = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\research\pit-engine.md"
size_before = os.path.getsize(p)
assert size_before + len(ENTRY.encode("utf-8")) <= 30720, "would breach 30KB cap"
with open(p, "a", encoding="utf-8") as fh:
    fh.write(ENTRY)
print("appended; size:", size_before, "->", os.path.getsize(p))
