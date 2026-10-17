"""r1074 bm-c S6 driver clone helper: canon-clone Tools/_r1073bmc_s6.py -> Tools/_r1074bmc_s6.py with fresh window docstring."""
import io
import re

SRC = "Tools/_r1073bmc_s6.py"
DST = "Tools/_r1074bmc_s6.py"

NEW_DOC = '''"""r1074 bm-c S6 chain driver (canon clone of r1073; r838 canon lineage): standing-leg canon clone -- identical leg list, leg count derived at runtime honest count. Full log to results/_r1074bmc_s6_log.txt. MUST run under the SYSTEM python (Python313): embedded ComfyUI python has no pandas/akshare (r516 lesson). Every leg subprocess passes CREATE_NO_WINDOW (U060 silence law). Per-leg stdout progress line (5-min zero-output kill guard, r1032 pit family). Saturday 19:3x run -- bars cutoff 10-16 current (weekend honest: update_daily/papers legs expected no-ops until Monday 10-19 15:30); bm-a/bm-b-owned lanes honest no-op on this machine per R31 lane guards. r1074 window = waits-upstream clean continuation: origin tip 30b9058d6 (=r1073 closeout, behind=0); W263 = bm-a window (splice LANDED f499817fa + burn 12/12 shards LANDED 355c716b7; sixgate/finalize pending on bm-a -- n1_w263_results.json absent on disk AND on origin ls-tree verified; satengine ALIVE rc0 dedup local_done=12; upstream ACTIVE verified: listener ALIVE + bm-a unpushed local head 46ba27c5fa8f in-flight) -- bm-c waits-upstream, next bm-c turn = W264 seat after W263 finalize; CEO gaming window 17:3x yield face per 19:2x ORD row (GPU frozen; loop CPU-only legal bookkeeping); S0.5: ORD 313c8c0f->f6d580cf consumed 1 row (19:2x bm-c r1058 receipt, own-lane already-executed, zero loop action) + DEC 1d4741e4 SAME (raw-blob sha256); unacked=0; smoke 49/49; orphan face=1 (user Doubao pythonw PID 32692 family legal-user-process zero-kill)."""'''

src = io.open(SRC, encoding="utf-8").read()
m = re.search(r'""".*?"""', src, re.S)
if not m:
    raise SystemExit("FATAL: docstring not found in source driver")
body = src[m.end():]
body = body.replace("r1073", "r1074")  # log path + log header labels (rollable canon labels)
assert "r1073" not in body, "stale r1073 tokens in body"
out = src[: m.start()] + NEW_DOC + body
assert "_r1074bmc_s6_log.txt" in out
assert out.count("r1074") >= 4
io.open(DST, "w", encoding="utf-8", newline="").write(out)
print("clone written:", DST, len(out), "bytes")
