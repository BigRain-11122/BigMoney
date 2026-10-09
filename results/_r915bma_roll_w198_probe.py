# -*- coding: utf-8 -*-
# r915 bm-a: roll _r915bma_w198_probe.py from _r914bma_w197_probe.py (one-generation
# bloodline roll; anchor-cut replacements, zero old-text transcription; count asserts).
import io, sys

SRC = 'results/_r914bma_w197_probe.py'
DST = 'results/_r915bma_w198_probe.py'
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
rep('r914 bm-a W197 pre-seat probe -- read-only band derivation',
    'r915 bm-a W198 pre-seat probe -- read-only band derivation')
cut('W197 candidate = first FREE number after the REGISTERED W196 row (bm-a r911',
    'zero roll-forward this window).',
    '''W198 candidate = first FREE number after the REGISTERED W197 row (bm-a r915
dead-session five-face freeze 13:0x + estate-absorbed same round; burn COMPLETE
12/12 engine self-burned 13:01..13:12 while the first-attempt r915 session
died 13:13 pre-closeout (dead-estate absorbed per r899 law); finalize LANDED
r915 session one-pass origin 522a0aef5-lineage -- ledger 845,545+2,200=847,745
EXACT zero-deviation fourth consecutive window, K=429,120+2,200=431,320 EXACT,
four pred keys PASS; W198 freeze-time anchor = W197 finalize actuals per
r590, zero roll-forward this window).''')
cut('Derivation faces (STAIRCASE GEOMETRY FIFTY-SEVENTH',
    'transcribed):',
    '''Derivation faces (STAIRCASE GEOMETRY FIFTY-EIGHTH instance expected per
the W197 prereg sec5.5 leg4 projection + the W197 prereg sec8 succession
note; W141 leg2 law + E36 card; the mandatory post-W197 re-derive -- reserve
own-wave A when deriving B is MANDATORY, this probe IS that re-derive; naive
pre-W197-universe continuation is REFUSED here on the live universe, never
transcribed):''')
cut('  A  arithmetic continuation from the registered W196 A tail',
    'live-registry-driven."""',
    '''  A  arithmetic continuation from the registered W197 A tail (live-registry
     read) -- expected REFUSED at its own start by the registered W197 B band
     450_204..450_403 (staircase A-hops-prior-B 58th); honest forward walk ->
     first-clean, hops counted.
  B  arithmetic continuation from the registered W197 B tail -- naive lands
     INSIDE the W198 own-wave A window (same-freeze mutual exclusion, W141
     precedent, leg2 law) -> reserved walk past own-A -> first-clean.
Bloodline: r910/r914 derive machinery verbatim, W198 facts
live-registry-driven."""''')
rep('receipt = {"probe": "r914 W197 pre-seat probe", "legs": {}}',
    'receipt = {"probe": "r915 W198 pre-seat probe", "legs": {}}')

# 2. leg0 block wholesale
cut('# --- leg 0: registry shape (single state: W196 registered, tail=W196) ----------',
    '(finalize LANDED, chain clean)")',
    '''# --- leg 0: registry shape (single state: W197 registered, tail=W197) ----------
keys = sorted(N1_BANDS)
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 198))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
W197_A = tuple(N1_BANDS[197]["a"])
W197_B = tuple(N1_BANDS[197]["b_exit"])
assert W197_A == (448_204, 450_203) and W197_B == (450_204, 450_403) and \\
    N1_BANDS[197].get("engine_owner") == "bm-a", "leg0 failed: W197 row drift"
assert tuple(N1_BANDS[196]["a"]) == (446_004, 448_003) and \\
    tuple(N1_BANDS[196]["b_exit"]) == (448_004, 448_203) and \\
    N1_BANDS[196].get("engine_owner") == "bm-a", "leg0 W196 row drift"
owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
assert len(owner_rows) == 187 and len(bma_rows) == 112, "leg0 ordinal drift"

# W197 finalize product machine-read (r587 never-transcribe face; W197
# finalize LANDED r915 one-pass on origin (522a0aef5 rebased lineage);
# cross-file prev==total chain assert; W198 freeze-time anchor = W197
# finalize actuals per r590, zero roll-forward)
w197_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w197_results.json"), encoding="utf-8"))
led = (w197_out.get("science_gates") or {}).get("ledger") or {}
assert led.get("total") == 847_745 and led.get("prev_total") == 845_545, \\
    f"leg0 failed: W197 ledger machine-read drift {led}"
w196_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces",
                                       "n1_w196_results.json"), encoding="utf-8"))
led196 = (w196_out.get("science_gates") or {}).get("ledger") or {}
assert led196.get("total") == 845_545 and led.get("prev_total") == led196.get("total"), \\
    "leg0 failed: chain-head prev != W196 total (cross-file drift)"
r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--",
                    "results/perpetual_faces/"], cwd=ROOT, capture_output=True)
onr = r.stdout.decode("utf-8", errors="replace").splitlines()
assert "results/perpetual_faces/n1_w197_results.json" in onr, \\
    "leg0 failed: W197 finalize product absent on origin"
receipt["legs"]["leg0"] = {"rows": len(N1_BANDS), "tail": "W197",
                           "owner_rows": len(owner_rows), "bma_rows": len(bma_rows),
                           "ordinal": 188, "bma_ordinal": 113,
                           "w197_ledger_head": led.get("total"),
                           "w196_status": ("registered bm-a r911 five-face freeze; burn COMPLETE "
                                           "12/12 engine self-burned 11:07..11:17 (r912 died "
                                           "pre-finalize, estate absorbed r913 per r899 law); "
                                           "finalize LANDED r913 session one-pass (ledger 845,545 "
                                           "EXACT, K=429,120 EXACT)"),
                           "w197_status": ("registered bm-a r915 dead-session five-face freeze "
                                           "13:0x + engine self-burn 12/12 13:01..13:12 (first-"
                                           "attempt session died 13:13 pre-closeout; dead-estate "
                                           "absorbed same-round r915 per r899 law); finalize LANDED "
                                           "r915 session one-pass origin 522a0aef5 (ledger 847,745 "
                                           "EXACT zero-deviation vs sec5 frozen projection fourth "
                                           "consecutive window, K=431,320 EXACT, four pred keys "
                                           "PASS) -- chain head FULLY CLEAN fourth consecutive "
                                           "window; W198 freeze-time anchor = W197 finalize actuals "
                                           "per r590, zero roll-forward")}
print(f"leg0: {len(N1_BANDS)} rows tail=W197, owner={len(owner_rows)} -> 188th wave, bm-a 113th owned, anchor W197 ledger head {led.get('total')} (finalize LANDED, chain clean)")''')

# 3. leg1 variable/prefix renames
rep('ARITH_A = (W196_A[1] + 1, W196_A[1] + WIDTH_A)',
    'ARITH_A = (W197_A[1] + 1, W197_A[1] + WIDTH_A)')
rep('ARITH_B = (W196_B[1] + 1, W196_B[1] + WIDTH_B)',
    'ARITH_B = (W197_B[1] + 1, W197_B[1] + WIDTH_B)')
rep('assert fc_a[0] == W196_B[1] + 1, "leg1 staircase A base != prior-B tail+1"',
    'assert fc_a[0] == W197_B[1] + 1, "leg1 staircase A base != prior-B tail+1"')
rep('''assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase expected per W196 prereg "
                               "sec5.5 leg4 projection + W196 seat MSG succession note "
                               "(W196-B-refuses-W197-A staircase anticipated, E36 card))")''',
    '''assert fc_a[0] > ARITH_A[0], ("leg1 A not refused (staircase expected per W197 prereg "
                               "sec5.5 leg4 projection + W197 prereg sec8 succession note "
                               "(W197-B-refuses-W198-A staircase anticipated, E36 card))")''')
rep('''"A_semantics": ("A arithmetic continuation REFUSED at start by registered W196 B band "
                    "448_004..448_203 (staircase A-hops-prior-B FIFTY-SEVENTH instance, E36 card; "
                    "W196 prereg sec5.5 leg4 + W196 seat MSG succession note both fulfilled); "
                    "honest forward walk, non-rotational r587"),''',
    '''"A_semantics": ("A arithmetic continuation REFUSED at start by registered W197 B band "
                    "450_204..450_403 (staircase A-hops-prior-B FIFTY-EIGHTH instance, E36 card; "
                    "W197 prereg sec5.5 leg4 + W197 prereg sec8 succession note both fulfilled); "
                    "honest forward walk, non-rotational r587"),''')

# 4. leg2 tags
rep('W197-{tag}', 'W198-{tag}', 6)
rep('f"leg2 failed: W197 conflicts {conflicts}"', 'f"leg2 failed: W198 conflicts {conflicts}"')

# 5. leg3 vacancy
rep('if "w197" in ln.lower() and "seat" in ln.lower()',
    'if "w198" in ln.lower() and "seat" in ln.lower()')
rep('f"leg3 failed: W197 seats already exist: {seats}"',
    'f"leg3 failed: W198 seats already exist: {seats}"')
rep("assert '197: {\"a\": (' not in out, \"leg3 failed: W197 row ALREADY on origin (r511 tail-lock)\"",
    "assert '198: {\"a\": (' not in out, \"leg3 failed: W198 row ALREADY on origin (r511 tail-lock)\"")
rep('\'"batch": "PERPETUAL-N1-W197"\' not in outn1, "leg3 failed: W197 WAVE_CONFIGS ALREADY on origin"',
    '\'"batch": "PERPETUAL-N1-W198"\' not in outn1, "leg3 failed: W198 WAVE_CONFIGS ALREADY on origin"')
rep('PERPETUAL_N1_W197_PREREG.md"], cwd=ROOT,',
    'PERPETUAL_N1_W198_PREREG.md"], cwd=ROOT,')
rep('assert not outpre, "leg3 failed: W197 per-wave prereg ALREADY on origin"',
    'assert not outpre, "leg3 failed: W198 per-wave prereg ALREADY on origin"')

# 6. leg4 projection
rep('(fc198_a, h197a) = first_clean(fc_a[1] + 1, WIDTH_A)',
    '(fc199_a, h198a) = first_clean(fc_a[1] + 1, WIDTH_A)')
rep('(fc198_b, h197b) = first_clean(fc_b[1] + 1, WIDTH_B)',
    '(fc199_b, h198b) = first_clean(fc_b[1] + 1, WIDTH_B)')
rep('inside197 = overlaps(fc198_b, fc198_a)', 'inside198 = overlaps(fc199_b, fc199_a)')
rep('''receipt["legs"]["leg4"] = {"W198p_A": f"{fc198_a[0]}..{fc198_a[1]}", "hops_A": h197a,
                           "W198p_B": f"{fc198_b[0]}..{fc198_b[1]}", "hops_B": h197b,
                           "W198p_B_lands_inside_W198p_A": inside197,
                           "note": ("W198+ naive projection on pre-W197 universe; "
                                    "the registered W197 B band will refuse the naive W198 A "
                                    "window once W197 is registered (W197-B-refuses-W198-A "
                                    "staircase anticipated, E36 card); W198 freezer MUST "
                                    "re-derive on the post-W197 universe AND reserve own-wave A "
                                    "when deriving B (W141 precedent, leg2 law, E36 staircase card) "
                                    "-- never transcribe r587)")}''',
    '''receipt["legs"]["leg4"] = {"W199p_A": f"{fc199_a[0]}..{fc199_a[1]}", "hops_A": h198a,
                           "W199p_B": f"{fc199_b[0]}..{fc199_b[1]}", "hops_B": h198b,
                           "W199p_B_lands_inside_W199p_A": inside198,
                           "note": ("W199+ naive projection on pre-W198 universe; "
                                    "the registered W198 B band will refuse the naive W199 A "
                                    "window once W198 is registered (W198-B-refuses-W199-A "
                                    "staircase anticipated, E36 card); W199 freezer MUST "
                                    "re-derive on the post-W198 universe AND reserve own-wave A "
                                    "when deriving B (W141 precedent, leg2 law, E36 staircase card) "
                                    "-- never transcribe r587)")}''')
rep('print(f"leg4: W198+ projection A {fc198_a[0]}..{fc198_a[1]} hops={h197a} / B {fc198_b[0]}..{fc198_b[1]} hops={h197b} (B inside A: {inside197})")',
    'print(f"leg4: W199+ projection A {fc199_a[0]}..{fc199_a[1]} hops={h198a} / B {fc199_b[0]}..{fc199_b[1]} hops={h198b} (B inside A: {inside198})")')

# 7. receipt path + final print
rep('"results",\n                                     "_r914bma_w197_probe_receipt.json"), "w",',
    '"results",\n                                     "_r915bma_w198_probe_receipt.json"), "w",')
rep('print(f"W197 PRE-SEAT PROBE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (staircase geometry held; receipt written)")',
    'print(f"W198 PRE-SEAT PROBE rc0 ADMIT: A {fc_a[0]}..{fc_a[1]} + B {fc_b[0]}..{fc_b[1]} (staircase geometry held; receipt written)")')

io.open(DST, 'w', encoding='utf-8', newline='').write(src)
print('rolled OK ->', DST, len(src), 'bytes')
