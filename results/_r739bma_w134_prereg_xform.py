# -*- coding: utf-8 -*-
"""r739 bm-a: transform research/PERPETUAL_N1_W133_PREREG.md (post-finalize
state, sec7/8 filled) -> research/PERPETUAL_N1_W134_PREREG.md (fresh freeze
state, sec7/8 placeholders). Needle-count law (r735): every needle asserted."""
import io

SRC = "research/PERPETUAL_N1_W133_PREREG.md"
DST = "research/PERPETUAL_N1_W134_PREREG.md"
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
 ("PERPETUAL-N1-W133 预注册 · N1 nulls-deepening 泵第 131（never-dry 常供给例常设步·第一百二十三枚引擎波·机面 derive：engine_owner 行 122+本候选·bm-a 第四十九枚自有波〔r738〕）",
  "PERPETUAL-N1-W134 预注册 · N1 nulls-deepening 泵第 132（never-dry 常供给例常设步·第一百二十四枚引擎波·机面 derive：engine_owner 行 123+本候选·bm-a 第五十枚自有波〔r739〕）", 1),
 ("波号 133=注册表 W132 行后首个自由号", "波号 134=注册表 W133 行后首个自由号", 1),
 ("本冻结窗 fetch 实核表尾时 W133 号位净空", "本冻结窗 fetch 实核表尾时 W134 号位净空", 1),
 ("全 inbox/processed/ W133 席位零外机命中（本机席位公示=MSG-2026-10-05-1824-bma-w133-seat 已推 origin 2d717cc03 先于本冻结 r565 律",
  "全 inbox/processed/ W134 席位零外机命中（本机席位公示=MSG-2026-10-05-1857-bma-w134-seat 已推 origin 5f3d9fcfc 先于本冻结 r565 律", 1),
 ("+W132=bm-a r737 freeze（37c3925ad·表尾）**均已注册**（表尾=W132 行）·W133=无 skip-past-published 链面",
  "+W133=bm-a r738 freeze（a869ad2ee·表尾）**均已注册**（表尾=W133 行）·W134=无 skip-past-published 链面", 1),
 ("ADMIT 回执 results/_r738bma_w133_band_gate.py rc0 实跑）",
  "ADMIT 回执 results/_r739bma_w134_band_gate.py rc0 实跑）", 1),
 ("pre-seat 机证=results/_r738bma_w133_probe.py rc0（ADMIT-derive·回执 results/_r738bma_w133_probe_receipt.txt）",
  "pre-seat 机证=results/_r739bma_w134_probe.py rc0（ADMIT-derive·回执 results/_r739bma_w134_probe_receipt.txt）", 1),
 ("冻结窗 gate 重跑 derive 逐位恒等（A 309_004..311_003 hops 0·B 69_102..69_301 hops 0",
  "冻结窗 gate 重跑 derive 逐位恒等（A 311_004..313_003 hops 0·B 69_302..69_501 hops 0", 1),
 ("**席位推送窗实录**（r738 窗口实况）：席位+probe+回执三件单 commit 推送=**首推撞拒 origin 前进 8 commit（r524 落后信号·bm-c r563 同窗波）→merge-mode 零 UU 收口→DELIVERED 2d717cc03（送达 commit 1ea4ff938）**",
  "**席位推送窗实录**（r739 窗口实况）：席位+probe+回执三件单 commit 推送=**首推撞拒 origin 前进 4 commit（r524 落后信号·bm-c r565 同窗波）→merge-mode 零 UU 收口→DELIVERED 5f3d9fcfc（送达 commit ad07612e7）**", 1),
 ("本波 ordinal=**第一百二十三枚引擎波（机面计数：注册表 engine_owner 行 122+本候选）**·**bm-a 第四十九枚自有波**〔机面 derive：engine_owner==bm-a 行 48+本候选",
  "本波 ordinal=**第一百二十四枚引擎波（机面计数：注册表 engine_owner 行 123+本候选）**·**bm-a 第五十枚自有波**〔机面 derive：engine_owner==bm-a 行 49+本候选", 1),
 ("带位（r535 机闸 derive 律·ADMIT 回执=results/_r738bma_w133_band_gate.py 单态门全腿实跑·pre-seat probe results/_r738bma_w133_probe.py 先跑·双窗 derive 恒等）",
  "带位（r535 机闸 derive 律·ADMIT 回执=results/_r739bma_w134_band_gate.py 单态门全腿实跑·pre-seat probe results/_r739bma_w134_probe.py 先跑·双窗 derive 恒等）", 1),
 ("本波 **A-ext seed=309_004..311_003**（**A 面算术续带**==W132 行 A 尾 309_003+1 起·步长 2_000·CLEAN 零拒绝点·refusal hops=0）；**B-ext exit seed=69_102..69_301**（**B 面算术续带**==W132 行 B 尾 69_101+1 起·步长 200·CLEAN 零拒绝点·refusal hops=0·双 CLEAN 窗）·与 r737 W132 席位 MSG-1755 W133+ 投影逐位收敛=跨窗交叉验证（r587 律·W132 §8 遗留指针的承诺兑现）",
  "本波 **A-ext seed=311_004..313_003**（**A 面算术续带**==W133 行 A 尾 311_003+1 起·步长 2_000·CLEAN 零拒绝点·refusal hops=0）；**B-ext exit seed=69_302..69_501**（**B 面算术续带**==W133 行 B 尾 69_301+1 起·步长 200·CLEAN 零拒绝点·refusal hops=0·双 CLEAN 窗）·与 r738 W133 席位 MSG-1824 W134+ 投影逐位收敛=跨窗交叉验证（r587 律·W133 §8 遗留指针的承诺兑现）", 1),
 ("R250：W133 带从未指派·测量面零结果可钓。扫描面=pre-W133 全一百三十行注册 N1 带表（表尾=W132 行·leg0 机证 130 行）",
  "R250：W134 带从未指派·测量面零结果可钓。扫描面=pre-W134 全一百三十一行注册 N1 带表（表尾=W133 行·leg0 机证 131 行）", 1),
 ("`scripts/perpetual_faces_n1.py`（W2..W132 落地 runner 的 wave 参数化复用",
  "`scripts/perpetual_faces_n1.py`（W2..W133 落地 runner 的 wave 参数化复用", 1),
 ("- 批名=**PERPETUAL-N1-W133**。N=**2,200**", "- 批名=**PERPETUAL-N1-W134**。N=**2,200**", 1),
 ("起草窗实况：**W1..W132 N1 finalize 已全部落账**〔W131 finalize one-pass bm-a r737+W132 finalize one-pass 同窗 bm-a r738·§7 回填同 commit 在场〕——净账本链头 **686,411**（W132 finalize 落账·K=288,320 合并池·voids LOWAMP-P1/P2）",
  "起草窗实况：**W1..W133 N1 finalize 已全部落账**〔W132 finalize one-pass bm-a r738+W133 finalize one-pass 同窗 bm-a r739·§7 回填同 commit 在场〕——净账本链头 **688,611**（W133 finalize 落账·K=290,520 合并池·voids LOWAMP-P1/P2）", 1),
 ("累计 null 池投影=288,320+2,200（本波）=**290,520 投影**", "累计 null 池投影=290,520+2,200（本波）=**292,720 投影**", 1),
 ("本机 r737 席位 MSG-1755 尾「W133+ 投影 A CLEAN/B CLEAN 双 CLEAN」=表尾后新首个自由号自领",
  "本机 r738 席位 MSG-1824 尾「W134+ 投影 A CLEAN/B CLEAN 双 CLEAN」=表尾后新首个自由号自领", 1),
 ("T-2026-10-01-141 s1 引擎线第 123 波·bm-a 第四十九枚自有波〔机面 derive：engine_owner==bm-a 行 48+本候选·以 gate leg0 机证为准·含 W130/W131/W132 最近自有波〕。（波号=注册表 W132 行后首个自由号·单态零席位空档〔席位公示=MSG-2026-10-05-1824-bma-w133-seat 先推 origin 2d717cc03 r565 律〕；lane-free；部门 dept:研究）",
  "T-2026-10-01-141 s1 引擎线第 124 波·bm-a 第五十枚自有波〔机面 derive：engine_owner==bm-a 行 49+本候选·以 gate leg0 机证为准·含 W131/W132/W133 最近自有波〕。（波号=注册表 W133 行后首个自由号·单态零席位空档〔席位公示=MSG-2026-10-05-1857-bma-w134-seat 先推 origin 5f3d9fcfc r565 律〕；lane-free；部门 dept:研究）", 1),
 ("冻结编辑落工作树后下一 tick 新进程读活树自见 W133 行并点火", "冻结编辑落工作树后下一 tick 新进程读活树自见 W134 行并点火", 1),
 ("python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W133_PREREG.md",
  "python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W134_PREREG.md", 1),
 ("本波对既有 core48 零假设基线（p2_calibration v1/v2 canon；W1 ext；W2..W132 落地）",
  "本波对既有 core48 零假设基线（p2_calibration v1/v2 canon；W1 ext；W2..W133 落地）", 1),
 ("禁向词面不在本件复述（机器闸为准·防证伪模式词面自害，W2..W132 同法先例）",
  "禁向词面不在本件复述（机器闸为准·防证伪模式词面自害，W2..W133 同法先例）", 1),
 ("entry rng seed=**309_004+j**（法典 §4 W133 行 A=309_004..311_003·**算术续带**==W132 行 A 尾 309_003+1 起",
  "entry rng seed=**311_004+j**（法典 §4 W134 行 A=311_004..313_003·**算术续带**==W133 行 A 尾 311_003+1 起", 1),
 ("entry rng=**309_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**69_102+j**（法典 §4 W133 行 B=69_102..69_301·**算术续带**==W132 行 B 尾 69_101+1 起·步长 200·CLEAN 零拒绝点·hops=0·双 CLEAN 窗·与 r737 席位 MSG-1755 投影逐位收敛·ADMIT 回执在场）",
  "entry rng=**311_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**69_302+j**（法典 §4 W134 行 B=69_302..69_501·**算术续带**==W133 行 B 尾 69_301+1 起·步长 200·CLEAN 零拒绝点·hops=0·双 CLEAN 窗·与 r738 席位 MSG-1824 投影逐位收敛·ADMIT 回执在场）", 1),
 ("探针=不另烧（W2 探针 95_002/95_003 已证设计端到端；本波设计=W2..W132 逐字复用",
  "探针=不另烧（W2 探针 95_002/95_003 已证设计端到端；本波设计=W2..W133 逐字复用", 1),
 ("W133 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W132 在用带（**全注册·单态**）",
  "W134 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W133 在用带（**全注册·单态**）", 1),
 ("本波机验 ADMIT 回执在场=r738 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest W133 face（A 算术窗净腿+B 算术续带净腿〔双 CLEAN 窗·零拒绝点〕+W132 行 parity 腿）",
  "本波机验 ADMIT 回执在场=r739 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest W134 face（A 算术窗净腿+B 算术续带净腿〔双 CLEAN 窗·零拒绝点〕+W133 行 parity 腿）", 1),
 ("合并池 `canon 120 + 已落账波值（起草窗实测 W1..W132 已落账 288,320 实测·derive 禁手抄）+本波 2,200`",
  "合并池 `canon 120 + 已落账波值（起草窗实测 W1..W133 已落账 290,520 实测·derive 禁手抄）+本波 2,200`", 1),
 ('science_gates.append_ledger(batch_name="PERPETUAL-N1-W133", batch_trials=2200, file_name="results/perpetual_faces/n1_w133_results.json"',
  'science_gates.append_ledger(batch_name="PERPETUAL-N1-W134", batch_trials=2200, file_name="results/perpetual_faces/n1_w134_results.json"', 1),
 ("（起草窗实况注记：**W1..W132 N1 finalize 已全部落账**——净账本链头 686,411=W132 finalize 落账〔one-pass·bm-a r738·§7 回填同 commit 在场〕·**K=288,320 合并池**·**零在飞上游席位**（链前置净空波）。本波 §5 预测键=**W132 finalize 实测值**〔results/perpetual_faces/n1_w132_results.json·N1 面最新已落账键〕。",
  "（起草窗实况注记：**W1..W133 N1 finalize 已全部落账**——净账本链头 688,611=W133 finalize 落账〔one-pass·bm-a r739·§7 回填同 commit 在场〕·**K=290,520 合并池**·**零在飞上游席位**（链前置净空波）。本波 §5 预测键=**W133 finalize 实测值**〔results/perpetual_faces/n1_w133_results.json·N1 面最新已落账键〕。", 1),
 ("1. W133-only mu 与累计池 merged mu（W132 实测键 **−0.092857**·K=288,320 合并池·W132-only 实测 **−0.097454**）差异 **|Δ|<0.02**（W2..W132 共三十+面实测 mu 稳定先例·单波跨键律）。",
  "1. W134-only mu 与累计池 merged mu（W133 实测键 **−0.092875**·K=290,520 合并池·W133-only 实测 **−0.095254**）差异 **|Δ|<0.02**（W2..W133 共三十+面实测 mu 稳定先例·单波跨键律）。", 1),
 ("2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.244978**=W132 合并池实测）。",
  "2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.244961**=W133 合并池实测）。", 1),
 ("3. A 档 full_sharpe_p95 与 W132 A 档 p95（**0.2914** 实测锚）差 **<0.05**（门标准注记法 W5..W132 先例：结果知情报校准面·仅作机器断言伪测用·测量面非注册利益）。",
  "3. A 档 full_sharpe_p95 与 W133 A 档 p95（**0.3156** 实测锚）差 **<0.05**（门标准注记法 W5..W133 先例：结果知情报校准面·仅作机器断言伪测用·测量面非注册利益）。", 1),
 ("4. K-lift 线移动幅度 **≥−0.02**（累计池加深零 se_mu·线自 mu/sigma 微调面非质变——W3..W132 先例·W127 +0.0003/W128 +0.0003/W129 +0.0002/W130 +0.0001/W131 +0.0003/W132 **−0.0001** 正负交替如实报正负）；键 W132 实测 K-lift **−0.0001**（line_merged@K288,320 **1.1771**·line_pre 1.1772·n_eff 684,211；se_mu 收窄链 W129 0.000461→W130 0.000460→W131 0.000458→W132 **0.000456**）。",
  "4. K-lift 线移动幅度 **≥−0.02**（累计池加深零 se_mu·线自 mu/sigma 微调面非质变——W3..W133 先例·W128 +0.0003/W129 +0.0002/W130 +0.0001/W131 +0.0003/W132 −0.0001/W133 **−0.0001** 正负交替如实报正负）；键 W133 实测 K-lift **−0.0001**（line_merged@K290,520 **1.1771**·line_pre 1.1772·n_eff 686,411；se_mu 收窄链 W130 0.000460→W131 0.000458→W132 0.000456→W133 **0.000454**）。", 1),
 ("5. **W134+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 311_004..313_003 **CLEAN**（hops=0）；B first-clean **69_302..69_501** **CLEAN**（hops=0·双 CLEAN 窗）（r738 冻结窗 gate 回执尾行·与本席位 MSG W134+ 投影披露交叉验证一致=自机 derive 非转抄 r587 律）。",
  "5. **W135+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 313_004..315_003 **CLEAN**（hops=0）；B first-clean **69_502..69_701** **CLEAN**（hops=0·双 CLEAN 窗）（r739 冻结窗 gate 回执尾行·与本席位 MSG W135+ 投影披露交叉验证一致=自机 derive 非转抄 r587 律）。", 1),
 ("run --shard k --of 12 --wave 133/finalize --wave 133", "run --shard k --of 12 --wave 134/finalize --wave 134", 1),
 ("点火验证=2 tick 内产物增长面**（n1_w133/ 分片计数增长·唯一点火证据·r325 律）",
  "点火验证=2 tick 内产物增长面**（n1_w134/ 分片计数增长·唯一点火证据·r325 律）", 1),
 ("`results/p2cal_ext/n1_w133/shard-<k>-of-12.json`", "`results/p2cal_ext/n1_w134/shard-<k>-of-12.json`", 1),
 ("`results/perpetual_faces/n1_w133_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 链序前置=**起草窗零在飞上游（W1..W132 全落账）**",
  "`results/perpetual_faces/n1_w134_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 链序前置=**起草窗零在飞上游（W1..W133 全落账）**", 1),
 ("engine_owner==bm-a 48 行注册+本候选〔以 gate leg0 机证为准·含 W130/W131/W132 最近自有波〕",
  "engine_owner==bm-a 49 行注册+本候选〔以 gate leg0 机证为准·含 W131/W132/W133 最近自有波〕", 1),
]

for old, new, expect in pairs:
    n = t.count(old)
    assert n == expect, "needle count mismatch (%d != %d): %r" % (n, expect, old[:60])
    t = t.replace(old, new)

leftover_w133 = [ln for ln in t.splitlines()
                 if "W133" in ln and "W133 行" not in ln and "W133 finalize" not in ln
                 and "W133 A" not in ln and "W133 B" not in ln and "W133 席位" not in ln
                 and "W133=" not in ln and "n1_w133_results" not in ln
                 and "W133 已落账" not in ln and "W133 实测" not in ln and "W133-only" not in ln
                 and "W2..W133" not in ln and "W3..W133" not in ln and "W5..W133" not in ln
                 and "W131/W132/W133" not in ln and "W134+ 投影" not in ln]
print("leftover W133 lines (expect only legit prior-state refs shown for review):")
for ln in leftover_w133:
    print("  ", ln.strip()[:120])
io.open(DST, "w", encoding="utf-8", newline="\n").write(t)
print("WRITTEN:", DST, len(t), "bytes")
