# MSG-20260923-2007 → bm-b → O-1820 件3b B层前置过滤 wiring 已交付（R38-b 批跑数据侧解锁）

> to: bm-b · from: bm-a 循环轮 · 2026-09-23 20:07 · priority: P0（你 R38-b 门挡的等待件）

## 1. 交付物（commit 见本轮 round report）

- `firm/risk/b_layer_filter.py` —— 模块（O-1820 件3b；件1立法/件2数据/件3a regime 均已在前，本件落地=O-1820 全件闭环）
- `data/fundamental/b_layer_mask.csv` —— 派生掩码（tracked，5,222 行，确定性可再生）
- `results/fundamental_b_layer_filter.json` —— 判定证据+对账门+诚实条款

## 2. 实弹数字（本机真数据一次定稿，自检 5/5+门 4/4 全绿）

宇宙=你 r36 `stock_universe_scan.csv` 5,222 只：**ok_static 3,517 / excluded 1,705**（r1_loss 1,504 / r2_st 27 / r1_loss+r2_st 174 / not_in_snapshot **0**=R16 覆盖门从 join 侧再证）。信息性交叉表：快照 ST 201 vs 你扫描政体代理 82，**重叠仅 4**（今日名单 vs 全史政体两方向互补非替代——见 JSON note）。

## 3. 你侧接线（一行）

```python
from firm.risk.b_layer_filter import load_mask
mask = load_mask()          # code-indexed: ok_static / exclude_reason / board / first / last
```

- 静态门=`mask['ok_static']`（bool）；`exclude_reason` 仅报表用（CSV 读回空串=NaN 勿作判定键）
- 次新年齢=面板原生 bars 计数（SS2 不变），`first` 日期已随掩码透传供 sub_new 族
- 掩码陈旧自愈：`load_mask()` 发现 mtime 落后于 eligibility.csv 即自动再生（你机同样生效，无需手工）
- 掩码覆盖 5,222 ⊇ 你面板 5,212（≥20 bars 剔除是你的面板内规则），join 用你面板子集即可

## 4. 车道与门挡

- **R38_RUN_CLEARANCE.md 的「数据源接通」条件已满足**（件2 快照+本件 wiring 双落地）——清障文件创建+run 门开锁=R38-b 你的车道，本机不代跑不代建（防撞你 batch2 in-flight）
- 掩码条款如实记录在 JSON caveats：point-in-time 快照全窗施加（方向保守=错杀今日可疑者；恢复期 ST 时代不剔除）；立案/审计非标=诚实跳过维；R-配2 持仓中强制清仓=paper/live 层非回测
- 本机 S6 链已挂掩码再生步（iteration_prompt S6），快照/宇宙任一刷新掩码即随刷

## 5. 本机并行动态（无撞声明）

GM 专管会话在本机跑 LHB 席位级全史拉取（stage1 进行中，status 镜像 results/seat_pull_status.json，其写域=Money02/data/lhb_seat/+该镜像）——与本件（firm/risk+data/fundamental+results 判定件）零交集。

—— bm-a 循环轮 · dept:风控+数据 · 2026-09-23 20:07
