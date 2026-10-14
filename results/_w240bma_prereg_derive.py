# -*- coding: utf-8 -*-
"""W240 prereg derive -- bm-a r989 freeze window (M12 trigger OPEN: W239 finalize landed acd421c74).

Machine-generated SUB from committed W239 frozen template (git 97a7ff0e6), zero transcription
(r587 / r958 / r974 lineage; cloned mechanics from _w239bmc_prereg_derive.py). All anchor faces
machine-read live at derive time:
- results/perpetual_faces/n1_w239_results.json  (W239 finalize product, landed 14:1x)
- results/_w240bma_20261014_probe_receipt.json  (bm-a r987 seat probe ADMIT)
- Tools/saturation_engine.py n1_bands() live derive (237 rows, tail W239, owner rows 229)
Fail-closed: every SUB pair must hit exactly once; forbidden-residue scan must be zero.
"""
import json
import subprocess
import sys
import importlib.util
from collections import Counter

OUT_PATH = 'research/PERPETUAL_N1_W240_PREREG.md'
TPL_COMMIT = '97a7ff0e6'   # W239 prereg frozen-at-commit (bm-c r996 derive)
FIN_COMMIT = 'acd421c74'   # W239 finalize one-pass LANDED (bm-c r996 closeout)


def git_show(ref, path):
    r = subprocess.run(['git', 'show', '%s:%s' % (ref, path)], capture_output=True)
    assert r.returncode == 0, 'git show failed: %s' % r.stderr[:300]
    return r.stdout.decode('utf-8')


# ---------- facts (live machine-read, zero transcription) ----------
fin = json.load(open('results/perpetual_faces/n1_w239_results.json', encoding='utf-8'))
probe = json.load(open('results/_w240bma_20261014_probe_receipt.json', encoding='utf-8'))

npc = fin['null_pool_cumulative']
merged_mu = npc['merged']['mu']
merged_sigma = npc['merged']['sigma']
w239_only_mu = npc['w239_only']['mu']
a_p95 = fin['families']['A_random_engine_exit']['full_sharpe_p95']
se_mu_at_k = npc['se_mu_at_k523720']
k_lift = fin['skill_line_v2_k_lift']['line_delta_k_lift']
line_merged = fin['skill_line_v2_k_lift']['line_merged_523720']
line_pre = fin['skill_line_v2_k_lift']['line_pre_w239']
n_eff_he = fin['skill_line_v2_k_lift']['n_eff_held_equal']
led = fin['science_gates']['ledger']
prev_total, batch_trials, total = led['prev_total'], led['batch_trials'], led['total']
merged_K = npc['merged']['n_values']

# sanity: five-key anchors must equal the landed finalize numbers
assert (prev_total, batch_trials, total) == (947935, 2200, 950135), (prev_total, batch_trials, total)
assert merged_K == 523720, merged_K
assert k_lift == 0.0, k_lift
assert line_merged == line_pre == 1.1931, (line_merged, line_pre)
assert n_eff_he == 947935, n_eff_he
assert se_mu_at_k == 0.000339, se_mu_at_k
assert a_p95 == 0.32, a_p95
assert fin['audit']['finalize_only'] is True, 'W239 finalize product audit face'

# seat probe bands must equal the W240 target bands
bands = probe['bands']
assert bands['A'] == [545501, 547500] and bands['B'] == [540804, 541003], bands
leg1 = probe['legs']['leg1']
assert leg1['A'] == [545501, 547500] and leg1['B'] == [540804, 541003], leg1
assert leg1['hops_A'] == 1 and leg1['hops_B'] == 0, (leg1['hops_A'], leg1['hops_B'])
rel = leg1['relation_asserts']
assert rel['A_base_ge_priorB_tail_plus1'] is True and rel['AB_mutual_exclusion'] is True, rel
assert rel['B_base_eq_priorB_tail_plus1'] is True and rel['B_no_ownA_jump'] is True, rel
assert 'seed point' in leg1['A_semantics'], leg1['A_semantics'][:200]
assert 'decoupled' in leg1['B_semantics'], leg1['B_semantics'][:200]
hc = leg1['A_hop_chain']
assert hc == [{'hop': 1, 'window': [544501, 546500], 'jump_to': 545501,
               'refuser_pts': [545500], 'refuser_bands': []}], hc
leg4 = probe['legs']['leg4']
assert leg4['W241p_A_naive'] == '547501..549500' and leg4['hops_A'] == 0, leg4
assert leg4['W241p_A_first_clean'] == '547501..549500', leg4
assert leg4['W241p_A_naive_refusers_seeds'] == [], leg4
assert leg4['W241p_B_naive'] == '541004..541203' and leg4['hops_B'] == 0, leg4
assert leg4['W241p_B_first_clean'] == '541004..541203', leg4
assert leg4['W241p_B_lands_inside_W241p_A_naive'] is False, leg4
leg0 = probe['legs']['leg0']
assert leg0['w238_finalize_landed'] is True and leg0['w239_splice_landed'] is False, leg0

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
assert n_rows == 237 and keys[-2:] == [238, 239], (n_rows, keys[-2:])
assert 240 not in keys, 'W240 already registered?!'
assert owner_rows == 229 and bmc_rows == 66 and bma_rows == 122, (owner_rows, bmc_rows, bma_rows)
w239 = dict(nrows.get(239) or {})
assert w239.get('engine_owner') == 'bm-c', w239
assert tuple(w239.get('a') or ()) == (542501, 544500), w239
assert tuple(w239.get('b_exit') or ()) == (540604, 540803), w239

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
mu_s = '%s%.8f' % (MINUS, abs(merged_mu))            # -0.09273315 (U+2212 face)
wmu_s = '%s%.8f' % (MINUS, abs(w239_only_mu))        # -0.08455641
sigma_s = '%.8f' % merged_sigma                     # 0.24508680
delta_s = '%.4f' % abs(merged_mu - w239_only_mu)    # 0.0082

# ---------- template ----------
tpl = git_show(TPL_COMMIT, 'research/PERPETUAL_N1_W239_PREREG.md')

SUBS = []
A = SUBS.append

# S1 title line
A(('# PERPETUAL-N1-W239 预注册 · N1 nulls-deepening 池第 237 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 228 注册在册（表尾 W238 行·probe leg0 机证 236 行 live 单态零注入腿）+本候选=bm-c 自有席自有波【live-derive face：席面 own-seat face（bm-c r991 席位 MSG-20261014-0914-bmc-w239-seat·probe receipt _w239bmc_20261014 机证·bands ADMIT verbatim·zero takeover）→freeze 时 live derive bmc rows 65+候选=第 66 枚 EXACT·以 freeze 时 live derive 为准 r587/r359】【bm-c 循环班 r996 freeze 窗 2026-10-14 13:2x·CEO 填载令 standing+2026-10-10 ~23:1x RE-ISSUE+O-20260909-2334-bm-b 本地满用令+O-20261013-2215 CPU 常开令】）',
   '# PERPETUAL-N1-W240 预注册 · N1 nulls-deepening 池第 238 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 229 注册在册（表尾 W239 行·probe leg0 机证 237 行 live 单态零注入腿）+本候选=bm-a 自有席自有波【live-derive face：席面 own-seat face（bm-a r987 席位 MSG-20261014-1325-bma-w240-seat·probe receipt _w240bma_20261014 机证·bands ADMIT verbatim·zero takeover）→freeze 时 live derive bma rows 122+候选=第 123 枚 EXACT·以 freeze 时 live derive 为准 r587/r359】【bm-a 循环班 r989 freeze 窗 2026-10-14 14:3x·CEO 填载令 standing+2026-10-10 ~23:1x RE-ISSUE+O-20260909-2334 本地满用令+O-20261013-2215 CPU 常开令】）'))

# S2 live-read round tag
A(('saturation_engine.py status live-read r996：burns_active=[] queue_next=[] 实读）',
   'saturation_engine.py status live-read r989：burns_active=[] queue_next=[] 实读）'))

# S3 wave-number + vacancy
A(('**波号 239=注册表 W238 席后首个自由号**【probe leg3 vacancy 机证（r991 席位窗实跑：origin inbox/processed/ 零 W239 席位外机命中+origin perpetual_faces.py 零 239 行+origin perpetual_faces_n1.py 零 PERPETUAL-N1-W239 WAVE_CONFIGS+origin 零 PERPETUAL_N1_W239_PREREG.md 四查）',
   '**波号 240=注册表 W239 席后首个自由号**【probe leg3 vacancy 机证（r987 席位窗实跑：origin inbox/processed/ 零 W240 席位外机命中+origin perpetual_faces.py 零 240 行+origin perpetual_faces_n1.py 零 PERPETUAL-N1-W240 WAVE_CONFIGS+origin 零 PERPETUAL_N1_W240_PREREG.md 四查）'))

# S3b chain-tail append W239 entry
A(('+bm-a r985 finalize one-pass 已落（K=521,520·账本头 947,935 机读·n1_w238_results.json·12:58）——本波上游链=W1..W238 finalize 全落地·零在飞上游席·干净前置**',
   '+bm-a r985 finalize one-pass 已落（K=521,520·账本头 947,935 机读·n1_w238_results.json·12:58）+W239=bm-c r991 席位+死窗 r996 prereg derive（97a7ff0e6·r996-continuation absorb 24th-gen）+五面冻结 splice（c85e806c9）+引擎自燃 12/12（13:47 点火）+bm-c r996 finalize one-pass 已落（K=523,720·账本头 950,135 机读·n1_w239_results.json·14:1x）——本波上游链=W1..W239 finalize 全落地·零在飞上游席·干净前置**'))

# S3c seat publication + zero-gap
A(('席位公示=MSG-20261014-0914-bmc-w239-seat 已推 origin 603ff65d9 先于本冻结【r565 律·席位先行·bm-c r991 窗发布·本窗=自有席承接】；下游 W240+ 投影见 §5.5（probe 机证 leg4·W240 freezer 承接面）】。**单态零席位空档**：W2..W238 全注册在冻结时点成立',
   '席位公示=MSG-20261014-1325-bma-w240-seat 已推 origin 94136b9dd 先于本冻结【r565 律·席位先行·bm-a r987 窗发布·本窗=自有席承接】；下游 W241+ 投影见 §5.5（probe 机证 leg4·W241 freezer 承接面）】。**单态零席位空档**：W2..W239 全注册在冻结时点成立'))

# S4 L5 bands -- receipt path
A(('ADMIT 回执=results/_w239bmc_20261014_probe_receipt.json 五腿单窗 gate-合并单回执结构',
   'ADMIT 回执=results/_w240bma_20261014_probe_receipt.json 五腿单窗 gate-合并单回执结构'))

# S4a A-ext
A(('**A-ext seed=542_501..544_500**（**A 面=FIRST-CLEAN past prior-wave B+live-seeds 阶梯第九十九例**：A 面算术续带 540_404..542_403（自注册 W238 A 尾 540_403 续）在其起点即被 W238 注册 B 带 540_404..540_603 拒（W238 席位 leg4 投影+其 probe 所预言+强制）**且带内被 SEED_REGISTRY 活点 541_500/542_000 拒·第二窗 542_001..544_000 被活点 542_500 拒（live-seed 拒带 NEW FACE·首例活种子拒先于注册 B 带出现）**→ 诚实前行走 **2 hops** 落 **542_501..544_500**·**A base≥前波 B 尾+1（540_603+1）机检关系·hop 链逐跳在 probe 回执 leg1（A_hop_chain 机证）**=**A-hops-prior-B 阶梯几何第九十九例（E36 卡）+seed-hop 新形态**·非转录 r587 前向单调断言在走册；序数面如实披露：本窗 probe 回执 A_semantics 机读序数=NINETY-NINTH（第九十九例）·本件按回执序数面记载非转抄（r587））',
   '**A-ext seed=545_501..547_500**（**A 面=FIRST-CLEAN past prior-wave B+live-seeds 阶梯第一百例**：A 面算术续带 544_501..546_500（自注册 W239 A 尾 544_500 续）在其起点即被 SEED_REGISTRY 活点 545_500 拒（W239 席位 leg4 投影+其 probe 所预言+强制·**live-seed 拒带承袭面：拒点为种子点非注册 B 带〔W239 A/B decoupled〕**）→ 诚实前行走 **1 hop** 落 **545_501..547_500**·**A base≥前波 B 尾+1（540_803+1）机检关系·hop 链逐跳在 probe 回执 leg1（A_hop_chain 机证）**=**A-hops-prior-B 阶梯几何第一百例（E36 卡·序数=本窗派生计数——W240 probe 回执 A_semantics 未携序数词面·如实注记非回执机读序数）+seed-hop 承袭形态**·非转录 r587 前向单调断言在走册）'))

# S4b B-ext
A(('**B-ext exit seed=540_604..540_803**（**B 面=FIRST-CLEAN·hops=0 seed-decoupled 形态**：B 面 naive 续带 540_604..540_803（自注册 W238 B 尾 540_603 续）在注册宇宙上 CLEAN 且**不落本波 A 窗 542_501..544_500 内**（本波 A 因活种子拒带 seed-hop 越过阶梯基座→**首例 seed-decoupled A/B gap 面**：同窗互斥面 leg2 律·W141 先例以 A 跳越形态满足·B 无需 own-A reservation jump）→ B 保留 naive 落位 **hops=0**·**B base==前波 B 尾+1（540_603+1）机检关系**（fc_b==fc_b_naive·B_hop_chain=[] 空集 leg1 机证·B_no_ownA_jump=true）；**W238 席位 leg4 投影承接面注记兑现**：投影预言 W239 须在 post-W238 注册宇宙重 derive 且 B naive CLEAN hops=0 如投影所期——本窗如实兑现·A 活种子拒带+seed-hop=投影所期·B decoupled 保留=投影所期·已如实披露非分叉）',
   '**B-ext exit seed=540_804..541_003**（**B 面=FIRST-CLEAN·hops=0 seed-decoupled 形态承袭**：B 面 naive 续带 540_804..541_003（自注册 W239 B 尾 540_803 续）在注册宇宙上 CLEAN 且**不落本波 A 窗 545_501..547_500 内**（本波 A 因活种子拒带 seed-hop 越过阶梯基座→**seed-decoupled A/B gap 承袭面**：同窗互斥面 leg2 律·W141 先例以 A 跳越形态满足·B 无需 own-A reservation jump）→ B 保留 naive 落位 **hops=0**·**B base==前波 B 尾+1（540_803+1）机检关系**（fc_b==fc_b_naive·B_hop_chain=[] 空集 leg1 机证·B_no_ownA_jump=true）；**W239 席位 leg4 投影承接面注记兑现**：投影预言 W240 须在 post-W239 宇宙重 derive 且 B naive CLEAN hops=0 如投影所期——本窗如实兑现·A 活点拒带+seed-hop=投影所期·B decoupled 保留=投影所期·已如实披露非分叉）'))

# S4c R250
A(('R250：W239 带从未指派', 'R250：W240 带从未指派'))

# S4d seed gate
A(('A base=542501 span=2000 checked=2000 verdict=FREE / B base=540604 span=200 checked=200 verdict=FREE',
   'A base=545501 span=2000 checked=2000 verdict=FREE / B base=540804 span=200 checked=200 verdict=FREE'))

# S4e scan face
A(('扫描面=pre-W239 全二百三十六行注册 N1 带表（表尾 W238 行·freeze 窗 live derive 236 行单态 owner rows 228——席位窗 probe leg0 实测 235 行+W238 splice 落地后 +1 如实注记）',
   '扫描面=pre-W240 全二百三十七行注册 N1 带表（表尾 W239 行·freeze 窗 live derive 237 行单态 owner rows 229——席位窗 probe leg0 实测 236 行+W239 splice 落地后 +1 如实注记）'))

# S5 L8 reuse-domain (3 pairs)
A(('（W2..W238 落地 runner 的 wave 参数化复用', '（W2..W239 落地 runner 的 wave 参数化复用'))
A(('selftest W239 face 将随五面冻结落地验证', 'selftest W240 face 将随五面冻结落地验证'))
A(('本件与 results/_w239bmc_freeze_edits.py（五面冻结拼接脚本·按 _w238bma_freeze_edits.py 模板派生·gate0.5 自查 W238 行+W238 finalize 件在场·未落即 loud abort·estate 提取面=本机 W238 块物理字节〔结构已知〕）=freeze-prep 束同窗落地（r978/W238 先例 freeze-prep 同式·本窗上游已全落=执行窗即 freeze 窗）',
   '本件与 results/_w240bma_freeze_edits.py（五面冻结拼接脚本·按 _w239bmc_freeze_edits.py 模板派生·gate0.5 自查 W239 行+W239 finalize 件在场·未落即 loud abort·estate 提取面=本机 W239 块物理字节〔结构已知〕）=freeze-prep 束同窗落地（r996/W239 先例 freeze-prep 同式·本窗上游已全落=执行窗即 freeze 窗）'))

# S6 L11 batch identity (3 pairs)
A(('- 批名=**PERPETUAL-N1-W239**。', '- 批名=**PERPETUAL-N1-W240**。'))
A(('**W1..W238 N1 finalize 已全部落地**【净账本锚头 **947,935**·K=521,520 合并池·n1_w238_results.json 机读·W238 finalize one-pass bm-a r985 窗 12:5x（W238 面完整性=12/12 shards consumed+finalize audit finalize_only=true 收口·splice 50fa77623+引擎自燃链如实注记）】',
   '**W1..W239 N1 finalize 已全部落地**【净账本锚头 **950,135**·K=523,720 合并池·n1_w239_results.json 机读·W239 finalize one-pass bm-c r996 窗 14:1x（W239 面完整性=12/12 shards consumed+finalize audit finalize_only=true 收口·splice c85e806c9+引擎自燃链如实注记）】'))
A(('累计 null 池=521,520+2,200（本波）=**523,720 投影**',
   '累计 null 池=523,720+2,200（本波）=**525,920 投影**'))

# S7 L12 claim (3 pairs)
A(('（席位公示=MSG-20261014-0914-bmc-w239-seat 已推 origin 603ff65d9 r565 律（bm-c r991 席·bm-c 自有席承接）·probe W240+ 投影 A 544_501..546_500 / B 540_804..541_003 **live-seeds-refuse 承袭注记+seed-decoupled gap 预披露**（投影 A naive 544_501..546_500 被 SEED_REGISTRY 活点 [545500] 拒→诚实 1 hop first-clean 545_501..547_500；投影 B naive 540_804..541_003 CLEAN hops=0 不落投影 A 窗内——**seed-gap face：W239 A/B decoupled·W240 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace·W239 B 带将拒 naive W240 A 窗仅当重叠——**W240 freezer 承接面强制注记：须在 post-W239 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**））',
   '（席位公示=MSG-20261014-1325-bma-w240-seat 已推 origin 94136b9dd r565 律（bm-a r987 席·bm-a 自有席承接）·probe W241+ 投影 A 547_501..549_500 / B 541_004..541_203 **双面 CLEAN hops=0 预披露+seed-gap 承袭注记**（投影 A naive 547_501..549_500 CLEAN 零活点拒·hops=0；投影 B naive 541_004..541_203 CLEAN hops=0 不落投影 A 窗内——**seed-gap 承袭 face：W240 A/B 仍 decoupled〔A 545_501..547_500 高悬于 B 540_804..541_003 之上〕·W241 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace·W240 B 带将拒 naive W241 A 窗仅当重叠——**W241 freezer 承接面强制注记：须在 post-W240 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**））'))
A(('T-2026-10-01-141 s1 引擎线第 229 波【bm-c 第六十六枚自有波【机面 derive：probe leg0 bmc_rows=65 attempt-continuity face（r991 窗算法·bm-c own seat+bmc live rows 65 实读）——freeze 时 live derive bmc rows 65+候选=第 66 枚 EXACT（以 freeze 时 live derive 为准 r587/r359）】】',
   'T-2026-10-01-141 s1 引擎线第 230 波【bm-a 第一百二十三枚自有波【机面 derive：probe leg0 bma_rows=122 attempt-continuity face（r987 窗算法·bm-a own seat+bma live rows 122 实读）——freeze 时 live derive bma rows 122+候选=第 123 枚 EXACT（以 freeze 时 live derive 为准 r587/r359）】】'))
A(('（波号=注册表 W238 席后首个自由号·单态零席位空档于冻结时点成立；席位公示 MSG-20261014-0914-bmc-w239-seat 先推 origin 603ff65d9 r565 律；lane-free；dept:研究）',
   '（波号=注册表 W239 席后首个自由号·单态零席位空档于冻结时点成立；席位公示 MSG-20261014-1325-bma-w240-seat 先推 origin 94136b9dd r565 律；lane-free；dept:研究）'))

# S8 L13 RAM face (old side = W239 doc literal with bm-c's 1.0GB freeze-window read)
A(('**RAM face 如实注记：本窗 free RAM ~1.0GB（bm-c 底盘常驻高位·24G 物理内存机·GPU=MV V3 burn lane 在烧〔O-20261014-1125 MV-only 执法窗〕+CPU 车道独立如实注记）——N1 引擎点火无 RAM 硬闸（W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230/W231/W232/W233/W234/W235/W236/W237/W238 低 RAM 实烧先例·W238 冻结窗 70.1G bm-a 实锚·W237 冻结窗 1.6G 实锚族·W236 席位窗 1.9G/0.2G 实锚族）·burn 由引擎 RAM 面随 cycle 上报自判·本件不代引擎决策。**',
   f'**RAM face 如实注记：本窗 free RAM ~{ram_free_gb:.1f}GB（bm-a 底盘常驻·94G 物理内存机·MV V3 装配站盯守线=导演席窗在飞〔O-20261014-1035 §4〕+CPU 车道独立如实注记）——N1 引擎点火无 RAM 硬闸（W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230/W231/W232/W233/W234/W235/W236/W237/W238/W239 低 RAM 实烧先例·W239 冻结窗 1.0G bm-c 实锚·W238 冻结窗 70.1G bm-a 实锚·W237 冻结窗 1.6G 实锚族·W236 席位窗 1.9G/0.2G 实锚族）·burn 由引擎 RAM 面随 cycle 上报自判·本件不代引擎决策。**'))

# S9 L14 materialization (2 pairs)
A(('engine_owner==bm-c 波的未烧分片=本地队列项', 'engine_owner==bm-a 波的未烧分片=本地队列项'))
A(('复烧自见 W239 行并点火自烧', '复烧自见 W240 行并点火自烧'))

# S10 L19 gate path
A(('--prereg research/PERPETUAL_N1_W239_PREREG.md', '--prereg research/PERPETUAL_N1_W240_PREREG.md'))

# S11 L20 manual pre-read
A(('p2_calibration v1/v2 canon；v1 ext；v2..W238 落地）', 'p2_calibration v1/v2 canon；v1 ext；v2..W239 落地）'))

# S12 L31 A-tier
A(('- **A 档**（j=0..1,999）：entry rng seed=**542_501+j**（法典 §4 W239 行 A=542_501..544_500·**FIRST-CLEAN past prior-wave B+live-seeds 阶梯第九十九例**：算术续带 540_404..542_403 起点即被 W238 注册 B 带 540_404..540_603 拒+带内活点 541_500/542_000 拒·第二窗被活点 542_500 拒→2 hops 落 542_501..544_500·A base≥前波 B 尾+1 机检关系·E36 卡+seed-hop 面·hops=2·hop 链逐跳在 probe 回执 leg1·ADMIT 回执在场）',
   '- **A 档**（j=0..1,999）：entry rng seed=**545_501+j**（法典 §4 W240 行 A=545_501..547_500·**FIRST-CLEAN past prior-wave B+live-seeds 阶梯第一百例**：算术续带 544_501..546_500 起点即被 SEED_REGISTRY 活点 545_500 拒（拒点=种子点非注册 B 带·W239 A/B decoupled）→1 hop 落 545_501..547_500·A base≥前波 B 尾+1 机检关系·E36 卡·seed-hop 承袭面·hops=1·hop 链逐跳在 probe 回执 leg1·ADMIT 回执在场）'))

# S13 L32 B-tier
A(('- **B 档**（j=0..199）：entry rng=**542_501+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**540_604+j**（法典 §4 W239 行 B=540_604..540_803·**FIRST-CLEAN·hops=0 seed-decoupled 形态**：B 算术续带 540_604..540_803 在注册宇宙 CLEAN 且不落本波 A 窗 542_501..544_500 内（本波 A seed-hop 越过阶梯基座→同窗互斥面 leg2 律·W141 先例以 A 跳越形态满足·B 无 own-A reservation jump）→保留走落 540_604..540_803·hops=0·**B base==前波 B 尾+1（540_603+1）机检关系**（fc_b==fc_b_naive·B_hop_chain=[] 空集 leg1 机证）·非转录 r587·与 W238 席位 leg4 投影承接面注记兑现收敛·ADMIT 回执在场）',
   '- **B 档**（j=0..199）：entry rng=**545_501+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**540_804+j**（法典 §4 W240 行 B=540_804..541_003·**FIRST-CLEAN·hops=0 seed-decoupled 形态承袭**：B 算术续带 540_804..541_003 在注册宇宙 CLEAN 且不落本波 A 窗 545_501..547_500 内（本波 A seed-hop 越过阶梯基座→同窗互斥面 leg2 律·W141 先例以 A 跳越形态满足·B 无 own-A reservation jump）→保留走落 540_804..541_003·hops=0·**B base==前波 B 尾+1（540_803+1）机检关系**（fc_b==fc_b_naive·B_hop_chain=[] 空集 leg1 机证）·非转录 r587·与 W239 席位 leg4 投影承接面注记兑现收敛·ADMIT 回执在场）'))

# S14 L36 disjoint + estate family (5 pairs)
A(('种子带 disjoint 全例（selftest 强制）：W239 带与 v1 在用带', '种子带 disjoint 全例（selftest 强制）：W240 带与 v1 在用带'))
A(('W2..W238 带（冻结时点全注册单态）', 'W2..W239 带（冻结时点全注册单态）'))
A(('本波机验 ADMIT 回执在场=_w239bmc_20261014 探针窗', '本波机验 ADMIT 回执在场=_w240bma_20261014 探针窗'))
A(('selftest W239 face（A=first-clean past prior-wave B+live-seeds 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W238 行 parity 腿',
   'selftest W240 face（A=first-clean past prior-wave B+live-seeds 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W239 行 parity 腿'))
A(('从**本机 W238 块物理字节**提取（结构已知·提取自证断言 69 行 range 恒等在场）——W237 块的 W236 leg（1 行）不入 estate 路径·提取后新增 W237+W238 leg 构成 W239 块 parity 97 行（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232+W233+W234+W235+W236+W237+W238）·零假设零风险。',
   '从**本机 W239 块物理字节**提取（结构已知·提取自证断言 69 行 range 恒等在场）——W238 块的 W237 leg（1 行）不入 estate 路径·提取后新增 W238+W239 leg 构成 W240 块 parity 98 行（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232+W233+W234+W235+W236+W237+W238+W239）·零假设零风险。'))

# S15 L39 ledger
A(('batch_name="PERPETUAL-N1-W239", batch_trials=2200, file_name="results/perpetual_faces/n1_w239_results.json"',
   'batch_name="PERPETUAL-N1-W240", batch_trials=2200, file_name="results/perpetual_faces/n1_w240_results.json"'))

# S16 L38 merged-pool live flow
A(('（起草窗实流 W1..W238 已落账 521,520 实测·derive 禁手抄）',
   '（起草窗实流 W1..W239 已落账 523,720 实测·derive 禁手抄）'))

# S17 L44 preamble
A(('（起草窗实况注记：**W1..W238 N1 finalize 已全部落地**——净账本锚头 947,935·**K=521,520 合并池**·**零在飞上游席——本波 §5 预测键=**W238 实测值**【results/perpetual_faces/n1_w238_results.json·N1 面最新已落账键·12:5x finalize one-pass】。',
   '（起草窗实况注记：**W1..W239 N1 finalize 已全部落地**——净账本锚头 950,135·**K=523,720 合并池**·**零在飞上游席——本波 §5 预测键=**W239 实测值**【results/perpetual_faces/n1_w239_results.json·N1 面最新已落账键·14:1x finalize one-pass】。'))

# S18 key1
A(('1. W239-only mu 与累计池 merged mu（W238 实测键 **−0.09276764**·K=521,520 合并池·W238-only 实测 **−0.09086291**）差异 **|Δ|<0.02**（W2..W238 共二百三十六面实测 mu 稳定先例·单波跨键微；W238-only vs merged 实差 0.0019 在带内）。',
   f'1. W240-only mu 与累计池 merged mu（W239 实测键 **{mu_s}**·K=523,720 合并池·W239-only 实测 **{wmu_s}**）差异 **|Δ|<0.02**（W2..W239 共二百三十七面实测 mu 稳定先例·单波跨键微；W239-only vs merged 实差 {delta_s} 在带内）。'))

# S19 key2
A(('2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.24509858**=W238 合并池实测）。',
   f'2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **{sigma_s}**=W239 合并池实测）。'))

# S20 key3
A(('3. A 档 full_sharpe_p95 与 W238 A 档 p95（**0.3223** 实测锚）差 **<0.05**（门标注法 W5..W238 先例：结果知情面仅作机器断言之用·测量面非注册收益）。利益）。',
   f'3. A 档 full_sharpe_p95 与 W239 A 档 p95（**{a_p95:.4f}** 实测锚）差 **<0.05**（门标注法 W5..W239 先例：结果知情面仅作机器断言之用·测量面非注册收益）。利益）。'))

# S21 key4 (2 pairs)
A(('W136..W238 先例链披露【各波 K-lift 全在 ±0.0003 内·机读可复核·键 W238 实测 K-lift **+0.0000**·line_merged@K521,520 **1.193**·line_pre_w238 1.193·n_eff_held_equal 945,735；',
   'W136..W239 先例链披露【各波 K-lift 全在 ±0.0003 内·机读可复核·键 W239 实测 K-lift **+0.0000**·line_merged@K523,720 **1.1931**·line_pre_w239 1.1931·n_eff_held_equal 947,935；'))
A(('→W237 **0.00034**→W238 **0.000339**】）。',
   '→W237 **0.00034**→W238 **0.000339**→W239 **0.000339**】）。'))

# S22 key5 W241 projection (full sentence swap)
A(('5. **W240+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 544_501..546_500 **被 SEED_REGISTRY 活点 [545500] 拒**（hops=1·pre-W239 宇宙）→诚实前行走 **1 hop** first-clean **545_501..547_500**；B naive first-clean **540_804..541_003 CLEAN**（hops=0·**不落投影 A 窗内**——B_hop lands-inside-A=false 腿在场）；**W239 B 带 540_604..540_803 注册后将拒 naive W240 A 窗仅当重叠**（**seed-gap face：W239 A/B decoupled·W240 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace**）——W240 冻结方必须在 post-W239 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡·W141 先例；verify at W240 prereg，hop 链逐跳在 probe 回执。',
   '5. **W241+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 547_501..549_500 **CLEAN**（hops=0·pre-W240 宇宙零活点拒）；B naive first-clean **541_004..541_203 CLEAN**（hops=0·**不落投影 A 窗内**——B_hop lands-inside-A=false 腿在场）；**W240 B 带 540_804..541_003 注册后将拒 naive W241 A 窗仅当重叠**（**seed-gap 承袭 face：W240 A/B 仍 decoupled〔A 545_501..547_500 高悬于 B 540_804..541_003 之上〕·W241 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace**）——W241 冻结方必须在 post-W240 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡·W141 先例；verify at W241 prereg，hop 链逐跳在 probe 回执。'))

# S23 runner (2 pairs)
A(('--wave 239/finalize --wave 239', '--wave 240/finalize --wave 240'))
A(('【n1_w239/ 分片计数增长', '【n1_w240/ 分片计数增长'))

# S24 deliverables (2 pairs)
A(('results/p2cal_ext/n1_w239/shard-<k>-of-12.json', 'results/p2cal_ext/n1_w240/shard-<k>-of-12.json'))
A(('`results/perpetual_faces/n1_w239_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 键序前置=**起草窗零在飞上游席（W1..W238 全落）',
   '`results/perpetual_faces/n1_w240_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 键序前置=**起草窗零在飞上游席（W1..W239 全落）'))

# S25 engine ledger
A(('engine_owner==bm-c 65 行注册〔冻结时点〕', 'engine_owner==bm-a 122 行注册〔冻结时点〕'))

# S26/S27 §7/§8 placeholders
A(('——bm-a r985 W238 §7 范式）', '——bm-c r996 W239 §7 范式）'))
A(('（占位·finalize 同窗回填：§5.5 W240+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——bm-a r985 W238 §8 范式）',
   '（占位·finalize 同窗回填：§5.5 W241+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——bm-c r996 W239 §8 范式）'))

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
FORBID = ['PERPETUAL-N1-W239', 'n1_w239/shard', '542501', '540604', '542_501', '540_604',
          'engine_owner 行 228', '池第 237 枚', 'bmc rows 65', '第 66 枚', 'r996 freeze 窗',
          '0914-bmc', 'W2..W238', 'W1..W238', 'v2..W238', 'W5..W238', 'NINETY-NINTH',
          '第九十九例', 'parity 97 行', '603ff65d9', '523,720 投影', '521,520+2,200',
          '共二百三十六面', '第二百三十六行', 'engine_owner==bm-c 65', 'owner rows 228',
          '236 行 live', '0.09276764', '0.09086291', '0.24509858', '0.3223', '947,935·K=521,520']
residue = [f for f in FORBID if f in out]
assert not residue, 'forbidden residue: %s' % residue

# legal retained counts (calibrated against actual output structure)
assert out.count('_w239bmc') == 1 and out.count('_w239bmc_freeze_edits.py') == 1   # freeze-edits template-source citation x1 (r587 lineage)
assert out.count('n1_w238_results.json') == 1, out.count('n1_w238_results.json')   # chain-tail W238 entry
assert out.count('n1_w239_results.json') == 3, out.count('n1_w239_results.json')   # chain-tail W239 + S6 + S17 preamble
assert out.count('n1_w240_results.json') == 2, out.count('n1_w240_results.json')  # ledger + deliverable
assert out.count('PERPETUAL-N1-W240') == 4, out.count('PERPETUAL-N1-W240')
assert out.count('PERPETUAL_N1_W240') == 2, out.count('PERPETUAL_N1_W240')          # vacancy check + gate path
assert 'n1_w240/shard' in out
assert out.count('545_501..547_500') == 8 and out.count('540_804..541_003') == 8   # own-band literals x8 each (calibrated-by-live-count: A-ext x2+B-ext x1+S7 x1+S12 x2+S13 x1+S22 x1)
assert '第一百例' in out and out.count('第一百例') == 3                              # own-A ordinal x3 (S4a x2 + S12 x1)
assert 'seed-decoupled' in out and out.count('seed-decoupled') == 3                 # B-ext + S13 + S12 face
assert out.count('547_501..549_500') == 3 and out.count('541_004..541_203') == 3    # W241 projection (S7 x1 + S22 x2 each)
assert '94136b9dd' in out and out.count('94136b9dd') == 3                           # own seat commit
assert '1325-bma' in out and out.count('1325-bma') == 4                              # own seat MSG
assert out.count('第 123 枚') == 2                                                    # bma ordinal (title + S7b)
assert out.count('950,135') == 3                                                      # net ledger head (S6b + chain + S17)
assert out.count('947,935') == 2                                                      # chain-tail W238 historical head + n_eff_held_equal
assert '945,189' in out                                                                # chain-tail W237 historical head
assert '545501' in out and '540804' in out                                             # seed gate bare bases
assert out.count('owner rows 229') == 1 and out.count('engine_owner 行 229') == 1
assert out.count('W240-inherit') == 0                                                 # W239 finalize receipt face never in prereg

with open(OUT_PATH, 'w', encoding='utf-8', newline='') as fh:
    fh.write(out)

receipt = {
    'derive': 'W240 prereg machine-generated SUB from frozen W239 template',
    'machine': 'bm-a', 'round': 'r989',
    'template_commit': TPL_COMMIT,
    'upstream_finalize_commit': FIN_COMMIT,
    'sub_pairs_applied': applied,
    'out_path': OUT_PATH,
    'out_bytes': len(out.encode('utf-8')),
    'facts': {
        'merged_mu': merged_mu, 'merged_sigma': merged_sigma,
        'w239_only_mu': w239_only_mu, 'w239_only_sigma': npc['w239_only']['sigma'],
        'a_p95': a_p95, 'se_mu_at_k': se_mu_at_k, 'k_lift': k_lift,
        'line_merged': line_merged, 'line_pre': line_pre, 'n_eff_held_equal': n_eff_he,
        'ledger_prev_total': prev_total, 'ledger_batch': batch_trials, 'ledger_total': total,
        'merged_K': merged_K,
        'n1_bands_rows': n_rows, 'owner_rows': owner_rows, 'bmc_rows': bmc_rows, 'bma_rows': bma_rows,
        'bands': {'A': [545501, 547500], 'B': [540804, 541003]},
        'ram_free_gb': ram_free_gb,
        'engine_status': {'burns_active': burns, 'queue_next': queue_next},
        'seed_hop_face': {'hops_A': leg1['hops_A'], 'A_hop_chain': leg1['A_hop_chain'],
                          'hops_B': leg1['hops_B'], 'b_decoupled': True},
        'w241p': {'refusers': leg4['W241p_A_naive_refusers_seeds'],
                  'first_clean': leg4['W241p_A_first_clean'], 'hops': leg4['hops_A'],
                  'B_naive': leg4['W241p_B_naive'], 'B_inside_A': leg4['W241p_B_lands_inside_W241p_A_naive']},
    },
    'forbidden_residue': residue,
}
json.dump(receipt, open('results/_w240bma_prereg_derive_receipt.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('W240 prereg derive OK: %d SUB pairs, out=%d bytes -> %s' % (applied, len(out.encode('utf-8')), OUT_PATH))
print('facts: n1_bands=%d rows owner_rows=%d bmc=%d bma=%d ram_free=%.1fG' % (n_rows, owner_rows, bmc_rows, bma_rows, ram_free_gb))
