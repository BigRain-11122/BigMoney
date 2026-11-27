# QA —— 一个钱包，两本书的合并票 (r2174 · bm-c)

产物：`scripts/paired_book_ticket.py` · `results/paired_book_ticket.json` · `results/paired_book_ticket.md`
顺带修复：`scripts/etf_book_nobond_ticket.py`（check 词）+ `Tools/s6_chain_bmc.py`（两条新腿）

## 0. 本轮先修的真缺陷（不是新功能）

`results/etf_book_nobond_ticket.json` 是已发布的票面，却停在 **2026-11-20**，其五只名单
是 `159549 / 159207 / 562550 / 515300 / 159307`，而它的父书 `results/etf_nobond_vt.json`
在 11-26 已换名成 `159207 / 159549 / 515300 / 562060 / 513690`。

根因两层：

1. **写者在盘、链上无腿**——`etf_book_nobond_ticket.py` 从未被 `Tools/s6_chain_bmc.py` 跑过，
   所以父书每天换名，票面永远停在写出那天（r2171 同族：`no_driver`）。
2. **它的 check 把「父书轮换」判成自相矛盾**——印 `check FAIL: - picks [...] are not the
   parent's book [...]`，不含 STALE 字样，而链腿只在文本含 `STALE` 时才付费补写
   （r1934/r1850 契约）。即使补了腿，这条腿也会永久红而永不刷新。

修法：`check` 先判父面是否移动（live_picks.as_of / evidence_cutoff），移动则把名单差异归入
`stale` 并说出「the book rotated since this ticket was priced: A -> B」；日期相同而名字不同
仍是 `probs`（真缺陷）。修后实测：

```
python scripts/etf_book_nobond_ticket.py check     -> STALE rc3（点名旧名单/新名单与两个日期）
python scripts/etf_book_nobond_ticket.py run       -> scale 0.7507 cash 0.2493 / TRADABLE_AT_1M
python scripts/etf_book_nobond_ticket.py check     -> ok rc0
python scripts/etf_book_nobond_ticket.py selftest  -> PASS 19/19
```

## 1. 自检

```
python scripts/paired_book_ticket.py selftest
paired_book_ticket selftest 19/19
```

| 腿 | 问的问题（答错就红） |
|---|---|
| L1 | 整手算术：10,000 元、权重 0.25/0.25、一手 200/400 → 12 手 / 6 手 |
| L2 | 钱的行恒等式：搁浅额 = 预算 − 已投，且不等于设计内现金 |
| L2b | 权重和 0.5 时，设计内现金必须是 5,000，且**不许**被算成搁浅 |
| L3 | 手续费地板：100 元票 3bp=0.03，5 元地板必须胜 |
| L4 | 预算不够一手→买 0 手并标 `fits=false`，不许四舍五入成 1 手 |
| L5-L7 | 判词阶梯：全拿且搁浅小→HOLDS_THE_BLEND；搁浅 5%→HOLDS_WITH_STRAND；转债袖 0 只→CB_SLEEVE_TOO_SMALL；转债袖 12/20→PARTIAL；ETF 袖 0 只→ETF_SLEEVE_TOO_SMALL |
| L8 | 最小钱包 = 一手门槛 / 袖权重（25,850.2/0.30 = 86,167.33） |
| L9 | 转债袖必须是 `cb_book_ticket_floor.ticket_math` 的数（import 不是重写） |
| L10 | 两个父面不同日→`bars_align` 必须拒绝（含缺 bar） |
| L11-L13 | **取整方向**：blend 印的 86,167 必须只拿 3/4（合成四名情形），86,168 必须拿 4/4 |

## 2. 真面读数（bar 2026-11-26，两个父面同日）

拆 30% 转债 / 70% ETF（权重取自 `book_pair_blend.best.w_cb`，本面**不选**权重）：

| 钱包 | 判词 | ETF 袖 | 转债袖 | 已投 | 现金 | 其中设计内 | 其中整手搁浅 |
|---|---|---|---|---|---|---|---|
| 50,000 | CB_SLEEVE_TOO_SMALL | 5/5 | **0/20** | 26,096 | 47.8% | — | 30.4% |
| 86,167 | PARTIAL | 5/5 | **19/20** | 65,151 | 24.4% | — | 6.9% |
| 86,168 | HOLDS_WITH_STRAND | 5/5 | 20/20 | 66,443 | 22.9% | — | 5.4% |
| 100,000 | HOLDS_WITH_STRAND | 5/5 | 20/20 | 73,911 | 26.1% | — | 8.6% |
| 200,000 | HOLDS_WITH_STRAND | 5/5 | 20/20 | 152,502 | 23.7% | — | 6.3% |
| 500,000 | HOLDS_WITH_STRAND | 5/5 | 20/20 | 400,980 | 19.8% | — | 2.4% |
| 1,000,000 | HOLDS_THE_BLEND | 5/5 | 20/20 | 814,111 | 18.6% | — | 1.1% |

### 本轮最重要的读数：公布的「最小钱包」差 1 元

`book_pair_blend` 印 `min_wallet_cny = 86,167`（=25,850.20 / 0.30 按元向下取整）。
整手网格不取整：86,167 × 0.30 = **25,850.10**，比 25,850.20 的一手门槛少 0.10 元，
于是最贵那只转债拿到 **0 手**——钱包里只有 19 只，不是回测里那 20 只的书。
86,168 × 0.30 = 25,850.40 才拿满。

这不是新坑，是 r1780 那条律的同一面：凡是「规则算出的门槛」，都要用**能下单的整数**再问一遍。
本面把它落成 `floor_check` 块（published / exact / ceil / 三个名单数 / gap=1 元），
断言腿 L11-L13 用合成四名情形钉死取整方向。

### 第二条读数：50,000 元买到的不是混合书

30% 袖 = 15,000 元 < 25,850 元一手门槛 → 一只转债都拿不到，钱包退化成 100% ETF 书，
且整手搁浅 30.4%。也就是说 `book_pair_blend` 的 30/70 在这个钱包规模下**不存在**。

## 3. 父面复现（本面不许出错的一条）

`reconciliation`：对父票面公布的三个资本（100,000 / 500,000 / 1,000,000），
本面的 ETF 袖必须逐名、逐手、逐额、逐费**等于**父票面自己的 legs →
实测 `diffs = []`（`match`）。最小钱包与 blend 面的 `executable_floor.min_wallet_cny`
一致（`min_wallet_matches_blend: true`）。

## 4. 契约

```
python scripts/paired_book_ticket.py check   -> CHECK OK: 7 wallets on bar 2026-11-26, first full hold at 86,168 CNY
```

- 三个输入的字节戳（bytes+mtime）任一变动 → `CHECK STALE:` + rc3（链据此付费补写）
- 页面与 `render_md` 不一致 → `CHECK FAILED:` + rc1（不含 STALE 字样，是自相矛盾不是漂移）
- 两个父面不同日 → `build()` 拒发（`SLEEVES_OFF_BY_DAYS`，rc3，旧面保持不动）

链接线：`etf_nobond_ticket`（r2174 新建，紧跟 `etf_nobond_vt`）+ `paired_book_ticket`（紧随其后）。
点名单腿实测 4/4 rc0：`cb_book_ticket_floor 0.1s / etf_nobond_vt 59.3s / etf_nobond_ticket 0.1s / paired_book_ticket 0.1s`。
加腿后契约词面重生成 **n_legs 399 / n_writer_legs 142 / n_candidates 13 / n_permanent_red 0**（rc0），
写者审计重生成后 `4 faces checked, 4 known check-only, 0 newly paired` rc0。

## 5. 未做 / 未验证（如实）

- 转债袖的**券商账单没算**：`cb_book_ticket_floor` 本身不印佣金，本面只为 ETF 袖计入 `max(5元, 3bp)`
  并按此报 `fees_cny`，转债袖的费记为 0.0（不是免费，是本面没有依据）。
- 两个袖之间的**调仓成本未建模**（blend 面自己的口径也是这样写的）。
- 30/70 是重叠窗样本内最优（`book_pair_blend` 已披露），不是定律。
- 本面只读**最后一根 bar** 的名单；下次换仓后需重跑（`check` 会因此转 STALE）。
- 未做逐笔撮合（次日开盘 + 冲击 + 最小佣金），只回答「权重能不能落地」。
