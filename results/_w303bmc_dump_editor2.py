# -*- coding: utf-8 -*-
import io

t = io.open("results/_w302bmc_freeze_edits.py", encoding="utf-8").read()
for probe in ('301: {"a"', 'dropped segment', 'w300_', 'w301_', 'w302_',
              'upstream_w301', 'parity rows', 'OWN W301 block', 'W248..W300 legs',
              'W248..W301 legs', 'THREE HUNDREDTH', 'HUNDRED-AND-NINETEENTH',
              'MSG-20261024-0550-bmc-w302-seat', '6a5e62e6bb', '2026-10-24 06:0x',
              'wave 302: ', '1_086_541', '1,086,541', '660_120'):
    print("%-38r %d" % (probe, t.count(probe)))
print()
for line in t.splitlines():
    if "dropped segment" in line or '301: {"a"' in line:
        print("LINE:", line)