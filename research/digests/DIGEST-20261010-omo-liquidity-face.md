# DIGEST-20261010-omo-liquidity-face — 央行 OMO 流动性指标面可达性扫描（E4 P3 队头·调研件）

> 车道：数据部·外源扫描（state/queue/explore.md E4 队头·Self-Drive v2.0·48h 节律）。
> 执行：bm-a r948（2026-10-10 09:0x-09:3x）。
> 纪律：R58/hsgt 探针血统（直连铁律·proxy 剥除·≥3s 礼貌间隔·45s 超时夹克·逐面诚实错误捕获）；零网络源码内省先行（akshare 1.18.96 无 macro_china_gksccz——0.6.x 后已删·__init__ 变更日志实证）；宣称≠验证。
> 探针请求账：EM datacenter ×3（reportName 候选逐个）+chinamoney FrrHis ×2（2015/2020 全年窗）+wrapper 短窗 ×1+jin10 shibor ×1+sina 央行资产负债 ×1=8 请求（6 接口·均 ≤3/接口）。
> 实证载体：scripts/omo_liquidity_probe.py（selftest 7/7）+results/shortline/omo_liquidity_probe.json。
> 零引擎零账本零判据零 prereg（reachability+描述面·任何策略面主张须另过预注册正门+T-67 §2 前向 12 个月冻结律）。

## 一、结论速览（候选评级表）

| 候选面 | 接口 | 判定 | 证据 | 流动性指标面候选评级 |
|---|---|---|---|---|
| OMO 日度净投放操作流（逆回购投放/到期/净投放） | EM datacenter reportName 候选族 | **未达（reportName 未知）** | RPT_ECONOMY_GKSCCZ / RPT_ECONOMY_OPEN_MARKET / RPT_ECONOMY_OMO 三候选均 EM code=9501「没有配置该参数」；akshare 0.6.10 曾有 macro_china_gksccz·现版已删（gksccz.html 页面在但数据经 JS 运行时加载·静态 HTML 零端点残留 82,310B 实证） | **数据债登记**（主候选面阻塞：需浏览器 dev-tools 抓真实 reportName 或 PBOC 官网公告页直连工程·超出 reachability 扫描面） |
| 银行间回购定盘利率 FDR001/007/014（日度·市场响应面） | chinamoney FrrHis（wrapper+直连双验） | **存活** | wrapper 30d 窗 17 行新鲜至 2026-10-09（FDR001 1.31%）；直连 2020 全年窗 249 行 FDR001 全活；2015 全年窗 249 记录但 FDR001 全为 '---' 占位（FR001 加权族在·定盘族 2015 年未起） | **可建面**（日度响应面·深度 ≥2020 实证·确界起点=数据债；**宽窗陷阱**：2020→today 一次性宽窗返回零记录→wrapper KeyError 'frValueMap'——span 上限·须分年分块拉取） |
| Shibor O/N..1Y 全期限梯（日度） | macro_china_shibor_all（jin10 CDN） | **存活** | 2,380 行 2015-05-08→2026-10-09·O/N+1W/2W/1M/3M/6M/9M/1Y 利率+涨跌 BP 列全在 | **可建面**（日度响应面·11.5 年深史） |
| 货币当局资产负债（月度·政策面） | macro_china_central_bank_balance（sina） | **存活** | 356 行 1993.3→2026.8·含「对其他存款性公司债权」列（OMO+MLF+PSL 持仓存量·月频政策面） | **可建面**（月度政策面·33 年深史；日度 OMO 净投放的月频代理） |
| rate_interbank（EM shibor 页 wrapper） | akshare 1.18.96 | **wrapper 破** | market_map KeyError（上游页面名漂移）；替代面 C（jin10）已覆盖 | 弃用（被 C 面替代） |

## 二、本地消费面联动（描述性·零阈值）

1. **GC001 交易所回购面板**（data/repo_daily/GC001.csv·3,742 行 2011-05-13→2026-10-09）：
   - 月末脉冲复证：dom≥26 均值 3.467% vs 月中 dom10-20 均值 2.397%（**+1.07pp 月末效应**·与 repo_pulse_probe r806 月末脉冲率 17.6%/lift 5.4x 同向互证）。
   - 名场面锚校验：Top 尖峰 2015-02-10 53.44%（春节前钱荒）+2014-08-28 45.175%——与 REPO_PANEL spec 冻结注记逐字一致=本地面板对已知历史锚自洽。
2. **FDR001（银行间定盘）↔ GC001（交易所收盘）逐日联接**（确定性·零网络）：
   - 2020 全年：243 共同交易日·corr 0.2826·GC001 均值 2.278% vs FDR001 均值 1.599%·**价差均值 +67.9bp（交易所溢价）·p95 +200bp**——交易所 vs 银行间市场分割面（月末交易所更尖）。
   - 近 30 日（2026-09-10→10-09）：16 共同日·corr 0.03（双低波动态）·价差均值 **-6.5bp**（当前宽流动性态下交易所利率贴着银行间定盘下缘）·p95 +10.7bp——价差状态面随流动性态翻转（2020 紧 vs 2026 松）·描述面即有信息量。

## 三、消费纪律与数据债登记

1. **E4 队列项收口判读**：OMO 日度净投放操作流（主候选）=**数据源未达**（EM reportName 未知·三候选诚实排除）；但流动性指标复合面=**月频政策面（央行资产负债 33 年）+日频市场响应面（FDR001 定盘 6.5 年实证深+Shibor 11.5 年）双柱可建**——REPO_PANEL 消费联动已量化（月末脉冲+市场分割价差状态面）。
2. **数据债登记**：①EM 真实 OMO reportName（浏览器 dev-tools 抓包·后续窗）；②FDR001 定盘确界起点（2015 窗全 '---'·分块二分可定）；③rate_interbank wrapper 上游名漂移（akshare 跟进债·已被 jin10 面替代不阻塞）。
3. **工程面（不自动开工）**：FDR001/Shibor 日度采集 gate 属 S6 采集器家族新车道——若立项须按 data-gate-wiring 范式接 update_* 家族契约（15:30 门/overlap 校验/车道归属/conn-fuse）·另走工程票；本件纯调研零面板写零采集落地。
4. **策略面禁开**：任何「OMO/流动性→回购利率择时」类主张须另过预注册正门（PREREG_TEMPLATE+science_gates 共享判据+出场轴显式门）+T-67 §2 前向 12 个月冻结律——本件描述面数字（+1.07pp 月末效应/+67.9bp 2020 价差/-6.5bp 当前价差）不构成判据宣称。
