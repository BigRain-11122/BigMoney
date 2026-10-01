# r562 bm-a: W57 prereg S7/S8 mechanical backfill (r307/r412 two-state law;
# bm-b _r561bmb_w5356_backfill precedent format). ALL numbers derived from
# results/perpetual_faces/n1_w57_results.json + anchor waves' own results
# files -- no hand transcription (derive-not-copy law). Byte-level edit per
# r500/r530 lesson: probe line endings, bytes in / bytes out.
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

M = '\u2212'  # U+2212 minus sign, prereg prose convention

def fmt(v, nd=6):
    return f"{v:.{nd}f}".replace('-', M)

def pct(v, nd=2):
    return f"{v:+.{nd}f}%".replace('-', M)

def signed(v, nd=4):
    return f"{v:+.{nd}f}".replace('-', M)

FP = 'research/PERPETUAL_N1_W57_PREREG.md'
raw = open(FP, 'rb').read()
crlf = raw.count(b'\r\n'); lf = raw.count(b'\n') - crlf
NL = b'\r\n' if crlf > lf else b'\n'
print('line endings: CRLF=%d LF=%d -> using %s' % (crlf, lf, 'CRLF' if NL==b'\r\n' else 'LF'))
text = raw.decode('utf-8')

# frozen-criteria presence assert (S5 gate strings must be in the prereg)
for probe in ('0.02', '10%', '0.05', '0.02'):
    assert probe in text, 'criteria probe missing: ' + probe

R = json.load(open('results/perpetual_faces/n1_w57_results.json', encoding='utf-8'))
R52 = json.load(open('results/perpetual_faces/n1_w52_results.json', encoding='utf-8'))
R56 = json.load(open('results/perpetual_faces/n1_w56_results.json', encoding='utf-8'))

np_ = R['null_pool_cumulative']
mu, sig = np_['w57_only']['mu'], np_['w57_only']['sigma']
merged = np_['merged']; mk = merged['n_values']
se = np_.get(f'se_mu_at_k{mk}')
p95 = R['families']['A_random_engine_exit']['full_sharpe_p95']
skl = R['skill_line_v2_k_lift']; kl = skl['line_delta_k_lift']
n_eff_held = skl['n_eff_held_equal']
lg = R['science_gates']['ledger']
prev, total = lg['prev_total'], lg['total']

# draft anchor = W52-only (frozen in prereg S5); rolling anchor = W56 (r516 derive law)
A_MU = R52['null_pool_cumulative']['w52_only']['mu']
A_SIG = R52['null_pool_cumulative']['w52_only']['sigma']
A_P95 = R52['families']['A_random_engine_exit']['full_sharpe_p95']
R_MU = R56['null_pool_cumulative']['w56_only']['mu']
R_SIG = R56['null_pool_cumulative']['w56_only']['sigma']
R_P95 = R56['families']['A_random_engine_exit']['full_sharpe_p95']

d_mu = abs(mu - A_MU); d_sig = (sig - A_SIG) / A_SIG * 100; d_p95 = p95 - A_P95
rd_mu = abs(mu - R_MU); rd_sig = (sig - R_SIG) / R_SIG * 100; rd_p95 = p95 - R_P95
assert d_mu < 0.02 and abs(d_sig) < 10 and abs(d_p95) < 0.05 and abs(kl) <= 0.02, 'W57 draft-anchor criteria FAIL'
assert rd_mu < 0.02 and abs(rd_sig) < 10 and abs(rd_p95) < 0.05, 'W57 rolling-anchor criteria FAIL'
assert prev == 487748 and total == 489948 and mk == 123320, 'ledger/merge envelope FAIL'
print('criteria 4/4 PASS both anchors; ledger prev=%d total=%d K=%d se=%s' % (prev, total, mk, se))

def enc(s):
    return s.encode('utf-8').replace(b'\n', NL)

S7_OLD = "## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3010\u8dd1\u524d\u5fc5\u987b\u4e3a\u7a7a\u2014\u2014\u5360\u4f4d\u7eaa\u5f8b\uff1a\u5199\u6570\u5b57\u5373\u9020\u5047\u3011\n\n- \uff08\u7a7a\u2014\u2014finalize \u540e\u673a\u68b0\u56de\u586b\uff09\n\n"
S8_OLD = "## \u00a78 \u6279\u540e\u590d\u76d8\u3010\u5fc5\u586b\u00b7s7-T\u3011\n\n- \uff08\u7a7a\u2014\u2014finalize \u540e\u673a\u68b0\u56de\u586b\uff09\n\n"

s7 = (
    f"## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3010\u8dd1\u524d\u5fc5\u987b\u4e3a\u7a7a\u2014\u2014\u5360\u4f4d\u7eaa\u5f8b\uff1a\u5199\u6570\u5b57\u5373\u9020\u5047\u3011\n\n"
    f"- finalize one-pass 2026-10-02 07:0x\uff08bm-a r562 \u540c\u7a97\u6536\u53e3\uff1abm-a r561 \u51bb\u7ed3 e3525e8ea\uff08A 157_004..159_003 / B 47_401..47_600\uff09\u2192\u672c\u673a tick \u5f15\u64ce\u70e7\u5f55 12/12\uff08\u5206\u7247 mtime 06:39..06:50 \u672c\u7a97\u70e7\u6bd5\u00b7\u5916\u79d1\u4ea4\u4ed8 origin r310 \u5b8c\u5907\u6027\u95e8\u540c commit\uff09\u2192\u672c\u7a97 finalize one-pass\uff1b\u94fe\u5e8f\u89e3\u9501=W53\uff08bm-c r352 \u9057\u4ea7 r353 \u6536\u517b\u843d\u8d26\uff09\u2192W54\u2192W55\u2192W56\uff08bm-b r561 \u94fe\u5f0f\u4e09\u8fde\u540c\u7a97\u843d\u8d26\uff09\u2192\u672c\u6ce2\u5168\u94fe W1..W57 \u8ffd\u5e73\u3001\u96f6\u5728\u98de\u4e0a\u6e38\u9762\uff1b\u540c\u7a97\u62ab\u9732\uff1a\u672c\u673a W53/W54 finalize \u9996\u8dd1\u5757\u4e0e origin \u5148\u8fbe\u5757\uff08bm-c/bm-b\uff09\u540c\u5934\u540c\u6570\u5b66\u9010\u4f4d\u540c\uff08\u786e\u5b9a\u6027\u5f8b\u4e09\u673a\u4ea4\u53c9\u9a8c\u8bc1\u5b9e\u8bc1\uff09\uff0c\u6309 r518 origin \u5148\u8fbe\u4e3a\u94fe\u4f4d\u672c\u673a\u8ba9\u8def\u3001\u672a\u63a8\u5757\u96f6\u5165\u8d26\u96f6\u6c61\u67d3\u3002\n"
    f"- S5 \u5224\u636e 4/4 PASS \u53cc\u951a\uff08\u951a\u6eda\u52a8\u5f8b\u62ab\u9732\uff1a\u8d77\u8349\u7a97\u951a=W52-only \u5b9e\u6d4b\u51bb\u7ed3\u9762\uff1bfinalize \u7a97\u6eda\u52a8\u951a=**W56 \u5b9e\u6d4b**\uff08\u6700\u65b0\u5df2\u843d\u8d26\u00b7r516 derive \u5f8b\uff09\u2014\u2014\u53cc\u951a\u5747 4/4\uff09\uff1a\n"
    f"  1. mu \u6f02\u79fb\uff1aW57-only **{fmt(mu)}** vs W52 \u951a {fmt(A_MU)}\u3010|\u0394|={d_mu:.4f}<0.02 PASS\u3011\uff0fvs W56 \u6eda\u52a8\u951a {fmt(R_MU)}\u3010|\u0394|={rd_mu:.4f}<0.02 PASS\u3011\uff1bmerged\uff08K={mk:,}\uff09**{fmt(merged['mu'])}**\u3002\n"
    f"  2. sigma \u76f8\u5bf9\u53d8\u5316\uff1aW57-only **{fmt(sig)}** vs W52 \u951a {fmt(A_SIG)}\u3010{pct(d_sig)}<\u00b110% PASS\u3011\uff0fvs W56 \u951a {fmt(R_SIG)}\u3010{pct(rd_sig)}<\u00b110% PASS\u3011\uff1bmerged **{fmt(merged['sigma'])}**\u3002\n"
    f"  3. A \u65cf full_sharpe_p95\uff1a**{p95:.4f}** vs W52 \u951a {A_P95:.4f}\u3010\u0394={signed(d_p95)}<0.05 PASS\u3011\uff0fvs W56 \u951a {R_P95:.4f}\u3010\u0394={signed(rd_p95)}<0.05 PASS\u3011\uff08\u95e8\u6821\u51c6\u6ce8\u8bb0\uff1a\u7ed3\u679c\u77e5\u60c5\u6821\u51c6\u9762\u00b7\u6d4b\u91cf\u9762\u96f6\u6ce8\u518c\u5229\u5bb3\uff09\u3002\n"
    f"  4. K-lift \u7ebf\u79fb\u52a8\uff1a**{signed(kl)}\u3010{skl[f'line_pre_w57']}->{skl[f'line_merged_{mk}']} @n_eff_held {n_eff_held:,}\u3011\u22640.02 PASS\uff08W3..W56 \u5148\u4f8b\u65cf\u5185\u6b63\u8d1f\u4ea4\u66ff\u2014\u2014\u52a0\u6df1\u4e0d\u5fc5\u7136\u62ac\u7ebf\u5148\u4f8b\u7eed\u00b7\u5982\u5b9e\u62a5\u6b63\u8d1f\uff09\u3002\n"
    f"- \u8d26\u672c\uff1aprev **{prev:,}**\u3010==W56 finalize \u843d\u8d26\u5934\u00b7derive \u7981\u624b\u6284\u81ea\u8bc1\u3011\uff0b\u672c\u6ce2 2,200\uff1dtotal **{total:,}**\u00b7voids_applied LOWAMP-P1/P2 \u7ee7\u627f\u9762 \u2713\uff1bskill_line_v2 \u6d88\u8d39 n_eff={n_eff_held:,}\uff08W57 \u5408\u5e76\u6c60 K={mk:,} \u540c\u6b65\u52a0\u6df1\u00b7se_mu {se}\uff09\u3002\n"
)
s8 = (
    f"## \u00a78 \u6279\u540e\u590d\u76d8\u3010\u5fc5\u586b\u00b7s7-T\u3011\n\n"
    f"- \u8bbe\u8ba1\u96f6\u504f\u5dee\uff1afrozen v1 \u8bbe\u8ba1\u9010\u5b57\u590d\u7528\uff08run_one \u5f15\u64ce\u540c\u6e90\uff09\uff0cW57-only mu/sigma \u4e0e\u5148\u4f8b\u65cf\u3010W2..W56\u3011\u9010\u9762\u540c\u57df\uff0c\u96f6\u65ad\u88c2\u4fe1\u53f7\uff1bB \u65cf p_exit=0.05 \u914d\u5bf9\u5f8b\u9f50\u5907\uff08n=200\uff09\u3002\n"
    f"- \u6ce2\u8282\u594f\u9762\uff1aW57=bm-a r561 \u51bb\u7ed3 e3525e8ea\u2192\u672c\u673a tick \u5f15\u64ce\u70e7\u5f55\uff08r535 \u67b6\u6784\u00b7\u5206\u7247\u9010\u5206\u949f\u81ea\u7136\u5b8c\u6210 12/12\uff09\u2192r562 \u540c\u7a97 finalize one-pass \u6536\u53e3\uff08r538 \u4e00\u8fc7\u5b9a\u7a3f\uff09\uff1b\u540c\u7a97\u94fe\u9762 W53/W54/W55/W56 \u7531 bm-c/bm-b \u843d\u8d26\uff0c\u672c\u673a W53/W54 \u540c\u7a97\u9996\u8dd1\u5757\u8ba9\u8def\uff08r518 \u5f8b\u00b7\u96f6\u6c61\u67d3\uff09\u3002\n"
    f"- \u6d4b\u91cf\u9762\u7ed3\u8bba\uff1a\u7d2f\u8ba1 null \u6c60 K={mk:,}\u3010+W57 2,200 \u5408\u5e76\u3011\uff0cmu {fmt(merged['mu'],4)} / sigma {fmt(merged['sigma'],4)} \u7a33\u5b9a\uff0cse_mu \u968f\u7d2f\u8ba1\u52a0\u6df1\u6536\u7a84\uff08{se}\uff09\u2014\u2014null \u57fa\u7ebf\u7f6e\u4fe1\u9762\u7ee7\u7eed\u52a0\u6df1\uff0c\u65e0\u8d28\u53d8\uff1bcanon flip \u4e0d\u5728\u672c\u6ce2\uff08\u6cbb\u7406\u63d0\u6848\u9762\u7d20\u6750\u7d2f\u8ba1\u00b7K2200 \u540c\u5f8b\uff09\u3002\n"
    f"- \u4e0b\u6e38\u63a5\u7ebf\uff1askill_line_v2 @n_eff {n_eff_held:,} \u7ebf {skl[f'line_merged_{mk}']}\uff08{signed(kl)}\uff09\uff1b\u4e0b\u4e00\u6ce2 finalize \u6d88\u8d39\u672c\u6ce2 {total:,} \u4e3a prev\uff1b**W58+ \u8b66\u793a\u627f\u7ee7**\uff1aA 159_004..161_003 \u4e0e B 47_601..47_800 \u53cc\u4fa7 CLEAN\uff08bm-a r561 \u5e26\u95f8\u673a\u8bc1\u6295\u5f71\uff09\u2014\u2014W58 \u51bb\u7ed3\u7a97\u4ecd\u987b\u5e26\u95f8 derive \u590d\u6838\uff08r535 \u5f8b\uff09\uff1b\u5168\u94fe W1..W57 \u8ffd\u5e73\u00b7\u96f6\u5728\u98de\u4e0a\u6e38\u9762\u3002\n"
)

for old, new in ((S7_OLD, s7), (S8_OLD, s8)):
    old_b = enc(old); new_b = enc(new)
    if raw.count(old_b) != 1:
        sys.exit('S7/S8 placeholder anchor count != 1 (found %d) -- abort, no edit' % raw.count(old_b))
    raw = raw.replace(old_b, new_b)

open(FP, 'wb').write(raw)
print('backfilled', FP, '| new bytes:', len(raw))
# verify: placeholders gone, two-state law (post-burn state present)
assert 'finalize 后机械回填）\n\n' not in raw.decode('utf-8'), 'placeholder residue'
print('two-state verification: placeholders replaced, post-burn state in place')
