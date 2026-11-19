# 期货车道：三张面各印一个日期（r1843，2026-11-19）

正身：`scripts/futures_tail_divergence.py`（selftest 14/14）+ `results/futures_tail_divergence.json`

## 一、读数（2026-11-19 15:2x 实测）

| 面 | 它说的日期 | 它读的盘 |
|---|---|---|
| `results/idx_fut_real_nav.json` | `evidence_cutoff` **2026-11-16** | `data/futures_contracts`（`cr.CONTRACT_DIR`） |
| `results/idx_fut_carry_paper/LEDGER.json` | `contract_cutoff` **2026-11-17** / `evidence_cutoff` 2026-11-18 | 主连收盘 + 上一行的 roll book |
| `results/idx_fut_contract_roll.json` | `evidence_cutoff` **2026-11-18** | 主连 `data/futures_daily/<品种>.csv` |
| `results/idx_fut_desk_sheet.json` | `evidence_cutoff` **2026-11-18** | 本面未声明源头 |

三张面都属于同一本「股指期货贴水」书，没有一张说谎，但它们分别锚在三张盘上。

## 二、盘上真实尾巴

```
data/futures_daily      newest=2026-11-18  files=10  git=10
  IC                    2026-11-17  -1 session   ← 比同级兄弟落后一天
  TF                    2026-11-17  -1 session
data/futures_contracts  newest=2026-11-16  files=418 read=335 live=8 expired=327  git=0
```

两条独立的病，修法完全不同：

1. **合约级面板没有生产者**。它在 `.gitignore:270` 里、`git ls-files` 计数 **0**、全仓没有任何脚本写它（只有 `idx_fut_contract_roll` 与 `idx_fut_carry_risk` 读它）。它最后一次落盘是 2026-11-16 22:30，是一份**手工拉进来的目录**，不是一条慢车道。327 个已到期合约的尾日是它们自己的到期日（第三个周五），属正常；8 个在交易中的合约最新只到 11-16——**交割月最后一周（IC2611 于 2026-11-20 到期）的换月证据在这张盘上根本不存在**。
2. **IC / TF 主连比兄弟慢一天**。IF/IH/IM 已到 11-18，IC/TF 停在 11-17；而这本书的 IC 腿正是用主连收盘 mark 的。

## 三、为什么车道面看不见

`scripts/data_lane_freshness.py` 的 futures 行用 `panel_tail_csv`，取的是**目录里最新那个文件**。于是：

- 合约目录整体冻结 → 被 `data/futures_daily` 的新鲜尾日盖住，印 `in_sync`；
- IC 比兄弟慢一天 → 被 IF/IH/IM 的 11-18 盖住，`missing_days=[]`。

盘上已有的 `panel_tail_csv_full`（r1261，会点名 laggard）没有接在这条车道上。

## 四、钱的意义

`idx_fut_contract_roll` 的挑合约（谁贴水最宽、deepest OI 是哪一张）只能看到 11-16，而它同一天发布的面声称 11-18。**读者按 11-18 的读数下单，用的是 11-16 的合约。** 这不是措辞问题：IC2611 明天 11-20 到期，最后一周的换月在这个盘上是空白。

## 五、下一步（不在本轮越权执行）

1. `data/futures_contracts` 必须有一个**仓内的生产者**（或明确降级为「仅历史快照、不参与当日决策」并在两面印出来）。本轮只做测量，不动别人的车道。
2. IC/TF 主连落后一天属 `update_futures` 的 per-symbol 失败；车道属主 bm-a，本机 `--takeover` 未取（车道护栏，R31）。
3. 把 `panel_tail_csv_full` 接到 futures 行——会改共享面，且 S6 链 r1842 仍在飞，留待链收口后的独占窗。
