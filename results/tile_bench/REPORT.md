# CPH4 低配机 2D 渲染性能基准 · tile 大城帧预算（bm-b RTX 3070 8GB 档）

> backlog #9 · claimed bm-b 2026-10-10T21:59:03+08:00 · 引擎=Tuanjie 2022.3.62t15 editor -batchmode 手动渲染循环 (RT 1600×900/内置管线) · 32px point-filter 运行时生成 tile · Tilemap chunk 模式
> 环境: GPU=NVIDIA GeForce RTX 3070 (8018MB) · CPU=AMD Ryzen 7 3800X 8-Core Processor  · RAM=23GB · editor-batchmode 无窗 RT 1600×900 手动渲染 · co-resident=Ollama 7b 常驻(~4.5GB VRAM) + astock 刷新 IO 后台

## 矩阵读数（hold=静止视角 / pan=12 tile/s 对角平移最坏段）

| 配置 | 地图 tiles | 可见 tiles/帧 | hold avg/p99 ms | pan avg/p99 ms | pan avg fps | 判定 |
|---|---|---|---|---|---|---|
| 01_s256_L1_o17 (L1,o17.0) | 65,536 | 2,055 | 3.308 / 4.549 | 3.245 / 4.546 | 308.2 | GREEN |
| 02_s512_L1_o17 (L1,o17.0) | 262,144 | 2,055 | 3.341 / 4.524 | 3.317 / 4.563 | 301.5 | GREEN |
| 03_s1024_L1_o17 (L1,o17.0) | 1,048,576 | 2,055 | 3.329 / 4.482 | 3.228 / 4.519 | 309.8 | GREEN |
| 04_s1024_L3_o17 (L3,o17.0) | 1,678,062 | 6,165 | 3.377 / 5.003 | 3.348 / 4.56 | 298.7 | GREEN |
| 05_s1024_L1_o34 (L1,o34.0) | 1,048,576 | 8,220 | 3.339 / 4.532 | 3.207 / 4.546 | 311.8 | GREEN |
| 06_s1024_L3_o34 (L3,o34.0) | 1,678,062 | 24,661 | 3.456 / 4.725 | 3.415 / 5.036 | 292.8 | GREEN |
| 07_s1024_L3_o8_5 (L3,o8.5) | 1,678,062 | 1,541 | 3.365 / 4.526 | 3.29 / 4.484 | 304.0 | GREEN |
| 08_s1024_L3_o17_r2 (L3,o17.0) | 1,678,062 | 6,165 | 3.37 / 4.481 | 3.151 / 4.536 | 317.4 | GREEN |

## 帧预算结论
- 全 GREEN 最大可见面: run06_s1024_L3_o34.json = 24,661 tiles/帧（pan p99 5.04ms ≤16.67）
- **tile 大城帧预算（bm-b 3070 档推荐值，含 20% 安全余量）: 每帧可见 tiles ≤ 19,729（60fps p99 口径）**
- 换算: 1600×900 窗口下 ortho 尺寸 ≤ 该可见面所对应视口；地图总尺寸受内存/生成成本约束（见 size sweep 对比）而非渲染
- size sweep（同视口 L1）: 256²=3.25ms · 512²=3.32ms · 1024²=3.23ms → 渲染成本由可见 tiles 主导，地图总尺寸主要抬升内存（reservedMB 见 JSON；workingSet 在 editor batchmode 下两 API 皆返 0=该口径不可用，如实留 0）
- 复跑一致性: pan avg 3.35 vs 3.15 ms（差 5.9%）

## 方法论与诚实披露
- r845 路线=editor -batchmode 手动渲染循环（r844 实测 standalone player 隐藏窗不进 player loop、可见窗被零窗律禁 → 弃 player 路线）。每 tick cam.Render() 渲至固定 RT 1600×900，1×1 ReadPixels 强制 GPU 排空，帧 dt=编辑器 loop tick 间隔（含渲染提交+GPU+循环开销）。
- 口径=standalone player 的保守下界：编辑器循环开销计入帧、无 DWM 合成收益，实机 player 通常更快；working set 含编辑器本体常驻开销，size sweep 读增量不读绝对值。无后处理、无灯光（Sprites/Default unlit）。
- 基准与 Ollama 7b 常驻(~4.5GB VRAM)、astock 全宇宙刷新 IO 并发运行=机队真实载荷口径。
- tile 为 32px/格点过滤/4 变体；deco 层 30% 稀疏填充模拟装饰覆盖。pan 段 12 tiles/s 对角平移=持续新块入视的最坏段。
- 判定: GREEN=pan p99 ≤16.67ms · YELLOW=avg 达标但 p99 超线 · RED=avg 超线。
