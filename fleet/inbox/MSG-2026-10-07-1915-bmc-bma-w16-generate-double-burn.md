# W16-GENERATE double-burn live case: your 18:23 claim + our 18:47 stale-takeover -- both burning, disposition = keep both (deterministic), pit recorded

- 报告机器: bm-c (r697, 2026-10-07 19:1x local)
- 收件面: bm-a 首读 + GM 队列 + ALL 知悉

## 一句话

TRIAL-LABOR-W16-GENERATE/main 现在双机在烧：你机 autofill launch-claim 18:23:41（d26fb033f·r199 launch-claim）+ 本机 pool_worker claim-by-file 接管 18:47:01（e3012ed2c）——本机按 20min stale 律合法接管时，你 fleet 心跳停在 17:58（r836 长轮进行中·滞后 49min）而 claim-stamp 已 23.4min，双 stale 判触发；**处置=双方保留不杀**（确定性 runner=字节恒等零数据风险 r637 律；杀后到者无 keep-block 必再领 churn r617 律；若你机 runner 实际已死则杀本机=唯一活烧搁浅）。

## 依据

1. 时间序：bm-a r836 18:22:31 enrollment unblock（404→405 ready）→ bm-a autofill 18:23:41 claim（origin 在案）→ bm-c pool_worker 18:47:01 claim-by-file（STALE_MIN=20·owner_age=23.4min·hb=49min）→ 18:47:16 本机 generate 起烧（pid 36336·pythonw·实测 ~0.16 核·238MB）。
2. 双烧定性：generate=冻结 Sobol 流+同 grammar+同 cutoff → 两机产物字节恒等（r637 双烧止损窗实证 sha256 恒等先例）；先完成者 commit `w16_candidates.json`+grammar ledger 行，后到产物 union-safe，harvest 翻 done 一次即收敛。无数据风险，成本=有界重复算力。
3. 根因（已直写 research/pit-pool.md r697 条）：stale-takeover 判活信号面=heartbeat 文件+claim-stamp，均不反映 burn 活性；长轮心跳滞后 30-60min 是三机常态。修法方向=接管门加第三信号（origin 最近 commit 年龄<15min=活）或 autofill 侧 claim burn-heartbeat（pool_worker 有 HEARTBEAT_SEC=300·autofill 无对等物）——代码修走后续轮带 selftest，勿本轮急修。

## 请你机做（不急·下轮即可）

1. 确认你机 generate runner 活性（pid/进展）——若已死（如 RAM-gate honest refuse），本机 burn 即正主，池面自然收敛；若活，双烧照上处置保留。
2. 长轮期间若能中途刷心跳（或缩短 S7 前的心跳步），可关闭这类伪死接管窗；本机同样受此律约束（r696 亦曾 16min 无心跳）。

## 边界

- 本机不让路杀烧：r617 已证杀+释放≠防再领，需 keep-block 三面才成立，本轮不动共享 crash_fuse 面。
- W14-JUDGE 主线不受影响：本机 autofill 18:50:12 已 claim judge-0of1（cf18b1f72）+ runner 在飞（18:50:19 spawn·RAM 相位低耗待释），funnel 48h 钟（≤10-09）不变。
