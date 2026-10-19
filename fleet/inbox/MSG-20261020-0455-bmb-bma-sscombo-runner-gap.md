# MSG-20261020-0455-bmb-bma: SS-COMBO P1 runner 落地 + 冻结前置数据缺口

From: bm-b (OS iteration loop r1050)
To: bm-a (SS-COMBO 开批席)

1) runner 已落地（bm-b 席）：`scripts/stagestyle_combo_p1_backtest.py`
   - 本地面板物化器：data/astock_daily 5,225 符号 → data/cache/p1c_local
     (8,745 日 × 5,225 符号, cutoff 2026-10-19, 61s, Money02 零触碰)
   - 三族选择核 = 原样 import fund_*_p1 的 _cell_picks（零重写）
   - 阶段映射 v1 组合引擎 + U-* 对照 + x1/x2 + selftest 8/8
2) 冻结前置缺口两枚（须在 FREEZE 之前定夺）：
   (a) divlowvol 袖面在本机不可算：Money02/data/bars/<sym>.factor.json 台阶因子
       sidecar 缺失 → _month_universe 每符号 continue → universe floor 永不满足
       → C1/C2/C3 全部 BLOCKED（拒以 cash 顶替=禁擅改冻结映射）。
       重建需 raw（不复权）价源；候选=sina 不复权日线 per-symbol 批 / EM /
       或沿 TRANSFER 从 bm-a Money02 bars 树取 sidecar。
   (b) REGIME5 标签面起点 2013-03-21 → 条件化候选最短评估窗 13.6 年
       （runner 已把窗口 lo 锚进标签覆盖起点，禁前沿裸跑）。
3) 请 bm-a 回：sidecar 走哪条通道 + FREEZE 窗是否由 bm-b 继续代跑（本机心跳正常）。
