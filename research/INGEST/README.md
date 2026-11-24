# 金融资料交接（跨机）

CEO 令：**生产力电脑把金融相关资料与文件交给传家宝，整合好。**

## 为什么不能「直接拷过去」

机队没有大文件通道（FleetLink `/sync` 只走 ≤256KB 的仓内件，SMB/WinRM 关闭）。
所以交接分两层，每层都有机器可核的凭据：

| 层 | 内容 | 怎么走 | 凭据 |
|---|---|---|---|
| 入库层 | git 跟踪的文件（脚本/研究页/结果面/文档） | `git push` / `git pull` | `git rev-list` 双零 + 文件 sha256 |
| 车道层 | gitignored 的数据（A股/资金流/龙虎榜/期权/期货合约…） | 重建脚本，或 ≤95MB 分包 | `PACKS.json`（路径+字节+sha256） |

## 工具（两边同一套，差异才可算）

```bash
# 任何一台机：清点自己的金融资料
python scripts/ingest_inventory.py --hash
#   产出 research/INGEST/INVENTORY-<机名>-<日期>.{json,md}

# 收到对方的清单后：算差异
python scripts/ingest_diff.py research/INGEST/INVENTORY-<对方机名>-<日期>.json
#   产出 research/INGEST/DIFF-latest.{json,md}
#   verdict=COMPLETE 才算交接完整；GAPS_FOUND 会列出缺哪些、哪条车道更新
```

## 清单里有什么

- `repo`：git 跟踪的每个文件（大小/mtime/[sha256]）、分支、领先/落后、未提交件、stash。
- `lanes`：每条数据车道的文件数/体量/最新 bar/修改时间，并标注 **git 搬不动**。
- `config_pointers`：配置与凭证文件的**路径**（不含内容——凭证永远不过机）。
- `research_surfaces`：研究页/结果面/试验格的计数。

## 交接规则（硬）

1. 凭证/密钥**只给路径**，内容一律不过机。
2. 单文件 >95MB 禁入 git；车道要么给重建命令，要么按 ≤95MB 分包。
3. 分包必须带 `PACKS.json`：每包 `{path, bytes, sha256, covers:[起,止]}`。
4. 收到包后，本机跑 `ingest_diff` 复核；`COMPLETE` 才在回执里写「已整合」。
5. 不删对方任何文件；不覆盖本机已有且更新的文件（差异先报，后决定）。

## 目录

```
research/INGEST/
  INVENTORY-<machine>-<date>.json/.md   谁的清单
  DIFF-latest.json/.md                  最近一次差异
  PACKS/<date>/                         收到的分包（≤95MB/包）
  PACKS.json                            分包索引（含 sha256）
  RECEIPT-<date>.md                     整合回执
```
