# --------------------------------------------- exclusion (28 real-reads)
def _load_exclusion_rows_w14(grammar):
    """FOURTEEN judged + FOURTEEN screen real-read source faces + the
    frozen serialized grammar face (prereg sec.1), all real-read at
    generate time.  All prior-wave keys are padded to the W14
    EIGHTEEN-tuple with resi/cnt=none (semantic-identity completion
    law).  Sources: 1 = frozen serialized grammar stop-gate-vol-...
    -sumn-resi-cnt-none face (18-tuple at build); 2-15 = W1/W2/MASS
    (declared tl3 translation)/W3/W4/W5/W6/W7/W8/W9/W10/W11/W12/W13
    screen survivors -- W13 is NEW vs the W13 runner's own loader
    (generate-time real-read; absent at build = zero rows honest per
    prereg sec.1); 16-29 = judged products (w1_judge / MASS judged /
    w2_judge ... w13_judge) -- generate-time real-read re-declare
    window (declared-unavailable -> zero rows, no fabrication).
    Honest tag note: the W13 runner's loader carried an off-by-one
    disc-key drift (files of wave N tagged wN+1) -- rows consumed were
    always correct (exact-key law); the W14 loader tags each source by
    its OWN wave number (cosmetic fix, zero effect on rows)."""
    rows = list(grammar["exclusion"]
                ["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_std_"
                 "rsqr_sumn_resi_cnt_none_face"])
    disc = {"grammar_stop_gate_vol_yang_vconf_streak_tstate_"
            "amp_mom_std_rsqr_sumn_resi_cnt_none_rows": len(rows)}

    def _screen_survivors(scr_path, cand_path, pad, tag):
        if not (os.path.exists(scr_path) and os.path.exists(cand_path)):
            return f"declared-unavailable ({os.path.basename(scr_path)} " \
                   f"absent)"
        scr = json.load(open(scr_path, encoding="utf-8"))
        cands = {c["candidate_id"]: c for c in
                 json.load(open(cand_path, encoding="utf-8"))["candidates"]}
        n = 0
        for cid in sorted(scr.get("survivors", [])):
            c = cands[cid]
            rows.append({"module": c["module"], "fn": c["fn"],
                         "sig_params": c["sig_params"],
                         "axis": list(c["axis"]) + pad,
                         "face": f"{tag}:stop-gate-vol-yang-vconf-"
                                 "streak-tstate-amp-mom-std-rsqr-sumn-"
                                 "resi-cnt-none",
                         "candidate_id": cid})
            n += 1
        return n

    # pads to the EIGHTEEN-tuple: wave axis-tuple length + pad == 18
    disc["w1_screen_survivors"] = _screen_survivors(
        os.path.join(tl1.RES_DIR, "w1_screen.json"),
        os.path.join(tl1.RES_DIR, "w1_candidates.json"),
        ["none"] * 14, "w1_screen_survivor")
    disc["w2_screen_survivors"] = _screen_survivors(
        os.path.join(tl2.RES_DIR, "w2_screen.json"),
        os.path.join(tl2.RES_DIR, "w2_candidates.json"),
        ["none"] * 13, "w2_screen_survivor")
    disc["w3_screen_survivors"] = _screen_survivors(
        os.path.join(tl3.RES_DIR, "w3_screen.json"),
        os.path.join(tl3.RES_DIR, "w3_candidates.json"),
        ["none"] * 12, "w3_screen_survivor")
    disc["w4_screen_survivors"] = _screen_survivors(
        tl4.SCREEN_FILE, tl4.CANDIDATES_FILE,
        ["none"] * 11, "w4_screen_survivor")
    disc["w5_screen_survivors"] = _screen_survivors(
        tl5.SCREEN_FILE, tl5.CANDIDATES_FILE,
        ["none"] * 10, "w5_screen_survivor")
    disc["w6_screen_survivors"] = _screen_survivors(
        tl6.SCREEN_FILE, tl6.CANDIDATES_FILE,
        ["none"] * 9, "w6_screen_survivor")
    disc["w7_screen_survivors"] = _screen_survivors(
        tl7.SCREEN_FILE, tl7.CANDIDATES_FILE,
        ["none"] * 8, "w7_screen_survivor")
    disc["w8_screen_survivors"] = _screen_survivors(
        tl8.SCREEN_FILE, tl8.CANDIDATES_FILE,
        ["none"] * 7, "w8_screen_survivor")
    disc["w9_screen_survivors"] = _screen_survivors(
        tl9.SCREEN_FILE, tl9.CANDIDATES_FILE,
        ["none"] * 6, "w9_screen_survivor")
    disc["w10_screen_survivors"] = _screen_survivors(
        tl10.SCREEN_FILE, tl10.CANDIDATES_FILE,
        ["none"] * 5, "w10_screen_survivor")
    disc["w11_screen_survivors"] = _screen_survivors(
        tl11.SCREEN_FILE, tl11.CANDIDATES_FILE,
        ["none"] * 4, "w11_screen_survivor")
    disc["w12_screen_survivors"] = _screen_survivors(
        tl12.SCREEN_FILE, tl12.CANDIDATES_FILE,
        ["none"] * 3, "w12_screen_survivor")
    disc["w13_screen_survivors"] = _screen_survivors(
        tl13.SCREEN_FILE, tl13.CANDIDATES_FILE,
        ["none"] * 2, "w13_screen_survivor")

    # MASS screen survivors: declared tl3 translation + the same
    # none-pad (translated rows are 6-tuples -> 12 more to 18)
    if os.path.exists(tl6.MASS_SCREEN_CKPT):
        n_tr = n_bad = 0
        with open(tl6.MASS_SCREEN_CKPT, encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln:
                    continue
                r = json.loads(ln)
                if r.get("row_type") != "candidate" \
                        or not r.get("screen_pass"):
                    continue
                tr = tl3._mass_translate_row(r)
                if tr is None:
                    n_bad += 1
                    continue
                tr["axis"] = list(tr["axis"]) + ["none"] * 12
                tr["face"] = "mass_screen_survivor:translated-exact"
                tr["candidate_id"] = r.get("id")
                rows.append(tr)
                n_tr += 1
        disc["mass_screen_survivors"] = {
            "consumed_pass_rows": n_tr + n_bad,
            "translated_exact_rows": n_tr,
            "non_translatable_disclosed": n_bad,
            "note": tl6.MASS_TRANSLATION_NOTE}
    else:
        disc["mass_screen_survivors"] = "declared-unavailable " \
                                        "(screen_checkpoint.jsonl absent)"

    # judged products: generate-time real-read re-declare window
    # (prereg sec.1/sec.9); absent -> declared-unavailable zero rows
    # (freeze-time expectation per prereg sec.0 (d): W1/MASS/W2/W3/
    # W4/W5/W6/W7/W8/W9/W10/W11/W12 judged landed; W13-JUDGE landed
    # 2026-09-30 12:28 -- FOURTEEN sources, seventh full-declare
    # window in history -- live re-read at generate time is the law)
    def _judged_source(jpath, cand_path, pad, tag, mass=False):
        if not os.path.exists(jpath):
            return "declared-unavailable at generate time " \
                   f"({os.path.basename(jpath)} absent; pool-waiting); " \
                   "zero rows"
        j = json.load(open(jpath, encoding="utf-8"))
        cells = j.get("cells", [])
        n = 0
        cands = {}
        if not mass and cand_path and os.path.exists(cand_path):
            cands = {c["candidate_id"]: c for c in json.load(
                open(cand_path, encoding="utf-8"))["candidates"]}
        for c in cells:
            if mass:
                tr = tl3._mass_translate_row(c)
                if tr is None:
                    continue
                tr["axis"] = list(tr["axis"]) + ["none"] * 12
                tr["face"] = f"{tag}:translated-exact"
                rows.append(tr)
            else:
                src = cands.get(c.get("candidate_id"))
                if src is None:
                    continue
                rows.append({"module": src["module"], "fn": src["fn"],
                             "sig_params": src["sig_params"],
                             "axis": list(src["axis"]) + pad,
                             "face": f"{tag}:stop-gate-vol-"
                                     "yang-vconf-streak-tstate-amp-"
                                     "mom-std-rsqr-sumn-resi-cnt-none",
                             "candidate_id": c.get("candidate_id")})
            n += 1
        return {"consumed_rows": n,
                "note": "judged product consumed as exclusion rows "
                        "(exact-key law, positive or negative verdicts "
                        "alike)"}

    disc["w1_judge_products"] = _judged_source(
        tl6.W1_JUDGE_FILE, os.path.join(tl1.RES_DIR, "w1_candidates.json"),
        ["none"] * 14, "w1_judged")
    disc["mass_judge_products"] = _judged_source(
        tl6.MASS_JUDGE_FILE, None, None, "mass_judged", mass=True)
    disc["w2_judge_products"] = _judged_source(
        tl6.W2_JUDGE_FILE, os.path.join(tl2.RES_DIR, "w2_candidates.json"),
        ["none"] * 13, "w2_judged")
    disc["w3_judge_products"] = _judged_source(
        tl6.W3_JUDGE_FILE, os.path.join(tl3.RES_DIR, "w3_candidates.json"),
        ["none"] * 12, "w3_judged")
    disc["w4_judge_products"] = _judged_source(
        tl4.JUDGE_FILE, tl4.CANDIDATES_FILE,
        ["none"] * 11, "w4_judged")
    disc["w5_judge_products"] = _judged_source(
        tl5.JUDGE_FILE, tl5.CANDIDATES_FILE,
        ["none"] * 10, "w5_judged")
    disc["w6_judge_products"] = _judged_source(
        tl6.JUDGE_FILE, tl6.CANDIDATES_FILE,
        ["none"] * 9, "w6_judged")
    disc["w7_judge_products"] = _judged_source(
        tl7.JUDGE_FILE, tl7.CANDIDATES_FILE,
        ["none"] * 8, "w7_judged")
    disc["w8_judge_products"] = _judged_source(
        tl8.JUDGE_FILE, tl8.CANDIDATES_FILE,
        ["none"] * 7, "w8_judged")
    disc["w9_judge_products"] = _judged_source(
        tl9.JUDGE_FILE, tl9.CANDIDATES_FILE,
        ["none"] * 6, "w9_judged")
    disc["w10_judge_products"] = _judged_source(
        tl10.JUDGE_FILE, tl10.CANDIDATES_FILE,
        ["none"] * 5, "w10_judged")
    disc["w11_judge_products"] = _judged_source(
        tl11.JUDGE_FILE, tl11.CANDIDATES_FILE,
        ["none"] * 4, "w11_judged")
    disc["w12_judge_products"] = _judged_source(
        tl12.JUDGE_FILE, tl12.CANDIDATES_FILE,
        ["none"] * 3, "w12_judged")
    disc["w13_judge_products"] = _judged_source(
        tl13.JUDGE_FILE, tl13.CANDIDATES_FILE,
        ["none"] * 2, "w13_judged")
    # (d)-face judged-supply weighting: frozen baseline uniform stands
    # (prereg sec.0 declare; sec.9 re-declare window = live prev
    # increment merged at generate time, uniform baseline absent an
    # append-confirm amendment -- disclosed, no fabrication)
    disc["judged_supply_weighting"] = (
        "frozen baseline uniform per prereg sec.0 declare (axis families "
        "equal allocation, zero judged weighting); sec.9 re-declare window "
        "requires a prereg-level append-confirm BEFORE generate runs -- "
        "none exists, uniform stands, availability of the FOURTEEN judge "
        "products disclosed above (freeze-time fourteen-source "
        "full-declare window = seventh in history)")
    return rows, disc


def _excluded_w14(cand, rows):
    """Exact already-judged cell test, resi/cnt=none face only (prereg
    sec.1: resi/cnt in member values = new-syntax legal cells --
    never excluded; W1-lineage cells implicitly stop/gate/vol/yang/
    vconf/streak/tstate/amp/mom/std/rsqr/sumn/resi/cnt=none; W2 cells
    carry their own stop face; W3 stop+gate; W4 stop+gate+vol; W5
    stop+gate+vol+yang; W6 stop+gate+vol+yang+vconf; W7
    stop+gate+vol+yang+vconf+streak; W8 stop+gate+vol+yang+vconf+
    streak+tstate; W9 +amp; W10 +mom; W11 +std; W12 +rsqr; W13 +sumn).
    Returns the exclusion face or None."""
    if cand["axis"][16] != "none" or cand["axis"][17] != "none":
        return None
    for e in rows:
        if (cand["module"], cand["fn"]) == (e["module"], e["fn"]) \
                and cand["sig_params"] == e["sig_params"] \
                and cand["axis"] == e["axis"]:
            return e.get("face", "excluded")
    return None
