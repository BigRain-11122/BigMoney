# r584 bm-a: W98 prereg sec7/8 mechanical backfill (bytes in/out, LF preserved, r530 law)
# Adoption completion of dead r583 session (finalize ran 16:31, died pre-commit; r471/r322 laws)
import json

P = 'research/PERPETUAL_N1_W98_PREREG.md'
b = open(P, 'rb').read()
assert b.count(b'\r\n') == 0, 'expected pure LF file, got CRLF'
s = b.decode('utf-8')

# verify finalize product numbers before writing (single source: results JSON, no hand copying of derived stats)
d = json.load(open('results/perpetual_faces/n1_w98_results.json'))
npc = d['null_pool_cumulative']
led = d['science_gates']['ledger']
assert led['prev_total'] == 577948 and led['batch_trials'] == 2200 and led['total'] == 580148
assert npc['w98_only']['n_values'] == 2200 and npc['merged']['n_values'] == 213520
assert npc['pre_w98_cumulative']['n_values'] == 211320

OLD7H = '## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010\u8dd1\u524d\u5fc5\u987b\u4e3a\u7a7a\u2014\u2014\u5360\u4f4d\u7eaa\u5f8b\uff1a\u5199\u6570\u5b57\u5373\u9020\u5047\u3011'
NEW7H = '## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010r583 bm-a finalize \u4ea7\u51fa\u00b7r584 \u6536\u517b\u6838\u9a8c\u56de\u586b\uff08\u731d\u6b7b\u4f1a\u8bdd\u6536\u517b r471/r529 \u5f8b\uff09\u3011'
OLD7B = '- \uff08finalize \u843d\u8d26\u540e\u673a\u68b0\u56de\u586b\uff1b\u4e24\u6001\u817f\u65ad\u8a00\u5728\u573a=r307 \u5f8b\uff09'
NEW7B = (
    '- 12/12 \u5206\u7247 bm-a \u5f15\u64ce\u70e7\u6bd5\uff08r582 \u7a97 tick \u81ea\u71c3\u00b7\u5206\u7247\u4ea7\u54c1 12/12 \u5df2\u63a8 origin\uff09\uff1bfinalize one-pass=\u6b7b\u4f1a\u8bdd r583 \u7a97 16:31 \u4ea7\u51fa\uff08r538 \u5f8b\u00b7n1_w98_results.json \u4e3a\u8be5 finalize \u9996\u4ea7\u975e\u9884\u5b58\u00b7r584 \u6536\u517b\u4e09\u8bc1\u6838\u9a8c\uff1aprev=577,948==W97 \u6d3b\u5934\u9010\u4f4d\u5439\u5408+pf 9/9+n1 \u7f3a\u7701\u6ce2 selftest PASS+attrition guard CLEAN \u540e\u843d\u5730\uff09\u3002\n'
    '- ledger\uff1aprev_total 577,948\uff08\u94fe\u5e8f W94 571,348 bm-a\u2192W95 573,548 bm-b\u2192W96 575,748 bm-a\u2192W97 577,948 bm-b \u5747\u5df2\u843d\u8d26\u89e3\u9501\uff09+ batch_trials 2,200 = **580,148**\uff1bvoids_applied=LOWAMP-P1/P2\u3002\n'
    '- w98-only\uff1an=2,200\u00b7mu=\u22120.1046935\u00b7sigma=0.2480436\uff1bmerged\uff1an=213,520\u00b7mu=\u22120.0929463\u00b7sigma=0.2449300\uff08\u00a70\u300c\u7d2f\u8ba1 null \u6c60\u6295\u5f71 211,320+2,200=213,520\u300d\u9010\u4f4d\u5439\u5408\uff09\uff1bmu_delta_w98_vs_w97ext=\u22120.010889\uff08\u5408\u5e76\u540e mu \u6f02 \u22120.000122\u00b7\u95e8\u5185\uff09\u3002\n'
    '- skill_line_v2 @n_eff_held 577,948\uff1a1.1687\u2192**1.1687**\uff08K-lift delta +0.0000\u22640.02 \u95e8\u5185\uff09\uff1bse_mu @K213,520=0.000530\uff08\u6536\u7a84\u94fe W92 0.000547\u2192W93 0.000544\u2192W94 0.000541\u2192W95 0.000538\u2192W96 0.000535\u2192W97 0.000533\u2192W98 0.000530\uff09\u3002\n'
    '- \u00a75 \u56db\u5224\u5168\u8fc7\uff1a\u2460W98-only vs W92 \u952e merged mu |\u0394|=0.0120<0.02 \u2713\uff1b\u2461sigma \u76f8\u5bf9\u53d8\u5316 +0.05%<\u00b110% \u2713\uff1b\u2462A \u6863 full_sharpe_p95 0.3131 vs W92 \u9524 0.3256 \u5dee 0.0125<0.05 \u2713\uff1b\u2463K-lift +0.0000\u2265\u22120.02 \u2713\u3002'
)
OLD8B = '- \uff08finalize \u843d\u8d26\u540e\u673a\u68b0\u56de\u586b\uff09'
NEW8B = (
    '- \u6d4b\u91cf\u52a0\u6df1\u9762\u95ed\u73af\uff1a\u7b2c 88 \u679a\u5f15\u64ce\u6ce2\uff08\u673a\u9762\u8ba1\u6570\uff09\u00b7bm-a \u7b2c 27 \u679a\u81ea\u6709\u5f15\u64ce\u6ce2\u00b7N1 \u7d2f\u8ba1\u6c60 K 213,520\uff08canon 120+W1..W98 \u5168\u843d\u8d26\uff09\uff1b\u96f6\u6ce8\u518c\u5ba3\u79f0\u00b7\u96f6\u5019\u9009\u6c60\u6c61\u67d3\u00b7\u8d26\u672c\u94fe\u6027 577,948\u2192580,148 \u65e0\u8df3\u53f7\u3002\n'
    '- \u672c\u6ce2\u4e3a W93/W94/W95/W96 \u56db\u7a7a\u6863\u5728\u98de\u7a97\u51bb\u7ed3\u7684\u7b2c\u4e00\u6ce2\uff08FAIL-CLOSED r307 \u8dd1\u65f6\u590d\u6838\u6052\u5728\u00b7finalize \u5b9e\u8dd1\u65f6 W93..W97 \u5df2\u5168\u90e8\u843d\u8d26=\u94fe\u5e8f\u81ea\u52a8\u89e3\u9501\u5b9e\u8bc1\uff09\uff1bcanon flip \u4e0d\u5728\u672c\u6ce2\uff08K2200 \u540c\u4f8b\u00b7\u6cbb\u7406\u63d0\u6848\u9762\uff09\u3002\n'
    '- \u51fa\u573a\u8f74=template_default \u6309\u8bbe\u8ba1\u6d4b\u2462\uff08\u6d4b\u91cf\u5224\u7b49 null \u57fa\u7ebf\u817f\uff09\uff1bDATA_GAP \u4e0d\u6d89\uff1bevidence_cutoff=2026-09-22 \u540c\u7a97\u5f8b\u5168\u7a0b\u672a\u6f02\u3002\n'
    '- \u731d\u6b7b\u6536\u517b\u6ce8\u8bb0\uff1afinalize \u7531 r583 \u4f1a\u8bdd\u4ea7\u51fa\u540e\u731d\u6b7b\u4e8e commit \u524d\uff08state \u505c 582+git \u81ea\u6807 r583 \u53cc\u8bc1=r529 \u8bca\u65ad\u5f8b\uff09\u00b7r584 \u6536\u517b\u6838\u9a8c\u843d\u5730\uff08r471 \u5f8b\u00b7\u4ea7\u7269\u4e09\u8bc1\uff1aprev \u5934\u5bf9\u8d26+selftest+attrition guard\uff09\u2014\u2014\u96f6\u91cd\u8dd1\u96f6\u91cd derive\uff08r538 \u7981\u76f2\u91cd\u8dd1\u5f8b\u00b7\u4ea7\u7269\u539f\u6837\u6536\u517b\uff09\u3002'
)

for old, new in ((OLD7H, NEW7H), (OLD7B, NEW7B), (OLD8B, NEW8B)):
    assert s.count(old) == 1, 'non-unique/missing anchor: ' + old[:40]
    s = s.replace(old, new)

open(P, 'wb').write(s.encode('utf-8'))
print('backfill written; bytes:', len(s.encode('utf-8')))
# post-verify: placeholders gone, new markers present
assert OLD7H not in s and OLD7B not in s and OLD8B not in s
assert '580,148' in s and '0.3131' in s and 'r584' in s
print('post-verify OK')
