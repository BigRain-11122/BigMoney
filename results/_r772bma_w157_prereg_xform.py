# -*- coding: utf-8 -*-
"""r772 bm-a W157 per-wave prereg xform: research/PERPETUAL_N1_W156_PREREG.md
-> research/PERPETUAL_N1_W157_PREREG.md. Needle-asserted (r745 extract-vs-insert
law, every needle count==1 measured); two-form checklist enforced at the tail.
Derived from the r769 xform pair chain: OLD side = r769 NEW strings verbatim (=
the live W156 prereg text, including the r771 editor faces), NEW side = ordered
value-map + ten marker-located overrides (seat narrative, freeze-list append,
push-record ordinals, daiwei A/B citation chains, S0 claim projection, S0 row,
S6 row, K-lift/se_mu chain extension, sec5.5 projection) + two live-text sec3
seed-scale overrides (the r771 T-90 fix faces -- pairs156 NEW sides carry the
pre-fix digits and no longer match the live text).
W157 facts (probe/gate machine-derived, receipts on disk): A=360_204..362_203
(staircase SIXTEENTH instance E36, hops=1; naive 360_004..362_003 refused at
own start by registered W156 B band 360_004..360_203) + B=362_204..362_403
(own-A mutual exclusion, hops=1; naive 360_204..360_403); seat
MSG-2026-10-06-113x-bma-w157-seat -> origin 4af40c72d (r772 pre-seat push,
direct delivery behind-0); band gate ADMIT receipt
results/_r772bma_w157_band_gate.json rc0; pre-seat probe r772 receipt.
W156 finalize = bm-a r772 one-pass (sec7/sec8 backfilled same-window), ledger
head 739,211, K=341,120 merged pool; W156-only mu -0.087805 / merged mu
-0.092818 (rounded anchor -0.0928) / sigma 0.245012 / A p95 0.3172 / K-lift
+0.0001 @line 1.1807->1.1808 / se_mu 0.000420 / mu_delta_w156_vs_w155ext
+0.004919 (all from results/perpetual_faces/n1_w156_results.json measured keys)."""
import io

R769 = "results/_r769bma_w156_prereg_xform.py"
src769 = io.open(R769, encoding="utf-8").read()
cut = src769.find("\n# --- sec7/sec8 span replacement")
assert cut > 0
ns = {}
exec(compile(src769[:cut], R769, "exec"), ns)
pairs156 = ns["pairs156"] if "pairs156" in ns else ns["pairs"]
rep = ns["rep"]
assert len(pairs156) >= 30, len(pairs156)

LIVE = r"research/PERPETUAL_N1_W156_PREREG.md"
live = io.open(LIVE, encoding="utf-8").read()

# --- ordered value-map (tokens first, then back-substitution) ---------------
TOK = [
    # band geometry (W156 values -> tokens)
    ("358_004..360_003", "@ABAND@"),      # W156 A band -> W157 A band
    ("360_004..360_203", "@BBAND@"),      # W156 B band -> W157 B band
    ("357_804..359_803", "@NABAND@"),     # W156 naive A
    ("358_004..358_203", "@NBBAND@"),     # W156 naive B
    ("357_804..358_003", "@PBBAND@"),     # prior-B cite (W155 B)
    ("358_003+1", "@ABASE@"),
    ("360_003+1", "@BBASE@"),
    # stats chains
    ("737,011", "@LEDG@"), ("734,811", "@NEFF@"),
    ("338,920", "@K1@"), ("341,120", "@K2@"),
    ("\u22120.092724", "@MU@"), ("0.3122", "@P95@"), ("\u22120.0929", "@MU4@"),
    # chinese ordinals
    ("一百五十四", "@CN1@"), ("一百五十三", "@CN2@"),
    ("第一百四十六", "@CN3@"), ("第七十二", "@CN4@"), ("第十五", "@CN5@"),
    # round / dir tokens (order: _r769bma before r769; r769 before r768)
    ("_r769bma", "@RDIR@"),
    ("r769", "@RW@"), ("r768", "@PRW@"),
    # seat identity
    ("MSG-2026-10-06-1009", "@SEATTS@"), ("ffce2936f", "@SHA@"),
    # wave tokens (order: W157+ before W157; W157 before W156; W156 before W155)
    ("W157+", "@PROJ@"), ("W157", "@PROJW@"),
    ("W156", "@WN@"), ("W155", "@WP@"),
    ("w156", "@wn@"), ("w155", "@wp@"),
    # bare arabic contexts
    ("第 146 波", "@WAVE145@"), ("波号 156", "@BARE156@"),
    ("--wave 156", "@WAVEFLAG@"), ("行 145", "@R144@"),
    ("行 71", "@R70@"), ("71 行注册", "@ROWS70@"),
    ("泵第 154 枚", "@PUMP153@"), ("153 行", "@L152@"),
]
BACK = [
    ("@ABAND@", "360_204..362_203"), ("@BBAND@", "362_204..362_403"),
    ("@NABAND@", "360_004..362_003"), ("@NBBAND@", "360_204..360_403"),
    ("@PBBAND@", "360_004..360_203"),
    ("@ABASE@", "360_203+1"), ("@BBASE@", "362_203+1"),
    ("@LEDG@", "739,211"), ("@NEFF@", "737,011"),
    ("@K1@", "341,120"), ("@K2@", "343,320"),
    ("@MU@", "\u22120.087805"), ("@P95@", "0.3172"), ("@MU4@", "\u22120.0928"),
    ("@CN1@", "一百五十五"), ("@CN2@", "一百五十四"),
    ("@CN3@", "第一百四十七"), ("@CN4@", "第七十三"), ("@CN5@", "第十六"),
    ("@RDIR@", "_r772bma"),
    ("@RW@", "r772"), ("@PRW@", "r771"),
    ("@SEATTS@", "MSG-2026-10-06-113x"), ("@SHA@", "4af40c72d"),
    ("@PROJ@", "W158+"), ("@PROJW@", "W158"),
    ("@WN@", "W157"), ("@WP@", "W156"),
    ("@wn@", "w157"), ("@wp@", "w156"),
    ("@WAVE145@", "第 147 波"), ("@BARE156@", "波号 157"),
    ("@WAVEFLAG@", "--wave 157"), ("@R144@", "行 146"),
    ("@R70@", "行 72"), ("@ROWS70@", "72 行注册"),
    ("@PUMP153@", "泵第 155 枚"), ("@L152@", "154 行"),
]


def valmap(s: str) -> str:
    for a, b in TOK:
        s = s.replace(a, b)
    for a, b in BACK:
        s = s.replace(a, b)
    return s


# --- marker-located overrides (OLD = pairs156 NEW side verbatim) ------------
OVR = [
    ("全 inbox/processed/ W156 席位零外机命中（本机席位公示=MSG-2026-10-06-1009-bma-w156-seat 已推 origin ffce2936f 先于本冻结【r565 律·推送窗=direct delivery ffce2936f（r769 pre-seat push·快进送达 behind-0 at fetch·零 merge 零 --no-verify）；self-ack inbox→processed 移位待 W156 finalize 收口窗】",
     "全 inbox/processed/ W157 席位零外机命中（本机席位公示=MSG-2026-10-06-113x-bma-w157-seat 已推 origin 4af40c72d 先于本冻结【r565 律·推送窗=direct delivery 4af40c72d（r772 pre-seat push·快进送达 behind-0 at fetch·零 merge 零 --no-verify）；self-ack inbox→processed 移位待 W157 finalize 收口窗】"),
    ("W152=bm-a r764 freeze（520eb01ca）；W153=bm-a r766 freeze（33388e082）；W154=bm-a r767 freeze（3095cb47e）；W155=bm-a r768 freeze（dde679c63·表尾）；**均已注册**（表尾 W155 行）。W156=本波 skip-past-published 链面零适用（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r769bma_w156_band_gate.json rc0 实跑）",
     "W153=bm-a r766 freeze（33388e082）；W154=bm-a r767 freeze（3095cb47e）；W155=bm-a r768 freeze（dde679c63）；W156=bm-a r771 freeze（13c989ba0·表尾）；**均已注册**（表尾 W156 行）。W157=本波 skip-past-published 链面零适用（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r772bma_w157_band_gate.json rc0 实跑）"),
    ("**席位推送窗实录（r769 窗口实况）**：席位+probe 回执单 commit 推送 origin 送达 **ffce2936f**（direct delivery 快进送达·behind-0 at fetch·零 merge 零 --no-verify；self-ack inbox→processed 移位待 W156 finalize 收口窗）。> **序数机面锚注记**：本波 ordinal=第一百四十六引擎波·bm-a 第七十二枚自有波【机面 derive：engine_owner==bm-a 行 71+本候选以 gate leg0 机证为准】。",
     "**席位推送窗实录（r772 窗口实况）**：席位+probe 回执单 commit 推送 origin 送达 **4af40c72d**（direct delivery 快进送达·behind-0 at fetch·零 merge 零 --no-verify；self-ack inbox→processed 移位待 W157 finalize 收口窗）。> **序数机面锚注记**：本波 ordinal=第一百四十七引擎波·bm-a 第七十三枚自有波【机面 derive：engine_owner==bm-a 行 72+本候选以 gate leg0 机证为准】。"),
    ("**带位（r535 机阀 derive 律·ADMIT 回执=results/_r769bma_w156_band_gate.json 单态门全腿实跑·pre-seat probe results/_r769bma_w156_probe.py 先跑·双窗 derive 恒等）**：本波 **A-ext seed=358_004..360_003**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第十五例**：A 面算术继续带 357_804..359_803 在其起点即被已注册 W155 B 带 357_804..358_003 **拒**（W155 席位 leg4+r768 gate leg3+r769 §8 承接三投影注记所预言）",
     "**带位（r535 机阀 derive 律·ADMIT 回执=results/_r772bma_w157_band_gate.json 单态门全腿实跑·pre-seat probe results/_r772bma_w157_probe.py 先跑·双窗 derive 恒等）**：本波 **A-ext seed=360_204..362_203**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第十六例**：A 面算术继续带 360_004..362_003 在其起点即被已注册 W156 B 带 360_004..360_203 **拒**（W156 席位 W157+ 投影+r771 gate leg3+r772 §8 承接三投影注记所预言）"),
    ("→ B 带本波 A 窗保留走 **1 hop** 落 **360_004..360_203**·**B base==本波 A 尾+1（360_003+1）机检关系**·hop 链逐跳在 probe 回执；**W155 席位 leg4+r768 gate leg3+r769 §8 承接 re-derive-MANDATORY 注记三面兑现**：投影预言 W156 须在 post-W155 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）。R250：W156 带从未指派·测量面零结果可锁。扫描面=pre-W156 全一百五十三行注册 N1 带表（表尾 W155 行·leg0 机证 153 行）",
     "→ B 带本波 A 窗保留走 **1 hop** 落 **362_204..362_403**·**B base==本波 A 尾+1（362_203+1）机检关系**·hop 链逐跳在 probe 回执；**W156 席位 W157+ 投影+r771 gate leg3+r772 §8 承接 re-derive-MANDATORY 注记三面兑现**：投影预言 W157 须在 post-W156 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）。R250：W157 带从未指派·测量面零结果可锁。扫描面=pre-W157 全一百五十四行注册 N1 带表（表尾 W156 行·leg0 机证 154 行）"),
    ("本机 r769 席位 MSG-2026-10-06-1009 投影 W157+ A 357_804..359_803 naive/B 358_004..358_203 naive **re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·投影 A 撞本波 B 带=阶梯 A-hops-prior-B 继承待 W157 注册宇宙复核）",
     "本机 r772 席位 MSG-2026-10-06-113x 投影 W158+ A 362_204..364_203 naive/B 362_404..362_603 naive **re-derive 强制注记+同窗互斥预披露**（投影 B 落投影 A 窗内·投影 A 撞本波 B 带=阶梯 A-hops-prior-B 继承待 W158 注册宇宙复核）"),
    ("T-2026-10-01-141 s1 引擎线第 146 波【bm-a 第七十二枚自有波【机面 derive：engine_owner==bm-a 行 71+本候选以 gate leg0 机证为准·同 W152/W153/W154/W155 最近自有波】。（波号=注册表 W155 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-06-1009-bma-w156-seat 先推 origin ffce2936f r565 律",
     "T-2026-10-01-141 s1 引擎线第 147 波【bm-a 第七十三枚自有波【机面 derive：engine_owner==bm-a 行 72+本候选以 gate leg0 机证为准·同 W153/W154/W155/W156 最近自有波】。（波号=注册表 W156 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-06-113x-bma-w157-seat 先推 origin 4af40c72d r565 律"),
    ("4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W155 先例·W136 +0.0000/W137 +0.0000/W138 −0.0002/W139 +0.0000/W140 +0.0000/W141 +0.0001/W143 +0.0001/W144 +0.0000/W145 +0.0000/W146 +0.0000/W147 −0.0001/W148 +0.0000/W149 +0.0002/W150 +0.0000/W151 +0.0002/W152 +0.0001/W153 −0.0002/W154 −0.0002/W155 **−0.0002** 如实披露；键 W155 实测 K-lift **−0.0002**【line_merged@K338,920 **1.1805**·line_pre 1.1807·n_eff 734,811；se_mu 收窄键 W140 0.000443→W141 0.000441→W142 0.000440→W143 0.000438→W144 0.000437→W145 0.000435→W146 0.000434→W147 0.000432→W148 0.000431→W149 0.000429→W150 0.000428→W151 0.000426→W152 0.000425→W153 0.000424→W154 0.000422→W155 **0.000421**】）。",
     "4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W156 先例·W136 +0.0000/W137 +0.0000/W138 −0.0002/W139 +0.0000/W140 +0.0000/W141 +0.0001/W143 +0.0001/W144 +0.0000/W145 +0.0000/W146 +0.0000/W147 −0.0001/W148 +0.0000/W149 +0.0002/W150 +0.0000/W151 +0.0002/W152 +0.0001/W153 −0.0002/W154 −0.0002/W155 −0.0002/W156 **+0.0001** 如实披露；键 W156 实测 K-lift **+0.0001**【line_merged@K341,120 **1.1808**·line_pre 1.1807·n_eff 737,011；se_mu 收窄键 W140 0.000443→W141 0.000441→W142 0.000440→W143 0.000438→W144 0.000437→W145 0.000435→W146 0.000434→W147 0.000432→W148 0.000431→W149 0.000429→W150 0.000428→W151 0.000426→W152 0.000425→W153 0.000424→W154 0.000422→W155 0.000421→W156 **0.000420**】）。"),
    ("5. **W157+ 投影（gate 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 357_804..359_803 **CLEAN**（hops=0）；B first-clean **358_004..358_203 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W157：W157 冻结方必须在 post-W156 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W156 B 带 360_004..360_203 注册后将拒 naive W157 A 窗**——W157 A 重 derive 同强制（越过 W156 B 带·阶梯 A-hops-prior-B 继承）；verify at W157 prereg，hop 链逐跳在 probe 回执。",
     "5. **W158+ 投影（gate 机证·下波冻结方复核非转抄 r587 律）**：A first-clean 362_204..364_203 **CLEAN**（hops=0）；B first-clean **362_404..362_603 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W158：W158 冻结方必须在 post-W157 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W157 B 带 362_204..362_403 注册后将拒 naive W158 A 窗**——W158 A 重 derive 同强制（越过 W157 B 带·阶梯 A-hops-prior-B 继承）；verify at W158 prereg，hop 链逐跳在 probe 回执。"),
    ("engine_owner==bm-a 71 行注册 + 本候选——以 gate leg0 机证为准·同 W152/W153/W154/W155 最近自有波",
     "engine_owner==bm-a 72 行注册 + 本候选——以 gate leg0 机证为准·同 W153/W154/W155/W156 最近自有波"),
]
OVR_OLD = {o for o, _ in OVR}


def locate(marker):
    hits = [i for i, (o, n) in enumerate(pairs156) if marker in n]
    assert len(hits) == 1, (marker, hits)
    return hits[0]


OVR_IDX = {}
for o, _n in OVR:
    OVR_IDX[locate(o[:40])] = o
assert len(OVR_IDX) == len(OVR), "override markers collided"
SKIP_IDX = set()
for marker in ("entry rng seed=**355_804+j**", "exit rng=**357_804+j**"):
    hits = [i for i, (o, n) in enumerate(pairs156) if marker in n]
    assert len(hits) == 1, (marker, hits)
    SKIP_IDX.add(hits[0])
assert len(SKIP_IDX) == 2, SKIP_IDX

pairs157 = []
for i, (o156, n156) in enumerate(pairs156):
    if i in OVR_IDX:
        pairs157.append((OVR_IDX[i], dict(OVR)[OVR_IDX[i]]))
    elif i in SKIP_IDX:
        continue  # replaced by live-text sec3 overrides below
    else:
        pairs157.append((n156, valmap(n156)))

# --- live-text sec3 seed-scale overrides (r771 T-90 fix faces) ---------------
def live_line(start_marker):
    i = live.find(start_marker)
    assert i >= 0, start_marker
    j = live.find("\n", i)
    assert j > i, start_marker
    return live[i:j]

s3a_old = live_line("- **A 档**（j=0..1,999）：entry rng seed=**358_004+j**")
assert "阶梯第十五例" in s3a_old and "357_804..359_803 起点即被 W155 B 带拒" in s3a_old, s3a_old[:120]
s3a_new = ("- **A 档**（j=0..1,999）：entry rng seed=**360_204+j**（法典 §4 W157 行 A=360_204..362_203·"
           "**FIRST-CLEAN past prior-wave B 阶梯第十六例**：算术续带 360_004..362_003 起点即被 W156 B 带拒"
           "→1 hop 落 360_204..362_203·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场）；"
           "p=`BASELINE_P[(j//50)%2]`（v1 50-seed 块交替惯例逐字）；随机入场短窗=**引擎退出口**（v1 设计逐字）。")
s3a_tail = s3a_old[s3a_old.find("）；p=`BASELINE_P"):]
assert s3a_new.endswith(s3a_tail), "sec3-A tail drift"
pairs157.append((s3a_old, s3a_new))

s3b_old = live_line("- **B 档**（j=0..199）：entry rng=**358_004+j**")
assert "W155 席位 leg4+r768 gate leg3+r769 §8 承接" in s3b_old and "W156+ 投影" in s3b_old, s3b_old[:120]
s3b_new = ("- **B 档**（j=0..199）：entry rng=**360_204+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；"
           "exit rng=**362_204+j**（法典 §4 W157 行 B=362_204..362_403·**FIRST-CLEAN past own-wave A**："
           "B 算术续带 360_204..360_403 在注册宇宙上 CLEAN 但落在本波 A 窗内→**同窗互斥面 leg2 律·W141 先例**"
           "强制 B 越本波 A 窗→保留走落 362_204..362_403·hops=1·**B base==本波 A 尾+1 机检关系**·非轮转 r587·"
           "hop 链逐跳在 probe 回执·与 W156 席位 W157+ 投影+r771 gate leg3+r772 §8 承接 W157+ 投影 re-derive-MANDATORY"
           "+同窗互斥预披露注记三面兑现收敛·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`。")
s3b_tail = s3b_old[s3b_old.find("）；p_exit=`P_EXIT=0.05`。"):]
assert s3b_new.endswith(s3b_tail), "sec3-B tail drift"
pairs157.append((s3b_old, s3b_new))

# --- apply ---------------------------------------------------------------------
span_probe = [p for p in pairs157 if "占位" in p[0] or "回填" in p[0][:60]]
assert span_probe == [], f"unexpected span-coupled needles: {span_probe}"

inter = rep(live, pairs157, "w157-prereg-xform")

# --- sec7/sec8 span replacement: r772 backfilled blocks -> W157 placeholders --
i7 = inter.find("## §7 跑后实证。【finalize 收口机械回填·bm-a r772")
i8 = inter.find("## §8 批后复盘。【finalize 同窗回填·bm-a r772")
ifin = inter.find("- **跑前冻结=本件 commit**")
assert i7 > 0 and i8 > i7 and ifin > i8, f"sec7/8 span anchors missing: {i7},{i8},{ifin}"
sec7_block, sec8_block = inter[i7:i8], inter[i8:ifin]
assert "n1_w156_results.json 冻结实测键" in sec7_block and "0.3172" in sec7_block \
    and "mu_delta_w156_vs_w155ext" in sec7_block, "sec7 backfill face drift"
assert "W157+ 投影承接" in sec8_block and "本批无新宝藏" in sec8_block, "sec8 backfill face drift"
ph7 = ("## §7 跑后实证。【finalize 收口机械回填·占位——跑前为空】\n"
       "- （占位：12/12 分片落地后 finalize one-pass 机械回填·回填限本节与 §8·judged 断言照 W156 例。）\n\n")
ph8 = ("## §8 批后复盘。【finalize 同窗回填·占位】\n"
       "- （占位：设计复用面+宝藏捕获问+W158+ 投影承接三行照 W156 例回填。）\n\n")
out = inter[:i7] + ph7 + ph8 + inter[ifin:]
assert out.count("占位：12/12") == 1 and out.count("占位：设计复用面") == 1, "placeholder splice drift"
assert "同窗即回填（r763..r769 窗先例延续" not in out, "backfilled sec7 residue"

# --- two-form checklist -------------------------------------------------------
assert out.count("波号 156") == 0, "bare wave number residue (r754 law)"
assert out.count("n1_w156") == 1, "n1_w156 must appear exactly once (sec5 prior-wave key)"
assert out.count("results/perpetual_faces/n1_w156_results.json·N1 面最新已落账键") == 1, "sec5 anchor context"
assert out.count("n1w156") == 0, "lowercase entry token residue (r754 law)"
assert out.count("PERPETUAL-N1-W156") == 0, "batch name residue"
assert out.count("ffce2936f") == 0, "stale seat sha residue"
assert out.count("358_004..360_003") == 0, "stale W156 A-band residue"
assert out.count("360_004..360_203") == 1 and \
    out.count("被已注册 W156 B 带 360_004..360_203 **拒**") == 1, \
    "W156 B-band must appear exactly once as prior-wave cite"
assert out.count("360_004..362_003") >= 1 and out.count("360_204..360_403") >= 1, "naive faces"
assert out.count("\u22120.0929") == 0, "stale merged-mu 4dp residue"
assert "波号 157=注册表 W156 行后首个自由号" in out and "360_204..362_203" in out \
    and "362_204..362_403" in out and "PERPETUAL-N1-W157" in out, "new W157 facts missing"
assert out.count("13c989ba0") == 1 and out.count("4af40c72d") >= 1, "freeze/seat sha anchors missing"
assert out.count("739,211") >= 1 and out.count("343,320") == 1 and out.count("0.3172") == 1 \
    and out.count("\u22120.087805") == 1, "W157 stat anchors missing"

io.open(r"research/PERPETUAL_N1_W157_PREREG.md", "w", encoding="utf-8", newline="\n").write(out)
print("W157 prereg written:", len(out), "chars |", len(pairs157), "needle pairs, all count==1 |",
      "sec7/8 span-replaced", len(sec7_block) + len(sec8_block), "->", len(ph7) + len(ph8), "bytes")
