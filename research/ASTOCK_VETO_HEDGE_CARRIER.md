# Which carrier do you short: IM futures or the 512100 ETF?

A hedge is a decision about a carrier before it is a decision about a size. Every face in this family since r2022 quoted one carrier at a time, and the IM discount travels through those pages as an annual cost. This face puts the two carriers on one ruler, on one window, at one k.

Evidence cutoff **2026-11-20**, parent beta face `results/astock_veto_hedgeable_beta.json` (generated 2026-11-24T03:29:09+08:00), basis face `results/idx_fut_basis.json` (generated 2026-11-24T05:22:07, cutoff 2026-11-20).

## 1. The same book, the same periods, two carriers

| hedge | ETF short ann. | IM short ann. | ETF vol | IM vol | ETF Sharpe | IM Sharpe |
|---|---|---|---|---|---|---|
| k=0.0 | 11.03% | 11.03% | 28.44% | 28.44% | 0.51 | 0.51 |
| k=0.5 | 12.58% | 12.61% | 17.34% | 16.83% | 0.77 | 0.79 |
| k=1.0 | 12.39% | 12.31% | 11.39% | 10.94% | 1.09 | 1.12 |

Sample: 52 periods, 2022-07-26 to 2026-11-11.

## 2. What the carrier actually charged

These are the hedging legs on their own, not the book. Shorting the ETF over these 52 periods (4.13 years) compounded **-21.03%**; shorting the futures compounded **-22.17%**. The futures short finished behind the ETF short by **0.354 pp a year**.

## 3. The ruler that is quoted is not the ruler that is paid

The basis face annualises the median daily (futures minus index) return to **8.91% a year** (net of drift 5.89%). Read alone that looks like the annual price of hedging with futures. But a median day is not a year: the compounded short-vs-short gap on the same window is **-0.354 pp a year -- 25 times smaller**. The typical day does charge the futures short (that is what the median says); the few days when the futures fall harder than the index pay it back, and almost nothing survives in the compounded number. The comparison assumes 512100 tracks CSI 1000 closely enough that what is left is the basis.

## 4. The notional is the same; the blocked cash is not

Short 901331 yuan of notional (beta 0.9013 on 1000000 yuan).

| carrier | assumption | blocked CNY | free cash CNY | annual impact |
|---|---|---|---|---|
| IM margin | 8% | 72107 | 927893 | +18558 CNY interest |
| IM margin | 12% | 108160 | 891840 | +17837 CNY interest |
| IM margin | 15% | 135200 | 864800 | +17296 CNY interest |
| ETF borrow | 50% haircut, 2% fee | 450666 | 549334 | -18027 CNY borrow |
| ETF borrow | 50% haircut, 5% fee | 450666 | 549334 | -45067 CNY borrow |
| ETF borrow | 50% haircut, 8% fee | 450666 | 549334 | -72107 CNY borrow |
| ETF borrow | 80% haircut, 2% fee | 721065 | 278935 | -18027 CNY borrow |
| ETF borrow | 80% haircut, 5% fee | 721065 | 278935 | -45067 CNY borrow |
| ETF borrow | 80% haircut, 8% fee | 721065 | 278935 | -72107 CNY borrow |
| ETF borrow | 100% haircut, 2% fee | 901331 | 98669 | -18027 CNY borrow |
| ETF borrow | 100% haircut, 5% fee | 901331 | 98669 | -45067 CNY borrow |
| ETF borrow | 100% haircut, 8% fee | 901331 | 98669 | -72107 CNY borrow |

The futures leg blocks a fraction of the notional and lets the rest earn; the ETF leg blocks most of it and pays borrow on top. Nothing on this table depends on the closed term structure -- it is the cash a broker asks for.

## 5. Verdict

**`DISCOUNT_IS_A_MEDIAN_ARTIFACT+IM_WINS_ON_CAPITAL`**

Every flag below is computed from its own inputs and several can hold at once; the headline names the two that change what a reader would do.

- `DISCOUNT_IS_A_MEDIAN_ARTIFACT` -- the published discount is a median day annualised; the compounded difference between the two short legs is an order of magnitude smaller
- `CARRIER_TIES_ON_RETURN_IM_QUIETER` -- on the shared window the two carriers compound to the same return, and the futures leg is the quieter one
- `IM_WINS_ON_CAPITAL` -- the notional that must be blocked is the difference: margin on the futures leg leaves cash earning, the ETF leg blocks it and pays borrow

## 6. Readings

- **R1.** on the shared 52 periods at k=1 the ETF short compounded 12.39% against 12.31% for the futures short (futures behind by 0.354 pp a year); without a hedge the same book did 11.03%
- **R2.** the futures leg is the quieter one: 10.94% annual volatility against 11.39%, so the same return arrives with a higher Sharpe (1.12 vs 1.09)
- **R3.** two rulers, one order of magnitude apart: the basis face annualises the median day to 8.91% a year, while the compounded short-vs-short gap over the same window is -0.354 pp a year -- the median day is not a year
- **R4.** the notional is the same, the blocked cash is not: 901331 yuan of short needs 108160 yuan of margin at 12% on the futures leg (leaving 891840 yuan earning 17837 yuan a year), against 450666..901331 yuan blocked on the ETF leg where the borrow itself costs 1.80..7.21 pp a year

## 7. What this face does not settle

- both legs are priced off their own panels (512100 secondary-market close, IM main continuous close); an ETF tracking error and its premium/discount are inside the gap and are not separated here
- the shared window is 52 periods because the IM panel starts 2022-07; the ETF arm's longer 77-period record is not used anywhere on this face
- the capital table sweeps margin and borrow assumptions instead of picking one; the cash yield is a declared 2% assumption, not a measured rate
- no borrow availability is modelled: an ETF short needs a lender and A-share borrow is frequently exhausted, which a number cannot cure
- this is a ruler and an execution note, not a trade instruction

Machine `bm-c`, generated 2026-11-24T07:08:17+08:00.
