# The repo curve at our size -- which tenors can we actually fill?

Window 2011-05-13 -> 2026-11-20. Baseline GC001 closes at 1.395%. Unit check: GC001 median turnover 806,739,750,000 元/day (band 100,000,000,000 .. 5,000,000,000,000) -> OK.

| tenor | last quote | median rate vs GC001 | bad-day turnover | 100万 | 300万 | 1000万 |
|---|---|---|---|---|---|---|
| GC001 (1d) | 1.395% | +0.00bp | 133,294,810,000 | OPEN (0.00%) | OPEN (0.00%) | OPEN (0.01%) |
| GC003 (3d) | 1.355% | +1.00bp | 1,496,200,000 | OPEN (0.07%) | OPEN (0.20%) | OPEN (0.67%) |
| GC004 (4d) | 1.380% | +3.00bp | 1,209,900,000 | OPEN (0.08%) | OPEN (0.25%) | OPEN (0.83%) |
| GC007 (7d) | 1.385% | +15.50bp | 17,982,530,000 | OPEN (0.01%) | OPEN (0.02%) | OPEN (0.06%) |
| GC014 (14d) | 1.385% | +22.25bp | 1,366,810,000 | OPEN (0.07%) | OPEN (0.22%) | OPEN (0.73%) |
| GC028 (28d) | 1.365% | +27.00bp | 310,030,000 | OPEN (0.32%) | OPEN (0.97%) | THIN (3.23%) |
| GC091 (91d) | 1.340% | +29.00bp | 5,800,000 | BLOCKED (17.24%) | BLOCKED (51.72%) | BLOCKED (172.41%) |
| GC182 (182d) | 1.340% | +22.00bp | 800,000 | BLOCKED (125.00%) | BLOCKED (375.00%) | BLOCKED (1250.00%) |
| R-001 (1d) | 1.380% | -6.50bp | 22,401,343,000 | OPEN (0.00%) | OPEN (0.01%) | OPEN (0.04%) |
| R-003 (3d) | 1.320% | -9.80bp | 181,311,200 | OPEN (0.55%) | THIN (1.65%) | THIN (5.52%) |
| R-007 (7d) | 1.375% | +5.00bp | 1,543,667,000 | OPEN (0.06%) | OPEN (0.19%) | OPEN (0.65%) |

**Headline: OPEN_TENORS_PAY_LESS_TODAY.**
Evidence: GC001, GC003, GC004, GC007, GC014, GC028, R-001, R-003, R-007.

Open at 100 万: GC001, GC003, GC004, GC007, GC014, GC028, R-001, R-003, R-007. Blocked at 100 万: GC091, GC182.

Overnight cash at the last quote: 10万 = 1,395 元/年, 100万 = 13,950 元/年, 300万 = 41,850 元/年, 1000万 = 139,500 元/年

Notes: Participation is measured against the p10 day, so 'OPEN at 100 万' means our whole order is <=1% of a bad day's turnover. The 1%/10% band is a convention against being visible on the tape; it is not a measured price impact. Rate pickup is a median of same-day quotes, never a forward-filled pair, and it is a rate difference -- not a return, because the tenors cannot be held for the same calendar days.
