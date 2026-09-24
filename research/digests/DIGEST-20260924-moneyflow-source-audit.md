# DIGEST-20260924-moneyflow-source-audit — 资金流数据源专项审计纪要

> 车道：SHORTLINE_PLAYBOOK P-3 域（资金流源修复，**O-1620 GM 已署名**）+ O-20260923-1636 外调队下一名。
> 执行：bm-a 循环轮·研究+数据 round 58（2026-09-24 08:30-08:50），认领=MSG-20260924-0830（commit 1d3d8cc）。
> 纪律：只走 akshare/公开免 key 接口（HEAT_ATTENTION_SPEC §1 源审计纪律同源）；cookie/key 源只登记候选。
> 实证载体：scripts/moneyflow_source_probe.py（selftest 15/15 + run 8 探针 + probe2 定向 4 探针，3s 节流+直连 ProxyHandler({})）+ results/shortline/moneyflow_source_probe.json + moneyflow_source_probe2.json（全部原始输出）。零引擎跑，账本 N=3041 不动。

## 一、结论速览

| 源 | 接口（域） | 判定 | 深度实证 | 相关性评级 |
|---|---|---|---|---|
| 个股主力资金流历史 | `stock_individual_fund_flow`（push2his fflow/daykline） | **forward_collect + 短窗回测类** | **源端硬顶 ~120 交易日**（akshare 已传 lmt=0 全史请求、源仍只回 120 行：2026-04-02→2026-09-23；3/3 代表股 000001/600519/300750 一致） | **B+**（h5/h10/h20 因子窗在 120d 内可算；2015-2026 长回测**不可得**） |
| 大盘资金流历史 | `stock_market_fund_flow`（push2his） | 同上 | 同 120 行顶（2026-04-02→09-23） | C（市场级聚合，因子增量低） |
| 板块资金流历史 | `stock_sector_fund_flow_hist`（push2his+**clist 码表腿**） | **blocked-at-wrapper**（可绕） | RemoteDisconnected ×2 持续=崩在板块名→BK 码表的 **push2 clist 腿**（已知 IP 阻断域，r40/bm-b 判例）；push2his fflow daykline 本体健康（A/C 探针同域同刻通过） | C（绕法=硬编码 BK 码表直打 push2his，P-B pb_heat_pull 同族） |
| 北向聚合序列 | `stock_hsgt_hist_em`（datacenter-web） | **历史素材可用·前向死源** | 2759 行自 2014-11-17；**2024-08 停披露后行壳延续但资金流字段全 NaN**（当日净买额/买入/卖出/历史累计/流入/余额=NaN、持股市值 0.0，尾部 5 行实证 2026-09-17→09-23），装饰列（领涨股/沪深300）照填 | C（2014-11→2024-08 真值段可做历史研究；在产因子**不可用**） |
| 北向个股明细 | `stock_hsgt_individual_detail_em`（datacenter-web） | **死源+截断史** | **机构级明细**（机构名称列，600519 ≈92 行/日）；**数据止于 2024-09-30**（停披露实证，playbook「2024-08 停实时披露」前提的精确补充）；akshare 12 页截断（6043 行只回到 2024-05-16） | D（前向零值+历史被截=双残） |
| 北向持股排行快照 | `stock_hsgt_hold_stock_em`（datacenter-web） | **wrapper 崩** | akshare 1.18.96 双 indicator（今日/5日排行）均 NoneType 解析崩=stock_news_em 封装崩同族（r40 坑③）；源状态未知 | D（快照类+封装死=双低优） |

## 二、机制定案（对本司因子路线的含义）

1. **主力资金流=「前向采集+短窗」双轨源类**（与 P-C 热度 L1 同类、窗更短）：源端 120d 硬顶意味着(a) 2015-2026 长回测**结构性不可得**——禁伪造长史；(b) 因子窗 h5/h10/h20 在源窗内可算=**从今日起前向日频采集积累**是唯一在产路径，~120d 后自然形成可回测段（2026-04 起已有 120d 沉淀可直接先做近窗 IC 参照批）；(c) 批跑设计若做，披露条款=「回测窗≤源窗 120d·IS/OOS 切分在该窗内重定义」——**禁与全史批同口径比较**。
2. **北向线正式出具死亡证明**（精确证据固定）：聚合序列 NaN 壳+个股明细 2024-09-30 停更+排行封装崩三证合一。playbook「替代口径」期望在 EM 免 key 域内**不存在**；HKEX 官方 CCASS 披露=境外源（cookie/key/爬虫类）→ 按 §1 纪律**只登记候选不采**。北向素材的残余价值=2014-11→2024-08 真值段历史研究（如政体对照），在产因子域除名。
3. **域纪律再证**：push2his fflow daykline 当场健康（3 探针 3s 节流零阻断）而 clist 腿持续死=EM 阻断**按子域×按接口路径**分化（r40 拆分判例的细化：同域不同路径可生死并存）；拉取管线设计**禁依赖 clist 码表腿**，码表一次性取得后本地硬编码+直打 push2his。

## 三、坑与纪律（新增入册）

- **源端深度顶≠封装深度顶**：lmt=0 全史请求被源端静默截到 120 行——「接口在」不等于「历史在」，深度必须探针实证（与 LHB seat pull「done 旗不信」同族：**永不信任请求参数承诺，直读响应行数**）。
- **行壳数据**（NaN shell）：序列 rows/首末看着健康，值列全 NaN——深度探针必须**抽样值列**，不能只数行数看日期（本审计 F1 定向探针抓出；若只看 A.depth 会误判北向可用）。
- **日期序陷阱**：datacenter 明细接口返回按多键排序（机构×日期），iloc[0]/iloc[-1] 的「首末」非日期 min/max——跨度判定必须对日期列做 min/max（F2 修正）。
- akshare 分页截断（12 页）在 datacenter 明细族普遍存在，长史回填须自写分页续拉（pb_heat_pull 同族先例）。

## 四、候选登记（择机另开预注册，本轮零采纳）

| 候选 | 说明 | 前置 |
|---|---|---|
| `mf_main_net_5/10/20` 主力净流入因子族（个股） | 前向采集管线（data/moneyflow/ 日快照，update_heat 同构）+120d 窗内近窗 IC 参照批 | P1 采集器骨架≈update_heat 改造；批设计须带「源窗披露条款」 |
| 板块资金流因子 | BK 码表硬编码绕法后就绪 | 与 P-B 热度板块族信息重合度先检（D6 门槛） |
| HKEX CCASS 持股披露（境外替代口径） | cookie/key/爬虫类 | **不采**，仅登记（§1 纪律） |

## 五、产物清单

- `scripts/moneyflow_source_probe.py`（selftest 15/15·run·probe2 三模式，可复跑）
- `results/shortline/moneyflow_source_probe.json`（8 探针原始输出+域图）+ `moneyflow_source_probe2.json`（定向 4 探针+北向尾部 8 行实证）
- `research/STRATEGY_LIBRARY.md` §四 资金流族行（登记处）
- 零引擎跑：引擎账本 N=3041 不动、因子账本 5394 不动、零注册零门槛变更

## 六、评级与下一步

- 相关性评级：**B+（个股主力资金流·前向采集类）/ C（板块+大盘）/ D（北向三件）**。
- 下一步（择机、各自另开预注册/认领）：①主力资金流前向采集器骨架（update_heat 同构，P1 门票级小件）；②120d 窗内近窗 IC 参照批（须先有采集器或直接用 120d 沉淀一次性拉取）。北向线收档为历史素材。
