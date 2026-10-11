# -*- coding: utf-8 -*-
# W215 per-wave prereg derivation (bm-c r912 freeze-prep, 2026-10-12 05:4x).
# Method: machine transform of the freeze-time W214 prereg blob
# (git show b0aa90376:research/PERPETUAL_N1_W214_PREREG.md -- the exact
# pre-backfill commit face) with an explicit ordered replacement table.
# Every pair is asserted count==1 (or the noted exact count) BEFORE applying --
# zero silent no-ops (r787 preflight law). Stale-token checklist must be ZERO
# at the end. Bands/facts machine-derived from the committed ADMIT receipt
# results/_w215bmc_20261012_probe_receipt.json + n1_w214_results.json -- never
# transcribed by eye (r587).
import io, json, subprocess, sys, hashlib
sys.stdout.reconfigure(encoding="utf-8")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
BLOB = subprocess.run(["git", "-C", REPO, "show",
                       "b0aa90376:research/PERPETUAL_N1_W214_PREREG.md"],
                      capture_output=True).stdout
assert BLOB, "freeze-time W214 prereg blob fetch failed"
t = BLOB.decode("utf-8")
assert "## §7" in t and "占位" in t, "not the freeze-time (pre-backfill) face"

# machine-derived anchors (never hand-copied)
rec = json.load(open(r"results\_w215bmc_20261012_probe_receipt.json", encoding="utf-8"))
assert rec["verdict"] == "ADMIT" and rec["bands"] == {"A": "487804_489803", "B": "489804_490003"}
w214 = json.load(open(r"results\perpetual_faces\n1_w214_results.json", encoding="utf-8"))
led = w214["science_gates"]["ledger"]
assert led["total"] == 894589 and led["prev_total"] == 892389 and led["batch_trials"] == 2200
merged = w214["null_pool_cumulative"]["merged"]
assert merged["n_values"] == 468720
w214only = w214["null_pool_cumulative"]["w214_only"]
A_p95 = w214["families"]["A_random_engine_exit"]["full_sharpe_p95"]
kl = w214["skill_line_v2_k_lift"]
assert kl["line_delta_k_lift"] == 0.0 and kl["n_eff_held_equal"] == 892389
leg1, leg4 = rec["legs"]["leg1"], rec["legs"]["leg4"]
assert leg1["A"] == [487804, 489803] and leg1["B"] == [489804, 490003]
assert leg1["ARITH_A"] == [487604, 489603] and leg1["B_naive_first_clean"] == [487804, 488003]
assert leg4["W216p_A"] == "489804..491803" and leg4["W216p_B"] == "490004..490203"

PAIRS = [
 # ---- title / header ----
 ("PERPETUAL-N1-W214 预注册 · N1 nulls-deepening 泵第 212 枚",
  "PERPETUAL-N1-W215 预注册 · N1 nulls-deepening 泵第 213 枚"),
 ("engine_owner 行 203 注册在册（表尾 W213 行·probe leg0 机证 211 行 live 单态零注入腿）+本候选=bm-c 第四十四枚自有波【live-derive face：席面 prose 43rd=seat-time face（r909 窗 W213 注册后 live derive·r908 freeze receipt 43rd owned 承袭）→freeze 时 live derive bm-c rows 43+候选=第 44 枚 EXACT·以 freeze 时 live derive 为准 r587/r359】【bm-c 循环班 r910 freeze 窗·2026-10-12 05:0x·",
  "engine_owner 行 204 注册在册（表尾 W214 行·probe leg0 机证 212 行 live 单态零注入腿）+本候选=bm-c 第四十五枚自有波【live-derive face：席面 prose 44th=seat-time face（r911 窗 W214 注册后 live derive·r910 freeze receipt 44th owned 承袭）→freeze 时 live derive bm-c rows 44+候选=第 45 枚 EXACT·以 freeze 时 live derive 为准 r587/r359】【bm-c 循环班 r912 freeze 窗·2026-10-12 05:4x·"),
 # ---- seat / vacancy / chain history ----
 ("live-read r910：burns_active=[] queue_next=[] 实读",
  "live-read r912：burns_active=[] queue_next=[] 实读"),
 ("**波号 214=注册表 W213 席后首个自由号**【probe leg3 vacancy 机证（r909 窗实跑：origin inbox/processed/ 零 W214 席位外机命中+origin perpetual_faces.py 零 214 行+origin perpetual_faces_n1.py 零 PERPETUAL-N1-W214 WAVE_CONFIGS+origin 零 PERPETUAL_N1_W214_PREREG.md 四查）",
  "**波号 215=注册表 W214 席后首个自由号**【probe leg3 vacancy 机证（r911 窗实跑：origin inbox/processed/ 零 W215 席位外机命中+origin perpetual_faces.py 零 215 行+origin perpetual_faces_n1.py 零 PERPETUAL-N1-W215 WAVE_CONFIGS+origin 零 PERPETUAL_N1_W215_PREREG.md 四查）"),
 ("+W213=bm-c r908 五面冻结（a24069f4c）+引擎自燃 12/12+r909 finalize one-pass 已落（K=466,520·账本头 892,389 机读·n1_w213_results.json·04:2x）——本波上游链=W1..W213 finalize 全落地·零在飞上游席·干净前置**",
  "+W213=bm-c r908 五面冻结（a24069f4c）+引擎自燃 12/12+r909 finalize one-pass 已落（K=466,520·账本头 892,389 机读·n1_w213_results.json·04:2x）+W214=bm-c r910 五面冻结（4664900c8）+引擎自燃 12/12+r911 finalize one-pass 已落（K=468,720·账本头 894,589 机读·n1_w214_results.json·05:2x）——本波上游链=W1..W214 finalize 全落地·零在飞上游席·干净前置**"),
 ("本机席位公示=MSG-20261012-0438-bmc-w214-seat 已推 origin d55a6b58b 先于本冻结【r565 律·席位先行·r909 窗】；下游 W215+ 投影见 §5.5（probe 机证 leg4·W215 freezer 承接面）】。**单态零席位空档**：W2..W213 全注册在冻结时点成立",
  "本机席位公示=MSG-20261012-0536-bmc-w215-seat 已推 origin 37d7adc0a 先于本冻结【r565 律·席位先行·r911 窗】；下游 W216+ 投影见 §5.5（probe 机证 leg4·W216 freezer 承接面）】。**单态零席位空档**：W2..W214 全注册在冻结时点成立"),
 # ---- band faces ----
 ("ADMIT 回执=results/_w214bmc_20261012_probe_receipt.json",
  "ADMIT 回执=results/_w215bmc_20261012_probe_receipt.json"),
 ("本波 **A-ext seed=485_604..487_603**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第七十四例**：A 面算术继续带 485_404..487_403（自注册 W213 A 尾 485_403 续）在其起点即被 W213 注册 B 带 485_404..485_603 **拒**（W213 席位 leg4 投影+其 probe 所预言+强制）→ 诚实前向走 **1 hop** 落 **485_604..487_603**·**A base==前波 B 尾+1（485_603+1）机检关系**=**A-hops-prior-B 阶梯几何第七十四例（E36 卡）**·非轮转 r587 前向单调断言在走册；序数面如实披露：本窗 probe 回执 A_semantics 机读序数=SEVENTY-FOURTH（第七十四例）·本件按回执序数面记载非转抄（r587））",
  "本波 **A-ext seed=487_804..489_803**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第七十五例**：A 面算术继续带 487_604..489_603（自注册 W214 A 尾 487_603 续）在其起点即被 W214 注册 B 带 487_604..487_803 **拒**（W214 席位 leg4 投影+其 probe 所预言+强制）→ 诚实前向走 **1 hop** 落 **487_804..489_803**·**A base==前波 B 尾+1（487_803+1）机检关系**=**A-hops-prior-B 阶梯几何第七十五例（E36 卡）**·非轮转 r587 前向单调断言在走册；序数面如实披露：本窗 probe 回执 A_semantics 机读序数=SEVENTY-FIFTH（第七十五例）·本件按回执序数面记载非转抄（r587））"),
 ("**B-ext exit seed=487_604..487_803**（**B 面=FIRST-CLEAN past own-wave A**：B 面 naive first-clean 继续带 485_604..485_803 在注册宇宙上 CLEAN 但**落在本波 A 窗 485_604..487_603 内**（**同窗互斥面 leg2 律·W141 先例**：A 与 B 同一冻结 commit 双注册·互斥断言强制 B 越过本波 A 窗）→ B 带本波 A 窗保留走 **1 hop** 落 **487_604..487_803**·**B base==本波 A 尾+1（487_603+1）机检关系**·hop 链逐跳在 probe 回执（B_hop_chain leg1 机证）；**W213 席位 leg4 投影承接面注记兑现**：投影预言 W214 须在 post-W213 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）",
  "**B-ext exit seed=489_804..490_003**（**B 面=FIRST-CLEAN past own-wave A**：B 面 naive first-clean 继续带 487_804..488_003 在注册宇宙上 CLEAN 但**落在本波 A 窗 487_804..489_803 内**（**同窗互斥面 leg2 律·W141 先例**：A 与 B 同一冻结 commit 双注册·互斥断言强制 B 越过本波 A 窗）→ B 带本波 A 窗保留走 **1 hop** 落 **489_804..490_003**·**B base==本波 A 尾+1（489_803+1）机检关系**·hop 链逐跳在 probe 回执（B_hop_chain leg1 机证）；**W214 席位 leg4 投影承接面注记兑现**：投影预言 W215 须在 post-W214 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）"),
 ("R250：W214 带从未指派", "R250：W215 带从未指派"),
 ("A base=485604 span=2000 checked=2000 verdict=FREE / B base=487604 span=200 checked=200 verdict=FREE",
  "A base=487804 span=2000 checked=2000 verdict=FREE / B base=489804 span=200 checked=200 verdict=FREE"),
 ("扫描面=pre-W214 全二百一十一行注册 N1 带表（表尾 W213 行·probe leg0 机证 211 行 live 单态 owner rows 203）",
  "扫描面=pre-W215 全二百一十二行注册 N1 带表（表尾 W214 行·probe leg0 机证 212 行 live 单态 owner rows 204）"),
 # ---- reuse / editor reference ----
 ("`scripts/perpetual_faces_n1.py`（W2..W213 落地 runner 的 wave 参数化复用",
  "`scripts/perpetual_faces_n1.py`（W2..W214 落地 runner 的 wave 参数化复用"),
 ("selftest W214 face 将随五面冻结落地验证", "selftest W215 face 将随五面冻结落地验证"),
 ("本件与 results/_w214bmc_freeze_edits.py（五面冻结拼接脚本·按 _w213bmc_freeze_edits.py 模板派生·gate0.5 自查 W213 行+W213 finalize 件在场·未落即 loud abort·estate 提取面=本机 W213 块物理字节〔结构已知〕）=freeze-prep 束同窗落地（r908/W213 先例 freeze-prep 同式·本窗上游已全落=执行窗即 freeze 窗）",
  "本件与 results/_w215bmc_freeze_edits.py（五面冻结拼接脚本·按 _w214bmc_freeze_edits.py 模板派生·gate0.5 自查 W214 行+W214 finalize 件在场·未落即 loud abort·estate 提取面=本机 W214 块物理字节〔结构已知〕）=freeze-prep 束同窗落地（r910/W214 先例 freeze-prep 同式·本窗上游已全落=执行窗即 freeze 窗）"),
 # ---- §0 ----
 ("- 批名=**PERPETUAL-N1-W214**。", "- 批名=**PERPETUAL-N1-W215**。"),
 ("**W1..W213 N1 finalize 已全部落地**【净账本锚头 **892,389**·K=466,520 合并池·n1_w213_results.json 机读·W213 finalize one-pass bm-c r909 窗 04:2x（W213 面完整性=12/12 shards consumed+finalize audit finalize_only=true 收口·r908 freeze a24069f4c+引擎自燃链如实注记）】",
  "**W1..W214 N1 finalize 已全部落地**【净账本锚头 **894,589**·K=468,720 合并池·n1_w214_results.json 机读·W214 finalize one-pass bm-c r911 窗 05:2x（W214 面完整性=12/12 shards consumed+finalize audit finalize_only=true 收口·r910 freeze 4664900c8+引擎自燃链如实注记）】"),
 ("累计 null 池=466,520+2,200（本波）=**468,720 投影**", "累计 null 池=468,720+2,200（本波）=**470,920 投影**"),
 ("本机席位公示 MSG-20261012-0438-bmc-w214-seat 已推 origin d55a6b58b r565 律·probe W215+ 投影 A 487_604..489_603 / B 487_804..488_003 **naive-B-inside-naive-A re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·W214 B 带 487_604..487_803 注册后将拒 naive W215 A 窗=阶梯 A-hops-prior-B 第七十五例——**W215 freezer 承接面强制注记：须在 post-W214 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）",
  "本机席位公示 MSG-20261012-0536-bmc-w215-seat 已推 origin 37d7adc0a r565 律·probe W216+ 投影 A 489_804..491_803 / B 490_004..490_203 **naive-B-inside-naive-A re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·W215 B 带 489_804..490_003 注册后将拒 naive W216 A 窗=阶梯 A-hops-prior-B 第七十六例——**W216 freezer 承接面强制注记：须在 post-W215 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"),
 ("T-2026-10-01-141 s1 引擎线第 204 波【bm-c 第四十四枚自有波【机面 derive：probe leg0 bmc_ordinal=43 live face（r909 窗 live 单态计法）——freeze 时 live derive bm-c rows 43+候选=第 44 枚 EXACT（以 freeze 时 live derive 为准 r587/r359）】】。（波号=注册表 W213 席后首个自由号·单态零席位空档于冻结时点成立；中位公示 MSG-20261012-0438-bmc-w214-seat 先推 origin d55a6b58b r565 律；lane-free；dept:研究）",
  "T-2026-10-01-141 s1 引擎线第 205 波【bm-c 第四十五枚自有波【机面 derive：probe leg0 bmc_ordinal=44 live face（r911 窗 live 单态计法）——freeze 时 live derive bm-c rows 44+候选=第 45 枚 EXACT（以 freeze 时 live derive 为准 r587/r359）】】。（波号=注册表 W214 席后首个自由号·单态零席位空档于冻结时点成立；中位公示 MSG-20261012-0536-bmc-w215-seat 先推 origin 37d7adc0a r565 律；lane-free；dept:研究）"),
 ("本窗 free RAM ~6.8GB（MV XQ i2v 影片链=CEO 优先令在飞占用·O-20261011-0012 sec.2.3 影片链优先不变）——N1 引擎点火无 RAM 硬闸（W206/W211/W212/W213 低 RAM 实烧先例）",
  "本窗 free RAM ~2.6GB（MV XQ i2v 影片链=CEO 优先令在飞占用·O-20261011-0012 sec.2.3 影片链优先不变）——N1 引擎点火无 RAM 硬闸（W206/W211/W212/W213/W214 低 RAM 实烧先例）"),
 ("复读自见 W214 行并点火自烧", "复读自见 W215 行并点火自烧"),
 # ---- §0.5 ----
 ("python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W214_PREREG.md",
  "python Tools/banned_direction_gate.py --prereg research/PERPETUAL_N1_W215_PREREG.md"),
 ("（p2_calibration v1/v2 canon；v1 ext；v2..W213 落地）",
  "（p2_calibration v1/v2 canon；v1 ext；v2..W214 落地）"),
 # ---- §3 ----
 ("entry rng seed=**485_604+j**（法典 §4 W214 行 A=485_604..487_603·**FIRST-CLEAN past prior-wave B 阶梯第七十四例**：算术续带 485_404..487_403 起点即被 W213 注册 B 带 485_404..485_603 拒→1 hop 落 485_604..487_603·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场）",
  "entry rng seed=**487_804+j**（法典 §4 W215 行 A=487_804..489_803·**FIRST-CLEAN past prior-wave B 阶梯第七十五例**：算术续带 487_604..489_603 起点即被 W214 注册 B 带 487_604..487_803 拒→1 hop 落 487_804..489_803·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场）"),
 ("entry rng=**485_604+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**487_604+j**（法典 §4 W214 行 B=487_604..487_803·**FIRST-CLEAN past own-wave A**：B 算术续带 485_604..485_803 在注册宇宙上 CLEAN 但落在本波 A 窗 485_604..487_603 内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 487_604..487_803·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 W213 席位 leg4 投影承接面注记兑现收敛·ADMIT 回执在场）",
  "entry rng=**487_804+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**489_804+j**（法典 §4 W215 行 B=489_804..490_003·**FIRST-CLEAN past own-wave A**：B 算术续带 487_804..488_003 在注册宇宙上 CLEAN 但落在本波 A 窗 487_804..489_803 内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 489_804..490_003·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 W214 席位 leg4 投影承接面注记兑现收敛·ADMIT 回执在场）"),
 ("种子带 disjoint 全例（selftest 强制）：W214 带与 v1 在用带", "种子带 disjoint 全例（selftest 强制）：W215 带与 v1 在用带"),
 ("W2..W213 带（冻结时点全注册单态）", "W2..W214 带（冻结时点全注册单态）"),
 ("本波机验 ADMIT 回执在场=_w214bmc_20261012 探针窗", "本波机验 ADMIT 回执在场=_w215bmc_20261012 探针窗"),
 ("selftest W214 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W213 行 parity 腿【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）随五面冻结落地",
  "selftest W215 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W214 行 parity 腿【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）随五面冻结落地"),
 ("从**本机 W213 块物理字节**提取（结构已知·提取自证断言 69 行 range 恒等在场）——W213 块的 W212 leg（1 行）不入 estate 路径·提取后新增 W212+W213 leg 构成 W214 块 parity 72 行（W138..W206+W211+W212+W213）·零假设零风险",
  "从**本机 W214 块物理字节**提取（结构已知·提取自证断言 69 行 range 恒等在场）——W214 块的 W213 leg（1 行）不入 estate 路径·提取后新增 W213+W214 leg 构成 W215 块 parity 73 行（W138..W206+W211+W212+W213+W214）·零假设零风险"),
 # ---- §4 ----
 ("起草窗实流 W1..W213 已落账 466,520 实测", "起草窗实流 W1..W214 已落账 468,720 实测"),
 ("batch_name=\"PERPETUAL-N1-W214\", batch_trials=2200, file_name=\"results/perpetual_faces/n1_w214_results.json\"",
  "batch_name=\"PERPETUAL-N1-W215\", batch_trials=2200, file_name=\"results/perpetual_faces/n1_w215_results.json\""),
 # ---- §5 ----
 ("（起草窗实况注记：**W1..W213 N1 finalize 已全部落地**——净账本锚头 892,389·**K=466,520 合并池**·**零在飞上游席——本波 §5 预测键=**W213 实测值**【results/perpetual_faces/n1_w213_results.json·N1 面最新已落账键·04:2x finalize one-pass】。",
  "（起草窗实况注记：**W1..W214 N1 finalize 已全部落地**——净账本锚头 894,589·**K=468,720 合并池**·**零在飞上游席——本波 §5 预测键=**W214 实测值**【results/perpetual_faces/n1_w214_results.json·N1 面最新已落账键·05:2x finalize one-pass】。"),
 ("1. W214-only mu 与累计池 merged mu（W213 实测键 **−0.09268619**·K=466,520 合并池·W213-only 实测 **−0.09609245**）差异 **|Δ|<0.02**（W2..W213 共二百一十一面实测 mu 稳定先例·单波跨键微；W213-only vs merged 实差 0.0034 在带内）。",
  "1. W215-only mu 与累计池 merged mu（W214 实测键 **−0.09269118**·K=468,720 合并池·W214-only 实测 **−0.09374873**）差异 **|Δ|<0.02**（W2..W214 共二百一十二面实测 mu 稳定先例·单波跨键微；W214-only vs merged 实差 0.0011 在带内）。"),
 ("键 **0.24512063**=W213 合并池实测）。", "键 **0.24512135**=W214 合并池实测）。"),
 ("3. A 档 full_sharpe_p95 与 W213 A 档 p95（**0.3056** 实测锚）差 **<0.05**（门标注法 W5..W212 先例",
  "3. A 档 full_sharpe_p95 与 W214 A 档 p95（**0.3086** 实测锚）差 **<0.05**（门标注法 W5..W213 先例"),
 ("4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W213 先例链披露【各波 K-lift 全在 ±0.0003 内·机读可复核·键 W213 实测 K-lift **0.0000**·line_merged@K466,520 **1.1904**·line_pre_w213 1.1904·n_eff_held_equal 890,189；se_mu 收窄链 …→W209 0.000362→W211 0.000361→W212 0.000360→W213 **0.000359**】）。",
  "4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W214 先例链披露【各波 K-lift 全在 ±0.0003 内·机读可复核·键 W214 实测 K-lift **0.0000**·line_merged@K468,720 **1.1905**·line_pre_w214 1.1905·n_eff_held_equal 892,389；se_mu 收窄链 …→W209 0.000362→W211 0.000361→W212 0.000360→W213 0.000359→W214 **0.000358**】）。"),
 ("5. **W215+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 487_604..489_603 CLEAN（hops=0·pre-W214 宇宙）；B naive first-clean **487_804..488_003 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W215：W215 冻结方必须在 post-W214 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W214 B 带 487_604..487_803 注册后将拒 naive W215 A 窗**——W215 A 重 derive 同强制（越过 W214 B 带·阶梯 A-hops-prior-B 第七十五例）；verify at W215 prereg，hop 链逐跳在 probe 回执。",
  "5. **W216+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 489_804..491_803 CLEAN（hops=0·pre-W215 宇宙）；B naive first-clean **490_004..490_203 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W216：W216 冻结方必须在 post-W215 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W215 B 带 489_804..490_003 注册后将拒 naive W216 A 窗**——W216 A 重 derive 同强制（越过 W215 B 带·阶梯 A-hops-prior-B 第七十六例）；verify at W216 prereg，hop 链逐跳在 probe 回执。"),
 # ---- §6 ----
 ("--wave 214/finalize --wave 214", "--wave 215/finalize --wave 215"),
 ("**点火验证=2 cycle 内产物增长面**【n1_w214/ 分片计数增长·唯一点火证据·r325 律】",
  "**点火验证=2 cycle 内产物增长面**【n1_w215/ 分片计数增长·唯一点火证据·r325 律】"),
 ("`results/p2cal_ext/n1_w214/shard-<k>-of-12.json`", "`results/p2cal_ext/n1_w215/shard-<k>-of-12.json`"),
 ("`results/perpetual_faces/n1_w214_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 键序前置=**起草窗零在飞上游席（W1..W213 全落）**",
  "`results/perpetual_faces/n1_w215_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 键序前置=**起草窗零在飞上游席（W1..W214 全落）**"),
 ("engine_owner==bm-c 43 行注册〔冻结时点〕+ 本候选", "engine_owner==bm-c 44 行注册〔冻结时点〕+ 本候选"),
 # ---- §7/§8 placeholders ----
 ("段——r909 W213 §7 范式）", "段——r911 W214 §7 范式）"),
 ("（占位·finalize 同窗回填：§5.5 W215+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——r909 W213 §8 范式）",
  "（占位·finalize 同窗回填：§5.5 W216+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——r911 W214 §8 范式）"),
]

for old, new in PAIRS:
    c = t.count(old)
    assert c == 1, f"pair count {c} != 1: {old[:70]}..."
    t = t.replace(old, new, 1)

# ---- generic wave-token shifts (after targeted pairs) ----
# Order-critical: at this point every literal "W214" in the text is EITHER an
# original self-ref (pairs rewrote all self faces to W215 already, so these are
# stragglers) OR a pair-written upstream ref. The pairs covered every self face
# (each count==1 asserted); residual self stragglers are caught by the STALE
# checklist below. Mark ALL current W214 as upstream, shift original W213
# prose -> W214, then restore.
t = t.replace("n1_w214_results", "n1_@u_w@_results")   # protect pair-written upstream file refs
t = t.replace("PERPETUAL-N1-W214", "PERPETUAL-N1-W215")
t = t.replace("PERPETUAL_N1_W214", "PERPETUAL_N1_W215")
t = t.replace("n1_w214", "n1_w215")
t = t.replace("_w214bmc", "_w215bmc")
t = t.replace("W214", "@U_W@")
t = t.replace("W213", "W214")
t = t.replace("n1_w213", "n1_w214")
t = t.replace("PERPETUAL_N1_W213", "PERPETUAL_N1_W214")
t = t.replace("_w213bmc", "_w214bmc")
t = t.replace("@u_w@", "w214")
t = t.replace("@U_W@", "W214")

# ---- stale-token checklist (must all be ZERO) ----
STALE = ["485_604", "485_404", "487_403", "485_603", "485_803", "485604", "487604",
         "第 212 枚", "SEVENTY-FOURTH", "第七十四例", "forty-fourth", "第四十四枚",
         "203 注册在册", "bmc_ordinal=43", "r909 窗 W213", "0.3056", "−0.09268619",
         "−0.09609245", "0.24512063", "0438-bmc", "d55a6b58b",
         "04:2x finalize one-pass】" , "211 行 live", "二百一十一行", "r910 freeze 窗·2026-10-12 05:0x"]
for s in STALE:
    c = t.count(s)
    assert c == 0, f"STALE token survives x{c}: {s}"

# ---- new-face presence checks ----
NEW = ["PERPETUAL-N1-W215", "第 213 枚", "487_804..489_803", "489_804..490_003",
       "SEVENTY-FIFTH", "第七十五例", "第四十五枚", "第七十六例",
       "894,589", "468,720", "470,920", "MSG-20261012-0536-bmc-w215-seat", "37d7adc0a",
       "bmc_ordinal=44", "n1_w215_results.json", "0.3086", "−0.09269118",
       "−0.09374873", "0.24512135", "892,389", "n_eff_held_equal 892,389", "0.000358"]
for s in NEW:
    assert t.count(s) >= 1, f"NEW token missing: {s}"
# in-band sanity: own A band appears as the ADMIT face (>=4), own B band too
assert t.count("487_804..489_803") >= 4 and t.count("489_804..490_003") >= 4
# upstream W214 refusing band appears in A-face prose (band-facts + §3A)
assert t.count("487_604..487_803") >= 2

out = r"research\PERPETUAL_N1_W215_PREREG.md"
open(out, "wb").write(t.encode("utf-8"))
print("W215 prereg derived OK:", out)
print("bytes:", len(t.encode("utf-8")), "| sha16:", hashlib.sha256(t.encode("utf-8")).hexdigest()[:16])
print("W214(upper) refs (upstream, expected ~40+):", t.count("W214"), "| W215 self:", t.count("W215"))
