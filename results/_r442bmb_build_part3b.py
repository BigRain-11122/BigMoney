"""r442 bm-b: W11 builder stage-3b. stage3a -> stage3b.
generate/screen/judge/intake threading: std lines added after the
analogous mom lines (zero disturbance law), std gates added beside
mom gates, std face keys/segments/outputs.
"""
SRC = open('results/_r442bmb_stage3a.py', encoding='utf-8').read()
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


# ================= generate leg =================
rep('cand["candidate_id"] = f"W10-{family}-{i:04d}"',
    'cand["candidate_id"] = f"W11-{family}-{i:04d}"', 'gen-cid')
# G-STD gate after G-MOM gate
rep('''    mom_state, mom_err = _mom_state_full()
    if mom_err:
        print(f"GENERATE-GATE: {mom_err} (prereg sec.2 G-MOM "
              "fail-closed) -- refuse")
        return 2
    excl_rows, excl_disc = _load_exclusion_rows_w11(grammar)''',
    '''    mom_state, mom_err = _mom_state_full()
    if mom_err:
        print(f"GENERATE-GATE: {mom_err} (prereg sec.2 G-MOM "
              "fail-closed, tl10 import face) -- refuse")
        return 2
    std_state, std_err = _std_state_full()
    if std_err:
        print(f"GENERATE-GATE: {std_err} (prereg sec.2 G-STD "
              "fail-closed) -- refuse")
        return 2
    excl_rows, excl_disc = _load_exclusion_rows_w11(grammar)''',
    'gen-std-gate')
# dedup mask call +std
rep('''        S = _effective_signal_mask_w11(mask, prices, cand["axis"][4], atr20,
                                      cand["axis"][5], cand["axis"][6],
                                      cand["axis"][7], cand["axis"][8],
                                      cand["axis"][9], cand["axis"][10],
                                      cand["axis"][11], cand["axis"][12],
                                      gate_state, vol_state, yang_state,
                                      vconf_state, streak_state,
                                      tstate_state, amp_state, mom_state)''',
    '''        S = _effective_signal_mask_w11(mask, prices, cand["axis"][4], atr20,
                                      cand["axis"][5], cand["axis"][6],
                                      cand["axis"][7], cand["axis"][8],
                                      cand["axis"][9], cand["axis"][10],
                                      cand["axis"][11], cand["axis"][12],
                                      cand["axis"][13],
                                      gate_state, vol_state, yang_state,
                                      vconf_state, streak_state,
                                      tstate_state, amp_state, mom_state,
                                      std_state)''', 'gen-dedupcall')
# face counts + k8->k9
rep('''    streak_counts, tstate_counts, amp_counts = {}, {}, {}
    mom_counts = {}
    gvvvsktsam_counts = {}''',
    '''    streak_counts, tstate_counts, amp_counts = {}, {}, {}
    mom_counts, std_counts = {}, {}
    gvvvsktsam_counts = {}''', 'gen-fc-decl')
rep('''        mom_counts[c["axis"][12]] = mom_counts.get(c["axis"][12], 0) + 1
        k8 = (f"{c['axis'][5]}|{c['axis'][6]}|{c['axis'][7]}|"
              f"{c['axis'][8]}|{c['axis'][9]}|{c['axis'][10]}|"
              f"{c['axis'][11]}|{c['axis'][12]}")
        gvvvsktsam_counts[k8] = gvvvsktsam_counts.get(k8, 0) + 1''',
    '''        mom_counts[c["axis"][12]] = mom_counts.get(c["axis"][12], 0) + 1
        std_counts[c["axis"][13]] = std_counts.get(c["axis"][13], 0) + 1
        k9 = (f"{c['axis'][5]}|{c['axis'][6]}|{c['axis'][7]}|"
              f"{c['axis'][8]}|{c['axis'][9]}|{c['axis'][10]}|"
              f"{c['axis'][11]}|{c['axis'][12]}|{c['axis'][13]}")
        gvvvsktsam_counts[k9] = gvvvsktsam_counts.get(k9, 0) + 1''',
    'gen-fc-body')
rep('''                                     "amp, mom); exclusion face = "
                                     "mom=none only (sec.1); prior-wave "
                                     "keys mom=none-completed; mom in "
                                     "{mom_oversold} = "
                                     "new-syntax legal cells"},''',
    '''                                     "amp, mom, std); exclusion face "
                                     "= std=none only (sec.1); prior-wave "
                                     "keys std=none-completed; std in "
                                     "{std20_hi, std10_hi} = "
                                     "new-syntax legal cells"},''',
    'gen-payload-note')
rep('''               "amp_face_counts": amp_counts,
               "mom_face_counts": mom_counts,
               "gate_vol_yang_vconf_streak_tstate_amp_mom_face_counts":
                   gvvvsktsam_counts,''',
    '''               "amp_face_counts": amp_counts,
               "mom_face_counts": mom_counts,
               "std_face_counts": std_counts,
               "gate_vol_yang_vconf_streak_tstate_amp_mom_std_face_"
               "counts":
                   gvvvsktsam_counts,''', 'gen-payload-fc')
rep('''               "amp_state_meta": amp_state[2],
               "mom_state_meta": mom_state[2],''',
    '''               "amp_state_meta": amp_state[2],
               "mom_state_meta": mom_state[2],
               "std_state_meta": std_state[2],''', 'gen-payload-meta')
rep('''                         "seed_berth_note": "berths 20311000/20311500/"
                         "20312000 held at the freeze commit (bm-b r437 "
                         "three-step re-verify ALL GREEN, no re-pick; "
                         "R250 one-step law; berth-open adoption of "
                         "the bm-c r228 MOM candidate whole package "
                         "per AMP->W9 precedent)",''',
    '''                         "seed_berth_note": "berths 20317000/"
                         "20317500/20318000 held at the freeze commit "
                         "(bm-b r441 three-step re-verify ALL GREEN, "
                         "no re-pick after the 20316000/20316500 "
                         "collision re-take per draft clause-5; R250 "
                         "one-step law; berth-open adoption of the "
                         "bm-c r237 STD candidate whole package per "
                         "AMP->W9->W10 adoption lineage)",''',
    'gen-payload-berth')
rep('''           f"raw {raw_total} (A{N_A}/B{N_B}, excl hits "
           f"{sum(excl_hits.values())}) | dedup -> {len(distinct)} "
           f"(mom faces {json.dumps(mom_counts, sort_keys=True)}; "
           f"gate x vol x yang x vconf x streak x tstate x amp x mom "
           f"{json.dumps(gvvvsktsam_counts, sort_keys=True)}) "''',
    '''           f"raw {raw_total} (A{N_A}/B{N_B}, excl hits "
           f"{sum(excl_hits.values())}) | dedup -> {len(distinct)} "
           f"(std faces {json.dumps(std_counts, sort_keys=True)}; "
           f"gate x vol x yang x vconf x streak x tstate x amp x mom "
           f"x std {json.dumps(gvvvsktsam_counts, sort_keys=True)}) "''',
    'gen-ledger-row')
rep('''           f"TRIAL-LABOR-W10-GENERATE, T-122 prereg bm-b r437 frozen / "
           f"runner bm-b r438) | "''',
    '''           f"TRIAL-LABOR-W11-GENERATE, T-123 prereg bm-b r441 frozen / "
           f"runner bm-b r442) | "''', 'gen-ledger-pool')

# ================= screen CSV columns =================
rep('''                      "vconf_zeroed", "streak_face", "streak_zeroed",
                      "tstate_face", "tstate_zeroed", "amp_face",
                      "amp_zeroed", "mom_face", "mom_zeroed",
                      "survives_screen"]''',
    '''                      "vconf_zeroed", "streak_face", "streak_zeroed",
                      "tstate_face", "tstate_zeroed", "amp_face",
                      "amp_zeroed", "mom_face", "mom_zeroed",
                      "std_face", "std_zeroed",
                      "survives_screen"]''', 'csv-cols')

# ================= screen cell (both branches + row) =================
rep('''        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \\
            tz, az, mz = run_candidate_curve_w11(
                cand, None, prices, P, states, st["atr20"],
                rng_matrix=mat, p_on=p_on, gate_state=st.get("gate_state"),
                vol_state=st.get("vol_state"),
                yang_state=st.get("yang_state"),
                vconf_state=st.get("vconf_state"),
                streak_state=st.get("streak_state"),
                tstate_state=st.get("tstate_state"),
                amp_state=st.get("amp_state"),
                mom_state=st.get("mom_state"))''',
    '''        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \\
            tz, az, mz, dz = run_candidate_curve_w11(
                cand, None, prices, P, states, st["atr20"],
                rng_matrix=mat, p_on=p_on, gate_state=st.get("gate_state"),
                vol_state=st.get("vol_state"),
                yang_state=st.get("yang_state"),
                vconf_state=st.get("vconf_state"),
                streak_state=st.get("streak_state"),
                tstate_state=st.get("tstate_state"),
                amp_state=st.get("amp_state"),
                mom_state=st.get("mom_state"),
                std_state=st.get("std_state"))''', 'scr-cell-null')
rep('''        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \\
            tz, az, mz = run_candidate_curve_w11(
                cand, template, prices, P, states, st["atr20"],
                fundamental_ok=st["fundamental_ok"],
                gate_state=st.get("gate_state"),
                vol_state=st.get("vol_state"),
                yang_state=st.get("yang_state"),
                vconf_state=st.get("vconf_state"),
                streak_state=st.get("streak_state"),
                tstate_state=st.get("tstate_state"),
                amp_state=st.get("amp_state"),
                mom_state=st.get("mom_state"))''',
    '''        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \\
            tz, az, mz, dz = run_candidate_curve_w11(
                cand, template, prices, P, states, st["atr20"],
                fundamental_ok=st["fundamental_ok"],
                gate_state=st.get("gate_state"),
                vol_state=st.get("vol_state"),
                yang_state=st.get("yang_state"),
                vconf_state=st.get("vconf_state"),
                streak_state=st.get("streak_state"),
                tstate_state=st.get("tstate_state"),
                amp_state=st.get("amp_state"),
                mom_state=st.get("mom_state"),
                std_state=st.get("std_state"))''', 'scr-cell-cand')
rep('''           "amp_zeroed": int(az), "mom_face": cand["axis"][12],
           "mom_zeroed": int(mz)}''',
    '''           "amp_zeroed": int(az), "mom_face": cand["axis"][12],
           "mom_zeroed": int(mz), "std_face": cand["axis"][13],
           "std_zeroed": int(dz)}''', 'scr-cell-row')

open('results/_r442bmb_stage3b.py', 'w', encoding='utf-8').write(SRC)
print('stage3b written, lines:', SRC.count(chr(10)) + 1)
print('applied:', len(done), 'fails:', len(fails))
for f in fails:
    print(' FAIL', f)
