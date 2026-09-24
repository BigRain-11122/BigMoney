# THS_PANEL — THS 全单聚合资金流辅助面板 spec（T-2026-09-25-43 slice-4）

> 车道：dept:数据｜bm-a 独占（R31 判例族）｜预注册=`research/shortline/THS_AGG_P1.md`（冻结 commit a30d2ee5，两相批 A 相采集面）
> 本件=采集/存储/消费契约 spec；科学判据一律以预注册为准（禁本件改判据）。
> 亲族：update_moneyflow（T-39 EM 主力分解面）。**量纲隔离律**：本面=全单聚合口径，与 EM 分解面分件分库，禁混读。

## §1 量纲诚实律（R118 律，最高约束）

- 源=同花顺 data.10jqka.com.cn/funds/ggzjl 横截面，**全单聚合口径**：`净额(元)=流入−流出`（实证 2.99亿−2.71亿≈2753.86万）；无主力/超大单/大单/中单/小单分解、无净占比列。
- 列名/列序与探针 raw（`results/shortline/t41_ths_probe_raw.json`）**字节恒等**：`序号/股票代码/股票简称/最新价/涨跌幅/换手率/流入资金(元)/流出资金(元)/净额(元)/成交额(元)`；任何漂移=即停采集待人工裁定（预注册 §2(c)）。
- **聚合量映射为主力/超大单/大单语义=量纲造假，禁行**；一切消费面标签必须写明「全单聚合口径」。
- 金额列原样保留「亿/万」后缀字符串，解析归消费侧（B 相脚本）；采集器零解析。
- **代码列 6 位恒等律（R121 实弹教训）**：`股票代码` 一律 6 位数字符串——pd.read_html 数值推断会把 000xxx 剥成短码（首发实弹 1491/5210 行踩中），采集器 `_fix_code` zfill(6) 确定性恢复（A 股代码恒 6 位=双射幂等，非数字值原样透传）；探针 raw 的 `numeric_cols` 字段=该列数值化预警，实现新源解析器前必读探针全 schema；自检夹具必含零前导样例（F8）。

## §2 面与日期戳语义（前向锁盒）

- ggzjl 为**当日快照面，无历史回填 API** → 面板=前向累积：每完整 bar 日一行截面，自 2026-09-25 起累积。
- date-stamp=**最后完整 bar 日**（本地 ETF 交易日历 data/daily 510300 主源，15:30 约定；T-39 item-1 语义）。
- **面纪一致性律（核心诚实不变量）**：快照永远显示「最后一个已完结 session」；拉取合法当且仅当 面纪日==date-stamp：
  - 交易日 T 开盘前（<09:15）：面=T 前一 session，stamp=日历末日（=同一日）✓ 一致（合法 gap-fill 窗）；
  - 交易日 T 09:15-15:30：面变异中/将翻→禁拉（预注册 09:15-15:05 盘中禁拉内含 + 15:05-15:30 戳险带，family rank guard）；
  - 交易日 T ≥15:30 且 T 未入本地日历：面=T 收盘终值但 stamp 仍=T−1（bar 未落）→ **不一致=禁拉**，待 update_daily 落 bar 自愈（日历推进=一致性 oracle，T-39 同构）；
  - 交易日 T ≥15:30 且 T 已入日历：面=T=stamp ✓；
  - 非交易日（周末/节假日）：面静态=最后 session ✓ 任意时刻合法（gap-fill 窗）。
- **日历滞后保守闸（calendar_face_consistent）**：stamp 与今日之间若存在**未记账周中日**（=该日无落 bar：节假日或 update_daily 整窗失败两态不可分辨）→ 保守禁拉——update_daily 失败态下面纪可能已翻到该日，拉取即错标日=造假；节假日代价=gap-fill 窗收窄（诚实 > 完备，前向锁盒容忍 gap）。
- 中断续拉（checkpoint resume）同受面纪律约束：`resume_valid()` 判定 progress.bar_day 与当前面纪是否同纪；**跨面纪续拉=混合日文件=造假，结构性禁行**（bar_day 之后有已落 bar 的交易日、或当日为交易日且 ≥09:15 → 旧 progress 弃置+诚实 gap 记录）。
- 丢日=永久 gap（源无回填）：如实缺席，禁编造；B 相完备门（≥130 交易日）按文件面计数。

## §3 采集契约（预注册 §6 冻结面）

- 预算：105 请求/日名义（105 页×50 行≈5,222-5,250 股；pages_total 以 page_info 实读为准，偏离如实记 status）。
- 公民步速 2.5s/页；页级重试×2（5s 退避）；conn-fuse=连续 3 页失败停发（checkpoint 保全，gate 30min spawn 节流自愈）。
- checkpoint：`_progress.json`={bar_day, pages_total, pages_data}（页集），逐页落盘；bar_day 滚动或面纪失效→reset+弃日记录。
- 逐页窗卫：每页拉取前复检 `pull_allowed`（防长拉跨 09:15 面变异）；中窗关闭=干净中止 exit 2（已拉页=同面纪静态数据，checkpoint 保全）。
- 同日幂等：`daily/<stamp>.csv` 在位=零网络 no-op（文件存在=该日完备，刷新只在全页集齐后一次性落盘）。
- 分离后台：gate=零网络判定+spawn detached refresh（update_moneyflow 先例）；IO 型非 CPU 批，不入 runnable_pool。
- 车道护栏：仅 bm-a 动作；他机 stdout-only 诚实 no-op、零落盘（R31+R65 律）。

## §4 存储与状态（machine-local，gitignore data/ths_ggzjl/）

- `data/ths_ggzjl/daily/<bar-day>.csv`：UTF-8 无 BOM，header=§1 十列，一行一股，值=源字符串口径原样（万/亿后缀保留）。
- `data/ths_ggzjl/_progress.json`：checkpoint（上）。
- `data/ths_ggzjl/status.json`：{ts, cutoff, complete, rows, pages_total, requests_used, crisis_flag, dup_count, abandoned_days[], blocked, block_reason, mode, last_spawn_attempt, last_refresh_exit}。
- `data/ths_ggzjl/_refresh.lock`：{pid,ts}，pid-liveness 判活（D-03 族）。

## §5 健康线与审计（A 相持续在岗，判读归 B 相/审计面）

- 分布界主责=日行数滚动 20 日 median ≥5,000；单日 <4,800=危机日志候选（大面积停牌潮形态）+豁免单列，不判腐坏不入样本（预注册 §2 三件套）；采集器仅记 rows+crisis_flag，median/豁免判读=B 相审计。
- 列名字节恒等校验败=blocked=true 停采待人工裁定（无自愈，gate 诚实 exit 3 上报）。
- B 相完备门：面板 ≥130 交易日 complete 且 EM 面板同日重叠 ≥30 日，未过门禁跑批。

## §6 消费契约（B 相，THS_AGG_P1 §0/§3 冻结面）

- 消费者=`scripts/ths_agg_p1.py`（两格 ths_net_ratio / ths_net_ratio_ma5，h10 门控，D6 四对 EM 冗余门控，seed 族 ths_agg_p1 56,000-56,049）。
- 万/亿后缀解析在消费侧（亿=×1e8、万=×1e4）；禁以 THS 快照价替代复权 close（前瞻收益面=p1c_stock 前复权缓存）。
- 面板列名只读：消费脚本禁改列名/列序（漂移即 §1 停采级事件）。

## §7 子命令与 exit 契约

- `python scripts\update_ths_panel.py`（无参=gate）/ `refresh` / `status` / `selftest`（离线四夹具+面纪续拉夹具，hermetic 零网络零仓写）。
- gate：exit 0=正常/no-op/已 spawn/刷新在途；2=机制故障；3=源形状漂移（blocked 待人工裁定）——2/3 原样上报勿掩盖。
- refresh：exit 0=当日截面完备落盘；2=未完成（fuse/中窗关闭/超页帽，checkpoint 保全自愈）；3=形状漂移（blocked）。

## §8 S6 链位与亲族指针

- 链位：`python scripts\update_moneyflow.py` 之后、`update_fund_premium.py snapshot` 之前（R121 接线）。
- 亲族：MF_COLLECTOR.md §8（量纲修正与候选登记）／T-39（EM 分解面，独立验收在飞，本面零触碰）／DIGEST-20260925-t41-alt-source-probe.md（源探针实证）。
