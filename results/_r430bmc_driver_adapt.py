"""_r430bmc_driver_adapt.py -- r429-law trio for S6 driver LOG path flip (r430).
Step 1 of the r429 pattern: byte count-assert replace (BOTH docstring and LOG
literal must flip), target-line assert. Driver restored to HEAD state after
the chain run (step 3, separate call). sha_pre recorded for the restore
verification."""
import hashlib

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r428bmc_s6.py"
OLD = b"_r428bmc_s6_log.txt"
NEW = b"_r430bmc_s6_log.txt"
b = open(P, "rb").read()
n = b.count(OLD)
assert n == 2, "count=%d (expect 2: docstring + LOG literal)" % n
sha_pre = hashlib.sha256(b).hexdigest()
open(P, "wb").write(b.replace(OLD, NEW))
t = open(P, "rb").read()
assert t.count(NEW) == 2 and t.count(OLD) == 0, "target-line assert FAILED"
lit = b'LOG = os.path.join(ROOT, "results", "_r430bmc_s6_log.txt")'
assert lit in t, "LOG literal assert FAILED"
print("ADAPT_OK sha_pre=%s" % sha_pre[:16])
