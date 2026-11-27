# 一个钱包，两本书：从「分散值得」到「今天买什么」 (r2174 · bm-c)

r2173 把「分散」定价了：30% 双低转债 / 70% 去债 ETF，同一段重叠日历上
9.07% / SR 1.066 / MDD -9.3% / vol 8.59%，比任何一本单书都更平。但那是一张研究面。
持钱的人读完只会问下一句：**那我今天具体买多少只、多少手、剩多少钱？**

本面就是那一句的答案。它不新造任何规则：

- 转债袖用 `scripts/cb_book_ticket_floor.py` 的 `ticket_math`（10 张一手，import 不重写）；
- ETF 袖用 `results/etf_book_nobond_ticket.json` 的名单与权重（8% 波动目标的降杠杆已在权重里）；
- 拆分权重读 `results/book_pair_blend.json` 的 `best.w_cb`，本面不选权重。

## 两个读数（bar 2026-11-26，两个父面同日）

### 1. 公布的「最小钱包」差 1 元

blend 面印 `min_wallet_cny = 86,167`（25,850.20 / 0.30 按元向下取整）。
整手网格不取整：86,167 × 0.30 = 25,850.10，比最贵那只转债的一手门槛少 0.10 元，
于是它拿到 **0 手**——钱包里只有 19 只转债，不是回测里那 20 只的书。
86,168 × 0.30 = 25,850.40 才拿满 20 只。

| 钱包 | 转债袖 | 判词 |
|---|---|---|
| 86,167 | 19/20 | PARTIAL |
| 86,168 | 20/20 | HOLDS_WITH_STRAND |

这就是 r1780「正确的零不是一个能下单的票」的同一面：凡是规则算出的门槛，
都要用户能下的**整数最小单位**再问一遍。

### 2. 50,000 元买到的不是混合书

30% 袖 = 15,000 元，低于 25,850 元的一手门槛 → 一只转债都买不到，
钱包退化成 100% ETF 书，且整手搁浅 30.4%。也就是说 30/70 这个小钱包规模下**不存在**。

## 两个现金口径必须分开印

| 口径 | 来源 | 是不是缺陷 |
|---|---|---|
| 设计内现金 | ETF 袖的 8% 波动目标主动降杠杆，本 bar 约 24.9% 的袖内预算 | 不是，是设计 |
| 整手搁浅 | 100 股 / 10 张的整手网格买不满预算的余数 | 是，`STRAND_CAP=2%` 判它 |

混在一起印，读者会把「波动目标要的现金」读成「票买不进」，或反过来把真搁浅当成设计。
本面把 `cash_cny` 拆成 `design_cash_cny` 与 `lot_grid_cash_cny` 两个数。

## 契约

- 三个输入（两张票面 + blend 面）的字节戳任一变动 → `CHECK STALE:` + rc3；链腿据此付费补写。
- 页面由 `render_md` 逐字生成，手改一位即 rc1（`CHECK FAILED`，不含 STALE 字样）。
- **两个父面不同日 → `build()` 拒发**（`SLEEVES_OFF_BY_DAYS`）。这条不是摆设：
  本轮之前 ETF 票面停在 11-20 而转债在 11-26，差六天，两个日子拼成的「一个钱包」是假的。

## 顺带修掉的一条烂面

`results/etf_book_nobond_ticket.json` 是已发布票面，却六天没动、名单已与父书不符
（父书 11-26 换成 `562060 / 513690`，票面还印 `562550 / 159307`）。根因两层：
**链上没有腿**（写者在盘无人跑），以及**它的 check 把「父书换名」判成自相矛盾**
（印 `check FAIL: picks ... are not the parent's book`，不含 STALE，链永远不付费补写）。

修法：check 先看父面是否移动（`live_picks.as_of` / `evidence_cutoff`），移动则归
`stale` 并说出「the book rotated since this ticket was priced: A -> B」；日期相同而名字不同
仍是真缺陷。随后补 `etf_nobond_ticket` 与 `paired_book_ticket` 两条链腿
（紧随 `etf_nobond_vt`，保证父书先重价）。

## 未做 / 未验证

- 转债袖没有券商账单依据（父面不印佣金），本面只为 ETF 袖计 `max(5 元, 3bp)`，转债袖费记 0.0；
- 两个袖之间的调仓成本未建模（与 blend 面同口径）；
- 30/70 是重叠窗样本内最优，不是定律；
- 只读最后一根 bar 的名单，换仓后需重跑（check 会转 STALE）；
- 未做逐笔撮合（次日开盘 + 冲击 + 最低佣金）。

正身：`scripts/paired_book_ticket.py`（selftest 19/19）· `results/paired_book_ticket.json|md` ·
`qa/paired-book-ticket-r2174.md` · `Tools/s6_chain_bmc.py` 腿 `etf_nobond_ticket` / `paired_book_ticket` ·
方法卡 `knowledge/METHODOLOGY_ASSETS.md` E-20261127-r2174。
