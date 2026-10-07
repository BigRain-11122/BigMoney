# ZT_POOL — 涨停池四面前向日采集面板（O-20261001-2103 R2 数据面）

- gate：`scripts/update_zt_pool.py`（S6 链位次=update_lhb 之后）
- 车道：bm-a 独占（R31 判例·O-20261001-2103 bm-a 认领线）；他机 stdout-only 诚实 no-op 零共享态写（R65）
- 血统：akshare EM zt-pool 族（本地 1.18.96 四 API 实核·`results/oss_eng_scan/vibe-probe-20261008.json`+`research/OSS_HARVEST_LEDGER.md` L130）；配线范式=bigmoney-data-gate-wiring 契约十律全过

## 数据面

| key | akshare API | 面 | 情绪轴 |
|---|---|---|---|
| zt | stock_zt_pool_em | 涨停股池（含连板数梯队） | 赚钱效应 |
| zbgc | stock_zt_pool_zbgc_em | 炸板股池 | 分歧 |
| dtgc | stock_zt_pool_dtgc_em | 跌停股池 | 亏钱效应 |
| strong | stock_zt_pool_strong_em | 强势股池 | 强度辅助 |

- 面板：`data/zt_pool/<key>.parquet`（全日 concat·首列 `日期`·追加去重键=(日期,代码)·原子写）
- 完备面：`data/zt_pool/collected_days.json`（逐端点日账——零行日=账记不落行；cutoff 从日账字节 derive）
- 状态镜：`results/zt_pool_update_status.json` + 本机 lane 镜 `zt_pool_update_status`

## 守卫（契约映射）

1. 15:30 no-op 门=**经日历传递**：只采集 update_daily 已落 bar 的交易日（bar 未落禁拉纯形，比墙钟 15:30 更严；sina 迟 bar 自愈=同 lhb 已录文行为）。
2. 前向积累制：FIRST_DATE=2026-10-08 起；gate 不回填历史（回填=GM 车道决策，lhb store-absent 同律）；**T-67 §2 冻结律：前向史≥12 个月才准新 prereg**——本道纯采集零回测零引擎。
3. overlap 行级校验：每次 pass 重拉各端点最新采集日，按（代码→涨跌幅）逐行比（NaN==NaN·顺序无关）；失配=**exit 3 本地不动**（池日片收盘即终态，无 LHB 迟披露超集受理面——如日后实证良性补全再按 r280 先例修法）。
4. 形状漂移=不变列（代码/名称/涨跌幅〔zt+strong 加连板数〕）缺失=blocked 旗标+exit 3 待人工裁定（ths 先例）；R58 行壳防御=空/NaN 代码行不落地。
5. conn-fuse 3 连败停发（已落日保留·断点=日账）；2.5s 限速；30min 节流+attempt 先记后拉（r18）；r806 45s 超时夹克。
6. exit 契约：0=正常/no-op；2=源失败/熔断中止；3=overlap 失配/形状漂移。禁吞错禁改码。

## 消费面（R2 供给指针，未建）

- 情绪周期三轴门（涨停数/炸板率/跌停数）→ REGIME-5 供给线（O-20261001-2103 §二 R2）
- 连板梯队/题材共振——zt 面连板数+所属行业列直接可用
- 判据面一切等前向史≥12 个月后预注册（先廉价普查后烧·O-1901 意义闸）
