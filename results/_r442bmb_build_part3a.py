"""r442 bm-b: W11 builder stage-3a. stage2 -> stage3a.
Exclusion loader threading + _excluded + effective mask + engine curve +
null draw + generate-leg threading.
"""
SRC = open('results/_r442bmb_stage2.py', encoding='utf-8').read()
fails = []
done = {}


def rep(old, new, tag, count=1):
    global SRC
    n = SRC.count(old)
    if n != count:
        fails.append(f'[{tag}] expected {count} got {n}: {old[:60]!r}')
        return
    done[tag] = n
    SRC = SRC.replace(old, new)


# ================= exclusion loader =================
# heading + docstring
rep('# ------------------------------------------------ exclusion (20 real-reads)',
    '# ------------------------------------------------ exclusion (22 real-reads)',
    'excl-head')
rep('''    """Twenty real-read source faces + the frozen serialized grammar
    face (prereg sec.1), all real-read at generate time.  All prior-wave
    keys are padded to the W11 FOURTEEN-tuple with std=none (semantic-
    identity completion law).  Sources: 1 = frozen serialized grammar
    stop-gate-vol-yang-vconf-streak-tstate-amp-mom-std-none face
    (14-tuple at build); 2-12 = W1/W2/MASS (declared tl3 translation)/
    W3/W4/W5/W6/W7/W8/W9/W10 screen survivors -- W10 is NEW vs W10's
    own loader (generate-time real-read; absent at build = zero rows
    honest per prereg sec.1); 13-23 = judged products (w1_judge / MASS
    judged / w2_judge / w3_judge / w4_judge / w5_judge / w6_judge /
    w7_judge / w8_judge / w9_judge / w10_judge) -- generate-time
    real-read re-declare window (declared-unavailable -> zero rows, no
    fabrication).
    """'''.replace('W11', 'W10'), 'XXBADXX', 'excl-doc-0', count=0)
# (the above is a guard probe; real doc edit below)
rep('"""Twenty real-read source faces + the frozen serialized grammar',
    '"""Twenty-two real-read source faces + the frozen serialized grammar',
    'excl-doc1')
rep('keys are padded to the W11 FOURTEEN-tuple with mom=none (semantic-',
    'keys are padded to the W11 FOURTEEN-tuple with std=none (semantic-',
    'excl-doc2', count=0)
rep('stop-gate-vol-yang-vconf-streak-tstate-amp-mom-none face (14-tuple at',
    'stop-gate-vol-yang-vconf-streak-tstate-amp-mom-std-none face '
    '(14-tuple at', 'excl-doc3')
rep('''2-11 = W1/W2/MASS (declared tl3 translation)/W3/W4/W5/W6/
    W7/W8/W9 screen survivors -- W9 is NEW vs W9's own loader
    (generate-time real-read; absent at build = zero rows honest per
    prereg sec.1); 12-21 = judged products (w1_judge / MASS judged /
    w2_judge / w3_judge / w4_judge / w5_judge / w6_judge / w7_judge /
    w8_judge / w9_judge) -- generate-time real-read re-declare window
    (declared-unavailable -> zero rows, no fabrication).''',
    '''2-12 = W1/W2/MASS (declared tl3 translation)/W3/W4/W5/W6/
    W7/W8/W9/W10 screen survivors -- W10 is NEW vs W10's own loader
    (generate-time real-read; absent at build = zero rows honest per
    prereg sec.1); 13-23 = judged products (w1_judge / MASS judged /
    w2_judge / w3_judge / w4_judge / w5_judge / w6_judge / w7_judge /
    w8_judge / w9_judge / w10_judge) -- generate-time real-read
    re-declare window (declared-unavailable -> zero rows, no
    fabrication).''', 'excl-doc4')
# grammar face key reads (2 sites: loader + generate write gate)
rep('["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_none_face"]',
    '["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_std_none_face"]',
    'excl-facekey', count=2)
# disc key
rep('"grammar_stop_gate_vol_yang_vconf_streak_tstate_'
    '"amp_mom_none_rows": len(rows)}',
    '"grammar_stop_gate_vol_yang_vconf_streak_tstate_'
    '"amp_mom_std_none_rows": len(rows)}', 'excl-disckey')
# face strings in row payloads (screen + judged)
rep('''                         "face": f"{tag}:stop-gate-vol-yang-"
                                 "vconf-streak-tstate-amp-mom-none",''',
    '''                         "face": f"{tag}:stop-gate-vol-yang-"
                                 "vconf-streak-tstate-amp-mom-std-"
                                 "none",''', 'excl-facestr1')
rep('''                             "face": f"{tag}:stop-gate-vol-yang-"
                                     "vconf-streak-tstate-amp-mom-none",''',
    '''                             "face": f"{tag}:stop-gate-vol-"
                                     "yang-vconf-streak-tstate-amp-"
                                     "mom-std-none",''', 'excl-facestr2')
# screen pads (+1 std none each)
rep('["none"] * 9, "w1_screen_survivor")', '["none"] * 10, '
    '"w1_screen_survivor")', 'pad-w1s')
rep('["none"] * 8, "w2_screen_survivor")', '["none"] * 9, '
    '"w2_screen_survivor")', 'pad-w2s')
rep('["none"] * 7, "w3_screen_survivor")', '["none"] * 8, '
    '"w3_screen_survivor")', 'pad-w3s')
rep('["none"] * 6, "w4_screen_survivor")', '["none"] * 7, '
    '"w4_screen_survivor")', 'pad-w4s')
rep('["none"] * 5, "w5_screen_survivor")', '["none"] * 6, '
    '"w5_screen_survivor")', 'pad-w5s')
rep('["none"] * 4, "w6_screen_survivor")', '["none"] * 5, '
    '"w6_screen_survivor")', 'pad-w6s')
rep('["none"] * 3, "w7_screen_survivor")', '["none"] * 4, '
    '"w7_screen_survivor")', 'pad-w7s')
rep('["none"] * 2, "w8_screen_survivor")', '["none"] * 3, '
    '"w8_screen_survivor")', 'pad-w8s')
rep('''    disc["w9_screen_survivors"] = _screen_survivors(
        tl9.SCREEN_FILE, tl9.CANDIDATES_FILE,
        ["none"], "w9_screen_survivor")''',
    '''    disc["w9_screen_survivors"] = _screen_survivors(
        tl9.SCREEN_FILE, tl9.CANDIDATES_FILE,
        ["none"] * 2, "w9_screen_survivor")
    disc["w10_screen_survivors"] = _screen_survivors(
        tl10.SCREEN_FILE, tl10.CANDIDATES_FILE,
        ["none"], "w10_screen_survivor")''', 'pad-w9s-add-w10s')
# MASS screen pad
rep('''    # MASS screen survivors: declared tl3 translation + vol-yang-vconf-
    # streak-tstate-amp-mom none pad (translated rows are 6-tuples)''',
    '''    # MASS screen survivors: declared tl3 translation + vol-yang-vconf-
    # streak-tstate-amp-mom-std none pad (translated rows are 6-tuples)''',
    'mass-doc1')
rep('tr["axis"] = list(tr["axis"]) + ["none"] * 7\n'
    '                tr["face"] = "mass_screen_survivor:translated-exact"',
    'tr["axis"] = list(tr["axis"]) + ["none"] * 8\n'
    '                tr["face"] = "mass_screen_survivor:translated-exact"',
    'mass-pad1')
# judged doc + landing comments
rep('''    # judged products: generate-time real-read re-declare window (prereg
    # sec.1/sec.9); absent -> declared-unavailable zero rows (freeze-time
    # expectation per prereg sec.0 (d): W1/MASS/W2/W3/W4/W5/W6 judged
    # landed; W7-JUDGE landed 2026-09-29 11:42:55; W8-JUDGE landed
    # 2026-09-29 15:26:25; W9-JUDGE landed 2026-09-29 17:47:46 -- TEN
    # sources, third full-declare window in history -- live re-read at
    # generate time is the law)''',
    '''    # judged products: generate-time real-read re-declare window (prereg
    # sec.1/sec.9); absent -> declared-unavailable zero rows (freeze-time
    # expectation per prereg sec.0 (d): W1/MASS/W2/W3/W4/W5/W6 judged
    # landed; W7-JUDGE landed 2026-09-29 11:42:55; W8-JUDGE landed
    # 2026-09-29 15:26:25; W9-JUDGE landed 2026-09-29 17:47:46;
    # W10-JUDGE landed 2026-09-29 20:31:29 -- ELEVEN sources, fourth
    # full-declare window in history -- live re-read at generate time
    # is the law)''', 'judged-doc')
# MASS judged pad (mass=True branch)
rep('''                tr["axis"] = list(tr["axis"]) + ["none"] * 7
                tr["face"] = f"{tag}:translated-exact"''',
    '''                tr["axis"] = list(tr["axis"]) + ["none"] * 8
                tr["face"] = f"{tag}:translated-exact"''', 'mass-pad2')
# judged pads
rep('["none"] * 9, "w1_judged")', '["none"] * 10, "w1_judged")', 'pad-w1j')
rep('["none"] * 8, "w2_judged")', '["none"] * 9, "w2_judged")', 'pad-w2j')
rep('["none"] * 7, "w3_judged")', '["none"] * 8, "w3_judged")', 'pad-w3j')
rep('["none"] * 6, "w4_judged")', '["none"] * 7, "w4_judged")', 'pad-w4j')
rep('["none"] * 5, "w5_judged")', '["none"] * 6, "w5_judged")', 'pad-w5j')
rep('["none"] * 4, "w6_judged")', '["none"] * 5, "w6_judged")', 'pad-w6j')
rep('["none"] * 3, "w7_judged")', '["none"] * 4, "w7_judged")', 'pad-w7j')
rep('["none"] * 2, "w8_judged")', '["none"] * 3, "w8_judged")', 'pad-w8j')
rep('''    disc["w9_judge_products"] = _judged_source(
        tl9.JUDGE_FILE, tl9.CANDIDATES_FILE,
        ["none"], "w9_judged")''',
    '''    disc["w9_judge_products"] = _judged_source(
        tl9.JUDGE_FILE, tl9.CANDIDATES_FILE,
        ["none"] * 2, "w9_judged")
    disc["w10_judge_products"] = _judged_source(
        tl10.JUDGE_FILE, tl10.CANDIDATES_FILE,
        ["none"], "w10_judged")''', 'pad-w9j-add-w10j')
# weighting disclosure
rep('''"none exists, uniform stands, availability of the TEN judge "
        "products disclosed above (freeze-time ten-source full-declare "
        "window = third in history)")''',
    '''"none exists, uniform stands, availability of the ELEVEN judge "
        "products disclosed above (freeze-time eleven-source "
        "full-declare window = fourth in history)")''', 'judged-weight')

# ================= _excluded =================
rep('''    """Exact already-judged cell test, mom=none face only (prereg
    sec.1: mom in {mom_oversold} = new-syntax legal cells --
    never excluded; W1-lineage cells implicitly stop/gate/vol/yang/
    vconf/streak/tstate/amp/mom=none; W2 cells carry their own stop face;
    W3 stop+gate; W4 stop+gate+vol; W5 stop+gate+vol+yang; W6
    stop+gate+vol+yang+vconf; W7 stop+gate+vol+yang+vconf+streak; W8
    stop+gate+vol+yang+vconf+streak+tstate; W9
    stop+gate+vol+yang+vconf+streak+tstate+amp).  Returns the exclusion''',
    '''    """Exact already-judged cell test, std=none face only (prereg
    sec.1: std in {std20_hi, std10_hi} = new-syntax legal cells --
    never excluded; W1-lineage cells implicitly stop/gate/vol/yang/
    vconf/streak/tstate/amp/mom/std=none; W2 cells carry their own
    stop face; W3 stop+gate; W4 stop+gate+vol; W5 stop+gate+vol+yang;
    W6 stop+gate+vol+yang+vconf; W7 stop+gate+vol+yang+vconf+streak;
    W8 stop+gate+vol+yang+vconf+streak+tstate; W9
    stop+gate+vol+yang+vconf+streak+tstate+amp; W10 +mom).  Returns
    the exclusion''', 'excl-fn-doc')
rep('''    if cand["axis"][12] != "none":
        return None''',
    '''    if cand["axis"][13] != "none":
        return None''', 'excl-fn-key')

# ================= _effective_signal_mask =================
rep('''def _effective_signal_mask_w11(mask, prices, stop_key, atr20, gate_key,
                               vol_key, yang_key, vconf_key, streak_key,
                               tstate_key, amp_key, mom_key, gate_state,
                               vol_state, yang_state, vconf_state,
                               streak_state, tstate_state, amp_state,
                               mom_state):''',
    '''def _effective_signal_mask_w11(mask, prices, stop_key, atr20, gate_key,
                               vol_key, yang_key, vconf_key, streak_key,
                               tstate_key, amp_key, mom_key, std_key,
                               gate_state, vol_state, yang_state,
                               vconf_state, streak_state, tstate_state,
                               amp_state, mom_state, std_state):''',
    'mask-sig')
rep('''    """Dedup-face holdings proxy with the frozen composition order
    GATE -> VOL -> YANG -> VCONF -> STREAK -> TSTATE -> AMP -> MOM ->
    initial-stop (prereg sec.3 fourteen-tuple dedup legs; zero engine
    burn).  mom=none + amp=none + tstate=none + streak=none + vconf=
    none + yang=none + vol=none + gate=none + stop=none = W1 identity;
    mom=none = W9 semantic baseline; all nine overlay faces
    deterministic layers of the same grammar stack (W9 order extended
    by the mom leg, zero disturbance to the first eight)."""
    G = tl3.gate_zero_mask(mask, gate_key, gate_state)
    V = tl4.vol_zero_mask(G, vol_key, vol_state)
    Y = tl5.yang_zero_mask(V, yang_key, yang_state)
    VC = tl6.vconf_zero_mask(Y, vconf_key, vconf_state)
    SK = tl7.streak_zero_mask(VC, streak_key, streak_state)
    TS = tl8.tstate_zero_mask(SK, tstate_key, tstate_state)
    AP = tl9.amp_zero_mask(TS, amp_key, amp_state)
    MO = mom_zero_mask(AP, mom_key, mom_state)
    return tl2._effective_signal_mask(MO, prices, stop_key, atr20)''',
    '''    """Dedup-face holdings proxy with the frozen composition order
    GATE -> VOL -> YANG -> VCONF -> STREAK -> TSTATE -> AMP -> MOM ->
    STD -> initial-stop (prereg sec.3 fourteen-tuple dedup legs; zero
    engine burn).  std=none + mom=none + amp=none + tstate=none +
    streak=none + vconf=none + yang=none + vol=none + gate=none +
    stop=none = W1 identity; std=none = W10 semantic baseline; all
    ten overlay faces deterministic layers of the same grammar stack
    (W10 order extended by the std leg, zero disturbance to the first
    nine)."""
    G = tl3.gate_zero_mask(mask, gate_key, gate_state)
    V = tl4.vol_zero_mask(G, vol_key, vol_state)
    Y = tl5.yang_zero_mask(V, yang_key, yang_state)
    VC = tl6.vconf_zero_mask(Y, vconf_key, vconf_state)
    SK = tl7.streak_zero_mask(VC, streak_key, streak_state)
    TS = tl8.tstate_zero_mask(SK, tstate_key, tstate_state)
    AP = tl9.amp_zero_mask(TS, amp_key, amp_state)
    MO = mom_zero_mask(AP, mom_key, mom_state)
    SD = std_zero_mask(MO, std_key, std_state)
    return tl2._effective_signal_mask(SD, prices, stop_key, atr20)''',
    'mask-body')

# ================= run_candidate_curve =================
rep('''def run_candidate_curve_w11(cand, template, prices, P, states, atr20=None,
                           fundamental_ok=None, rng_matrix=None, p_on=None,
                           gate_state=None, vol_state=None, yang_state=None,
                           vconf_state=None, streak_state=None,
                           tstate_state=None, amp_state=None,
                           mom_state=None):''',
    '''def run_candidate_curve_w11(cand, template, prices, P, states, atr20=None,
                           fundamental_ok=None, rng_matrix=None, p_on=None,
                           gate_state=None, vol_state=None, yang_state=None,
                           vconf_state=None, streak_state=None,
                           tstate_state=None, amp_state=None,
                           mom_state=None, std_state=None):''', 'curve-sig')
rep('''    mom_key = cand["axis"][12]
    if gate_state is None:''',
    '''    mom_key = cand["axis"][12]
    std_key = cand["axis"][13]
    if gate_state is None:''', 'curve-key')
rep('''    if mom_state is None:
        mom_state = mom_state_series(prices)
    if stop_key != "none"''',
    '''    if mom_state is None:
        mom_state = mom_state_series(prices)
    if std_state is None:
        std_state = std_state_series(prices)
    if stop_key != "none"''', 'curve-lazy')
rep('''    AP = tl9.amp_zero_mask(TS, amp_key, amp_state)
    MO = mom_zero_mask(AP, mom_key, mom_state)
    gate_zeroed = int((mask > 0).sum().sum() - (G > 0).sum().sum())''',
    '''    AP = tl9.amp_zero_mask(TS, amp_key, amp_state)
    MO = mom_zero_mask(AP, mom_key, mom_state)
    SD = std_zero_mask(MO, std_key, std_state)
    gate_zeroed = int((mask > 0).sum().sum() - (G > 0).sum().sum())''',
    'curve-chain')
rep('''    mom_zeroed = int((AP > 0).sum().sum() - (MO > 0).sum().sum())
    if stop_key == "none":
        S, stop_fired = MO, 0
    else:
        S = tl2._effective_signal_mask(MO, prices, stop_key, atr20)
        d = (MO > 0) & (S == 0)''',
    '''    mom_zeroed = int((AP > 0).sum().sum() - (MO > 0).sum().sum())
    std_zeroed = int((MO > 0).sum().sum() - (SD > 0).sum().sum())
    if stop_key == "none":
        S, stop_fired = SD, 0
    else:
        S = tl2._effective_signal_mask(SD, prices, stop_key, atr20)
        d = (SD > 0) & (S == 0)''', 'curve-stop')
rep('''    return eq, res["trades"], res["metrics"], params, patch, stop_fired, \\
        gate_zeroed, vol_zeroed, yang_zeroed, vconf_zeroed, \\
        streak_zeroed, tstate_zeroed, amp_zeroed, mom_zeroed''',
    '''    return eq, res["trades"], res["metrics"], params, patch, stop_fired, \\
        gate_zeroed, vol_zeroed, yang_zeroed, vconf_zeroed, \\
        streak_zeroed, tstate_zeroed, amp_zeroed, mom_zeroed, \\
        std_zeroed''', 'curve-ret')
rep('''    vconf_zeroed, streak_zeroed, tstate_zeroed, amp_zeroed,
    mom_zeroed)."""
    stop_key = cand["axis"][4]''',
    '''    vconf_zeroed, streak_zeroed, tstate_zeroed, amp_zeroed,
    mom_zeroed, std_zeroed)."""
    stop_key = cand["axis"][4]''', 'curve-doc1')
rep('''    pinned); mom in {mom_oversold} = new W10 syntax (entry-permittance
    only, never excluded).  Returns (eq, trades, metrics, params,''',
    '''    pinned); std=none -> tl10 W10 face (parity law, selftest-pinned);
    std in {std20_hi, std10_hi} = new W11 syntax (entry-permittance
    only, never excluded).  Returns (eq, trades, metrics, params,''',
    'curve-doc2')

# ================= _null_axis_draw =================
rep('''          tl9.AXIS_AMP[int(rng.integers(len(tl9.AXIS_AMP)))],
          AXIS_MOM[int(rng.integers(len(AXIS_MOM)))])
    return p_on, list(ax), rng''',
    '''          tl9.AXIS_AMP[int(rng.integers(len(tl9.AXIS_AMP)))],
          AXIS_MOM[int(rng.integers(len(AXIS_MOM)))],
          AXIS_STD[int(rng.integers(len(AXIS_STD)))])
    return p_on, list(ax), rng''', 'null-draw')

open('results/_r442bmb_stage3a.py', 'w', encoding='utf-8').write(SRC)
print('stage3a written, lines:', SRC.count(chr(10)) + 1)
print('done:', len(done), 'fails:', len(fails))
for f in fails:
    print(' FAIL', f)
