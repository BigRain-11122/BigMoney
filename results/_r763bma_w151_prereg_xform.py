# -*- coding: utf-8 -*-
"""r763 bm-a W151 per-wave prereg xform: research/PERPETUAL_N1_W150_PREREG.md
-> research/PERPETUAL_N1_W151_PREREG.md. Needle-asserted (r745 extract-vs-insert
law, every needle count==1 measured); two-form checklist enforced at the
tail (bare wave number and lowercase n1_w150/n1w150 tokens must be
ZERO-residue after xform, except the ONE legitimate sec5 prior-wave key
anchor, r547 owner-context law). sec7/sec8 span-replaced from the r763
same-window backfilled blocks to W151 placeholders (boundary-anchored,
zero byte-drift).
W151 facts: A=347_004..349_003 (staircase tenth instance E36, hops=1) +
B=349_004..349_203 (own-A mutual exclusion, hops=1); seat
MSG-2026-10-06-075x-bma-w151-seat -> origin f8e1306c8 (r763 pre-seat push;
same-window self-ack inbox->processed move 351170f89 r763); band gate ADMIT
receipt results/_r763bma_w151_band_gate.py rc0; pre-seat probe r763 receipt.
W150 finalize = bm-a r763 one-pass (sec7/sec8 backfilled same-window),
ledger head 726,011, K=327,920 merged pool;
W150-only mu -0.1000 / merged mu -0.0928 / sigma 0.2450 / A p95 0.3114 /
K-lift +0.0000 @line 1.1797->1.1797 / se_mu 0.000428
(all from results/perpetual_faces/n1_w150_results.json measured keys)."""
import io


def rep(src, pairs, tag):
    for i, p in enumerate(pairs):
        assert len(p) == 2, f"{tag}: pair {i} arity={len(p)}"
        old, new = p
        n = src.count(old)
        assert n == 1, f"{tag}: needle {i} count={n} expect=1: {old[:70]!r}"
        src = src.replace(old, new)
    return src


src = io.open(r"research/PERPETUAL_N1_W150_PREREG.md", encoding="utf-8").read()

pairs = [
    # --- L1 title ---
    ("# PERPETUAL-N1-W150 预注册 · N1 nulls-deepening 泵第 148 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 139+本候选=bm-a 第六十六枚自有波【r762】）",
     "# PERPETUAL-N1-W151 预注册 · N1 nulls-deepening 泵第 149 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 140+本候选=bm-a 第六十七枚自有波【r763】）"),
    # --- L3 seat/vacancy/list cluster ---
    ("**波号 150=注册表 W149 行后首个自由号**【本冻结窗 fetch 实核表尾时 W150 号位空档",
     "**波号 151=注册表 W150 行后首个自由号**【本冻结窗 fetch 实核表尾时 W151 号位空档"),
    ("全 inbox/processed/ W150 席位零外机命中（本机席位公示=MSG-2026-10-06-070x-bma-w150-seat 已推 origin bb33022de 先于本冻结【r565 律·推送窗=direct delivery bb33022de（r762 pre-seat push）+同窗 self-ack inbox→processed 移位 860d529f3（r762）——零 behind-signal·零 --no-verify】",
     "全 inbox/processed/ W151 席位零外机命中（本机席位公示=MSG-2026-10-06-075x-bma-w151-seat 已推 origin f8e1306c8 先于本冻结【r565 律·推送窗=direct delivery f8e1306c8（r763 pre-seat push）+同窗 self-ack inbox→processed 移位 351170f89（r763）——零 behind-signal·零 --no-verify】"),
    ("W147=bm-a r757 freeze（3961555de）；W148=bm-a r759 freeze（92c5ab03c）；W149=bm-a r761 freeze（0cef02a00·表尾）；**均已注册**（表尾 W149 行）。W150=本波 skip-past-published 链面零适用（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r762bma_w150_band_gate.py rc0 实跑）",
     "W147=bm-a r757 freeze（3961555de）；W148=bm-a r759 freeze（92c5ab03c）；W149=bm-a r761 freeze（0cef02a00）；W150=bm-a r762 freeze（fedebeb32·表尾）；**均已注册**（表尾 W150 行）。W151=本波 skip-past-published 链面零适用（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r763bma_w151_band_gate.py rc0 实跑）"),
    ("pre-seat 机证=results/_r762bma_w150_probe.py rc0（ADMIT-derive·回执 results/_r762bma_w150_probe_receipt.json·**A 首窗拒+同窗互斥面机证在内**）；冻结窗 gate 重跑 derive 逐位恒等（A 344_804..346_803 hops 1·B 346_804..347_003 hops 1——**A=FIRST-CLEAN past prior-wave B 阶梯第九例（A-hops-prior-B·E36 卡）·B=FIRST-CLEAN past own-wave A（W141 先例 leg2 律）**",
     "pre-seat 机证=results/_r763bma_w151_probe.py rc0（ADMIT-derive·回执 results/_r763bma_w151_probe_receipt.json·**A 首窗拒+同窗互斥面机证在内**）；冻结窗 gate 重跑 derive 逐位恒等（A 347_004..349_003 hops 1·B 349_004..349_203 hops 1——**A=FIRST-CLEAN past prior-wave B 阶梯第十例（A-hops-prior-B·E36 卡）·B=FIRST-CLEAN past own-wave A（W141 先例 leg2 律）**"),
    ("**席位推送窗实录（r762 窗口实况）**：席位+probe 回执随 r762 W149 finalize 收口单 commit 推送 origin 直接快进送达 **bb33022de**（零 behind-signal·零 --no-verify；同窗 self-ack inbox→processed 移位 860d529f3 r762 再推送达）。> **序数机面锚注记**：本波 ordinal=第一百四十引擎波·bm-a 第六十六枚自有波【机面 derive：engine_owner==bm-a 行 65+本候选以 gate leg0 机证为准】。",
     "**席位推送窗实录（r763 窗口实况）**：席位+probe 回执单 commit 推送 origin 直接快进送达 **f8e1306c8**（零 behind-signal·零 --no-verify；同窗 self-ack inbox→processed 移位 351170f89 r763 再推送达）。> **序数机面锚注记**：本波 ordinal=第一百四十一引擎波·bm-a 第六十七枚自有波【机面 derive：engine_owner==bm-a 行 66+本候选以 gate leg0 机证为准】。"),
    # --- L5 band block ---
    ("**带位（r535 机阀 derive 律·ADMIT 回执=results/_r762bma_w150_band_gate.py 单态门全腿实跑·pre-seat probe results/_r762bma_w150_probe.py 先跑·双窗 derive 恒等）**：本波 **A-ext seed=344_804..346_803**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第九例**：A 面算术继续带 344_604..346_603 在其起点即被已注册 W149 B 带 344_604..344_803 **拒**（W149 席位 leg4+r761 gate leg3 双投影注记所预言）",
     "**带位（r535 机阀 derive 律·ADMIT 回执=results/_r763bma_w151_band_gate.py 单态门全腿实跑·pre-seat probe results/_r763bma_w151_probe.py 先跑·双窗 derive 恒等）**：本波 **A-ext seed=347_004..349_003**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第十例**：A 面算术继续带 346_804..348_803 在其起点即被已注册 W150 B 带 346_804..347_003 **拒**（W150 席位 leg4+r762 gate leg3 双投影注记所预言）"),
    ("→ 诚实前向走 **1 hop** 落 **344_804..346_803**·**A base==前波 B 尾+1（344_803+1）机检关系**=**A-hops-prior-B 阶梯几何第九例（E36 卡）**·非轮转 r587 前向单调断言在走册）；**B-ext exit seed=346_804..347_003**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 344_804..345_003 在注册宇宙上 CLEAN 但**落在本波 A 窗内**",
     "→ 诚实前向走 **1 hop** 落 **347_004..349_003**·**A base==前波 B 尾+1（347_003+1）机检关系**=**A-hops-prior-B 阶梯几何第十例（E36 卡）**·非轮转 r587 前向单调断言在走册）；**B-ext exit seed=349_004..349_203**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 347_004..347_203 在注册宇宙上 CLEAN 但**落在本波 A 窗内**"),
    ("→ B 带本波 A 窗保留走 **1 hop** 落 **346_804..347_003**·**B base==本波 A 尾+1（346_803+1）机检关系**·hop 链逐跳在 probe 回执；**W149 席位 leg4+r761 gate leg3 re-derive-MANDATORY 注记双面兑现**：投影预言 W150 须在 post-W149 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）。R250：W150 带从未指派·测量面零结果可锁。扫描面=pre-W150 全一百四十七行注册 N1 带表（表尾 W149 行·leg0 机证 147 行）；v1 ext；v1 在用带；SEED_REGISTRY 全键 188 值",
     "→ B 带本波 A 窗保留走 **1 hop** 落 **349_004..349_203**·**B base==本波 A 尾+1（349_003+1）机检关系**·hop 链逐跳在 probe 回执；**W150 席位 leg4+r762 gate leg3 re-derive-MANDATORY 注记双面兑现**：投影预言 W151 须在 post-W150 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）。R250：W151 带从未指派·测量面零结果可锁。扫描面=pre-W151 全一百四十八行注册 N1 带表（表尾 W150 行·leg0 机证 148 行）；v1 ext；v1 在用带；SEED_REGISTRY 全键 188 值"),
    # --- L9 reuse domain ---
    ("（W2..W149 落地 runner 的 wave 参数化复用", "（W2..W150 落地 runner 的 wave 参数化复用"),
    # --- S0 ---
    ("- 批名=**PERPETUAL-N1-W150**。N=", "- 批名=**PERPETUAL-N1-W151**。N="),
    ("起稿窗实况：**W1..W149 N1 finalize 已全部落地**【W149 finalize one-pass bm-a r762·§7/§8 回填 r762 同窗收口】——净账本锚头 **723,811**（W149 finalize 落账【one-pass·K=325,720 合并池·voids LOWAMP-P1/P2】）",
     "起稿窗实况：**W1..W150 N1 finalize 已全部落地**【W150 finalize one-pass bm-a r763·§7/§8 回填 r763 同窗收口】——净账本锚头 **726,011**（W150 finalize 落账【one-pass·K=327,920 合并池·voids LOWAMP-P1/P2】）"),
    ("累计 null 池=325,720+2,200（本波）=**327,920 投影**", "累计 null 池=327,920+2,200（本波）=**330,120 投影**"),
    ("本机 r762 席位 MSG-2026-10-06-070x 投影 W151+ A 346_804..348_803 naive/B 347_004..347_203 naive **re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·投影 A 撞本波 B 带=阶梯 A-hops-prior-B 继承待 W151 注册宇宙复核）",
     "本机 r763 席位 MSG-2026-10-06-075x 投影 W152+ A 349_004..351_003 naive/B 349_204..349_403 naive **re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·投影 A 撞本波 B 带=阶梯 A-hops-prior-B 继承待 W152 注册宇宙复核）"),
    ("T-2026-10-01-141 s1 引擎线第 140 波【bm-a 第六十六枚自有波【机面 derive：engine_owner==bm-a 行 65+本候选以 gate leg0 机证为准·同 W146/W147/W148/W149 最近自有波】。（波号=注册表 W149 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-06-070x-bma-w150-seat 先推 origin bb33022de r565 律",
     "T-2026-10-01-141 s1 引擎线第 141 波【bm-a 第六十七枚自有波【机面 derive：engine_owner==bm-a 行 66+本候选以 gate leg0 机证为准·同 W147/W148/W149/W150 最近自有波】。（波号=注册表 W150 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-06-075x-bma-w151-seat 先推 origin f8e1306c8 r565 律"),
    ("自见 W150 行并点火自烧", "自见 W151 行并点火自烧"),
    # --- S0.5 / S1 / S2 ---
    ("--prereg research/PERPETUAL_N1_W150_PREREG.md", "--prereg research/PERPETUAL_N1_W151_PREREG.md"),
    ("v2..W149 落地）的种子带扩展重测", "v2..W150 落地）的种子带扩展重测"),
    # --- S3 ---
    ("entry rng seed=**344_804+j**（法典 §4 W150 行 A=344_804..346_803·**FIRST-CLEAN past prior-wave B 阶梯第九例**：算术续带 344_604..346_603 起点即被 W149 B 带拒→1 hop 落 344_804..346_803·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场）",
     "entry rng seed=**347_004+j**（法典 §4 W151 行 A=347_004..349_003·**FIRST-CLEAN past prior-wave B 阶梯第十例**：算术续带 346_804..348_803 起点即被 W150 B 带拒→1 hop 落 347_004..349_003·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场）"),
    ("entry rng=**344_804+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**346_804+j**（法典 §4 W150 行 B=346_804..347_003·**FIRST-CLEAN past own-wave A**：B 算术续带 344_804..345_003 在注册宇宙上 CLEAN 但落在本波 A 窗内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 346_804..347_003·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 W149 席位 leg4+r761 gate leg3 W150+ 投影 re-derive-MANDATORY+同窗互斥预披露注记双面兑现收敛·ADMIT 回执在场）",
     "entry rng=**347_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**349_004+j**（法典 §4 W151 行 B=349_004..349_203·**FIRST-CLEAN past own-wave A**：B 算术续带 347_004..347_203 在注册宇宙上 CLEAN 但落在本波 A 窗内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 349_004..349_203·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 W150 席位 leg4+r762 gate leg3 W151+ 投影 re-derive-MANDATORY+同窗互斥预披露注记双面兑现收敛·ADMIT 回执在场）"),
    ("本波设计=W2..W149 逐字复用", "本波设计=W2..W150 逐字复用"),
    ("W150 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W149 在用带（**全注册单态**）",
     "W151 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W150 在用带（**全注册单态**）"),
    ("本波机验 ADMIT 回执在场=r762 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest W150 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W149 行 parity 腿【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）。",
     "本波机验 ADMIT 回执在场=r763 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest W151 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W150 行 parity 腿【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）。"),
    # --- S4 ---
    ("（起草窗实流 W1..W149 已落账 325,720 实测·derive 禁手抄）", "（起草窗实流 W1..W150 已落账 327,920 实测·derive 禁手抄）"),
    ('batch_name="PERPETUAL-N1-W150", batch_trials=2200, file_name="results/perpetual_faces/n1_w150_results.json"',
     'batch_name="PERPETUAL-N1-W151", batch_trials=2200, file_name="results/perpetual_faces/n1_w151_results.json"'),
    # --- S5 ---
    ("（起草窗实况注记：**W1..W149 N1 finalize 已全部落地**——净账本锚头 723,811=W149 finalize 落账【one-pass·bm-a r762·§7/§8 回填 r762 同窗收口】·**K=325,720 合并池**·**零在飞上游席位中**（链前置出空波）。本波 §5 预测键=**W149 finalize 实测值**【results/perpetual_faces/n1_w149_results.json·N1 面最新已落账键】。",
     "（起草窗实况注记：**W1..W150 N1 finalize 已全部落地**——净账本锚头 726,011=W150 finalize 落账【one-pass·bm-a r763·§7/§8 回填 r763 同窗收口】·**K=327,920 合并池**·**零在飞上游席位中**（链前置出空波）。本波 §5 预测键=**W150 finalize 实测值**【results/perpetual_faces/n1_w150_results.json·N1 面最新已落账键】。"),
    ("1. W150-only mu 与累计池 merged mu（W149 实测键 **−0.0927**·K=325,720 合并池·W149-only 实测 **−0.0870**）差异 **|Δ|<0.02**（W2..W149 共一百四十八面实测 mu 稳定先例·单波跨键微）。",
     "1. W151-only mu 与累计池 merged mu（W150 实测键 **−0.0928**·K=327,920 合并池·W150-only 实测 **−0.1000**）差异 **|Δ|<0.02**（W2..W150 共一百四十九面实测 mu 稳定先例·单波跨键微）。"),
    ("2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.2450**=W149 合并池实测）。",
     "2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.2450**=W150 合并池实测）。"),
    ("3. A 档 full_sharpe_p95 与 W149 A 档 p95（**0.3412** 实测锚）差 **<0.05**（门标注法 W5..W149 先例：结果知情面仅作机器断言之用·测量面非注册利益）。",
     "3. A 档 full_sharpe_p95 与 W150 A 档 p95（**0.3114** 实测锚）差 **<0.05**（门标注法 W5..W150 先例：结果知情面仅作机器断言之用·测量面非注册利益）。"),
    ("4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W149 先例·W136 +0.0000/W137 +0.0000/W138 −0.0002/W139 +0.0000/W140 +0.0000/W141 +0.0001/W143 +0.0001/W144 +0.0000/W145 +0.0000/W146 +0.0000/W147 −0.0001/W148 +0.0000/W149 **+0.0002** 如实披露；键 W149 实测 K-lift **+0.0002**【line_merged@K325,720 **1.1796**·line_pre 1.1794·n_eff 721,611；se_mu 收窄键 W140 0.000443→W141 0.000441→W142 0.000440→W143 0.000438→W144 0.000437→W145 0.000435→W146 0.000434→W147 0.000432→W148 0.000431→W149 **0.000429**】）。",
     "4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W150 先例·W136 +0.0000/W137 +0.0000/W138 −0.0002/W139 +0.0000/W140 +0.0000/W141 +0.0001/W143 +0.0001/W144 +0.0000/W145 +0.0000/W146 +0.0000/W147 −0.0001/W148 +0.0000/W149 +0.0002/W150 **+0.0000** 如实披露；键 W150 实测 K-lift **+0.0000**【line_merged@K327,920 **1.1797**·line_pre 1.1797·n_eff 723,811；se_mu 收窄键 W140 0.000443→W141 0.000441→W142 0.000440→W143 0.000438→W144 0.000437→W145 0.000435→W146 0.000434→W147 0.000432→W148 0.000431→W149 0.000429→W150 **0.000428**】）。"),
    ("5. **W151+ 投影（gate 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 346_804..348_803 **CLEAN**（hops=0）；B first-clean **347_004..347_203 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W151：W151 冻结方必须在 post-W150 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W150 B 带 346_804..347_003 注册后将拒 naive W151 A 窗**——W151 A 重 derive 同强制（越过 W150 B 带·阶梯 A-hops-prior-B 继承）；verify at W151 prereg，hop 链逐跳在 probe 回执。",
     "5. **W152+ 投影（gate 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 349_004..351_003 **CLEAN**（hops=0）；B first-clean **349_204..349_403 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W152：W152 冻结方必须在 post-W151 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W151 B 带 349_004..349_203 注册后将拒 naive W152 A 窗**——W152 A 重 derive 同强制（越过 W151 B 带·阶梯 A-hops-prior-B 继承）；verify at W152 prereg，hop 链逐跳在 probe 回执。"),
    # --- S6 ---
    ("run --shard k --of 12 --wave 150/finalize --wave 150", "run --shard k --of 12 --wave 151/finalize --wave 151"),
    ("n1_w150/ 分片计数增长", "n1_w151/ 分片计数增长"),
    ("results/p2cal_ext/n1_w150/shard-<k>-of-12.json", "results/p2cal_ext/n1_w151/shard-<k>-of-12.json"),
    ("results/perpetual_faces/n1_w150_results.json`（finalize 合并件", "results/perpetual_faces/n1_w151_results.json`（finalize 合并件"),
    ("（W1..W149 全落账）", "（W1..W150 全落账）"),
    ("engine_owner==bm-a 65 行注册 + 本候选——以 gate leg0 机证为准·同 W146/W147/W148/W149 最近自有波", "engine_owner==bm-a 66 行注册 + 本候选——以 gate leg0 机证为准·同 W147/W148/W149/W150 最近自有波"),
]

inter = rep(src, pairs, "prereg-xform")

# --- sec7/sec8 span replacement: r763 same-window backfilled blocks -> placeholders
i7 = inter.find("## §7 跑后实证。【finalize 收口机械回填·bm-a r763")
i8 = inter.find("## §8 批后复盘。【finalize 同窗回填·bm-a r763")
ifin = inter.find("- **跑前冻结=本件 commit**")
assert i7 > 0 and i8 > i7 and ifin > i8, f"sec7/8 span anchors missing: {i7},{i8},{ifin}"
assert inter.count("## §7 跑后实证。【finalize 收口机械回填·bm-a r763") == 1
assert inter.count("## §8 批后复盘。【finalize 同窗回填·bm-a r763") == 1
sec7_block, sec8_block = inter[i7:i8], inter[i8:ifin]
assert "n1_w150_results.json 冻结实测键" in sec7_block and "0.3114" in sec7_block \
    and "mu_delta_w150_vs_w149ext" in sec7_block, "sec7 backfill face drift"
assert "W151+ 投影承接" in sec8_block and "本批无新宝藏" in sec8_block, "sec8 backfill face drift"
ph7 = ("## §7 跑后实证。【finalize 收口机械回填·占位——跑前为空】\n"
       "- （占位：12/12 分片落地后 finalize one-pass 机械回填·回填限本节与 §8·judged 断言照 W150 例。）\n\n")
ph8 = ("## §8 批后复盘。【finalize 同窗回填·占位】\n"
       "- （占位：设计复用面+宝藏捕获问+W152+ 投影承接三行照 W150 例回填。）\n\n")
out = inter[:i7] + ph7 + ph8 + inter[ifin:]
assert out.count("占位：12/12") == 1 and out.count("占位：设计复用面") == 1, "placeholder splice drift"
assert "同窗即回填（r762 窗先例延续" not in out, "backfilled sec7 residue"

# --- two-form checklist (bare wave number + lowercase tokens residue) ---
assert out.count("波号 150") == 0, "bare wave number residue (r754 law)"
# The ONE legitimate n1_w150 occurrence = sec5 prediction-key anchor
assert out.count("n1_w150") == 1, "n1_w150 must appear exactly once (sec5 prior-wave key)"
assert out.count("results/perpetual_faces/n1_w150_results.json·N1 面最新已落账键") == 1, "sec5 anchor context"
assert out.count("n1w150") == 0, "lowercase entry token residue (r754 law)"
assert out.count("PERPETUAL-N1-W150") == 0, "batch name residue"
assert out.count("bb33022de") == 0, "stale seat sha residue"
assert out.count("860d529f3") == 0, "stale self-ack sha residue"
# W150 A-band must be fully gone; W150 B-band remains exactly once as the
# prior-wave geometry cite in the L5 derivation narrative
assert out.count("344_804..346_803") == 0, "stale W150 A-band residue"
assert out.count("346_804..347_003") == 1 and \
    out.count("被已注册 W150 B 带 346_804..347_003 **拒**") == 1, \
    "W150 B-band must appear exactly once as prior-wave cite"
assert "波号 151=注册表 W150 行后首个自由号" in out and "347_004..349_003" in out \
    and "349_004..349_203" in out and "PERPETUAL-N1-W151" in out, "new W151 facts missing"

io.open(r"research/PERPETUAL_N1_W151_PREREG.md", "w", encoding="utf-8", newline="\n").write(out)
print("W151 prereg written:", len(out), "chars |", len(pairs), "needle pairs, all count==1 |",
      "sec7/8 span-replaced", len(sec7_block) + len(sec8_block), "->", len(ph7) + len(ph8), "bytes")
