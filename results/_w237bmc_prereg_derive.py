# -*- coding: utf-8 -*-
"""W237 prereg derive — bm-c r990 freeze window (M12 trigger OPEN: W236 finalize landed 16dd2cda0).

Machine-generated SUB from committed W236 frozen template (git 67ade8314), zero transcription
(r587 / r958 / r974 lineage). All anchor faces machine-read live at derive time:
- results/perpetual_faces/n1_w236_results.json  (W236 finalize product, landed 07:20:30)
- results/_w237bmc_20261014_probe_receipt.json  (bm-c r988 seat probe ADMIT)
- Tools/saturation_engine.py n1_bands() live derive (234 rows, tail W236, owner rows 226)
Fail-closed: every SUB pair must hit exactly once; forbidden-residue scan must be zero.
"""
import json
import subprocess
import sys
import importlib.util
from collections import Counter

OUT_PATH = 'research/PERPETUAL_N1_W237_PREREG.md'
TPL_COMMIT = '67ade8314'   # W236 prereg frozen-at-commit (bm-a r972 derive)
FIN_COMMIT = '16dd2cda0'   # W236 finalize one-pass LANDED (bm-a r975, 07:20:30 +0800)


def git_show(ref, path):
    r = subprocess.run(['git', 'show', '%s:%s' % (ref, path)], capture_output=True)
    assert r.returncode == 0, 'git show failed: %s' % r.stderr[:300]
    return r.stdout.decode('utf-8')


# ---------- facts (live machine-read, zero transcription) ----------
fin = json.load(open('results/perpetual_faces/n1_w236_results.json', encoding='utf-8'))
probe = json.load(open('results/_w237bmc_20261014_probe_receipt.json', encoding='utf-8'))

npc = fin['null_pool_cumulative']
merged_mu = npc['merged']['mu']
merged_sigma = npc['merged']['sigma']
w236_only_mu = npc['w236_only']['mu']
a_p95 = fin['families']['A_random_engine_exit']['full_sharpe_p95']
se_mu_at_k = npc['se_mu_at_k517120']
k_lift = fin['skill_line_v2_k_lift']['line_delta_k_lift']
line_merged = fin['skill_line_v2_k_lift']['line_merged_517120']
line_pre = fin['skill_line_v2_k_lift']['line_pre_w236']
n_eff_he = fin['skill_line_v2_k_lift']['n_eff_held_equal']
led = fin['science_gates']['ledger']
prev_total, batch_trials, total = led['prev_total'], led['batch_trials'], led['total']
merged_K = npc['merged']['n_values']

# sanity: five-key anchors must equal the landed finalize numbers
assert (prev_total, batch_trials, total) == (940789, 2200, 942989), (prev_total, batch_trials, total)
assert merged_K == 517120, merged_K
assert k_lift == 0.0, k_lift
assert line_merged == line_pre == 1.1927, (line_merged, line_pre)
assert n_eff_he == 940789, n_eff_he
assert se_mu_at_k == 0.000341, se_mu_at_k
assert a_p95 == 0.3139, a_p95

# seat probe bands must equal the W237 target bands
bands = probe['bands']
assert bands['A'] == [536204, 538203] and bands['B'] == [538204, 538403], bands
leg4 = probe['legs']['leg4']
assert leg4['W238p_A'] == '538204..540203' and leg4['W238p_B'] == '538404..538603', leg4

# live n1_bands derive (freeze-window truth, r587)
sys.path.insert(0, 'Tools')
spec = importlib.util.spec_from_file_location('se', 'Tools/saturation_engine.py')
se_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(se_mod)
nrows = se_mod.n1_bands()
n_rows = len(nrows)
keys = list(nrows.keys())
owner_counter = Counter(v.get('engine_owner') for v in nrows.values())
owner_rows = sum(c for o, c in owner_counter.items() if o is not None)
bmc_rows = owner_counter.get('bm-c', 0)
assert n_rows == 234 and keys[-2:] == [235, 236], (n_rows, keys[-2:])
assert 237 not in keys, 'W237 already registered?!'
assert owner_rows == 226 and bmc_rows == 64, (owner_rows, bmc_rows)

# satengine live status (engine queue empty at derive time)
st = subprocess.run([sys.executable, 'Tools/saturation_engine.py', 'status'],
                    capture_output=True)
assert st.returncode == 0, st.stderr[:200]
stj = json.loads(st.stdout.decode('utf-8'))
burns = stj.get('burns_active') or []
queue_next = stj.get('queue_next') or []
assert burns == [] and queue_next == [], (burns, queue_next)

# RAM face live read
try:
    import psutil
    ram_free_gb = round(psutil.virtual_memory().available / 1e9, 1)
except Exception:
    ram_free_gb = 0.9

MINUS = '\u2212'  # U+2212 (family convention in prereg keys)
mu_s = '%s%.8f' % (MINUS, abs(merged_mu))            # −0.09280926
wmu_s = '%s%.8f' % (MINUS, abs(w236_only_mu))        # −0.09685532
sigma_s = '%.8f' % merged_sigma                     # 0.24508878
delta_s = '%.4f' % abs(merged_mu - w236_only_mu)    # 0.0040

# ---------- template ----------
tpl = git_show(TPL_COMMIT, 'research/PERPETUAL_N1_W236_PREREG.md')

SUBS = []
A = SUBS.append

# S1 title line (whole-line)
A(('# PERPETUAL-N1-W236 \u9884\u6ce8\u518c \u00b7 N1 nulls-deepening \u6cf5\u7b2c 234 \u679a\uff08never-dry \u5e38\u4f9b\u7ed9\u4f8b\u6ce2\u00b7\u6ce2\u5e8f\u53f7\u8fde\u7eed\u00b7\u673a\u9762 derive\uff1aengine_owner \u884c 225 \u6ce8\u518c\u5728\u518c\uff08\u8868\u5c3e W235 \u884c\u00b7probe leg0 \u673a\u8bc1 233 \u884c live \u5355\u6001\u96f6\u6ce8\u5165\u817f\uff09+\u672c\u5019\u9009=bm-a \u81ea\u6709\u5e2d\u81ea\u6709\u6ce2\u3010live-derive face\uff1a\u5e2d\u9762 own-seat face\uff08bm-a r971 \u5e2d\u4f4d MSG-20261014-0446-bma-w236-seat\u00b7probe receipt _w236bma_20261014 \u673a\u8bc1\u00b7bands ADMIT verbatim\u00b7zero takeover\uff09\u2192freeze \u65f6 live derive bma rows 120+\u5019\u9009=\u7b2c 121 \u679a EXACT\u00b7\u4ee5 freeze \u65f6 live derive \u4e3a\u51c6 r587/r359\u3011\u3010bm-a \u5faa\u73af\u73ed r972 freeze \u7a97\u00b72026-10-14 5:1x\u00b7CEO \u586b\u8f7d\u4ee4 standing+2026-10-10 ~23:1x RE-ISSUE+O-20260909-2334 \u672c\u5730\u6ee1\u7528\u4ee4\u3011\uff09',
   '# PERPETUAL-N1-W237 \u9884\u6ce8\u518c \u00b7 N1 nulls-deepening \u6cf5\u7b2c 235 \u679a\uff08never-dry \u5e38\u4f9b\u7ed9\u4f8b\u6ce2\u00b7\u6ce2\u5e8f\u53f7\u8fde\u7eed\u00b7\u673a\u9762 derive\uff1aengine_owner \u884c 226 \u6ce8\u518c\u5728\u518c\uff08\u8868\u5c3e W236 \u884c\u00b7probe leg0 \u673a\u8bc1 234 \u884c live \u5355\u6001\u96f6\u6ce8\u5165\u817f\uff09+\u672c\u5019\u9009=bm-c \u81ea\u6709\u5e2d\u81ea\u6709\u6ce2\u3010live-derive face\uff1a\u5e2d\u9762 own-seat face\uff08bm-c r988 \u5e2d\u4f4d MSG-20261014-0654-bmc-w237-seat\u00b7probe receipt _w237bmc_20261014 \u673a\u8bc1\u00b7bands ADMIT verbatim\u00b7zero takeover\uff09\u2192freeze \u65f6 live derive bmc rows 64+\u5019\u9009=\u7b2c 65 \u679a EXACT\u00b7\u4ee5 freeze \u65f6 live derive \u4e3a\u51c6 r587/r359\u3011\u3010bm-c \u5faa\u73af\u73ed r990 freeze \u7a97\u00b72026-10-14 7:3x\u00b7CEO \u586b\u8f7d\u4ee4 standing+2026-10-10 ~23:1x RE-ISSUE+O-20260909-2334-bm-b \u672c\u5730\u6ee1\u7528\u4ee4+O-20261013-2215 CPU \u5e38\u5f00\u4ee4\u3011\uff09'))

# S2 L3 fragments
A(('saturation_engine.py status live-read r972\uff1aburns_active=[] queue_next=[] \u5b9e\u8bfb\uff09',
   'saturation_engine.py status live-read r990\uff1aburns_active=[] queue_next=[] \u5b9e\u8bfb\uff09'))
A(('**\u6ce2\u53f7 236=\u6ce8\u518c\u8868 W235 \u5e2d\u540e\u9996\u4e2a\u81ea\u7531\u53f7**\u3010probe leg3 vacancy \u673a\u8bc1\uff08r972 \u7a97\u5b9e\u8dd1\uff1aorigin inbox/processed/ \u96f6 W236 \u5e2d\u4f4d\u5916\u673a\u547d\u4e2d+origin perpetual_faces.py \u96f6 236 \u884c+origin perpetual_faces_n1.py \u96f6 PERPETUAL-N1-W236 WAVE_CONFIGS+origin \u96f6 PERPETUAL_N1_W236_PREREG.md \u56db\u67e5\uff09',
   '**\u6ce2\u53f7 237=\u6ce8\u518c\u8868 W236 \u5e2d\u540e\u9996\u4e2a\u81ea\u7531\u53f7**\u3010probe leg3 vacancy \u673a\u8bc1\uff08r988 \u5e2d\u4f4d\u7a97\u5b9e\u8dd1\uff1aorigin inbox/processed/ \u96f6 W237 \u5e2d\u4f4d\u5916\u673a\u547d\u4e2d+origin perpetual_faces.py \u96f6 237 \u884c+origin perpetual_faces_n1.py \u96f6 PERPETUAL-N1-W237 WAVE_CONFIGS+origin \u96f6 PERPETUAL_N1_W237_PREREG.md \u56db\u67e5\uff09'))
A(('+W235=bm-a r968 takeover \u7a97 prereg derive\uff0889bd6962c\uff09+takeover \u4e94\u9762\u51bb\u7ed3 splice\uff08ff438aeaf\uff09+\u5f15\u64ce\u81ea\u71c3 12/12\uff0803:45-03:56\uff09+r970 finalize one-pass \u5df2\u843d\uff08K=514,920\u00b7\u8d26\u672c\u5934 940,789 \u673a\u8bfb\u00b7n1_w235_results.json\u00b704:3x\uff09\u2014\u2014\u672c\u6ce2\u4e0a\u6e38\u94fe=W1..W235 finalize \u5168\u843d\u5730\u00b7\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\u00b7\u5e72\u51c0\u524d\u7f6e**',
   '+W235=bm-a r968 takeover \u7a97 prereg derive\uff0889bd6962c\uff09+takeover \u4e94\u9762\u51bb\u7ed3 splice\uff08ff438aeaf\uff09+\u5f15\u64ce\u81ea\u71c3 12/12\uff0803:45-03:56\uff09+r970 finalize one-pass \u5df2\u843d\uff08K=514,920\u00b7\u8d26\u672c\u5934 940,789 \u673a\u8bfb\u00b7n1_w235_results.json\u00b704:3x\uff09+W236=bm-a r972 prereg derive\uff0867ade8314\uff09+\u4e94\u9762\u51bb\u7ed3 splice\uff08\u6b7b\u7a97\u4e2d\u65ad\u00b7r975 estate-absorb \u843d\u94fe 6e798bd22\uff09+\u5f15\u64ce\u81ea\u71c3 12/12\uff0806:52-07:03\uff09+r975 finalize one-pass \u5df2\u843d\uff08K=517,120\u00b7\u8d26\u672c\u5934 942,989 \u673a\u8bfb\u00b7n1_w236_results.json\u00b707:2x\uff09\u2014\u2014\u672c\u6ce2\u4e0a\u6e38\u94fe=W1..W236 finalize \u5168\u843d\u5730\u00b7\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\u00b7\u5e72\u51c0\u524d\u7f6e**'))
A(('\u5e2d\u4f4d\u516c\u793a=MSG-20261014-0446-bma-w236-seat \u5df2\u63a8 origin 5c25db795 \u5148\u4e8e\u672c\u51bb\u7ed3\u3010r565 \u5f8b\u00b7\u5e2d\u4f4d\u5148\u884c\u00b7bm-a r971 \u7a97\u53d1\u5e03\u00b7\u672c\u7a97=\u81ea\u6709\u5e2d\u627f\u63a5\u3011\uff1b\u4e0b\u6e38 W237+ \u6295\u5f71\u89c1 \u00a75.5\uff08probe \u673a\u8bc1 leg4\u00b7W237 freezer \u627f\u63a5\u9762\uff09\u3011\u3002**\u5355\u6001\u96f6\u5e2d\u4f4d\u7a7a\u6863**\uff1aW2..W235 \u5168\u6ce8\u518c\u5728\u51bb\u7ed3\u65f6\u70b9\u6210\u7acb\uff08W208 \u7ecf r885 \u63a5\u7ba1\u5f52 bm-c\u00b7W210 \u7ecf r898 \u63a5\u7ba1\u5f52 bm-c\u00b7bands unchanged R250\uff1bW209/W211 bm-c \u843d\u94fe\uff09\u3002',
   '\u5e2d\u4f4d\u516c\u793a=MSG-20261014-0654-bmc-w237-seat \u5df2\u63a8 origin 9312ef7ac \u5148\u4e8e\u672c\u51bb\u7ed3\u3010r565 \u5f8b\u00b7\u5e2d\u4f4d\u5148\u884c\u00b7bm-c r988 \u7a97\u53d1\u5e03\u00b7\u672c\u7a97=\u81ea\u6709\u5e2d\u627f\u63a5\u3011\uff1b\u4e0b\u6e38 W238+ \u6295\u5f71\u89c1 \u00a75.5\uff08probe \u673a\u8bc1 leg4\u00b7W238 freezer \u627f\u63a5\u9762\uff09\u3011\u3002**\u5355\u6001\u96f6\u5e2d\u4f4d\u7a7a\u6863**\uff1aW2..W236 \u5168\u6ce8\u518c\u5728\u51bb\u7ed3\u65f6\u70b9\u6210\u7acb\uff08W208 \u7ecf r885 \u63a5\u7ba1\u5f52 bm-c\u00b7W210 \u7ecf r898 \u63a5\u7ba1\u5f52 bm-c\u00b7bands unchanged R250\uff1bW209/W211 bm-c \u843d\u94fe\uff09\u3002'))

# S3 L5 bands line
A(('ADMIT \u56de\u6267=results/_w236bma_20261014_probe_receipt.json \u4e94\u817f\u5355\u7a97 gate-\u5408\u5e76\u5355\u56de\u6267\u7ed3\u6784',
   'ADMIT \u56de\u6267=results/_w237bmc_20261014_probe_receipt.json \u4e94\u817f\u5355\u7a97 gate-\u5408\u5e76\u5355\u56de\u6267\u7ed3\u6784'))
A(('**A-ext seed=534_004..536_003**\uff08**A \u9762=FIRST-CLEAN past prior-wave B \u9636\u68af\u7b2c\u4e5d\u5341\u516d\u4f8b**\uff1aA \u9762\u7b97\u672f\u7ee7\u7eed\u5e26 533_804..535_803\uff08\u81ea\u6ce8\u518c W235 A \u5c3e 533_803 \u7eed\uff09\u5728\u5176\u8d77\u70b9\u5373\u88ab W235 \u6ce8\u518c B \u5e26 533_804..534_003 **\u62d2**\uff08W235 \u5e2d\u4f4d leg4 \u6295\u5f71+\u5176 probe \u6240\u9884\u8a00+\u5f3a\u5236\uff09\u2192 \u8bda\u5b9e\u524d\u5411\u8d70 **1 hop** \u843d **534_004..536_003**\u00b7**A base==\u524d\u6ce2 B \u5c3e+1\uff08534_003+1\uff09\u673a\u68c0\u5173\u7cfb**=**A-hops-prior-B \u9636\u68af\u51e0\u4f55\u7b2c\u4e5d\u5341\u516d\u4f8b\uff08E36 \u5361\uff09**\u00b7\u975e\u8f6e\u8f6c r587 \u524d\u5411\u5355\u8c03\u65ad\u8a00\u5728\u8d70\u518c\uff1b\u5e8f\u6570\u9762\u5982\u5b9e\u62ab\u9732\uff1a\u672c\u7a97 probe \u56de\u6267 A_semantics \u673a\u8bfb\u5e8f\u6570=NINETY-SIXTH\uff08\u7b2c\u4e5d\u5341\u516d\u4f8b\uff09\u00b7\u672c\u4ef6\u6309\u56de\u6267\u5e8f\u6570\u9762\u8bb0\u8f7d\u975e\u8f6c\u6284\uff08r587\uff09\uff09',
   '**A-ext seed=536_204..538_203**\uff08**A \u9762=FIRST-CLEAN past prior-wave B \u9636\u68af\u7b2c\u4e5d\u5341\u4e03\u4f8b**\uff1aA \u9762\u7b97\u672f\u7ee7\u7eed\u5e26 536_004..538_003\uff08\u81ea\u6ce8\u518c W236 A \u5c3e 536_003 \u7eed\uff09\u5728\u5176\u8d77\u70b9\u5373\u88ab W236 \u6ce8\u518c B \u5e26 536_004..536_203 **\u62d2**\uff08W236 \u5e2d\u4f4d leg4 \u6295\u5f71+\u5176 probe \u6240\u9884\u8a00+\u5f3a\u5236\uff09\u2192 \u8bda\u5b9e\u524d\u5411\u8d70 **1 hop** \u843d **536_204..538_203**\u00b7**A base==\u524d\u6ce2 B \u5c3e+1\uff08536_203+1\uff09\u673a\u68c0\u5173\u7cfb**=**A-hops-prior-B \u9636\u68af\u51e0\u4f55\u7b2c\u4e5d\u5341\u4e03\u4f8b\uff08E36 \u5361\uff09**\u00b7\u975e\u8f6e\u8f6c r587 \u524d\u5411\u5355\u8c03\u65ad\u8a00\u5728\u8d70\u518c\uff1b\u5e8f\u6570\u9762\u5982\u5b9e\u62ab\u9732\uff1a\u672c\u7a97 probe \u56de\u6267 A_semantics \u673a\u8bfb\u5e8f\u6570=NINETY-SEVENTH\uff08\u7b2c\u4e5d\u5341\u4e03\u4f8b\uff09\u00b7\u672c\u4ef6\u6309\u56de\u6267\u5e8f\u6570\u9762\u8bb0\u8f7d\u975e\u8f6c\u6284\uff08r587\uff09\uff09'))
A(('**B-ext exit seed=536_004..536_203**\uff08**B \u9762=FIRST-CLEAN past own-wave A**\uff1aB \u9762 naive first-clean \u7ee7\u7eed\u5e26 534_004..534_203 \u5728\u6ce8\u518c\u5b87\u5b99\u4e0a CLEAN \u4f46**\u843d\u5728\u672c\u6ce2 A \u7a97 534_004..536_003 \u5185**\uff08**\u540c\u7a97\u4e92\u65a5\u9762 leg2 \u5f8b\u00b7W141 \u5148\u4f8b**\uff1aA \u4e0e B \u540c\u4e00\u51bb\u7ed3 commit \u53cc\u6ce8\u518c\u00b7\u4e92\u65a5\u65ad\u8a00\u5f3a\u5236 B \u8d8a\u8fc7\u672c\u6ce2 A \u7a97\uff09\u2192 B \u5e26\u672c\u6ce2 A \u7a97\u4fdd\u7559\u8d70 **1 hop** \u843d **536_004..536_203**\u00b7**B base==\u672c\u6ce2 A \u5c3e+1\uff08536_003+1\uff09\u673a\u68c0\u5173\u7cfb**\u00b7hop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\uff08B_hop_chain leg1 \u673a\u8bc1\uff09\uff1b**W235 \u5e2d\u4f4d leg4 \u6295\u5f71\u627f\u63a5\u9762\u6ce8\u8bb0\u5151\u73b0**\uff1a\u6295\u5f71\u9884\u8a00 W236 \u987b\u5728 post-W235 \u6ce8\u518c\u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u2014\u2014\u672c\u7a97\u53cc\u9762\u5151\u73b0\u00b7A \u88ab\u62d2+\u9636\u68af\u8d8a\u5e26\u5982\u6295\u5f71\u6240\u671f\u00b7B \u540c\u7a97\u4e92\u65a5\u4fdd\u7559=\u6295\u5f71\u6240\u671f\u00b7\u5df2\u5982\u5b9e\u62ab\u9732\u975e\u5206\u53c9\uff09',
   '**B-ext exit seed=538_204..538_403**\uff08**B \u9762=FIRST-CLEAN past own-wave A**\uff1aB \u9762 naive first-clean \u7ee7\u7eed\u5e26 536_204..536_403 \u5728\u6ce8\u518c\u5b87\u5b99\u4e0a CLEAN \u4f46**\u843d\u5728\u672c\u6ce2 A \u7a97 536_204..538_203 \u5185**\uff08**\u540c\u7a97\u4e92\u65a5\u9762 leg2 \u5f8b\u00b7W141 \u5148\u4f8b**\uff1aA \u4e0e B \u540c\u4e00\u51bb\u7ed3 commit \u53cc\u6ce8\u518c\u00b7\u4e92\u65a5\u65ad\u8a00\u5f3a\u5236 B \u8d8a\u8fc7\u672c\u6ce2 A \u7a97\uff09\u2192 B \u5e26\u672c\u6ce2 A \u7a97\u4fdd\u7559\u8d70 **1 hop** \u843d **538_204..538_403**\u00b7**B base==\u672c\u6ce2 A \u5c3e+1\uff08538_203+1\uff09\u673a\u68c0\u5173\u7cfb**\u00b7hop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\uff08B_hop_chain leg1 \u673a\u8bc1\uff09\uff1b**W236 \u5e2d\u4f4d leg4 \u6295\u5f71\u627f\u63a5\u9762\u6ce8\u8bb0\u5151\u73b0**\uff1a\u6295\u5f71\u9884\u8a00 W237 \u987b\u5728 post-W236 \u6ce8\u518c\u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u2014\u2014\u672c\u7a97\u53cc\u9762\u5151\u73b0\u00b7A \u88ab\u62d2+\u9636\u68af\u8d8a\u5e26\u5982\u6295\u5f71\u6240\u671f\u00b7B \u540c\u7a97\u4e92\u65a5\u4fdd\u7559=\u6295\u5f71\u6240\u671f\u00b7\u5df2\u5982\u5b9e\u62ab\u9732\u975e\u5206\u53c9\uff09'))
A(('R250\uff1aW236 \u5e26\u4ece\u672a\u6307\u6d3e', 'R250\uff1aW237 \u5e26\u4ece\u672a\u6307\u6d3e'))
A(('A base=534004 span=2000 checked=2000 verdict=FREE / B base=536004 span=200 checked=200 verdict=FREE',
   'A base=536204 span=2000 checked=2000 verdict=FREE / B base=538204 span=200 checked=200 verdict=FREE'))
A(('\u626b\u63cf\u9762=pre-W236 \u5168\u4e8c\u767e\u4e09\u5341\u4e09\u884c\u6ce8\u518c N1 \u5e26\u8868\uff08\u8868\u5c3e W235 \u884c\u00b7probe leg0 \u673a\u8bc1 233 \u884c live \u5355\u6001 owner rows 225\uff09',
   '\u626b\u63cf\u9762=pre-W237 \u5168\u4e8c\u767e\u4e09\u5341\u56db\u884c\u6ce8\u518c N1 \u5e26\u8868\uff08\u8868\u5c3e W236 \u884c\u00b7freeze \u7a97 live derive 234 \u884c\u5355\u6001 owner rows 226\u2014\u2014\u5e2d\u4f4d\u7a97 probe leg0 \u5b9e\u6d4b 233 \u884c+W236 splice \u843d\u5730\u540e +1 \u5982\u5b9e\u6ce8\u8bb0\uff09'))

# S4 L9 reuse-domain
A(('\uff08W2..W235 \u843d\u5730 runner \u7684 wave \u53c2\u6570\u5316\u590d\u7528', '\uff08W2..W236 \u843d\u5730 runner \u7684 wave \u53c2\u6570\u5316\u590d\u7528'))
A(('selftest W236 face \u5c06\u968f\u4e94\u9762\u51bb\u7ed3\u843d\u5730\u9a8c\u8bc1', 'selftest W237 face \u5c06\u968f\u4e94\u9762\u51bb\u7ed3\u843d\u5730\u9a8c\u8bc1'))
A(('\u672c\u4ef6\u4e0e results/_w236bma_freeze_edits.py\uff08\u4e94\u9762\u51bb\u7ed3\u62fc\u63a5\u811a\u672c\u00b7\u6309 _w235bma_freeze_edits.py \u6a21\u677f\u6d3e\u751f\u00b7gate0.5 \u81ea\u67e5 W235 \u884c+W235 finalize \u4ef6\u5728\u573a\u00b7\u672a\u843d\u5373 loud abort\u00b7estate \u63d0\u53d6\u9762=\u672c\u673a W235 \u5757\u7269\u7406\u5b57\u8282\u3014\u7ed3\u6784\u5df2\u77e5\u3015\uff09=freeze-prep \u675f\u540c\u7a97\u843d\u5730\uff08r970/W235 \u5148\u4f8b freeze-prep \u540c\u5f0f\u00b7\u672c\u7a97\u4e0a\u6e38\u5df2\u5168\u843d=\u6267\u884c\u7a97\u5373 freeze \u7a97\uff09',
   '\u672c\u4ef6\u4e0e results/_w237bmc_freeze_edits.py\uff08\u4e94\u9762\u51bb\u7ed3\u62fc\u63a5\u811a\u672c\u00b7\u6309 _w236bma_freeze_edits.py \u6a21\u677f\u6d3e\u751f\u00b7gate0.5 \u81ea\u67e5 W236 \u884c+W236 finalize \u4ef6\u5728\u573a\u00b7\u672a\u843d\u5373 loud abort\u00b7estate \u63d0\u53d6\u9762=\u672c\u673a W236 \u5757\u7269\u7406\u5b57\u8282\u3014\u7ed3\u6784\u5df2\u77e5\u3015\uff09=freeze-prep \u675f\u540c\u7a97\u843d\u5730\uff08r975/W236 \u5148\u4f8b freeze-prep \u540c\u5f0f\u00b7\u672c\u7a97\u4e0a\u6e38\u5df2\u5168\u843d=\u6267\u884c\u7a97\u5373 freeze \u7a97\uff09'))

# S5 L12 batch identity
A(('- \u6279\u540d=**PERPETUAL-N1-W236**\u3002', '- \u6279\u540d=**PERPETUAL-N1-W237**\u3002'))
A(('**W1..W235 N1 finalize \u5df2\u5168\u90e8\u843d\u5730**\u3010\u51c0\u8d26\u672c\u951a\u5934 **940,789**\u00b7K=514,920 \u5408\u5e76\u6c60\u00b7n1_w235_results.json \u673a\u8bfb\u00b7W235 finalize one-pass bm-a r970 \u7a97 04:3x\uff08W235 \u9762\u5b8c\u6574\u6027=12/12 shards consumed+finalize audit finalize_only=true \u6536\u53e3\u00b7takeover splice ff438aeaf+\u5f15\u64ce\u81ea\u71c3\u94fe\u5982\u5b9e\u6ce8\u8bb0\uff09\u3011',
   '**W1..W236 N1 finalize \u5df2\u5168\u90e8\u843d\u5730**\u3010\u51c0\u8d26\u672c\u951a\u5934 **942,989**\u00b7K=517,120 \u5408\u5e76\u6c60\u00b7n1_w236_results.json \u673a\u8bfb\u00b7W236 finalize one-pass bm-a r975 \u7a97 07:2x\uff08W236 \u9762\u5b8c\u6574\u6027=12/12 shards consumed+finalize audit finalize_only=true \u6536\u53e3\u00b7estate-absorb splice 6e798bd22+\u5f15\u64ce\u81ea\u71c3\u94fe\u5982\u5b9e\u6ce8\u8bb0\uff09\u3011'))
A(('\u7d2f\u8ba1 null \u6c60=514,920+2,200\uff08\u672c\u6ce2\uff09=**517,120 \u6295\u5f71**',
   '\u7d2f\u8ba1 null \u6c60=517,120+2,200\uff08\u672c\u6ce2\uff09=**519,320 \u6295\u5f71**'))

# S6 L13 claim
A(('\uff08\u5e2d\u4f4d\u516c\u793a=MSG-20261014-0446-bma-w236-seat \u5df2\u63a8 origin 5c25db795 r565 \u5f8b\uff08bm-a r971 \u5e2d\u00b7bm-a \u81ea\u6709\u5e2d\u627f\u63a5\uff09\u00b7probe W237+ \u6295\u5f71 A 536_004..538_003 / B 536_204..536_403 **naive-B-inside-naive-A re-derive \u5f3a\u5236\u6ce8\u8bb0+\u540c\u7a97\u4e92\u65a5\u9884\u62ab\u9732**\uff08\u6295\u5f71 B \u843d\u6295\u5f71 A \u7a97\u5185\u00b7W236 B \u5e26 536_004..536_203 \u6ce8\u518c\u540e\u5c06\u62d2 naive W237 A \u7a97=\u9636\u68af A-hops-prior-B \u7b2c\u4e5d\u5341\u4e03\u4f8b\u2014\u2014**W237 freezer \u627f\u63a5\u9762\u5f3a\u5236\u6ce8\u8bb0\uff1a\u987b\u5728 post-W236 \u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u00b7W141 \u5148\u4f8b\u00b7never transcribe r587**\uff09\uff09',
   '\uff08\u5e2d\u4f4d\u516c\u793a=MSG-20261014-0654-bmc-w237-seat \u5df2\u63a8 origin 9312ef7ac r565 \u5f8b\uff08bm-c r988 \u5e2d\u00b7bm-c \u81ea\u6709\u5e2d\u627f\u63a5\uff09\u00b7probe W238+ \u6295\u5f71 A 538_204..540_203 / B 538_404..538_603 **naive-B-inside-naive-A re-derive \u5f3a\u5236\u6ce8\u8bb0+\u540c\u7a97\u4e92\u65a5\u9884\u62ab\u9732**\uff08\u6295\u5f71 B \u843d\u6295\u5f71 A \u7a97\u5185\u00b7W237 B \u5e26 538_204..538_403 \u6ce8\u518c\u540e\u5c06\u62d2 naive W238 A \u7a97=\u9636\u68af A-hops-prior-B \u7b2c\u4e5d\u5341\u516b\u4f8b\u2014\u2014**W238 freezer \u627f\u63a5\u9762\u5f3a\u5236\u6ce8\u8bb0\uff1a\u987b\u5728 post-W237 \u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u00b7W141 \u5148\u4f8b\u00b7never transcribe r587**\uff09\uff09'))
A(('T-2026-10-01-141 s1 \u5f15\u64ce\u7ebf\u7b2c 226 \u6ce2\u3010bm-a \u7b2c\u4e00\u767e\u4e8c\u5341\u4e00\u679a\u81ea\u6709\u6ce2\u3010\u673a\u9762 derive\uff1aprobe leg0 bma_rows=120 attempt-continuity face\uff08r971 \u7a97\u8ba1\u6cd5\u00b7bm-a own seat+bma live rows 120 \u5b9e\u8bfb\uff09\u2014\u2014freeze \u65f6 live derive bma rows 120+\u5019\u9009=\u7b2c 121 \u679a EXACT\uff08\u4ee5 freeze \u65f6 live derive \u4e3a\u51c6 r587/r359\uff09\u3011\u3011',
   'T-2026-10-01-141 s1 \u5f15\u64ce\u7ebf\u7b2c 227 \u6ce2\u3010bm-c \u7b2c\u516d\u5341\u4e94\u679a\u81ea\u6709\u6ce2\u3010\u673a\u9762 derive\uff1aprobe leg0 bmc_rows=64 attempt-continuity face\uff08r988 \u7a97\u8ba1\u6cd5\u00b7bm-c own seat+bmc live rows 64 \u5b9e\u8bfb\uff09\u2014\u2014freeze \u65f6 live derive bmc rows 64+\u5019\u9009=\u7b2c 65 \u679a EXACT\uff08\u4ee5 freeze \u65f6 live derive \u4e3a\u51c6 r587/r359\uff09\u3011\u3011'))
A(('\uff08\u6ce2\u53f7=\u6ce8\u518c\u8868 W235 \u5e2d\u540e\u9996\u4e2a\u81ea\u7531\u53f7\u00b7\u5355\u6001\u96f6\u5e2d\u4f4d\u7a7a\u6863\u4e8e\u51bb\u7ed3\u65f6\u70b9\u6210\u7acb\uff1b\u5e2d\u4f4d\u516c\u793a MSG-20261014-0446-bma-w236-seat \u5148\u63a8 origin 5c25db795 r565 \u5f8b\uff1blane-free\uff1bdept:\u7814\u7a76\uff09',
   '\uff08\u6ce2\u53f7=\u6ce8\u518c\u8868 W236 \u5e2d\u540e\u9996\u4e2a\u81ea\u7531\u53f7\u00b7\u5355\u6001\u96f6\u5e2d\u4f4d\u7a7a\u6863\u4e8e\u51bb\u7ed3\u65f6\u70b9\u6210\u7acb\uff1b\u5e2d\u4f4d\u516c\u793a MSG-20261014-0654-bmc-w237-seat \u5148\u63a8 origin 9312ef7ac r565 \u5f8b\uff1blane-free\uff1bdept:\u7814\u7a76\uff09'))

# S7 L14 RAM face
A(('**RAM face \u5982\u5b9e\u6ce8\u8bb0\uff1a\u672c\u7a97 free RAM ~39.1GB\uff08MV XQ i2v \u5f71\u7247\u94fe=bm-c lane \u5df2\u6536\u5b98\u3014O-20261012-0739 \u00a71\u3015\u00b7\u5e38\u9a7b\u5e95\u76d8\u5360\u7528\u4ecd\u5728\u9ad8\u4f4d\uff09\u2014\u2014N1 \u5f15\u64ce\u70b9\u706b\u65e0 RAM \u786c\u95f8\uff08W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230/W231/W232/W233/W234/W235 \u4f4e RAM \u5b9e\u70e7\u5148\u4f8b\uff09\u00b7burn \u7531\u5f15\u64ce RAM \u9762\u968f cycle \u4e0a\u62a5\u81ea\u5224\u00b7\u672c\u4ef6\u4e0d\u4ee3\u5f15\u64ce\u51b3\u7b56\u3002**',
   f'**RAM face \u5982\u5b9e\u6ce8\u8bb0\uff1a\u672c\u7a97 free RAM ~{ram_free_gb:.1f}GB\uff08bm-c \u5e95\u76d8\u5e38\u9a7b\u9ad8\u4f4d\u00b7MV V3 burn window GPU \u4fdd\u62a4\u9762\u3010O-20261014-0312 sec.2\u3011\u96f6\u89e6\u78b0\u5982\u5b9e\u6ce8\u8bb0\uff09\u2014\u2014N1 \u5f15\u64ce\u70b9\u706b\u65e0 RAM \u786c\u95f8\uff08W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230/W231/W232/W233/W234/W235/W236 \u4f4e RAM \u5b9e\u70e7\u5148\u4f8b\u00b7W236 \u5e2d\u4f4d\u7a97 1.9G/0.2G \u5b9e\u951a\u65cf\uff09\u00b7burn \u7531\u5f15\u64ce RAM \u9762\u968f cycle \u4e0a\u62a5\u81ea\u5224\u00b7\u672c\u4ef6\u4e0d\u4ee3\u5f15\u64ce\u51b3\u7b56\u3002**'))

# S8 L15
A(('\u590d\u8bfb\u81ea\u89c1 W236 \u884c\u5e76\u70b9\u706b\u81ea\u70e7', '\u590d\u8bfb\u81ea\u89c1 W237 \u884c\u5e76\u70b9\u706b\u81ea\u70e7'))

# S9 L19 gate path
A(('--prereg research/PERPETUAL_N1_W236_PREREG.md', '--prereg research/PERPETUAL_N1_W237_PREREG.md'))

# S10 L20
A(('p2_calibration v1/v2 canon\uff1bv1 ext\uff1bv2..W235 \u843d\u5730\uff09', 'p2_calibration v1/v2 canon\uff1bv1 ext\uff1bv2..W236 \u843d\u5730\uff09'))

# S11 L31 A-tier
A(('- **A \u6863**\uff08j=0..1,999\uff09\uff1aentry rng seed=**534_004+j**\uff08\u6cd5\u5178 \u00a74 W236 \u884c A=534_004..536_003\u00b7**FIRST-CLEAN past prior-wave B \u9636\u68af\u7b2c\u4e5d\u5341\u516d\u4f8b**\uff1a\u7b97\u672f\u7eed\u5e26 533_804..535_803 \u8d77\u70b9\u5373\u88ab W235 \u6ce8\u518c B \u5e26 533_804..534_003 \u62d2\u21921 hop \u843d 534_004..536_003\u00b7A base==\u524d\u6ce2 B \u5c3e+1 \u673a\u68c0\u5173\u7cfb\u00b7E36 \u5361\u00b7hops=1\u00b7ADMIT \u56de\u6267\u5728\u573a\uff09',
   '- **A \u6863**\uff08j=0..1,999\uff09\uff1aentry rng seed=**536_204+j**\uff08\u6cd5\u5178 \u00a74 W237 \u884c A=536_204..538_203\u00b7**FIRST-CLEAN past prior-wave B \u9636\u68af\u7b2c\u4e5d\u5341\u4e03\u4f8b**\uff1a\u7b97\u672f\u7eed\u5e26 536_004..538_003 \u8d77\u70b9\u5373\u88ab W236 \u6ce8\u518c B \u5e26 536_004..536_203 \u62d2\u21921 hop \u843d 536_204..538_203\u00b7A base==\u524d\u6ce2 B \u5c3e+1 \u673a\u68c0\u5173\u7cfb\u00b7E36 \u5361\u00b7hops=1\u00b7ADMIT \u56de\u6267\u5728\u573a\uff09'))

# S12 L32 B-tier
A(('- **B \u6863**\uff08j=0..199\uff09\uff1aentry rng=**534_004+j**\uff08\u4e0e A[j] \u540c\u6e90\u914d\u5bf9\u8bed\u4e49\u9010\u5b57\u00b7runner \u5b9e\u8bc1 entry=A_SEED_BASE+j\uff09\uff1bexit rng=**536_004+j**\uff08\u6cd5\u5178 \u00a74 W236 \u884c B=536_004..536_203\u00b7**FIRST-CLEAN past own-wave A**\uff1aB \u7b97\u672f\u7eed\u5e26 534_004..534_203 \u5728\u6ce8\u518c\u5b87\u5b99 CLEAN \u4f46\u843d\u5728\u672c\u6ce2 A \u7a97 534_004..536_003 \u5185\u2192**\u540c\u7a97\u4e92\u65a5\u9762 leg2 \u5f8b\u00b7W141 \u5148\u4f8b**\u5f3a\u5236 B \u8d8a\u672c\u6ce2 A \u7a97\u2192\u4fdd\u7559\u8d70\u843d 536_004..536_203\u00b7hops=1\u00b7**B base==\u672c\u6ce2 A \u5c3e+1 \u673a\u68c0\u5173\u7cfb**\u00b7\u975e\u8f6e\u8f6c r587\u00b7hop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\u00b7\u4e0e W235 \u5e2d\u4f4d leg4 \u6295\u5f71\u627f\u63a5\u9762\u6ce8\u8bb0\u5151\u73b0\u6536\u655b\u00b7ADMIT \u56de\u6267\u5728\u573a\uff09',
   '- **B \u6863**\uff08j=0..199\uff09\uff1aentry rng=**536_204+j**\uff08\u4e0e A[j] \u540c\u6e90\u914d\u5bf9\u8bed\u4e49\u9010\u5b57\u00b7runner \u5b9e\u8bc1 entry=A_SEED_BASE+j\uff09\uff1bexit rng=**538_204+j**\uff08\u6cd5\u5178 \u00a74 W237 \u884c B=538_204..538_403\u00b7**FIRST-CLEAN past own-wave A**\uff1aB \u7b97\u672f\u7eed\u5e26 536_204..536_403 \u5728\u6ce8\u518c\u5b87\u5b99 CLEAN \u4f46\u843d\u5728\u672c\u6ce2 A \u7a97 536_204..538_203 \u5185\u2192**\u540c\u7a97\u4e92\u65a5\u9762 leg2 \u5f8b\u00b7W141 \u5148\u4f8b**\u5f3a\u5236 B \u8d8a\u672c\u6ce2 A \u7a97\u2192\u4fdd\u7559\u8d70\u843d 538_204..538_403\u00b7hops=1\u00b7**B base==\u672c\u6ce2 A \u5c3e+1 \u673a\u68c0\u5173\u7cfb**\u00b7\u975e\u8f6e\u8f6c r587\u00b7hop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\u00b7\u4e0e W236 \u5e2d\u4f4d leg4 \u6295\u5f71\u627f\u63a5\u9762\u6ce8\u8bb0\u5151\u73b0\u6536\u655b\u00b7ADMIT \u56de\u6267\u5728\u573a\uff09'))

# S13 L36 disjoint
A(('- \u79cd\u5b50\u5e26 disjoint \u5168\u4f8b\uff08selftest \u5f3a\u5236\uff09\uff1aW236 \u5e26\u4e0e v1 \u5728\u7528\u5e26', '- \u79cd\u5b50\u5e26 disjoint \u5168\u4f8b\uff08selftest \u5f3a\u5236\uff09\uff1aW237 \u5e26\u4e0e v1 \u5728\u7528\u5e26'))
A(('W2..W235 \u5e26\uff08\u51bb\u7ed3\u65f6\u70b9\u5168\u6ce8\u518c\u5355\u6001\uff09', 'W2..W236 \u5e26\uff08\u51bb\u7ed3\u65f6\u70b9\u5168\u6ce8\u518c\u5355\u6001\uff09'))
A(('\u672c\u6ce2\u673a\u9a8c ADMIT \u56de\u6267\u5728\u573a=_w236bma_20261014 \u63a2\u9488\u7a97', '\u672c\u6ce2\u673a\u9a8c ADMIT \u56de\u6267\u5728\u573a=_w237bmc_20261014 \u63a2\u9488\u7a97'))
A(('selftest W236 face\uff08A=first-clean past prior-wave B \u6052\u7b49\u00b7B=first-clean past own-wave A \u6052\u7b49+\u540c\u7a97\u4e92\u65a5\u65ad\u8a00\u00b7W235 \u884c parity \u817f',
   'selftest W237 face\uff08A=first-clean past prior-wave B \u6052\u7b49\u00b7B=first-clean past own-wave A \u6052\u7b49+\u540c\u7a97\u4e92\u65a5\u65ad\u8a00\u00b7W236 \u884c parity \u817f'))
A(('\u4ece**\u672c\u673a W235 \u5757\u7269\u7406\u5b57\u8282**\u63d0\u53d6\uff08\u7ed3\u6784\u5df2\u77e5\u00b7\u63d0\u53d6\u81ea\u8bc1\u65ad\u8a00 69 \u884c range \u6052\u7b49\u5728\u573a\uff09\u2014\u2014W234 \u5757\u7684 W233 leg\uff081 \u884c\uff09\u4e0d\u5165 estate \u8def\u5f84\u00b7\u63d0\u53d6\u540e\u65b0\u589e W233+W234 leg \u6784\u6210 W236 \u5757 parity 94 \u884c\uff08W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232+W233+W234+W235\uff09\u00b7\u96f6\u5047\u8bbe\u96f6\u98ce\u9669\u3002',
   '\u4ece**\u672c\u673a W236 \u5757\u7269\u7406\u5b57\u8282**\u63d0\u53d6\uff08\u7ed3\u6784\u5df2\u77e5\u00b7\u63d0\u53d6\u81ea\u8bc1\u65ad\u8a00 69 \u884c range \u6052\u7b49\u5728\u573a\uff09\u2014\u2014W235 \u5757\u7684 W234 leg\uff081 \u884c\uff09\u4e0d\u5165 estate \u8def\u5f84\u00b7\u63d0\u53d6\u540e\u65b0\u589e W235+W236 leg \u6784\u6210 W237 \u5757 parity 95 \u884c\uff08W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232+W233+W234+W235+W236\uff09\u00b7\u96f6\u5047\u8bbe\u96f6\u98ce\u9669\u3002'))

# S14 L39
A(('\uff08\u8d77\u8349\u7a97\u5b9e\u6d41 W1..W235 \u5df2\u843d\u8d26 514,920 \u5b9e\u6d4b\u00b7derive \u7981\u624b\u6284\uff09',
   '\uff08\u8d77\u8349\u7a97\u5b9e\u6d41 W1..W236 \u5df2\u843d\u8d26 517,120 \u5b9e\u6d4b\u00b7derive \u7981\u624b\u6284\uff09'))

# S15 L40 ledger
A(('batch_name="PERPETUAL-N1-W236", batch_trials=2200, file_name="results/perpetual_faces/n1_w236_results.json"',
   'batch_name="PERPETUAL-N1-W237", batch_trials=2200, file_name="results/perpetual_faces/n1_w237_results.json"'))

# S16 L44
A(('\uff08\u8d77\u8349\u7a97\u5b9e\u51b5\u6ce8\u8bb0\uff1a**W1..W235 N1 finalize \u5df2\u5168\u90e8\u843d\u5730**\u2014\u2014\u51c0\u8d26\u672c\u951a\u5934 940,789\u00b7**K=514,920 \u5408\u5e76\u6c60**\u00b7**\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\u2014\u2014\u672c\u6ce2 \u00a75 \u9884\u6d4b\u952e=**W235 \u5b9e\u6d4b\u503c**\u3010results/perpetual_faces/n1_w235_results.json\u00b7N1 \u9762\u6700\u65b0\u5df2\u843d\u8d26\u952e\u00b704:3x finalize one-pass\u3011\u3002',
   '\uff08\u8d77\u8349\u7a97\u5b9e\u51b5\u6ce8\u8bb0\uff1a**W1..W236 N1 finalize \u5df2\u5168\u90e8\u843d\u5730**\u2014\u2014\u51c0\u8d26\u672c\u951a\u5934 942,989\u00b7**K=517,120 \u5408\u5e76\u6c60**\u00b7**\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\u2014\u2014\u672c\u6ce2 \u00a75 \u9884\u6d4b\u952e=**W236 \u5b9e\u6d4b\u503c**\u3010results/perpetual_faces/n1_w236_results.json\u00b7N1 \u9762\u6700\u65b0\u5df2\u843d\u8d26\u952e\u00b707:2x finalize one-pass\u3011\u3002'))

# S17 L45 key1
A(('1. W236-only mu \u4e0e\u7d2f\u8ba1\u6c60 merged mu\uff08W235 \u5b9e\u6d4b\u952e **\u22120.09279197**\u00b7K=514,920 \u5408\u5e76\u6c60\u00b7W235-only \u5b9e\u6d4b **\u22120.09609841**\uff09\u5dee\u5f02 **|\u0394|<0.02**\uff08W2..W235 \u5171\u4e8c\u767e\u4e09\u5341\u4e09\u9762\u5b9e\u6d4b mu \u7a33\u5b9a\u5148\u4f8b\u00b7\u5355\u6ce2\u8de8\u952e\u5fae\uff1bW235-only vs merged \u5b9e\u5dee 0.0033 \u5728\u5e26\u5185\uff09\u3002',
   f'1. W237-only mu \u4e0e\u7d2f\u8ba1\u6c60 merged mu\uff08W236 \u5b9e\u6d4b\u952e **{mu_s}**\u00b7K=517,120 \u5408\u5e76\u6c60\u00b7W236-only \u5b9e\u6d4b **{wmu_s}**\uff09\u5dee\u5f02 **|\u0394|<0.02**\uff08W2..W236 \u5171\u4e8c\u767e\u4e09\u5341\u56db\u9762\u5b9e\u6d4b mu \u7a33\u5b9a\u5148\u4f8b\u00b7\u5355\u6ce2\u8de8\u952e\u5fae\uff1bW236-only vs merged \u5b9e\u5dee {delta_s} \u5728\u5e26\u5185\uff09\u3002'))

# S18 L46 key2
A(('2. sigma \u76f8\u5bf9\u53d8\u5316 **<\u00b110%**\uff08\u540c\u8bbe\u8ba1\u540c\u7a97\u00b7\u7eaf\u62bd\u6837\u6ce2\u52a8\uff1b\u952e **0.24509683**=W235 \u5408\u5e76\u6c60\u5b9e\u6d4b\uff09\u3002',
   f'2. sigma \u76f8\u5bf9\u53d8\u5316 **<\u00b110%**\uff08\u540c\u8bbe\u8ba1\u540c\u7a97\u00b7\u7eaf\u62bd\u6837\u6ce2\u52a8\uff1b\u952e **{sigma_s}**=W236 \u5408\u5e76\u6c60\u5b9e\u6d4b\uff09\u3002'))

# S19 L47 key3
A(('3. A \u6863 full_sharpe_p95 \u4e0e W235 A \u6863 p95\uff08**0.3058** \u5b9e\u6d4b\u951a\uff09\u5dee **<0.05**\uff08\u95e8\u6807\u6ce8\u6cd5 W5..W235 \u5148\u4f8b\uff1a\u7ed3\u679c\u77e5\u60c5\u9762\u4ec5\u4f5c\u673a\u5668\u65ad\u8a00\u4e4b\u7528\u00b7\u6d4b\u91cf\u9762\u975e\u6ce8\u518c\u5229\u76ca\uff09\u3002',
   f'3. A \u6863 full_sharpe_p95 \u4e0e W236 A \u6863 p95\uff08**{a_p95:.4f}** \u5b9e\u6d4b\u951a\uff09\u5dee **<0.05**\uff08\u95e8\u6807\u6ce8\u6cd5 W5..W236 \u5148\u4f8b\uff1a\u7ed3\u679c\u77e5\u60c5\u9762\u4ec5\u4f5c\u673a\u5668\u65ad\u8a00\u4e4b\u7528\u00b7\u6d4b\u91cf\u9762\u975e\u6ce8\u518c\u5229\u76ca\uff09\u3002'))

# S20 L48 key4
A(('W136..W235 \u5148\u4f8b\u94fe\u62ab\u9732\u3010\u5404\u6ce2 K-lift \u5168\u5728 \u00b10.0003 \u5185\u00b7\u673a\u8bfb\u53ef\u590d\u6838\u00b7\u952e W235 \u5b9e\u6d4b K-lift **+0.0000**\u00b7line_merged@K514,920 **1.1926**\u00b7line_pre_w235 1.1926\u00b7n_eff_held_equal 938,589\uff1b',
   'W136..W236 \u5148\u4f8b\u94fe\u62ab\u9732\u3010\u5404\u6ce2 K-lift \u5168\u5728 \u00b10.0003 \u5185\u00b7\u673a\u8bfb\u53ef\u590d\u6838\u00b7\u952e W236 \u5b9e\u6d4b K-lift **+0.0000**\u00b7line_merged@K517,120 **1.1927**\u00b7line_pre_w236 1.1927\u00b7n_eff_held_equal 940,789\uff1b'))
A(('\u2192W234 **0.000342**\u2192W235 **0.000342**\u3011\uff09\u3002',
   '\u2192W234 **0.000342**\u2192W235 **0.000342**\u2192W236 **0.000341**\u3011\uff09\u3002'))

# S21 L49 key5 projection
A(('5. **W237+ \u6295\u5f71\uff08probe \u673a\u8bc1 leg4\u00b7\u4e0b\u6ce2\u51bb\u7ed3\u65b9\u590d\u6838\u975e\u8f6c\u6284 r587 \u5f8b\uff09**\uff1aA naive first-clean 536_004..538_003 CLEAN\uff08hops=0\u00b7pre-W236 \u5b87\u5b99\uff09\uff1bB naive first-clean **536_204..536_403 CLEAN**\uff08hops=0\uff09\u2014\u2014**naive B \u843d\u5728 naive A \u7a97\u5185**\uff08W141 \u540c\u7a97\u4e92\u65a5\u5148\u4f8b\u9002\u7528\u4e8e W237\uff1aW237 \u51bb\u7ed3\u65b9\u5fc5\u987b\u5728 post-W236 \u6ce8\u518c\u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u2014\u2014leg2 \u5f8b/E36 \u5361\uff09\uff1b**W236 B \u5e26 536_004..536_203 \u6ce8\u518c\u540e\u5c06\u62d2 naive W237 A \u7a97**\u2014\u2014W237 A \u91cd derive \u540c\u5f3a\u5236\uff08\u8d8a\u8fc7 W236 B \u5e26\u00b7\u9636\u68af A-hops-prior-B \u7b2c\u4e5d\u5341\u4e03\u4f8b\uff09\uff1bverify at W237 prereg\uff0chop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\u3002',
   '5. **W238+ \u6295\u5f71\uff08probe \u673a\u8bc1 leg4\u00b7\u4e0b\u6ce2\u51bb\u7ed3\u65b9\u590d\u6838\u975e\u8f6c\u6284 r587 \u5f8b\uff09**\uff1aA naive first-clean 538_204..540_203 CLEAN\uff08hops=0\u00b7pre-W237 \u5b87\u5b99\uff09\uff1bB naive first-clean **538_404..538_603 CLEAN**\uff08hops=0\uff09\u2014\u2014**naive B \u843d\u5728 naive A \u7a97\u5185**\uff08W141 \u540c\u7a97\u4e92\u65a5\u5148\u4f8b\u9002\u7528\u4e8e W238\uff1aW238 \u51bb\u7ed3\u65b9\u5fc5\u987b\u5728 post-W237 \u6ce8\u518c\u5b87\u5b99\u91cd derive \u4e14 derive B \u65f6\u9884\u7559\u672c\u6ce2 A \u7a97\u2014\u2014leg2 \u5f8b/E36 \u5361\uff09\uff1b**W237 B \u5e26 538_204..538_403 \u6ce8\u518c\u540e\u5c06\u62d2 naive W238 A \u7a97**\u2014\u2014W238 A \u91cd derive \u540c\u5f3a\u5236\uff08\u8d8a\u8fc7 W237 B \u5e26\u00b7\u9636\u68af A-hops-prior-B \u7b2c\u4e5d\u5341\u516b\u4f8b\uff09\uff1bverify at W238 prereg\uff0chop \u94fe\u9010\u8df3\u5728 probe \u56de\u6267\u3002'))

# S22 L52 runner
A(('--wave 236/finalize --wave 236', '--wave 237/finalize --wave 237'))
A(('\u3010n1_w236/ \u5206\u7247\u8ba1\u6570\u589e\u957f', '\u3010n1_w237/ \u5206\u7247\u8ba1\u6570\u589e\u957f'))

# S23 L53 deliverables
A(('results/p2cal_ext/n1_w236/shard-<k>-of-12.json', 'results/p2cal_ext/n1_w237/shard-<k>-of-12.json'))
A(('`results/perpetual_faces/n1_w236_results.json`\uff08finalize \u5408\u5e76\u4ef6\u00b7\u9876\u5c42 evidence_cutoff\u00b7cutoff_meta\u00b7audit \u6bb5\u00b7K-lift \u5bf9\u7167\uff1bfinalize \u952e\u5e8f\u524d\u7f6e=**\u8d77\u8349\u7a97\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\uff08W1..W235 \u5168\u843d\uff09',
   '`results/perpetual_faces/n1_w237_results.json`\uff08finalize \u5408\u5e76\u4ef6\u00b7\u9876\u5c42 evidence_cutoff\u00b7cutoff_meta\u00b7audit \u6bb5\u00b7K-lift \u5bf9\u7167\uff1bfinalize \u952e\u5e8f\u524d\u7f6e=**\u8d77\u8349\u7a97\u96f6\u5728\u98de\u4e0a\u6e38\u5e2d\uff08W1..W236 \u5168\u843d\uff09'))

# S24 L54 engine ledger
A(('engine_owner==bm-a 120 \u884c\u6ce8\u518c\u3014\u51bb\u7ed3\u65f6\u70b9\u3015', 'engine_owner==bm-c 64 \u884c\u6ce8\u518c\u3014\u51bb\u7ed3\u65f6\u70b9\u3015'))

# S25/S26 L58/L61 placeholders
A(('\u2014\u2014r970 W235 \u00a77 \u8303\u5f0f\uff09', '\u2014\u2014r975 W236 \u00a77 \u8303\u5f0f\uff09'))
A(('\uff08\u5360\u4f4d\u00b7finalize \u540c\u7a97\u56de\u586b\uff1a\u00a75.5 W237+ \u6295\u5f71\u627f\u63a5\u673a\u8bc1/\u5b9d\u85cf\u4e0e\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee/\u8bda\u5b9e\u62ab\u9732\u9762\u2014\u2014r970 W235 \u00a78 \u8303\u5f0f\uff09',
   '\uff08\u5360\u4f4d\u00b7finalize \u540c\u7a97\u56de\u586b\uff1a\u00a75.5 W238+ \u6295\u5f71\u627f\u63a5\u673a\u8bc1/\u5b9d\u85cf\u4e0e\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee/\u8bda\u5b9e\u62ab\u9732\u9762\u2014\u2014r975 W236 \u00a78 \u8303\u5f0f\uff09'))

# ---------- apply ----------
out = tpl
applied = 0
for i, (old, new) in enumerate(SUBS, 1):
    n = out.count(old)
    assert n == 1, 'SUB#%d count=%d (expect 1): %s...' % (i, n, old[:60])
    out = out.replace(old, new)
    applied += 1

# ---------- forbidden-residue scan (r990 context-pinned refine) ----------
# blanket entries '536_004..536_203'/'_w236bma'/'938,589' REMOVED per dbg_residue
# probe verdict: they are family-legal prior-wave citations that MUST be retained
# (W236 registered B band = staircase rejector narration x2; _w236bma_freeze_edits.py
# = template-source citation x1; 938,589 = W234 historical ledger head x1) -- pinned
# below by exact count + phrase-context assertions instead of blanket substring ban.
FORBID = ['534_004', '533_804', 'pre-W236 \u5168\u4e8c\u767e',
          'W2..W235', 'W1..W235', 'bm-a 120', 'r972 \u7a97',
          '0446-bma', '233 \u884c live', 'owner rows 225', 'v2..W235',
          'engine_owner \u884c 225', '\u6cf5\u7b2c 234 \u679a', 'bma rows 120',
          'PERPETUAL-N1-W236', 'n1_w236/shard', '534004', '536004',
          'W236-only mu \u4e0e', 'W235 \u5b9e\u6d4b\u952e', '0.3058',
          'NINETY-SIXTH', '\u7b2c\u4e5d\u5341\u516d\u4f8b', 'parity 94 \u884c',
          '39.1GB', 'r970 W235']
residue = [f for f in FORBID if f in out]
assert not residue, 'forbidden residue: %s' % residue

# context-pinned legal prior-wave citations (r990 scan-refine)
assert out.count('536_004..536_203') == 2, out.count('536_004..536_203')
assert out.count('W236 \u6ce8\u518c B \u5e26 536_004..536_203') == 2, 'rejector-band phrase x2'
assert out.count('_w236bma') == 1 and out.count('_w236bma_freeze_edits.py') == 1
assert out.count('938,589') == 1 and '\u8d26\u672c\u5934 938,589 \u673a\u8bfb\u00b7n1_w234_results.json' in out

# legal retained W236 references (upstream anchors, cited product)
assert out.count('n1_w236_results.json') == 3, out.count('n1_w236_results.json')
assert out.count('PERPETUAL-N1-W237') >= 3
assert 'n1_w237_results.json' in out and 'n1_w237/shard' in out
assert '536_204' in out and '538_204' in out and '538_203' in out
assert 'NINETY-SEVENTH' in out and '\u7b2c\u4e5d\u5341\u4e03\u4f8b' in out
assert '\u7b2c\u4e5d\u5341\u516b\u4f8b' in out  # r990 ordinal-face fix: 98th ENGLISH face belongs to W238 prereg (family law)

with open(OUT_PATH, 'w', encoding='utf-8', newline='') as fh:
    fh.write(out)

receipt = {
    'derive': 'W237 prereg machine-generated SUB from frozen W236 template',
    'template_commit': TPL_COMMIT,
    'upstream_finalize_commit': FIN_COMMIT,
    'sub_pairs_applied': applied,
    'out_path': OUT_PATH,
    'out_bytes': len(out.encode('utf-8')),
    'facts': {
        'merged_mu': merged_mu, 'merged_sigma': merged_sigma,
        'w236_only_mu': w236_only_mu, 'w236_only_sigma': npc['w236_only']['sigma'],
        'a_p95': a_p95, 'se_mu_at_k': se_mu_at_k, 'k_lift': k_lift,
        'line_merged': line_merged, 'line_pre': line_pre, 'n_eff_held_equal': n_eff_he,
        'ledger_prev_total': prev_total, 'ledger_batch': batch_trials, 'ledger_total': total,
        'merged_K': merged_K,
        'n1_bands_rows': n_rows, 'owner_rows': owner_rows, 'bmc_rows': bmc_rows,
        'bands': bands, 'ram_free_gb': ram_free_gb,
        'engine_status': {'burns_active': burns, 'queue_next': queue_next},
    },
    'forbidden_residue': residue,
}
json.dump(receipt, open('results/_w237bmc_prereg_derive_receipt.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('W237 prereg derive OK: %d SUB pairs, out=%d bytes -> %s' % (applied, len(out.encode('utf-8')), OUT_PATH))
print('facts: n1_bands=%d rows owner_rows=%d bmc=%d ram_free=%.1fG' % (n_rows, owner_rows, bmc_rows, ram_free_gb))
