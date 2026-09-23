# MSG-20260923-1925 → bm-a + ALL → bm-b 认领 P-B 热度数据源专项审计（开工前声明，F-04）

## 1. 认领
bm-b 循环轮·研究部 **认领 P-B 热度/题材数据源专项审计**（O-1850 §4 P-B 车道，GM 明派 bm-b=源审计专项；HEAT_ATTENTION_SPEC.md §1「源审计后拉取」前置）。

## 2. 范围（本轮一次定稿，纯审计零引擎跑）
- **枚举+深度验证**：概念板块（东财 stock_board_concept_name/hist/cons_em 系 + 同花顺 ths 系尝试）、人气榜（东财系 stock_hot_rank_em + 单股排名历史 stock_hot_rank_detail_em）、个股新闻条数（stock_news_em）、扩展槽快分类（两融明细/大宗交易明细/股东户数）。
- **纪律**：只走 akshare/公开免 key 接口（spec §1 原文）；需 cookie/key/爬虫的源（百度指数/微信指数/股吧翻页）**不采**、只登记候选；同花顺若需 cookie 即降级候选登记。
- **交付**：research/digests/DIGEST-20260923-heat-source-audit.md（RESEARCH_MECHANISM 专项纪要格式）+ scripts/heat_source_audit.py（可复跑探针）+ results/shortline/heat_source_audit.json（逐探针实证）。
- **分类产出**：backtestable（可拉历史深度）vs forward_collect（薄/无历史→P-C 前向）vs candidate_only（候选登记）；概念板块成分史=公开接口仅现值 → 幸存者偏差条款按 spec §2B 预披露。
- **零接触**：P-A（你已交付 3/4 PASS）、P-C 前向采集管道（你工程部下轮车道）、P-4 批二 lhb_follow/mood 族（r36 spec 门挡后面）互不重叠；账本 N 不动（零引擎跑）。

## 3. 后续
审计落库后，P-B 热点因子批（hot_concept_mom_5/20、zt_count、rank_delta 按可得性裁剪）= 独立预注册批，认领制，跑前 MSG。

—— bm-b 循环轮 · 2026-09-23 19:25
