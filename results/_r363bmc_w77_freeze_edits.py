# -*- coding: utf-8 -*-
"""r363 bm-c W77 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening (r561/r566/r568/r570/r571 lineage).

FIX-A (origin-blob freshness): every tracked edit target must show zero
  deleted lines vs origin/main BEFORE any edit runs (r559 stale-base cure).
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W76, bm-b's);
  after every edit each registered row signature must survive exactly
  (count unchanged) with exactly one new W77 signature added.
FIX-C (pure-insertion delta): post-edit, `git diff origin/main --numstat`
  must show ZERO deleted lines for each edited file.

W77 = SIXTY-SIXTH engine wave, bm-c's TWENTY-FOURTH owned per
machine-derive (engine_owner==bm-c rows 23 + candidate). r565
yield-then-reoccupy: this machine's W76 draft (gate ADMIT
results/_r363bmc_w76_band_gate.py, bands A 195_004..197_003 /
B 52_401..52_600, seat MSG-20261002-1145-bmc LOCAL-ONLY never pushed =
invisible to peers, visibility failure disclosed) was yielded to bm-b
r572 (24ec53190 first-land per r511 commit-order; registered bands
BITWISE == this machine's gate-derived candidates = r530 family 11th
deterministic cross-validation; the local engine had self-ignited on the
pre-registration working-tree rows per r359 law and burned 12/12 twin
shards -- audit.machine=bm-c verified, discarded; finalize never ran,
ledger untouched = zero science pollution). W77 = re-occupation in the
yield-receipt window (seat published=reserved MSG-20261002-1150-bmc).

Bands = BOTH SIDES ARITHMETIC CONTINUATION from the registered W76 tail,
zero skip (r535 law): A 197_004..199_003 (== W76 A end 197_003 + 1) /
B 52_601..52_800 (== W76 B end 52_600 + 1); single reading, no fork face
(== the W76 row W77+ WARNING projection verbatim). TWO in-flight upstream
seats at this freeze: W75 bm-a (12/12 burned, finalize pending) + W76 bm-b
(registered, burn pending) -- finalize chain-pending FAIL-CLOSED r307.
W1..W74 finalizes ALL LANDED (net head 527,348, K=160,720 -- bm-b r572).
ADMIT receipt results/_r363bmc_w77_band_gate.py.
"""
import subprocess, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREAT = 0x08000000  # CREATE_NO_WINDOW (session-host flash guard)

def git(*a):
    r = subprocess.run(['git', '-C', REPO] + list(a), capture_output=True,
                       creationflags=CREAT)
    if r.returncode != 0:
        sys.exit('GIT FAIL %s -> %s' % (a[:3], r.stderr.decode('utf-8', 'replace')))
    return r.stdout

def load(fp):
    b = open(fp, 'rb').read()
    t = b.decode('utf-8')
    eol = '\r\n' if t.count('\r\n') * 2 > t.count('\n') else '\n'
    return t, eol

def save(fp, t):
    open(fp, 'wb').write(t.encode('utf-8'))

def rep(t, old, new, eol, tag):
    oldX = old.replace('\n', eol)
    newX = new.replace('\n', eol)
    assert t.count(oldX) == 1, f"{tag}: anchor not unique ({t.count(oldX)})"
    return t.replace(oldX, newX)

# ---------------- FIX-A: origin-blob freshness (pre-edit) --------------------
git('fetch', 'origin')
TARGETS = [
    'scripts/perpetual_faces.py',
    'scripts/perpetual_faces_n1.py',
    'research/PERPETUAL_FACES.md',
]
for p in TARGETS:
    r = subprocess.run(['git', '-C', REPO, 'diff', 'origin/main', '--numstat', '--', p],
                       capture_output=True, creationflags=CREAT)
    out = r.stdout.decode('utf-8', 'replace').strip()
    if r.returncode != 0:
        sys.exit(f'FIX-A git fail on {p}')
    for line in out.splitlines():
        add, dele, path = line.split('\t')
        if int(dele) > 0:
            sys.exit(f'STALE BASE (FIX-A abort): {p} shows {dele} deleted lines vs '
                     f'origin/main -- checkout origin version first (r559 clobber cure)')
print('FIX-A: all 3 tracked edit targets show zero deletions vs origin/main (fresh base)')

# ---------------- survival signature baseline (FIX-B) ------------------------
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 77))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in
       range(58, 77)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 77)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[77] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '77: {"a": (197_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    76: {"a": (195_004, 197_003), "b_exit": (52_401, 52_600),\n'
          '         "engine_owner": "bm-b"},\n')
    NEW = ('    76: {"a": (195_004, 197_003), "b_exit": (52_401, 52_600),\n'
           '         "engine_owner": "bm-b"},\n'
           '    # SIXTY-SIXTH ENGINE-OWNED WAVE (r363 bm-c freeze): bm-c\'s\n'
           '    # twenty-fourth owned per machine-derive (engine_owner==bm-c\n'
           '    # rows 23 + candidate). Wave 77 = first free number after the\n'
           '    # registered W76 row (r511 tail-lock, fetch-checked vacancy).\n'
           '    # r565 yield-then-reoccupy: this machine drafted W76 first\n'
           '    # (gate ADMIT results/_r363bmc_w76_band_gate.py, bands\n'
           '    # A 195_004..197_003 / B 52_401..52_600, seat\n'
           '    # MSG-20261002-1145-bmc LOCAL-ONLY never pushed = invisible\n'
           '    # to peers -- visibility failure disclosed) and yielded to\n'
           '    # bm-b r572 (24ec53190 first-land per r511 commit-order;\n'
           '    # registered bands BITWISE == the gate-derived candidates =\n'
           '    # r530 family 11th cross-validation; engine self-ignited on\n'
           '    # the pre-registration tree rows per r359 law, 12/12 twin\n'
           '    # shards audit.machine=bm-c verified and discarded, finalize\n'
           '    # never ran, ledger untouched = zero science pollution);\n'
           '    # W77 = re-occupation in the yield-receipt window (seat\n'
           '    # published=reserved MSG-20261002-1150-bmc).\n'
           '    # Bands = BOTH SIDES ARITHMETIC CONTINUATION from the\n'
           '    # registered W76 tail, zero skip (r535 law):\n'
           '    # A 197_004..199_003 == W76 A end 197_003 + 1 /\n'
           '    # B 52_601..52_800 == W76 B end 52_600 + 1; single reading,\n'
           '    # no fork face (F-20261002-03 not triggered).\n'
           '    # W1..W74 finalizes ALL LANDED (net head 527,348,\n'
           '    # K=160,720 -- W74 bm-b r572); W75 bm-a (12/12 burned,\n'
           '    # finalize pending) + W76 bm-b (registered, burn pending) =\n'
           '    # TWO in-flight upstream seats at this freeze (finalize\n'
           '    # chain-pending FAIL-CLOSED r307).\n'
           '    # ADMIT receipt results/_r363bmc_w77_band_gate.py;\n'
           '    # NOT a re-pick (R250: W77 bands were never assigned).\n'
           '    77: {"a": (197_004, 199_003), "b_exit": (52_601, 52_800),\n'
           '         "engine_owner": "bm-c"},\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[77] landed (anchor=W76 row, insert after)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[77] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '77: {"batch": "PERPETUAL-N1-W77"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w76", "out_name": "n1_w76_results.json",\n'
          '                            "engine_owner": "bm-b"},\n')
    NEW2 = A2 + (
        '                       77: {"batch": "PERPETUAL-N1-W77",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W77_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; SIXTY-SIXTH ENGINE-OWNED WAVE, "\n'
        '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
        '                                       "(first-free-number law over the registered W76 row; "\n'
        '                                       "r565 yield-then-reoccupy: this machine\'s W76 draft "\n'
        '                                       "yielded to bm-b r572 24ec53190 first-land per r511 "\n'
        '                                       "commit-order -- seat MSG-20261002-1145-bmc was "\n'
        '                                       "LOCAL-ONLY never pushed = invisible to peers, "\n'
        '                                       "visibility failure disclosed; registered bands "\n'
        '                                       "bitwise == this machine\'s gate-derived candidates "\n'
        '                                       "= r530 family 11th cross-validation; the local "\n'
        '                                       "engine self-ignited on pre-registration tree rows "\n'
        '                                       "per r359 law, 12/12 twin shards audit-verified "\n'
        '                                       "and discarded, finalize never ran, ledger "\n'
        '                                       "untouched = zero science pollution; seat published="\n'
        '                                       "reserved MSG-20261002-1150-bmc; bands = BOTH SIDES "\n'
        '                                       "ARITHMETIC CONTINUATION from the registered W76 "\n'
        '                                       "tail zero skip per r535 law, single reading, no "\n'
        '                                       "fork face, F-20261002-03 not triggered; TWO "\n'
        '                                       "in-flight upstream seats W75 bm-a finalize-pending "\n'
        '                                       "+ W76 bm-b burn-pending -- FAIL-CLOSED r307), "\n'
        '                                       "engine_owner=bm-c; W1..W74 finalizes ALL LANDED at "\n'
        '                                       "this freeze (net chain head 527,348, K=160,720, "\n'
        '                                       "bm-b r572)"),\n'
        '                            "a_seed_base": 197_004,        # law sec.4 W77 A: 197_004..199_003 (arithmetic continuation)\n'
        '                            "b_exit_seed_base": 52_601,   # law sec.4 W77 B: 52_601..52_800 (arithmetic continuation)\n'
        '                            "shard_subdir": "n1_w77", "out_name": "n1_w77_results.json",\n'
        '                            "engine_owner": "bm-c"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[77] landed (anchor=W76 entry tail, insert after)')

# ---------------- edit 3: perpetual_faces_n1.py selftest W77 leg --------------
LEG77 = '''
    # --- W77 materializer face (r363 bm-c freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-c's
    #     twenty-fourth owned per machine-derive (engine_owner==bm-c
    #     rows 23 + candidate); wave 77 = first free number after the
    #     registered W76 row. r565 yield-then-reoccupy: this machine
    #     drafted W76 first (gate ADMIT _r363bmc_w76_band_gate.py, seat
    #     MSG-20261002-1145-bmc LOCAL-ONLY never pushed = invisible to
    #     peers) and yielded to bm-b r572 24ec53190 first-land per
    #     r511 commit-order (registered bands BITWISE == this
    #     machine's gate-derived candidates = r530 family 11th
    #     cross-validation; 12/12 local twin shards audit-verified
    #     and discarded, finalize never ran, zero ledger pollution);
    #     W77 = re-occupation in the yield-receipt window (seat
    #     published=reserved MSG-20261002-1150-bmc). Bands = BOTH
    #     SIDES ARITHMETIC CONTINUATION from the registered W76 tail,
    #     zero skip (r535 law), single reading. TWO in-flight upstream
    #     seats at this freeze: W75 bm-a (finalize pending) + W76
    #     bm-b (burn pending) (finalize chain-pending FAIL-CLOSED
    #     r307 at run time). ADMIT receipt
    #     results/_r363bmc_w77_band_gate.py; not a re-pick -- R250:
    #     W77 bands were never assigned --
    _set_wave(77)
    try:
        assert WAVE_CONFIGS[77]["a_seed_base"] == pf.N1_BANDS[77]["a"][0], \\
            "W77 A band drift vs law mirror"
        assert WAVE_CONFIGS[77]["b_exit_seed_base"] == \\
            pf.N1_BANDS[77]["b_exit"][0], "W77 B band drift vs law mirror"
        assert WAVE_CONFIGS[77].get("engine_owner") == \\
            pf.N1_BANDS[77].get("engine_owner") == "bm-c", \\
            "W77 engine_owner drift (law mirror parity)"
        w77_a = {A_SEED_BASE + j for j in range(A_N)}
        w77_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w77_a & w77_b), "W77 A/B band overlap"
        assert not (w77_a & reg_ints) and not (w77_b & reg_ints), \\
            "W77 hits SEED_REGISTRY"
        for nm, band in (("A", w77_a), ("B", w77_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W77 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W77 {nm} hits W1"
            assert not (band & probes), f"W77 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W70..W76 are
        # REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly (W76 == bm-b r572; W75 == bm-a r571).
        assert pf.N1_BANDS[70] == {"a": (183_004, 185_003),
                                   "b_exit": (51_001, 51_200),
                                   "engine_owner": "bm-b"}, \\
            "registered W70 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[71] == {"a": (185_004, 187_003),
                                   "b_exit": (51_201, 51_400),
                                   "engine_owner": "bm-c"}, \\
            "registered W71 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[72] == {"a": (187_004, 189_003),
                                   "b_exit": (51_401, 51_600),
                                   "engine_owner": "bm-b"}, \\
            "registered W72 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[73] == {"a": (189_004, 191_003),
                                   "b_exit": (51_601, 51_800),
                                   "engine_owner": "bm-a"}, \\
            "registered W73 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[74] == {"a": (191_004, 193_003),
                                   "b_exit": (52_001, 52_200),
                                   "engine_owner": "bm-b"}, \\
            "registered W74 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[75] == {"a": (193_004, 195_003),
                                   "b_exit": (52_201, 52_400),
                                   "engine_owner": "bm-a"}, \\
            "registered W75 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[76] == {"a": (195_004, 197_003),
                                   "b_exit": (52_401, 52_600),
                                   "engine_owner": "bm-b"}, \\
            "registered W76 row parity drift (r307 two-state; bm-b r572 " \\
            "landed bitwise == this machine's yielded W76 draft)"
        # prior-wave disjointness incl. W48..W76 (all registered; the
        # W76 row is the direct arithmetic upstream of W77).
        for wprev in REG_WAVES_ALL:
            assert not (w77_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W77 A hits W{wprev}"
            assert not (w77_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W77 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W77 clears it.
        n3r1_used77 = set(range(70_000, 70_006))
        assert not (w77_a & n3r1_used77) and not (w77_b & n3r1_used77), \\
            "W77 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w77_a & lfc_actual12) and not (w77_b & lfc_actual12), \\
            "W77 bands must clear the lfc actual draw range"
        assert not (w77_a & options_actual12) and \\
            not (w77_b & options_actual12), \\
            "W77 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W77 row, r363): BOTH SIDES ARITHMETIC
        # CONTINUATION from the registered W76 tail, zero skip.
        assert WAVE_CONFIGS[77]["a_seed_base"] == 197_004 == \\
            pf.N1_BANDS[76]["a"][1] + 1, \\
            "W77 A must start at the registered W76 A end + 1 " \\
            "(arithmetic continuation window 197_004..199_003 CLEAN)"
        assert WAVE_CONFIGS[77]["b_exit_seed_base"] == 52_601 == \\
            pf.N1_BANDS[76]["b_exit"][1] + 1, \\
            "W77 B must start at the registered W76 B end + 1 " \\
            "(arithmetic continuation window 52_601..52_800 CLEAN)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W77-SHARD-0",
                                          "n1w77-0of12"), "W77 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W77-SHARD-11",
                                          "n1w77-11of12")
        assert SHARD_DIR.endswith("n1_w77") and OUT.endswith(
            "n1_w77_results.json"), "W77 path drift"
        for wprev in REG_WAVES_ALL:
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W77 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W77_PREREG.md")), \\
            "W77 per-wave prereg missing (materializer requirement)"
        # W77 finalize cumulative deps: W17..W74 outputs ALL PRESENT
        # (static landed seats; chain head 527,348 = W74 bm-b r572
        # K=160,720; W75 bm-a + W76 bm-b = TWO in-flight upstream
        # seats -- the finalize merge loop derives the wave set from
        # registry keys at run time and stays FAIL-CLOSED on the
        # not-yet-finalized seats, r307 two-state law).
        for _depw in range(17, 75):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W77 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law):
        # prior-wave set derives from registry keys below 77 (no 15,
        # incl. 48..76 -- all registered, W75/W76 in-flight,
        # FAIL-CLOSED at run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 77) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 77)], \\
            "W77 prior-wave set must derive from registry keys (no 15; " \\
            "incl. 48..76 -- W75/W76 registered before this freeze landed)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W77 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    REG_WAVES_ALL = '[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 77)]'
    LEG77 = LEG77.replace('REG_WAVES_ALL', REG_WAVES_ALL)
    A3 = '\n    # --- T-141 s2 lane face'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    t2b = t2b.replace(rep_probe, LEG77.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W77 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment (the 5th face) ------
t2c, eol2c = load(FP2)
if '+ W77 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('cluster leg, law sec.4 W76 row, r572 bm-b] "\n'
          '          "+ T-141 s2 ')
    SEG77 = ('cluster leg, law sec.4 W76 row, r572 bm-b] "\n'
             '          "+ W77 materializer face [same guard set, dep=W17..W74 "\n'
             '          "outputs ALL PRESENT (landed chain head 527,348, "\n'
             '          "K=160,720, bm-b r572), W75 bm-a + W76 bm-b = TWO "\n'
             '          "in-flight upstream seats (FAIL-CLOSED r307 at run "\n'
             '          "time), SIXTY-SIXTH ENGINE-OWNED WAVE bm-c\'s twenty-"\n'
             '          "fourth owned claim per machine-derive "\n'
             '          "(engine_owner==bm-c rows 23 + candidate), "\n'
             '          "engine_owner=bm-c per engine de-throttle law "\n'
             '          "O-20261001-2355 sec.2 own-continuous-series "\n'
             '          "(wave 77 = first FREE number after the registered "\n'
             '          "W76 row; r565 yield-then-reoccupy after the W76 "\n'
             '          "zero-cost yield to bm-b r572 24ec53190 per r511 "\n'
             '          "commit-order -- seat MSG-20261002-1145-bmc was "\n'
             '          "LOCAL-ONLY never pushed, visibility failure "\n'
             '          "disclosed; registered bands bitwise == this "\n'
             '          "machine\'s gate-derived candidates = r530 family "\n'
             '          "11th cross-validation; 12/12 local twin shards "\n'
             '          "audit-verified and discarded, finalize never ran, "\n'
             '          "zero ledger pollution; seat published=reserved "\n'
             '          "MSG-20261002-1150-bmc; bands = BOTH SIDES "\n'
             '          "ARITHMETIC CONTINUATION from the W76 tail zero "\n'
             '          "skip per r535 law, single reading, no fork face), "\n'
             '          "N3-R1 used-seed leg, probe-seed cluster leg, law "\n'
             '          "sec.4 W77 row, r363 bm-c] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG77, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W77 segment landed (insert after W76 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W77 row -------------------
ROW77 = """
- N1 波77（r363 bm-c 冻·prereg 时展行）：**第六十六枚引擎波·bm-c 第二十四枚自有波〔机面 derive：engine_owner==bm-c 行 23+本候选〕**·engine_owner=bm-c·SATURATION_ENGINE_LAW §1/§2 同 W10-W76 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-c 实例=常驻架构 v0.4 per-tick 重读（D-20261002-03 修法·W59/W60/W61/W66/W69/W71 同窗实证——冻结 commit 后常驻实例下一 tick 重读活树自见新行自燃=免杀重启免做·点火验证唯一证据=2 tick 内产物增长面 r325 律·state queue 面不信）】·【never-dry 供给律常设步·**波号 77=注册表 W76 行后首个自由号**·**r565 让路-同窗再占位律执行**——W76 号位本机先起草（**gate ADMIT=results/_r363bmc_w76_band_gate.py**·本机机闸独立 derive 候选 **A 195_004..197_003／B 52_401..52_600**·席位公示 MSG-20261002-1145-bmc **本地未推故对侧不可见=如实披露〔r297 可见性族：认领锁可视面=远端 commit·未推席位=零防护〕**）·bm-b r572 同窗先落 origin（24ec53190）=r511 commit 时序正主·本机让路处置=r558 五步（12 分片孪生已由引擎按 r359 自燃律烧毕〔冻结编辑落工作树后 pre-commit 自燃〕·audit.machine=bm-c 逐件验属后随 reset 弃置·finalize 从未跑·append_ledger 零触碰=零科学污染零账本双计）·**正主注册带与本机 gate 派生候选逐位同（双侧）=r530 族第 11 例确定性交叉验证**·席位公示=MSG-20261002-1150-bmc（published=reserved r518-① 律·让路回执内同窗再占位）·r511 表尾锁例冻结前 fetch 实核表尾时 W77 号位净空·origin 侧 vacancy 机验】·**带位=注册 W76 尾双面算术续带零跳位（r535 机闸 derive 律）**：本波 **A-ext seed=197_004..199_003**（==W76 A 尾 197_003+1·步长逐字·A 面算术续带零跳位）；**B-ext exit seed=52_601..52_800**（==W76 B 尾 52_600+1·步长逐字·B 面算术续带零跳位·双侧算术窗零拒绝点=单读法零分叉〔r566 面〕·==W76 行 W77+ 警示投影逐字〔bm-b r572 gate 投影腿机证+本波 r363 bm-c gate 机闸独立复核逐字同=双机互证〕·R250：W77 带从未指派·测量面零结果可钓）·【机证净空——leg0 七十五键（74 注册行+候选）+leg0b W76 行 W77+ 投影 prose 软校验（W71 缺席合法先例·机闸 derive 为唯一 derive 面）+leg1-A/leg1-B 算术位 CLEAN 机证+leg2 双侧首净窗==算术==候选+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验·**MSG-0640 三修工具**（FIX-A 编辑前 origin-blob 等值断言+FIX-B 锚=最后注册行 W76+行存活核查+FIX-C 推送前纯增量 diff 断言）〕·ADMIT 回执=results/_r363bmc_w77_band_gate.py·r363 bm-c 起草窗实跑】·扫描面=pre-W77 七十四行 N1 带表【含 **W72 行 187_004..189_003/51_401..51_600〔bm-b r570·finalize 已落账 K=156,320·链头 522,948〕**·**W73 行 189_004..191_003/51_601..51_800〔bm-a r570·finalize 已落账 K=158,520·链头 525,148〕**·**W74 行 191_004..193_003/52_001..52_200〔bm-b r571·finalize 已落账 K=160,720·净链头 527,348·bm-b r572 本窗〕**·**W75 行 193_004..195_003/52_201..52_400〔bm-a r571·12/12 烧毕〔bm-a r572a ride 交付〕·finalize 未落账〕**·**W76 行 195_004..197_003/52_401..52_600〔bm-b r572 注册·本机让路草稿逐位同·烧录待启〕**】·**两在飞上游席披露：W75 bm-a（12/12 烧毕 finalize 未落账）+W76 bm-b（注册烧录待启）→本波 finalize 链序前置=W75+W76 落账·FAIL-CLOSED r307 两态律**·带域不相交·W1 ext·v1 在用带·SEED_REGISTRY 全键（160 int 值·LOWAMP-P1/P2/P3 键 20.33M 域零交集）·**N3-R1 实际种子带 70_000..70_005**（r529 裁定行②强制腿）·**runner 探针种子簇 95_000..95_003**（r335 发现腿·W26 起强制）·N2/N4 设计探针保留点 40_000/40_001·N2-W15 草案探针点 31_000/31_500/32_000·lfc 实际流 30_000..30_099·options_wave2 实际流 63_000..63_049（leg-3e 实际流避让腿）·**W78+ 投影（gate 投影腿机证=results/_r363bmc_w77_band_gate.py 尾投影·W78 prereg 窗机闸复核 r335 律）：A 199_004..201_003 CLEAN／B 52_801..53_000 REFUSED〔SEED_REGISTRY 点 53_000 尾点命中〕→W78 B 面须按 r307 尾律机 derive 首净窗跳过 53_000（W39-B/W43-B/W47-B/W51-B/W59-B/W66-B 跳位族先例·两侧独立裁定如实披露）**·prereg=PERPETUAL_N1_W77_PREREG.md 冻结〔S5 锚=W74 实测（锚滚动律·W75/W76 在飞未落）：merged mu −0.092106/W74-only mu −0.087584/sigma 0.2467/A-p95 0.3117/K-lift +0.0002·累计池投影 167,320（含 W75+W76 在飞 4,400）〕·burn 由本机常驻引擎 v0.4 per-tick 自燃·finalize=活链头 derive one-pass（r538 一过律·链序前置=W75+W76 双落账）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce277\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW77.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W77 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    77: {"a": (197_004') == 1, 'FIX-B FAIL: W77 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W77"') == 1, 'FIX-B FAIL: W77 config not exactly once'
for w in range(58, 77):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W77 materializer face') == 2, \
    'FIX-B FAIL: W77 leg+summary must be exactly 2'
for w in range(48, 77):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce277\uff08') == 1, 'FIX-B FAIL: canon W77 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W77 added per face')

# ---------------- FIX-C: pure-insertion delta vs origin -----------------------
for p in TARGETS:
    out = git('diff', 'origin/main', '--numstat', '--', p).decode('utf-8').strip()
    if not out:
        sys.exit(f'FIX-C FAIL: no diff shown for {p} (edits missing?)')
    for line in out.splitlines():
        add, dele, path = line.split('\t')
        assert int(dele) == 0, f'FIX-C FAIL: {p} shows {dele} deleted lines ' \
                               f'(pure insertion violated -- r519 content-variant abort)'
        print(f'FIX-C: {p} +{add} -0 (pure insertion)')
print('FREEZE_EDITS_OK')
