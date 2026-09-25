# R-20260925 bm-a 本地编码能力试点预注册（O-20260925-2313 CEO 令·跑前冻结）

- 上游令：fleet/orders/O-20260925-2313-bm-c.md（CEO 原话「bm-a机器 去弄吧，去做一下力所能及的编码工作，看看什么结果，持续观察，记得汇报」）
- 上游研究件：HQ `cph4/research/R-20260925-local-coding.md`（commit 9fcce33）·框架件 P-08 机队模型适配矩阵（本试点=其 bm-a 侧首个实弹件，实测数据回填任务-模型-机器映射表）
- 受令机=bm-a（9950X 32T · RAM 96GB 总量 · 4070S 12GB VRAM）·试点窗=2026-09-25 → **2026-10-09 中期判读**
- **冻结律：本文件落 git 后才准开跑 A/B；判据/任务清单/提示词模板跑后禁改（改=VIOLATION 如实上报）**

## §1 装机面（§0 物理依赖=19GB 下载在途）

- 模型：`qwen3-coder:30b`（Q4_K_M≈19GB · 30B-A3B MoE agent coder · 编码专训）
- 服务配置：NUM_PARALLEL=1 · KV cache q8_0 · ctx 32768（infra-3 §3.3 例外登记）
- 混合推理：GPU(12GB) 置激活参数+CPU/RAM 置专家（MoE 3B 激活→搬运便宜，预估 10-20 tok/s）
- 让路护栏（令 §2 冻结）：主产线在飞（回测/收单/判定批）时试点让路；**RAM 空闲<30GB 禁载入 19GB 级模型**；与在役三件（qwen2.5:7b-instruct/qwen2.5:14b/bge-m3）VRAM 冲突走 keepwarm.pause 释放阀或离峰窗 03:00-07:00
- 装机实况记录：logs/qwen3coder_pull.log（分离下载·断点续传·5 连重试律；三降级路径=tag 不识→升 ollama→fresh sweep 同档替代→hf-mirror GGUF+llama-server 兜底，逐级留痕）

## §2 A/B 协议（跑前冻结）

- **任务宇宙=10 件本仓自身车道力所能及真实编码单**（小工具/校验器/报表生成/JSON 处理类；每件带确定性验证命令=exit-code 契约；**禁碰他人 claimed 票域**（T-66/T-68/T-16 等）·单项目纪律不破）
- **候选池 12 件 FIFO 取前 10**（禁樱桃：清单先冻结、序固定、后 2 件=前 10 有预跑前不适格项时的替补，替换须留痕）：见 §5
- 同单双跑：**A 臂=云端基线**（现行生产编码通道）vs **B 臂=本地 qwen3-coder:30b**（Ollama OpenAI 兼容端点）；**同一冻结提示词**（任务规格+目标路径+验证命令，模板见 §4），双臂信息面恒等
- 单件产物隔离：results/local_coding_pilot/tasks/<NN>/<arm>/（代码+运行日志+验证输出），互不可见对方产物（盲评纪律）

## §3 四判据（令 §3 冻结·跑后禁改）

1. **功能通过率**：该件冻结的确定性验证命令通过（exit 0）=PASS；跑通/测试绿口径
2. **码质盲评**：四维 1-10 分（可读性/惯用法契合/边界处理/结构组织），评者盲（不见臂标签）；**本地均分 ≥ 云端−0.5 = 非劣判过**
3. **时延**：p50/p95（首 token 时延+总时长），双臂同记
4. **资源面**：VRAM/RAM 实占 · tok/s 实测 · 溢出次数（context overflow / OOM / 让路触发各计一次）

**过线定义（中期判读 2026-10-09）**：①功能通过率 ≥ 云端−0 件 AND ②码质非劣 AND ③④如实呈报（无硬线，资源面=披露项）→ 过线；任一不满足→如实报坑清单。
**过线后**：每周维持 ≥5 件本地件持续采样（非全切·云端降级阀保留）；呈 P1 购买卡（24GB 专用编码机·fleet-allocations §六.6 判据 A 形态）。

## §4 冻结提示词模板（双臂恒等）

```
任务：<一句话规格>
目标文件：scripts/<name>.py（新建；仅此一件产物）
约束：Python 3.14 可跑；零第三方新依赖；selftest 子命令=离线断言；exit 0=通过
验证命令：python scripts/<name>.py selftest
输入样例与输出契约：<per-task frozen spec>
```

## §5 候选池（12 件冻结·FIFO 前 10；全部=本仓自有车道小件，零碰撞他票）

| # | 单 | 验证命令（冻结） |
|---|---|---|
| 01 | round report 行 lint（R 行五字段结构+时间戳格式校验器） | python scripts/rr_lint.py selftest |
| 02 | watermark_red.json schema 校验器（字段/类型/红牌键） | python scripts/wm_red_lint.py selftest |
| 03 | options 采集道健康摘要器（status→一行 verdict 生成） | python scripts/opt_lane_digest.py selftest |
| 04 | fleet 任务板 aging 报表（claimed 时长/状态计数） | python scripts/board_aging.py selftest |
| 05 | inbox 消息 aging/未处理扫描器（逐件 ETA 行） | python scripts/inbox_aging.py selftest |
| 06 | token 台账 per-leg 增量分解工具（读 token_usage.json 派生表） | python scripts/token_breakdown.py selftest |
| 07 | update_status 面板新鲜度矩阵（S6 各腿 last-run 年龄表） | python scripts/leg_freshness.py selftest |
| 08 | options_update_cells.jsonl 对账器（checkpoint 行数 vs panel.universe/attempted） | python scripts/opt_cells_recon.py selftest |
| 09 | 分离刷新道日志进度解析器（options/ah/mf 三 log→一行进度） | python scripts/lane_log_digest.py selftest |
| 10 | fleet 心跳 epoch 类型 lint（全机 heartbeat_epoch_utc int 扫描=F7 面） | python scripts/hb_epoch_lint.py selftest |
| 11 | HANDOVER 快照窗 delta 工具（相邻快照行轮号差校验） | python scripts/handover_delta.py selftest |
| 12 | core48 日线缺口审计器（vs 510300 日历 in-span 缺失列举） | python scripts/daily_gap_audit.py selftest |

（替补纪律：01-10 任一件在首跑前发现不适格（重复既有件/碰撞他票），按序以 11/12 顶替并在台账留痕；首跑后清单死锁禁换。）

## §6 记账与观察（令 §4/§5 冻结）

- 跑一单记一行：results/local_coding_pilot/ledger.jsonl（task/arm/pass/四判据数值/tokens 本地估算 vs 云端省减/timestamp）
- token-economy：本地处理 N 件·云端省 M（粗估口径如实标注，与 token_meter 同源字节/3.5 口径）
- 每轮报告一行试点进展；心跳 orders_ack 回执 O-20260925-2313-bm-c
- 结果文件持续累积（禁删除失败记录·失败如实记）

—— bm-a 总经办 R195 收令即冻结（2026-09-26 00:1x · 落 git 即生效 · 跑后禁改）
