# r379 bm-c W105 finalize closeout: prereg S7/S8 mechanical backfill (bytes-safe, r530 law; r588bm-a pattern)
import sys
P = 'research/PERPETUAL_N1_W105_PREREG.md'
raw = open(P, 'rb').read()
ph = ("## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010\u8dd1\u524d\u5fc5\u987b\u4e3a\u7a7a\u2014\u2014\u5360\u4f4d\u7eaa\u5f8b\uff1a\u5199\u6570\u5b57\u5373\u9020\u5047\u3011\n"
      "\n- \uff08finalize \u843d\u8d26\u540e\u673a\u68b0\u56de\u586b\uff1b\u4e24\u6001\u817f\u65ad\u8a00\u5728\u573a=r307 \u5f8b\uff09\n"
      "\n## \u00a78 \u6279\u540e\u590d\u76d8\u3002\u3010\u5fc5\u586b\u00b7\u7ec8 7-T\u3011\n"
      "\n- \uff08finalize \u843d\u8d26\u540e\u673a\u68b0\u56de\u586b\uff09\n").encode('utf-8')
ph_crlf = ph.replace(b'\n', b'\r\n')
if ph in raw:
    eol = b'\n'; old = ph
elif ph_crlf in raw:
    eol = b'\r\n'; old = ph_crlf
else:
    print('PLACEHOLDER NOT FOUND'); sys.exit(1)
NB = eol
S7 = ("## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010r376 \u51bb\u7ed3\u5360\u4f4d\u00b7r379 bm-c finalize \u6536\u53e3\u673a\u68b0\u56de\u586b\u3011").encode('utf-8')
S8 = ("## \u00a78 \u6279\u540e\u590d\u76d8\u3002\u3010\u5fc5\u586b\u00b7\u7ec8 7-T\u3011").encode('utf-8')
L = [
 "- 12/12 \u5206\u7247 bm-c \u5f15\u64ce\u70e7\u6bd5\uff08r376 \u51bb\u7ed3\u7a97\u8d77\u70e7\u00b7\u9996 9 \u7247 r376 wrap \u843d\u8d26+\u5c3e 3 \u7247 83438cc37 \u4ea4\u4ed8 origin\u00b7finalize \u524d 12/12 \u5b8c\u5907+origin \u96f6 n1_w105_results \u5728\u573a\u6838\u9a8c\uff09\uff1bfinalize one-pass\uff08r538 \u5f8b\u00b7\u9996\u8dd1\u7981\u91cd\u8dd1\u00b7r379 \u9996\u8dd1=\u552f\u4e00\u4e00\u8dd1\uff09\u3002",
 "- ledger\uff1aprev_total 593,348\uff08W104 bm-a r588 0abbaa458 \u843d\u8d26\u89e3\u9501\u00b7\u94fe\u5e8f W102 588,948 bm-c\u2192W103 591,148 bm-b\u2192W104 593,348 bm-a\uff09+ batch_trials 2,200 = **595,548**\uff1bvoids_applied=LOWAMP-P1/P2\u3002",
 "- w105-only\uff1an=2,200\u00b7mu=\u22120.087087954545454552\u00b7sigma=0.2392291964349654\uff1bmerged\uff1aK=228,920\u00b7mu=\u22120.092706789708195014\u00b7sigma=0.24480936713499979\u3002",
 "- skill_line_v2 @n_eff_held 593,348\uff1a1.1698\u2192**1.1696**\uff08K-lift delta \u22120.0002 \u2265\u22120.02 \u95e8\u5185\u00b7\u6b63\u8d1f\u4ea4\u66ff\u5982\u5b9e\u62a5\u3014W100 \u22120.0005\u2192W101 \u22120.0003\u2192W102 +0.0001\u2192W103 +0.0005\u2192W104 \u22120.0001\u2192W105 \u22120.0002\u3015\uff09\uff1bse_mu @K228,920=0.000512\uff08\u6536\u7a84\u94fe\u6301\u7eed\uff1aW99 0.000527\u2192W104 0.000514\u2192W105 0.000512\uff09\uff1bcanon_flip \u672a\u6267\u884c\uff08\u6cbb\u7406\u63d0\u6848\u9762\u00b7K2200 \u540c\u6cd5\uff09\u3002",
 "- \u00a75 \u9884\u6d4b\u56db\u95e8\u5168\u8fc7\uff08\u51bb\u7ed3\u951a=W99 finalize \u5b9e\u6d4b\u952e\u00b7\u8d77\u8349\u7a97\u6700\u65b0\u5df2\u843d\u8d26\u9762\u00b7r576 \u951a\u6eda\u52a8\u5f8b\uff09\uff1a|\u0394mu|=0.0056<0.02\uff08W105-only \u22120.0871 \u00b7 \u5355\u6ce2\u504f\u79bb\u9762\u5982\u5b9e\u62a5\u00b7\u95e8\u5185\uff09\uff1b\u03c3 \u53d8\u5316 \u22120.0465%<\u00b110%\uff08\u951a 0.24492323649678793\u00b7\u672c\u6ce2 merged 0.24480936713499979\uff09\uff1bA \u6863 p95 \u5dee \u22120.0224<0.05\uff08\u951a 0.3262\u00b7\u672c\u6ce2 0.3038\u00b7n=2,000\uff09\uff1bK-lift \u22120.0002\u2265\u22120.02\u3002\u4ea7\u7269 results/perpetual_faces/n1_w105_results.json\uff08\u9876\u5c42 evidence_cutoff=2026-09-22\u00b7audit.machine=bm-c\u00b7finalize_only=True\u00b7shards_consumed 12\uff09\u3002",
 "",
]
L8 = [
 "- \u5168\u94fe\u4ea7\u54c1\u6d41\u5065\u5eb7\uff1aW105 \u70e7\u5f55\uff08bm-c \u5f15\u64ce 12/12\u00b783438cc37 \u4ea4\u4ed8\uff09\u2192finalize\uff08r379 \u9996\u8dd1\u4e00\u8fc7\uff09\u2192\u94fe\u5934 595,548 \u843d\u8d26\u00b7K=228,920\uff1b\u4e0b\u6e38 W106 finalize \u968f\u5373\u89e3\u5c01\uff08W106 bm-b \u70e7\u6bd5\u5019\u94fe\u5e8f\uff09\u3002",
 "- \u8bda\u5b9e\u6ce8\u8bb0\uff1a\u00a75 \u51bb\u7ed3\u951a=W99\uff08\u8d77\u8349\u7a97\u6700\u65b0\u5df2\u843d\u8d26 finalize\u00b7r376 \u51bb\u7ed3\u65f6\u70b9\uff09\u00b7\u6536\u53e3\u7a97 W100..W104 \u4e94\u6ce2\u5df2\u76f8\u7ee7\u843d\u8d26=\u951a\u6eda\u52a8\u5f8b\u5408\u6cd5\u8de8\u952e\uff08r576\uff09\uff1b\u56db\u95e8\u5728 W99 \u951a\u4e0a\u5168\u8fc7\u3002",
 "- \u8f6e\u8f6c\u9762\uff1a\u672c\u673a\u4e0b\u4e00\u81ea\u6709\u6ce2 finalize \u5ea7\u4f4d\u5f85\u94fe\u5e8f\uff08W108 \u70e7\u6bd5 12/12\u00b7finalize \u5019 W106/W107 \u94fe\u5e8f\uff09\uff1bW110 \u5e2d\u4f4d bm-a \u5df2\u516c\u793a\uff08MSG-20261002-1829-bma\uff09\u00b7W111 \u53d6\u53f7\u987b\u5f85 W110 \u6ce8\u518c\u540e\u3002",
 "",
]
body = S7 + NB + NB.join(l.encode('utf-8') for l in L) + NB + S8 + NB + NB.join(l.encode('utf-8') for l in L8)
new = body
assert raw.count(old) == 1
raw2 = raw.replace(old, new)
assert raw2 != raw and raw2.count(new) == 1
open(P, 'wb').write(raw2)
print('S7/S8 backfilled bytes=%d (eol=%r)' % (len(new), eol))
