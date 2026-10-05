# -*- coding: utf-8 -*-
"""r741 bm-a: transform research/PERPETUAL_N1_W135_PREREG.md (post-finalize
state, sec7/8 filled) -> research/PERPETUAL_N1_W136_PREREG.md (fresh freeze
state, sec7/8 placeholders). Needle-count law (r735): every needle asserted."""
import io

SRC = "research/PERPETUAL_N1_W135_PREREG.md"
DST = "research/PERPETUAL_N1_W136_PREREG.md"
t = io.open(SRC, encoding="utf-8", newline="").read()

# --- 1. sec7/8 filled block -> placeholders (slicing, not needles) ---
i7 = t.find("## §7 跑后实证。【finalize 收口机械回填")
i_freeze = t.find("- **跑前冻结=本件 commit**")
assert i7 > 0 and i_freeze > i7, "sec7/8 block anchors"
placeholder = (
"## §7 跑后实证。【占位·finalize 收口机械回填】\n\n"
"## §8 批后复盘。【占位·跑前为空·终 7-T】\n\n"
)
t = t[:i7] + placeholder + t[i_freeze:]

pairs = [
 ("PERPETUAL-N1-W135 预注册 · N1 nulls-deepening 泵第 133（never-dry 常供给例常设步·第一百二十五枚引擎波·机面 derive：engine_owner 行 124+本候选·bm-a 第五十一枚自有波〔r740〕）",
  "PERPETUAL-N1-W136 预注册 · N1 nulls-deepening 泵第 134（never-dry 常供给例常设步·第一百二十六枚引擎波·机面 derive：engine_owner 行 125+本候选·bm-a 第五十二枚自有波〔r741〕）", 1),
 ("波号 135=注册表 W134 行后首个自由号", "波号 136=注册表 W135 行后首个自由号", 1),
 ("本冻结窗 fetch 实核表尾时 W135 号位净空", "本冻结窗 fetch 实核表尾时 W136 号位净空", 1),
 ("本机席位公示=MSG-2026-10-05-1933-bma-w135-seat 已推 origin 98712a0e3 先于本冻结 r565 律",
  "本机席位公示=MSG-2026-10-05-1952-bma-w136-seat 已推 origin 20d0036dc 先于本冻结 r565 律", 1),
 ("+W134=bm-a r739 freeze（d6b64dddd·表尾）**均已注册**（表尾=W134 行）·W135=无 skip-past-published 链面",
  "+W135=bm-a r740 freeze（bc921896a·表尾）**均已注册**（表尾=W135 行）·W136=无 skip-past-published 链面", 1),
 ("ADMIT 回执 results/_r740bma_w135_band_gate.py rc0 实跑）",
  "ADMIT 回执 results/_r741bma_w136_band_gate.py rc0 实跑）", 1),
 ("pre-seat 机证=results/_r740bma_w135_probe.py rc0（ADMIT-derive·回执 results/_r740bma_w135_probe_receipt.txt）",
  "pre-seat 机证=results/_r741bma_w136_probe.py rc0（ADMIT-derive·回执 results/_r741bma_w136_probe_receipt.txt）", 1),
 ("冻结窗 gate 重跑 derive 逐位恒等（A 313_004..315_003 hops 0·B 69_502..69_701 hops 0",
  "冻结窗 gate 重跑 derive 逐位恒等（A 315_004..317_003 hops 0·B 69_702..69_901 hops 0", 1),
 ("**席位推送窗实录**（r740 窗口实况）：席位+probe+回执三件单 commit 推送=**直推干净快进零撞拒零合并窗→DELIVERED 98712a0e3（origin 当场送达实证）**。",
  "**席位推送窗实录**（r741 窗口实况）：席位+probe+回执三件单 commit 推送=**首推撞拒 origin 前进 1 commit（r524 落后信号·bm-c r568 同窗波）→merge-mode 零 UU 收口→DELIVERED 20d0036dc（送达 commit 2564ba798）**。", 1),
 ("本波 ordinal=**第一百二十五枚引擎波（机面计数：注册表 engine_owner 行 124+本候选）**·**bm-a 第五十一枚自有波**〔机面 derive：engine_owner==bm-a 行 50+本候选",
  "本波 ordinal=**第一百二十六枚引擎波（机面计数：注册表 engine_owner 行 125+本候选）**·**bm-a 第五十二枚自有波**〔机面 derive：engine_owner==bm-a 行 51+本候选", 1),
 ("带位（r535 机闸 derive 律·ADMIT 回执=results/_r740bma_w135_band_gate.py 单态门全腿实跑·pre-seat probe results/_r740bma_w135_probe.py 先跑·双窗 derive 恒等）",
  "带位（r535 机闸 derive 律·ADMIT 回执=results/_r741bma_w136_band_gate.py 单态门全腿实跑·pre-seat probe results/_r741bma_w136_probe.py 先跑·双窗 derive 恒等）", 1),
 ("本波 **A-ext seed=313_004..315_003**（**A 面算术续带**==W134 行 A 尾 313_003+1 起·步长 2_000·CLEAN 零拒绝点·refusal hops=0）；**B-ext exit seed=69_502..69_701**（**B 面算术续带**==W134 行 B 尾 69_501+1 起·步长 200·CLEAN 零拒绝点·refusal hops=0·双 CLEAN 窗）·与 r739 W134 席位 MSG-1857 W135+ 投影逐位收敛=跨窗交叉验证（r587 律·W134 §8 遗留指针的承诺兑现）",
  "本波 **A-ext seed=315_004..317_003**（**A 面算术续带**==W135 行 A 尾 315_003+1 起·步长 2_000·CLEAN 零拒绝点·refusal hops=0）；**B-ext exit seed=69_702..69_901**（**B 面算术续带**==W135 行 B 尾 69_701+1 起·步长 200·CLEAN 零拒绝点·refusal hops=0·双 CLEAN 窗）·与 r740 W135 席位 MSG-1933 W136+ 投影逐位收敛=跨窗交叉验证（r587 律·W135 §8 遗留指针的承诺兑现）", 1),
 ("R250：W135 带从未指派·测量面零结果可钓。扫描面=pre-W135 全一百三十二行注册 N1 带表（表尾=W134 行·leg0 机证 132 行）",
  "R250：W136 带从未指派·测量面零结果可钓。扫描面=pre-W136 全一百三十三行注册 N1 带表（表尾=W135 行·leg0 机证 133 行）", 1),
 ("`scripts/perpetual_faces_n1.py`（W2..W134 落地 runner 的 wave 参数化复用",
  "`scripts/perpetual_faces_n1.py`（W2..W135 落地 runner 的 wave 参数化复用", 1),
 ("- 批名=**PERPETUAL-N1-W135**。N=**2,200**", "- 批名=**PERPETUAL-N1-W136**。N=**2,200**", 1),
 ("起草窗实况：**W1..W134 N1 finalize 已全部落账**〔W133 finalize one-pass bm-a r739+W134 finalize one-pass 同窗 bm-a r740·§7 回填同 commit 在场〕——净账本链头 **690,811**（W134 finalize 落账·K=292,720 合并池·voids LOWAMP-P1/P2）",
  "起草窗实况：**W1..W135 N1 finalize 已全部落账**〔W134 finalize one-pass bm-a r740+W135 finalize one-pass 同窗 bm-a r741·§7 回填同 commit 在场〕——净账本链头 **693,011**（W135 finalize 落账·K=294,920 合并池·voids LOWAMP-P1/P2）", 1),
 ("累计 null 池投影=292,720+2,200（本波）=**294,920 投影**", "累计 null 池投影=294,920+2,200（本波）=**297,120 投影**", 1),
 ("本机 r739 席位 MSG-1857 尾「W135+ 投影 A CLEAN/B CLEAN 双 CLEAN」=表尾后新首个自由号自领",
  "本机 r740 席位 MSG-1933 尾「W136+ 投影 A CLEAN/B CLEAN 双 CLEAN」=表尾后新首个自由号自领", 1),
 ("T-2026-10-01-141 s1 引擎线第 125 波·bm-a 第五十一枚自有波〔机面 derive：engine_owner==bm-a 行 50+本候选·以 gate leg0 机证为准·含 W132/W133/W134 最近自有波〕。（波号=注册表 W134 行后首个自由号·单态零席位空档〔席位公示=MSG-2026-10-05-1933-bma-w135-seat 先推 origin 98712a0e3 r565 律〕；lane-free；部门 dept:研究）",
  "T-2026-10-01-141 s1 引擎线第 126 波·bm-a 第五十二枚自有波〔机面 derive：engine_owner==bm-a 行 51+本候选·以 gate leg0 机证为准·含 W133/W134/W135 最近自有波〕。（波号=注册表 W135 行后首个自由号·单态零席位空档〔席位公示=MSG-2026-10-05-1952-bma-w136-seat 先推 origin 20d0036dc r565 律〕；lane-free；部门 dept:研究）", 1),
 ("冻结编辑落工作树后下一 tick 新进程读活树自见 W135 行并点火", "冻结编辑落工作树后下一 tick 新进程读活树自见 W136 行并点火", 1),
 ("python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W135_PREREG.md",
  "python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W136_PREREG.md", 1),
 ("本波对既有 core48 零假设基线（p2_calibration v1/v2 canon；W1 ext；W2..W134 落地）",
  "本波对既有 core48 零假设基线（p2_calibration v1/v2 canon；W1 ext；W2..W135 落地）", 1),
 ("禁向词面不在本件复述（机器闸为准·防证伪模式词面自害，W2..W134 同法先例）",
  "禁向词面不在本件复述（机器闸为准·防证伪模式词面自害，W2..W135 同法先例）", 1),
 ("entry rng seed=**313_004+j**（法典 §4 W135 行 A=313_004..315_003·**算术续带**==W134 行 A 尾 313_003+1 起",
  "entry rng seed=**315_004+j**（法典 §4 W136 行 A=315_004..317_003·**算术续带**==W135 行 A 尾 315_003+1 起", 1),
 ("entry rng=**313_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**69_502+j**（法典 §4 W135 行 B=69_502..69_701·**算术续带**==W134 行 B 尾 69_501+1 起·步长 200·CLEAN 零拒绝点·hops=0·双 CLEAN 窗·与 r739 席位 MSG-1857 投影逐位收敛·ADMIT 回执在场）",
  "entry rng=**315_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**69_702+j**（法典 §4 W136 行 B=69_702..69_901·**算术续带**==W135 行 B 尾 69_701+1 起·步长 200·CLEAN 零拒绝点·hops=0·双 CLEAN 窗·与 r740 席位 MSG-1933 投影逐位收敛·ADMIT 回执在场）", 1),
 ("探针=不另烧（W2 探针 95_002/95_003 已证设计端到端；本波设计=W2..W134 逐字复用",
  "探针=不另烧（W2 探针 95_002/95_003 已证设计端到端；本波设计=W2..W135 逐字复用", 1),
 ("W135 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W134 在用带（**全注册·单态**）",
  "W136 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W135 在用带（**全注册·单态**）", 1),
 ("本波机验 ADMIT 回执在场=r740 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest W135 face（A 算术窗净腿+B 算术续带净腿〔双 CLEAN 窗·零拒绝点〕+W134 行 parity 腿）",
  "本波机验 ADMIT 回执在场=r741 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest W136 face（A 算术窗净腿+B 算术续带净腿〔双 CLEAN 窗·零拒绝点〕+W135 行 parity 腿）", 1),
 ("合并池 `canon 120 + 已落账波值（起草窗实测 W1..W134 已落账 292,720 实测·derive 禁手抄）+本波 2,200`",
  "合并池 `canon 120 + 已落账波值（起草窗实测 W1..W135 已落账 294,920 实测·derive 禁手抄）+本波 2,200`", 1),
 ('science_gates.append_ledger(batch_name="PERPETUAL-N1-W135", batch_trials=2200, file_name="results/perpetual_faces/n1_w135_results.json"',
  'science_gates.append_ledger(batch_name="PERPETUAL-N1-W136", batch_trials=2200, file_name="results/perpetual_faces/n1_w136_results.json"', 1),
 ("（起草窗实况注记：**W1..W134 N1 finalize 已全部落账**——净账本链头 690,811=W134 finalize 落账〔one-pass·bm-a r740·§7 回填同 commit 在场〕·**K=292,720 合并池**·**零在飞上游席位**（链前置净空波）。本波 §5 预测键=**W134 finalize 实测值**〔results/perpetual_faces/n1_w134_results.json·N1 面最新已落账键〕。",
  "（起草窗实况注记：**W1..W135 N1 finalize 已全部落账**——净账本链头 693,011=W135 finalize 落账〔one-pass·bm-a r741·§7 回填同 commit 在场〕·**K=294,920 合并池**·**零在飞上游席位**（链前置净空波）。本波 §5 预测键=**W135 finalize 实测值**〔results/perpetual_faces/n1_w135_results.json·N1 面最新已落账键〕。", 1),
 ("1. W135-only mu 与累计池 merged mu（W134 实测键 **−0.092883**·K=292,720 合并池·W134-only 实测 **−0.094033**）差异 **|Δ|<0.02**（W2..W134 共三十+面实测 mu 稳定先例·单波跨键律）。",
  "1. W136-only mu 与累计池 merged mu（W135 实测键 **−0.092854**·K=294,920 合并池·W135-only 实测 **−0.088966**）差异 **|Δ|<0.02**（W2..W135 共三十+面实测 mu 稳定先例·单波跨键律）。", 1),
 ("2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.244989**=W134 合并池实测）。",
  "2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.244971**=W135 合并池实测）。", 1),
 ("3. A 档 full_sharpe_p95 与 W134 A 档 p95（**0.3117** 实测锚）差 **<0.05**（门标准注记法 W5..W134 先例：",
  "3. A 档 full_sharpe_p95 与 W135 A 档 p95（**0.3192** 实测锚）差 **<0.05**（门标准注记法 W5..W135 先例：", 1),
 ("4. K-lift 线移动幅度 **≥−0.02**（累计池加深零 se_mu·线自 mu/sigma 微调面非质变——W3..W134 先例·W129 +0.0002/W130 +0.0001/W131 +0.0003/W132 −0.0001/W133 −0.0001/W134 **+0.0001** 正负交替如实报正负）；键 W134 实测 K-lift **+0.0001**（line_merged@K292,720 **1.1774**·line_pre 1.1773·n_eff 688,611；se_mu 收窄链 W131 0.000458→W132 0.000456→W133 0.000454→W134 **0.000453**）。",
  "4. K-lift 线移动幅度 **≥−0.02**（累计池加深零 se_mu·线自 mu/sigma 微调面非质变——W3..W135 先例·W130 +0.0001/W131 +0.0003/W132 −0.0001/W133 −0.0001/W134 +0.0001/W135 **+0.0000** 正负交替如实报正负）；键 W135 实测 K-lift **+0.0000**（line_merged@K294,920 **1.1775**·line_pre 1.1775·n_eff 690,811；se_mu 收窄链 W132 0.000456→W133 0.000454→W134 0.000453→W135 **0.000451**）。", 1),
 ("5. **W136+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 315_004..317_003 **CLEAN**（hops=0）；B first-clean **69_702..69_901** **CLEAN**（hops=0·双 CLEAN 窗）（r740 冻结窗 gate 回执尾行·与本席位 MSG W136+ 投影披露交叉验证一致=自机 derive 非转抄 r587 律）。",
  "5. **W137+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 317_004..319_003 **CLEAN**（hops=0）；B first-clean **94_001..94_200** **CLEAN**（hops=12·诚实前向扫过 N3-R1 used band 与多 SEED_REGISTRY 点后首净窗）（r741 冻结窗 gate 回执尾行·与本席位 MSG W137+ 投影披露交叉验证一致=自机 derive 非转抄 r587 律）。", 1),
 ("run --shard k --of 12 --wave 135/finalize --wave 135", "run --shard k --of 12 --wave 136/finalize --wave 136", 1),
 ("点火验证=2 tick 内产物增长面**（n1_w135/ 分片计数增长·唯一点火证据·r325 律）",
  "点火验证=2 tick 内产物增长面**（n1_w136/ 分片计数增长·唯一点火证据·r325 律）", 1),
 ("`results/p2cal_ext/n1_w135/shard-<k>-of-12.json`", "`results/p2cal_ext/n1_w136/shard-<k>-of-12.json`", 1),
 ("`results/perpetual_faces/n1_w135_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 链序前置=**起草窗零在飞上游（W1..W134 全落账）**",
  "`results/perpetual_faces/n1_w136_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 链序前置=**起草窗零在飞上游（W1..W135 全落账）**", 1),
 ("engine_owner==bm-a 50 行注册+本候选〔以 gate leg0 机证为准·含 W132/W133/W134 最近自有波〕",
  "engine_owner==bm-a 51 行注册+本候选〔以 gate leg0 机证为准·含 W133/W134/W135 最近自有波〕", 1),
]

for old, new, expect in pairs:
    n = t.count(old)
    assert n == expect, "needle count mismatch (%d != %d): %r" % (n, expect, old[:60])
    t = t.replace(old, new)

leftover_w135 = [ln for ln in t.splitlines()
                 if "W135" in ln and "W135 行" not in ln and "W135 finalize" not in ln
                 and "W135 A" not in ln and "W135 B" not in ln and "W135 席位" not in ln
                 and "W135=" not in ln and "n1_w135_results" not in ln
                 and "W135 已落账" not in ln and "W135 实测" not in ln and "W135-only" not in ln
                 and "W2..W135" not in ln and "W3..W135" not in ln and "W5..W135" not in ln
                 and "W133/W134/W135" not in ln and "W136+" not in ln and "W137+" not in ln
                 and "W135 §8" not in ln]
print("leftover W135 lines (expect only legit prior-state refs shown for review):")
for ln in leftover_w135:
    print("  ", ln.strip()[:120])
io.open(DST, "w", encoding="utf-8", newline="\n").write(t)
print("WRITTEN:", DST, len(t), "bytes")
