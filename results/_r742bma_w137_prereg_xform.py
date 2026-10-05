# -*- coding: utf-8 -*-
"""r742 bm-a: (1) backfill PERPETUAL_N1_W136_PREREG.md sec7/8 from the W136
finalize one-pass (mechanical, same-commit law); (2) transform the post-
finalize W136 prereg -> research/PERPETUAL_N1_W137_PREREG.md (fresh freeze
state, sec7/8 placeholders). Needle-count law (r735): every needle asserted.
Bloodline: r741 _r741bma_w136_prereg_xform.py + W137 facts (B = honest
12-hop forward walk, NOT arithmetic)."""
import io

# ============ 1. W136 prereg sec7/8 backfill (mechanical, from finalize) ============
P136 = "research/PERPETUAL_N1_W136_PREREG.md"
t = io.open(P136, encoding="utf-8", newline="").read()

i7 = t.find("## §7 跑后实证。【占位·finalize 收口机械回填】")
i8 = t.find("## §8 批后复盘。【占位·跑前为空·终 7-T】")
i_freeze = t.find("- **跑前冻结=本件 commit**")
assert i7 > 0 and i8 > i7 and i_freeze > i8, "W136 sec7/8 placeholder anchors"

sec7 = """## §7 跑后实证。【finalize 收口机械回填·bm-a r742 2026-10-05 20:2x】
- finalize one-pass rc=0；12/12 分片 2,200/2,200 位取（A=2,000/B=200 算术检·分片名去重门 dup-free）；上游链 derive 复核 PASS（W1..W135 落账已在位·W135 total 693,011 为 prev 键头〔零在飞上游=键序前置净空·键序合法〕）；r708 预检三腿在场（回执 results/_r742bma_w136_preflight.json）：文件完备 12/12+finalize 输出缺位 + 活进程探针 v2 零命中（python.exe N1 runner 全扫·本窗全程串行执行 r738 律）+ 席位 MSG-2026-10-05-1952-bma-w136-seat 在 git 史（published=reserved r565 律·r741 冻结链预推）=GREEN_FINALIZE_READY 先行。
- w136_only mu **−0.085702** sigma 0.243464（K=2,200）；pre-W136 池 mu −0.092854 sigma 0.244971（K=294,920）；merged mu **−0.092801** sigma **0.244960**（K=**297,120**=294,920+2,200 算术检·与 §0 投影恒等）。
- skill_line_v2 @n_eff 持平键位 693,011：1.1776 → **1.1776**（K-lift **+0.0000**·正负交替如实报零号·机器键 line_delta_k_lift=0.0）；se_mu 收窄链 W133 0.000454 → W134 0.000453 → W135 0.000451 → **0.000449**（@K297,120）。
- A 档 full_sharpe_p95 **0.3245** / p99 0.4495（A mu −0.080890）；账本 append 单发：prev 693,011 + 2,200 = **695,211**（单记·voids LOWAMP-P1/P2）。
- §5 断言对账：①|w136_only−merged|=0.007100<0.02 **PASS**（机器键 mu_delta 面）；②sigma 相对变化 −0.0045%<±10% **PASS**；③A p95 vs W135 键 0.3192 差 +0.0053<0.05 **PASS**；④K-lift +0.0000≥−0.02 **PASS**——四断言全 PASS。
- audit.machine=bm-a·finalize_only=true；evidence_cutoff=2026-09-22 顶层+ cutoff_meta 双写在场。

"""
sec8 = """## §8 批后复盘。【占位·跑前为空·终 7-T】→ 回填 2026-10-05 r742
- 零异常零补获：freeze r741（W136 FREEZE 链 2564ba798 送达·席位 MSG-2026-10-05-1952 r565 律先推 20d0036dc·引擎 tick 19:59 自燃实证 shard-0 落地·r325 产物增长面）→分片连续烧全落地（12/12 齐位于 r742 轮首·shard-9..11 由 r742 轮首 churn-absorb 收编实证）→finalize 本窗 r742 one-pass（20:2x·同轮生命周期：r741 冻结+点火→r742 收口·单会话连续窗）。
- 方法论捕获：无新方法论（测量加深面零新发现宣称）；宝藏捕获：无。
- 遗留：W137=表尾后下个自由号——**A 317_004..319_003 CLEAN / B first-clean 94_001..94_200（hops=12 诚实前向走·非轮转 r587）**（见本件 §5.5 投影·r741 gate 回执尾行·下波冻结窗必复核非镜像 r587 律）。

"""
t = t[:i7] + sec7 + sec8 + t[i_freeze:]
io.open(P136, "w", encoding="utf-8", newline="\n").write(t)
print("W136 sec7/8 backfilled:", len(t), "bytes")

# ============ 2. transform W136 prereg (post-finalize) -> W137 prereg ============
SRC = "research/PERPETUAL_N1_W136_PREREG.md"
DST = "research/PERPETUAL_N1_W137_PREREG.md"
t = io.open(SRC, encoding="utf-8", newline="").read()

# --- 2a. sec7/8 filled block -> placeholders (slicing, not needles) ---
i7 = t.find("## §7 跑后实证。【finalize 收口机械回填")
i_freeze = t.find("- **跑前冻结=本件 commit**")
assert i7 > 0 and i_freeze > i7, "sec7/8 block anchors"
placeholder = (
"## §7 跑后实证。【占位·finalize 收口机械回填】\n\n"
"## §8 批后复盘。【占位·跑前为空·终 7-T】\n\n"
)
t = t[:i7] + placeholder + t[i_freeze:]

pairs = [
 ("PERPETUAL-N1-W136 预注册 · N1 nulls-deepening 泵第 134（never-dry 常供给例常设步·第一百二十六枚引擎波·机面 derive：engine_owner 行 125+本候选·bm-a 第五十二枚自有波〔r741〕）",
  "PERPETUAL-N1-W137 预注册 · N1 nulls-deepening 泵第 135（never-dry 常供给例常设步·第一百二十七枚引擎波·机面 derive：engine_owner 行 126+本候选·bm-a 第五十三枚自有波〔r742〕）", 1),
 ("波号 136=注册表 W135 行后首个自由号", "波号 137=注册表 W136 行后首个自由号", 1),
 ("本冻结窗 fetch 实核表尾时 W136 号位净空", "本冻结窗 fetch 实核表尾时 W137 号位净空", 1),
 ("全 inbox/processed/ W134 席位零外机命中（本机席位公示=MSG-2026-10-05-1952-bma-w136-seat 已推 origin 20d0036dc 先于本冻结 r565 律",
  "全 inbox/processed/ W135 席位零外机命中（本机席位公示=MSG-2026-10-05-202x-bma-w137-seat 已推 origin af1c3c267 先于本冻结 r565 律", 1),
 ("+W135=bm-a r740 freeze（bc921896a·表尾）**均已注册**（表尾=W135 行）·W136=无 skip-past-published 链面",
  "+W136=bm-a r741 freeze（7cafbc7ab·表尾）**均已注册**（表尾=W136 行）·W137=无 skip-past-published 链面", 1),
 ("ADMIT 回执 results/_r741bma_w136_band_gate.py rc0 实跑）",
  "ADMIT 回执 results/_r742bma_w137_band_gate.py rc0 实跑）", 1),
 ("pre-seat 机证=results/_r741bma_w136_probe.py rc0（ADMIT-derive·回执 results/_r741bma_w136_probe_receipt.txt）",
  "pre-seat 机证=results/_r742bma_w137_probe.py rc0（ADMIT-derive·回执 results/_r742bma_w137_probe_receipt.json·B 12-hop 链逐跳机证在内）", 1),
 ("冻结窗 gate 重跑 derive 逐位恒等（A 315_004..317_003 hops 0·B 69_702..69_901 hops 0——双 CLEAN 算术续带窗·零拒绝点·终窗 CLEAN）",
  "冻结窗 gate 重跑 derive 逐位恒等（A 317_004..319_003 hops 0·B 94_001..94_200 hops 12——A 算术续带窗零拒绝点·B 诚实前向走首净窗·非轮转 r587 前向单调断言在走内）", 1),
 ("**席位推送窗实录**（r741 窗口实况）：席位+probe+回执三件单 commit 推送=**首推撞拒 origin 前进 1 commit（r524 落后信号·bm-c r568 同窗波）→merge-mode 零 UU 收口→DELIVERED 20d0036dc（送达 commit 2564ba798）**。",
  "**席位推送窗实录**（r742 窗口实况）：席位+probe 回执+preflight 收据单 commit=**推送窗内 fetch 实核 origin 前进 2 commits（r524 落后信号·bm-c r570 同窗波）→先 merge-mode 零 UU 收口再单推→DELIVERED（seat commit af1c3c267·送达 merge d28d392ce·rev-list 0/0 双向自证）**。", 1),
 ("本波 ordinal=**第一百二十六枚引擎波（机面计数：注册表 engine_owner 行 125+本候选）**·**bm-a 第五十二枚自有波**〔机面 derive：engine_owner==bm-a 行 51+本候选·gate leg0 机证在场·r359 律计数面以 gate 机输出为准〕。",
  "本波 ordinal=**第一百二十七枚引擎波（机面计数：注册表 engine_owner 行 126+本候选）**·**bm-a 第五十三枚自有波**〔机面 derive：engine_owner==bm-a 行 52+本候选·gate leg0 机证在场·r359 律计数面以 gate 机输出为准〕。", 1),
 ("带位（r535 机闸 derive 律·ADMIT 回执=results/_r741bma_w136_band_gate.py 单态门全腿实跑·pre-seat probe results/_r741bma_w136_probe.py 先跑·双窗 derive 恒等）",
  "带位（r535 机闸 derive 律·ADMIT 回执=results/_r742bma_w137_band_gate.py 单态门全腿实跑·pre-seat probe results/_r742bma_w137_probe.py 先跑·双窗 derive 恒等）", 1),
 ("本波 **A-ext seed=315_004..317_003**（**A 面算术续带**==W135 行 A 尾 315_003+1 起·步长 2_000·CLEAN 零拒绝点·refusal hops=0）；**B-ext exit seed=69_702..69_901**（**B 面算术续带**==W135 行 B 尾 69_701+1 起·步长 200·CLEAN 零拒绝点·refusal hops=0·双 CLEAN 窗）·与 r740 W135 席位 MSG-1933 W136+ 投影逐位收敛=跨窗交叉验证（r587 律·W135 §8 遗留指针的承诺兑现）",
  "本波 **A-ext seed=317_004..319_003**（**A 面算术续带**==W136 行 A 尾 317_003+1 起·步长 2_000·CLEAN 零拒绝点·refusal hops=0）；**B-ext exit seed=94_001..94_200**（**B 面 first-clean 窗**==W136 行 B 尾 69_901+1 起首窗 69_902..70_101 被拒〔N3-R1 用种带+连续注册 2_000 宽带 70_001..94_000〕→**诚实前向走 12 hops**→94_001..94_200·非轮转 r587〔每跳严格越过拒绝带·前向单调断言在走内·逐跳链在 probe 回执〕）·与 r741 W136 席位 MSG-1952 W137+ 投影逐位收敛=跨窗交叉验证（r587 律·W136 §8 遗留指针的承诺兑现）", 1),
 ("R250：W136 带从未指派·测量面零结果可钓。扫描面=pre-W136 全一百三十三行注册 N1 带表（表尾=W135 行·leg0 机证 133 行）",
  "R250：W137 带从未指派·测量面零结果可钓。扫描面=pre-W137 全一百三十四行注册 N1 带表（表尾=W136 行·leg0 机证 134 行）", 1),
 ("`scripts/perpetual_faces_n1.py`（W2..W135 落地 runner 的 wave 参数化复用",
  "`scripts/perpetual_faces_n1.py`（W2..W136 落地 runner 的 wave 参数化复用", 1),
 ("- 批名=**PERPETUAL-N1-W136**。N=**2,200**", "- 批名=**PERPETUAL-N1-W137**。N=**2,200**", 1),
 ("起草窗实况：**W1..W135 N1 finalize 已全部落账**〔W134 finalize one-pass bm-a r740+W135 finalize one-pass 同窗 bm-a r741·§7 回填同 commit 在场〕——净账本链头 **693,011**（W135 finalize 落账·K=294,920 合并池·voids LOWAMP-P1/P2）",
  "起草窗实况：**W1..W136 N1 finalize 已全部落账**〔W135 finalize one-pass bm-a r741+W136 finalize one-pass 同窗 bm-a r742·§7 回填同 commit 在场〕——净账本链头 **695,211**（W136 finalize 落账·K=297,120 合并池·voids LOWAMP-P1/P2）", 1),
 ("累计 null 池投影=294,920+2,200（本波）=**297,120 投影**", "累计 null 池投影=297,120+2,200（本波）=**299,320 投影**", 1),
 ("本机 r740 席位 MSG-1933 尾「W136+ 投影 A CLEAN/B CLEAN 双 CLEAN」=表尾后新首个自由号自领",
  "本机 r741 席位 MSG-1952 尾「W137+ 投影 A CLEAN/B 94_001..94_200 hops=12」=表尾后新首个自由号自领", 1),
 ("T-2026-10-01-141 s1 引擎线第 126 波·bm-a 第五十二枚自有波〔机面 derive：engine_owner==bm-a 行 51+本候选·以 gate leg0 机证为准·含 W133/W134/W135 最近自有波〕。（波号=注册表 W135 行后首个自由号·单态零席位空档〔席位公示=MSG-2026-10-05-1952-bma-w136-seat 先推 origin 20d0036dc r565 律〕；lane-free；部门 dept:研究）",
  "T-2026-10-01-141 s1 引擎线第 127 波·bm-a 第五十三枚自有波〔机面 derive：engine_owner==bm-a 行 52+本候选·以 gate leg0 机证为准·含 W134/W135/W136 最近自有波〕。（波号=注册表 W136 行后首个自由号·单态零席位空档〔席位公示=MSG-2026-10-05-202x-bma-w137-seat 先推 origin af1c3c267 r565 律〕；lane-free；部门 dept:研究）", 1),
 ("冻结编辑落工作树后下一 tick 新进程读活树自见 W136 行并点火", "冻结编辑落工作树后下一 tick 新进程读活树自见 W137 行并点火", 1),
 ("python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W136_PREREG.md",
  "python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W137_PREREG.md", 1),
 ("本波对既有 core48 零假设基线（p2_calibration v1/v2 canon；W1 ext；W2..W135 落地）",
  "本波对既有 core48 零假设基线（p2_calibration v1/v2 canon；W1 ext；W2..W136 落地）", 1),
 ("禁向词面不在本件复述（机器闸为准·防证伪模式词面自害，W2..W135 同法先例）",
  "禁向词面不在本件复述（机器闸为准·防证伪模式词面自害，W2..W136 同法先例）", 1),
 ("entry rng seed=**315_004+j**（法典 §4 W136 行 A=315_004..317_003·**算术续带**==W135 行 A 尾 315_003+1 起",
  "entry rng seed=**317_004+j**（法典 §4 W137 行 A=317_004..319_003·**算术续带**==W136 行 A 尾 317_003+1 起", 1),
 ("exit rng=**69_702+j**（法典 §4 W136 行 B=69_702..69_901·**算术续带**==W135 行 B 尾 69_701+1 起·步长 200·CLEAN 零拒绝点·hops=0·双 CLEAN 窗·与 r740 席位 MSG-1933 投影逐位收敛·ADMIT 回执在场）",
  "exit rng=**94_001+j**（法典 §4 W137 行 B=94_001..94_200·**first-clean 窗**==W136 行 B 尾 69_901+1 起首窗被拒〔N3-R1 用种带+连续注册带 70_001..94_000〕→诚实前向走 12 hops·非轮转 r587·与 r741 席位 MSG-1952 投影逐位收敛·ADMIT 回执在场）", 1),
 ("探针=不另烧（W2 探针 95_002/95_003 已证设计端到端；本波设计=W2..W135 逐字复用",
  "探针=不另烧（W2 探针 95_002/95_003 已证设计端到端；本波设计=W2..W136 逐字复用", 1),
 ("W136 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W135 在用带（**全注册·单态**）",
  "W137 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W136 在用带（**全注册·单态**）", 1),
 ("本波机验 ADMIT 回执在场=r741 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest W136 face（A 算术窗净腿+B 算术续带净腿〔双 CLEAN 窗·零拒绝点〕+W135 行 parity 腿）",
  "本波机验 ADMIT 回执在场=r742 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest W137 face（A 算术窗净腿+B first-clean 窗净腿〔诚实前向走 12 hops·非轮转 r587〕+W136 行 parity 腿）", 1),
 ("合并池 `canon 120 + 已落账波值（起草窗实测 W1..W135 已落账 294,920 实测·derive 禁手抄）+本波 2,200`",
  "合并池 `canon 120 + 已落账波值（起草窗实测 W1..W136 已落账 297,120 实测·derive 禁手抄）+本波 2,200`", 1),
 ('science_gates.append_ledger(batch_name="PERPETUAL-N1-W136", batch_trials=2200, file_name="results/perpetual_faces/n1_w136_results.json"',
  'science_gates.append_ledger(batch_name="PERPETUAL-N1-W137", batch_trials=2200, file_name="results/perpetual_faces/n1_w137_results.json"', 1),
 ("（起草窗实况注记：**W1..W135 N1 finalize 已全部落账**——净账本链头 693,011=W135 finalize 落账〔one-pass·bm-a r741·§7 回填同 commit 在场〕·**K=294,920 合并池**·**零在飞上游席位**（链前置净空波）。本波 §5 预测键=**W135 finalize 实测值**〔results/perpetual_faces/n1_w135_results.json·N1 面最新已落账键〕。",
  "（起草窗实况注记：**W1..W136 N1 finalize 已全部落账**——净账本链头 695,211=W136 finalize 落账〔one-pass·bm-a r742·§7 回填同 commit 在场〕·**K=297,120 合并池**·**零在飞上游席位**（链前置净空波）。本波 §5 预测键=**W136 finalize 实测值**〔results/perpetual_faces/n1_w136_results.json·N1 面最新已落账键〕。", 1),
 ("1. W136-only mu 与累计池 merged mu（W135 实测键 **−0.092854**·K=294,920 合并池·W135-only 实测 **−0.088966**）差异 **|Δ|<0.02**（W2..W135 共三十+面实测 mu 稳定先例·单波跨键律）。",
  "1. W137-only mu 与累计池 merged mu（W136 实测键 **−0.092801**·K=297,120 合并池·W136-only 实测 **−0.085702**）差异 **|Δ|<0.02**（W2..W136 共三十+面实测 mu 稳定先例·单波跨键律）。", 1),
 ("2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.244971**=W135 合并池实测）。",
  "2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.244960**=W136 合并池实测）。", 1),
 ("3. A 档 full_sharpe_p95 与 W135 A 档 p95（**0.3192** 实测锚）差 **<0.05**（门标准注记法 W5..W135 先例：",
  "3. A 档 full_sharpe_p95 与 W136 A 档 p95（**0.3245** 实测锚）差 **<0.05**（门标准注记法 W5..W136 先例：", 1),
 ("4. K-lift 线移动幅度 **≥−0.02**（累计池加深零 se_mu·线自 mu/sigma 微调面非质变——W3..W135 先例·W130 +0.0001/W131 +0.0003/W132 −0.0001/W133 −0.0001/W134 +0.0001/W135 **+0.0000** 正负交替如实报正负）；键 W135 实测 K-lift **+0.0000**（line_merged@K294,920 **1.1775**·line_pre 1.1775·n_eff 690,811；se_mu 收窄链 W132 0.000456→W133 0.000454→W134 0.000453→W135 **0.000451**）。",
  "4. K-lift 线移动幅度 **≥−0.02**（累计池加深零 se_mu·线自 mu/sigma 微调面非质变——W3..W136 先例·W131 +0.0003/W132 −0.0001/W133 −0.0001/W134 +0.0001/W135 +0.0000/W136 **+0.0000** 正负交替如实报正负）；键 W136 实测 K-lift **+0.0000**（line_merged@K297,120 **1.1776**·line_pre 1.1776·n_eff 693,011；se_mu 收窄链 W133 0.000454→W134 0.000453→W135 0.000451→W136 **0.000449**）。", 1),
 ("5. **W137+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 317_004..319_003 **CLEAN**（hops=0）；B first-clean **94_001..94_200** **CLEAN**（hops=12·诚实前向扫过 N3-R1 used band 与多 SEED_REGISTRY 点后首净窗）（r741 冻结窗 gate 回执尾行·与本席位 MSG W137+ 投影披露交叉验证一致=自机 derive 非转抄 r587 律）。",
  "5. **W138+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 319_004..321_003 **CLEAN**（hops=0）；B first-clean **94_201..94_400** **CLEAN**（hops=0·双 CLEAN 窗）（r742 冻结窗 gate 回执尾行·与本席位 MSG W138+ 投影披露交叉验证一致=自机 derive 非转抄 r587 律）。", 1),
 ("run --shard k --of 12 --wave 136/finalize --wave 136", "run --shard k --of 12 --wave 137/finalize --wave 137", 1),
 ("点火验证=2 tick 内产物增长面**（n1_w136/ 分片计数增长·唯一点火证据·r325 律）",
  "点火验证=2 tick 内产物增长面**（n1_w137/ 分片计数增长·唯一点火证据·r325 律）", 1),
 ("`results/p2cal_ext/n1_w136/shard-<k>-of-12.json`", "`results/p2cal_ext/n1_w137/shard-<k>-of-12.json`", 1),
 ("`results/perpetual_faces/n1_w136_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 链序前置=**起草窗零在飞上游（W1..W135 全落账）**",
  "`results/perpetual_faces/n1_w137_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 链序前置=**起草窗零在飞上游（W1..W136 全落账）**", 1),
 ("engine_owner==bm-a 51 行注册+本候选〔以 gate leg0 机证为准·含 W133/W134/W135 最近自有波〕",
  "engine_owner==bm-a 52 行注册+本候选〔以 gate leg0 机证为准·含 W134/W135/W136 最近自有波〕", 1),
]

for old, new, expect in pairs:
    n = t.count(old)
    assert n == expect, "needle count mismatch (%d != %d): %r" % (n, expect, old[:60])
    t = t.replace(old, new)

io.open(DST, "w", encoding="utf-8", newline="\n").write(t)
print("WRITTEN:", DST, len(t), "bytes")
