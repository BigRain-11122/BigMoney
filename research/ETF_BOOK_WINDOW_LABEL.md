# 表头写「全窗」，格子里是 2.8 年

证据面：`results/etf_book_window_label.json` ｜ 定价截止 2026-10-30

## 研究

**ROW_LABELED_BY_WINDOW**

- the value under the 全窗 header is the 2.82-year window; the same book over the full window reads 7.71%, i.e. +5.07 pp/yr and the header is not what the cell holds

## 同一本书的两个窗口（你手上这一本：5 名·beta 0.20·8bp）

| 窗口 | 年化 | 夏普 | 最大回撤 | bars |
|---|---|---|---|---|
| 页面今天印在「全窗年化」下 | 12.78% | 1.73 | -5.78% | 683 |
| 2020-2023 年（同一把尺子） | 3.71% | 0.90 | -3.97% | 842 |
| 同一本书从 2020 起（真全窗） | 7.71% | 1.34 | -5.78% | 1525 |
- 2020-2023 段（同一把尺子）：**3.71%**（842 bars），三段 bars 842+683=1525 恰好拼满全窗 （容差±1 bar）。

- 两个格子的差 = **+5.07 pp/年**，就是 r1214 量到的「起点」旋钮：它不是策略变了，是同一本书换了起跑线。

## 身份门

- the full-window cell's own window reproduces the ticket：实测 12.78% / 发表 12.78% / 差 0.0 pp -> PASS

## 页面该怎么印

- 全窗年化 = **7.71%**（1525 bars），2024 起 = **12.78%**（683 bars）。

## 冻结（跑之前写的）

ROW_LABELED_BY_WINDOW iff the value under the 全窗 header and the same book's full-window cell differ by >= tol_pp_per_year; SAME_WINDOW if they do not. IDENTITY_FAILED refuses every printed row when the cell that supplies the full window no longer reproduces the ticket's own published number.

容差：0.25 pp/年；身份门：0.125 pp。

数据：`results/etf_book_window_label.json::rows`。
