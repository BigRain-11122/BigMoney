# -*- coding: utf-8 -*-
import json, os
B = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
P = os.path.join(B, "research", "THEME_JUDGE_P2.md")
src = open(P, encoding="utf-8").read()
needle = "## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】\n\n## §8 批后复盘【必填·s7-T】\n"
assert src.count(needle) == 1, "needle count=%d" % src.count(needle)
S7 = """## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

**2026-10-04 13:14:13 finalize 实跑回填**（autofill 池化点火 claim 13:07:52→results 落盘 13:14:13≈**381s/26 workers·BelowNormal·预算 600s 内**；burn_state+results JSON 双件在盘；r678 收口轮=本窗完成池面双翻〔entry+shard→done·done_at 13:14:13·r668 律〕+本 §7/§8 回填+轮报告回执）

- **判决：judged_negative（theme 机械翻译族级诚实关线——含 order-chain 保留的 0.75 深破面；redirect candidates exhausted；E24-ii 递归门=无第三恒定面重试）**——主面 TJ2-SOLO-x1 pooled Sharpe **0.2899** ＜ 判线 **1.2545**；g1_pass_v2=**false** ×4 面、g2_eligible_v2=**false** ×4 面、DSR=**0.0** ×4 面（n_eff=633,985）。
- 四面读数（Sharpe｜null μ±σ｜判线｜CI95）：TJ2-FULL-x1 0.2364｜0.3702±0.1615｜1.2050｜[−0.3753,+0.8445]；TJ2-FULL-x2 0.2269｜0.3613±0.1620｜1.1989｜[−0.3895,+0.8346]；TJ2-SOLO-x1 0.2899｜0.3886±0.1675｜1.2545｜[−0.1401,+0.7661]；TJ2-SOLO-x2 0.2789｜0.3798±0.1678｜1.2470｜[−0.1488,+0.7553]。
- M1 t 值面（TJ2-SOLO-x1·claim_class=new_factor）：t=**1.2652**＜3.0 门槛=fail；族 PBO（4 格 CSCV-8）=**0.3857**（observe 带 0.25＜p≤0.5）。
- 出场普查：illegal reason=**0**（§0.6 门过·P2 门在 0 非 cap 值）；censored_share=**42.15%**（768/1,822·P1 31.34%→上移）；截断后尾部翻转 **1 例**如实披露（159901·2024-09-30 点火·census_break 2026-09-28＞evidence_cutoff·end_pos_under_truncation=true）。
- LOO 796 折：**796 稳**（100%·零符号翻转·无单一 ETF 驱动）；全窗 pooled sys **+133.10%** vs 同窗被动 **+96.79%**（P1 同口径 +108.26%——深线 0.75 较 0.80 多吃 drift 段，与 (c) null 上移同源）。
- famous16 分层（逐 ride 净均值）：famous(n=52) sys −2.63% vs bh −3.76%（边 **+1.13pp**·P1 +2.65pp）；rest(n=1,770) sys +5.48% vs bh +7.07%（边 **−1.59pp**·P1 −4.64pp）——E25 幸存者溢价**进一步塌缩**（两面均向零收敛）。
- 分位分层（pooled 净）：tercile_0 sys 1.2831 vs bh 0.9917；tercile_1 0.1772 vs 0.2171；tercile_2 0.0860 vs 0.1111——边沿分位单调衰减复现（P1 同形态）。
- 分段披露腿（P1 run 内 error 面本批修复·regime_segments 正常落盘）：bull **+152.23%**（n=1,501）／bear **−119.69%**（n=1,504）／chop +26.44%（n=259）／na +63.00%（n=1,537）——熊市段深扛 0.75 的骑乘暴露如实入账（(d) 深线加注兑现）。

## §8 批后复盘【必填·s7-T】

- **预测对账**：(a) SOLO-x1 方向**部分命中**——Sharpe 0.2899 落预测带 0.5-1.5 **下方**（较 P1 headline 0.2735 仅 +0.0164·「显著高于 P1」未兑现）；「仍不过重算后判线」**命中**（0.2899≪1.2545）；§5 预警兑现=sens 锚 1.0203 为同窗 in-sample 选择偏差读数，真实判线面 0.29 远低于锚。(b) FULL＜SOLO **命中**（0.2364＜0.2899·E28 分层价值同向复现）。(c) null 带**命中**——μ 0.3613-0.3886 落 0.35-0.65 带内且较 P1 上移（主面 0.3886＞0.3734·深线多吃 drift 预测兑现）；σ 0.1615-0.1678 落 0.12-0.30 带内且较 P1 收窄；**净判线反而下移**（1.3172→1.2545·σ 收窄效应＞μ 上移效应——预测「判线随 null 上移」方向**错**，如实记录）；无 μ≥0.9/σ≥1.0 构造异常。(d) 极端日先验披露如仪（2024-09-30 簇 FULL 年 cohort n=677 边均 −2.75pp；2015 段 SOLO cohort n=53 边均 −11.59pp 深扛兑现）。(e) 出场普查**命中**——censored 42.15% 落 33-45% 带内（P1 31.34% 上移兑现）；illegal 0 ✓。(f) 换手**命中**——census 均值 **2.61 次/ride**（P1 ~4 下移兑现·带 1.5-4 内）；x2 pooled 拖累 FULL **0.30pp**/SOLO **0.39pp**＜2pp 门槛。(g) 邻域敏感腿 **8/8 落盘**——**四向字节级镜像保真实证**：P2 冻结面（bl0.75/rb1.25）pooled FULL **0.32297**/SOLO **1.020301** 与 P1 sens 同常数腿**完全恒等**；P2 sens bl0.80/rb1.25 腿 FULL **0.108618**/SOLO **0.833841** 与 P1 冻结面**完全恒等**（确定性引擎跨批复现）；bl0.70 邻腿=未测新面：SOLO 1.0755/FULL 0.4474 均**高于**冻结面（预测「接近或低于」**部分错**·+5.5pp/+12.4pp 相对差如实记录）；rb 邻腿 rb1.30＞rb1.20 两分层同向**命中**（SOLO 1.3044＞0.5207·FULL 0.4194＞0.0574·方向沿 P1 sens）；**判线不因变体读数重设**（E24-②）·主面判负=族关线（verdict 冻结词：no third constant-face retry）。
- **损耗账**：`results/gate_attrition.json` entries 追加一行（kind=judgment·cells_ledger_delta=**8,004**·ledger_total_after=**641,985**·ts 2026-10-04 13:14:13·r248 律）；trials_ledger 链 633,981→**641,985**（LOWAMP-P1/P2 void 已净）。
- **判线 v2 当批读数**：skill_line TJ2-SOLO-x1=**1.2545**（null_term 1.2545＋passive_term 0.3599·μ_null 0.3886·σ_null 0.1675·n_eff 633,985·pool core48）；主面 Sharpe 0.2899 距线 −0.96——判负非擦线负。
- **全起点分布【§1.3】**（episodes.csv 1,822 逐起点·逐 ride 边=sys−bh）：TJ2-FULL(n=1,171) 最好 +194.1%／最坏 −62.1%／p25 −7.9%／中位 0.0%／p75 +3.2%，边均值 **−0.78pp**、正边占比 31.8%；TJ2-SOLO(n=651) 最好 +298.1%／最坏 −96.0%／p25 −15.9%／中位 −1.9%／p75 +4.8%，边均值 **−2.85pp**、正边占比 34.4%。**点火年 cohort：SOLO 13/20 年边均值为负**（最大样本年 2026 n=137 +3.78pp·2024 n=82 −7.90pp·2022 n=60 −12.36pp）——多数 cohort 不成立→撤回判定成立，与判负同谳；FULL 面 3/6 年为负（2014/2020/2024·集群日集中 2024-09-30 n=677）。
- **试验量归因【§1.4】**：本批新增试验数 **8,004**（4 judged cells+4×2,000 nulls·预算门内）；theme 机械翻译族自此**全族关线**（P1=0.80 主面+sens 16 变体判负·P2=0.75 保留面+sens 8 变体判负·redirect candidates exhausted）。
- 回执：轮报告 r678 回执行＋池面双翻已落（r668）；**主面不过线→不注册**：注册件/live/paper 接线/smoke 锚定门全部不触发（本批只判不注册·判决词冻结）。
"""
new = src.replace(needle, S7)
assert new != src
open(P, "w", encoding="utf-8", newline="\n").write(new)
# verify
chk = open(P, encoding="utf-8").read()
assert "381s/26 workers" in chk
assert chk.count("judged_negative") >= 3
assert "## §8 批后复盘【必填·s7-T】" in chk
i7 = chk.find("## §7"); i8 = chk.find("## §8")
assert 0 < i7 < i8
print("BACKFILL_OK len=%d -> %d" % (len(src), len(chk)))
