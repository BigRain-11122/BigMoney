# QA — 宽度表第一次能说「我过期了」（r2162）

轮次：bm-c r2162 ｜ 时间：2026-11-27 05:2x +0800 ｜ 起因：r2159 新面
`results/chain_contract_word_audit.json` 点名的 22 条腿里的一条（r2160/r2161 各清一条，这是第三条）

## 1. 缺陷（可从指纹复现，不是感觉）

`results/etf_book_width_fit.json` 在链里**本来就是** `(check, run)` 一对
（`Tools/s6_chain_bmc.py` 的 `etf_book_width_fit` 腿），也就是「修一次要付 48.4s 的写」已经声明好了。
问题是它的 `check` **永远不会说自己过期**：

- 它把 `decision_bar` 与票面比、发现不一致 → 打印 `decision_bar X != ticket Y`（**没有 STALE 这个词**）；
- `run_leg` 只在探针文本里出现 `stale` / `face missing` 时才付钱补写（r1850 契约词，`Tools/s6_chain_bmc.py::run_leg`）；
- 于是票面滚到新 bar、这张表还钉在旧书上时，腿**红着、且永远红**，没人会重算它 ——
  正是 r1345 立的那个陷阱：**看起来像检查通过（或永远红），实际是把共享面冻在旧的一天**。

审计面自己给出的证据：`n_candidates=22`（结构风险腿），本腿在列，`verdict=STRUCTURAL_RISK_ONLY`。

## 2. 修法（三处，最小面）

1. `scripts/etf_book_width_fit.py` 新增 `drift(payload, t, g)`：**只读两个外部锚**——
   票面写的 `decision_bar`、闸面写的 `data.last`（闸在每个 bar 上重推导，它的容量读数随当日
   live five 变）。任一滚到新 bar 就打印 `STALE: ...`。
   两个锚都是外部面：闸面**没有**顶层 `evidence_cutoff`（实测为 None），所以给 `gate_reads()`
   加了 `gate_bar = data.last` 这一键，否则这条锚是死的。
2. `check()` 拆身份：`bar_moved` 时跳过与票面逐项比对（那是同一个事件的第二遍，且「市场前进」
   不是「自相矛盾」）；真算错（每名一手价与资本/n 对不上等）仍然原样报错，**不带 STALE 字样**。
3. `main_check()` 三态：`CHECK_FAIL`(rc1) / `CHECK_STALE`(rc3) / `CHECK_OK`(rc0)。
   rc3 与仓里既有惯例一致（`treasury_curve_page` 同一形状）。

## 3. 验证（逐条实跑）

| 检查 | 命令 | 结果 |
|---|---|---|
| selftest（新增 4 腿：同 bar 不报过期 / 票面滚一格报 STALE / 闸面滚一格报 STALE / 真算错不带 STALE） | `python scripts\etf_book_width_fit.py selftest` | **26/26 PASS**，rc0 |
| 现行面自洽 | `python scripts\etf_book_width_fit.py check` | `CHECK_OK ... bar 2026-11-11 (1.0649%)`，rc0 |
| 面重建（换掉 11-19 那一代，写入 `gate_bar`） | `python scripts\etf_book_width_fit.py run` | rc0，**48.4s** |
| **真 check()** 上四态行为腿（不是自派生） | `python results\_r2162bmc_width_fit_stale_probe.py` | **4/4 PASS**：原样→CHECK_OK rc0；decision_bar 退一格→CHECK_STALE rc3；gate_bar 退一格→CHECK_STALE rc3；width5 一手价改 1 元→CHECK_FAIL rc1 且无 STALE |
| 审计面复算 | `python scripts\chain_contract_word_audit.py run` | `n_candidates` **22 → 21**，`n_permanent_red=0` |
| 审计面自校 | `python scripts\chain_contract_word_audit.py --check` | `{"ok": true, "problems": []}`，`n_current=21` |
| 链腿三连（写者在前） | `python Tools\s6_chain_bmc.py --round 2162 --only=permission_vs_size_write,permission_vs_size,etf_book_width_fit` | **3/3 rc0** |

## 4. 顺带修掉的红（不是本轮主产出，但同窗实跑发现）

- 全量冒烟里的 `product: etf_book_permission_vs_size (permission and lot words re-derived)` rc3：
  `STALE: results/etf_book_supply_gate_decision/DECISION.json moved` —— 闸面重推导换了字节，
  按链序 `permission_vs_size_write` 跑一次 1.0s 即复原（`CHECK OK`）。
- `product: chain contract-word audit (live column still matches its scripts)` 在冒烟跑到一半时红：
  本轮 05:2x 重跑了审计面本身，属 r1861「面在动」族；复跑 `--check` 已 `ok:true`。

## 5. 剩下的欠账（照实记，不宣称完成）

审计面 `n_candidates=21`，逐腿点名：

    etf_book_dividend_credit, liquidity_select_write, liquidity_era_write, etf_book_fill_venue,
    etf_book_tail_dependence, etf_book_voltarget_phase, alias_census, harvest_census,
    alias_stability, etf_book_width_neighbors, etf_book_k_gap, premium_phases, year_caliber,
    sibling_entry, swap_trigger, swap_toll, toll_scope, swap_convergence, swap_effect,
    swap_units, trial_labor_direction_audit

按同一条配方（锚外部输入 + 拆 drift/self-contradiction 两种红 + 行为腿钉死）逐条收，
每轮 2–3 条可在轮预算内完成。
