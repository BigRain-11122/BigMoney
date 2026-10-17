# POOL-0020 回执补交（bm-b · r987 · 2026-10-17 09:3x）

卡 ID: POOL-0020 · 动作: **done**（工作 10-15 23:34 执行 · 回执 10-17 补交 · 催办在案认账）

## 验收物证据指针（卡③逐项）

1. **nvidia-smi power_limit 实测=239.80W**：2026-10-17 09:2x 活体复读 `239.80 W, 33C, 8192 MiB` ✓
2. **两 PowerCap 任务删除实证**：Get-ScheduledTask GPU-PowerCap-180W-Boot / GPU-PowerCap-180W-Hourly = **0 found**（已删无漏）✓
3. **GPU 停车旗解除实证**：machine-state GPU 面复役（O-20261015-0906-bm-b §4 反向恢复·r986 执行）
4. **烧机 30min 档案**：results/_r986bmb_gpu_burn_evidence.csv（361 行·BURN DONE dur=30min·max_draw=239.1W·max_temp=77C·零断电零 WHEA）✓
5. **orders 回执行**：r986 轮账本+心跳 did（O-20261015-1821 CEO「bm-b我换好了，开工」执行面）
6. **commit sha**：c1f67faba（round 986 closeout·origin 在位）+ f900a7bb3（segment B）

## 附记

- card-lint REJECT 事项（spec 指针=memory\bmb-power-loss 本地记忆路径·group 仓不可解析）：权威替代=CEO 直令 O-20261015-0952/O-1821 + group 仓回执件 cph4/fleet/bm-b-powermax-20261015.md（10-15 循环轮携带推）
- POOL.json 状态翻面归 dispatcher 写手席（本机禁写 POOL.json·代理席写手制）——本回执=翻卡依据件
