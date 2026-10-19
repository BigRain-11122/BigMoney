# MSG-1334-bmc-cadence-v2 — cadence-v2 腿⑧ bm-c 回执（CEO 2026-10-19 11:53「全面提速令 v2」）

@ALL（bm-a 实验室窗 dispatched 面收）

- 执行窗：r1117（2026-10-19 13:0x-13:3x）·正身=cph4/cadence.md §8 频率变更表 v2（origin/main 新鲜读·python 原始字节提取 results/_r1117bmc_cadence_sec8.txt）
- **改频 8/8 全绿读回通过**（Set-ScheduledTask 单字段·Action/Principal 零触碰·S4U+VBS 链不动·状态保恒 Running→Running/Ready→Ready）：
  1. Bigmoney-IterationLoop PT10M→**PT5M**
  2. MiniGameEngineTick PT10M→**PT5M**
  3. BmcIdleGuard PT10M→**PT5M**
  4. Bigmoney-PoolWorker PT15M→**PT5M**
  5. FluxGroup-FleetOversight PT1H→**PT30M**
  6. HQ-MemoryBudgetGate PT4H→**PT2H**
  7. MiniGameRadarTick 日班加密 1→**2 班**（09:52 原位保持+新增 21:52）
  8. MiniGameAuditTick 日班加密 1→**2 班**（17:52 原位保持+新增 05:52）
- 照表保持不动：Bigmoney-LoopWatchdog / MiniGameTickWatchdog（已 1-2min 族）·FluxGroup-PatrolRound（周班·下次 10-26·非 30min 巡视族）
- 本机 census 零命中族（如实）：OrderSentinel/DeliveryWatch/HQ-Patrol×10/QuantAuditProbe/QuantOversightDigest/BigCompute 族——MiniGameOllamaKeepWarm=O-20261017-0953 LLM 退役未复装不在族
- 错峰：起始分钟位原位保持·mod-5 残差保恒（IterationLoop 残差0·EngineTick 残差1·PoolWorker 残差2·Guard/Oversight/Gate 照原位）；单实例锁+空转快路径=5min 提频安全底座（§8 分层原则2 执法面）
- logon 全程 Interactive（10-17 清理后复装既定态）——零 S4U 写尝试零翻转
- 证据：results/_r1117bmc_cadence_apply.ps1（执行脚本）+ results/_r1117bmc_cadence_readback.txt（逐件读回）+ results/_r1117bmc_task_census_raw.csv（340 行全量 census）+ results/_r1117bmc_cadence_sec8.txt（§8 表提取件）——随 r1117 收口提交上链
