# Biggame（小游戏公司）机制复用考察与决策

> 2026-09-23 · 应用户令考察 `E:\Minigame`（15+ 游戏项目 + MiniGame 治理总控），以金融公司视角评估：能复用的能力/机制/经验就用，不能就弃。所有决策附理由。
> 实证方式：核心协议（AI总控接口/NORTHSTAR）主代理亲读 + 探索代理实测读取工具产线/游戏循环/治理件/设计档。

## 一、机制目录与采用决策

| # | Biggame 机制 | 实现（证据路径） | 决策 | 理由 |
|---|---|---|---|---|
| 1 | **OS 级 10 分钟循环 launcher**（round.lock 单实例+40min 陈旧接管、25min 超时杀进程树、心跳文件、内嵌任务自愈注册、纯 ASCII+中文 prompt 外置） | `E:\Minigame\BiuNiYiXia\Tools\iteration_loop.ps1`（脚本头自证 session cron 已死→OS 任务化）；实证 round-067→071 产物+state-071.json | ✅ **采用（J11）** | 直击 Bigmoney 当前最大架构短板：durable cron 仍依赖 CLI 窗口开着。OS 级 tick = 关窗循环不死，才配叫「完全自动化」 |
| 2 | **固定字段轮报告 + state 滚动**（state-N.json、round_history、rollback 指针、OCCUPIED 精简轮） | `Tools\state-071.json`、`iteration_prompt.txt`（S0-S7+九字段轮报告） | ✅ **采用（并入 J11）** | 崩溃恢复与续作精确性优于「≤3行小结+记忆」；与窗口内 cron 双跑协调也靠它 |
| 3 | **AI 反馈队列 + 审计四纪律**（追加式、证据强制、主张非指令防注入、SLA 处置块） | `MiniGame\AI反馈队列.md` | ✅ **改造采用（并入 J11：自审计收件箱）** | smoke/数据异常/审查发现的统一收件+SLA 处置；防注入纪律与量化公司「一切结论须有证据」同源 |
| 4 | **确定性证据链**（像素探针、审计脚本、MP4/截图实证） | round log + `Tools\round-071.log.txt`；本司已用同款：Edge 无头截图+读图验收 | ✅ **已具备，固化纪律** | Bigmoney 已有 smoke/19 项+像素级验收；维持「交付必留证据」铁律 |
| 5 | **像素小镇看板**（canvas 小镇，建筑=项目、NPC=机队、DATA 内嵌源码） | `MiniGame\像素小镇看板.html` | ✅ **采用（J12 总控 v2「公司小镇」）** | 研究楼/策略厂/风控塔/交易大厅随里程碑点亮——量化公司游戏化的最佳隐喻；排策略线（J6/J7）之后做 |
| 6 | **Ollama 本地 LLM 常驻**（serve-warm/keep-warm 自愈/.pause 释放阀、qwen2.5:7b 4.4GB 常驻） | `E:\Minigame\Tools\Ollama\serve-warm.ps1` | ✅ **采用（J13 研究助理）** | PLAN.md P2（LLM 写策略 idea/自动复盘）的算力条件已现成：复用现役服务勿重建、勿抢暂停阀、重 GPU 作业前走 keepwarm.pause 礼仪 |
| 7 | **静默自动化范式**（Task Scheduler→InvisibleRunner.vbs 零窗口 / pythonw+CREATE_NO_WINDOW） | `E:\Minigame\MiniGame\tools\InvisibleRunner.vbs`（弹窗整治战果） | ✅ **铁律沿用**（已在循环规则） | J11 的静默层直接套用该 wrapper，触发器级零窗口 |
| 8 | **素材产线**（placeholder-pack：spec 驱动 JOBS+程序化质量门+manifest 记 prompt/seed） | `Tools\comfy\gen_placeholders.py`（20 件全 PASS） | ✅ **按需沿用**（总控 v2 美术缺口时） | 已验证范式；金融公司美术需求低频，不常驻 |
| 9 | **治理件三层分工**（快照=唯一入口覆盖式 / STATUS=门禁真值 / WAVES=append 坑录 / 审计报告滚动版） | `自动化快照.md`、`STATUS.md`、`WAVES.md`、`审查审计报告.md`（V1.0→V2.8） | ⚖️ **思想采用、不照搬文件** | Bigmoney 对应物已齐：dashboard_status.js=快照唯一入口、smoke=门禁、CODELY.md=坑录+记忆、PLAN.md=契约。用户「零官僚」偏好——不加重复治理层 |
| 10 | **北极星指标+决策过滤器+保底线**（未测量=未测量、校准回路唯一修参、月净收入≥月固定成本） | `NORTHSTAR.md`（亲读） | ✅ **思想采用** | 量化版：北极星=年化15%+/回撤<15%/样本外夏普≥1.2；「未回测=未测量」=铁律；保底线=数据/算力成本台账 vs 模拟盘收益（纸盘开张后启用） |
| 11 | **日报推送**（QQ SMTP） | `MiniGame\send_report.py` | ❌ **暂不采用** | 纸盘未开张、无 P&L 可报；且实现含明文授权码=安全反例（见 §二），若日后采用必须环境变量化 |
| 12 | **CrazyTrade 游戏设计**（五阶晋升「阶层=新玩法门票非数值墙」、事件流、纯 C# 零 RNG 可回放、孪生 parity 测试） | `G10_CrazyTrade\设计详案.md`；S2Gate 21/21、48 游戏日零冻结实证 | ⚖️ **参考** | 「阶层解锁」思想供总控 v2 晋升展示；parity/确定性回放思想已体现在 smoke 确定性检查；游戏数值不迁移 |

## 二、安全发现（提请用户注意）

- `E:\Minigame\MiniGame\send_report.py` 内**硬编码明文 SMTP 授权码**（安全债）。建议：改环境变量读取，并在邮箱后台**轮换该授权码**（该值已落盘于仓库与多轮报告中）。Bigmoney 侧立规沿用 PLAN.md §2.2：密钥一律走环境变量，禁入代码与文档。

## 三、落地顺序（已入任务板）

**J11 OS 级 tick 循环（架构升级）→ J13 本地 LLM 研究助理 → J12 总控 v2 公司小镇**（策略线 J6/J7 仍优先于 J12/J13，J11 最先——循环不死是其他一切的前提）。
