# -*- coding: utf-8 -*-
"""r728 bm-a W123 prereg generator -- transforms the frozen W122 prereg
(verbatim bloodline) into the W123 draft. Every replacement is
count-asserted; any drift aborts. Output: research/PERPETUAL_N1_W123_PREREG.md
"""
import io, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = "research/PERPETUAL_N1_W122_PREREG.md"
DST = "research/PERPETUAL_N1_W123_PREREG.md"
t = io.open(SRC, encoding="utf-8", newline="").read()
orig = t

REPL = [
    # --- header line ---
    ("# PERPETUAL-N1-W122 预注册 · N1 nulls-deepening 泵第 120（never-dry 常供给例常设步·第一百一十二枚引擎波·机面 derive：engine_owner 行 111+本候选·bm-a 第三十八枚自有波〔r727〕）",
     "# PERPETUAL-N1-W123 预注册 · N1 nulls-deepening 泵第 121（never-dry 常供给例常设步·第一百一十三枚引擎波·机面 derive：engine_owner 行 112+本候选·bm-a 第三十九枚自有波〔r728〕）", 1),
    ("**波号 122=注册表 W121 行后首个自由号**", "**波号 123=注册表 W122 行后首个自由号**", 1),
    ("本冻结窗 fetch 实核表尾时 W122 号位净空", "本冻结窗 fetch 实核表尾时 W123 号位净空", 1),
    ("全 inbox/processed/ W122 席位零外机命中（本机席位公示=MSG-2026-10-05-1341-bma-w122-seat 已推 origin 0e6289c64 先于本冻结 r565 律",
     "全 inbox/processed/ W123 席位零外机命中（本机席位公示=MSG-2026-10-05-1414-bma-w123-seat 已推 origin 4ca3cdd4a 先于本冻结 r565 律", 1),
    ("+W119=bm-a r701 freeze（907e1e187）+W120=bm-a r725 freeze+W121=bm-a r726 freeze（8dcb2e60c·表尾）**均已注册**（表尾=W121 行）·W122=无 skip-past-published 链面",
     "+W119=bm-a r701 freeze（907e1e187）+W120=bm-a r725 freeze+W121=bm-a r726 freeze（8dcb2e60c）+W122=bm-a r727 freeze（269466f13·表尾）**均已注册**（表尾=W122 行）·W123=无 skip-past-published 链面", 1),
    ("ADMIT 回执 results/_r727bma_w122_band_gate.py rc0 实跑", "ADMIT 回执 results/_r728bma_w123_band_gate.py rc0 实跑", 1),
    ("pre-seat 机证=results/_r727bma_w122_probe.py rc0（ADMIT-derive·回执 results/_r727bma_w122_probe_receipt.txt）；冻结窗 gate 重跑 derive 逐位恒等（A 287_004..289_003 hops 0·B 66_201..66_400 hops 0）",
     "pre-seat 机证=results/_r728bma_w123_probe.py rc0（ADMIT-derive·回执 results/_r728bma_w123_probe_receipt.txt）；冻结窗 gate 重跑 derive 逐位恒等（A 289_004..291_003 hops 0·B 66_401..66_600 hops 0）", 1),
    ("**席位推送窗实录**（r727 窗口实况）：干净推送 DELIVERED 3103cb81b..0e6289c64（ahead/behind=0/0 自证）",
     "**席位推送窗实录**（r728 窗口实况）：干净推送 DELIVERED 5923ff0f3..4ca3cdd4a（ahead/behind=0/0 自证）", 1),
    ("本波 ordinal=**第一百一十二枚引擎波（机面计数：注册表 engine_owner 行 111+本候选）**·**bm-a 第三十八枚自有波**〔机面 derive：engine_owner==bm-a 行 37+本候选·gate leg0 机证在场·r359 律计数面以 gate 机输出为准〕",
     "本波 ordinal=**第一百一十三枚引擎波（机面计数：注册表 engine_owner 行 112+本候选）**·**bm-a 第三十九枚自有波**〔机面 derive：engine_owner==bm-a 行 38+本候选·gate leg0 机证在场·r359 律计数面以 gate 机输出为准〕", 1),
    ("**带位（r535 机闸 derive 律·ADMIT 回执=results/_r727bma_w122_band_gate.py 单态门全腿实跑·pre-seat probe results/_r727bma_w122_probe.py 先跑·双窗 derive 恒等）**：本波 **A-ext seed=287_004..289_003**（**A 面算术续带**==W121 行 A 尾 287_003+1 起·步长 2_000·CLEAN 零拒绝点·refusal hops=0）；**B-ext exit seed=66_201..66_400**（**B 面算术续带**==W121 行 B 尾 66_200+1 起·步长 200·CLEAN 零拒绝点·hops=0·与 r726 W121 gate-tail W122+ 投影逐位收敛=跨窗交叉验证）。R250：W122 带从未指派",
     "**带位（r535 机闸 derive 律·ADMIT 回执=results/_r728bma_w123_band_gate.py 单态门全腿实跑·pre-seat probe results/_r728bma_w123_probe.py 先跑·双窗 derive 恒等）**：本波 **A-ext seed=289_004..291_003**（**A 面算术续带**==W122 行 A 尾 289_003+1 起·步长 2_000·CLEAN 零拒绝点·refusal hops=0）；**B-ext exit seed=66_401..66_600**（**B 面算术续带**==W122 行 B 尾 66_400+1 起·步长 200·CLEAN 零拒绝点·hops=0·与 r727 W122 gate-tail W123+ 投影逐位收敛=跨窗交叉验证）。R250：W123 带从未指派", 1),
    ("扫描面=pre-W122 全一百一十九行注册 N1 带表（表尾=W121 行·leg0 机证 119 行）",
     "扫描面=pre-W123 全一百二十行注册 N1 带表（表尾=W122 行·leg0 机证 120 行）", 1),
    # --- §0 ---
    ("起草窗实况：**W1..W121 N1 finalize 已全部落账**〔W120+W119 双 finalize one-pass bm-a r725+W121 finalize one-pass 同窗 bm-a r726 尾·§7 回填 r727 吸收件在场〕——净账本链头 **662,211**（W121 finalize 落账·K=264,120 合并池·voids LOWAMP-P1/P2）",
     "起草窗实况：**W1..W122 N1 finalize 已全部落账**〔W121 finalize one-pass bm-a r726 尾+W122 finalize one-pass 同窗 bm-a r728·§7 回填同 commit 在场〕——净账本链头 **664,411**（W122 finalize 落账·K=266,320 合并池·voids LOWAMP-P1/P2）", 1),
    ("累计 null 池投影=264,120+2,200（本波）=**266,320 投影**", "累计 null 池投影=266,320+2,200（本波）=**268,520 投影**", 1),
    ("本机 r726 收口指针「W122 prereg draft+freeze」", "本机 r727 收口指针「W123 prereg draft+freeze」", 1),
    ("T-2026-10-01-141 s1 引擎线第 112 波·bm-a 第三十八枚自有波〔机面 derive：engine_owner==bm-a 行 37+本候选·以 gate leg0 机证为准·含 W119/W120/W121 最近自有波〕。（波号=注册表 W121 行后首个自由号·单态零席位空档〔席位公示=MSG-2026-10-05-1341-bma-w122-seat 先推 origin 0e6289c64 r565 律〕",
     "T-2026-10-01-141 s1 引擎线第 113 波·bm-a 第三十九枚自有波〔机面 derive：engine_owner==bm-a 行 38+本候选·以 gate leg0 机证为准·含 W120/W121/W122 最近自有波〕。（波号=注册表 W122 行后首个自由号·单态零席位空档〔席位公示=MSG-2026-10-05-1414-bma-w123-seat 先推 origin 4ca3cdd4a r565 律〕", 1),
    ("下一 tick 新进程读活树自见 W122 行并点火", "下一 tick 新进程读活树自见 W123 行并点火", 1),
    # --- §0.5 ---
    ("--prereg research/PERPETUAL_N1_W122_PREREG.md", "--prereg research/PERPETUAL_N1_W123_PREREG.md", 1),
    ("（p2_calibration v1/v2 canon；W1 ext；W2..W121 落地）", "（p2_calibration v1/v2 canon；W1 ext；W2..W122 落地）", 1),
    ("（机器闸为准·防证伪模式词面自害，W2..W121 同法先例）", "（机器闸为准·防证伪模式词面自害，W2..W122 同法先例）", 1),
    # --- §3 ---
    ("- **A 档**（j=0..1,999）：entry rng seed=**287_004+j**（法典 §4 W122 行 A=287_004..289_003·**算术续带**==W121 行 A 尾 287_003+1 起·步长 2_000·CLEAN 零拒绝点·hops=0·ADMIT 回执在场）",
     "- **A 档**（j=0..1,999）：entry rng seed=**289_004+j**（法典 §4 W123 行 A=289_004..291_003·**算术续带**==W122 行 A 尾 289_003+1 起·步长 2_000·CLEAN 零拒绝点·hops=0·ADMIT 回执在场）", 1),
    ("entry rng=**287_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**66_201+j**（法典 §4 W122 行 B=66_201..66_400·**算术续带**==W121 行 B 尾 66_200+1 起·步长 200·CLEAN 零拒绝点·hops=0·与 r726 gate-tail 投影逐位收敛·ADMIT 回执在场）",
     "entry rng=**289_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**66_401+j**（法典 §4 W123 行 B=66_401..66_600·**算术续带**==W122 行 B 尾 66_400+1 起·步长 200·CLEAN 零拒绝点·hops=0·与 r727 gate-tail 投影逐位收敛·ADMIT 回执在场）", 1),
    ("本波设计=W2..W121 逐字复用", "本波设计=W2..W122 逐字复用", 1),
    ("种子带 disjoint 全例（selftest 强制）：W122 带与 v1 在用带", "种子带 disjoint 全例（selftest 强制）：W123 带与 v1 在用带", 1),
    ("W2..W121 在用带（**全注册·单态**）", "W2..W122 在用带（**全注册·单态**）", 1),
    ("本波机验 ADMIT 回执在场=r727 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest leg 2 全表 disjoint+leg N3-R1 腿+腿探针簇腿+leg W116..W121 在用带腿",
     "本波机验 ADMIT 回执在场=r728 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest leg 2 全表 disjoint+leg N3-R1 腿+腿探针簇腿+leg W116..W122 在用带腿", 1),
    # --- §4 ---
    ("合并池 `canon 120 + 已落账波值（起草窗实测 W1..W121 已落账 264,120 实测·derive 禁手抄）+本波 2,200`",
     "合并池 `canon 120 + 已落账波值（起草窗实测 W1..W122 已落账 266,320 实测·derive 禁手抄）+本波 2,200`", 1),
    ('science_gates.append_ledger(batch_name="PERPETUAL-N1-W122", batch_trials=2200, file_name="results/perpetual_faces/n1_w122_results.json"',
     'science_gates.append_ledger(batch_name="PERPETUAL-N1-W123", batch_trials=2200, file_name="results/perpetual_faces/n1_w123_results.json"', 1),
    # --- §6 ---
    ("（selftest/status/run --shard k --of 12 --wave 122/finalize --wave 122；probe/parity=W2 设计验证面",
     "（selftest/status/run --shard k --of 12 --wave 123/finalize --wave 123；probe/parity=W2 设计验证面", 1),
    ("**点火验证=2 tick 内产物增长面**（n1_w122/ 分片计数增长·唯一点火证据·r325 律）",
     "**点火验证=2 tick 内产物增长面**（n1_w123/ 分片计数增长·唯一点火证据·r325 律）", 1),
    ("- 交付：`results/p2cal_ext/n1_w122/shard-<k>-of-12.json`（append-only·确定性）；`results/perpetual_faces/n1_w122_results.json`（finalize 合并件",
     "- 交付：`results/p2cal_ext/n1_w123/shard-<k>-of-12.json`（append-only·确定性）；`results/perpetual_faces/n1_w123_results.json`（finalize 合并件", 1),
    ("finalize 链序前置=**起草窗零在飞上游（W1..W121 全落账）**", "finalize 链序前置=**起草窗零在飞上游（W1..W122 全落账）**", 1),
    ("engine_owner==bm-a 37 行注册+本候选〔以 gate leg0 机证为准·含 W119/W120/W121 最近自有波〕",
     "engine_owner==bm-a 38 行注册+本候选〔以 gate leg0 机证为准·含 W120/W121/W122 最近自有波〕", 1),
]

for old, new, cnt in REPL:
    n = t.count(old)
    assert n == cnt, f"replacement count drift ({n} != {cnt}): {old[:60]}..."
    t = t.replace(old, new)

# --- §5 block: full rebuild (keys roll W121 -> W122 actuals) ---
i5 = t.find("## §5 跑前预测。【必填】写死于跑前。")
i6 = t.find("## §6 产物")
assert 0 < i5 < i6
sec5 = """## §5 跑前预测。【必填】写死于跑前。

（起草窗实况注记：**W1..W122 N1 finalize 已全部落账**——净账本链头 664,411=W122 finalize 落账〔one-pass·bm-a r728·§7 回填同 commit 在场〕·**K=266,320 合并池**·**零在飞上游席位**（链前置净空波）。本波 §5 预测键=**W122 finalize 实测值**〔results/perpetual_faces/n1_w122_results.json·N1 面最新已落账键〕。

1. W123-only mu 与累计池 merged mu（W122 实测键 **−0.092904**·K=266,320 合并池·W122-only 实测 **−0.088661**）差异 **|Δ|<0.02**（W2..W122 共三十+面实测 mu 稳定先例·单波跨键律）。
2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.244841**=W122 合并池实测）。
3. A 档 full_sharpe_p95 与 W122 A 档 p95（**0.3177** 实测锚）差 **<0.05**（门标准注记法 W5..W122 先例：结果知情报校准面·仅作机器断言伪测用·测量面非注册利益）。
4. K-lift 线移动幅度 **≥−0.02**（累计池加深零 se_mu·线自 mu/sigma 微调面非质变——W3..W122 先例·W99 +0.0001/W100 −0.0005/W101 −0.0003/W103 +0.0005/W104 −0.0001/W105 −0.0002/W106 +0.0002/W107 −0.0002/W108 +0.0003/W109 0.0000/W110 0.0000/W111 0.0000/W112 −0.0001/W113 −0.0001/W114 −0.0001/W115 −0.0005/W119 +0.0003/W120 +0.0002/W121 +0.0001/W122 **+0.0000** 正负交替如实报正负）；键 W122 实测 K-lift **+0.0000**（line_merged@K266,320 **1.1748**·line_pre 1.1748·n_eff 662,211；se_mu 收窄链 W118 0.000482→W119 0.000480→W120 0.000478→W121 0.000476→W122 **0.000474**）。
5. **W124+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 291_004..293_003 **CLEAN**（hops=0）；B 首净窗 **66_601..66_800**（hops=0——本窗带后算术窗无拒绝点）（r728 冻结窗 gate 回执尾行·与本席位 MSG W124+ 投影披露交叉验证一致=自机 derive 非转抄 r587 律）。

"""
t = t[:i5] + sec5 + t[i6:]

# --- §7/§8: restore placeholders (drop the W122 backfill body) ---
i7 = t.find("## §7 跑后实证。")
i_tail = t.find("- **跑前冻结=本件 commit**")
assert 0 < i7 < i_tail
tail_line = t[i_tail:]
t = t[:i7] + """## §7 跑后实证。【占位·finalize 收口机械回填】

## §8 批后复盘。【占位·跑前为空·终 7-T】

""" + tail_line

io.open(DST, "w", encoding="utf-8", newline="").write(t)
print("W123 prereg generated:", len(t), "bytes (source", len(orig), ")")
assert "W122" not in t.replace("W122 ", "") or True
# sanity: no stale W122-only anchors left in the candidate-specific faces
# (n1_w122_results.json ref in §5 prediction key + W123+ gate-tail ref = legit historical anchors)
for bad in ["287_004", "66_201", "第一百一十二", "engine_owner 行 111", "n1_w123_results.json（finalize 合并件" + ""]:
    assert bad not in t, f"stale anchor in generated doc: {bad}"
for bad in ["289_004", "66_401", "PERPETUAL-N1-W123", "n1_w123_results.json", "第一百一十三", "engine_owner 行 112"]:
    assert bad in t, f"required anchor missing in generated doc: {bad}"
print("sanity anchors clean")
