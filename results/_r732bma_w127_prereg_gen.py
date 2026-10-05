# -*- coding: utf-8 -*-
"""r732 bm-a W127 prereg generator: transform research/PERPETUAL_N1_W126_PREREG.md
(its §7/§8 backfilled state) into research/PERPETUAL_N1_W127_PREREG.md with §7/§8
placeholders restored. Needle-asserted replacements."""
import io, re

src = io.open(r"research\PERPETUAL_N1_W126_PREREG.md", encoding="utf-8").read()

pairs = [
 ("# PERPETUAL-N1-W126 预注册 · N1 nulls-deepening 泵第 124（never-dry 常供给例常设步·第一百一十六枚引擎波·机面 derive：engine_owner 行 115+本候选·bm-a 第四十二枚自有波〔r731〕）",
  "# PERPETUAL-N1-W127 预注册 · N1 nulls-deepening 泵第 125（never-dry 常供给例常设步·第一百一十七枚引擎波·机面 derive：engine_owner 行 116+本候选·bm-a 第四十三枚自有波〔r732〕）"),
 ("**波号 126=注册表 W125 行后首个自由号**〔本冻结窗 fetch 实核表尾时 W126 号位净空",
  "**波号 127=注册表 W126 行后首个自由号**〔本冻结窗 fetch 实核表尾时 W127 号位净空"),
 ("全 inbox/processed/ W126 席位零外机命中（本机席位公示=MSG-2026-10-05-1528-bma-w126-seat 已推 origin 7d70b01fd 先于本冻结 r565 律〕",
  "全 inbox/processed/ W127 席位零外机命中（本机席位公示=MSG-2026-10-05-1548-bma-w127-seat 已推 origin bef555332 先于本冻结 r565 律〕"),
 ("+W125=bm-a r730 freeze（77cd1f6ee·表尾）**均已注册**（表尾=W125 行）·W126=无 skip-past-published 链面（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r731bma_w126_band_gate.py rc0 实跑）",
  "+W125=bm-a r730 freeze（77cd1f6ee）+W126=bm-a r731 freeze（db9da0e92·表尾）**均已注册**（表尾=W126 行）·W127=无 skip-past-published 链面（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r732bma_w127_band_gate.py rc0 实跑）"),
 ("pre-seat 机证=results/_r731bma_w126_probe.py rc0（ADMIT-derive·回执 results/_r731bma_w126_probe_receipt.txt）；冻结窗 gate 重跑 derive 逐位恒等（A 295_004..297_003 hops 0·B 67_401..67_600 hops 0·双侧算术续带 CLEAN 零拒绝点）",
  "pre-seat 机证=results/_r732bma_w127_probe.py rc0（ADMIT-derive·回执 results/_r732bma_w127_probe_receipt.txt）；冻结窗 gate 重跑 derive 逐位恒等（A 297_004..299_003 hops 0·B 67_601..67_800 hops 0·双侧算术续带 CLEAN 零拒绝点）"),
 ("**席位推送窗实录**（r731 窗口实况）：首推撞 behind 3（bm-c r551 假期值守轮三件·r524 律落后信号）→merge-mode 零 UU→DELIVERED 4a77367d3 0/0 双向自证（r524 两跳收口正法）。",
  "**席位推送窗实录**（r732 窗口实况）：首推撞 behind 3（bm-b r733/r734 假期值守轮三件·r524 律落后信号）→merge-mode 零 UU→DELIVERED b78dc4cc4 0/0 双向自证（r524 两跳收口正法）。"),
 ("本波 ordinal=**第一百一十六枚引擎波（机面计数：注册表 engine_owner 行 115+本候选）**·**bm-a 第四十二枚自有波**〔机面 derive：engine_owner==bm-a 行 41+本候选·gate leg0 机证在场·r359 律计数面以 gate 机输出为准〕。",
  "本波 ordinal=**第一百一十七枚引擎波（机面计数：注册表 engine_owner 行 116+本候选）**·**bm-a 第四十三枚自有波**〔机面 derive：engine_owner==bm-a 行 42+本候选·gate leg0 机证在场·r359 律计数面以 gate 机输出为准〕。"),
 ("**带位（r535 机闸 derive 律·ADMIT 回执=results/_r731bma_w126_band_gate.py 单态门全腿实跑·pre-seat probe results/_r731bma_w126_probe.py 先跑·双窗 derive 恒等）**：本波 **A-ext seed=295_004..297_003**（**A 面算术续带**==W125 行 A 尾 295_003+1 起·步长 2_000·CLEAN 零拒绝点·refusal hops=0）；**B-ext exit seed=67_401..67_600**（**B 面算术续带**==W125 行 B 尾 67_400+1 起·步长 200·CLEAN 零拒绝点·hops=0·与 r730 W125 gate-tail W126+ 投影逐位收敛=跨窗交叉验证）。R250：W126 带从未指派·测量面零结果可钓。扫描面=pre-W126 全一百二十三行注册 N1 带表（表尾=W125 行·leg0 机证 123 行）",
  "**带位（r535 机闸 derive 律·ADMIT 回执=results/_r732bma_w127_band_gate.py 单态门全腿实跑·pre-seat probe results/_r732bma_w127_probe.py 先跑·双窗 derive 恒等）**：本波 **A-ext seed=297_004..299_003**（**A 面算术续带**==W126 行 A 尾 297_003+1 起·步长 2_000·CLEAN 零拒绝点·refusal hops=0）；**B-ext exit seed=67_601..67_800**（**B 面算术续带**==W126 行 B 尾 67_600+1 起·步长 200·CLEAN 零拒绝点·hops=0·与 r731 W126 gate-tail W127+ 投影逐位收敛=跨窗交叉验证）。R250：W127 带从未指派·测量面零结果可钓。扫描面=pre-W127 全一百二十四行注册 N1 带表（表尾=W126 行·leg0 机证 124 行）"),
 ("（p2_calibration v1/v2 canon；W1 ext；W2..W125 落地）的种子带扩展重测",
  "（p2_calibration v1/v2 canon；W1 ext；W2..W126 落地）的种子带扩展重测"),
 ("`scripts/perpetual_faces_n1.py`（W2..W125 落地 runner 的 wave 参数化复用",
  "`scripts/perpetual_faces_n1.py`（W2..W126 落地 runner 的 wave 参数化复用"),
 ("- 批名=**PERPETUAL-N1-W126**。", "- 批名=**PERPETUAL-N1-W127**。"),
 ("起草窗实况：**W1..W125 N1 finalize 已全部落账**〔W124 finalize one-pass bm-a r730+W125 finalize one-pass 同窗 bm-a r731·§7 回填同 commit 在场〕——净账本链头 **671,011**（W125 finalize 落账·K=272,920 合并池·voids LOWAMP-P1/P2）",
  "起草窗实况：**W1..W126 N1 finalize 已全部落账**〔W125 finalize one-pass bm-a r731+W126 finalize one-pass 同窗 bm-a r732·§7 回填同 commit 在场〕——净账本链头 **673,211**（W126 finalize 落账·K=275,120 合并池·voids LOWAMP-P1/P2）"),
 ("累计 null 池投影=272,920+2,200（本波）=**275,120 投影**",
  "累计 null 池投影=275,120+2,200（本波）=**277,320 投影**"),
 ("本机 r730 收口指针「W126 prereg draft+freeze」=表尾后新首个自由号自领",
  "本机 r731 收口指针 W126 gate-tail「W127+ 投影 CLEAN」=表尾后新首个自由号自领"),
 ("T-2026-10-01-141 s1 引擎线第 116 波·bm-a 第四十二枚自有波〔机面 derive：engine_owner==bm-a 行 41+本候选·以 gate leg0 机证为准·含 W123/W124/W125 最近自有波〕。（波号=注册表 W125 行后首个自由号·单态零席位空档〔席位公示=MSG-2026-10-05-1528-bma-w126-seat 先推 origin 7d70b01fd r565 律〕；lane-free；部门 dept:研究）。",
  "T-2026-10-01-141 s1 引擎线第 117 波·bm-a 第四十三枚自有波〔机面 derive：engine_owner==bm-a 行 42+本候选·以 gate leg0 机证为准·含 W124/W125/W126 最近自有波〕。（波号=注册表 W126 行后首个自由号·单态零席位空档〔席位公示=MSG-2026-10-05-1548-bma-w127-seat 先推 origin bef555332 r565 律〕；lane-free；部门 dept:研究）。"),
 ("冻结编辑落工作树后下一 tick 新进程读活树自见 W126 行并点火",
  "冻结编辑落工作树后下一 tick 新进程读活树自见 W127 行并点火"),
 ("`python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W126_PREREG.md`",
  "`python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W127_PREREG.md`"),
 ("- **A 档**（j=0..1,999）：entry rng seed=**295_004+j**（法典 §4 W126 行 A=295_004..297_003·**算术续带**==W125 行 A 尾 295_003+1 起·步长 2_000·CLEAN 零拒绝点·hops=0·ADMIT 回执在场）",
  "- **A 档**（j=0..1,999）：entry rng seed=**297_004+j**（法典 §4 W127 行 A=297_004..299_003·**算术续带**==W126 行 A 尾 297_003+1 起·步长 2_000·CLEAN 零拒绝点·hops=0·ADMIT 回执在场）"),
 ("- **B 档**（j=0..199）：entry rng=**295_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**67_401+j**（法典 §4 W126 行 B=67_401..67_600·**算术续带**==W125 行 B 尾 67_400+1 起·步长 200·CLEAN 零拒绝点·hops=0·与 r730 gate-tail 投影逐位收敛·ADMIT 回执在场）",
  "- **B 档**（j=0..199）：entry rng=**297_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**67_601+j**（法典 §4 W127 行 B=67_601..67_800·**算术续带**==W126 行 B 尾 67_600+1 起·步长 200·CLEAN 零拒绝点·hops=0·与 r731 gate-tail 投影逐位收敛·ADMIT 回执在场）"),
 ("种子带 disjoint 全例（selftest 强制）：W126 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W125 在用带（**全注册·单态**）",
  "种子带 disjoint 全例（selftest 强制）：W127 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W126 在用带（**全注册·单态**）"),
 ("本波机验 ADMIT 回执在场=r731 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest leg 2 全表 disjoint+leg N3-R1 腿+腿探针簇腿+leg W118..W125 在用带腿+A 算术窗净腿+B 算术窗净腿（双侧 CLEAN 零拒绝点机证腿）。",
  "本波机验 ADMIT 回执在场=r732 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest leg 2 全表 disjoint+leg N3-R1 腿+腿探针簇腿+leg W118..W126 在用带腿+A 算术窗净腿+B 算术窗净腿（双侧 CLEAN 零拒绝点机证腿）。"),
 ("合并池 `canon 120 + 已落账波值（起草窗实测 W1..W125 已落账 272,920 实测·derive 禁手抄）",
  "合并池 `canon 120 + 已落账波值（起草窗实测 W1..W126 已落账 275,120 实测·derive 禁手抄）"),
 ('batch_name="PERPETUAL-N1-W126", batch_trials=2200, file_name="results/perpetual_faces/n1_w126_results.json"',
  'batch_name="PERPETUAL-N1-W127", batch_trials=2200, file_name="results/perpetual_faces/n1_w127_results.json"'),
 ("（起草窗实况注记：**W1..W125 N1 finalize 已全部落账**——净账本链头 671,011=W125 finalize 落账〔one-pass·bm-a r731·§7 回填同 commit 在场〕·**K=272,920 合并池**·**零在飞上游席位**（链前置净空波）。本波 §5 预测键=**W125 finalize 实测值**〔results/perpetual_faces/n1_w125_results.json·N1 面最新已落账键〕。",
  "（起草窗实况注记：**W1..W126 N1 finalize 已全部落账**——净账本链头 673,211=W126 finalize 落账〔one-pass·bm-a r732·§7 回填同 commit 在场〕·**K=275,120 合并池**·**零在飞上游席位**（链前置净空波）。本波 §5 预测键=**W126 finalize 实测值**〔results/perpetual_faces/n1_w126_results.json·N1 面最新已落账键〕。"),
 ("1. W126-only mu 与累计池 merged mu（W125 实测键 **−0.092816**·K=272,920 合并池·W125-only 实测 **−0.097976**）差异 **|Δ|<0.02**（W2..W125 共三十+面实测 mu 稳定先例·单波跨键律）。",
  "1. W127-only mu 与累计池 merged mu（W126 实测键 **−0.092894**·K=275,120 合并池·W126-only 实测 **−0.102509**）差异 **|Δ|<0.02**（W2..W126 共三十+面实测 mu 稳定先例·单波跨键律）。"),
 ("2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.244835**=W125 合并池实测）。",
  "2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.244807**=W126 合并池实测）。"),
 ("3. A 档 full_sharpe_p95 与 W125 A 档 p95（**0.3077** 实测锚）差 **<0.05**（门标准注记法 W5..W125 先例：结果知情报校准面·仅作机器断言伪测用·测量面非注册利益）。",
  "3. A 档 full_sharpe_p95 与 W126 A 档 p95（**0.3007** 实测锚）差 **<0.05**（门标准注记法 W5..W126 先例：结果知情报校准面·仅作机器断言伪测用·测量面非注册利益）。"),
 ("4. K-lift 线移动幅度 **≥−0.02**（累计池加深零 se_mu·线自 mu/sigma 微调面非质变——W3..W125 先例·W119 +0.0003/W120 +0.0002/W121 +0.0001/W122 +0.0000/W123 +0.0000/W124 +0.0003/W125 **−0.0001** 正负交替如实报正负）；键 W125 实测 K-lift **−0.0001**（line_merged@K272,920 **1.1753**·line_pre 1.1754·n_eff 668,811；se_mu 收窄链 W121 0.000476→W122 0.000474→W123 0.000472→W124 0.000471→W125 **0.000469**）。",
  "4. K-lift 线移动幅度 **≥−0.02**（累计池加深零 se_mu·线自 mu/sigma 微调面非质变——W3..W126 先例·W120 +0.0002/W121 +0.0001/W122 +0.0000/W123 +0.0000/W124 +0.0003/W125 −0.0001/W126 **−0.0002** 正负交替如实报正负）；键 W126 实测 K-lift **−0.0002**（line_merged@K275,120 **1.1752**·line_pre 1.1754·n_eff 671,011；se_mu 收窄链 W122 0.000474→W123 0.000472→W124 0.000471→W125 0.000469→W126 **0.000467**）。"),
 ("5. **W127+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 297_004..299_003 **CLEAN**（hops=0）；B **67_601..67_800**（hops=0）（r731 冻结窗 gate 回执尾行·与本席位 MSG W127+ 投影披露交叉验证一致=自机 derive 非转抄 r587 律）。",
  "5. **W128+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 299_004..301_003 **CLEAN**（hops=0）；B **68_001..68_200**（hops=1·refusal fact cny_window_p1=68_000 upper-edge endpoint→past-hit restart·D-20261002-05 pin 双读法恒同解族）（r732 冻结窗 gate 回执尾行·与本席位 MSG W128+ 投影披露交叉验证一致=自机 derive 非转抄 r587 律）。"),
 ("- 交付：`results/p2cal_ext/n1_w126/shard-<k>-of-12.json`（append-only·确定性）；`results/perpetual_faces/n1_w126_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 链序前置=**起草窗零在飞上游（W1..W125 全落账）**",
  "- 交付：`results/p2cal_ext/n1_w127/shard-<k>-of-12.json`（append-only·确定性）；`results/perpetual_faces/n1_w127_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 链序前置=**起草窗零在飞上游（W1..W126 全落账）**"),
 ("（engine_owner==bm-a 41 行注册+本候选〔以 gate leg0 机证为准·含 W123/W124/W125 最近自有波〕）；attrition 账本完整性 tripwire 覆盖本波产物件（r448 律）",
  "（engine_owner==bm-a 42 行注册+本候选〔以 gate leg0 机证为准·含 W124/W125/W126 最近自有波〕）；attrition 账本完整性 tripwire 覆盖本波产物件（r448 律）"),
]
for old, new in pairs:
    n = src.count(old)
    assert n == 1, f"needle count={n}: {old[:50]!r}"
    src = src.replace(old, new)

# restore §7/§8 placeholders (strip the W126 backfill)
i7 = src.find("## §7")
i_tail = src.find("- **跑前冻结=本件 commit**", i7)
assert i7 > 0 and i_tail > i7
placeholder = """## §7 跑后实证。【占位·finalize 收口机械回填】

## §8 批后复盘。【占位·跑前为空·终 7-T】

"""
src = src[:i7] + placeholder + src[i_tail:]

io.open(r"research\PERPETUAL_N1_W127_PREREG.md", "w", encoding="utf-8", newline="\n").write(src)
print("W127 prereg written:", len(src), "bytes,", src.count(chr(10)) + 1, "lines")
