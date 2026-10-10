# r837 bm-c W204 five-face freeze phase-2 -- live splice editor.
# Lineage: _r936bma_w203_freeze_edits.py pattern + r787 preflight law
# (preflight already ALL GREEN on this exact tree) + r609 origin-verbatim
# base + r761 programmatic quote wrapping + r909 physical-byte anchors.
# Zero hardcoded band values: all band facts from the committed ADMIT
# receipt (results/_w204bmc_20261010_probe_receipt.json).
import json, hashlib, os, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PF = os.path.join(REPO, "scripts", "perpetual_faces.py")
N1 = os.path.join(REPO, "scripts", "perpetual_faces_n1.py")
RECEIPT_IN = os.path.join(REPO, "results", "_w204bmc_20261010_probe_receipt.json")
RECEIPT_OUT = os.path.join(REPO, "results", "_r837bmc_w204_freeze_receipt.json")

def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True)

# ---------- gate 0: fresh origin, working == origin (r609 law) ----------
git("fetch", "origin")
r = git("rev-parse", "HEAD"); head = r.stdout.decode().strip()
ro = git("rev-parse", "origin/main"); omain = ro.stdout.decode().strip()
assert head == omain, f"HEAD {head} != origin/main {omain} -- rebase first (r609)"
for path in ("scripts/perpetual_faces.py", "scripts/perpetual_faces_n1.py"):
    b = git("show", f"origin/main:{path}")
    w = open(os.path.join(REPO, path), "rb").read()
    assert b.stdout == w, f"working {path} != origin blob -- stale base (r609 abort)"

# ---------- band facts from the committed ADMIT receipt (never transcribed) ----------
rec = json.load(open(RECEIPT_IN, encoding="utf-8"))
assert rec["verdict"] == "ADMIT"
A = rec["bands"]["A"]; B = rec["bands"]["B"]          # "463604_465603" / "465604_465803"
a_lo, a_hi = (int(x) for x in A.split("_"))
b_lo, b_hi = (int(x) for x in B.split("_"))
leg1 = rec["legs"]["leg1"]
assert [a_lo, a_hi] == leg1["A"] and [b_lo, b_hi] == leg1["B"], "receipt band mismatch"
w203_b_tail = 463_603   # registered W203 row b_exit hi (asserted below from pf import)
pri_b_tail = a_hi       # own-wave A tail

# ---------- read files, EOL ----------
pf_b = open(PF, "rb").read(); pf_t = pf_b.decode("utf-8")
n1_b = open(N1, "rb").read(); n1_t = n1_b.decode("utf-8")
EOL = "\r\n"; PF_EOL = "\r\n"
assert pf_t.count("\r\n") > 0 and n1_t.count("\r\n") > 0

def must(t, s, n, what):
    c = t.count(s)
    assert c == n, f"anchor {what}: count {c} != {n}"
    return s

# ---------- extract parity section (physical bytes, never re-typed) ----------
a6 = '    # --- W203 materializer face'
a4 = '    # --- T-141 s2 lane face'
w203_start = n1_t.find(a6); t141_pos = n1_t.find(a4)
blk = n1_t[w203_start:t141_pos]
par_marker = "        # registered row parity (r307 pinned constants, recent estate)"
disj_marker = "        # prior-wave disjointness W2..W202 (single state: all"
par_sec = blk[blk.find(par_marker):blk.find(disj_marker)]
assert par_sec.count("assert pf.N1_BANDS[") == 50 and par_sec.endswith(EOL)

# ---------- indent extraction (physical, not assumed) ----------
def line_indent(t, needle):
    i = t.find(needle)
    assert i >= 0, f"indent needle not found: {needle[:40]}"
    ls = t.rfind(EOL, 0, i) + 2
    line = t[ls:t.find(EOL, ls)]
    return line[:len(line) - len(line.lstrip(" "))]

CFG_I  = line_indent(n1_t, '203: {"batch"')            # cfg entry key indent (23)
PRE_KEY_I = line_indent(n1_t, '"prereg": ("research/PERPETUAL_N1_W203_PREREG.md')  # 28
PRE_I  = line_indent(n1_t, '"pre-run; design = frozen v1 null calibration verbatim, "')  # 39
MEM_I  = line_indent(n1_t, '"a_seed_base": 461_404')    # cfg member indent (28)
ROW_I  = line_indent(pf_t,  '203: {"a"')                # pf row indent (4)
ROWC_I = line_indent(pf_t,  '"engine_owner": "bm-a"},')  # pf row continuation (9)

# ---------- pf comment + row ----------
pf_comment = EOL.join([
"    # W204 (bm-c r837 five-face freeze phase-2 splice rebuild, seat",
"    # MSG-2026-10-10-0022-bmc-w204-seat pushed to origin 7cf82c262",
"    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen",
"    # commit 1422ad767 (prereg research/PERPETUAL_N1_W204_PREREG.md,",
"    # probe results/_w204bmc_20261010_probe_receipt.json);",
"    # deletion-set EMPTY; delivery window = splice rebuild after the",
"    # W139/W140 SEED_REGISTRY adjudication carve-outs landed 7464be852",
"    # (O-20261010-1906-bm-c adjudicated; receipt",
"    # MSG-2026-10-10-1940) -- the C1804 dead-session spliced dual",
"    # files were NOT recoverable (r836 verified, all worktrees",
"    # searched); this row is the honest rebuild from the committed",
"    # ADMIT receipt on an origin-verbatim base (r609 lesson:",
"    # execution-time rev-parse + fresh blob, no stale-cache reuse);",
"    # zero --no-verify; the W204 seat MSG sits in",
"    # fleet/inbox/processed/ at freeze time, honest archived",
"    # per S7 law);",
"    # band gate ADMIT results/_w204bmc_20261010_probe_receipt.json: A = FIRST-CLEAN",
"    # past the registered W203 B band (arithmetic continuation",
"    # 463_404..465_403 REFUSED at its own start by the W203 B band",
"    # 463_404..463_603, exactly as the W203 pf/probe leg4",
"    # W204+ succession projection notes anticipated;",
"    # honest forward walk hops=1 -> 463_604..465_603, non-rotational",
"    # r587 forward-monotone walk; A base == prior-wave B tail+1",
"    # (463_603+1) machine-checkable -- A-hops-prior-B staircase",
"    # SIXTY-FOURTH instance, E36 card);",
"    # B = FIRST-CLEAN past the own-wave A window (arithmetic",
"    # continuation 463_604..463_803 CLEAN on the registered",
"    # universe but lands INSIDE the W204 A band window --",
"    # same-freeze mutual exclusion (W141 precedent, leg2 law) --",
"    # the walk with the own-wave A window reserved jumps to",
"    # 465_604 -> 465_604..465_803, hops=1, non-rotational",
"    # r587 forward-monotone walk; B base == own-wave A tail+1",
"    # (465_603+1) machine-checkable);",
"    # single-window derive (r812 merged the gate legs INTO the",
"    # pre-seat probe; dual-window parity N/A honest); scan face =",
"    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1",
"    # used-seed band + probe cluster 95_000..95_003 + cross-face",
"    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/",
"    # N2-W15 probe points.",
"    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention upgrade,",
"    # Tools/seed_admit_gate.py, run on the pre-splice universe):",
"    # rc0 base=463604 span=2000 checked=2000 verdict=FREE /",
"    # rc0 base=465604 span=200 checked=200 verdict=FREE.",
"    # W205+ projection (gate-derived pre-seat probe leg4, pre-W204",
"    # universe): A first-clean 465_604..467_603 CLEAN hops=0 /",
"    # B first-clean 465_804..466_003 CLEAN hops=0 -- naive B lands",
"    # INSIDE the naive A window and the registered W204 B band",
"    # 465_604..465_803 will refuse the naive W205 A window (W205",
"    # seat MSG-2026-10-10-1627-bma already declared A 465_804..467_803",
"    # / B 467_804..468_003 on the post-W204-declared universe;",
"    # if the W204 row lands before the W205 freeze the W205 freezer",
"    # MUST re-pull and re-verify the universe face); W206 freezer",
"    # MUST re-derive on the post-W205 universe AND reserve the",
"    # own-wave A window when deriving B (W141 precedent, leg2 law,",
"    # E36 staircase card; never transcribe r587).",
"    # NOT a re-pick (R250: W204 bands were never assigned).",
])
def fmt(n):  # 463604 -> "463_604" (W-family display form)
    return f"{n // 1000}_{n % 1000:03d}"
pf_row = (f'{ROW_I}204: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), '
          f'"b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'
          + EOL + f'{ROWC_I}"engine_owner": "bm-c"}},' + EOL)
# belt-and-braces: display form must equal the canonical W-family text
assert pf_row.split(EOL)[0].strip() == \
    '204: {"a": (463_604, 465_603), "b_exit": (465_604, 465_803),'

old_pf = must(pf_t, ('         "engine_owner": "bm-a"},' + PF_EOL + '}'
                     + PF_EOL + '# v1 + ext(wave-1) in-use bands'), 1, "pf_close")
new_pf = ('         "engine_owner": "bm-a"},' + PF_EOL
          + pf_comment + EOL + pf_row
          + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands')
pf_t2 = pf_t.replace(old_pf, new_pf, 1)

# ---------- n1 cfg entry (programmatic quote wrapping, r761 law) ----------
cfg_lines = [
 f'{CFG_I}204: {{"batch": "PERPETUAL-N1-W204",',
 f'{PRE_KEY_I}"prereg": ("research/PERPETUAL_N1_W204_PREREG.md (wave-level frozen "',
]
PRE = [
 "pre-run; design = frozen v1 null calibration verbatim, ",
 "new seed bands only; TWO HUNDRED AND FOURTH ENGINE-OWNED WAVE ",
 "BY MACHINE-DERIVE (engine_owner rows 193 + candidate), ",
 "own-series continuation per O-20261001-2355 sec.2 (first-free-",
 "number law after the REGISTERED W203 row bm-a r936 freeze ",
 "b2bb60963, SINGLE STATE zero seat gap W2..W203 all ",
 "registered; W1..W203 finalize ALL LANDED (W203 bm-a r938 ",
 "one-pass, ledger head 860,945, merged pool K=444,520) -- ",
 "ZERO in-flight upstream seats at splice time, clean precondition; ",
 "seat published=reserved ",
 "MSG-20261010-0022-bmc-w204-seat PUSHED to origin 7cf82c262 ",
 "BEFORE this freeze per r565 early-visibility law (payload = ",
 "seat MSG + prereg + pre-seat probe script + probe receipt, ",
 "frozen commit 1422ad767); ",
 "deletion-set EMPTY; delivery window = phase-2 splice rebuild ",
 "after the W139/W140 SEED_REGISTRY adjudication carve-outs ",
 "landed 7464be852 (O-20261010-1906-bm-c adjudicated, receipt ",
 "MSG-2026-10-10-1940; the C1804 dead-session spliced dual ",
 "files were NOT recoverable, r836 verified -- this entry is ",
 "the honest rebuild from the committed ADMIT receipt on an ",
 "origin-verbatim base per the r609 lesson); zero merge at ",
 "freeze delivery, zero ",
 "--no-verify; single-window derive -- r812 merged the gate ",
 "legs INTO the pre-seat probe; parity N/A honest), ",
 "engine_owner=bm-c, wave 204: ",
 "A = FIRST-CLEAN past the registered W203 B band (the ",
 "arithmetic continuation 463_404..465_403 is REFUSED at its ",
 "own start by the W203 B band 463_404..463_603, exactly as ",
 "the W203 pf/probe leg4 succession ",
 "projection notes anticipated; honest forward walk hops=1 -> ",
 "463_604..465_603; A base == prior-wave B tail+1 ",
 "machine-checkable = A-hops-prior-B staircase SIXTY-FOURTH ",
 "instance, E36 card; non-rotational r587 forward-monotone ",
 "walk) + B = FIRST-CLEAN past the own-wave A window (the ",
 "arithmetic continuation 463_604..463_803 is CLEAN on the ",
 "registered universe but lands INSIDE the W204 A band ",
 "window -- same-freeze mutual exclusion, W141 precedent, ",
 "leg2 law -- the walk with the own-wave A window reserved ",
 "jumps to 465_604, first-clean 465_604..465_803 hops=1, ",
 "non-rotational r587 forward-monotone walk; B base == ",
 "own-wave A tail+1 machine-checkable; cross-window ",
 "convergence with the W203 pf/probe leg4 succession projection ",
 "notes re-derived -- all ",
 "MANDATORY notes honored (post-W203 universe re-derive + ",
 "own-wave A reservation); ADMIT receipt ",
 "results/_w204bmc_20261010_probe_receipt.json + ",
 "seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a ",
 "ADMIT convention upgrade); W205+ projection ",
 "per this window gate: A first-clean 465_604..467_603 ",
 "CLEAN / B first-clean 465_804..466_003 CLEAN -- naive ",
 "B lands INSIDE the naive A window and the registered ",
 "W204 B band 465_604..465_803 will refuse the naive ",
 "W205 A window (W205 seat MSG-2026-10-10-1627-bma declared ",
 "on the post-W204-declared universe; the W205 freezer MUST ",
 "re-pull and re-verify if the W204 row lands before the ",
 "W205 freeze); W206+ freezer MUST re-derive on the ",
 "post-W205 universe AND reserve the own-wave A window ",
 "when deriving B (W141 precedent, leg2 law, E36 ",
 "staircase card); W1..W203 finalize ALL LANDED (W203 ",
 "finalize one-pass bm-a r938, net chain head 860,945, ",
 "merged pool K=444,520) -- ZERO in-flight upstream ",
 "seats, clean finalize chain precondition -- finalize ",
 "merge loop still derives the wave set from registry ",
 "keys at run time, FAIL-CLOSED r307 always on)",
]
for s in PRE:
    cfg_lines.append(f'{PRE_I}"{s}"')
cfg_lines += [
 f'{PRE_I}"),',
 f'{MEM_I}"a_seed_base": 463_604,        # law sec.4 W204 A: 463_604..465_603 (FIRST-CLEAN past the registered W203 B band; arithmetic 463_404..465_403 REFUSED at own start by the W203 B band 463_404..463_603; hops=1; A-hops-prior-B staircase SIXTY-FOURTH instance, E36 card; ordinal machine-read SIXTY-FOURTH per probe receipt)',
 f'{MEM_I}"b_exit_seed_base": 465_604,   # law sec.4 W204 B: 465_604..465_803 (FIRST-CLEAN past the own-wave A window; arithmetic 463_604..463_803 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
 f'{MEM_I}"shard_subdir": "n1_w204", "out_name": "n1_w204_results.json",',
 f'{MEM_I}"engine_owner": "bm-c"}},',
]
cfg_block = EOL.join(cfg_lines)
old_cfg = must(n1_t, ('                       }' + EOL
                      + 'PREREG = WAVE_CONFIGS[2]["prereg"]'), 1, "n1_cfg_close")
# cfg_block lines carry their own CFG_I indents -- no outer indent prepended
new_cfg = (cfg_block + EOL
           + '                       }' + EOL
           + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
assert new_cfg.count('204: {"batch": "PERPETUAL-N1-W204"') == 1
n1_t2 = n1_t.replace(old_cfg, new_cfg, 1)

# ---------- n1 materializer block ----------
hdr = [
 "    # --- W204 materializer face (r837 bm-c five-face freeze phase-2",
 "    #     splice rebuild, own-series law under CEO fill-order standing",
 "    #     2026-10-08 ~23:5x + O-20261009-2334-bm-b sec.1-2 local-full-use",
 "    #     + O-20260924-1730 claim-and-start same-round law): bm-c's",
 "    #     thirty-sixth owned per machine-derive (engine_owner==bm-c",
 "    #     rows 35 + candidate); wave 204 = first free number after",
 "    #     the REGISTERED W203 row (bm-a r936 freeze b2bb60963) --",
 "    #     SINGLE STATE zero seat gap (W2..W203 all registered). Seat",
 "    #     published=reserved MSG-20261010-0022-bmc-w204-seat pushed",
 "    #     to origin 7cf82c262 BEFORE this freeze, r565 law (payload =",
 "    #     seat MSG + prereg + pre-seat probe script + probe receipt",
 "    #     frozen commit 1422ad767; deletion-set EMPTY; delivery window",
 "    #     = splice rebuild after the W139/W140 SEED_REGISTRY",
 "    #     adjudication carve-outs landed 7464be852",
 "    #     (O-20261010-1906-bm-c adjudicated, receipt",
 "    #     MSG-2026-10-10-1940) -- the C1804 dead-session spliced",
 "    #     dual files were NOT recoverable (r836 verified), this",
 "    #     block is the honest rebuild from the committed ADMIT",
 "    #     receipt, origin-verbatim base per the r609 lesson; zero",
 "    #     --no-verify; the W204 seat MSG sits in",
 "    #     fleet/inbox/processed/ at freeze time, honest archived",
 "    #     per S7 law).",
 "    #     TWO HUNDRED AND FOURTH engine wave BY",
 "    #     MACHINE-DERIVE (engine_owner rows 193 + candidate; gate",
 "    #     leg0 machine output governs per r359 law).",
 "    #     W1..W203 finalize ALL LANDED (net chain head 860,945,",
 "    #     K=444,520 merged pool; W203 finalize one-pass bm-a r938)",
 "    #     -- ZERO in-flight upstream seats at splice time, clean",
 "    #     finalize chain precondition; the finalize merge loop",
 "    #     still derives the wave set from registry keys at run",
 "    #     time, FAIL-CLOSED r307 always on. ADMIT receipt",
 "    #     results/_w204bmc_20261010_probe_receipt.json;",
 "    #     seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a",
 "    #     ADMIT convention upgrade); banned gate ADMIT 0;",
 "    #     not a re-pick (R250: W204 bands were never assigned).",
 "    _set_wave(204)",
 "    try:",
 '        assert WAVE_CONFIGS[203]["a_seed_base"] == pf.N1_BANDS[203]["a"][0], \\',
 '            "W204 A band drift vs law mirror"',
 "        assert WAVE_CONFIGS[203][\"b_exit_seed_base\"] == \\",
 '            pf.N1_BANDS[203]["b_exit"][0], "W204 B band drift vs law mirror"',
 "        assert WAVE_CONFIGS[203].get(\"engine_owner\") == \\",
 '            pf.N1_BANDS[203].get("engine_owner") == "bm-a", \\',
 '            "W204 engine_owner drift (law mirror parity)"',
 "        w203_a = {A_SEED_BASE + j for j in range(A_N)}",
 "        w203_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
 '        assert not (w203_a & w203_b), "W204 A/B band overlap"',
 "        assert not (w203_a & reg_ints) and not (w203_b & reg_ints), \\",
 '            "W204 hits SEED_REGISTRY"',
 '        for nm, band in (("A", w203_a), ("B", w203_b)):',
 '            assert not (band & v1_a) and not (band & v1_b), f"W204 {nm} hits v1"',
 '            assert not (band & w1_a) and not (band & w1_b), f"W204 {nm} hits W1"',
 '            assert not (band & probes), f"W204 {nm} hits probe seeds"',
]
w203_leg = [
 '        assert pf.N1_BANDS[203] == {"a": (461_404, 463_403),',
 '                                    "b_exit": (463_404, 463_603),',
 '                                    "engine_owner": "bm-a"}, \\',
 '            "registered W203 row parity drift (r307; bm-a r936)"',
]
tail = [
 "        # prior-wave disjointness W2..W203 (single state: all",
 "        # registered, dynamic registry derive, r511 law)",
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 204):",
 '            assert not (w203_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
 "                                 for j in range(A_N)}), f\"W204 A hits W{wprev}\"",
 '            assert not (w203_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
 "                                  for j in range(B_N)}), f\"W204 B hits W{wprev}\"",
 "        n3r1_used203 = set(range(70_000, 70_006))",
 "        assert not (w203_a & n3r1_used203) and not (w203_b & n3r1_used203), \\",
 '            "W204 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
 "        assert not (w203_a & lfc_actual12) and not (w203_b & lfc_actual12), \\",
 '            "W204 bands must clear the lfc actual draw range"',
 "        assert not (w203_a & options_actual12) and \\",
 "            not (w203_b & options_actual12), \\",
 '            "W204 bands must clear the options_wave2 actual draw range"',
 "        # band facts (law sec.4 W204 row): A = FIRST-CLEAN past",
 "        # the registered W203 B band (the arithmetic continuation",
 "        # 463_404..465_403 is REFUSED at its own start by the W203",
 "        # B band 463_404..463_603, exactly as the W203 pf/probe",
 "        # leg4 succession projection notes anticipated; honest",
 "        # forward walk hops=1 lands 463_604..465_603; A base ==",
 "        # prior-wave B tail+1 (463_603+1) machine-checkable --",
 "        # A-hops-prior-B staircase SIXTY-FOURTH instance, E36 card;",
 "        # non-rotational r587 forward-monotone walk);",
 "        # B = FIRST-CLEAN past the own-wave A window (the",
 "        # arithmetic continuation 463_604..463_803 is CLEAN on the",
 "        # registered universe but lands INSIDE the W204 A band",
 "        # window -- same-freeze mutual exclusion (W141 precedent,",
 "        # leg2 law) -- the walk with the own-wave A window reserved",
 "        # jumps to 465_604 and lands 465_604..465_803, hops=1,",
 "        # non-rotational r587 forward-monotone walk; B base ==",
 "        # own-wave A tail+1 (465_603+1) machine-checkable;",
 "        # cross-window convergence with the W203 pf/probe leg4 +",
 "        # W204 pre-seat probe leg4 succession projection notes --",
 "        # all MANDATORY notes honored (post-W203 universe",
 "        # re-derive + own-wave A reservation when deriving B);",
 "        # seat MSG-0022 tail, re-derived).",
 '        assert WAVE_CONFIGS[204]["a_seed_base"] == 463_604 == 463_603 + 1, (',
 '            "W204 A must be the first-clean window past the registered "',
 '            "W203 B band tail 463_603+1 (arithmetic continuation "',
 '            "463_404..465_403 REFUSED at its own start by the W203 B "',
 '            "band 463_404..463_603, exactly as the W203 pf/probe leg4 "',
 '            "succession projection notes "',
 '            "anticipated; honest forward walk hops=1; A base == "',
 '            "prior-wave B tail+1 machine-checkable = A-hops-prior-B "',
 '            "staircase SIXTY-FOURTH instance, E36 card)")',
 "        arith_a203 = set(range(463_604, 465_604))",
 "        assert not (arith_a203 & reg_ints), \\",
 '            "W204 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
 '        assert WAVE_CONFIGS[204]["b_exit_seed_base"] == 465_604 == 465_603 + 1, (',
 '            "W204 B must be the first-clean window past the own-wave A "',
 '            "band tail 465_603+1 (arithmetic continuation "',
 '            "463_604..463_803 CLEAN on the registered universe but "',
 '            "lands INSIDE the W204 A band window; same-freeze mutual "',
 '            "exclusion (W141 precedent, leg2 law) -- the walk with the "',
 '            "own-wave A window reserved jumps to 465_604, first-clean "',
 '            "hops=1, non-rotational r587 forward-monotone walk; B "',
 '            "base == own-wave A tail+1 machine-checkable)")',
 "        arith_b203 = set(range(465_604, 465_804))",
 "        assert not (arith_b203 & reg_ints), \\",
 '            "W204 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
 "        assert not (arith_b203 & arith_a203), \\",
 '            "W204 A/B same-freeze mutual exclusion (B hops past own A)"',
 '        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W204-SHARD-0",',
 '                                          "n1w204-0of12"), "W204 entry identity"',
 '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W204-SHARD-11",',
 '                                           "n1w204-11of12")',
 "        assert SHARD_DIR.endswith(\"n1_w204\") and OUT.endswith(",
 '            "n1_w204_results.json"), "W204 path drift"',
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 204):",
 "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(",
 "                PATHS.results_dir, \"p2cal_ext\",",
 "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\",
 '                f"W204 shard dir collides with W{wprev}"',
 "        # W204 finalize cumulative deps: W17..W203 outputs ALL PRESENT",
 "        # (landed net chain head 860,945 = W203 bm-a r938 one-pass)",
 "        # -- ZERO in-flight upstream seats at splice, clean precondition",
 "        # freeze window; the finalize merge loop derives the wave",
 "        # set from registry keys at run time and stays",
 "        # FAIL-CLOSED, r307 two-state law).",
 "        for _depw in range(17, 204):",
 "            assert os.path.exists(os.path.join(",
 "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\",
 '                f"W204 finalize cumulative dep (W{_depw} output) missing"',
 "        # finalize wave-set derivation face (r511 derive law): every",
 "        # registered wave below 204 composes; wave 15 excluded by",
 "        # design; SINGLE STATE (W2..W203 all registered -- no",
 "        # two-state seat disclosure needed at this freeze).",
 "        assert sorted(w for w in WAVE_CONFIGS if w < 204) == \\",
 "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\",
 "            [w for w in range(16, 204)], \\",
 '            "W204 prior-wave set must derive from registry keys (no 15; " \\',
 '            "W2..W203 registered single state)"',
 "        assert os.path.exists(os.path.join(",
 '            PATHS.root, "research", "PERPETUAL_N1_W204_PREREG.md")), \\',
 '            "W204 per-wave prereg missing (materializer requirement)"',
 '        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"',
 "    finally:",
 "        _set_wave(2)",
]
block = EOL.join(hdr) + EOL + par_sec + EOL.join(w203_leg) + EOL + EOL.join(tail) + EOL
old_blk_anchor = must(n1_t2, "    # --- T-141 s2 lane face", 1, "t141_marker")
n1_t3 = n1_t2.replace(old_blk_anchor, block + old_blk_anchor, 1)

# ---------- n1 print line ----------
pr = [
 '          "+ W204 materializer face [same guard set, dep=W17..W203 "',
 '          "outputs ALL PRESENT (landed net chain head 860,945 = "',
 '          "W203 bm-a r938 one-pass, K=444,520 merged pool) -- ZERO "',
 '          "in-flight upstream seats at splice, clean precondition, TWO HUNDRED AND FOURTH "',
 '          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 193 "',
 '          "+ candidate) bm-c\'s thirty-sixth owned claim per "',
 '          "machine-derive (engine_owner==bm-c rows 35 + candidate), "',
 '          "A=FIRST-CLEAN past the registered W203 B band (staircase "',
 '          "SIXTY-FOURTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
 '          "own-wave A window (W141 precedent, leg2 law, same-freeze "',
 '          "mutual exclusion, hops=1), phase-2 splice rebuild from the "',
 '          "committed ADMIT receipt + seed_admit_gate rc0 both bands FREE "',
 '          "(O-20261010-1945-bm-a ADMIT convention upgrade), "',
 '          "ADMIT receipt "',
 '          "results/_w204bmc_20261010_probe_receipt.json, law sec.4 W204 row, "',
 '          "r837 bm-c] "',
]
old_pr = must(n1_t3, '          "+ T-141 s2 "', 1, "print_t141")
n1_t4 = n1_t3.replace(old_pr, EOL.join(pr) + EOL + old_pr, 1)

# ---------- post-edit count gates ----------
assert n1_t4.count('"PERPETUAL-N1-W204"') == 1
assert n1_t4.count("W204 materializer face") == 1
assert n1_t4.count('204: {"batch": "PERPETUAL-N1-W204"') == 1
assert pf_t2.count('    204: {"a"') == 1
assert pf_t2.count('"engine_owner": "bm-c"},\r\n}') == 1
assert n1_t4.count('    # --- T-141 s2 lane face') == 1
assert n1_t4.count('"PERPETUAL-N1-W204-SHARD-0"') == 1
assert n1_t4.count('f"W204 A hits W{wprev}"') == 1
assert n1_t4.count('assert pf.N1_BANDS[203] == {"a": (461_404, 463_403),') == 1
# no start>end malformed windows in inserted prose (r773 law)
import re
for seg in (pf_comment, cfg_block, block, EOL.join(pr)):
    for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", seg):
        lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
        assert lo <= hi, f"malformed window {m.group(0)} in inserted prose"

# ---------- write + AST gate ----------
open(PF, "wb").write(pf_t2.encode("utf-8"))
open(N1, "wb").write(n1_t4.encode("utf-8"))
import py_compile
py_compile.compile(PF, doraise=True)
py_compile.compile(N1, doraise=True)

# ---------- receipt ----------
receipt = {
  "round": 837, "machine": "bm-c", "wave": 204,
  "phase": "five-face freeze phase-2 splice rebuild (C1804 loss, honest rebuild)",
  "origin_base": omain,
  "pf_sha16_pre": hashlib.sha256(pf_b).hexdigest()[:16],
  "n1_sha16_pre": hashlib.sha256(n1_b).hexdigest()[:16],
  "pf_sha16_post": hashlib.sha256(pf_t2.encode("utf-8")).hexdigest()[:16],
  "n1_sha16_post": hashlib.sha256(n1_t4.encode("utf-8")).hexdigest()[:16],
  "bands": {"A": A, "B": B, "a_lo": a_lo, "a_hi": a_hi, "b_lo": b_lo, "b_hi": b_hi},
  "admit_receipt": "results/_w204bmc_20261010_probe_receipt.json",
  "seed_admit_gate": ["rc0 base=463604 span=2000 checked=2000 verdict=FREE",
                      "rc0 base=465604 span=200 checked=200 verdict=FREE"],
  "banned_gate": "ADMIT rc0 (re-run r837 freeze window)",
  "adjudication_unblock": "W139/W140 carve-outs 7464be852 (O-20261010-1906-bm-c, receipt MSG-2026-10-10-1940)",
  "parity_section": {"source": "W203 block physical bytes (rows 138..187)",
                     "bytes": len(par_sec), "row_asserts": 50},
  "eol": {"n1_crlf": True, "pf_crlf": True},
  "liveness_anchors": {"t141_marker_kept": 1, "w203_block_kept": 1},
}
open(RECEIPT_OUT, "w", encoding="utf-8").write(json.dumps(receipt, indent=1))
print(json.dumps({k: receipt[k] for k in
      ("phase", "origin_base", "pf_sha16_post", "n1_sha16_post", "bands")}, indent=1))
print("SPLICE OK -- py_compile both green")
