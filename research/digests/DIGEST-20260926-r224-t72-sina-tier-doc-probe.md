# DIGEST-20260926-r224-t72-sina-tier-doc-probe — 档位语义官方面扫描（open item ④ 关联腿）

> 认领线：bm-a 数据部·T-2026-09-26-72 in-flight 维护轮附产（O-1721 外源常态线）。
> 触发：SINA_MF_PREREG §5 open item「档位阈值官方文档（sina 页面 JS/帮助面）→ 外源扫描
> 常态线下批收口；收口前消费面档位语义=UNDOCUMENTED 诚实标注」——首拉在飞窗的本轮批腿。
> 预算纪律：五探针共 18 请求后收线（R109 节制律；每探针头注预注册决策矩阵）。

## §〇 结论先行（一句话）

**PARTIAL-LABELS**：sina 自家前端把 r0 档标为「主力净流入(元)」、r3 档标为「散户净流入(元)」
（utils-hq.js 官方 JS 铁证）——sina 四档叙事=**投资主体类**非 EM 式**单笔单量类**；
r1/r2 档名与档位阈值在已探面仍 UNDOCUMENTED（open item 维持开、诚实标注收窄）。

## §一 证据链（全部 sina 自有域名面=最高证据等级）

| # | 面 | 读数 |
|---|---|---|
| r1 | `finance.sina.com.cn/realstock/company/sh600519/nc.shtml`（个股行情页 157KB） | 页面本体零四档关键词；56 个 script src 收集 |
| r2 | src 粗筛族 4 件（hq.sinajs/swfobject/jquery/FinanceAppTextPic） | 全零命中（预算损耗诚实记） |
| r3 | `n.sinaimg.cn/finance/hq2018/utils-hq.js`（行情页官方工具 JS 57KB） | **命中 r0_net**：`r0_in: title:"主力净流入(元)"`、`r3_in: title:"散户净流入(元)"`、`r0_net_3/5: 3日/5日净流入` |
| r4 | `n.sinaimg.cn/finance/hq2018/js/stock20180116.js`（行情页主 JS 156KB） | MoneyFlow 家族调用点：**饼图=主力买入/主力卖出/散户买入/散户卖出**（走 `MoneyFlow.ssi_ssfx_flzjtj` 另一 API）；`ssl_bkzj_ssggzj` 净额面 dTitle=净流入(万元) |
| r5 | 消费页定位腿：`xh1.php` view 404；realstock 兄弟页 zjlx/cjfb/lscjfb/hiszjlx 全 404；Bing/Baidu 精确串 SERP 噪音/空；akshare 零 sina moneyflow wrapper（R215 已扫） | lscjfb 表格消费页未定位 |

## §二 语义发现（量纲纪律增量）

1. **r0/r3 官方档名到手**：utils-hq.js 的 `r0_in`/`r3_in` 与 lscjfb 的 `r0_net`/`r3_net` 同名族
   （r0..r3 四档族跨 sina moneyflow 面共用命名）——**r0=主力档、r3=散户档**为 sina 官方面证据，
   非 folklore。同名族识别=合理归纳（命名同族），但「utils-hq.js 的 r0_in 必与 lscjfb r0_net
   同档定义」未经 API 级证实——消费面沿用按 PARTIAL 口径，禁升格为 DOCUMENTED。
2. **R118 禁映射律获直接证据升级**：sina 的「主力」（r0，投资主体类）与 EM 的「主力」
   （=超大单+大单聚合，单量类）是**同名不同构**——两平台互映射在标签层即伪、不止阈值层。
   原 folklore 假设「sina 四档=EM 式超大/大/中/小单」被 sina 自家前端叙事**反证**
   （官方叙事=主力↔散户两极+中间两档）。
3. **r1/r2=中间档**（档名未文档化；folklore 候选=大单/中单或大户/中户——**均无证据、不采**）；
   档位数值阈值（万元级定义）已探面零文档。

## §三 判定与后续

- **open item ④ 状态：ADVANCED-PARTIAL**——档位语义诚实标注从「全 UNDOCUMENTED」收窄为
  「r0=主力/r3=散户（官方面）+r1/r2/阈值 UNDOCUMENTED」；**open item 维持开**
  （阈值面未文档化），后续外源常态线续批：候选面=sina 帮助页/移动端 wap 面/历史 blog 面
  （精确串 SERP 已证无效，禁再烧；换面不换串）。
- **消费面纪律**（T-72 s3 接线前适用）：消费面 r0/r3 可按「主力/散户（sina 官方叙事·投资主体类）」
  命名呈现，须带「与 EM 主力=单量聚合不同构」注记；r1/r2 呈现=原始列名 r1/r2 诚实禁猜档名；
  任何跨 EM/THS 合成面=继续 R118 禁行。
- **对本轮首拉零影响**：纯只读探针，判据/schema/护栏零触碰（冻结律完好）。

## §四 证据件

- `results/_r224_bma_sina_tier_doc_probe.py/.json`（探针-1：页面/JS 梯 6 请求）
- `results/_r224_bma_sina_tier_title_map.py/.json`（精修-2：utils-hq.js r0/r3 title 抽取）
- `results/_r224_bma_lscjfb_consumer_probe.py/.json`（精修-2b：消费页定位 5 请求+候选清单）
- `results/_r224_bma_stockjs_tier_full.py/.json`（精修-3：stock20180116.js 全抽取=饼图叙事）
- `results/_r224_bma_zhulijs_tier_map.py/.json`（精修-4：hqZhuli 小件死胡同诚实记录）
- `results/_r224_bma_sibling_pages_scan.py/.json`（精修-5：兄弟页 404 族）
- 前件：DIGEST-20260926-r215-t71-sina-mf-probe.md + DIGEST-20260926-r216-t71-sina-mf-freshness.md
