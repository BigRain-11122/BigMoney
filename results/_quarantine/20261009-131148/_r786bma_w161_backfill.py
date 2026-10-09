# -*- coding: utf-8 -*-
# r786 bm-a: W161 prereg sec7/sec8 finalize backfill (machine keys from n1_w161_results.json)
import io, sys

P = r"research\PERPETUAL_N1_W161_PREREG.md"
t = io.open(P, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in t else "\n"

H7_OLD = "## " + chr(167) + "7 跑后实证。【finalize 收口机械回填·届时空窗】"
B7_OLD = "- （占位·finalize 收口窗回填：合并池 pre/W-only/merged 键、账本 prev+2,200、skill_line_v2 K-lift、se_mu 收窄、A 档 p95、" + chr(167) + "5 四预测键机证、canon flip 态、审计段。回填限本节与 " + chr(167) + "8·冻结后判据零改。）"
H8_OLD = "## " + chr(167) + "8 批后复盘。【finalize 同窗回填·届时空窗】"
B8_OLD = "- （占位·finalize 收口窗回填：设计复用面结论、宝藏捕获问（O-20261003-2030 §1 判决 finalize 收口步）、W162+ 投影承接注记。）".replace("§1", chr(167) + "1")

assert t.count(H7_OLD) == 1, "H7 not unique"
assert t.count(B7_OLD) == 1, "B7 not unique"
assert t.count(H8_OLD) == 1, "H8 not unique"
assert t.count(B8_OLD) == 1, "B8 not unique"

H7_NEW = ("## " + chr(167) + "7 跑后实证。【finalize 收口机械回填·bm-a r786·one-pass rc0·12/12 分片消费；"
          "回填窗注记：r785 冻结→tick 点火 17:0x→12/12 交付 17:12:04→本窗 finalize"
          "（r708 活进程探针+文件探针双绿后单跑·r381 12/12 交付同轮收口律·死 r785 会话 S7 尾由本窗吸收）"
          "——回填内容=n1_w161_results.json 冻结实测键·零改判据】")

B7_LINES = [
  "- **合并池**：pre-W161 K=349,920（mu=−0.092931·sigma=0.245122）→ W161-only K=2,200（mu=−0.082264·sigma=0.248453）→ **merged K=352,120（mu=−0.092865·sigma=0.245144）**；账本 prev=**757,412**+2,200=**759,612**（voids_applied=LOWAMP-P1/P2·file=results/perpetual_faces/n1_w161_results.json·evidence_cutoff=2026-09-22）。",
  "- **skill_line_v2 K-lift**（n_eff 恒等 757,412）：1.1825 → **1.1827**（Δ=**+0.0002**）；se_mu 收窄链 W159 0.000416 → W160 0.000414 → **0.000413**（0.2451/√352,120·results 键 se_mu_at_k352120）。",
  "- **A 档 full_sharpe_p95=0.3334**（2,000 runs·W160 锚=0.3297【n1_w160_results.json 机读】·差 **+0.0037**；<0.05 门过·正向微扩如实披露·抽样波动面）。",
  "- **" + chr(167) + "5 四预测键全过（机证）**：①|W161-only mu − merged mu|=0.0106<0.02 ✓ ②sigma 相对变化 +0.009%<±10% ✓ ③A p95 差 +0.0037<0.05 ✓ ④K-lift +0.0002≤±0.02 ✓。",
  "- **canon flip：NOT performed**（K2,200 同例法·治理提锚面 only·结果件如实注记）。",
  "- 审计：12 shards 零重叠连续覆盖 A[0,2000)/B[0,200)·n_backtests 合计 2,200·machine=bm-a·audit.finalize_only=true·批内波间漂移键 mu_delta_w161_vs_w160ext=**+0.008484**。",
]
B7_NEW = nl.join(B7_LINES)

H8_NEW = "## " + chr(167) + "8 批后复盘。【finalize 同窗回填·bm-a r786】"
B8_LINES = [
  "- 设计=v1 冻结逐字复用·纯种子带深化——零新机制零新方法；**宝藏捕获问（O-20261003-2030 " + chr(167) + "1 判决 finalize 收口步）：本批无新宝藏**（A-hops-prior-B 阶梯第二十例已由 r785 冻结窗 gate leg3 确认兑现·own-A 保留 leg2 面同窗·E36 卡既有·finalize 无新增面）；方法论资产卡无 append 面。",
  "- W162+ 投影承接（r785 冻结窗 gate leg3 已披露 + " + chr(167) + "5 键 5 同律）：A naive 371_004..373_003（post-W161 宇宙将被本波 B 带 371_004..371_203 于自家起点拒——阶梯 A-hops-prior-B 继承第二十一例·「W161-B-refuses-W162-A staircase 21st anticipated」预注待 W162 兑现）→ W162 A 重 derive 同强制（越过 W161 B 带·hops=1 预期→371_204..373_203）；B naive 371_204..371_403（CLEAN hops=0）落重 derive 后 A 窗内=**同窗互斥 leg2 律**——**W162 冻结方必在 post-W161 注册宇宙重 derive 且 derive B 时预留本波 A 窗**（E36 卡·W141 先例链）；verify at W162 prereg，hop 链逐跳在 probe 回执。",
]
B8_NEW = nl.join(B8_LINES)

t2 = t.replace(H7_OLD, H7_NEW).replace(B7_OLD, B7_NEW).replace(H8_OLD, H8_NEW).replace(B8_OLD, B8_NEW)
assert t2 != t
io.open(P, "w", encoding="utf-8", newline="").write(t2)

# self-check: line delta = +5 lines for sec7 (1->6 lines) and +1 line for sec8 (1->2 lines)
old_lines = t.count(nl); new_lines = t2.count(nl)
assert new_lines - old_lines == 6, (old_lines, new_lines)
assert "届时空窗" not in t2.split("跑前冻结")[0].split("## "+chr(167)+"7")[1] if ("## "+chr(167)+"7") in t2 else True
print("backfill OK; lines", old_lines, "->", new_lines)
