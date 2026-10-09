# -*- coding: utf-8 -*-
# r918 bm-a: roll _r918bma_w199_probe.py from _r915bma_w198_probe.py (one-generation
# bloodline roll; anchor-cut replacements, zero old-text transcription; count asserts).
import io, sys

SRC = 'results/_r915bma_w198_probe.py'
DST = 'results/_r918bma_w199_probe.py'
src = io.open(SRC, encoding='utf-8').read()

def cut(start_anchor, end_anchor, new_text):
    global src
    i = src.index(start_anchor)
    j = src.index(end_anchor, i) + len(end_anchor)
    src = src[:i] + new_text + src[j:]

def rep(old, new, n=1):
    global src
    assert src.count(old) == n, ('count mismatch', old[:60], src.count(old))
    src = src.replace(old, new)

# 1. docstring header
rep('r915 bm-a W198 pre-seat probe -- read-only band derivation',
    'r918 bm-a W199 pre-seat probe -- read-only band derivation')
cut('W198 candidate = first FREE number after the REGISTERED W197 row (bm-a r915',
    'zero roll-forward this window).',
    '''W199 candidate = first FREE number after the REGISTERED W198 row (bm-a r916
five-face freeze 14:0x + engine self-burn 12/12 14:11..; finalize LANDED
r917 session one-pass origin d4ea4b348 closeout lineage -- ledger 847,745+2,200
=849,945 EXACT five-window consecutive zero-deviation streak, K=433,520 EXACT,
four pred keys 4/4 PASS; W199 freeze-time anchor = W198 finalize actuals per
r590, zero roll-forward this window).''')
cut('Derivation faces (STAIRCASE GEOMETRY FIFTY-EIGHTH',
    'transcribed):',
    '''Derivation faces (STAIRCASE GEOMETRY FIFTY-NINTH instance expected per
the W198 prereg sec5.5 leg4 projection + the W198 prereg sec8 succession
note; W141 leg2 law + E36 card; the mandatory post-W198 re-derive -- reserve
own-wave A when deriving B is MANDATORY, this probe IS that re-derive; naive
pre-W198-universe continuation is REFUSED here on the live universe, never
transcribed):''')
cut('  A  arithmetic continuation from the registered W197 A tail',
    'live-registry-driven."""',
    '''  A  arithmetic continuation from the registered W198 A tail (live-registry
     read) -- expected REFUSED at its own start by the registered W198 B band
     452_404..452_603 (staircase A-hops-prior-B 59th); honest forward walk ->
     first-clean, hops counted.
  B  arithmetic continuation from the registered W198 B tail -- naive lands
     INSIDE the W199 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean.
Bloodline: r910/r914/r915 derive machinery verbatim, W199 facts
live-registry-driven."""''')
rep('receipt = {"probe": "r915 W198 pre-seat probe", "legs": {}}',
    'receipt = {"probe": "r918 W199 pre-seat probe", "legs": {}}')

# 2. leg0 block wholesale
cut('# --- leg 0: registry shape (single state: W197 registered, tail=W197) ----------',
    '(finalize LANDED, chain clean)")',
    '''# --- leg 0: registry shape (single state: W198 registered, tail=W198) ----------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 199))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W198_A = tuple(N1_BANDS[198]["a"])
W198_B = tuple(N1_BANDS[198]["b_exit"])
assert W198_A == (450_404, 452_403) and W198_B == (452_404, 452_603) and \\
    N1_BANDS[198].get("engine_owner") == "bm-a", "leg0 failed: W198 row drift"
assert tuple(N1_BANDS[197]["a"]) == (448_204, 450_203) and \\
    tuple(N1_BANDS[197]["b_exit"]) == (450_204, 450_403) and \\
    N1_BANDS[197].get("engine_owner") == "bm-a", "leg0 W197 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 188 and len(bma_rows) == 113, "leg0 ordinal drift"

# W198 finalize product machine-read (r587 never-transcribe face; W198
# finalize LANDED r917 one-pass on origin (d4ea4b348 closeout lineage);
# cross-file prev==total chain assert; W199 freeze-time anchor = W198
# finalize actuals per r590, zero roll-forward)
w198_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w198_results.json"), encoding="utf-8"))
led = (w198_out.get("science_gates") or {}).get("ledger") or {}
assert led.get("total") == 849_945 and led.get("prev_total") == 847_745, \\
    f"leg0 failed: W198 ledger machine-read drift {led}"
w197_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w197_results.json"), encoding="utf-8"))
led197 = (w197_out.get("science_gates") or {}).get("ledger") or {}
assert led197.get("total") == 847_745 and led.get("prev_total") == led197.get("total"), \\
    "leg0 failed: chain-head prev != W197 total (cross-file drift)"
r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--",
                    "results/perpetual_faces/"], cwd=ROOT, capture_output=True)
onr = r.stdout.decode("utf-8", errors="replace").splitlines()
assert "results/perpetual_faces/n1_w198_results.json" in onr, \\
    "leg0 failed: W198 finalize product absent on origin"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W198",
                           "owner_rows": len(owner_rows), "bma_rows": len(bma_rows),
                           "ordinal": 189, "bma_ordinal": 114,
                           "w198_ledger_head": led.get("total"),
                           "w197_status": ("registered bm-a r915 dead-session five-face freeze "
                                           "13:0x + engine self-burn 12/12 13:01..13:12 (first-"
                                           "attempt session died 13:13 pre-closeout; dead-estate "
                                           "absorbed same-round per r899 law); finalize LANDED "
                                           "r915 session one-pass (ledger 847,745 EXACT "
                                           "zero-deviation vs sec5 frozen projection fourth "
                                           "consecutive window, K=431,320 EXACT, four pred keys "
                                           "PASS)"),
                           "w198_status": ("registered bm-a r916 five-face freeze 14:0x + engine "
                                           "self-burn 12/12 14:11.. (r916 session landed prereg+"
                                           "freeze same window); finalize LANDED r917 session "
                                           "one-pass origin d4ea4b348 (ledger 847,745+2,200="
                                           "849,945 EXACT zero-deviation vs sec5 frozen "
                                           "projection five-window consecutive streak, K=433,520 "
                                           "EXACT, four pred keys 4/4 PASS) -- chain head FULLY "
                                           "CLEAN five-window consecutive streak; W199 freeze-time "
                                           "anchor = W198 finalize actuals per r590, zero "
                                           "roll-forward")}
print(f"leg0: {len(N1_BANDS)} rows tail=W198, owner={len(owner_rows)} -> 189th wave, bm-a 114th owned, anchor W198 ledger head {led.get('total')} (finalize LANDED, chain clean)")''')

# 3. leg1 variable/prefix renames
rep('# --- leg 1: honest forward walk from the live-registry W196 tails -------------',
    '# --- leg 1: honest forward walk from the live-registry W198 tails -------------')
rep('ARITH_A = (W197_A[1] + 1, W197_A[1] + WIDTH_A)',
    'ARITH_A = (W198_A[1] + 1, W198_A[1] + WIDTH_A)')
rep('ARITH_B = (W197_B[1] + 1, W197_B[1] + WIDTH_B)',
    'ARITH_B = (W198_B[1] + 1, W198_B[1] + WIDTH_B)')
rep('assert fc_a[0] == W197_B[1] + 1, "leg1 staircase A base != prior-B tail+1"',
    'assert fc_a[0] == W198_B[1] + 1, "leg1 staircase A base != prior-B tail+1"')
rep('''assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase expected per W197 prereg "
                               "sec5.5 leg4 projection + W197 prereg sec8 succession note "
                               "(W197-B-refuses-W198-A staircase anticipated, E36 card))")''',
    '''assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase expected per W198 prereg "
                               "sec5.5 leg4 projection + W198 prereg sec8 succession note "
                               "(W198-B-refuses-W199-A staircase anticipated, E36 card))")''')
rep('''"A_semantics": ("A arithmetic continuation REFUSED at start by registered W197 B band "
                    "450_204..450_403 (staircase A-hops-prior-B FIFTY-EIGHTH instance, E36 card; "
                    "W197 prereg sec5.5 leg4 + W197 prereg sec8 succession note both fulfilled); "
                    "honest forward walk, non-rotational r587"),''',
    '''"A_semantics": ("A arithmetic continuation REFUSED at start by registered W198 B band "
                    "452_404..452_603 (staircase A-hops-prior-B FIFTY-NINTH instance, E36 card; "
                    "W198 prereg sec5.5 leg4 + W198 prereg sec8 succession note both fulfilled); "
                    "honest forward walk, non-rotational r587"),''')

# 4. leg2 tags
rep('W198-{tag}', 'W199-{tag}', 6)
rep('f"leg2 failed: W198 conflicts {conflicts}"', 'f"leg2 failed: W199 conflicts {conflicts}"')

# 5. leg3 vacancy
rep('if "w198" in ln.lower() and "seat" in ln.lower()',
    'if "w199" in ln.lower() and "seat" in ln.lower()')
rep('f"leg3 failed: W198 seats already exist: {seats}"',
    'f"leg3 failed: W199 seats already exist: {seats}"')
rep("assert '198: {\"a\": (' not in out, \"leg3 failed: W198 row ALREADY on origin (r511 tail-lock)\"",
    "assert '199: {\"a\": (' not in out, \"leg3 failed: W199 row ALREADY on origin (r511 tail-lock)\"")
rep('\'"batch": "PERPETUAL-N1-W198"\' not in outn1, "leg3 failed: W198 WAVE_CONFIGS ALREADY on origin"',
    '\'"batch": "PERPETUAL-N1-W199"\' not in outn1, "leg3 failed: W199 WAVE_CONFIGS ALREADY on origin"')
rep('PERPETUAL_N1_W198_PREREG.md"], cwd=ROOT,',
    'PERPETUAL_N1_W199_PREREG.md"], cwd=ROOT,')
rep('assert not outpre, "leg3 failed: W198 per-wave prereg ALREADY on origin"',
    'assert not outpre, "leg3 failed: W199 per-wave prereg ALREADY on origin"')

# 6. leg4 projection
rep('(fc199_a, h198a) = first_clean(fc_a[1] + 1, WIDTH_A)',
    '(fc200_a, h199a) = first_clean(fc_a[1] + 1, WIDTH_A)')
rep('(fc199_b, h198b) = first_clean(fc_b[1] + 1, WIDTH_B)',
    '(fc200_b, h199b) = first_clean(fc_b[1] + 1, WIDTH_B)')
rep('inside198 = overlaps(fc199_b, fc199_a)', 'inside199 = overlaps(fc200_b, fc200_a)')
rep('''receipt["legs"]["leg4"] = {"W199p_A": f"{fc199_a[0]}..{fc199_a[1]}", "hops_A": h198a,
                           "W199p_B": f"{fc199_b[0]}..{fc199_b[1]}", "hops_B": h198b,
                           "W199p_B_lands_inside_W199p_A": inside198,
                           "note": ("W199+ naive projection on pre-W198 universe; "
                                    "the registered W198 B band will refuse the naive W199 A "
                                    "window once W198 is registered (W198-B-refuses-W199-A "
                                    "staircase anticipated, E36 card); W199 freezer MUST "
                                    "re-derive on the post-W198 universe AND reserve own-wave A "
                                    "when deriving B (W141 precedent, leg2 law, E36 staircase card) "
                                    "-- never transcribe r587)")}''',
    '''receipt["legs"]["leg4"] = {"W200p_A": f"{fc200_a[0]}..{fc200_a[1]}", "hops_A": h199a,
                           "W200p_B": f"{fc200_b[0]}..{fc200_b[1]}", "hops_B": h199b,
                           "W200p_B_lands_inside_W200p_A": inside199,
                           "note": ("W200+ naive projection on pre-W199 universe; "
                                    "the registered W199 B band will refuse the naive W200 A "
                                    "window once W199 is registered (W199-B-refuses-W200-A "
                                    "staircase anticipated, E36 card); W200 freezer MUST "
                                    "re-derive on the post-W199 universe AND reserve own-wave A "
                                    "when deriving B (W141 precedent, leg2 law, E36 staircase card) "
                                    "-- never transcribe r587)")}''')
rep('print(f"leg4: W199+ projection A {fc199_a[0]}..{fc199_a[1]} hops={h198a} / B {fc199_b[0]}..{fc199_b[1]} hops={h198b} (B inside A: {inside198})")',
    'print(f"leg4: W200+ projection A {fc200_a[0]}..{fc200_a[1]} hops={h199a} / B {fc200_b[0]}..{fc200_b[1]} hops={h199b} (B inside A: {inside199})")')

# 7. receipt path + final print
rep('"results",\n                                     "_r915bma_w198_probe_receipt.json"), "w",',
    '"results",\n                                     "_r918bma_w199_probe_receipt.json"), "w",')
rep('print(f"W198 PRE-SEAT PROBE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (staircase geometry held; receipt written)")',
    'print(f"W199 PRE-SEAT PROBE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (staircase geometry held; receipt written)")')

io.open(DST, 'w', encoding='utf-8', newline='').write(src)
print('rolled OK ->', DST, len(src), 'bytes')
