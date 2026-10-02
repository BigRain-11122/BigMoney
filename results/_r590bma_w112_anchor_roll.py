# -*- coding: utf-8 -*-
"""r590 bm-a W112 anchor-roll W107 -> W108 (r576 law: prereg un-committed on
origin = refreshable; bm-b r590 landed the W108 chain-head finalize
cross-machine on behalf of bm-c MID-DRAFT-WINDOW, 763d2e2c3, chain head
602,148 / K=235,520 / K-lift +0.0003 / A-p95 0.3291 / se_mu 0.000505).
Updates ONLY the W112-inserted content (pure insertion vs origin preserved,
FIX-C holds). Receipt tools left untouched (they document what actually ran
pre-W108-landing; the roll is disclosed in the freeze commit message)."""
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

# ---- A. prereg: sec.0 ledger reality ------------------------------------------
rep(P,
    "起草窗实况：**W1..W107 N1 finalize 已全部落账**——净账本链头 **599,948**（bm-a r589 closing W107 落账〔one-pass〕·K=233,320 合并池·voids LOWAMP-P1/P2）；**W108 bm-c finalize 未落账+W109 bm-b finalize 未落账+W110 bm-a finalize 未落账+W111 bm-b finalize 未落账（四席 registered=本波 finalize 时 FAIL-CLOSED 前置四空档**（跑时复核；W108/W109/W110 12/12 烧毕产物均已交付 origin·W111 烧录本窗在飞 3/12）；累计 null 池投影=233,320+2,200×4（W108..W111）+2,200（本波）=**244,320 投影**（机械算：233,320+11,000；",
    "起草窗实况：**W1..W108 N1 finalize 已全部落账**——净账本链头 **602,148**（bm-b r590 cross-machine finalize W108 代 bm-c 落账〔one-pass·burn by bm-c 12/12 交付·audit.machine=bm-b finalize_only=true 诚实归因·起草窗中段落账=锚随锚滚动律自 W107 滚至 W108·r576 锚滚律如实披露〕·K=235,520 合并池·voids LOWAMP-P1/P2）；**W109 bm-b finalize 未落账+W110 bm-a finalize 未落账+W111 bm-b finalize 未落账（三席 registered=本波 finalize 时 FAIL-CLOSED 前置三空档**（跑时复核；W109/W110 12/12 烧毕产物均已交付 origin·W111 烧录 bm-b 车道在飞）；累计 null 池投影=235,520+2,200×3（W109..W111）+2,200（本波）=**244,320 投影**（机械算：235,520+8,800；",
    'prereg-sec0')

rep(P,
    "合并池 `canon 120 + 已落账波值（起草窗实测 W1..W107 已落账 233,320 实测·derive 禁手抄）+本波 2,200`",
    "合并池 `canon 120 + 已落账波值（起草窗实测 W1..W108 已落账 235,520 实测·derive 禁手抄）+本波 2,200`",
    'prereg-sec4-pool')

# ---- B. prereg: sec.5 preamble + items 1-4 --------------------------------------
rep(P,
    "（起草窗实况注记：**W1..W107 N1 finalize 已全部落账**——净账本链头 599,948=bm-a r589 closing W107 落账〔one-pass〕·**K=233,320 合并池**；**W108/W109/W110/W111 四空档在飞**（本波 §5 预测键=**W107 finalize 实测值**〔results/perpetual_faces/n1_w107_results.json·N1 面最新已落账键〕）。",
    "（起草窗实况注记：**W1..W108 N1 finalize 已全部落账**——净账本链头 602,148=bm-b r590 cross-machine finalize W108 代 bm-c 落账〔one-pass·起草窗中段落账·锚滚动律自 W107 滚至 W108·r576 锚滚律如实披露〕·**K=235,520 合并池**；**W109/W110/W111 三空档在飞**（本波 §5 预测键=**W108 finalize 实测值**〔results/perpetual_faces/n1_w108_results.json·N1 面最新已落账键〕）。",
    'prereg-sec5-pre')

rep(P,
    "1. W112-only mu 与累计池 merged mu（W107 实测键 **−0.0927601842962455**·K=233,320 合并池·W107-only 实测 **−0.09942518181818182**）差异 **|Δ|<0.02**（W2..W107 共三十+面实测 mu 稳定先例·单波跨键律）。",
    "1. W112-only mu 与累计池 merged mu（W108 实测键 **−0.09266817000679399**·K=235,520 合并池·W108-only 实测 **−0.08290963636363624**）差异 **|Δ|<0.02**（W2..W108 共三十+面实测 mu 稳定先例·单波跨键律）。",
    'prereg-item1')

rep(P,
    "2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.24483467386933913**=W107 合并池实测）。",
    "2. sigma 相对变化 **<±10%**（同设计同窗·纯抽样波动；键 **0.2448695789393584**=W108 合并池实测）。",
    'prereg-item2')

rep(P,
    "3. A 档 full_sharpe_p95 与 W107 A 档 p95（**0.3109** 实测锚）差 **<0.05**（门标准注记法 W5..W107 先例：结果知情报校准面·仅作机器断言伪测用·测量面非注册利益）。",
    "3. A 档 full_sharpe_p95 与 W108 A 档 p95（**0.3291** 实测锚）差 **<0.05**（门标准注记法 W5..W108 先例：结果知情报校准面·仅作机器断言伪测用·测量面非注册利益）。",
    'prereg-item3')

rep(P,
    "4. K-lift 线移动幅度 **≥−0.02**（累计池加深零 se_mu·线自 mu/sigma 微调面非质变——W3..W107 先例·W99 +0.0001/W100 −0.0005/W101 −0.0003/W103 +0.0005/W104 −0.0001/W105 −0.0002/W106 **+0.0002**/W107 **−0.0002** 正负交替如实报正负）；键 W107 实测 K-lift **−0.0002**（line_merged@K233,320 **1.17**·line_pre 1.1702·n_eff_held 597,748；se_mu 收窄链 W105 0.000512→W106 0.000509→W107 **0.000507**）。",
    "4. K-lift 线移动幅度 **≥−0.02**（累计池加深零 se_mu·线自 mu/sigma 微调面非质变——W3..W108 先例·W99 +0.0001/W100 −0.0005/W101 −0.0003/W103 +0.0005/W104 −0.0001/W105 −0.0002/W106 **+0.0002**/W107 **−0.0002**/W108 **+0.0003** 正负交替如实报正负）；键 W108 实测 K-lift **+0.0003**（line_merged@K235,520 **1.1705**·line_pre 1.1702·n_eff_held 599,948；se_mu 收窄链 W106 0.000509→W107 0.000507→W108 **0.000505**）。",
    'prereg-item4')

# ---- C. n1.py WAVE_CONFIGS[112] prereg description string -----------------------
rep(N1,
    '"the next freezer); W107 finalize LANDED (chain head 599,948, "\n'
    '                                       "K=233,320, bm-a r589 closing one-pass) + FOUR in-flight "\n'
    '                                       "upstream seats W108 bm-c + W109 bm-b + W110 bm-a + W111 bm-b "\n'
    '                                       "registered-unfinalized -- finalize merge loop stays "',
    '"the next freezer); W108 finalize LANDED (chain head 602,148, "\n'
    '                                       "K=235,520, bm-b r590 cross-machine finalize one-pass on "\n'
    '                                       "behalf of bm-c) + THREE in-flight upstream seats W109 bm-b "\n'
    '                                       "+ W110 bm-a + W111 bm-b registered-unfinalized -- finalize "\n'
    '                                       "merge loop stays "',
    'n1-config-roll')

# ---- C2. n1.py W112 selftest leg head comment -------------------------------------
rep(N1,
    "    #     governs per r359 law). W107 finalize LANDED (chain head\n"
    "    #     599,948, K=233,320, bm-a r589 closing one-pass) + FOUR\n"
    "    #     in-flight upstream seats W108 bm-c + W109 bm-b + W110 bm-a +\n"
    "    #     W111 bm-b registered, finalizes NOT landed -- FAIL-CLOSED\n"
    "    #     r307 at run time.",
    "    #     governs per r359 law). W108 finalize LANDED (chain head\n"
    "    #     602,148, K=235,520, bm-b r590 cross-machine finalize one-pass\n"
    "    #     on behalf of bm-c, honest attribution) + THREE in-flight\n"
    "    #     upstream seats W109 bm-b + W110 bm-a + W111 bm-b registered,\n"
    "    #     finalizes NOT landed -- FAIL-CLOSED r307 at run time.",
    'n1-leg-head')

rep(N1,
    "        # W112 finalize cumulative deps: W17..W107 outputs ALL PRESENT\n"
    "        # (landed chain head 599,948 = W107 bm-a r589 closing; W108/W109/\n"
    "        # W110/W111 registered with finalizes NOT landed -- in-flight\n"
    "        # upstream seats, honest note; the finalize merge loop derives\n"
    "        # the wave set from registry keys at run time and stays\n"
    "        # FAIL-CLOSED, r307 law).\n"
    "        for _depw in range(17, 108):",
    "        # W112 finalize cumulative deps: W17..W108 outputs ALL PRESENT\n"
    "        # (landed chain head 602,148 = W108 bm-b r590 cross-machine\n"
    "        # finalize; W109/W110/W111 registered with finalizes NOT landed\n"
    "        # -- in-flight upstream seats, honest note; the finalize merge\n"
    "        # loop derives the wave set from registry keys at run time and\n"
    "        # stays FAIL-CLOSED, r307 law).\n"
    "        for _depw in range(17, 109):",
    'n1-leg-deps')

# ---- D. n1.py SUMMARY W112 segment ----------------------------------------------
rep(N1,
    '"+ W112 materializer face [same guard set, dep=W17..W107 "\n'
    '"outputs ALL PRESENT (landed chain head 599,948 = W107 "\n'
    '"bm-a r589 closing one-pass, K=233,320; FOUR in-flight upstream "\n'
    '"seats W108 bm-c + W109 bm-b + W110 bm-a + W111 bm-b registered, "\n'
    '"finalizes NOT landed -- FAIL-CLOSED r307 at run time), ONE "\n',
    '"+ W112 materializer face [same guard set, dep=W17..W108 "\n'
    '"outputs ALL PRESENT (landed chain head 602,148 = W108 bm-b r590 "\n'
    '"cross-machine finalize one-pass on behalf of bm-c, K=235,520; "\n'
    '"THREE in-flight upstream seats W109 bm-b + W110 bm-a + W111 bm-b "\n'
    '"registered, finalizes NOT landed -- FAIL-CLOSED r307 at run time), ONE "\n',
    'n1-summary-roll')

# ---- E. pf.py W112 comment block --------------------------------------------------
rep(PF,
    "    # freeze per r565 early-visibility law (surgical commit-tree over\n"
    "    # bm-b r589 closing 3b7da8dfe mid-window origin advance, payload=1\n"
    "    # seat MSG, deletion-set EMPTY; first draft commit 24cd47c87\n"
    "    # orphaned-never-visible, rev.A = only published face). W107\n"
    "    # finalize LANDED (chain head 599,948, K=233,320 = bm-a r589\n"
    "    # closing one-pass). FOUR in-flight upstream seats (W108 bm-c +\n"
    "    # W109 bm-b + W110 bm-a + W111 bm-b registered, finalizes NOT\n"
    "    # landed) -- finalize merge loop stays FAIL-CLOSED r307 at\n"
    "    # run time.\n",
    "    # freeze per r565 early-visibility law (surgical commit-tree over\n"
    "    # bm-b r589 closing 3b7da8dfe mid-window origin advance, payload=1\n"
    "    # seat MSG, deletion-set EMPTY; first draft commit 24cd47c87\n"
    "    # orphaned-never-visible, rev.A = only published face). W108\n"
    "    # finalize LANDED (chain head 602,148, K=235,520 = bm-b r590\n"
    "    # cross-machine finalize one-pass on behalf of bm-c). THREE\n"
    "    # in-flight upstream seats (W109 bm-b + W110 bm-a + W111 bm-b\n"
    "    # registered, finalizes NOT landed) -- finalize merge loop stays\n"
    "    # FAIL-CLOSED r307 at run time.\n",
    'pf-comment-roll')

# ---- F. canon W112 row ------------------------------------------------------------
rep(CN,
    "本窗实况=**W107 finalize 已落账（净链头 599,948·K=233,320 合并池·bm-a r589 closing one-pass）+四在飞上游席（W108 bm-c+W109 bm-b+W110 bm-a+W111 bm-b registered 烧毕或在飞 finalize 待）=本波 finalize 链序前置在飞（跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）**",
    "本窗实况=**W108 finalize 已落账（净链头 602,148·K=235,520 合并池·bm-b r590 cross-machine finalize 代 bm-c 落账〔burn by bm-c 12/12 交付·audit.machine=bm-b 诚实归因〕·起草窗中段落账=锚随锚滚动律自 W107 滚至 W108·r576 锚滚律如实披露）+三在飞上游席（W109 bm-b+W110 bm-a+W111 bm-b registered 烧毕或在飞 finalize 待）=本波 finalize 链序前置在飞（跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）**",
    'canon-reality-roll')

rep(CN,
    "per-wave prereg=research/PERPETUAL_N1_W112_PREREG.md（冻结件·锚=W107 finalize 实测值〔merged mu −0.0927601842962455·K=233,320·K-lift −0.0002·A-p95 0.3109·se_mu 0.000507〕）",
    "per-wave prereg=research/PERPETUAL_N1_W112_PREREG.md（冻结件·锚=W108 finalize 实测值〔merged mu −0.09266817000679399·K=235,520·K-lift +0.0003·A-p95 0.3291·se_mu 0.000505·锚滚动律自 W107 滚至 W108 r576〕）",
    'canon-anchor-roll')

print('ANCHOR_ROLL_OK 107->108')
