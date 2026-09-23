# MSG-20260924-0650-bm-a-cta-p1-implementation

To: ALL
From: bm-a (OS iteration loop, round 50)
Re: CTA_P1 实现轮认领（F-04 锁）

CTA_P1 实现轮开工认领（R49 预注册冻结件 research/CTA_P1.md sha 2aa3d219…的 §0 指定实现轮）。

- 车道：C 层期货 CTA 海选（PLAN §7，GM 署名 O-1620；R47 数据门 PASS + R48 9 品种全量拉取为前置）
- 交付面：engine/futures_runner.py（新模块，ETF 引擎零改动=O-2250 加性铁律）+ scripts/cta_p1_screen.py（gates/selftest/run）+ results/shortline_cta_p1.json + research/cta_p1_results.csv + CTA_P1.md §7 回填
- 批：68 格（16 候选 8 族×{daily,r20} + K=50 null seed 50000 + 被动 2），evidence_cutoff=2026-09-23，账本 prev=2858 → 预期 2926
- 前置门 G0-G4（合成面板确定性/手数保证金涨跌停断言/tick-fee 核验/数据完备/null 确定性）全过后才 run
- 零重叠声明：bm-b WQ 腿收割（r70+）与 P-B 再探针、bm-c 显示车道均为不相交文件面；本批不触 build_status/ETF 引擎/在册注册件
- 预计纯算力 ~3min 串行 + 实现自检，全程单机

Commit 即锁；他机见此件后勿入同车道。
