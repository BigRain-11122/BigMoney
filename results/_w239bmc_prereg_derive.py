# -*- coding: utf-8 -*-
"""W239 prereg derive -- bm-c r996 freeze window (M12 trigger OPEN: W238 finalize landed f597934fa).

Machine-generated SUB from committed W238 frozen template (git 8049952c9), zero transcription
(r587 / r958 / r974 lineage; cloned mechanics from _w238bma_prereg_derive.py). All anchor faces
machine-read live at derive time:
- results/perpetual_faces/n1_w238_results.json  (W238 finalize product, landed 12:58)
- results/_w239bmc_20261014_probe_receipt.json  (bm-c r991 seat probe ADMIT)
- Tools/saturation_engine.py n1_bands() live derive (236 rows, tail W238, owner rows 228)
Fail-closed: every SUB pair must hit exactly once; forbidden-residue scan must be zero.
"""
import json
import subprocess
import sys
import importlib.util
from collections import Counter

OUT_PATH = 'research/PERPETUAL_N1_W239_PREREG.md'
TPL_COMMIT = '8049952c9'   # W238 prereg frozen-at-commit (bm-a r978 derive)
FIN_COMMIT = 'f597934fa'   # W238 finalize one-pass LANDED (bm-a r985 closeout)


def git_show(ref, path):
    r = subprocess.run(['git', 'show', '%s:%s' % (ref, path)], capture_output=True)
    assert r.returncode == 0, 'git show failed: %s' % r.stderr[:300]
    return r.stdout.decode('utf-8')


# ---------- facts (live machine-read, zero transcription) ----------
fin = json.load(open('results/perpetual_faces/n1_w238_results.json', encoding='utf-8'))
probe = json.load(open('results/_w239bmc_20261014_probe_receipt.json', encoding='utf-8'))

npc = fin['null_pool_cumulative']
merged_mu = npc['merged']['mu']
merged_sigma = npc['merged']['sigma']
w238_only_mu = npc['w238_only']['mu']
a_p95 = fin['families']['A_random_engine_exit']['full_sharpe_p95']
se_mu_at_k = npc['se_mu_at_k521520']
k_lift = fin['skill_line_v2_k_lift']['line_delta_k_lift']
line_merged = fin['skill_line_v2_k_lift']['line_merged_521520']
line_pre = fin['skill_line_v2_k_lift']['line_pre_w238']
n_eff_he = fin['skill_line_v2_k_lift']['n_eff_held_equal']
led = fin['science_gates']['ledger']
prev_total, batch_trials, total = led['prev_total'], led['batch_trials'], led['total']
merged_K = npc['merged']['n_values']

# sanity: five-key anchors must equal the landed finalize numbers
assert (prev_total, batch_trials, total) == (945735, 2200, 947935), (prev_total, batch_trials, total)
assert merged_K == 521520, merged_K
assert k_lift == 0.0, k_lift
assert line_merged == line_pre == 1.193, (line_merged, line_pre)
assert n_eff_he == 945735, n_eff_he
assert se_mu_at_k == 0.000339, se_mu_at_k
assert a_p95 == 0.3223, a_p95

# seat probe bands must equal the W239 target bands
bands = probe['bands']
assert bands['A'] == [542501, 544500] and bands['B'] == [540604, 540803], bands
leg1 = probe['legs']['leg1']
assert leg1['A'] == [542501, 544500] and leg1['B'] == [540604, 540803], leg1
assert leg1['hops_A'] == 2 and leg1['hops_B'] == 0, (leg1['hops_A'], leg1['hops_B'])
rel = leg1['relation_asserts']
assert rel['A_base_ge_priorB_tail_plus1'] is True and rel['AB_mutual_exclusion'] is True, rel
assert rel['B_base_eq_priorB_tail_plus1'] is True and rel['B_no_ownA_jump'] is True, rel
assert 'NINETY-NINTH' in leg1['A_semantics'], leg1['A_semantics'][:200]
assert 'seed-decoupled' in leg1['B_semantics'], leg1['B_semantics'][:200]
leg4 = probe['legs']['leg4']
assert leg4['W240p_A_naive'] == '544501..546500' and leg4['hops_A'] == 1, leg4
assert leg4['W240p_A_first_clean'] == '545501..547500', leg4
assert leg4['W240p_A_naive_refusers_seeds'] == [545500], leg4
assert leg4['W240p_B_naive'] == '540804..541003' and leg4['hops_B'] == 0, leg4
assert leg4['W240p_B_lands_inside_W240p_A_naive'] is False, leg4

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
assert n_rows == 236 and keys[-2:] == [237, 238], (n_rows, keys[-2:])
assert 239 not in keys, 'W239 already registered?!'
assert owner_rows == 228 and bmc_rows == 65 and bma_rows == 122, (owner_rows, bmc_rows, bma_rows)

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
mu_s = '%s%.8f' % (MINUS, abs(merged_mu))            # -0.09276764 (U+2212 face)
wmu_s = '%s%.8f' % (MINUS, abs(w238_only_mu))        # -0.09086291
sigma_s = '%.8f' % merged_sigma                     # 0.24509858
delta_s = '%.4f' % abs(merged_mu - w238_only_mu)    # 0.0019

# ---------- template ----------
tpl = git_show(TPL_COMMIT, 'research/PERPETUAL_N1_W238_PREREG.md')

SUBS = []
A = SUBS.append

# S1 title line (whole-line)
A(('# PERPETUAL-N1-W238 预注册 · N1 nulls-deepening 池第 236 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 227 注册在册（表尾 W237 行·probe leg0 机证 235 行 live 单态零注入腿）+本候选=bm-a 自有席自有波【live-derive face：席面 own-seat face（bm-a r976 席位 MSG-20261014-0745-bma-w238-seat·probe receipt _w238bma_20261014 机证·bands ADMIT verbatim·zero takeover）→freeze 时 live derive bma rows 121+候选=第 122 枚 EXACT·以 freeze 时 live derive 为准 r587/r359】【bm-a 循环班 r978 freeze 窗 2026-10-14 9:2x·CEO 填载令 standing+2026-10-10 ~23:1x RE-ISSUE+O-20260909-2334 本地满用令+O-20261013-2215 CPU 常开令】）',
   '# PERPETUAL-N1-W239 预注册 · N1 nulls-deepening 池第 237 枚（never-dry 常供给例波·波序号连续·机面 derive：engine_owner 行 228 注册在册（表尾 W238 行·probe leg0 机证 236 行 live 单态零注入腿）+本候选=bm-c 自有席自有波【live-derive face：席面 own-seat face（bm-c r991 席位 MSG-20261014-0914-bmc-w239-seat·probe receipt _w239bmc_20261014 机证·bands ADMIT verbatim·zero takeover）→freeze 时 live derive bmc rows 65+候选=第 66 枚 EXACT·以 freeze 时 live derive 为准 r587/r359】【bm-c 循环班 r996 freeze 窗 2026-10-14 13:2x·CEO 填载令 standing+2026-10-10 ~23:1x RE-ISSUE+O-20260909-2334-bm-b 本地满用令+O-20261013-2215 CPU 常开令】）'))

# S2 L3 fragments
A(('saturation_engine.py status live-read r978：burns_active=[] queue_next=[] 实读）',
   'saturation_engine.py status live-read r996：burns_active=[] queue_next=[] 实读）'))
A(('**波号 238=注册表 W237 席后首个自由号**【probe leg3 vacancy 机证（r976 席位窗实跑：origin inbox/processed/ 零 W238 席位外机命中+origin perpetual_faces.py 零 238 行+origin perpetual_faces_n1.py 零 PERPETUAL-N1-W238 WAVE_CONFIGS+origin 零 PERPETUAL_N1_W238_PREREG.md 四查）',
   '**波号 239=注册表 W238 席后首个自由号**【probe leg3 vacancy 机证（r991 席位窗实跑：origin inbox/processed/ 零 W239 席位外机命中+origin perpetual_faces.py 零 239 行+origin perpetual_faces_n1.py 零 PERPETUAL-N1-W239 WAVE_CONFIGS+origin 零 PERPETUAL_N1_W239_PREREG.md 四查）'))
A(('+W237=bm-c r990 prereg derive（d311a5439）+五面冻结 splice（e4a23cc7a）+引擎自燃 12/12（ledger append 38f6e6b87/d7fd42a62）+r990 finalize one-pass 已落（K=519,320·账本头 945,189 机读·n1_w237_results.json·08:5x）——本波上游链=W1..W237 finalize 全落地·零在飞上游席·干净前置**',
   '+W237=bm-c r990 prereg derive（d311a5439）+五面冻结 splice（e4a23cc7a）+引擎自燃 12/12（ledger append 38f6e6b87/d7fd42a62）+r990 finalize one-pass 已落（K=519,320·账本头 945,189 机读·n1_w237_results.json·08:5x）+W238=bm-a r978 prereg derive（8049952c9）+五面冻结 splice（50fa77623）+引擎自燃 12/12（12:44:04 delivered·daemon self-ignite 零 kill-restart）+bm-a r985 finalize one-pass 已落（K=521,520·账本头 947,935 机读·n1_w238_results.json·12:58）——本波上游链=W1..W238 finalize 全落地·零在飞上游席·干净前置**'))
A(('席位公示=MSG-20261014-0745-bma-w238-seat 已推 origin 3e551d846 先于本冻结【r565 律·席位先行·bm-a r976 窗发布·本窗=自有席承接】；下游 W239+ 投影见 §5.5（probe 机证 leg4·W239 freezer 承接面）】。**单态零席位空档**：W2..W237 全注册在冻结时点成立（W208 经 r885 接管归 bm-c·W210 经 r898 接管归 bm-c·bands unchanged R250；W209/W211 bm-c 落链）。',
   '席位公示=MSG-20261014-0914-bmc-w239-seat 已推 origin 603ff65d9 先于本冻结【r565 律·席位先行·bm-c r991 窗发布·本窗=自有席承接】；下游 W240+ 投影见 §5.5（probe 机证 leg4·W240 freezer 承接面）】。**单态零席位空档**：W2..W238 全注册在冻结时点成立（W208 经 r885 接管归 bm-c·W210 经 r898 接管归 bm-c·bands unchanged R250；W209/W211 bm-c 落链）。'))

# S3 L5 bands line
A(('ADMIT 回执=results/_w238bma_20261014_probe_receipt.json 五腿单窗 gate-合并单回执结构',
   'ADMIT 回执=results/_w239bmc_20261014_probe_receipt.json 五腿单窗 gate-合并单回执结构'))
A(('**A-ext seed=538_404..540_403**（**A 面=FIRST-CLEAN past prior-wave B 阶梯第九十八例**：A 面算术续带 538_204..540_203（自注册 W237 A 尾 538_203 续）在其起点即被 W237 注册 B 带 538_204..538_403 拒（W237 席位 leg4 投影+其 probe 所预言+强制）→ 诚实前行走 **1 hop** 落 **538_404..540_403**·**A base==前波 B 尾+1（538_403+1）机检关系**=**A-hops-prior-B 阶梯几何第九十八例（E36 卡）**·非转录 r587 前向单调断言在走册；序数面如实披露：本窗 probe 回执 A_semantics 机读序数=NINETY-EIGHTH（第九十八例）·本件按回执序数面记载非转抄（r587））',
   '**A-ext seed=542_501..544_500**（**A 面=FIRST-CLEAN past prior-wave B+live-seeds 阶梯第九十九例**：A 面算术续带 540_404..542_403（自注册 W238 A 尾 540_403 续）在其起点即被 W238 注册 B 带 540_404..540_603 拒（W238 席位 leg4 投影+其 probe 所预言+强制）**且带内被 SEED_REGISTRY 活点 541_500/542_000 拒·第二窗 542_001..544_000 被活点 542_500 拒（live-seed 拒带 NEW FACE·首例活种子拒先于注册 B 带出现）**→ 诚实前行走 **2 hops** 落 **542_501..544_500**·**A base≥前波 B 尾+1（540_603+1）机检关系·hop 链逐跳在 probe 回执 leg1（A_hop_chain 机证）**=**A-hops-prior-B 阶梯几何第九十九例（E36 卡）+seed-hop 新形态**·非转录 r587 前向单调断言在走册；序数面如实披露：本窗 probe 回执 A_semantics 机读序数=NINETY-NINTH（第九十九例）·本件按回执序数面记载非转抄（r587））'))
A(('**B-ext exit seed=540_404..540_603**（**B 面=FIRST-CLEAN past own-wave A**：B 面 naive first-clean 续带 538_404..538_603 在注册宇宙上 CLEAN 但**落在本波 A 窗 538_404..540_403 内**（**同窗互斥面 leg2 律·W141 先例**：A 与 B 同一冻结 commit 双注册·互斥断言强制 B 越过本波 A 窗）→ B 带本波 A 窗保留走 **1 hop** 落 **540_404..540_603**·**B base==本波 A 尾+1（540_403+1）机检关系**·hop 链逐跳在 probe 回执（B_hop_chain leg1 机证）；**W237 席位 leg4 投影承接面注记兑现**：投影预言 W238 须在 post-W237 注册宇宙重 derive 且 derive B 时预留本波 A 窗——本窗双面兑现·A 被拒+阶梯越带如投影所期·B 同窗互斥保留=投影所期·已如实披露非分叉）',
   '**B-ext exit seed=540_604..540_803**（**B 面=FIRST-CLEAN·hops=0 seed-decoupled 形态**：B 面 naive 续带 540_604..540_803（自注册 W238 B 尾 540_603 续）在注册宇宙上 CLEAN 且**不落本波 A 窗 542_501..544_500 内**（本波 A 因活种子拒带 seed-hop 越过阶梯基座→**首例 seed-decoupled A/B gap 面**：同窗互斥面 leg2 律·W141 先例以 A 跳越形态满足·B 无需 own-A reservation jump）→ B 保留 naive 落位 **hops=0**·**B base==前波 B 尾+1（540_603+1）机检关系**（fc_b==fc_b_naive·B_hop_chain=[] 空集 leg1 机证·B_no_ownA_jump=true）；**W238 席位 leg4 投影承接面注记兑现**：投影预言 W239 须在 post-W238 注册宇宙重 derive 且 B naive CLEAN hops=0 如投影所期——本窗如实兑现·A 活种子拒带+seed-hop=投影所期·B decoupled 保留=投影所期·已如实披露非分叉）'))
A(('R250：W238 带从未指派', 'R250：W239 带从未指派'))
A(('A base=538404 span=2000 checked=2000 verdict=FREE / B base=540404 span=200 checked=200 verdict=FREE',
   'A base=542501 span=2000 checked=2000 verdict=FREE / B base=540604 span=200 checked=200 verdict=FREE'))
A(('扫描面=pre-W238 全二百三十五行注册 N1 带表（表尾 W237 行·freeze 窗 live derive 235 行单态 owner rows 227——席位窗 probe leg0 实测 234 行+W237 splice 落地后 +1 如实注记）',
   '扫描面=pre-W239 全二百三十六行注册 N1 带表（表尾 W238 行·freeze 窗 live derive 236 行单态 owner rows 228——席位窗 probe leg0 实测 235 行+W238 splice 落地后 +1 如实注记）'))

# S4 L9 reuse-domain
A(('（W2..W237 落地 runner 的 wave 参数化复用', '（W2..W238 落地 runner 的 wave 参数化复用'))
A(('selftest W238 face 将随五面冻结落地验证', 'selftest W239 face 将随五面冻结落地验证'))
A(('本件与 results/_w238bma_freeze_edits.py（五面冻结拼接脚本·按 _w237bmc_freeze_edits.py 模板派生·gate0.5 自查 W237 行+W237 finalize 件在场·未落即 loud abort·estate 提取面=本机 W237 块物理字节〔结构已知〕）=freeze-prep 束同窗落地（r990/W237 先例 freeze-prep 同式·本窗上游已全落=执行窗即 freeze 窗）',
   '本件与 results/_w239bmc_freeze_edits.py（五面冻结拼接脚本·按 _w238bma_freeze_edits.py 模板派生·gate0.5 自查 W238 行+W238 finalize 件在场·未落即 loud abort·estate 提取面=本机 W238 块物理字节〔结构已知〕）=freeze-prep 束同窗落地（r978/W238 先例 freeze-prep 同式·本窗上游已全落=执行窗即 freeze 窗）'))

# S5 L12 batch identity
A(('- 批名=**PERPETUAL-N1-W238**。', '- 批名=**PERPETUAL-N1-W239**。'))
A(('**W1..W237 N1 finalize 已全部落地**【净账本锚头 **945,189**·K=519,320 合并池·n1_w237_results.json 机读·W237 finalize one-pass bm-c r990 窗 08:5x（W237 面完整性=12/12 shards consumed+finalize audit finalize_only=true 收口·splice e4a23cc7a+引擎自燃链如实注记）】',
   '**W1..W238 N1 finalize 已全部落地**【净账本锚头 **947,935**·K=521,520 合并池·n1_w238_results.json 机读·W238 finalize one-pass bm-a r985 窗 12:5x（W238 面完整性=12/12 shards consumed+finalize audit finalize_only=true 收口·splice 50fa77623+引擎自燃链如实注记）】'))
A(('累计 null 池=519,320+2,200（本波）=**521,520 投影**',
   '累计 null 池=521,520+2,200（本波）=**523,720 投影**'))

# S6 L13 claim
A(('（席位公示=MSG-20261014-0745-bma-w238-seat 已推 origin 3e551d846 r565 律（bm-a r976 席·bm-a 自有席承接）·probe W239+ 投影 A 540_404..542_403 / B 540_604..540_803 **live-seeds-refuse NEW FACE 强制注记+同窗互斥预披露**（投影 A naive 540_404..542_403 被 SEED_REGISTRY 活点 [541500, 542000] 拒→诚实 2 hops first-clean 542_501..544_500；投影 B 落投影 A naive 窗内·W238 B 带 540_404..540_603 注册后将拒 naive W239 A 窗=阶梯 A-hops-prior-B 第九十九例——**W239 freezer 承接面强制注记：须在 post-W238 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**））',
   '（席位公示=MSG-20261014-0914-bmc-w239-seat 已推 origin 603ff65d9 r565 律（bm-c r991 席·bm-c 自有席承接）·probe W240+ 投影 A 544_501..546_500 / B 540_804..541_003 **live-seeds-refuse 承袭注记+seed-decoupled gap 预披露**（投影 A naive 544_501..546_500 被 SEED_REGISTRY 活点 [545500] 拒→诚实 1 hop first-clean 545_501..547_500；投影 B naive 540_804..541_003 CLEAN hops=0 不落投影 A 窗内——**seed-gap face：W239 A/B decoupled·W240 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace·W239 B 带将拒 naive W240 A 窗仅当重叠——**W240 freezer 承接面强制注记：须在 post-W239 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**））'))
A(('T-2026-10-01-141 s1 引擎线第 228 波【bm-a 第一百二十二枚自有波【机面 derive：probe leg0 bma_rows=121 attempt-continuity face（r976 窗算法·bm-a own seat+bma live rows 121 实读）——freeze 时 live derive bma rows 121+候选=第 122 枚 EXACT（以 freeze 时 live derive 为准 r587/r359）】】',
   'T-2026-10-01-141 s1 引擎线第 229 波【bm-c 第六十六枚自有波【机面 derive：probe leg0 bmc_rows=65 attempt-continuity face（r991 窗算法·bm-c own seat+bmc live rows 65 实读）——freeze 时 live derive bmc rows 65+候选=第 66 枚 EXACT（以 freeze 时 live derive 为准 r587/r359）】】'))
A(('（波号=注册表 W237 席后首个自由号·单态零席位空档于冻结时点成立；席位公示 MSG-20261014-0745-bma-w238-seat 先推 origin 3e551d846 r565 律；lane-free；dept:研究）',
   '（波号=注册表 W238 席后首个自由号·单态零席位空档于冻结时点成立；席位公示 MSG-20261014-0914-bmc-w239-seat 先推 origin 603ff65d9 r565 律；lane-free；dept:研究）'))

# S7 L14 RAM face (old side = W238 doc literal with bm-a's 70.1GB freeze-window read)
A(('**RAM face 如实注记：本窗 free RAM ~70.1GB（bm-a 底盘常驻·94G 物理内存机·MV XQ i2v 影片链=bm-c lane 已收官〔O-20261012-0739 §1〕如实注记）——N1 引擎点火无 RAM 硬闸（W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230/W231/W232/W233/W234/W235/W236/W237 低 RAM 实烧先例·W237 冻结窗 1.6G 实锚族·W236 席位窗 1.9G/0.2G 实锚族）·burn 由引擎 RAM 面随 cycle 上报自判·本件不代引擎决策。**',
   f'**RAM face 如实注记：本窗 free RAM ~{ram_free_gb:.1f}GB（bm-c 底盘常驻高位·24G 物理内存机·GPU=MV V3 burn lane 在烧〔O-20261014-1125 MV-only 执法窗〕+CPU 车道独立如实注记）——N1 引擎点火无 RAM 硬闸（W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230/W231/W232/W233/W234/W235/W236/W237/W238 低 RAM 实烧先例·W238 冻结窗 70.1G bm-a 实锚·W237 冻结窗 1.6G 实锚族·W236 席位窗 1.9G/0.2G 实锚族）·burn 由引擎 RAM 面随 cycle 上报自判·本件不代引擎决策。**'))

# S8 L15
A(('复烧自见 W238 行并点火自烧', '复烧自见 W239 行并点火自烧'))

# S9 L19 gate path
A(('--prereg research/PERPETUAL_N1_W238_PREREG.md', '--prereg research/PERPETUAL_N1_W239_PREREG.md'))

# S10 L20
A(('p2_calibration v1/v2 canon；v1 ext；v2..W237 落地）', 'p2_calibration v1/v2 canon；v1 ext；v2..W238 落地）'))

# S11 L31 A-tier
A(('- **A 档**（j=0..1,999）：entry rng seed=**538_404+j**（法典 §4 W238 行 A=538_404..540_403·**FIRST-CLEAN past prior-wave B 阶梯第九十八例**：算术续带 538_204..540_203 起点即被 W237 注册 B 带 538_204..538_403 拒→1 hop 落 538_404..540_403·A base==前波 B 尾+1 机检关系·E36 卡·hops=1·ADMIT 回执在场）',
   '- **A 档**（j=0..1,999）：entry rng seed=**542_501+j**（法典 §4 W239 行 A=542_501..544_500·**FIRST-CLEAN past prior-wave B+live-seeds 阶梯第九十九例**：算术续带 540_404..542_403 起点即被 W238 注册 B 带 540_404..540_603 拒+带内活点 541_500/542_000 拒·第二窗被活点 542_500 拒→2 hops 落 542_501..544_500·A base≥前波 B 尾+1 机检关系·E36 卡+seed-hop 面·hops=2·hop 链逐跳在 probe 回执 leg1·ADMIT 回执在场）'))

# S12 L32 B-tier
A(('- **B 档**（j=0..199）：entry rng=**538_404+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**540_404+j**（法典 §4 W238 行 B=540_404..540_603·**FIRST-CLEAN past own-wave A**：B 算术续带 538_404..538_603 在注册宇宙 CLEAN 但落本波 A 窗 538_404..540_403 内→**同窗互斥面 leg2 律·W141 先例**强制 B 越本波 A 窗→保留走落 540_404..540_603·hops=1·**B base==本波 A 尾+1 机检关系**·非转录 r587·hop 链逐跳在 probe 回执·与 W237 席位 leg4 投影承接面注记兑现收敛·ADMIT 回执在场）',
   '- **B 档**（j=0..199）：entry rng=**542_501+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；exit rng=**540_604+j**（法典 §4 W239 行 B=540_604..540_803·**FIRST-CLEAN·hops=0 seed-decoupled 形态**：B 算术续带 540_604..540_803 在注册宇宙 CLEAN 且不落本波 A 窗 542_501..544_500 内（本波 A seed-hop 越过阶梯基座→同窗互斥面 leg2 律·W141 先例以 A 跳越形态满足·B 无 own-A reservation jump）→保留走落 540_604..540_803·hops=0·**B base==前波 B 尾+1（540_603+1）机检关系**（fc_b==fc_b_naive·B_hop_chain=[] 空集 leg1 机证）·非转录 r587·与 W238 席位 leg4 投影承接面注记兑现收敛·ADMIT 回执在场）'))

# S13 L36 disjoint + estate family (6 pairs)
A(('种子带 disjoint 全例（selftest 强制）：W238 带与 v1 在用带', '种子带 disjoint 全例（selftest 强制）：W239 带与 v1 在用带'))
A(('W2..W237 带（冻结时点全注册单态）', 'W2..W238 带（冻结时点全注册单态）'))
A(('本波机验 ADMIT 回执在场=_w238bma_20261014 探针窗', '本波机验 ADMIT 回执在场=_w239bmc_20261014 探针窗'))
A(('selftest W238 face（A=first-clean past prior-wave B 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W237 行 parity 腿',
   'selftest W239 face（A=first-clean past prior-wave B+live-seeds 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W238 行 parity 腿'))
A(('从**本机 W237 块物理字节**提取（结构已知·提取自证断言 69 行 range 恒等在场）——W236 块的 W235 leg（1 行）不入 estate 路径·提取后新增 W236+W237 leg 构成 W238 块 parity 96 行（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232+W233+W234+W235+W236+W237）·零假设零风险。',
   '从**本机 W238 块物理字节**提取（结构已知·提取自证断言 69 行 range 恒等在场）——W237 块的 W236 leg（1 行）不入 estate 路径·提取后新增 W237+W238 leg 构成 W239 块 parity 97 行（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232+W233+W234+W235+W236+W237+W238）·零假设零风险。'))

# S14 L39
A(('（起草窗实流 W1..W237 已落账 519,320 实测·derive 禁手抄）',
   '（起草窗实流 W1..W238 已落账 521,520 实测·derive 禁手抄）'))

# S15 L40 ledger
A(('batch_name="PERPETUAL-N1-W238", batch_trials=2200, file_name="results/perpetual_faces/n1_w238_results.json"',
   'batch_name="PERPETUAL-N1-W239", batch_trials=2200, file_name="results/perpetual_faces/n1_w239_results.json"'))

# S16 L44
A(('（起草窗实况注记：**W1..W237 N1 finalize 已全部落地**——净账本锚头 945,189·**K=519,320 合并池**·**零在飞上游席——本波 §5 预测键=**W237 实测值**【results/perpetual_faces/n1_w237_results.json·N1 面最新已落账键·08:5x finalize one-pass】。',
   '（起草窗实况注记：**W1..W238 N1 finalize 已全部落地**——净账本锚头 947,935·**K=521,520 合并池**·**零在飞上游席——本波 §5 预测键=**W238 实测值**【results/perpetual_faces/n1_w238_results.json·N1 面最新已落账键·12:5x finalize one-pass】。'))

# S17 L45 key1
A(('1. W238-only mu 与累计池 merged mu（W237 实测键 **−0.09277571**·K=519,320 合并池·W237-only 实测 **−0.08489014**）差异 **|Δ|<0.02**（W2..W237 共二百三十五面实测 mu 稳定先例·单波跨键微；W237-only vs merged 实差 0.0079 在带内）。',
   f'1. W239-only mu 与累计池 merged mu（W238 实测键 **{mu_s}**·K=521,520 合并池·W238-only 实测 **{wmu_s}**）差异 **|Δ|<0.02**（W2..W238 共二百三十六面实测 mu 稳定先例·单波跨键微；W238-only vs merged 实差 {delta_s} 在带内）。'))

# S18 L46 key2
A(('2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.24509712**=W237 合并池实测）。',
   f'2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **{sigma_s}**=W238 合并池实测）。'))

# S19 L47 key3
A(('3. A 档 full_sharpe_p95 与 W237 A 档 p95（**0.3326** 实测锚）差 **<0.05**（门标注法 W5..W237 先例：结果知情面仅作机器断言之用·测量面非注册收益）。利益）。',
   f'3. A 档 full_sharpe_p95 与 W238 A 档 p95（**{a_p95:.4f}** 实测锚）差 **<0.05**（门标注法 W5..W238 先例：结果知情面仅作机器断言之用·测量面非注册收益）。利益）。'))

# S20 L48 key4 (2 pairs)
A(('W136..W237 先例链披露【各波 K-lift 全在 ±0.0003 内·机读可复核·键 W237 实测 K-lift **+0.0000**·line_merged@K519,320 **1.1928**·line_pre_w237 1.1928·n_eff_held_equal 942,989；',
   'W136..W238 先例链披露【各波 K-lift 全在 ±0.0003 内·机读可复核·键 W238 实测 K-lift **+0.0000**·line_merged@K521,520 **1.193**·line_pre_w238 1.193·n_eff_held_equal 945,735；'))
A(('→W234 **0.000342**→W235 **0.000342**→W236 **0.000341**→W237 **0.00034**】）。',
   '→W234 **0.000342**→W235 **0.000342**→W236 **0.000341**→W237 **0.00034**→W238 **0.000339**】）。'))

# S21 L49 key5 projection (seed-decoupled face)
A(('5. **W239+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 540_404..542_403 **被 SEED_REGISTRY 活点 [541500, 542000] 拒**（hops=2·pre-W238 宇宙 NEW FACE：首次 live-seed 拒带先于注册 B 带出现）→诚实前行走 **2 hops** first-clean **542_501..544_500**；B naive first-clean **540_604..540_803 CLEAN**（hops=0）——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W239：W239 冻结方必须在 post-W238 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；**W238 B 带 540_404..540_603 注册后将拒 naive W239 A 窗**——W239 A 重 derive 同强制（越过 W238 B 带·阶梯 A-hops-prior-B 第九十九例）；verify at W239 prereg，hop 链逐跳在 probe 回执。',
   '5. **W240+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 544_501..546_500 **被 SEED_REGISTRY 活点 [545500] 拒**（hops=1·pre-W239 宇宙）→诚实前行走 **1 hop** first-clean **545_501..547_500**；B naive first-clean **540_804..541_003 CLEAN**（hops=0·**不落投影 A 窗内**——B_hop lands-inside-A=false 腿在场）；**W239 B 带 540_604..540_803 注册后将拒 naive W240 A 窗仅当重叠**（**seed-gap face：W239 A/B decoupled·W240 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace**）——W240 冻结方必须在 post-W239 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡·W141 先例；verify at W240 prereg，hop 链逐跳在 probe 回执。'))

# S22 L52 runner (2 pairs)
A(('--wave 238/finalize --wave 238', '--wave 239/finalize --wave 239'))
A(('【n1_w238/ 分片计数增长', '【n1_w239/ 分片计数增长'))

# S23 L53 deliverables (2 pairs)
A(('results/p2cal_ext/n1_w238/shard-<k>-of-12.json', 'results/p2cal_ext/n1_w239/shard-<k>-of-12.json'))
A(('`results/perpetual_faces/n1_w238_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 键序前置=**起草窗零在飞上游席（W1..W237 全落）',
   '`results/perpetual_faces/n1_w239_results.json`（finalize 合并件·顶层 evidence_cutoff·cutoff_meta·audit 段·K-lift 对照；finalize 键序前置=**起草窗零在飞上游席（W1..W238 全落）'))

# S24 L54 engine ledger
A(('engine_owner==bm-a 121 行注册〔冻结时点〕', 'engine_owner==bm-c 65 行注册〔冻结时点〕'))

# S25/S26 L58/L61 placeholders
A(('——r990 W237 §7 范式）', '——bm-a r985 W238 §7 范式）'))
A(('（占位·finalize 同窗回填：§5.5 W239+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——r990 W237 §8 范式）',
   '（占位·finalize 同窗回填：§5.5 W240+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——bm-a r985 W238 §8 范式）'))

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
FORBID = ['PERPETUAL-N1-W238', 'n1_w238/shard', '538404', '540404', 'engine_owner 行 227',
          '池第 236 枚', 'bma rows 121', '第 122 枚', 'r978 freeze 窗', '0745-bma',
          'W2..W237', 'W1..W237', 'v2..W237', 'W5..W237', 'NINETY-EIGHTH', '第九十八例',
          'parity 96 行', '70.1GB', 'r990 W237 §', 'bm-a 121 行', 'pre-W238 全二百三十五',
          '538_204..538_403', 'W238-only mu 与', 'W237 实测键', '0.3326',
          'W237 席位 leg4 投影', 'owner rows 227', '235 行 live',
          '3e551d846', '521,520 投影', '519,320+2,200', '共二百三十五面', '第二百三十五行']
residue = [f for f in FORBID if f in out]
assert not residue, 'forbidden residue: %s' % residue

# legal retained counts (calibrated against actual output structure)
assert out.count('_w238bma') == 1 and out.count('_w238bma_freeze_edits.py') == 1   # freeze-edits template-source citation x1 (r587 lineage)
assert out.count('n1_w237_results.json') == 1, out.count('n1_w237_results.json')   # chain-tail W237 entry
assert out.count('n1_w238_results.json') == 3, out.count('n1_w238_results.json')   # chain-tail W238 + S0 + S5 preamble
assert out.count('n1_w239_results.json') == 2, out.count('n1_w239_results.json')  # ledger + deliverable
assert out.count('PERPETUAL-N1-W239') == 4, out.count('PERPETUAL-N1-W239')
assert out.count('PERPETUAL_N1_W239') == 2, out.count('PERPETUAL_N1_W239')          # vacancy check + gate path
assert 'n1_w239/shard' in out
assert out.count('542_501..544_500') == 6 and out.count('540_604..540_803') == 6   # own-band literals x6 each (A-ext x2+B-ext x1+S11 x2+S12 x1 / B-ext x2+S12 x3+S21 x1)
assert out.count('540_404..540_603') == 2, out.count('540_404..540_603')            # W238 registered B rejector x2 (S3b + S11)
assert 'NINETY-NINTH' in out and out.count('第九十九例') == 4                        # own-A ordinal x4 (S3b x3 + S11)
assert 'seed-decoupled' in out and out.count('seed-decoupled') == 4                 # B-ext + S12 + S6a + S21
assert out.count('545_501..547_500') == 2 and out.count('544_501..546_500') == 3    # W240 projection (S6a x1+S21 x1 / S6a x2+S21 x1)
assert '603ff65d9' in out and out.count('603ff65d9') == 3                           # own seat commit
assert '0914-bmc' in out and out.count('0914-bmc') == 4                              # own seat MSG
assert out.count('第 66 枚') == 2                                                    # bmc ordinal (title + S6b)
assert out.count('947,935') == 3                                                     # net ledger head (S5b + chain + S16)
assert out.count('945,189') == 1                                                     # chain-tail W237 historical head
assert '942,989' in out                                                              # chain-tail W236 historical head
assert '542501' in out and '540604' in out                                           # seed gate bare bases
assert out.count('owner rows 228') == 1 and out.count('engine_owner 行 228') == 1
assert out.count('W239-inherit') == 0                                                # W238 finalize receipt face never in prereg

with open(OUT_PATH, 'w', encoding='utf-8', newline='') as fh:
    fh.write(out)

receipt = {
    'derive': 'W239 prereg machine-generated SUB from frozen W238 template',
    'machine': 'bm-c', 'round': 'r996',
    'template_commit': TPL_COMMIT,
    'upstream_finalize_commit': FIN_COMMIT,
    'sub_pairs_applied': applied,
    'out_path': OUT_PATH,
    'out_bytes': len(out.encode('utf-8')),
    'facts': {
        'merged_mu': merged_mu, 'merged_sigma': merged_sigma,
        'w238_only_mu': w238_only_mu, 'w238_only_sigma': npc['w238_only']['sigma'],
        'a_p95': a_p95, 'se_mu_at_k': se_mu_at_k, 'k_lift': k_lift,
        'line_merged': line_merged, 'line_pre': line_pre, 'n_eff_held_equal': n_eff_he,
        'ledger_prev_total': prev_total, 'ledger_batch': batch_trials, 'ledger_total': total,
        'merged_K': merged_K,
        'n1_bands_rows': n_rows, 'owner_rows': owner_rows, 'bmc_rows': bmc_rows, 'bma_rows': bma_rows,
        'bands': {'A': [542501, 544500], 'B': [540604, 540803]},
        'ram_free_gb': ram_free_gb,
        'engine_status': {'burns_active': burns, 'queue_next': queue_next},
        'seed_hop_new_face': {'hops_A': leg1['hops_A'], 'A_hop_chain': leg1['A_hop_chain'],
                              'hops_B': leg1['hops_B'], 'b_decoupled': True},
        'w240p': {'refusers': leg4['W240p_A_naive_refusers_seeds'],
                  'first_clean': leg4['W240p_A_first_clean'], 'hops': leg4['hops_A'],
                  'B_naive': leg4['W240p_B_naive'], 'B_inside_A': leg4['W240p_B_lands_inside_W240p_A_naive']},
    },
    'forbidden_residue': residue,
}
json.dump(receipt, open('results/_w239bmc_prereg_derive_receipt.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('W239 prereg derive OK: %d SUB pairs, out=%d bytes -> %s' % (applied, len(out.encode('utf-8')), OUT_PATH))
print('facts: n1_bands=%d rows owner_rows=%d bmc=%d bma=%d ram_free=%.1fG' % (n_rows, owner_rows, bmc_rows, bma_rows, ram_free_gb))
