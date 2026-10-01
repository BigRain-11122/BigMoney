# -*- coding: utf-8 -*-
"""r545 bm-a: land law sec.4 W35 row in research/PERPETUAL_FACES.md
(engine de-throttle law O-20261001-2355 sec.2 first bm-a own-series wave)."""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = "research/PERPETUAL_FACES.md"
raw = open(p, "rb").read()
eol = b"\r\n" if raw.count(b"\r\n") > (raw.count(b"\n") - raw.count(b"\r\n")) else b"\n"
E = eol.decode("ascii")
src = open(p, encoding="utf-8", newline="").read()

anchor = "## §5 计账（跨波累计 N_eff 恒不重置）"
assert src.count(anchor) == 1, f"anchor not unique: {src.count(anchor)}"

w35_row = E.join([
    "- N1 波35（r545 bm-a 落 prereg 时展行·**第二十四枚引擎波·bm-a 第八枚自有波**〔engine_owner=bm-a·SATURATION_ENGINE_LAW §1/§2 同 W10-W33 合同·不入池·免预认领·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二首枚 bm-a 自持连续系列波**〔本机上一波 W33 收口（finalize 落账 bm-a r544·K=70,520·账本 437,148 链性）→秒级物化下一波=同机零间隔接力·座位制同令废止·波号=35=W34 公示认领后首个自由号〕·never-dry 供给律常设步〔r545 实况=引擎活〔status exit 0〕·队列 0〔W33 已收口〕·板负面已毕·核闲红旗 5min 线=去节流令执法面〕·**冻结窗合法性**：本机冻结前 fetch 实核表尾无 W34/W35 行=W35 号净空〔r511 表尾锁律·W34=bm-b r527 预扫 ADMIT-READY 回执在 origin 公示=公示投影带预留面 r518〕〕）：A-ext seed=**113_004..115_003**（**强制跳位面**〔算术位 111_004..113_003==W34 公示投影带=bm-b 预扫认领面·r518 公示投影=预留面→跳位被迫非自由挑·带闸 leg1 refusal facts 机证〕·**机证净空·registry-derive**〔候选=注册表 derive 非散文·带闸 leg1/leg2 机证==W34 公示投影尾+1·双带零额外跳位〕·扫描面=pre-W35 三十一行 N1 带表〔含 W30 行 103_004..105_003/41_001..41_200·W31 行 105_004..107_003/41_201..41_400·W32 行 107_004..109_003/41_401..41_600·**W33 行 109_004..111_003/41_601..41_800〔r544 bm-a·已收口 K=70,520〕**〕＋**W34 公示投影带 111_004..113_003/41_801..42_000〔bm-b r527 预扫 ADMIT-READY·冻结待 bm-b 座=预留面 r518〕**＋W1 ext＋v1 在用带＋SEED_REGISTRY 全值＋**N3-R1 实际种子集 70_000..70_005**〔r529 裁定行②强制腿〕＋**runner 探针种子簇 95_000..95_003**〔r335 发现腿·W26 起强制〕＋N2/N4 设计探针保留点 40_000/40_001＋N2-W15 草案探针点 31_000/31_500/32_000＋lfc 实际流 30_000..30_099＋options_wave2 实际流 63_000..63_049〔leg-3e 实际流避让腿〕·**ADMIT 回执=results/_r545bma_w35_band_gate.py**〔r545 bm-a 起草窗实跑·leg0 三十一行+候选注册面校验〔无 15 无 34〕+leg0b W33 行 W34+ 警示 prose 在场校验+leg1 算术窗==W34 公示投影→REFUSED〔跳位被迫性机证〕+leg2 公示投影后首净窗==候选双带+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+W34 公示投影 disjoint 腿〕·非重挑〔W35 带从未指派·测量面零结果可钓·R250〕〕）；B-ext exit seed=**42_001..42_200**（==W34 公示投影 B 尾 42_000+1·强制跳位同律·零额外跳位如实注记）。**N2/N4 让位注记**：本波 A 带 113_004..115_003——N2/N4 波级 prereg 冻结时按本表防撞律回避该域。**W36+ 警示**：A +2_000 算术位（115_004..117_003）与 B +200 算术位（42_201..42_400）投影以 r545 带闸回执 W36+ 投影腿机证为准（机闸 derive 非 prose 转抄·r535 律·去节流令下=首个自由号法·无座位指派）。",
    "",
])
src = src.replace(anchor, w35_row + anchor)
open(p, "w", encoding="utf-8", newline="").write(src)
print("law sec.4 W35 row landed")
