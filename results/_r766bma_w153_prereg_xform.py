# -*- coding: utf-8 -*-
"""r766 bm-a W153 per-wave prereg xform: research/PERPETUAL_N1_W152_PREREG.md
-> research/PERPETUAL_N1_W153_PREREG.md. Needle-asserted (r745 extract-vs-insert
law, every needle count==1 measured); two-form checklist enforced at the
tail (bare wave number and lowercase n1_w152/n1w152 tokens must be
ZERO-residue after xform, except the ONE legitimate sec5 prior-wave key
anchor, r547 owner-context law). sec7/sec8 span-replaced from the r765
same-window backfilled blocks to W153 placeholders (boundary-anchored,
zero byte-drift).
W153 facts: A=351_404..353_403 (staircase twelfth instance E36, hops=1) +
B=353_404..353_603 (own-A mutual exclusion, hops=1); seat
MSG-2026-10-06-084x-bma-w153-seat -> origin 3ae290395 (r766 pre-seat push;
delivery window absorbed a behind-3 bm-c r607 peer wave via rebase + own
daemon churn-absorb precede, zero --no-verify; same-window self-ack
inbox->processed move r766); band gate ADMIT
receipt results/_r766bma_w153_band_gate.json rc0; pre-seat probe r766 receipt.
W152 finalize = bm-a r765 one-pass (sec7/sec8 backfilled same-window),
ledger head 730,411, K=332,320 merged pool;
W152-only mu -0.094571 / merged mu -0.0928 / sigma 0.2450 / A p95 0.3366 /
K-lift +0.0002 @line 1.1801->1.1803 / se_mu 0.000425 / mu_delta_w152_vs_w151ext
-0.00244
(all from results/perpetual_faces/n1_w152_results.json measured keys)."""
import io


def rep(src, pairs, tag):
    for i, p in enumerate(pairs):
        assert len(p) == 2, f"{tag}: pair {i} arity={len(p)}"
        old, new = p
        n = src.count(old)
        assert n == 1, f"{tag}: needle {i} count={n} expect=1: {old[:70]!r}"
        src = src.replace(old, new)
    return src


src = io.open(r"research/PERPETUAL_N1_W152_PREREG.md", encoding="utf-8").read()

pairs = [
    # --- L1 title ---
    ("# PERPETUAL-N1-W152 预注册 · N1 nulls-deepening 泵第 150 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 141+本候选=bm-a 第六十八枚自有波【r764】）",
     "# PERPETUAL-N1-W153 预注册 · N1 nulls-deepening 泵第 151 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 142+本候选=bm-a 第六十九枚自有波【r766】）"),
    # --- L3 seat/vacancy/list cluster ---
    ("**波号 152=注册表 W151 行后首个自由号**【本冻结窗 fetch 实核表尾时 W152 号位空档",
     "**波号 153=注册表 W152 行后首个自由号**【本冻结窗 fetch 实核表尾时 W153 号位空档"),
    ("全 inbox/processed/ W152 席位零外机命中（本机席位公示=MSG-2026-10-06-080x-bma-w152-seat 已推 origin 6a4081c01 先于本冻结【r565 律·推送窗=direct delivery 6a4081c01（r764 pre-seat push·GitHub SSH 瞬态+behind-3 pre-push 爪拦 r759 幻影删除面 merge 吸收后送达·零 --no-verify）+同窗 self-ack inbox→processed 移位 r764】",
     "全 inbox/processed/ W153 席位零外机命中（本机席位公示=MSG-2026-10-06-084x-bma-w153-seat 已推 origin 3ae290395 先于本冻结【r565 律·推送窗=direct delivery 3ae290395（r766 pre-seat push·behind-3 bm-c r607 peer wave rebase 吸收+own daemon churn-absorb 前置后送达·零 --no-verify）+同窗 self-ack inbox→processed 移位 r766】"),
    ("W148=bm-a r759 freeze（92c5ab03c）；W149=bm-a r761 freeze（0cef02a00）；W150=bm-a r762 freeze（fedebeb32）；W151=bm-a r763 freeze（bd4cd7159·表尾）；**均已注册**（表尾 W151 行）。W152=本波 skip-past-published 链面零适用（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r764bma_w152_band_gate.json rc0 实跑）",
     "W148=bm-a r759 freeze（92c5ab03c）；W149=bm-a r761 freeze（0cef02a00）；W150=bm-a r762 freeze（fedebeb32）；W151=bm-a r763 freeze（bd4cd7159）；W152=bm-a r764 freeze（520eb01ca·表尾）；**均已注册**（表尾 W152 行）。W153=本波 skip-past-published 链面零适用（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r766bma_w153_band_gate.json rc0 实跑）"),
    ("pre-seat 机证=results/_r764bma_w152_probe.py rc0（ADMIT-derive·回执 results/_r764bma_w152_probe_receipt.json·**A 首窗拒+同窗互斥面机证在内**）；冻结窗 gate 重跑 derive 逐位恒等（A 349_204..351_203 hops 1·B 351_204..351_403 hops 1——**A=FIRST-CLEAN past prior-wave B 阶梯第十一例（A-hops-prior-B·E36 卡）·B=FIRST-CLEAN past own-wave A（W141 先例 leg2 律）**",
     "pre-seat 机证=results/_r766bma_w153_probe.py rc0（ADMIT-derive·回执 results/_r766bma_w153_probe_receipt.json·**A 首窗拒+同窗互斥面机证在内**）；冻结窗 gate 重跑 derive 逐位恒等（A 351_404..353_403 hops 1·B 353_404..353_603 hops 1——**A=FIRST-CLEAN past prior-wave B 阶梯第十二例（A-hops-prior-B·E36 卡）·B=FIRST-CLEAN past own-wave A（W141 先例 leg2 律）**"),
    ("**席位推送窗实录（r764 窗口实况）**：席位+probe 回执随 W151 finalize 收口窗单 commit 推送 origin 送达 **6a4081c01**（推送窗 GitHub SSH 瞬态两连拒后自愈+behind-3 pre-push 爪拦 r759 幻影删除面 merge 吸收后快进送达·零 --no-verify；同窗 self-ack inbox→processed 移位 r764 再推送达）。> **序数机面锚注记**：本波 ordinal=第一百四十二引擎波·bm-a 第六十八枚自有波【机面 derive：engine_owner==bm-a 行 67+本候选以 gate leg0 机证为准】。",
     "**席位推送窗实录（r766 窗口实况）**：席位+probe 回执单 commit 推送 origin 送达 **3ae290395**（推送窗 behind-3 bm-c r607 peer wave 先 rebase 吸收+own daemon churn-absorb 前置后快进送达·零 --no-verify；同窗 self-ack inbox→processed 移位 r766 再推送达）。> **序数机面锚注记**：本波 ordinal=第一百四十三引擎波·bm-a 第六十九枚自有波【机面 derive：engine_owner==bm-a 行 68+本候选以 gate leg0 机证为准】。"),
    # --- L5 band block ---
    ("**带位（r535 机阀 derive 律·ADMIT 回执=results/_r764bma_w152_band_gate.json 单态门全腿实跑·pre-seat probe results/_r764bma_w152_probe.py 先跑·双窗 derive 恒等）**：本波 **A-ext seed=349_204..351_203**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第十一例**：A 面算术继续带 349_004..351_003 在其起点即被已注册 W151 B 带 349_004..349_203 **拒**（W151 席位 leg4+r763 gate leg3 双投影注记所预言）",
     "**带位（r535 机阀 derive 律·ADMIT 回执=results/_r766bma_w153_band_gate.json 单态门全腿实跑·pre-seat probe results/_r766bma_w153_probe.py 先跑·双窗 derive 恒等）**：本波 **A-ext seed=351_404..353_403**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第十二例**：A 面算术继续带 351_204..353_203 在其起点即被已注册 W152 B 带 351_204..351_403 **拒**（W152 席位 leg4+r764 gate leg3+r765 §8 承接三投影注记所预言）"),
    ("→ 诚实前向走 **1 hop** 落 **349_204..351_203**·**A base==前波 B 尾+1（349_203+1）机检关系**=**A-hops-prior-B 阶梯几何第十一例（E36 卡）**·非轮转 r587 前向单调断言在走册）；**B-ext exit seed=351_204..351_403**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 349_204..349_403 在注册宇宙上 CLEAN 但**落在本波 A 窗内**",
     "→ 诚实前向走 **1 hop** 落 **351_404..353_403**·**A base==前波 B 尾+1（351_403+1）机检关系**=**A-hops-prior-B 阶梯几何第十二例（E36 卡）**·非轮转 r587 前向单调断言在走册）；**B-ext exit seed=353_404..353_603**（**B 面=FIRST-CLEAN past own-wave A**：B 面算术继续带 351_404..351_603 在注册宇宙上 CLEAN 但**落在本波 A 窗内**"),
    ("→ B 带本波 A 窗保留走 **1 hop** 落 **351_204..351_403**·**B base==本波 A 尾+1（351_203+1）机检关系**·hop 链逐跳在 probe 回执；**W151 席位 leg4+r763 gate leg3 re-derive-MANDATORY 注记双面兑现**：投影预言 W152 须在 post-W151 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）。R250：W152 带从未指派·测量面零结果可锁。扫描面=pre-W152 全一百四十九行注册 N1 带表（表尾 W151 行·leg0 机证 149 行）；v1 ext；v1 在用带；SEED_REGISTRY 全键 188 值",
     "→ B 带本波 A 窗保留走 **1 hop** 落 **353_404..353_603**·**B base==本波 A 尾+1（353_403+1）机检关系**·hop 链逐跳在 probe 回执；**W152 席位 leg4+r764 gate leg3+r765 §8 承接 re-derive-MANDATORY 注记三面兑现**：投影预言 W153 须在 post-W152 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）。R250：W153 带从未指派·测量面零结果可锁。扫描面=pre-W153 全一百五十行注册 N1 带表（表尾 W152 行·leg0 机证 150 行）；v1 ext；v1 在用带；SEED_REGISTRY 全键 188 值"),
    # --- L9 reuse domain ---
    ("（W2..W151 落地 runner 的 wave 参数化复用", "（W2..W152 落地 runner 的 wave 参数化复用"),
    # --- S0 ---
    ("- 批名=**PERPETUAL-N1-W152**。N=", "- 批名=**PERPETUAL-N1-W153**。N="),
    ("起稿窗实况：**W1..W151 N1 finalize 已全部落地**【W151 finalize one-pass bm-a r764·§7/§8 回填 r764 同窗收口】——净账本锚头 **728,211**（W151 finalize 落账【one-pass·K=330,120 合并池·voids LOWAMP-P1/P2】）",
     "起稿窗实况：**W1..W152 N1 finalize 已全部落地**【W152 finalize one-pass bm-a r765·§7/§8 回填 r765 同窗收口】——净账本锚头 **730,411**（W152 finalize 落账【one-pass·K=332,320 合并池·voids LOWAMP-P1/P2】）"),
    ("累计 null 池=330,120+2,200（本波）=**332,320 投影**", "累计 null 池=332,320+2,200（本波）=**334,520 投影**"),
    ("本机 r764 席位 MSG-2026-10-06-080x 投影 W153+ A 351_204..353_203 naive/B 351_404..351_603 naive **re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·投影 A 撞本波 B 带=阶梯 A-hops-prior-B 继承待 W153 注册宇宙复核）",
     "本机 r766 席位 MSG-2026-10-06-084x 投影 W154+ A 353_404..355_403 naive/B 353_604..353_803 naive **re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·投影 A 撞本波 B 带=阶梯 A-hops-prior-B 继承待 W154 注册宇宙复核）"),
    ("T-2026-10-01-141 s1 引擎线第 142 波【bm-a 第六十八枚自有波【机面 derive：engine_owner==bm-a 行 67+本候选以 gate leg0 机证为准·同 W148/W149/W150/W151 最近自有波】。（波号=注册表 W151 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-06-080x-bma-w152-seat 先推 origin 6a4081c01 r565 律",
     "T-2026-10-01-141 s1 引擎线第 143 波【bm-a 第六十九枚自有波【机面 derive：engine_owner==bm-a 行 68+本候选以 gate leg0 机证为准·同 W149/W150/W151/W152 最近自有波】。（波号=注册表 W152 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-06-084x-bma-w153-seat 先推 origin 3ae290395 r565 律"),
    ("自见 W152 行并点火自烧", "自见 W153 行并点火自烧"),
    # --- S0.5 / S1 / S2 ---
    ("--prereg research/PERPETUAL_N1_W152_PREREG.md", "--prereg research/PERPETUAL_N1_W153_PREREG.md"),
    ("v2..W151 落地）的种子带扩展重测", "v2..W152 落地）的种子带扩展重测"),
    # --- S3 ---
    ("entry rng seed=**349_204+j**（法典 §4 W152 行 A=349_204..351_203·**FIRST-CLEAN past prior-wave B 阶梯第十一例**：算术续带 349_004..351_003 起点即被 W151 B 带拒→1 hop 落 349_204..351_203·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场）",
     "entry rng seed=**351_404+j**（法典 §4 W153 行 A=351_404..353_403·**FIRST-CLEAN past prior-wave B 阶梯第十二例**：算术续带 351_204..353_203 起点即被 W152 B 带拒→1 hop 落 351_404..353_403·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场）"),
    ("entry rng=**349_204+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**351_204+j**（法典 §4 W152 行 B=351_204..351_403·**FIRST-CLEAN past own-wave A**：B 算术续带 349_204..349_403 在注册宇宙上 CLEAN 但落在本波 A 窗内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 351_204..351_403·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 W151 席位 leg4+r763 gate leg3 W152+ 投影 re-derive-MANDATORY+同窗互斥预披露注记双面兑现收敛·ADMIT 回执在场）",
     "entry rng=**351_404+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**353_404+j**（法典 §4 W153 行 B=353_404..353_603·**FIRST-CLEAN past own-wave A**：B 算术续带 351_404..351_603 在注册宇宙上 CLEAN 但落在本波 A 窗内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 353_404..353_603·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·hop 链逐跳在 probe 回执·与 W152 席位 leg4+r764 gate leg3+r765 §8 承接 W153+ 投影 re-derive-MANDATORY+同窗互斥预披露注记三面兑现收敛·ADMIT 回执在场）"),
    ("本波设计=W2..W151 逐字复用", "本波设计=W2..W152 逐字复用"),
    ("W152 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W151 在用带（**全注册单态**）",
     "W153 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W152 在用带（**全注册单态**）"),
    ("本波机验 ADMIT 回执在场=r764 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest W152 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W151 行 parity 腿【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）。",
     "本波机验 ADMIT 回执在场=r766 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）；selftest W153 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W152 行 parity 腿【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）。"),
    # --- S4 ---
    ("（起草窗实流 W1..W151 已落账 330,120 实测·derive 禁手抄）", "（起草窗实流 W1..W152 已落账 332,320 实测·derive 禁手抄）"),
    ('batch_name="PERPETUAL-N1-W152", batch_trials=2200, file_name="results/perpetual_faces/n1_w152_results.json"',
     'batch_name="PERPETUAL-N1-W153", batch_trials=2200, file_name="results/perpetual_faces/n1_w153_results.json"'),
    # --- S5 ---
    ("（起草窗实况注记：**W1..W151 N1 finalize 已全部落地**——净账本锚头 728,211=W151 finalize 落账【one-pass·bm-a r764·§7/§8 回填 r764 同窗收口】·**K=330,120 合并池**·**零在飞上游席位中**（链前置出空波）。本波 §5 预测键=**W151 finalize 实测值**【results/perpetual_faces/n1_w151_results.json·N1 面最新已落账键】。",
     "（起草窗实况注记：**W1..W152 N1 finalize 已全部落地**——净账本锚头 730,411=W152 finalize 落账【one-pass·bm-a r765·§7/§8 回填 r765 同窗收口】·**K=332,320 合并池**·**零在飞上游席位中**（链前置出空波）。本波 §5 预测键=**W152 finalize 实测值**【results/perpetual_faces/n1_w152_results.json·N1 面最新已落账键】。"),
    ("1. W152-only mu 与累计池 merged mu（W151 实测键 **−0.0928**·K=330,120 合并池·W151-only 实测 **−0.0921**）差异 **|Δ|<0.02**（W2..W151 共一百五十面实测 mu 稳定先例·单波跨键微）。",
     "1. W153-only mu 与累计池 merged mu（W152 实测键 **−0.0928**·K=332,320 合并池·W152-only 实测 **−0.094571**）差异 **|Δ|<0.02**（W2..W152 共一百五十一面实测 mu 稳定先例·单波跨键微）。"),
    ("2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.2450**=W151 合并池实测）。",
     "2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.2450**=W152 合并池实测）。"),
    ("3. A 档 full_sharpe_p95 与 W151 A 档 p95（**0.3247** 实测锚）差 **<0.05**（门标注法 W5..W151 先例：结果知情面仅作机器断言之用·测量面非注册利益）。",
     "3. A 档 full_sharpe_p95 与 W152 A 档 p95（**0.3366** 实测锚）差 **<0.05**（门标注法 W5..W152 先例：结果知情面仅作机器断言之用·测量面非注册利益）。"),
    ("4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W151 先例·W136 +0.0000/W137 +0.0000/W138 −0.0002/W139 +0.0000/W140 +0.0000/W141 +0.0001/W143 +0.0001/W144 +0.0000/W145 +0.0000/W146 +0.0000/W147 −0.0001/W148 +0.0000/W149 +0.0002/W150 +0.0000/W151 **+0.0002** 如实披露；键 W151 实测 K-lift **+0.0002**【line_merged@K330,120 **1.18**·line_pre 1.1798·n_eff 726,011；se_mu 收窄键 W140 0.000443→W141 0.000441→W142 0.000440→W143 0.000438→W144 0.000437→W145 0.000435→W146 0.000434→W147 0.000432→W148 0.000431→W149 0.000429→W150 0.000428→W151 **0.000426**】）。",
     "4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W152 先例·W136 +0.0000/W137 +0.0000/W138 −0.0002/W139 +0.0000/W140 +0.0000/W141 +0.0001/W143 +0.0001/W144 +0.0000/W145 +0.0000/W146 +0.0000/W147 −0.0001/W148 +0.0000/W149 +0.0002/W150 +0.0000/W151 +0.0002/W152 **+0.0002** 如实披露；键 W152 实测 K-lift **+0.0002**【line_merged@K332,320 **1.1803**·line_pre 1.1801·n_eff 728,211；se_mu 收窄键 W140 0.000443→W141 0.000441→W142 0.000440→W143 0.000438→W144 0.000437→W145 0.000435→W146 0.000434→W147 0.000432→W148 0.000431→W149 0.000429→W150 0.000428→W151 0.000426→W152 **0.000425**】）。"),
    ("5. **W153+ 投影（gate 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 351_204..353_203 **CLEAN**（hops=0）；B first-clean **351_404..351_603 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W153：W153 冻结方必须在 post-W152 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W152 B 带 351_204..351_403 注册后将拒 naive W153 A 窗**——W153 A 重 derive 同强制（越过 W152 B 带·阶梯 A-hops-prior-B 继承）；verify at W153 prereg，hop 链逐跳在 probe 回执。",
     "5. **W154+ 投影（gate 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 353_404..355_403 **CLEAN**（hops=0）；B first-clean **353_604..353_803 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W154：W154 冻结方必须在 post-W153 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W153 B 带 353_404..353_603 注册后将拒 naive W154 A 窗**——W154 A 重 derive 同强制（越过 W153 B 带·阶梯 A-hops-prior-B 继承）；verify at W154 prereg，hop 链逐跳在 probe 回执。"),
    # --- S6 ---
    ("run --shard k --of 12 --wave 152/finalize --wave 152", "run --shard k --of 12 --wave 153/finalize --wave 153"),
    ("n1_w152/ 分片计数增长", "n1_w153/ 分片计数增长"),
    ("results/p2cal_ext/n1_w152/shard-<k>-of-12.json", "results/p2cal_ext/n1_w153/shard-<k>-of-12.json"),
    ("results/perpetual_faces/n1_w152_results.json`（finalize 合并件", "results/perpetual_faces/n1_w153_results.json`（finalize 合并件"),
    ("（W1..W151 全落账）", "（W1..W152 全落账）"),
    ("engine_owner==bm-a 67 行注册 + 本候选——以 gate leg0 机证为准·同 W148/W149/W150/W151 最近自有波", "engine_owner==bm-a 68 行注册 + 本候选——以 gate leg0 机证为准·同 W149/W150/W151/W152 最近自有波"),
]

inter = rep(src, pairs, "prereg-xform")

# --- sec7/sec8 span replacement: r765 same-window backfilled blocks -> placeholders
i7 = inter.find("## §7 跑后实证。【finalize 收口机械回填·bm-a r765")
i8 = inter.find("## §8 批后复盘。【finalize 同窗回填·bm-a r765")
ifin = inter.find("- **跑前冻结=本件 commit**")
assert i7 > 0 and i8 > i7 and ifin > i8, f"sec7/8 span anchors missing: {i7},{i8},{ifin}"
assert inter.count("## §7 跑后实证。【finalize 收口机械回填·bm-a r765") == 1
assert inter.count("## §8 批后复盘。【finalize 同窗回填·bm-a r765") == 1
sec7_block, sec8_block = inter[i7:i8], inter[i8:ifin]
assert "n1_w152_results.json 冻结实测键" in sec7_block and "0.3366" in sec7_block \
    and "mu_delta_w152_vs_w151ext" in sec7_block, "sec7 backfill face drift"
assert "W153+ 投影承接" in sec8_block and "本批无新宝藏" in sec8_block, "sec8 backfill face drift"
ph7 = ("## §7 跑后实证。【finalize 收口机械回填·占位——跑前为空】\n"
       "- （占位：12/12 分片落地后 finalize one-pass 机械回填·回填限本节与 §8·judged 断言照 W152 例。）\n\n")
ph8 = ("## §8 批后复盘。【finalize 同窗回填·占位】\n"
       "- （占位：设计复用面+宝藏捕获问+W154+ 投影承接三行照 W152 例回填。）\n\n")
out = inter[:i7] + ph7 + ph8 + inter[ifin:]
assert out.count("占位：12/12") == 1 and out.count("占位：设计复用面") == 1, "placeholder splice drift"
assert "同窗即回填（r763/r764 窗先例延续" not in out, "backfilled sec7 residue"

# --- two-form checklist (bare wave number + lowercase tokens residue) ---
assert out.count("波号 152") == 0, "bare wave number residue (r754 law)"
# The ONE legitimate n1_w152 occurrence = sec5 prediction-key anchor
assert out.count("n1_w152") == 1, "n1_w152 must appear exactly once (sec5 prior-wave key)"
assert out.count("results/perpetual_faces/n1_w152_results.json·N1 面最新已落账键") == 1, "sec5 anchor context"
assert out.count("n1w152") == 0, "lowercase entry token residue (r754 law)"
assert out.count("PERPETUAL-N1-W152") == 0, "batch name residue"
assert out.count("6a4081c01") == 0, "stale seat sha residue"
# W152 A-band must be fully gone; W152 B-band remains exactly once as the
# prior-wave geometry cite in the L5 derivation narrative
assert out.count("349_204..351_203") == 0, "stale W152 A-band residue"
assert out.count("351_204..351_403") == 1 and \
    out.count("被已注册 W152 B 带 351_204..351_403 **拒**") == 1, \
    "W152 B-band must appear exactly once as prior-wave cite"
assert "波号 153=注册表 W152 行后首个自由号" in out and "351_404..353_403" in out \
    and "353_404..353_603" in out and "PERPETUAL-N1-W153" in out, "new W153 facts missing"

io.open(r"research/PERPETUAL_N1_W153_PREREG.md", "w", encoding="utf-8", newline="\n").write(out)
print("W153 prereg written:", len(out), "chars |", len(pairs), "needle pairs, all count==1 |",
      "sec7/8 span-replaced", len(sec7_block) + len(sec8_block), "->", len(ph7) + len(ph8), "bytes")
