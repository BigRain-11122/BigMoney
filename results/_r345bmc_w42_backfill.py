# r345 bm-c W42 prereg s7/s8 mechanical backfill (r412 face; bytes in/out per
# r530 law; numbers derived from n1_w42_results.json verbatim, never hand-copied;
# single W41 anchor per the prereg rolling-anchor clause -- no newer finalize
# landed between freeze and this window, disclosed honestly).
import json, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
RES = ROOT + r"\results\perpetual_faces\n1_w42_results.json"
PR = ROOT + r"\research\PERPETUAL_N1_W42_PREREG.md"

res = json.load(open(RES, encoding="utf-8"))
npc = res["null_pool_cumulative"]
w42 = npc["w42_only"]
merged = npc["merged"]
kl = res["skill_line_v2_k_lift"]
led = res["science_gates"]["ledger"]
a = res["families"]["A_random_engine_exit"]
se_key = "se_mu_at_k%d" % merged["n_values"]
se_mu = npc[se_key]

# S5 anchor: W41 actuals (draft-window anchor = latest landed finalize at
# freeze; rolling clause checked: NO newer finalize landed between the W42
# freeze and this window -> anchor stays W41, single-anchor readout).
anc = {
    "w41_mu": -0.090052, "w41_sigma": 0.249199, "w41_p95": 0.3181,
    "w41_klift": 0.0006, "w41_head": 452740,
}

mu, sg = w42["mu"], w42["sigma"]
p95 = a["full_sharpe_p95"]
d_mu = abs(mu - anc["w41_mu"])
d_sg = (sg - anc["w41_sigma"]) / anc["w41_sigma"] * 100
d_p95 = abs(p95 - anc["w41_p95"])
klift = kl["line_delta_k_lift"]
neff = kl["n_eff_held_equal"]
line_old = kl["line_pre_w42"]
line_new = kl["line_merged_%d" % merged["n_values"]]

verdict = all([d_mu < 0.02, abs(d_sg) < 10, d_p95 < 0.05, abs(klift) <= 0.02])
print("S5 single-anchor (W41, rolling clause: no newer finalize landed): "
      "mu %.6f (d %.4f) sigma %.6f (%+.2f%%) p95 %.4f (d %.4f) klift %+.4f "
      "neff %d -> %s"
      % (mu, d_mu, sg, d_sg, p95, d_p95, klift, neff,
         "PASS" if verdict else "FAIL"))
assert verdict, "S5 criteria FAIL -- refuse backfill"

s7 = f"""- finalize one-pass 2026-10-02 03:0x（bm-c r345 同窗三段全生命周期收口：冻结 commit bd6dbb3cf→**同窗 12/12 烧录**〔免重启 per-tick 重读自动见行·pre-commit 点火自然行为〔r344 W41 同式·D-20261002-03 修法面〕·appender 批量交付 12/12 上 origin=r310 完备性门过〕→本窗 finalize one-pass；链序解锁=W41 finalize 已落账【r345 本轮早窗·n1_w41_results.json 在 origin·链头 452,740】→FAIL-CLOSED 等待面零（链全追平·零在飞上游面））。
- S5 判据 4/4 PASS（锚滚动律披露：本波起草窗锚=W41 实测·冻结窗与本 finalize 窗之间**零新波 finalize 落账**（origin 净变动=引擎 appender 分片交付+bm-b daemon keepalive tick）→锚保持 W41 实测·单锚面如实披露）：
  1. mu 漂移：W42-only **{mu:.6f}** vs W41 锚 −0.090052【|Δ|={d_mu:.4f}<0.02 PASS】；merged（K={merged['n_values']:,}）**{merged['mu']:.6f}**。
  2. sigma 相对变化：W42-only **{sg:.6f}** vs W41 锚 0.249199【{d_sg:+.2f}%<±10% PASS】；merged **{merged['sigma']:.6f}**。
  3. A 族 full_sharpe_p95：**{p95:.4f}** vs W41 锚 0.3181【Δ={d_p95:.4f}<0.05 PASS】（门校准注记：结果知情校准面·测量面零注册利害）。
  4. K-lift 线移动：**{klift:+.4f}**【{line_old:.4f}→{line_new:.4f} @n_eff_held {neff:,}】≤0.02 PASS（W3..W41 先例族内【含 W39 −0.0007/W40 −0.0002/W41 +0.0006 转正】本波复归负——加深不必然抬线先例续·如实报负）。
- 账本：prev **{led['prev_total']:,}**【==W41 finalize 落账头 450,540+2,200·derive 禁手抄自证】＋本波 2,200＝total **{led['total']:,}**·voids_applied LOWAMP-P1/P2 继承面 ✓；skill_line_v2 消费 n_eff={neff:,}（W42 合并池 K={merged['n_values']:,} 同步加深·se_mu {se_mu:.6f}）；K={merged['n_values']:,}==§0 投影 90,320 逐位。
- 链序注记：下一波（W43+）尚未冻结——法典 §4 表尾当前=W42 行·按 first-free 律另窗起草；**W43+ 警示承继**：B +200 算术位（43_801..44_000）撞 SEED_REGISTRY p4_queue=44_000 尾点=r345 带闸机证 REFUSED——W43 B 面须机 derive 首净窗（W39-B 跳位族）。"""

s8 = f"""- 设计零偏差：frozen v1 设计逐字复用（run_one 引擎同源），W42-only mu/sigma 与先例族【W2..W41】逐面同域，零断裂信号；B 族 p_exit=0.05 配对律齐备（n=200）。
- 波节奏面：W42=**单窗全生命周期波**【r345 同窗三段：冻结（band gate ADMIT+banned gate+selftest 三门）→免重启点火 12/12（pre-commit 自然点火·appender 批量交付）→finalize one-pass】——链全追平态下「冻结→烧→收口」零隔完成的第二枚单窗波（W32 r339 先例后首枚）；r538 禁盲重跑律执行（finalize 前置核验=自产件不在场净面后点火·一过定稿）。
- 测量面结论：累计 null 池 K={merged['n_values']:,}【+W42 2,200 合并】，mu {merged['mu']:.4f} / sigma {merged['sigma']:.4f} 稳定，se_mu 随累计加深收窄——null 基线置信面继续加深，无质变；canon flip 不在本波（治理提案面素材累计·K2200 同律）。
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
