"""r442 bm-b patch-3: complete the W10->W11 selftest conversion in the
L12-L15 engine/null/CSV legs (std axis slot + std_state args + 15-tuple
unpack + 14-tuple null draw + CSV std columns + parser labels)."""
import io

p = 'scripts/trial_labor_w11.py'
src = io.open(p, encoding='utf-8').read()
edits = [
    # L12 frames3: std state + both mask calls carry std slot
    ('    ms3 = mom_state_series(frames3)\n'
     '    sig = pd.DataFrame(1.0, index=P3["close"].index,\n'
     '                       columns=P3["close"].columns)\n'
     '    m_none = _effective_signal_mask_w11(\n'
     '        sig, frames3, "none", None, "none", "none", "none", "none",\n'
     '        "none", "none", "none", "none", gs3, vs3, ys3, cs3, sk3, ts3,\n'
     '        as3, ms3)\n',
     '    ms3 = mom_state_series(frames3)\n'
     '    ss3 = std_state_series(frames3)\n'
     '    sig = pd.DataFrame(1.0, index=P3["close"].index,\n'
     '                       columns=P3["close"].columns)\n'
     '    m_none = _effective_signal_mask_w11(\n'
     '        sig, frames3, "none", None, "none", "none", "none", "none",\n'
     '        "none", "none", "none", "none", "none", gs3, vs3, ys3, cs3,\n'
     '        sk3, ts3, as3, ms3, ss3)\n'),
    ('    m_ov = _effective_signal_mask_w11(\n'
     '        sig, frames3, "none", None, "none", "none", "none", "none",\n'
     '        "none", "none", "none", "mom_oversold", gs3, vs3, ys3, cs3,\n'
     '        sk3, ts3, as3, ms3)\n',
     '    m_ov = _effective_signal_mask_w11(\n'
     '        sig, frames3, "none", None, "none", "none", "none", "none",\n'
     '        "none", "none", "none", "mom_oversold", "none", gs3, vs3,\n'
     '        ys3, cs3, sk3, ts3, as3, ms3, ss3)\n'),
    # L12c frames5: std state + both mask calls
    ('    ms5 = mom_state_series(frames5)\n'
     '    sig5 = pd.DataFrame(1.0, index=P5["close"].index,\n'
     '                        columns=P5["close"].columns)\n'
     '    m5_none = _effective_signal_mask_w11(\n'
     '        sig5, frames5, "none", None, "none", "none", "none", "none",\n'
     '        "none", "none", "none", "none", gs5, vs5, ys5, cs5, sk5, ts5,\n'
     '        as5, ms5)\n'
     '    m5_ov = _effective_signal_mask_w11(\n'
     '        sig5, frames5, "none", None, "none", "none", "none", "none",\n'
     '        "none", "none", "none", "mom_oversold", gs5, vs5, ys5, cs5,\n'
     '        sk5, ts5, as5, ms5)\n',
     '    ms5 = mom_state_series(frames5)\n'
     '    ss5 = std_state_series(frames5)\n'
     '    sig5 = pd.DataFrame(1.0, index=P5["close"].index,\n'
     '                        columns=P5["close"].columns)\n'
     '    m5_none = _effective_signal_mask_w11(\n'
     '        sig5, frames5, "none", None, "none", "none", "none", "none",\n'
     '        "none", "none", "none", "none", "none", gs5, vs5, ys5, cs5,\n'
     '        sk5, ts5, as5, ms5, ss5)\n'
     '    m5_ov = _effective_signal_mask_w11(\n'
     '        sig5, frames5, "none", None, "none", "none", "none", "none",\n'
     '        "none", "none", "none", "mom_oversold", "none", gs5, vs5,\n'
     '        ys5, cs5, sk5, ts5, as5, ms5, ss5)\n'),
    # L13 base axis: 14-tuple (std slot appended)
    ('            "axis": ["none", "time_stop_5d", "equal_weight",\n'
     '                     "daily_signal", "none", "none", "none", "none",\n'
     '                     "none", "none", "none", "none", "none"]}\n',
     '            "axis": ["none", "time_stop_5d", "equal_weight",\n'
     '                     "daily_signal", "none", "none", "none", "none",\n'
     '                     "none", "none", "none", "none", "none",\n'
     '                     "none"]}\n'),
    # L13 eq10: 15-tuple unpack + std_state arg
    ('    eq10, tr10, m10, _, _, _, _, _, _, _, sz10, tz10, az10, mz10 = \\\n'
     '        run_candidate_curve_w11(\n'
     '            base, None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,\n'
     '            yang_state=ys3, vconf_state=cs3, streak_state=sk3,\n'
     '            tstate_state=ts3, amp_state=as3, mom_state=ms3)\n',
     '    eq10, tr10, m10, _, _, _, _, _, _, _, sz10, tz10, az10, mz10, \\\n'
     '        sdz10 = \\\n'
     '        run_candidate_curve_w11(\n'
     '            base, None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,\n'
     '            yang_state=ys3, vconf_state=cs3, streak_state=sk3,\n'
     '            tstate_state=ts3, amp_state=as3, mom_state=ms3,\n'
     '            std_state=ss3)\n'),
    # L13 eq10b: 15-tuple unpack + std_state arg
    ('    eq10b, _, _, _, _, _, _, _, _, _, sz10b, tz10b, az10b, mz10b = \\\n'
     '        run_candidate_curve_w11(\n'
     '            dict(base, candidate_id="ST-B-0001"), None, frames3, P3,\n'
     '            st3, gate_state=gs3, vol_state=vs3, yang_state=ys3,\n'
     '            vconf_state=cs3, streak_state=sk3, tstate_state=ts3,\n'
     '            amp_state=as3, mom_state=ms3)\n',
     '    eq10b, _, _, _, _, _, _, _, _, _, sz10b, tz10b, az10b, mz10b, \\\n'
     '        _ = \\\n'
     '        run_candidate_curve_w11(\n'
     '            dict(base, candidate_id="ST-B-0001"), None, frames3, P3,\n'
     '            st3, gate_state=gs3, vol_state=vs3, yang_state=ys3,\n'
     '            vconf_state=cs3, streak_state=sk3, tstate_state=ts3,\n'
     '            amp_state=as3, mom_state=ms3, std_state=ss3)\n'),
    # L13 eq5n
    ('    eq5n, tr5n, m5n, _, _, _, _, _, _, _, _, _, az5n, mz5n = \\\n'
     '        run_candidate_curve_w11(\n'
     '            dict(base, axis=list(base["axis"])), None, frames5, P5,\n'
     '            st5, gate_state=gs5, vol_state=vs5, yang_state=ys5,\n'
     '            vconf_state=cs5, streak_state=sk5, tstate_state=ts5,\n'
     '            amp_state=as5, mom_state=ms5)\n',
     '    eq5n, tr5n, m5n, _, _, _, _, _, _, _, _, _, az5n, mz5n, _ = \\\n'
     '        run_candidate_curve_w11(\n'
     '            dict(base, axis=list(base["axis"])), None, frames5, P5,\n'
     '            st5, gate_state=gs5, vol_state=vs5, yang_state=ys5,\n'
     '            vconf_state=cs5, streak_state=sk5, tstate_state=ts5,\n'
     '            amp_state=as5, mom_state=ms5, std_state=ss5)\n'),
    # L13 eq5o: 14-tuple mom axis + std slot
    ('    eq5o, tr5o, m5o, _, _, _, _, _, _, _, _, _, az5o, mz5o = \\\n'
     '        run_candidate_curve_w11(\n'
     '            dict(base, axis=[*base["axis"][:12], "mom_oversold"]), None,\n'
     '            frames5, P5, st5, gate_state=gs5, vol_state=vs5,\n'
     '            yang_state=ys5, vconf_state=cs5, streak_state=sk5,\n'
     '            tstate_state=ts5, amp_state=as5, mom_state=ms5)\n',
     '    eq5o, tr5o, m5o, _, _, _, _, _, _, _, _, _, az5o, mz5o, _ = \\\n'
     '        run_candidate_curve_w11(\n'
     '            dict(base, axis=[*base["axis"][:12], "mom_oversold",\n'
     '                             "none"]), None,\n'
     '            frames5, P5, st5, gate_state=gs5, vol_state=vs5,\n'
     '            yang_state=ys5, vconf_state=cs5, streak_state=sk5,\n'
     '            tstate_state=ts5, amp_state=as5, mom_state=ms5,\n'
     '            std_state=ss5)\n'),
    # L13 eq3o: 14-tuple mom axis + std slot
    ('    eq3o, tr3o, m3o, _, _, _, _, _, _, _, _, _, az3o, mz3o = \\\n'
     '        run_candidate_curve_w11(\n'
     '            dict(base, axis=[*base["axis"][:12], "mom_oversold"]), None,\n'
     '            frames3, P3, st3, gate_state=gs3, vol_state=vs3,\n'
     '            yang_state=ys3, vconf_state=cs3, streak_state=sk3,\n'
     '            tstate_state=ts3, amp_state=as3, mom_state=ms3)\n',
     '    eq3o, tr3o, m3o, _, _, _, _, _, _, _, _, _, az3o, mz3o, _ = \\\n'
     '        run_candidate_curve_w11(\n'
     '            dict(base, axis=[*base["axis"][:12], "mom_oversold",\n'
     '                             "none"]), None,\n'
     '            frames3, P3, st3, gate_state=gs3, vol_state=vs3,\n'
     '            yang_state=ys3, vconf_state=cs3, streak_state=sk3,\n'
     '            tstate_state=ts3, amp_state=as3, mom_state=ms3,\n'
     '            std_state=ss3)\n'),
    # L14: fourteen-tuple + std domain + W11 berth label
    ('    _ok("L14 null-axis draw determinism + FOURTEEN-tuple with mom in "\n'
     '        "the frozen domain (W10 null berth 20311500)",\n'
     '        p1 == p2 and ax1 == ax2 and len(ax1) == 13\n'
     '        and ax1[12] in AXIS_MOM and ax1[11] in tl9.AXIS_AMP\n',
     '    _ok("L14 null-axis draw determinism + FOURTEEN-tuple with mom+std "\n'
     '        "in the frozen domains (W11 null berth 20317500)",\n'
     '        p1 == p2 and ax1 == ax2 and len(ax1) == 14\n'
     '        and ax1[12] in AXIS_MOM and ax1[13] in AXIS_STD\n'
     '        and ax1[11] in tl9.AXIS_AMP\n'),
    # L15 mom_dom
    ('    mom_dom = ax0[12] in AXIS_MOM and ax0[4] in tl2.AXIS_STOP \\\n'
     '        and len(ax0) == 13\n',
     '    mom_dom = (ax0[12] in AXIS_MOM and ax0[13] in AXIS_STD\n'
     '               and ax0[4] in tl2.AXIS_STOP and len(ax0) == 14)\n'),
    # L15 eqn run: 15-tuple + std_state + W11 null id
    ('    eqn, trn, mtn, prn, pt, frn, gzn, vzn, yzn, czn, szn, tzn, azn, mzn = \\\n'
     '        run_candidate_curve_w11(\n'
     '            {"module": "null", "fn": "random_signal",\n'
     '             "sig_params": {"p_on": p_on0}, "axis": ax0,\n'
     '             "candidate_id": "W10-NULL-0000", "family": "NULL"},\n'
     '            None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,\n'
     '            yang_state=ys3, vconf_state=cs3, streak_state=sk3,\n'
     '            tstate_state=ts3, amp_state=as3, mom_state=ms3,\n'
     '            rng_matrix=mat0, p_on=p_on0)\n',
     '    eqn, trn, mtn, prn, pt, frn, gzn, vzn, yzn, czn, szn, tzn, azn, \\\n'
     '        mzn, _ = \\\n'
     '        run_candidate_curve_w11(\n'
     '            {"module": "null", "fn": "random_signal",\n'
     '             "sig_params": {"p_on": p_on0}, "axis": ax0,\n'
     '             "candidate_id": "W11-NULL-0000", "family": "NULL"},\n'
     '            None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,\n'
     '            yang_state=ys3, vconf_state=cs3, streak_state=sk3,\n'
     '            tstate_state=ts3, amp_state=as3, mom_state=ms3,\n'
     '            std_state=ss3, rng_matrix=mat0, p_on=p_on0)\n'),
    # L15 eqnb run: 15-tuple + std_state + W11 null id
    ('    eqnb, _, _, _, _, _, _, _, _, _, _, _, _, mznb = \\\n'
     '        run_candidate_curve_w11(\n'
     '            {"module": "null", "fn": "random_signal",\n'
     '             "sig_params": {"p_on": p_on0b}, "axis": ax0b,\n'
     '             "candidate_id": "W10-NULL-0000", "family": "NULL"},\n'
     '            None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,\n'
     '            yang_state=ys3, vconf_state=cs3, streak_state=sk3,\n'
     '            tstate_state=ts3, amp_state=as3, mom_state=ms3,\n'
     '            rng_matrix=mat0b, p_on=p_on0b)\n',
     '    eqnb, _, _, _, _, _, _, _, _, _, _, _, _, mznb, _ = \\\n'
     '        run_candidate_curve_w11(\n'
     '            {"module": "null", "fn": "random_signal",\n'
     '             "sig_params": {"p_on": p_on0b}, "axis": ax0b,\n'
     '             "candidate_id": "W11-NULL-0000", "family": "NULL"},\n'
     '            None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,\n'
     '            yang_state=ys3, vconf_state=cs3, streak_state=sk3,\n'
     '            tstate_state=ts3, amp_state=as3, mom_state=ms3,\n'
     '            std_state=ss3, rng_matrix=mat0b, p_on=p_on0b)\n'),
    # L15c CSV contract: std pair tail
    ('    _ok("L15c screen CSV contract carries the mom columns in the "\n'
     '        "frozen order (cell_id/candidate_id head + mom pair before "\n'
     '        "survives_screen)",\n'
     '        csv_cols_screen_w11[:2] == ["cell_id", "candidate_id"]\n'
     '        and csv_cols_screen_w11[-3:] == ["mom_face", "mom_zeroed",\n'
     '                                         "survives_screen"]\n'
     '        and "mom_face" in csv_cols_screen_w11\n'
     '        and {"gate_zeroed", "vol_zeroed", "yang_zeroed", "vconf_zeroed",\n'
     '             "streak_zeroed", "tstate_zeroed", "amp_zeroed",\n'
     '             "mom_zeroed"} <= set(csv_cols_screen_w11))\n',
     '    _ok("L15c screen CSV contract carries the mom+std columns in the "\n'
     '        "frozen order (cell_id/candidate_id head + std pair before "\n'
     '        "survives_screen)",\n'
     '        csv_cols_screen_w11[:2] == ["cell_id", "candidate_id"]\n'
     '        and csv_cols_screen_w11[-3:] == ["std_face", "std_zeroed",\n'
     '                                         "survives_screen"]\n'
     '        and "mom_face" in csv_cols_screen_w11\n'
     '        and {"gate_zeroed", "vol_zeroed", "yang_zeroed", "vconf_zeroed",\n'
     '             "streak_zeroed", "tstate_zeroed", "amp_zeroed",\n'
     '             "mom_zeroed", "std_zeroed"} <= set(csv_cols_screen_w11))\n'),
    # parser labels
    ('ap = argparse.ArgumentParser(description="TRIAL_LABOR_W11 runner "\n'
     '                                     "(mom-gate thirteen-gate wave)")',
     'ap = argparse.ArgumentParser(description="TRIAL_LABOR_W11 runner "\n'
     '                                     "(MOM+STD fourteen-gate wave)")'),
    ('sub.add_parser("grammar", help="serialize the frozen W10 grammar")',
     'sub.add_parser("grammar", help="serialize the frozen W11 grammar")'),
]
for i, (old, new) in enumerate(edits, 1):
    n = src.count(old)
    assert n == 1, f"E{i}: found {n} occurrences (expected 1)"
    src = src.replace(old, new)
io.open(p, 'w', encoding='utf-8', newline='\n').write(src)
print(f"patch-3: all {len(edits)} edits applied cleanly")
