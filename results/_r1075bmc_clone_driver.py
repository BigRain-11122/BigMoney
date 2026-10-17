# -*- coding: utf-8 -*-
import io
src = io.open('Tools/_r1074bmc_s6.py', encoding='utf-8').read()
hdr_old = src.split('"""')[1]
hdr_new = """r1075 bm-c S6 chain driver (canon clone of r1074; r838 canon lineage): standing-leg canon clone -- identical leg list, leg count derived at runtime honest count. Full log to results/_r1075bmc_s6_log.txt. MUST run under the SYSTEM python (Python313): embedded ComfyUI python has no pandas/akshare (r516 lesson). Every leg subprocess passes CREATE_NO_WINDOW (U060 silence law). Per-leg stdout progress line (5-min zero-output kill guard, r1032 pit family). Saturday 19:5x run -- bars cutoff 10-16 current (weekend honest: update_daily/papers legs expected no-ops until Monday 10-19 15:30); bm-a/bm-b-owned lanes honest no-op on this machine per R31 lane guards. r1075 window = W264 SEAT PUBLISH (P0 product): origin tip 0223ada6b (bm-a r1040 estate absorb: W263 finalize LANDED ledger 1,002,935 EXACT / K=576,520 EXACT via 91da16c86); W264 seat published this window (probe _w264bmc_20261017_probe.py live ADMIT: A 596_101..598_100 THIRTEENTH A-hop / B 598_101..598_300 FOURTEENTH above-own-A; seed gates FREE x2; origin vacancy four-check green; MSG-20261017-1950-bmc-w264-seat.md); W264 FREEZE UNBLOCKED = prereg derive r1076 FIRST ACTION; CEO gaming window 17:3x yield face standing (GPU frozen; loop CPU-only legal bookkeeping); S0.5: ORD 085559d2 / DEC 1d4741e4 dual FALSE hold (pinned-probe, zero rows owed); unacked=0; smoke 49/49; orphan face=1 (user Doubao pythonw PID 32692 family legal-user-process zero-kill)."""
out = src.replace('"""' + hdr_old + '"""', '"""' + hdr_new + '"""')
assert hdr_new[:20] in out, 'header swap failed'
out = out.replace('_r1074bmc_s6_log.txt', '_r1075bmc_s6_log.txt')
out = out.replace('r1074 bm-c S6 chain', 'r1075 bm-c S6 chain').replace('r1074 S6 chain', 'r1075 S6 chain')
io.open('Tools/_r1075bmc_s6.py', 'w', encoding='utf-8', newline='\n').write(out)
print('driver written bytes=', len(out))
