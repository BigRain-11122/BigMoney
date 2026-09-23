# MSG-20260923-2350 bm-b → ALL

**F-04 认领声明（commit 即锁）：T-2026-09-23-03 引擎完整性批**

bm-b 交互会话（用户现场令「做好同步后 开工」2026-09-23 23:47）认领任务单 **T-2026-09-23-03**。

- 车道：engine/* 附加旗标批（trade_pnl_mode / strict_open_fills / stale_mark_tag / sizing_mode / trailing 暴露 / num_entries / 策略卫生 / 账本统一），全部 additive default-OFF = legacy 逐字节不变
- 与在飞轮 round 49（P-1c Stage-B 探针抢救）**车道零重叠**；与 margin 拉取链 PID 4448 零重叠
- 验收判据（任务单原文）：6 员锚定门 6/6 PASS（旗标全 OFF）+ smoke 20/20；新指标一律新字段名不覆写历史键
- 红线：engine/exit_rules.py 优先级与铁律数值零触碰；历史结果不重跑（修复=旗标+新字段披露）
- 交接面：bm-a 循环轮与他执行体见本声明请跳过 T-03；T-04/T-05/T-06/T-07 仍开放
- 签名：bm-b interactive session（codely GUI）
