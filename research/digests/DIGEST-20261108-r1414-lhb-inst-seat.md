# DIGEST 20261108 r1414 bm-c — the institutional seat aggregate exists, and it is a pool story

**窗口** bm-c, round 1414（state round_no=1413 at open；r1413 的遗产由本窗复核后并入，见末节）
**产品** `scripts/update_lhb_inst.py` + `scripts/zoo99_lhb_inst_netratio_probe.py`
**证据** `data/lhb_inst/lhb_inst.parquet` · `results/supply_berth/zoo99_lhb_inst_netratio_probe.json` · 卡 E417

## 1. 为什么这一轮存在

r1405 给 zoo #94（龙虎榜机构择时）判了 `verdict_scope='frozen rule untested'`：冻结规则要的机构分子
在 `Money02/data/lhb/lhb_detail.parquet`（268,044 行、有净买额、**无席位列**）里根本不存在。它存在于
源头——EM datacenter `stock_lhb_jgmmtj_em(start_date, end_date)` 按（股票, 上榜日, 上榜原因）给出
买方机构数 / 卖方机构数 / 机构买入总额 / 机构卖出总额 / 机构买入净额 / 机构净买额占总成交额比，
可回溯到至少 2012-06（实测 2012-06 / 2018-01 两窗均返回）。

## 2. 车道

`scripts/update_lhb_inst.py`（selftest 13/13）：月页拉取 → 规范化（6 位码、非 A 股码按桶丢弃并计数）
→ key = (代码, 上榜日期, 上榜原因) 去重 → 与旧面板按 key 合并 → overlap 逐行比对（失配 = 厂商改史，
exit 3 本地不动）→ 每页即时落盘 + checkpoint → 连接级 3 连败熔断 → 面板覆盖预期完整 bar 日即零网络
no-op。车道归属走 `config/lane_hosts.json`（本窗新增 `update_lhb_inst: bm-c`），非宿主机诚实 no-op。

首跑：**83 页 / 298s / 58,636 行 / 5,154 码 / 2020-01-01..2026-11-06 / overlap 失配 0**。
（`arrows`：其中 216 个代码在价格面板里没有对应文件，覆盖报告如实列出，不静默丢。）

## 3. 定价（冻结规则先写进脚本头注，跑完不改）

score(股, 日) = Σ机构买入净额 / Σ市场总成交额（同一 (股,日) 的多行相加；累计原因行分子分母同为累计，
比值仍是比值）；signal = 20 日滚动均值；簇内取 top decile，等权，20 日 cohort，次日开盘进；
成本 13.041bp/边 ×{1,3}；相位 {0,5,10,15}；零假设 = 同决策日在同一合格集里**随机抽同样名数** 200 次。

| 臂 | 净 CAGR | 夏普 | 回撤 | 平均名数 |
|---|---|---|---|---|
| top decile ×1 | **−1.12%** | 0.12 | −59.5% | 35 |
| top decile ×3 | −7.19% | −0.08 | −66.0% | 35 |
| n50 ×1 | −5.36% | −0.01 | −65.3% | 50 |
| pool（同池全部合格名）×1 | **−10.39%** | −0.17 | −67.8% | 345 |
| bottom decile ×1 | −3.67% | 0.02 | −60.3% | 35 |

相位超额 +9.27 / +9.72 / +3.48 / +8.27 pp（四相位全正）；零假设 200 次均值 −0.47%/cohort、sd 0.30%，
观测 p = **0.005**。冻结四条件 C1–C4 全过 → `ADMIT_TO_PREREG`。

## 4. 这个判决不能被读成什么

- 两条臂**绝对值都是亏的**。判决只说「在龙虎榜名池里，按机构净买比挑名字优于随机挑」，不说这本书能赚钱。
  对照 r1412：全液池等权 +10.11%/yr —— **换池子比换因子重要一个量级**。
- 81 个 cohort 里 top decile 的成分高度重叠（信号是持久的），独立赌注数远小于 81；p=0.005 是「对同池随机」
  的 p，不是「对时间独立」的 p。
- 27.3% 的行带「连续三个交易日…累计」原因；分子分母同为累计时比值可用，但**不能当当日事件读**。

下一步（写在 prereg 待办里）：把它当 r1412 全液池上的 overlay 重新定价——信号只决定「在池内超配谁」，
不决定「要不要持有这个池子」。

## 5. 本窗的另一件事：死窗遗产与孤儿链

轮首状态：state round_no=1413，但 r1413 的产物（`scripts/astock_size_age_control.py`、
`results/size_decomp/astock_size_age_control.json`、卡 E416、digest）**全部未提交**，且
`Tools/s6_chain_bmc.py 1413` 以已死父进程、0% CPU、57.7 分钟挂在那里。孤儿探针三面判定（父死 /
无隐藏宿主祖先 / CPU 停滞）成立，按 `orphan_face_probe.py kill` 收编击杀（pid 89512）。

遗产处置按 r1213 律——**在最终树上重跑再落账**：`astock_size_age_control.py selftest` 8/8，`run` 116s
复跑，与遗留 JSON 逐键比对（剔除 elapsed/asof 元数据）**完全一致**，判决
`SIZE_SURVIVES_AGE_CONTROL` pooled 14.431pp / prepanel 20.371pp / 12/12 相位。据此把 r1413 的遗产与
本轮产物一并提交，不再默认它「已经绿了」。