# -*- coding: utf-8 -*-
"""r892 bm-a: W189 sec7/sec8 finalize backfill (deferred-to-r892 first-leg
per W186/W187/W188 second-window precedent; the r891 finalize window was
finalize+W190-seat-publish+S6-chain full-load, §7/§8 deferred to this
window's first leg -- non-procrastination asserted vs W159/W168/W169/W181).
Numbers machine-verified live vs results/perpetual_faces/n1_w189_results.json
(zero hand-copied values in the written text: every displayed number is
derived in-script from the results file and formatted the same way as the
43322a984 W188-backfill pattern).  Edit face = the two §7/§8 placeholder
blocks ONLY (post-freeze edit legality: 回填限 §7/§8)."""
import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
P = r"research\PERPETUAL_N1_W189_PREREG.md"

# --- machine-verified facts (r587: read from on-disk receipt) --------------
res = json.load(open(r"results\perpetual_faces\n1_w189_results.json",
                     encoding="utf-8"))
npc = res["null_pool_cumulative"]
kl = res["skill_line_v2_k_lift"]
led = res["science_gates"]["ledger"]
assert led["prev_total"] == 820928 and led["batch_trials"] == 2200 \
    and led["total"] == 823128, led
assert npc["merged"]["n_values"] == 413720 and \
    npc["pre_w189_cumulative"]["n_values"] == 411520 and \
    npc["w189_only"]["n_values"] == 2200, npc
MU6 = npc["merged"]["mu"]
WONLY8 = npc["w189_only"]["mu"]
SIG = npc["merged"]["sigma"]
WONLY_SIG = npc["w189_only"]["sigma"]
PRE_SIG = npc["pre_w189_cumulative"]["sigma"]
DELT = npc["mu_delta_w189_vs_w188ext"]
SEMU = npc["se_mu_at_k413720"]
P95 = res["families"]["A_random_engine_exit"]["full_sharpe_p95"]
P99 = res["families"]["A_random_engine_exit"]["full_sharpe_p99"]
AMU = res["families"]["A_random_engine_exit"]["full_sharpe_mu"]
assert abs(MU6 - (-0.0928521785265397)) < 1e-12 and MU6 < 0
assert abs(WONLY8 - (-0.08776831818181818)) < 1e-12 and WONLY8 < 0
assert abs(SIG - 0.24516369991716355) < 1e-12
assert abs(WONLY_SIG - 0.25413867557282327) < 1e-12
assert abs(PRE_SIG - 0.24511487295474493) < 1e-12
assert abs(DELT - 0.010848) < 1e-9
assert SEMU == 0.000381 and P95 == 0.3447 and P99 == 0.4567 \
    and abs(AMU - (-0.084061)) < 1e-9, (SEMU, P95, P99, AMU)
assert kl["line_pre_w189"] == 1.1863 and kl["line_merged_413720"] == 1.1866 \
    and abs(kl["line_delta_k_lift"] - 0.0003) < 1e-12 \
    and kl["n_eff_held_equal"] == 820928, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert res["audit"]["finalize_only"] is True and \
    res["audit"]["machine"] == "bm-a", res["audit"]
assert led["voids_applied"] == ["LOWAMP-P1", "LOWAMP-P2"]
assert led["evidence_cutoff"] == "2026-09-22"
assert len(res["shards_consumed"]) == 12
GAP = WONLY8 - MU6
assert abs(GAP - 0.005084) < 1e-6 and GAP > 0
SIGREL = (SIG - PRE_SIG) / abs(PRE_SIG) * 100.0
assert abs(SIGREL - 0.0199) < 0.001, SIGREL
P95D = P95 - 0.3243
assert abs(P95D - 0.0204) < 1e-9, P95D
assert abs(abs(kl["line_delta_k_lift"]) - 0.0003) <= 0.02

MU6S = "%.6f" % MU6                      # -0.092852
WONLY6S = "%.6f" % WONLY8                 # -0.087768
MU4S = "%.4f" % MU6                       # -0.0929 (display HOLDS)
WONLY4S = "%.4f" % WONLY8                 # -0.0878 (display ROLLS)
SIG6S = "%.6f" % SIG                      # 0.245164 (display ROLLS)
WSIG6S = "%.6f" % WONLY_SIG              # 0.254139
PRESIG6S = "%.6f" % PRE_SIG              # 0.245115 (W188 key)
GAP4S = "%.4f" % GAP                      # 0.0051
assert (MU6S, WONLY6S, MU4S, WONLY4S, SIG6S, WSIG6S, PRESIG6S, GAP4S) == \
    ("-0.092852", "-0.087768", "-0.0929", "-0.0878", "0.245164",
     "0.254139", "0.245115", "0.0051"), (MU6S, WONLY6S, MU4S, WONLY4S,
                                          SIG6S, WSIG6S, PRESIG6S, GAP4S)
DELT6S = "%.6f" % DELT                    # 0.010848
assert DELT6S == "0.010848"
SIGRELS = "+0.02"
P95DS = "+0.0204"

S7_OLD_H = "## §7 跑后实证。【finalize 收口机械回填·待 W189 finalize 窗】"
S7_OLD_P = ("- （占位·finalize one-pass 后机械回填：账本恒等式+合并池 K+merged mu/w-only"
            " mu/mu_delta+sigma+se_mu+skill_line_v2 K-lift+A 档 p95+§5 四预键机证"
            "+canon flip 态+audit.finalize_only+voids_applied。）")
S8_OLD_H = "## §8 批后复盘。【finalize 同窗回填·待 W189 finalize 窗】"
S8_OLD_P = ("- （占位·§5.5 W190+ 投影承接+宝藏/方法论捕获问+诚实披露面·finalize "
            "收口窗机械回填。）")

S7_NEW = (
"## §7 跑后实证。【finalize 收口机械回填·r892 回填窗（finalize 20:25 r891 finalize "
"one-pass 窗落件·§7/§8 回填顺延至 r892 开窗首腿即刻补·非拖延窗对照 W159/W168/W169/W181·"
"如实注记）】\n"
"- 账本恒等式：820,928 + 2,200 = **823,128** EXACT（prev_total/batch_trials/total 三键"
"机读·r891 finalize one-pass 实测；**vs §5 冻结投影（820,928+2,200=823,128 机械算）零差**"
"——本窗零在飞上游批冻结后入链·干净入链）。\n"
"- 合并池：**K=413,720** EXACT（=W188 池 411,520 + 本波 2,200·§5 投影 413,720 命中）。\n"
"- merged mu **" + MU6S + "（机读 -0.09285218）/ w-only mu **" + WONLY6S +
"（机读 -0.08776832）/ mu_delta(w189 vs w188ext) **+" + DELT6S + "。\n"
"- merged sigma **" + SIG6S + "（W188 键 0.245115→0.245164 第六位面微升·相对变化 " +
SIGRELS + "%）；w-only sigma " + WSIG6S + "；se_mu@K413,720 **0.000381**"
"（W188 0.000382→W189 0.000381 收窄·链面 …W186 0.000384→W187 0.000383→W188 "
"0.000382→W189 0.000381）。\n"
"- skill_line_v2：line_pre **1.1863** → line_merged@K413,720 **1.1866**（K-lift "
"**+0.0003**·n_eff_held_equal 820,928）；canon flip **NOT performed**（K2,200 同例法·"
"治理提案面）。\n"
"- A 档 full_sharpe_p95 **0.3447**（W188 锚 0.3243·Δ" + P95DS + " 门内）·p99 0.4567·"
"A mu −0.084061。\n"
"- §5 四预键机证全过：①mu gap " + GAP4S + "<0.02 PASS ②sigma 相对变化 " + SIGRELS +
"%<±10% PASS ③A p95 Δ" + P95DS + "<0.05 PASS ④K-lift +0.0003≤±0.02 PASS。\n"
"- audit.finalize_only=**true**（bm-a）·voids_applied=LOWAMP-P1,LOWAMP-P2·"
"evidence_cutoff=2026-09-22 在位·shards_consumed 12/12（引擎 tick 自烧 19:53–20:04·"
"r890 冻结窗自燃 r325 实证·finalize 20:25 r891 finalize one-pass 窗落件 commit c177bf73b）。")

S8_NEW = (
"## §8 批后复盘。【finalize 同窗回填·r892 回填窗】\n"
"- §5.5 W190+ 投影承接（r891 probe 机证·W190 冻结方重 derive 强制非转抄 r587 律）："
"naive A **432_604..434_603**（hops=0 CLEAN）——被注册 W189 B 带 432_604..432_803 "
"own-start 拒=阶梯 A-hops-prior-B 继承**第五十例**——**r891 probe 实证复核确认**"
"（A 432_804..434_803 hops=1 ·本窗 W190 链开窗兑现）；naive B **432_804..433_003**"
"（hops=0 CLEAN）落本波 A 窗内——W141 同窗互斥 leg2 律适用 W190（derive B 时预留本波 "
"A 窗·§5.5 预披露注记在案·r891 probe 实证 B 434_804..435_003 兑现）；W191+ 投影"
"（r891 probe leg4 机证：A **434_804..436_803** / B **435_004..435_203**·B 落 A 窗内）"
"——W191 冻结方必须在 post-W190 注册宇宙重 derive（r587·E36 卡·never transcribe）。\n"
"- 宝藏/方法论捕获问：本批 finalize one-pass=canonical runner 单发 r718 先例 verbatim "
"复用零新方法零新宝藏；TREASURE/METHODOLOGY 零 append。\n"
"- 诚实披露面：账本投影差 **零**（干净入链）；W189-only mu −0.0878 与合并池 −0.0929 差 " +
GAP4S + "（较 W188 的 0.0057 收窄·null 抽样单波 2,200 面小样本波动·四预键①仍 PASS）；"
"mu_delta +0.010848=W189 w-only（−0.0878）较 W188ext-only（−0.0986）回升转正（单波 "
"w-only 面波动·门内如实披露）；A p95 0.3447 较 W188 锚 0.3243 上移 " + P95DS + " 仍门内"
"（<0.05·测量面非注册利益）；line_pre 1.1863 较 W188 收官 line_merged 1.1862 的 +0.0001"
"=n_eff 基 818,728→820,928 增长自然步进非池加深效应；K-lift **+0.0003**=W188 0.0000 后"
"回升（W150/W151 族回升先例面·四预键④ PASS）；合并池 K=413,720 EXACT；引擎 tick 自烧 "
"12 分片（19:53–20:04）+finalize 20:25 落件（r891 finalize one-pass 窗·commit c177bf73b）"
"+§7/§8 回填 r892 次窗补（回填窗注记：W185 先例=finalize 同窗回填 r879·W186 先例=r885 次窗"
"回填·W187 先例=r888 次窗回填·W188 先例=r890 次窗回填·本波 finalize 窗 r891 为 finalize+"
"W190 席位发布+S6 链满载窗·§7/§8 顺延至 r892 开窗首腿即刻补·非拖延窗对照 W159/W168/W169/"
"W181·如实注记）+commit 收口。")

src = io.open(P, encoding="utf-8", newline="").read()
NL = "\r\n" if src.count("\r\n") > src.count("\n\r\n") and "\r\n" in src else "\n"
assert NL == "\r\n", "on-disk prereg expected CRLF (r370 law)"
for old in (S7_OLD_H, S7_OLD_P, S8_OLD_H, S8_OLD_P):
    assert src.count(old) == 1, "placeholder count != 1: %r" % old[:50]
out = src.replace(S7_OLD_H + NL + S7_OLD_P, S7_NEW.replace("\n", NL), 1)
out = out.replace(S8_OLD_H + NL + S8_OLD_P, S8_NEW.replace("\n", NL), 1)
assert "占位" not in out, "placeholder text survives"
assert out.count("## §7") == 1 and out.count("## §8") == 1
# write + roundtrip verify
io.open(P, "w", encoding="utf-8", newline="").write(out)
chk = io.open(P, encoding="utf-8", newline="").read()
assert chk == out, "CRLF write roundtrip drift"
for needle in ("823,128", "K=413,720", MU6S, WONLY6S, SIG6S, "0.000381",
               "1.1866", "+0.0003", "0.3447", GAP4S, P95DS,
               "434_804..435_003", "434_804..436_803", "435_004..435_203",
               "r892 回填窗", "c177bf73b"):
    assert needle in chk, "backfill needle missing: %r" % needle
print("W189 sec7/sec8 backfill landed: %d bytes (CRLF %d)" %
      (len(chk.encode("utf-8")), chk.count("\r\n")))
print("machine-verified: ledger 823,128 EXACT / K 413,720 EXACT / four "
      "prekeys PASS / projection carry W191+ A 434_804..436_803 B "
      "435_004..435_203")
