"""_r472bmb_w14_edits2.py -- screen cell (unpack sites + resi/cnt row
faces), G-ANCHOR 18-tuple pad, and the residual SIXTEEN/sixteen
textual faces."""
import sys

DRAFT = "results/_r472bmb_w14_runner_draft.py"
text = open(DRAFT, encoding="utf-8").read()
log = []


def rep(old, new, expect=1, name=""):
    global text
    n = text.count(old)
    if n != expect:
        print(f"EDIT2-FAIL [{name}]: found {n} != {expect}")
        sys.exit(1)
    text = text.replace(old, new)
    log.append((name, n))


# --- _screen_cell_w14: null-branch unpack ---
rep("""        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \\
            tz, az, mz, dz, rz, nz = run_candidate_curve_w14(
                cand, None, prices, P, states, st["atr20"],
                rng_matrix=mat, p_on=p_on, gate_state=st.get("gate_state"),""",
    """        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \\
            tz, az, mz, dz, rz, nz, rz2, cnz = run_candidate_curve_w14(
                cand, None, prices, P, states, st["atr20"],
                rng_matrix=mat, p_on=p_on, gate_state=st.get("gate_state"),""",
    1, "screen null unpack")

# --- _screen_cell_w14: cand-branch unpack ---
rep("""        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \\
            tz, az, mz, dz, rz, nz = run_candidate_curve_w14(
                cand, template, prices, P, states, st["atr20"],
                fundamental_ok=st["fundamental_ok"],""",
    """        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \\
            tz, az, mz, dz, rz, nz, rz2, cnz = run_candidate_curve_w14(
                cand, template, prices, P, states, st["atr20"],
                fundamental_ok=st["fundamental_ok"],""",
    1, "screen cand unpack")

# --- screen cell null-branch state kwargs (+resi/cnt) ---
rep("""                std_state=st.get("std_state"),
                rsqr_state=st.get("rsqr_state"),
                sumn_state=st.get("sumn_state"))
    else:""",
    """                std_state=st.get("std_state"),
                rsqr_state=st.get("rsqr_state"),
                sumn_state=st.get("sumn_state"),
                resi_state=st.get("resi_state"),
                cnt_state=st.get("cnt_state"))
    else:""",
    1, "screen null states")

# --- screen cell cand-branch state kwargs (+resi/cnt) ---
rep("""                std_state=st.get("std_state"),
                rsqr_state=st.get("rsqr_state"),
                sumn_state=st.get("sumn_state"))
    row = {""",
    """                std_state=st.get("std_state"),
                rsqr_state=st.get("rsqr_state"),
                sumn_state=st.get("sumn_state"),
                resi_state=st.get("resi_state"),
                cnt_state=st.get("cnt_state"))
    row = {""",
    1, "screen cand states")

# --- screen cell row keys (+resi/cnt faces) ---
rep("""           "rsqr_zeroed": int(rz),
            "sumn_face": cand["axis"][15],
            "sumn_zeroed": int(nz)}""",
    """           "rsqr_zeroed": int(rz),
            "sumn_face": cand["axis"][15],
            "sumn_zeroed": int(nz),
            "resi_face": cand["axis"][16],
            "resi_zeroed": int(rz2),
            "cnt_face": cand["axis"][17],
            "cnt_zeroed": int(cnz)}""",
    1, "screen row keys")

# --- G-ANCHOR identity pad 12 -> 14 none (18-tuple; r446(1) law site) ---
rep("""                "axis": list(tl1.DEFAULT_AXIS)
                + ["none", "none", "none", "none", "none", "none",
                   "none", "none", "none", "none", "none", "none"]}""",
    """                "axis": list(tl1.DEFAULT_AXIS)
                + ["none", "none", "none", "none", "none", "none",
                   "none", "none", "none", "none", "none", "none",
                   "none", "none"]}""",
    1, "G-ANCHOR 18-tuple pad")

# --- residual SIXTEEN textual faces -> EIGHTEEN (post-axis-16 sites) ---
rep("EIGHTEEN-tuple axis stream", "EIGHTEEN-tuple axis stream", 1,
    "sobol docstring (already landed)")
rep("""    (W13 berth 20328000, distinct from the W12 berth 20321000 -- zero
    stream overlap by construction); consumption order frozen = p_on
    regime -> SIXTEEN-tuple axis R/X/S/T/STOP/GATE/VOL/YANG/VCONF/
    STREAK/TSTATE/AMP/MOM/STD/RSQR/SUMN -> signal matrix (the sumn gate leg merged
    into the same grid/param space draw per prereg sec.3).  Same
    engine/cost/panel as candidate cells incl. the gate + vol + yang +
    vconf + streak + tstate + amp + mom + std + rsqr + sumn legs
    (BACKTEST_PLAN three iron rules).\"\"\"""",
    """    (W14 berth 20328000, distinct from the W13 berth 20323500 -- zero
    stream overlap by construction); consumption order frozen = p_on
    regime -> EIGHTEEN-tuple axis R/X/S/T/STOP/GATE/VOL/YANG/VCONF/
    STREAK/TSTATE/AMP/MOM/STD/RSQR/SUMN/RESI/CNT -> signal matrix (the resi/cnt
    gate legs merged into the same grid/param space draw per prereg
    sec.3).  Same engine/cost/panel as candidate cells incl. the
    gate + vol + yang + vconf + streak + tstate + amp + mom + std +
    rsqr + sumn + resi + cnt legs (BACKTEST_PLAN three iron rules).\"\"\"""",
    1, "null draw docstring")
rep("RSQR -> SUMN -> initial-stop (prereg sec.3 sixteen-tuple dedup legs",
    "RSQR -> SUMN -> RESI -> CNT -> initial-stop (prereg sec.3 eighteen-tuple dedup legs", 1,
    "eff-mask docstring")
rep("W9 cmd_screen_prep\n    caliber on the W10 sixteen-tuple grammar face",
    "W13 cmd_screen_prep\n    caliber on the W13 sixteen-tuple grammar face extended by the\n    W14 resi/cnt layer (eighteen-tuple)", 1,
    "screen-prep docstring")
rep("W9 cmd_judge_prep caliber on the W10 sixteen-tuple\n    grammar face",
    "W13 cmd_judge_prep caliber on the W13 sixteen-tuple\n    grammar face extended by the W14 resi/cnt layer (eighteen-tuple)", 1,
    "judge-prep docstring")
rep("G-MOM gate + sixteen-tuple grammar", "G-MOM gate + eighteen-tuple grammar", 1,
    "status print")
rep("the SIXTEEN-tuple face): per-slot Sobol", "the EIGHTEEN-tuple face): per-slot Sobol", 1,
    "generate docstring")
rep('"draw_order": "p_on regime -> SIXTEEN-tuple "\n                                         "axis R/X/S/T/STOP/GATE/VOL/"\n                                         "YANG/VCONF/STREAK/TSTATE/AMP/"\n                                         "MOM/STD/RSQR/SUM -> signal matrix (frozen "\n                                         "runner face, gate+vol+yang+"\n                                         "vconf+streak+tstate+amp+mom+std+',
    '"draw_order": "p_on regime -> EIGHTEEN-tuple "\n                                         "axis R/X/S/T/STOP/GATE/VOL/"\n                                         "YANG/VCONF/STREAK/TSTATE/AMP/"\n                                         "MOM/STD/RSQR/SUMN/RESI/CNT -> signal matrix (frozen "\n                                         "runner face, gate+vol+yang+"\n                                         "vconf+streak+tstate+amp+mom+std+', 1,
    "finalize draw_order")
rep("EIGHTEEN-tuple cell key=", "EIGHTEEN-tuple cell key=", 1,
    "exclusion header (already landed)")

open(DRAFT, "w", encoding="utf-8", newline="\n").write(text)
print(f"edits2 OK: {len(log)} verified replacements")
for name, n in log:
    print(f"  [{name}] x{n}")
rem = [(text.count("SIXTEEN"), text.count("sixteen"))]
print("residual SIXTEEN/sixteen counts:", rem)
for k in ("SIXTEEN-tuple", "sixteen-tuple"):
    print(k, text.count(k))
