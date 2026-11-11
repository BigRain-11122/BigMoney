# DIGEST r1548 — the single-row suspension words are not scattered noise

**Question.** r1547 published that 116 of 141 blocked runs are a single NAV row and called them
"a blip and not a policy". Was that sentence ever counted, or only asserted?

**What was measured.** Every single-row 暂停申购 run, as a sample of *days*:

| reading | value |
|---|---|
| single-row runs | 116 of 141 blocked runs |
| on one weekday (Tue) | 59 (50.9%) vs 20.3% of all priced sessions |
| one-sided binomial chance | 2.6e-13 |
| bracketed by 场内买入 on both sides | 116 / 116 |
| with a NAV jump >3% (a split/distribution could explain it) | 1 (513100 2022-01-13, 5.19 -> 1.01) |
| peak days of the month | 26 (11), 5 (8), 20 (8) |
| legs that clear the line on their own | 1 of 4 (513100, 60%, 9.8e-09) |

**Verdict word published:** `BLIP_WEEKDAY_CADENCE` pooled; `BLIP_NO_CADENCE` on 159501/513690/159577
(too few runs), `TOO_FEW_BLIPS` on 159263.

**What the face refuses to say.** That the cause is known. A source that refreshes its status
word on a weekly rhythm and a fund that announces one-day suspensions look identical from this
side of the data. The block is titled "when the word is printed, not why" and the page says the
two are indistinguishable here.

**Why it matters.** The clause r1547 needed ("a one-row word is not a policy") now rests on a
counted cadence test rather than on the word "blip". The other direction matters too: the same
test would have gone red if the days had looked like ordinary sessions, so the sentence is
falsifiable.

**Enforcement.** `_cadence_verdict` derives the verdict and the modal weekday from the weekday
counts alone, so a hand-edited verdict fails `check`; `check` also fails when the page drops the
section or omits the pooled sentence while 116 runs exist.

**Files.** `scripts/etf_book_premium_subscription.py` (selftest 51/51) · `results/etf_premium/
PREMIUM-SUBSCRIPTION.json` (`blip_cadence` per leg, `blip_cadence_pooled`) and `.md`
(`## Why the blips`) · card E540/E541 · chain leg `premium_subscription`.
