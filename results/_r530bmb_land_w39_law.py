from pathlib import Path

# r500 byte-level lesson (LF-only target): research/PERPETUAL_FACES.md is
# pure-LF on disk; byte-level patch with explicit LF normalization.

p = Path(r"research/PERPETUAL_FACES.md")
data = p.read_bytes().decode("utf-8")

anchor = "\n## §5 计账（跨波累计 N_eff 恒不重置）"
anchor = anchor.replace("\r\n", "\n")
assert data.count(anchor) == 1, "anchor not unique"

w39_row = (
    "- N1 波39（r530 bm-b 落 prereg 时展行·**第二十八枚引擎波·bm-b 第十三枚自有波**"
    "〔engine_owner=bm-b·SATURATION_ENGINE_LAW §1/§2 同 W10-W38 合同·不入池·免预认领·"
    "cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**"
    "〔本机上一波 W38 同窗 12/12 烧毕（r530：产品外科交付 origin 840df662a·r310 交付律·"
    "finalize 链序受阻=W37 块未落〔bm-c 面·MSG-20261002-012x 已提醒〕·r543 链序 W37→W38→W39〕"
    "→零间隔物化下一波·波号=39=W38 公示认领后首个自由号〔bm-b r529 W38 行落地=号位占用·"
    "r511 表尾锁律冻结前 fetch 实核表尾无 W39 行=号位净空·first-free-number 法〕〕·"
    "never-dry 供给律常设步〔r530 实况=引擎活〔status exit 0〕·队列空〔W38 12/12 烧毕〕·"
    "板负面已毕·禁空转禁等 CEO 提醒〕〕）：A-ext seed=**121_004..123_003**"
    "（**A 面算术顺延**〔==W38 A 尾 121_003+1·步长逐字·零跳位〕·**机证净空·registry-derive**"
    "〔候选=注册表 derive 非散文·带闸 leg1-A/leg2-A 机证==W38 行公示投影 CLEAN==候选〕·"
    "扫描面=pre-W39 三十六行 N1 带表〔含 W34 行 111_004..113_003/41_801..42_000"
    "〔r527 bm-b·finalize 已落账 K=72,720〕·W35 行 113_004..115_003/42_001..42_200"
    "〔r545 bm-a·finalize 已落账 K=74,920〕·**W36 行 115_004..117_003/42_201..42_400"
    "〔r528 bm-b·finalize 已落账 K=77,120·净链头 441,740〕**·**W37 行 117_004..119_003/"
    "42_401..42_600〔r341 bm-c·12/12 烧毕=注册在用面·finalize 链序待落〕**·"
    "**W38 行 119_004..121_003/42_601..42_800〔r529 bm-b·12/12 烧毕同窗=注册在用面·"
    "finalize 链序待落·带域不相交=异带共存 r531 律〕**〕＋W1 ext＋v1 在用带＋"
    "SEED_REGISTRY 全值〔**161 值·起草窗实测·bm-a LOWAMP-P3 新登记 3 值已并入**〕＋"
    "**N3-R1 实际种子集 70_000..70_005**〔r529 裁定行②强制腿〕＋**runner 探针种子簇 "
    "95_000..95_003**〔r335 发现腿·W26 起强制〕＋N2/N4 设计探针保留点 40_000/40_001＋"
    "N2-W15 草案探针点 31_000/31_500/32_000＋lfc 实际流 30_000..30_099＋options_wave2 "
    "实际流 63_000..63_049〔leg-3e 实际流避让腿〕·**ADMIT 回执=results/_r530bmb_w39_band_"
    "gate.py**〔r530 bm-b 起草窗实跑·leg0 三十六行+候选注册面校验+leg0b W38 行 W39+ 警示 "
    "prose 在场校验+leg1-A registry-derive 算术窗 CLEAN 机证+leg1-B refusal facts="
    "[43_000 p4_folk] 跳位被迫性机证+leg2-A 首净窗==候选〔零跳位〕+leg2-B 跳位后首净窗=="
    "候选〔强制跳位〕+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验〕·非重挑"
    "〔W39 带从未指派·测量面零结果可钓·R250〕〕）；B-ext exit seed=**43_001..43_200**"
    "（**B 面强制跳位**：算术位 42_801..43_000 **REFUSED**〔尾点 43_000=SEED_REGISTRY"
    "〔p4_folk〕在册值命中·leg1-B refusal facts 机证=跳位被迫性非自由挑·r307 常供面波带尾律"
    "先例〕→跳过 43_000 后首净窗 43_001..43_200〔leg2-B derive·全预留面穷尽扫描机证〕·"
    "两侧独立裁定如实披露〔A 侧仍按算术位〕＝W38 行 W39+ 警示原文逐字执行）。"
    "**N2/N4 让位注记**：本波 A 带 121_004..123_003——N2/N4 波级 prereg 冻结时按本表防撞律"
    "回避该域。**W40+ 警示**：A +2_000 算术位（123_004..125_003）与 B +200 算术位"
    "（43_201..43_400）投影以 r530 带闸回执 W40+ 投影腿机证为准（双投影 CLEAN·机闸 derive "
    "非 prose 转抄·r535 律·去节流令下=首个自由号法·无座位指派）。\n"
)
w39_row = w39_row.replace("\r\n", "\n")

t = data.replace(anchor, "\n" + w39_row + anchor[1:])
p.write_bytes(t.encode("utf-8"))
print("W39 law row landed in research/PERPETUAL_FACES.md sec.4 (byte-level LF)")
