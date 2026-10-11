# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
t = open(r"research\PERPETUAL_N1_W212_PREREG.md", encoding="utf-8").read()
i = t.find("5. **W213+ \u6295\u5f71")
phys = t[i:i+400]
mine = ("5. **W213+ \u6295\u5f71\uff08probe \u673a\u8bc1 leg4\u00b7\u4e0b\u6ce2\u51bb\u7ed3\u65b9\u590d\u6838\u975e\u8f6c\u6284 r587 \u5f8b\uff09**\uff1aA naive first-clean 483_204..485_203 CLEAN\uff08hops=0\u00b7pre-W212 \u5b87\u5b99\uff09\uff1bB naive first-clean **483_404..483_603 CLEAN**\uff08hops=0\uff09\u2014\u2014**naive B \u843d\u5728 naive A \u7a97\u5185**\uff08W141 \u540c\u7a97\u4e92\u65a5\u5148\u4f8b\u9002\u7528\u4e8e W213\uff1aW213 \u51bb\u7ed3\u65b9\u5fc5\u987b\u5728 post-W212 \u6ce8\u518c\u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u2014\u2014leg2 \u5f8b/E36 \u5361\uff09\uff1b**W212 B \u5e26 483_204..483_403 \u6ce8\u518c\u540e\u5c06\u62d2 naive W213 A \u7a97**\u2014\u2014W213 A \u91cd derive \u540c\u5f3a\u5236\uff08\u8d8a\u8fc7 W212 B \u5e26\u00b7\u9636\u68af A-hops-prior-B \u7b2c\u4e03\u5341\u4e09\u4f8b\uff09\uff1bverify at W213 prereg\uff0chip \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\u3002")
n = min(len(phys), len(mine))
for k in range(n):
    if phys[k] != mine[k]:
        print(f"divergence at {k}: phys={phys[max(0,k-15):k+15]!r}")
        print(f"                   mine={mine[max(0,k-15):k+15]!r}")
        break
else:
    print("common prefix", n, "phys len", len(phys), "mine len", len(mine))
