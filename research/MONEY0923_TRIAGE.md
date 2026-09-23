# Money0923 盘点整合报告（O-20260923-1514-bm-a）

> CEO 令 2026-09-23 15:14：「Money0923 查一下，看里面的数据 系统什么的，有用的留下来整合，可以学的学，没用的全删」。
> 执行机 bm-a（quant 专管会话）。本报告=删除前留档（Money02 清理报告同构）。

## 一、Money0923 是什么（盘点定性）

- 位置 `quant\Money0923`，2026-09-19→09-22 开发的「Money·自进化量化交易系统（A股+ETF+期货）」完整一代系统；2026-09-22 21:50 CEO 停机令「money 有关的自动化全部取消」后封存。**本报告全程静态整合，未恢复任何自动化**（停机令继续有效，恢复须 CEO 明令，步骤见归档 DEV_NOTES.md 顶部）。
- 原始规模：**24,313 件 / 2.03GB**。
- 停机时实况（state.json）：账户 ¥99,965（-0.03%）· 冠军 multifactor（样本外 0.5794）· 联赛 33,605 局 · 认证池 200 · GA 2900+ 代。
- 血脉关系：BigMoney 的 35 策略 / 分仓（SLEEVE_P3）/ market_rules 与其同源（35 族 / S1-S3 分仓 / 规则表一脉相承）——**本代=BigMoney 直系前代**，独立价值在于 BigMoney 尚缺的件（见 §三）。

## 二、整合清单（有用集 → 已入本仓 `Money0923/`，782 件 / 95.8MB，robocopy 0 失败）

| 项 | 价值 |
|---|---|
| 系统代码：run.py + quant/ 32 模块 + tests/ 13 套 + tools/ | 完整可运行一代系统 |
| 顶层文档：README / SYSTEM_AUDIT（14 节全量自审）/ HANDOFF / DEV_NOTES / CODELY | 系统设计+红线档案 |
| data/daily：25 年日线面板 204 只（2001-09 起，全 regime 谱）35.8MB | 跨 2001 熊/2007 泡沫/2015 股灾/2018 熊/2019-21 结构牛的回测语料 |
| data/minute_store + minute：分钟语料 57.2MB | 「滚动窗不存即蒸发」不可再生资产 |
| data/repo_daily.csv：逆回购利率 2013→今全史 | 现金管理燃料 |
| data 其余（negative/futures_daily/universe/纪元/校验报告） | 池与数据治理留痕 |
| state/state.json 0.84MB | 唯一复活锚点（进化代数/认证池/账户轨道） |
| logs 提纯战绩：report/review/walkforward/top10/verdict/audit + champion_equity/trades.csv + audit_ledger.jsonl + arena_board.html | 模拟盘战绩证据链（CEO 钦定唯一计分板） |
| MoneyViz 源：Assets 5 脚本（StateFeeder 2s 轮询 state.json/程序化像素零美术/VizSelfCheck）+场景+Packages/ProjectSettings+双 README | **J12 总控 v2 的团结引擎前代参照** |
| codely_memory_archive_20260922_codely_full.md（105KB 蒸馏原文） | 开发史不可再生档案 |

未复制：config.json（机内局部配置，其自声明不入库；无密钥：账号空、dry_run=true、mode=paper）。

## 三、可学清单（BigMoney 择机采纳；**均须 CEO 署名才立项**，本报告只登记不实施）

1. **QMT 实盘桥**（quant/broker_qmt.py + live.py，dry_run 分级 + 程序化交易报备注记）——BigMoney 实盘阶段的现成通道。
2. **国债逆回购现金管理**（repo.py：收盘借出 GC001/次日归还/回测·模拟·实盘三端一致计息）。
3. **分钟语料库纪律**（minute_store.py：滚动窗即蒸发→每日落盘）——日线波段外的未来燃料。
4. **数据纪元/污染清除**（validation.py + data_epoch：坏数据不进模型、证据分级清除）。
5. **防作弊审计三件**（无未来函数抽查/复算哈希/先声明后揭示）——与 BigMoney 零假设校准互补。
6. **gamble 随机对照组**（35 族含随机基线，所有策略须跑赢它才配谈超额）——便宜的科学底线。
7. **GPU 广域海选模式**（GPU 出广度/CPU 引擎出深度/闸门出裁决，20000 组/族/夜）——Optuna 线加速思路。
8. **联赛认证选拔**（200 队×随机 1 年窗×3 连胜认证+证据制淘汰+多样性硬约束 同族≤3/相关性<0.85）。
9. **指标预热缓冲**（评估窗前 300 日供指标计算，防长回看策略结构性失能）——窗评估方法论教训。
10. **Token 经济**（run.py ctx ~300 token 入口 + 危险文件禁读表 + 按任务选读）。
11. **负面清单三层执行**（池筛→备单终检→持仓离场）。
12. 同源证据降级铁律（联赛内对比永久降级参考，有效性只认前瞻独立证据）——CEO 科学总纲的工程化范例。

## 四、删除清单（无用集，原目录整体移除）

| 项 | 体量 | 判定 |
|---|---|---|
| MoneyViz/Library（PackageCache/ShaderCache/StateCache/TempArtifacts） | **1.76GB** | 团结引擎可再生缓存 |
| data/eval_cache.db(+wal/shm) | 60MB | SQLite 计算缓存，口径/纪元变更自动失效重刷 |
| state/backups 48 份滚动备份 | 39.1MB | 同一 state 的 24h 内近重复 |
| logs/auto.log + hist_pull.log + watchdog.log + watchdog_start_*(172 件) | ~50MB | 原始过程日志，提纯报告已留 |
| __pycache__ / bin / obj / *.pyc / sln / csproj / UserSettings | 零散 | 可再生 |
| config.json | 0.6KB | 机内局部配置 |
| **合计** | **≈1.93GB / ≈23,531 件** | |

删除执行时点：本仓 commit+push（GitHub 远端备份）确认后，原 `quant\Money0923` 整目录移除。

## 五、复活路径（仅 CEO 明令时）

归档在本仓即完整系统：clone BigMoney → `Money0923/` → 复制 config.example.json 为 config.json → 按 DEV_NOTES.md 顶部「停机令恢复三步」走（删 watchdog_pause → 启用计划任务 → 拉起守护）。数据纪元 s9/f1 与评估缓存口径见归档 SYSTEM_AUDIT §3.4。

—— bm-a quant 专管会话 · 2026-09-23
