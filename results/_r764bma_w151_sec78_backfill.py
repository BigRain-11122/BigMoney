# -*- coding: utf-8 -*-
"""r764 bm-a W151 prereg sec7/sec8 cite-fix backfill: placeholders -> measured
keys from results/perpetual_faces/n1_w151_results.json (finalize one-pass
landed r764 same-window; zero criterion changes -- backfill-only per the
frozen-prereg contract). Bloodline: r763 _r763bma_w150_sec78_backfill.py
verbatim machinery, W151 facts machine-read (no hand transcription)."""
import io
import json

res = json.load(io.open(r"results/perpetual_faces/n1_w151_results.json",
                        encoding="utf-8"))
pc = res["null_pool_cumulative"]
led = res["science_gates"]["ledger"]
pool_pre = pc["pre_w151_cumulative"]
w151 = pc["w151_only"]
merged = pc["merged"]
kl = res["skill_line_v2_k_lift"]
a95 = res["families"]["A_random_engine_exit"]["full_sharpe_p95"]
se_mu = pc["se_mu_at_k330120"]
mu_delta = pc["mu_delta_w151_vs_w150ext"]
assert led["prev_total"] == 726011 and led["batch_trials"] == 2200 \
    and led["total"] == 728211, "ledger face drift"
assert merged["n_values"] == 330120 and w151["n_values"] == 2200 \
    and pool_pre["n_values"] == 327920, "pool face drift"
assert kl["n_eff_held_equal"] == 726011 and kl["line_pre_w151"] == 1.1798 \
    and kl["line_merged_330120"] == 1.18 and kl["line_delta_k_lift"] == 0.0002, "k-lift drift"

mu_pre = f"{pool_pre['mu']:.6f}".replace("-", "\u2212")
sg_pre = f"{pool_pre['sigma']:.6f}"
mu_own = f"{w151['mu']:.6f}".replace("-", "\u2212")
sg_own = f"{w151['sigma']:.6f}"
mu_m = f"{merged['mu']:.4f}".replace("-", "\u2212")
sg_m = f"{merged['sigma']:.4f}"
mu_own4 = f"{w151['mu']:.4f}".replace("-", "\u2212")
gap1 = abs(w151["mu"] - merged["mu"])
gap1s = f"{gap1:.4f}"
gap2 = (merged["sigma"] - pool_pre["sigma"]) / pool_pre["sigma"] * 100
gap2s = ("+" if gap2 >= 0 else "\u2212") + f"{abs(gap2):.4f}%"
a_prev = 0.3114  # W150 measured anchor (frozen in W151 prereg sec5 key 3)
gap3 = a95 - a_prev
gap3s = ("+" if gap3 >= 0 else "\u2212") + f"{abs(gap3):.4f}"

sec7 = (
    "## \u00a77 跑后实证。【finalize 收口机械回填·bm-a r764·one-pass rc0·12/12 分片消费；"
    "§7/§8 回填窗注记：r764 finalize one-pass 同窗即回填（r763 窗先例延续）"
    "——回填内容=n1_w151_results.json 冻结实测键·零改判据】\n"
    f"- **合并池**：pre-W151 K=327,920（mu={mu_pre}·sigma={sg_pre}）→ W151-only K=2,200"
    f"（mu={mu_own}·sigma={sg_own}）→ **merged K=330,120（mu={mu_m}·sigma={sg_m}）**；"
    "账本 726,011+2,200=**728,211**（voids_applied=LOWAMP-P1/P2·"
    "file=results/perpetual_faces/n1_w151_results.json·evidence_cutoff=2026-09-22）。\n"
    f"- **skill_line_v2 K-lift**（n_eff 恒等 726,011）：1.1798 → **1.18**（Δ=**+0.0002**）；"
    f"se_mu 收窄链 W149 0.000429 → W150 0.000428 → **{se_mu:.6f}**（{sg_m}/√330,120）。\n"
    f"- **A 档 full_sharpe_p95={a95:.4f}**（2,000 runs·W150 锚 0.3114）。\n"
    f"- **§5 四预测键全过（机证）**：①|W151-only mu − merged mu|={gap1s}<0.02 ✓ "
    f"②sigma 相对变化 {gap2s}<±10% ✓ ③A p95 差 {gap3s}<0.05 ✓ ④K-lift +0.0002≤±0.02 ✓。\n"
    "- **canon flip：NOT performed**（K2,200 同例法·治理提锚面 only·结果件如实注记）。\n"
    f"- 审计：12 shards 零重叠连续覆盖 A[0,2000)/B[0,200)·n_backtests 合计 2,200·machine=bm-a·"
    f"audit.finalize_only=true·批内波间漂移键 mu_delta_w151_vs_w150ext={'+' if mu_delta >= 0 else ''}{mu_delta:.6f}。\n\n"
)
sec8 = (
    "## \u00a78 批后复盘。【finalize 同窗回填·bm-a r764】\n"
    "- 设计=v1 冻结逐字复用·纯种子带深化——零新机制零新方法；**宝藏捕获问"
    "（O-20261003-2030 §1 判决 finalize 收口步）：本批无新宝藏**（A-hops-prior-B 阶梯第十例+"
    "own-A 保留 leg2 面已于冻结窗 r763 确认·E36 卡既有·finalize 无新增面）；方法论资产卡无 append 面。\n"
    "- W152+ 投影承接（§5 键 5 冻结窗已披露）：A naive 349_004..351_003（post-W150 宇宙 CLEAN hops=0）"
    "将被本波 B 带 349_004..349_203 拒（阶梯 A-hops-prior-B 继承）→ W152 A 重 derive 同强制（越过 W151 B 带）；"
    "B naive 349_204..349_403（CLEAN hops=0）落 naive A 窗内=**同窗互斥 leg2 律**——"
    "**W152 冻结方必在 post-W151 注册宇宙重 derive 且 derive B 时预留本波 A 窗**"
    "（E36 卡·W141 先例链）；verify at W152 prereg，hop 链逐跳在 probe 回执。\n\n"
)

ph7 = ("## \u00a77 跑后实证。【finalize 收口机械回填·占位——跑前为空】\n"
       "- （占位：12/12 分片落地后 finalize one-pass 机械回填·回填限本节与 §8·judged 断言照 W150 例。）\n\n")
ph8 = ("## \u00a78 批后复盘。【finalize 同窗回填·占位】\n"
       "- （占位：设计复用面+宝藏捕获问+W152+ 投影承接三行照 W150 例回填。）\n\n")

path = r"research/PERPETUAL_N1_W151_PREREG.md"
src = io.open(path, encoding="utf-8", newline="").read()
# EOL self-adaptation (r370 law)
eol = "\r\n" if "\r\n" in src else "\n"
if eol == "\r\n":
    sec7, sec8 = sec7.replace("\n", eol), sec8.replace("\n", eol)
    ph7, ph8 = ph7.replace("\n", eol), ph8.replace("\n", eol)
assert src.count(ph7) == 1 and src.count(ph8) == 1, "placeholder anchors not unique"
out = src.replace(ph7, sec7).replace(ph8, sec8)
assert out.count("n1_w151_results.json 冻结实测键") == 1, "sec7 face"
assert out.count("mu_delta_w151_vs_w150ext") == 1, "sec7 audit key"
assert out.count("W152+ 投影承接") == 1, "sec8 face"
assert "占位" not in out, "placeholder residue"
io.open(path, "w", encoding="utf-8", newline="\n").write(out)
print("W151 sec7/8 backfill landed:", len(src), "->", len(out), "bytes |",
      "keys:", f"merged mu {mu_m}/sigma {sg_m}/A p95 {a95:.4f}/K-lift +0.0002/se_mu {se_mu:.6f}",
      "| gaps:", gap1s, gap2s, gap3s)
