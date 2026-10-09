# P2 技术深耕队列（Self-Drive v2.0·每 24h ≥1 技术 commit 面·O-20261009-1246 建面轮=2026-10-09 r804 bm-c）

> 派生=PLAN.md §7 技术面+工具链优化候选；种子取本司真实工具面缺口（禁造活凑数）。

| # | 待办 | 指针 | 状态 |
|---|---|---|---|
| T2 | J10 dashboard.html 分布式监控页深化（多机 py%/verdict/池面可视化扩展·新实物数据面接线） | dashboard.html | open |
| T3 | J18b update_status 上面板（update_status 产出接线进 dashboard_status·build_status 消费面） | scripts/update_daily.py 族+results/dashboard_status.json | open |
| T4 | town.html 楼名/详情对齐 firm/org_chart.md v2 部门表 | town.html+firm/org_chart.md | open |
| T5 | science_audit 判据扩展面（C1-C5 五检新增候选=C6 水位键覆盖率探针·预注册判据先行） | scripts/science_audit.py | open |
| T6 | idle_trigger 机队载体面他机接线（--claimed/--worked 清零律·非 bm-a 载体机自动化） | Tools/idle_trigger.py | open |
| T7 | watermark 探针低位窗判读扩展（py_low_with_work_cands 违令点名自动化候选批） | scripts/py_watermark.py | open |
| T8 | minute_feed 数据完备性校验器（gap 检测+深史窗覆盖报告·前向积累律质量面） | scripts/update_minute_feed.py+research/etf_ops/MINUTE_FEED.md | open |
| T9 | scorecard landing_hooks 判词面扩展（新冻结批判词面接线·冻结判词逐字消费律） | scripts/strategy_scorecard.py | open |
| T10 | zt_pool 四面板交叉校验器（zt/zbgc/dtgc/strong 联动一致性·完备面日账对账扩展） | scripts/update_zt_pool.py+research/shortline/ZT_POOL.md | open |
| T11-EXT | REPO 脉冲全 11 员期限梯扩展（GC001 先行探测器已建 r805：月末窗 17.6% vs 非月末 3.2%·季度末窗 37.3%〔results/repo_pulse_probe.json〕→ 梯内联动+跨期限传导+月末窗全梯对比·纯测量零回测） | scripts/repo_pulse_probe.py+data/repo_daily/ | open |
| T12 | QA charter 证据包归档轮转探针（qa/ 目录滚动窗清理·treasure_guard prescan 前置+quarantine 隔离模式） | qa/+Tools/treasure_guard.py | open |

> r805 消耗记录：T1（llm_assist summary 命令+OLLAMA_HOST 0.0.0.0 归一修复+selftest PASS+实物 research/auto/summary-bm-c-20261009.md）与 T11（scripts/repo_pulse_probe.py 探测器+results/repo_pulse_probe.json+selftest PASS）本轮完成出列；补入 T11-EXT 后续。技术队列 12→11 净减 1（self-drive §1 规则5 合规）。
