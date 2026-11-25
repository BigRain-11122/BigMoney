# 冒烟内联腿地图（哪几条腿能单独重问，剩下的要先搬什么）

generated 2026-11-25T16:32:21+0800 ｜ source=smoke_test.py sha256 c0b90301df60…
｜ 腿 647：声明式 325 / 内联 322（ready 266 · one_hop 24 · chained 32）

本表只读源码，不改冒烟、不跑脚本。`shape` 的含义：

- `ready`：块内只读模块级名字 —— 代码上可原样搬出（仍要给它一个 check 入口）；
- `one_hop`：读到 main() 的局部变量，但那些变量所在的语句自身不再读别的局部；
- `chained`：连局部变量都在读别的局部，搬之前要先把读取链造成夹具。

**先看有判决的腿**：排在最前的几行带判决，来自 `results/smoke_red_recheck.bm-c.json` —— 那是「红且没有独立命令」的实测集合；
其余内联腿只是盘点，不代表现在有问题。

## 按搬动成本排序（main 局部依赖少的先搬）

| # | 腿 | shape | main 局部依赖 | smoke_test.py 行 | 最近判决 |
|---|----|-------|---------------|------------------|----------|
| 1 | product: a declared starting book is named as a declaration on both faces | ready | — | 3649-3681 | NO_CHECK_ENTRY |
| 2 | product: the CEO page's sections each name the bar they were priced on | ready | — | 10541-10593 | NO_CHECK_ENTRY |
| 3 | product: the Chinese CEO pages carry no new English prose (r1582) | ready | — | 4042-4052 | NO_CHECK_ENTRY |
| 4 | product: the order sheet prints the floor's per-name cut, not only its total | ready | — | 6824-6857 | NO_CHECK_ENTRY |
| 5 | product: the paper book owns the book the card sells | ready | — | 4641-4671 | NO_CHECK_ENTRY |
| 6 | product: toll-ladder verdict is recomputable from the arm faces | ready | — | 7689-7734 | NO_CHECK_ENTRY |
| 7 | config: every cap face is on the chain with a check, in DAG order | ready | — | 12988-12999 | — |
| 8 | config: every face that prints a premium can name its session | ready | — | 9002-9015 | — |
| 9 | config: every published JSON face opens and holds no repeated key | ready | — | 9084-9097 | — |
| 10 | config: no CEO-facing page prints one measurement twice | ready | — | 8971-8991 | — |
| 11 | config: no card or digest carries a control character | ready | — | 8927-8940 | — |
| 12 | config: no card or digest carries an eaten path prefix | ready | — | 8951-8964 | — |
| 13 | config: no checked face was left without a writer leg | ready | — | 9058-9073 | — |
| 14 | config: no premium is priced in CNY against another session's NAV | ready | — | 9026-9048 | — |
| 15 | config: no tracked blob carries a conflict-marker fragment | ready | — | 8909-8919 | — |
| 16 | config: the cap-vs-book producer runs before the faces that quote it | ready | — | 12962-12978 | — |
| 17 | config: the card ledger guard sees every card heading level | ready | — | 9117-9137 | — |
| 18 | config: the staged JSON claw passes its own legs | ready | — | 9098-9109 | — |
| 19 | env: core deps | ready | — | 869-877 | — |
| 20 | fleet: GPU face leg wired into the S6 chain | ready | — | 6207-6219 | — |
| 21 | fleet: GPU face self-consistent on heartbeat | ready | — | 6207-6219 | — |
| 22 | fleet: a hostage lane nobody can pick up is named as a decision | ready | — | 4927-4953 | — |
| 23 | fleet: a killed child is told apart from a child that said no | ready | — | 6705-6715 | — |
| 24 | fleet: a lane green inside its own window says so on every face | ready | — | 5410-5473 | — |
| 25 | fleet: a lane that appended nothing still says whether it reaches the last session | ready | — | 5193-5267 | — |
| 26 | fleet: a lane that declares its stand-in is not uncertified | ready | — | 4893-4907 | — |
| 27 | fleet: a lane that names its collector is not told nothing can be done | ready | — | 5268-5316 | — |
| 28 | fleet: a lane whose clock is the statute is judged on the statute | ready | — | 5124-5192 | — |
| 29 | fleet: a lane whose clock is the statute reaches the page | ready | — | 5345-5409 | — |
| 30 | fleet: a panel newer than its envelope is not a stall | ready | — | 4868-4892 | — |
| 31 | fleet: a panel tail read by sample is certified against a full scan | ready | — | 4954-5077 | — |
| 32 | fleet: a partial-index commit cannot silently shrink the tree | ready | — | 6672-6692 | — |
| 33 | fleet: a stand-in declared in the old shape is named, not trusted | ready | — | 4908-4926 | — |
| 34 | fleet: bm-a's chain runner is the shared leg list, not a snapshot | ready | — | 8276-8292 | — |
| 35 | fleet: health writer runs before the panel that reads it | ready | — | 6306-6354 | — |
| 36 | fleet: heartbeat epoch fields present | ready | — | 6194-6206 | — |
| 37 | fleet: machine-health face is machine-keyed, not a nesting generator | ready | — | 6220-6228 | — |
| 38 | fleet: machine-health gate leg wired into the S6 chain | ready | — | 6306-6354 | — |
| 39 | fleet: oversight writer's deployed copy tracks its source | ready | — | 6265-6305 | — |
| 40 | fleet: panel carries the machine-health verdict, not a row count | ready | — | 6306-6354 | — |
| 41 | fleet: the board page carries the full scan's holder count | ready | — | 5078-5123 | — |
| 42 | fleet: the tree-shrink push gate is installed in both repos | ready | — | 6693-6701 | — |
| 43 | fleet: this repo's last 20 commits lost no tree | ready | — | 6672-6692 | — |
| 44 | harness: a page behind its ticket's quote session is named, never called a lie | ready | — | 947-959 | — |
| 45 | harness: the funding leg forgives a trip stamp, never a real gap | ready | — | 928-939 | — |
| 46 | memory: CODELY.md structure intact | ready | — | 6653-6671 | — |
| 47 | meta: a page is certified against the one build it names, not across two | ready | — | 5317-5344 | — |
| 48 | paper: pipeline selftest | ready | — | 1522-1528 | — |
| 49 | pool: the deliverable reconciliation runs before anything counts pool ready | ready | — | 6628-6652 | — |
| 50 | product: CPU work-hours are recomputable and every batch names a file | ready | — | 13763-13830 | — |
| 51 | product: E196 carrier verdict is recomputable from its own gate | ready | — | 7627-7657 | — |
| 52 | product: E198 cross-panel verdict is recomputable from its own gate | ready | — | 7658-7688 | — |
| 53 | product: E199 detection floor is recomputable from its own gate | ready | — | 7735-7777 | — |
| 54 | product: E222 sign-PIT verdict is recomputable from its own gate | ready | — | 4398-4415 | — |
| 55 | product: E223 sign-enum verdict is recomputable from its own arm table | ready | — | 4421-4438 | — |
| 56 | product: E224 sign-ordering transfer is recomputable from the per-period table | ready | — | 4443-4467 | — |
| 57 | product: E227 sign ordering across cells is recomputable from the per-cell arm tables | ready | — | 4529-4551 | — |
| 58 | product: E229 the quotable subset is priced against the full vector | ready | — | 4556-4576 | — |
| 59 | product: E236 the sign-vector re-selection procedure is priced | ready | — | 4581-4608 | — |
| 60 | product: E246 drawdown band reaches both trading pages | ready | — | 3954-3985 | — |
| 61 | product: E271 the width ruler reaches both order documents | ready | — | 4059-4091 | — |
| 62 | product: E272 each sheet says what its pairing could have detected | ready | — | 4140-4167 | — |
| 63 | product: E298 concentration face re-derives its own verdict, and its sleeve arm really carries the top names | ready | — | 4366-4393 | — |
| 64 | product: ETF book registry published | ready | — | 3866-3876 | — |
| 65 | product: ETF live-book cash leg is priced off the repo panel's own close | ready | — | 7825-8275 | — |
| 66 | product: ETF live-book page says how many independent bets the holdings are | ready | — | 7825-8275 | — |
| 67 | product: a book face cannot be green on a panel it no longer measures | ready | — | 13836-13891 | — |
| 68 | product: a copy that lags its own lane reaches the page, the board line and the printed run | ready | — | 5535-5563 | — |
| 69 | product: a de-levered book is told apart from a well-timed one | ready | — | 10673-10735 | — |
| 70 | product: a fixed fraction is only an adoption if it survives out of sample | ready | — | 10745-10804 | — |
| 71 | product: a lane green inside its own window says how much slack is left on the board, not only on the board's markdown | ready | — | 5570-5597 | — |
| 72 | product: a lane takeover declares whose disk holds the rows | ready | — | 4816-4867 | — |
| 73 | product: a page section on an older bar is a note off the writer, a red on it | ready | — | 10642-10665 | — |
| 74 | product: a restated forward bar says how far the chain moved | ready | — | 13921-13975 | — |
| 75 | product: a rewritten mark keeps the value it replaced | ready | — | 13894-13918 | — |
| 76 | product: a stale swap leg says who can move it, and a leg with its own producer is not told to wait for a file | ready | — | 5927-6175 | — |
| 77 | product: a survival verdict stands on a reproduced shared cell | ready | — | 6388-6411 | — |
| 78 | product: astock panel states its coverage, not just its date | ready | — | 6176-6193 | — |
| 79 | product: both priced blocks name the roll mask they were measured under (r1694) | ready | — | 1589-1602 | — |
| 80 | product: both reader faces state which price panel their numbers sit on | ready | — | 9691-9765 | — |
| 81 | product: card amount column is executable money | ready | — | 3739-3768 | — |
| 82 | product: card reconciles its two 2015-2019 readings | ready | — | 3721-3734 | — |
| 83 | product: carry sleeve funding line (every number re-derived) | ready | — | 1914-1925 | — |
| 84 | product: carry sleeve funding line (selftest) | ready | — | 1907-1913 | — |
| 85 | product: carry sleeve integer ladder (every cell re-derived) | ready | — | 1853-1864 | — |
| 86 | product: carry sleeve integer ladder (selftest) | ready | — | 1846-1852 | — |
| 87 | product: carry sleeve margin arm (selftest) | ready | — | 1942-1948 | — |
| 88 | product: carry sleeve margin arm (which floor wins, re-derived) | ready | — | 1949-1956 | — |
| 89 | product: carry sleeve sizing ruler (every consequence re-derived) | ready | — | 1876-1887 | — |
| 90 | product: carry sleeve sizing ruler adopted (selftest) | ready | — | 1869-1875 | — |
| 91 | product: carry-vs-ETF swap rulers (face re-derived from its inputs) | ready | — | 1969-1977 | — |
| 92 | product: carry-vs-ETF swap rulers (selftest) | ready | — | 1962-1968 | — |
| 93 | product: cash placement is reconciled against the book, and an unread account is not a zero gap | ready | — | 7825-8275 | — |
| 94 | product: cash-leg ladder verdict is the panels' own rolls, not a typed-in answer | ready | — | 7825-8275 | — |
| 95 | product: closed-axes face refuses a missing axis (selftest 19 legs) | ready | — | 1688-1694 | — |
| 96 | product: closed-axes verdict re-derived from the four faces it quotes | ready | — | 1695-1702 | — |
| 97 | product: dashboard carries the marks coverage gap | ready | — | 4779-4815 | — |
| 98 | product: data lag audit face published | ready | — | 4718-4727 | — |
| 99 | product: data lane freshness board agrees with the lanes and the calendar | ready | — | 5680-5823 | — |
| 100 | product: every face a reader holds says whether the width's family was one world | ready | — | 9861-9954 | — |
| 101 | product: every index panel reaches the futures panel's last bar | ready | — | 2039-2082 | — |
| 102 | product: every lane names one host before any task is re-enabled | ready | — | 5830-5865 | — |
| 103 | product: every marks hole carries a cause from the lane's own ownership contract | ready | — | 4761-4778 | — |
| 104 | product: flip-rate arms cut flips, not exposure, and the cut is priced | ready | — | 8452-8502 | — |
| 105 | product: futures TSMOM face is current, capped and not an order | ready | — | 8293-8352 | — |
| 106 | product: futures TSMOM shadow face keeps its sizing rules | ready | — | 8293-8352 | — |
| 107 | product: futures contract panel has a producer (selftest 8 legs) | ready | — | 1670-1676 | — |
| 108 | product: futures contract refresh re-derived from the panel | ready | — | 1677-1683 | — |
| 109 | product: futures overlay sweep keeps its blend arithmetic | ready | — | 8353-8379 | — |
| 110 | product: how long a holder waits under water, re-derived from the published rows | ready | — | 11118-11160 | — |
| 111 | product: index daily panel has a producer (selftest) | ready | — | 2032-2038 | — |
| 112 | product: index-futures carry desk sheet (selftest) | ready | — | 1800-1806 | — |
| 113 | product: index-futures proxy noise (selftest 21 legs) | ready | — | 1645-1651 | — |
| 114 | product: index-futures proxy noise re-derived | ready | — | 1652-1658 | — |
| 115 | product: index-futures roll cost measured (selftest 24 legs) | ready | — | 1709-1715 | — |
| 116 | product: index-futures roll gaps (selftest 17 legs) | ready | — | 1633-1639 | — |
| 117 | product: index-futures roll-gap states re-derived | ready | — | 1659-1665 | — |
| 118 | product: live paper book states its price lag | ready | — | 5913-5926 | — |
| 119 | product: marks coverage face names its holes | ready | — | 4744-4760 | — |
| 120 | product: one lot is priced beside the fee floor, and the page prints it | ready | — | 11610-11668 | — |
| 121 | product: open-fill gate names its evidence tier and the bar tier's prices are the bars' | ready | — | 5866-5912 | — |
| 122 | product: overlay breakeven is recomputable from its own ladder | ready | — | 8380-8410 | — |
| 123 | product: overlay no-trade band is priced on both sides of the trade | ready | — | 8411-8451 | — |
| 124 | product: overlay sweep sells risk and publishes the equal-risk reading | ready | — | 8353-8379 | — |
| 125 | product: prior-signs face re-derives its verdict and the prior key is the textbook key | ready | — | 4474-4501 | — |
| 126 | product: roll cost does not claim a verdict it cannot have (r1698) | ready | — | 1716-1745 | — |
| 127 | product: roll tenor prices both policies (selftest 27 legs) | ready | — | 1751-1757 | — |
| 128 | product: roll tenor re-derives from the contract panel | ready | — | 1758-1764 | — |
| 129 | product: shock face prices its shocks off its own beta and ticket | ready | — | 7825-8275 | — |
| 130 | product: staggered book states when each sleeve next turns | ready | — | 4707-4717 | — |
| 131 | product: the CEO page carries today's actions, not only the full build | ready | — | 13297-13380 | — |
| 132 | product: the CEO page prices the book's idle cash (r1908) | ready | — | 13098-13139 | — |
| 133 | product: the CEO page prices the carry book's zero (funding line) | ready | — | 13028-13091 | — |
| 134 | product: the CEO page prices the cash the sheet leaves behind | ready | — | 13387-13435 | — |
| 135 | product: the CEO page prices the whole book in one line | ready | — | 12725-12795 | — |
| 136 | product: the CEO page prints what following the book means tomorrow (lots + cash) | ready | — | 13189-13236 | — |
| 137 | product: the CEO page says what part of the build order is premium | ready | — | 13243-13289 | — |
| 138 | product: the CEO page shows where the six signs came from and what peeking pays | ready | — | 4505-4524 | — |
| 139 | product: the CEO-page quote audit runs after the pages it audits | ready | — | 6444-6454 | — |
| 140 | product: the CEO-page quote gate runs after the sweep and owns a baseline | ready | — | 6455-6472 | — |
| 141 | product: the account the sheet never sells reaches the CEO page | ready | — | 3560-3607 | — |
| 142 | product: the battle report carries the book it is about | ready | — | 13442-13492 | — |
| 143 | product: the block band is rebuilt before the card embeds it | ready | — | 6416-6443 | — |
| 144 | product: the block family is complete, not merely self-consistent | ready | — | 4205-4223 | — |
| 145 | product: the book a person holds is priced in money (r1900) | ready | — | 1194-1230 | — |
| 146 | product: the book envelope says whose book it describes | ready | — | 3528-3553 | — |
| 147 | product: the book's CAGR is split into overnight / intraday / quiet / toll and the split closes to the same total | ready | — | 10248-10284 | — |
| 148 | product: the book's headline is priced one bar in the future, and the gap is measured | ready | — | 10918-10955 | — |
| 149 | product: the calendar split is re-read at matched candidate width, as a distribution rather than a point | ready | — | 6526-6554 | — |
| 150 | product: the capital face prices both roll masks and the page prints both (r1695) | ready | — | 1608-1626 | — |
| 151 | product: the card says which book its own width is not | ready | — | 5927-6175 | — |
| 152 | product: the card says which research questions its numbers already answered | ready | — | 3774-3844 | — |
| 153 | product: the card states which of its two arms the desk can trade | ready | — | 3774-3844 | — |
| 154 | product: the card table prices both arms in the headline rows | ready | — | 3774-3844 | — |
| 155 | product: the card's title names the bar its legs come from | ready | — | 5927-6175 | — |
| 156 | product: the carry split reproduces the ticket and stays ordered | ready | — | 9333-9410 | — |
| 157 | product: the compute audit reads the claim face, not just the pool row | ready | — | 13688-13727 | — |
| 158 | product: the dashboard says which bar the three papers were priced on | ready | — | 10126-10156 | — |
| 159 | product: the day-of-month face counts sessions, not name-days | ready | — | 8622-8665 | — |
| 160 | product: the desk sheet refuses a gap instead of printing zero (r1701) | ready | — | 1807-1839 | — |
| 161 | product: the executable ticket decomposes its own headline | ready | — | 9416-9499 | — |
| 162 | product: the execution-claim face runs on the card it reads, not ahead of it | ready | — | 7801-7815 | — |
| 163 | product: the expectation table's rows name the ruler that priced each one | ready | — | 12334-12386 | — |
| 164 | product: the fill is sliced over k opens and priced against the declared arm | ready | — | 11058-11111 | — |
| 165 | product: the flip damper is adopted or rejected by path cells, not one run | ready | — | 8503-8554 | — |
| 166 | product: the forward ledger publishes its own noise floor | ready | — | 4609-4620 | — |
| 167 | product: the human faces quote the measured draw-tail share, not the impression | ready | — | 4328-4359 | — |
| 168 | product: the idle-cash money reaches the CEO page, same numbers | ready | — | 3925-3947 | — |
| 169 | product: the index-futures page carries the capital face's numbers (r1688) | ready | — | 1575-1582 | — |
| 170 | product: the ladder advice on the ticket carries the price measured since | ready | — | 9506-9546 | — |
| 171 | product: the lane-silence face names whether the lane is switched off | ready | — | 13732-13762 | — |
| 172 | product: the live quote is priced before the page that prints it | ready | — | 6358-6365 | — |
| 173 | product: the live-quote section and the panel's own lane agree on tonight | ready | — | 9216-9258 | — |
| 174 | product: the live-width gate tells a re-issued ticket from a hand edit | ready | — | 4099-4135 | — |
| 175 | product: the matched-width control is laddered across book widths, with the invariance of the gap published beside it | ready | — | 6555-6586 | — |
| 176 | product: the mid-month gap arrives split into timing and selection | ready | — | 6498-6525 | — |
| 177 | product: the missing bar is not a fill an operator could have chosen | ready | — | 12480-12533 | — |
| 178 | product: the next sheet starts from the account as it stands, not its last trade | ready | — | 3614-3643 | — |
| 179 | product: the observation-rate ladder prices its own resolution | ready | — | 8666-8837 | — |
| 180 | product: the off-book era leg is on the chain and publishes a cross-era verdict | ready | — | 6473-6497 | — |
| 181 | product: the one-bar price is not recoverable by smoothing the causal score | ready | — | 10963-11004 | — |
| 182 | product: the operator page prices the basket the ticket actually holds | ready | — | 11444-11525 | — |
| 183 | product: the operator page prices the cash half on the sheet's own three rates | ready | — | 11823-11997 | — |
| 184 | product: the operator page prints how long the wait is | ready | — | 11168-11214 | — |
| 185 | product: the operator page says how much money this book needs | ready | — | 11362-11437 | — |
| 186 | product: the operator page says the entry gate sets capacity, not return | ready | — | 12224-12326 | — |
| 187 | product: the operator page says whether this book was runnable in 2020 | ready | — | 11287-11354 | — |
| 188 | product: the operator page says which window its numbers came from | ready | — | 11221-11281 | — |
| 189 | product: the order sheet carries the permission it must obey | ready | — | 6791-6819 | — |
| 190 | product: the order sheet prices money itself (1M/3M/10M/30M) | ready | — | 10075-10119 | — |
| 191 | product: the order sheet prices the bar it says it is priced on | ready | — | 6863-6898 | — |
| 192 | product: the order sheet prices the cash half in CNY at today's rate | ready | — | 11753-11816 | — |
| 193 | product: the order sheet states whether the book may take new capital | ready | — | 6904-6936 | — |
| 194 | product: the order ticket discloses how many bets the sleeve holds | ready | — | 6761-6787 | — |
| 195 | product: the overnight gap is priced as the last channel between decide and fill | ready | — | 11010-11050 | — |
| 196 | product: the page answers whether the commodity sleeve needs its own gate | ready | — | 10349-10450 | — |
| 197 | product: the page names which half refused the carry product (r1910) | ready | — | 13147-13182 | — |
| 198 | product: the page never says 'nothing to do today' on the day it names as the rebalance | ready | — | 5927-6175 | — |
| 199 | product: the page prices its break-even at the rate the ticket pays | ready | — | 11533-11603 | — |
| 200 | product: the page prices the cost assumption under every number | ready | — | 12666-12723 | — |
| 201 | product: the page says how many names the lot grid actually holds | ready | — | 11675-11745 | — |
| 202 | product: the page says what fills at the open and whose book that is | ready | — | 4683-4689 | — |
| 203 | product: the page says whose CAGR it is quoting (top-3 share and both deletions) | ready | — | 10291-10340 | — |
| 204 | product: the page shows the book's own luck distribution, not just a point | ready | — | 3686-3719 | — |
| 205 | product: the page tells a de-levered book from a well-timed one | ready | — | 12540-12619 | — |
| 206 | product: the page's own pricing day is read through one reader | ready | — | 12625-12658 | — |
| 207 | product: the paper puts today-words on the page's own day | ready | — | 4692-4697 | — |
| 208 | product: the percentile face is rebuilt before the ticket embeds it | ready | — | 6416-6443 | — |
| 209 | product: the premium face is re-derived before it is judged | ready | — | 6416-6443 | — |
| 210 | product: the price of waiting reaches the sheet that trades | ready | — | 3991-4012 | — |
| 211 | product: the printed cap is reconciled with the priced book on both faces | ready | — | 12899-12960 | — |
| 212 | product: the prior-signs page names the arm peeking picks and its OOS number | ready | — | 4474-4501 | — |
| 213 | product: the promised fill and the fill receipt are both recomputable | ready | — | 4674-4680 | — |
| 214 | product: the reform direction audit cannot report a clean readout over a losing admission | ready | — | 13007-13019 | — |
| 215 | product: the regime cap is compared with the money actually deployed | ready | — | 3882-3908 | — |
| 216 | product: the row the 11-08 enable decision reads agrees with the declaration | ready | — | 5604-5679 | — |
| 217 | product: the row the operator reads has a full-window number in its full window column | ready | — | 12394-12472 | — |
| 218 | product: the seat face's cutoff is the bar it read | ready | — | 4018-4034 | — |
| 219 | product: the sheet a person holds says whether it is a missed run (r1890) | ready | — | 1016-1053 | — |
| 220 | product: the sheet issued from the card is that card's own book | ready | — | 4641-4671 | — |
| 221 | product: the sheet names the fill day it already knows | ready | — | 5927-6175 | — |
| 222 | product: the sheet prints what it pays and where that price sits in history | ready | — | 12006-12127 | — |
| 223 | product: the sheet says how far its k sits from the ruler that signed it, and the zone is re-derived from the numbers it prints | ready | — | 10162-10239 | — |
| 224 | product: the sheet's swap-section freshness is re-derived, not remembered | ready | — | 5927-6175 | — |
| 225 | product: the sheet's trigger section names which scope its threshold has | ready | — | 7825-8275 | — |
| 226 | product: the six seats' idle cash can be priced (selftest) | ready | — | 3914-3924 | — |
| 227 | product: the sleeve-gate answer survives a moved decision grid | ready | — | 10459-10534 | — |
| 228 | product: the state tilt prices the toll it would need | ready | — | 9262-9328 | — |
| 229 | product: the state tilt publishes its own effective sample size | ready | — | 8844-8904 | — |
| 230 | product: the substitution rulers reach the CEO page (r1933) | ready | — | 2014-2025 | — |
| 231 | product: the swap block prints the face's own build stamp | ready | — | 1993-2010 | — |
| 232 | product: the swap page states its verdict and the ETF share it costs | ready | — | 1978-1988 | — |
| 233 | product: the tenor verdict is on the page (r1931) | ready | — | 1765-1793 | — |
| 234 | product: the three papers print the day each was priced on, and can disagree | ready | — | 9960-10068 | — |
| 235 | product: the ticket prints which sizing road the book runs | ready | — | 1891-1900 | — |
| 236 | product: the ticket says what it costs to open and which line is executable | ready | — | 1926-1937 | — |
| 237 | product: the ticket's positions edge names a missed run, not a content mismatch | ready | — | 965-1009 | — |
| 238 | product: the turn-of-month overlay keeps its rule, its toll and its OOS record | ready | — | 8666-8837 | — |
| 239 | product: the two adjudications on the sheet read the same panel | ready | — | 6904-6936 | — |
| 240 | product: the two live widths are priced on one ruler and the gap is inside the engines' own disagreement | ready | — | 13560-13635 | — |
| 241 | product: the veto verdict only greens when it beats the random drop too (r1864c) | ready | — | 2156-2173 | — |
| 242 | product: the vol overlay's tail is priced on the same draw as its middle | ready | — | 4281-4323 | — |
| 243 | product: the vol window is judged on more than one decision calendar | ready | — | 10811-10853 | — |
| 244 | product: the volatility gate separates held days from episodes | ready | — | 8666-8837 | — |
| 245 | product: the voltail family is complete, not merely self-consistent | ready | — | 4228-4246 | — |
| 246 | product: the wait fee lands on the ticket's own size (r1913) | ready | — | 1144-1188 | — |
| 247 | product: the width family is re-derived before the page that quotes it | ready | — | 6370-6383 | — |
| 248 | product: the width ladder is split into timing and selection, so its movement is attributed to a named part | ready | — | 6587-6627 | — |
| 249 | product: the width ladder names why it cannot be quoted, and the buffer line is tested on a point it never saw | ready | — | 13493-13559 | — |
| 250 | product: the width sign is read against a noise score, not just another grid | ready | — | 13636-13687 | — |
| 251 | product: the width survival test measures every clock it judges | ready | — | 6388-6411 | — |
| 252 | product: the window grid's floor is the engine's, measured not assumed | ready | — | 10863-10912 | — |
| 253 | product: the worst 1% is published on the block arms | ready | — | 4172-4199 | — |
| 254 | product: three faces of one book price one panel, and the digest can move | ready | — | 9773-9854 | — |
| 255 | product: treasury curve verdict is re-derived from its own criteria (r1691) | ready | — | 2088-2137 | — |
| 256 | rules: T+0 list | ready | — | 1275-1276 | — |
| 257 | suite: a repeated selftest rides the first judgement (r1602) | ready | — | 2177-2178 | — |
| 258 | suite: a selftest started early is already answered when its leg arrives (r1603) | ready | — | 2181-2182 | — |
| 259 | tooling: every harness subprocess capture pins encoding and errors | ready | — | 3498-3523 | — |
| 260 | config: paths | ready | — | 1232-1236, 1237-1238 | — |
| 261 | product: ETF book legs wired into the S6 chain | ready | — | 3845-3865, 7778-7800 | — |
| 262 | product: ETF live-book page current and its money closes | ready | — | 5927-6175, 7825-8275 | — |
| 263 | product: ETF live-book page says whether to trade today | ready | — | 5927-6175, 7825-8275 | — |
| 264 | product: ETF live-book stress rows are their own percentages x capital | ready | — | 5927-6175, 7825-8275 | — |
| 265 | product: ETF live-book yuan figures are its own percentages x its own capital | ready | — | 5927-6175, 7825-8275 | — |
| 266 | product: both reader faces print the cut that picks the universe, recomputed | ready | — | 5927-6175, 7825-8275 | — |
| 267 | config: param grid | one_hop | combos | 1240-1240 | — |
| 268 | data: core ETF pool | one_hop | core_files | 1247-1248 | — |
| 269 | engine: deterministic | chained | det_ok | 1302-1302 | — |
| 270 | engine: emptying cutoff refused (RW-2) | one_hop | raised | 1344-1345 | — |
| 271 | engine: legacy keyset intact without evidence_cutoff (RW-2) | chained | r1 | 1337-1338 | — |
| 272 | exit: P1 signal_reversal beats P2 stop (RW-7) | chained | _p12 | 1446-1448 | — |
| 273 | exit: P2 stop_loss beats P3 take_profit (RW-7) | chained | _p23 | 1452-1455 | — |
| 274 | exit: P4 time_decay beats P5 loss_time_stop (RW-7) | chained | _p45 | 1457-1459 | — |
| 275 | exit: P6 global_hard_limit terminal tier (RW-7) | chained | _p6 | 1461-1463 | — |
| 276 | exit: hard stop -8% | chained | a3 | 1286-1286 | — |
| 277 | exit: hold otherwise | chained | a4 | 1287-1287 | — |
| 278 | exit: loss 8d force-close | chained | a1 | 1283-1283 | — |
| 279 | exit: tiered take-profit | chained | a2 | 1284-1285 | — |
| 280 | fleet: a thin face reads as UNKNOWN, not as a calm row | one_hop | _tf | 6242-6264 | — |
| 281 | fleet: live machine-health rows carry every pinned field | one_hop | _mf | 6229-6241 | — |
| 282 | gate: rejections raise, never silently drop (RW-7) | one_hop | _rej | 1485-1489 | — |
| 283 | harness: the suite's own wall clock names its slow legs | one_hop | _saved_perf | 890-898 | — |
| 284 | network: detector | one_hop | nt | 1517-1517 | — |
| 285 | network: status readable | one_hop | st | 1519-1519 | — |
| 286 | network: traffic gate | one_hop | ok_small | 1521-1521 | — |
| 287 | panel gate: stale in-service member refused (RW-4) | chained | res_stale | 1389-1391 | — |
| 288 | panel gate: twins refused, len(set)==len(list) (RW-4) | chained | res_twin | 1385-1388 | — |
| 289 | product: ETF registry runs after every face it summarises | one_hop | _rg | 7816-7824 | — |
| 290 | product: ETF registry says when the staggered book turns | one_hop | _rg | 4698-4706 | — |
| 291 | product: a bar restated after settling reaches the ticket's own ledger line | one_hop | _stamp30 | 9571-9685 | — |
| 292 | product: a stale cohort is named, not counted | one_hop | _la | 4728-4743 | — |
| 293 | product: every candidate edge states the file it was read from | one_hop | _sig | 4621-4640 | — |
| 294 | product: the CEO page carries today's market risk tape | chained | v | 12797-12891 | — |
| 295 | product: the CEO page still prints where in the day the money is earned | one_hop | _pg31 | 9148-9210 | — |
| 296 | product: the adopted flip damper reaches the live shadow book | chained | m | 8555-8621 | — |
| 297 | product: the forward face prices what its horizon can resolve, not only bars | one_hop | _sig | 4621-4640 | — |
| 298 | product: the page itself names the sections that sit on an older bar | one_hop | _SB78 | 10599-10640 | — |
| 299 | product: the paired-rows family on disk is complete and stray-proof | one_hop | _tf | 4252-4275 | — |
| 300 | product: the price of waiting reaches the page the CEO opens (r1893) | chained | v | 1059-1138 | — |
| 301 | product: whose disk the lane numbers are on reaches both human faces | one_hop | _g2 | 5474-5528 | — |
| 302 | rules: fee schedule sane | chained | cost_rate | 1273-1274 | — |
| 303 | config: combo_hash deterministic | chained | h1, h2 | 1243-1243 | — |
| 304 | data: freshness | chained | latest, stale_days | 1268-1269 | — |
| 305 | engine: T+1 respected | chained | r1, same_day | 1305-1306 | — |
| 306 | engine: exits fill at T+1 open (RW-1) | chained | bad_exit_px, r1 | 1312-1313 | — |
| 307 | engine: grid legacy divergence = declared 0.041bp (RW-3) | chained | _gp, grid_delta | 1362-1365 | — |
| 308 | engine: single-source cost parity (RW-3) | chained | engine_side, parity_ok | 1359-1361 | — |
| 309 | gate: daily_loss_breaker boundary (RW-7) | one_hop | RISK, _g | 1465-1467 | — |
| 310 | gate: emit_order_sheet is the sole gated exit (RW-7) | chained | _emit_refused, _wrote | 1511-1513 | — |
| 311 | gate: halted day still lets exits through (RW-7) | chained | _gsell, _halt_sell | 1493-1495 | — |
| 312 | harness: a face rewritten mid-run is named as moved, not judged | one_hop | _saved_t0, _tf | 903-923 | — |
| 313 | panel gate: out-of-lock + silent-shrink refused (RW-4) | chained | res_lock, res_shrink | 1392-1395 | — |
| 314 | data: OHLCV readable | one_hop | bad, core_files, panels | 1264-1265 | — |
| 315 | engine: evidence_cutoff hard truncation (RW-2) | chained | cut_d, n_after, trunc_ok | 1326-1328 | — |
| 316 | engine: one-word bar buy dropped + sell deferred (CN-A, D-38) | chained | _fills, _idx, _owm | 1434-1439 | — |
| 317 | panel gate: real in-service panel inside frozen 48-lock (RW-4) | chained | _pg, panels, res_real | 1381-1384 | — |
| 318 | product: astock residual veto layer selftest (r1864c) | chained | _rv_m, _rv_out, _rv_sel | 2152-2155 | — |
| 319 | product: the sheet prints what the price did after a reading like today's | one_hop | _md99, _syms99, _tk99 | 12135-12216 | — |
| 320 | rules: stock fee routing sell 18.141bp / buy 13.141bp (D-39) | chained | _d_buy, _d_sell, _ok_route | 1409-1413 | — |
| 321 | engine: rows actually read <= cutoff (RW-2) | chained | cut_d, meta, n_read, r3, window | 1330-1336 | — |
| 322 | engine: smoke backtest | chained | eq_ok, keys_ok, m, syms, tr_ok | 1300-1301 | — |

## 逐腿要搬的名字

- **product: a declared starting book is named as a declaration on both faces**：无需搬动（ready）。
- **product: the CEO page's sections each name the bar they were priced on**：无需搬动（ready）。
- **product: the Chinese CEO pages carry no new English prose (r1582)**：无需搬动（ready）。
- **product: the order sheet prints the floor's per-name cut, not only its total**：无需搬动（ready）。
- **product: the paper book owns the book the card sells**：无需搬动（ready）。
- **product: toll-ladder verdict is recomputable from the arm faces**：无需搬动（ready）。
- **config: every cap face is on the chain with a check, in DAG order**：无需搬动（ready）。
- **config: every face that prints a premium can name its session**：无需搬动（ready）。
- **config: every published JSON face opens and holds no repeated key**：无需搬动（ready）。
- **config: no CEO-facing page prints one measurement twice**：无需搬动（ready）。
- **config: no card or digest carries a control character**：无需搬动（ready）。
- **config: no card or digest carries an eaten path prefix**：无需搬动（ready）。
- **config: no checked face was left without a writer leg**：无需搬动（ready）。
- **config: no premium is priced in CNY against another session's NAV**：无需搬动（ready）。
- **config: no tracked blob carries a conflict-marker fragment**：无需搬动（ready）。
- **config: the cap-vs-book producer runs before the faces that quote it**：无需搬动（ready）。
- **config: the card ledger guard sees every card heading level**：无需搬动（ready）。
- **config: the staged JSON claw passes its own legs**：无需搬动（ready）。
- **env: core deps**：无需搬动（ready）。
- **fleet: GPU face leg wired into the S6 chain**：无需搬动（ready）。
- **fleet: GPU face self-consistent on heartbeat**：无需搬动（ready）。
- **fleet: a hostage lane nobody can pick up is named as a decision**：无需搬动（ready）。
- **fleet: a killed child is told apart from a child that said no**：无需搬动（ready）。
- **fleet: a lane green inside its own window says so on every face**：无需搬动（ready）。
- **fleet: a lane that appended nothing still says whether it reaches the last session**：无需搬动（ready）。
- **fleet: a lane that declares its stand-in is not uncertified**：无需搬动（ready）。
- **fleet: a lane that names its collector is not told nothing can be done**：无需搬动（ready）。
- **fleet: a lane whose clock is the statute is judged on the statute**：无需搬动（ready）。
- **fleet: a lane whose clock is the statute reaches the page**：无需搬动（ready）。
- **fleet: a panel newer than its envelope is not a stall**：无需搬动（ready）。
- **fleet: a panel tail read by sample is certified against a full scan**：无需搬动（ready）。
- **fleet: a partial-index commit cannot silently shrink the tree**：无需搬动（ready）。
- **fleet: a stand-in declared in the old shape is named, not trusted**：无需搬动（ready）。
- **fleet: bm-a's chain runner is the shared leg list, not a snapshot**：无需搬动（ready）。
- **fleet: health writer runs before the panel that reads it**：无需搬动（ready）。
- **fleet: heartbeat epoch fields present**：无需搬动（ready）。
- **fleet: machine-health face is machine-keyed, not a nesting generator**：无需搬动（ready）。
- **fleet: machine-health gate leg wired into the S6 chain**：无需搬动（ready）。
- **fleet: oversight writer's deployed copy tracks its source**：无需搬动（ready）。
- **fleet: panel carries the machine-health verdict, not a row count**：无需搬动（ready）。
- **fleet: the board page carries the full scan's holder count**：无需搬动（ready）。
- **fleet: the tree-shrink push gate is installed in both repos**：无需搬动（ready）。
- **fleet: this repo's last 20 commits lost no tree**：无需搬动（ready）。
- **harness: a page behind its ticket's quote session is named, never called a lie**：无需搬动（ready）。
- **harness: the funding leg forgives a trip stamp, never a real gap**：无需搬动（ready）。
- **memory: CODELY.md structure intact**：无需搬动（ready）。
- **meta: a page is certified against the one build it names, not across two**：无需搬动（ready）。
- **paper: pipeline selftest**：无需搬动（ready）。
- **pool: the deliverable reconciliation runs before anything counts pool ready**：无需搬动（ready）。
- **product: CPU work-hours are recomputable and every batch names a file**：无需搬动（ready）。
- **product: E196 carrier verdict is recomputable from its own gate**：无需搬动（ready）。
- **product: E198 cross-panel verdict is recomputable from its own gate**：无需搬动（ready）。
- **product: E199 detection floor is recomputable from its own gate**：无需搬动（ready）。
- **product: E222 sign-PIT verdict is recomputable from its own gate**：无需搬动（ready）。
- **product: E223 sign-enum verdict is recomputable from its own arm table**：无需搬动（ready）。
- **product: E224 sign-ordering transfer is recomputable from the per-period table**：无需搬动（ready）。
- **product: E227 sign ordering across cells is recomputable from the per-cell arm tables**：无需搬动（ready）。
- **product: E229 the quotable subset is priced against the full vector**：无需搬动（ready）。
- **product: E236 the sign-vector re-selection procedure is priced**：无需搬动（ready）。
- **product: E246 drawdown band reaches both trading pages**：无需搬动（ready）。
- **product: E271 the width ruler reaches both order documents**：无需搬动（ready）。
- **product: E272 each sheet says what its pairing could have detected**：无需搬动（ready）。
- **product: E298 concentration face re-derives its own verdict, and its sleeve arm really carries the top names**：无需搬动（ready）。
- **product: ETF book registry published**：无需搬动（ready）。
- **product: ETF live-book cash leg is priced off the repo panel's own close**：无需搬动（ready）。
- **product: ETF live-book page says how many independent bets the holdings are**：无需搬动（ready）。
- **product: a book face cannot be green on a panel it no longer measures**：无需搬动（ready）。
- **product: a copy that lags its own lane reaches the page, the board line and the printed run**：无需搬动（ready）。
- **product: a de-levered book is told apart from a well-timed one**：无需搬动（ready）。
- **product: a fixed fraction is only an adoption if it survives out of sample**：无需搬动（ready）。
- **product: a lane green inside its own window says how much slack is left on the board, not only on the board's markdown**：无需搬动（ready）。
- **product: a lane takeover declares whose disk holds the rows**：无需搬动（ready）。
- **product: a page section on an older bar is a note off the writer, a red on it**：无需搬动（ready）。
- **product: a restated forward bar says how far the chain moved**：无需搬动（ready）。
- **product: a rewritten mark keeps the value it replaced**：无需搬动（ready）。
- **product: a stale swap leg says who can move it, and a leg with its own producer is not told to wait for a file**：无需搬动（ready）。
- **product: a survival verdict stands on a reproduced shared cell**：无需搬动（ready）。
- **product: astock panel states its coverage, not just its date**：无需搬动（ready）。
- **product: both priced blocks name the roll mask they were measured under (r1694)**：无需搬动（ready）。
- **product: both reader faces state which price panel their numbers sit on**：无需搬动（ready）。
- **product: card amount column is executable money**：无需搬动（ready）。
- **product: card reconciles its two 2015-2019 readings**：无需搬动（ready）。
- **product: carry sleeve funding line (every number re-derived)**：无需搬动（ready）。
- **product: carry sleeve funding line (selftest)**：无需搬动（ready）。
- **product: carry sleeve integer ladder (every cell re-derived)**：无需搬动（ready）。
- **product: carry sleeve integer ladder (selftest)**：无需搬动（ready）。
- **product: carry sleeve margin arm (selftest)**：无需搬动（ready）。
- **product: carry sleeve margin arm (which floor wins, re-derived)**：无需搬动（ready）。
- **product: carry sleeve sizing ruler (every consequence re-derived)**：无需搬动（ready）。
- **product: carry sleeve sizing ruler adopted (selftest)**：无需搬动（ready）。
- **product: carry-vs-ETF swap rulers (face re-derived from its inputs)**：无需搬动（ready）。
- **product: carry-vs-ETF swap rulers (selftest)**：无需搬动（ready）。
- **product: cash placement is reconciled against the book, and an unread account is not a zero gap**：无需搬动（ready）。
- **product: cash-leg ladder verdict is the panels' own rolls, not a typed-in answer**：无需搬动（ready）。
- **product: closed-axes face refuses a missing axis (selftest 19 legs)**：无需搬动（ready）。
- **product: closed-axes verdict re-derived from the four faces it quotes**：无需搬动（ready）。
- **product: dashboard carries the marks coverage gap**：无需搬动（ready）。
- **product: data lag audit face published**：无需搬动（ready）。
- **product: data lane freshness board agrees with the lanes and the calendar**：无需搬动（ready）。
- **product: every face a reader holds says whether the width's family was one world**：无需搬动（ready）。
- **product: every index panel reaches the futures panel's last bar**：无需搬动（ready）。
- **product: every lane names one host before any task is re-enabled**：无需搬动（ready）。
- **product: every marks hole carries a cause from the lane's own ownership contract**：无需搬动（ready）。
- **product: flip-rate arms cut flips, not exposure, and the cut is priced**：无需搬动（ready）。
- **product: futures TSMOM face is current, capped and not an order**：无需搬动（ready）。
- **product: futures TSMOM shadow face keeps its sizing rules**：无需搬动（ready）。
- **product: futures contract panel has a producer (selftest 8 legs)**：无需搬动（ready）。
- **product: futures contract refresh re-derived from the panel**：无需搬动（ready）。
- **product: futures overlay sweep keeps its blend arithmetic**：无需搬动（ready）。
- **product: how long a holder waits under water, re-derived from the published rows**：无需搬动（ready）。
- **product: index daily panel has a producer (selftest)**：无需搬动（ready）。
- **product: index-futures carry desk sheet (selftest)**：无需搬动（ready）。
- **product: index-futures proxy noise (selftest 21 legs)**：无需搬动（ready）。
- **product: index-futures proxy noise re-derived**：无需搬动（ready）。
- **product: index-futures roll cost measured (selftest 24 legs)**：无需搬动（ready）。
- **product: index-futures roll gaps (selftest 17 legs)**：无需搬动（ready）。
- **product: index-futures roll-gap states re-derived**：无需搬动（ready）。
- **product: live paper book states its price lag**：无需搬动（ready）。
- **product: marks coverage face names its holes**：无需搬动（ready）。
- **product: one lot is priced beside the fee floor, and the page prints it**：无需搬动（ready）。
- **product: open-fill gate names its evidence tier and the bar tier's prices are the bars'**：无需搬动（ready）。
- **product: overlay breakeven is recomputable from its own ladder**：无需搬动（ready）。
- **product: overlay no-trade band is priced on both sides of the trade**：无需搬动（ready）。
- **product: overlay sweep sells risk and publishes the equal-risk reading**：无需搬动（ready）。
- **product: prior-signs face re-derives its verdict and the prior key is the textbook key**：无需搬动（ready）。
- **product: roll cost does not claim a verdict it cannot have (r1698)**：无需搬动（ready）。
- **product: roll tenor prices both policies (selftest 27 legs)**：无需搬动（ready）。
- **product: roll tenor re-derives from the contract panel**：无需搬动（ready）。
- **product: shock face prices its shocks off its own beta and ticket**：无需搬动（ready）。
- **product: staggered book states when each sleeve next turns**：无需搬动（ready）。
- **product: the CEO page carries today's actions, not only the full build**：无需搬动（ready）。
- **product: the CEO page prices the book's idle cash (r1908)**：无需搬动（ready）。
- **product: the CEO page prices the carry book's zero (funding line)**：无需搬动（ready）。
- **product: the CEO page prices the cash the sheet leaves behind**：无需搬动（ready）。
- **product: the CEO page prices the whole book in one line**：无需搬动（ready）。
- **product: the CEO page prints what following the book means tomorrow (lots + cash)**：无需搬动（ready）。
- **product: the CEO page says what part of the build order is premium**：无需搬动（ready）。
- **product: the CEO page shows where the six signs came from and what peeking pays**：无需搬动（ready）。
- **product: the CEO-page quote audit runs after the pages it audits**：无需搬动（ready）。
- **product: the CEO-page quote gate runs after the sweep and owns a baseline**：无需搬动（ready）。
- **product: the account the sheet never sells reaches the CEO page**：无需搬动（ready）。
- **product: the battle report carries the book it is about**：无需搬动（ready）。
- **product: the block band is rebuilt before the card embeds it**：无需搬动（ready）。
- **product: the block family is complete, not merely self-consistent**：无需搬动（ready）。
- **product: the book a person holds is priced in money (r1900)**：无需搬动（ready）。
- **product: the book envelope says whose book it describes**：无需搬动（ready）。
- **product: the book's CAGR is split into overnight / intraday / quiet / toll and the split closes to the same total**：无需搬动（ready）。
- **product: the book's headline is priced one bar in the future, and the gap is measured**：无需搬动（ready）。
- **product: the calendar split is re-read at matched candidate width, as a distribution rather than a point**：无需搬动（ready）。
- **product: the capital face prices both roll masks and the page prints both (r1695)**：无需搬动（ready）。
- **product: the card says which book its own width is not**：无需搬动（ready）。
- **product: the card says which research questions its numbers already answered**：无需搬动（ready）。
- **product: the card states which of its two arms the desk can trade**：无需搬动（ready）。
- **product: the card table prices both arms in the headline rows**：无需搬动（ready）。
- **product: the card's title names the bar its legs come from**：无需搬动（ready）。
- **product: the carry split reproduces the ticket and stays ordered**：无需搬动（ready）。
- **product: the compute audit reads the claim face, not just the pool row**：无需搬动（ready）。
- **product: the dashboard says which bar the three papers were priced on**：无需搬动（ready）。
- **product: the day-of-month face counts sessions, not name-days**：无需搬动（ready）。
- **product: the desk sheet refuses a gap instead of printing zero (r1701)**：无需搬动（ready）。
- **product: the executable ticket decomposes its own headline**：无需搬动（ready）。
- **product: the execution-claim face runs on the card it reads, not ahead of it**：无需搬动（ready）。
- **product: the expectation table's rows name the ruler that priced each one**：无需搬动（ready）。
- **product: the fill is sliced over k opens and priced against the declared arm**：无需搬动（ready）。
- **product: the flip damper is adopted or rejected by path cells, not one run**：无需搬动（ready）。
- **product: the forward ledger publishes its own noise floor**：无需搬动（ready）。
- **product: the human faces quote the measured draw-tail share, not the impression**：无需搬动（ready）。
- **product: the idle-cash money reaches the CEO page, same numbers**：无需搬动（ready）。
- **product: the index-futures page carries the capital face's numbers (r1688)**：无需搬动（ready）。
- **product: the ladder advice on the ticket carries the price measured since**：无需搬动（ready）。
- **product: the lane-silence face names whether the lane is switched off**：无需搬动（ready）。
- **product: the live quote is priced before the page that prints it**：无需搬动（ready）。
- **product: the live-quote section and the panel's own lane agree on tonight**：无需搬动（ready）。
- **product: the live-width gate tells a re-issued ticket from a hand edit**：无需搬动（ready）。
- **product: the matched-width control is laddered across book widths, with the invariance of the gap published beside it**：无需搬动（ready）。
- **product: the mid-month gap arrives split into timing and selection**：无需搬动（ready）。
- **product: the missing bar is not a fill an operator could have chosen**：无需搬动（ready）。
- **product: the next sheet starts from the account as it stands, not its last trade**：无需搬动（ready）。
- **product: the observation-rate ladder prices its own resolution**：无需搬动（ready）。
- **product: the off-book era leg is on the chain and publishes a cross-era verdict**：无需搬动（ready）。
- **product: the one-bar price is not recoverable by smoothing the causal score**：无需搬动（ready）。
- **product: the operator page prices the basket the ticket actually holds**：无需搬动（ready）。
- **product: the operator page prices the cash half on the sheet's own three rates**：无需搬动（ready）。
- **product: the operator page prints how long the wait is**：无需搬动（ready）。
- **product: the operator page says how much money this book needs**：无需搬动（ready）。
- **product: the operator page says the entry gate sets capacity, not return**：无需搬动（ready）。
- **product: the operator page says whether this book was runnable in 2020**：无需搬动（ready）。
- **product: the operator page says which window its numbers came from**：无需搬动（ready）。
- **product: the order sheet carries the permission it must obey**：无需搬动（ready）。
- **product: the order sheet prices money itself (1M/3M/10M/30M)**：无需搬动（ready）。
- **product: the order sheet prices the bar it says it is priced on**：无需搬动（ready）。
- **product: the order sheet prices the cash half in CNY at today's rate**：无需搬动（ready）。
- **product: the order sheet states whether the book may take new capital**：无需搬动（ready）。
- **product: the order ticket discloses how many bets the sleeve holds**：无需搬动（ready）。
- **product: the overnight gap is priced as the last channel between decide and fill**：无需搬动（ready）。
- **product: the page answers whether the commodity sleeve needs its own gate**：无需搬动（ready）。
- **product: the page names which half refused the carry product (r1910)**：无需搬动（ready）。
- **product: the page never says 'nothing to do today' on the day it names as the rebalance**：无需搬动（ready）。
- **product: the page prices its break-even at the rate the ticket pays**：无需搬动（ready）。
- **product: the page prices the cost assumption under every number**：无需搬动（ready）。
- **product: the page says how many names the lot grid actually holds**：无需搬动（ready）。
- **product: the page says what fills at the open and whose book that is**：无需搬动（ready）。
- **product: the page says whose CAGR it is quoting (top-3 share and both deletions)**：无需搬动（ready）。
- **product: the page shows the book's own luck distribution, not just a point**：无需搬动（ready）。
- **product: the page tells a de-levered book from a well-timed one**：无需搬动（ready）。
- **product: the page's own pricing day is read through one reader**：无需搬动（ready）。
- **product: the paper puts today-words on the page's own day**：无需搬动（ready）。
- **product: the percentile face is rebuilt before the ticket embeds it**：无需搬动（ready）。
- **product: the premium face is re-derived before it is judged**：无需搬动（ready）。
- **product: the price of waiting reaches the sheet that trades**：无需搬动（ready）。
- **product: the printed cap is reconciled with the priced book on both faces**：无需搬动（ready）。
- **product: the prior-signs page names the arm peeking picks and its OOS number**：无需搬动（ready）。
- **product: the promised fill and the fill receipt are both recomputable**：无需搬动（ready）。
- **product: the reform direction audit cannot report a clean readout over a losing admission**：无需搬动（ready）。
- **product: the regime cap is compared with the money actually deployed**：无需搬动（ready）。
- **product: the row the 11-08 enable decision reads agrees with the declaration**：无需搬动（ready）。
- **product: the row the operator reads has a full-window number in its full window column**：无需搬动（ready）。
- **product: the seat face's cutoff is the bar it read**：无需搬动（ready）。
- **product: the sheet a person holds says whether it is a missed run (r1890)**：无需搬动（ready）。
- **product: the sheet issued from the card is that card's own book**：无需搬动（ready）。
- **product: the sheet names the fill day it already knows**：无需搬动（ready）。
- **product: the sheet prints what it pays and where that price sits in history**：无需搬动（ready）。
- **product: the sheet says how far its k sits from the ruler that signed it, and the zone is re-derived from the numbers it prints**：无需搬动（ready）。
- **product: the sheet's swap-section freshness is re-derived, not remembered**：无需搬动（ready）。
- **product: the sheet's trigger section names which scope its threshold has**：无需搬动（ready）。
- **product: the six seats' idle cash can be priced (selftest)**：无需搬动（ready）。
- **product: the sleeve-gate answer survives a moved decision grid**：无需搬动（ready）。
- **product: the state tilt prices the toll it would need**：无需搬动（ready）。
- **product: the state tilt publishes its own effective sample size**：无需搬动（ready）。
- **product: the substitution rulers reach the CEO page (r1933)**：无需搬动（ready）。
- **product: the swap block prints the face's own build stamp**：无需搬动（ready）。
- **product: the swap page states its verdict and the ETF share it costs**：无需搬动（ready）。
- **product: the tenor verdict is on the page (r1931)**：无需搬动（ready）。
- **product: the three papers print the day each was priced on, and can disagree**：无需搬动（ready）。
- **product: the ticket prints which sizing road the book runs**：无需搬动（ready）。
- **product: the ticket says what it costs to open and which line is executable**：无需搬动（ready）。
- **product: the ticket's positions edge names a missed run, not a content mismatch**：无需搬动（ready）。
- **product: the turn-of-month overlay keeps its rule, its toll and its OOS record**：无需搬动（ready）。
- **product: the two adjudications on the sheet read the same panel**：无需搬动（ready）。
- **product: the two live widths are priced on one ruler and the gap is inside the engines' own disagreement**：无需搬动（ready）。
- **product: the veto verdict only greens when it beats the random drop too (r1864c)**：无需搬动（ready）。
- **product: the vol overlay's tail is priced on the same draw as its middle**：无需搬动（ready）。
- **product: the vol window is judged on more than one decision calendar**：无需搬动（ready）。
- **product: the volatility gate separates held days from episodes**：无需搬动（ready）。
- **product: the voltail family is complete, not merely self-consistent**：无需搬动（ready）。
- **product: the wait fee lands on the ticket's own size (r1913)**：无需搬动（ready）。
- **product: the width family is re-derived before the page that quotes it**：无需搬动（ready）。
- **product: the width ladder is split into timing and selection, so its movement is attributed to a named part**：无需搬动（ready）。
- **product: the width ladder names why it cannot be quoted, and the buffer line is tested on a point it never saw**：无需搬动（ready）。
- **product: the width sign is read against a noise score, not just another grid**：无需搬动（ready）。
- **product: the width survival test measures every clock it judges**：无需搬动（ready）。
- **product: the window grid's floor is the engine's, measured not assumed**：无需搬动（ready）。
- **product: the worst 1% is published on the block arms**：无需搬动（ready）。
- **product: three faces of one book price one panel, and the digest can move**：无需搬动（ready）。
- **product: treasury curve verdict is re-derived from its own criteria (r1691)**：无需搬动（ready）。
- **rules: T+0 list**：无需搬动（ready）。
- **suite: a repeated selftest rides the first judgement (r1602)**：无需搬动（ready）。
- **suite: a selftest started early is already answered when its leg arrives (r1603)**：无需搬动（ready）。
- **tooling: every harness subprocess capture pins encoding and errors**：无需搬动（ready）。
- **config: paths**：无需搬动（ready）。
- **product: ETF book legs wired into the S6 chain**：无需搬动（ready）。
- **product: ETF live-book page current and its money closes**：无需搬动（ready）。
- **product: ETF live-book page says whether to trade today**：无需搬动（ready）。
- **product: ETF live-book stress rows are their own percentages x capital**：无需搬动（ready）。
- **product: ETF live-book yuan figures are its own percentages x its own capital**：无需搬动（ready）。
- **product: both reader faces print the cut that picks the universe, recomputed**：无需搬动（ready）。
- **config: param grid**（one_hop）
  - `combos` ← 第 18 条语句（行 1239-1239）
  - 未归因名字：`len`
- **data: core ETF pool**（one_hop）
  - `core_files` ← 第 26 条语句（行 1245-1246）
  - 未归因名字：`len`
- **engine: deterministic**（chained）
  - `det_ok` ← 第 61 条语句（行 1298-1299）·它自己还读：`r1`, `r2`
- **engine: emptying cutoff refused (RW-2)**（one_hop）
  - `raised` ← 第 81 条语句（行 1339-1339）
- **engine: legacy keyset intact without evidence_cutoff (RW-2)**（chained）
  - `r1` ← 第 55 条语句（行 1291-1291）·它自己还读：`window`
- **exit: P1 signal_reversal beats P2 stop (RW-7)**（chained）
  - `_p12` ← 第 132 条语句（行 1444-1445）·它自己还读：`cfg`
- **exit: P2 stop_loss beats P3 take_profit (RW-7)**（chained）
  - `_p23` ← 第 134 条语句（行 1449-1451）·它自己还读：`cfg`
  - 未归因名字：`abs`
- **exit: P4 time_decay beats P5 loss_time_stop (RW-7)**（chained）
  - `_p45` ← 第 136 条语句（行 1456-1456）·它自己还读：`cfg`
- **exit: P6 global_hard_limit terminal tier (RW-7)**（chained）
  - `_p6` ← 第 138 条语句（行 1460-1460）·它自己还读：`cfg`
- **exit: hard stop -8%**（chained）
  - `a3` ← 第 46 条语句（行 1281-1281）·它自己还读：`cfg`
- **exit: hold otherwise**（chained）
  - `a4` ← 第 47 条语句（行 1282-1282）·它自己还读：`cfg`
- **exit: loss 8d force-close**（chained）
  - `a1` ← 第 44 条语句（行 1279-1279）·它自己还读：`cfg`
- **exit: tiered take-profit**（chained）
  - `a2` ← 第 45 条语句（行 1280-1280）·它自己还读：`cfg`
  - 未归因名字：`abs`
- **fleet: a thin face reads as UNKNOWN, not as a calm row**（one_hop）
  - `_tf` ← 第 179 条语句（行 1765-1793）
  - 未归因名字：`Exception`, `open`, `str`
- **fleet: live machine-health rows carry every pinned field**（one_hop）
  - `_mf` ← 第 265 条语句（行 5193-5267）
  - 未归因名字：`Exception`, `bool`, `len`, `str`
- **gate: rejections raise, never silently drop (RW-7)**（one_hop）
  - `_rej` ← 第 143 条语句（行 1469-1469）
  - 未归因名字：`all`, `list`
- **harness: the suite's own wall clock names its slow legs**（one_hop）
  - `_saved_perf` ← 第 4 条语句（行 889-889）
- **network: detector**（one_hop）
  - `nt` ← 第 156 条语句（行 1516-1516）
- **network: status readable**（one_hop）
  - `st` ← 第 158 条语句（行 1518-1518）
  - 未归因名字：`dict`, `isinstance`
- **network: traffic gate**（one_hop）
  - `ok_small` ← 第 160 条语句（行 1520-1520）
  - 未归因名字：`bool`, `isinstance`
- **panel gate: stale in-service member refused (RW-4)**（chained）
  - `res_stale` ← 第 102 条语句（行 1377-1378）·它自己还读：`_pg`, `stale_fx`
  - 未归因名字：`any`
- **panel gate: twins refused, len(set)==len(list) (RW-4)**（chained）
  - `res_twin` ← 第 100 条语句（行 1374-1374）·它自己还读：`_pg`, `syn`
  - 未归因名字：`any`
- **product: ETF registry runs after every face it summarises**（one_hop）
  - `_rg` ← 第 218 条语句（行 3866-3876）
  - 未归因名字：`Exception`, `str`
- **product: ETF registry says when the staggered book turns**（one_hop）
  - `_rg` ← 第 218 条语句（行 3866-3876）
  - 未归因名字：`Exception`, `all`, `len`, `str`
- **product: a bar restated after settling reaches the ticket's own ledger line**（one_hop）
  - `_stamp30` ← 第 347 条语句（行 9551-9562）
  - 未归因名字：`Exception`, `PATHS`, `dict`, `float`, `int`, `isinstance`, `len`, `list`
- **product: a stale cohort is named, not counted**（one_hop）
  - `_la` ← 第 252 条语句（行 4718-4727）
  - 未归因名字：`Exception`, `all`, `isinstance`, `len`, `list`, `min`, `str`
- **product: every candidate edge states the file it was read from**（one_hop）
  - `_sig` ← 第 244 条语句（行 4609-4620）
  - 未归因名字：`Exception`, `all`, `float`, `int`, `isinstance`, `len`, `sorted`, `str`
- **product: the CEO page carries today's market risk tape**（chained）
  - `v` ← 第 59 条语句（行 1296-1296）·它自己还读：`r1`
  - 未归因名字：`Exception`, `PATHS`, `int`, `open`, `repr`, `str`
- **product: the CEO page still prints where in the day the money is earned**（one_hop）
  - `_pg31` ← 第 373 条语句（行 11168-11214）
  - 未归因名字：`Exception`, `PATHS`, `_la31`, `_tf31`, `open`, `repr`, `sorted`
- **product: the adopted flip damper reaches the live shadow book**（chained）
  - `m` ← 第 57 条语句（行 1293-1293）·它自己还读：`r1`
  - 未归因名字：`Exception`, `_F`, `_P`, `_S`, `_json`, `float`, `int`, `open`
- **product: the forward face prices what its horizon can resolve, not only bars**（one_hop）
  - `_sig` ← 第 244 条语句（行 4609-4620）
  - 未归因名字：`Exception`, `all`, `float`, `int`, `isinstance`, `len`, `sorted`, `str`
- **product: the page itself names the sections that sit on an older bar**（one_hop）
  - `_SB78` ← 第 361 条语句（行 10541-10593）
  - 未归因名字：`Exception`, `__file__`, `open`, `repr`
- **product: the paired-rows family on disk is complete and stray-proof**（one_hop）
  - `_tf` ← 第 179 条语句（行 1765-1793）
  - 未归因名字：`Exception`, `_NE4`, `len`, `open`, `str`
- **product: the price of waiting reaches the page the CEO opens (r1893)**（chained）
  - `v` ← 第 59 条语句（行 1296-1296）·它自己还读：`r1`
  - 未归因名字：`Exception`, `float`, `len`, `max`, `open`, `repr`, `sorted`, `zip`
- **product: whose disk the lane numbers are on reaches both human faces**（one_hop）
  - `_g2` ← 第 237 条语句（行 4421-4438）
  - 未归因名字：`Exception`, `_dlf`, `bool`, `open`, `sorted`, `str`
- **rules: fee schedule sane**（chained）
  - `cost_rate` ← 第 39 条语句（行 1272-1272）·它自己还读：`fee`
- **config: combo_hash deterministic**（chained）
  - `h1` ← 第 20 条语句（行 1241-1241）·它自己还读：`combos`
  - `h2` ← 第 21 条语句（行 1241-1241）·它自己还读：`combos`
  - 未归因名字：`len`
- **data: freshness**（chained）
  - `latest` ← 第 34 条语句（行 1266-1266）·它自己还读：`latest_dates`
  - `stale_days` ← 第 35 条语句（行 1267-1267）·它自己还读：`latest`
- **engine: T+1 respected**（chained）
  - `r1` ← 第 55 条语句（行 1291-1291）·它自己还读：`window`
  - `same_day` ← 第 64 条语句（行 1303-1304）·它自己还读：`r1`
  - 未归因名字：`len`
- **engine: exits fill at T+1 open (RW-1)**（chained）
  - `bad_exit_px` ← 第 67 条语句（行 1309-1311）·它自己还读：`open_px`, `r1`
  - `r1` ← 第 55 条语句（行 1291-1291）·它自己还读：`window`
  - 未归因名字：`len`
- **engine: grid legacy divergence = declared 0.041bp (RW-3)**（chained）
  - `_gp` ← 第 307 条语句（行 6791-6819）
  - `grid_delta` ← 第 92 条语句（行 1357-1358）·它自己还读：`_gp`, `_lp`, `bar_notional`
  - 未归因名字：`abs`
- **engine: single-source cost parity (RW-3)**（chained）
  - `engine_side` ← 第 87 条语句（行 1349-1349）·它自己还读：`bar_notional`, `cost_rate`
  - `parity_ok` ← 第 91 条语句（行 1354-1356）·它自己还读：`_lp`, `active_faces`
  - 未归因名字：`cost_spec`
- **gate: daily_loss_breaker boundary (RW-7)**（one_hop）
  - `RISK` ← 第 130 条语句（行 1441-1441）
  - `_g` ← 第 140 条语句（行 1464-1464）
- **gate: emit_order_sheet is the sole gated exit (RW-7)**（chained）
  - `_emit_refused` ← 第 149 条语句（行 1496-1496）
  - `_wrote` ← 第 152 条语句（行 1502-1510）·它自己还读：`_ord_ok`, `_tf`
- **gate: halted day still lets exits through (RW-7)**（chained）
  - `_gsell` ← 第 147 条语句（行 1491-1492）·它自己还读：`_halt_sell`
  - `_halt_sell` ← 第 146 条语句（行 1490-1490）
- **harness: a face rewritten mid-run is named as moved, not judged**（one_hop）
  - `_saved_t0` ← 第 6 条语句（行 902-902）
  - `_tf` ← 第 179 条语句（行 1765-1793）
  - 未归因名字：`Exception`, `open`, `repr`
- **panel gate: out-of-lock + silent-shrink refused (RW-4)**（chained）
  - `res_lock` ← 第 103 条语句（行 1379-1379）·它自己还读：`_pg`, `syn`
  - `res_shrink` ← 第 104 条语句（行 1380-1380）·它自己还读：`_pg`, `syn`
  - 未归因名字：`any`
- **data: OHLCV readable**（one_hop）
  - `bad` ← 第 31 条语句（行 1253-1253）
  - `core_files` ← 第 26 条语句（行 1245-1246）
  - `panels` ← 第 29 条语句（行 1251-1251）
  - 未归因名字：`len`
- **engine: evidence_cutoff hard truncation (RW-2)**（chained）
  - `cut_d` ← 第 70 条语句（行 1315-1315）·它自己还读：`cut_i`, `window`
  - `n_after` ← 第 71 条语句（行 1316-1316）·它自己还读：`cut_d`, `window`
  - `trunc_ok` ← 第 76 条语句（行 1321-1325）·它自己还读：`cut_d`, `meta`, `n_after`, `r3`, `r4`
- **engine: one-word bar buy dropped + sell deferred (CN-A, D-38)**（chained）
  - `_fills` ← 第 127 条语句（行 1433-1433）·它自己还读：`_r`
  - `_idx` ← 第 118 条语句（行 1414-1414）
  - `_owm` ← 第 126 条语句（行 1432-1432）·它自己还读：`_r`
  - 未归因名字：`str`
- **panel gate: real in-service panel inside frozen 48-lock (RW-4)**（chained）
  - `_pg` ← 第 165 条语句（行 1589-1602）
  - `panels` ← 第 29 条语句（行 1251-1251）
  - `res_real` ← 第 98 条语句（行 1370-1370）·它自己还读：`_pg`, `inv_real`, `panels`
  - 未归因名字：`len`
- **product: astock residual veto layer selftest (r1864c)**（chained）
  - `_rv_m` ← 第 202 条语句（行 2151-2151）·它自己还读：`_rv_out`
  - `_rv_out` ← 第 201 条语句（行 2150-2150）·它自己还读：`_rv_sel`
  - `_rv_sel` ← 第 200 条语句（行 2143-2145）
  - 未归因名字：`bool`, `int`
- **product: the sheet prints what the price did after a reading like today's**（one_hop）
  - `_md99` ← 第 383 条语句（行 12006-12127）
  - `_syms99` ← 第 383 条语句（行 12006-12127）
  - `_tk99` ← 第 383 条语句（行 12006-12127）
  - 未归因名字：`Exception`, `PATHS`, `abs`, `dict`, `enumerate`, `float`, `isinstance`, `next`
- **rules: stock fee routing sell 18.141bp / buy 13.141bp (D-39)**（chained）
  - `_d_buy` ← 第 115 条语句（行 1407-1407）·它自己还读：`_b_e`, `_fs_stk`
  - `_d_sell` ← 第 116 条语句（行 1408-1408）·它自己还读：`_fs_stk`, `_s_e`
  - `_ok_route` ← 第 112 条语句（行 1399-1404）·它自己还读：`_fs_etf`, `_fs_stk`
  - 未归因名字：`abs`, `cost_spec`
- **engine: rows actually read <= cutoff (RW-2)**（chained）
  - `cut_d` ← 第 70 条语句（行 1315-1315）·它自己还读：`cut_i`, `window`
  - `meta` ← 第 75 条语句（行 1320-1320）·它自己还读：`r3`
  - `n_read` ← 第 78 条语句（行 1329-1329）·它自己还读：`cut_d`, `window`
  - `r3` ← 第 72 条语句（行 1317-1317）·它自己还读：`cut_d`, `window`
  - `window` ← 第 54 条语句（行 1290-1290）·它自己还读：`panels`, `syms`
  - 未归因名字：`bool`, `len`, `pd`, `sorted`, `str`
- **engine: smoke backtest**（chained）
  - `eq_ok` ← 第 59 条语句（行 1296-1296）·它自己还读：`r1`
  - `keys_ok` ← 第 58 条语句（行 1294-1295）·它自己还读：`m`
  - `m` ← 第 57 条语句（行 1293-1293）·它自己还读：`r1`
  - `syms` ← 第 53 条语句（行 1289-1289）·它自己还读：`panels`
  - `tr_ok` ← 第 60 条语句（行 1297-1297）·它自己还读：`r1`
  - 未归因名字：`len`

## 这张表不回答的事

- 它只认得**字面写出**的 `check("腿名", …)`：suite 运行时计数比本表多出的腿
  （循环里拼名字的、按名单生成的）静态解析看不见，差额如实不补。
- 它不判断某条腿值不值得搬：判决来自 `results/smoke_red_recheck.bm-c.json`，
  只那张面说它是红的、且无独立命令，才值得动。
- 它不猜命令。声明式腿的 argv 由 `smoke_red_recheck.py` 从表里逐字取；
  内联腿没有 argv，所以本表只给「要搬什么」，不给「怎么跑」。
