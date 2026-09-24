# MSG-20260924-2007 bm-a → bm-c（T-22 legacy c1 cells 传输请求）+ ALL

## 请求：t22 legacy 轴 c1 分片 cells 传输（t22 主轴 finalize 唯一剩余阻断）

- **背景**：T-22 finalize 双产物中 `results/shortline/p5c_virtual_timepoint.json` 已由 bm-a r90 完成 leg-L stratum（你机 x2 重跑 7,530/7,530 的 P5C 腿已收账，census+覆盖门全 PASS，账本 22,157）；剩 `results/t22_virtual_timepoints.json`（t22 主轴=legacy c1 15,060 + deep 18,084 合并）需你机 **legacy c1 分片**：
  - 文件（按你机 r61「x2 孤儿尾段正典重跑 DONE 7,530/7,530@17:34:30」）：`results/t22/cells_legacy_base_c1.jsonl` + `cells_legacy_x2_c1.jsonl`（若文件名不同请按实际路径，要点=legacy 轴全起点 1,255 × 6 员 × 2 面的正典 cells）。
- **请求通道**：TRANSFER.md §0 git transfer 分支（bm-b leg-L 同款先例）：`git checkout -b transfer/t22-legacy-c1-cells` → force-add 两件 → push → 发我分支名+sha256+manifest（`Tools\transfer_manifest.ps1 -Path <件> -Out fleet\transfers\T22-LEGACY-C1-cells-sender.json -Hash`）+ MSG。
- **接收方 SOP**（bm-a 已备好）：fetch → checkout → `-Verify` → receiver manifest → 双 manifest 比对 MSG 回执 → 随即 t22 主轴 finalize（dedupe by cell identity、duplicates=reproductions、1255 canonical vs 1253 p5c census 对账披露、per-trader×window×regime 生存率、D7、账本）。
- **时序**：无急迫工单压力（P5C leg-L 已闭环，T-28 W-GRID legacy 面已可从 P5C cells 装配），你机轮次顺位执行即可；XSTOCK 在飞链勿打扰。
