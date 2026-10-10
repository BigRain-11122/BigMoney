import py_compile

SRC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r835bmc_s6.py"
DST = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r837bmc_s6.py"

new_hdr = '"""r837 bm-c S6 chain driver: standing-leg canon clone (r835/r834/r832\ncanon lineage; canon leg list, leg count derived at runtime honest count).\nFull log to results/_r837bmc_s6_log.txt, compact per-leg rc summary to\nstdout. MUST run under the SYSTEM python (Python313): sys.executable\ninherited by every leg; embedded ComfyUI python has no pandas/akshare\n(r516 lesson). Every leg subprocess passes CREATE_NO_WINDOW (zero-desktop-\nflash; U060/2026-10-01 silence law -- safe in ANY host context).\nr837 continuation closeout: prior r837 session died post-W204-push at the\nfinal push-rebase leg (context overflow, .err evidence) -- S6 never ran in\nthat window; this driver is the r837 S6 duty. Weekend ~20:3x run -- market-\ndata legs expected honest no-op (10-09 Friday bar face held); CEO video\nchain still holds the GPU/RAM lane (ComfyUI 8188 resident) -- no S6 leg\ntouches the GPU lane; bm-a/bm-b-owned lanes honest no-op on this machine\nper R31 lane guards."""'

src = open(SRC, encoding="utf-8").read()
end = src.index('"""', 3) + 3
src2 = new_hdr + src[end:]
src2 = src2.replace("_r835bmc_s6_log.txt", "_r837bmc_s6_log.txt")
src2 = src2.replace("r835 bm-c S6 chain run", "r837 bm-c S6 chain run")
assert "_r837bmc_s6_log.txt" in src2 and "r837 bm-c S6 chain run" in src2
assert "LEGS = [" in src2 and src2.count("def main") == 1
open(DST, "w", encoding="utf-8", newline="").write(src2)
py_compile.compile(DST, doraise=True)
print("clone ok len", len(src2))
