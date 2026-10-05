# -*- coding: utf-8 -*-
"""r759 bm-a W148 per-wave prereg xform: research/PERPETUAL_N1_W147_PREREG.md
-> research/PERPETUAL_N1_W148_PREREG.md. Needle-asserted (r745 extract-vs-insert
law, every needle count==1 measured); two-form checklist enforced at the
tail (bare wave number and lowercase n1_w147/n1w147 tokens must be
ZERO-residue after xform, except the ONE legitimate sec5 prior-wave key
anchor, r547 owner-context law).
W148 facts: A=340_404..342_403 (staircase seventh instance E36, hops=1) +
B=342_404..342_603 (own-A mutual exclusion, hops=1); seat
MSG-2026-10-06-052x-bma-w148-seat -> origin d2c6353ec (r758 pre-seat push;
same-window self-ack inbox->processed move c136baed2 r759); band gate ADMIT
receipt results/_r759bma_w148_band_gate.py rc0; pre-seat probe r758 receipt.
W147 finalize = bm-a r758 one-pass (sec7/sec8 backfill = r759 cite-fix leg),
ledger head 719,411, K=321,320 merged pool;
W147-only mu -0.0921 / merged mu -0.0928 / sigma 0.2449 / A p95 0.3246 /
K-lift -0.0001 @line 1.1792->1.1791 / se_mu 0.000432
(all from results/perpetual_faces/n1_w147_results.json measured keys)."""
import io


def rep(src, pairs, tag):
    # r745 pre-replacement-count law: every needle count==1 at its position
    # in the sequence keeps the fail-closed contract.
    for i, p in enumerate(pairs):
        assert len(p) == 2, f"{tag}: pair {i} arity={len(p)}"
        old, new = p
        n = src.count(old)
        assert n == 1, f"{tag}: needle {i} count={n} expect=1: {old[:70]!r}"
        src = src.replace(old, new)
    return src


src = io.open(r"research\PERPETUAL_N1_W147_PREREG.md", encoding="utf-8").read()

pairs = [
    # --- L1 title ---
    ("# PERPETUAL-N1-W147 预注册 · N1 nulls-deepening 泵第 145 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 136+本候选=bm-a 第六十三枚自有波【r756】）",
     "# PERPETUAL-N1-W148 预注册 · N1 nulls-deepening 泵第 146 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 137+本候选=bm-a 第六十四枚自有波【r758】）"),
    # --- L3 seat/vacancy/list cluster ---
    ("**波号 147=注册表 W146 行后首个自由号**【本冻结窗 fetch 实核表尾时 W147 号位空档",
     "**波号 148=注册表 W147 行后首个自由号**【本冻结窗 fetch 实核表尾时 W148 号位空档"),
    ("全 inbox/processed/ W147 席位零外机命中（本机席位公示=MSG-2026-10-06-045x-bma-w147-seat 已推 origin a5eadcdd7 先于本冻结【r565 律·推送窗=single-hop direct delivery a5eadcdd7——零 behind-signal·零 --no-verify】",
     "全 inbox/processed/ W148 席位零外机命中（本机席位公示=MSG-2026-10-06-052x-bma-w148-seat 已推 origin d2c6353ec 先于本冻结【r565 律·推送窗=direct delivery d2c6353ec（r758 pre-seat push）+同窗 self-ack inbox→processed 移位 c136baed2（r759）——零 behind-signal·零 --no-verify】"),
    ("W144=bm-a r752 freeze（ff6d2f918）；W145=bm-a r754 freeze（98c661f8f）；W146=bm-a r755 freeze（8f06f6910·表尾）；**均已注册**（表尾 W146 行）。W147=本波 skip-past-published 链面零适用（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r757bma_w147_band_gate.py rc0 实跑）",
     "W144=bm-a r752 freeze（ff6d2f918）；W145=bm-a r754 freeze（98c661f8f）；W146=bm-a r755 freeze（8f06f6910）；W147=bm-a r757 freeze（3961555de·表尾）；**均已注册**（表尾 W147 行）。W148=本波 skip-past-published 链面零适用（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r759bma_w148_band_gate.py rc0 实跑）"),
    ("pre-seat 机证=results/_r756bma_w147_probe.py rc0（ADMIT-derive·回执 results/_r756bma_w147_probe_receipt.json·**A 首窗拒+同窗互斥面机证在内**）；冻结窗 gate 重跑 derive 逐位恒等（A 338_204..340_203 hops 1·B 340_204..340_403 hops 1——**A=FIRST-CLEAN past prior-wave B 阶梯第六例（A-hops-prior-B·E36 卡）·B=FIRST-CLEAN past own-wave A（W141 先例 leg2 律）**",
     "pre-seat 机证=results/_r758bma_w148_probe.py rc0（ADMIT-derive·回执 results/_r758bma_w148_probe_receipt.json·**A 首窗拒+同窗互斥面机证在内**）；冻结窗 gate 重跑 derive 逐位恒等（A 340_404..342_403 hops 1·B 342_404..342_603 hops 1——**A=FIRST-CLEAN past prior-wave B 阶梯第七例（A-hops-prior-B·E36 卡）·B=FIRST-CLEAN past own-wave A（W141 先例 leg2 律）**"),
    ("**席位推送窗实录（r756 窗口实况）**：席位+probe 回执单 commit 推送 origin 直接快进送达 **a5eadcdd7**（零 behind-signal·零 --no-verify；W146 finalize 产物 ba6355cab 先窗已独立 delivery 5de34bd42）。> **序数机面锚注记**：本波 ordinal=第一百三十七引擎波·bm-a 第六十三枚自有波【机面 derive：engine_owner==bm-a 行 62+本候选以 gate leg0 机证为准】。",
     "**席位推送窗实录（r758 窗口实况）**：席位+probe 回执随 r758 收口窗单 commit 推送 origin 送达 **d2c6353ec**（零 behind-signal·零 --no-verify；r759 冻结窗同窗 self-ack inbox→processed 移位 c136baed2 再推送达）。> **序数机面锚注记**：本波 ordinal=第一百三十八引擎波·bm-a 第六十四枚自有波【机面 derive：engine_owner==bm-a 行 63+本候选以 gate leg0 机证为准】。"),
    # --- L5 band block ---
    ("ADMIT 回执=results/_r757bma_w147_band_gate.py 单态门全腿实跑·pre-seat probe results/_r756bma_w147_probe.py 先跑",
     "ADMIT 回执=results/_r759bma_w148_band_gate.py 单态门全腿实跑·pre-seat probe results/_r758bma_w148_probe.py 先跑"),
    ("本波 **A-ext seed=338_204..340_203**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第六例**：A 面算术继续带 338_004..340_003 在其起点即被已注册 W146 B 带 338_004..338_203 **拒**（r755 W146 gate 尾投影注记所预言）",
     "本波 **A-ext seed=340_404..342_403**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第七例**：A 面算术继续带 340_204..342_203 在其起点即被已注册 W147 B 带 340_204..340_403 **拒**（W147 席位 leg4+r757 gate leg3 双投影注记所预言）"),
    ("→ 诚实前向走 **1 hop** 落 **338_204..340_203**·**A base==前波 B 尾+1（338_203+1）机检关系**=**A-hops-prior-B 阶梯几何第六例（E36 卡）**·非轮转 r587 前向单调断言在走册）；**B-ext exit seed=340_204..340_403**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 338_204..338_403 在注册宇宙上 CLEAN 但**落在本波 A 窗内**",
     "→ 诚实前向走 **1 hop** 落 **340_404..342_403**·**A base==前波 B 尾+1（340_403+1）机检关系**=**A-hops-prior-B 阶梯几何第七例（E36 卡）**·非轮转 r587 前向单调断言在走册）；**B-ext exit seed=342_404..342_603**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 340_404..340_603 在注册宇宙上 CLEAN 但**落在本波 A 窗内**"),
    ("→ B 带本波 A 窗保留走 **1 hop** 落 **340_204..340_403**·**B base==本波 A 尾+1（340_203+1）机检关系**·hop 链逐跳在 probe 回执；**r755 W146 gate 尾投影 re-derive-MANDATORY 注记双面兑现**：投影预言 W147 须在 post-W146 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）。R250：W147 带从未指派·测量面零结果可锁。扫描面=pre-W147 全一百四十四行注册 N1 带表（表尾 W146 行·leg0 机证 144 行）",
     "→ B 带本波 A 窗保留走 **1 hop** 落 **342_404..342_603**·**B base==本波 A 尾+1（342_403+1）机检关系**·hop 链逐跳在 probe 回执；**W147 席位 leg4+r757 gate leg3 re-derive-MANDATORY 注记双面兑现**：投影预言 W148 须在 post-W147 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）。R250：W148 带从未指派·测量面零结果可锁。扫描面=pre-W148 全一百四十五行注册 N1 带表（表尾 W147 行·leg0 机证 145 行）"),
    # --- L9 reuse domain ---
    ("（W2..W146 落地 runner 的 wave 参数化复用", "（W2..W147 落地 runner 的 wave 参数化复用"),
    # --- S0 ---
    ("- 批名=**PERPETUAL-N1-W147**。N=", "- 批名=**PERPETUAL-N1-W148**。N="),
    ("起稿窗实况：**W1..W146 N1 finalize 已全部落地**【W146 finalize one-pass bm-a r756·§7/§8 回填同 commit 在场】——净账本锚头 **717,211**（W146 finalize 落账【one-pass·K=319,120 合并池·voids LOWAMP-P1/P2】）",
     "起稿窗实况：**W1..W147 N1 finalize 已全部落地**【W147 finalize one-pass bm-a r758·§7/§8 回填 r759 cite-fix 腿补呈】——净账本锚头 **719,411**（W147 finalize 落账【one-pass·K=321,320 合并池·voids LOWAMP-P1/P2】）"),
    ("累计 null 池=319,120+2,200（本波）=**321,320 投影**", "累计 null 池=321,320+2,200（本波）=**323,320 投影**"),
    ("本机 r756 席位 MSG-2026-10-06-045x 投影 W148+ A 340_204..342_203 naive/B 340_404..340_603 naive **re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·投影 A 撞本波 B 带=阶梯 A-hops-prior-B 继承待 W148 注册宇宙复核）",
     "本机 r758 席位 MSG-2026-10-06-052x 投影 W149+ A 342_404..344_403 naive/B 342_604..342_803 naive **re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·投影 A 撞本波 B 带=阶梯 A-hops-prior-B 继承待 W149 注册宇宙复核）"),
    ("T-2026-10-01-141 s1 引擎线第 137 波【bm-a 第六十三枚自有波【机面 derive：engine_owner==bm-a 行 62+本候选以 gate leg0 机证为准·同 W143/W144/W145/W146 最近自有波】。（波号=注册表 W146 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-06-045x-bma-w147-seat 先推 origin a5eadcdd7 r565 律",
     "T-2026-10-01-141 s1 引擎线第 138 波【bm-a 第六十四枚自有波【机面 derive：engine_owner==bm-a 行 63+本候选以 gate leg0 机证为准·同 W144/W145/W146/W147 最近自有波】。（波号=注册表 W147 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-06-052x-bma-w148-seat 先推 origin d2c6353ec r565 律"),
    ("自见 W147 行并点火自烧", "自见 W148 行并点火自烧"),
    # --- S0.5 / S1 / S2 ---
    ("--prereg research/PERPETUAL_N1_W147_PREREG.md", "--prereg research/PERPETUAL_N1_W148_PREREG.md"),
    ("v2..W146 落地）的种子带扩展重测", "v2..W147 落地）的种子带扩展重测"),
    # --- S3 ---
    ("entry rng seed=**338_204+j**（法典 §4 W147 行 A=338_204..340_203·**FIRST-CLEAN past prior-wave B 阶梯第六例**：算术续带 338_004..340_003 起点即被 W146 B 带拒→1 hop 落 338_204..340_203·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场）",
     "entry rng seed=**340_404+j**（法典 §4 W148 行 A=340_404..342_403·**FIRST-CLEAN past prior-wave B 阶梯第七例**：算术续带 340_204..342_203 起点即被 W147 B 带拒→1 hop 落 340_404..342_403·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场）"),
    ("entry rng=**338_204+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**340_204+j**（法典 §4 W147 行 B=340_204..340_403·**FIRST-CLEAN past own-wave A**：B 算术续带 338_204..338_403 在注册宇宙上 CLEAN 但落在本波 A 窗内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 340_204..340_403·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 r755 W146 gate leg3 W147+ 投影 re-derive-MANDATORY+同窗互斥预披露注记双面兑现收敛·ADMIT 回执在场）",
     "entry rng=**340_404+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**342_404+j**（法典 §4 W148 行 B=342_404..342_603·**FIRST-CLEAN past own-wave A**：B 算术续带 340_404..340_603 在注册宇宙上 CLEAN 但落在本波 A 窗内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 342_404..342_603·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 W147 席位 leg4+r757 gate leg3 W148+ 投影 re-derive-MANDATORY+同窗互斥预披露注记双面兑现收敛·ADMIT 回执在场）"),
    ("本波设计=W2..W146 逐字复用", "本波设计=W2..W147 逐字复用"),
    ("W147 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W146 在用带（**全注册单态**）",
     "W148 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W147 在用带（**全注册单态**）"),
    ("本波机验 ADMIT 回执在场=r757 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest W147 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W146 行 parity 腿【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）。",
     "本波机验 ADMIT 回执在场=r759 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest W148 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W147 行 parity 腿【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）。"),
    # --- S4 ---
    ("（起草窗实流 W1..W146 已落账 319,120 实测·derive 禁手抄）", "（起草窗实流 W1..W147 已落账 321,320 实测·derive 禁手抄）"),
    ('batch_name="PERPETUAL-N1-W147", batch_trials=2200, file_name="results/perpetual_faces/n1_w147_results.json"',
     'batch_name="PERPETUAL-N1-W148", batch_trials=2200, file_name="results/perpetual_faces/n1_w148_results.json"'),
    # --- S5 ---
    ("（起草窗实况注记：**W1..W146 N1 finalize 已全部落地**——净账本锚头 717,211=W146 finalize 落账【one-pass·bm-a r756·§7/§8 回填同 commit 在场】·**K=319,120 合并池**·**零在飞上游席位中**（链前置出空波）。本波 §5 预测键=**W146 finalize 实测值**【results/perpetual_faces/n1_w146_results.json·N1 面最新已落账键】。",
     "（起草窗实况注记：**W1..W147 N1 finalize 已全部落地**——净账本锚头 719,411=W147 finalize 落账【one-pass·bm-a r758·§7/§8 回填 r759 cite-fix 腿补呈】·**K=321,320 合并池**·**零在飞上游席位中**（链前置出空波）。本波 §5 预测键=**W147 finalize 实测值**【results/perpetual_faces/n1_w147_results.json·N1 面最新已落账键】。"),
    ("1. W147-only mu 与累计池 merged mu（W146 实测键 **−0.0928**·K=319,120 合并池·W146-only 实测 **−0.0888**）差异 **|Δ|<0.02**（W2..W146 共一百四十五面实测 mu 稳定先例·单波跨键微）。",
     "1. W148-only mu 与累计池 merged mu（W147 实测键 **−0.0928**·K=321,320 合并池·W147-only 实测 **−0.0921**）差异 **|Δ|<0.02**（W2..W147 共一百四十六面实测 mu 稳定先例·单波跨键微）。"),
    ("2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.2449**=W146 合并池实测）。",
     "2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.2449**=W147 合并池实测）。"),
    ("3. A 档 full_sharpe_p95 与 W146 A 档 p95（**0.3121** 实测锚）差 **<0.05**（门标注法 W5..W146 先例：结果知情面仅作机器断言之用·测量面非注册利益）。",
     "3. A 档 full_sharpe_p95 与 W147 A 档 p95（**0.3246** 实测锚）差 **<0.05**（门标注法 W5..W147 先例：结果知情面仅作机器断言之用·测量面非注册利益）。"),
    ("4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W146 先例·W136 +0.0000/W137 +0.0000/W138 −0.0002/W139 +0.0000/W140 +0.0000/W141 +0.0001/W143 +0.0001/W144 +0.0000/W145 +0.0000/W146 **+0.0000** 如实披露；键 W146 实测 K-lift **+0.0000**【line_merged@K319,120 **1.179**·line_pre 1.179·n_eff 715,011；se_mu 收窄键 W140 0.000443→W141 0.000441→W142 0.000440→W143 0.000438→W144 0.000437→W145 0.000435→W146 **0.000434**】）。",
     "4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W147 先例·W136 +0.0000/W137 +0.0000/W138 −0.0002/W139 +0.0000/W140 +0.0000/W141 +0.0001/W143 +0.0001/W144 +0.0000/W145 +0.0000/W146 +0.0000/W147 **−0.0001** 如实披露；键 W147 实测 K-lift **−0.0001**【line_merged@K321,320 **1.1791**·line_pre 1.1792·n_eff 717,211；se_mu 收窄键 W140 0.000443→W141 0.000441→W142 0.000440→W143 0.000438→W144 0.000437→W145 0.000435→W146 0.000434→W147 **0.000432**】）。"),
    ("5. **W148+ 投影（gate 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 340_204..342_203 **CLEAN**（hops=0）；B first-clean **340_404..340_603 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W148：W148 冻结方必须在 post-W147 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W147 B 带 340_204..340_403 注册后将拒 naive W148 A 窗**——W148 A 重 derive 同强制（越过 W147 B 带·阶梯 A-hops-prior-B 继承）；verify at W148 prereg，hop 链逐跳在 probe 回执。",
     "5. **W149+ 投影（gate 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 342_404..344_403 **CLEAN**（hops=0）；B first-clean **342_604..342_803 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W149：W149 冻结方必须在 post-W148 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W148 B 带 342_404..342_603 注册后将拒 naive W149 A 窗**——W149 A 重 derive 同强制（越过 W148 B 带·阶梯 A-hops-prior-B 继承）；verify at W149 prereg，hop 链逐跳在 probe 回执。"),
    # --- S6 ---
    ("run --shard k --of 12 --wave 147/finalize --wave 147", "run --shard k --of 12 --wave 148/finalize --wave 148"),
    ("n1_w147/ 分片计数增长", "n1_w148/ 分片计数增长"),
    ("results/p2cal_ext/n1_w147/shard-<k>-of-12.json", "results/p2cal_ext/n1_w148/shard-<k>-of-12.json"),
    ("results/perpetual_faces/n1_w147_results.json`（finalize 合并件", "results/perpetual_faces/n1_w148_results.json`（finalize 合并件"),
    ("（W1..W146 全落账）", "（W1..W147 全落账）"),
    ("engine_owner==bm-a 62 行注册 + 本候选——以 gate leg0 机证为准·同 W143/W144/W145/W146 最近自有波", "engine_owner==bm-a 63 行注册 + 本候选——以 gate leg0 机证为准·同 W144/W145/W146/W147 最近自有波"),
    # --- S7 backfilled region (r759 cite-fix) -> W148 placeholder ---
    ("## §7 跑后实证。【finalize 收口机械回填·bm-a r758·one-pass rc0·12/12 分片消费；§7/§8 回填窗注记：r758 finalize one-pass 压缩收口窗未及回填·r759 W148 冻结窗 cite-fix 腿补呈——回填内容=n1_w147_results.json 冻结实测键·零改判据】\n- **合并池**：pre-W147 K=319,120（mu=−0.092829·sigma=0.244947）→ W147-only K=2,200（mu=−0.092147·sigma=0.243162）→ **merged K=321,320（mu=−0.0928·sigma=0.2449）**；账本 717,211+2,200=**719,411**（voids_applied=LOWAMP-P1/P2·file=results/perpetual_faces/n1_w147_results.json·evidence_cutoff=2026-09-22）。\n- **skill_line_v2 K-lift**（n_eff 恒等 717,211）：1.1792 → **1.1791**（Δ=**−0.0001**）；se_mu 收窄链 W146 0.000434 → **0.000432**（0.244935/√321,320）。\n- **A 档 full_sharpe_p95=0.3246**（2,000 runs·W146 锚 0.3121）。\n- **§5 四预测键全过（机证）**：①|W147-only mu − merged mu|=0.0007<0.02 ✓ ②sigma 相对变化 −0.0051%<±10% ✓ ③A p95 差 +0.0125<0.05 ✓ ④K-lift −0.0001≤±0.02 ✓。\n- **canon flip：NOT performed**（K2,200 同例法·治理提锚面 only·结果件如实注记）。\n- 审计：12 shards 零重叠连续覆盖 A[0,2000)/B[0,200)·n_backtests 合计 2,200·machine=bm-a·audit.finalize_only=true·批内波间漂移键 mu_delta_w147_vs_w146ext=−0.003312。",
     "## §7 跑后实证。【finalize 收口机械回填·占位——跑前为空】\n- （占位：12/12 分片落地后 finalize one-pass 机械回填·回填限本节与 §8·judged 断言照 W147 例。）"),
    # --- S8 backfilled region (r759 cite-fix) -> W148 placeholder ---
    ("## §8 批后复盘。【finalize 同窗回填·bm-a r758（cite-fix 补呈窗 r759）】\n- 设计=v1 冻结逐字复用·纯种子带深化——零新机制零新方法；**宝藏捕获问（O-20261003-2030 §1 判决 finalize 收口步）：本批无新宝藏**（A-hops-prior-B 阶梯第六例+同窗互斥 leg2 面已于冻结窗 r757 确认·E36 卡既有·finalize 无新增面）；方法论资产卡无 append 面。\n- W148+ 投影承接（§5 键 5 冻结窗已披露）：A naive 340_204..342_203 将被本波 B 带 340_204..340_403 拒（阶梯 A-hops-prior-B 继承）→ W148 A 重 derive 同强制（越过 W147 B 带）；B naive 340_404..340_603 落重 derive 后 A 窗内=**同窗互斥 leg2 律**——**W148 冻结方必在 post-W147 注册宇宙重 derive 且 derive B 时预留本波 A 窗**（E36 卡·W141/W143/W145/W147 先例链）；verify at W148 prereg，hop 链逐跳在 probe 回执。",
     "## §8 批后复盘。【finalize 同窗回填·占位】\n- （占位：设计复用面+宝藏捕获问+W149+ 投影承接三行照 W147 例回填。）"),
]

out = rep(src, pairs, "prereg-xform")

# --- two-form checklist (bare wave number + lowercase tokens residue) ---
assert out.count("波号 147") == 0, "bare wave number residue (r754 law)"
# The ONE legitimate n1_w147 occurrence = sec5 prediction-key anchor
# (prior-wave measured values file; needle new text by design -- W148 sec5
# keys off W147 as latest finalized). r547 law: pin owner context, not bare
# token; all own-wave n1_w147 forms (shard dir, ignition counter, file_name)
# were replaced by needles above.
assert out.count("n1_w147") == 1, "n1_w147 must appear exactly once (sec5 prior-wave key)"
assert out.count("results/perpetual_faces/n1_w147_results.json·N1 面最新已落账键") == 1, "sec5 anchor context"
assert out.count("n1w147") == 0, "lowercase entry token residue (r754 law)"
assert out.count("PERPETUAL-N1-W147") == 0, "batch name residue"
assert out.count("a5eadcdd7") == 0, "stale seat sha residue"
# W147 A-band must be fully gone; W147 B-band remains exactly once as the
# prior-wave geometry cite in the L5 derivation narrative
# ("rejected by registered W147 B band") -- needle new text by design.
assert out.count("338_204..340_203") == 0, "stale W147 A-band residue"
assert out.count("340_204..340_403") == 1 and \
    out.count("被已注册 W147 B 带 340_204..340_403 **拒**") == 1, \
    "W147 B-band must appear exactly once as prior-wave cite"
# W147 mentions remain legitimately as PRIOR-wave refs; sanity: new facts present
assert "波号 148=注册表 W147 行后首个自由号" in out and "340_404..342_403" in out \
    and "342_404..342_603" in out and "PERPETUAL-N1-W148" in out, "new W148 facts missing"

io.open(r"research\PERPETUAL_N1_W148_PREREG.md", "w", encoding="utf-8", newline="\n").write(out)
print("W148 prereg written:", len(out), "bytes |", len(pairs), "needle pairs, all count==1")
