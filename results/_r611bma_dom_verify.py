"""r611 bm-a DOM live-fire verification: Edge headless dump-dom on
dashboard.html (r593 law: subprocess encoding='utf-8' errors='replace'),
assert the new family-verdict chainRow renders with machine-read numbers."""
import subprocess

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
URL = ("file:///C:/Users/sjs20/Desktop/FluxGroup/quant/"
       "bigmoney/dashboard.html")

r = subprocess.run(
    [EDGE, "--headless", "--disable-gpu", "--no-sandbox", "--dump-dom", URL],
    capture_output=True, timeout=90,
    encoding="utf-8", errors="replace")  # r593 decoding law
dom = r.stdout or ""
open(r"results/_r611bma_dom_dump.html", "w", encoding="utf-8").write(dom)

checks = [
    "家族判决图 · 深轴战役",
    "LOWAMP-DEEP-P1[judged-negative]",
    "S 1.066",
    "DSR 0.700",
    "账 617500",
    "N4 (B1+B2+B3 pooled)[window-closed]",
    "K_eff 499",
    "CI95下界&gt;0 2/6",
    "N3-R2[judged]",
    "144窗",
    "账 615492",
    "基本面族战役",
]
fails = [c for c in checks if c not in dom]
print("dom bytes:", len(dom))
for c in checks:
    print(("PASS " if c not in fails else "FAIL ") + c)
if fails:
    raise SystemExit("DOM VERIFY FAIL: %d missing" % len(fails))
print("DOM VERIFY ALL PASS")
