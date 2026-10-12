# -*- coding: utf-8 -*-
# r936 bm-c S6 driver clone: r871 canon lineage, header + log path re-anchored.
src = open(r"Tools\_r871bmc_s6.py", encoding="utf-8").read()
end = src.index('"""', 10) + 3
old_hdr = src[:end]
new_hdr = ('"""r936 bm-c S6 chain driver: standing-leg canon clone (r838 canon '
           'lineage; r871 canon clone -- identical leg list, leg count derived at '
           'runtime honest count). Full log to results/_r936bmc_s6_log.txt. MUST '
           'run under the SYSTEM python (Python313): embedded ComfyUI python has '
           'no pandas/akshare (r516 lesson). Every leg subprocess passes '
           'CREATE_NO_WINDOW (U060 silence law). Monday 18:2x run -- new Monday '
           'bars expected on update_daily (r933 verdict: Monday bars pending); '
           'papers chain on bar landing; W224 prereg landed this window, engine '
           'DRY (queue_next empty at derive time); bm-a/bm-b-owned lanes honest '
           'no-op on this machine per R31 lane guards."""')
src = new_hdr + src[len(old_hdr):]
src = src.replace("_r871bmc_s6_log.txt", "_r936bmc_s6_log.txt")
src = src.replace("r871 bm-c S6 chain run", "r936 bm-c S6 chain run")
open(r"Tools\_r936bmc_s6.py", "w", encoding="utf-8", newline="").write(src)
print("clone written")
