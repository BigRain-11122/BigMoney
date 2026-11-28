# 哪些链腿永远不会自己好

> 生成 2026-11-28T19:07:45+0800 ｜ 链 `Tools\s6_chain_bmc.py` ｜ 420 腿 / 163 条带写者的腿

## 一句话

链只在探针自己印出 **STALE**（或“face missing”）时才付钱重生一张面（r1934/r1850 判例，这条规矩是对的——放宽它等于用重生把真缺陷抹掉）。于是凡是把「上游动了」写成 “behind / moved / advanced” 而从不写 STALE 的腿，就成了**永久红**：写者永远不会被买，面停在旧 bar 上，只有人手动跑一次才会绿。

读数：**163 条带写者的腿里 14 条不会说那个词，其中今天红着、且无法自愈的 0 条**。判词 **STRUCTURAL_RISK_ONLY**。

## 逐腿

| 腿 | 脚本 | 现在 | 它用来描述「上游动了」的词 | 首行 |
|---|---|---|---|---|
| alias_census | `scripts/etf_alias_census.py` | CURRENT | moved, drift | {"ok": true, "problems": [], "families": 41, "chains": 40} |
| alias_stability | `scripts/etf_alias_stability.py` | CURRENT | drift | {"artifact": "etf_alias_stability", "ok": true, "problems": [], "n_pairs": 741, "verdict": "WINDOW_LUCK"} |
| etf_book_bond_bear_stress | `scripts/etf_book_bond_bear_stress.py` | CURRENT | （一个都没有） | check ok: 4 arms, base 8.95% -> flat 7.72%, gate 0.0 |
| etf_book_fill_venue | `scripts/etf_book_fill_venue.py` | CURRENT | moved, drift | CHECK OK: INFORMATION_DOMINATES (gap +1.14pp, recovered -0.03pp, share -0.0263, budget NONE) |
| etf_book_k_gap | `scripts/etf_book_k_gap.py` | CURRENT | drift | ����Ҫ **0.458463**�����ֻ�� **0.435003**���� 2.35pp�������ŵ�������� **37 �� + 40 �� + 25 �� + 43 �� + 28 ��**�������Եļ��۳ |
| etf_book_voltarget_phase | `scripts/etf_book_voltarget_phase.py` | CURRENT | drift, changed | voltarget_phase --check OK {'cells': 16, 'share_up': 1.0, 'median_pp': 1.5, 'noise_pp': 1.81} -> within noise: the arm w |
| etf_book_width_neighbors | `scripts/etf_book_width_neighbors.py` | CURRENT | behind | CHECK_OK SIX_NAMES_SURVIVES_EVERY_CLOCK across clocks 10/20/40 |
| harvest_census | `scripts/etf_swap_harvest_census.py` | CURRENT | drift | CHECK OK problems=[] rows=1076 measured=834 |
| sibling_entry | `scripts/etf_book_sibling_entry.py` | CURRENT | moved | [sibling_entry] CHECK_OK the ticket already buys the cheapest live ticker of every index it holds: no swap saves anythin |
| swap_convergence | `scripts/etf_book_swap_convergence.py` | CURRENT | behind, moved, changed | CHECK_OK measured=0 |
| swap_effect | `scripts/etf_book_swap_effect.py` | CURRENT | drift | CHECK_OK rows=0 level=None path=None combined=None |
| swap_units | `scripts/etf_book_swap_units.py` | CURRENT | drift | CHECK_OK rows=0 shares=None lots=None realised=None |
| toll_scope | `scripts/etf_book_toll_scope.py` | CURRENT | moved, drift, changed | CHECK_OK |
| trial_labor_direction_audit | `scripts/trial_labor_direction_audit.py` | CURRENT | drift | CHECK OK: DIRECTION_BLIND_MEMBERS_NAMED / faces 5 / admitted 2 / negative 2 |

## 这张面不回答什么

- 它不判这些面算得对不对：`CURRENT` 只说明此刻是绿的，`PERMANENT_RED` 只说明它红了且没有写者会被买。

- 源码里出现 STALE 不等于运行时一定会印（词可能在另一条分支上），反向也只对本次运行成立——所以 live 列带着每条腿脚本的摘要，脚本一改这张面的 live 列就 STALE。

- 只查 `s6_chain_bmc.py` 的 LEGS 表；冒烟腿与人工跑的面不在射程。

复现：`python scripts\chain_contract_word_audit.py run`（只跑候选腿，约 20.1s）；`--check` 静态复核 + 摘要门；`--selftest` 离线行为腿。

