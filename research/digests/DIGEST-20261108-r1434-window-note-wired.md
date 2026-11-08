# DIGEST · r1434 · 探针读数印到红灯旁边（bm-c）

## 起点

r1433 量出「years_for_half 中位 2 vs 线 3」不是窗的产物（五个窗起点：3 fail / 2 undecidable / 0 pass），
按纪律不动生产判据。桌面因此有一个信息盲区：操作员在阶梯板看到红字，看不到「这条红字是不是
换个窗就消失」。

## 本轮做了什么（只印不改）

- `scripts/supply_calendar_face.py`
  - 新 `window_sensitivity(elected, root, path)`：读 `results/etf_book_window_sensitivity.json`，
    按**选举出来的尺子**取每个窗的 adjudication 块（不写死 `years_for_half`；无选举→不印句子；
    收据缺席→`block=None, error="absent"`）。
  - 新 `classify_windows()` / `window_sentence()`：判词完全由各窗状态派生（does_not_heal /
    heals / partly_heals / fails_where_it_can_be_judged / ruler_not_on_record …）。
  - `build()` 输出 `window_sensitivity` + `window_sensitivity_error`；`summary_line()` 追加该句；
    `write_md()` 追加「这个拒法换个大点的窗还在吗」小节与五窗表。
  - `check_published()` 整块重 derive 并逐键比对 → 手改发布面即红。
  - selftest 39 → 49/49。
- `Tools/fill_ladder.py`：`_calendar_block()` 透传 `window_sensitivity` 句子，`_explain_line()`
  印在 reason 之后；selftest 加两腿（有注记必须出现、无注记不得出现 `window:`）。

## 实读（发布面）

```
window: years_for_half median 2/3 vs line 3, 3 fail/2 undecidable/0 pass over 5 starts
-> a wider window changes nothing where it can be judged
(widest start 2013-01-01 cagr 8.060% maxdd -16.850%; plain arm only, exploratory -- decides nothing)
```

判决词不变：`NO_CANDIDATE_PASSES_CALENDAR`（4 候选 4 拒），阶梯板 `EXHAUSTED_NO_LAWFUL_SUPPLY`。

## 为什么不是「又一张卡」

一个探索读数如果回答的是操作员面对当前红灯时的下一个疑问，它就该出现在那个红灯的同一行；
否则「我量过了」只对量的人成立。同一条纪律的下半句：印这一步同样不许手写尺子名——
窗收据里四把尺子都有裁定块，写死一把就是把 r1429 的选举抄成常量。

## 验证

- `python scripts/supply_calendar_face.py --selftest` → 49/49 PASS
- `python scripts/supply_calendar_face.py --check` → OK (NO_CANDIDATE_PASSES_CALENDAR)
- `python Tools/fill_ladder.py selftest` → all assertions PASS
- `python Tools/fill_ladder.py explain` → 板面含 reason + window 两句
- `python Tools/card_text_hygiene.py scan` → 480 files, 0 control chars, 0 eaten prefixes

## 下轮

「日历该问哪个问题」的采纳轮证据包（r1428 ETA + r1433 窗敏感性 + 本轮操作面接线）备齐待 GM 署名；
禁在本轮口径上再找旋钮。