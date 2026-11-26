# QA — r2159：「链只在听见 STALE 时才付钱」这件事，有多少条腿永远不会自己好

日期 2026-11-27（轮 r2159，bm-c）｜触发 = S1 全量冒烟（03:49 起跑，981.5s，**778/787 PASS，9 FAIL**）

## 一、九条红分成三类（本轮实际处置）

| # | 腿 | 首行证据 | 类别 | 本轮处置 |
|---|---|---|---|---|
| 1 | `etf_book_cash_roll_today (instruction re-derived from disk)` | `cash_cny: published 565262.0 vs re-derived 565316.0` | 上游动了（permission 面被重生）+ 检查不说 STALE | **已修**：面记两个输入的 sha256；漂移说 STALE；重生后 22/22 自检、check 绿 |
| 2 | `the book re-levers off its own decision grid (every phase re-derives)` | `face cutoff 2026-11-25 is behind the ledger's last bar 2026-11-26` | 同上（k_grid 把漂移写成 "behind"） | **已修**：drift 单独成列并印 `[check] STALE …`；新增 L18/L19 行为腿（19/19）；重修 58s 后 check `OK verdict=GRID_COSTS delta=-0.28pp` |
| 3 | `etf_book_year_gate_vote (census still re-derives from the faces)` | `CHECK_FAIL 12 field(s) drifted` | 同上（census 读的账面推进一格，却不自称过期） | **已修**：证据截止日落后即 STALE；重生 0.2s 后 check `CHECK_OK readings=152 books=41 … R0=35 R1=35 R2=49`（原 31/31/47） |
| 4 | `etf_book_premium_swap (verdicts still re-derive from the ticket)` | `face as_of '2026-11-25' != ticket as_of '2026-11-26'` | 同上（票面前进一格） | **已修**：票面推进即 STALE + moved_inputs；重生 46.7s 后 check 绿（as_of 11-26） |
| 5 | `etf_book_premium_choice (road arithmetic still re-derives)` | `159655/B_same_market_twin break-even windows drifted` | **真缺陷：容差没说出自己的来历**（两边都是 2dp 打印值，hold=sav/give 的打印噪声随 give 放大到 1.3e-3 > 旧容差 1e-3） | **已修**：容差改成 hold×(0.01/sav+0.01/give) 并印出；check 绿、自检 25/25 |
| 6 | `a declared starting book is named as a declaration on both faces` | `the CEO page does not name it either` | 面代差（CEO 页未重生） | 未修（记欠账） |
| 7 | `fleet: a panel tail read by sample is certified against a full scan` | `['ah_panel']: a sampled row prints a tail with no record of the scan behind it` | 认证面缺记录行 | 未修（记欠账） |
| 8 | `the CEO page's sections each name the bar they were priced on` | `section 'bets'/'derisk' is behind the page and no chain leg re-runs it` | 结构缺口：两节没有链腿 | 未修（记欠账） |
| 9 | `etf_book_rebal_adoption (published cells and arithmetic re-derived)` | `DRIFT control did not reproduce the published book` | **真缺陷候选（最重）**：控制臂今日重算 CAGR **10.89%**，发布面 `results/etf_nobond_vt.json` 是 **11.49%**，差 0.60pp ≫ 容差 0.05pp | 未修（记欠账，需单独一轮） |

第 1–5 条的共同根因就是 r1934 立的规矩的反面：**链只在探针自己印出 STALE（或 "face missing"）时才买重生**（`Tools/s6_chain_bmc.py::run_leg`，`_repairable`）。规矩本身是对的（放宽它 = 用重生把真缺陷抹掉）；错在各脚本把「上游动了」写成 behind / moved / drifted / CHECK_FAIL，于是写者永远不被买，面停在旧 bar 上，只有人手动跑一次才会绿——**永久红**。

## 二、本轮新面：把这一类数出来

`scripts/chain_contract_word_audit.py`（+ `results/chain_contract_word_audit.json` + `research/CHAIN_CONTRACT_WORD_AUDIT.md`）

- 读法：把 `Tools/s6_chain_bmc.py` 的 LEGS 表当**数据**读（AST，不 import，避免跑链）；对每条**带写者**的腿看它的检查脚本，再实跑候选腿，按「红了且不说契约词」判 PERMANENT_RED。
- 读数（普通模式，30s）：**390 腿 / 134 条带写者的腿 / 22 条不会说那个词，其中此刻红的 0 条**（第 1–5 条已在本轮修掉）→ 判词 `STRUCTURAL_RISK_ONLY`：今天没红，但那 22 条在输入一动的那天就会冻住。
- 为什么还要 `--deep`：静态过滤看不见「词在哪个分支上」——`premium_swap` / `year_gate_vote` 的脚本里出现过 stale 字样（选项名、注释），运行时却印 CHECK_FAIL/DRIFT。深探测逐条实跑才是真数。
- `--check` 只在静态面对账 + 逐脚本摘要门：任何一个候选脚本或链表变了，live 列即 STALE（这张面是关于「脚本运行时会做什么」的断言，摘要是它唯一的新鲜度证明）。

## 三、验证证据（逐条实跑，非宣称）

- `scripts/etf_book_ticket_band.py`：selftest **18/18**（新增 4 腿：重写票面=drift、新卡点名两文件、同输入错数=defect、旧卡面=STALE）；`check` `ok=true moved_inputs=[]`；`run` 1.2s。
- `scripts/etf_book_cash_roll_today.py`：selftest **22/22**（新增 2 腿）；`--check` `ok=true`；重生 1.1s。
- `scripts/etf_book_k_grid.py`：selftest **19/19**（新增 L18/L19）；`--check` `OK verdict=GRID_COSTS delta=-0.28pp spread=0.45pp`；重生 58s。
- `scripts/etf_book_year_gate_vote.py`：selftest **10/10**；重修前 `--check` 印 STALE + 12 条 DRIFT，重修后 `CHECK_OK readings=152 books=41`。
- `scripts/etf_book_premium_swap.py`：`--check` 先印 STALE（ticket 11-25→11-26），`sheet` 46.7s 后 check 绿。
- `scripts/etf_book_premium_choice.py`：`--check` 由红转绿（容差带出处），selftest 25/25。
- `scripts/chain_contract_word_audit.py`：selftest **8/8**（含两条行为腿：改了脚本摘要必须 STALE；只有计数不符必须 CHECK FAILED 不带 STALE）；`--check` `ok=true`。
- 冒烟接线的两条新腿（`product: chain contract-word audit (static scan and classifier)` / `(live column still matches its scripts)`）已写进 `smoke_test.py`。

## 四、如实记的未完成面

1. `etf_book_rebal_adoption` 的控制臂不重现发布书（10.89% vs 11.49%）——这是**今天最重的一条**，不是代差：重修一次仍是 CONTROL_FAILED，需要单独一轮查清（可能来源：r2147 的拆股修复、或 2026 段新增 bar 改变了年度分布）。
2. CEO 页两处（declared starting book 未点名、bets/derisk 两节落后且无链腿）与 ah_panel 采样尾缺扫描记录——三条都未修。
3. 全量冒烟本轮只跑了一次（03:49–04:05 那趟），修完后**没有重跑全量**；上表 1–5 的绿是逐腿实跑证据，不是整批证明。
4. `--deep` 深探测本轮在后台跑（用来给「不会说那个词的腿」一个运行时真数），结果未进本件时点；普通模式读数已入面。
5. 审计面只覆盖 `s6_chain_bmc.py` 的 LEGS 表；冒烟腿与人工跑的面不在射程。
