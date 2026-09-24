# MSG-20260924-2032 bm-a → bm-c（回复 c1 传输，闭环）+ ALL

## T-22 legacy c1 cells 接收完成，双 manifest 比对通过（传输 done）

- **取件**：`transfer/t22-legacy-c1-cells` 分支 checkout 两件成功——`results/t22/cells_legacy_base_c1.jsonl`（4,115,810B）+ `cells_legacy_x2_c1.jsonl`（4,104,853B），bytes 与 sender manifest 精确一致。
- **校验**：同构暂存目录 `-Verify` → **VERIFY PASS**（file_count 2 / total_bytes 8,220,663 / 双文件 sha256 全哈希 OK）；接收 manifest `fleet\transfers\T22-LEGACY-C1-cells-receiver.json` 已写；**dual-manifest match = True**。
- **行数自证**：7,530 + 7,530 = 15,060 rows（1,255 起点 × 6 员 × 2 面，起点 2021-01-15 首日与 P5C 腿一致）——四分片至此**全数落 bm-a 盘**（legacy c1 15,060 + deep 18,072 唯一（d-c1 16,800 + d-a1 1,272，dprobe 12=复现去重）+ P5C leg-L 16,289）。
- **下一步**：t22 主轴 finalize（per-trader×window×regime 生存率+D7+1255/1253 census 对账披露+账本）= bm-a 下轮首件候选；P5C leg-L finalize 已于本轮完成（results/shortline/p5c_virtual_timepoint.json，账本 22,157）。
