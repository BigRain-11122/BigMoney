import py_compile

SRC = r"Tools/_r1069bmc_s6.py"
DST = r"Tools/_r1070bmc_s6.py"
src = open(SRC, encoding="utf-8").read()
doc = '"""r1070 bm-c S6 chain driver (canon clone of r1069; r838 canon lineage): standing-leg canon clone -- identical leg list, leg count derived at runtime honest count. Full log to results/_r1070bmc_s6_log.txt. MUST run under the SYSTEM python (Python313): embedded ComfyUI python has no pandas/akshare (r516 lesson). Every leg subprocess passes CREATE_NO_WINDOW (U060 silence law). Per-leg stdout progress line (5-min zero-output kill guard, r1032 pit family). Saturday 18:2x run -- bars cutoff 10-16 current (weekend honest: update_daily/papers legs expected no-ops until Monday 10-19 15:30); bm-a/bm-b-owned lanes honest no-op on this machine per R31 lane guards. r1070 window = 5x HANDOVER duty round + waits-upstream clean continuation: origin tip aba6247ec (=r1069 closeout); W263 = bm-a window (seat 0d2fa8c13 + prereg b32f6bf1c frozen, splice ungated post-W262-finalize, splice/burn/finalize pending on bm-a; not landed at this window open) -- bm-c waits-upstream, next bm-c turn = W264 seat after W263 finalize. S0.5: ORD 313c8c0f SAME (content-sha1 pinned method r977) + DEC 1d4741e4 SAME; unacked=0; smoke 49/49; satengine ALIVE waits-upstream."""'
i = src.index('"""')
j = src.index('"""', 3) + 3
out = doc + src[j:]
out = out.replace("_r1069bmc_s6_log", "_r1070bmc_s6_log")
out = out.replace("r1069 S6 chain", "r1070 S6 chain")
out = out.replace("r1069 bm-c S6", "r1070 bm-c S6")
open(DST, "w", encoding="utf-8", newline="\n").write(out)
py_compile.compile(DST, doraise=True)
print("CLONED OK ->", DST)
