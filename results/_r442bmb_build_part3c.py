"""r442 bm-b: W11 builder stage-3c (complete). stage3b -> stage3c.
screen prep/worker/finalize + judge overlay/cell/prep/cmd/finalize +
intake + W10-NULL + seed faces.
"""
SRC = open('results/_r442bmb_stage3b.py', encoding='utf-8').read()
fails = []
done = []


def rep(old, new, tag, count=1):
    global SRC
    n = SRC.count(old)
    if n != count:
        fails.append(f'[{tag}] expected {count} got {n}: {old[:60]!r}')
        return
    done.append(tag)
    SRC = SRC.replace(old, new)


# ============ screen prep ============
rep('''    mom_state_full, mom_err = _mom_state_full()
    if mom_err:
        print(f"PREP-GATE FAIL: G-MOM {mom_err}")
        return 1
    mom_meta_core = mom_state_full[2]
''',
    '''    mom_state_full, mom_err = _mom_state_full()
    if mom_err:
        print(f"PREP-GATE FAIL: G-MOM {mom_err}")
        return 1
    mom_meta_core = mom_state_full[2]

    # G-STD on the raw full-history face (prereg sec.2 probe basis =
    # data/daily/sh510300.csv close; 120-bar warmup + probe anchors
    # decidable 3,363 / open 391 / std10 3363/399 + eight-gate 256-cell
    # 103/153 law + extreme-day 2/7 std20-open states)
    std_state_full, std_err = _std_state_full()
    if std_err:
        print(f"PREP-GATE FAIL: G-STD {std_err}")
        return 1
    std_meta_core = std_state_full[2]
''', 'prep-std-gate')
rep('''                "axis": list(tl1.DEFAULT_AXIS)
                + ["none", "none", "none", "none", "none", "none",
                   "none", "none", "none"]}''',
    '''                "axis": list(tl1.DEFAULT_AXIS)
                + ["none", "none", "none", "none", "none", "none",
                   "none", "none", "none", "none"]}''', 'prep-anchor-axis')
rep('''    for member, gate_name in ((tl7.STREAK_MEMBER, "streak"),
                              (tl8.TSTATE_MEMBER, "tstate"),
                              (AMP_MEMBER, "amp"),
                              (MOM_MEMBER, "mom")):''',
    '''    for member, gate_name in ((tl7.STREAK_MEMBER, "streak"),
                              (tl8.TSTATE_MEMBER, "tstate"),
                              (AMP_MEMBER, "amp"),
                              (MOM_MEMBER, "mom"),
                              (STD_MEMBER, "std")):''', 'prep-member-loop')
rep('''    _, _, mom_meta = mom_state_series(prices)
    if not _mom_structure_pass(mom_meta):
        print(f"PREP-GATE FAIL: G-MOM leg-L structural invariants "
              f"broken {mom_meta} -- honest refuse")
        return 1
''',
    '''    _, _, mom_meta = mom_state_series(prices)
    if not _mom_structure_pass(mom_meta):
        print(f"PREP-GATE FAIL: G-MOM leg-L structural invariants "
              f"broken {mom_meta} -- honest refuse")
        return 1
    _o20, _d20, std_meta, _o10, _d10 = std_state_series(prices)
    if not _std_structure_pass(std_meta):
        print(f"PREP-GATE FAIL: G-STD leg-L structural invariants "
              f"broken {std_meta} -- honest refuse")
        return 1
''', 'prep-legL-std')
rep('''                                 "core48": mom_meta_core,
                                 "legL": mom_meta,''',
    '''                                 "core48": mom_meta_core,
                                 "legL": mom_meta,
                                 "core48_std": std_meta_core,
                                 "legL_std": std_meta,''', 'prep-out-meta')
rep('''                                     "core48_mom_open_rate":
                                     MOM_ANCHOR["core48_mom_open_rate"],''',
    '''                                     "core48_mom_open_rate":
                                     MOM_ANCHOR["core48_mom_open_rate"],
                                     "core48_std20_open_rate":
                                     STD_ANCHOR["core48_std20_open_rate"],''',
    'prep-out-c48')
rep('''            "amp_meta": amp_meta, "mom_meta": mom_meta,''',
    '''            "amp_meta": amp_meta, "mom_meta": mom_meta,
            "std_meta": std_meta,''', 'prep-out-metas')
rep('''    print(f"mom meta L/D 139-bar-warmup "
          f"{mom_meta['L']['open_days']}open/"
          f"{mom_meta['L']['closed_days']}closed decidable "
          f"{mom_meta['L']['decidable_days']}")''',
    '''    print(f"mom meta L/D 139-bar-warmup "
          f"{mom_meta['L']['open_days']}open/"
          f"{mom_meta['L']['closed_days']}closed decidable "
          f"{mom_meta['L']['decidable_days']}")
    print(f"std meta L 120-bar-warmup "
          f"{std_meta['L']['open_days']}open/"
          f"{std_meta['L']['closed_days']}closed decidable "
          f"{std_meta['L']['decidable_days']} std10-open "
          f"{std_meta['L']['std10_open_days']}")''', 'prep-print')

# ============ screen worker state ============
rep('''    mom_state = mom_state_series(prices)''',
    '''    mom_state = mom_state_series(prices)
    std_state = std_state_series(prices)''', 'scr-worker-state')
rep('''              "mom_state": mom_state}''',
    '''              "mom_state": mom_state,
              "std_state": std_state}''', 'scr-worker-dict')
rep('''f"W10-NULL-{cell['i']:04d}"''', '''f"W11-NULL-{cell['i']:04d}"''',
    'null-cid')

# ============ screen finalize ============
rep('''        mom_counts[mf] = mom_counts.get(mf, 0) + 1''',
    '''        mom_counts[mf] = mom_counts.get(mf, 0) + 1
        std_counts[stf] = std_counts.get(stf, 0) + 1''', 'fin-count')
rep('''                         (amp_seg, af), (mom_seg, mf),''',
    '''                         (amp_seg, af), (mom_seg, mf),
                         (std_seg, stf),''', 'fin-seglist')
rep('''                         (gvvvsktsam_seg,
                          f"{gf}|{vf}|{yf}|{cf}|{sf}|{tf}|{af}|{mf}")):''',
    '''                         (gvvvsktsam_seg,
                          f"{gf}|{vf}|{yf}|{cf}|{sf}|{tf}|{af}|{mf}"),
                         (gvvvsktsams_seg,
                          f"{gf}|{vf}|{yf}|{cf}|{sf}|{tf}|{af}|{mf}|"
                          f"{stf}")):''', 'fin-seglist2')
rep('''    for seg in (gate_seg, vol_seg, yang_seg, vconf_seg, streak_seg,
                tstate_seg, amp_seg, mom_seg, gvvy_seg, gvvvsk_seg,
                gvvvskts_seg, gvvvsktsa_seg, gvvvsktsam_seg):''',
    '''    for seg in (gate_seg, vol_seg, yang_seg, vconf_seg, streak_seg,
                tstate_seg, amp_seg, mom_seg, std_seg, gvvy_seg,
                gvvvsk_seg, gvvvskts_seg, gvvvsktsa_seg,
                gvvvsktsam_seg, gvvvsktsams_seg):''', 'fin-segtuple')
rep('''    mom_meta = prep.get("mom_meta")''',
    '''    mom_meta = prep.get("mom_meta")
    std_meta = prep.get("std_meta")''', 'fin-prepget')
rep('''           "mom_face_counts": mom_counts,''',
    '''           "mom_face_counts": mom_counts,
           "std_face_counts": std_counts,''', 'fin-out-fc')
rep('''           "mom_segmented_survival": mom_seg,''',
    '''           "mom_segmented_survival": mom_seg,
           "std_segmented_survival": std_seg,''', 'fin-out-seg')
rep('''           "gate_vol_yang_vconf_streak_tstate_amp_mom_interaction_"
           "survival": gvvvsktsam_seg,''',
    '''           "gate_vol_yang_vconf_streak_tstate_amp_mom_interaction_"
           "survival": gvvvsktsam_seg,
           "gate_vol_yang_vconf_streak_tstate_amp_mom_std_interaction_"
           "survival": gvvvsktsams_seg,''', 'fin-out-int')
rep('''           "mom_na_window_bars": (mom_meta["na_window_bars"]
                                   if mom_meta else None),''',
    '''           "mom_na_window_bars": (mom_meta["na_window_bars"]
                                   if mom_meta else None),
           "std_na_window_bars": (std_meta["na_window_bars"]
                                   if std_meta else None),''',
    'fin-out-nawin')
rep('''                              "mom 139-bar warmup "
                              "(panel-level counts in gate/vol/yang/vconf/"
                              "streak/tstate/amp/mom_na_window_bars); "''',
    '''                              "mom 139-bar warmup / std 120-bar "
                              "warmup (panel-level counts in gate/vol/"
                              "yang/vconf/streak/tstate/amp/mom/"
                              "std_na_window_bars); "''', 'fin-audit1')
rep('''                              "mom_oversold keep face = open AND "
                              "decidable (same erratum law -- the naive "
                              "comparison bool face alone masquerades "
                              "warmup bars as mom_closed, BANNED); "''',
    '''                              "mom_oversold keep face = open AND "
                              "decidable (same erratum law -- the naive "
                              "comparison bool face alone masquerades "
                              "warmup bars as mom_closed, BANNED); "
                              "std20_hi/std10_hi keep face = open AND "
                              "decidable (same erratum law -- the naive "
                              "comparison bool face alone masquerades "
                              "warmup bars as std_closed, BANNED); "''',
    'fin-audit2')
rep('''    print(f"mom segmented survival: {json.dumps(mom_seg, sort_keys=True)}")''',
    '''    print(f"mom segmented survival: {json.dumps(mom_seg, sort_keys=True)}")
    print(f"std segmented survival: {json.dumps(std_seg, sort_keys=True)}")''',
    'fin-print1')
rep('''    print(f"gate x vol x yang x vconf x streak x tstate x amp x mom "
          f"interaction survival: "
          f"{json.dumps(gvvvsktsam_seg, sort_keys=True)[:400]}")''',
    '''    print(f"gate x vol x yang x vconf x streak x tstate x amp x mom "
          f"interaction survival: "
          f"{json.dumps(gvvvsktsam_seg, sort_keys=True)[:400]}")
    print(f"gate x vol x yang x vconf x streak x tstate x amp x mom "
          f"x std interaction survival: "
          f"{json.dumps(gvvvsktsams_seg, sort_keys=True)[:400]}")''',
    'fin-print2')

# ============ judge overlay ============
rep('''def _overlay_stop_disclosure_w11(cand, prices, P, atr20, fundamental_ok,
                                gate_state, vol_state, yang_state,
                                vconf_state, streak_state, tstate_state,
                                amp_state, mom_state):''',
    '''def _overlay_stop_disclosure_w11(cand, prices, P, atr20, fundamental_ok,
                                gate_state, vol_state, yang_state,
                                vconf_state, streak_state, tstate_state,
                                amp_state, mom_state, std_state):''',
    'jov-sig')
rep('''    MO = mom_zero_mask(AP, cand["axis"][12], mom_state)
    _, ev = tl2.stop_exit_overlay(MO, prices, stop_key, atr20)''',
    '''    MO = mom_zero_mask(AP, cand["axis"][12], mom_state)
    SD = std_zero_mask(MO, cand["axis"][13], std_state)
    _, ev = tl2.stop_exit_overlay(SD, prices, stop_key, atr20)''',
    'jov-chain')
rep('''    with the W10 composition order (filter -> timing -> GATE -> VOL ->
    YANG -> VCONF -> STREAK -> TSTATE -> AMP -> MOM -> initial-stop;
    MSG-0440 E1 mapping + MSG-0450 annex 1).  Mirrors
    tl9._overlay_stop_disclosure_w9 with the mom overlay inserted before
    stop arming (engine-face consistency law; summary math imported)."""''',
    '''    with the W11 composition order (filter -> timing -> GATE -> VOL ->
    YANG -> VCONF -> STREAK -> TSTATE -> AMP -> MOM -> STD ->
    initial-stop; MSG-0440 E1 mapping + MSG-0450 annex 1).  Mirrors
    tl10._overlay_stop_disclosure_w10 with the std overlay inserted
    before stop arming (engine-face consistency law; summary math
    imported)."""''', 'jov-doc')

# ============ judge cell ============
rep('''           "amp_face": cand["axis"][11], "mom_face": cand["axis"][12]}''',
    '''           "amp_face": cand["axis"][11], "mom_face": cand["axis"][12],
           "std_face": cand["axis"][13]}''', 'jcell-out')
rep('''        mo = st[f"mom_state_{leg}"]''',
    '''        mo = st[f"mom_state_{leg}"]
        sd = st[f"std_state_{leg}"]''', 'jcell-mo')
rep('''        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \\
            tz, az, mz = run_candidate_curve_w11(cand, template, prices,
                                                 P, st["states"],
                                                 st[f"atr20_{leg}"],
                                                 fundamental_ok=fok,
                                                 gate_state=gs,
                                                 vol_state=vs,
                                                 yang_state=ys,
                                                 vconf_state=cs,
                                                 streak_state=sk,
                                                 tstate_state=ts,
                                                 amp_state=ap,
                                                 mom_state=mo)''',
    '''        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \\
            tz, az, mz, dz = run_candidate_curve_w11(cand, template,
                                                 prices,
                                                 P, st["states"],
                                                 st[f"atr20_{leg}"],
                                                 fundamental_ok=fok,
                                                 gate_state=gs,
                                                 vol_state=vs,
                                                 yang_state=ys,
                                                 vconf_state=cs,
                                                 streak_state=sk,
                                                 tstate_state=ts,
                                                 amp_state=ap,
                                                 mom_state=mo,
                                                 std_state=sd)''',
    'jcell-run1')
rep('''            eq2, _, m2, _, _, fired2, gz2, vz2, yz2, cz2, sz2, tz2, \\
                az2, mz2 = run_candidate_curve_w11(
                    cand, template, prices, P, st["states"],
                    st[f"atr20_{leg}"], fundamental_ok=fok, gate_state=gs,
                    vol_state=vs, yang_state=ys, vconf_state=cs,
                    streak_state=sk, tstate_state=ts, amp_state=ap,
                    mom_state=mo)''',
    '''            eq2, _, m2, _, _, fired2, gz2, vz2, yz2, cz2, sz2, tz2, \\
                az2, mz2, dz2 = run_candidate_curve_w11(
                    cand, template, prices, P, st["states"],
                    st[f"atr20_{leg}"], fundamental_ok=fok, gate_state=gs,
                    vol_state=vs, yang_state=ys, vconf_state=cs,
                    streak_state=sk, tstate_state=ts, amp_state=ap,
                    mom_state=mo, std_state=sd)''', 'jcell-run2')
rep('''                         "amp_zeroed": 0,
                         "amp_zeroed_x2": 0, "mom_zeroed": 0,
                         "mom_zeroed_x2": 0,''',
    '''                         "amp_zeroed": 0,
                         "amp_zeroed_x2": 0, "mom_zeroed": 0,
                         "mom_zeroed_x2": 0, "std_zeroed": 0,
                         "std_zeroed_x2": 0,''', 'jcell-degen')

# ============ judge prep ============
rep('''    mom_state_full, mom_err = _mom_state_full()
    if mom_err:
        print(f"JUDGE-PREP-GATE FAIL: G-MOM {mom_err}")
        return 1
    starts, gate_meta, vol_meta = {}, {}, {}
    yang_meta, vconf_meta, streak_meta = {}, {}, {}
    tstate_meta, amp_meta, mom_meta = {}, {}, {}''',
    '''    mom_state_full, mom_err = _mom_state_full()
    if mom_err:
        print(f"JUDGE-PREP-GATE FAIL: G-MOM {mom_err}")
        return 1
    std_state_full, std_err = _std_state_full()
    if std_err:
        print(f"JUDGE-PREP-GATE FAIL: G-STD {std_err}")
        return 1
    starts, gate_meta, vol_meta = {}, {}, {}
    yang_meta, vconf_meta, streak_meta = {}, {}, {}
    tstate_meta, amp_meta, mom_meta, std_meta = {}, {}, {}, {}''',
    'jprep-gate')
rep('''                                  (AMP_MEMBER, "amp"),
                                  (MOM_MEMBER, "mom")):''',
    '''                                  (AMP_MEMBER, "amp"),
                                  (MOM_MEMBER, "mom"),
                                  (STD_MEMBER, "std")):''', 'jprep-member')
rep('''        _, _, mometa = mom_state_series(prices)
        if not _mom_structure_pass(mometa):
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} G-MOM structural "
                  f"invariants broken {mometa} -- honest refuse")
            return 1
        mom_meta[leg] = mometa''',
    '''        _, _, mometa = mom_state_series(prices)
        if not _mom_structure_pass(mometa):
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} G-MOM structural "
                  f"invariants broken {mometa} -- honest refuse")
            return 1
        mom_meta[leg] = mometa
        _so20, _sd20, stdeta, _so10, _sd10 = std_state_series(prices)
        if not _std_structure_pass(stdeta):
            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} G-STD structural "
                  f"invariants broken {stdeta} -- honest refuse")
            return 1
        std_meta[leg] = stdeta''', 'jprep-legmeta')
rep('''    mom_meta["full_raw_face"] = mom_state_full[2]''',
    '''    mom_meta["full_raw_face"] = mom_state_full[2]
    std_meta["full_raw_face"] = std_state_full[2]''', 'jprep-rawface')
rep('''                "amp_meta": amp_meta, "mom_meta": mom_meta,''',
    '''                "amp_meta": amp_meta, "mom_meta": mom_meta,
                "std_meta": std_meta,''', 'jprep-out1', count=2)
rep('''            "mom_meta": mom_meta,''',
    '''            "mom_meta": mom_meta,
            "std_meta": std_meta,''', 'jprep-out2')
rep('''    print(f"mom meta L/D 139-bar-warmup "
          f"{mom_meta['L']['open_days']}open/"''',
    '''    print(f"std meta L 120-bar-warmup "
          f"{std_meta['L']['open_days']}open/"
          f"{std_meta['L']['closed_days']}closed decidable "
          f"{std_meta['L']['decidable_days']} std10-open "
          f"{std_meta['L']['std10_open_days']}")
    print(f"mom meta L/D 139-bar-warmup "
          f"{mom_meta['L']['open_days']}open/"''', 'jprep-print')

# ============ judge cmd ============
rep('''    mom_state_full, mom_err = _mom_state_full()
    if mom_err:
        print(f"JUDGE-GATE: {mom_err} (prereg sec.2 G-MOM "
              "fail-closed) -- refuse")
        return 2
    state = {}''',
    '''    mom_state_full, mom_err = _mom_state_full()
    if mom_err:
        print(f"JUDGE-GATE: {mom_err} (prereg sec.2 G-MOM "
              "fail-closed) -- refuse")
        return 2
    std_state_full, std_err = _std_state_full()
    if std_err:
        print(f"JUDGE-GATE: {std_err} (prereg sec.2 G-STD "
              "fail-closed) -- refuse")
        return 2
    state = {}''', 'jcmd-gate')
rep('''        mo = mom_state_series(prices)
        state[f"mom_state_{leg}"] = mo
        state[f"mom_meta_{leg}"] = mo[2]''',
    '''        mo = mom_state_series(prices)
        state[f"mom_state_{leg}"] = mo
        state[f"mom_meta_{leg}"] = mo[2]
        sdst = std_state_series(prices)
        state[f"std_state_{leg}"] = sdst
        state[f"std_meta_{leg}"] = sdst[2]''', 'jcmd-state')

# ============ judge finalize ============
rep('''    amp_sum, mom_sum = {}, {}
    gvy_sum, gvvy_sum, gvvvsk_sum = {}, {}, {}
    gvvvskts_sum, gvvvsktsa_sum, gvvvsktsam_sum = {}, {}, {}''',
    '''    amp_sum, mom_sum, std_sum = {}, {}, {}
    gvy_sum, gvvy_sum, gvvvsk_sum = {}, {}, {}
    gvvvskts_sum, gvvvsktsa_sum, gvvvsktsam_sum = {}, {}, {}
    gvvvsktsams_sum = {}''', 'jfin-decl')
rep('''        m = r.get("mom_face", "none")''',
    '''        m = r.get("mom_face", "none")
        stf = r.get("std_face", "none")''', 'jfin-m')
rep('''                         (tstate_sum, t), (amp_sum, a), (mom_sum, m),''',
    '''                         (tstate_sum, t), (amp_sum, a), (mom_sum, m),
                         (std_sum, stf),''', 'jfin-seglist')
rep('''                         (gvvvsktsam_sum,
                          f"{g}|{v}|{y}|{c}|{s}|{t}|{a}|{m}")):''',
    '''                         (gvvvsktsam_sum,
                          f"{g}|{v}|{y}|{c}|{s}|{t}|{a}|{m}"),
                         (gvvvsktsams_sum,
                          f"{g}|{v}|{y}|{c}|{s}|{t}|{a}|{m}|{stf}")):''',
    'jfin-seglist2')
rep('''           "mom_face_judgment": mom_sum,''',
    '''           "mom_face_judgment": mom_sum,
           "std_face_judgment": std_sum,''', 'jfin-out1')
rep('''           "gate_vol_yang_vconf_streak_tstate_amp_mom_interaction_"
           "judgment": gvvvsktsam_sum,''',
    '''           "gate_vol_yang_vconf_streak_tstate_amp_mom_interaction_"
           "judgment": gvvvsktsam_sum,
           "gate_vol_yang_vconf_streak_tstate_amp_mom_std_interaction_"
           "judgment": gvvvsktsams_sum,''', 'jfin-out2')
rep('''                             "gate + vol + yang + vconf + streak + "
                             "tstate + amp + MOM overlays carried per "''',
    '''                             "gate + vol + yang + vconf + streak + "
                             "tstate + amp + MOM + STD overlays carried "
                             "per "''', 'jfin-audit1')
rep('''                             "-> timing -> GATE -> VOL -> YANG -> VCONF "
                             "-> STREAK -> TSTATE -> AMP -> MOM -> "
                             "initial-stop; "''',
    '''                             "-> timing -> GATE -> VOL -> YANG -> VCONF "
                             "-> STREAK -> TSTATE -> AMP -> MOM -> STD "
                             "-> initial-stop; "''', 'jfin-audit2')
rep('''                             "P=2000 sign-flip, seed [20312000, cell]); "''',
    '''                             "P=2000 sign-flip, seed [20318000, "
                             "cell]); "''', 'jfin-seed')
rep('''    print(f"mom-face judgment: {json.dumps(mom_sum, sort_keys=True)}")''',
    '''    print(f"mom-face judgment: {json.dumps(mom_sum, sort_keys=True)}")
    print(f"std-face judgment: {json.dumps(std_sum, sort_keys=True)}")''',
    'jfin-print')
rep('''    print(f"gate x vol x yang x vconf x streak x tstate x amp x mom "
          f"judgment: {json.dumps(gvvvsktsam_sum, sort_keys=True)}"
          f"[:400]")''', 'XXBADXX2', 'jfin-print2-probe', count=0)

# legs[leg] row std fields (mom_zeroed tail after streak_zeroed_x2)
rep('''                     "streak_zeroed": int(sz),
                     "streak_zeroed_x2": int(sz2),''',
    '''                     "streak_zeroed": int(sz),
                     "streak_zeroed_x2": int(sz2),
                     "std_zeroed": int(dz),
                     "std_zeroed_x2": int(dz2),''', 'jcell-legs-tail')

open('results/_r442bmb_stage3c.py', 'w', encoding='utf-8').write(SRC)
print('stage3c written, lines:', SRC.count(chr(10)) + 1)
print('applied:', len(done), 'fails:', len(fails))
for f in fails:
    print(' FAIL', f)
