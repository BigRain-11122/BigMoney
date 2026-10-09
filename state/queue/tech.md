# P2 技术深耕队列（Self-Drive v2.0·每 24h ≥1 技术 commit 面·O-20261009-1246 建面轮=2026-10-09 r804 bm-c）

> 派生=PLAN.md §7 技术面+工具链优化候选；种子取本司真实工具面缺口（禁造活凑数）。

| # | 待办 | 指针 | 状态 |
|---|---|---|---|
| T4 | town.html 楼名/详情对齐 firm/org_chart.md v2 部门表 | town.html+firm/org_chart.md | open |
| T5 | science_audit 判据扩展面（C1-C5 五检新增候选=C6 水位键覆盖率探针·预注册判据先行） | scripts/science_audit.py | open |
| T6 | idle_trigger 机队载体面他机接线（--claimed/--worked 清零律·非 bm-a 载体机自动化） | Tools/idle_trigger.py | open |
| T7 | watermark 探针低位窗判读扩展（py_low_with_work_cands 违令点名自动化候选批） | scripts/py_watermark.py | open |
| T8 | minute_feed 数据完备性校验器（gap 检测+深史窗覆盖报告·前向积累律质量面） | scripts/update_minute_feed.py+research/etf_ops/MINUTE_FEED.md | open |
| T9 | scorecard landing_hooks 判词面扩展（新冻结批判词面接线·冻结判词逐字消费律） | scripts/strategy_scorecard.py | open |
| T10 | zt_pool 四面板交叉校验器（zt/zbgc/dtgc/strong 联动一致性·完备面日账对账扩展） | scripts/update_zt_pool.py+research/shortline/ZT_POOL.md | open |
| T12 | QA charter 证据包归档轮转探针（qa/ 目录滚动窗清理·treasure_guard prescan 前置+quarantine 隔离模式） | qa/+Tools/treasure_guard.py | open |

> r805 消耗记录：T1（llm_assist summary 命令+OLLAMA_HOST 0.0.0.0 归一修复+selftest PASS+实物 research/auto/summary-bm-c-20261009.md）与 T11（scripts/repo_pulse_probe.py 探测器+results/repo_pulse_probe.json+selftest PASS）本轮完成出列；补入 T11-EXT 后续。技术队列 12→11 净减 1（self-drive §1 规则5 合规）。
> r806 消耗记录：T11-EXT 本轮完成出列（scripts/repo_pulse_probe.py 全 11 员期限梯扩展+selftest PASS〔ladder join 腿新增〕+results/repo_pulse_probe.json 全梯面）。真发现=月末脉冲率随期限单调衰减（GC001 17.6%/lift 5.4x→GC003 13.2%→GC004 11.1%→GC007 8.2%→GC014 2.6%/GC028 0.8%〔两员反转低于非月末〕）+深市 R-001 月末 lift 4.7x+传导衰减（GC001 脉冲日 GC003 mean z 5.73→GC014 2.67→GC028 1.19）+GC091/182 非有限 z（平基线 MAD=0±∞）剔除计数披露。技术队列 11→10 净减 1。prereg 面按 T-67 §2 冻结律+P1 署名门不自动开（纯测量纪律维持）。
> r807 消耗记录（r808 补录·当轮 close 漏记账如实披露）：T2 本轮完成出列（dashboard.html 三新面接线=常供池 autofill 行+饱和审计面行+试用劳力线行+engine 行 active_burns 烧录可视化·node --check rc=0+三面字段交叉核零缺失·bm-a 下轮 build 落 CEO 面）。技术队列 10→9。
> r808 消耗记录：T3 本轮完成出列（**J18b 数据采集墙**：monitor/build_status.py `_collector_wall_state()` 18 采集器一面墙=日线核心/LHB/涨停池/热度/期货/逆回购/期权/主力资金流/Sina四档/THS/财务资格/财报三面/AH溢价/个股日线qfq/五员ETF/ETF分钟/基金NAV/基金史回填——单源各车道·诚实降级·age/cutoff/mode 分类〔bad=fail/ok=False·warn=在途/未完备/>24h·ok=落地/合法no-op/完备终态〕+build() data.collector_wall 接线+dashboard.html renderChains「数据采集墙」行〔非绿面点名 note〕；验证=实数据读出 18 面 ok12/warn5/bad0/待产出1+全量 build() payload 断言+node --check rc=0〔Tools/_r808bmc_t3_verify.py〕；真发现=minute_feed 2 天未跑〔bm-b〕+moneyflow 源阻断 30min 自愈+astock qfq refresh 在途 5217/5229+options RETIRED 后 spawn 陈旗）。技术队列 9→8。
