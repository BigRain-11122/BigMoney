# r247 contract probe 2: pbo + ew6 + composite_ic + market_regime imports
import io, re

src = io.open("screening/pbo.py", encoding="utf-8").read()
for pat in (r"def cscv_pbo.*?\):", r"def align_returns.*?\):"):
    m = re.search(pat, src, re.S)
    print("PBO:", m.group(0).replace("\n", " ")[:200] if m else "MISSING")

src = io.open("scripts/ew6_portfolio.py", encoding="utf-8").read()
m = re.search(r"def member_run.*?\):", src, re.S)
print("EW6 member_run:", m.group(0).replace("\n", " ")[:200] if m else "MISSING")
print("EW6 PRICES_FULL decl:", "PRICES_FULL" in src)

src = io.open("scripts/composite_ic.py", encoding="utf-8").read()
m = re.search(r"IS_END = .*", src)
print("IS_END:", m.group(0) if m else "MISSING")

src = io.open("scripts/market_regime.py", encoding="utf-8").read()
for pat in (r"^GREEN.*", r"^ORANGE.*", r"^RED.*", r"^YELLOW.*"):
    m = re.search(pat, src, re.M)
    print("REGIME CONST:", m.group(0)[:60] if m else "MISSING")

# regime_calibration faces used by div_lowvol
src = io.open("scripts/regime_calibration.py", encoding="utf-8").read()
for name in ("def build_bench", "def bench_dim_series", "def breadth_series",
             "def raw_series", "def state_replay"):
    m = re.search(re.escape(name) + r".*?\):", src, re.S)
    print("RC:", m.group(0).replace("\n", " ")[:120] if m else "MISSING")
