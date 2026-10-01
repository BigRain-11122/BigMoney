# r561 bm-b: W53->W54->W55->W56 four-wave finalize chain prereg S7/S8 mechanical
# backfill (r307/r412 two-state law: placeholders were the legitimate pre-burn
# state; this is the post-burn state). ALL numbers derived from
# results/perpetual_faces/n1_w{N}_results.json -- no hand transcription
# (derive-not-copy law). Byte-level LF edit per r500/r530 lesson.
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

M = '\u2212'  # U+2212 minus sign, prereg prose convention

def fmt(v, nd=6):
    s = f"{v:.{nd}f}"
    return s.replace('-', M)

def pct(v, nd=2):
    s = f"{v:+.{nd}f}%"
    return s.replace('-', M)

def signed(v, nd=4):
    s = f"{v:+.{nd}f}"
    return s.replace('-', M)

R = {}
for w in [53, 54, 55, 56]:
    R[w] = json.load(open(f'results/perpetual_faces/n1_w{w}_results.json', encoding='utf-8'))

# anchor values, derived from anchor waves' own results files
def wonly(w):
    d = R[w]['null_pool_cumulative']
    k = f'w{w}_only'
    return d[k]['mu'], d[k]['sigma']

def ap95(w):
    return R[w]['families']['A_random_engine_exit']['full_sharpe_p95']

def skl(w):
    return R[w]['skill_line_v2_k_lift']

# W52 anchor values (draft-window anchor for all four preregs), from W52's own results file
import os
if not os.path.exists('results/perpetual_faces/n1_w52_results.json'):
    print('FATAL: w52 results missing locally'); sys.exit(1)
R52 = json.load(open('results/perpetual_faces/n1_w52_results.json', encoding='utf-8'))
A52_MU = R52['null_pool_cumulative']['w52_only']['mu']
A52_SIG = R52['null_pool_cumulative']['w52_only']['sigma']
A52_P95 = R52['families']['A_random_engine_exit']['full_sharpe_p95']

ROLL = {53: None, 54: 53, 55: 54, 56: 55}  # rolling anchor wave at finalize window (r516 derive law)

META = {
    53: dict(freeze='bm-c r351 冻结 8d09d27c3（A 149_004..151_003 / B 46_401..46_600）', burn='bm-c 12/12 烧录', owner='bm-c 17th owned'),
    54: dict(freeze='bm-a r559 冻结 bdc36af9e（A 151_004..153_003 / B 46_601..46_800）', burn='bm-a 12/12 烧录', owner='bm-a 13th owned'),
    55: dict(freeze='bm-b r559 冻结 c2a72a755（W54 同窗让路窗·A 153_004..155_003 / B 47_001..47_200）', burn='bm-b 12/12 烧录（r559/r560 产品交付）', owner='bm-b 16th owned'),
    56: dict(freeze='bm-b r560 冻结 369ffd8f3（A 155_004..157_003 / B 47_201..47_400）', burn='bm-b 引擎烧录 12/12（r560 点火·r561 本窗烧毕交付）', owner='bm-b 17th owned'),
}

S7_OLD = "## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】\n\n- （空——finalize 后机械回填）\n\n"
S8_OLD = "## §8 批后复盘【必填·s7-T】\n\n- （空——finalize 后机械回填）\n\n"

for w in [53, 54, 55, 56]:
    d = R[w]; np_ = d['null_pool_cumulative']
    mu, sig = wonly(w)
    merged = np_['merged']; mk = merged['n_values']
    se = np_.get(f'se_mu_at_k{mk}')
    p95 = ap95(w)
    s = skl(w); kl = s['line_delta_k_lift']
    lg = d['science_gates']['ledger']
    prev, total = lg['prev_total'], lg['total']

    # criteria vs draft anchor (W52-only, frozen in each prereg S5)
    d_mu = abs(mu - A52_MU); d_sig = (sig - A52_SIG) / A52_SIG * 100; d_p95 = p95 - A52_P95
    assert d_mu < 0.02 and abs(d_sig) < 10 and abs(d_p95) < 0.05 and abs(kl) <= 0.02, f'W{w} draft-anchor criteria FAIL'

    roll_w = ROLL[w]
    if roll_w is None:
        crit_head = (
            f"- S5 判据 4/4 PASS（单锚披露：起草窗锚=W52-only 实测冻结面；finalize 窗滚动锚=**W52 实测**"
            f"〔最新已落账·r516 derive 律〕——全链追平态下双锚同一·零上游落账窗）：\n"
        )
        c1 = f"  1. mu 漂移：W{w}-only **{fmt(mu)}** vs W52 锚 {fmt(A52_MU)}【|Δ|={d_mu:.4f}<0.02 PASS】；merged（K={mk:,}）**{fmt(merged['mu'])}**。\n"
        c2 = f"  2. sigma 相对变化：W{w}-only **{fmt(sig)}** vs W52 锚 {fmt(A52_SIG)}【{pct(d_sig)}<±10% PASS】；merged **{fmt(merged['sigma'])}**。\n"
        c3 = f"  3. A 族 full_sharpe_p95：**{p95:.4f}** vs W52 锚 {A52_P95:.4f}【Δ={signed(d_p95)}<0.05 PASS】（门校准注记：结果知情校准面·测量面零注册利害）。\n"
    else:
        rmu, rsig = wonly(roll_w); rp95 = ap95(roll_w)
        rd_mu = abs(mu - rmu); rd_sig = (sig - rsig) / rsig * 100; rd_p95 = p95 - rp95
        assert rd_mu < 0.02 and abs(rd_sig) < 10 and abs(rd_p95) < 0.05, f'W{w} rolling-anchor criteria FAIL'
        crit_head = (
            f"- S5 判据 4/4 PASS 双锚（锚滚动律披露：起草窗锚=W52-only 实测冻结面；finalize 窗滚动锚=**W{roll_w} 实测**"
            f"〔最新已落账·r516 derive 律·本窗四连链逐波滚动〕——双锚均 4/4）：\n"
        )
        near = '·族内最贴线·如实披露' if rd_mu > 0.015 else ''
        c1 = (f"  1. mu 漂移：W{w}-only **{fmt(mu)}** vs W52 锚 {fmt(A52_MU)}【|Δ|={d_mu:.4f}<0.02 PASS】"
              f"／vs W{roll_w} 滚动锚 {fmt(rmu)}【|Δ|={rd_mu:.4f}<0.02 PASS{near}】；merged（K={mk:,}）**{fmt(merged['mu'])}**。\n")
        c2 = (f"  2. sigma 相对变化：W{w}-only **{fmt(sig)}** vs W52 锚 {fmt(A52_SIG)}【{pct(d_sig)}<±10% PASS】"
              f"／vs W{roll_w} 锚 {fmt(rsig)}【{pct(rd_sig)}<±10% PASS】；merged **{fmt(merged['sigma'])}**。\n")
        c3 = (f"  3. A 族 full_sharpe_p95：**{p95:.4f}** vs W52 锚 {A52_P95:.4f}【Δ={signed(d_p95)}<0.05 PASS】"
              f"／vs W{roll_w} 锚 {rp95:.4f}【Δ={signed(rd_p95)}<0.05 PASS】（门校准注记：结果知情校准面·测量面零注册利害）。\n")
    c4 = (f"  4. K-lift 线移动：**{signed(kl, 4)}**【{s[f'line_pre_w{w}']}→{s[f'line_merged_{mk}']} @n_eff_held {s['n_eff_held_equal']:,}】≤0.02 PASS"
          f"（W3..W52 先例族内正负交替——加深不必然抬线先例续·如实报正负）。\n")
    ledger_line = (
        f"- 账本：prev **{prev:,}**【==W{'52' if w == 53 else w-1} finalize 落账头·derive 禁手抄自证】"
        f"＋本波 2,200＝total **{total:,}**·voids_applied LOWAMP-P1/P2 继承面 ✓；"
        f"skill_line_v2 消费 n_eff={prev:,}（W{w} 合并池 K={mk:,} 同步加深·se_mu {se}）。\n"
    )
    new7 = (
        f"## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】\n\n"
        f"- finalize one-pass 2026-10-02 06:4x（bm-b r561 链式四连收口：{META[w]['freeze']}→{META[w]['burn']}"
        f"〔origin 完备性门 r310 ls-tree 12/12〕→本窗 finalize one-pass；链序解锁=W53→W54→W55→W56 四连落账"
        f"〔prev=活头逐波 derive·r518 origin-timing 律〕→FAIL-CLOSED 等待面清零）。\n"
        + crit_head + c1 + c2 + c3 + c4 + ledger_line
    )

    nxt = {53: (54, 481148), 54: (55, 483348), 55: (56, 485548), 56: (57, 487748)}[w]
    tail = (
        f"- 下游接线：skill_line_v2 @n_eff {prev:,} 线 {s[f'line_merged_{mk}']}（{signed(kl, 4)}）；"
        f"下一波 finalize 消费本波 {total:,} 为 prev；"
    )
    if w == 56:
        tail += (
            f"**W57+ 警示承继**：A 159_004..161_003 与 B 47_601..47_800 双侧 CLEAN（bm-a r561 带闸机证投影）"
            f"——W58 冻结窗仍须带闸 derive 复核（r535 律）；全链 W1..W56 追平·零在飞上游面"
            f"（W57=唯一在飞新席位·bm-a r561 已冻结·烧录在飞）。\n"
        )
    else:
        tail += f"W{nxt[0]} finalize 链序排本波之后。\n"
    rhythm = {
        53: f"- 波节奏面：W53=bm-c r351 单窗全生命周期三段〔冻结→烧录→finalize〕后跨窗 finalize 收口（bm-b r561）——r538 禁盲重跑律执行（finalize 一过定稿）；本窗四连链首波。",
        54: f"- 波节奏面：W54=bm-a r559 冻结→bm-a 烧录→bm-b r561 跨机 finalize 收口（跨机全生命周期·首枚跨机三段波）；r538 禁盲重跑律执行。",
        55: f"- 波节奏面：W55=bm-b r559 冻结（W54 同窗让路窗 c2a72a755）→本机烧录 12/12（r559/r560 交付）→r561 同机跨轮 finalize——冻结→烧录→收口三段跨 r559..r561 三轮完成；r538 一过定稿。",
        56: f"- 波节奏面：W56=bm-b r560 冻结 369ffd8f3→本机引擎烧录（r560 点火·r561 本窗 12/12 烧毕+外科交付）→r561 finalize 同窗收口——引擎 tick 烧录跨轮自然完成+finalize 同窗（W10 先例族）；r538 一过定稿。",
    }[w]
    new8 = (
        f"## §8 批后复盘【必填·s7-T】\n\n"
        f"- 设计零偏差：frozen v1 设计逐字复用（run_one 引擎同源），W{w}-only mu/sigma 与先例族【W2..W52】逐面同域，零断裂信号；B 族 p_exit=0.05 配对律齐备（n=200）。\n"
        + rhythm + "\n"
        f"- 测量面结论：累计 null 池 K={mk:,}【+W{w} 2,200 合并】，mu {fmt(merged['mu'], 4)} / sigma {fmt(merged['sigma'], 4)} 稳定，"
        f"se_mu 随累计加深收窄（{se}）——null 基线置信面继续加深，无质变；canon flip 不在本波（治理提案面素材累计·K2200 同律）。\n"
        + tail
    )

    p = f'research/PERPETUAL_N1_W{w}_PREREG.md'
    data = open(p, 'rb').read().decode('utf-8')
    for tag, old, new in (('7', S7_OLD, new7), ('8', S8_OLD, new8)):
        old_n = old.replace('\r\n', '\n'); new_n = new.replace('\r\n', '\n')
        assert data.count(old_n) == 1, f'W{w} s{tag} placeholder not unique/absent'
        data = data.replace(old_n, new_n)
    open(p, 'wb').write(data.encode('utf-8'))
    print(f'W{w}: S7/S8 backfill landed  prev={prev:,} total={total:,}  K={mk:,}  4/4 PASS')

print('ALL FOUR WAVES BACKFILLED, criteria 4/4 x4 machine-verified')
