# -*- coding: utf-8 -*-
"""r779 bm-a W159 per-wave prereg xform: research/PERPETUAL_N1_W158_PREREG.md
-> research/PERPETUAL_N1_W159_PREREG.md. Needle-asserted (r745 extract-vs-insert
law, every needle count==1 measured); two-form checklist enforced at the tail.
Derived from the r773 xform pair chain: OLD side = r773 NEW strings verbatim (=
the live W158 prereg text incl. the r778 backfilled sec7/8), NEW side = ordered
whole-string value-map (r773 pit law: composite carriers tokenized WHOLE, bare
prefixes LAST) + two live-text sec3 seed-scale overrides.
W159 facts (probe/gate machine-derived, receipts on disk): A=364_604..366_603
(staircase EIGHTEENTH instance E36, hops=1; naive 364_404..366_403 refused at
own start by registered W158 B band 364_404..364_603) + B=366_604..366_803
(own-A mutual exclusion, hops=1; naive 364_604..364_803); seat
MSG-2026-10-06-142x-bma-w159-seat -> origin 7b60d09da (r779 pre-seat push via
merge-absorb window: 6 daemon commits absorbed, zero --no-verify); band gate
ADMIT receipt results/_r779bma_w159_band_gate.json rc0; pre-seat probe r779
receipt. W158 finalize = bm-a r778 one-pass (sec7/sec8 backfilled), ledger head
753,012, K=345,520 merged pool; W158-only mu -0.100651 / merged mu -0.092893
(rounded anchor -0.0929) / sigma 0.245045 (0.2450) / A p95 0.2999 / K-lift
+0.0000 @line 1.1818->1.1818 / se_mu 0.000417 / n_eff 750,812 (all from
results/perpetual_faces/n1_w158_results.json measured keys; ledger head from
science_gates.ledger_head())."""
import io

R773 = "results/_r773bma_w158_prereg_xform.py"
src773 = io.open(R773, encoding="utf-8").read()
cut = src773.find("\n# --- apply")
assert cut > 0
ns = {}
exec(compile(src773[:cut], R773, "exec"), ns)
pairs158 = ns["pairs158"]
rep = ns["rep"]
assert len(pairs158) >= 30, len(pairs158)

LIVE = r"research/PERPETUAL_N1_W158_PREREG.md"
live = io.open(LIVE, encoding="utf-8").read()

# --- machine-derived facts (r587: read from on-disk receipts) ----------------
import sys, os
sys.path.insert(0, ".")
sys.path.insert(0, "research")
sys.path.insert(0, "scripts")
import science_gates
head = science_gates.ledger_head()
assert head["total"] == 753012 and head["file"].endswith("n1_w158_results.json"), head
r158 = science_gates.json  # placeholder guard, replaced below
import json as _json
w158res = _json.load(open("results/perpetual_faces/n1_w158_results.json",
                          encoding="utf-8"))
npc = w158res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 345520
assert round(npc["merged"]["mu"], 4) == -0.0929 and npc["w158_only"]["mu"] == -0.100651
assert npc["se_mu_at_k345520"] == 0.000417
kl = w158res["skill_line_v2_k_lift"]
assert kl["n_eff_held_equal"] == 750812 and kl["line_delta_k_lift"] == 0.0
assert kl["line_pre_w158"] == 1.1818 and kl["line_merged_345520"] == 1.1818
gate = _json.load(open("results/_r779bma_w159_band_gate.json", encoding="utf-8"))
leg1 = gate["legs"]["leg1"]
assert leg1["A"] == [364604, 366603] and leg1["hops_A"] == 1, leg1
assert leg1["B"] == [366604, 366803] and leg1["hops_B"] == 1, leg1
assert leg1["B_naive_first_clean"] == [364604, 364803], leg1
leg3 = gate["legs"]["leg3"]
assert leg3["W160p_A"] == "366604..368603" and leg3["W160p_B"] == "366804..367003", leg3

# --- ordered value-map (composite carriers WHOLE, bare prefixes LAST) --------
TOK = [
    # freeze-list cluster (historical rounds must NOT shift)
    ("W154=bm-a r767 freeze（3095cb47e）；W155=bm-a r768 freeze（dde679c63）；W156=bm-a r771 freeze（13c989ba0）；W157=bm-a r772 freeze（aed41df3e·表尾）", "@FL@"),
    # seat-push honesty faces (r779 window = merge-absorb, not direct delivery)
    ("席位+probe 回执+W157 finalize 收口件单 commit 推送 origin 送达 **24aff72f5**（direct delivery 快进送达·behind-0 at fetch·零 merge 零 --no-verify；self-ack", "@PUSH2@"),
    ("推送窗=direct delivery 24aff72f5（r773 pre-seat push·快进送达 behind-0 at fetch·零 merge 零 --no-verify）", "@PUSH1@"),
    # gate-leg3 + sec8-succession composite (r772=gate window -> r773; r773=sec8 window -> r778)
    ("r772 gate leg3+r773 §8 承接", "@G@"),
    # W157-finalize round cites (W158 finalize was r778, not the freeze round)
    ("W157 finalize one-pass bm-a r773·§7/§8 回填 r773 同窗收口】", "@FIN0@"),
    ("one-pass·bm-a r773·§7/§8 回填 r773 同窗收口】", "@FIN5@"),
    # sec5 item-4 K-lift + se_mu chain composites (chain extension W157 -> +W158)
    ("+0.0001/W157 **+0.0002** 如实披露；键 W157 实测 K-lift **+0.0002**【line_merged@K343,320 **1.1811**·line_pre 1.1809·n_eff 739,211；", "@KL1@"),
    ("→W155 0.000421→W156 0.000420→W157 **0.000418**】", "@SE@"),
    # recent-own-waves window shift (both occurrences share the whole string)
    ("同 W154/W155/W156/W157 最近自有波", "@OWN4@"),
    # band geometry (W158 values -> tokens)
    ("362_404+j", "@SEEDA@"),             # W158 A seed base -> W159 A seed base
    ("364_404+j", "@SEEDB@"),             # W158 B seed base -> W159 B seed base
    ("364_404..366_403", "@NA159P@"),    # W159+ projected naive A -> W160+ projection
    ("364_604..364_803", "@NB159P@"),    # W159+ projected naive B -> W160+ projection
    ("362_404..364_403", "@ABAND@"),     # W158 A band -> W159 A band
    ("364_404..364_603", "@BBAND@"),     # W158 B band -> W159 B band
    ("362_204..364_203", "@NABAND@"),    # W158 naive A -> W159 naive A
    ("362_404..362_603", "@NBBAND@"),    # W158 naive B -> W159 naive B
    ("362_204..362_403", "@PBBAND@"),    # prior-B cite (W157 B) -> W158 B cite
    ("362_403+1", "@ABASE@"),
    ("364_403+1", "@BBASE@"),
    # stats chains
    ("741,411", "@LEDG@"), ("739,211", "@NEFF@"),
    ("343,320", "@K1@"), ("345,520", "@K2@"),
    ("\u22120.096645", "@MU@"), ("0.3039", "@P95@"), ("\u22120.0928", "@MU4@"),
    # chinese ordinals
    ("一百五十六", "@CN0@"), ("一百五十五", "@CN1@"),
    ("第一百四十八", "@CN3@"), ("第七十四", "@CN4@"), ("第十七", "@F16@"),
    # round / dir tokens (order: _r773bma before r773; r773 before r772 residue)
    ("_r773bma", "@RDIR@"),
    ("r773", "@RW@"), ("r772", "@PRW@"),
    # seat identity
    ("MSG-2026-10-06-120x", "@SEATTS@"), ("24aff72f5", "@SEATSHA@"),
    # wave tokens (order: W159+ before W159; W159 before W158; W158 before W157)
    ("W159+", "@PROJ@"), ("W159", "@PROJW@"),
    ("W158", "@WN@"), ("W157", "@WP@"),
    ("w158", "@wn@"), ("w157", "@wp@"),
    # bare arabic contexts
    ("第 148 波", "@WAVE146@"), ("波号 158", "@BARE157@"),
    ("--wave 158", "@WAVEFLAG@"), ("行 147", "@R145@"),
    ("行 73", "@R71@"), ("73 行注册", "@ROWS71@"),
    ("泵第 156 枚", "@PUMP154@"), ("155 行", "@L153@"),
]
BACK = [
    ("@FL@", "W155=bm-a r768 freeze（dde679c63）；W156=bm-a r771 freeze（13c989ba0）；W157=bm-a r772 freeze（aed41df3e）；W158=bm-a r775 freeze（6957f509e·表尾）"),
    ("@PUSH2@", "席位+probe 回执单 commit 推送——origin 同窗已进 6 daemon commit→fetch→merge 吸收→重推送达 **7b60d09da**（merge-absorb 窗·behind-0 at fetch 复核·零 --no-verify；self-ack"),
    ("@PUSH1@", "推送窗=pre-seat push 经 merge-absorb 窗送达 7b60d09da（r779 pre-seat push·origin 同窗已进 6 daemon commit→fetch→merge 吸收→重推·behind-0 at fetch 复核·零 --no-verify）"),
    ("@G@", "r773 gate leg3+r778 §8 承接"),
    ("@FIN0@", "W158 finalize one-pass bm-a r778·§7/§8 回填 r778 同窗收口】"),
    ("@FIN5@", "one-pass·bm-a r778·§7/§8 回填 r778 同窗收口】"),
    ("@KL1@", "+0.0001/W157 +0.0000/W158 **+0.0000** 如实披露；键 W158 实测 K-lift **+0.0000**【line_merged@K345,520 **1.1818**·line_pre 1.1818·n_eff 750,812；"),
    ("@SE@", "→W155 0.000421→W156 0.000420→W157 0.000418→W158 **0.000417**】"),
    ("@OWN4@", "同 W155/W156/W157/W158 最近自有波"),
    ("@NA159P@", "366_604..368_603"), ("@NB159P@", "366_804..367_003"),
    ("@ABAND@", "364_604..366_603"), ("@BBAND@", "366_604..366_803"),
    ("@SEEDA@", "364_604+j"), ("@SEEDB@", "366_604+j"),
    ("@NABAND@", "364_404..366_403"), ("@NBBAND@", "364_604..364_803"),
    ("@PBBAND@", "364_404..364_603"),
    ("@ABASE@", "364_603+1"), ("@BBASE@", "366_603+1"),
    ("@LEDG@", "753,012"), ("@NEFF@", "750,812"),
    ("@K1@", "345,520"), ("@K2@", "347,720"),
    ("@MU@", "\u22120.100651"), ("@P95@", "0.2999"), ("@MU4@", "\u22120.0929"),
    ("@CN0@", "一百五十七"), ("@CN1@", "一百五十六"),
    ("@CN3@", "第一百四十九"), ("@CN4@", "第七十五"), ("@F16@", "第十八"),
    ("@RDIR@", "_r779bma"),
    ("@RW@", "r779"), ("@PRW@", "r773"),
    ("@SEATTS@", "MSG-2026-10-06-142x"), ("@SEATSHA@", "7b60d09da"),
    ("@PROJ@", "W160+"), ("@PROJW@", "W160"),
    ("@WN@", "W159"), ("@WP@", "W158"),
    ("@wn@", "w159"), ("@wp@", "w158"),
    ("@WAVE146@", "第 149 波"), ("@BARE157@", "波号 159"),
    ("@WAVEFLAG@", "--wave 159"), ("@R145@", "行 148"),
    ("@R71@", "行 74"), ("@ROWS71@", "74 行注册"),
    ("@PUMP154@", "泵第 157 枚"), ("@L153@", "156 行"),
]


def valmap(s: str) -> str:
    for a, b in TOK:
        s = s.replace(a, b)
    for a, b in BACK:
        s = s.replace(a, b)
    return s


# --- sec3 A/B lines: already carried by pairs158 (r773 live-text append
# entries); the seed-scale values ride the @SEEDA@/@SEEDB@ whole tokens. Verify
# the valmap output for those two pairs before the apply pass.
pairs159 = [(n158, valmap(n158)) for (_o157, n158) in pairs158]
_sec3a_new = [n for o, n in pairs159 if o.startswith("- **A 档**")][0]
_sec3b_new = [n for o, n in pairs159 if o.startswith("- **B 档**")][0]
assert "entry rng seed=**364_604+j**" in _sec3a_new and \
    "法典 §4 W159 行 A=364_604..366_603" in _sec3a_new and "阶梯第十八例" in _sec3a_new, \
    "sec3-A valmap drift"
assert "entry rng=**364_604+j**" in _sec3b_new and \
    "exit rng=**366_604+j**" in _sec3b_new and \
    "法典 §4 W159 行 B=366_604..366_803" in _sec3b_new and \
    "r773 gate leg3+r778 §8 承接 W159+ 投影 re-derive-MANDATORY" in _sec3b_new, \
    "sec3-B valmap drift"

# --- apply ---------------------------------------------------------------------
span_probe = [p for p in pairs159 if "占位" in p[0] or "回填" in p[0][:60]]
assert span_probe == [], f"unexpected span-coupled needles: {span_probe}"

inter = rep(live, pairs159, "w159-prereg-xform")

# --- sec7/sec8 span replacement: r778 backfilled blocks -> W159 placeholders --
i7 = inter.find("## §7 跑后实证。【finalize 收口机械回填·bm-a r778")
i8 = inter.find("## §8 批后复盘。【finalize 同窗回填·bm-a r778")
ifin = inter.find("- **跑前冻结=本件 commit**")
assert i7 > 0 and i8 > i7 and ifin > i8, f"sec7/8 span anchors missing: {i7},{i8},{ifin}"
sec7_block, sec8_block = inter[i7:i8], inter[i8:ifin]
assert "n1_w158_results.json 冻结实测键" in sec7_block and "0.2999" in sec7_block \
    and "mu_delta_w158_vs_w157ext" in sec7_block, "sec7 backfill face drift"
assert "W159+ 投影承接" in sec8_block and "本批无新宝藏" in sec8_block, "sec8 backfill face drift"
ph7 = ("## §7 跑后实证。【finalize 收口机械回填·占位——跑前为空】\n"
       "- （占位：12/12 分片落地后 finalize one-pass 机械回填·回填限本节与 §8·judged 断言照 W158 例。）\n\n")
ph8 = ("## §8 批后复盘。【finalize 同窗回填·占位】\n"
       "- （占位：设计复用面+宝藏捕获问+W160+ 投影承接三行照 W158 例回填。）\n\n")
out = inter[:i7] + ph7 + ph8 + inter[ifin:]
assert out.count("占位：12/12") == 1 and out.count("占位：设计复用面") == 1, "placeholder splice drift"
assert "mu_delta_w158_vs_w157ext" not in out, "backfilled sec7 residue"
assert "bm-a r778·one-pass rc0" not in out, "backfilled sec7 heading residue"

# --- two-form checklist -------------------------------------------------------
assert out.count("波号 158") == 0, "bare wave number residue (r754 law)"
assert out.count("n1_w158") == 1, "n1_w158 must appear exactly once (sec5 prior-wave key)"
assert out.count("results/perpetual_faces/n1_w158_results.json·N1 面最新已落账键") == 1, "sec5 anchor context"
assert out.count("n1w158") == 0, "lowercase entry token residue (r754 law)"
assert out.count("PERPETUAL-N1-W158") == 0, "batch name residue"
assert out.count("24aff72f5") == 0, "stale seat sha residue"
assert out.count("362_404..364_403") == 0, "stale W158 A-band residue"
assert out.count("364_404..364_603") == 1 and \
    out.count("被已注册 W158 B 带 364_404..364_603 **拒**") == 1, \
    "W158 B-band must appear exactly once as prior-wave cite"
assert out.count("364_404..366_403") >= 1 and out.count("364_604..364_803") >= 1, "naive faces"
assert out.count("\u22120.0929") == 1, "prior merged-mu 4dp anchor count"
assert "波号 159=注册表 W158 行后首个自由号" in out and "364_604..366_603" in out \
    and "366_604..366_803" in out and "PERPETUAL-N1-W159" in out, "new W159 facts missing"
assert out.count("6957f509e") == 1 and out.count("7b60d09da") >= 2, "freeze/seat sha anchors missing"
assert out.count("753,012") >= 2 and out.count("347,720") == 1 and out.count("0.2999") == 1 \
    and out.count("\u22120.100651") == 1, "W159 stat anchors missing"
assert out.count("bm-a r778·§7/§8 回填 r778 同窗收口】") == 2, "W158-finalize round cite count"
assert out.count("bm-a r779·§7/§8 回填 r779 同窗收口】") == 0, "freeze-round leaked into finalize cite"
assert out.count("r773 gate leg3+r778 §8 承接") == 3, "gate/§8 succession composite count"
assert out.count("同 W155/W156/W157/W158 最近自有波") == 2, "recent-own-waves window"
assert out.count("+0.0000/W158 **+0.0000** 如实披露") == 1, "K-lift chain extension"
assert out.count("W157 0.000418→W158 **0.000417**】") == 1, "se_mu chain extension"
assert out.count("W158=bm-a r775 freeze（6957f509e·表尾）") == 1, "freeze-list W158 entry"
assert out.count("W154=bm-a r767 freeze") == 0, "freeze-list trim residue"
assert out.count("MSG-2026-10-06-142x") >= 2 and out.count("MSG-2026-10-06-120x") == 0, "seat ts residue"
assert "merge 吸收→重推" in out, "seat-push honesty face missing"
assert "366_604..368_603" in out and "366_804..367_003" in out, "W160+ projections missing"
assert "verify at W160 prereg" in out, "W160 verify line missing"

io.open(r"research/PERPETUAL_N1_W159_PREREG.md", "w", encoding="utf-8", newline="\n").write(out)
print("W159 prereg written:", len(out), "chars |", len(pairs159), "needle pairs, all count==1 |",
      "sec7/8 span-replaced", len(sec7_block) + len(sec8_block), "->", len(ph7) + len(ph8), "bytes")
