# -*- coding: utf-8 -*-
"""r1110 bm-c S4: append derive-builder live-state collision pit to CODELY.md (multi-writer
file -> fresh read-modify-write per 2026-10-06 law; <=10KB hot-layer law check)."""
import io

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\CODELY.md"
ENTRY = (
    "- [2026-10-19 07:3x r1110 bm-c] **derive builder 活值碰撞坑两枚（W276 prereg derive 实弹·2D "
    "sweep RAM×GPU 21/21 边界定谳）**：①死 needle 的 OLD 面==当场活值时静默回滚上游 roll——"
    "r1107 canon-clone 继承的 (\"本窗 free RAM ~3.3GB\"→\"~4.0GB\") needle 在本 canon 零命中（死针），"
    "但 psutil 活值≈3.3GB 时其 OLD 面==BL495 刚产出的活面，把 MUST 活面条目回滚成字面 ~4.0GB"
    "→SIM MUST missing（瞬态难复现·全边界 sweep 才定位；r1107 heal-(4) 是同一家族的另一面）；"
    "正法=死针即删（0 命中实测后）+ 活值依赖 needle 全清单盘点。②裸值 stale ban 与活面碰撞——"
    "MUST_NOT ban \"本窗 free RAM ~4.4GB\"（上代 stale live 面）在活值==4.4GB 时误杀本代活面；"
    "正法=ban 一律 context-scoped：stale 长面的 doubled-GPU-prose 尾（T0 内唯一·活 NEW 面出生即愈 "
    "doubling·任何活值零碰撞）。How to apply：canon-clone builder 过 2D sweep（RAM×GPU 全边界值）"
    "才算 green；ban 清单逐条问「当场活值会不会撞」；0 命中死针即删勿留传代。\n")

raw = io.open(P, encoding="utf-8", newline="").read()
assert "活值碰撞坑两枚" not in raw, "entry already present"
eol = "\r\n" if "\r\n" in raw[-200:] else "\n"
if not raw.endswith(eol):
    raw += eol
raw += ENTRY.replace("\n", eol)
io.open(P, "w", encoding="utf-8", newline="").write(raw)
size = len(raw.encode("utf-8"))
print("CODELY.md appended, new size=%d bytes (hot-line 10240)" % size)
assert size <= 10240, "OVER 10KB -> hot-cold reorganization owed this window"
back = io.open(P, encoding="utf-8", newline="").read()
assert "活值碰撞坑两枚" in back and "doubled-GPU-prose" in back
print("readback OK")
