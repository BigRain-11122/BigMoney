# -*- coding: utf-8 -*-
"""r590 bm-a W112 anchor-roll #2: W108 -> W110 (r576 law chain: the prereg is
still un-committed on origin; bm-b r590 drained the whole 3-wave backlog
MID-FREEZE-WINDOW -- 86a8178fd W109 finalize (bm-b owned) + 07e8b2ebc W110
finalize (on behalf of bm-a per the W108 cross-machine precedent).
Rolled keys from results/perpetual_faces/n1_w110_results.json (origin face):
merged mu -0.09271653342780928 / sigma 0.24487617466590078 / K=239,920 /
chain head 606,548 / K-lift 0.0000 / A-p95 0.3159 / se_mu 0.0005."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load(fp):
    b = open(fp, 'rb').read()
    t = b.decode('utf-8')
    eol = '\r\n' if t.count('\r\n') * 2 > t.count('\n') else '\n'
    return t, eol

def save(fp, t):
    open(fp, 'wb').write(t.encode('utf-8'))

def rep(fp, old, new, tag, count=1):
    t, eol = load(fp)
    o = old.replace('\n', eol)
    n = new.replace('\n', eol)
    if n in t and o not in t:
        print('roll skip (already applied):', tag)
        return
    c = t.count(o)
    assert c == count, f'{tag}: anchor count {c} != {count}: {old[:60]!r}'
    t = t.replace(o, n)
    save(fp, t)
    print('roll ok:', tag)

P = os.path.join(REPO, 'research', 'PERPETUAL_N1_W112_PREREG.md')
N1 = os.path.join(REPO, 'scripts', 'perpetual_faces_n1.py')
PF = os.path.join(REPO, 'scripts', 'perpetual_faces.py')
CN = os.path.join(REPO, 'research', 'PERPETUAL_FACES.md')

# 1. prereg sec.0 ledger reality
rep(P,
    "起草窗实况：**W1..W108 N1 finalize 已全部落账**——净账本链头 **602,148**（bm-b r590 cross-machine finalize W108 代 bm-c 落账〔one-pass·burn by bm-c 12/12 交付·audit.machine=bm-b finalize_only=true 诚实归因·起草窗中段落账=锚随锚滚动律自 W107 滚至 W108·r576 锚滚律如实披露〕·K=235,520 合并池·voids LOWAMP-P1/P2）；**W109 bm-b finalize 未落账+W110 bm-a finalize 未落账+W111 bm-b finalize 未落账（三席 registered=本波 finalize 时 FAIL-CLOSED 前置三空档**（跑时复核；W109/W110 12/12 烧毕产物均已交付 origin·W111 烧录 bm-b 车道在飞）；累计 null 池投影=235,520+2,200×3（W109..W111）+2,200（本波）=**244,320 投影**（机械算：235,520+8,800；",
    "起草窗实况：**W1..W110 N1 finalize 已全部落账**——净账本链头 **606,548**（bm-b r590 三波积压清空 cross-machine finalize〔W108 代 bm-c+W109 bm-b 自有+W110 代 bm-a·audit.machine=bm-b finalize_only=true 诚实归因·起草窗双中窗落账=锚随锚滚动律自 W107 滚至 W108 再滚至 W110·r576 锚滚律如实披露〕·K=239,920 合并池·voids LOWAMP-P1/P2）；**W111 bm-b finalize 未落账（一席 registered=本波 finalize 时 FAIL-CLOSED 前置一空档**（跑时复核；W111 烧录 bm-b 车道在飞）；累计 null 池投影=239,920+2,200（W111）+2,200（本波）=**244,320 投影**（机械算：239,920+4,400；",
    'prereg-sec0')

# 2. prereg sec.4 pool
rep(P,
    "合并池 `canon 120 + 已落账波值（起草窗实测 W1..W108 已落账 235,520 实测·derive 禁手抄）+本波 2,200`",
    "合并池 `canon 120 + 已落账波值（起草窗实测 W1..W110 已落账 239,920 实测·derive 禁手抄）+本波 2,200`",
    'prereg-sec4-pool')

# 3. prereg sec.5 preamble
rep(P,
    "（起草窗实况注记：**W1..W108 N1 finalize 已全部落账**——净账本链头 602,148=bm-b r590 cross-machine finalize W108 代 bm-c 落账〔one-pass·起草窗中段落账·锚滚动律自 W107 滚至 W108·r576 锚滚律如实披露〕·**K=235,520 合并池**；**W109/W110/W111 三空档在飞**（本波 §5 预测键=**W108 finalize 实测值**〔results/perpetual_faces/n1_w108_results.json·N1 面最新已落账键〕）。",
    "（起草窗实况注记：**W1..W110 N1 finalize 已全部落账**——净账本链头 606,548=bm-b r590 三波积压清空 cross-machine finalize〔W108 代 bm-c+W109 bm-b 自有+W110 代 bm-a·起草窗双中窗落账·锚滚动律自 W107 滚至 W108 再滚至 W110·r576 锚滚律如实披露〕·**K=239,920 合并池**；**W111 一空档在飞**（本波 §5 预测键=**W110 finalize 实测值**〔results/perpetual_faces/n1_w110_results.json·N1 面最新已落账键〕）。",
    'prereg-sec5-pre')

# 4-7. prereg sec.5 items
rep(P,
    "1. W112-only mu 与累计池 merged mu（W108 实测键 **−0.09266817000679399**·K=235,520 合并池·W108-only 实测 **−0.08290963636363624**）差异 **|Δ|<0.02**（W2..W108 共三十+面实测 mu 稳定先例·单波跨键律）。",
    "1. W112-only mu 与累计池 merged mu（W110 实测键 **−0.09271653342780928**·K=239,920 合并池·W110-only 实测 **−0.10390695454545468**）差异 **|Δ|<0.02**（W2..W110 共三十+面实测 mu 稳定先例·单波跨键律）。",
    'prereg-item1')
rep(P,
    "2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.2448695789393584**=W108 合并池实测）。",
    "2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.24487617466590078**=W110 合并池实测）。",
    'prereg-item2')
rep(P,
    "3. A 档 full_sharpe_p95 与 W108 A 档 p95（**0.3291** 实测锚）差 **<0.05**（门标准注记法 W5..W108 先例：结果知情报校准面·仅作机器断言伪测用·测量面非注册利益）。",
    "3. A 档 full_sharpe_p95 与 W110 A 档 p95（**0.3159** 实测锚）差 **<0.05**（门标准注记法 W5..W110 先例：结果知情报校准面·仅作机器断言伪测用·测量面非注册利益）。",
    'prereg-item3')
rep(P,
    "4. K-lift 线移动幅度 **≥−0.02**（累计池加深零 se_mu·线自 mu/sigma 微调面非质变——W3..W108 先例·W99 +0.0001/W100 −0.0005/W101 −0.0003/W103 +0.0005/W104 −0.0001/W105 −0.0002/W106 **+0.0002**/W107 **−0.0002**/W108 **+0.0003** 正负交替如实报正负）；键 W108 实测 K-lift **+0.0003**（line_merged@K235,520 **1.1705**·line_pre 1.1702·n_eff_held 599,948；se_mu 收窄链 W106 0.000509→W107 0.000507→W108 **0.000505**）。",
    "4. K-lift 线移动幅度 **≥−0.02**（累计池加深零 se_mu·线自 mu/sigma 微调面非质变——W3..W110 先例·W99 +0.0001/W100 −0.0005/W101 −0.0003/W103 +0.0005/W104 −0.0001/W105 −0.0002/W106 **+0.0002**/W107 **−0.0002**/W108 **+0.0003**/W109 **0.0000**/W110 **0.0000** 正负交替如实报正负）；键 W110 实测 K-lift **0.0000**（line_merged@K239,920 **1.1708**·line_pre 1.1708·n_eff_held 604,348；se_mu 收窄链 W107 0.000507→W108 0.000505→W109 0.000502→W110 **0.0005**）。",
    'prereg-item4')

# 8. n1 config string
rep(N1,
    '"the next freezer); W108 finalize LANDED (chain head 602,148, "\n'
    '                                       "K=235,520, bm-b r590 cross-machine finalize one-pass on "\n'
    '                                       "behalf of bm-c) + THREE in-flight upstream seats W109 bm-b "\n'
    '                                       "+ W110 bm-a + W111 bm-b registered-unfinalized -- finalize "\n'
    '                                       "merge loop stays "',
    '"the next freezer); W110 finalize LANDED (chain head 606,548, "\n'
    '                                       "K=239,920, bm-b r590 three-wave backlog drain cross-machine "\n'
    '                                       "finalize one-pass: W108 on behalf of bm-c + W109 bm-b owned "\n'
    '                                       "+ W110 on behalf of bm-a) + ONE in-flight upstream seat W111 "\n'
    '                                       "bm-b registered-unfinalized -- finalize merge loop stays "',
    'n1-config-roll')

# 9. n1 leg head
rep(N1,
    "    #     governs per r359 law). W108 finalize LANDED (chain head\n"
    "    #     602,148, K=235,520, bm-b r590 cross-machine finalize one-pass\n"
    "    #     on behalf of bm-c, honest attribution) + THREE in-flight\n"
    "    #     upstream seats W109 bm-b + W110 bm-a + W111 bm-b registered,\n"
    "    #     finalizes NOT landed -- FAIL-CLOSED r307 at run time.",
    "    #     governs per r359 law). W110 finalize LANDED (chain head\n"
    "    #     606,548, K=239,920, bm-b r590 three-wave backlog drain\n"
    "    #     cross-machine finalize one-pass: W108 for bm-c + W109 bm-b\n"
    "    #     owned + W110 for bm-a, honest attribution) + ONE in-flight\n"
    "    #     upstream seat W111 bm-b registered, finalize NOT landed --\n"
    "    #     FAIL-CLOSED r307 at run time.",
    'n1-leg-head')

# 10. n1 leg deps
rep(N1,
    "        # W112 finalize cumulative deps: W17..W108 outputs ALL PRESENT\n"
    "        # (landed chain head 602,148 = W108 bm-b r590 cross-machine\n"
    "        # finalize; W109/W110/W111 registered with finalizes NOT landed\n"
    "        # -- in-flight upstream seats, honest note; the finalize merge\n"
    "        # loop derives the wave set from registry keys at run time and\n"
    "        # stays FAIL-CLOSED, r307 law).\n"
    "        for _depw in range(17, 109):",
    "        # W112 finalize cumulative deps: W17..W110 outputs ALL PRESENT\n"
    "        # (landed chain head 606,548 = W110 bm-b r590 three-wave backlog\n"
    "        # drain cross-machine finalize; W111 registered with finalize\n"
    "        # NOT landed -- in-flight upstream seat, honest note; the\n"
    "        # finalize merge loop derives the wave set from registry keys\n"
    "        # at run time and stays FAIL-CLOSED, r307 law).\n"
    "        for _depw in range(17, 111):",
    'n1-leg-deps')

# 11. n1 summary
rep(N1,
    '"+ W112 materializer face [same guard set, dep=W17..W108 "\n'
    '"outputs ALL PRESENT (landed chain head 602,148 = W108 bm-b r590 "\n'
    '"cross-machine finalize one-pass on behalf of bm-c, K=235,520; "\n'
    '"THREE in-flight upstream seats W109 bm-b + W110 bm-a + W111 bm-b "\n'
    '"registered, finalizes NOT landed -- FAIL-CLOSED r307 at run time), ONE "\n',
    '"+ W112 materializer face [same guard set, dep=W17..W110 "\n'
    '"outputs ALL PRESENT (landed chain head 606,548 = W110 bm-b r590 "\n'
    '"three-wave backlog drain cross-machine finalize one-pass "\n'
    '"(W108 for bm-c + W109 bm-b owned + W110 for bm-a), K=239,920; "\n'
    '"ONE in-flight upstream seat W111 bm-b registered, finalize NOT "\n'
    '"landed -- FAIL-CLOSED r307 at run time), ONE "\n',
    'n1-summary-roll')

# 12. pf comment
rep(PF,
    "    # orphaned-never-visible, rev.A = only published face). W108\n"
    "    # finalize LANDED (chain head 602,148, K=235,520 = bm-b r590\n"
    "    # cross-machine finalize one-pass on behalf of bm-c). THREE\n"
    "    # in-flight upstream seats (W109 bm-b + W110 bm-a + W111 bm-b\n"
    "    # registered, finalizes NOT landed) -- finalize merge loop stays\n"
    "    # FAIL-CLOSED r307 at run time.\n",
    "    # orphaned-never-visible, rev.A = only published face). W110\n"
    "    # finalize LANDED (chain head 606,548, K=239,920 = bm-b r590\n"
    "    # three-wave backlog drain cross-machine finalize one-pass:\n"
    "    # W108 on behalf of bm-c + W109 bm-b owned + W110 on behalf of\n"
    "    # bm-a). ONE in-flight upstream seat (W111 bm-b registered,\n"
    "    # finalize NOT landed) -- finalize merge loop stays\n"
    "    # FAIL-CLOSED r307 at run time.\n",
    'pf-comment-roll')

# 13. canon reality
rep(CN,
    "本窗实况=**W108 finalize 已落账（净链头 602,148·K=235,520 合并池·bm-b r590 cross-machine finalize 代 bm-c 落账〔burn by bm-c 12/12 交付·audit.machine=bm-b 诚实归因〕·起草窗中段落账=锚随锚滚动律自 W107 滚至 W108·r576 锚滚律如实披露）+三在飞上游席（W109 bm-b+W110 bm-a+W111 bm-b registered 烧毕或在飞 finalize 待）=本波 finalize 链序前置在飞（跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）**",
    "本窗实况=**W110 finalize 已落账（净链头 606,548·K=239,920 合并池·bm-b r590 三波积压清空 cross-machine finalize〔W108 代 bm-c+W109 bm-b 自有+W110 代 bm-a·audit.machine=bm-b 诚实归因〕·起草窗双中窗落账=锚随锚滚动律自 W107 滚至 W108 再滚至 W110·r576 锚滚律如实披露）+一在飞上游席（W111 bm-b registered 烧录在飞 finalize 待）=本波 finalize 链序前置在飞（跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）**",
    'canon-reality-roll')

# 14. canon anchor
rep(CN,
    "per-wave prereg=research/PERPETUAL_N1_W112_PREREG.md（冻结件·锚=W108 finalize 实测值〔merged mu −0.09266817000679399·K=235,520·K-lift +0.0003·A-p95 0.3291·se_mu 0.000505·锚滚动律自 W107 滚至 W108 r576〕）",
    "per-wave prereg=research/PERPETUAL_N1_W112_PREREG.md（冻结件·锚=W110 finalize 实测值〔merged mu −0.09271653342780928·K=239,920·K-lift 0.0000·A-p95 0.3159·se_mu 0.0005·锚滚动律自 W107 滚至 W108 再滚至 W110 r576 双中窗〕）",
    'canon-anchor-roll')

print('ANCHOR_ROLL2_OK 108->110')
