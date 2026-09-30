"""_r472bmb_w14_edits1.py -- targeted edits: effective-signal mask,
run_candidate_curve (resi/cnt layers + 19-tuple return), null axis
draw (+2 legs).  Count-verified ordered replacements."""
import sys

DRAFT = "results/_r472bmb_w14_runner_draft.py"
text = open(DRAFT, encoding="utf-8").read()
log = []


def rep(old, new, expect=1, name=""):
    global text
    n = text.count(old)
    if n != expect:
        print(f"EDIT1-FAIL [{name}]: found {n} != {expect}")
        sys.exit(1)
    text = text.replace(old, new)
    log.append((name or old[:44], n))


# --- _effective_signal_mask_w14: signature + layers ---
rep("""def _effective_signal_mask_w14(mask, prices, stop_key, atr20, gate_key,
                               vol_key, yang_key, vconf_key, streak_key,
                               tstate_key, amp_key, mom_key, std_key,
                               rsqr_key, sumn_key, gate_state, vol_state, yang_state,
                               vconf_state, streak_state, tstate_state,
                               amp_state, mom_state, std_state, rsqr_state,
                               sumn_state):""",
    """def _effective_signal_mask_w14(mask, prices, stop_key, atr20, gate_key,
                               vol_key, yang_key, vconf_key, streak_key,
                               tstate_key, amp_key, mom_key, std_key,
                               rsqr_key, sumn_key, resi_key, cnt_key,
                               gate_state, vol_state, yang_state,
                               vconf_state, streak_state, tstate_state,
                               amp_state, mom_state, std_state, rsqr_state,
                               sumn_state, resi_state, cnt_state):""",
    1, "eff-mask signature")

rep("""    MO = mom_zero_mask(AP, mom_key, mom_state)
    SD = std_zero_mask(MO, std_key, std_state)
    RQ = rsqr_zero_mask(SD, rsqr_key, rsqr_state)
    SU = sumn_zero_mask(RQ, sumn_key, sumn_state)
    return tl2._effective_signal_mask(SU, prices, stop_key, atr20)""",
    """    MO = mom_zero_mask(AP, mom_key, mom_state)
    SD = std_zero_mask(MO, std_key, std_state)
    RQ = rsqr_zero_mask(SD, rsqr_key, rsqr_state)
    SU = sumn_zero_mask(RQ, sumn_key, sumn_state)
    RE = resi_zero_mask(SU, resi_key, resi_state)
    CN = cnt_zero_mask(RE, cnt_key, cnt_state)
    return tl2._effective_signal_mask(CN, prices, stop_key, atr20)""",
    1, "eff-mask layers")

# --- run_candidate_curve_w14: signature + keys + defaults + layers +
# zeroed counts + return ---
rep("""                           mom_state=None, std_state=None, rsqr_state=None,
                           sumn_state=None):""",
    """                           mom_state=None, std_state=None, rsqr_state=None,
                           sumn_state=None, resi_state=None,
                           cnt_state=None):""",
    1, "curve signature")

rep("""    std_key = cand["axis"][13]
    rsqr_key = cand["axis"][14]
    sumn_key = cand["axis"][15]""",
    """    std_key = cand["axis"][13]
    rsqr_key = cand["axis"][14]
    sumn_key = cand["axis"][15]
    resi_key = cand["axis"][16]
    cnt_key = cand["axis"][17]""",
    1, "curve axis keys")

rep("""    if sumn_state is None:
        sumn_state = sumn_state_series(prices)""",
    """    if sumn_state is None:
        sumn_state = sumn_state_series(prices)
    if resi_state is None:
        resi_state = resi_state_series(prices)
    if cnt_state is None:
        cnt_state = cnt_state_series(prices)""",
    1, "curve state defaults")

rep("""    MO = mom_zero_mask(AP, mom_key, mom_state)
    SD = std_zero_mask(MO, std_key, std_state)
    RQ = rsqr_zero_mask(SD, rsqr_key, rsqr_state)
    SU = sumn_zero_mask(RQ, sumn_key, sumn_state)
    gate_zeroed = int((mask > 0).sum().sum() - (G > 0).sum().sum())""",
    """    MO = mom_zero_mask(AP, mom_key, mom_state)
    SD = std_zero_mask(MO, std_key, std_state)
    RQ = rsqr_zero_mask(SD, rsqr_key, rsqr_state)
    SU = sumn_zero_mask(RQ, sumn_key, sumn_state)
    RE = resi_zero_mask(SU, resi_key, resi_state)
    CN = cnt_zero_mask(RE, cnt_key, cnt_state)
    gate_zeroed = int((mask > 0).sum().sum() - (G > 0).sum().sum())""",
    1, "curve layers")

rep("""    sumn_zeroed = int((RQ > 0).sum().sum() - (SU > 0).sum().sum())
    if stop_key == "none":
        S, stop_fired = SU, 0
    else:
        S = tl2._effective_signal_mask(SU, prices, stop_key, atr20)
        d = (SU > 0) & (S == 0)""",
    """    sumn_zeroed = int((RQ > 0).sum().sum() - (SU > 0).sum().sum())
    resi_zeroed = int((SU > 0).sum().sum() - (RE > 0).sum().sum())
    cnt_zeroed = int((RE > 0).sum().sum() - (CN > 0).sum().sum())
    if stop_key == "none":
        S, stop_fired = CN, 0
    else:
        S = tl2._effective_signal_mask(CN, prices, stop_key, atr20)
        d = (CN > 0) & (S == 0)""",
    1, "curve zeroed + stop source")

rep("""    return eq, res["trades"], res["metrics"], params, patch, stop_fired, \\
        gate_zeroed, vol_zeroed, yang_zeroed, vconf_zeroed, \\
        streak_zeroed, tstate_zeroed, amp_zeroed, mom_zeroed, \\
        std_zeroed, rsqr_zeroed, sumn_zeroed""",
    """    return eq, res["trades"], res["metrics"], params, patch, stop_fired, \\
        gate_zeroed, vol_zeroed, yang_zeroed, vconf_zeroed, \\
        streak_zeroed, tstate_zeroed, amp_zeroed, mom_zeroed, \\
        std_zeroed, rsqr_zeroed, sumn_zeroed, resi_zeroed, cnt_zeroed""",
    1, "curve return")

# --- _null_axis_draw_w14: +2 draws ---
rep("""          AXIS_RSQR[int(rng.integers(len(AXIS_RSQR)))],
          AXIS_SUMN[int(rng.integers(len(AXIS_SUMN)))])
    return p_on, list(ax), rng""",
    """          AXIS_RSQR[int(rng.integers(len(AXIS_RSQR)))],
          AXIS_SUMN[int(rng.integers(len(AXIS_SUMN)))],
          AXIS_RESI[int(rng.integers(len(AXIS_RESI)))],
          AXIS_CNT[int(rng.integers(len(AXIS_CNT)))])
    return p_on, list(ax), rng""",
    1, "null draw +2")

open(DRAFT, "w", encoding="utf-8", newline="\n").write(text)
print(f"edits1 OK: {len(log)} verified replacements")
for name, n in log:
    print(f"  [{name}] x{n}")
