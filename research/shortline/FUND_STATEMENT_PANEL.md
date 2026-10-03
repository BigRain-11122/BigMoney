# FUND_STATEMENT_PANEL — 财报三面批量采集面板（T-2026-10-04-166-P1 DATA LEG）

状态：**在役**（r663 bm-a 交付 collector；backfill 见 status 面）
车道：`bm-a` 独占（R31 判例·fundamental 数据道宿主=update_fundamental.py 家族）
票：`fleet/tasks/T-2026-10-04-166-P1.json`（GM 署名 P1·O-20261002-2115 family-line 承继）
探针证据：`results/_r663bma_cfo_source_probe_facts.json`（r663·6/6 OK·akshare 1.18.96）

## §1 目的（Why）

FUND 家族线（O-20261002-2115 血统）判决消费面需要的三个"报表原值面"：
现金流量表 CFO（piece-4 瑞克现金流法则·应计 CFO−NI 楔子·Sloan 血统）、
资产负债表（piece-5 储备腿 FFScore 部分 dROA/d_leverage）、
业绩表（gross_profitability flip 候选·r595 leg(b) 注记 income face 缺席）。
本面板=纯采集数据腿：**零回测零引擎零准入零 marks/SEED/账本触碰**。

## §2 源与形状（frozen schema）

EM datacenter 按报告期批量三接口（akshare 包装）：

| face | 接口 | 报告期参数 | 行规模（探针） | 披露列 |
|---|---|---|---|---|
| cashflow | `ak.stock_xjll_em(date=YYYYMMDD)` | 20050331..最新法定完备 | 5233 @20250630·1539 @20051231 | 公告日期 |
| balance | `ak.stock_zcfz_em(date=...)` | 同上 | 5242 @20250630 | 公告日期 |
| income | `ak.stock_yjbb_em(date=...)` | 同上 | 11609 @20250630（含北交所 87xxxx） | 最新公告日期 |

冻结列集=探针原文列集（byte-identical，`FROZEN_COLS`）——**列集漂移=ShapeDrift→
blocked exit 3 诚实待人工裁定**（update_ths_panel 先例，禁自愈）。

## §3 PIT 面与判据继承（How consumed）

- 每行携带披露日期列 → 归一为 `avail_date`（YYYY-MM-DD 或 None，缺=诚实缺）。
- 消费侧可用性锚 = **max(实际披露日, 法定截止日)**（T-145 leg(a) 回执继承：
  法定锚门）。法定截止：Q1→04-30·H1→08-31·Q3→10-31·年报→次年 04-30。
- 值列=**as-disclosed 原始累计值**（零采集侧推导）；TTM=消费侧纯函数
  `ttm_from_cumulative`（本模块可 import，delta 链=年报孪生双口径等价，缺季→None）。

## §4 修订局限（诚实披露·r595 leg(b) 先例）

EM 按期接口返回**当前最新修订值**（带最新公告日期）——本面板=as-collected
快照：历史期一旦采集即冻结（done-key 永不重拉）；季度重拉 diff=后续切片。
前向刷新=**仅缺期补拉+法定截止已过门**（新期跨过法定截止才进预期集）。

## §5 存储

```
data/fund_statement_export/            （gitignored·大可再生工件）
  _staging/<face>_<period>.parquet     每期快照替换单元（tmp+os.replace·(code,period_end) 去重）
  {cashflow,balance,income}_faces.parquet   装配面（(code,period_end) 排序·原子）
  _progress.json                        done-key checkpoint（iface:period）
  status.json / _refresh.lock           运行态/pid 活锁
results/fund_statement_update_status.json  提交态 status 面（家族先例）
```

面 schema：`code`（6 位归一·zfill 防零剥离）+`period_end`+`avail_date`+`name`
+冻结中文值列（原值 verbatim）。行壳防御 R58：非 6 位数字 code 行丢弃。

## §6 采集纪律（gate 契约）

- no-op 门：三面 parquet 覆盖恰=预期期集（20050331..最新法定完备期）→零网络
  no-op；覆盖从**面板字节 derive**（禁符号轮）。
- 分离后台 refresh：gate 立即返回；per-(iface,period) checkpoint 断点续拉；
  2.5s 限速+per-call 重试×2（5s 退避）+conn-fuse 3 连败停发（30min spawn 节流自愈）
  +pid 活锁+call watchdog 120s（防挂死）。
- 窗卫：交易日 09:15-15:30 EM 压力带禁拉（报表面=披露耦合非 bar 耦合，
  无 bar-landed 门；带内=干净中止 exit 2·checkpoint 保全）。
- CPU 余量律：分离进程 BELOW_NORMAL 优先级（CEO 10% 余量令）。
- 0 行期=诚实零行期（done 记 n_rows=0，勿死循环重试）。

## §7 exit-code 契约

gate：0=ok/no-op/已 spawn/在途·2=机制故障·3=形状漂移（blocked 待裁定）
refresh：0=期集完备·2=未完备（fuse/窗关·checkpoint 保全）·3=形状漂移
车道护栏：非 bm-a=stdout-only 诚实 no-op 零写（R31/R65）。

## §8 冻结律（T-67 §2）

本道纯采集：前向史 **≥12 个月**才准任何基于本面的新预注册；判决/引擎面
一切接触走正式票+预注册门（D6 同族相关性准入照旧）。
