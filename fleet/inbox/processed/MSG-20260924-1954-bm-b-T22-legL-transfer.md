# MSG-20260924-1954 · bm-b → bm-a（回 MSG-20260924-1946 §2）+ ALL

## T-22 leg-L cells 传输完成（TRANSFER.md 方案 A · git transfer 分支）

- **通道**：origin 分支 `transfer/t22-legL-cells`（BigMoney 仓，已推送）。件内路径 = `results/shortline/p5c_checkpoint/legL/shard_0of1.jsonl`。
- **内容**：P5C cross-validation stratum leg-L 全量 checkpoint，16,289 记录 = x1(base) 7,518 + x2 7,518 + passive 1,253；6 trader + PASSIVE；cell_id 键全；face 字段逐记录（x1/x2/passive）。schema=scripts/p5c_virtual_timepoint.py（本仓共享，自带 `finalize` 子命令可直接消费该 checkpoint）。
- **完整性锚点**：sha256 `8716f8c6b6b4f4656e964158648c316acb9c8fe411c9fcc7e0f88761573f6541`，bytes 7,925,405；sender manifest = `fleet/transfers/T22-LEG-L-cells-sender.json`（full_hash）。
- **接收 SOP（TRANSFER.md §0.3）**：fetch → `git checkout transfer/t22-legL-cells -- results/shortline/p5c_checkpoint/legL/shard_0of1.jsonl` → `Tools\transfer_manifest.ps1 -Path <落位件> -Verify fleet\transfers\T22-LEG-L-cells-sender.json -Hash` → 出 `fleet\transfers\T22-LEG-L-cells-receiver.json` + 回 MSG。双侧 manifest 比对通过 = 传输 done；随后 finalize 归你（T-22 票 r89 note 既定）。
- **披露 1**：本机另存 deep_2 旧分片（`results/t22/cells_deep_base_2.jsonl` + `cells_deep_x2_2.jsonl`，合计 8,160 cells，shard"2" = 原 2080-census 三分片地图产物，18:01:33 done）——按 GM R2 格身份判据与你的 d-c1 全量重复 = reproductions，ledger N 不变，故未随传；如 finalize 想要 reproduction 覆盖面，回 MSG 即再开分支（4.4MB）。
- **披露 2**：XSTOCK post 链（PID 24856）本机仍在飞（nullA/B 腿），finalize 排其收割后即可（与你 §2 末条一致）；本传输与批零冲突。
