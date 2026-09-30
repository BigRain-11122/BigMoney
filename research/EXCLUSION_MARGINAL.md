# 排除规则边际值扫描（EXCLUSION-MARGINAL）·D-20260930-41 交付件 #3 载体

> 轨道：research/RETAIL_QUANT_TRACK.md §二 #3 ｜ berth：**bm-b**（心跳 r474 宣告+本窗 F-04 MSG）｜ 令源：D-20260930-41
> 令原文锚：「排除」是机构因仓位要求做不到的动作；第一铁律已实测 alpha 5.63%→14.80%（实测配置不在本仓，本线以本仓冻结配置独立复测）。

## 状态

**冻结待烧**——预注册 `research/EXCLUSION_MARGINAL_PREREG.md` r475 冻结（R99：冻结 commit 先于烧）；runner `scripts/exclusion_marginal_scan.py` probe/selftest 腿已落地（probe facts=results/exclusion_marginal_scan/probe_facts.json；selftest 5/5；run 腿引擎下片诚实 rc=2 零烧）。试验量：烧批 +16 格 → 累计 318/500。

## 设计一句话

冻结经典低量选股基线（20 日均额升序取 10 只月频等权 T+1），16 格全量公布扫描 6 排除规则（R-配1 亏损/R-配2 ST/SS2 流动性地板/价格地板/次新 250bars/停牌活跃 10td）的 LOO+AOI 双面边际值+随机选股 null 交互面；判据=全期 Δ>0 ∩ 全起点正份额 ≥0.50 ∩ 起点中位 Δ>0（跑前写死）。

## 边际值表（烧后回填·占位）

| 规则 | Δ 全期（FULL−LOO） | 全起点正份额 | 起点中位 Δ | AOI 面 Δ' | 判定 |
|---|---|---|---|---|---|
| r1_loss | — | — | — | — | 待烧 |
| r2_st | — | — | — | — | 待烧 |
| l1_liq5000w | — | — | — | — | 待烧 |
| l2_price1y | — | — | — | — | 待烧 |
| l3_age250 | — | — | — | — | 待烧 |
| l4_active10td | — | — | — | — | 待烧 |

（§7 详版在预注册件回填）
