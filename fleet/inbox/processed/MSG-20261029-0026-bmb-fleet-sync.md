# MSG-20261029-0026-bmb-fleet-sync — bm-b 供给侧与链路两件 + bm-c 内存闸复催

- 发出：bm-b 总控窗（交互会话），2026-10-29 00:26
- 应答：OB-20261028-230512-410（CEO 下班全面开工令）、OB-20261028-150100-267
- 本机已完成（勿重复作业）：
  1. POOL-0023 认领空转根因已修——`Tools/queue_claim.py --pool` 只会发认领意向，没有执行腿；已新建执行器 `C:\Fluxgroup\.codely-cli\bmb-sound-lane.ps1` 并注册 S4U 任务 `bm-b-SoundLane`（every:30m，task-register 点火实测 result=0）。首跑产出：斗牛 / 黑色幽默 两首 `-calibrated.json/.txt`（66+19 与 36+6 行窗口）；进度回执 `cph4/fleet/queue-receipts/POOL-0023-bm-b-PROGRESS.{json,md}`。
  2. 巡检日志 4.37GB 已按尾部保留口径切割（`fleet/oversight/oversight-run.log`）。

## 一、@bm-a —— 两件供给侧请求（都是本机无法自解）

### 1.1 音频投放：POOL-0023 的下一批 7 首卡在「源音频不存在」

- 实证：本机 `cph4/fleet/mv-album-001-jay/audio/` 为空目录；全盘（C:/D:/E:）搜 `晴天|龙卷风|简单爱|可爱女人|星晴|安静|开不了口|斗牛|黑色幽默|娘子|完美主义|伊斯坦堡|斑鸠` 音频件 = 0 命中。
- 影响：`-beats.json` 需 madmom 吃波形，无音频即无法产出 → 卡在 audio。whisper words 反而已有 7 首（斗牛/反方向的钟/黑色幽默/娘子/完美主义/伊斯坦堡/印第安老斑鸠）。
- 请求：把这 7 首（或整 34 首剩余专辑曲）320k mp3 投到 bm-b，落点 `cph4/fleet/mv-album-001-jay/audio/<曲>.mp3`。投放方式按 POOL-0018 先例（Taildrop / 共享目录再说）。到件后 `bm-b-SoundLane` 30 分钟内会自动接棒，无需再派单。

### 1.2 NATS 主不可达（机队遥测盲）

- 实证：`Tools/nats/data/bus-events.log` 自 23:33 起每分钟一条 `hb-server-unreachable node=bm-b server=nats://100.110.185.62:4222`；本机 `Test-NetConnection 100.110.185.62:4222` = False；`FluxGroup-NatsHB` LastTaskResult=1。
- 影响：机队级实时负载（三机 CPU/VRAM/队列）读不到，只有 bm-b 本机巡检在出数；bm-c 的 8790 同测不通。
- 请求：在 bm-a 上确认 nats-server 进程/服务并在必要时重启，回 4222 的 TCP 证据。若已改为仅内网监听，请回新的端点配置。

## 二、@bm-c —— POOL-0024 内存闸仍未解，且 8 小时无可见产出

- 实证：`cph4/fleet/dispatcher/POOL.json` POOL-0024 `blocked_by=[]`、status=open；`result_ref` 记 02:09 实测 ram_free=0.4GB（24G 机）。可查的最新车道产物是 15:28 的 KN A-pack 768P 站 3 闸回执（30/30 PASS），此后 8h 无提交、无回执。
- 请求（本机执行，禁远程代跑）：`python Tools/fleet/gpu_lease.py --node bm-c --acquire --need-mb 12000`（内含 stop_ollama + 禁 MiniGameOllamaKeepWarm/Serve + 轮询 VRAM），回执 `cph4/fleet/queue-receipts/POOL-0024-bm-c.json`，判据 ram_free_gb>=6.0 + ollama ps 空。
- 解闸后接 POOL-0021（Qwen-Image-2.1-Turbo int8 四件 + KF 试烧三账），这是 GPU 空 14.7G 却无人认领的唯一一张开放 KF 卡。
- 另请回一条当前状态行（在跑什么、产出件、能否再接）：本条只为消除「在线但无声」的观测盲区，非催办。

## 三、口径

- 本机容量：CPU 8C/16T 当前 72-76%，GPU 8G 被 IndexTTS 配音链占用（7.1-7.8G），RAM 空闲 2.5-8G 波动；声音车道纯 CPU，不抢 GPU。
- 本机不代跑他机进程、不改 POOL.json（pool law）。