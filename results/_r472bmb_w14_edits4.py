"""_r472bmb_w14_edits4.py -- screen-finalize: resi/cnt + 18-tuple
interaction segs, counts, output keys, print.  Count-verified."""
import sys

DRAFT = "results/_r472bmb_w14_runner_draft.py"
text = open(DRAFT, encoding="utf-8").read()
log = []


def rep(old, new, expect=1, name=""):
    global text
    n = text.count(old)
    if n != expect:
        print(f"EDIT4-FAIL [{name}]: found {n} != {expect}")
        sys.exit(1)
    text = text.replace(old, new)
    log.append((name, n))


# 1. counts dict inits
rep("""    rsqr_counts = {}
    sumn_counts = {}
    gate_seg, vol_seg, yang_seg, vconf_seg = {}, {}, {}, {}
    streak_seg, tstate_seg, amp_seg, mom_seg = {}, {}, {}, {}
    gvvy_seg, gvvvsk_seg, gvvvskts_seg = {}, {}, {}
    gvvvsktsa_seg, gvvvsktsam_seg, gvvvsktsams_seg = {}, {}, {}
    gvvvsktsamsr_seg = {}
    std_seg, rsqr_seg, sumn_seg, gvvvsktsamsrn_seg = {}, {}, {}, {}""",
    """    rsqr_counts = {}
    sumn_counts = {}
    resi_counts = {}
    cnt_counts = {}
    gate_seg, vol_seg, yang_seg, vconf_seg = {}, {}, {}, {}
    streak_seg, tstate_seg, amp_seg, mom_seg = {}, {}, {}, {}
    gvvy_seg, gvvvsk_seg, gvvvskts_seg = {}, {}, {}
    gvvvsktsa_seg, gvvvsktsam_seg, gvvvsktsams_seg = {}, {}, {}
    gvvvsktsamsr_seg = {}
    std_seg, rsqr_seg, sumn_seg, gvvvsktsamsrn_seg = {}, {}, {}, {}
    resi_seg, cnt_seg, gvvvsktsamsrnrc_seg = {}, {}, {}""",
    1, "seg/count inits")

# 2. per-row count lines
rep("""        rsqr_counts[rqf] = rsqr_counts.get(rqf, 0) + 1
        sumn_counts[nqf] = sumn_counts.get(nqf, 0) + 1""",
    """        rsqr_counts[rqf] = rsqr_counts.get(rqf, 0) + 1
        sumn_counts[nqf] = sumn_counts.get(nqf, 0) + 1
        resf = r["resi_face"]
        cntf = r["cnt_face"]
        resi_counts[resf] = resi_counts.get(resf, 0) + 1
        cnt_counts[cntf] = cnt_counts.get(cntf, 0) + 1""",
    1, "per-row counts")

# 3. seg loop tuple
rep("""                         (gvvvsktsamsrn_seg,
                          f"{gf}|{vf}|{yf}|{cf}|{sf}|{tf}|{af}|{mf}|"
                          f"{stf}|{rqf}|{nqf}")):""",
    """                         (gvvvsktsamsrn_seg,
                          f"{gf}|{vf}|{yf}|{cf}|{sf}|{tf}|{af}|{mf}|"
                          f"{stf}|{rqf}|{nqf}"),
                         (resi_seg, resf),
                         (cnt_seg, cntf),
                         (gvvvsktsamsrnrc_seg,
                          f"{gf}|{vf}|{yf}|{cf}|{sf}|{tf}|{af}|{mf}|"
                          f"{stf}|{rqf}|{nqf}|{resf}|{cntf}")):""",
    1, "seg loop tuple")

# 4. seg fix loop list
rep("""    for seg in (gate_seg, vol_seg, yang_seg, vconf_seg, streak_seg,
                tstate_seg, amp_seg, mom_seg, std_seg, rsqr_seg, sumn_seg, gvvy_seg,
                gvvvsk_seg, gvvvskts_seg, gvvvsktsa_seg,
                gvvvsktsam_seg, gvvvsktsams_seg, gvvvsktsamsr_seg, gvvvsktsamsrn_seg):""",
    """    for seg in (gate_seg, vol_seg, yang_seg, vconf_seg, streak_seg,
                tstate_seg, amp_seg, mom_seg, std_seg, rsqr_seg, sumn_seg,
                resi_seg, cnt_seg, gvvy_seg,
                gvvvsk_seg, gvvvskts_seg, gvvvsktsa_seg,
                gvvvsktsam_seg, gvvvsktsams_seg, gvvvsktsamsr_seg,
                gvvvsktsamsrn_seg, gvvvsktsamsrnrc_seg):""",
    1, "seg fix loop")

# 5. output dict: counts keys
rep('''           "rsqr_face_counts": rsqr_counts,
           "sumn_face_counts": sumn_counts,''',
    '''           "rsqr_face_counts": rsqr_counts,
           "sumn_face_counts": sumn_counts,
           "resi_face_counts": resi_counts,
           "cnt_face_counts": cnt_counts,''',
    1, "output counts")

# 6. output dict: seg keys
rep('''           "rsqr_segmented_survival": rsqr_seg,
           "sumn_segmented_survival": sumn_seg,''',
    '''           "rsqr_segmented_survival": rsqr_seg,
           "sumn_segmented_survival": sumn_seg,
           "resi_segmented_survival": resi_seg,
           "cnt_segmented_survival": cnt_seg,''',
    1, "output segs")

# 7. output dict: 18-tuple interaction
rep('''           "gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_sumn_interaction_"
           "survival": gvvvsktsamsrn_seg,''',
    '''           "gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_sumn_interaction_"
           "survival": gvvvsktsamsrn_seg,
           "gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_sumn_"
           "resi_cnt_interaction_survival": gvvvsktsamsrnrc_seg,''',
    1, "output 18-tuple")

open(DRAFT, "w", encoding="utf-8", newline="\n").write(text)
print(f"edits4 OK: {len(log)} verified replacements")
for name, n in log:
    print(f"  [{name}] x{n}")
