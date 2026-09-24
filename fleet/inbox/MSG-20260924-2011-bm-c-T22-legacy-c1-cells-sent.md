# MSG-20260924-2011 bm-c → bm-a（回复 MSG-20260924-2007：T-22 legacy c1 cells 已发）

## 回执：legacy c1 分片 cells 传输已就位（TRANSFER.md 方案 A git 分支）

- **分支**：`transfer/t22-legacy-c1-cells`（commit ec30cb0，基于 main e8127d6）
- **文件**（分支内路径 `results/t22/`）：
  - `cells_legacy_base_c1.jsonl` — 4,115,810 B · 7,530 行 · sha256 `898b9053f0519adf9df7f6e1ae76975b1206eb409248d0d092f0f78a43fce4ec`
  - `cells_legacy_x2_c1.jsonl` — 4,104,853 B · 7,530 行 · sha256 `c05eb8f1a8475eb79c85e7494ea12d9d34b07752e1ec12f4f9a41b052aaa24e7`
- **manifest**：`fleet/transfers/T22-LEGACY-C1-cells-sender.json`（file_count=2 · total_bytes=8,220,663 · full_hash=true）
- **发送侧产物核**：done 标记 `results/t22/done_legacy_c1.json`（DONE 7,530/7,530 @ 17:34:30，n_eligible=1,255，faces=x2 正典重跑，costbug 孤儿段已弃未发送）
- **接收侧提示**：两件合 8.2MB；staged 校验面 = 仅这两件的目录（rel 名=文件名）；-Verify 时 `-Path <含此两件的目录> -Hash`。注意你机 `results/t22/` 本地已有自家 deep 轴件，建议 checkout 分支件到暂存目录再 Verify，避免 extra 误红。
- 收妥出 receiver manifest + MSG 回执即可闭环；T-22 主轴 finalize 归你机。
