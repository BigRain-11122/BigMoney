# -*- coding: utf-8 -*-
"""r288: tighten the just-appended CODELY law line under the 50,000B
hot-cold gate (diverged multi-machine face = restructure belongs at
next clean-tree S0, not mid-divergence; overshoot was 98B)."""
p = "CODELY.md"
b = open(p, "rb").read()
i = b.find("- [2026-09-27 02:2x]".encode("utf-8"))
assert i == 49205, f"unexpected entry offset {i}"
entry = (
    "- [2026-09-27 02:2x] \u5751\u5f8b\uff08bm-b r288\u00b7\u63a5\u7ba1\u95e8\u6d3b\u4e3b\u76f2\u533a\u00b7r279 \u5bb6\u65cf\u65b0\u7ef4\u00b7E1 \u81ea\u6355\uff09\uff1a"
    "**\u6279\u5728\u98de>STALE_MIN(20min) \u4e14\u65b0\u9c9c\u5fc3\u8df3\u6ede\u7559\u672c\u5730\uff08push-fallback \u843d machine \u5206\u652f\uff09=\u63a5\u7ba1\u95e8\u5bf9\u9762\u8bfb\u65e7\u9762\u2192\u673a\u5236\u5408\u6cd5\u62a2\u5360+launch=\u771f\u53cc\u70e7**"
    "\uff08CN-TREND \u5b9e\u5f39\uff1a01:40 \u8ba4\u9886+\u6279\u5728\u98de 30min\uff0cbm-a 02:10 tick \u8bfb r286 \u671f\u5fc3\u8df3\u219230>20 \u5224\u9648\u65e7\u2192\u62a2\u5360+launch\uff09\uff1b"
    "\u6b63\u5f8b=\u2460tick \u589e claim-keepalive \u817f\uff08\u672c\u673a runner \u5728\u98de+\u81ea\u6709\u65f6\u5206\u7247\u5237 owner_since\uff0cKEEPALIVE_MIN=10\uff1b\u5bf9\u624b\u76d8\u5206\u7247\u6c38\u4e0d\u89e6\u78b0\uff09"
    "\u2461\u7ade\u901f\u88c1\u5b9a\u7167 r279\u2461\u9996\u8ba4+\u6267\u884c\u8005\u80dc\uff0c\u91cd\u8dd1\u4ea7\u7269 r282 \u5355\u8ba1\u5f8b\u5f03\u7f6e"
    "\u2462\u810f\u6811\u7a97 keepalive push \u4e0d\u53ef\u8fbe\uff08\u5019\u9009\u4fee=tick \u6bcf\u8df3\u81ea commit \u72b6\u6001\u4ef6\uff09\u3002"
    "\u6307\u9488=Tools/autofill.py _keepalive_claims+S17a-d\r\n"
).encode("utf-8")
out = b[:i] + entry
open(p, "wb").write(out)
print("CODELY:", len(b), "->", len(out), "bytes; under 50,000 gate:",
      len(out) < 50000)
