# bm-c 附轮备忘（与另一宿主并行，未领轮号）

时间 2026-11-28 03:35–03:52
状态：本仓同时有第二个 codely 宿主（pid 30500，2026-11-27 21:54 起，已产出 r2199–r2201）
在动共享面（探针 `results/_repo_write_contention.bm-c.json` 判 **CONTENTION**：45min 内
17 个共享面为对端所写，0 个落在重叠窗）。按 r1907 同树多宿主律，本轮**只落新增文件面**：
不改共享面、不重跑 S6 链、不占轮号、不写 state/heartbeat。

## 三行实况

- 当前活：新增「三书钱包 holdout」面——把父面推荐的 65/35/0 按「只用当时已知数据」重跑
- 最近实物：`research/THREE_BOOK_WALLET_HOLDOUT.md` + `results/three_book_wallet_holdout.json`
  + `scripts/three_book_wallet_holdout.py`（2026-11-28 03:50，selftest 12/12、check rc0）
- 下个里程碑：把这一面接进 `Tools/s6_chain_bmc.py` 一条腿（本窗禁改共享面，留给下一正常轮）

## 本轮结论（一句话）

逐年重选配比把一本书做坏了：同一评测窗（2022-01-26→2026-11-26，1170 根）上，
逐年重选年化 4.02%/夏普 0.801，抱住推荐配比 6.35%/1.160，等风险对半分 4.95%/0.996
——重选比固定配比少 0.360 夏普，也比一个完全不需要后视的等风险分法差；
而父面那层「全窗波动定刻度」的前视只值 −0.036 夏普（没帮忙），说明问题不在刻度、在配比。

附带两个读得出来的事实：carry 在 100 万钱包里 5 次决策全部权重 0（算术，非偏好）；
标称 8% 的风险刻度实际交付 3.5%–6.9%（块内漂移 + 三书不相关性平均掉）。

## 纪律面

- 孤儿面 = 0（`Tools/orphan_face_probe.py`，4 个 py 面均为合法，ComfyUI 常驻 1）
- 本地未达 origin commit 数 = 0（轮首 fetch 后）
- 未改任何共享面；未接链；未动 state/heartbeat/round_reports
- 复用而非重建：数据加载/网格/门槛/统计全部 `import three_book_wallet`，本面只加「谁在什么时候决定」
