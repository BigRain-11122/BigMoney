# -*- coding: utf-8 -*-
"""W245 prereg derive -- bm-a r1010 freeze window (freeze UNBLOCKED: W244 finalize
landed 5e24d1fdb r1008 07:47; seat MSG-20261015-0844-bma-w245-seat published by
the dead r1010 seat window @ origin 2b0947947 -- pushed to origin by THIS r1010
estate-absorption successor window; GM re-assignment takeover lane: bm-c
declared the W245 turn at its r1020 closeout 07:31 then stalled, heartbeat
frozen 64.5min, zero origin commits post the W244-finalize unblock -- takeover
per the r1009 next-pointer stall rule).

Machine-generated SUB from committed W244 frozen template (git 260ffd3f8),
zero transcription (r587 / r958 / r974 lineage; cloned mechanics from
_w244bma_prereg_derive.py + _w242 lineage). All anchor faces machine-read live
at derive time:
- results/perpetual_faces/n1_w244_results.json  (W244 finalize product, landed 07:47)
- results/_w245bma_20261015_probe_receipt.json  (bm-a r1010 seat probe ADMIT)
- Tools/saturation_engine.py n1_bands() live derive (242 rows, tail W244, owner rows 234)
Fail-closed: every SUB pair must hit exactly once; forbidden-residue scan must be zero.
B face semantic delta (live-seed refusal, hops=1): W245 B naive continuation
541_901..542_100 hits live-seed SEED_REGISTRY 542_000 -> honest forward walk
first-clean 542_001..542_200 (receipt leg1 B_semantics governs).
"""
import json
import subprocess
import sys
import importlib.util
from collections import Counter

OUT_PATH = 'research/PERPETUAL_N1_W245_PREREG.md'


def git_show(ref, path):
    r = subprocess.run(['git', 'show', '%s:%s' % (ref, path)], capture_output=True)
    assert r.returncode == 0, 'git show failed: %s' % r.stderr[:300]
    return r.stdout.decode('utf-8')


def pickaxe_add(path):
    r = subprocess.run(['git', 'log', '--diff-filter=A', '--format=%H', '--', path],
                       capture_output=True)
    lines = r.stdout.decode('utf-8').strip().splitlines()
    assert lines, 'pickaxe add-commit empty for %s' % path
    return lines[0]


TPL_COMMIT = pickaxe_add('research/PERPETUAL_N1_W244_PREREG.md')
FIN_COMMIT = pickaxe_add('results/perpetual_faces/n1_w244_results.json')

# ---------- facts (live machine-read, zero transcription) ----------
fin = json.load(open('results/perpetual_faces/n1_w244_results.json', encoding='utf-8-sig'))
probe = json.load(open('results/_w245bma_20261015_probe_receipt.json', encoding='utf-8-sig'))

npc = fin['null_pool_cumulative']
merged_mu = npc['merged']['mu']
merged_sigma = npc['merged']['sigma']
w244_only_mu = npc['w244_only']['mu']
a_p95 = fin['families']['A_random_engine_exit']['full_sharpe_p95']
se_mu_at_k = npc['se_mu_at_k534720']
k_lift = fin['skill_line_v2_k_lift']['line_delta_k_lift']
line_merged = fin['skill_line_v2_k_lift']['line_merged_534720']
line_pre = fin['skill_line_v2_k_lift']['line_pre_w244']
n_eff_he = fin['skill_line_v2_k_lift']['n_eff_held_equal']
led = fin['science_gates']['ledger']
prev_total, batch_trials, total = led['prev_total'], led['batch_trials'], led['total']
merged_K = npc['merged']['n_values']

# sanity: five-key anchors must equal the landed W244 finalize numbers
assert (prev_total, batch_trials, total) == (958935, 2200, 961135), (prev_total, batch_trials, total)
assert merged_K == 534720, merged_K
assert k_lift == -0.0001, k_lift
assert line_merged == 1.1934 and line_pre == 1.1935, (line_merged, line_pre)
assert n_eff_he == 958935, n_eff_he
assert se_mu_at_k == 0.000335, se_mu_at_k
assert a_p95 == 0.2952, a_p95
assert fin['audit']['finalize_only'] is True, 'W244 finalize product audit face'

# seat probe bands must equal the W245 target bands
bands = probe['bands']
assert bands['A'] == [555501, 557500] and bands['B'] == [542001, 542200], bands
leg1 = probe['legs']['leg1']
assert leg1['A'] == [555501, 557500] and leg1['B'] == [542001, 542200], leg1
assert leg1['hops_A'] == 0 and leg1['hops_B'] == 1, (leg1['hops_A'], leg1['hops_B'])
assert leg1['A_hop_chain'] == [] and len(leg1['B_hop_chain']) == 1, (leg1['A_hop_chain'], leg1['B_hop_chain'])
hop = leg1['B_hop_chain'][0]
assert hop['window'] == [541901, 542100] and hop['jump_to'] == 542001 and hop['refuser_pts'] == [542000], hop
assert leg1['ARITH_A'] == [555501, 557500] and leg1['ARITH_B'] == [541901, 542100], (leg1['ARITH_A'], leg1['ARITH_B'])
assert leg1['B_naive_first_clean'] == [542001, 542200] and leg1['B_naive_hops'] == 1, leg1
rel = leg1['relation_asserts']
assert rel['A_clean_at_naive_start'] is True and rel['AB_mutual_exclusion'] is True, rel
assert rel['B_honest_forward_hop_expected_face'] is True and rel['B_no_ownA_jump'] is True, rel
assert rel['A_base_ge_priorB_tail_plus1'] is True and rel['B_base_above_priorB_tail'] is True, rel
assert rel['B_hop_lands_inside_A'] is False, rel
assert 'sixth consecutive seed-gap A-continuation' in leg1['A_semantics'], leg1['A_semantics'][:200]
assert 'seed-driven' in leg1['B_semantics'], leg1['B_semantics'][:200]
leg4 = probe['legs']['leg4']
assert leg4['W246p_A_naive'] == '557501..559500' and leg4['hops_A'] == 0, leg4
assert leg4['W246p_A_first_clean'] == '557501..559500', leg4
assert leg4['W246p_A_naive_refusers_seeds'] == [], leg4
assert leg4['W246p_B_naive'] == '542201..542400' and leg4['hops_B'] == 0, leg4
assert leg4['W246p_B_first_clean'] == '542201..542400', leg4
assert leg4['W246p_B_lands_inside_W246p_A_naive'] is False, leg4
leg0 = probe['legs']['leg0']
assert leg0['rows'] == 242 and leg0['w244_splice_landed'] is True, leg0
assert leg0['w244_finalize_landed'] is True and leg0['owner_rows'] == 234, leg0
assert leg0['bmc_rows'] == 67 and leg0['bma_rows'] == 126 and leg0['bmb_rows'] == 41, leg0
assert leg0['ordinal'] == 235 and leg0['bma_ordinal'] == 127, leg0
assert leg0['w244_bands'] == {'A': [553501, 555500], 'B': [541701, 541900]}, leg0
fa = leg0['w244_finalize_anchors']
assert fa['ledger_total'] == 961135 and fa['merged_n'] == 534720 and fa['skill_line_delta_k_lift'] == -0.0001, fa

# live n1_bands derive (freeze-window truth, r587)
sys.path.insert(0, 'scripts')
sys.path.insert(0, 'research')
spec = importlib.util.spec_from_file_location('pfn1', 'scripts/perpetual_faces.py')
pf_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pf_mod)
nrows = pf_mod.N1_BANDS
n_rows = len(nrows)
keys = sorted(nrows.keys())
owner_counter = Counter(v.get('engine_owner') for v in nrows.values())
owner_rows = sum(c for o, c in owner_counter.items() if o is not None)
bmc_rows = owner_counter.get('bm-c', 0)
bma_rows = owner_counter.get('bm-a', 0)
assert n_rows == 242 and keys[-2:] == [243, 244], (n_rows, keys[-2:])
assert 245 not in keys, 'W245 already registered?!'
assert owner_rows == 234 and bmc_rows == 67 and bma_rows == 126, (owner_rows, bmc_rows, bma_rows)
w244 = dict(nrows.get(244) or {})
assert w244.get('engine_owner') == 'bm-a', w244
assert tuple(w244.get('a') or ()) == (553501, 555500), w244
assert tuple(w244.get('b_exit') or ()) == (541701, 541900), w244

# satengine live status (engine queue empty at derive time)
st = subprocess.run([sys.executable, 'scripts/saturation_engine.py', 'status'],
                    capture_output=True)
assert st.returncode == 0, st.stderr[:200]
stj = json.loads(st.stdout.decode('utf-8'))
burns = stj.get('active_burns') or stj.get('burns_active') or []
queue_next = stj.get('queue_next') or []
queue_depth = stj.get('queue_depth', 0)
assert burns == [] and queue_next == [] and queue_depth == 0, (burns, queue_next, queue_depth)

# RAM face live read
try:
    import psutil
    ram_free_gb = round(psutil.virtual_memory().available / 1e9, 1)
except Exception:
    ram_free_gb = 5.0

MINUS = '\u2212'  # U+2212 (family convention in prereg keys)
mu_s = '%s%.8f' % (MINUS, abs(merged_mu))            # -0.09280471 (U+2212 face)
wmu_s = '%s%.8f' % (MINUS, abs(w244_only_mu))        # -0.10390359
sigma_s = '%.8f' % merged_sigma                      # 0.24505388
delta_s = '%.4f' % abs(merged_mu - w244_only_mu)     # 0.0111
if k_lift < 0:
    k_lift_s = '%s%.4f' % (MINUS, abs(k_lift))       # -0.0001 (U+2212 face, first-negative)
else:
    k_lift_s = '+%.4f' % k_lift

# ---------- template ----------
tpl = git_show(TPL_COMMIT, 'research/PERPETUAL_N1_W244_PREREG.md')

SUBS = []
A = SUBS.append

# S1 title (4 pairs)
A(('# PERPETUAL-N1-W244 预注册 · N1 nulls-deepening 池第 242 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 233 注册在册',
   '# PERPETUAL-N1-W245 预注册 · N1 nulls-deepening 池第 243 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 234 注册在册'))
A(('（表尾 W243 行·probe leg0 机证 241 行〔W243 splice 先于席位窗已落地〕live 单态如实注记）',
   '（表尾 W244 行·probe leg0 机证 242 行〔W244 splice 先于席位窗已落地〕live 单态如实注记）'))
A(('（bm-a r1004 席位 MSG-20261015-0206-bma-w244-seat·probe receipt _w244bma_20261015 机证·bands ADMIT verbatim·zero takeover）→freeze 时 live derive bma rows 125+候选=第 126 枚 EXACT',
   '（bm-a r1010 席位 MSG-20261015-0844-bma-w245-seat·probe receipt _w245bma_20261015 机证·bands ADMIT verbatim·GM re-assignment takeover lane）→freeze 时 live derive bma rows 126+候选=第 127 枚 EXACT'))
A(('【bm-a 循环班 r1005 freeze 窗 2026-10-15 02:4x·CEO 填载令 standing',
   '【bm-a 循环班 r1010 freeze 窗 2026-10-15 09:3x·CEO 填载令 standing'))

# S2 live-read round tag
A(('saturation_engine.py status live-read r1005：burns_active=[] queue_next=[] 实读',
   'saturation_engine.py status live-read r1010：burns_active=[] queue_next=[] 实读'))

# S3 wave-number + vacancy
A(('**波号 244=注册表 W243 席后首个自由号**【probe leg3 vacancy 机证（r1004 席位窗实跑：origin inbox/processed/ 零 W244 席位外机命中+origin perpetual_faces.py 零 244 行+origin perpetual_faces_n1.py 零 PERPETUAL-N1-W244 WAVE_CONFIGS+origin 零 PERPETUAL_N1_W244_PREREG.md 四查）',
   '**波号 245=注册表 W244 席后首个自由号**【probe leg3 vacancy 机证（r1010 席位窗实跑：origin inbox/processed/ 零 W245 席位外机命中+origin perpetual_faces.py 零 245 行+origin perpetual_faces_n1.py 零 PERPETUAL-N1-W245 WAVE_CONFIGS+origin 零 PERPETUAL_N1_W245_PREREG.md 四查）'))

# S3b chain-tail append W244 completion entry
A(('·n1_w243_results.json·01:4x）——本波上游链=W1..W243 finalize 全落地·零在飞上游席·干净前置**',
   '·n1_w243_results.json·01:4x）+W244=bm-a r1004 席位+r1005 prereg derive（machine-SUB from frozen W243 tpl 70141bc22）+五面冻结 splice（r1007 10bdb987b pushed）+引擎自燃 12/12（07:11:04 done claim-exempt engine lane）+bm-a r1008 finalize one-pass 已落（K=534,720·账本头 961,135 机读·n1_w244_results.json·07:4x）——本波上游链=W1..W244 finalize 全落地·零在飞上游席·干净前置**'))

# S3c seat publication + zero-gap
A(('席位公示=MSG-20261015-0206-bma-w244-seat 已推 origin 08df387e0 先于本冻结【r565 律·席位先行·bm-a r1004 窗发布·本窗=自有席承接】；下游 W245+ 投影见 §5.5（probe 机证 leg4·W245 freezer 承接面）】。**单态零席位空档**：W2..W243 全注册在冻结时点成立',
   '席位公示=MSG-20261015-0844-bma-w245-seat 已推 origin 2b0947947 先于本冻结【r565 律·席位先行·bm-a r1010 窗发布·本窗=GM re-assignment takeover 承接】；下游 W246+ 投影见 §5.5（probe 机证 leg4·W246 freezer 承接面）】。**单态零席位空档**：W2..W244 全注册在冻结时点成立'))

# S4 bands receipt path
A(('ADMIT 回执=results/_w244bma_20261015_probe_receipt.json 五腿单窗 gate-合并单回执结构',
   'ADMIT 回执=results/_w245bma_20261015_probe_receipt.json 五腿单窗 gate-合并单回执结构'))

# S4a A-ext (sixth consecutive seed-gap A-continuation)
A(('**A-ext seed=553_501..555_500**（**A 面=FIRST-CLEAN·hops=0 seed-decoupled A-continuation 形态**：A 面算术续带 553_501..555_500（自注册 W243 A 尾 553_500 续）在 post-W243 注册宇宙上起点即 CLEAN 零活点拒（W243 席位 leg4 投影兑现·连续第五个 seed-gap face·W243 A/B decoupled 承袭·probe leg1 A_semantics 机证）→ 保留 naive 落位 **hops=0**·**A base==前波 A 尾+1（553_500+1）机检关系**（fc_a==fc_a_naive·A_hop_chain=[] 空集 leg1 机证·A_clean_at_naive_start=true）·非转录 r587 前向单调断言在走册）',
   '**A-ext seed=555_501..557_500**（**A 面=FIRST-CLEAN·hops=0 seed-decoupled A-continuation 形态**：A 面算术续带 555_501..557_500（自注册 W244 A 尾 555_500 续）在 post-W244 注册宇宙上起点即 CLEAN 零活点拒（W244 席位 leg4 投影兑现·连续第六个 seed-gap face·W244 A/B decoupled 承袭·probe leg1 A_semantics 机证）→ 保留 naive 落位 **hops=0**·**A base==前波 A 尾+1（555_500+1）机检关系**（fc_a==fc_a_naive·A_hop_chain=[] 空集 leg1 机证·A_clean_at_naive_start=true）·非转录 r587 前向单调断言在走册）'))

# S4b B-ext (live-seed refusal hops=1 face, mirrors the W243-template B style)
A(('**B-ext exit seed=541_701..541_900**（**B 面=FIRST-CLEAN·hops=0 seed-decoupled 形态承袭**：B 面算术续带 541_701..541_900（自注册 W243 B 尾 541_700 续）在注册宇宙上 CLEAN 且**不落本波 A 窗 553_501..555_500 内**（本波 A 高悬于 B 阶梯之上→**seed-decoupled A/B gap 承袭面**：同窗互斥面 leg2 律·W141 先例·B 无需 own-A reservation jump）→ B 保留 naive 落位 **hops=0**·**B base==前波 B 尾+1（541_700+1）EXACT 机检关系**（fc_b==fc_b_naive·B_hop_chain=[] 空集 leg1 机证·B_no_ownA_jump=true·B_semantics seed-decoupled gap face sixth consecutive 回执在场）；**W243 席位 leg4 投影承接面注记兑现**：投影预言 W244 须在 post-W243 宇宙重 derive 且 A/B naive 双 CLEAN hops=0 如投影所期——本窗如实兑现·A 零活点拒=投影所期·B decoupled CLEAN 保留=投影所期·已如实披露非分叉）',
   '**B-ext exit seed=542_001..542_200**（**B 面=LIVE-SEED-REFUSAL·hops=1 seed-decoupled 形态承袭**：B 面 naive 续带 541_901..542_100（自注册 W244 B 尾 541_900 续）被 SEED_REGISTRY 活点 542_000 拒→诚实前行走 hop 1 first-clean 542_001..542_200 且**不落本波 A 窗 555_501..557_500 内**（本波 A 高悬于 B 阶梯之上→**seed-decoupled A/B gap 承袭面**：同窗互斥面 leg2 律·W141 先例·B 无需 own-A reservation jump）→ B 保留走落 542_001..542_200·**hops=1**·**B base==live-seed hop first-clean 机检关系**（fc_b==fc_b_naive hop 面·B_hop_chain=[naive 541_901..542_100→542_001·refuser 542_000] leg1 机证·B_no_ownA_jump=true·B_semantics seed-driven honest forward hop 回执在场）；**W244 席位 leg4 投影承接面注记兑现**：投影预言 W245 须在 post-W244 宇宙重 derive 且 A CLEAN hops=0+B live-seed hop 拒带面如投影所期——本窗如实兑现·A 零活点拒=投影所期·B live-seed hop 拒带=投影所期·已如实披露非分叉）'))

# S4c R250
A(('R250：W244 带从未指派', 'R250：W245 带从未指派'))

# S4d seed gate
A(('A base=553501 span=2000 checked=2000 verdict=FREE / B base=541701 span=200 checked=200 verdict=FREE',
   'A base=555501 span=2000 checked=2000 verdict=FREE / B base=542001 span=200 checked=200 verdict=FREE'))

# S4e scan face
A(('扫描面=pre-W244 全二百四十一行注册 N1 带表（表尾 W243 行·freeze 窗 live derive 241 行单态 owner rows 233——席位窗 probe leg0 实测 241 行〔W243 splice 先于席位窗已落地·零 +1〕如实注记）',
   '扫描面=pre-W245 全二百四十二行注册 N1 带表（表尾 W244 行·freeze 窗 live derive 242 行单态 owner rows 234——席位窗 probe leg0 实测 242 行〔W244 splice 先于席位窗已落地·零 +1〕如实注记）'))

# S5 reuse-domain (3 pairs)
A(('（W2..W243 落地 runner 的 wave 参数化复用', '（W2..W244 落地 runner 的 wave 参数化复用'))
A(('selftest W244 face 将随五面冻结落地验证', 'selftest W245 face 将随五面冻结落地验证'))
A(('本件与 results/_w244bma_freeze_edits.py（五面冻结拼接脚本·按 _w243bma_freeze_edits.py 模板派生·gate0.5 自查 W243 行+W243 finalize 件在场·未落即 loud abort·estate 提取面=本机 W243 块物理字节〔结构已知〕）=freeze-prep 束同窗落地（r1001/W243 先例 freeze-prep 同式·本窗上游已全落=执行窗即 freeze 窗）',
   '本件与 results/_w245bma_freeze_edits.py（五面冻结拼接脚本·按 _w244bma_freeze_edits.py 模板派生·gate0.5 自查 W244 行+W244 finalize 件在场·未落即 loud abort·estate 提取面=本机 W244 块物理字节〔结构已知〕）=freeze-prep 束同窗落地（r1005/W244 先例 freeze-prep 同式·本窗上游已全落=执行窗即 freeze 窗）'))

# S6 batch identity (3 pairs)
A(('- 批名=**PERPETUAL-N1-W244**。', '- 批名=**PERPETUAL-N1-W245**。'))
A(('**W1..W243 N1 finalize 已全部落地**【净账本锚头 **958,935**·K=532,520 合并池·n1_w243_results.json 机读·W243 finalize one-pass bm-a r1003 窗 01:4x（W243 面完整性=12/12 shards consumed+finalize audit finalize_only=true 收口·死窗 estate 收养+引擎自燃链如实注记）】',
   '**W1..W244 N1 finalize 已全部落地**【净账本锚头 **961,135**·K=534,720 合并池·n1_w244_results.json 机读·W244 finalize one-pass bm-a r1008 窗 07:4x（W244 面完整性=12/12 shards consumed+finalize audit finalize_only=true 收口·死窗 estate 收养+引擎自燃链如实注记）】'))
A(('累计 null 池=532,520+2,200（本波）=**534,720 投影**',
   '累计 null 池=534,720+2,200（本波）=**536,920 投影**'))

# S7 claim (seat + W246+ projection with CLEAN face)
A(('（席位公示=MSG-20261015-0206-bma-w244-seat 已推 origin 08df387e0 r565 律（bm-a r1004 席·bm-a 自有席承接）·probe W245+ 投影 A 555_501..557_500 / B naive 541_901..542_100→first-clean 542_001..542_200 **A CLEAN hops=0+B hops=1 拒带面预披露+seed-gap 承袭注记**（投影 A naive 555_501..557_500 CLEAN 零活点拒·hops=0；投影 B naive 541_901..542_100 **hops=1 拒带面**——窗内被活点拒→诚实前行走 first-clean 542_001..542_200·hops=1——**seed-gap 承袭 face：W244 A/B 仍 decoupled〔A 553_501..555_500 高悬于 B 541_701..541_900 之上〕·W245 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace·W244 B 带将拒 naive W245 A 窗仅当重叠——**W245 freezer 承接面强制注记：须在 post-W244 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**））',
   '（席位公示=MSG-20261015-0844-bma-w245-seat 已推 origin 2b0947947 r565 律（bm-a r1010 席·GM re-assignment takeover 承接）·probe W246+ 投影 A 557_501..559_500 / B 542_201..542_400 **双面 CLEAN hops=0 预披露+seed-gap 承袭注记**（投影 A naive 557_501..559_500 CLEAN 零活点拒·hops=0；投影 B naive 542_201..542_400 CLEAN hops=0 不落投影 A 窗内——**seed-gap 承袭 face：W245 A/B 仍 decoupled〔A 555_501..557_500 高悬于 B 542_001..542_200 之上〕·W246 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace·W245 B 带将拒 naive W246 A 窗仅当重叠——**W246 freezer 承接面强制注记：须在 post-W245 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**））'))

# S7b ordinal
A(('T-2026-10-01-141 s1 引擎线第 234 波【bm-a 第一百二十六枚自有波【机面 derive：probe leg0 bma_rows=125 attempt-continuity face（r1004 窗算法·bm-a own seat+bma live rows 125 实读）——freeze 时 live derive bma rows 125+候选=第 126 枚 EXACT（以 freeze 时 live derive 为准 r587/r359）】】',
   'T-2026-10-01 s1 引擎线第 235 波【bm-a 第一百二十七枚自有波【机面 derive：probe leg0 bma_rows=126 attempt-continuity face（r1010 窗算法·bm-a own seat+bma live rows 126 实读）——freeze 时 live derive bma rows 126+候选=第 127 枚 EXACT（以 freeze 时 live derive 为准 r587/r359）】】'))

# S7c
A(('（波号=注册表 W243 席后首个自由号·单态零席位空档于冻结时点成立；席位公示 MSG-20261015-0206-bma-w244-seat 先推 origin 08df387e0 r565 律；lane-free；dept:研究）',
   '（波号=注册表 W244 席后首个自由号·单态零席位空档于冻结时点成立；席位公示 MSG-20261015-0844-bma-w245-seat 先推 origin 2b0947947 r565 律；lane-free；dept:研究）'))

# S8 RAM face (live read; prior-window anchors shift +1, tail trims per family list discipline)
A(('**RAM face 如实注记：本窗 free RAM ~41.9GB（bm-a 底盘常驻·94G 物理内存机·MV V3 终剪线=CEO 夜令 O-20261014-1855 在飞〔MV 优先级最高·导演席窗〕+CPU 车道独立如实注记）——N1 引擎点火无 RAM 硬闸（W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230/W231/W232/W233/W234/W235/W236/W237/W238/W239/W240/W241/W242/W243 低 RAM 实烧先例·W243 冻结窗 64.0G bm-a 实锚·W242 冻结窗 17.6G bm-a 实锚·W241 冻结窗 1.8G bm-c 实锚·W240 冻结窗 33.2G bm-a 实锚·W239 冻结窗 1.0G bm-c 实锚·W238 冻结窗 70.1G bm-a 实锚·W237 冻结窗 1.6G 实锚族）·burn 由引擎 RAM 面随 cycle 上报自判·本件不代引擎决策。**',
   f'**RAM face 如实注记：本窗 free RAM ~{ram_free_gb:.1f}GB（bm-a 底盘常驻·94G 物理内存机·MV V3 终剪线=CEO 夜令 O-20261014-1855 在飞〔MV 优先级最高·导演席窗〕+CPU 车道独立如实注记）——N1 引擎点火无 RAM 硬闸（W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230/W231/W232/W233/W234/W235/W236/W237/W238/W239/W240/W241/W242/W243/W244 低 RAM 实烧先例·W244 冻结窗 41.9G bm-a 实锚·W243 冻结窗 64.0G bm-a 实锚·W242 冻结窗 17.6G bm-a 实锚·W241 冻结窗 1.8G bm-c 实锚·W240 冻结窗 33.2G bm-a 实锚·W239 冻结窗 1.0G bm-c 实锚·W238 冻结窗 70.1G bm-a 实锚）·burn 由引擎 RAM 面随 cycle 上报自判·本件不代引擎决策。**'))

# S9 materialization (self-see wave face)
A(('自见 W244 行并点火自烧', '自见 W245 行并点火自烧'))

# S10 banned gate path
A(('--prereg research/PERPETUAL_N1_W244_PREREG.md', '--prereg research/PERPETUAL_N1_W245_PREREG.md'))

# S11 manual pre-read
A(('（p2_calibration v1/v2 canon；v1 ext；v2..W243 落地）', '（p2_calibration v1/v2 canon；v1 ext；v2..W244 落地）'))

# S12 A-tier
A(('- **A 档**（j=0..1,999）：entry rng seed=**553_501+j**（法典 §4 W244 行 A=553_501..555_500·**FIRST-CLEAN·hops=0 seed-decoupled A-continuation 形态**：A 算术续带 553_501..555_500（自注册 W243 A 尾 553_500 续）在 post-W243 注册宇宙上起点即 CLEAN 零活点拒（W243 席位 leg4 投影兑现·连续第五个 seed-gap face·W243 A/B decoupled 承袭）→保留 naive 落位 hops=0·**A base==前波 A 尾+1（553_500+1）机检关系**（fc_a==fc_a_naive·A_hop_chain=[] 空集 probe leg1 机证·A_clean_at_naive_start=true）·非转录 r587·ADMIT 回执在场）',
   '- **A 档**（j=0..1,999）：entry rng seed=**555_501+j**（法典 §4 W245 行 A=555_501..557_500·**FIRST-CLEAN·hops=0 seed-decoupled A-continuation 形态**：A 算术续带 555_501..557_500（自注册 W244 A 尾 555_500 续）在 post-W244 注册宇宙上起点即 CLEAN 零活点拒（W244 席位 leg4 投影兑现·连续第六个 seed-gap face·W244 A/B decoupled 承袭）→保留 naive 落位 hops=0·**A base==前波 A 尾+1（555_500+1）机检关系**（fc_a==fc_a_naive·A_hop_chain=[] 空集 probe leg1 机证·A_clean_at_naive_start=true）·非转录 r587·ADMIT 回执在场）'))

# S13 B-tier (live-seed hops=1 face, mirrors the W243-template B style)
A(('- **B 档**（j=0..199）：entry rng=**553_501+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**541_701+j**（法典 §4 W244 行 B=541_701..541_900·**FIRST-CLEAN·hops=0 seed-decoupled 形态承袭**：B 算术续带 541_701..541_900（自注册 W243 B 尾 541_700 续）在注册宇宙 CLEAN 且不落本波 A 窗 553_501..555_500 内（本波 A 高悬于 B 阶梯之上→同窗互斥面 leg2 律·W141 先例·B 无需 own-A reservation jump）→保留走落 541_701..541_900·hops=0·**B base==前波 B 尾+1（541_700+1）EXACT 机检关系**（fc_b==fc_b_naive·B_hop_chain=[] 空集 leg1 机证·B_no_ownA_jump=true·B_semantics seed-decoupled gap face sixth consecutive 回执在场）·非转录 r587·与 W243 席位 leg4 投影承接面注记兑现收敛·ADMIT 回执在场）',
   '- **B 档**（j=0..199）：entry rng=**555_501+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**542_001+j**（法典 §4 W245 行 B=542_001..542_200·**LIVE-SEED-REFUSAL·hops=1 seed-decoupled 形态承袭**：B naive 续带 541_901..542_100（自注册 W244 B 尾 541_900 续）被 SEED_REGISTRY 活点 542_000 拒→诚实前行走 hop 1 first-clean 542_001..542_200 且不落本波 A 窗 555_501..557_500 内（本波 A 高悬于 B 阶梯之上→同窗互斥面 leg2 律·W141 先例·B 无需 own-A reservation jump）→保留走落 542_001..542_200·hops=1·**B base==live-seed hop first-clean 机检关系**（fc_b==fc_b_naive hop 面·B_hop_chain=[naive 541_901..542_100→542_001·refuser 542_000] leg1 机证·B_no_ownA_jump=true·B_semantics seed-driven honest forward hop 回执在场）·非转录 r587·与 W244 席位 leg4 投影承接面注记兑现收敛·ADMIT 回执在场）'))

# S14 disjoint + estate family (5 pairs)
A(('种子带 disjoint 全例（selftest 强制）：W244 带与 v1 在用带', '种子带 disjoint 全例（selftest 强制）：W245 带与 v1 在用带'))
A(('W2..W243 带（冻结时点全注册单态）', 'W2..W244 带（冻结时点全注册单态）'))
A(('本波机验 ADMIT 回执在场=_w244bma_20261015 探针窗', '本波机验 ADMIT 回执在场=_w245bma_20261015 探针窗'))
A(('selftest W244 face（A=first-clean A-continuation past prior-wave A tail+live-seeds 恒等·B=first-clean past prior-wave B tail+own-wave A 同窗互斥断言·W243 行 parity 腿',
   'selftest W245 face（A=first-clean A-continuation past prior-wave A tail+live-seeds 恒等·B=live-seed-hop first-clean past own-wave A 同窗互斥断言·W244 行 parity 腿'))
A(('从**本机 W243 块物理字节**提取（结构已知·提取自证断言 69 行 range 恒等在场）——W243 块的自有 W233..W242 legs（10 行）不入 estate 路径·提取后新增 W233..W243 leg（11 行）构成 W244 块 parity 102 行（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232+W233+W234+W235+W236+W237+W238+W239+W240+W241+W242+W243）·零假设零风险。',
   '从**本机 W244 块物理字节**提取（结构已知·提取自证断言 69 行 range 恒等在场）——W244 块的自有 W234..W243 legs（10 行）不入 estate 路径·提取后新增 W234..W244 leg（11 行）构成 W245 块 parity 103 行（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232+W233+W234+W235+W236+W237+W238+W239+W240+W241+W242+W243+W244）·零假设零风险。'))

# S15 ledger
A(('batch_name="PERPETUAL-N1-W244", batch_trials=2200, file_name="results/perpetual_faces/n1_w244_results.json"',
   'batch_name="PERPETUAL-N1-W245", batch_trials=2200, file_name="results/perpetual_faces/n1_w245_results.json"'))

# S16 merged-pool live flow
A(('（起草窗实流 W1..W243 已落账 532,520 实测·derive 禁手抄）',
   '（起草窗实流 W1..W244 已落账 534,720 实测·derive 禁手抄）'))

# S17 preamble
A(('（起草窗实况注记：**W1..W243 N1 finalize 已全部落地**——净账本锚头 958,935·**K=532,520 合并池**·**零在飞上游席——本波 §5 预测键=**W243 实测值**【results/perpetual_faces/n1_w243_results.json·N1 面最新已落账键·01:4x finalize one-pass】。',
   '（起草窗实况注记：**W1..W244 N1 finalize 已全部落地**——净账本锚头 961,135·**K=534,720 合并池**·**零在飞上游席——本波 §5 预测键=**W244 实测值**【results/perpetual_faces/n1_w244_results.json·N1 面最新已落账键·07:4x finalize one-pass】。'))

# S18 key1
A(('1. W244-only mu 与累计池 merged mu（W243 实测键 **\u22120.09275885**·K=532,520 合并池·W243-only 实测 **\u22120.09687705**）差异 **|Δ|<0.02**（W2..W243 共二百四十一面实测 mu 稳定先例·单波跨键微；W243-only vs merged 实差 0.0041 在带内）。',
   f'1. W245-only mu 与累计池 merged mu（W244 实测键 **{mu_s}**·K=534,720 合并池·W244-only 实测 **{wmu_s}**）差异 **|Δ|<0.02**（W2..W244 共二百四十二面实测 mu 稳定先例·单波跨键微；W244-only vs merged 实差 {delta_s} 在带内）。'))

# S19 key2
A(('2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.24506859**=W243 合并池实测）。',
   f'2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **{sigma_s}**=W244 合并池实测）。'))

# S20 key3
A(('3. A 档 full_sharpe_p95 与 W243 A 档 p95（**0.3193** 实测锚）差 **<0.05**（门标注法 W5..W243 先例：结果知情面仅作机器断言之用·测量面非注册收益）。利益）。',
   f'3. A 档 full_sharpe_p95 与 W244 A 档 p95（**{a_p95:.4f}** 实测锚）差 **<0.05**（门标注法 W5..W244 先例：结果知情面仅作机器断言之用·测量面非注册收益）。利益）。'))

# S21 key4 (2 pairs)
A(('W136..W243 先例链披露【各波 K-lift 全在 ±0.0003 内·机读可复核·键 W243 实测 K-lift **+0.0001**·line_merged@K532,520 **1.1934**·line_pre_w243 1.1933·n_eff_held_equal 956,735；',
   'W136..W244 先例链披露【各波 K-lift 全在 ±0.0003 内·机读可复核·键 W244 实测 K-lift **%s**·line_merged@K534,720 **1.1934**·line_pre_w244 1.1935·n_eff_held_equal 958,935；' % k_lift_s))
A(('→W241 **0.000337**→W242 **0.000337**→W243 **0.000336**】）。',
   '→W242 **0.000337**→W243 **0.000336**→W244 **0.000335**】）。'))

# S22 key5 W246+ projection (CLEAN face)
A(('5. **W245+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 555_501..557_500 **CLEAN**（hops=0·pre-W244 宇宙零活点拒）；B naive first-clean **542_001..542_200 hops=1 拒带面**（naive 541_901..542_100 窗内被活点拒→诚实前行走 first-clean 542_001..542_200·**不落投影 A 窗内**——B_hop lands-inside-A=false 腿在场）；**W244 B 带 541_701..541_900 注册后将拒 naive W245 A 窗仅当重叠**（**seed-gap 承袭 face：W244 A/B 仍 decoupled〔A 553_501..555_500 高悬于 B 541_701..541_900 之上〕·W245 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace**）——W245 冻结方必须在 post-W244 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡·W141 先例；verify at W245 prereg，hop 链逐跳在 probe 回执。',
   '5. **W246+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 557_501..559_500 **CLEAN**（hops=0·pre-W245 宇宙零活点拒）；B naive first-clean **542_201..542_400 CLEAN**（hops=0·**不落投影 A 窗内**——B_hop lands-inside-A=false 腿在场）；**W245 B 带 542_001..542_200 注册后将拒 naive W246 A 窗仅当重叠**（**seed-gap 承袭 face：W245 A/B 仍 decoupled〔A 555_501..557_500 高悬于 B 542_001..542_200 之上〕·W246 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace**）——W246 冻结方必须在 post-W245 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡·W141 先例；verify at W246 prereg，hop 链逐跳在 probe 回执。'))

# S23 runner (2 pairs)
A(('--shard k --of 12 --wave 244/finalize --wave 244', '--shard k --of 12 --wave 245/finalize --wave 245'))
A(('【n1_w244/ 分片计数增长', '【n1_w245/ 分片计数增长'))

# S24 deliverables (2 pairs)
A(('results/p2cal_ext/n1_w244/shard-<k>-of-12.json', 'results/p2cal_ext/n1_w245/shard-<k>-of-12.json'))
A(('`results/perpetual_faces/n1_w244_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 键序前置=**起草窗零在飞上游席（W1..W243 全落）',
   '`results/perpetual_faces/n1_w245_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 键序前置=**起草窗零在飞上游席（W1..W244 全落）'))

# S25 engine ledger
A(('engine_owner==bm-a 125 行注册〔冻结时点〕', 'engine_owner==bm-a 126 行注册〔冻结时点〕'))

# S26/S27 §7/§8 placeholders
A(('——bm-a r1003 W243 §7 范式）', '——bm-a r1008 W244 §7 范式）'))
A(('（占位·finalize 同窗回填：§5.5 W245+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——bm-a r1003 W243 §8 范式）',
   '（占位·finalize 同窗回填：§5.5 W246+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——bm-a r1008 W244 §8 范式）'))

# ---------- apply ----------
out = tpl
applied = 0
fails = []
for i, (old, new) in enumerate(SUBS, 1):
    n = out.count(old)
    if n != 1:
        fails.append('SUB#%d count=%d: %s...' % (i, n, old[:80]))
        continue
    out = out.replace(old, new)
    applied += 1
assert not fails, 'SUB misses (%d/%d applied):\n' % (applied, len(SUBS)) + '\n'.join(fails)

# ---------- forbidden-residue scan ----------
FORBID = ['PERPETUAL-N1-W244', 'n1_w244/shard', '553501', '541701', '553_501..555_500', '541_701..541_900',
          'engine_owner 行 233', '池第 242 枚', 'r1005 freeze 窗',
          '0206-bma', 'W2..W243', 'W1..W243', 'v2..W243', 'W5..W243', 'W136..W243',
          'parity 102 行', '08df387e0', '534,720 投影', '532,520+2,200',
          '共二百四十一面', '二百四十一行', 'engine_owner==bm-a 125', 'owner rows 233',
          '241 行', '240 行', '239 行', '0.09275885', '0.09687705', '0.24506859', '0.3193', '958,935·K=532,520',
          'fourth consecutive', 'fifth consecutive', 'sixth consecutive', '连续第五个 seed-gap', '第 234 波', 'r1004 席·bm-a 自有席承接',
          '第 126 枚', 'bma rows 125', 'W244-inherit']
residue = [f for f in FORBID if f in out]
assert not residue, 'forbidden residue: %s' % residue

# legal retained counts (calibrated against the frozen-template live counts:
# own-band literals mirror the template's own-band counts; wave-count faces mirror 1:1)
assert out.count('_w244bma') == 1 and out.count('_w244bma_freeze_edits.py') == 1   # freeze-edits template-source citation x1 (r587 lineage)
assert out.count('_w245bma') == 4                                                    # title + 带位 receipt + freeze-edits own + §3 probe-window
assert out.count('n1_w240_results.json') == 1                                        # chain-tail W240 historical entry
assert out.count('n1_w241_results.json') == 1                                        # chain-tail W241 historical entry
assert out.count('n1_w242_results.json') == 1                                        # chain-tail W242 historical entry
assert out.count('n1_w243_results.json') == 1                                        # chain-tail W243 historical entry
assert out.count('n1_w244_results.json') == 3                                        # chain-tail W244 append + S6 + S17 preamble
assert out.count('n1_w245_results.json') == 2                                        # ledger + deliverable
assert out.count('PERPETUAL-N1-W245') == 4, out.count('PERPETUAL-N1-W245')
assert out.count('PERPETUAL_N1_W245') == 2, out.count('PERPETUAL_N1_W245')           # vacancy check + gate path
assert 'n1_w245/shard' in out
assert out.count('555_501..557_500') == 8 and out.count('542_001..542_200') == 9   # own-band literals (A x8 mirror template; B x9 hops=1 face mirror W243-template own-B count)
assert out.count('seed-driven honest forward hop') == 2                             # B-ext + S13 face
assert out.count('连续第六个 seed-gap') == 2                                       # A-ext + S12 face (mirror template 连续第五个 x2)
assert out.count('557_501..559_500') == 3 and out.count('542_201..542_400') == 3   # W246 projection (S7 header+narrative + S22)
assert '0844-bma' in out and out.count('0844-bma') == 4                            # own seat MSG
assert '2b0947947' in out and out.count('2b0947947') == 3                          # own seat commit
assert out.count('第 127 枚') == 2                                                 # bma ordinal (title + S7b)
assert out.count('961,135') == 3                                                    # net ledger head (S6 + chain append + S17)
assert out.count('958,935') == 2                                                    # chain-tail W243 entry + n_eff_held_equal
assert out.count('956,735') == 1                                                    # chain-tail W242 entry
assert out.count('954,535') == 1                                                    # chain-tail W241 entry
assert '952,335' in out and '950,135' in out and '945,189' in out                  # deep chain history entries
assert '555501' in out and '542001' in out                                          # seed gate bare bases
assert out.count('owner rows 234') == 1 and out.count('engine_owner 行 234') == 1
assert out.count('242 行') == 3                                                     # title + S4e x2 (W244 splice pre-seat face)
assert out.count('W2..W244') == 4 and out.count('W1..W244') == 5
assert out.count('v2..W244') == 1 and out.count('W5..W244') == 1
assert out.count('17:3x') == 1 and out.count('19:5x') == 2 and out.count('20:4x') == 1 and out.count('01:4x') == 1 and out.count('07:4x') == 3   # chain W243 entry + S6 + S17 + chain W244 append
assert out.count('第 235 波') == 1 and out.count('池第 243 枚') == 1
assert out.count('parity 103 行') == 1 and out.count('共二百四十二面') == 1 and out.count('二百四十二行') == 1
assert out.count('536,920 投影') == 1 and out.count('534,720+2,200') == 1
assert out.count('W246-inherit') == 0                                               # stale face never in prereg

with open(OUT_PATH, 'w', encoding='utf-8', newline='') as fh:
    fh.write(out)

receipt = {
    'derive': 'W245 prereg machine-generated SUB from frozen W244 template',
    'machine': 'bm-a', 'round': 'r1010',
    'template_commit': TPL_COMMIT,
    'upstream_finalize_commit': FIN_COMMIT,
    'sub_pairs_applied': applied,
    'out_path': OUT_PATH,
    'out_bytes': len(out.encode('utf-8')),
    'takeover_face': 'GM re-assignment takeover lane (bm-c declared W245 turn at r1020 closeout 07:31 then stalled; seat MSG-20261015-0844-bma-w245-seat published by dead r1010 window @ commit 2b0947947, pushed to origin by this r1010 estate-absorption successor)',
    'facts': {
        'merged_mu': merged_mu, 'merged_sigma': merged_sigma,
        'w244_only_mu': w244_only_mu, 'w244_only_sigma': npc['w244_only']['sigma'],
        'a_p95': a_p95, 'se_mu_at_k': se_mu_at_k, 'k_lift': k_lift,
        'line_merged': line_merged, 'line_pre': line_pre, 'n_eff_held_equal': n_eff_he,
        'ledger_prev_total': prev_total, 'ledger_batch': batch_trials, 'ledger_total': total,
        'merged_K': merged_K,
        'n1_bands_rows': n_rows, 'owner_rows': owner_rows, 'bmc_rows': bmc_rows, 'bma_rows': bma_rows,
        'bands': {'A': [555501, 557500], 'B': [542001, 542200]},
        'ram_free_gb': ram_free_gb,
        'engine_status': {'active_burns': burns, 'queue_next': queue_next, 'queue_depth': queue_depth},
        'seed_hop_face': {'hops_A': leg1['hops_A'], 'A_hop_chain': leg1['A_hop_chain'],
                          'hops_B': leg1['hops_B'], 'b_hop_chain': leg1['B_hop_chain'],
                          'b_refuser': 542000, 'b_decoupled': True},
        'w246p': {'refusers': leg4['W246p_A_naive_refusers_seeds'],
                  'first_clean': leg4['W246p_A_first_clean'], 'hops': leg4['hops_A'],
                  'B_naive': leg4['W246p_B_naive'], 'B_first_clean': leg4['W246p_B_first_clean'],
                  'B_hops': leg4['hops_B'], 'B_inside_A': leg4['W246p_B_lands_inside_W246p_A_naive']},
    },
    'forbidden_residue': residue,
}
json.dump(receipt, open('results/_w245bma_prereg_derive_receipt.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('W245 prereg derive OK: %d SUB pairs, out=%d bytes -> %s' % (applied, len(out.encode('utf-8')), OUT_PATH))
print('facts: n1_bands=%d rows owner_rows=%d bmc=%d bma=%d ram_free=%.1fG' % (n_rows, owner_rows, bmc_rows, bma_rows, ram_free_gb))
