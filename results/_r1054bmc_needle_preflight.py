# r1054 bm-c: W254 derive-editor needle pre-flight probe (zero-transcription law)
# Simulates the planned blankets on the W253 freeze script and counts every planned
# needle, so the derive editor's expect-asserts are machine-verified BEFORE authoring.
# Also reads the frozen W254 prereg for the authored-window face + sec.3 counts.
import io, json, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = io.open(os.path.join(REPO, "results", "_w253bmc_freeze_edits.py"), encoding="utf-8").read()
t = SRC

# my xf(): blankets in pass order + my P5a mappings (post-blanket forms)
def xf(s):
    s = s.replace("W254", "W255")
    s = s.replace("253", "254")
    s = s.replace("252", "253")
    s = s.replace("MSG-20261016-12xx-bmc-w254-seat", "MSG-20261016-14xx-bmc-w254-seat")
    s = s.replace("r1050 splice window", "r1053 splice window")
    s = s.replace("r1050", "r1053")
    s = s.replace("r1052", "r1054")
    s = s.replace("978,735", "980,935")
    s = s.replace("552,320", "554,520")
    s = s.replace("SEVENTY-THIRD", "SEVENTY-FOURTH")
    s = s.replace("TWO HUNDRED AND FIFTY-THIRD", "TWO HUNDRED AND FIFTY-FOURTH")
    s = s.replace("forty-first consecutive", "forty-second consecutive")
    s = s.replace("bmc_ordinal=73", "bmc_ordinal=74")
    s = s.replace("authored 13:2x", "authored 17:4x")
    s = s.replace("f6433ee61", "fa70f3765")
    s = s.replace("741371846", "e2c4b543e")
    s = s.replace("2026-10-16 14:2x bm-c r1053 freeze window", "2026-10-16 18:4x bm-c r1054 freeze window")
    s = s.replace("W253 finalize one-pass bm-c r1050 window closeout 12:2x",
                  "W253 finalize one-pass bm-c r1053 window closeout 14:4x")
    s = s.replace("transitive window W240..W249 checked", "transitive window W241..W250 checked")
    s = s.replace("engine_owner==bm-c rows 72 + candidate", "engine_owner==bm-c rows 73 + candidate")
    return s

tx = xf(t)
print("post-blanket len:", len(tx), "(src", len(t), ")")

# planned plain needles (post-xf forms) with planned dsts -- count check
plain = [
    # P1 needles are pre-blanket (run before xf): count them on SRC
]
p1 = [
    ("(249, 248, 247, 246, 245, 244, 243, 242, 241, 240)", "(250, 249, 248, 247, 246, 245, 244, 243, 242, 241)"),
    ("range(209, 254)", "range(209, 255)"),
    ('def fmt(n):  # 571901 -> "571_901"', 'def fmt(n):  # 574101 -> "574_101"'),
]
print("--- P1 (counted on RAW src, pre-blanket) ---")
for old, new in p1:
    print(f"  {t.count(old)}x  {old[:60]!r}")

print("--- P2 blanket: W254 occurrences in RAW src (downstream faces) ---")
print("  W254:", t.count("W254"))

print("--- P5a plain reps (counted on post-xf text) ---")
p5a = [
    ("980_935", None), ("554_520", None),
    ("980,935", None), ("554,520", None),
    ("bmc_ordinal=74", None), ("SEVENTY-FOURTH", None),
    ("TWO HUNDRED AND FIFTY-FOURTH", None), ("forty-second consecutive", None),
    ("74th own wave", None), ("MSG-20261016-14xx-bmc-w254-seat", None),
    ("fa70f3765", None), ("e2c4b543e", None),
    ("r1053 splice window", None), ("r1053", None), ("r1054", None),
    ("r1050", None), ("r1052", None),
    ("f6433ee61", None), ("741371846", None),
    ("978,735", None), ("552,320", None), ("978_735", None), ("552_320", None),
    ("SEVENTY-THIRD", None), ("bmc_ordinal=73", None), ("73rd own wave", None),
    ("authored 17:4x", None), ("authored 13:2x", None),
    ("2026-10-16 18:4x bm-c r1054 freeze window", None),
    ("W253 finalize one-pass bm-c r1053 window closeout 14:4x", None),
    ("transitive window W241..W250 checked", None),
    ("engine_owner==bm-c rows 73 + candidate", None),
]
for needle, _ in p5a:
    print(f"  {tx.count(needle)}x  {needle!r}")

print("--- P5b plain reps (post-xf) ---")
p5b = [
    "# block's own W239..W251 legs (13 rows) do NOT enter the estate path;",
    "# block's own W239..W252 legs (14 rows) do NOT enter the estate path;",
    "# after extraction, fresh W239..W253 legs (14 rows) are added,",
    "# after extraction, fresh W239..W253 legs (15 rows) are added,",
    "# parity = 111 rows (W138..W206 + W211..W253). Zero assumption zero risk.",
    "# parity = 112 rows (W138..W206 + W211..W253). Zero assumption zero risk.",
    "# block's own W239..W251 legs (13) are EXCLUDED from the estate path per the",
    "# prereg mandate; the W254 block appends fresh W239..W253 legs (14,",
    "# machine-derived from the LIVE pf registry at freeze time) -> 111 parity",
    "!= 111 (69 estate + W211..W251 legs 41)",
    "!= 111 (69 estate + W211..W252 legs 42)",
    "legs segment not W211..W251 forty-one legs",
    "legs segment not W211..W252 forty-two legs",
    "dropped segment not W239..W251 thirteen legs",
    "dropped segment not W239..W252 fourteen legs",
    '"fresh_legs_row_asserts": 14,',
    '+ legs_kept.count("assert pf.N1_BANDS[") + 14,',
    '"    #     physical bytes; the W253 block\'s own W239..W251 legs (13) are",',
    '"    #     W239..W253 legs (14) added, machine-derived from the live pf",',
    '"    #     registry at freeze time -> 111 parity rows (W138..W206+W211..W253).",',
]
for needle in p5b:
    print(f"  {tx.count(needle)}x  {needle[:80]!r}")

print("--- P5c band literals (post-xf) ---")
p5c = [
    "assert (a_lo, a_hi) == (571_901, 573_900) and (b_lo, b_hi) == (573_901, 574_100), \\",
    "assert (a_lo, a_hi) == (574_101, 576_100) and (b_lo, b_hi) == (576_101, 576_300), \\",
]
for needle in p5c:
    print(f"  {tx.count(needle)}x  {needle[:70]!r}")

print("--- P5d faces (post-xf) ---")
p5d = [
    "assert len(owner_rows_live) == 242 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 72, \\",
    "(expect 242/129/72 PRE-splice post-W253 registration; this candidate = bm-c's 73rd own wave per the same live-derive law, r587/r359)",
    "# receipt leg0 face owner_rows=242 / bmc_rows=72 / bmc_ordinal=74",
    "-> owner rows 242 + candidate = 243rd EXACT; bm-c rows 72 +",
    "# candidate = 73rd EXACT -- bm-c own-seat continuity face (bm-c published the",
    "freeze-time live face owner rows 242 + candidate = 243rd EXACT",
    "freeze-time live derive bmc rows 72 + candidate 73rd EXACT per r587/r359",
    "post-W253 registration: bm-c rows 72 + candidate = 73rd owned",
    '"probe_receipt_bmc_ordinal_face": 73,',
    'f"W253+W248..W239 finalize products present "',
]
for needle in p5d:
    print(f"  {tx.count(needle)}x  {needle[:80]!r}")

print("--- P5e single-line reps (post-xf) ---")
p5e = [
    'assert w253_b_tail + 1 == a_lo, "A staircase-hop landing base relation (A base == registered prior-wave B tail+1 EXACT -- the 1-hop walk past the registered W253 B band; second consecutive A-hop of the staircase era; A_staircase_hop_past_W253_B=true)"',
    'assert a_lo >= w253_b_tail + 1, "A staircase landing floor relation (A base >= registered prior-wave B tail+1; the fourteen-wave seed-gap face ENDED at W253 -- second consecutive A-hop of the staircase era, A base == prior-B tail+1 EXACT this window per the prereg floor-relation mandate)"',
    'assert b_lo == a_hi + 1, "B base == own-A tail+1 EXACT (the 1-hop own-A reservation cascade lands ABOVE own-A -- third consecutive above-own-A; B_hop_lands_inside_A=false; B_lands_above_own_A=true)"',
    'W251_W253_bands_respected_A',
    'W251_W252_W253_bands_respected_A',
    '"W253 B 1-HOP own-A RESERVATION face: the naive continuation "',
    '"W253 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation landing)"',
    '"W253 A/B same-freeze mutual exclusion (B lands ABOVE own-A at tail+1 EXACT -- third consecutive above-own-A; zero overlap)"',
]
for needle in p5e:
    print(f"  {tx.count(needle)}x  {needle[:80]!r}")

print("--- narrative presence counters (post-xf, for chunk anchors) ---")
for needle in [
    "NEW FACE vs the W253 editor (honest disclosure, frozen W254 prereg sec.3",
    "# W254 FACE (probe receipt leg1 relation_asserts):",
    "wave 254: ",
    "a_seed_base\": {a_lo},        # law sec.4 W254 A:",
    "b_exit_seed_base\": {b_lo},   # law sec.4 W254 B:",
    "band facts (law sec.4 W254 row): A = 1-HOP STAIRCASE-AFFECTS-A",
    "W255p face per this window's probe leg4 (pre-W254 universe):",
    "SECOND consecutive A-hop",
    "THIRD consecutive above-own-A",
    "second consecutive A-hop of the staircase era",
    "third consecutive above-own-A landing",
    "W255p_A_naive",
    "W254p_A_naive",
]:
    print(f"  {tx.count(needle)}x  {needle[:70]!r}")

print("--- prereg authored-window face ---")
pr = io.open(os.path.join(REPO, "research", "PERPETUAL_N1_W254_PREREG.md"), encoding="utf-8").read()
for pat in ["r1054", "authored", "17:4x", "18:0", "freeze 窗"]:
    hits = [m.start() for m in re.finditer(re.escape(pat), pr)]
    print(f"  prereg {pat!r}: {len(hits)}x")
m = re.search(r"authored[^。；\n]{0,80}", pr)
print("  prereg authored ctx:", m.group(0)[:100] if m else "NONE")
