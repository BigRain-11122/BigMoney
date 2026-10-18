# -*- coding: utf-8 -*-
# r1085 bm-c: S6 driver canon-clone r1084 -> r1085 (label roll only, leg list identical)
import io

src = io.open('Tools/_r1084bmc_s6.py', encoding='utf-8').read()
old_doc = src[:src.index('"""', 3) + 3]
new_doc = '''"""r1085 bm-c S6 chain driver (canon clone of r1084; r838 canon lineage): standing-leg canon clone -- identical leg list, leg count derived at runtime honest count. Full log to results/_r1085bmc_s6_log.txt. MUST run under the SYSTEM python (Python313): embedded ComfyUI python has no pandas/akshare (r516 lesson). Every leg subprocess passes CREATE_NO_WINDOW (U060 silence law). Per-leg stdout progress line (5-min zero-output kill guard, r1032 pit family). Sunday 09:1x run -- bars cutoff 10-16 current (weekend honest: update_daily/papers legs expected no-ops until Monday 10-19 15:30); bm-a/bm-b-owned lanes honest no-op on this machine per R31 lane guards. r1085 window: W266 PREREG FREEZE LANDED (595433d63c, dead-window estate absorbed + heal#8 count-gate; splice = next window FIRST ACTION); upstream W265 cycle complete (finalize 1,007,335/K=580,920 + fivekeys 6/6 + W266 seat ace19ba85b); CEO gaming yield standing (loop CPU-only); O-20261018-0137 recovery lineage standing."""'''
src = new_doc + src[len(old_doc):]
src = src.replace('_r1084bmc_s6_log.txt', '_r1085bmc_s6_log.txt')
src = src.replace('r1084 bm-c S6 chain run', 'r1085 bm-c S6 chain run')
src = src.replace('r1084 S6 chain start', 'r1085 S6 chain start')
io.open('Tools/_r1085bmc_s6.py', 'w', encoding='utf-8', newline='').write(src)
print('clone written, %d bytes' % len(src))
