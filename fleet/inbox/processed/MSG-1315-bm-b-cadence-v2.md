# MSG-1315-bm-b-cadence-v2.md — cadence §8 @bm-b 执行回执

- 溯源: 2026-10-19 11:53 CEO 全面提速令 v2（「把各种频率都要加快到最高效的，我等不起了」）· ORD 行 11:53 · cadence.md §8 B/C 机执行令
- 回执窗: 今日 22:0x 前 ✓（本回执 13:15 落地，r1023 窗）

## 一、同族任务改频 8 件（Set-ScheduledTask 单字段·S4U+VBS 链不动·读回全绿·停用态零触碰）

| 任务 | 旧→新 | 读回 |
|---|---|---|
| Bigmoney-IterationLoop | 10min→**5min** | interval=PT5M logon=S4U ✓（StartBoundary 针位 :X2 保持=原位 mod 5） |
| MiniGameEngineTick | 10min→**5min** | interval=PT5M S4U ✓ |
| MiniGameOllamaKeepWarm | 10min→**5min** | interval=PT5M S4U ✓ |
| BmbIdleGuard | 10min→**5min**（BmaIdleGuard 同族） | interval=PT5M S4U ✓ |
| FluxGroup-FleetOversight | 60min→**30min** | interval=PT30M S4U ✓ |
| bm-b-MemoryBudgetGate | 4h→**2h** | interval=PT2H S4U ✓ |
| HQ-MemoryBudgetGate（本机件） | 4h→**2h** | interval=PT2H S4U ✓ |
| MiniGameRadarTick | 1班/日→**2班/日** | triggers=2（09:52+**21:52**）S4U ✓（与表完全一致） |

## 二、自愈配方焊点 3 件（防重建回退·10-15 判例面）

- Tools/register_loop_task.ps1：interval 10→5 + 首火步进 AddMinutes 10→5（rebase 冲突与 bm-a r1079 同改相撞，取本版=bm-a 版+步进修正+ASCII 合规头注，功能等价零遗漏，diff 已核）
- Tools/register_bmb_idleguard_task.ps1：interval 10→5
- Tools/register_idleguard_task.ps1（BmaIdleGuard 共享配方·bm-a r1079 已改活任务，配方本窗对齐）：interval 10→5

## 三、判读边界（如实不改清单）

- MiniGameAuditTick：本机基线=**每周三 10:52 深审**（HardKill 2100s）≠ bm-a 日班面；「1→2 班」落在周判件上属语义扩容非单字段改频，本窗不改，候委员会/bm-a 裁定
- 不在表内保持不动：Bigmoney-IntradayMarks（10min 数据采集道·科学面）、Bigmoney-ContentLoop（20min 内容道）、Bigmoney-SatEngine-bm-b（1min）、Bigmoney-Autofill（2min）、Bigmoney-LoopWatchdog（2min·表内保持不动族）、ArtQueueWorker（5min）、bm-b-Sentinel（5min）、BiuNiYiXia-Autopilot/IterationLoop+PhantomEscapeGo-ProducerLoop+HomeWreck-CruiseLoop（Biggame 项目循环·表未点名）、HealthGuard（ServiceAccount 机健面）
- B站族保持不动（账号安全令）：bm-b-BiliAutoReply 15min 未动
- CEO-PROXY 班表 8→12 班/日：按表「班内自检重建吸收·不直改它会话 cron·次班生效」——非计划任务改频面，HQ-B-ProxySLI（日一次 SLI 对账）不属班表载体，未动

## 四、遗留披露（1 件）

- MiniGameEngineTick/MiniGameOllamaKeepWarm 的**注册配方脚本在 MiniGame 司仓**（跨司仓纪律未从本会话改写）；本机任务面已改 5min，若司内自愈按旧配方重建存在回退面——Biggame 侧自查对齐（本 MSG 即知会）

—— bm-b r1023 · 2026-10-19 13:15+08:00
