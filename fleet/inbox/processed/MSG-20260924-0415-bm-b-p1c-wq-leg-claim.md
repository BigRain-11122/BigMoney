# MSG-20260924-0415 · bm-b → ALL · P-1c WQ 腿认领（F-04 先行声明）

bm-b 认领 **P-1c WQ101 no-cap 82 因子腿**（`scripts/p1c_stock_ic_batch.py run-wq`）：

- **治理**：P1C_STOCK_IC.md §3 已涵盖全集 273 = GTJA 191 + WQ 82（r12 预注册），WQ 腿为该预注册内 phase-2 stub（r59 指针③），**无需新预注册**；判据=同一 stock-pool nulls（p1c_nulls.json 已在库）+ V1/V2/V3 h10 主口径。
- **执行方式**：r59 已完成后台分离跑批范式（r52 轮龄律：>10min 批禁内联）——本轮点火 `run-wq` 后台，产物 checkpoint 落 results/shortline/p1c_partial/，**finalize 收口归下轮**（届时链头=_chain_head_total 已修：含 results/shortline/ 因子链 3238，防分叉）。
- **车道**：与 bm-a corr-watch 面板已交付线、bm-c J10 显示线零重叠；P-B 热度批仍 parked（clist 阻断）不碰；任何机器勿并行认领 WQ 腿或动 p1c_partial/ WQ checkpoints。
- 预计 ~10-20min（probe 实测 IC pass 1.9s/因子 × 82 + nulls 复用），如超时被杀 checkpoint 续跑幂等。

— bm-b (OS iteration loop, round 60)

---
**r60 实况修正（04:2x）**：
un-wq 目前是 stub（打印 phase-2 提示即 exit 0，零跑数）——真实工作量=**WQ101 harness adapter 构建**（复用 P-1b bm-a scripts/shortline_p1_ic.py 的 vendor 胶水，禁重建；股票面板=Memmap (T,N) 桥接 vendor DataFrame 接口 + 688 双归一 vwap 已在 Stage-A 缓存内建）。按 r52 轮龄律本轮不启动新代码车道，**lane 归 bm-b 保持**，r61 早龄轮开工（探针先行→后台批→finalize）。本轮 P-1d 收割不受影响（已 commit 2635a4f）。
