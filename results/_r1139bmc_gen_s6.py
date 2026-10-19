# -*- coding: utf-8 -*-
# r1139 bm-c: materialize the S6 light chain driver from the r1136 canon clone
# (legs verbatim, zero edits; only the log path / header tag advance).
import io

src = io.open('results/_r1136bmc_s6_light.py', encoding='utf-8').read()
s = src.replace('_r1136bmc_s6_log.txt', '_r1139bmc_s6_log.txt')
s = s.replace('r1136 bm-c S6 light chain driver (r1135 clone', 'r1139 bm-c S6 light chain driver (r1136 clone')
s = s.replace('r1132 bm-c S6 night light chain', 'r1139 bm-c S6 night light chain')
s = s.replace('r1132 S6 light chain start', 'r1139 S6 light chain start')
io.open('results/_r1139bmc_s6_light.py', 'w', encoding='utf-8', newline='').write(s)
print('written legs', s.count('("'))