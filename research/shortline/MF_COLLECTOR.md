# MF_COLLECTOR — 个股主力资金流前向采集管道 spec 小件 V1（数据车道）

> 认领：bm-a 数据部（MSG-20260924-0920，F-04 先行；2026-09-24 R63）。
> 定位：R58 资金流源审计续作（`research/digests/DIGEST-20260924-moneyflow-source-audit.md`）；
> O-1620 GM 已批「资金流数据源」域（SHORTLINE_PLAYBOOK P-3 lane）；QUEUE_BANDIT explore 臂
> event-attention 的现成材料（R58 点名 mf_main_net_5/10/20 前向采集器）。
> 范式：update_daily / update_lhb / update_futures 同族（守卫幂等+原子写+诚实 exit 码+selftest 离线）。

## §1 采集物 V1（个股日频主力资金流滚动史面板）

- **源**：EM `push2his.eastmoney.com` 个股资金流日线（akshare `stock_individual_fund_flow(stock, market)`，
  R58 探针 A 三股实证从 bm-a 直连可用；120 交易日/股滚动窗硬顶——R58 定案：**lmt=0 请求也被源静默截断，
  永不信任请求参数，以响应行数为准**）。
- **滚动窗反推设计（本件核心裁定）**：源=120 交易日/股滚动窗 → **周期性全宇宙重拉即可维持无缝日频面板**
  （每股每次拉取都带回过去 120td 完整日线），刷新间隔只需 < 120 交易日。
  - 刷新触发门：面板 cutoff 落后最近完整 bar 日 **20 个交易日**（本地 ETF 交易日历，update_lhb R51 同构；
    无日历退化=28 自然日近似，如实降级）；首拉/未完成面板恒触发。
  - 拒绝「每日 5222 请求」设计（EM datacenter 公民义务，R19/P-C 单发纪律）；月度级全宇宙重拉
    ≈5222 请求 × 2.5s 限速 ≈ 3.6h，**一律后台分离跑**（r52 轮龄律），checkpoint 断点续拉。
- **宇宙**：`Money02/data/bars/*.parquet` glob = 5222 只（R36 宇宙扫描口径；北交所整库缺席=结构性）。
  market 推导：代码首 6=sh、其余 0/3=sz；非 0/3/6 前缀诚实跳过计数（`skipped_unmapped`）。
  bars 宇宙为静态快照 → 后续 IPO 不入面板（如实局限，与 P-1c 缓存同口径）。
- **字段**（冻结 schema，CSV utf-8 无 BOM，中文列名原样）：`date` + 12 值列
  `收盘价/涨跌幅/主力净流入-净额/主力净流入-净占比/超大单净流入-净额/超大单净流入-净占比/大单净流入-净额/大单净流入-净占比/中单净流入-净额/中单净流入-净占比/小单净流入-净额/小单净流入-净占比`；
  硬契约=`主力净流入-净额` 必在（缺→该股校验失败诚实计入，不落盘）；价格列只做溯源存储
  （复权口径不保证），**禁当行情数据消费**（行情唯一源=Money02 bars）。

## §2 守卫（S6 链 10 分钟轮询安全）

1. **完整性守卫**：15:30 前**丢弃当日行**（源盘中有实时半根行=盘中资金流在变动；update_futures
   completeness_filter 同构）；周末/节假日自然由滚动窗覆盖。
2. **新鲜度门（gate 子命令=S6 步）**：面板 `complete=true` 且 cutoff 未落后 20td → **零网络 no-op**
   （仅刷状态件 ts/last_attempt 保 panel reader 新鲜）；否则（首拉/未完成/过期）→ 检查刷新锁：
   锁活=「刷新在途」no-op；锁死=**分离启动后台刷新**（DETACHED+无窗口，日志 `logs/moneyflow_refresh.log`）。
   **30min 最小重试间隔**：`last_attempt` 先写镜像后动作（r18 坑律：中途崩也节流，防 spawn 风暴）。
3. **限速与保险丝**：2.5s/请求全局限速（EM push2 公民义务）；**双级熔断**（实现期精化，首弹实弹抓获）：
   - **连接级 3 连失败 → 判源阻断即停**（RemoteDisconnected/Timeout 族=IP 级阻断签名，r40/r46 同族；
     **不记 per-symbol attempts**——持续阻断下 gate 30min 重启×3 轮会把全宇宙错误 quarantine 成永久跳过
     =quarantine 风暴设计缺陷，实弹首跑当场暴露当场修）；每 30min 重试窗仅烧 3 请求，阻断解除自愈续拉；
   - **任意 5 连失败 → 保险丝熔断**（checkpoint 保留，exit 2，`complete=false`）；
   - **累计 3 轮失败 → 单股 quarantine**（只适用于股票级失败如校验失败/端点缺列；连接级失败永不累积）；
   - 下轮 gate 过 30min 节流窗自愈续拉。**实弹现状（交付时）**：bm-a push2his 首拉 3/3 连接级失败
     =源阻断中（R58 昨晨同端点可用=阻断按日波动），面板 parked 待 gate 自愈，诚实非缺陷。
4. **直连铁律**：proxy env 清空（Clash 劫持 EM 域，J13/r39/R34 坑律）；判定探针生死看 stdout 产物
   不看 tqdm/exit（r39）。
5. **诚实失败**：校验失败/源失败 → 不落盘该股、原样计数上报，绝不落假数据。
6. **断点续拉**：`data/moneyflow/_progress.json`（已抓集合）；每股原子写后即更 checkpoint
   （崩了最多重抓一股）；全宇宙跑尽 → `complete=true` 写面板汇总。

## §3 数据语义（消费方必读，写死于交付时）

- **只追加不重写**：overlap 行比对**主字段 `主力净流入-净额`（元，tol 1.0=分位稳定）**；
  mismatch（源改史）→ 该股本地不动、计 `overlap_mismatch`、整轮 exit 3（锚定门禁诚实律；
  消费批暴露漂移）。价格列不参与 overlap 比对（源可能改复权）。
- **滚动窗=可回填**：未建面板的日期只要还在源 120td 窗内即可补——**但窗口每天左移一格**，
  超过 120td 的历史只能靠本地面板保存（面板即档案）。
- **行数上限 130/股**（120+源侧松量）；日期严格单调无重复；行数/日期域/主字段非全 NaN 校验门。
- **信号滞后对齐例**：EM 资金流日线为盘后终值（当日行 T 收盘后才完整）→ 因子位用 **T+1**
  （P-A LHB 滞后 1 交易日同构；15:30 守卫已保证盘中半行不入面板）。

## §4 因子转化（另开工，认领制 MSG 先行，不在本件范围）

| 腿 | 内容 | 状态 |
|---|---|---|
| V1 采集器+面板 | scripts/update_moneyflow.py + data/moneyflow/per/（gate/refresh/status/selftest） | **本件交付** |
| MF-IC 参照批 | mf_main_net_5/10/20（R58 点名）+超大单/占比族；**须另开预注册**（PREREG_TEMPLATE：α 机制段+股票池 P-1c harness 主口径 h10+null 校正线+120d 源窗披露条款=禁与全史批同口径比较+SEED_REGISTRY 查占用）；素材=滚动窗首拉即得 ~120td 面板 | 未启动 |
| 合成入料 | 过门幸存者进 XSTOCK 型跨库合成货架（须全新预注册） | 未启动 |

## §4.1 面板局限条款（消费方必读）

- 宇宙=bars 静态快照 5222 只（后续 IPO 缺席）；停牌/退市股源停止出新行（面板保留其窗内史）；
- 首拉面板起点=源窗左沿（2026-04-02 级），**2026-04 前历史结构性不存在**（R58 北向/120d 窗定案）；
- 面板新鲜度=月度级（20td 门），**非日更**——日频「当日新行」只随每次全量重拉落地；
  实时性敏感消费场景须另立日更子集方案（如 LHB 事件股跟随，另开工）。

## §5 S6 链接线与运维口径

- 链位：`update_futures` 之后（`python scripts\update_moneyflow.py` 无参=gate；
  刷新动作在分离进程内跑，不占轮预算——轮内只做门判定+spawn，秒级）。
- exit 契约：gate 0=正常/no-op/已 spawn/在途；2=机制故障。refresh（分离进程）：0=全宇宙完成
  （complete=true）；2=保险丝/失败熔断（checkpoint 保留）；3=完成但有 overlap_mismatch（面板已更）。
- 状态件：`results/moneyflow_update_status.json`（ts/last_attempt/mode/no_op_reason/panel
  {cutoff, complete, n_symbols, n_rows, universe_n}/last_refresh{failures, mismatches, appended}）；
  data/ 面板 gitignored（可再生）。
- 判链活性：看状态件 ts + `logs/moneyflow_refresh.log` 尾部 + `data/moneyflow/_progress.json` 计数
  （勿信 done 旗读磁盘——margin 假绿坑律 r47）。

## §6 源面死亡证明与 v2 修复裁定（2026-09-25 R108 addendum）

- **V1 主源已死**：daykline 面（`fflow/daykline/get`）自 09-24 夜起接口级硬断 ≥25h——双域（push2his/push2）
  双路（代理/直连）仿冒头均 RemoteDisconnected 即断；同域 kline 面活=域活路径死。
  「阻断按日波动」前提**证伪为阻断按日轮换**（R58 晨=daykline 活×clist 死；R108 夜=完全倒转）。
  证据件=`research/digests/DIGEST-20260925-moneyflow-daykline-dead.md`（三探针表+坑律）。
- **v2 修复票=T-2026-09-25-39**（bm-a 数据车道）：主面换 `push2 clist/get` 排行横截面
  （60 请求/日全市场 5920→bars 宇宙 5222 join，12 值列全映射 f62/f184/f66/f69/f72/f75/f78/f81/f84/f87，
  schema 冻结面零改动）；**窗语义=纯前向日频**（横截面无回看）；daykline 路径保留为机会性回填副面
  （120td 回看=天然 gap 修复器，自愈机制零改动复用）；盘中 09:15-15:05 禁拉（快照≠终值）；
  日期=本地 ETF 日历最近完整 bar 日自戳。V1 的 §1「月度级重拉+20td 门」与 §4.1「月度新鲜度」
  口径在 v2 落地后由 T-39 同步修订为日频门；此前 gate 3 请求/30min 探测=诚实空烧已知态（非缺陷）。
- 面板存量（53/5222 股 daykline 史）不废：合法回填存量，v2 追加不重写。
## §7 v2 rank 面实现实况（2026-09-25 R109 addendum·T-39 执行中）

- **实现落地**：`scripts/update_moneyflow.py` v2 rank 面（push2 `clist/get` fid=f62 分页 pz=100）
  全量落地——12 值列全映射零 schema 漂移（f2→收盘价/f3→涨跌幅/f62/f184→主力净额占比/
  f66/f69→超大单/f72/f75→大单/f78/f81→中单/f84/f87→小单）；日期自戳=本地 ETF 日历最近完整 bar 日
  （15:30 约定）；同日幂等（date 已在面板→主字段 tol 1.0 比对跳过）；宇宙 join=rank 5920∩bars 5222
  （非 bars 诚实 skipped_not_in_universe）；gate cadence v2=cutoff 落后 1td 即触发（仅 rank 道；
  daykline 回填道保留 20td 旧门未动）；selftest 20/20（窗卫/映射/幂等/触发/分页/宇宙 join 六新节）。
- **窗卫实现口径**：票面 09:15-15:05 盘中禁拉之上，加封 15:05-15:30 戳一致性带——该带内快照值已是
  当日终值而 15:30 戳约定会把它们错戳到前一交易日（值/日错配=污染面板）。净效果=交易日 09:15-15:30
  禁拉；盘前/夜间/非交易日合法。封多不封少（保守侧安全）。
- **步速教训（实弹冻结）**：票面 0.5s 节流≈0.5min 是 digest 估算值，实弹在 0.5s 批量步速下页 3 起
  RemoteDisconnected 间歇丢连；已改公民步速 2.5s（daykline 道/akshare 同族先例）+页级重试 2 次
  （5s 退避）。60 页≈2.5min/全宇宙，仍符合 60 请求/日预算量级。
- **live-fire 现况（诚实）**：R109 当窗 01:09-01:15 三轮尝试全被端点级阻断——双路对照（直连/系统代理
  同死）+域对照组（同域 kline 面同死）证明=push2 域对本 IP 的间歇→硬化阻断（疑 00:47 R108 单探后
  批量探针触发限流加深，或 EM 阻断面按日/时轮换再现）。gate 30min 节流自愈在飞（01:15:18 已武装，
  ~01:45/02:15…自动重试；同日幂等使每次重试成本≈3 请求页 1 探针）。**票 T-39 未闭**——验收判据
  （≥5000 股全量一行/完整 bar 日）未达，待阻断解除后 gate 自动完成；S1/S4.1 日频措辞改写按票面
  授权顺延至 live-fire 通过后执行。
- **车道耦合披露**：rank 道在 stale+夜窗时 gate 早返回，daykline 回填道在该窗饥饿——但日间
  09:15-15:30 rank 窗卫期 legacy 道正常获得 tick，两道合计覆盖全日；daykline 面本身硬断≥25h 其
  spawn 仅为 3 请求探针，饥饿=省烧。若未来 daykline 面复活而 rank 道长阻，再评估车道回退调度。

## §8 替代源冗余审计收线（2026-09-25 R118 addendum·T-20260925-41 done 诚实负结果）

- **R108 双面冗余律量纲修正**：个股主力分解（超大+大单族分解+占比）截面的可达双面=**EM 族内跨端点**
  （push2 rank 主面 × push2his daykline 回填面），两 端点阻断按日轮换实证独立阻断窗（R58 晨 vs R108
  夜完全倒转）；**跨 provider 冗余对该量纲在免费 API 空间结构性不存在**——THS ggzjl 传输面 ALIVE
  （105 页×50≈全市场）但为全单聚合口径（流入/流出/净额/成交额，无主力分解无占比），映射表无物可映，
  聚合冒充主力=量纲造假禁行；EM `stock_main_fund_flow` 源码内省证伪=push2 同端点（docstring 网页壳
  datacenter≠API 背面）。证据三件=`research/digests/DIGEST-20260925-t41-alt-source-probe.md` +
  `results/shortline/t41_ths_probe_raw.json` + `t41_endpoint_map.json`（13 函数端点图）。
- **长阻期数据面风险接受**（GM 裁定 2026-09-25 03:50）：rank 道断供由 daykline 复活窗回填补片
  （120td 回看=gap 修复器），gate 30min 自愈 3 请求/窗维持，两道新鲜度门并存（rank 1td / 回填 20td）。
- **THS 聚合面登记为候选辅助面板**（新方向另开票另预注册：mf_ths_net 全单净额日频~105 请求/日，
  本 spec scope 外；金额列亿/万后缀须单位解析器）。T-41 收线=验收第二路径（诚实负结果+证据+升级件）。
