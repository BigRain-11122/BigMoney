# r582 bm-b: W95 prereg sec7/8 mechanical backfill (bytes-safe, LF preserved)
import io, sys

P = 'research/PERPETUAL_N1_W95_PREREG.md'
b = open(P, 'rb').read()
assert b.count(b'\r\n') == 0, 'expected pure LF file'
s = b.decode('utf-8')

old7 = '## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010\u8dd1\u524d\u5fc5\u987b\u4e3a\u7a7a\u2014\u2014\u5360\u4f4d\u7eaa\u5f8b\uff1a\u5199\u6570\u5b57\u5373\u9020\u5047\u3011\n\n- \uff08\u5360\u4f4d\u00b7finalize \u540e\u673a\u68b0\u56de\u586b\uff09\n'
old8 = '## \u00a78 \u6279\u540e\u590d\u76d8\u3002\u3010\u5fc5\u586b\u00b7\u7ed3 7-T\u3011\n\n- \uff08\u5360\u4f4d\u00b7finalize \u540e\u673a\u68b0\u56de\u586b\uff09\n'

new7 = (
'## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010r580 \u51bb\u7ed3\u5360\u4f4d\u00b7r582 finalize \u6536\u53e3\u673a\u68b0\u56de\u586b\u3011\n\n'
'- 12/12 \u5206\u7247 bm-b \u5f15\u64ce\u70e7\u6bd5\uff08r580 \u51bb\u7ed3 commit \u540e tick \u67b6\u6784\u81ea\u71c3\u514d\u91cd\u542f\u00b7r535 \u5f8b\u00b7r581 \u7a97 12/12 \u70e7\u6bd5\u00b7\u4ea7\u54c1 12/12 r581 \u5df2\u4ea4\u4ed8 origin=r310 \u5b8c\u5907\u6027\u95e8\u5b9e\u6838\uff09\uff1bfinalize one-pass\uff08r538 \u5f8b\u00b7\u9996\u8dd1\u7981\u91cd\u8dd1\u00b7\u672c\u5730\u65e0\u672a commit \u81ea\u4ea7\u6ce2\u4ef6\u524d\u7f6e\u6838\u9a8c\u00b7r582\uff09\u3002\n'
'- ledger\uff1aprev_total 571,348\uff08W94 bm-a r582 \u843d\u8d26\u89e3\u9501\u00b7\u94fe\u5e8f W89 560,348 bm-b\u2192W90 562,548 bm-a\u2192W91 564,748 bm-b\u2192W92 566,948 bm-c\u2192W93 569,148 bm-b\u2192W94 571,348 bm-a\uff09+ batch_trials 2,200 = **573,548**\uff1bvoids_applied=LOWAMP-P1/P2\u3002\n'
'- w95-only\uff1an=2,200\u00b7mu=\u22120.0977067\u00b7sigma=0.2453123\uff1bmerged\uff1an=206,920\u00b7mu=\u22120.0928112\u00b7sigma=0.2448052\uff08\u00a70 \u6295\u5f71\u300cW94 \u843d\u8d26\u540e K=204,720+\u672c\u6ce2 2,200\u300d\u9010\u4f4d\u543b\u5408\uff09\uff1bmu_delta_w95_vs_w94ext=\u22120.002355\uff08\u672c\u6ce2\u6279\u8f83 W94 \u6279\u66f4\u6df1\u00b7\u4ecd\u6d45\u4e8e\u5b58\u91cf\u6c60\u2014\u2014\u5408\u5e76\u540e mu \u6f02 \u22120.0000526\u00b7\u95e8\u5185\uff09\u3002\n'
'- skill_line_v2 @n_eff_held 571,348\uff1a1.1677\u2192**1.1677**\uff08K-lift delta +0.0000\u22640.02 \u95e8\u5185\u00b7\u6b63\u8d1f\u4ea4\u66ff\u5982\u5b9e\u62a5\u3014W93 \u22120.0002\u2192W94 +0.0000\u2192W95 +0.0000\u3015\uff09\uff1bse_mu @K206,920=0.000538\uff08\u6536\u7a84\u94fe\u5ef6\u7eed\uff1aW91 0.000550\u2192W93 0.000544\u2192W94 0.000541\u2192W95 0.000538\uff09\uff1bcanon_flip \u672a\u6267\u884c\uff08\u6cbb\u7406\u63d0\u6848\u9762\u00b7K2200 \u540c\u6cd5\uff09\u3002\n'
'- \u00a75 \u9884\u6d4b\u56db\u95e8\u5168\u8fc7\uff1a|\u0394mu|=0.0050<0.02\uff08\u00a75 \u51bb\u7ed3\u951a=W91 merged \u22120.0927138\u00b7\u8d77\u8349\u7a97\u6eda\u52a8\u951a\uff09\uff1b\u03c3 \u53d8\u5316 \u22121.30%<\u00b110%\uff08\u951a W91-only 0.2485487\u00b7\u672c\u6ce2 0.2453123\uff09\uff1bA \u6876 p95 \u5dee 0.0184<0.05\uff08\u951a 0.3275\u00b7\u672c\u6ce2 0.3091\uff09\uff1bK-lift +0.0000\u22640.02\u3002\u4ea7\u7269 `results/perpetual_faces/n1_w95_results.json`\uff08\u9876\u5c42 evidence_cutoff=2026-09-22\u00b7cutoff_meta\u00b7audit.machine=bm-b\u00b7shards_consumed 12\uff09\u3002\n'
)

new8 = (
'## \u00a78 \u6279\u540e\u590d\u76d8\u3002\u3010r582 \u8865\u5168\u3011\n\n'
'- \u94fe\u5e8f\u5b9e\u51b5\uff1a\u51bb\u7ed3\u7a97\uff08r580\uff09\u5728\u98de\u4e0a\u6e38\u5e2d\u5df2\u5168\u90e8\u843d\u8d26\uff08W92 bm-c r372\u2192W93 bm-b r581\u2192W94 bm-a r582\uff09\u2014\u2014\u672c\u6ce2 finalize one-pass \u6536\u53e3\uff0cr307 \u4e24\u6001\u5f8b\u8dd1\u65f6\u590d\u6838\u901a\u8fc7\uff08pre-W95 K=204,720\u00b7mu=\u22120.0927586\u00b7sigma=0.2447998 \u4e0e W94 merged \u9010\u4f4d\u543b\u5408=\u94fe\u8fde\u7eed\u6027\u5b9e\u8bc1\uff09\u3001\u96f6\u6539\u5224\u636e\u3002\n'
'- \u4f9b\u7ed9\u9762\uff1a\u672c\u6ce2 finalize \u89e3\u9501 W96 bm-a finalize \u94fe\u5e8f\uff0812/12 \u4ea7\u54c1\u5df2\u5728 origin\uff09\uff1b\u540c\u7a97 W97 bm-b 12/12 \u70e7\u6bd5 finalize-pending\uff08\u94fe\u5e8f\u5019 W96\u00b7\u4ea7\u54c1 12/12 \u672c\u5730\u5f85 ride \u4ea4\u4ed8\uff09+W98 bm-a r582 \u51bb\u7ed3\u5728\u6848\u2014\u2014\u4f9b\u7ed9\u7ebf\u8fde\u7eed\uff1bbm-b \u4e0b\u4e00 finalize=W97\uff08\u5019 W96 \u843d\u8d26+\u672c\u673a\u4ea7\u54c1\u4ea4\u4ed8 origin \u540e\uff09\u3002\n'
'- \u00a75 W96+ \u6295\u5f71\u590d\u6838\uff1aA 235_004..237_003 CLEAN/B 57_701..57_900 CLEAN\u2014\u2014\u4e0b\u6ce2\u51bb\u7ed3\u65b9 bm-a r581 \u673a\u9a8c\u9010\u4f4d\u543b\u5408\uff08ADMIT \u56de\u6267 results/_r581bma_w96_band_gate.py hops 0/0\u00b7r302 \u6295\u5f71\u4e09\u67e5\u5148\u4f8b\uff09\u3002\n'
)

assert old7 in s, 'sec7 placeholder anchor not found'
assert old8 in s, 'sec8 placeholder anchor not found'
s2 = s.replace(old7, new7, 1)
s2 = s2.replace(old8, new8, 1)
assert '\u5360\u4f4d\u00b7finalize \u540e\u673a\u68b0\u56de\u586b' not in s2, 'placeholder residue remains'
open(P, 'wb').write(s2.encode('utf-8'))
print('backfill written, bytes', len(b), '->', len(s2.encode('utf-8')))
