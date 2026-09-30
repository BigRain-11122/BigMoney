"""_r472bmb_w14_edits3.py -- screen-prep: identity-first-run reorder
(candidates gate to tail), G-RESI/G-CNT gates, leg-L faces, prep dict
+ print.  Count-verified."""
import sys

DRAFT = "results/_r472bmb_w14_runner_draft.py"
text = open(DRAFT, encoding="utf-8").read()
log = []


def rep(old, new, expect=1, name=""):
    global text
    n = text.count(old)
    if n != expect:
        print(f"EDIT3-FAIL [{name}]: found {n} != {expect}")
        sys.exit(1)
    text = text.replace(old, new)
    log.append((name, n))


# 1. docstring gate list (honest full list)
OLD_GATES = ('    """G-PANEL / G-ANCHOR / G-CENSUS / G-EXCLUDE / G-VOL'
             ' / G-YANG /\n    G-VCONF / G-STREAK / G-TSTATE / G-AMP'
             ' / G-MOM fail-closed gates +')
NEW_GATES = ('    """G-PANEL / G-ANCHOR / G-CENSUS / G-EXCLUDE / G-VOL'
             ' / G-YANG /\n    G-VCONF / G-STREAK / G-TSTATE / G-AMP'
             ' / G-MOM / G-STD / G-RSQR /\n    G-SUMN / G-RESI / G-CNT'
             ' fail-closed gates +')
rep(OLD_GATES, NEW_GATES, 1, "prep docstring gates")

# 2. head gate reorder (identity-first-run law)
rep("""    print(f"=== {WAVE} screen-prep (fail-closed gates) ===")
    for p, what in ((GRAMMAR_FILE, "w14_grammar.json"),
                    (CANDIDATES_FILE, "w14_candidates.json")):
        if not os.path.exists(p):
            print(f"PREP-GATE FAIL: {what} absent -- generate pending")
            return 2
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    if FROZEN_SHA16 and _grammar_sha16(grammar) != FROZEN_SHA16:
        print(f"PREP-GATE FAIL: grammar sha drift "
              f"{grammar['grammar_sha256'][:16]} != frozen {FROZEN_SHA16}")
        return 1
    cg = json.load(open(CANDIDATES_FILE, encoding="utf-8"))
    if str(cg.get("grammar_sha256", ""))[:16] != (FROZEN_SHA16
                                                  or
                                                  grammar[
                                                      "grammar_sha256"][
                                                      :16]):
        print("PREP-GATE FAIL: candidates grammar_sha256 != frozen anchor")
        return 1
    tl1.GRAMMAR = grammar   # tl1._signal_frame reads tl1's global""",
    """    print(f"=== {WAVE} screen-prep (fail-closed gates) ===")
    # r446bmb three-command identity-first-run law: ALL panel/anchor/
    # census identity faces run BEFORE the candidates-presence refusal
    # so the full identity face exercises on real data pre-generate
    # (rc=2 honest "generate pending" lands at the TAIL; W12 r446
    # precedent + prereg sec.9 sequencing adjudication)
    if not os.path.exists(GRAMMAR_FILE):
        print("PREP-GATE FAIL: w14_grammar.json absent -- run `grammar` "
              "first")
        return 2
    grammar = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    if FROZEN_SHA16 and _grammar_sha16(grammar) != FROZEN_SHA16:
        print(f"PREP-GATE FAIL: grammar sha drift "
              f"{grammar['grammar_sha256'][:16]} != frozen {FROZEN_SHA16}")
        return 1
    tl1.GRAMMAR = grammar   # tl1._signal_frame reads tl1's global""",
    1, "prep head reorder")

# 3. G-RESI/G-CNT gates after G-SUMN
rep("""    sumn_state_full, sumn_err = _sumn_state_full()
    if sumn_err:
        print(f"PREP-GATE FAIL: G-SUMN {sumn_err}")
        return 1
    sumn_meta_core = sumn_state_full[2]

    # G-ANCHOR: registered six replayed through the W10 grammar""",
    """    sumn_state_full, sumn_err = _sumn_state_full()
    if sumn_err:
        print(f"PREP-GATE FAIL: G-SUMN {sumn_err}")
        return 1
    sumn_meta_core = sumn_state_full[2]

    # G-RESI on the raw full-history face (prereg sec.2/3 probe basis
    # = data/daily/sh510300.csv; 120-bar warmup + probe anchors
    # resi60 decidable 3,363 / open 390 (11.20%) + slope split 352/38
    # + nine-gate 512-cell 103/409 max 41 + extreme-day states + the
    # r470 facts per-cell cross-check)
    resi_state_full, resi_err = _resi_state_full()
    if resi_err:
        print(f"PREP-GATE FAIL: G-RESI {resi_err}")
        return 1
    resi_meta_core = resi_state_full[2]

    # G-CNT on the raw full-history face (prereg sec.2/3 probe basis
    # = data/daily/sh510300.csv; 119-bar first-decidable one-bar
    # construction-family note + cntd5 3,364/137 (3.93% thin tail) +
    # cntn20 3,364/265 (7.61%) + grids 109/403 + 103/409 + the
    # r470/r471 facts per-cell cross-checks)
    cnt_state_full, cnt_err = _cnt_state_full()
    if cnt_err:
        print(f"PREP-GATE FAIL: G-CNT {cnt_err}")
        return 1
    cnt_meta_core = cnt_state_full[4]

    # G-ANCHOR: registered six replayed through the W10 grammar""",
    1, "G-RESI/G-CNT gates")

# 4. leg-L member tuple
rep("""    for member, gate_name in ((tl7.STREAK_MEMBER, "streak"),
                              (tl8.TSTATE_MEMBER, "tstate"),
                              (AMP_MEMBER, "amp"),
                              (MOM_MEMBER, "mom"), (STD_MEMBER, "std"),
                              (RSQR_MEMBER, "rsqr"),
                              (SUMN_MEMBER, "sumn")):
        if member not in prices:
            print(f"PREP-GATE FAIL: leg-L panel missing {gate_name} "
                  f"member {member} ({gate_name} series underivable)")
            return 1""",
    """    for member, gate_name in ((tl7.STREAK_MEMBER, "streak"),
                              (tl8.TSTATE_MEMBER, "tstate"),
                              (AMP_MEMBER, "amp"),
                              (MOM_MEMBER, "mom"), (STD_MEMBER, "std"),
                              (RSQR_MEMBER, "rsqr"),
                              (SUMN_MEMBER, "sumn"),
                              (RESI_MEMBER, "resi"),
                              (CNT_MEMBER, "cnt")):
        if member not in prices:
            print(f"PREP-GATE FAIL: leg-L panel missing {gate_name} "
                  f"member {member} ({gate_name} series underivable)")
            return 1""",
    1, "leg-L members")

# 5. leg-L structural passes
rep("""    _n20o, _n20d, sumn_meta, _n10o, _n10d = sumn_state_series(prices)
    if not _sumn_structure_pass(sumn_meta):
        print(f"PREP-GATE FAIL: G-SUMN leg-L structural "
              f"invariants broken {sumn_meta} -- honest refuse")
        return 1
    close = P["close"]""",
    """    _n20o, _n20d, sumn_meta, _n10o, _n10d = sumn_state_series(prices)
    if not _sumn_structure_pass(sumn_meta):
        print(f"PREP-GATE FAIL: G-SUMN leg-L structural "
              f"invariants broken {sumn_meta} -- honest refuse")
        return 1
    _ro, _rd, resi_meta = resi_state_series(prices)
    if not _resi_structure_pass(resi_meta):
        print(f"PREP-GATE FAIL: G-RESI leg-L structural "
              f"invariants broken {resi_meta} -- honest refuse")
        return 1
    _cd5o, _cd5d, _cn20o, _cn20d, cnt_meta = cnt_state_series(prices)
    if not _cnt_structure_pass(cnt_meta):
        print(f"PREP-GATE FAIL: G-CNT leg-L structural "
              f"invariants broken {cnt_meta} -- honest refuse")
        return 1
    close = P["close"]""",
    1, "leg-L structural passes")

# 6. candidates gate at the TAIL (before prep assembly)
rep("""        passive_6m[int(p)] = round(float(rel.iloc[-1] - 1.0), 6)

    prep = {"wave": WAVE, "evidence_cutoff": CUTOFF,""",
    """        passive_6m[int(p)] = round(float(rel.iloc[-1] - 1.0), 6)

    # candidates-presence gate at the TAIL (identity-first-run law:
    # every panel/anchor/census face above has ALREADY exercised on
    # real data by this point; generate-stage product face)
    if not os.path.exists(CANDIDATES_FILE):
        print("PREP-GATE FAIL: w14_candidates.json absent -- generate "
              "pending (identity faces above ALL PASS on real data)")
        return 2
    cg = json.load(open(CANDIDATES_FILE, encoding="utf-8"))
    if str(cg.get("grammar_sha256", ""))[:16] != (FROZEN_SHA16
                                                  or
                                                  grammar[
                                                      "grammar_sha256"][
                                                      :16]):
        print("PREP-GATE FAIL: candidates grammar_sha256 != frozen "
              "anchor")
        return 1

    prep = {"wave": WAVE, "evidence_cutoff": CUTOFF,""",
    1, "candidates tail gate")

# 7. prep dict G-RESI/G-CNT entries
rep('''                       "G-SUMN": {"pass": True,
                                  "core48": sumn_meta_core,
                                  "legL": sumn_meta},''',
    '''                       "G-SUMN": {"pass": True,
                                  "core48": sumn_meta_core,
                                  "legL": sumn_meta},
                      "G-RESI": {"pass": True,
                                 "core48": resi_meta_core,
                                 "legL": resi_meta},
                      "G-CNT": {"pass": True,
                                "core48": cnt_meta_core,
                                "legL": cnt_meta},''',
    1, "prep dict gates")

# 8. prep dict meta keys
rep("""            "rsqr_meta": rsqr_meta,
            "sumn_meta": sumn_meta,
            "n_distinct": cg["n"], "n_starts_6m": len(starts),""",
    """            "rsqr_meta": rsqr_meta,
            "sumn_meta": sumn_meta,
            "resi_meta": resi_meta,
            "cnt_meta": cnt_meta,
            "n_distinct": cg["n"], "n_starts_6m": len(starts),""",
    1, "prep dict metas")

# 9. prep print tail
rep("""          f"G-SUMN {sumn_meta['open_days']}open/"
          f"{sumn_meta['closed_days']}closed decidable "
          f"{sumn_meta['decidable_days']} sumn10-open "
          f"{sumn_meta['sumn10_open_days']}")
    return 0""",
    """          f"G-SUMN {sumn_meta['open_days']}open/"
          f"{sumn_meta['closed_days']}closed decidable "
          f"{sumn_meta['decidable_days']} sumn10-open "
          f"{sumn_meta['sumn10_open_days']}; "
          f"G-RESI {resi_meta['open_days']}open/"
          f"{resi_meta['closed_days']}closed decidable "
          f"{resi_meta['decidable_days']} slope-split "
          f"{resi_meta['slope_sign_split']}; "
          f"G-CNT cntd5 {cnt_meta['cntd5_open_days']}open/"
          f"{cnt_meta['cntd5_decidable_days']}decidable + cntn20 "
          f"{cnt_meta['cntn20_open_days']}open/"
          f"{cnt_meta['cntn20_decidable_days']}decidable")
    return 0""",
    1, "prep print")

open(DRAFT, "w", encoding="utf-8", newline="\n").write(text)
print(f"edits3 OK: {len(log)} verified replacements")
for name, n in log:
    print(f"  [{name}] x{n}")
