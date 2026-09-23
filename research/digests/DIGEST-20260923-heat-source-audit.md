# DIGEST-20260923-heat-source-audit — P-B 热度/题材数据源专项审计纪要

> 车道：O-20260923-1850 §4 P-B（GM 明派 bm-b），HEAT_ATTENTION_SPEC.md §1 前置件。
> 执行：bm-b 循环轮·研究部 round 39（2026-09-23 19:25-19:45），认领=MSG-20260923-1925。
> 纪律：只走 akshare/公开免 key 接口（spec §1 原文）；cookie/key/爬虫源只登记候选。
> 实证载体：scripts/heat_source_audit.py（14 探针，逐探针子进程+硬超时，可复跑）+ results/shortline/heat_source_audit.json（全部原始探针输出）。零引擎跑，账本 N 不动。

## 一、结论速览（分类表=审计 JSON classification 字段，全数据驱动）

| 源 | 家族 | 判定 | 深度实证 | 相关性评级 |
|---|---|---|---|---|
| THS 概念板块列表+指数日线（stock_board_concept_name_ths / index_ths） | P-B | **backtestable** | 375 板块；新板样本 661 bars 自 2024-01-02；老板块**物联网 3088 bars 自 2011-01-04**（深度=板块创立日截断） | **A**（ETF/股票日线域即用，P-B 批首选分类法） |
| EM 概念板块成分（stock_board_concept_cons_em / raw clist fs=b:BKxxxx） | P-B | forward_collect + 幸存者偏差条款 | 现值快照 68 成分（单发实证）；**无公开成分变更史接口** | B（spec §2B 披露条款强制） |
| EM 概念板块指数日线（push2his kline secid=90.BKxxxx） | P-B | unverified（被限流） | 限流未获深度（见 §三坑 2）；THS 已满足深度需求 | B（备选分类法，拉取管线就绪后复验） |
| EM 人气榜（stock_hot_rank_em + 单股排名历史 detail_em） | P-C(前向) | forward_collect | run-1 实证：单股排名历史 366 bars 自 2025-09-23（≈1 年窗）；终轮限流未复现 → **窗口深度待管线首拉定稿** | B（1 年窗可做近窗验证，主体仍前向） |
| EM 个股新闻（search-api-web jsonp，raw 直连） | P-C(前向) | forward_collect | 000001 页1 100 条，最早 2026-06-24（≈3 个月喂给窗） | C（薄史，双轨采集+paper 前向） |
| akshare stock_news_em 封装 | P-C | **broken_on_this_stack** | pandas 3.0.6/Arrow 解析崩（ArrowInvalid regex）→ 用 raw jsonp 直连替代（已验通） | C |
| 两融明细（stock_margin_detail_sse） | 扩展槽 | **backtestable** | 2010-03-31 探针 25 行>0 → 全史 2010-03 起 | B |
| 大宗交易明细（stock_dzjy_mrmx） | 扩展槽 | **backtestable** | 2013-01-04 探针 1 行>0 → ≥2013 | B |
| 股东户数（stock_zh_a_gdhs 按季） | 扩展槽 | **backtestable** | 2015-09-30 探针 2454 行>0 → ≥2015Q3 | B |
| 股吧翻页/百度指数/微信指数 | 候选 | candidate_only | 纪律不采，仅登记 | D |

## 二、对 P-B 热点因子批的直接推论

1. **分类法裁定：THS 概念板块为主分类法**。`hot_concept_mom_5/20` 可直接用 THS 板块指数日线（15 年深度覆盖 IS/OOS 全段）；EM 板块指数作备选（限流解除后复验再定）。
2. **成分归属约束**：THS 成分史同样仅现值可拉（与 EM 同病，幸存者偏差条款对 THS 同样适用）→ P-B 批若做 `hot_concept_zt_count`（所属概念当日涨停家数）须按 spec §2B 写死「现值成分回填历史」的偏差声明，或把因子降级为纯板块指数层（不逐股归属）。
3. **两融/大宗/股东户数三扩展槽全过 2010-2015 深度门** → 可作独立预注册批素材（先审 IC，非本轮决定）。
4. P-C（股吧/新闻/人气榜）维持 spec §2C/D/E 前向轨道不变：bm-a 工程部采集管道车道（data/heat/），本审计不越界。

## 三、坑（全部实证，写入 JSON）

1. **Clash 代理劫持 EM 行情域**：akshare 经代理打 push2/clist 恒 RemoteDisconnected（~22s 挂死后断）；**raw 直连（ProxyHandler({})）首发即通**（68 成分实证）——与 J13「回环被劫持」同族，EM 行情域新增一例；凡打 push2*/emappdata 必须直连 opener。
2. **EM push2/emappdata 突发限流**：同 IP 短时多轮探针后**瞬时 RemoteDisconnected（<200ms）**，跨 90s 冷却+4s 间隔重试仍封——P-B 拉取管线必须带限速（≥3-5s/请求）+指数退避+可断点续拉；本审计 EM 板块指数深度未验证如实留白，THS 替代已够。
3. **akshare × pandas 3.0.6 兼容破损**：stock_news_em 在 Arrow 解析层崩（ArrowInvalid: invalid escape sequence）——源不死、封装死；raw jsonp 直连 1 次调用拿到同等数据（100 条/页）。
4. **THS 板块名≠直觉名**：'半导体' 不在 THS 名录（名录含 '第三代半导体'/'芯片概念'）——按码表精确名调用，勿猜。
5. tqdm 进度条走 stderr 且 exit code 1 假阴性（本审计 2>$null 仍 exit 1 但 JSON 正常）——判探针生死看 stdout 产物不看退出码。

## 四、建议动作（后续轮，认领制）

1. **P-B 热点因子批预注册**（研究部，认领 MSG 先行）：素材=THS 板块指数日线全量拉取（375 板块×~4000 bars 估 ~150 万行）+ 现值成分映射（偏差条款写死）；因子=hot_concept_mom_5/20 + 板块级 zt_count（用 bars+P-4②a zt 快照推板块涨停家数，免逐股成分依赖）；走 P-1c harness 或独立批，V1/V2/V3 + K=50 null + N 记账原文适用。
2. **拉取管线工程约束**：THS 拉取 39 页码表 tqdm 每次重拉（~2s）+ 板块指数逐板块限速 ≥1-2s → 全量首拉估 375×2s≈12.5min 级，落 Money02/data/cache/ 同范式 gitignored 缓存。
3. 两融/大宗/股东户数三槽入 BACKTEST_PLAN 待办池候选（批前另开预注册）。

—— bm-b 循环轮·研究部 · 2026-09-23 19:45 · 实证=results/shortline/heat_source_audit.json
