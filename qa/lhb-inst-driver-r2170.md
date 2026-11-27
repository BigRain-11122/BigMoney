# QA — lhb_inst：把「被指派」变成「有驱动」（r2170, bm-c）

## 问题（从哪来）

r2169 的 `scripts/lane_lag_attribution.py` 把 `data_lane_freshness` 的每一行滞后拆成「谁本该动它」，读数里有一条最刺眼的：

```
lane=lhb_inst  verdict=stalled  tail=2026-11-20  expected=2026-11-26  n_missing=4
cause=declared_host_without_driver
detail=drivers: chain=False task=0 register=0 declared_host=bm-c
```

三层事实同时成立：车道被 `config/lane_hosts.json` 指派给 bm-c、写入器 `scripts/update_lhb_inst.py`（18,710B）在盘、面板 `data/lhb_inst/lhb_inst.parquet` 在盘——但**四源驱动里三源（链腿 / 计划任务 / 注册脚本）全空**，所以它停 4 个交易日而所有审计只印「owner bm-c, host alive」。这张面板是 r1405 曾因缺机构席位列而把 LHB 机构择时规则降级为 `frozen rule untested` 的唯一数据来源。

## 做了什么

1. **跑了一次写入器**（不是改代码，是让已有写入器真的执行）：
   `python scripts/update_lhb_inst.py run` → 拉 20261101..20261126 月页，overlap 校验 0 失配。
2. **把驱动接进链**：`Tools/s6_chain_bmc.py` 在 `update_lhb` 之后加一腿
   `("update_lhb_inst", ["python", "scripts/update_lhb_inst.py", "run"])`，位置理由=与 `update_lhb` 同为同一 vendor 同一 `上榜日期` 的席位列聚合，写者排在读者之前。

## 实测读数（本轮，2026-11-27）

| 项 | 前 | 后 |
|---|---|---|
| `cutoff` | 2026-11-20 | **2026-11-26** |
| `rows` | 59,022 | **59,180**（+158） |
| `codes` | 5,157 | 5,157 |
| `months_done` | 83 | 84 |
| overlap `mismatch` | — | **0** |

逐日行数（`上榜日期` 聚合，11-16 起）：

```
2026-11-16  31
2026-11-17  49
2026-11-18  46
2026-11-19  49
2026-11-20  32
2026-11-21   -   (周六)
2026-11-22   -   (周日)
2026-11-23  46
2026-11-24  31
2026-11-25  39
2026-11-26  42
```

新增四天 = 46+31+39+42 = **158**，与 `rows` 增量逐位相等 → 面板是真的逐交易日补齐，不是「只拉到某一天然后把 cutoff 写成最后一天」。

## 幂等与链门

- 新腿首次单跑：`0 update_lhb_inst  13.8s  lhb_inst: no-op (cutoff 2026-11-26 == expected 2026-11-26)`，`chain: 1/1 rc0` → 面板已覆盖时期望日时**零网络**，不会每轮打一次 EM。
- 链自检：`python Tools/s6_chain_bmc.py --selftest` → **17/17 PASS**（含「every leg is (name, cmd[, refresh])」「check-only legs declare a refresh (n=137)」两条覆盖 LEGS 表结构的腿）。

## 同族第二半：接管权被宣告了，没有人行使（heat / repo）

`data_lane_freshness` 同时印着：

```
SILENT-OWNER bm-a age_h=206.65 lanes=futures,heat,lhb,repo
               taken_over=futures<-bm-c,heat<-bm-c,lhb<-bm-c,repo<-bm-c
```

接管权已经判给本机，但直接调 `update_heat.py` / `update_repo.py` 的实际输出是：

```
no-op: heat lane host bm-a authority, this machine (bm-c) stdout-only (R31 lane-guard);
       takeover refused: no --takeover flag
no-op: repo rates lane owned by bm-a, not this machine (bm-c);
       takeover refused: no --takeover flag
```

链腿写的是**裸调用**，而这两个写入器的接管门要一个显式 `--takeover`。于是「有接管权」与「接管被执行」之间差一个 flag，面板就停着——与 r2169 的 `declaration != driver` 是同一个病的两个面：**permission != exercise**。

修复采用仓库里已有的范式（`update_futures` r1850 就是这么写的），两条链腿各加 `--takeover`：

| 车道 | 改前 | 改后 |
|---|---|---|
| `update_heat` | 裸调用（每轮拒绝） | `--takeover`（owner 已静默 206.6h ≥ 120min 门槛，接管生效） |
| `update_repo` | 裸调用（每轮拒绝） | `--takeover`（同上） |

门本身没有被削弱：owner 心跳一旦回到门槛内，`takeover_decision` 会重新拒绝，调用退回诚实 no-op。

**repo 的实测推进**（11 员各 +1 行，全部到 2026-11-26，exit 0）：

```
GC003 +1 → 3776   GC004 +1 → 3776   GC007 +1 → 3776   GC014 +1 → 3776
GC028 +1 → 3776   GC091 +1 → 3730   GC182 +1 → 3417   R-001 +1 → 3345
R-003 +1 → 3281   R-007 +1 → 3360
```

`data_lane_freshness` 复跑：`in_sync 10 → 11`、`behind_1d 2 → 1`。

**heat 是诚实的「补不回来」**：接管后它 refusal 变成了新的理由——

```
no-op: 2026-11-26 close is stale: the 2026-11-27 session opened at 09:15:00
       and the live ranking has moved on (a missed day stays missing)
```

人气榜是实时排行，错过的日子源端不再提供；11-20..11-26 永久缺失是数据源语义而不是本机缺陷，明天 15:30 后移交的链会采到 11-27 那份。

**lhb 不动（铁律优先）**：`update_lhb.py` 的写入目标是 `Money02/data/lhb`，本司铁律「不动 Money02」压过接管权。所以这条车道即使被宣告 `taken_over=lhb<-bm-c` 在本机也**不可行使**——已如实记入下轮指针，不擅自改链腿去绕过铁律。

## 没验证的（如实）

1. 只修了**驱动**，没动 `data_lane_freshness` 的 `window_trading_days` 阈值——这条车道下次若再停，审计仍只会说「stalled」，不会自动补拉（链腿是驱动，不是看门狗）。
2. `lhb_inst_ic.json` 的 `evidence_cutoff` 仍是 **2026-11-11**，且它**没有链腿**（同一个「有写入器没驱动」的病，另一处）。本轮不重跑它：它的 verdict 是 `CLOSE`（C1 IC 0.0202 < 0.03、C2 spread 0.433 < 0.5），按「判负真关线禁保载续烧」不该为了刷新鲜度再烧 51s。
3. 其余三条 `host_dead_takeover_available`（heat/lhb/repo，属主 bm-a 心跳已停）本轮未接管——那是另一台机器的车道，接管需要单独判断 owner 心跳龄是否已过 `TAKEOVER_STALE_MIN`。
4. `cb_panel`（`no_driver`，连指派都没有）本轮只做了归因，未实施：`data_lane_freshness` 把 writer 记为 `cb_dual_low`，但该脚本实际是**消费者**（读 `data/cb_panel.csv.gz`），真正的写者尚未定位 → 下轮指针。
