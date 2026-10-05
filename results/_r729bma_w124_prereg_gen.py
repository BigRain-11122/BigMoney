# -*- coding: utf-8 -*-
"""r729 bm-a W124 prereg generator -- transforms the backfilled W123 prereg
(verbatim bloodline) into the W124 draft. Every replacement is
count-asserted; any drift aborts. Output: research/PERPETUAL_N1_W124_PREREG.md
Bloodline note: the W123 prereg sec0 batch-name line carried an inherited
typo (PERPETUAL-N1-W122 inside the W123 file, r728 generator miss); fixed
honestly here for W124 (frozen W123 history untouched, disclosed in r729).
"""
import io, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = "research/PERPETUAL_N1_W123_PREREG.md"
DST = "research/PERPETUAL_N1_W124_PREREG.md"
t = io.open(SRC, encoding="utf-8", newline="").read()
orig = t

REPL = [
    # --- header line ---
    ("# PERPETUAL-N1-W123 预注册 · N1 nulls-deepening 泵第 121（never-dry 常供给例常设步·第一百一十三枚引擎波·机面 derive：engine_owner 行 112+本候选·bm-a 第三十九枚自有波〔r728〕）",
     "# PERPETUAL-N1-W124 预注册 · N1 nulls-deepening 泵第 122（never-dry 常供给例常设步·第一百一十四枚引擎波·机面 derive：engine_owner 行 113+本候选·bm-a 第四十枚自有波〔r729〕）", 1),
    ("**波号 123=注册表 W122 行后首个自由号**", "**波号 124=注册表 W123 行后首个自由号**", 1),
    ("本冻结窗 fetch 实核表尾时 W123 号位净空", "本冻结窗 fetch 实核表尾时 W124 号位净空", 1),
    ("全 inbox/processed/ W123 席位零外机命中（本机席位公示=MSG-2026-10-05-1414-bma-w123-seat 已推 origin 4ca3cdd4a 先于本冻结 r565 律",
     "全 inbox/processed/ W124 席位零外机命中（本机席位公示=MSG-2026-10-05-1437-bma-w124-seat 已推 origin 68cca11d5 先于本冻结 r565 律", 1),
    ("+W122=bm-a r727 freeze（269466f13·表尾）**均已注册**（表尾=W122 行）·W123=无 skip-past-published 链面",
     "+W122=bm-a r727 freeze（269466f13）+W123=bm-a r728 freeze（cd049a2ab·表尾）**均已注册**（表尾=W123 行）·W124=无 skip-past-published 链面", 1),
    ("ADMIT 回执 results/_r728bma_w123_band_gate.py rc0 实跑", "ADMIT 回执 results/_r729bma_w124_band_gate.py rc0 实跑", 1),
    ("pre-seat 机证=results/_r728bma_w123_probe.py rc0（ADMIT-derive·回执 results/_r728bma_w123_probe_receipt.txt）；冻结窗 gate 重跑 derive 逐位恒等（A 289_004..291_003 hops 0·B 66_401..66_600 hops 0）",
     "pre-seat 机证=results/_r729bma_w124_probe.py rc0（ADMIT-derive·回执 results/_r729bma_w124_probe_receipt.txt）；冻结窗 gate 重跑 derive 逐位恒等（A 291_004..293_003 hops 0·B 66_601..66_800 hops 0）", 1),
    ("**席位推送窗实录**（r728 窗口实况）：干净推送 DELIVERED 5923ff0f3..4ca3cdd4a（ahead/behind=0/0 自证）——零爪拦零 --no-verify",
     "**席位推送窗实录**（r729 窗口实况）：首推撞 origin 前进 7 commit（r524 律=落后信号非误写）→merge-mode 零 UU 收口→DELIVERED 4bef7f830..53c0ecbc5（seat commit 68cca11d5 随 merge 送达·ahead/behind=0/0 自证）——零爪拦零 --no-verify", 1),
    ("本波 ordinal=**第一百一十三枚引擎波（机面计数：注册表 engine_owner 行 112+本候选）**·**bm-a 第三十九枚自有波**〔机面 derive：engine_owner==bm-a 行 38+本候选",
     "本波 ordinal=**第一百一十四枚引擎波（机面计数：注册表 engine_owner 行 113+本候选）**·**bm-a 第四十枚自有波**〔机面 derive：engine_owner==bm-a 行 39+本候选", 1),
    ("ADMIT 回执=results/_r728bma_w123_band_gate.py 单态门全腿实跑·pre-seat probe results/_r728bma_w123_probe.py 先跑·双窗 derive 恒等）**：本波 **A-ext seed=289_004..291_003**（**A 面算术续带**==W122 行 A 尾 289_003+1 起·步长 2_000·CLEAN 零拒绝点·refusal hops=0）；**B-ext exit seed=66_401..66_600**（**B 面算术续带**==W122 行 B 尾 66_400+1 起·步长 200·CLEAN 零拒绝点·hops=0·与 r727 W122 gate-tail W123+ 投影逐位收敛=跨窗交叉验证）。R250：W123 带从未指派",
     "ADMIT 回执=results/_r729bma_w124_band_gate.py 单态门全腿实跑·pre-seat probe results/_r729bma_w124_probe.py 先跑·双窗 derive 恒等）**：本波 **A-ext seed=291_004..293_003**（**A 面算术续带**==W123 行 A 尾 291_003+1 起·步长 2_000·CLEAN 零拒绝点·refusal hops=0）；**B-ext exit seed=66_601..66_800**（**B 面算术续带**==W123 行 B 尾 66_600+1 起·步长 200·CLEAN 零拒绝点·hops=0·与 r728 W123 gate-tail W124+ 投影逐位收敛=跨窗交叉验证）。R250：W124 带从未指派", 1),
    ("扫描面=pre-W123 全一百二十行注册 N1 带表（表尾=W122 行·leg0 机证 120 行）",
     "扫描面=pre-W124 全一百二十一行注册 N1 带表（表尾=W123 行·leg0 机证 121 行）", 1),
    # --- §0 ---
    ("批名=**PERPETUAL-N1-W122**", "批名=**PERPETUAL-N1-W124**", 1),
    ("起草窗实况：**W1..W122 N1 finalize 已全部落账**〔W121 finalize one-pass bm-a r726 尾+W122 finalize one-pass 同窗 bm-a r728·§7 回填同 commit 在场〕——净账本链头 **664,411**（W122 finalize 落账·K=266,320 合并池·voids LOWAMP-P1/P2）",
     "起草窗实况：**W1..W123 N1 finalize 已全部落账**〔W122 finalize one-pass bm-a r728+W123 finalize one-pass 同窗 bm-a r729·§7 回填同 commit 在场〕——净账本链头 **666,611**（W123 finalize 落账·K=268,520 合并池·voids LOWAMP-P1/P2）", 1),
    ("累计 null 池投影=266,320+2,200（本波）=**268,520 投影**", "累计 null 池投影=268,520+2,200（本波）=**270,720 投影**", 1),
    ("本机 r727 收口指针「W123 prereg draft+freeze」", "本机 r728 收口指针「W124 prereg draft+freeze」", 1),
    ("T-2026-10-01-141 s1 引擎线第 113 波·bm-a 第三十九枚自有波〔机面 derive：engine_owner==bm-a 行 38+本候选·以 gate leg0 机证为准·含 W120/W121/W122 最近自有波〕。（波号=注册表 W122 行后首个自由号·单态零席位空档〔席位公示=MSG-2026-10-05-1414-bma-w123-seat 先推 origin 4ca3cdd4a r565 律〕",
     "T-2026-10-01-141 s1 引擎线第 114 波·bm-a 第四十枚自有波〔机面 derive：engine_owner==bm-a 行 39+本候选·以 gate leg0 机证为准·含 W121/W122/W123 最近自有波〕。（波号=注册表 W123 行后首个自由号·单态零席位空档〔席位公示=MSG-2026-10-05-1437-bma-w124-seat 先推 origin 68cca11d5 r565 律〕", 1),
    ("下一 tick 新进程读活树自见 W123 行并点火", "下一 tick 新进程读活树自见 W124 行并点火", 1),
    # --- §0.5 ---
    ("--prereg research/PERPETUAL_N1_W123_PREREG.md", "--prereg research/PERPETUAL_N1_W124_PREREG.md", 1),
    ("（p2_calibration v1/v2 canon；W1 ext；W2..W122 落地）", "（p2_calibration v1/v2 canon；W1 ext；W2..W123 落地）", 1),
    ("（机器闸为准·防证伪模式词面自害，W2..W122 同法先例）", "（机器闸为准·防证伪模式词面自害，W2..W123 同法先例）", 1),
    # --- §3 ---
    ("entry rng seed=**289_004+j**（法典 §4 W123 行 A=289_004..291_003·**算术续带**==W122 行 A 尾 289_003+1 起·步长 2_000·CLEAN 零拒绝点·hops=0·ADMIT 回执在场）",
     "entry rng seed=**291_004+j**（法典 §4 W124 行 A=291_004..293_003·**算术续带**==W123 行 A 尾 291_003+1 起·步长 2_000·CLEAN 零拒绝点·hops=0·ADMIT 回执在场）", 1),
    ("entry rng=**289_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**66_401+j**（法典 §4 W123 行 B=66_401..66_600·**算术续带**==W122 行 B 尾 66_400+1 起·步长 200·CLEAN 零拒绝点·hops=0·与 r727 gate-tail 投影逐位收敛·ADMIT 回执在场）",
     "entry rng=**291_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**66_601+j**（法典 §4 W124 行 B=66_601..66_800·**算术续带**==W123 行 B 尾 66_600+1 起·步长 200·CLEAN 零拒绝点·hops=0·与 r728 gate-tail 投影逐位收敛·ADMIT 回执在场）", 1),
    ("本波设计=W2..W122 逐字复用", "本波设计=W2..W123 逐字复用", 1),
    ("种子带 disjoint 全例（selftest 强制）：W123 带与 v1 在用带", "种子带 disjoint 全例（selftest 强制）：W124 带与 v1 在用带", 1),
    ("W2..W122 在用带（**全注册·单态**）", "W2..W123 在用带（**全注册·单态**）", 1),
    ("本波机验 ADMIT 回执在场=r728 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest leg 2 全表 disjoint+leg N3-R1 腿+腿探针簇腿+leg W116..W122 在用带",
     "本波机验 ADMIT 回执在场=r729 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest leg 2 全表 disjoint+leg N3-R1 腿+腿探针簇腿+leg W116..W123 在用带", 1),
    # --- §4 ---
    ("合并池 `canon 120 + 已落账波值（起草窗实测 W1..W122 已落账 266,320 实测·derive 禁手抄）+本波 2,200`",
     "合并池 `canon 120 + 已落账波值（起草窗实测 W1..W123 已落账 268,520 实测·derive 禁手抄）+本波 2,200`", 1),
    ('science_gates.append_ledger(batch_name="PERPETUAL-N1-W123", batch_trials=2200, file_name="results/perpetual_faces/n1_w123_results.json"',
     'science_gates.append_ledger(batch_name="PERPETUAL-N1-W124", batch_trials=2200, file_name="results/perpetual_faces/n1_w124_results.json"', 1),
    # --- §6 ---
    ("（selftest/status/run --shard k --of 12 --wave 123/finalize --wave 123；probe/parity=W2 设计验证面",
     "（selftest/status/run --shard k --of 12 --wave 124/finalize --wave 124；probe/parity=W2 设计验证面", 1),
    ("**点火验证=2 tick 内产物增长面**（n1_w123/ 分片计数增长·唯一点火证据·r325 律）",
     "**点火验证=2 tick 内产物增长面**（n1_w124/ 分片计数增长·唯一点火证据·r325 律）", 1),
    ("- 交付：`results/p2cal_ext/n1_w123/shard-<k>-of-12.json`（append-only·确定性）；`results/perpetual_faces/n1_w123_results.json`（finalize 合并件",
     "- 交付：`results/p2cal_ext/n1_w124/shard-<k>-of-12.json`（append-only·确定性）；`results/perpetual_faces/n1_w124_results.json`（finalize 合并件", 1),
    ("finalize 链序前置=**起草窗零在飞上游（W1..W122 全落账）**", "finalize 链序前置=**起草窗零在飞上游（W1..W123 全落账）**", 1),
    ("engine_owner==bm-a 38 行注册+本候选〔以 gate leg0 机证为准·含 W120/W121/W122 最近自有波〕",
     "engine_owner==bm-a 39 行注册+本候选〔以 gate leg0 机证为准·含 W121/W122/W123 最近自有波〕", 1),
]

for old, new, cnt in REPL:
    n = t.count(old)
    assert n == cnt, f"replacement count drift ({n} != {cnt}): {old[:60]}..."
    t = t.replace(old, new)

# --- §5 block: full rebuild (keys roll W123 -> W124 actuals) ---
i5 = t.find("## §5 跑前预测。【必填】写死于跑前。")
i6 = t.find("## §6 产物")
assert 0 < i5 < i6
sec5 = """## §5 跑前预测。【必填】写死于跑前。

（起草窗实况注记：**W1..W123 N1 finalize 已全部落账**——净账本链头 666,611=W123 finalize 落账〔one-pass·bm-a r729·§7 回填同 commit 在场〕·**K=268,520 合并池**·**零在飞上游席位**（链前置净空波）。本波 §5 预测键=**W123 finalize 实测值**〔results/perpetual_faces/n1_w123_results.json·N1 面最新已落账键〕。

1. W124-only mu 与累计池 merged mu（W123 实测键 **−0.092893**·K=268,520 合并池·W123-only 实测 **−0.091522**）差异 **|Δ|<0.02**（W2..W123 共三十+面实测 mu 稳定先例·单波跨键律）。
2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.244828**=W123 合并池实测）。
3. A 档 full_sharpe_p95 与 W123 A 档 p95（**0.3049** 实测锚）差 **<0.05**（门标准注记法 W5..W123 先例：结果知情报校准面·仅作机器断言伪测用·测量面非注册利益）。
4. K-lift 线移动幅度 **≥−0.02**（累计池加深零 se_mu·线自 mu/sigma 微调面非质变——W3..W123 先例·W99 +0.0001/W100 −0.0005/W101 −0.0003/W103 +0.0005/W104 −0.0001/W105 −0.0002/W106 +0.0002/W107 −0.0002/W108 +0.0003/W109 0.0000/W110 0.0000/W111 0.0000/W112 −0.0001/W113 −0.0001/W114 −0.0001/W115 −0.0005/W119 +0.0003/W120 +0.0002/W121 +0.0001/W122 +0.0000/W123 **+0.0000** 正负交替如实报正负）；键 W123 实测 K-lift **+0.0000**（line_merged@K268,520 **1.1749**·line_pre 1.1749·n_eff 664,411；se_mu 收窄链 W119 0.000480→W120 0.000478→W121 0.000476→W122 0.000474→W123 **0.000472**）。
5. **W125+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 293_004..295_003 **CLEAN**（hops=0）；B 首净窗 **67_201..67_400**（hops=2——66_801..67_200 区间含拒绝点·gate leg3 机证披露）（r729 冻结窗 gate 回执尾行·与本席位 MSG W125+ 投影披露交叉验证一致=自机 derive 非转抄 r587 律）。

"""
t = t[:i5] + sec5 + t[i6:]

# --- §7/§8: restore placeholders (drop the W123 backfill body) ---
i7 = t.find("## §7 跑后实证。")
i_tail = t.find("- **跑前冻结=本件 commit**")
assert 0 < i7 < i_tail
tail_line = t[i_tail:]
t = t[:i7] + """## §7 跑后实证。【占位·finalize 收口机械回填】

## §8 批后复盘。【占位·跑前为空·终 7-T】

""" + tail_line

io.open(DST, "w", encoding="utf-8", newline="").write(t)
print("W124 prereg generated:", len(t), "bytes (source", len(orig), ")")
# sanity: no stale W123-specific anchors in candidate faces
for bad in ["289_004", "66_401+j", "第一百一十三", "engine_owner 行 112", "engine_owner==bm-a 行 38", "266,320+2,200", "664,411**（W122 finalize"]:
    assert bad not in t, f"stale anchor in generated doc: {bad}"
for need in ["291_004", "66_601+j", "PERPETUAL-N1-W124", "n1_w124_results.json", "第一百一十四", "engine_owner 行 113", "270,720 投影", "批名=**PERPETUAL-N1-W124**"]:
    assert need in t, f"required anchor missing in generated doc: {need}"
print("sanity anchors clean")
