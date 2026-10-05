# -*- coding: utf-8 -*-
"""r755 bm-a W146 per-wave prereg xform: research/PERPETUAL_N1_W145_PREREG.md
-> research/PERPETUAL_N1_W146_PREREG.md. Needle-asserted (r745 extract-vs-insert
law); r754 two-form checklist enforced at the tail (bare wave number 波号 145
and lowercase n1_w145/n1w145 tokens must be ZERO after xform).
W146 facts: A=336_004..338_003 (staircase fifth instance, hops=1) +
B=338_004..338_203 (own-A mutual exclusion, hops=1); seat c8183f342 ->
delivery 8d4248daf; W145 finalize = bm-a r755 one-pass, ledger head 715,011,
K=316,920 merged pool; W145-only mu -0.0913 / merged mu -0.0929 /
sigma 0.2450 / A p95 0.3095 / K-lift +0.0000 @line 1.1789 / se_mu 0.000435
(all from results/perpetual_faces/n1_w145_results.json measured keys)."""
import io


def rep(src, pairs, tag):
    # r755 dead-tail patch: pairs authored as 2-tuples before expect counts were
    # added; measured 2026-10-06 this session: every needle count==1 at its
    # position in the sequence (r735 pre-replacement-count law), so assert
    # count==1 per needle keeps the fail-closed contract.
    for i, p in enumerate(pairs):
        assert len(p) == 2, f"{tag}: pair {i} arity={len(p)}"
        old, new = p
        n = src.count(old)
        assert n == 1, f"{tag}: needle {i} count={n} expect=1: {old[:70]!r}"
        src = src.replace(old, new)
    return src


src = io.open(r"research\PERPETUAL_N1_W145_PREREG.md", encoding="utf-8").read()

pairs = [
    # --- L1 title ---
    ("# PERPETUAL-N1-W145 预注册 · N1 nulls-deepening 泵第 143 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 134+本候选=bm-a 第六十一枚自有波【r754】）",
     "# PERPETUAL-N1-W146 预注册 · N1 nulls-deepening 泵第 144 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 135+本候选=bm-a 第六十二枚自有波【r755】）"),
    # --- L3 seat/vacancy/list cluster ---
    ("**波号 145=注册表 W144 行后首个自由号**【本冻结窗 fetch 实核表尾时 W145 号位空档",
     "**波号 146=注册表 W145 行后首个自由号**【本冻结窗 fetch 实核表尾时 W146 号位空档"),
    ("全 inbox/processed/ W145 席位零外机命中（本机席位公示=MSG-2026-10-06-023x-bma-w145-seat 已推 origin 55c2a1715 先于本冻结【r565 律·推送窗=two-hop merge delivery 55c2a1715→d5fdbb317",
     "全 inbox/processed/ W146 席位零外机命中（本机席位公示=MSG-2026-10-06-033x-bma-w146-seat 已推 origin c8183f342 先于本冻结【r565 律·推送窗=two-hop merge delivery c8183f342→8d4248daf"),
    ("W144=bm-a r752 freeze（ff6d2f918·表尾）；**均已注册**（表尾 W144 行）。W145=本波 skip-past-published 链面零适用（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r753bma_w145_band_gate.py rc0 实跑）",
     "W144=bm-a r752 freeze（ff6d2f918）；W145=bm-a r754 freeze（98c661f8f·表尾）；**均已注册**（表尾 W145 行）。W146=本波 skip-past-published 链面零适用（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r755bma_w146_band_gate.py rc0 实跑）"),
    ("pre-seat 机证=results/_r753bma_w145_probe.py rc0（ADMIT-derive·回执 results/_r753bma_w145_probe_receipt.json",
     "pre-seat 机证=results/_r755bma_w146_probe.py rc0（ADMIT-derive·回执 results/_r755bma_w146_probe_receipt.json"),
    ("（A 333_804..335_803 hops 1·B 335_804..336_003 hops 1——**A=FIRST-CLEAN past prior-wave B 阶梯第四例（A-hops-prior-B·E36 卡）·B=FIRST-CLEAN past own-wave A（W141 先例 leg2 律）**",
     "（A 336_004..338_003 hops 1·B 338_004..338_203 hops 1——**A=FIRST-CLEAN past prior-wave B 阶梯第五例（A-hops-prior-B·E36 卡）·B=FIRST-CLEAN past own-wave A（W141 先例 leg2 律）**"),
    ("**席位推送窗实录（r753 窗口实况）**：席位+probe 回执单 commit 推送撞 origin 前进（r524 behind-signal·非快进拒）→ merge-mode 收口 two-hop delivery 送达 **55c2a1715 → d5fdbb317**（零 --no-verify）。> **序数机面锚注记**：本波 ordinal=第一百三十五引擎波·bm-a 第六十一枚自有波【机面 derive：engine_owner==bm-a 行 60+本候选以 gate leg0 机证为准】。",
     "**席位推送窗实录（r755 窗口实况）**：席位+probe 回执+W145 finalize 产物单 commit 推送撞 origin 前进（r524 behind-signal·非快进拒）→ merge-mode 收口 two-hop delivery 送达 **c8183f342 → 8d4248daf**（零 --no-verify）。> **序数机面锚注记**：本波 ordinal=第一百三十六引擎波·bm-a 第六十二枚自有波【机面 derive：engine_owner==bm-a 行 61+本候选以 gate leg0 机证为准】。"),
    # --- L5 band block ---
    ("ADMIT 回执=results/_r753bma_w145_band_gate.py 单态门全腿实跑·pre-seat probe results/_r753bma_w145_probe.py 先跑",
     "ADMIT 回执=results/_r755bma_w146_band_gate.py 单态门全腿实跑·pre-seat probe results/_r755bma_w146_probe.py 先跑"),
    ("本波 **A-ext seed=333_804..335_803**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第四例**：A 面算术继续带 333_604..335_603 在其起点即被已注册 W144 B 带 333_604..333_803 **拒**（r752 W145 gate 尾投影注记所预言）",
     "本波 **A-ext seed=336_004..338_003**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第五例**：A 面算术继续带 335_804..337_803 在其起点即被已注册 W145 B 带 335_804..336_003 **拒**（r753 W146 gate 尾投影注记所预言）"),
    ("→ 诚实前向走 **1 hop** 落 **333_804..335_803**·**A base==前波 B 尾+1（333_803+1）机检关系**=**A-hops-prior-B 阶梯几何第二例（E36 卡）**",
     "→ 诚实前向走 **1 hop** 落 **336_004..338_003**·**A base==前波 B 尾+1（336_003+1）机检关系**=**A-hops-prior-B 阶梯几何第五例（E36 卡·W145 预注册内嵌陈旧「第二例」计数如实归正）**"),
    ("；**B-ext exit seed=335_804..336_003**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 333_804..334_003 在注册宇宙上 CLEAN 但**落在本波 A 窗内**",
     "；**B-ext exit seed=338_004..338_203**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 336_004..336_203 在注册宇宙上 CLEAN 但**落在本波 A 窗内**"),
    ("→ B 带本波 A 窗保留走 **1 hop** 落 **335_804..336_003**·**B base==本波 A 尾+1（335_803+1）机检关系**",
     "→ B 带本波 A 窗保留走 **1 hop** 落 **338_004..338_203**·**B base==本波 A 尾+1（338_003+1）机检关系**"),
    ("**r752 W145 gate 尾投影 re-derive-MANDATORY 注记双面兑现**：投影预言 W145 须在 post-W144 注册宇宙重 derive 且 derive B 时预留本波 A 窗",
     "**r753 W146 gate 尾投影 re-derive-MANDATORY 注记双面兑现**：投影预言 W146 须在 post-W145 注册宇宙重 derive 且 derive B 时预留本波 A 窗"),
    ("R250：W145 带从未指派·测量面零结果可锁。扫描面=pre-W145 全一百四十二行注册 N1 带表（表尾 W144 行·leg0 机证 142 行）",
     "R250：W146 带从未指派·测量面零结果可锁。扫描面=pre-W146 全一百四十三行注册 N1 带表（表尾 W145 行·leg0 机证 143 行）"),
    # --- L9 reuse domain ---
    ("（W2..W144 落地 runner 的 wave 参数化复用", "（W2..W145 落地 runner 的 wave 参数化复用"),
    # --- §0 ---
    ("- 批名=**PERPETUAL-N1-W145**。N=", "- 批名=**PERPETUAL-N1-W146**。N="),
    ("起稿窗实况：**W1..W144 N1 finalize 已全部落地**【W144 finalize one-pass bm-a r753 247e53cf8·§7/§8 回填同 commit 在场】——净账本锚头 **712,811**（W144 finalize 落账【one-pass·K=314,720 合并池·voids LOWAMP-P1/P2】）",
     "起稿窗实况：**W1..W145 N1 finalize 已全部落地**【W145 finalize one-pass bm-a r755·§7/§8 回填同 commit 在场】——净账本锚头 **715,011**（W145 finalize 落账【one-pass·K=316,920 合并池·voids LOWAMP-P1/P2】）"),
    ("累计 null 池=314,720+2,200（本波）=**316,920 投影**", "累计 null 池=316,920+2,200（本波）=**319,120 投影**"),
    ("本机 r753 席位 MSG-2026-10-06-023x 投影 W145+ A 333_604..335_603 naive/B **re-derive 强制注记+同窗互斥预披露**（投影 A 落 W144 B 带内·B 落本波 A 窗内）",
     "本机 r755 席位 MSG-2026-10-06-033x 投影 W146+ A 335_804..337_803 naive/B **re-derive 强制注记+同窗互斥预披露**（投影 A 落 W145 B 带内·B 落本波 A 窗内）"),
    ("T-2026-10-01-141 s1 引擎线第 135 波【bm-a 第六十一枚自有波【机面 derive：engine_owner==bm-a 行 60+本候选以 gate leg0 机证为准·同 W141/W142/W143/W144 最近自有波】。（波号=注册表 W144 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-06-023x-bma-w145-seat 先推 origin 55c2a1715 r565 律",
     "T-2026-10-01-141 s1 引擎线第 136 波【bm-a 第六十二枚自有波【机面 derive：engine_owner==bm-a 行 61+本候选以 gate leg0 机证为准·同 W142/W143/W144/W145 最近自有波】。（波号=注册表 W145 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-06-033x-bma-w146-seat 先推 origin c8183f342 r565 律"),
    ("自见 W145 行并点火自烧", "自见 W146 行并点火自烧"),
    # --- §0.5 / §1 / §2 ---
    ("--prereg research/PERPETUAL_N1_W145_PREREG.md", "--prereg research/PERPETUAL_N1_W146_PREREG.md"),
    ("v2..W144 落地）的种子带扩展重测", "v2..W145 落地）的种子带扩展重测"),
    # --- §3 ---
    ("entry rng seed=**333_804+j**（法典 §4 W145 行 A=333_804..335_803·**FIRST-CLEAN past prior-wave B 阶梯第四例**：算术续带 333_604..335_603 起点即被 W144 B 带拒→1 hop 落 333_804..335_803·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场）",
     "entry rng seed=**336_004+j**（法典 §4 W146 行 A=336_004..338_003·**FIRST-CLEAN past prior-wave B 阶梯第五例**：算术续带 335_804..337_803 起点即被 W145 B 带拒→1 hop 落 336_004..338_003·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场）"),
    ("entry rng=**333_804+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**335_804+j**（法典 §4 W145 行 B=335_804..336_003·**FIRST-CLEAN past own-wave A**：B 算术续带 333_804..334_003 在注册宇宙上 CLEAN 但落在本波 A 窗内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 335_804..336_003·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 r753 席位 MSG W145+ 投影 re-derive-MANDATORY+同窗互斥预披露注记双面兑现收敛·ADMIT 回执在场）",
     "entry rng=**336_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**338_004+j**（法典 §4 W146 行 B=338_004..338_203·**FIRST-CLEAN past own-wave A**：B 算术续带 336_004..336_203 在注册宇宙上 CLEAN 但落在本波 A 窗内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 338_004..338_203·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 r753 W145 gate leg3 W146+ 投影 re-derive-MANDATORY+同窗互斥预披露注记双面兑现收敛·ADMIT 回执在场）"),
    ("本波设计=W2..W144 逐字复用", "本波设计=W2..W145 逐字复用"),
    ("W145 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W144 在用带（**全注册单态**）",
     "W146 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W145 在用带（**全注册单态**）"),
    ("本波机验 ADMIT 回执在场=r753→r754 bm-a 冻结窗（r753 窗死尾·r754 续成收口——pre-seat probe 先跑·双窗 derive 恒等）（pre-seat probe 先跑·双窗 derive 恒等）；selftest W145 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W144 行 parity 腿【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）。",
     "本波机验 ADMIT 回执在场=r755 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest W146 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W145 行 parity 腿【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）。"),
    # --- §4 ---
    ("（起草窗实流 W1..W144 已落账 314,720 实测·derive 禁手抄）", "（起草窗实流 W1..W145 已落账 316,920 实测·derive 禁手抄）"),
    ('batch_name="PERPETUAL-N1-W145", batch_trials=2200, file_name="results/perpetual_faces/n1_w145_results.json"',
     'batch_name="PERPETUAL-N1-W146", batch_trials=2200, file_name="results/perpetual_faces/n1_w146_results.json"'),
    # --- §5 ---
    ("（起草窗实况注记：**W1..W144 N1 finalize 已全部落地**——净账本锚头 712,811=W144 finalize 落账【one-pass·bm-a r753 247e53cf8·§7/§8 回填同 commit 在场】·**K=314,720 合并池**·**零在飞上游席位中**（链前置出空波）。本波 §5 预测键=**W144 finalize 实测值**【results/perpetual_faces/n1_w144_results.json·N1 面最新已落账键】。",
     "（起草窗实况注记：**W1..W145 N1 finalize 已全部落地**——净账本锚头 715,011=W145 finalize 落账【one-pass·bm-a r755·§7/§8 回填同 commit 在场】·**K=316,920 合并池**·**零在飞上游席位中**（链前置出空波）。本波 §5 预测键=**W145 finalize 实测值**【results/perpetual_faces/n1_w145_results.json·N1 面最新已落账键】。"),
    ("1. W145-only mu 与累计池 merged mu（W144 实测键 **−0.0929**·K=314,720 合并池·W144-only 实测 **−0.1049**）差异 **|Δ|<0.02**（W2..W144 共一百四十三面实测 mu 稳定先例·单波跨键微）。",
     "1. W146-only mu 与累计池 merged mu（W145 实测键 **−0.0929**·K=316,920 合并池·W145-only 实测 **−0.0913**）差异 **|Δ|<0.02**（W2..W145 共一百四十四面实测 mu 稳定先例·单波跨键微）。"),
    ("2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.2450**=W144 合并池实测）。",
     "2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.2450**=W145 合并池实测）。"),
    ("3. A 档 full_sharpe_p95 与 W144 A 档 p95（**0.3029** 实测锚）差 **<0.05**（门标注法 W5..W144 先例：结果知情面仅作机器断言之用·测量面非注册利益）。",
     "3. A 档 full_sharpe_p95 与 W145 A 档 p95（**0.3095** 实测锚）差 **<0.05**（门标注法 W5..W145 先例：结果知情面仅作机器断言之用·测量面非注册利益）。"),
    ("4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W144 先例·W136 +0.0000/W137 +0.0000/W138 −0.0002/W139 +0.0000/W140 +0.0000/W141 +0.0001/W143 +0.0001/W144 **+0.0000** 如实披露；键 W144 实测 K-lift **+0.0000**【line_merged@K314,720 **1.1788**·line_pre 1.1788·n_eff 710,611；se_mu 收窄键 W140 0.000443→W141 0.000441→W142 0.000440→W143 0.000438→W144 **0.000437**】）。",
     "4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W145 先例·W136 +0.0000/W137 +0.0000/W138 −0.0002/W139 +0.0000/W140 +0.0000/W141 +0.0001/W143 +0.0001/W144 +0.0000/W145 **+0.0000** 如实披露；键 W145 实测 K-lift **+0.0000**【line_merged@K316,920 **1.1789**·line_pre 1.1789·n_eff 712,811；se_mu 收窄键 W140 0.000443→W141 0.000441→W142 0.000440→W143 0.000438→W144 0.000437→W145 **0.000435**】）。"),
    ("5. **W146+ 投影（gate 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 335_804..337_803 **CLEAN**（hops=0）；B first-clean **336_004..336_203 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W146：W146 冻结方必须在 post-W145 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W145 B 带 335_804..336_003 注册后将拒 naive W146 A 窗**——W146 A 重 derive 同强制（越过 W145 B 带·阶梯 A-hops-prior-B 继承）；verify at W146 prereg，hop 链逐跳在 probe 回执。",
     "5. **W147+ 投影（gate 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 338_004..340_003 **CLEAN**（hops=0）；B first-clean **338_204..338_403 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W147：W147 冻结方必须在 post-W146 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W146 B 带 338_004..338_203 注册后将拒 naive W147 A 窗**——W147 A 重 derive 同强制（越过 W146 B 带·阶梯 A-hops-prior-B 继承）；verify at W147 prereg，hop 链逐跳在 probe 回执。"),
    # --- §6 ---
    ("run --shard k --of 12 --wave 145/finalize --wave 145", "run --shard k --of 12 --wave 146/finalize --wave 146"),
    ("n1_w145/ 分片计数增长", "n1_w146/ 分片计数增长"),
    ("results/p2cal_ext/n1_w145/shard-<k>-of-12.json", "results/p2cal_ext/n1_w146/shard-<k>-of-12.json"),
    ("results/perpetual_faces/n1_w145_results.json`（finalize 合并件", "results/perpetual_faces/n1_w146_results.json`（finalize 合并件"),
    ("（W1..W144 全落账）", "（W1..W145 全落账）"),
    ("engine_owner==bm-a 60 行注册 + 本候选——以 gate leg0 机证为准·同 W141/W142/W143/W144 最近自有波", "engine_owner==bm-a 61 行注册 + 本候选——以 gate leg0 机证为准·同 W142/W143/W144/W145 最近自有波"),
    # --- §7/§8 ---
    ("judged 断言照 W144 例", "judged 断言照 W145 例"),
    ("W146+ 投影承接三行照 W144 例回填", "W147+ 投影承接三行照 W145 例回填"),
]

out = rep(src, pairs, "prereg-xform")

# --- r754 two-form checklist (bare wave number + lowercase tokens must be zero) ---
assert out.count("波号 145") == 0, "bare wave number residue (r754 law)"
# r755 dead-tail patch: the ONE legitimate n1_w145 occurrence = §5 prediction-key
# anchor (prior-wave measured values file; needle-30 new text by design — W146
# §5 keys off W145 as latest finalized). r547 law: pin owner context, not bare
# token; all own-wave n1_w145 forms (shard dir, ignition counter, file_name)
# were replaced by needles 29/37/38/39 above.
assert out.count("n1_w145") == 1, "n1_w145 must appear exactly once (§5 prior-wave key)"
assert out.count("results/perpetual_faces/n1_w145_results.json·N1 面最新已落账键") == 1, "§5 anchor context"
assert out.count("n1w145") == 0, "lowercase entry token residue (r754 law)"
assert out.count("PERPETUAL-N1-W145") == 0, "batch name residue"
assert out.count("55c2a1715") == 0 and out.count("d5fdbb317") == 0, "stale seat sha residue"
# r755 dead-tail patch: W145 A-band must be fully gone; W145 B-band remains
# exactly once as the prior-wave geometry cite in the L5 derivation narrative
# ("rejected by registered W145 B band") — needle-08 new text by design.
assert out.count("333_804..335_803") == 0, "stale W145 A-band residue"
assert out.count("335_804..336_003") == 1 and \
    out.count("被已注册 W145 B 带 335_804..336_003 **拒**") == 1, \
    "W145 B-band must appear exactly once as prior-wave cite"
# W145 mentions remain legitimately as PRIOR-wave refs; sanity: new facts present
assert "波号 146=注册表 W145 行后首个自由号" in out and "336_004..338_003" in out \
    and "338_004..338_203" in out and "PERPETUAL-N1-W146" in out, "new W146 facts missing"

io.open(r"research\PERPETUAL_N1_W146_PREREG.md", "w", encoding="utf-8", newline="\n").write(out)
print("W146 prereg written:", len(out), "bytes |", len(pairs), "needle pairs, all count==expect")
