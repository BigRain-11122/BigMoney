"""r442 bm-b: W11 builder stage-2. Input results/_r442bmb_stage1.py ->
output results/_r442bmb_stage2.py. Fn renames, tl10 import, sha pins,
MOM layer -> import-face + NEW STD layer (frozen probe anchors from
results/_r237bmc_stdq90_w11_probe_facts.json), build_grammar, draw.
"""
import json

SRC = open('results/_r442bmb_stage1.py', encoding='utf-8').read()
fails = []


def rep(old, new, tag, must=True, count=None):
    global SRC
    n = SRC.count(old)
    if count is not None and n != count:
        fails.append(f'[{tag}] expected {count} got {n}: {old[:70]!r}')
        return
    if n == 0 and must:
        fails.append(f'[{tag}] NOT FOUND: {old[:70]!r}')
        return
    SRC = SRC.replace(old, new)


# ---------------- function-name renames ----------------
for fn in ('build_grammar_w10', 'draw_candidate_sobol_w10',
           '_load_exclusion_rows_w10', '_excluded_w10',
           '_effective_signal_mask_w10', 'run_candidate_curve_w10',
           '_null_axis_draw_w10', '_screen_cell_w10', '_cell_list_w10',
           '_dual_nulls_w10', '_overlay_stop_disclosure_w10',
           '_judge_cell_w10', 'csv_cols_screen_w10'):
    rep(fn, fn.replace('w10', 'w11'), 'fn:' + fn)

# ---------------- leftovers from stage-1 fails ----------------
rep('[20311000+family_idx, 7919])', '[20317000+family_idx, 7919])',
    'seedder2')
rep('W10 berth 20311500, distinct from the W9 berth 20310000',
    'W11 berth 20317500, distinct from the W10 berth 20311500', 'seednull')
rep('amp overlay (tl9 import face)', 'mom overlay (tl10 import face)',
    'impface-b')
rep('The FULL amp machinery is imported verbatim from tl9 (W9 frozen',
    'The FULL mom machinery is imported verbatim from tl10 (W10 frozen',
    'impface-c1')
rep('# face; import-face law; zero re-implementation) -- the W10 runner only',
    '# face; import-face law; zero re-implementation) -- the W11 runner only',
    'impface-c2')
rep('# adds the NEW mom overlay layer on top of it.',
    '# adds the NEW std overlay layer on top of it.', 'impface-c3')

# ---------------- import chain: add tl10 ----------------
rep('import trial_labor_w9 as tl9  # amp overlay + twelve-tuple machinery\n',
    'import trial_labor_w9 as tl9  # amp overlay + twelve-tuple machinery\n'
    'import trial_labor_w10 as tl10  # mom overlay + thirteen-tuple machinery\n',
    'tl10-import', count=1)

# ---------------- FROZEN_SHA16 placeholder + PRIOR dict ----------------
rep('FROZEN_SHA16 = "e21c7eb83087035c"   # pinned at slice-1 serialization '
    '(W9 precedent)',
    'FROZEN_SHA16 = None   # pinned at slice-1 serialization (W10 '
    'precedent; None = print sha for the pin, refuse nothing)',
    'frozen-sha', count=1)
rep('    "W9": tl9.FROZEN_SHA16,      # 0601dda70b0209fa\n}',
    '    "W9": tl9.FROZEN_SHA16,      # 0601dda70b0209fa\n'
    '    "W10": tl10.FROZEN_SHA16,    # e21c7eb83087035c\n}',
    'prior-dict', count=1)

# ---------------- extract frozen STD anchor values from probe facts ----
pf = json.load(open('results/_r237bmc_stdq90_w11_probe_facts.json',
                    encoding='utf-8'))
cells = pf['eight_gate_cells']
assert len(cells) == 256, len(cells)
empty = sorted(k for k, v in cells.items() if v <= 0)
nonzero = [v for v in cells.values() if v > 0]
assert (len(empty) == 153 and len(nonzero) == 103
        and min(nonzero) == 1 and max(cells.values()) == 41), \
    (len(empty), len(nonzero), min(nonzero), max(cells.values()))
extreme = pf['extreme_day_states']
assert len(extreme) == 7
c48 = pf['core48_std20_open_rate']


def pyl(v, indent):
    return json.dumps(v, ensure_ascii=False)


# ---------------- build the STD layer block ----------------
L = []
A = L.append
A('# momentum-confirmation axis (W10 frozen face, imported verbatim from')
A('# tl10 -- import-face law; the W11 runner re-derives ZERO mom')
A('# machinery)')
A('AXIS_MOM = tl10.AXIS_MOM                 # ["none","mom_oversold"]')
A('MOM_MEMBER = tl10.MOM_MEMBER              # "510300"')
A('MOM_ANCHOR = tl10.MOM_ANCHOR             # W10 frozen probe anchors')
A('mom_state_series = tl10.mom_state_series')
A('mom_zero_mask = tl10.mom_zero_mask')
A('_mom_state_full = tl10._mom_state_full')
A('_mom_structure_pass = tl10._mom_structure_pass')
A('_mom_series_raw = tl10._mom_series_raw')
A('# MOM_SPEC/MOM_ANCHOR carried from tl10.build_grammar_w10() inside')
A('# build_grammar_w11 (import-time grammar-chain build is heavy; lazy')
A('# face = build-time read)')
A('')
A('# dispersion-confirmation axis (prereg sec.3 NEW W11 frozen layer)')
A('AXIS_STD = ["none", "std20_hi", "std10_hi"]')
A('AXIS_COMBOS = tl10.AXIS_COMBOS * len(AXIS_STD)  # 10,450,944 * 3 = '
  '31,352,832')
A('STD_MEMBER = "510300"          # core48 member (prereg sec.2 probe fact)')
A('PROBE_FACTS_FILE = os.path.join("results",')
A('                                "_r237bmc_stdq90_w11_probe_facts.json")')
A('STD_SPEC = {')
A('    "member": STD_MEMBER,')
A('    "series": "r237 probe verbatim / A158-TSGATE-P1 frozen STD "')
A('              "construction (zero-invention law; STD20_q90 = "')
A('              "close.rolling(20, min_periods=1).std(ddof=1)/close "')
A('              "A158 L240 verbatim, price-LEVEL std incl. drift, "')
A('              "distinct from the W4 return-std by construction): "')
A('              "signal-day-d close info set on the member face",')
A('    "std20": "std20(d) = close.rolling(20, min_periods=1).std(ddof=1)"')
A('             "/close (price-level 20-bar dispersion incl. drift)",')
A('    "q90_ref": "q90_ref = std20.rolling(252, min_periods=120)"')
A('               ".quantile(0.90) (own-trailing 252-observation "')
A('               "upper-decile reference)",')
A('    "std20_hi": "std20 > q90_ref (20-bar price dispersion entering "')
A('                "its own top decile = high-dispersion state; "')
A('                "volatility-clustering folklore (GARCH-family "')
A('                "statistical basis); A158-TSGATE census OOS med_t "')
A('                "+2.06 universe face 1,724 codes + GATE-RECHECK "')
A('                "5/5 five-member = LONG anchor; 5-day window "')
A('                "un-halved in-register (+0.89% t=4.47), "')
A('                "term-structure note honest)",')
A('    "std10_hi": "std10(d) = close.rolling(10, min_periods=1).std('
  'ddof=1)"')
A('                "/close vs q90_ref10 same construction; std10 > "')
A('                "q90_ref10 (10-bar face; std10-vs-std20 mutual open "')
A('                "50.13%/49.12% partial redundancy disclosed -- "')
A('                "same-family two-window axis-value variant, W4 "')
A('                "calm/wild same-family precedent)",')
A('    "none": "no gate (W10 semantic baseline face)",')
A('    "info_set": "signal-day d close; entry fills d+1 open (T+1 causal, "')
A('                "same info set as GATE/VOL/YANG/VCONF/STREAK/TSTATE/"')
A('                "AMP/MOM, zero lookahead)",')
A('    "warmup": "120-bar warmup window gate-closed honest (std20 "')
A('              "single-observation ddof=1 -> NaN at bar 0, valid "')
A('              "from bar 1; q90_ref min_periods 120 -> first "')
A('              "decidable bar-idx == 120, fail-closed asserted; "')
A('              "structure spectrum vs YANG 0 / STREAK 2 / VCONF 19 / "')
A('              "AMP 19 / RSV 59 / MAD60 178 / MOM 139 / VOL 519)",')
A('    "engine_note": "entry-permittance only (effective signal zeroed, "')
A('                   "MSG-0440 E1-mapping primitive; exit logic zero "')
A('                   "change; engine/exit_rules.py zero touch)",')
A('    "nan_artifact_note": "NaN comparisons (std20 > q90_ref) yield "')
A('                         "False NOT decidable (pit-95 batch-95 "')
A('                         "law); the decidable face derives from "')
A('                         "the underlying values notna (q90_ref."')
A('                         "notna() & std20.notna()); the naive "')
A('                         "comparison bool face masquerades warmup "')
A('                         "bars as std_closed -- BANNED at the mask "')
A('                         "level",')
A('    "w4_vol_adjacency_note": "W4 VOL collapse-adjacency main "')
A('                             "disclosure carried verbatim (prereg "')
A('                             "honest-adjacency (a)): 88.92% of "')
A('                             "std20-open days fall inside the W4 "')
A('                             "wild face + 38 std-only days + "')
A('                             "305/1,441 re-split inside wild = the "')
A('                             "wave\'s true question (tail-quantile "')
A('                             "gate inside an already-burned median-"')
A('                             "split conditional space); the wave "')
A('                             "is judged on the criterion lines, "')
A('                             "not pre-judged; D6 max|corr| audit "')
A('                             "column face at intake",')
A('    "drift_face_note": "honest negative finding carried (prereg "')
A('                       "adjacency (b)): std20-open AND calm 18 "')
A('                       "decidable-day forward-20d -2.83% vs "')
A('                       "std-open AND wild +1.90% (Welch t=-4.37) "')
A('                       "-- drift-dominated high-dispersion face = "')
A('                       "dilution risk disclosed pre-run",')
A('    "composition_order": "signal -> filter -> timing -> GATE -> VOL -> "')
A('                         "YANG -> VCONF -> STREAK -> TSTATE -> AMP -> "')
A('                         "MOM -> STD -> initial-stop (a std-blocked "')
A('                         "signal never arms a stop; W10 order "')
A('                         "extended, prereg sec.3 fourteen-tuple order "')
A('                         "R/X/S/T/STOP/GATE/VOL/YANG/VCONF/STREAK/"')
A('                         "TSTATE/AMP/MOM/STD)",')
A('}')
A('STD_ANCHOR = ' + json.dumps({
    'n_bars': 3483, 'first_date': '2012-05-28', 'cutoff': '2026-09-22',
    'first_decidable_bar_idx': 120,
    'decidable_days': pf['std20_decidable_days'],
    'open_days': pf['std20_open_days'],
    'closed_days': pf['std20_decidable_days'] - pf['std20_open_days'],
    'std10_decidable_days': pf['std10_decidable_days'],
    'std10_open_days': pf['std10_open_days'],
    'std20_open_rate_on_decidable': pf['std20_open_rate_on_decidable'],
    'std10_open_rate_on_decidable': pf['std10_open_rate_on_decidable'],
    'rate_caliber_note': ('probe-facts rate = open/rows(3483); runner '
                         'meta rate = open/decidable -- INTS asserted '
                         'exact, rate values carried verbatim as '
                         'recorded (zero-invention law)'),
    'eight_gate_all_decidable_days': pf['eight_gate_all_decidable_days'],
    'eight_gate_256cells_nonzero_count': pf[
        'eight_gate_256_cells_nonzero_count'],
    'eight_gate_256cells_empty_count': pf['eight_gate_256_cells_empty_count'],
    'eight_gate_256cells_min_nonzero': pf['eight_gate_256_cells_min_nonzero'],
    'eight_gate_256cells_max': pf['eight_gate_256_cells_max'],
    'eight_gate_256cells_empty': empty,
    'extreme_days': extreme,
    'streak_anchor_reproduction': {'up_streak_days': 844,
                                    'down_streak_days': 817,
                                    'neither_days': 1820},
    'tstate_anchor_reproduction': {'mad60_gate_true_days': 383,
                                    'rsv60_gate_true_days': 632},
    'amp_anchor_reproduction': {'wide_days': 1718, 'narrow_days': 1746,
                                 'zero_range_rows': 0},
    'core48_std20_open_rate': c48,
    'probe_facts': ('results/_r237bmc_stdq90_w11_probe_facts.json '
                    '(r237 bm-c STD probe; exact per-cell 256-grid '
                    'cross-check face when present; probe-facts face '
                    'not a results face)'),
    'probe_basis': ('cross-tables on the r237 probe basis VERBATIM: '
                    'gate = close > ma200 strict NaN->False both '
                    'sides; vol = vol20 vs med500 NaN->False both '
                    'sides; yang = close > open strict (doji red); '
                    'surge = volume > med20 (min_periods=20, INCL d), '
                    'dry = ~surge; streak = W7 close-over-close '
                    'double; tstate = the tl8 census-verbatim faces; '
                    'amp = the r417 face; std20 = the A158 STD20_q90 '
                    'face above (eight-gate all-decidable window m8 = '
                    'dec_std20 & amp_known & streak-decidable & '
                    'dec_mad & dec_rsv == 3,305 days)'),
    'note': ('STD core anchors (warmup 120 / decidable 3,363 / open '
             '391 / std10 decidable 3,363 / std10 open 399) asserted '
             'EXACT; TSTATE/STREAK/AMP cross faces asserted as '
             'reproduction counts per prereg sec.2; eight-gate 256 '
             'cells asserted 103-non-empty with the exact frozen '
             '153-empty name list (probe range 1-41) + exact per-cell '
             'cross-check vs the git-tracked probe facts file when '
             'present; extreme-day gate states asserted exact (std20 '
             'values at probe 6-decimal rounding, ratios at 3-decimal, '
             'rsv at 4-decimal; 2/7 std20-open incl. 2024-02-28 ratio '
             '1.244 + 2024-09-30 ratio 2.565; std10 3/7 open adds '
             '2024-09-24 + 2025-04-07 + 2024-09-30; 2015-07-27 0.848 / '
             '2016-01-04 0.324 / 2026-01-19 0.614 closed honest); '
             'STREAK/TSTATE/AMP reproduction counts asserted exact '
             '(W7/W8/W9/W10 cross-probe determinism law)'),
}, indent=1))
A('')
A('')
A('def _std_series_raw(prices: dict):')
A('    """r237-probe-verbatim STD series computation (single computation')
A('    site for both window faces + decidable + raw values; A158-TSGATE-P1')
A('    frozen STD20_q90/STD10_q90 construction): std20 = close.rolling(20,')
A('    min_periods=1).std(ddof=1)/close; q90_ref = std20.rolling(252,')
A('    min_periods=120).quantile(0.90); open_perm = std20 > q90_ref')
A('    (comparison NaN->False); decidable derives from the underlying')
A('    values notna (pit-95 batch-95 law).  std10 same construction on the')
A('    10-bar window.  Returns (open20, dec20, meta, std20, q90_ref,')
A('    open10, dec10, std10, q90_ref10); deterministic pure function of')
A('    the (cutoff-truncated) panel."""')
A('    df = prices[STD_MEMBER]')
A('    close = df["close"].astype(float).sort_index()')
A('    std20 = close.rolling(20, min_periods=1).std(ddof=1) / close')
A('    q90_ref = std20.rolling(252, min_periods=120).quantile(0.90)')
A('    dec = q90_ref.notna() & std20.notna()  # underlying notna (pit-95)')
A('    open_perm = (std20 > q90_ref)           # comparison face: NaN->False')
A('    std10 = close.rolling(10, min_periods=1).std(ddof=1) / close')
A('    q90_ref10 = std10.rolling(252, min_periods=120).quantile(0.90)')
A('    dec10 = q90_ref10.notna() & std10.notna()')
A('    open10 = (std10 > q90_ref10)')
A('    n = len(close)')
A('')
A('    def _first_true(s):')
A('        arr = s.fillna(False).astype(bool).values')
A('        nz = np.flatnonzero(arr)')
A('        return int(nz[0]) if len(nz) else None')
A('')
A('    dec_n = int(dec.sum())')
A('    open_n = int((open_perm & dec).sum())')
A('    closed_n = int(((~open_perm) & dec).sum())')
A('    meta = {"n_bars": int(n),')
A('            "warmup_gate_closed_bars": _first_true(dec),')
A('            "first_decidable_bar_idx": _first_true(dec),')
A('            "decidable_days": dec_n,')
A('            "open_days": open_n, "closed_days": closed_n,')
A('            "open_rate_on_decidable":')
A('            (round(float(open_n / dec_n), 4) if dec_n else None),')
A('            "std10_decidable_days": int(dec10.sum()),')
A('            "std10_open_days": int((open10 & dec10).sum()),')
A('            "na_window_bars": 120,   # the gate family\'s warmup')
A('            }')
A('    return open_perm, dec, meta, std20, q90_ref, open10, dec10, \\')
A('        std10, q90_ref10')
A('')
A('')
A('def std_state_series(prices: dict):')
A('    """Frozen STD spec (prereg sec.2/3): member 510300 signal-day info')
A('    set -- std20 open perm + decidable face + the std10 faces.')
A('    Returns (open20, dec20, meta, open10, dec10): boolean Series on')
A('    the member\'s own date index + structural meta + the 10-bar')
A('    faces.  Deterministic pure function of the (cutoff-truncated)')
A('    panel."""')
A('    o20, d20, meta, _s20, _q20, o10, d10, _s10, _q10 = \\')
A('        _std_series_raw(prices)')
A('    return o20, d20, meta, o10, d10')
A('')
A('')
A('def _std_face_full():')
A('    """Frozen sec.2 STD-series face (r237 probe basis): the git-tracked')
A('    raw full-history member file data/daily/sh510300.csv (open + high +')
A('    low + close + volume columns), truncated at the evidence cutoff.')
A('    (tl8._tstate_face_full loading caliber reused verbatim -- same')
A('    member, same columns, same cutoff law; import-face law.)"""')
A('    return tl8._tstate_face_full()')
A('')
A('')
A('def _std_state_full():')
A('    """Canonical full-face std_state with the frozen probe anchors')
A('    asserted (prereg sec.2 G-STD fail-closed): n_bars == 3,483;')
A('    first-decidable == 120 / decidable == 3,363 / open == 391 /')
A('    closed == 2,972 / std10 decidable == 3,363 / std10 open == 399')
A('    exact; cross reproduction counts {streak up 844/down 817/neither')
A('    1820, mad60 383, rsv60 632, wide 1718/narrow 1746/zero-range 0};')
A('    eight-gate (gate x vol x yang x vconf x streak x tstate x amp x')
A('    std20) 256 open-window cells 103-non-empty with the exact frozen')
A('    153-empty name list (probe range 1-41; all-decidable 3,305) +')
A('    exact per-cell cross-check vs the git-tracked probe facts file')
A('    when present; extreme-day gate states exact (std20 values at')
A('    probe 6-decimal rounding, ratios at 3-decimal, rsv at 4-decimal;')
A('    2/7 std20-open incl. 2024-02-28 + 2024-09-30; std10 3/7 open')
A('    adds 2024-09-24 + 2025-04-07 + 2024-09-30).  Returns')
A('    (std_state, err); err is a one-line honest refusal reason when')
A('    not None."""')
A('    face = _std_face_full()')
A('    if face is None:')
A('        return None, (f"raw member face data/daily/sh{STD_MEMBER}.csv "')
A('                      f"absent/open-high-low-close-volume columns "')
A('                      f"missing or truncated tail != cutoff {CUTOFF}")')
A('    open20, dec, meta, std20, q90_ref, open10, dec10, std10, \\')
A('        q90_ref10 = _std_series_raw(face)')
A('    a = STD_ANCHOR')
A('    if (meta.get("n_bars") != a["n_bars"]')
A('            or meta["first_decidable_bar_idx"]')
A('            != a["first_decidable_bar_idx"]')
A('            or meta["decidable_days"] != a["decidable_days"]')
A('            or meta["open_days"] != a["open_days"]')
A('            or meta["closed_days"] != a["closed_days"]')
A('            or meta["std10_decidable_days"]')
A('            != a["std10_decidable_days"]')
A('            or meta["std10_open_days"] != a["std10_open_days"]):')
A('        return None, (f"G-STD core anchors {meta} != probe "')
A('                      f"{{n 3483, warmup 120, decidable 3363, open "')
A('                      f"391, closed 2972, std10 dec 3363 open 399}}")')
A('    # ---- r237 probe basis faces VERBATIM (cross + eight-gate grid)')
A('    df = face[STD_MEMBER]')
A('    close = df["close"].astype(float).sort_index()')
A('    o_ = df["open"].astype(float).reindex(close.index)')
A('    h_ = df["high"].astype(float).reindex(close.index)')
A('    l_ = df["low"].astype(float).reindex(close.index)')
A('    v_ = df["volume"].astype(float).reindex(close.index)')
A('    amp = (h_ - l_) / close')
A('    med20amp = amp.rolling(20, min_periods=20).median()')
A('    amp_known = med20amp.notna()')
A('    wide_face = (amp > med20amp) & amp_known')
A('    up1 = close > close.shift(1)')
A('    up2 = close.shift(1) > close.shift(2)')
A('    dn1 = close < close.shift(1)')
A('    dn2 = close.shift(1) < close.shift(2)')
A('    judge = close.shift(2).notna()      # bars 0-1 warmup gate-closed')
A('    up_st = judge & (up1 & up2).fillna(False)')
A('    dn_st = judge & (dn1 & dn2).fillna(False)')
A('    neither_st = judge & ~((up1 & up2).fillna(False)')
A('                           | (dn1 & dn2).fillna(False))')
A('    ma60 = close.rolling(60).mean()')
A('    dist = close / ma60 - 1.0')
A('    ts_q10 = dist.rolling(252, min_periods=120).quantile(0.10)')
A('    mad_q10 = dist < ts_q10')
A('    dec_mad = ts_q10.notna()')
A('    hh60 = h_.rolling(60).max()')
A('    ll60 = l_.rolling(60).min()')
A('    rng60 = (hh60 - ll60).replace(0, np.nan)')
A('    rsv60 = (close - ll60) / rng60')
A('    rsv_low = rsv60 < 0.2')
A('    dec_rsv = rsv60.notna()')
A('    # reproduction counts (W7/W8/W9/W10 cross-probe determinism law)')
A('    sar = a["streak_anchor_reproduction"]')
A('    if (int(up_st.sum()) != sar["up_streak_days"]')
A('            or int(dn_st.sum()) != sar["down_streak_days"]')
A('            or int(neither_st.sum()) != sar["neither_days"]):')
A('        return None, (f"G-STD streak-anchor reproduction broken "')
A('                      f"up {int(up_st.sum())}/down {int(dn_st.sum())}/"')
A('                      f"neither {int(neither_st.sum())} != {sar}")')
A('    tar = a["tstate_anchor_reproduction"]')
A('    if (int((mad_q10 & dec_mad).sum()) != tar["mad60_gate_true_days"]')
A('            or int((rsv_low & dec_rsv).sum())')
A('            != tar["rsv60_gate_true_days"]):')
A('        return None, (f"G-STD tstate-anchor reproduction broken "')
A('                      f"mad60 {int((mad_q10 & dec_mad).sum())}/"')
A('                      f"rsv60 {int((rsv_low & dec_rsv).sum())} != "')
A('                      f"{tar}")')
A('    aar = a["amp_anchor_reproduction"]')
A('    if (int(wide_face.sum()) != aar["wide_days"]')
A('            or int((amp_known & ~wide_face).sum()) != aar["narrow_days"]')
A('            or int((h_ == l_).sum()) != aar["zero_range_rows"]):')
A('        return None, (f"G-STD amp-anchor reproduction broken "')
A('                      f"wide {int(wide_face.sum())}/narrow "')
A('                      f"{int((amp_known & ~wide_face).sum())}/"')
A('                      f"zero-range {int((h_ == l_).sum())} != {aar}")')
A('    # eight-gate 256-cell cross on the r237 probe basis VERBATIM')
A('    # (all-decidable window m8 = dec_std20 & amp_known & streak-')
A('    # decidable & dec_mad & dec_rsv == 3,305 days; gate/vol/yang/')
A('    # vconf faces are NaN->False comparison faces, notna() always True)')
A('    ma200 = close.rolling(200).mean()')
A('    bull = close > ma200')
A('    bear = ~bull')
A('    ret = close.pct_change()')
A('    vol20 = ret.rolling(20, min_periods=20).std(ddof=1)')
A('    med500 = vol20.rolling(500, min_periods=500).median()')
A('    calm = vol20 <= med500')
A('    wild = vol20 > med500')
A('    med20v = v_.rolling(20, min_periods=20).median()')
A('    surge = v_ > med20v')
A('    yang = close > o_')
A('    red = ~yang')
A('    narrow_face = (amp <= med20amp) & amp_known')
A('    std_open_face = open20 & dec')
A('    std_closed_face = (~open20) & dec')
A('    m8 = dec & amp_known & judge & dec_mad & dec_rsv')
A('    cells = {}')
A('    for bname, b in (("bull", bull), ("bear", bear)):')
A('        for vname, vv in (("calm", calm), ("wild", wild)):')
A('            for yname, y in (("yang", yang), ("red", red)):')
A('                for sname, s in (("surge", surge), ("dry", ~surge)):')
A('                    for kname, k in (("up_streak", up_st),')
A('                                     ("down_streak", dn_st)):')
A('                        for tname, t in (("mad60", mad_q10),')
A('                                         ("rsv60", rsv_low)):')
A('                            for aname, aa in (("wide", wide_face),')
A('                                              ("narrow", narrow_face)):')
A('                                for mname, mm in (')
A('                                        ("std20_open", std_open_face),')
A('                                        ("std20_closed", std_closed_face)):')
A('                                    cells[f"{bname}|{vname}|{yname}|"')
A('                                          f"{sname}|{kname}|{tname}|"')
A('                                          f"{aname}|{mname}"] = \\')
A('                                          int((m8 & b & vv & y & s & k')
A('                                             & t & aa & mm).sum())')
A('    empty = sorted(k for k, n_ in cells.items() if n_ <= 0)')
A('    nonzero = [x for x in cells.values() if x > 0]')
A('    if (len(cells) != 256')
A('            or len(nonzero)')
A('            != a["eight_gate_256cells_nonzero_count"]')
A('            or len(empty) != a["eight_gate_256cells_empty_count"]')
A('            or empty != sorted(a["eight_gate_256cells_empty"])')
A('            or min(nonzero) < a["eight_gate_256cells_min_nonzero"]')
A('            or max(cells.values()) > a["eight_gate_256cells_max"]')
A('            or int(m8.sum())')
A('            != a["eight_gate_all_decidable_days"]):')
A('        return None, (f"G-STD eight-gate 256-cell cross drift "')
A('                      f"(nonzero {len(nonzero)}/103, empty "')
A('                      f"{len(empty)}/153, min {min(nonzero)}, max "')
A('                      f"{max(cells.values())}, all-decidable "')
A('                      f"{int(m8.sum())}/3305)")')
A('    # exact per-cell cross-check vs the git-tracked probe facts file')
A('    # (r237 determinism cross-check law; skip-face = file absent,')
A('    # header counts above still binding)')
A('    if os.path.exists(PROBE_FACTS_FILE):')
A('        pf_ = json.load(open(PROBE_FACTS_FILE, encoding="utf-8"))')
A('        pcells = pf_.get("eight_gate_cells", {})')
A('        drift = [f"{k}: {cells.get(k)} != {v_}"')
A('                 for k, v_ in pcells.items() if cells.get(k) != v_]')
A('        if pcells and drift:')
A('            return None, (f"G-STD probe-facts per-cell cross-check "')
A('                          f"drift: {drift[:3]}")')
A('    # extreme-day gate states (frozen face; std20 values at probe')
A('    # 6-decimal rounding + ratios at 3-decimal + rsv at 4-decimal,')
A('    # tolerance 5.001e-6 on values)')
A('    for dstr, want in a["extreme_days"].items():')
A('        ts = pd.Timestamp(dstr)')
A('        if ts not in close.index:')
A('            return None, f"G-STD extreme day {dstr} absent from face"')
A('        rv20 = std20.loc[ts]')
A('        if pd.isna(rv20):')
A('            return None, f"G-STD extreme day {dstr} std20 NaN"')
A('        got_open = bool(open20.loc[ts]) if bool(dec.loc[ts]) else None')
A('        got_open10 = (bool(open10.loc[ts]) if bool(dec10.loc[ts])')
A('                      else None)')
A('        got_val = round(float(rv20), 6)')
A('        qr = q90_ref.loc[ts]')
A('        got_ratio = (None if pd.isna(qr) or qr == 0')
A('                     else round(float(rv20 / qr), 3))')
A('        got_streak = ("up_streak2" if bool(up_st.loc[ts])')
A('                      else "down_streak2" if bool(dn_st.loc[ts])')
A('                      else "neither")')
A('        rsv_v = rsv60.loc[ts]')
A('        rsv_v = (None if pd.isna(rsv_v) else round(float(rsv_v), 4))')
A('        got_amp = ("wide" if bool(wide_face.loc[ts]) else "narrow")')
A('        if (got_open != want["std20_open"]')
A('                or got_open10 != want["std10_open"]')
A('                or abs(got_val - want["std20_value"]) > 5.01e-6')
A('                or got_streak != want["streak"]')
A('                or bool(mad_q10.loc[ts]) != want["tstate_mad60_q10"]')
A('                or bool(rsv_low.loc[ts]) != want["tstate_rsv60_low"]')
A('                or rsv_v is None')
A('                or abs(rsv_v - want["rsv60_value"]) > 5.001e-5')
A('                or got_amp != want["amp_state"]')
A('                or got_ratio is None')
A('                or abs(got_ratio - want["std20_over_q90ref"]) > 5.01e-4):')
A('            return None, (f"G-STD extreme day {dstr} drift: open "')
A('                          f"{got_open}/{want[\'std20_open\']}, open10 "')
A('                          f"{got_open10}/{want[\'std10_open\']}, std20 "')
A('                          f"{got_val}/{want[\'std20_value\']}, ratio "')
A('                          f"{got_ratio}/{want[\'std20_over_q90ref\']}, "')
A('                          f"streak {got_streak}/{want[\'streak\']}, "')
A('                          f"mad {bool(mad_q10.loc[ts])}/"')
A('                          f"{want[\'tstate_mad60_q10\']}, rsv "')
A('                          f"{bool(rsv_low.loc[ts])}/"')
A('                          f"{want[\'tstate_rsv60_low\']}, amp "')
A('                          f"{got_amp}/{want[\'amp_state\']}")')
A('    meta = dict(meta)')
A('    meta["eight_gate_256cells"] = cells')
A('    meta["eight_gate_256cells_empty"] = empty')
A('    meta["eight_gate_all_decidable_days"] = int(m8.sum())')
A('    meta["streak_anchor"] = {k: sar[k] for k in')
A('                             ("up_streak_days", "down_streak_days",')
A('                              "neither_days")}')
A('    meta["tstate_anchor"] = dict(tar)')
A('    meta["amp_anchor"] = dict(aar)')
A('    return (open20, dec, meta, open10, dec10), None')
A('')
A('')
A('def std_zero_mask(mask: pd.DataFrame, std_key: str, std_state):')
A('    """Grammar-layer std entry gate (prereg sec.3 dispersion-')
A('    confirmation face; E1-mapping primitive): off-face signal days ->')
A('    effective signal zeroed (entry blocked; engine-native signal-off')
A('    exit semantics -- the same primitive every cell uses when its')
A('    own signal turns off; zero engine touch).  std=none = W10')
A('    semantic baseline (identity).  The keep face derives from the')
A('    DECIDABLE face (pit-95 law): std20_hi keeps std20-open AND')
A('    decidable; std10_hi keeps std10-open AND decidable -- the naive')
A('    comparison bool face alone would masquerade warmup bars as')
A('    std_closed (BANNED).  Member dates missing from the mask index')
A('    -> std-closed (conservative reindex law,')
A('    tl3/tl4/tl5/tl6/tl7/tl8/tl9/tl10 gate caliber)."""')
A('    if std_key == "none":')
A('        return mask')
A('    open20, dec20, _meta, open10, dec10 = std_state')
A('    if std_key == "std20_hi":')
A('        keep = (open20.reindex(mask.index).fillna(False).astype(int)')
A('                & dec20.reindex(mask.index).fillna(False).astype(int))')
A('    elif std_key == "std10_hi":')
A('        keep = (open10.reindex(mask.index).fillna(False).astype(int)')
A('                & dec10.reindex(mask.index).fillna(False).astype(int))')
A('    else:')
A('        raise ValueError(f"unknown std_key {std_key}")')
A('    return mask.mul(keep, axis=0)')
A('')
A('')
A('def _std_structure_pass(std_meta) -> bool:')
A('    """Series-structure invariants on every panel face (fail-closed):')
A('    120-bar warmup -- first-decidable + decidable partitions n_bars;')
A('    open <= decidable and closed <= decidable.  A face shorter than')
A('    the warmup (first-decidable None) honestly refuses."""')
A('    if not isinstance(std_meta, dict):')
A('        return False')
A('    n = std_meta.get("n_bars", -1)')
A('    fv = std_meta.get("first_decidable_bar_idx")')
A('    return (fv is not None')
A('            and fv + std_meta.get("decidable_days", -10**9) == n')
A('            and std_meta.get("open_days", -1)')
A('            <= std_meta.get("decidable_days", -1)')
A('            and std_meta.get("closed_days", -1)')
A('            <= std_meta.get("decidable_days", -1))')
NEW_LAYER = '\n'.join(L)

# ---------------- replace the MOM layer block ----------------
start_anchor = '# momentum-confirmation axis (prereg sec.3 NEW W10 frozen layer)\n'
i0 = SRC.find(start_anchor)
assert i0 >= 0, 'mom layer start not found'
end_anchor = ('# ------------------------------------------------------------ '
              'grammar build')
i1 = SRC.find(end_anchor, i0)
assert i1 >= 0, 'grammar build marker not found'
SRC = SRC[:i0] + NEW_LAYER + '\n\n' + SRC[i1:]

# ---------------- replace build_grammar body ----------------
g0 = SRC.find('def build_grammar_w11():')
assert g0 >= 0
g1 = SRC.find('# ------------------------------------------------------------ '
              'Sobol draw leg')
assert g1 > g0
NEW_GRAMMAR = '''def build_grammar_w11():
    """tl10 grammar extended with the NEW std axis + W11 seeds/counts
    (frozen face).  FOURTEEN-tuple axes R/X/S/T/STOP/GATE/VOL/YANG/
    VCONF/STREAK/TSTATE/AMP/MOM/STD = 31,352,832 axis combos.

    Exclusion law (prereg sec.1): exact already-judged cells are
    excluded on the std=none face only; all prior-wave lineage keys
    are std=none completed (W1 4-tuple + stop/gate/vol/yang/vconf/
    streak/tstate/amp/mom/std none; W2 5-tuple + gate/vol/yang/vconf/
    streak/tstate/amp/mom/std none; W3 6-tuple + vol/yang/vconf/
    streak/tstate/amp/mom/std none; W4 7-tuple + yang/vconf/streak/
    tstate/amp/mom/std none; W5 8-tuple + vconf/streak/tstate/amp/
    mom/std none; W6 9-tuple + streak/tstate/amp/mom/std none; W7
    10-tuple + tstate/amp/mom/std none; W8 11-tuple + amp/mom/std
    none; W9 12-tuple + mom/std none; W10 13-tuple + std none; MASS
    via the declared translation); std in {std20_hi, std10_hi}
    faces = new-syntax legal cells (never excluded)."""
    g10 = tl10.build_grammar_w10()      # frozen W10 machinery face
    excl = []
    for e in g10["exclusion"]["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_none_face"]:
        excl.append({**e, "axis": list(e["axis"]) + ["none"],
                     "face": "stop-gate-vol-yang-vconf-streak-"
                             "tstate-amp-mom-std-none"})
    grammar = {
        "wave": WAVE, "prereg": PREREG, "evidence_cutoff": CUTOFF,
        "grammar_kind": "w11-std-gate-extended",
        "seeds": {"trial_labor_w11_gen": SEED_GEN,
                  "trial_labor_w11_scrnull": SEED_NULL,
                  "trial_labor_w11_unc": SEED_UNC,
                  "derivation": "Sobol(seed=20317000+family_idx, "
                                "scramble) param box + default_rng("
                                "[20317000+family_idx, 7919]) FOURTEEN-"
                                "tuple axis stream R/X/S/T/STOP/GATE/"
                                "VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/"
                                "STD (prereg s.3; A idx 0-5, B idx "
                                "6+slot; berth re-take 20317000/"
                                "20317500/20318000 per the draft "
                                "clause-5 collision clause (20316000/"
                                "20316500 collided with bm-a r445 "
                                "A12-PREDCOND), W9 two-collision "
                                "precedent; berths held at the freeze "
                                "commit per R250 one-step law, bm-b "
                                "r441 three-step re-verify ALL GREEN "
                                "no re-pick)"},
        "n_draws": {"A": N_A, "B": N_B}, "k_nulls": K_NULLS,
        "axes": {**g10["axes"], "std": AXIS_STD},
        "axis_combos": AXIS_COMBOS,
        "stop_formula": g10["stop_formula"],
        "stop_fill_mapping": g10["stop_fill_mapping"],
        "gate_spec": g10["gate_spec"],
        "vol_spec": g10["vol_spec"],
        "yang_spec": g10["yang_spec"],
        "vconf_spec": g10["vconf_spec"],
        "streak_spec": g10["streak_spec"],
        "tstate_spec": g10["tstate_spec"],
        "amp_spec": g10["amp_spec"],
        "mom_spec": g10["mom_spec"],
        "std_spec": STD_SPEC,
        "vol_anchor": g10["vol_anchor"],
        "yang_anchor": g10["yang_anchor"],
        "vconf_anchor": g10["vconf_anchor"],
        "streak_anchor": g10["streak_anchor"],
        "tstate_anchor": g10["tstate_anchor"],
        "amp_anchor": g10["amp_anchor"],
        "mom_anchor": g10["mom_anchor"],
        "std_anchor": STD_ANCHOR,
        "families": g10["families"], "value_domains": g10["value_domains"],
        "faces": g10["faces"],
        "exclusion": {
            "stop_gate_vol_yang_vconf_streak_tstate_amp_mom_std_none_face":
                excl,
            "sources": list(g10["exclusion"]["sources"])
            + ["w10_screen.json survivors (generate-time)",
               "w10_judge products (generate-time real-read "
               "re-declare window; W10-JUDGE landed 2026-09-29 "
               "20:31:29)"],
            "note": "exclusion face = std=none only; prior-wave keys "
                    "std=none-completed (semantic identity match); "
                    "std in {std20_hi, std10_hi} = new-syntax legal "
                    "cells (prereg sec.1)"},
        "negative_priors": g10.get("negative_priors"),
        "inventory_audit": g10["inventory_audit"],
    }
    grammar["grammar_sha256"] = _grammar_sha16(grammar)
    return grammar


'''
SRC = SRC[:g0] + NEW_GRAMMAR + SRC[g1:]

# ---------------- replace draw function ----------------
d0 = SRC.find('def draw_candidate_sobol_w11(')
assert d0 >= 0
d1 = SRC.find('# ------------------------------------------------ exclusion')
assert d1 > d0
NEW_DRAW = '''def draw_candidate_sobol_w11(grammar, family, slot, n_draws):
    """Yield (draw_idx, cand) for one family slot per prereg sec.3:
    Sobol over the normalized param box (seed=SEED_GEN+family_idx) mapped
    to discrete domain indices + FOURTEEN-tuple axis stream
    default_rng([SEED_GEN+family_idx, 7919]) in the frozen consumption
    order R/X/S/T/STOP/GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD (the
    first thirteen axis arrays are the W10-order stream VERBATIM --
    order-frozen consumption law; the std leg appends AFTER mom,
    zero disturbance).  Deterministic, zero band use."""
    from scipy.stats import qmc
    fam_idx = slot if family == "A" else 6 + slot   # A 0-5, B 6+ (prereg)
    spec = grammar["families"][family][slot]
    mk = f"{spec['module']}.{spec['fn']}"
    dom = grammar["value_domains"][mk]
    names = sorted(nm for nm, vs in dom.items() if len(vs) > 1)
    sob = qmc.Sobol(max(1, len(names)), scramble=True,
                    seed=SEED_GEN + fam_idx)
    box = sob.random(n_draws)
    rng = np.random.default_rng([SEED_GEN + fam_idx, 7919])
    ax = list(zip(rng.integers(0, len(tl1.AXIS_FILTERS), n_draws),
                  rng.integers(0, len(tl1.AXIS_EXITS), n_draws),
                  rng.integers(0, len(tl1.AXIS_SIZING), n_draws),
                  rng.integers(0, len(tl1.AXIS_TIMING), n_draws),
                  rng.integers(0, len(tl2.AXIS_STOP), n_draws),
                  rng.integers(0, len(tl3.AXIS_GATE), n_draws),
                  rng.integers(0, len(tl4.AXIS_VOL), n_draws),
                  rng.integers(0, len(tl5.AXIS_YANG), n_draws),
                  rng.integers(0, len(tl6.AXIS_VCONF), n_draws),
                  rng.integers(0, len(tl7.AXIS_STREAK), n_draws),
                  rng.integers(0, len(tl8.AXIS_TSTATE), n_draws),
                  rng.integers(0, len(tl9.AXIS_AMP), n_draws),
                  rng.integers(0, len(AXIS_MOM), n_draws),
                  rng.integers(0, len(AXIS_STD), n_draws)))
    for i in range(n_draws):
        params = {}
        j = 0
        for nm in sorted(dom):
            values = dom[nm]
            if len(values) <= 1:
                params[nm] = values[0] if values else None
                continue
            params[nm] = values[min(int(box[i, j] * len(values)),
                                    len(values) - 1)]
            j += 1
        r_, x_, s_, t_, st_, gt_, vt_, yg_, vc_, sk_, ts_, ap_, mo_, sd_ \\
            = ax[i]
        yield i, {"module": spec["module"], "fn": spec["fn"],
                  "sig_params": params,
                  "axis": [tl1.AXIS_FILTERS[r_], tl1.AXIS_EXITS[x_],
                           tl1.AXIS_SIZING[s_], tl1.AXIS_TIMING[t_],
                           tl2.AXIS_STOP[st_], tl3.AXIS_GATE[gt_],
                           tl4.AXIS_VOL[vt_], tl5.AXIS_YANG[yg_],
                           tl6.AXIS_VCONF[vc_], tl7.AXIS_STREAK[sk_],
                           tl8.AXIS_TSTATE[ts_], tl9.AXIS_AMP[ap_],
                           AXIS_MOM[mo_], AXIS_STD[sd_]],
                  "family": family}


'''
SRC = SRC[:d0] + NEW_DRAW + SRC[d1:]

open('results/_r442bmb_stage2.py', 'w', encoding='utf-8').write(SRC)
print('stage2 written, lines:', SRC.count(chr(10)) + 1)
print('fails:', len(fails))
for f in fails:
    print(' FAIL', f)
