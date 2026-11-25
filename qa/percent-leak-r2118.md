# QA — 读者眼里的 `%%`（r2118 / bm-c / 2026-11-26）

## 为什么这一轮做这件事

r2111 立了 `Tools/page_fmt_guard.py` 静态闸，全仓查出 31 处字面 `%%`，但**只报告不修**：
那 31 处散在他人脚本面，修法需要独占窗。本轮（竞争探针 rc0 CLEAN，单宿主）
把「读者真的会看到两个百分号」的那些行改掉。

判据很硬：`L.append("…1%% ADV…")` 这种**没有经过 `%` 格式化**的字符串，
`%%` 不会被折叠成一个 `%`，而是原样印到 `.md` 上。读者看到的是 `1%% ADV`。

## 改了哪些（18 处，其中 16 处是页面文字、2 处是更严重的）

脚本源码（16 处真泄漏，逐处锚唯一上下文、断言恰好命中 1 次后才写）：

| 文件 | 行 | 修前 | 修后 |
|---|---|---|---|
| `scripts/_r1684bmc_closeout.py` | 86 | `CAGR 11.55%% / 1M impact 0.85%%` | 单 `%` |
| `scripts/astock_veto_hedgeable_beta.py` | 479, 481 | `0/2/5 %%/yr`、`excess over 0%%` | 单 `%` |
| `scripts/defensive_ruler_decision_impact.py` | 329 | `带 8%% 波动目标` | `8%` |
| `scripts/etf_book_cap_beta_power.py` | 399 | `相对 20%% 帽` | `20%` |
| `scripts/etf_book_capacity_floor_gap.py` | 328 | `1%% ADV … maxdd @5%%`（5 处） | 单 `%` |
| `scripts/etf_book_entry_lag.py` | 243 | `整本 + 8%% 波动目标` | `8%` |
| `scripts/etf_book_era_capacity.py` | 265 | `no 1%%-of-ADV line` | `1%` |
| `scripts/etf_book_lot_ladder.py` | 377 | `71%% 的钱留在现金里` | `71%` |
| `scripts/etf_book_open_slicing.py` | 468 | `same 8%% vol-target sizing` | `8%` |
| `scripts/etf_book_phase_atlas_arms.py` | 2829 | `引擎按 8%% 波动目标` | `8%` |
| `scripts/idx_fut_carry_capital.py` | 406 | `净 %%/yr`（3 处） | `%/yr` |
| `scripts/idx_fut_carry_impact_decay.py` | 458 | `占 ADV%%/日` | `ADV%/日` |
| `scripts/idx_fut_roll_gap.py` | 498 | `sum %%/yr` | `%/yr` |
| `scripts/policy_return_lattice.py` | 375 | `3.5%%`、`6.0%%` | 单 `%` |
| `scripts/money_band_blind_spot.py` | 397 | `its own 1.00%% band` | `1.00%` |

发布页面同步（页面是脚本产物，脚本修了但页面不会自己变）：

`research/` 下 13 个页面共 16 行 → 全部改为单 `%`：
`ETF_BOOK_CAPACITY_FLOOR_GAP.md`(5) / `HANDOVER.md`(4) / `IDX_FUT_BASIS_VERDICT.md`(3) /
`IDX_FUT_CARRY_IMPACT_DECAY.md`(2) / `POLICY_RETURN_LADDER.md`(2) / 以及
`ASTOCK_VETO_HEDGEABLE_BETA` `DEFENSIVE-RULER-DECISION-IMPACT` `ETF_BOOK_CAP_BETA_POWER`
`ETF_BOOK_ENTRY_LAG` `ETF_BOOK_LOT_LADDER` `ETF_BOOK_OPEN_SLICING`
`ETF_BOOK_PHASE_ATLAS_ARMS` `IDX_FUT_ROLL_GAP` 各 1 行。

`HANDOVER.md` 的三行是历史轮记录里的笔误（`cpu 26.0%%`、`RAM 98.9%%`、`i%%4 路由`），
改的是文字不改事实；如实记在这里，方便将来有人问「历史台账为什么被动过」。

## 两处比「印错字」更严重的

1. **`scripts/astock_veto_liquidity_legs.py:414` 是一个确定性崩溃**
   整串被 `% _pct(d26)` 应用，而串里写着 `−0.3983%`（单个 `%`，后面跟全角分号）。
   Python 当场抛 `ValueError: unsupported format character '?' (0xff1b) at index 62`。
   实测复现（本轮跑过）：

   ```
   >>> ('…连乘口径 −0.3983%；本面两条腿的年度总额差 %s…' % '-0.40pp')
   ValueError: unsupported format character '?' (0xff1b) at index 62
   ```

   说明那个分支**从来没有被跑到过**——页面上的那句话不是这条代码产出的。
   改 `%%` 后同一表达正常格式化（已复验）。

2. **`scripts/idx_fut_carry_portfolio.py:100`** 是 prereg 判据文本里的 `20%%`，
   该串没有被格式化，会原样进发布面。

## 剩下的 25 条为什么不动

复扫 `results/page_fmt_guard.scan.json`：`LITERAL_DOUBLE_PCT 37→20`、
`BARE_PCT_IN_FORMAT 5→4`、`SYNTAX_ERROR 1`（不变）。

剩下的 20 条逐条看过，没有一条是「读者会看到的双百分号」：

- **检测器自身**（12 条）：`capital_placement.py:592` 的 `if "%%" in s`、
  `cash_leg_shelf_decision.py:604/606`、`cash_shelf_total_return_audit.py:821`、
  `etf_book_capacity_ticket.py:316`、`etf_book_ticket_band.py:368`、
  `etf_book_hysteresis.py:580`、`money_subband_jump_audit.py:1135/1136`、
  `reader_text_audit.py:114`、`ticket_open_capacity.py:604`、`daily_report.py:2266`（assert）
  ——它们的工作就是**发现** `%%`，自身必然含这两个字符。
- **对端 v2 闸的 fixture/文档**（6 条）：`Tools/page_fmt_guard_v2.py` 的
  `_NON_PAGE` 样例、`S_DETECTOR/S_TEMPLATE` 的规则说明文字、`corpus` 样例。
- **`%.1f%%` 格式串片段**（1 条）：`idx_fut_carry_drawdown_experience.py:468`，
  该串会被 `%` 应用，`%%` 折叠成 `%` 是**正确**写法。
- **`head % primary`**（1 条）：`regime_cap_breach_cash_vs_repo.py:483` 同理，正确写法。

4 条 `BARE_PCT_IN_FORMAT` 里有三条是**误报**（它们确实被 `%` 应用，`%%` 是正确转义）：
`a158_tsgate_probe.py:624`、`mp1_tsgate_probe.py:704`（`%(gen)s` dict 格式化）、
`astock_veto_lot_drag.py:457`（`≥95%%` + `%s` + `%.1f%%` 全被 `%` 应用）、
`futures_tsmom_signal.py:710`（`%(same)s` dict 格式化）。
第四条（`astock_veto_liquidity_legs.py`）就是上面那个真崩溃，已修。

**闸的精度欠账照旧挂着**：`page_fmt_guard` 还不能区分「写入器实参」与「检测器/断言文本」，
20 条里 19 条是这个原因。接进链之前必须先把这个精度提上来，否则链腿天天红在噪声上
（r1789「永久红会训练读者把真缺陷当背景噪声」）。

## 验证

```
$ python Tools/page_fmt_guard.py scan --json results/page_fmt_guard.scan.json
counts {'LITERAL_DOUBLE_PCT': 20, 'BARE_PCT_IN_FORMAT': 4, 'SYNTAX_ERROR': 1,
        'literal_in_writer_call': 4, 'literal_in_container': 16, 'total': 25}
verdict PAGE_FMT_HAZARDS     (修前：37 / 5 / 1 / total 43)
```

```
$ python -c "…glob research/*.md + docs/**/*.md, count('%%')"
LEAK_TOTAL 3  FILES 3        (修前：16 / 13)
```

剩下 3 处全部是「描述 `%%` 这个现象本身」的说明性文字：
`research/pit-protocol-lane.md`（坑律：字面 % 混 %-format 崩）、
`research/pit-engine-freeze-editor.md`、`research/PAGE_FMT_GUARD_V2.md`（v2 闸的规则文档）。

全部 17 个改过的脚本 `py_compile` 通过。其中 `scripts/_r1684bmc_closeout.py` 被
`.gitignore` 的 `_r[0-9]*` 规则忽略（历史收口脚本，本地件不入库），
所以入库的是 **16 个脚本**，它在本地一并改掉、不会因为重跑把 `%%` 写回心跳。

## 没做的（如实）

- **没有重跑那 13 个页面的生成脚本**——页面是直接按行改的，脚本也改了，
  所以下一次重跑不会把 `%%` 带回来；但「改过的手改行」与「重跑产物」还没有逐字节对过一次。
  这是下一窗第一件事：重跑一遍，确认 `git diff` 里那 16 行不再出现。
- **闸没有接进 `Tools/s6_chain_bmc.py` 与 `smoke_test.py`**（需要先提精度，见上）。
- **`Tools/_r820bmc_close.py:130` 的未闭合字符串没修**（r2111 已记录，仍是 `SYNTAX_ERROR`）。
- 全量冒烟本轮在后台跑，结果另记，不在本 QA 内。
