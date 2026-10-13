# -*- coding: utf-8 -*-
# r967 W232 prereg chain runner: restore committed faces byte-faithfully,
# then phase A -> phase B -> subgen -> assembly -> py_compile.
import hashlib, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def blob_bytes(rev, path):
    b = subprocess.run([r"C:\Program Files\Git\cmd\git.exe", "-C", REPO, "show", f"{rev}:{path}"],
                       capture_output=True).stdout
    assert b, f"blob fetch failed {rev}:{path}"
    return b

# 1. restore the committed W231 tpl to its canonical path (byte-faithful)
tpl = blob_bytes("aebe0a5ac", "results/_w231bmc_prereg_derive_tpl.py")
open(r"results\_w231bmc_prereg_derive_tpl.py", "wb").write(tpl)
print("tpl restored:", len(tpl), "bytes, sha16:", hashlib.sha256(tpl).hexdigest()[:16])

# 2. verify the on-disk W231 derive script == committed blob (subgen SRC)
disk = open(r"results\_w231bmc_prereg_derive.py", "rb").read()
ref = blob_bytes("aebe0a5ac", "results/_w231bmc_prereg_derive.py")
assert disk == ref, "on-disk _w231bmc_prereg_derive.py != committed blob"
print("derive script verified byte-identical to aebe0a5ac blob:", len(disk), "bytes")

# 3. phase A + phase B + subgen
for script in [r"results\_r967bmc_tplgen.py", r"results\_r967bmc_tplgen_b.py",
               r"results\_w232bmc_subgen.py"]:
    r = subprocess.run([sys.executable, script], cwd=REPO, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    print(f"=== {script} rc={r.returncode} ===")
    print((r.stdout or "")[-600:])
    if r.returncode != 0:
        print((r.stderr or "")[-1500:])
        sys.exit(1)

# 4. assembly: replace @@SUB_BLOCK@@ with the emitted block
tpl2 = open(r"results\_w232bmc_prereg_derive_tpl.py", encoding="utf-8").read()
block = open(r"results\_w232bmc_sub_block.py", encoding="utf-8").read()
assert tpl2.count("@@SUB_BLOCK@@") == 1
final = tpl2.replace("@@SUB_BLOCK@@", block.rstrip("\n"))
open(r"results\_w232bmc_prereg_derive.py", "w", encoding="utf-8", newline="").write(final)
import py_compile
py_compile.compile(r"results\_w232bmc_prereg_derive.py", doraise=True)
print("assembly OK: results/_w232bmc_prereg_derive.py bytes:", len(final.encode("utf-8")))
