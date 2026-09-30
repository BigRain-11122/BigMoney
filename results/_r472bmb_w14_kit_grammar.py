def build_grammar_w14():
    """tl13 grammar extended with the NEW resi + cnt axes + W14
    seeds/counts (frozen face).  EIGHTEEN-tuple axes R/X/S/T/STOP/
    GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD/RSQR/SUMN/RESI/CNT
    = 1,693,052,928 axis combos (W13 282,175,488 x RESI 2-value x
    CNT 3-value adjudicated member-set mult; prereg sec.3).

    Exclusion law (prereg sec.1): exact already-judged cells are
    excluded on the resi=none AND cnt=none face only; all prior-wave
    lineage keys are resi/cnt-none-completed (W1 4-tuple + stop/gate/
    vol/yang/vconf/streak/tstate/amp/mom/std/rsqr/sumn/resi/cnt none;
    W2 5-tuple + gate/vol/yang/vconf/streak/tstate/amp/mom/std/rsqr/
    sumn/resi/cnt none; W3 6-tuple + vol/yang/vconf/streak/tstate/
    amp/mom/std/rsqr/sumn/resi/cnt none; W4 7-tuple + yang/vconf/
    streak/tstate/amp/mom/std/rsqr/sumn/resi/cnt none; W5 8-tuple +
    vconf/streak/tstate/amp/mom/std/rsqr/sumn/resi/cnt none; W6
    9-tuple + streak/tstate/amp/mom/std/rsqr/sumn/resi/cnt none; W7
    10-tuple + tstate/amp/mom/std/rsqr/sumn/resi/cnt none; W8 11-tuple
    + amp/mom/std/rsqr/sumn/resi/cnt none; W9 12-tuple + mom/std/rsqr/
    sumn/resi/cnt none; W10 13-tuple + std/rsqr/sumn/resi/cnt none;
    W11 14-tuple + rsqr/sumn/resi/cnt none; W12 15-tuple + sumn/resi/
    cnt none; W13 16-tuple + resi/cnt none; MASS via the declared
    translation); resi/cnt in member values = new-syntax legal cells
    (never excluded)."""
    g13 = tl13.build_grammar_w13()    # frozen W13 machinery face
    excl = []
    for e in g13["exclusion"]["stop_gate_vol_yang_vconf_streak_"
                             "tstate_amp_mom_std_rsqr_sumn_none_face"]:
        excl.append({**e, "axis": list(e["axis"]) + ["none", "none"],
                     "face": "stop-gate-vol-yang-vconf-streak-"
                             "tstate-amp-mom-std-rsqr-sumn-resi-cnt-"
                             "none"})
    grammar = {
        "wave": WAVE, "prereg": PREREG, "evidence_cutoff": CUTOFF,
        "grammar_kind": "w14-resicnt-gate-extended",
        "seeds": {"trial_labor_w14_gen": SEED_GEN,
                  "trial_labor_w14_scrnull": SEED_NULL,
                  "trial_labor_w14_unc": SEED_UNC,
                  "derivation": "Sobol(seed=20327500+family_idx, "
                                "scramble) param box + default_rng("
                                "[20327500+family_idx, 7919]) EIGHTEEN-"
                                "tuple axis stream R/X/S/T/STOP/GATE/"
                                "VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/"
                                "STD/RSQR/SUMN/RESI/CNT (prereg s.3; "
                                "A idx 0-5, B idx 6+slot; the first "
                                "sixteen axis arrays are the W13-order "
                                "stream VERBATIM -- order-frozen "
                                "consumption law; the resi+cnt legs "
                                "append AFTER sumn, zero disturbance; "
                                "berths 20327500/20328000/20328500 "
                                "held at the freeze commit per R250 "
                                "one-step law, bm-b r471 three-step "
                                "re-verify ALL GREEN no re-pick; berth "
                                "adoption lineage AMP->W9/MOM->W10/STD->"
                                "W11/RSQR->W12/SUMN->W13/RESI+CNT->W14)"},
        "n_draws": {"A": N_A, "B": N_B}, "k_nulls": K_NULLS,
        "axes": {**g13["axes"], "resi": AXIS_RESI, "cnt": AXIS_CNT},
        "axis_combos": AXIS_COMBOS,
        "stop_formula": g13["stop_formula"],
        "stop_fill_mapping": g13["stop_fill_mapping"],
        "gate_spec": g13["gate_spec"],
        "vol_spec": g13["vol_spec"],
        "yang_spec": g13["yang_spec"],
        "vconf_spec": g13["vconf_spec"],
        "streak_spec": g13["streak_spec"],
        "tstate_spec": g13["tstate_spec"],
        "amp_spec": g13["amp_spec"],
        "mom_spec": g13["mom_spec"],
        "std_spec": g13["std_spec"],
        "rsqr_spec": g13["rsqr_spec"],
        "sumn_spec": g13["sumn_spec"],
        "resi_spec": RESI_SPEC,
        "cnt_spec": CNT_SPEC,
        "vol_anchor": g13["vol_anchor"],
        "yang_anchor": g13["yang_anchor"],
        "vconf_anchor": g13["vconf_anchor"],
        "streak_anchor": g13["streak_anchor"],
        "tstate_anchor": g13["tstate_anchor"],
        "amp_anchor": g13["amp_anchor"],
        "mom_anchor": g13["mom_anchor"],
        "std_anchor": g13["std_anchor"],
        "rsqr_anchor": g13["rsqr_anchor"],
        "sumn_anchor": g13["sumn_anchor"],
        "resi_anchor": RESI_ANCHOR,
        "cnt_anchor": CNT_ANCHOR,
        "families": g13["families"], "value_domains": g13["value_domains"],
        "faces": g13["faces"],
        "exclusion": {
            "stop_gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_"
            "sumn_resi_cnt_none_face":
                excl,
            "sources": list(g13["exclusion"]["sources"])
            + ["w13 screen survivors (generate-time real-read; "
               "W13 = THIRTEENTH screen source, seventh full-declare "
               "window)",
               "w13 judge products (generate-time real-read "
               "re-declare window; W13-JUDGE landed 2026-09-30 "
               "12:28 = FOURTEENTH judged source)"],
            "note": "exclusion face = resi=none AND cnt=none only; "
                    "prior-wave keys resi/cnt-none-completed "
                    "(semantic identity match); resi/cnt in member "
                    "values = new-syntax legal cells (prereg sec.1)"},
        "negative_priors": g13.get("negative_priors"),
        "inventory_audit": g13["inventory_audit"],
    }
    grammar["grammar_sha256"] = _grammar_sha16(grammar)
    return grammar
