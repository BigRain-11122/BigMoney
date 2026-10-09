# -*- coding: utf-8 -*-
"""r820 bm-c 1-gen clone helper: s6 driver from r818 (mechanism verbatim,
round-numbered paths + r820 watch-faces block refreshed)."""
import io

src = io.open('Tools/_r818bmc_s6.py', encoding='utf-8').read()
src = (src.replace('_r818bmc_s6_log', '_r820bmc_s6_log')
          .replace('r818 bm-c S6 chain', 'r820 bm-c S6 chain')
          .replace('Clone credit: Tools/_r817bmc_s6.py (r817 canonical chain, 40 legs rc0).',
                   'Clone credit: Tools/_r818bmc_s6.py (r818 canonical chain, 40 legs rc0).'))
head, rest = src.split('r818 watch-faces:', 1)
_, tail = rest.split('lane guards."""', 1)
w20 = '''r820 watch-faces: update_daily 10-09 bar landing retry (sina late-bar
self-heal round 13; cutoff 10-08 held r808-r819 twelve runs); W17 screens
0/8 burned all day 10-09 -- KeyError('faces') root-caused and FIXED at
r820 (worker state carried the w17 wave grammar which has no faces key,
overwriting tl1.GRAMMAR in every spawn worker; w16 face grammar now
rides initargs; fuse auto-clears on runner hash change) + judge state
grammar field added same window (w16 cmd_judge L3710 precedent); RAM
gate park face below 4GB honest (r354/r379; autofill resubmit owns the
lane); H3 768P T2V first piece DELIVERED r819 (gate 7.5/10, video-only,
outbound local bmc-local-768p-t2v-20261009.mp4); shared 8188 server
idle-held as H3 reuse face (r817 orphan-face adjudication);
fund_premium 10-09 NAV publishes T+1 (10-10 15:30+) so today stays an
honest no-op face; update_options leg = RETIRED honest no-op exit 0 per
O-20261009-1105 (leg STAYS in the chain as the honest no-op face);
bm-a/bm-b-owned lanes honest no-op on this machine per R31 lane guards."""
'''
out = head + w20 + tail
io.open('Tools/_r820bmc_s6.py', 'w', encoding='utf-8', newline='\n').write(out)
print('cloned s6 driver ok', len(out))
