# -*- coding: utf-8 -*-
"""r768 bm-a W155 per-wave prereg xform: research/PERPETUAL_N1_W154_PREREG.md
-> research/PERPETUAL_N1_W155_PREREG.md. Needle-asserted (r745 extract-vs-insert
law, every needle count==1 measured); two-form checklist enforced at the
tail (bare wave number and lowercase n1_w154/n1w154 tokens must be
ZERO-residue after xform, except the ONE legitimate sec5 prior-wave key
anchor, r547 owner-context law). sec7/sec8 span-replaced from the r768
same-window backfilled blocks to W155 placeholders (boundary-anchored,
zero byte-drift).
W155 facts: A=355_804..357_803 (staircase fourteenth instance E36, hops=1) +
B=357_804..358_003 (own-A mutual exclusion, hops=1); seat
MSG-2026-10-06-0943-bma-w155-seat -> origin 1fedffbe4 (r768 pre-seat push;
delivery absorbed the bm-c r610 guard-round peer wave via merge, zero
--no-verify); band gate ADMIT receipt results/_r768bma_w155_band_gate.json rc0;
pre-seat probe r768 receipt. W154 finalize = bm-a r768 one-pass (sec7/sec8
backfilled same-window), ledger head 734,811, K=336,720 merged pool;
W154-only mu -0.094237 / merged mu -0.092852 / sigma 0.245021 / A p95 0.3031 /
K-lift -0.0002 @line 1.1807->1.1805 / se_mu 0.000422 / mu_delta_w154_vs_w153ext
+0.005025
(all from results/perpetual_faces/n1_w154_results.json measured keys)."""
import io


def rep(src, pairs, tag):
    for i, p in enumerate(pairs):
        assert len(p) == 2, f"{tag}: pair {i} arity={len(p)}"
        old, new = p
        n = src.count(old)
        assert n == 1, f"{tag}: needle {i} count={n} expect=1: {old[:70]!r}"
        src = src.replace(old, new)
    return src


src = io.open(r"research/PERPETUAL_N1_W154_PREREG.md", encoding="utf-8").read()

pairs = [
    # --- L1 title ---
    ("# PERPETUAL-N1-W154 预注册 · N1 nulls-deepening 泵第 152 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 143+本候选=bm-a 第七十枚自有波【r767】）",
     "# PERPETUAL-N1-W155 预注册 · N1 nulls-deepening 泵第 153 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 144+本候选=bm-a 第七十一枚自有波【r768】）"),
    # --- L3 seat/vacancy/list cluster ---
    ("**波号 154=注册表 W153 行后首个自由号**【本冻结窗 fetch 实核表尾时 W154 号位空档",
     "**波号 155=注册表 W154 行后首个自由号**【本冻结窗 fetch 实核表尾时 W155 号位空档"),
    ("全 inbox/processed/ W154 席位零外机命中（本机席位公示=MSG-2026-10-06-090x-bma-w154-seat 已推 origin dd1702d11 先于本冻结【r565 律·推送窗=direct delivery dd1702d11（r767 pre-seat push·behind-3 bm-b r769 closeout wave-2 peer merge 吸收后快进送达·零 --no-verify）+同窗 self-ack inbox→processed 移位 r767】",
     "全 inbox/processed/ W155 席位零外机命中（本机席位公示=MSG-2026-10-06-0943-bma-w155-seat 已推 origin 1fedffbe4 先于本冻结【r565 律·推送窗=direct delivery 1fedffbe4（r768 pre-seat push·behind-2 bm-c r610 guard-round peer merge 吸收后快进送达·零 --no-verify）+同窗 self-ack inbox→processed 移位 r768】"),
    ("W152=bm-a r764 freeze（520eb01ca）；W153=bm-a r766 freeze（33388e082·表尾）；**均已注册**（表尾 W153 行）。W154=本波 skip-past-published 链面零适用（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r767bma_w154_band_gate.json rc0 实跑）",
     "W152=bm-a r764 freeze（520eb01ca）；W153=bm-a r766 freeze（33388e082）；W154=bm-a r767 freeze（3095cb47e·表尾）；**均已注册**（表尾 W154 行）。W155=本波 skip-past-published 链面零适用（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r768bma_w155_band_gate.json rc0 实跑）"),
    ("pre-seat 机证=results/_r767bma_w154_probe.py rc0（ADMIT-derive·回执 results/_r767bma_w154_probe_receipt.json·**A 首窗拒+同窗互斥面机证在内**）；冻结窗 gate 重跑 derive 逐位恒等（A 353_604..355_603 hops 1·B 355_604..355_803 hops 1——**A=FIRST-CLEAN past prior-wave B 阶梯第十三例（A-hops-prior-B·E36 卡）·B=FIRST-CLEAN past own-wave A（W141 先例 leg2 律）**",
     "pre-seat 机证=results/_r768bma_w155_probe.py rc0（ADMIT-derive·回执 results/_r768bma_w155_probe_receipt.json·**A 首窗拒+同窗互斥面机证在内**）；冻结窗 gate 重跑 derive 逐位恒等（A 355_804..357_803 hops 1·B 357_804..358_003 hops 1——**A=FIRST-CLEAN past prior-wave B 阶梯第十四例（A-hops-prior-B·E36 卡）·B=FIRST-CLEAN past own-wave A（W141 先例 leg2 律）**"),
    ("**席位推送窗实录（r767 窗口实况）**：席位+probe 回执随 W153 finalize 收口窗单 commit 推送 origin 送达 **dd1702d11**（推送窗 behind-3 bm-b r769 closeout wave-2 peer merge 吸收后快进送达·零 --no-verify；同窗 self-ack inbox→processed 移位 r767 再推送达）。> **序数机面锚注记**：本波 ordinal=第一百四十四引擎波·bm-a 第七十枚自有波【机面 derive：engine_owner==bm-a 行 69+本候选以 gate leg0 机证为准】。",
     "**席位推送窗实录（r768 窗口实况）**：席位+probe 回执单 commit、W154 finalize 收口产物同窗随 merge 吸收推送 origin 送达 **1fedffbe4**（推送窗 behind-2 bm-c r610 guard-round peer merge 吸收后快进送达·零 --no-verify；同窗 self-ack inbox→processed 移位 r768 再推送达）。> **序数机面锚注记**：本波 ordinal=第一百四十五引擎波·bm-a 第七十一枚自有波【机面 derive：engine_owner==bm-a 行 70+本候选以 gate leg0 机证为准】。"),
    # --- L5 band block ---
    ("**带位（r535 机阀 derive 律·ADMIT 回执=results/_r767bma_w154_band_gate.json 单态门全腿实跑·pre-seat probe results/_r767bma_w154_probe.py 先跑·双窗 derive 恒等）**：本波 **A-ext seed=353_604..355_603**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第十三例**：A 面算术继续带 353_404..355_403 在其起点即被已注册 W153 B 带 353_404..353_603 **拒**（W153 席位 leg4+r766 gate leg3+r767 §8 承接三投影注记所预言）",
     "**带位（r535 机阀 derive 律·ADMIT 回执=results/_r768bma_w155_band_gate.json 单态门全腿实跑·pre-seat probe results/_r768bma_w155_probe.py 先跑·双窗 derive 恒等）**：本波 **A-ext seed=355_804..357_803**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第十四例**：A 面算术继续带 355_604..357_603 在其起点即被已注册 W154 B 带 355_604..355_803 **拒**（W154 席位 leg4+r767 gate leg3+r768 §8 承接三投影注记所预言）"),
    ("→ 诚实前向走 **1 hop** 落 **353_604..355_603**·**A base==前波 B 尾+1（353_603+1）机检关系**=**A-hops-prior-B 阶梯几何第十三例（E36 卡）**·非轮转 r587 前向单调断言在走册）；**B-ext exit seed=355_604..355_803**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 353_604..353_803 在注册宇宙上 CLEAN 但",
     "→ 诚实前向走 **1 hop** 落 **355_804..357_803**·**A base==前波 B 尾+1（355_803+1）机检关系**=**A-hops-prior-B 阶梯几何第十四例（E36 卡）**·非轮转 r587 前向单调断言在走册）；**B-ext exit seed=357_804..358_003**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 355_804..356_003 在注册宇宙上 CLEAN 但"),
    ("→ B 带本波 A 窗保留走 **1 hop** 落 **355_604..355_803**·**B base==本波 A 尾+1（355_603+1）机检关系**·hop 链逐跳在 probe 回执；**W153 席位 leg4+r766 gate leg3+r767 §8 承接 re-derive-MANDATORY 注记三面兑现**：投影预言 W154 须在 post-W153 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）。R250：W154 带从未指派·测量面零结果可锁。扫描面=pre-W154 全一百五十一行注册 N1 带表（表尾 W153 行·leg0 机证 151 行）",
     "→ B 带本波 A 窗保留走 **1 hop** 落 **357_804..358_003**·**B base==本波 A 尾+1（357_803+1）机检关系**·hop 链逐跳在 probe 回执；**W154 席位 leg4+r767 gate leg3+r768 §8 承接 re-derive-MANDATORY 注记三面兑现**：投影预言 W155 须在 post-W154 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）。R250：W155 带从未指派·测量面零结果可锁。扫描面=pre-W155 全一百五十二行注册 N1 带表（表尾 W154 行·leg0 机证 152 行）"),
    # --- L9 reuse domain ---
    ("（W2..W153 落地 runner 的 wave 参数化复用", "（W2..W154 落地 runner 的 wave 参数化复用"),
    # --- S0 ---
    ("- 批名=**PERPETUAL-N1-W154**。N=", "- 批名=**PERPETUAL-N1-W155**。N="),
    ("起稿窗实况：**W1..W153 N1 finalize 已全部落地**【W153 finalize one-pass bm-a r767·§7/§8 回填 r767 同窗收口】——净账本锚头 **732,611**（W153 finalize 落账【one-pass·K=334,520 合并池·voids LOWAMP-P1/P2】）",
     "起稿窗实况：**W1..W154 N1 finalize 已全部落地**【W154 finalize one-pass bm-a r768·§7/§8 回填 r768 同窗收口】——净账本锚头 **734,811**（W154 finalize 落账【one-pass·K=336,720 合并池·voids LOWAMP-P1/P2】）"),
    ("累计 null 池=334,520+2,200（本波）=**336,720 投影**", "累计 null 池=336,720+2,200（本波）=**338,920 投影**"),
    ("本机 r767 席位 MSG-2026-10-06-090x 投影 W155+ A 355_604..357_603 naive/B 355_804..356_003 naive **re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·投影 A 撞本波 B 带=阶梯 A-hops-prior-B 继承待 W155 注册宇宙复核）",
     "本机 r768 席位 MSG-2026-10-06-0943 投影 W156+ A 357_804..359_803 naive/B 358_004..358_203 naive **re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·投影 A 撞本波 B 带=阶梯 A-hops-prior-B 继承待 W156 注册宇宙复核）"),
    ("T-2026-10-01-141 s1 引擎线第 144 波【bm-a 第七十枚自有波【机面 derive：engine_owner==bm-a 行 69+本候选以 gate leg0 机证为准·同 W150/W151/W152/W153 最近自有波】。（波号=注册表 W153 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-06-090x-bma-w154-seat 先推 origin dd1702d11 r565 律",
     "T-2026-10-01-141 s1 引擎线第 145 波【bm-a 第七十一枚自有波【机面 derive：engine_owner==bm-a 行 70+本候选以 gate leg0 机证为准·同 W151/W152/W153/W154 最近自有波】。（波号=注册表 W154 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-06-0943-bma-w155-seat 先推 origin 1fedffbe4 r565 律"),
    ("自见 W154 行并点火自烧", "自见 W155 行并点火自烧"),
    # --- S0.5 / S1 / S2 ---
    ("--prereg research/PERPETUAL_N1_W154_PREREG.md", "--prereg research/PERPETUAL_N1_W155_PREREG.md"),
    ("v2..W153 落地）的种子带扩展重测", "v2..W154 落地）的种子带扩展重测"),
    # --- S3 ---
    ("entry rng seed=**353_604+j**（法典 §4 W154 行 A=353_604..355_603·**FIRST-CLEAN past prior-wave B 阶梯第十三例**：算术续带 353_404..355_403 起点即被 W153 B 带拒→1 hop 落 353_604..355_603·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场）",
     "entry rng seed=**355_804+j**（法典 §4 W155 行 A=355_804..357_803·**FIRST-CLEAN past prior-wave B 阶梯第十四例**：算术续带 355_604..357_603 起点即被 W154 B 带拒→1 hop 落 355_804..357_803·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场）"),
    ("entry rng=**353_604+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**355_604+j**（法典 §4 W154 行 B=355_604..355_803·**FIRST-CLEAN past own-wave A**：B 算术续带 353_604..353_803 在注册宇宙上 CLEAN 但落在本波 A 窗内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 355_604..355_803·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 W153 席位 leg4+r766 gate leg3+r767 §8 承接 W154+ 投影 re-derive-MANDATORY+同窗互斥预披露注记三面兑现收敛·ADMIT 回执在场）",
     "entry rng=**355_804+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**357_804+j**（法典 §4 W155 行 B=357_804..358_003·**FIRST-CLEAN past own-wave A**：B 算术续带 355_804..356_003 在注册宇宙上 CLEAN 但落在本波 A 窗内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 357_804..358_003·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 W154 席位 leg4+r767 gate leg3+r768 §8 承接 W155+ 投影 re-derive-MANDATORY+同窗互斥预披露注记三面兑现收敛·ADMIT 回执在场）"),
    ("本波设计=W2..W153 逐字复用", "本波设计=W2..W154 逐字复用"),
    ("W154 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W153 在用带（**全注册单态**）",
     "W155 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W154 在用带（**全注册单态**）"),
    ("本波机验 ADMIT 回执在场=r767 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest W154 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W153 行 parity 腿【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）。",
     "本波机验 ADMIT 回执在场=r768 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest W155 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W154 行 parity 腿【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）。"),
    # --- S4 ---
    ("（起草窗实流 W1..W153 已落账 334,520 实测·derive 禁手抄）", "（起草窗实流 W1..W154 已落账 336,720 实测·derive 禁手抄）"),
    ('batch_name="PERPETUAL-N1-W154", batch_trials=2200, file_name="results/perpetual_faces/n1_w154_results.json"',
     'batch_name="PERPETUAL-N1-W155", batch_trials=2200, file_name="results/perpetual_faces/n1_w155_results.json"'),
    # --- S5 ---
    ("（起草窗实况注记：**W1..W153 N1 finalize 已全部落地**——净账本锚头 732,611=W153 finalize 落账【one-pass·bm-a r767·§7/§8 回填 r767 同窗收口】·**K=334,520 合并池**·**零在飞上游席位中**（链前置出空波）。本波 §5 预测键=**W153 finalize 实测值**【results/perpetual_faces/n1_w153_results.json·N1 面最新已落账键】。",
     "（起草窗实况注记：**W1..W154 N1 finalize 已全部落地**——净账本锚头 734,811=W154 finalize 落账【one-pass·bm-a r768·§7/§8 回填 r768 同窗收口】·**K=336,720 合并池**·**零在飞上游席位中**（链前置出空波）。本波 §5 预测键=**W154 finalize 实测值**【results/perpetual_faces/n1_w154_results.json·N1 面最新已落账键】。"),
    ("1. W154-only mu 与累计池 merged mu（W153 实测键 **−0.0928**·K=334,520 合并池·W153-only 实测 **−0.099262**）差异 **|Δ|<0.02**（W2..W153 共一百五十二面实测 mu 稳定先例·单波跨键微）。",
     "1. W155-only mu 与累计池 merged mu（W154 实测键 **−0.0929**·K=336,720 合并池·W154-only 实测 **−0.094237**）差异 **|Δ|<0.02**（W2..W154 共一百五十三面实测 mu 稳定先例·单波跨键微）。"),
    ("2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.2451**=W153 合并池实测）。",
     "2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.2450**=W154 合并池实测）。"),
    ("3. A 档 full_sharpe_p95 与 W153 A 档 p95（**0.3089** 实测锚）差 **<0.05**（门标注法 W5..W153 先例：结果知情面仅作机器断言之用·测量面非注册利益）。",
     "3. A 档 full_sharpe_p95 与 W154 A 档 p95（**0.3031** 实测锚）差 **<0.05**（门标注法 W5..W154 先例：结果知情面仅作机器断言之用·测量面非注册利益）。"),
    ("4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W153 先例·W136 +0.0000/W137 +0.0000/W138 −0.0002/W139 +0.0000/W140 +0.0000/W141 +0.0001/W143 +0.0001/W144 +0.0000/W145 +0.0000/W146 +0.0000/W147 −0.0001/W148 +0.0000/W149 +0.0002/W150 +0.0000/W151 +0.0002/W152 +0.0001/W153 **+0.0001** 如实披露；键 W153 实测 K-lift **+0.0001**【line_merged@K334,520 **1.1806**·line_pre 1.1805·n_eff 730,411；se_mu 收窄键 W140 0.000443→W141 0.000441→W142 0.000440→W143 0.000438→W144 0.000437→W145 0.000435→W146 0.000434→W147 0.000432→W148 0.000431→W149 0.000429→W150 0.000428→W151 0.000426→W152 0.000425→W153 **0.000424**】）。",
     "4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W154 先例·W136 +0.0000/W137 +0.0000/W138 −0.0002/W139 +0.0000/W140 +0.0000/W141 +0.0001/W143 +0.0001/W144 +0.0000/W145 +0.0000/W146 +0.0000/W147 −0.0001/W148 +0.0000/W149 +0.0002/W150 +0.0000/W151 +0.0002/W152 +0.0001/W153 −0.0002/W154 **−0.0002** 如实披露；键 W154 实测 K-lift **−0.0002**【line_merged@K336,720 **1.1805**·line_pre 1.1807·n_eff 732,611；se_mu 收窄键 W140 0.000443→W141 0.000441→W142 0.000440→W143 0.000438→W144 0.000437→W145 0.000435→W146 0.000434→W147 0.000432→W148 0.000431→W149 0.000429→W150 0.000428→W151 0.000426→W152 0.000425→W153 0.000424→W154 **0.000422**】）。"),
    ("5. **W155+ 投影（gate 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 355_604..357_603 **CLEAN**（hops=0）；B first-clean **355_804..356_003 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W155：W155 冻结方必须在 post-W154 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W154 B 带 355_604..355_803 注册后将拒 naive W155 A 窗**——W155 A 重 derive 同强制（越过 W154 B 带·阶梯 A-hops-prior-B 继承）；verify at W155 prereg，hop 链逐跳在 probe 回执。",
     "5. **W156+ 投影（gate 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 357_804..359_803 **CLEAN**（hops=0）；B first-clean **358_004..358_203 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W156：W156 冻结方必须在 post-W155 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W155 B 带 357_804..358_003 注册后将拒 naive W156 A 窗**——W156 A 重 derive 同强制（越过 W155 B 带·阶梯 A-hops-prior-B 继承）；verify at W156 prereg，hop 链逐跳在 probe 回执。"),
    # --- S6 ---
    ("run --shard k --of 12 --wave 154/finalize --wave 154", "run --shard k --of 12 --wave 155/finalize --wave 155"),
    ("n1_w154/ 分片计数增长", "n1_w155/ 分片计数增长"),
    ("results/p2cal_ext/n1_w154/shard-<k>-of-12.json", "results/p2cal_ext/n1_w155/shard-<k>-of-12.json"),
    ("results/perpetual_faces/n1_w154_results.json`（finalize 合并件", "results/perpetual_faces/n1_w155_results.json`（finalize 合并件"),
    ("（W1..W153 全落账）", "（W1..W154 全落账）"),
    ("engine_owner==bm-a 69 行注册 + 本候选——以 gate leg0 机证为准·同 W150/W151/W152/W153 最近自有波", "engine_owner==bm-a 70 行注册 + 本候选——以 gate leg0 机证为准·同 W151/W152/W153/W154 最近自有波"),
]

inter = rep(src, pairs, "prereg-xform")

# --- sec7/sec8 span replacement: r768 same-window backfilled blocks -> placeholders
i7 = inter.find("## §7 跑后实证。【finalize 收口机械回填·bm-a r768")
i8 = inter.find("## §8 批后复盘。【finalize 同窗回填·bm-a r768")
ifin = inter.find("- **跑前冻结=本件 commit**")
assert i7 > 0 and i8 > i7 and ifin > i8, f"sec7/8 span anchors missing: {i7},{i8},{ifin}"
assert inter.count("## §7 跑后实证。【finalize 收口机械回填·bm-a r768") == 1
assert inter.count("## §8 批后复盘。【finalize 同窗回填·bm-a r768") == 1
sec7_block, sec8_block = inter[i7:i8], inter[i8:ifin]
assert "n1_w154_results.json 冻结实测键" in sec7_block and "0.3031" in sec7_block \
    and "mu_delta_w154_vs_w153ext" in sec7_block, "sec7 backfill face drift"
assert "W155+ 投影承接" in sec8_block and "本批无新宝藏" in sec8_block, "sec8 backfill face drift"
ph7 = ("## §7 跑后实证。【finalize 收口机械回填·占位——跑前为空】\n"
       "- （占位：12/12 分片落地后 finalize one-pass 机械回填·回填限本节与 §8·judged 断言照 W154 例。）\n\n")
ph8 = ("## §8 批后复盘。【finalize 同窗回填·占位】\n"
       "- （占位：设计复用面+宝藏捕获问+W156+ 投影承接三行照 W154 例回填。）\n\n")
out = inter[:i7] + ph7 + ph8 + inter[ifin:]
assert out.count("占位：12/12") == 1 and out.count("占位：设计复用面") == 1, "placeholder splice drift"
assert "同窗即回填（r763..r767 窗先例延续" not in out, "backfilled sec7 residue"

# --- two-form checklist (bare wave number + lowercase tokens residue) ---
assert out.count("波号 154") == 0, "bare wave number residue (r754 law)"
# The ONE legitimate n1_w154 occurrence = sec5 prediction-key anchor
assert out.count("n1_w154") == 1, "n1_w154 must appear exactly once (sec5 prior-wave key)"
assert out.count("results/perpetual_faces/n1_w154_results.json·N1 面最新已落账键") == 1, "sec5 anchor context"
assert out.count("n1w154") == 0, "lowercase entry token residue (r754 law)"
assert out.count("PERPETUAL-N1-W154") == 0, "batch name residue"
assert out.count("dd1702d11") == 0, "stale seat sha residue"
# W154 A-band must be fully gone; W154 B-band remains exactly once as the
# prior-wave geometry cite in the L5 derivation narrative
assert out.count("353_604..355_603") == 0, "stale W154 A-band residue"
assert out.count("355_604..355_803") == 1 and \
    out.count("被已注册 W154 B 带 355_604..355_803 **拒**") == 1, \
    "W154 B-band must appear exactly once as prior-wave cite"
assert "波号 155=注册表 W154 行后首个自由号" in out and "355_804..357_803" in out \
    and "357_804..358_003" in out and "PERPETUAL-N1-W155" in out, "new W155 facts missing"

io.open(r"research/PERPETUAL_N1_W155_PREREG.md", "w", encoding="utf-8", newline="\n").write(out)
print("W155 prereg written:", len(out), "chars |", len(pairs), "needle pairs, all count==1 |",
      "sec7/8 span-replaced", len(sec7_block) + len(sec8_block), "->", len(ph7) + len(ph8), "bytes")
