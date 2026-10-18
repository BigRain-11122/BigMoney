# -*- coding: utf-8 -*-
"""r1102-continuation S6 light driver clone (canon-clone of _r1101bmc_s6_light.py,
count-asserted needle rolls only)."""
import io

SRC = "results/_r1101bmc_s6_light.py"
DST = "results/_r1102bmc_s6_light.py"
body = io.open(SRC, encoding="utf-8", newline="").read()

PAIRS = [
    ('r1101 bm-c S6 weekend light chain driver (10 legs, r1096/r1098/r1099/r1100 canon',
     'r1102-continuation bm-c S6 Monday pre-market light chain driver (10 legs, r1096-r1101 canon'),
    ('Log to results/_r1101bmc_s6_log.txt.',
     'Log to results/_r1102bmc_s6_log.txt.'),
    ('Sunday\n~21:2x run -- bars cutoff 10-16 current (weekend honest: update_daily/papers\nno-ops until Monday 15:30); bm-a/bm-b-owned lanes not in the light subset per\nR31. r1101 window: W273 SEAT PUBLISHED origin 39e1bb32f1 (probe ADMIT\nfirst-try A 615_901..617_900 / B 617_901..618_100, 22nd consecutive A-hop /\n23rd consecutive above-own-A); CEO weekend production standing (MV PACK-A\nGPU lane, loop CPU-only).',
     'Monday\n~01:2x run -- bars cutoff 10-16 current (weekend honest: update_daily/papers\nno-ops until Monday 15:30); bm-a/bm-b-owned lanes not in the light subset per\nR31. r1102-continuation window: W274 SEAT PUBLISHED origin 70b21a0264 (probe\nADMIT first-try A 618_101..620_100 / B 620_101..620_300, 23rd consecutive\nA-hop / 24th consecutive above-own-A); absorb face = r1102 dead window\ndied post-closeout-commit pre-counter-advance (healed this window).'),
    ('LOG = os.path.join(ROOT, "results", "_r1101bmc_s6_log.txt")',
     'LOG = os.path.join(ROOT, "results", "_r1102bmc_s6_log.txt")'),
    ('log.write("r1101 bm-c S6 weekend light chain run %s legs=%d\\n" % (started, len(LEGS)))',
     'log.write("r1102-continuation bm-c S6 Monday pre-market light chain run %s legs=%d\\n" % (started, len(LEGS)))'),
    ('print("r1101 S6 light chain start %s legs=%d" % (started, len(LEGS)))',
     'print("r1102-continuation S6 light chain start %s legs=%d" % (started, len(LEGS)))'),
]

for old, new in PAIRS:
    n = body.count(old)
    assert n == 1, (n, old[:60])
    body = body.replace(old, new)

for stale in ('r1101 bm-c S6', '_r1101bmc_s6_log', 'r1101 window', 'r1101 S6 light'):
    assert stale not in body, 'r1101 residue leaked: ' + stale
io.open(DST, "w", encoding="utf-8", newline="").write(body)
print("CLONE OK", DST, len(body))
