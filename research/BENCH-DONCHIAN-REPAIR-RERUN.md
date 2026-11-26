# 把高低价换回收盘的单位之后，这些卡翻不翻

cell `donchian_repair_rerun` · cutoff **2026-11-25** · 生成 2026-11-26T18:22:37+08:00

r2142 找出毛病（突破规则拿“调整后的收盘指数”跟“原始价位高低价”比），r2143 量出它只坏了一条规则。这一件回答后面那个真正会改决策的问题：**单位修好之后，有哪张卡的判词会翻？钱会不会冒出来？**

做法：同一份今天的面板，只换高低价的单位，其余（成本 3bp/边、波动目标、样本外切点 2024-01-01、判据、随机对照 100 次同种子）全部不动。发布的卡片数字并列印出，只作忠实度核对——面板比那些卡生成时已经长了两天。

## 一句话

- 修好单位之后**判词翻面的卡：1/4**（census_commodity: CENSUS_SIGN_MIXED → CENSUS_LEANS_POSITIVE）
- 修好之后最好的可分辨臂：**+3.41% / 夏普 0.41 / 回撤 -35.21%**（`census_commodity` · `donchian|{'entry': 20, 'exit': 10}|long` · MDE 4.16pp）
- 够格上钱（判词 GO）的臂：**0 条**——修好单位只是让它能往两边做，并没有把噪声变成边际

## 两种修法给出相反的答案（本轮最重要的一条）

同一条规则、同一份面板、同一套成本，只因为“把换月跳空怎么处理”不同，`fut_trend` 的 `donchian` 相差 **+10.72pp/年**：

| 修法 | 做多占比 | 年化 | 夏普 | 回撤 | 样本外 | 随机对照 p | 判词 |
|---|---|---|---|---|---|---|---|
| `per_bar` | 0.3701 | -2.12% | -0.086 | -39.70% | +6.58% | 0.5167 | **NO_EDGE** |
| `first_close` | 0.7974 | +8.60% | 0.733 | -28.08% | +12.31% | 0.0583 | **NO_EDGE** |

**不能按哪个数好看选哪个修法。** 定这次口径的不是收益，是收益面本来怎么算的：`bench_core.roll_adjusted_returns` 已经把换月跳空从收益里剔掉（跳空那根 bar 的收益记 0），所以任何“能拿到的收益”都不包含跳空。若通道里仍保留跳空（`first_close`），规则就会对着一个**在收益里不存在**的价格跳空做决定——这类信号天然不可实现。因此本件采 `per_bar`（乘子 = 同 bar 调整价/原始价，逐 bar 变化，正好抵消跳空），`first_close` 只作敏感性并列，不推荐。

## 方法：三种单位，同一个面板

| 方法 | 怎么算 | 意思 |
|---|---|---|
| `raw_panel` | published behaviour: adjusted close compared against raw high/low | 发布口径（有缺陷） |
| `per_bar` | high/low x (raw close / adjusted close) on the same bar | 候选修法 |
| `first_close` | high/low / first raw close of that product | 候选修法 |

两种修法不是同一个答案：`per_bar` 的乘子随换月变化，把“已在收盘序列里剔除的换月跳空”同样从高低价里剔掉；`first_close` 一个品种一个常数，高低价里仍带着换月跳空。表格里两列并列，读者自己看差多大。

## 逐卡读数

### 判词

| 卡 | 发布判词 | 今天·原始高低价 | `per_bar` | `first_close` | 翻面? |
|---|---|---|---|---|---|
| `census_commodity` | CENSUS_SIGN_MIXED | CENSUS_SIGN_MIXED | CENSUS_LEANS_POSITIVE | CENSUS_LEANS_POSITIVE | **翻** |
| `census_index_futures` | CENSUS_UNPOWERED | CENSUS_UNPOWERED | CENSUS_UNPOWERED | CENSUS_UNPOWERED | **不翻** |
| `robust_donchian_index` | UNSTABLE_ACROSS_PARAMS | UNSTABLE_ACROSS_PARAMS | UNSTABLE_ACROSS_PARAMS | UNSTABLE_ACROSS_PARAMS | **不翻** |
| `fut_trend` | NO_EDGE | NO_EDGE | NO_EDGE | NO_EDGE | **不翻** |

### 每条 donchian 臂：做多占比（缺陷的指纹）

| 卡 | 臂 | 原始做多占比 | `per_bar` | 原始年化 | `per_bar` 年化 | `first_close` 年化 | 可分辨? | 判词(`per_bar`) |
|---|---|---|---|---|---|---|---|---|
| `census_commodity` | donchian|{'entry': 20, 'exit': 10}|long | 0.0 | 0.4651 | -4.52% | +3.41% | +6.77% | True | **NO_EDGE** |
| `census_commodity` | donchian|{'entry': 20, 'exit': 10}|ls | 0.0 | 0.4076 | -4.52% | +2.11% | +6.46% | True | **NO_EDGE** |
| `census_commodity` | donchian|{'entry': 55, 'exit': 20}|long | 0.0 | 0.3931 | -4.25% | +2.11% | +5.48% | True | **NO_EDGE** |
| `census_commodity` | donchian|{'entry': 55, 'exit': 20}|ls | 0.0 | 0.3553 | -4.25% | +1.86% | +6.06% | True | **NO_EDGE** |
| `census_index_futures` | donchian|{'entry': 20, 'exit': 10}|long | 0.0 | 0.4017 | -3.91% | +0.79% | +0.29% | False | **NO_EDGE** |
| `census_index_futures` | donchian|{'entry': 20, 'exit': 10}|ls | 0.0 | 0.3505 | -3.91% | -2.90% | -2.57% | False | **NO_EDGE** |
| `census_index_futures` | donchian|{'entry': 40, 'exit': 15}|long | 0.0 | 0.3547 | -3.99% | +0.10% | -0.68% | False | **NO_EDGE** |
| `census_index_futures` | donchian|{'entry': 40, 'exit': 15}|ls | 0.0 | 0.3264 | -3.99% | -1.16% | -1.19% | False | **NO_EDGE** |
| `census_index_futures` | donchian|{'entry': 55, 'exit': 20}|long | 0.0 | 0.3756 | -3.70% | +1.44% | +1.24% | False | **NO_EDGE** |
| `census_index_futures` | donchian|{'entry': 55, 'exit': 20}|ls | 0.0 | 0.3419 | -3.70% | -0.07% | +0.58% | False | **NO_EDGE** |
| `robust_donchian_index` | 20_10 | 0.0 | 0.3505 | -3.91% | -2.90% | -2.57% | False | **NO_EDGE** |
| `robust_donchian_index` | 40_15 | 0.0 | 0.3264 | -3.99% | -1.16% | -1.19% | False | **NO_EDGE** |
| `robust_donchian_index` | 55_20 | 0.0 | 0.3419 | -3.70% | -0.07% | +0.58% | False | **NO_EDGE** |

### `bench_fut_trend` 的第五条风格（同一个毛病，另一份脚本）

它自己那套判据（H1 6% / H2 4%+0.5 / H4 2% / H5 0.05）和“必须赢过同篮子持有 2pp”的追加条款原样沿用，同篮子持有年化 +12.67%。

| 方法 | 做多占比 | 年化 | 夏普 | 回撤 | 样本外 | 相对持有 | 判词 |
|---|---|---|---|---|---|---|---|
| `raw_panel` | 0.0 | -13.35% | -0.914 | -81.03% | -16.23% | -26.02% | **NO_EDGE** |
| `per_bar` | 0.3701 | -2.12% | -0.086 | -39.70% | +6.58% | -14.79% | **NO_EDGE** |
| `first_close` | 0.7974 | +8.60% | 0.733 | -28.08% | +12.31% | -4.07% | **NO_EDGE** |

## 忠实度（我们能不能重跑出发布过的数）

- `census_commodity`：对上 4 条，最大差 0.02pp；无一条超 1pp
- `census_index_futures`：对上 6 条，最大差 0.23pp；无一条超 1pp
- `robust_donchian_index`：对上 3 条，最大差 0.23pp；无一条超 1pp
- `fut_trend`：对上 1 条，最大差 0.0pp；无一条超 1pp

面板延伸到今天，所以差几个零点几本来就是预期的；真差到 pp 级才是分歧。

## 换月面：两种修法分歧的来源

- `census_commodity`：共 **103** 根 bar 被 `bench_core` 判为换月（判据 8× 中位绝对变动且 >0.5%），逐品种 AU=49、RB=41、SC=13。这些 bar 就是 `first_close` 把跳空留回通道、`per_bar` 把它抵消掉的地方。
- `census_index_futures`：共 **56** 根 bar 被 `bench_core` 判为换月（判据 8× 中位绝对变动且 >0.5%），逐品种 IH=17、IC=16、IF=15、IM=8。这些 bar 就是 `first_close` 把跳空留回通道、`per_bar` 把它抵消掉的地方。
- `robust_donchian_index`：共 **56** 根 bar 被 `bench_core` 判为换月（判据 8× 中位绝对变动且 >0.5%），逐品种 IH=17、IC=16、IF=15、IM=8。这些 bar 就是 `first_close` 把跳空留回通道、`per_bar` 把它抵消掉的地方。
- `fut_trend`：共 **182** 根 bar 被 `bench_core` 判为换月（判据 8× 中位绝对变动且 >0.5%），逐品种 AU=49、RB=41、IH=17、IC=16、IF=15、SC=13、TF=11、IM=8、T=8、TS=4。这些 bar 就是 `first_close` 把跳空留回通道、`per_bar` 把它抵消掉的地方。

## 射程与未验证（如实）

1. 本件**不改** `bench_generic.sig_donchian`、不改任何已发布卡片，也不应用判词翻面——修共享代码面需要无竞争窗（本轮同宿主在写共享面，只落新增文件）。
2. 单位修好只解决“能不能做多”。`per_bar` 里乘子来自同一根 bar 的收盘，而每根 bar 的 high/low 是真实成交区间，滚动窗口跨换月时窗口内仍然是不同合约的价位；更严格的修法是回测层面用后复权连续合约，属数据面工程，不在本件射程。
3. 随机对照是同一组权重换符号（`bench_core.random_sign_control`，100 次、同种子），它检验的是“方向是否比乱摆强”，不检验入场时点。
4. 修正后的 MDE 与可分辨性沿用卡片自己的目标边际（5pp / fut_trend 自带 6pp 档），本件没有重新标定门槛。
5. 口径选定 `per_bar` 的理由是“收益面已剔除换月跳空，信号面不能对着跳空决策”，这是口径论证，不是收益论证；`first_close` 的数字并列印出正是为了让读者看到“按钱选口径”会把一条死风格抬成 4/5 门候选。
6. 判词翻面只报不应用：`census_commodity` 从 MIXED 翻到 LEANS_POSITIVE 的意思是“这个空间里可分辨的臂全是正的”，**不等于**有一本书可以上钱——最好的可分辨臂 年化 3.41%、回撤 -35.21%，自己那五道门一条都没全过。

## 下一手

- 无竞争窗时：把 `sig_donchian` 的输入改到同一套单位（推荐 `per_bar`），重跑 `census_commodity` / `census_index_futures` / `robust_donchian_index` / `bench_fut_trend` 四张卡，并把 r2140 答卷册与 r2141 去重面重 derive（它们把 14 行缺陷臂算成 EXHAUSTED 证据）。
- 把「新信号族必须过单位扰动」做成冒烟腿（r2143 已给判据，本件给的是它翻不了判词的证据）。

