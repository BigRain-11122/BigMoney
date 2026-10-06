# -*- coding: utf-8 -*-
"""r769 bm-a W156 per-wave prereg xform: research/PERPETUAL_N1_W155_PREREG.md
-> research/PERPETUAL_N1_W156_PREREG.md. Needle-asserted (r745 extract-vs-insert
law, every needle count==1 measured); two-form checklist enforced at the tail.
Derived from the r768 xform pairs: OLD side = r768 NEW strings verbatim (= the
live W155 prereg text), NEW side = ordered value-map + six manual override
needles (freeze-list append, seat-delivery window narrative, seat-push-record
ordinals, K-lift/se_mu chain extension, S0 engine-wave row, S6 engine-rows row).
W156 facts: A=358_004..360_003 (staircase FIFTEENTH instance E36, hops=1) +
B=360_004..360_203 (own-A mutual exclusion, hops=1); seat
MSG-2026-10-06-1009-bma-w156-seat -> origin ffce2936f (r769 pre-seat push,
direct delivery behind-0); band gate ADMIT receipt
results/_r769bma_w156_band_gate.json rc0; pre-seat probe r769 receipt.
W155 finalize = bm-a r769 one-pass (sec7/sec8 backfilled same-window), ledger
head 737,011, K=338,920 merged pool; W155-only mu -0.092724 / merged mu
-0.092851 / sigma 0.244997 / A p95 0.3122 / K-lift -0.0002 @line 1.1807->1.1805
/ se_mu 0.000421 / mu_delta_w155_vs_w154ext +0.001512
(all from results/perpetual_faces/n1_w155_results.json measured keys)."""
import io

R768 = "results/_r768bma_w155_prereg_xform.py"
src768 = io.open(R768, encoding="utf-8").read()
cut = src768.find("# --- sec7/sec8 span replacement")
assert cut > 0
ns = {}
exec(compile(src768[:cut], R768, "exec"), ns)
pairs768 = ns["pairs"]
rep = ns["rep"]
assert len(pairs768) >= 30, len(pairs768)

# --- ordered value-map (tokens first, then back-substitution) ---------------
TOK = [
    # band geometry (W155 values -> tokens)
    ("355_804..357_803", "@ABAND@"),      # W155 A band -> W156 A band
    ("357_804..358_003", "@BBAND@"),      # W155 B band -> W156 B band
    ("355_604..357_603", "@NABAND@"),     # naive A
    ("355_804..356_003", "@NBBAND@"),     # naive B
    ("355_604..355_803", "@PBBAND@"),     # prior-B cite (W154 B)
    ("355_803+1", "@ABASE@"),
    ("357_803+1", "@BBASE@"),
    # stats chains
    ("734,811", "@LEDG@"), ("732,611", "@NEFF@"),
    ("336,720", "@K1@"), ("338,920", "@K2@"),
    ("\u22120.094237", "@MU@"), ("0.3031", "@P95@"),
    # chinese ordinals
    ("一百五十三", "@CN1@"), ("一百五十二", "@CN2@"),
    ("第一百四十五", "@CN3@"), ("第七十一", "@CN4@"), ("第十四", "@CN5@"),
    # round / dir tokens (order: _r768bma before r768; r768 before r767)
    ("_r768bma", "@RDIR@"),
    ("r768", "@RW@"), ("r767", "@PRW@"),
    # seat identity
    ("MSG-2026-10-06-0943", "@SEATTS@"), ("1fedffbe4", "@SHA@"),
    ("3095cb47e", "@PSHA@"),
    # wave tokens (order: W156+/W156 captured before W155->W156)
    ("W156+", "@PROJ@"), ("W156", "@PROJW@"),
    ("W155", "@WN@"), ("W154", "@WP@"),
    ("w155", "@wn@"), ("w154", "@wp@"),
    # bare arabic contexts
    ("第 145 波", "@WAVE145@"), ("波号 155", "@BARE155@"),
    ("--wave 155", "@WAVEFLAG@"), ("行 144", "@R144@"),
    ("行 70", "@R70@"), ("70 行注册", "@ROWS70@"),
    ("泵第 153 枚", "@PUMP153@"), ("152 行", "@L152@"),
]
BACK = [
    ("@ABAND@", "358_004..360_003"), ("@BBAND@", "360_004..360_203"),
    ("@NABAND@", "357_804..359_803"), ("@NBBAND@", "358_004..358_203"),
    ("@PBBAND@", "357_804..358_003"),
    ("@ABASE@", "358_003+1"), ("@BBASE@", "360_003+1"),
    ("@LEDG@", "737,011"), ("@NEFF@", "734,811"),
    ("@K1@", "338,920"), ("@K2@", "341,120"),
    ("@MU@", "\u22120.092724"), ("@P95@", "0.3122"),
    ("@CN1@", "一百五十四"), ("@CN2@", "一百五十三"),
    ("@CN3@", "第一百四十六"), ("@CN4@", "第七十二"), ("@CN5@", "第十五"),
    ("@RDIR@", "_r769bma"),
    ("@RW@", "r769"), ("@PRW@", "r768"),
    ("@SEATTS@", "MSG-2026-10-06-1009"), ("@SHA@", "ffce2936f"),
    ("@PSHA@", "dde679c63"),
    ("@PROJ@", "W157+"), ("@PROJW@", "W157"),
    ("@WN@", "W156"), ("@WP@", "W155"),
    ("@wn@", "w156"), ("@wp@", "w155"),
    ("@WAVE145@", "第 146 波"), ("@BARE155@", "波号 156"),
    ("@WAVEFLAG@", "--wave 156"), ("@R144@", "行 145"),
    ("@R70@", "行 71"), ("@ROWS70@", "71 行注册"),
    ("@PUMP153@", "泵第 154 枚"), ("@L152@", "153 行"),
]


def valmap(s: str) -> str:
    for a, b in TOK:
        s = s.replace(a, b)
    for a, b in BACK:
        s = s.replace(a, b)
    return s


# --- six manual override needles (OLD = live W155 prereg text verbatim) -----
OVERRIDES = [
    ("W152=bm-a r764 freeze（520eb01ca）；W153=bm-a r766 freeze（33388e082）；W154=bm-a r767 freeze（3095cb47e·表尾）；**均已注册**（表尾 W154 行）。W155=本波 skip-past-published 链面零适用（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r768bma_w155_band_gate.json rc0 实跑）",
     "W152=bm-a r764 freeze（520eb01ca）；W153=bm-a r766 freeze（33388e082）；W154=bm-a r767 freeze（3095cb47e）；W155=bm-a r768 freeze（dde679c63·表尾）；**均已注册**（表尾 W155 行）。W156=本波 skip-past-published 链面零适用（本波 gate=单态门·pre-seat probe 与冻结窗 gate 双跑 derive 逐位恒等·ADMIT 回执 results/_r769bma_w156_band_gate.json rc0 实跑）"),
    ("全 inbox/processed/ W155 席位零外机命中（本机席位公示=MSG-2026-10-06-0943-bma-w155-seat 已推 origin 1fedffbe4 先于本冻结【r565 律·推送窗=direct delivery 1fedffbe4（r768 pre-seat push·behind-2 bm-c r610 guard-round peer merge 吸收后快进送达·零 --no-verify）+同窗 self-ack inbox→processed 移位 r768】",
     "全 inbox/processed/ W156 席位零外机命中（本机席位公示=MSG-2026-10-06-1009-bma-w156-seat 已推 origin ffce2936f 先于本冻结【r565 律·推送窗=direct delivery ffce2936f（r769 pre-seat push·快进送达 behind-0 at fetch·零 merge 零 --no-verify）；self-ack inbox→processed 移位待 W156 finalize 收口窗】"),
    ("**席位推送窗实录（r768 窗口实况）**：席位+probe 回执单 commit、W154 finalize 收口产物同窗随 merge 吸收推送 origin 送达 **1fedffbe4**（推送窗 behind-2 bm-c r610 guard-round peer merge 吸收后快进送达·零 --no-verify；同窗 self-ack inbox→processed 移位 r768 再推送达）。> **序数机面锚注记**：本波 ordinal=第一百四十五引擎波·bm-a 第七十一枚自有波【机面 derive：engine_owner==bm-a 行 70+本候选以 gate leg0 机证为准】。",
     "**席位推送窗实录（r769 窗口实况）**：席位+probe 回执单 commit 推送 origin 送达 **ffce2936f**（direct delivery 快进送达·behind-0 at fetch·零 merge 零 --no-verify；self-ack inbox→processed 移位待 W156 finalize 收口窗）。> **序数机面锚注记**：本波 ordinal=第一百四十六引擎波·bm-a 第七十二枚自有波【机面 derive：engine_owner==bm-a 行 71+本候选以 gate leg0 机证为准】。"),
    ("4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W154 先例·W136 +0.0000/W137 +0.0000/W138 −0.0002/W139 +0.0000/W140 +0.0000/W141 +0.0001/W143 +0.0001/W144 +0.0000/W145 +0.0000/W146 +0.0000/W147 −0.0001/W148 +0.0000/W149 +0.0002/W150 +0.0000/W151 +0.0002/W152 +0.0001/W153 −0.0002/W154 **−0.0002** 如实披露；键 W154 实测 K-lift **−0.0002**【line_merged@K336,720 **1.1805**·line_pre 1.1807·n_eff 732,611；se_mu 收窄键 W140 0.000443→W141 0.000441→W142 0.000440→W143 0.000438→W144 0.000437→W145 0.000435→W146 0.000434→W147 0.000432→W148 0.000431→W149 0.000429→W150 0.000428→W151 0.000426→W152 0.000425→W153 0.000424→W154 **0.000422**】）。",
     "4. K-lift 线移动幅度 **≤±0.02**（累计池加深零 se_mu 收窄线自 mu/sigma 微调面非质变——W136..W155 先例·W136 +0.0000/W137 +0.0000/W138 −0.0002/W139 +0.0000/W140 +0.0000/W141 +0.0001/W143 +0.0001/W144 +0.0000/W145 +0.0000/W146 +0.0000/W147 −0.0001/W148 +0.0000/W149 +0.0002/W150 +0.0000/W151 +0.0002/W152 +0.0001/W153 −0.0002/W154 −0.0002/W155 **−0.0002** 如实披露；键 W155 实测 K-lift **−0.0002**【line_merged@K338,920 **1.1805**·line_pre 1.1807·n_eff 734,811；se_mu 收窄键 W140 0.000443→W141 0.000441→W142 0.000440→W143 0.000438→W144 0.000437→W145 0.000435→W146 0.000434→W147 0.000432→W148 0.000431→W149 0.000429→W150 0.000428→W151 0.000426→W152 0.000425→W153 0.000424→W154 0.000422→W155 **0.000421**】）。"),
    ("T-2026-10-01-141 s1 引擎线第 145 波【bm-a 第七十一枚自有波【机面 derive：engine_owner==bm-a 行 70+本候选以 gate leg0 机证为准·同 W151/W152/W153/W154 最近自有波】。（波号=注册表 W154 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-06-0943-bma-w155-seat 先推 origin 1fedffbe4 r565 律",
     "T-2026-10-01-141 s1 引擎线第 146 波【bm-a 第七十二枚自有波【机面 derive：engine_owner==bm-a 行 71+本候选以 gate leg0 机证为准·同 W152/W153/W154/W155 最近自有波】。（波号=注册表 W155 行后首个自由号·单态零席位空档；中位公示 MSG-2026-10-06-1009-bma-w156-seat 先推 origin ffce2936f r565 律"),
    ("engine_owner==bm-a 70 行注册 + 本候选——以 gate leg0 机证为准·同 W151/W152/W153/W154 最近自有波",
     "engine_owner==bm-a 71 行注册 + 本候选——以 gate leg0 机证为准·同 W152/W153/W154/W155 最近自有波"),
]
OVERRIDES_OLD = {o for o, _ in OVERRIDES}


def build_pair(old768: str, new768: str):
    """old768/new768 = r768's pair. W156 pair = (new768, ...) with overrides."""
    if new768 in OVERRIDES_OLD:
        for o, n in OVERRIDES:
            if o == new768:
                return (o, n)
    return (new768, valmap(new768))


pairs156 = [build_pair(o, n) for o, n in pairs768]
# drop pairs whose OLD text lives inside the sec7/8 span (backfilled blocks)
span_probe = [p for p in pairs156 if "占位" in p[0] or "回填" in p[0][:60]]
assert span_probe == [], f"unexpected span-coupled needles: {span_probe}"

src = io.open(r"research/PERPETUAL_N1_W155_PREREG.md", encoding="utf-8").read()
inter = rep(src, pairs156, "w156-prereg-xform")

# --- sec7/sec8 span replacement: r769 backfilled blocks -> W156 placeholders --
i7 = inter.find("## §7 跑后实证。【finalize 收口机械回填·bm-a r769")
i8 = inter.find("## §8 批后复盘。【finalize 同窗回填·bm-a r769")
ifin = inter.find("- **跑前冻结=本件 commit**")
assert i7 > 0 and i8 > i7 and ifin > i8, f"sec7/8 span anchors missing: {i7},{i8},{ifin}"
sec7_block, sec8_block = inter[i7:i8], inter[i8:ifin]
assert "n1_w155_results.json 冻结实测键" in sec7_block and "0.3122" in sec7_block \
    and "mu_delta_w155_vs_w154ext" in sec7_block, "sec7 backfill face drift"
assert "W156+ 投影承接" in sec8_block and "本批无新宝藏" in sec8_block, "sec8 backfill face drift"
ph7 = ("## §7 跑后实证。【finalize 收口机械回填·占位——跑前为空】\n"
       "- （占位：12/12 分片落地后 finalize one-pass 机械回填·回填限本节与 §8·judged 断言照 W155 例。）\n\n")
ph8 = ("## §8 批后复盘。【finalize 同窗回填·占位】\n"
       "- （占位：设计复用面+宝藏捕获问+W157+ 投影承接三行照 W155 例回填。）\n\n")
out = inter[:i7] + ph7 + ph8 + inter[ifin:]
assert out.count("占位：12/12") == 1 and out.count("占位：设计复用面") == 1, "placeholder splice drift"
assert "同窗即回填（r763..r768 窗先例延续" not in out, "backfilled sec7 residue"

# --- two-form checklist -------------------------------------------------------
assert out.count("波号 155") == 0, "bare wave number residue (r754 law)"
assert out.count("n1_w155") == 1, "n1_w155 must appear exactly once (sec5 prior-wave key)"
assert out.count("results/perpetual_faces/n1_w155_results.json·N1 面最新已落账键") == 1, "sec5 anchor context"
assert out.count("n1w155") == 0, "lowercase entry token residue (r754 law)"
assert out.count("PERPETUAL-N1-W155") == 0, "batch name residue"
assert out.count("1fedffbe4") == 0, "stale seat sha residue"
assert out.count("355_804..357_803") == 0, "stale W155 A-band residue"
assert out.count("357_804..358_003") == 1 and \
    out.count("被已注册 W155 B 带 357_804..358_003 **拒**") == 1, \
    "W155 B-band must appear exactly once as prior-wave cite"
assert out.count("357_804..359_803") >= 1 and out.count("358_004..358_203") >= 1, "naive faces"
assert "波号 156=注册表 W155 行后首个自由号" in out and "358_004..360_003" in out \
    and "360_004..360_203" in out and "PERPETUAL-N1-W156" in out, "new W156 facts missing"
assert out.count("737,011") >= 1 and out.count("341,120") == 1 and out.count("0.3122") == 1 \
    and out.count("\u22120.092724") == 1, "W156 stat anchors missing"

io.open(r"research/PERPETUAL_N1_W156_PREREG.md", "w", encoding="utf-8", newline="\n").write(out)
print("W156 prereg written:", len(out), "chars |", len(pairs156), "needle pairs, all count==1 |",
      "sec7/8 span-replaced", len(sec7_block) + len(sec8_block), "->", len(ph7) + len(ph8), "bytes")
