# 心跳面同一量印了七个值 —— 别名一致性审计（r2129 第二件）

- 轮次：r2129（bm-c）
- 产品件：`Tools/heartbeat_alias_audit.py`、`results/heartbeat_alias_audit.json`
- 自检 23/23、`run` rc0、`check` **CHECK OK**（3 台心跳 / 0 台大小写重复键 / 3 台别名互相矛盾 / 2 台单位错标）
- 只读面：从不改任何心跳、从不挑一个"真值"

## 1. 起因

本轮写心跳前想用 `ConvertFrom-Json` 读一下本机文件，直接被拒：

```
ConvertFrom-Json: 无法转换 JSON 字符串，因为它包含具有不同大小写的键…
尝试添加到现有键 'CPU_load_pct' 的键是 'cpu_load_pct'
```

`fleet/machines/*.json` 是多写者合并面，每个写者各造一个键名。于是同台机器同时印着 `cpu_load_pct=97`、`CPU_load_pct=10.2`、`cpu_pct=37`、`cpu_total_pct=33`。这既是 r1909「自洽要按读者能读到的每个字母算」的舰队版，也是一个硬缺陷：**严格读 JSON 的读者连文件都打不开**。

## 2. 审计口径（冻结在代码里）

- `R1` 只把「名字明说是同一个测量」的键编组（`cpu` 这种裸键不算机器总负载）；
- `R2` GB/GiB 一律 ×1024 换到 MiB 再比，百分比与内存永不混；
- `R3` 一致性 = 离散度 ≤ max(64 MiB, 中位 × 2%)，阈值先写后读；
- `R4` 没有写者发布的数量记 `MISSING`，不是 0；
- `R5` 大小写重复键即使数值一致也必须报（它破坏严格读者）；
- `R6` 只读，从不改写、从不选一个权威；
- `R7` 单位错标独立判据：**不信键名**，只问「这个 `_gb`/`_gib` 键的原始数字是否正好等于那组 MiB 键的中位、而换算后不是」——是就点名，两个读数一起印。

## 3. 实测（2026-11-26 12:2x，三台全读，本机修完之后）

| 机器 | 判词 | cpu_load_pct | ram_free_mb | vram_free_mb |
|---|---|---|---|---|
| bm-a | DISAGREEING_ALIASES | 分歧 | 分歧（18,157 MB） | 分歧（**1,061,888 MB**，由单位错标造成） |
| bm-b | DISAGREEING_ALIASES | 分歧（2.1 pp） | 分歧（2,466 MB） | AGREE |
| bm-c | DISAGREEING_ALIASES | 分歧（仍） | **AGREE** | 分歧（唯一原因 = `_gib` 单位错标） |

台数统计：重复大小写键 **0** 台（本机已修）、别名矛盾 3 台、矛盾数量 **7** 个、缺失 0 个、**单位错标 2 台 / 2 个键**。

### 根因不在 bm-a 的手，在共享写手

给本机写心跳时按预提交爪的要求走官方写手 `python Tools/gpu_face.py apply`，它写完本机就长出了同样的毛病：

```
gpu_free_mib / gpu_free_mb / vram_free_mb = 13754      <- 真值（MiB）
gpu_free_vram_gib = 13754                              <- 同一个数，键名说的是 GiB
```

bm-a 的 `gpu_free_vram_gib = 1038` 与它同型。任何按键名换算的读者会看到 bm-a 有 1 TB、bm-c 有 13 TB 空闲显存。`gpu_face.py` 头注记着 r1311 修过同族一个别名（`gpu_vram_free_gb` 进了 `FREE_KEYS` 没进 `GB_KEYS`），而 `gpu_free_vram_gib` 至今没进——**所以这不是手工笔误，是共享写手还在生产这个缺陷**，两台跑过它的机器都中招（bm-b 没有这个键，所以干净）。

### 次要读数

bm-a 的 RAM 侧 18 GB 离散超出任何舍入解释（`ram_free_gb 28.1` / `free_ram_gb 38.0` / `ram_free_mb 45.8` / `free_ram_mb 43.2` GiB，四种读法），谁也说不清哪个是当前值。bm-c 的 cpu 组在删掉重复键后仍分歧（`cpu_pct=37` / `cpu_total_pct=33` 是别的探针按自己的时刻写的），本轮没有代它们改：写者收口不是改一次能治的事，审计就让它继续红。

## 4. 本轮只做测量，不做裁决

- 别名归属与单位修正是**写者/属主**的决定，本面只给证据。
- 唯一例外是本机自己的文件（自己的文件坏了当窗修，别人的不动）：删掉大小写重复键 `CPU_load_pct` 并写实测值；GPU 面改由 `gpu_face.py apply` 重写；ram 四键与百分比键写成同一次实测。修后本机重复键 1 → 0、ram 组 AGREE、GPU 面色带自洽（free 13754 + used 2630 = 16384）。
- 预提交爪本轮**拦下过一次**：手写的 GPU 数（free 13279 / used 2628）与真实探针（free 13754 / used 2630）对不上、19 个别名离散 477 MiB。教训与 r1413 同源——**心跳的 GPU 面不许手写，必须走写手**；改走写手后爪随即放行。

## 5. 续作点

1. **根因在 `Tools/gpu_face.py`**：把 `gpu_free_vram_gib`（以及家族里其余 `*_gib` 键）加进 `GB_KEYS`，或不再产出 `_gib` 别名。此文件是共享面，本轮竞争窗 rc=3 禁改，挂账。
2. 三台各自收口：bm-a 定 RAM 权威别名；bm-b 统一 cpu 与 ram 两组；bm-c 剩 `cpu_pct` / `cpu_total_pct`。
3. 本工具接 S6 链一条腿（零网络零计算，`check` 秒级）当心跳面常规哨兵；须在无竞争窗改 `Tools/s6_chain_bmc.py`。
4. 若舰队要求「心跳必须能被严格读者打开」，可把 `duplicate_case_keys` 与 `unit_mislabels` 提升为 gate——需要集团层定，不在本司单方改。
