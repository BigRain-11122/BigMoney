# r602 bm-b: decode UTF-16 S6 log (r559 law) + extract key verdicts
import re, json, io
log = open(r"results\_r602bmb_s6_runner.log", "rb").read().decode("utf-16-le", "replace")
pat = re.compile(r"ZERO-DRIFT|DRIFT|streak|verdict|flags|delta|CLEAN|red\"?:|nonzero|FAIL", re.I)
hits = [l.strip() for l in log.splitlines() if pat.search(l)]
def safe(s):
    return s.encode("ascii", "replace").decode()
for h in hits[:40]:
    print(safe(h[:220]))
print("---tail---")
for l in log.splitlines()[-15:]:
    print(safe(l[:220]))
