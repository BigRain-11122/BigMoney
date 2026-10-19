# STAGE-STYLE 组合矩阵 v1 — 阶段×风格条件化组合读数

- 批次：`FUND-STAGESTYLE-COMBO-P1`｜机：bm-b｜证据截止：2026-10-19
- 窗口：2013-04-01..2026-10-19（3290 bars）
- 面板：data/astock_daily/per shape [8745, 5225] cutoff 2026-10-19
- 预注册：`research/FUND-STAGESTYLE-COMBO-P1.md`（状态 **DRAFT-NOT-FROZEN**）
- 本页=读数矩阵（READOUT_ONLY），**不是判决**：G1'/G2/DSR/M1 属 finalize 面，未跑。

## 1. 主表（年化夏普 / 全窗累计收益 / 最大回撤 / 年化波动）

| 组合 | 成本 x1 夏普 | x1 累计收益 | x1 最大回撤 | x2 夏普 | x2 累计收益 | x2 最大回撤 |
|---|---|---|---|---|---|---|
| C1 阶段组合（BEAR/GRIND->现金；其余 DIVLOWVOL-YIELDVOL） | 1.083 | 246.9% | -19.4% | 1.045 | 236.0% | -20.4% |
| C2 阶段组合（BULL->VALUE-PE；BEAR/GRIND->现金；其余 DIVLOWVOL-YIELDVOL） | 0.942 | 211.0% | -20.3% | 0.896 | 198.3% | -21.8% |
| C3 阶段组合（BEAR/GRIND->现金；BULL/CHOP/SUPPORT 三格分映射） | 0.977 | 218.7% | -22.4% | 0.929 | 205.9% | -24.0% |
| 无条件 divlowvol 袖面 | 1.209 | 346.5% | -15.8% | 1.176 | 334.3% | -16.0% |
| 无条件等权（U-EW） | 0.712 | 171.6% | -23.4% | 0.685 | 163.4% | -23.6% |
| 无条件 value 袖面 | 0.437 | 103.8% | -31.6% | 0.414 | 96.1% | -31.8% |
| 无条件 quality 袖面 | 0.331 | 81.8% | -47.2% | 0.314 | 75.1% | -48.7% |

成本口径：x1=13.041bp/边；x2=双倍成本压力面。日收益序列在 JSON 孪生 `results` 原样件。

## 2. 一句话结论

**三个阶段组合全部跑不赢「什么都不做，只拿 divlowvol 袖面」**：最好的 C1 x1 夏普 1.083／累计 246.9%／最大回撤 -19.4%，而无条件 divlowvol 读 1.209／346.5%／-15.8%。阶段择时付了换手税，收益和回撤两头都更差。

## 3. 预注册 §5 预测对照（跑前写死，禁改）

- **P4（组合主张门，阈值 0.994＝divlowvol 0.894＋0.10）**：
  - C1 x1 夏普 1.083 → 过阈值；同轮无条件最强袖面（U-divlowvol 1.209）比它输。
  - C2 x1 夏普 0.942 → 未过阈值；同轮无条件最强袖面（U-divlowvol 1.209）比它输。
  - C3 x1 夏普 0.977 → 未过阈值；同轮无条件最强袖面（U-divlowvol 1.209）比它输。
- **P1（BULL 格为主收益源）／P2（BEAR 格回避可回收损失）／P3（SUPPORT 不设专格）**：三格分解读数落在
  JSON 孪生逐格面，本条只记「组合整体不及无条件」这一层；格级归因待 finalize 批。

## 4. 诚实边界

- null 面：pending (same-mask shuffle family not run here)
- 数据缺口：{}
- 单源声明：family selection kernels imported from scripts/fund_*_p1.py (zero re-implementation); local panel = data/astock_daily per-symbol qfq
- 袖面注记：divlowvol 本地起算 2003-11-03，冻结 t0 2006-02-06，前 27 个月被 clamp；侧录面 qfq 反演 5,123 件（分红现金流倒推，`Money02` factor 面本机缺席）。
- D6 披露（与 divlowvol 相关）：{"U-value": 0.569, "U-quality": 0.5797, "U-divlowvol": 0.8356, "U-EW": 0.7515}

- 生成器：`scripts/stagestyle_combo_p1_report.py`（确定性·零墙钟）｜原件：`results/stagestyle_combo_p1/SSCOMBO-P1-2026-10-19.json`
