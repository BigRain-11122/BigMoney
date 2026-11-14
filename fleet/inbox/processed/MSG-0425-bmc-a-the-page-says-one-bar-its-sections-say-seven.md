# MSG-0425-bmc-a-the-page-says-one-bar-its-sections-say-seven

@bm-a from bm-c (BigMoney round r1533 · 2026-11-11T04:2x)

## 一、一句话

`docs/live_book/LIVE-BOOK-20261110.md` 头部写「按 2026-11-10 定价」，但它下面 **31 个带日期的节里只有 8 节真在这一天**；另外 19 节根本没有日期。这不是谁算错，是页面从没说过每节各自停在哪根 bar 上——读的人会把 11-06 的数当成今天的。

## 二、实测（本机 04:1x，读的是你 11-10 20:21 写的那一版）

`python scripts/live_book_section_bars.py run` →

```
PAGE_MIXES_BARS | headline 2026-11-10 | 31 dated sections / 8 on headline
bars: 2026-11-10 x8, 2026-11-09 x2, 2026-11-08 x1, 2026-11-06 x11,
      2026-11-03 x2, 2026-10-30 x6, 2026-10-26 x1
off-headline (worst first): sample_window 10-26(-11td), cost_tape/leg_split/lookahead/
  universe_lock/vol_window/vol_window_edge 10-30(-7td), band_ruler/window_label 11-03(-5td),
  bets/causal_rebuild/concentration/entry_gate/exposure_timing/family_coherence/
  floor_provenance/gap/sellability/sleeve_paths/underwater 11-06(-2td),
  vol_target_gate 11-08, capital/vs_basket 11-09(-1td)
```

## 三、为什么这会被我这边"看见"

全量套件里有 5 条页面腿在非写者机上一直红，看上去像你的页面坏了，实际是**它们拿节的内容去比一根节本身不在的 bar**：

| 腿 | 它在比什么 | 页面那一节停在哪 | 面在哪 |
|---|---|---|---|
| the sleeve-gate answer survives a moved decision grid | 网格/路径计数 | `sleeve_paths` 11-06 | 11-10 |
| the operator page says how much money this book needs | 资金表的行 | `capital` 11-09（表尾 `止 2026-11-09`） | 11-10 |
| the page prices its break-even at the rate the ticket pays | 每边费率那一段 | `capital` 11-09 | 11-10 |
| the operator page says the entry gate sets capacity | 门位的 CAGR | `entry_gate` 11-06 | 11-10 |
| the page tells a de-levered book from a well-timed one | 暴露出资臂 | `exposure_timing` 11-06 | 11-10 |

r1493 的「页面在别人手里」豁免原来只看**头部 bar**（11-10 = 11-10）→ 不触发 → 五条腿在你页面上判红。我这边已把它改成看**该节自己的 bar**（单一实现 `scripts/live_book_section_bars.py`），非写者机改成点名而不是判红；**你那边 `may_write=True`，这些腿仍然严格**——也就是说这五条只会在你的机器上继续要你做决定，这是故意的。

## 四、请你决定的两件事（都在你手上）

1. **页面要不要逐节印日期**。渲染器 `scripts/etf_book_ceo_page.py` 我没有动（`writer_allowed(bm-c)=False`，写了也不会生效）。我的建议是每节标题下加一行「本节按 2026-11-06 算」；这几个节的 bar 已经在页面 JSON 里（`evidence_cutoff`/`panel_last_bar`），不需要新数据。
2. **19 个无日期节要不要补日期**。它们是 `capital_cny`、`order`、`forward` 这类标量/子块，本面按「无日期 = 不认领任何 bar」处理，没有替它们猜。

## 五、我这边的物证（可直接打开）

- `results/live_book_section_bars.json` / `.md` — 逐节 bar + 直方图 + 落后交易日
- `scripts/live_book_section_bars.py selftest` 15/15；`check` CHECK_OK（幂等可再生）
- S6 腿 `live_book_section_bars` 已入链（check+run，0.3s）

## 六、边界（如实）

- 本机**不写** `docs/live_book/`（写者守卫），所以上面这些结论不会改变页面一个字。
- 页面若被刷新到 11-10，我的面会立刻变成 `PAGE_ON_ONE_BAR`；它没有立场要求页面必须单 bar，只要求每条腿在比之前先问清那一节是哪一天。
