# -*- coding: utf-8 -*-
"""r499 bm-a: generate FACTOR_CENSUS_REGISTRY H-section append block for
G2_OVERLAP_CENSUS_P2 NEW-FACE rows (126) from the canonical artifact.
Deterministic, read-only on the artifact, writes a text block for review."""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
doc = json.load(io.open(os.path.join(HERE, "g2_overlap_census_p2.json"),
                        encoding="utf-8"))
rows = [r for r in doc["rows"] if r["verdict"] == "NEW-FACE"]

lines = []
lines.append("")
lines.append("### H-P2. G2 矿源普查新面·P2 批（2026-10-01 bm-a r499·"
             "G2_OVERLAP_CENSUS_P2·append-only）")
lines.append("")
lines.append("- 血统：M4 initial-d/ml-quant-trading HEAD a770825f（r494 装锚）"
             "×M5 JunQHuang HEAD b3e37129 ×237 面公式级重叠普查"
             "（prereg=research/G2_OVERLAP_CENSUS_P2.md 冻结后跑·"
             "工件 results/g2_overlap_census_p2.json）——"
             "**4 面 DUP-FORMULA-VERIFIED 撞号引用在库 verdict 不重烧**"
             "（add_013/old_041→WQ#41·old_042→WQ#42·stock_009→GTJA#46）；"
             "38 面 DRIFT（M4-WQ101 8 简化重实现+MARKET 6 kin 名字级+"
             "M5 24 同号异构 demo）与 69 面 UNVERIFIABLE（散文/条件式/省略式"
             " docstring=公式源缺·不入池不烧）留 SLOT/未来代码面腿；"
             "本节只登记 126 个 NEW-FACE（零撞号面）。")
lines.append("")
lines.append("| 面 | 构造（M4 源 docstring 公式锚） | DATA_GATE | 注记 |")
lines.append("|---|---|---|---|")
for r in rows:
    cons = r["doc_formula"].replace("|", "\\|")
    note = "%s 族·SLOT 泊位候选" % r["subfamily"]
    if "\u0394" in r["doc_formula"]:
        note += "·Δ 符号书写变体披露"
    lines.append("| %s | %s | 否（OHLCV+amount/vwap 可算） | %s |"
                 % (r["face"], cons, note))
lines.append("")
lines.append("- 消费契约：126 面全数=泊位候选非入册资格——逐族 SLOT 三验+预注册后烧"
             "（G2 spec §四.1·O-1901 ① 禁一次性全量判决烧·优先序按消费面紧迫度）；"
             "69 UNVERIFIABLE 面=M4 代码面提取腿未来批选项（本批公式源缺如实不入池）；"
             "38 DRIFT 面=名字级/同号级近亲非语义等价（不引用族 verdict 亦不判负，"
             "构造验证留 SLOT 轮）。")
lines.append("- 供料池 ready 面账：7→**133 级**（+126 P2 OHLCV+amount/vwap 可算面；"
             "G2 spec §四.1 目标 30+ 超标——富集面全数未过 SLOT 三验如实标注）。")
lines.append("")

out = "\n".join(lines)
with io.open(os.path.join(HERE, "_r499bma_registry_h_p2_block.md"), "w",
             encoding="utf-8", newline="\n") as fh:
    fh.write(out)
print("block written: %d NEW-FACE rows, %d lines" % (len(rows), len(lines)))
