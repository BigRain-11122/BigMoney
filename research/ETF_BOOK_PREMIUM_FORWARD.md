# Does a top-decile premium cost anything? (r1500, bm-c)

`results/etf_premium/PREMIUM-FORWARD.json` — producer: `scripts/etf_book_premium_forward.py`
(single implementation: the panel reader is `scripts/etf_book_premium_percentile.py`).

## The question the sheet left open

r1497 answered "how high is today's premium" (own-history percentile). r1498 answered "is
that reading real or a NAV-stamp artifact" (persistence + lag ladder). The sheet then says,
honestly, **高分位不是卖单** — high percentile is not a sell order — because a limited fund
can stay expensive for years and this house holds no subscription-status data.

What neither ruler answers is the one thing the person placing the order needs: *if I pay a
100th-percentile premium, what did the price do afterwards in this fund's own record?* That
is measurable from the panel already on disk.

## Two rulers

* **Causal percentile** — each session ranked against the sessions *before* it (≥60 priors).
  Ranking a session inside its own full sample would let the future label the past.
* **Outcome = the price**, close[t+h]/close[t]−1, h ∈ {5, 20}. Not the NAV: a premium that
  "reverts" because the NAV caught up is not a loss to somebody holding the price.

Buckets: BOTTOM <10, LOW 10–30, MID 30–70, UPPER 70–90, TOP ≥90. The t-stat is computed on
**non-overlapping** samples (stride h) — h overlapping windows repeat the same move h times
and would inflate it; the overlapping count is reported only as coverage.

## Reading (panel cutoff 2026-11-09, ticket 2026-11-09, 5 legs)

Pooled rank IC of the percentile with the next 20 sessions: **−0.133** (5 legs); at 5
sessions: −0.050.

| leg | today's percentile | bucket | next 20 sessions after that bucket | n | t | on this ticket's amount |
|---|---|---|---|---|---|---|
| 159501 | 99.9 | TOP | +0.49% | 282 | +1.6 | +￥382 |
| 513100 | 98.9 | TOP | −0.22% | 295 | −0.5 | −￥175 |
| 159577 | 98.9 | TOP | −0.95% | 124 | −2.6 | −￥749 |
| 513690 | 50.5 | MID | +0.12% | 171 | +0.3 | +￥394 |
| 159263 | 16.7 | LOW | −0.64% | 32 | +4.2 | −￥505 |

Verdict **MIXED** — derived, not typed: one leg prints a real penalty (159577, t=−2.6), the
leg paying the largest premium today prints none (159501, t=+1.6), so the sign is not the
same across the book.

## What this changes for the operator

Nothing in the sizing rule: this face is a description of these funds' own records, not a
forecast, and not a cross-sectional study. What it removes is the unspoken assumption behind
"don't chase premium" — on this ticket the three TOP-decile legs have, on their own history,
a combined 20-session drift of about **−￥542 on ￥235,616**, with the sign spread across
legs. Nobody should read that as a reason to drop 159577 or to add 159501.

## Guards

`check` re-derives every bucket mean/t, the pooled IC and the verdict word from
`premium_history.csv`, and asserts the money column is *priced* (a percent-only face fails:
r1499's leg examined zero symbols and passed). Falsified four ways: a bucket mean edited in
the published JSON, the verdict word hand-typed, the ticket absent (no CNY), and the
percentile made non-causal — the first three turn `check` red, the fourth breaks selftest
L8.

## r1501 — 这张面现在印在票面上（2026-11-10）

r1500 的收口句是「票面自己该印前向行」。落地：scripts/etf_book_order.py 读

esults/etf_premium/PREMIUM-FORWARD.json（premium_read() 的 wd_* 块），ORDER 页在
「溢价读数」节里多一张表，TICKET JSON 里同块给机器读者（wd_rows / wd_verdict /
wd_horizon / wd_sentence / wd_cny_total / wd_missing_legs）。

判据三件：①判词、原句、桶均值一律从生产者面读，禁手抄；②钱列 = 本单金额 × 同档历史前向均值，
合计只把真取到的腿相加；③面缺/腿缺时页面必须写「还没被量过 / 请按没测读」，缺件禁读成「没什么事」。

2026-11-09 票面读数：TOP 三条合计 −￥542、MID +￥394、LOW −￥505，全单 **−￥652**（判词 MIXED）。
写在页面上的句子仍然只有一句结论：**这一列量的是价格，不是建议**。

## r1554 — 订单真正能等的那一个会话（2026-11-11）

r1553 留下的问题是「三只在自身 98.8–99.9 分位的腿，今天买还是等一个会话」。这张面在此之前只量
5 日/20 日，而订单能选的等待只有**一个会话**；同时 TOP≥90 的十分位桶把今天这三只（98.8–99.9）
和 90–95 的样本混在一起，均值被稀释。

本轮补两件，都在同一个生产者里（`scripts/etf_book_premium_forward.py`，无第二个实现）：
①尾部细档 `P95_98 [95,98)` 与 `P98P [98,+inf)`，逐腿 + 池化；②`horizon=1` 的前向回报（价格，
不是净值），给出**中位**与**下跌占比**——一个均值分不开「51% 小跌」和「90% 跌 + 10% 大赚」。

读数（`results/etf_premium/PREMIUM-FORWARD.json`，面板切至 2026-11-09）：

| 集合 | n | 下一会话涨跌中位 | 均值 | 下跌占比 |
|---|---|---|---|---|
| 池化 P98P | 326 | +0.00% | -0.04% | 49% |
| 池化 P95_98 | 281 | +0.00% | -0.07% | 49% |
| 159501（今日 99.9） | 167 | +0.00% | — | 49% |
| 513100（今日 98.9） | 68 | -0.28% | — | 54% |
| 159577（今日 98.9） | 48 | -0.30% | — | 56% |

判词 `NO_READ`：池化的下一会话中位 0.00%、下跌占比 49%——**「等一天让溢价回落」在这些基金
自己的记录里没有优势**。两只偏负的腿（513100/159577）样本只有 48/68 个会话、下跌占比 54–56%，
而本单最大的一只（159501，n=167）恰好是 0.00%。这一列回答的是「等一个会话历史上值不值」，
答案是既不值也不亏；它**不**回答 20 日尺度（那是 MIXED）。

判据三条：①中位与下跌占比由样本派生，`check` 重算臂逐档比对 n/mean/share_down，并断言池化
n == 各腿 n 之和；②`defer_verdict` 由池化 P98P 的 median 与 share_down 派生（WAITING_PAID /
WAITING_COST / NO_READ），手改即红；③订单页必须**真的印出**它依赖的池化下跌占比，缺即红。

落到订单面：`TICKET-*-card.json` 与 ORDER 页「溢价读数」节多一段「等一个会话再买，历史上有没有用」，
逐腿印「今日分位 / 该档下一会话涨跌中位 / 下跌占比 / n」；缺档时写「还没被观察到」，不写「没差别」。
