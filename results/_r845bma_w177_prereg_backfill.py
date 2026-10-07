# -*- coding: utf-8 -*-
"""r845 bm-a W177 prereg sec7/sec8 mechanical backfill (the ONLY legal
post-freeze edit face; W159/W168/W169 delayed-window precedent -- the
r843 dead-tail session died pre-commit, r844 adopted the finalize
products but the sec7/sec8 backfill slipped to this window).
All displayed values machine-read this window from
results/perpetual_faces/n1_w177_results.json +
results/_r845bma_w177_three_gate.json (fresh re-derive, r587 law).
Single-file fresh-read-modify-write (multi-writer law); CRLF preserved.
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
P = r"research\PERPETUAL_N1_W177_PREREG.md"
NL = "\r\n"

res = json.load(io.open(r"results\perpetual_faces\n1_w177_results.json",
                        encoding="utf-8"))
npc = res["null_pool_cumulative"]
kl = res["skill_line_v2_k_lift"]
fam = res["families"]["A_random_engine_exit"]
tg = json.load(io.open(r"results\_r845bma_w177_three_gate.json", encoding="utf-8"))
MIN = "\u2212"

def f6(x):
    return ("%.6f" % x).replace("-", MIN)

def f4(x):
    return ("%.4f" % x).replace("-", MIN)

assert npc["merged"]["n_values"] == 387320
assert kl["line_merged_387320"] == 1.1847 and kl["line_delta_k_lift"] == 0.0001
assert fam["full_sharpe_p95"] == 0.3116
pk = tg["finalize"]["pred_keys"]

SEC7 = (
    "## §7 跑后实证。【finalize 收口机械回填·已回填 r845 窗（r844 dead-tail 收养窗三闸内联首跑"
    "+本窗机读补件复跑值恒等·拖延窗先例 W159/W168/W169 同律·如实注记）】" + NL +
    "- **合并池**：pre-W177 K=385,120（mu=" + f6(npc["pre_w177_cumulative"]["mu"]) +
    "·sigma=" + f6(npc["pre_w177_cumulative"]["sigma"]) + "）→ W177-only K=2,200（mu=" +
    f6(npc["w177_only"]["mu"]) + "·sigma=" + f6(npc["w177_only"]["sigma"]) +
    "）→ **merged K=387,320（mu=" + f6(npc["merged"]["mu"]) + "·sigma=" +
    f6(npc["merged"]["sigma"]) + "）**；账本 prev=**793,105**（届时空窗活链头 runtime derive）"
    "+2,200=**795,305**（voids_applied=本波无〔键 None·机读如实〕·"
    "file=results/perpetual_faces/n1_w177_results.json·evidence_cutoff=2026-09-22）。" + NL + NL +
    "- **skill_line_v2 K-lift**（n_eff 恒等 793,105）：" +
    "%.4f" % kl["line_pre_w177"] + " → **" + "%.4f" % kl["line_merged_387320"] +
    "**（Δ **+" + "%.4f" % kl["line_delta_k_lift"] +
    "**·nulls-deepening 纯零显著质变如实注记）；se_mu 收窄链 W173 0.000398→W174 0.000397→"
    "W175 0.000396→W176 0.000395→**0.000394**（=0.245080/√387,320·results 键 "
    "se_mu_at_k387320）。" + NL + NL +
    "- **A 档 full_sharpe_p95=" + "%.4f" % fam["full_sharpe_p95"] +
    "**（2,000 runs·W176 键 0.3118 机读）→差 **" + MIN + "0.0002**·<0.05 门过·"
    "抽样波动面如实披露；A p99=" + "%.4f" % fam["full_sharpe_p99"] + "。" + NL + NL +
    "- **§5 四预键全过（机证）**：①|W177-only mu − merged mu|=" +
    ("%.4f" % pk["1_mu_gap"]).lstrip("0") + "<0.02 ✓ ②sigma 相对变化 +" +
    ("%.4f" % pk["2_sigma_rel_pct"]).lstrip("0") + "%<±10% ✓ ③A p95 差 " + MIN +
    "0.0002<0.05 ✓ ④K-lift +0.0001≤±0.02 ✓。" + NL + NL +
    "- **canon flip：NOT performed**（K2,200 同例法·治理提案面 only·结果如实注记）。" + NL + NL +
    "- 审计：12 shards 零重叠连续覆盖 A[0,2000)/B[0,200)·n_backtests 合计 2,200·machine=bm-a·"
    "audit.finalize_only=true·批内波间漂移键 mu_delta_w177_vs_w176ext=**" +
    ("%.6f" % npc["mu_delta_w177_vs_w176ext"]).replace("-", MIN) +
    "**；三闸 r752 回执=results/_r845bma_w177_three_gate.json PASS（A 2,000/B 200 半开无缝 "
    "tiling 分片机读·r844 收养窗内联首跑+本窗补件复跑值恒等·种子连续性 A 404204..406203 唯一/"
    "B-exit 406204..406403==注册带/B-entry 404204..404403=W176 同族设计）。"
)

SEC8 = (
    "## §8 批后复盘。【finalize 同窗回填·已回填 r845 窗（dead-tail 拖延窗先例同律·如实注记）】" + NL +
    "- **§5.5 W178+ 投影承接（r841 probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean "
    "406_204..408_203 CLEAN（hops=0）；B first-clean 406_404..406_603 CLEAN（hops=0）——"
    "naive B 落在 naive A 窗内（W141 同窗互斥先例适用于 W178：W178 冻结方必须在 post-W177 "
    "注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W177 B 带 "
    "406_204..406_403 注册后已拒 naive W178 A 窗**（本波已落账注册=拒绝面现实——r844 probe "
    "实跑证实：A 406_204..408_203 起点即被拒→1 hop 落 406_404..408_403=阶梯第三十八例）——"
    "W178 A 重 derive 同强制（越过 W177 B 带·阶梯 A-hops-prior-B 继承第三十八例）；"
    "verify at W178 prereg，hop 链逐跳在 probe 回执。" + NL + NL +
    "- 宝藏/方法论捕获问（O-20261003-2030/O-20261002-2100 收口步）：本波测量加深零新方法零新宝藏"
    "（nulls-deepening 例波·设计 verbatim 复用·如实注记）；dead-tail finalize 收养三重门面"
    "（r752 三闸+r381 origin 无孪生+r708 零活进程）r844 窗已立法在册。" + NL + NL +
    "- 诚实披露面：本波 full-lifecycle 多窗节律（prereg r842 窗建→冻结 r843 窗 commit c06cc230f→"
    "引擎 tick 自燃→finalize=r844 窗收口）；**finalize 收口窗遭遇 dead-tail 会话窗**（r843 会话"
    "写 state 21:20 后跑 finalize 21:28:50、pre-commit 死亡——r844 窗三重门收养〔零活 finalize "
    "进程+origin 无孪生+三 identity 门全绿〕churn-absorb 落 origin；§7/§8 回填顺延至 r845 窗="
    "拖延窗先例同律·如实注记）。"
)

src = io.open(P, encoding="utf-8", newline="").read()
old7 = ("## §7 跑后实证。【finalize 收口机械回填·待 W177 finalize 窗】" + NL +
        "- （占位·finalize one-pass 后机械回填：账本恒等式+合并池 K+merged mu/w-only mu/"
        "mu_delta+sigma+se_mu+skill_line_v2 K-lift+A 档 p95+§5 四预键机证+canon flip 态+"
        "audit.finalize_only+voids_applied。）")
old8 = ("## §8 批后复盘。【finalize 同窗回填·待 W177 finalize 窗】" + NL +
        "- （占位·§5.5 W178+ 投影承接+宝藏/方法论捕获问+诚实披露面·finalize 收口窗机械回填。）")
assert src.count(old7) == 1, ("sec7 anchor", src.count(old7))
assert src.count(old8) == 1, ("sec8 anchor", src.count(old8))
out = src.replace(old7, SEC7).replace(old8, SEC8)
assert "待 W177 finalize 窗" not in out, "stale placeholder remains"
assert out.count("已回填 r845 窗") == 2
io.open(P, "w", encoding="utf-8", newline="").write(out)
chk = io.open(P, encoding="utf-8", newline="").read()
assert chk == out, "write roundtrip drift"
print("sec7/sec8 backfill landed: %d -> %d bytes (CRLF preserved, anchors 1+1)" %
      (len(src.encode("utf-8")), len(out.encode("utf-8"))))
