# r583 bm-a: W96 prereg sec7/8 mechanical backfill (bytes-safe, LF preserved, W95 r582bm-b pattern; anchors re-derived from file bytes after first-miss)
import json

P = 'research/PERPETUAL_N1_W96_PREREG.md'
b = open(P, 'rb').read()
assert b.count(b'\r\n') == 0, 'expected pure LF file'
s = b.decode('utf-8')

old7 = '## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010\u8dd1\u524d\u5fc5\u987b\u4e3a\u7a7a\u2014\u2014\u5360\u4f4d\u7eaa\u5f8b\uff1a\u5199\u6570\u5b57\u5373\u9020\u5047\u3011\n\n- \uff08finalize \u843d\u8d26\u540e\u673a\u68b0\u56de\u586b\uff1b\u4e24\u6001\u817f\u65ad\u8a00\u5728\u573a=r307 \u5f8b\uff09\n'
old8 = '## \u00a78 \u6279\u540e\u590d\u76d8\u3002\u3010\u5fc5\u586b\u00b7\u7ec8 7-T\u3011\n\n- \uff08finalize \u843d\u8d26\u540e\u673a\u68b0\u56de\u586b\uff09\n'

assert s.count(old7) == 1, 'sec7 anchor count=%d' % s.count(old7)
assert s.count(old8) == 1, 'sec8 anchor count=%d' % s.count(old8)

d = json.load(open('results/perpetual_faces/n1_w96_results.json', encoding='utf-8'))
npc = d['null_pool_cumulative']
sl = d['skill_line_v2_k_lift']
mu_w = npc['w96_only']['mu']; sig_w = npc['w96_only']['sigma']
mu_m = npc['merged']['mu']; sig_m = npc['merged']['sigma']
a_runs = d['families']['A_random_engine_exit']['runs']
full = sorted(r['full']['sharpe'] for r in a_runs)
import math
p95 = full[int(math.ceil(0.95 * len(full))) - 1]
delta_mu = abs(mu_w - mu_m)
sig_rel = abs(sig_w / sig_m - 1.0)
p95_gate = abs(p95 - 0.3256)
kl = sl['line_delta_k_lift']
assert delta_mu < 0.02 and sig_rel < 0.10 and p95_gate < 0.05 and kl <= 0.02, \
    'sec5 gate FAIL: %r %r %r %r' % (delta_mu, sig_rel, p95_gate, kl)

new7 = (
'## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010r581 \u51bb\u7ed3\u5360\u4f4d\u00b7r583 finalize \u6536\u53e3\u673a\u68b0\u56de\u586b\u3011\n\n'
'- 12/12 \u5206\u7247 bm-a \u5f15\u64ce\u70e7\u6bd5\uff08r581/r582 \u7a97\u5b9e\u51b5\u00b7\u4ea7\u54c1 12/12 \u5df2\u4ea4\u4ed8 origin=r310 \u5b8c\u5907\u6027\u95e8\u5b9e\u6838\uff09\uff1bfinalize one-pass\uff08r538 \u5f8b\u00b7\u9996\u8dd1\u7981\u91cd\u8dd1\u00b7\u672c\u5730\u65e0\u81ea\u4ea7\u6ce2\u4ef6\u524d\u7f6e\u6838\u9a8c\u00b7r583 \u8fd0\u884c\uff09\u3002\n'
'- ledger\uff1aprev_total 573,548\uff08W95 bm-b r582 16:13 \u843d\u8d26\u89e3\u9501\uff1b\u94fe\u5e8f W92 566,948 bm-c\u2192W93 569,148 bm-b\u2192W94 571,348 bm-a\u2192W95 573,548 bm-b\uff09+ batch_trials 2,200 = **575,748**\uff1bvoids_applied=LOWAMP-P1/P2\u3002\u8d77\u8349\u7a97\u6295\u5f71\u94fe\u5934 564,748\uff08W91\uff09\u2192\u8fd0\u884c\u65f6 derive 573,548=\u6cd5\u5185\u6eda\u52a8\u9762\u5b9e\u51b5\u5982\u5b9e\u62ab\u9732\uff08r576 \u951a\u6eda\u52a8\u5f8b\uff09\u3002\n'
'- w96-only\uff1an=2,200\u00b7mu=\u22120.0930500\u00b7sigma=0.2476040\uff1bpre-pool\uff1an=206,920\u00b7mu=\u22120.0928112\u00b7sigma=0.2448052\uff1bmerged\uff1an=209,120\u00b7mu=\u22120.0928137\u00b7sigma=0.2448342\u3002\n'
'- \u00a75 \u95e8 4/4 PASS\uff1a\u2460 W-only vs merged mu \u5dee |{d:.5f}|<0.02 \u2713\uff1b\u2461 sigma \u76f8\u5bf9\u53d8\u5316 {r:.2%}<\u00b110% \u2713\uff1b\u2462 A \u6865 full_sharpe_p95 {p:.4f} vs \u95e8\u6807 0.3256 \u5dee {pg:.4f}<0.05 \u2713\uff08\u7ed3\u679c\u77e5\u60c5\u62a5\u8d26\u9762\u00b7\u975e\u6ce8\u518c\u6536\u76ca\uff09\uff1b\u2463 K-lift \u7ebf\u79fb {k:+.4f}\u22640.02 \u2713\uff08\u6b63\u8d1f\u4ea4\u66ff\u5982\u5b9e\u62a5\uff09\u3002\n'
'- skill_line_v2 @n_eff_held 573,548\uff1a1.1679\u2192**1.168**\uff08K-lift delta +0.0001\uff09\uff1bse_mu @K209,120=0.000535\uff08\u6536\u7a84\u94fe\uff1aW93 0.000544\u2192W94 0.000541\u2192W95 0.000538\u2192W96 0.000535\uff09\uff1bcanon_flip \u672a\u6267\u884c\uff08K2200 \u540c\u4f8b\u00b7\u6cbb\u7406\u63d0\u6848\u9762\uff09\u3002\n'
).format(d=delta_mu, r=sig_rel, p=p95, pg=p95_gate, k=kl)

new8 = (
'## \u00a78 \u6279\u540e\u590d\u76d8\u3002\u3010\u5fc5\u586b\u00b7\u7ec8 7-T\u00b7r583 \u673a\u68b0\u56de\u586b\u3011\n\n'
'- \u5ef6\u8bef\u5b9a\u6027\uff1ar582 wrap \u6587\u672c\u300cW94 finalize landed (ledger 571,348 K=204,720)\u300d\u4ec5\u8fbd W94 \u5355\u6ce2\u5b9e\u51b5\uff08K 204,720=W92 200,320+W93 2,200+W94 2,200 \u9010\u4f4d\u5bf9\u8d26\uff09\uff1bW96 finalize \u5728 r582 \u7a97\u672a\u8dd1\uff08\u65e0\u53cc\u8ba1\u65e0\u94fe\u65ad\u00b7\u5e8f\u4f4d\u7a7a\u7f3a\u5408\u6cd5\uff09\uff0cr583 \u6309\u94fe\u5e8f\u8865\u8dd1\u6536\u53e3\u2014\u2014\u5bf9\u7167 MSG-20261002-012x finalize-chain-priority\uff08W93 bm-b\u2192W94 bm-a\u2192W95 bm-b\u2192W96 bm-a\uff09\u3002\n'
'- \u672c\u673a\u5f15\u64ce\u4ef6\u9762\uff1aW98\uff08\u672c\u673a r582 \u51bb\u7ed3\u00b7\u5206\u7247 12/12 \u5df2\u4ea4\u4ed8 origin\uff09finalize \u88ab W97\uff08bm-b \u6ce8\u518c\u00b7\u70e7\u6bd5\u672a finalize\uff09\u5360\u4f4d\u963b\u585e\uff08\u6c60\u626b\u63cf FAIL-CLOSED \u786c\u62d2\u7f3a\u4ef6\uff09\u2014\u2014\u94fe\u5e8f\u4f9d\u8d56\u5982\u5b9e\u7559\u75d5\uff0c\u5f85 bm-b W97 \u843d\u8d26\u540e\u4e0b\u8f6e\u6536\u53e3\uff1b\u672c\u8f6e\u7981\u8de8\u5e2d\u4ee3\u8dd1\uff08\u4ed6\u673a\u6ce8\u518c\u9762\u7981\u78b0\uff09\u3002\n'
'- \u53cc\u8dd1\u786e\u5b9a\u6027\u5f8b\uff1a\u540c seed \u5206\u7247\u4ef6\u5b57\u8282\u6052\u7b49\u4fdd\u969c\u96f6\u53cc\u8ba1\uff1b\u672c\u6ce2 one-pass \u65e0\u91cd\u8dd1\u9762\uff08r538\uff09\u3002\n'
)

s2 = s.replace(old7, new7).replace(old8, new8)
assert s2 != s and s2.count('\u00a77') == s.count('\u00a77')
open(P, 'wb').write(s2.encode('utf-8'))
print('backfill written; bytes:', len(b), '->', len(s2.encode('utf-8')))
print('gates: d_mu=%.5f sig_rel=%.4f p95=%.4f(gate_d=%.4f) k_lift=%+.4f' % (delta_mu, sig_rel, p95, p95_gate, kl))
