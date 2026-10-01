import subprocess
p = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\research\PERPETUAL_FACES.md"
raw = open(p, "rb").read()
nl = b"\r\n"
text = raw.decode("utf-8")
sep = nl.decode("ascii")
lines = text.split(sep)
idx = None
for i, l in enumerate(lines):
    if l.startswith("- N1 波40"):
        idx = i
        break
assert idx is not None, "W40 law row not found"
print("W40 row at split-index", idx, "| next repr:", repr(lines[idx + 1][:30]))
w41 = "- N1 波41（r344 bm-c 冻·prereg 时展行）：**第三十一枚引擎波·bm-c 第十枚自有波**·engine_owner=bm-c·SATURATION_ENGINE_LAW §1/§2 同 W10-W40 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机上波=W39 同窗全生命周期收官（r342 冻结→12/12 免重启烧录 01:25-01:27〔D-20261002-03 修法 live 验证面 PASS·免重启首验波〕→r343 finalize one-pass K=83,720·账本链头 448,340·prereg s7/s8 回填齐·r344 产品件补交付 origin）→零隔接力·波号 41=W40 行落账后首个自由号·r511 表尾锁例冻结前 fetch 实核表尾时 W41 号位净空·first-free-number 法】·【never-dry 供给律常设步·r344 实况=引擎活·status exit 0·队列空·W39 12/12 在册·W40 bm-b 烧录在飞·池面 LOWAMP-P3 族 bm-a 认领在飞·车道负怠已披露禁空转禁等 CEO 提醒】·A-ext seed=**125_004..127_003**（**A 面算术顺延**·=W40 A 尾 125_003+1·步长逐字·**零跳位**·【机证净空**registry-derive**——leg1-A/leg2-A 机证==W40 行公示投影 CLEAN==候选**】·扫描面=pre-W41 三十八行 N1 带表【含 W37 行 117_004..119_003/42_401..42_600（r341 bm-c·finalize 实落账 K=79,320）·W38 行 119_004..121_003/42_601..42_800（r529 bm-b·finalize 实落账 K=81,520·链头 446,140）·W39 行 121_004..123_003/43_001..43_200（r342 bm-c·finalize 实落账 K=83,720·链头 448,340）·W40 行 123_004..125_003/43_201..43_400（r531 bm-b·烧录在飞=注册在用面）】·带域不相交·异带共存 r531 律·W1 ext·v1 在用带·SEED_REGISTRY 全集**161 值·起扫窗实证**·**N3-R1 实际种子带 70_000..70_005**（r529 裁定行强制腿）·**runner 探针种子簇 95_000..95_003**（r335 发现腿·W26 起强制）·N2/N4 设计探针保留点 40_000/40_001·N2-W15 草案探针点 31_000/31_500/32_000·lfc 实际抽带 30_000..30_099·options_wave2 实际抽带 63_000..63_049·leg-3e 实际流避让**】·**ADMIT 回执=results/_r344bmc_w41_band_gate.py**·r344 bm-c 起草窗实跑【leg0 三十八行+候选注册面校验+leg0b W40 行 W41+ 警示 prose 在场校验+leg1-A registry-derive 算术面 CLEAN 机证+leg1-B 算术面 CLEAN 机证+leg2-A 首净窗=候选**零跳位**·leg2-B 首净窗=候选**零跳位**·leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验**非重挑 R250**·W41 带从未指派·测量面零结果可钓**】·B-ext exit seed=**43_401..43_600**（**B 面算术顺延**·=W40 B 尾 43_400+1·步长逐字·**零跳位**·【机证净空**registry-derive**——leg1-B/leg2-B 机证==W40 行公示投影 CLEAN==候选·两侧独立裁定如实披露·A/B 双侧零跳位】）。**N2/N4 让位注记**：本波 A 带 125_004..127_003——N2/N4 波级 prereg 冻结时按本表防撞律回避该域。**W42+ 警示**：A +2_000 算术位（127_004..129_003）与 B +200 算术位（43_601..43_800）为 r344 带闸投影——执行 W42+ 投影仍以届时带闸 derive 为准（带闸 derive 非 prose 转抄·r535 律；去节流令下号位=上枚行落账后首个自由号生成·见§5 账本·跨波累计 N_eff 恒不重置）。"
lines.insert(idx + 1, w41)
open(p, "wb").write(sep.join(lines).encode("utf-8"))
print("INSERTED after split-index", idx, "| new total lines:", len(lines))
r = subprocess.run(["git", "-C", r"K:\Fluxgroup\FluxGroup\quant\bigmoney",
                    "diff", "--stat", "research/PERPETUAL_FACES.md"],
                   capture_output=True, encoding="utf-8")
print(r.stdout)
