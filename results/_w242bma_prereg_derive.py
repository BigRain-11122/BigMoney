# -*- coding: utf-8 -*-
"""W242 prereg derive -- bm-a r998 freeze window (freeze UNBLOCKED: W241 finalize
landed af6ec72f9 19:5x; seat MSG-20261014-1814-bma-w242-seat published by bm-a
itself @ origin 138a94745 r995, own-seat continuity, zero takeover).

Machine-generated SUB from committed W241 frozen template (git a9ab3b51d), zero
transcription (r587 / r958 / r974 lineage; cloned mechanics from
_w240bma_prereg_derive.py + _w241bmc prereg-derive lineage). All anchor faces
machine-read live at derive time:
- results/perpetual_faces/n1_w241_results.json  (W241 finalize product, landed 19:5x)
- results/_w242bma_20261014_probe_receipt.json  (bm-a r995 seat probe ADMIT)
- Tools/saturation_engine.py n1_bands() live derive (239 rows, tail W241, owner rows 231)
Fail-closed: every SUB pair must hit exactly once; forbidden-residue scan must be zero.
"""
import json
import subprocess
import sys
import importlib.util
from collections import Counter

OUT_PATH = 'research/PERPETUAL_N1_W242_PREREG.md'
TPL_COMMIT = 'a9ab3b51d'   # W241 prereg frozen-at-commit (bm-c r1003 derive, r1004 estate absorb)
FIN_COMMIT = 'af6ec72f9'   # W241 finalize one-pass LANDED (bm-c r1005/r1006 estate closeout)


def git_show(ref, path):
    r = subprocess.run(['git', 'show', '%s:%s' % (ref, path)], capture_output=True)
    assert r.returncode == 0, 'git show failed: %s' % r.stderr[:300]
    return r.stdout.decode('utf-8')


# ---------- facts (live machine-read, zero transcription) ----------
fin = json.load(open('results/perpetual_faces/n1_w241_results.json', encoding='utf-8'))
probe = json.load(open('results/_w242bma_20261014_probe_receipt.json', encoding='utf-8'))

npc = fin['null_pool_cumulative']
merged_mu = npc['merged']['mu']
merged_sigma = npc['merged']['sigma']
w241_only_mu = npc['w241_only']['mu']
a_p95 = fin['families']['A_random_engine_exit']['full_sharpe_p95']
se_mu_at_k = npc['se_mu_at_k528120']
k_lift = fin['skill_line_v2_k_lift']['line_delta_k_lift']
line_merged = fin['skill_line_v2_k_lift']['line_merged_528120']
line_pre = fin['skill_line_v2_k_lift']['line_pre_w241']
n_eff_he = fin['skill_line_v2_k_lift']['n_eff_held_equal']
led = fin['science_gates']['ledger']
prev_total, batch_trials, total = led['prev_total'], led['batch_trials'], led['total']
merged_K = npc['merged']['n_values']

# sanity: five-key anchors must equal the landed finalize numbers
assert (prev_total, batch_trials, total) == (952335, 2200, 954535), (prev_total, batch_trials, total)
assert merged_K == 528120, merged_K
assert k_lift == 0.0, k_lift
assert line_merged == line_pre == 1.1933, (line_merged, line_pre)
assert n_eff_he == 952335, n_eff_he
assert se_mu_at_k == 0.000337, se_mu_at_k
assert a_p95 == 0.3216, a_p95
assert fin['audit']['finalize_only'] is True, 'W241 finalize product audit face'

# seat probe bands must equal the W242 target bands
bands = probe['bands']
assert bands['A'] == [549501, 551500] and bands['B'] == [541204, 541403], bands
leg1 = probe['legs']['leg1']
assert leg1['A'] == [549501, 551500] and leg1['B'] == [541204, 541403], leg1
assert leg1['hops_A'] == 0 and leg1['hops_B'] == 0, (leg1['hops_A'], leg1['hops_B'])
rel = leg1['relation_asserts']
assert rel['A_clean_at_naive_start'] is True and rel['A_base_ge_priorB_tail_plus1'] is True, rel
assert rel['B_base_eq_priorB_tail_plus1'] is True and rel['AB_mutual_exclusion'] is True, rel
assert rel['B_no_ownA_jump'] is True, rel
assert leg1['A_hop_chain'] == [] and leg1['B_hop_chain'] == [], (leg1['A_hop_chain'], leg1['B_hop_chain'])
assert leg1['ARITH_A'] == [549501, 551500] and leg1['ARITH_B'] == [541204, 541403], (leg1['ARITH_A'], leg1['ARITH_B'])
assert leg1['B_naive_first_clean'] == [541204, 541403] and leg1['B_naive_hops'] == 0, leg1
assert 'seed-gap' in leg1['A_semantics'], leg1['A_semantics'][:200]
assert 'seed-decoupled' in leg1['B_semantics'], leg1['B_semantics'][:200]
leg4 = probe['legs']['leg4']
assert leg4['W243p_A_naive'] == '551501..553500' and leg4['hops_A'] == 0, leg4
assert leg4['W243p_A_first_clean'] == '551501..553500', leg4
assert leg4['W243p_A_naive_refusers_seeds'] == [], leg4
assert leg4['W243p_B_naive'] == '541404..541603' and leg4['hops_B'] == 1, leg4
assert leg4['W243p_B_first_clean'] == '541501..541700', leg4
assert leg4['W243p_B_lands_inside_W243p_A_naive'] is False, leg4
leg0 = probe['legs']['leg0']
assert leg0['w240_finalize_landed'] is True and leg0['w241_splice_landed'] is False, leg0

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
bma_rows = owner_counter.get('bm-a', 0)
assert n_rows == 239 and keys[-2:] == [240, 241], (n_rows, keys[-2:])
assert 242 not in keys, 'W242 already registered?!'
assert owner_rows == 231 and bmc_rows == 67 and bma_rows == 123, (owner_rows, bmc_rows, bma_rows)
w241 = dict(nrows.get(241) or {})
assert w241.get('engine_owner') == 'bm-c', w241
assert tuple(w241.get('a') or ()) == (547501, 549500), w241
assert tuple(w241.get('b_exit') or ()) == (541004, 541203), w241

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
    ram_free_gb = 5.0

MINUS = '\u2212'  # U+2212 (family convention in prereg keys)
mu_s = '%s%.8f' % (MINUS, abs(merged_mu))            # -0.09275777 (U+2212 face)
wmu_s = '%s%.8f' % (MINUS, abs(w241_only_mu))        # -0.09104545
sigma_s = '%.8f' % merged_sigma                      # 0.24509946
delta_s = '%.4f' % abs(merged_mu - w241_only_mu)     # 0.0017

# ---------- template ----------
tpl = git_show(TPL_COMMIT, 'research/PERPETUAL_N1_W241_PREREG.md')

SUBS = []
A = SUBS.append

# S1 title line
A(('# PERPETUAL-N1-W241 预注册 · N1 nulls-deepening 池第 239 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 230 注册在册（表尾 W240 行·probe leg0 机证 238 行 live 单态零注入腿）+本候选=bm-c 自有席自有波【live-derive face：席面 own-seat face（bm-c r1002 席位 MSG-20261014-1755-bmc-w241-seat·probe receipt _w241bmc_20261014 机证·bands ADMIT verbatim·zero takeover）→freeze 时 live derive bmc rows 66+候选=第 67 枚 EXACT·以 freeze 时 live derive 为准 r587/r359】【bm-c 循环班 r1003 freeze 窗 2026-10-14 18:3x·CEO 填载令 standing+2026-10-10 ~23:1x RE-ISSUE+O-20260909-2334 本地满用令+O-20261013-2215 CPU 常开令】）',
   '# PERPETUAL-N1-W242 预注册 · N1 nulls-deepening 池第 240 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 231 注册在册（表尾 W241 行·probe leg0 机证 238 行+W241 splice 落地后 239 行 live 单态如实注记）+本候选=bm-a 自有席自有波【live-derive face：席面 own-seat face（bm-a r995 席位 MSG-20261014-1814-bma-w242-seat·probe receipt _w242bma_20261014 机证·bands ADMIT verbatim·zero takeover）→freeze 时 live derive bma rows 123+候选=第 124 枚 EXACT·以 freeze 时 live derive 为准 r587/r359】【bm-a 循环班 r998 freeze 窗 2026-10-14 20:2x·CEO 填载令 standing+2026-10-10 ~23:1x RE-ISSUE+O-20260909-2334 本地满用令+O-20261013-2215 CPU 常开令】）'))

# S2 live-read round tag
A(('saturation_engine.py status live-read r1003：burns_active=[] queue_next=[] 实读）',
   'saturation_engine.py status live-read r998：burns_active=[] queue_next=[] 实读）'))

# S3 wave-number + vacancy
A(('**波号 241=注册表 W240 席后首个自由号**【probe leg3 vacancy 机证（r1002 席位窗实跑：origin inbox/processed/ 零 W241 席位外机命中+origin perpetual_faces.py 零 241 行+origin perpetual_faces_n1.py 零 PERPETUAL-N1-W241 WAVE_CONFIGS+origin 零 PERPETUAL_N1_W241_PREREG.md 四查）',
   '**波号 242=注册表 W241 席后首个自由号**【probe leg3 vacancy 机证（r995 席位窗实跑：origin inbox/processed/ 零 W242 席位外机命中+origin perpetual_faces.py 零 242 行+origin perpetual_faces_n1.py 零 PERPETUAL-N1-W242 WAVE_CONFIGS+origin 零 PERPETUAL_N1_W242_PREREG.md 四查）'))

# S3b chain-tail append W241 completion entry
A(('+bm-a r993 finalize one-pass 已落（K=525,920·账本头 952,335 机读·n1_w240_results.json·17:3x）——本波上游链=W1..W240 finalize 全落地·零在飞上游席·干净前置**',
   '+bm-a r993 finalize one-pass 已落（K=525,920·账本头 952,335 机读·n1_w240_results.json·17:3x）+W241=bm-c r1002 席位+死窗 r1003 prereg derive（machine-SUB from frozen W240 tpl 22c6c3374·a9ab3b51d via bm-c r1004 estate absorb）+五面冻结 splice（8e980ce3e·死窗 18:40-19:28 chain estate 吸收落地）+引擎自燃 12/12+bm-c r1005/r1006 estate finalize one-pass 已落（K=528,120·账本头 954,535 机读·n1_w241_results.json·19:5x）——本波上游链=W1..W241 finalize 全落地·零在飞上游席·干净前置**'))

# S3c seat publication + zero-gap
A(('席位公示=MSG-20261014-1755-bmc-w241-seat 已推 origin 20782916a 先于本冻结【r565 律·席位先行·bm-c r1002 窗发布·本窗=自有席承接】；下游 W242+ 投影见 §5.5（probe 机证 leg4·W242 freezer 承接面）】。**单态零席位空档**：W2..W240 全注册在冻结时点成立',
   '席位公示=MSG-20261014-1814-bma-w242-seat 已推 origin 138a94745 先于本冻结【r565 律·席位先行·bm-a r995 窗发布·本窗=自有席承接】；下游 W243+ 投影见 §5.5（probe 机证 leg4·W243 freezer 承接面）】。**单态零席位空档**：W2..W241 全注册在冻结时点成立'))

# S4 L5 bands -- receipt path
A(('ADMIT 回执=results/_w241bmc_20261014_probe_receipt.json 五腿单窗 gate-合并单回执结构',
   'ADMIT 回执=results/_w242bma_20261014_probe_receipt.json 五腿单窗 gate-合并单回执结构'))

# S4a A-ext
A(('**A-ext seed=547_501..549_500**（**A 面=FIRST-CLEAN·hops=0 seed-decoupled A-continuation 形态**：A 面算术续带 547_501..549_500（自注册 W240 A 尾 547_500 续）在 post-W240 注册宇宙上起点即 CLEAN 零活点拒（W240 席位 leg4 投影兑现·连续第二个 seed-gap face·W240 A/B decoupled 承袭·probe leg1 A_semantics 机证）→ 保留 naive 落位 **hops=0**·**A base==前波 A 尾+1（547_500+1）机检关系**（fc_a==fc_a_naive·A_hop_chain=[] 空集 leg1 机证·A_clean_at_naive_start=true）·非转录 r587 前向单调断言在走册）',
   '**A-ext seed=549_501..551_500**（**A 面=FIRST-CLEAN·hops=0 seed-decoupled A-continuation 形态**：A 面算术续带 549_501..551_500（自注册 W241 A 尾 549_500 续）在 post-W241 注册宇宙上起点即 CLEAN 零活点拒（W241 席位 leg4 投影兑现·连续第三个 seed-gap face·W241 A/B decoupled 承袭·probe leg1 A_semantics 机证）→ 保留 naive 落位 **hops=0**·**A base==前波 A 尾+1（549_500+1）机检关系**（fc_a==fc_a_naive·A_hop_chain=[] 空集 leg1 机证·A_clean_at_naive_start=true）·非转录 r587 前向单调断言在走册）'))

# S4b B-ext
A(('**B-ext exit seed=541_004..541_203**（**B 面=FIRST-CLEAN·hops=0 seed-decoupled 形态承袭**：B 面 naive 续带 541_004..541_203（自注册 W240 B 尾 541_003 续）在注册宇宙上 CLEAN 且**不落本波 A 窗 547_501..549_500 内**（本波 A 高悬于 B 阶梯之上→**seed-decoupled A/B gap 承袭面**：同窗互斥面 leg2 律·W141 先例·B 无需 own-A reservation jump）→ B 保留 naive 落位 **hops=0**·**B base==前波 B 尾+1（541_003+1）机检关系**（fc_b==fc_b_naive·B_hop_chain=[] 空集 leg1 机证·B_no_ownA_jump=true·B_semantics seed-decoupled gap face third consecutive 回执在场）；**W240 席位 leg4 投影承接面注记兑现**：投影预言 W241 须在 post-W240 宇宙重 derive 且 A/B naive 双 CLEAN hops=0 如投影所期——本窗如实兑现·A 零活点拒=投影所期·B decoupled 保留=投影所期·已如实披露非分叉）',
   '**B-ext exit seed=541_204..541_403**（**B 面=FIRST-CLEAN·hops=0 seed-decoupled 形态承袭**：B 面 naive 续带 541_204..541_403（自注册 W241 B 尾 541_203 续）在注册宇宙上 CLEAN 且**不落本波 A 窗 549_501..551_500 内**（本波 A 高悬于 B 阶梯之上→**seed-decoupled A/B gap 承袭面**：同窗互斥面 leg2 律·W141 先例·B 无需 own-A reservation jump）→ B 保留 naive 落位 **hops=0**·**B base==前波 B 尾+1（541_203+1）机检关系**（fc_b==fc_b_naive·B_hop_chain=[] 空集 leg1 机证·B_no_ownA_jump=true·B_semantics seed-decoupled gap face fourth consecutive 回执在场）；**W241 席位 leg4 投影承接面注记兑现**：投影预言 W242 须在 post-W241 宇宙重 derive 且 A/B naive 双 CLEAN hops=0 如投影所期——本窗如实兑现·A 零活点拒=投影所期·B decoupled 保留=投影所期·已如实披露非分叉）'))

# S4c R250
A(('R250：W241 带从未指派', 'R250：W242 带从未指派'))

# S4d seed gate
A(('A base=547501 span=2000 checked=2000 verdict=FREE / B base=541004 span=200 checked=200 verdict=FREE',
   'A base=549501 span=2000 checked=2000 verdict=FREE / B base=541204 span=200 checked=200 verdict=FREE'))

# S4e scan face
A(('扫描面=pre-W241 全二百三十八行注册 N1 带表（表尾 W240 行·freeze 窗 live derive 238 行单态 owner rows 230——席位窗 probe leg0 实测 237 行+W240 splice 落地后 +1 如实注记）',
   '扫描面=pre-W242 全二百三十九行注册 N1 带表（表尾 W241 行·freeze 窗 live derive 239 行单态 owner rows 231——席位窗 probe leg0 实测 238 行+W241 splice 落地后 +1 如实注记）'))

# S5 L8 reuse-domain (3 pairs)
A(('（W2..W240 落地 runner 的 wave 参数化复用', '（W2..W241 落地 runner 的 wave 参数化复用'))
A(('selftest W241 face 将随五面冻结落地验证', 'selftest W242 face 将随五面冻结落地验证'))
A(('本件与 results/_w241bmc_freeze_edits.py（五面冻结拼接脚本·按 _w240bma_freeze_edits.py 模板派生·gate0.5 自查 W240 行+W240 finalize 件在场·未落即 loud abort·estate 提取面=本机 W240 块物理字节〔结构已知〕）=freeze-prep 束同窗落地（r993/W240 先例 freeze-prep 同式·本窗上游已全落=执行窗即 freeze 窗）',
   '本件与 results/_w242bma_freeze_edits.py（五面冻结拼接脚本·按 _w241bmc_freeze_edits.py 模板派生·gate0.5 自查 W241 行+W241 finalize 件在场·未落即 loud abort·estate 提取面=本机 W241 块物理字节〔结构已知〕）=freeze-prep 束同窗落地（r1005/W241 先例 freeze-prep 同式·本窗上游已全落=执行窗即 freeze 窗）'))

# S6 L11 batch identity (3 pairs)
A(('- 批名=**PERPETUAL-N1-W241**。', '- 批名=**PERPETUAL-N1-W242**。'))
A(('**W1..W240 N1 finalize 已全部落地**【净账本锚头 **952,335**·K=525,920 合并池·n1_w240_results.json 机读·W240 finalize one-pass bm-a r993 窗 17:3x（W240 面完整性=12/12 shards consumed+finalize audit finalize_only=true 收口·splice dc27f5217 死窗遗产吸收+引擎自燃链如实注记）】',
   '**W1..W241 N1 finalize 已全部落地**【净账本锚头 **954,535**·K=528,120 合并池·n1_w241_results.json 机读·W241 finalize one-pass bm-c r1005/r1006 estate 窗 19:5x（W241 面完整性=12/12 shards consumed+finalize audit finalize_only=true 收口·splice 8e980ce3e 死窗遗产吸收+引擎自燃链如实注记）】'))
A(('累计 null 池=525,920+2,200（本波）=**528,120 投影**',
   '累计 null 池=528,120+2,200（本波）=**530,320 投影**'))

# S7 L12 claim (3 pairs)
A(('（席位公示=MSG-20261014-1755-bmc-w241-seat 已推 origin 20782916a r565 律（bm-c r1002 席·bm-c 自有席承接）·probe W242+ 投影 A 549_501..551_500 / B 541_204..541_403 **双面 CLEAN hops=0 预披露+seed-gap 承袭注记**（投影 A naive 549_501..551_500 CLEAN 零活点拒·hops=0；投影 B naive 541_204..541_403 CLEAN hops=0 不落投影 A 窗内——**seed-gap 承袭 face：W241 A/B 仍 decoupled〔A 547_501..549_500 高悬于 B 541_004..541_203 之上〕·W242 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace·W241 B 带将拒 naive W242 A 窗仅当重叠——**W242 freezer 承接面强制注记：须在 post-W241 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**））',
   '（席位公示=MSG-20261014-1814-bma-w242-seat 已推 origin 138a94745 r565 律（bm-a r995 席·bm-a 自有席承接）·probe W243+ 投影 A 551_501..553_500 / B 541_404..541_603 **A CLEAN hops=0+B hops=1 拒带面预披露**（投影 A naive 551_501..553_500 CLEAN 零活点拒·hops=0；投影 B naive 541_404..541_603 **hops=1 拒带面**——541_404..541_603 窗内被 SEED_REGISTRY 活点 541_500（perpetual_n2_w15_gen）拒→诚实前行走 first-clean 541_501..541_700·逐跳在 probe 回执 leg4——**seed-gap 承袭 face：W242 A/B 仍 decoupled〔A 549_501..551_500 高悬于 B 541_204..541_403 之上〕·W243 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace·W242 B 带将拒 naive W243 A 窗仅当重叠——**W243 freezer 承接面强制注记：须在 post-W242 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**））'))
A(('T-2026-10-01-141 s1 引擎线第 231 波【bm-c 第六十七枚自有波【机面 derive：probe leg0 bmc_rows=66 attempt-continuity face（r1002 窗算法·bm-c own seat+bmc live rows 66 实读）——freeze 时 live derive bmc rows 66+候选=第 67 枚 EXACT（以 freeze 时 live derive 为准 r587/r359）】】',
   'T-2026-10-01-141 s1 引擎线第 232 波【bm-a 第一百二十四枚自有波【机面 derive：probe leg0 bma_rows=123 attempt-continuity face（r995 窗算法·bm-a own seat+bma live rows 123 实读）——freeze 时 live derive bma rows 123+候选=第 124 枚 EXACT（以 freeze 时 live derive 为准 r587/r359）】】'))
A(('（波号=注册表 W240 席后首个自由号·单态零席位空档于冻结时点成立；席位公示 MSG-20261014-1755-bmc-w241-seat 先推 origin 20782916a r565 律；lane-free；dept:研究）',
   '（波号=注册表 W241 席后首个自由号·单态零席位空档于冻结时点成立；席位公示 MSG-20261014-1814-bma-w242-seat 先推 origin 138a94745 r565 律；lane-free；dept:研究）'))

# S8 L13 RAM face (live read)
A(('**RAM face 如实注记：本窗 free RAM ~1.8GB（bm-c 底盘常驻·24G 物理内存机·MV wave2 runner 烧制线在飞〔O-20261014-1125 GPU 生成视觉-only 律〕+CPU 车道独立如实注记）——N1 引擎点火无 RAM 硬闸（W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230/W231/W232/W233/W234/W235/W236/W237/W238/W239/W240 低 RAM 实烧先例·W240 冻结窗 33.2G bm-a 实锚·W239 冻结窗 1.0G bm-c 实锚·W238 冻结窗 70.1G bm-a 实锚·W237 冻结窗 1.6G 实锚族·W236 席位窗 1.9G/0.2G 实锚族）·burn 由引擎 RAM 面随 cycle 上报自判·本件不代引擎决策。**',
   f'**RAM face 如实注记：本窗 free RAM ~{ram_free_gb:.1f}GB（bm-a 底盘常驻·94G 物理内存机·MV V3 装配站盯守线=导演席窗在飞〔O-20261014-1035 §4〕+CPU 车道独立如实注记）——N1 引擎点火无 RAM 硬闸（W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230/W231/W232/W233/W234/W235/W236/W237/W238/W239/W240/W241 低 RAM 实烧先例·W241 冻结窗 1.8G bm-c 实锚·W240 冻结窗 33.2G bm-a 实锚·W239 冻结窗 1.0G bm-c 实锚·W238 冻结窗 70.1G bm-a 实锚·W237 冻结窗 1.6G 实锚族·W236 席位窗 1.9G/0.2G 实锚族）·burn 由引擎 RAM 面随 cycle 上报自判·本件不代引擎决策。**'))

# S9 L14 materialization (2 pairs)
A(('engine_owner==bm-c 波的未烧分片=本地队列项', 'engine_owner==bm-a 波的未烧分片=本地队列项'))
A(('复烧自见 W241 行并点火自烧', '复烧自见 W242 行并点火自烧'))

# S10 L19 gate path
A(('--prereg research/PERPETUAL_N1_W241_PREREG.md', '--prereg research/PERPETUAL_N1_W242_PREREG.md'))

# S11 L20 manual pre-read
A(('p2_calibration v1/v2 canon；v1 ext；v2..W240 落地）', 'p2_calibration v1/v2 canon；v1 ext；v2..W241 落地）'))

# S12 L31 A-tier
A(('- **A 档**（j=0..1,999）：entry rng seed=**547_501+j**（法典 §4 W241 行 A=547_501..549_500·**FIRST-CLEAN·hops=0 seed-decoupled A-continuation 形态**：A 算术续带 547_501..549_500（自注册 W240 A 尾 547_500 续）在 post-W240 注册宇宙上起点即 CLEAN 零活点拒（W240 席位 leg4 投影兑现·连续第二个 seed-gap face·W240 A/B decoupled 承袭）→保留 naive 落位 hops=0·**A base==前波 A 尾+1（547_500+1）机检关系**（fc_a==fc_a_naive·A_hop_chain=[] 空集 probe leg1 机证·A_clean_at_naive_start=true）·非转录 r587·ADMIT 回执在场）',
   '- **A 档**（j=0..1,999）：entry rng seed=**549_501+j**（法典 §4 W242 行 A=549_501..551_500·**FIRST-CLEAN·hops=0 seed-decoupled A-continuation 形态**：A 算术续带 549_501..551_500（自注册 W241 A 尾 549_500 续）在 post-W241 注册宇宙上起点即 CLEAN 零活点拒（W241 席位 leg4 投影兑现·连续第三个 seed-gap face·W241 A/B decoupled 承袭）→保留 naive 落位 hops=0·**A base==前波 A 尾+1（549_500+1）机检关系**（fc_a==fc_a_naive·A_hop_chain=[] 空集 probe leg1 机证·A_clean_at_naive_start=true）·非转录 r587·ADMIT 回执在场）'))

# S13 L32 B-tier
A(('- **B 档**（j=0..199）：entry rng=**547_501+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**541_004+j**（法典 §4 W241 行 B=541_004..541_203·**FIRST-CLEAN·hops=0 seed-decoupled 形态承袭**：B 算术续带 541_004..541_203（自注册 W240 B 尾 541_003 续）在注册宇宙 CLEAN 且不落本波 A 窗 547_501..549_500 内（本波 A 高悬于 B 阶梯之上→同窗互斥面 leg2 律·W141 先例·B 无需 own-A reservation jump）→保留走落 541_004..541_203·hops=0·**B base==前波 B 尾+1（541_003+1）机检关系**（fc_b==fc_b_naive·B_hop_chain=[] 空集 leg1 机证·B_no_ownA_jump=true·B_semantics seed-decoupled gap face third consecutive 回执在场）·非转录 r587·与 W240 席位 leg4 投影承接面注记兑现收敛·ADMIT 回执在场）',
   '- **B 档**（j=0..199）：entry rng=**549_501+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**541_204+j**（法典 §4 W242 行 B=541_204..541_403·**FIRST-CLEAN·hops=0 seed-decoupled 形态承袭**：B 算术续带 541_204..541_403（自注册 W241 B 尾 541_203 续）在注册宇宙 CLEAN 且不落本波 A 窗 549_501..551_500 内（本波 A 高悬于 B 阶梯之上→同窗互斥面 leg2 律·W141 先例·B 无需 own-A reservation jump）→保留走落 541_204..541_403·hops=0·**B base==前波 B 尾+1（541_203+1）机检关系**（fc_b==fc_b_naive·B_hop_chain=[] 空集 leg1 机证·B_no_ownA_jump=true·B_semantics seed-decoupled gap face fourth consecutive 回执在场）·非转录 r587·与 W241 席位 leg4 投影承接面注记兑现收敛·ADMIT 回执在场）'))

# S14 L36 disjoint + estate family (5 pairs)
A(('种子带 disjoint 全例（selftest 强制）：W241 带与 v1 在用带', '种子带 disjoint 全例（selftest 强制）：W242 带与 v1 在用带'))
A(('W2..W240 带（冻结时点全注册单态）', 'W2..W241 带（冻结时点全注册单态）'))
A(('本波机验 ADMIT 回执在场=_w241bmc_20261014 探针窗', '本波机验 ADMIT 回执在场=_w242bma_20261014 探针窗'))
A(('selftest W241 face（A=first-clean past prior-wave B+live-seeds 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W240 行 parity 腿',
   'selftest W242 face（A=first-clean past prior-wave B+live-seeds 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W241 行 parity 腿'))
A(('从**本机 W240 块物理字节**提取（结构已知·提取自证断言 69 行 range 恒等在场）——W239 块的 W238 leg（1 行）不入 estate 路径·提取后新增 W239+W240 leg 构成 W241 块 parity 99 行（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232+W233+W234+W235+W236+W237+W238+W239+W240）·零假设零风险。',
   '从**本机 W241 块物理字节**提取（结构已知·提取自证断言 69 行 range 恒等在场）——W240 块的 W239 leg（1 行）不入 estate 路径·提取后新增 W240+W241 leg 构成 W242 块 parity 100 行（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232+W233+W234+W235+W236+W237+W238+W239+W240+W241）·零假设零风险。'))

# S15 L39 ledger
A(('batch_name="PERPETUAL-N1-W241", batch_trials=2200, file_name="results/perpetual_faces/n1_w241_results.json"',
   'batch_name="PERPETUAL-N1-W242", batch_trials=2200, file_name="results/perpetual_faces/n1_w242_results.json"'))

# S16 L38 merged-pool live flow
A(('（起草窗实流 W1..W240 已落账 525,920 实测·derive 禁手抄）',
   '（起草窗实流 W1..W241 已落账 528,120 实测·derive 禁手抄）'))

# S17 L44 preamble
A(('（起草窗实况注记：**W1..W240 N1 finalize 已全部落地**——净账本锚头 952,335·**K=525,920 合并池**·**零在飞上游席——本波 §5 预测键=**W240 实测值**【results/perpetual_faces/n1_w240_results.json·N1 面最新已落账键·17:3x finalize one-pass】。',
   '（起草窗实况注记：**W1..W241 N1 finalize 已全部落地**——净账本锚头 954,535·**K=528,120 合并池**·**零在飞上游席——本波 §5 预测键=**W241 实测值**【results/perpetual_faces/n1_w241_results.json·N1 面最新已落账键·19:5x finalize one-pass】。'))

# S18 key1
A(('1. W241-only mu 与累计池 merged mu（W240 实测键 **−0.09276493**·K=525,920 合并池·W240-only 实测 **−0.10033100**）差异 **|Δ|<0.02**（W2..W240 共二百三十八面实测 mu 稳定先例·单波跨键微；W240-only vs merged 实差 0.0076 在带内）。',
   f'1. W242-only mu 与累计池 merged mu（W241 实测键 **{mu_s}**·K=528,120 合并池·W241-only 实测 **{wmu_s}**）差异 **|Δ|<0.02**（W2..W241 共二百三十九面实测 mu 稳定先例·单波跨键微；W241-only vs merged 实差 {delta_s} 在带内）。'))

# S19 key2
A(('2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.24510199**=W240 合并池实测）。',
   f'2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **{sigma_s}**=W241 合并池实测）。'))

# S20 key3
A(('3. A 档 full_sharpe_p95 与 W240 A 档 p95（**0.3160** 实测锚）差 **<0.05**（门标注法 W5..W240 先例：结果知情面仅作机器断言之用·测量面非注册收益）。利益）。',
   f'3. A 档 full_sharpe_p95 与 W241 A 档 p95（**{a_p95:.4f}** 实测锚）差 **<0.05**（门标注法 W5..W241 先例：结果知情面仅作机器断言之用·测量面非注册收益）。利益）。'))

# S21 key4 (2 pairs)
A(('W136..W240 先例链披露【各波 K-lift 全在 ±0.0003 内·机读可复核·键 W240 实测 K-lift **+0.0000**·line_merged@K525,920 **1.1932**·line_pre_w240 1.1932·n_eff_held_equal 950,135；',
   'W136..W241 先例链披露【各波 K-lift 全在 ±0.0003 内·机读可复核·键 W241 实测 K-lift **+0.0000**·line_merged@K528,120 **1.1933**·line_pre_w241 1.1933·n_eff_held_equal 952,335；'))
A(('→W238 **0.000339**→W239 **0.000339**→W240 **0.000338**】）。',
   '→W239 **0.000339**→W240 **0.000338**→W241 **0.000337**】）。'))

# S22 key5 W243 projection (full sentence swap)
A(('5. **W242+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 549_501..551_500 **CLEAN**（hops=0·pre-W241 宇宙零活点拒）；B naive first-clean **541_204..541_403 CLEAN**（hops=0·**不落投影 A 窗内**——B_hop lands-inside-A=false 腿在场）；**W241 B 带 541_004..541_203 注册后将拒 naive W242 A 窗仅当重叠**（**seed-gap 承袭 face：W241 A/B 仍 decoupled〔A 547_501..549_500 高悬于 B 541_004..541_203 之上〕·W242 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace**）——W242 冻结方必须在 post-W241 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡·W141 先例；verify at W242 prereg, hop 链逐跳在 probe 回执。',
   '5. **W243+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 551_501..553_500 **CLEAN**（hops=0·pre-W242 宇宙零活点拒）；B naive first-clean **541_404..541_603 hops=1 拒带面**（541_404..541_603 窗内被 SEED_REGISTRY 活点 **541_500**（perpetual_n2_w15_gen）拒→诚实前行走 first-clean **541_501..541_700**·**不落投影 A 窗内**——B_hop lands-inside-A=false 腿在场）；**W242 B 带 541_204..541_403 注册后将拒 naive W243 A 窗仅当重叠**（**seed-gap 承袭 face：W242 A/B 仍 decoupled〔A 549_501..551_500 高悬于 B 541_204..541_403 之上〕·W243 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace**）——W243 冻结方必须在 post-W242 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡·W141 先例；verify at W243 prereg，hop 链逐跳在 probe 回执。'))

# S23 runner (2 pairs)
A(('--wave 241/finalize --wave 241', '--wave 242/finalize --wave 242'))
A(('【n1_w241/ 分片计数增长', '【n1_w242/ 分片计数增长'))

# S24 deliverables (2 pairs)
A(('results/p2cal_ext/n1_w241/shard-<k>-of-12.json', 'results/p2cal_ext/n1_w242/shard-<k>-of-12.json'))
A(('`results/perpetual_faces/n1_w241_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 键序前置=**起草窗零在飞上游席（W1..W240 全落）',
   '`results/perpetual_faces/n1_w242_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 键序前置=**起草窗零在飞上游席（W1..W241 全落）'))

# S25 engine ledger
A(('engine_owner==bm-c 66 行注册〔冻结时点〕', 'engine_owner==bm-a 123 行注册〔冻结时点〕'))

# S26/S27 §7/§8 placeholders
A(('——bm-a r993 W240 §7 范式）', '——bm-c r1005 W241 §7 范式）'))
A(('（占位·finalize 同窗回填：§5.5 W242+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——bm-a r993 W240 §8 范式）',
   '（占位·finalize 同窗回填：§5.5 W243+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——bm-c r1005 W241 §8 范式）'))

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
FORBID = ['PERPETUAL-N1-W241', 'n1_w241/shard', '547501', '541004', '547_501', '541_004',
          'engine_owner 行 230', '池第 239 枚', 'bmc rows 66', '第 67 枚', 'r1003 freeze 窗',
          '1755-bmc', 'W2..W240', 'W1..W240', 'v2..W240', 'W5..W240',
          'parity 99 行', '20782916a', '528,120 投影', '525,920+2,200',
          '共二百三十八面', '二百三十八行', 'engine_owner==bm-c 66', 'owner rows 230',
          '238 行 live', '0.09276493', '0.10033100', '0.24510199', '0.3160', '952,335·K=525,920',
          'third consecutive', '连续第二个 seed-gap', '第 231 波', 'r1002 席·bm-c 自有席承接',
          'engine_owner==bm-c 波的未烧分片', '复烧自见 W241 行']
residue = [f for f in FORBID if f in out]
assert not residue, 'forbidden residue: %s' % residue

# legal retained counts (calibrated against the frozen-template live counts:
# own-band literals x8 mirror the template's 8; wave-count faces mirror 1:1)
assert out.count('_w241bmc') == 1 and out.count('_w241bmc_freeze_edits.py') == 1   # freeze-edits template-source citation x1 (r587 lineage)
assert out.count('n1_w240_results.json') == 1                                       # chain-tail W240 completion entry
assert out.count('n1_w241_results.json') == 3                                       # chain-tail W241 append + S6 + S17 preamble
assert out.count('n1_w242_results.json') == 2                                       # ledger + deliverable
assert out.count('PERPETUAL-N1-W242') == 4, out.count('PERPETUAL-N1-W242')
assert out.count('PERPETUAL_N1_W242') == 2, out.count('PERPETUAL_N1_W242')          # vacancy check + gate path
assert 'n1_w242/shard' in out
assert out.count('549_501..551_500') == 8 and out.count('541_204..541_403') == 8   # own-band literals x8 each (mirror template count)
assert 'fourth consecutive' in out and out.count('fourth consecutive') == 2        # B-ext + S13 face (mirror template third-consecutive x2)
assert out.count('连续第三个 seed-gap') == 2                                       # A-ext + S12 face (mirror template 连续第二个 x2)
assert out.count('551_501..553_500') == 3 and out.count('541_501..541_700') == 2   # W243 projection (S7 x2 + S22 x1 / first-clean S7+S22)
assert '138a94745' in out and out.count('138a94745') == 3                          # own seat commit
assert '1814-bma' in out and out.count('1814-bma') == 4                            # own seat MSG
assert out.count('第 124 枚') == 2                                                 # bma ordinal (title + S7b)
assert out.count('954,535') == 3                                                    # net ledger head (S6 + chain append + S17)
assert out.count('952,335') == 2                                                    # chain-tail W240 entry + n_eff_held_equal
assert out.count('950,135') == 1                                                    # chain-tail W239 historical entry
assert '945,189' in out                                                            # chain-tail W237 historical head
assert '549501' in out and '541204' in out                                          # seed gate bare bases
assert out.count('owner rows 231') == 1 and out.count('engine_owner 行 231') == 1
assert out.count('238 行') == 2 and out.count('239 行') == 2
assert out.count('W2..W241') == 4 and out.count('W1..W241') == 5
assert out.count('v2..W241') == 1 and out.count('W5..W241') == 1
assert out.count('17:3x') == 1 and out.count('19:5x') == 4
assert out.count('第 232 波') == 1 and out.count('池第 240 枚') == 1
assert out.count('parity 100 行') == 1 and out.count('共二百三十九面') == 1 and out.count('二百三十九行') == 1
assert out.count('530,320 投影') == 1 and out.count('528,120+2,200') == 1
assert out.count('W242-inherit') == 0                                              # stale face never in prereg

with open(OUT_PATH, 'w', encoding='utf-8', newline='') as fh:
    fh.write(out)

receipt = {
    'derive': 'W242 prereg machine-generated SUB from frozen W241 template',
    'machine': 'bm-a', 'round': 'r998',
    'template_commit': TPL_COMMIT,
    'upstream_finalize_commit': FIN_COMMIT,
    'sub_pairs_applied': applied,
    'out_path': OUT_PATH,
    'out_bytes': len(out.encode('utf-8')),
    'facts': {
        'merged_mu': merged_mu, 'merged_sigma': merged_sigma,
        'w241_only_mu': w241_only_mu, 'w241_only_sigma': npc['w241_only']['sigma'],
        'a_p95': a_p95, 'se_mu_at_k': se_mu_at_k, 'k_lift': k_lift,
        'line_merged': line_merged, 'line_pre': line_pre, 'n_eff_held_equal': n_eff_he,
        'ledger_prev_total': prev_total, 'ledger_batch': batch_trials, 'ledger_total': total,
        'merged_K': merged_K,
        'n1_bands_rows': n_rows, 'owner_rows': owner_rows, 'bmc_rows': bmc_rows, 'bma_rows': bma_rows,
        'bands': {'A': [549501, 551500], 'B': [541204, 541403]},
        'ram_free_gb': ram_free_gb,
        'engine_status': {'burns_active': burns, 'queue_next': queue_next},
        'seed_hop_face': {'hops_A': leg1['hops_A'], 'A_hop_chain': leg1['A_hop_chain'],
                          'hops_B': leg1['hops_B'], 'b_decoupled': True},
        'w243p': {'refusers': leg4['W243p_A_naive_refusers_seeds'],
                  'first_clean': leg4['W243p_A_first_clean'], 'hops': leg4['hops_A'],
                  'B_naive': leg4['W243p_B_naive'], 'B_first_clean': leg4['W243p_B_first_clean'],
                  'B_hops': leg4['hops_B'], 'B_inside_A': leg4['W243p_B_lands_inside_W243p_A_naive']},
    },
    'forbidden_residue': residue,
}
json.dump(receipt, open('results/_w242bma_prereg_derive_receipt.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('W242 prereg derive OK: %d SUB pairs, out=%d bytes -> %s' % (applied, len(out.encode('utf-8')), OUT_PATH))
print('facts: n1_bands=%d rows owner_rows=%d bmc=%d bma=%d ram_free=%.1fG' % (n_rows, owner_rows, bmc_rows, bma_rows, ram_free_gb))
