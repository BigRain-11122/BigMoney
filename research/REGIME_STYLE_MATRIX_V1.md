# REGIME-STYLE MATRIX v1 — 策略-阶段矩阵规格件+切换律（O-20261007-2215 bm-c ①）

- 法源：O-20261007-2215（CEO 方向令：不同风格策略适配不同市场阶段——牛市/震荡/阴跌/熊市/护盘期；现在是防守型不错，但牛市开始就不一定了）。
- 交付：本件（规格）+ `scripts/regime_style_matrix.py`（可运行引擎+selftest）＝同一窗落地活产出；大限 ≤10-16 12:00。
- 本件为工程车道规格；阶段判别归 bm-a REGIME-5（≤10-14），五态路由器规格归 bm-b（≤10-16）。科学门不降：矩阵数值面的历史验证按 K≥1000 律+成本压测，禁因 CEO 需求降门（CEO 研究导向哲学 09-28）。

## 一、输入契约（frozen contract）

bm-a REGIME-5 判别器产出标签落 `results/regime5_labels/<任意名>.json`（bm-c 消费取最新一件）：

```json
{"cutoff": "YYYY-MM-DD", "source": "REGIME-5 (bm-a)",
 "labels": [{"date": "YYYY-MM-DD", "state": "BULL|CHOP|GRIND|BEAR|SUPPORT"}, ...]}
```

五态键：`BULL`=牛市 · `CHOP`=震荡 · `GRIND`=阴跌 · `BEAR`=熊市 · `SUPPORT`=护盘期。上游形态不合契约=接线时写适配器（禁改本契约）。

## 二、矩阵 v1（specialists + 禁用清单 + 权重）

袖面（O-2215 §二 现状盘点 verbatim 映射）：`defensive_six`=现役六员 COMPOSITE-CE-01（熊市主场）· `grid`=GRID 族 5 活 cells（震荡收割）· `lowvol`=低波红利家族（2675 格显著·p=0.0018）· `dip_rebound`=超跌反弹淬炼版（熊市闸三件套）· `cta_trend`=CTA_P1 趋势线（牛市第一候选·2026-10-08 复市起纸盘试用期·GM 署名放行）。

| 态 | defensive_six | grid | lowvol | dip_rebound | cta_trend | cap | 禁用清单（结构性·证据=O-2215 §二） | 专精员缺口（如实） |
|---|---|---|---|---|---|---|---|---|
| BULL 牛市 | 0.20 | 0 | 0.10 | 0 | 0.50 | 0.80 | dip_rebound（熊市闸设计件·牛市无主场） | 第二专精员=牛市进攻供给扫描（bm-a ≤10-14） |
| CHOP 震荡 | 0.30 | 0.30 | 0.20 | 0 | 0 | 0.80 | cta_trend（区间市 whipsaw） | 无 |
| GRIND 阴跌 | 0.40 | 0 | 0.20 | 0.20 | 0 | 0.80 | cta_trend+grid（缓步阴跌=趋势伪信号+网格漏底） | 无 |
| BEAR 熊市 | 0.50 | 0 | 0.20 | 0.20 | 0 | 0.90 | cta_trend（ETF 多头趋势件熊市失主场·期货空腿属独立账户） | 无 |
| SUPPORT 护盘期 | 0.40 | 0.10 | 0.30 | 0.10 | 0 | 0.90 | 无（空白新建·判据面归 bm-b ≤10-16） | 专精员双空白（判据+策略均待 bm-b 供给） |

**修订窗律**（mirror ROUTE_TABLE_V1 amendment-window law）：数值权重=冻结 v1.0 实例化，修订窗开至首个 REGIME-5 标签翻面事件落账为止；结构性规则（每态专精员 ≥2 或如实缺口标记、禁用袖面权重恒 0、Σ权重 ≤ cap）**不在修订窗内**，由 selftest t4/t5/t7 恒锁。现金残差=cap−Σ权重（0 收益如实披露）。

## 三、切换律三件（O-2215 §一.3）

1. **确认窗防抖**：原始标签须连续 `N_CONF=3` 交易日不变才确认翻面（hysteresis；首标签=bootstrap）。防来回打脸；N_CONF 缺省 3，上游判别器全史回放（K≥1000 律）校准后冻结——校准归 bm-a 判别器验证批，非本件。
2. **切换滞后成本入判据**：每次确认翻面计一次性过渡成本 `Σ|Δw_i| × COST_X1`（COST_X1=13.041bp/边·`rev_osc_stock_p1` 冻结常量 import·与 SYSTEM-V1 滑翔律同式零重实现）。成本进翻面判据面（判别器回放时翻面净收益须吃得过过渡成本）。
3. **翻面权重切换（w_eff 滑翔律 mirror）**：确认日仍跑旧态权重；确认日次一日起跑新态权重——无中途强制平仓，权重渐次生效。

## 四、验证与接线

- `python scripts/regime_style_matrix.py selftest`＝离线确定性 40 检（hysteresis/抖动零翻面/成本公式/矩阵完整性/禁用执行/滑翔日序/专精员计数/契约校验）。
- `python scripts/regime_style_matrix.py run`＝标签在位时产 `results/regime_style_matrix/MATRIX-<cutoff>.json`（权重时间线+翻面事件+过渡成本）；标签未落=诚实 awaiting_upstream no-op（exit 0）。
- 接线窗：bm-a REGIME-5 落地（≤10-14）→ 标签入契约面 → run 首产；bm-b 路由器规格（≤10-16）→ SUPPORT 行补全。判据回访 10-21（O-2215 §四）。
- 本面零交易零注册件触碰（live.paper 锚定门禁保护对象不受本件扰动）；月界首考 10-31 不受扰动。
