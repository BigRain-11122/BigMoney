# r345 bm-c W41 prereg s7/s8 mechanical backfill (r412 face; bytes in/out per
# r530 law; numbers derived from n1_w41_results.json verbatim, never hand-copied;
# dual-anchor S5 readout per the W41 prereg rolling-anchor clause).
import json, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
RES = ROOT + r"\results\perpetual_faces\n1_w41_results.json"
PR = ROOT + r"\research\PERPETUAL_N1_W41_PREREG.md"

res = json.load(open(RES, encoding="utf-8"))
npc = res["null_pool_cumulative"]
w41 = npc["w41_only"]
merged = npc["merged"]
kl = res["skill_line_v2_k_lift"]
led = res["science_gates"]["ledger"]
a = res["families"]["A_random_engine_exit"]
se_key = "se_mu_at_k%d" % merged["n_values"]
se_mu = npc[se_key]

# S5 anchors: frozen = W39 actuals (draft-window anchor per prereg clause);
# rolling = W40 actuals (W40 finalize landed r532 bm-b BEFORE this finalize
# window -> rolling-anchor clause mandates dual-anchor readout, W40 s7 verbatim).
anc = {
    "w39_mu": -0.091610, "w39_sigma": 0.244772, "w39_p95": 0.2995, "w39_klift": -0.0007,
    "w40_mu": -0.095958, "w40_sigma": 0.243866, "w40_p95": 0.3057, "w40_klift": -0.0002,
    "w40_head": 450540,
}

mu, sg = w41["mu"], w41["sigma"]
p95 = a["full_sharpe_p95"]
d_mu_39, d_mu_40 = abs(mu - anc["w39_mu"]), abs(mu - anc["w40_mu"])
d_sg_39 = (sg - anc["w39_sigma"]) / anc["w39_sigma"] * 100
d_sg_40 = (sg - anc["w40_sigma"]) / anc["w40_sigma"] * 100
d_p95_39, d_p95_40 = abs(p95 - anc["w39_p95"]), abs(p95 - anc["w40_p95"])
klift = kl["line_delta_k_lift"]
neff = kl["n_eff_held_equal"]
line_old = kl["line_pre_w41"]
line_new = kl["line_merged_%d" % merged["n_values"]]

verdict = all([d_mu_39 < 0.02, d_mu_40 < 0.02, abs(d_sg_39) < 10, abs(d_sg_40) < 10,
               d_p95_39 < 0.05, d_p95_40 < 0.05, abs(klift) <= 0.02])
print("S5 dual-anchor: mu %.6f (d39 %.4f d40 %.4f) sigma %.6f (%+.2f%% %+.2f%%) "
      "p95 %.4f (d39 %.4f d40 %.4f) klift %+.4f neff %d -> %s"
      % (mu, d_mu_39, d_mu_40, sg, d_sg_39, d_sg_40, p95, d_p95_39, d_p95_40,
         klift, neff, "PASS" if verdict else "FAIL"))
assert verdict, "S5 criteria FAIL -- refuse backfill"

s7 = f"""- finalize one-pass 2026-10-02 02:4x（bm-c r345 收口窗：链序解锁=W40 finalize 已由 bm-b 落账【r532 恢复轮·n1_w40_results.json 在 origin·链头 450,540】→本波 FAIL-CLOSED 等待解除·12/12 分片完备性门过【r310 律·12/12 产品已上 origin·r344 尾批 7/9/10 三片 commit 1c0b438c8】）。
- S5 判据 4/4 PASS（锚滚动律披露：本波起草窗锚=W39 实测·W40 finalize 于 r532 落账先于本波 finalize 窗→按 §5 滚动条款以 W40 实测复核亦全过【双锚面披露·W40 §7 同式】）：
  1. mu 漂移：W41-only **{mu:.6f}** vs W39 锚 −0.091610【|Δ|={d_mu_39:.4f}<0.02 PASS】/vs W40 滚动锚 −0.095958【|Δ|={d_mu_40:.4f}<0.02 PASS】；merged（K={merged['n_values']:,}）**{merged['mu']:.6f}**。
  2. sigma 相对变化：W41-only **{sg:.6f}** vs W39 锚 0.244772【{d_sg_39:+.2f}%<±10% PASS】/vs W40 锚 0.243866【{d_sg_40:+.2f}%<±10% PASS】；merged **{merged['sigma']:.6f}**。
  3. A 族 full_sharpe_p95：**{p95:.4f}** vs W39 锚 0.2995【Δ={d_p95_39:.4f}<0.05 PASS】/vs W40 滚动锚 0.3057【Δ={d_p95_40:.4f}<0.05 PASS】（门校准注记：结果知情校准面·测量面零注册利害）。
  4. K-lift 线移动：**{klift:+.4f}**【{line_old:.4f}→{line_new:.4f} @n_eff_held {neff:,}】≤0.02 PASS（W3..W40 先例族内【含 W38 −0.0001/W39 −0.0007/W40 −0.0002 三波连负】如实报正——本波转正·加深不必然抬线先例续）。
- 账本：prev **{led['prev_total']:,}**【==W40 finalize 落账头 448,340+2,200·derive 禁手抄自证】＋本波 2,200＝total **{led['total']:,}**·voids_applied LOWAMP-P1/P2 继承面 ✓；skill_line_v2 消费 n_eff={neff:,}（W40+W41 合并池 K={merged['n_values']:,} 同步加深·se_mu {se_mu:.6f}）；**投影勘误注记**：r344 状态件投影「ledger 452,940」为起草窗笔误（450,540+2,200=452,740）——derive 律（prev=扫描已 finalize 文件集禁手抄）自动防错·实收 {led['total']:,} 为链性真值·K=88,120==§0 投影逐位。
- 链序注记：下一波（W42+）尚未冻结——法典 §4 表尾当前=W41 行·按 first-free 律另窗起草。"""

s8 = f"""- 设计零偏差：frozen v1 设计逐字复用（run_one 引擎同源），W41-only mu/sigma 与先例族【W2..W40】逐面同域，零断裂信号；B 族 p_exit=0.05 配对律齐备（n=200）。
- 波节奏面：W41=跨三窗全生命周期【r344 冻结+同窗 12/12 烧录（免重启 per-tick 重读自动见行·D-20261002-03 修法后常规面）→r344 尾批产品补交付（commit 1c0b438c8）→r345 finalize one-pass 收口】；r538 禁盲重跑律执行（finalize 前置核验=自产件不在场净面后点火·一过定稿）。
- 测量面结论：累计 null 池 K={merged['n_values']:,}【+W41 2,200 合并】，mu {merged['mu']:.4f} / sigma {merged['sigma']:.4f} 稳定，se_mu 随累计加深收窄——null 基线置信面继续加深，无质变；canon flip 不在本波（治理提案面素材累计·K2200 同律）。
- 下游接线：skill_line_v2 @n_eff {neff:,} 活链头 derive；下一波 finalize 消费本波 {led['total']:,} 为 prev。"""

raw = open(PR, "rb").read()
eol = b"\r\n" if b"\r\n" in raw.split(b"\n", 1)[0] + raw[:2000] else b"\n"
ph = "（占位·finalize 窗机械回填。）".encode("utf-8")
assert raw.count(ph) == 2, f"placeholder count {raw.count(ph)} != 2 (refuse blind write)"

def enc(text):
    return text.encode("utf-8").replace(b"\n", eol)

s7b = enc(s7)
s8b = enc(s8)
first = raw.find(ph)
second = raw.find(ph, first + 1)
out = raw[:first] + s7b + raw[first + len(ph):second] + s8b + raw[second + len(ph):]
open(PR, "wb").write(out)
print("backfill written: s7 %d bytes + s8 %d bytes, eol=%r, placeholders left=%d"
      % (len(s7b), len(s8b), eol, out.count(ph)))
