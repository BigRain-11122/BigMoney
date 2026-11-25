# QA · r2119 bm-c · 三个冒烟红与一个「一个 tick 不是两个答案」

日期 2026-11-26 06:35-07:05 · 机器 bm-c · 竞争探针 `results/_repo_write_contention.bm-c.json` rc0 CLEAN（单 codely 宿主）

## 1 全量冒烟的两条 CHECK FAIL：面比输入旧一代，不是算错

| 腿 | 修前 | 处置 | 修后 |
|---|---|---|---|
| `product: etf_book_supply_gate_decision (verdict re-derived from receipts)` | `CHECK FAIL 6/9 drift=money_constructions_that_are_gifts,cross_receipt_agreement,sources` | `python scripts/etf_book_supply_gate_decision.py run` 重生（不动判据） | `CHECK OK 9/9 verdict=CALIBER_IRRELEVANT_TO_MONEY` |
| `product: etf_book_live_size_provenance (figures re-derived)` | `check: 11/12` | `python scripts/etf_book_live_size_provenance.py run` | `check: 12/12` |

两条都是「盘上已发布的面停在上一代回执上」，判据本身没动（r1852/r1860 族：面代差不是算法错）。重生后逐腿复跑转绿。

## 2 日词普查：页面每个日词都有日期，仍有 4 个日期「没人认领」

修前 `python scripts/live_book_day_words.py check`：

```
verdict PRINTED_BUT_UNANCHORED | DATES claims 21 | ok 21 | mismatch 0 | unverifiable 0 | unmapped 4 | rules 22
DATE-UNMAPPED 付了溢价之后… | 2026-11-24
DATE-UNMAPPED 付了溢价之后… | 2026-11-25
DATE-UNMAPPED 为什么这张单只能下这么大 | 2026-11-24
DATE-UNMAPPED 为什么这张单只能下这么大 | 2026-11-25
```

两句话各印**两个**日期（源面被定价的那天 + 本页被定价的那天），`CLAIM_RULES` 里没有规则认领它们，于是页面被读成 `PRINTED_BUT_UNANCHORED`。

页面原文（`docs/live_book/LIVE-BOOK-20261126.md`）：

- `这张读数按 **2026-11-24** 的票面算，本页价的日期是 **2026-11-25**——…`
- `额度来源面锚在 **2026-11-24**，本页的价是 **2026-11-25**——…`

发句子的字段都在页面自己的 JSON 里读过：`premium_forward.face_asof=2026-11-24`、`floor_provenance.evidence_cutoff=2026-11-24`、`priced_bar=2026-11-25`。按 r1849/E685 正法补两条规则（每条日期指向它自己的来源字段，第二个日期都指向页面自己的 `priced_bar`），不动任何判据。

修后：

```
verdict ANCHORED | DATES claims 25 | ok 25 | mismatch 0 | unverifiable 0 | unmapped 0 | rules 24
--selftest 46/46
```

新增一条负控腿：同一对句子在源面缺席时必须读成 `unverifiable`（页面自己的价日仍可核验 = 2 ok / 2 unverifiable），并在源面在位时 4/4 ok。首版断言我写成「4 unverifiable」，是**我的期望错**、不是判据错——harness 当场抓到，改断言不放宽规则。

## 3 一个 tick 不是两个答案（`idx_fut_carry_one_lot_ruler`）

修前该面 `CONSUMERS_ONE_GENERATION_BEHIND`，三张 11-23 的面仍印旧代一手成本（IC 1,124,479 / IM 1,152,596），与今日尺（1,132,145.38 / 1,161,161.25）差 **7,666 / 8,565 元**。三张面全部重生 → 5/6 消费者 FRESH，剩 `tradeable_hedge_capital` 差 **0.02 / 0.03 元**（相对 1.8e-8），被判 `DISAGREE`——它和权威面是同一个测量，只是累加顺序不同。

正法=第三种状态 `PRECISION_ONLY`，阈值有来历：指数报价存 4 位小数，合约一手 = 乘数 × 0.0001 = **0.02 元**（IC/IM 乘数 200）；最大显示误差再给一分钱（两面各 2 位小数的四舍五入）。超出即仍判 `DISAGREE`（自检腿钉死「两个半 tick 必红」）。

```
verdict ONE_RULER_UP_TO_ONE_TICK | 10 consumers | rebuilt list 0
  tradeable_hedge_capital IC 1,132,145.36 vs 1,132,145.38 PRECISION_ONLY -0.02
  tradeable_hedge_capital IM 1,161,161.22 vs 1,161,161.25 PRECISION_ONLY -0.03
--selftest 16/16 · check CHECK_OK
```

## 未做（如实）

1. 该面**仍未接进** `Tools/s6_chain_bmc.py` 与 `smoke_test.py`：该文件本窗开工时已是他人未提交脏面（+45 行），且有 `pythonw Tools\s6_chain_bmc.py 2117`（04:15 起）在跑，禁写。
2. 全量冒烟本轮**已用分离日志跑**（`logs/smoke_full_r2119.out`，07:00 已到 315 行），单轮窗口内未跑完，不宣称总数。
3. `PCR`／链序：本窗未跑 S6 全链（另一驱动正在跑同一文件）。
