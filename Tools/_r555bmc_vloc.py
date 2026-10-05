"""r555 bm-c py_watermark verdict locator (r547 split-anchor family probe)."""
import io
import re

s = io.open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r555bmc_s6_log.txt",
            encoding="utf-8-sig", errors="replace").read()
idx = s.find('"verdict": "py_low_board_clear"')
print("verdict-char-idx=%d" % idx)
if idx >= 0:
    before = s[:idx]
    markers = re.findall(r"=== (\S+) rc=", before)
    print("last-leg-before-verdict=%s" % (markers[-1] if markers else "none"))
    seg = s.split("=== 03_py_watermark", 1)
    print("has-03-marker=%s seg1-len=%d" % (len(seg) == 2, len(seg[1]) if len(seg) == 2 else -1))
    if len(seg) == 2:
        inside = seg[1].split("=== 04_update_daily", 1)[0]
        print("verdict-in-03-seg=%s" % ('"verdict"' in inside))
        print("03-seg-head=%r" % inside[:200])
