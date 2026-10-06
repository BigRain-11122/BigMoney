# -*- coding: utf-8 -*-
"""r773 bm-a W158 per-wave prereg xform: research/PERPETUAL_N1_W157_PREREG.md
-> research/PERPETUAL_N1_W158_PREREG.md. Needle-asserted (r745 extract-vs-insert
law, every needle count==1 measured); two-form checklist enforced at the tail.
Derived from the r772 xform pair chain: OLD side = r772 NEW strings verbatim (=
the live W157 prereg text), NEW side = ordered value-map + ten marker-located
overrides (seat narrative, freeze-list append, push-record ordinals, daiwei A/B
citation chains, S0 claim projection, S0 row, K-lift/se_mu chain extension,
sec5.5 projection) + two live-text sec3 seed-scale overrides.
W158 facts (probe/gate machine-derived, receipts on disk): A=362_404..364_403
(staircase SEVENTEENTH instance E36, hops=1; naive 362_204..364_203 refused at
own start by registered W157 B band 362_204..362_403) + B=364_404..364_603
(own-A mutual exclusion, hops=1; naive 362_404..362_603); seat
MSG-2026-10-06-120x-bma-w158-seat -> origin 24aff72f5 (r773 pre-seat push,
direct delivery behind-0); band gate ADMIT receipt
results/_r773bma_w158_band_gate.json rc0; pre-seat probe r773 receipt.
W157 finalize = bm-a r773 one-pass (sec7/sec8 backfilled same-window), ledger
head 741,411, K=343,320 merged pool; W157-only mu -0.096645 / merged mu
-0.092843 (rounded anchor -0.0928) / sigma 0.245044 / A p95 0.3039 / K-lift
+0.0002 @line 1.1809->1.1811 / se_mu 0.000418 / mu_delta_w157_vs_w156ext
-0.00884 (all from results/perpetual_faces/n1_w157_results.json measured keys)."""
import io

R772 = "results/_r772bma_w157_prereg_xform.py"
src772 = io.open(R772, encoding="utf-8").read()
cut = src772.find("\n# --- apply")
assert cut > 0
ns = {}
exec(compile(src772[:cut], R772, "exec"), ns)
pairs157 = ns["pairs157"]
rep = ns["rep"]
assert len(pairs157) >= 30, len(pairs157)

LIVE = r"research/PERPETUAL_N1_W157_PREREG.md"
live = io.open(LIVE, encoding="utf-8").read()

# --- ordered value-map (tokens first, then back-substitution) ---------------
TOK = [
    # band geometry (W157 values -> tokens)
    ("360_204..362_203", "@ABAND@"),      # W157 A band -> W158 A band
    ("362_204..362_403", "@BBAND@"),      # W157 B band -> W158 B band
    ("360_004..362_003", "@NABAND@"),     # W157 naive A
    ("360_204..360_403", "@NBBAND@"),     # W157 naive B
    ("360_004..360_203", "@PBBAND@"),     # prior-B cite (W156 B)
    ("360_203+1", "@ABASE@"),
    ("362_203+1", "@BBASE@"),
    # stats chains
    ("739,211", "@LEDG@"), ("737,011", "@NEFF@"),
    ("341,120", "@K1@"), ("343,320", "@K2@"),
    ("\u22120.087805", "@MU@"), ("0.3172", "@P95@"), ("\u22120.0928", "@MU4@"),
    # chinese ordinals
    ("一百五十五", "@CN1@"), ("一百五十四", "@CN2@"),
    ("第一百四十七", "@CN3@"), ("第七十三", "@CN4@"), ("第十六", "@CN5@"),
    # round / dir tokens (order: _r772bma before r772; r772 before r771)
    ("_r772bma", "@RDIR@"),
    ("r772", "@RW@"), ("r771", "@PRW@"),
    # seat identity
    ("MSG-2026-10-06-113x", "@SEATTS@"), ("4af40c72d", "@SHA@"),
    # wave tokens (order: W158+ before W158; W158 before W157; W157 before W156)
    ("W158+", "@PROJ@"), ("W158", "@PROJW@"),
    ("W157", "@WN@"), ("W156", "@WP@"),
    ("w157", "@wn@"), ("w156", "@wp@"),
    # bare arabic contexts
    ("第 147 波", "@WAVE146@"), ("波号 157", "@BARE157@"),
    ("--wave 157", "@WAVEFLAG@"), ("行 146", "@R145@"),
    ("行 72", "@R71@"), ("72 行注册", "@ROWS71@"),
    ("泵第 155 枚", "@PUMP154@"), ("154 行", "@L153@"),
]
BACK = [
    ("@ABAND@", "362_404..364_403"), ("@BBAND@", "364_404..364_603"),
    ("@NABAND@", "362_204..364_203"), ("@NBBAND@", "362_404..362_603"),
    ("@PBBAND@", "362_204..362_403"),
    ("@ABASE@", "362_403+1"), ("@BBASE@", "364_403+1"),
    ("@LEDG@", "741,411"), ("@NEFF@", "739,211"),
    ("@K1@", "343,320"), ("@K2@", "345,520"),
    ("@MU@", "\u22120.096645"), ("@P95@", "0.3039"), ("@MU4@", "\u22120.0928"),
    ("@CN1@", "一百五十六"), ("@CN2@", "一百五十五"),
    ("@CN3@", "第一百四十八"), ("@CN4@", "第七十四"), ("@CN5@", "第十七"),
    ("@RDIR@", "_r773bma"),
    ("@RW@", "r773"), ("@PRW@", "r772"),
    ("@SEATTS@", "MSG-2026-10-06-120x"), ("@SHA@", "24aff72f5"),
    ("@PROJ@", "W159+"), ("@PROJW@", "W159"),
    ("@WN@", "W158"), ("@WP@", "W157"),
    ("@wn@", "w158"), ("@wp@", "w157"),
    ("@WAVE146@", "第 148 波"), ("@BARE157@", "波号 158"),
    ("@WAVEFLAG@", "--wave 158"), ("@R145@", "行 147"),
    ("@R71@", "行 73"), ("@ROWS71@", "73 行注册"),
    ("@PUMP154@", "泵第 156 枚"), ("@L153@", "155 行"),
]


def valmap(s: str) -> str:
    for a, b in TOK:
        s = s.replace(a, b)
    for a, b in BACK:
        s = s.replace(a, b)
    return s


# --- marker-located overrides (OLD = pairs157 NEW side verbatim) ------------
OVR = [
    ("全 inbox/processed/ W157 席位零外机命中（本机席位公示=MSG-2026-10-06-113x-bma-w157-seat 已推 origin 4af40c72d 先于本冻结【r565 律·推送窗=direct delivery 4af40c72d（r772 pre-seat push·快进送达 behind-0 at fetch·零 merge 零 --no-verify）；self-ack inbox→processed 移位待 W157 finalize 收口窗】",
     "全 inbox/processed/ W158 席位零外机命中（本机席位公示=MSG-2026-10-06-120x-bma-w158-seat 已推 origin 24aff72f5 先于本冻结【r565 律·推送窗=direct delivery 24aff72f5（r773 pre-seat push·快进送达 behind-0 at fetch·零 merge 零 --no-verify）；self-ack inbox→processed 移位待 W158 finalize 收口窗】"),
    ("W153=bm-a r766 freeze（33388e082）；W154=bm-a r767 freeze（3095cb47e）；W155=bm-a r768 freeze（dde679c63）；W156=bm-a r771 freeze（13c989ba0·表尾）；**均已注册**（表尾 W156 行）。W157=本波 skip-past-published 链面零适用（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r772bma_w157_band_gate.json rc0 实跑）",
     "W154=bm-a r767 freeze（3095cb47e）；W155=bm-a r768 freeze（dde679c63）；W156=bm-a r771 freeze（13c989ba0）；W157=bm-a r772 freeze（aed41df3e·表尾）；**均已注册**（表尾 W157 行）。W158=本波 skip-past-published 链面零适用（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r773bma_w158_band_gate.json rc0 实跑）"),
    ("**席位推送窗实录（r772 窗口实况）**：席位+probe 回执单 commit 推送 origin 送达 **4af40c72d**（direct delivery 快进送达·behind-0 at fetch·零 merge 零 --no-verify；self-ack inbox→processed 移位待 W157 finalize 收口窗）。> **序数机面锚注记**：本波 ordinal=第一百四十七引擎波·bm-a 第七十三枚自有波【机面 derive：engine_owner==bm-a 行 72+本候选以 gate leg0 机证为准】。",
     "**席位推送窗实录（r773 窗口实况）**：席位+probe 回执+W157 finalize 收口件单 commit 推送 origin 送达 **24aff72f5**（direct delivery 快进送达·behind-0 at fetch·零 merge 零 --no-verify；self-ack inbox→processed 移位待 W158 finalize 收口窗）。> **序数机面锚注记**：本波 ordinal=第一百四十八引擎波·bm-a 第七十四枚自有波【机面 derive：engine_owner==bm-a 行 73+本候选以 gate leg0 机证为准】。"),
    ("**带位（r535 机阀 derive 律·ADMIT 回执=results/_r772bma_w157_band_gate.json 单态门全腿实跑·pre-seat probe results/_r772bma_w157_probe.py 先跑·双窗 derive 恒等）**：本波 **A-ext seed=360_204..362_203**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第十六例**：A 面算术继续带 360_004..362_003 在其起点即被已注册 W156 B 带 360_004..360_203 **拒**（W156 席位 W157+ 投影+r771 gate leg3+r772 §8 承接三投影注记所预言）",
     "**带位（r535 机阀 derive 律·ADMIT 回执=results/_r773bma_w158_band_gate.json 单态门全腿实跑·pre-seat probe results/_r773bma_w158_probe.py 先跑·双窗 derive 恒等）**：本波 **A-ext seed=362_404..364_403**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第十七例**：A 面算术继续带 362_204..364_203 在其起点即被已注册 W157 B 带 362_204..362_403 **拒**（W157 席位 W158+ 投影+r772 gate leg3+r773 §8 承接三投影注记所预言）"),
    ("→ B 带本波 A 窗保留走 **1 hop** 落 **362_204..362_403**·**B base==本波 A 尾+1（362_203+1）机检关系**·hop 链逐跳在 probe 回执；**W156 席位 W157+ 投影+r771 gate leg3+r772 §8 承接 re-derive-MANDATORY 注记三面兑现**：投影预言 W157 须在 post-W156 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）。R250：W157 带从未指派·测量面零结果可锁。扫描面=pre-W157 全一百五十四行注册 N1 带表（表尾 W156 行·leg0 机证 154 行）",
     "→ B 带本波 A 窗保留走 **1 hop** 落 **364_404..364_603**·**B base==本波 A 尾+1（364_403+1）机检关系**·hop 链逐跳在 probe 回执；**W157 席位 W158+ 投影+r772 gate leg3+r773 §8 承接 re-derive-MANDATORY 注记三面兑现**：投影预言 W158 须在 post-W157 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）。R250：W158 带从未指派·测量面零结果可锁。扫描面=pre-W158 全一百五十五行注册 N1 带表（表尾 W157 行·leg0 机证 155 行）"),
    ("本机 r772 席位 MSG-2026-10-06-113x 投影 W158+ A 362_204..364_203 naive/B 362_404..362_603 naive **re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·投影 A 撞本波 B 带=阶梯 A-hops-prior-B 继承待 W158 注册宇宙复核）",
     "本机 r773 席位 MSG-2026-10-06-120x 投影 W159+ A 364_404..366_403 naive/B 364_604..364_803 naive **re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·投影 A 撞本波 B 带=阶梯 A-hops-prior-B 继承待 W159 注册宇宙复核）"),
    ("T-2026-10-01-141 s1 引擎线第 147 波【bm-a 第七十三枚自有波【机面 derive：engine_owner==bm-a 行 72+本候选以 gate leg0 机证为准·同 W153/W154/W155/W156 最近自有波】。（波号=注册表 W156 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-06-113x-bma-w157-seat 先推 origin 4af40c72d r565 律",
     "T-2026-10-01-141 s1 引擎线第 148 波【bm-a 第七十四枚自有波【机面 derive：engine_owner==bm-a 行 73+本候选以 gate leg0 机证为准·同 W154/W155/W156/W157 最近自有波】。（波号=注册表 W157 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-06-120x-bma-w158-seat 先推 origin 24aff72f5 r565 律"),
    ("4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W156 先例·W136 +0.0000/W137 +0.0000/W138 −0.0002/W139 +0.0000/W140 +0.0000/W141 +0.0001/W143 +0.0001/W144 +0.0000/W145 +0.0000/W146 +0.0000/W147 −0.0001/W148 +0.0000/W149 +0.0002/W150 +0.0000/W151 +0.0002/W152 +0.0001/W153 −0.0002/W154 −0.0002/W155 −0.0002/W156 **+0.0001** 如实披露；键 W156 实测 K-lift **+0.0001**【line_merged@K341,120 **1.1808**·line_pre 1.1807·n_eff 737,011；se_mu 收窄键 W140 0.000443→W141 0.000441→W142 0.000440→W143 0.000438→W144 0.000437→W145 0.000435→W146 0.000434→W147 0.000432→W148 0.000431→W149 0.000429→W150 0.000428→W151 0.000426→W152 0.000425→W153 0.000424→W154 0.000422→W155 0.000421→W156 **0.000420**】）。",
     "4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W157 先例·W136 +0.0000/W137 +0.0000/W138 −0.0002/W139 +0.0000/W140 +0.0000/W141 +0.0001/W143 +0.0001/W144 +0.0000/W145 +0.0000/W146 +0.0000/W147 −0.0001/W148 +0.0000/W149 +0.0002/W150 +0.0000/W151 +0.0002/W152 +0.0001/W153 −0.0002/W154 −0.0002/W155 −0.0002/W156 +0.0001/W157 **+0.0002** 如实披露；键 W157 实测 K-lift **+0.0002**【line_merged@K343,320 **1.1811**·line_pre 1.1809·n_eff 739,211；se_mu 收窄键 W140 0.000443→W141 0.000441→W142 0.000440→W143 0.000438→W144 0.000437→W145 0.000435→W146 0.000434→W147 0.000432→W148 0.000431→W149 0.000429→W150 0.000428→W151 0.000426→W152 0.000425→W153 0.000424→W154 0.000422→W155 0.000421→W156 0.000420→W157 **0.000418**】）。"),
    ("5. **W158+ 投影（gate 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 362_204..364_203 **CLEAN**（hops=0）；B first-clean **362_404..362_603 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W158：W158 冻结方必须在 post-W157 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W157 B 带 362_204..362_403 注册后将拒 naive W158 A 窗**——W158 A 重 derive 同强制（越过 W157 B 带·阶梯 A-hops-prior-B 继承）；verify at W158 prereg，hop 链逐跳在 probe 回执。",
     "5. **W159+ 投影（gate 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 364_404..366_403 **CLEAN**（hops=0）；B first-clean **364_604..364_803 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W159：W159 冻结方必须在 post-W158 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W158 B 带 364_404..364_603 注册后将拒 naive W159 A 窗**——W159 A 重 derive 同强制（越过 W158 B 带·阶梯 A-hops-prior-B 继承）；verify at W159 prereg，hop 链逐跳在 probe 回执。"),
    ("engine_owner==bm-a 72 行注册 + 本候选——以 gate leg0 机证为准·同 W153/W154/W155/W156 最近自有波",
     "engine_owner==bm-a 73 行注册 + 本候选——以 gate leg0 机证为准·同 W154/W155/W156/W157 最近自有波"),
]
OVR_OLD = {o for o, _ in OVR}


def locate(marker):
    hits = [i for i, (o, n) in enumerate(pairs157) if marker in n]
    assert len(hits) == 1, (marker, hits)
    return hits[0]


OVR_IDX = {}
for o, _n in OVR:
    OVR_IDX[locate(o[:40])] = o
assert len(OVR_IDX) == len(OVR), "override markers collided"
SKIP_IDX = set()
for marker in ("entry rng seed=**360_204+j**", "exit rng=**362_204+j**"):
    hits = [i for i, (o, n) in enumerate(pairs157) if marker in n]
    assert len(hits) == 1, (marker, hits)
    SKIP_IDX.add(hits[0])
assert len(SKIP_IDX) == 2, SKIP_IDX

pairs158 = []
for i, (o157, n157) in enumerate(pairs157):
    if i in OVR_IDX:
        pairs158.append((OVR_IDX[i], dict(OVR)[OVR_IDX[i]]))
    elif i in SKIP_IDX:
        continue  # replaced by live-text sec3 overrides below
    else:
        pairs158.append((n157, valmap(n157)))

# --- live-text sec3 seed-scale overrides --------------------------------------
def live_line(start_marker):
    i = live.find(start_marker)
    assert i >= 0, start_marker
    j = live.find("\n", i)
    assert j > i, start_marker
    return live[i:j]

s3a_old = live_line("- **A 档**（j=0..1,999）：entry rng seed=**360_204+j**")
assert "阶梯第十六例" in s3a_old and "360_004..362_003 起点即被 W156 B 带拒" in s3a_old, s3a_old[:120]
s3a_new = ("- **A 档**（j=0..1,999）：entry rng seed=**362_404+j**（法典 §4 W158 行 A=362_404..364_403·"
           "**FIRST-CLEAN past prior-wave B 阶梯第十七例**：算术续带 362_204..364_203 起点即被 W157 B 带拒"
           "→1 hop 落 362_404..364_403·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场）；"
           "p=`BASELINE_P[(j//50)%2]`（v1 50-seed 块交替惯例逐字）；随机入场短窗=**引擎退出口**（v1 设计逐字）。")
s3a_tail = s3a_old[s3a_old.find("）；p=`BASELINE_P"):]
assert s3a_new.endswith(s3a_tail), "sec3-A tail drift"
pairs158.append((s3a_old, s3a_new))

s3b_old = live_line("- **B 档**（j=0..199）：entry rng=**360_204+j**")
assert "W156 席位 W157+ 投影+r771 gate leg3+r772 §8 承接" in s3b_old and "W157+ 投影" in s3b_old, s3b_old[:120]
s3b_new = ("- **B 档**（j=0..199）：entry rng=**362_404+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；"
           "exit rng=**364_404+j**（法典 §4 W158 行 B=364_404..364_603·**FIRST-CLEAN past own-wave A**："
           "B 算术续带 362_404..362_603 在注册宇宙上 CLEAN 但落在本波 A 窗内→**同窗互斥面 leg2 律·W141 先例**"
           "强制 B 越本波 A 窗→保留走落 364_404..364_603·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·"
           "hop 链逐跳在 probe 回执·与 W157 席位 W158+ 投影+r772 gate leg3+r773 §8 承接 W158+ 投影 re-derive-MANDATORY"
           "+同窗互斥预披露注记三面兑现收敛·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`。")
s3b_tail = s3b_old[s3b_old.find("）；p_exit=`P_EXIT=0.05`。"):]
assert s3b_new.endswith(s3b_tail), "sec3-B tail drift"
pairs158.append((s3b_old, s3b_new))

# --- apply ---------------------------------------------------------------------
span_probe = [p for p in pairs158 if "占位" in p[0] or "回填" in p[0][:60]]
assert span_probe == [], f"unexpected span-coupled needles: {span_probe}"

inter = rep(live, pairs158, "w158-prereg-xform")

# --- sec7/sec8 span replacement: r773 backfilled blocks -> W158 placeholders --
i7 = inter.find("## §7 跑后实证。【finalize 收口机械回填·bm-a r773")
i8 = inter.find("## §8 批后复盘。【finalize 同窗回填·bm-a r773")
ifin = inter.find("- **跑前冻结=本件 commit**")
assert i7 > 0 and i8 > i7 and ifin > i8, f"sec7/8 span anchors missing: {i7},{i8},{ifin}"
sec7_block, sec8_block = inter[i7:i8], inter[i8:ifin]
assert "n1_w157_results.json 冻结实测键" in sec7_block and "0.3039" in sec7_block \
    and "mu_delta_w157_vs_w156ext" in sec7_block, "sec7 backfill face drift"
assert "W158+ 投影承接" in sec8_block and "本批无新宝藏" in sec8_block, "sec8 backfill face drift"
ph7 = ("## §7 跑后实证。【finalize 收口机械回填·占位——跑前为空】\n"
       "- （占位：12/12 分片落地后 finalize one-pass 机械回填·回填限本节与 §8·judged 断言照 W157 例。）\n\n")
ph8 = ("## §8 批后复盘。【finalize 同窗回填·占位】\n"
       "- （占位：设计复用面+宝藏捕获问+W159+ 投影承接三行照 W157 例回填。）\n\n")
out = inter[:i7] + ph7 + ph8 + inter[ifin:]
assert out.count("占位：12/12") == 1 and out.count("占位：设计复用面") == 1, "placeholder splice drift"
assert "同窗即回填（r763..r772 窗先例延续" not in out, "backfilled sec7 residue"

# --- two-form checklist -------------------------------------------------------
assert out.count("波号 157") == 0, "bare wave number residue (r754 law)"
assert out.count("n1_w157") == 1, "n1_w157 must appear exactly once (sec5 prior-wave key)"
assert out.count("results/perpetual_faces/n1_w157_results.json·N1 面最新已落账键") == 1, "sec5 anchor context"
assert out.count("n1w157") == 0, "lowercase entry token residue (r754 law)"
assert out.count("PERPETUAL-N1-W157") == 0, "batch name residue"
assert out.count("4af40c72d") == 0, "stale seat sha residue"
assert out.count("360_204..362_203") == 0, "stale W157 A-band residue"
assert out.count("362_204..362_403") == 1 and \
    out.count("被已注册 W157 B 带 362_204..362_403 **拒**") == 1, \
    "W157 B-band must appear exactly once as prior-wave cite"
assert out.count("362_204..364_203") >= 1 and out.count("362_404..362_603") >= 1, "naive faces"
assert out.count("\u22120.0928") == 1, "prior merged-mu 4dp anchor count"
assert "波号 158=注册表 W157 行后首个自由号" in out and "362_404..364_403" in out \
    and "364_404..364_603" in out and "PERPETUAL-N1-W158" in out, "new W158 facts missing"
assert out.count("aed41df3e") == 1 and out.count("24aff72f5") >= 1, "freeze/seat sha anchors missing"
assert out.count("741,411") >= 1 and out.count("345,520") == 1 and out.count("0.3039") == 1 \
    and out.count("\u22120.096645") == 1, "W158 stat anchors missing"

io.open(r"research/PERPETUAL_N1_W158_PREREG.md", "w", encoding="utf-8", newline="\n").write(out)
print("W158 prereg written:", len(out), "chars |", len(pairs158), "needle pairs, all count==1 |",
      "sec7/8 span-replaced", len(sec7_block) + len(sec8_block), "->", len(ph7) + len(ph8), "bytes")
