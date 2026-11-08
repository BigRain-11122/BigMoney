# DIGEST r1435 — 这「2 年」是哪两年

**一句话**：供给梯板上被读了三十九轮的 `years_for_half median 2 vs line 3` 从来没说过「前置」；
拆开后主年在三本书里全是 **2025**（7 年表里最新一个完整年），一半净额由一年单独供给。

## 触发

- 供给地板 `ready 0 < floor 3` 连续三十九轮红（`compute_audit` agenda_cause=calendar）。
- 拒因句子：`nobond_vt08_adopted refused at years_for_half median 2 vs line 3 (FAIL)`。
- 桌面读法（r1429/r1432/r1433 笔记）：front-loading / 钱早就赚完 / 该换书。

## 机制

`etf_book_year_caliber.calibers` 把各年净值**降序**累加到一半——排序抹掉年份信息。
它量集中度，不量先后。本轮把 `years_for_half` 拆成 `members`（按日历顺序）、
`direction`（位置阈值：`one_year`/`early`/`late`/`interleaved`，冻结在 `RULE`）、
`dominant_year` 及其占净额比例、残年标注。

## 读数（3 书 × 5 相位 = 15 格，引擎与尺子全部 import）

| 书 | 方向（众数/相位） | 一半由谁供给 | 主年占净额 |
|---|---|---|---|
| nobond_vt08_adopted | one_year 2/5 | 2025 单年 +43.06pp（净额 +81.06pp） | 53.1% |
| nobond_base | interleaved 4/5 | 2020 +22.19pp 与 2025 +53.73pp | 48.8% |
| nobond_vt08_floor_050 | one_year 2/5 | 2025 单年 +42.65pp（净额 +84.99pp） | 50.2% |

- `early` 15 格 0 次 → 桌面对「前置」的用法无一处成立。
- 集中度在**末尾**（2025 是第 6 行，2026 是残年）→「钱花完了」方向反了。
- 真正的问题是「单年异常值能不能复现」，处置与「换书」相反。

## 交付

- `scripts/etf_book_half_year_provenance.py`（selftest 15/15 · check 0 problem）
- `results/etf_book_half_year_provenance.json`（evidence_cutoff 2026-11-06）
- `research/ETF_BOOK_HALF_YEAR_PROVENANCE.md`
- 卡 `knowledge/METHODOLOGY_ASSETS.md` E441
- 接线：`supply_calendar_face.half_year()`（自检 49→58/58）→ `summary_line`/`write_md` →
  `Tools/fill_ladder.py` 阶梯板 `half_year:` 行（selftest 加两腿）→ S6 腿 `half_year_provenance`
  （纯 JSON check，排在 `supply_calendar` 之前）

## 判决未动

4 候选 4 拒 → `NO_CANDIDATE_PASSES_CALENDAR` / `EXHAUSTED_NO_LAWFUL_SUPPLY` 不变。
只换解释，不换判据（r1431 A2）。

## 自踩

首版 `provenance` 从全精度年行算、`check` 从发布年表（6 位）重算 → 8 格在第六位小数炸。
正法：provenance 也从发布表算（不能自我复现的回执＝没人能审计的回执）。

另：本轮方法论卡首版用 PS 双引号 here-string 追加，反引号被 PowerShell 当转义符吃掉
（`` `n ``→换行、`` `e ``→ESC、`` `y ``→无），已整段回退后用 write_file 落文本文件再拼接重写；
`card_text_hygiene scan` 481 文件 0 控制字符 0 吃前缀。