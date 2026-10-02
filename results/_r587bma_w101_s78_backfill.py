# -*- coding: utf-8 -*-
"""W101 prereg SS7/SS8 mechanical backfill (r307 two-state law; finalize
landed r587 bm-a one-pass first-run. W99 exemplar r376 pattern)."""
import io, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FP = os.path.join(REPO, "research", "PERPETUAL_N1_W101_PREREG.md")
b = open(FP, "rb").read()
t = b.decode("utf-8")
eol = "\r\n" if t.count("\r\n") * 2 > t.count("\n") else "\n"
print("EOL:", repr(eol), "bytes:", len(b))

def rep(old, new, tag):
    global t
    ox = old.replace("\n", eol); nx = new.replace("\n", eol)
    assert t.count(ox) == 1, f"{tag}: anchor count={t.count(ox)}"
    t = t.replace(ox, nx)

# --- SS7 header + placeholder -> backfilled section ---------------------------
OLD7H = ("## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010\u8dd1\u524d\u5fc5\u987b\u4e3a\u7a7a"
         "\u2014\u2014\u5360\u4f4d\u7eaa\u5f8b\uff1a\u5199\u6570\u5b57\u5373\u9020\u5047\u3011")
NEW7H = ("## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010r583 \u51bb\u7ed3\u5360\u4f4d"
         "\u00b7r587 bm-a finalize \u6536\u53e3\u673a\u68b0\u56de\u586b\u3011")
rep(OLD7H, NEW7H, "ss7-header")

OLD7B = "- \uff08finalize \u843d\u8d26\u540e\u673a\u68b0\u56de\u586b\uff1b\u4e24\u6001\u817f\u65ad\u8a00\u5728\u573a=r307 \u5f8b\uff09"
NEW7B = (
    "- 12/12 \u5206\u7247 bm-a \u5e38\u9a7b\u5f15\u64ce\u70e7\u6bd5\uff08r583 bm-a \u51bb\u7ed3 ffd844431 \u540e\u5f15\u64ce\u81ea\u71c3\u00b7\u4ea7\u54c1 12/12 \u5df2\u4ea4\u4ed8 origin\uff09\uff1bfinalize one-pass\uff08r538 \u5f8b\u00b7\u9996\u8dd1\u7981\u91cd\u8dd1\u00b7r587 \u9996\u8dd1=\u552f\u4e00\u4e00\u8dd1\uff09\u3002\n"
    "- ledger\uff1aprev_total 584,548\uff08W100 bm-b r585 \u843d\u8d26\u89e3\u9501\u00b7\u94fe\u5e8f W98 580,148 bm-a\u2192W99 582,348 bm-c\u2192W100 584,548 bm-b\uff09+ batch_trials 2,200 = **586,748**\uff1bvoids_applied=LOWAMP-P1/P2\u3002\n"
    "- w101-only\uff1an=2,200\u00b7mu=\u22120.0950309\u00b7sigma=0.2408679\uff1bmerged\uff1aK=220,120\u00b7mu=\u22120.0928742\u00b7sigma=0.2447945\uff1bmu_delta_w101_vs_w100ext=+0.000127\u3002\n"
    "- skill_line_v2 @n_eff_held 584,548\uff1a1.1689\u2192**1.1686**\uff08K-lift delta \u22120.0003\u22640.02 \u95e8\u5185\u00b7\u6b63\u8d1f\u4ea4\u66ff\u5982\u5b9e\u62a5\u3014W98 +0.0000\u2192W99 +0.0001\u2192W100 +0.0001\u2192W101 \u22120.0003\u3015\uff09\uff1bse_mu @K220,120=0.000522\uff08\u6536\u7a84\u94fe\uff1aW98 0.000530\u2192W99 0.000527\u2192W100 0.000525\u2192W101 0.000522\uff09\uff1bcanon_flip \u672a\u6267\u884c\uff08\u6cbb\u7406\u63d0\u6848\u9762\u00b7K2200 \u540c\u6cd5\uff09\u3002\n"
    "- \u00a75 \u9884\u6d4b\u56db\u95e8\u5168\u8fc7\uff08\u9522\u6eda\u52a8\u5f8b\u5408\u6cd5\u8de8\u952e\u00b7\u51bb\u7ed3\u9522=W96 merged \u22120.0928137\uff09\uff1a|\u0394mu|=0.0022<0.02\uff08W101-only \u22120.0950309\u00b7\u5355\u6ce2\u504f\u79bb\u9762\u5982\u5b9e\u62a5\u00b7\u95e8\u5185\uff09\uff1b\u03c3 \u53d8\u5316 \u22120.02%<\u00b110%\uff08\u9522 0.2448342\u00b7\u672c\u6ce2 merged 0.2447945\uff09\uff1bA \u6863 p95 \u5dee 0.0230<0.05\uff08\u9522 0.3183\u00b7\u672c\u6ce2 0.2953\uff09\uff1bK-lift \u22120.0003\u22640.02\u3002\u4ea7\u7269 results/perpetual_faces/n1_w101_results.json\uff08\u9876\u5c42 evidence_cutoff=2026-09-22\u00b7audit.machine=bm-a\u00b7finalize_only=True\u00b7shards_consumed 12\uff09\u3002")
rep(OLD7B, NEW7B, "ss7-body")

# --- SS8 placeholder -> backfilled bullets (freeze line preserved) ------------
OLD8B = "- \uff08finalize \u843d\u8d26\u540e\u673a\u68b0\u56de\u586b\uff09"
NEW8B = (
    "- \u5168\u94fe\u4ea7\u54c1\u6d41\u5065\u5eb7\uff1aW101 \u70e7\u5f55\uff08bm-a \u5f15\u64ce 12/12\u00b7r583 \u4ea4\u4ed8\uff09\u2192finalize\uff08r587 \u9996\u8dd1\u4e00\u8fc7\uff09\u2192\u94fe\u5934 586,748 \u843d\u8d26\u00b7K=220,120\uff1b\u4e0b\u6e38 W102 bm-c finalize \u968f\u5373\u89e3\u5c01\u3002\n"
    "- \u8bda\u5b9e\u6ce8\u8bb0\uff1a\u00a75 \u51bb\u7ed3\u9522=W96\uff08\u8d77\u8349\u7a97\u6700\u65b0\u5df2\u843d\u8d26 finalize\uff09\u00b7\u6536\u53e3\u7a97 W97..W100 \u56db\u6ce2\u5df2\u76f8\u7ee7\u843d\u8d26=\u9522\u6eda\u52a8\u5f8b\u5408\u6cd5\u8de8\u952e\uff08r576\uff09\uff1b\u56db\u95e8\u5728 W96 \u9522\u4e0a\u5168\u8fc7\u3002")
rep(OLD8B, NEW8B, "ss8-body")

out = t.encode("utf-8")
open(FP, "wb").write(out)
print("backfill written, bytes:", len(out))
# post-verify: no placeholder remains, measured values present
assert "\u8dd1\u524d\u5fc5\u987b\u4e3a\u7a7a" not in t, "placeholder survived"
for probe in ("586,748", "220,120", "1.1686", "0.2953", "ffd844431", "r587"):
    assert probe in t, "missing: " + probe
print("post-verify PASS: placeholders gone, measured values in place")
