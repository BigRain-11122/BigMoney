# DIGEST 2026-11-09 r1479 (bm-c) — 一张票面写着本机看不见的证据日

## 症状
`scripts/etf_book_live_size_provenance.py run` 判 `IDENTITY_FAIL`：
票面 `evidence_cutoff=2026-11-09`，本面重导出的 `names_bar=2026-11-06`（L_bar False）。

## 归因（不是缺陷，是两台机的世界）
`TICKET-2026-11-09.json` 由另一台面板已到 11-09 的机器写出（本机 `data/etf_daily` 面板
末 bar=2026-11-06，`results/etf_daily_pull_status.json` 记 `data_cutoff 2026-11-06`）。
同日 r1480 的修复把票面选择从「按文件名」改为「按证据日」——于是这张本机复现不了的
票面反而赢了排序，面拒绝给任何读数。

## 修法（本轮）
1. `latest_ticket(panel_last)` 增加外部边界：自称证据日晚于本机面板末 bar 的票面进
   `tickets_unverifiable`，从选择集剔除，回退到本机能复现的最新一张。
2. 披露成句：`tickets_unverifiable_sentence`（带面板末 bar 与票面自称日期），`run()`
   打到 stdout；`tickets_superseded_sentence` 同理点名被跳过的「名字更新、证据更旧」表。
3. `--check` 用回执里的 `panel_last_bar` 重导同一选择，新增 4 条腿（跳过清单、句子、
   有跳过必带边界），check 8/8 → 12/12。

## 读数（实树）
verdict `DIFFERENT_BOOK_AND_SIZE`：k_beta 0.460253（β 规则）/ k_vol 0.648195（8% 波动目标书），
gap −18.79pp，票面权重 0.393073，五名 159501/513100/513690/159577/159263。

## 复发防线
任何「最新」选择器的边界必须是外部参照（本机面板末 bar / 官方日历 / 本机产物），
禁信任被选对象自称的日期；被挡下的每一件必须成句披露，且 --check 逐轮重导。

正身：scripts/etf_book_live_size_provenance.py（selftest 28/28）+ 卡 E489。