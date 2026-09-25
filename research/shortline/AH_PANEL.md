# AH_PANEL — AH 股溢价面板采集器 spec（T-2026-09-24-17 deliverable-2 主体）

> 车道：dept:数据，bm-a 独占（R31 判例族）；T-17 ARB-2 研究线（O-20260924-1155 GM 署名）。
> 本件=采集/存储/消费契约 spec；科学判据一律以预注册为准（P-B1 prereg 另立，禁本件改判据）。
> 证据链：faces 探针=`results/shortline/ah_face_probes.json`（cutoff 2026-09-24）；单对合成验证=
> `results/shortline/ah_synth_validate_02318.json`（slice-1，冻结公式）。

## §1 冻结口径（不可漂移）

- **溢价公式（slice-1 L7 冻结）**：`premium = close_A / (close_H × fx_HKD_CNY) − 1`；
  premium > 0 = A 股对 H 股溢价。
- **汇率基（rate-basis 披露律，probe fx_basis_preview 冻结「先冻结一个基再 join」）**：
  **BOC 官方中间价**（`currency_boc_sina('港币')` iloc4 列，per-100 港元计价 → /100 归一）。
  面板内 FX 缺日 **仅前向填充**（ffill：取 ≤ 面板日的最近官方中间价），首值前日期整行弃置；
  两项处理在 status 与面板文件头永久披露。
- **H 腿年窗铁律（R167 L1/L3c 实证）**：`stock_zh_ah_daily` 全窗调用截断于 2019-12-31——
  采集器**必须显式年窗** `start_year/end_year`（2015→当前年一发多窗，02318 实证 5351 行）。
- **窗口**：2015-01-01 → 今（研究视界；A 腿全史拉取后过滤 ≥2015）。
- **日历合并**：A∩H 共同交易日 inner join（两地节假日差异自然丢行，诚实 gap，禁编造）。

## §2 宇宙与 A↔H 映射（权威源=东财 AH 比价表）

- **映射权威面**：EM push2 clist `fs=b:DLMK0101`（f193 名称/f12 H 码/f191 A 码/f186 A 现价
  RMB/f188 溢价%/f189 比价）——唯一自带 A/H 双码的在册面。
- **访问配方**：直连 urllib + `ProxyHandler({})` + UA/Referer（moneyflow T4 冻结配方；
  registry proxy 会杀 akshare requests 面——stock_zh_ah_spot_em 包装死因实证）。
- **EM 域间歇性**：push2 同域 moneyflow 面今日 12:00-13:40 活/15:15 死实证——映射腿
  conn-fuse 3 连败=本次 run 映射不可得=诚实 exit 2（面板零动），gate 30min spawn 节流自愈重试。
- **腾讯普查面（辅助）**：`hk_rank.php` board=A_H（akshare stock_zh_ah_spot 同源，页级重试）；
  行第 14 字段=溢价率%——用作**逐对映射交叉验**：|合成 premium − 腾讯溢价% /100| ≤ 0.05
  过；**超标=映射疑误=该对隔离**（错映射=毒因子数据，宁可停对人工复核）。
- 宇宙漂移如实记（探针日 220 对 vs 采集日 200 对实证）；EM total 与腾讯 census 差集入 status。

## §3 采集契约（house 模式=update_moneyflow/THS 族）

- 逐对节流 2.5s；页/腿级重试 ×2（5s 退避）；conn-fuse 3 连败停发；**连续 5 腿败停整 run**
  （checkpoint 保全，gate 自愈续拉）。
- **累计 3 次失败对隔离**（quarantine，诚实保宇宙可完备）；交叉验超标同入隔离。
- checkpoint=`data/ah_panel/_progress.json`（run_target bar 日 + done 集 + attempts）；
  对完成=文件 cutoff ≥ 该对本次拉取 max 共同日。
- **增量腿**：A 腿=stock_zh_a_daily（sina 全史一发）；H 腿=年窗一发；
  已有本地文件者 **overlap 边界校验**（重算重叠日 premium，tol 1e-6）——失配对本地不动
  计 mismatch（整 run 完成但有失配=exit 3，futures/moneyflow 语义）。
- 粗错护栏：|premium| > 5.0 = 腿失败计数（非隔离）；FX 值域 0.7-1.0 CNY/HKD 漂移旗如实记。
- gate 判鲜（纯函数）：`target_bar = 今 A 历 bar 日（≥16:30 时）/前一 A 交易日（<16:30）`
  （H 腿 16:00 收盘+源滞后，防 15:30-16:00 空转窗）；`cutoff < target_bar 或 not complete`
  → 分离后台刷新（锁 + 30min spawn 节流）；IO 型非 CPU 批，不入 runnable_pool。
- 车道护栏：仅 bm-a 动作（R31）；他机 stdout-only 诚实 no-op 零落盘（R65 律）。

## §4 存储与状态（machine-local data/ah_panel/ gitignored）

- `data/ah_panel/per/{H码}.csv`：`date,close_A,close_H,fx_HKD_CNY,premium`（append-only+边界校验）。
- `data/ah_panel/_universe_em.json` / `_universe_tx.json`：映射冻结件+普查件（fetched_at 戳）。
- `data/ah_panel/fx_series.csv`、`hsahp_index.csv`（HSAHP=恒生 AH 溢价指数，
  sina 面仅近窗 ~55 行**短史诚实披露**；深史=逐对构建归 B 相）。
- `data/ah_panel/ah_premium_panel.parquet`：finalize 长表面板
  （date,h_code,a_code,close_A,close_H,fx_HKD_CNY,premium）。
- `results/ah_panel_status.json`（tracked）：cutoff/complete/universe/mapped/fresh/
  quarantined/cross_check/mismatch/last_refresh_exit/**evidence_cutoff**（=A 历最新 bar 日，
  science_gates C2 合法键）。
- exit codes：gate 0=ok/no-op/spawned/在途、2=机制故障；refresh 0=完备、2=未完备
  （fuse/映射不可得/checkpoint 保全）、3=完备但有 overlap 失配。

## §5 健康线（A 相持续上岗）

- 逐对行数漂移监测（status 记 per-pair rows）；census 差集日报；FX/溢价粗错旗；
  列名恒等校验败（A 腿缺 `close` 列 / H 腿列数 ≠ 6 / FX 列数 ≠ 6）=源形状漂移 → blocked
  待人工裁定（gate 诚实上报，无自愈）。

## §6 消费面（P-B1 前置，本件不建判据）

- P-B1 prereg（AH 溢价水平/变化作为 A 股 ETF 域因子，跨市场信息传导假设）从
  `research/PREREG_TEMPLATE.md` 起草，判据调 science_gates 共享库；面板=唯一原料面。
