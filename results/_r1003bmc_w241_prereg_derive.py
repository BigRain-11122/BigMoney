# -*- coding: utf-8 -*-
"""W241 prereg derive -- bm-c r1003 freeze window (M12 trigger OPEN: W240 finalize landed 22c6c3374).

Machine-generated SUB from committed W240 frozen template (git 22c6c3374, sec78-backfilled
final state), zero transcription (r587 / r958 / r974 lineage; cloned mechanics from
_w240bma_prereg_derive.py). All anchor faces machine-read live at derive time:
- results/perpetual_faces/n1_w240_results.json  (W240 finalize product, landed 17:3x)
- results/_w241bmc_20261014_probe_receipt.json   (bm-c r1002 seat probe ADMIT)
- Tools/saturation_engine.py n1_bands() live derive (238 rows, tail W240, owner rows 230)
Fail-closed: every SUB pair must hit exactly once (or the declared count); anchor-prefix
line asserts; forbidden-residue scan must be zero.
"""
import json
import subprocess
import sys
import importlib.util
from collections import Counter

OUT_PATH = 'research/PERPETUAL_N1_W241_PREREG.md'
TPL_COMMIT = '22c6c3374'   # W240 prereg frozen-at-commit (bm-a r993, sec78 backfilled final)
FIN_COMMIT = '22c6c3374'   # W240 finalize one-pass LANDED (bm-a r993 closeout)


def git_show(ref, path):
    r = subprocess.run(['git', 'show', '%s:%s' % (ref, path)], capture_output=True)
    assert r.returncode == 0, 'git show failed: %s' % r.stderr[:300]
    return r.stdout.decode('utf-8')


# ---------- facts (live machine-read, zero transcription) ----------
fin = json.load(open('results/perpetual_faces/n1_w240_results.json', encoding='utf-8'))
probe = json.load(open('results/_w241bmc_20261014_probe_receipt.json', encoding='utf-8'))

npc = fin['null_pool_cumulative']
merged_mu = npc['merged']['mu']
merged_sigma = npc['merged']['sigma']
w240_only_mu = npc['w240_only']['mu']
a_p95 = fin['families']['A_random_engine_exit']['full_sharpe_p95']
se_mu_at_k = npc['se_mu_at_k525920']
k_lift = fin['skill_line_v2_k_lift']['line_delta_k_lift']
line_merged = fin['skill_line_v2_k_lift']['line_merged_525920']
line_pre = fin['skill_line_v2_k_lift']['line_pre_w240']
n_eff_he = fin['skill_line_v2_k_lift']['n_eff_held_equal']
led = fin['science_gates']['ledger']
prev_total, batch_trials, total = led['prev_total'], led['batch_trials'], led['total']
merged_K = npc['merged']['n_values']

# sanity: five-key anchors must equal the landed W240 finalize numbers
assert (prev_total, batch_trials, total) == (950135, 2200, 952335), (prev_total, batch_trials, total)
assert merged_K == 525920, merged_K
assert k_lift == 0.0, k_lift
assert line_merged == line_pre == 1.1932, (line_merged, line_pre)
assert n_eff_he == 950135, n_eff_he
assert se_mu_at_k == 0.000338, se_mu_at_k
assert a_p95 == 0.316, a_p95
assert fin['audit']['finalize_only'] is True, 'W240 finalize product audit face'

# seat probe bands must equal the W241 target bands
bands = probe['bands']
assert bands['A'] == [547501, 549500] and bands['B'] == [541004, 541203], bands
leg1 = probe['legs']['leg1']
assert leg1['A'] == [547501, 549500] and leg1['B'] == [541004, 541203], leg1
assert leg1['hops_A'] == 0 and leg1['hops_B'] == 0, (leg1['hops_A'], leg1['hops_B'])
assert leg1['A_hop_chain'] == [] and leg1['B_hop_chain'] == [], (leg1['A_hop_chain'], leg1['B_hop_chain'])
assert leg1['B_naive_first_clean'] == [541004, 541203] and leg1['B_naive_hops'] == 0, leg1
rel = leg1['relation_asserts']
assert rel['A_clean_at_naive_start'] is True and rel['AB_mutual_exclusion'] is True, rel
assert rel['B_base_eq_priorB_tail_plus1'] is True and rel['B_no_ownA_jump'] is True, rel
assert 'seed-decoupled A-continuation' in leg1['A_semantics'], leg1['A_semantics'][:200]
assert 'second consecutive seed-gap face' in leg1['A_semantics'], leg1['A_semantics'][:200]
assert 'seed-decoupled gap face third consecutive' in leg1['B_semantics'], leg1['B_semantics'][:200]
leg2 = probe['legs']['leg2']
assert leg2['conflicts'] == 0 and len(leg2['seed_admit_gate']) == 2, leg2
assert 'base=547501 span=2000 checked=2000 verdict=FREE' in leg2['seed_admit_gate'][0], leg2
assert 'base=541004 span=200 checked=200 verdict=FREE' in leg2['seed_admit_gate'][1], leg2
leg0 = probe['legs']['leg0']
assert leg0['rows'] == 238 and leg0['w240_splice_landed'] is True, leg0
assert leg0['w239_finalize_landed'] is True and leg0['owner_rows'] == 230, leg0
assert leg0['bmc_rows'] == 66 and leg0['bma_rows'] == 123 and leg0['bmb_rows'] == 41, leg0
assert leg0['ordinal'] == 231 and leg0['bmc_ordinal'] == 67, leg0
assert leg0['w240_bands']['A'] == [545501, 547500] and leg0['w240_bands']['B'] == [540804, 541003], leg0
leg3 = probe['legs']['leg3']
assert leg3['origin_vacancy'] is True, leg3
leg4 = probe['legs']['leg4']
assert leg4['W242p_A_naive'] == '549501..551500' and leg4['hops_A'] == 0, leg4
assert leg4['W242p_A_first_clean'] == '549501..551500', leg4
assert leg4['W242p_A_naive_refusers_seeds'] == [], leg4
assert leg4['W242p_B_naive'] == '541204..541403' and leg4['hops_B'] == 0, leg4
assert leg4['W242p_B_first_clean'] == '541204..541403', leg4
assert leg4['W242p_B_lands_inside_W242p_A_naive'] is False, leg4

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
assert n_rows == 238 and keys[-2:] == [239, 240], (n_rows, keys[-2:])
assert 241 not in keys, 'W241 already registered?!'
assert owner_rows == 230 and bmc_rows == 66 and bma_rows == 123, (owner_rows, bmc_rows, bma_rows)
w240 = dict(nrows.get(240) or {})
assert w240.get('engine_owner') == 'bm-a', w240
assert tuple(w240.get('a') or ()) == (545501, 547500), w240
assert tuple(w240.get('b_exit') or ()) == (540804, 541003), w240

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
    ram_free_gb = 1.5

MINUS = '\u2212'  # U+2212 (family convention in prereg keys)
mu_s = '%s%.8f' % (MINUS, abs(merged_mu))            # W240 merged pool key
wmu_s = '%s%.8f' % (MINUS, abs(w240_only_mu))        # W240-only key
sigma_s = '%.8f' % merged_sigma                      # 0.24510199
delta_s = '%.4f' % abs(merged_mu - w240_only_mu)     # 0.0076
p95_s = '%.4f' % a_p95                              # 0.3160

# ---------- template ----------
tpl = git_show(TPL_COMMIT, 'research/PERPETUAL_N1_W240_PREREG.md')
lines = tpl.split('\n')
assert len(lines) == 75, len(lines)   # 74 content + trailing empty

# ---------- helpers ----------
def line_assert(idx, prefix):
    assert lines[idx].startswith(prefix), (idx, lines[idx][:80])

def set_line(idx, new_text):
    lines[idx] = new_text

def sub_once(text, old, new):
    n = text.count(old)
    assert n == 1, 'expect 1 hit, got %d: %s' % (n, old[:80])
    return text.replace(old, new)

# ---------- L0 title ----------
line_assert(0, '# PERPETUAL-N1-W240 ')
NEW_L0 = (
 '# PERPETUAL-N1-W241 预注册 · N1 nulls-deepening 池第 239 枚（never-dry 常供给例波·波序号连续·机面 derive：'
 'engine_owner 行 230 注册在册（表尾 W240 行·probe leg0 机证 238 行 live 单态零注入腿）'
 '+本候选=bm-c 自有席自有波【live-derive face：席面 own-seat face'
 '（bm-c r1002 席位 MSG-20261014-1755-bmc-w241-seat·probe receipt _w241bmc_20261014 机证·bands ADMIT verbatim·zero takeover）'
 '→freeze 时 live derive bmc rows 66+候选=第 67 枚 EXACT·以 freeze 时 live derive 为准 r587/r359】'
 '【bm-c 循环班 r1003 freeze 窗 2026-10-14 18:3x·CEO 填载令 standing+2026-10-10 ~23:1x RE-ISSUE'
 '+O-20260909-2334 本地满用令+O-20261013-2215 CPU 常开令】）')
set_line(0, NEW_L0)

# ---------- L2 order-source line (7 in-line subs) ----------
line_assert(2, '> 令源：CEO 直令 ')
L2 = lines[2]
L2 = sub_once(L2,
 'saturation_engine.py status live-read r989：burns_active=[] queue_next=[] 实读',
 'saturation_engine.py status live-read r1003：burns_active=[] queue_next=[] 实读')
L2 = sub_once(L2,
 '**波号 240=注册表 W239 席后首个自由号**【probe leg3 vacancy 机证（r987 席位窗实跑：origin inbox/processed/ 零 W240 席位外机命中'
 '+origin perpetual_faces.py 零 240 行+origin perpetual_faces_n1.py 零 PERPETUAL-N1-W240 WAVE_CONFIGS'
 '+origin 零 PERPETUAL_N1_W240_PREREG.md 四查）',
 '**波号 241=注册表 W240 席后首个自由号**【probe leg3 vacancy 机证（r1002 席位窗实跑：origin inbox/processed/ 零 W241 席位外机命中'
 '+origin perpetual_faces.py 零 241 行+origin perpetual_faces_n1.py 零 PERPETUAL-N1-W241 WAVE_CONFIGS'
 '+origin 零 PERPETUAL_N1_W241_PREREG.md 四查）')
L2 = sub_once(L2,
 '+bm-c r996 finalize one-pass 已落（K=523,720·账本头 950,135 机读·n1_w239_results.json·14:1x）——本波上游链=W1..W239 finalize 全落地·零在飞上游席·干净前置**',
 '+bm-c r996 finalize one-pass 已落（K=523,720·账本头 950,135 机读·n1_w239_results.json·14:1x）'
 '+W240=bm-a r987 席位+死窗 r991/r992 prereg derive（3e44118e2·r992-continuation absorb 25th-gen）'
 '+五面冻结 splice（dc27f5217·死窗 16:18-fire 遗产吸收落地）+引擎自燃 12/12（r992 splice 携带·12:44:04 delivered）'
 '+bm-a r993 finalize one-pass 已落（K=525,920·账本头 952,335 机读·n1_w240_results.json·17:3x）'
 '——本波上游链=W1..W240 finalize 全落地·零在飞上游席·干净前置**')
L2 = sub_once(L2,
 '席位公示=MSG-20261014-1325-bma-w240-seat 已推 origin 94136b9dd 先于本冻结【r565 律·席位先行·bm-a r987 窗发布·本窗=自有席承接】',
 '席位公示=MSG-20261014-1755-bmc-w241-seat 已推 origin 20782916a 先于本冻结【r565 律·席位先行·bm-c r1002 窗发布·本窗=自有席承接】')
L2 = sub_once(L2,
 '下游 W241+ 投影见 §5.5（probe 机证 leg4·W241 freezer 承接面）',
 '下游 W242+ 投影见 §5.5（probe 机证 leg4·W242 freezer 承接面）')
L2 = sub_once(L2,
 '**单态零席位空档**：W2..W239 全注册在冻结时点成立',
 '**单态零席位空档**：W2..W240 全注册在冻结时点成立')
set_line(2, L2)

# ---------- L4 bands line ----------
line_assert(4, '> **带位（r535 机阀 derive 律·ADMIT 回执=results/')
NEW_L4 = (
 '> **带位（r535 机阀 derive 律·ADMIT 回执=results/_w241bmc_20261014_probe_receipt.json 五腿单窗 gate-合并单回执结构'
 '（r812/r820/r823 先例承袭·dual-window parity N/A 诚实注记））**：'
 '**A-ext seed=547_501..549_500**（**A 面=FIRST-CLEAN·hops=0 seed-decoupled A-continuation 形态**：'
 'A 面算术续带 547_501..549_500（自注册 W240 A 尾 547_500 续）在 post-W240 注册宇宙上起点即 CLEAN 零活点拒'
 '（W240 席位 leg4 投影兑现·连续第二个 seed-gap face·W240 A/B decoupled 承袭·probe leg1 A_semantics 机证）'
 '→ 保留 naive 落位 **hops=0**·**A base==前波 A 尾+1（547_500+1）机检关系**'
 '（fc_a==fc_a_naive·A_hop_chain=[] 空集 leg1 机证·A_clean_at_naive_start=true）·非转录 r587 前向单调断言在走册）；'
 '**B-ext exit seed=541_004..541_203**（**B 面=FIRST-CLEAN·hops=0 seed-decoupled 形态承袭**：'
 'B 面 naive 续带 541_004..541_203（自注册 W240 B 尾 541_003 续）在注册宇宙上 CLEAN 且**不落本波 A 窗 547_501..549_500 内**'
 '（本波 A 高悬于 B 阶梯之上→**seed-decoupled A/B gap 承袭面**：同窗互斥面 leg2 律·W141 先例·B 无需 own-A reservation jump）'
 '→ B 保留 naive 落位 **hops=0**·**B base==前波 B 尾+1（541_003+1）机检关系**'
 '（fc_b==fc_b_naive·B_hop_chain=[] 空集 leg1 机证·B_no_ownA_jump=true·B_semantics seed-decoupled gap face third consecutive 回执在场）；'
 '**W240 席位 leg4 投影承接面注记兑现**：投影预言 W241 须在 post-W240 宇宙重 derive 且 A/B naive 双 CLEAN hops=0 如投影所期'
 '——本窗如实兑现·A 零活点拒=投影所期·B decoupled 保留=投影所期·已如实披露非分叉）。'
 'R250：W241 带从未指派·测量面零结果可锁。'
 '**seed_admit_gate（O-20261010-1945-bm-a ADMIT convention）rc0 双带 FREE**：'
 'A base=547501 span=2000 checked=2000 verdict=FREE / B base=541004 span=200 checked=200 verdict=FREE'
 '（probe leg2 机证·新 null-base 选点 N1_BANDS 保留域查点强制腿在场）。'
 '扫描面=pre-W241 全二百三十八行注册 N1 带表（表尾 W240 行·freeze 窗 live derive 238 行单态 owner rows 230'
 '——席位窗 probe leg0 实测 237 行+W240 splice 落地后 +1 如实注记）+v1 ext；v1 在用带；SEED_REGISTRY 全键零交叠（leg2 机证）；'
 '**N3 已用种子带脚**（N3-R1=70_000..70_005 共 6 值·MSG-183x r529 裁定行强制脚·探针腿 71_000..71_005 双带避让）；'
 '**runner 设计探针种子簇 95_000..95_003**（r335 发现腿 W26 起一切带间隙回执强制携）；'
 '**跨面探针点 95_004/95_006**（r602 披露腿）；N2/N4 设计探针点 40_000/40_001；N2-W15 草案探针点 31_000/31_500/32_000；'
 'lfc 实际流 30_000..30_099；options_wave2 实际流 63_000..63_049【leg-3e 实际流避让带】。')
set_line(4, NEW_L4)

# ---------- L8 reuse-domain line (3 subs) ----------
line_assert(8, '> 复用域 verbatim import 禁重写：')
L8 = lines[8]
L8 = sub_once(L8, 'W2..W239 落地 runner', 'W2..W240 落地 runner')
L8 = sub_once(L8, 'selftest W240 face 将随五面冻结落地验证', 'selftest W241 face 将随五面冻结落地验证')
L8 = sub_once(L8,
 '本件与 results/_w240bma_freeze_edits.py（五面冻结拼接脚本·按 _w239bmc_freeze_edits.py 模板派生·gate0.5 自查 W239 行+W239 finalize 件在场·未落即 loud abort·estate 提取面=本机 W239 块物理字节〔结构已知〕）=freeze-prep 束同窗落地（r996/W239 先例 freeze-prep 同式·本窗上游已全落=执行窗即 freeze 窗）',
 '本件与 results/_w241bmc_freeze_edits.py（五面冻结拼接脚本·按 _w240bma_freeze_edits.py 模板派生·gate0.5 自查 W240 行+W240 finalize 件在场·未落即 loud abort·estate 提取面=本机 W240 块物理字节〔结构已知〕）=freeze-prep 束同窗落地（r993/W240 先例 freeze-prep 同式·本窗上游已全落=执行窗即 freeze 窗）')
set_line(8, L8)

# ---------- L11 batch identity (2 subs) ----------
line_assert(11, '- 批名=**PERPETUAL-N1-W240**。N=**2,200**')
L11 = lines[11]
L11 = sub_once(L11,
 '**W1..W239 N1 finalize 已全部落地**【净账本锚头 **950,135**·K=523,720 合并池·n1_w239_results.json 机读·W239 finalize one-pass bm-c r996 窗 14:1x（W239 面完整性=12/12 shards consumed+finalize audit finalize_only=true 收口·splice c85e806c9+引擎自燃链如实注记）】',
 '**W1..W240 N1 finalize 已全部落地**【净账本锚头 **952,335**·K=525,920 合并池·n1_w240_results.json 机读·W240 finalize one-pass bm-a r993 窗 17:3x（W240 面完整性=12/12 shards consumed+finalize audit finalize_only=true 收口·splice dc27f5217 死窗遗产吸收+引擎自燃链如实注记）】')
L11 = sub_once(L11,
 '累计 null 池=523,720+2,200（本波）=**525,920 投影**',
 '累计 null 池=525,920+2,200（本波）=**528,120 投影**')
set_line(11, L11)

# ---------- L12 claim line (full rewrite) ----------
line_assert(12, '- 认领：never-dry 常供给例波（TRIAL_LABOR_LAW §4')
NEW_L12 = (
 '- 认领：never-dry 常供给例波（TRIAL_LABOR_LAW §4·板空/池饿/无在飞判决批=默认续跑下一波——本机引擎队列空转+burns_active 0 实读；'
 '**CEO 直令 2026-10-08 ~23:5x 领单 standing+2026-10-10 ~23:1x RE-ISSUE「机队CPU算力全部用于回测，排满」'
 '+O-20260909-2334-bm-b §1-2 本地满用令**（'
 '席位公示=MSG-20261014-1755-bmc-w241-seat 已推 origin 20782916a r565 律（bm-c r1002 席·bm-c 自有席承接）'
 '·probe W242+ 投影 A 549_501..551_500 / B 541_204..541_403 **双面 CLEAN hops=0 预披露+seed-gap 承袭注记**'
 '（投影 A naive 549_501..551_500 CLEAN 零活点拒·hops=0；投影 B naive 541_204..541_403 CLEAN hops=0 不落投影 A 窗内——'
 '**seed-gap 承袭 face：W241 A/B 仍 decoupled〔A 547_501..549_500 高悬于 B 541_004..541_203 之上〕'
 '·W242 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace·W241 B 带将拒 naive W242 A 窗仅当重叠——'
 '**W242 freezer 承接面强制注记：须在 post-W241 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**））；'
 'O-20260924-1730 CEO 即时律（认领与开动同轮·禁排未来轮次）；T-2026-10-01-141 s1 引擎线第 231 波'
 '【bm-c 第六十七枚自有波【机面 derive：probe leg0 bmc_rows=66 attempt-continuity face（r1002 窗算法·bm-c own seat+bmc live rows 66 实读）'
 '——freeze 时 live derive bmc rows 66+候选=第 67 枚 EXACT（以 freeze 时 live derive 为准 r587/r359）】】。'
 '（波号=注册表 W240 席后首个自由号·单态零席位空档于冻结时点成立；'
 '席位公示 MSG-20261014-1755-bmc-w241-seat 先推 origin 20782916a r565 律；lane-free；dept:研究）。')
set_line(12, NEW_L12)

# ---------- L13 compute budget line (RAM face 2 subs) ----------
line_assert(13, '- 算力预算=**引擎本地队列烧录**')
L13 = lines[13]
L13 = sub_once(L13,
 '本窗 free RAM ~33.2GB（bm-a 底盘常驻·94G 物理内存机·MV V3 装配站盯守线=导演席窗在飞〔O-20261014-1035 §4〕+CPU 车道独立如实注记）',
 '本窗 free RAM ~%.1fGB（bm-c 底盘常驻·24G 物理内存机·MV wave2 runner 烧制线在飞〔O-20261014-1125 GPU 生成视觉-only 律〕+CPU 车道独立如实注记）' % ram_free_gb)
L13 = sub_once(L13,
 'W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230/W231/W232/W233/W234/W235/W236/W237/W238/W239 低 RAM 实烧先例·W239 冻结窗 1.0G bm-c 实锚·W238 冻结窗 70.1G bm-a 实锚·W237 冻结窗 1.6G 实锚族·W236 席位窗 1.9G/0.2G 实锚族',
 'W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230/W231/W232/W233/W234/W235/W236/W237/W238/W239/W240 低 RAM 实烧先例·W240 冻结窗 33.2G bm-a 实锚·W239 冻结窗 1.0G bm-c 实锚·W238 冻结窗 70.1G bm-a 实锚·W237 冻结窗 1.6G 实锚族·W236 席位窗 1.9G/0.2G 实锚族')
set_line(13, L13)

# ---------- L14 materialization (2 subs) ----------
line_assert(14, '- 物化条件（法典冻结标签行·runner 落地与批产物一批）：本波')
L14 = lines[14]
L14 = sub_once(L14, 'engine_owner==bm-a 波的未烧分片=本地队列项', 'engine_owner==bm-c 波的未烧分片=本地队列项')
L14 = sub_once(L14, '自见 W240 行并点火自烧', '自见 W241 行并点火自烧')
set_line(14, L14)

# ---------- L19 manual pre-read ----------
line_assert(19, '- 人工预读结论：**零命中**——本波对既有 core48 零假设基线')
L19 = sub_once(lines[19], 'v2..W239 落地', 'v2..W240 落地')
set_line(19, L19)

# ---------- L30 A-tier (full rewrite) ----------
line_assert(30, '- **A 档**（j=0..1,999）：entry rng seed=**545_501+j**')
NEW_L30 = (
 '- **A 档**（j=0..1,999）：entry rng seed=**547_501+j**（法典 §4 W241 行 A=547_501..549_500·'
 '**FIRST-CLEAN·hops=0 seed-decoupled A-continuation 形态**：'
 'A 算术续带 547_501..549_500（自注册 W240 A 尾 547_500 续）在 post-W240 注册宇宙上起点即 CLEAN 零活点拒'
 '（W240 席位 leg4 投影兑现·连续第二个 seed-gap face·W240 A/B decoupled 承袭）'
 '→保留 naive 落位 hops=0·**A base==前波 A 尾+1（547_500+1）机检关系**'
 '（fc_a==fc_a_naive·A_hop_chain=[] 空集 probe leg1 机证·A_clean_at_naive_start=true）·非转录 r587·ADMIT 回执在场）；'
 'p=`BASELINE_P[(j//50)%2]`（v1 50-seed 块交替惯例逐字）；随机入场短窗=**引擎退出口**（v1 设计逐字）。')
set_line(30, NEW_L30)

# ---------- L31 B-tier (full rewrite) ----------
line_assert(31, '- **B 档**（j=0..199）：entry rng=**545_501+j**')
NEW_L31 = (
 '- **B 档**（j=0..199）：entry rng=**547_501+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）；'
 'exit rng=**541_004+j**（法典 §4 W241 行 B=541_004..541_203·**FIRST-CLEAN·hops=0 seed-decoupled 形态承袭**：'
 'B 算术续带 541_004..541_203（自注册 W240 B 尾 541_003 续）在注册宇宙 CLEAN 且不落本波 A 窗 547_501..549_500 内'
 '（本波 A 高悬于 B 阶梯之上→同窗互斥面 leg2 律·W141 先例·B 无需 own-A reservation jump）'
 '→保留走落 541_004..541_203·hops=0·**B base==前波 B 尾+1（541_003+1）机检关系**'
 '（fc_b==fc_b_naive·B_hop_chain=[] 空集 leg1 机证·B_no_ownA_jump=true·B_semantics seed-decoupled gap face third consecutive 回执在场）'
 '·非转录 r587·与 W240 席位 leg4 投影承接面注记兑现收敛·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`。')
set_line(31, NEW_L31)

# ---------- L35 disjoint-all-case line (4 subs) ----------
line_assert(35, '- 种子带 disjoint 全例（selftest 强制）：W240 带')
L35 = lines[35]
L35 = sub_once(L35,
 'W240 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W239 带（冻结时点全注册单态）',
 'W241 带与 v1 在用带（10_000..10_099/20_000..20_019）、W1 ext 带（10_100..12_099/20_100..20_299）、W2..W240 带（冻结时点全注册单态）')
L35 = sub_once(L35,
 '本波机验 ADMIT 回执在场=_w240bma_20261014 探针窗',
 '本波机验 ADMIT 回执在场=_w241bmc_20261014 探针窗')
L35 = sub_once(L35,
 'selftest W240 face（A=first-clean past prior-wave B+live-seeds 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W239 行 parity 腿【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）随五面冻结落地',
 'selftest W241 face（A=first-clean past prior-wave B+live-seeds 恒等·B=first-clean past own-wave A 恒等+同窗互斥断言·W240 行 parity 腿【r735 测量-实现分叉族防护面：A/B 窗 set-range 针在场】）随五面冻结落地')
L35 = sub_once(L35,
 '从**本机 W239 块物理字节**提取（结构已知·提取自证断言 69 行 range 恒等在场）——W238 块的 W237 leg（1 行）不入 estate 路径·提取后新增 W238+W239 leg 构成 W240 块 parity 98 行（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232+W233+W234+W235+W236+W237+W238+W239）·零假设零风险',
 '从**本机 W240 块物理字节**提取（结构已知·提取自证断言 69 行 range 恒等在场）——W239 块的 W238 leg（1 行）不入 estate 路径·提取后新增 W239+W240 leg 构成 W241 块 parity 99 行（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232+W233+W234+W235+W236+W237+W238+W239+W240）·零假设零风险')
set_line(35, L35)

# ---------- L38 readout pool ----------
line_assert(38, '- 合并池 `canon 120 + 已落账净值（起草窗实流 W1..W')
L38 = sub_once(lines[38], '起草窗实流 W1..W239 已落账 523,720 实测', '起草窗实流 W1..W240 已落账 525,920 实测')
set_line(38, L38)

# ---------- L39 ledger ----------
line_assert(39, '- 账本：finalize 止 `science_gates.append_ledger')
L39 = sub_once(lines[39], 'file_name="results/perpetual_faces/n1_w240_results.json"',
               'file_name="results/perpetual_faces/n1_w241_results.json"')
set_line(39, L39)

# ---------- L43 §5 preamble ----------
line_assert(43, '（起草窗实况注记：**W1..W239 N1 finalize 已全部落地**')
NEW_L43 = (
 '（起草窗实况注记：**W1..W240 N1 finalize 已全部落地**——净账本锚头 952,335·**K=525,920 合并池**·'
 '**零在飞上游席——本波 §5 预测键=**W240 实测值**【results/perpetual_faces/n1_w240_results.json·'
 'N1 面最新已落账键·17:3x finalize one-pass】。')
set_line(43, NEW_L43)

# ---------- L44 key1 ----------
line_assert(44, '1. W240-only mu 与累计池 merged mu（W239 ')
NEW_L44 = (
 '1. W241-only mu 与累计池 merged mu（W240 实测键 **' + mu_s + '**·K=525,920 合并池·W240-only 实测 **' + wmu_s + '**）差异 **|Δ|<0.02**'
 '（W2..W240 共二百三十八面实测 mu 稳定先例·单波跨键微；W240-only vs merged 实差 ' + delta_s + ' 在带内）。')
set_line(44, NEW_L44)

# ---------- L45 key2 ----------
line_assert(45, '2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 ')
NEW_L45 = (
 '2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **' + sigma_s + '**=W240 合并池实测）。')
set_line(45, NEW_L45)

# ---------- L46 key3 ----------
line_assert(46, '3. A 档 full_sharpe_p95 与 W239 A 档 p95')
NEW_L46 = (
 '3. A 档 full_sharpe_p95 与 W240 A 档 p95（**' + p95_s + '** 实测锚）差 **<0.05**'
 '（门标注法 W5..W240 先例：结果知情面仅作机器断言之用·测量面非注册收益）。利益）。')
set_line(46, NEW_L46)

# ---------- L47 key4 (2 subs) ----------
line_assert(47, '4. K-lift 线移动幅度 **≤±0.02**')
L47 = lines[47]
L47 = sub_once(L47,
 'W136..W239 先例链披露【各波 K-lift 全在 ±0.0003 内·机读可复核·键 W239 实测 K-lift **+0.0000**·line_merged@K523,720 **1.1931**·line_pre_w239 1.1931·n_eff_held_equal 947,935；',
 'W136..W240 先例链披露【各波 K-lift 全在 ±0.0003 内·机读可复核·键 W240 实测 K-lift **+0.0000**·line_merged@K525,920 **1.1932**·line_pre_w240 1.1932·n_eff_held_equal 950,135；')
L47 = sub_once(L47,
 '→W238 **0.000339**→W239 **0.000339**】）',
 '→W238 **0.000339**→W239 **0.000339**→W240 **0.000338**】）')
set_line(47, L47)

# ---------- L48 key5 W242+ projection (full rewrite) ----------
line_assert(48, '5. **W241+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**')
NEW_L48 = (
 '5. **W242+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：'
 'A naive first-clean 549_501..551_500 **CLEAN**（hops=0·pre-W241 宇宙零活点拒）；'
 'B naive first-clean **541_204..541_403 CLEAN**（hops=0·**不落投影 A 窗内**——B_hop lands-inside-A=false 腿在场）；'
 '**W241 B 带 541_004..541_203 注册后将拒 naive W242 A 窗仅当重叠**'
 '（**seed-gap 承袭 face：W241 A/B 仍 decoupled〔A 547_501..549_500 高悬于 B 541_004..541_203 之上〕'
 '·W242 冻结方禁假设 staircase A-base==prior-B-tail+1 恒等·须重读 live trace**）'
 '——W242 冻结方必须在 post-W241 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡·W141 先例；'
 'verify at W242 prereg, hop 链逐跳在 probe 回执。')
set_line(48, NEW_L48)

# ---------- L51 runner ----------
line_assert(51, '- runner=`scripts/perpetual_faces_n1.py`')
L51 = sub_once(lines[51], 'n1_w240/ 分片计数增长', 'n1_w241/ 分片计数增长')
set_line(51, L51)

# ---------- L52 deliverables ----------
line_assert(52, '- 交付：`results/p2cal_ext/n1_w240/shard-<k>-of-12.json`')
L52 = sub_once(lines[52], '起草窗零在飞上游席（W1..W239 全落）', '起草窗零在飞上游席（W1..W240 全落）')
set_line(52, L52)

# ---------- L53 engine ledger ----------
line_assert(53, '- 引擎台账：bm-c live daemon 架构=engine ledger jsonl')
L53 = sub_once(lines[53], 'engine_owner==bm-a 122 行注册〔冻结时点〕+ 本候选',
               'engine_owner==bm-c 66 行注册〔冻结时点〕+ 本候选')
set_line(53, L53)

# ---------- §7 already-backfilled block -> placeholder (lines 57..65) ----------
line_assert(56, '## §7 跑后实证。【finalize 收口机械回填】')
assert lines[57].startswith('- **finalize one-pass 已落地（r993 bm-a'), lines[57][:60]
NEW_L57 = (
 '- （占位·finalize one-pass 后回填：账本恒等式/合并池 K/merged mu·sigma·se_mu/K-lift 对照/§5 五预键机证件/六门探针/canon flip 态/audit 段'
 '——bm-a r993 W240 §7 范式）')
lines[57] = NEW_L57
for i in range(58, 66):
    lines[i] = None   # dropped

# ---------- §8 already-backfilled block -> placeholder (lines 68..71) ----------
line_assert(67, '## §8 批后复盘。【finalize 同窗回填】')
assert lines[68].startswith('- **批后复盘（bm-a r993 own-wave 窗回填）'), lines[68][:60]
NEW_L68 = (
 '- （占位·finalize 同窗回填：§5.5 W242+ 投影承接机证/宝藏与方法论捕获问/诚实披露面'
 '——bm-a r993 W240 §8 范式）')
lines[68] = NEW_L68
for i in range(69, 72):
    lines[i] = None   # dropped

# drop Nones, rejoin
out_lines = [l for l in lines if l is not None]
assert out_lines[-2].startswith('- **跑前冻结=本件 commit**'), out_lines[-2][:60]
assert out_lines[-1] == '', repr(out_lines[-1])   # trailing newline artifact
text = '\n'.join(out_lines)

# ---------- global mechanical pairs (post-context; declared counts) ----------
MECH = [
 ('PERPETUAL-N1-W240', 'PERPETUAL-N1-W241', 2),          # L11 batch, L39 batch_name (L0/L2 already context-subbed)
 ('PERPETUAL_N1_W240_PREREG.md', 'PERPETUAL_N1_W241_PREREG.md', 1),  # L18 gate path (L2 four-check already substituted)
 ('n1_w240_results.json', 'n1_w241_results.json', 2),   # L39 file_name already subbed -> remaining: L52 deliverable + §5 preamble ref stays W240!
 ('n1_w240/', 'n1_w241/', 1),                            # L51 shard-growth already subbed -> L52 deliverable path remains
 ('--wave 240', '--wave 241', 2),
 ('WAVE_CONFIGS[240]', 'WAVE_CONFIGS[241]', 0),
 ('MSG-20261014-1325-bma-w240-seat', 'MSG-20261014-1755-bmc-w241-seat', 0),
 ('94136b9dd', '20782916a', 0),
 ('_w240bma_20261014', '_w241bmc_20261014', 0),
]
# NOTE: 'n1_w240_results.json' stays as the W240 FINALIZE KEY in three places (L2 chain-tail
# W240 entry, L11 anchor-head, L43 preamble) and the L52 deliverable must swap to w241 -> 4 left.
n_left = text.count('n1_w240_results.json')
assert n_left == 4, n_left   # L2 chain-tail + L11 anchor-head + L43 preamble (all stay) + L52 deliverable (to swap)
# swap ONLY the L52 deliverable occurrence (the one inside backticked 'results/perpetual_faces/n1_w240_results.json`（finalize 合并件')
old_deliv = 'results/perpetual_faces/n1_w240_results.json`（finalize 合并件'
assert text.count(old_deliv) == 1
text = text.replace(old_deliv, 'results/perpetual_faces/n1_w241_results.json`（finalize 合并件')

for old, new, expect in MECH:
    if old == 'n1_w240_results.json':
        continue   # handled surgically above
    n = text.count(old)
    assert n == expect, 'mech pair count mismatch: %s expect %d got %d' % (old, expect, n)
    if n:
        text = text.replace(old, new)

# batch-name mechanical check: PERPETUAL-N1-W241 must now appear in L11 + L39
assert text.count('PERPETUAL-N1-W241') >= 4, text.count('PERPETUAL-N1-W241')

# ---------- forbidden residue scan ----------
FORBID = [
 'W239 finalize one-pass bm-c r996',      # stale anchor-head phrasing
 '波号 240=', '第 238 枚', 'engine_owner 行 229',
 'bma rows 122', '第 123 枚', '第一百二十三枚',
 '545_501..547_500', '540_804..541_003', '545501', '540804',
 '−0.09273315', '−0.08455641', '0.24508680', '0.3200',
 '950,135**·K=523,720 合并池',
 'K=523,720 合并池·**W239',           # stale §5 preamble face
 'engine_owner==bm-a', 'bm-a 122 行注册',
 'MSG-20261014-1325-bma-w240-seat', '94136b9dd', '_w240bma_20261014',
 'r989：burns', '第 230 波',
 '523,720+2,200', '525,920 投影**（机械算',
 '本波 §5 预测键=**W239',
 'W241+ 投影（probe 机证 leg4',
 '自见 W240 行',
 'v2..W239 落地', 'W2..W239 落地', 'W2..W239 带',
 'W1..W239 N1 finalize 已全部落地',
 'W1..W239 全落）', 'W1..W239 已落账',
 'selftest W240 face', 'W136..W239 先例链', 'W5..W239 先例',
 '表尾 W239 行', '237 行 live',
 'pre-W240 全二百三十七行',
 'W239-only 实测', '共二百三十七面',
 'W241 freezer 承接面', 'W240 B 带将拒 naive W241 A 窗',
 'hops=0·pre-W240 宇宙',
 'W239 行 parity 腿', 'W239 块物理字节',
]
residue = [f for f in FORBID if f in text]
# positive-allowed exceptions check
assert 'results/perpetual_faces/n1_w240_results.json·N1 面最新已落账键' in text  # §5 preamble keeps W240 finalize key
assert text.count('n1_w240_results.json') == 3   # L2 chain-tail W240 entry + L11 anchor-head + §5 preamble key
assert text.count('n1_w241_results.json') == 2   # L39 file_name + L52 deliverable
assert residue == [], residue

# ---------- write out ----------
with open(OUT_PATH, 'w', encoding='utf-8', newline='') as f:
    f.write(text)

receipt = {
 'derive': 'W241 prereg machine-generated SUB from frozen W240 template',
 'machine': 'bm-c', 'round': 'r1003',
 'template_commit': TPL_COMMIT, 'upstream_finalize_commit': FIN_COMMIT,
 'seat_msg': 'MSG-20261014-1755-bmc-w241-seat', 'seat_msg_origin': '20782916a',
 'out_path': OUT_PATH, 'out_bytes': len(text.encode('utf-8')),
 'facts': {
  'merged_mu': merged_mu, 'merged_sigma': merged_sigma,
  'w240_only_mu': w240_only_mu, 'a_p95': a_p95,
  'se_mu_at_k': se_mu_at_k, 'k_lift': k_lift,
  'line_merged': line_merged, 'line_pre': line_pre,
  'n_eff_held_equal': n_eff_he,
  'ledger_prev_total': prev_total, 'ledger_batch': batch_trials, 'ledger_total': total,
  'merged_K': merged_K,
  'n1_bands_rows': n_rows, 'owner_rows': owner_rows,
  'bmc_rows': bmc_rows, 'bma_rows': bma_rows,
  'bands': {'A': [547501, 549500], 'B': [541004, 541203]},
  'ram_free_gb': ram_free_gb,
  'engine_status': {'burns_active': burns, 'queue_next': queue_next},
  'w242p': {'A': '549501..551500', 'B': '541204..541403', 'hops': 0, 'lands_inside': False},
 },
 'forbidden_residue': residue,
}
with open('results/_r1003bmc_w241_prereg_derive_receipt.json', 'w', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print('OK out_bytes=%d ram=%.1f residue=%d' % (len(text.encode('utf-8')), ram_free_gb, len(residue)))
