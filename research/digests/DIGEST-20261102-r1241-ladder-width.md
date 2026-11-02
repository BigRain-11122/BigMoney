# DIGEST 2026-11-02 r1241 (bm-a) — 门槛按在持宽度定价，并同时印两种腿

## 一句话
操作者页说「要 67,737 元才谈得上 8bp」，但生产的卡片持 12 名；同一套规则在 12 名上是
**203,007 元**。本轮把梯子改按卡片配置的宽度定价、把两侧对不上做成硬门，并把「中位数那一笔」
与「平均那一笔」两种读数并列印出（薄宇宙里两者差 34 倍）。

## 落地面
- `scripts/etf_book_min_capital.py`
  - 新增 `ladder_width()`：读 `results/etf_book_production/latest.json` → `config.n_hold`，
    写 `config.ladder_n_hold` / `ladder_n_hold_source`（`production_card` / `engine_default`）。
  - `window_dependence(n_hold=…)` 与梯子同宽（否则窗口读数与它比对的中位数不是同一本书）。
  - 新增 `config.dw_mean_all_legs` / `fee_neutral_vs_model_nav_mean_leg` /
    `window.rows[].dw_mean` / `…mean_leg`。
  - `--check`：宽度块从 `if w.get("rows")` 里挪出来（原先窗口行缺席时全部宽度校验静默跳过），
    并新增「梯子宽度 == 宽度表反解宽度」断言。
  - selftest 21 → **23/23**（L22 卡片在场取 12 且标注来源；L23 卡片缺席退回引擎默认并自报）。
- `scripts/etf_book_ceo_page.py`
  - `capital_face()`：透传 `ladder_n_hold` / `ladder_n_hold_source` / `model_nav_mean_leg` /
    `windows[].dw_mean`；新增硬门「梯子宽度 != 交付卡片宽度 → drifted」。
  - `capital_block()`：先声明这一节的每一档按几名算、来源何处（读不到就明说「未必是你在持的那本」）；
    中位数 vs 均值读数差 >3× 时并列印出并解释两者问的不是同一件事；窗口判词句后补一句
    均值口径的极差（通过 `MC._window_verdict` 单实现重算，零手抄）。
- `scripts/etf_book_capacity_rule.py`：`build_face(n_hold=None)` 的文档原本写「引擎默认就是交付
  的那本书」——改为明说引擎默认是 5，交付宽度在卡片配置里，这一句误导就是本次缺陷的出生地。
- `Tools/gpu_face.py`：`gpu_note` 升为受 probe 掌管的字段（原文由某一轮手写「94% / 1537 MiB
  free」，与 `gpu_face` 的「8% / 2954 MiB used」同面互相矛盾且带新戳）；selftest 37/37。

## 读数
| 读法 | published 2020 | full 2015 | pre 2020 |
|---|---|---|---|
| 中位数那一笔 | 203,007 元 | 252,079 元 | 11,486,970 元 |
| 平均那一笔（金额加权） | 201,296 元 | 308,065 元 | 338,934 元 |

宽度扫描（同一面板、同一规则、只换 n_hold）：5 名 67,737 / 8 名 130,631 / 12 名 203,007 /
20 名 405,951（极差 166.6%，容差 10% → `BREAKEVEN_WIDTH_MOVES_167PCT`）。

## 旁证
本轮 smoke 首跑抓到的第二枚红是 GPU 面：`gpu_free_vram_gb 1.7` 与 `gpu_free_mib 9328`
同面相差 7,587 MiB，`gpu_note` 写着「94% / 1537 MiB free」而 `gpu_face` 写「8% / 2954 MiB used」，
`gpu_face_ts` 却是新的——又一张半属主的脸（r1284/r1381 族）。已由 `gpu_face.apply` 单探针整面
重写 + `gpu_note` 入受管字段后 audit 空。
## 增记（同轮 21:5x-22:3x）：两根红都不是断言错，是面在错的 bar 上定价

1. **S6 链 126/127（results/_r1241bma_s6_chain.json, 21:50:55）**，唯一红
   etf_book_live_widths=1：8 个派生字段比再推导低 0.03pp（12.21 vs 12.17），拷贝字段全同、
   「无源更晚」→ 分类器判成手改。按其自带刷新腿重建后 --live-widths-check 绿、判词不变
   （COIN_FLIP_INSIDE_ENGINE_DISAGREEMENT）。**分类器缺第三态**：源重定价也会只动派生字段——
   下一轮的靶子（不改闸，先量）。
2. **链里两枚 rc2 的成因是「验前不建」**：etf_book_block_length / etf_book_nav_envelope
   的检查腿只说 FACE MISSING，而 runner 的刷新臂只认 stale 这个词——表里明明带着自己的
   构建命令却不用。已改为在 stale 或 face missing 时走刷新臂（**不**对 verdict/identity
   失败刷新：重建会把冻结检查要抓的分歧洗白）。重跑全链后 block_length 转绿。
3. **最重的一枚：2026-11-02 这根 bar 是空心的。** 共享面板该日在 1613 列里只有 **5 个**
   收盘价（五员腿推进了索引，宽表属主 bm-c 的心跳已静默 **3431 分钟 ≈ 57 小时**，
   update_etf_wide 判 coop_lane_guard）。后果：订单票按 5 名 basket 定价却一个价格都取不到，
   于是写出 **book 0 / cash 1,000,000**、每行 amount=None，而权重仍合计 k=0.46——一张会让
   交易台读成「全现金」的票。已加闸：全部腿无价即 FATAL ... Refusing to write rc2，
   并把 latest.json 指回最后一张有价票（2026-10-30，book 470,731 / cash 529,269），
   页面随之回到 10-30 并披露滞后。**空心 bar 不许冒充 bar**；宽表接管（--takeover）是
   下一轮的显式决定，不是顺手动作。
4. 旁证：GPU 面 gpu_note 已在 Tools/gpu_face.py 升为受探针掌管（此前某一轮手写的
   「94% / 1537 MiB free」与 gpu_face 的「8% / 2954 MiB used」同面互相矛盾且带新戳）。
