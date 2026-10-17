# -*- coding: utf-8 -*-
# r1076 bm-c: clone the r1075 S6 driver to r1076 (canon-clone law, age() machine lineage).
import io, os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "Tools", "_r1075bmc_s6.py")
DST = os.path.join(REPO, "Tools", "_r1076bmc_s6.py")

t = io.open(SRC, encoding="utf-8", newline="").read()
NEW_DOC = '"""r1076 bm-c S6 chain driver (canon clone of r1075; r838 canon lineage): standing-leg canon clone -- identical leg list, leg count derived at runtime honest count. Full log to results/_r1076bmc_s6_log.txt. MUST run under the SYSTEM python (Python313): embedded ComfyUI python has no pandas/akshare (r516 lesson). Every leg subprocess passes CREATE_NO_WINDOW (U060 silence law). Per-leg stdout progress line (5-min zero-output kill guard, r1032 pit family). Saturday 20:3x run -- bars cutoff 10-16 current (weekend honest: update_daily/papers legs expected no-ops until Monday 10-19 15:30); bm-a/bm-b-owned lanes honest no-op on this machine per R31 lane guards. r1076 window = W264 PREREG FREEZE LANDED origin f4ffdb34e (P0 product: machine-SUB from frozen W263 tpl b32f6bf1c pre-backfill face per r1052/r1049 law; derive ALL GATES PASS vmap 39 + floors 54 + post-legs 17 + blocks 8 + MUST 64 + MUST_NOT 54; banned_direction_gate ADMIT rc0 on final bytes; bands A 596_101..598_100 THIRTEENTH consecutive A-hop zero-divergence / B 598_101..598_300 FOURTEENTH consecutive above-own-A; W263 finalize anchors machine-read ledger 1,002,935 EXACT / K=576,520; splice = next window FIRST ACTION, editor derive from _w263bma template per E63 age() law); CEO gaming window 17:3x yield face standing (GPU frozen; loop CPU-only legal bookkeeping); S0.5: ORD 085559d2 / DEC 1d4741e4 dual FALSE hold (pinned-probe, zero rows owed); unacked=0; smoke 49/49; orphan face=1 (user Doubao pythonw PID 32692 family legal-user-process zero-kill)."""'

t2 = re.sub(r'^""".*?"""', NEW_DOC, t, count=1, flags=re.S)
assert t2 != t, "docstring not replaced"
t2 = t2.replace("r1075", "r1076")
assert "_r1076bmc_s6_log.txt" in t2
io.open(DST, "w", encoding="utf-8", newline="").write(t2)
print("written %s (%d bytes)" % (DST, len(t2.encode("utf-8"))))
