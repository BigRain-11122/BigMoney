# -*- coding: utf-8 -*-
"""r558 bm-a: W48 prereg SS7/SS8 mechanical backfill (r412; bytes-safe per r530)."""
import io

FP = r"research\PERPETUAL_N1_W48_PREREG.md"
b = open(FP, "rb").read()
t = b.decode("utf-8")

PH7 = "（跑后回填：全起点分布+预测对账+损耗账——finalize 窗机械回填，禁改判据禁重跑。）"
PH8 = "（跑后回填：verdict 数字面=测量读出·N/A 三态如实。）"
H7 = "## §7 跑后回填【预留】"
H8 = "## §8 结论【预留】"

S7 = """- finalize one-pass 2026-10-02 05:2x（bm-a r558 **落账序让路-重derive窗**：冻结 commit **71b4b9601**〔r557 构式合并同窗 W49 双冻结面·r531〕→ tick 引擎免重启烧录 12/12〔early-ignition r557 起燃·产物增长面验证 r325/r535 律·pool_core_samples multicore_burn 遥测 ~15.1s/片·4.65 effective cores〕→ **首跑 finalize 05:12:09 prev=467,948〔W47 头〕撞 bm-b W49 同窗先落账**〔e488e8008 ledger 470,148·seat ahead of in-flight W48/W50 per r518〕＝**同 prev 双头**→ S0 整合让路（首跑 stale 产品未 commit 即删＝r538 净面·首跑陈旧回填同步回退）→ **二次 finalize one-pass 终稿 prev=470,148 derive**＝total **472,348**；链序披露：本波＝低号波后落账的 r518 全谱系第二例（W17×W19 首例的高低反向面）——合并基＝冻结 §0 申报组分（canon+W1+W2..W47·101,320→103,520）按 ordinal 扫描实现＝**冻结语义**、不受落账序影响（W49 贡献由 W49 自件与其后波 ordinal 组分承载·跨件并集零缺失）。
- S5 判据 4/4 PASS（锚＝冻结 §5 W47 finalize 实测；滚动披露：W49 同窗落账〔bm-b r558〕——锚按冻结时点最新可得＝W47 实测执行·W49 实测双锚复核 4/4 同过如实报）：
  1. mu 漂移：W48-only **−0.108583** vs W47 finalize 实测锚 −0.094223【|Δ|=0.0144<0.02 PASS】（runner 机证 mu_delta_w48_vs_w47ext=**−0.01436**）；vs W49-only 复核锚 −0.090470【|Δ|=0.0181<0.02 PASS】；merged（K=103,520）**−0.092158**。
  2. sigma 相对变化：W48-only **0.249151** vs W47-only 锚 0.247066【**+0.84%**<±10% PASS】；vs W49-only 复核锚 0.245455【+1.51%<±10% PASS】；merged **0.244850**。
  3. A 族 full_sharpe_p95：**0.3099** vs W47 锚 0.3112【Δ=−0.0013<0.05 PASS】；vs W49 复核锚 0.3146【Δ=−0.0047<0.05 PASS】（门校准注记：结果知情校准面·测量面零注册利害）。
  4. K-lift 线移动：**+0.0002**【1.1591→1.1593 @n_eff_held 470,148】≤0.02 PASS（W3..W47 先例族内【W45 −0.0001/W46 −0.0003/W47 +0.0002/本波 +0.0002】正负交替如实报——加深不必然抬线先例续）。
- 账本：prev **470,148**【==bm-b W49 finalize 落账头·r518 origin-timing 律 derive 禁手抄自证】＋本波 2,200＝total **472,348**·voids_applied LOWAMP-P1/P2 继承面 ✓；K=**103,520**==§0 投影 103,520 逐位；se_mu 0.000769→**0.000761** 续收窄；skill_line_v2 消费 n_eff=470,148。
- 回填同窗合规：r307 两态守卫律兑现（本回填同窗+回填后缺省波 selftest 复跑绿）；r538 一过定稿执行（首跑产品删后重derive·重derive后未再跑·自产件在场净面自证 n1_w48_results.json）。
- 链序注记：在飞下游 **W50/W51=bm-c 已登记**（r350·finalize 消费本波 **472,348** 为 prev per r518 origin-timing 律·带位与本波 disjoint 由 ADMIT 回执机证 r531 律）；本机下一自有波=法典表尾 fetch 实核后 first-free-number derive（r511 表尾锁律）。"""

S8 = """- 设计零偏差：frozen v1 设计逐字复用（run_one 引擎同源），W48-only mu/sigma 与先例族【W2..W47】逐面同域，零断裂信号；B 族 p_exit=0.05 配对律齐备（n=200·45_201..45_400 算术顺延带==W47 B 尾 45_200+1·ADMIT 回执机证 results/_r557bma_w48_band_gate.py）。
- 波节奏面：W48=**落账序让路-重derive复合窗**【r557 冻结（r555 让渡回执自报 W48 claim·bm-b r556 承让跳位 W49＝r518① 公示=预留律首例）→ tick 引擎 12/12 → 首跑 stale-prev → W49 先落账 → S0 让路 → 二次 finalize 终稿 one-pass】——r518 撞链头净路的 bm-a 首例＋低号后落账全谱系第二例；S0 同窗外科双 commit 治愈（pool_core_samples 混合行尾 union 事故+行级去重修复）如实入轮报告 r558。
- 测量面结论：累计 null 池 K=103,520【+W48 2,200 合并】，mu −0.0922 / sigma 0.2449 稳定，se_mu 随累计加深收窄（0.000769→0.000761）——null 基线置信面继续加深，无质变；canon flip 不在本波（治理提案面素材累计·K2200 同律）。
- 下游接线：skill_line_v2 @n_eff 470,148 活链头 derive；下一波 finalize 消费本波 **472,348** 为 prev（r518 origin-timing 律）。"""

assert t.count(PH7) == 1 and t.count(PH8) == 1, "placeholder not unique"
assert t.count(H7) == 1 and t.count(H8) == 1, "heading not unique"
t = t.replace(H7, "## §7 跑后回填【已回填 2026-10-02】")
t = t.replace(H8, "## §8 结论【已回填 2026-10-02】")
t = t.replace(PH7, S7)
t = t.replace(PH8, S8)
nb = t.encode("utf-8")
# worktree file is pure CRLF: normalize inserted LF-only lines to CRLF
nb = nb.replace(b"\r\n", b"\x00KEEP\x00").replace(b"\n", b"\r\n").replace(b"\x00KEEP\x00", b"\r\n")
open(FP, "wb").write(nb)
print("backfill written, bytes:", len(nb))
