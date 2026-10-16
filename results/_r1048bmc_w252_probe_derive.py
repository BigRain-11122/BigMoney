# -*- coding: utf-8 -*-
# r1048 bm-c: derive W252 pre-seat probe from committed W251 probe
# (_w251bmc_20261016_probe.py, origin-landed in r1046 closeout bc3b2b693)
# via count-asserted ordered transform. E63 canon-clone: zero hand-walk,
# walk machinery verbatim (universe-driven via live N1_BANDS), only
# anchors/labels/assert-faces roll 251->252.
import io
import py_compile

SRC = "results/_w251bmc_20261016_probe.py"
DST = "results/_w252bmc_20261016_probe.py"
t = io.open(SRC, encoding="utf-8").read()
fails = []


def leg(needle, repl, expect):
    n = t.count(needle)
    if n != expect:
        fails.append(f"{n}!={expect} :: {needle[:70]!r}")
        return
    t_new = t.replace(needle, repl)
    globals()['t'] = t_new


L = leg
# ---- docstring block: upstream chain face + universe + anticipated face -------
L('''"""W251 pre-seat probe (bm-c loop window r1046, 2026-10-16 08:5x; queue-head
supply lane: upstream W250 = bm-c OWN registered+FINALIZED complete chain
(seat r1043 window origin cc06f1f4a -> prereg r1045 LANDED 4f7a130ff ->
r1046 dead-window five-face splice 29930f489 (incl disclosed print-face heal
rows 68->69) -> engine self-burn 12/12 (ledger appends 486458150+77a4f529a
batched 6+6) -> r1046 continuation finalize: ledger 974,335 EXACT
(972,135+2,200) / merged pool K=547,920 (545,720+2,200) / fivekeys ALL PASS
results/_r1046bmc_w250_fivekeys.json / sixgate ALL PASS
results/_r1046bmc_w250_sixgate.json PRE-FINALIZE phase, gate-1 anchored to
landed git blob n1 22a957f851fd3adc / pf 40b0befe37ebbe2c)
-- NO in-flight seat upstream: the W251 FREEZE is UNBLOCKED at seat time (no
waits-upstream face; the W251 freezer proceeds prereg derive + five-face splice
on the post-W250-REGISTERED universe per seat-first law O-20261010-2350-bm-c
sec.2, prereg derive = next window FIRST ACTION).''',
   '''"""W252 pre-seat probe (bm-c loop window r1048, 2026-10-16 10:xx; queue-head
supply lane: upstream W251 = bm-c OWN registered+FINALIZED complete chain
(seat r1046 window origin bc3b2b693 -> prereg r1047 LANDED 9f5f106d6 ->
r1048 dead-window five-face splice c813471cd (zero post-splice heal) ->
engine self-burn 12/12 (ledger appends c15c32afd+e46094052 batched 6+6
self-commit) -> r1048 continuation finalize: ledger 976,535 EXACT
(974,135+2,200) / merged pool K=550,120 (547,920+2,200) / fivekeys ALL PASS
results/_r1048bmc_w251_fivekeys.json / sixgate ALL PASS
results/_r1048bmc_w251_sixgate.json PRE-FINALIZE phase, gate-1 triple identity
worktree==receipt==landed git blob n1 c9de218d7c362499 / pf d88cd951f44dfaf6)
-- NO in-flight seat upstream: the W252 FREEZE is UNBLOCKED at seat time (no
waits-upstream face; the W252 freezer proceeds prereg derive + five-face splice
on the post-W251-REGISTERED universe per seat-first law O-20261010-2350-bm-c
sec.2, prereg derive = next window FIRST ACTION).''', 1)
L('''Universe face = post-W250-REGISTERED (live registry, 240 owner rows:
bm-a 129 / bm-b 41 / bm-c 70 incl W250; W251 candidate = 241st wave,
bm-c 71st owned).
Anticipated face (W250 prereg sec.5 item5 + W250 probe leg4, honest forward
face): naive W251 A continuation 567_501..569_500 first-clean hops=0 (no live
refusers) / naive B 545_301..545_500 REFUSED at start (SEED_REGISTRY seed
545_500 + W240..W249 A-ladder refusal face) -- the pre-W250 projected B
first-clean 565_501..565_700 is now INSIDE the registered W250 A band
565_501..567_500 = the post-W250 walk must hop past it AND past the own-wave
A window; live re-derive governs either way, non-rotational r587
forward-monotone enforced in-walk; never transcribe r587.
Bloodline: _w250bmc_20261016_probe.py derive machinery verbatim, W251 facts
live-registry-driven; leg0 extended with the W249->W250 chain-relation
anchors leg (+2,200/+2,200) and the no-skip-claim leg (W252/W253 inbox
vacancy -- seat numbering stays dense)."""''',
   '''Universe face = post-W251-REGISTERED (live registry, 241 owner rows:
bm-a 129 / bm-b 41 / bm-c 71 incl W251; W252 candidate = 242nd wave,
bm-c 72nd owned).
Anticipated face (W251 prereg sec.5 item5 + W251 probe leg4, honest forward
face): naive W252 A continuation 569_501..571_500 first-clean hops=0 (no live
refusers) / naive B 569_701..569_900 CLEAN at naive start BUT lands INSIDE
the own-wave W252 A window 569_501..571_500 (staircase re-emergence face:
W251 B 569_501..569_700 registered INSIDE the W251 A 2,000-span ladder
region) -- the post-W251 walk must hop past the own-wave A tail 571_500 ->
~571_501..571_700 staircase face re-emerges; live re-derive governs either
way, non-rotational r587 forward-monotone enforced in-walk; never transcribe
r587; W252 freezer MUST reserve own-A + own-B when deriving.
Bloodline: _w251bmc_20261016_probe.py derive machinery verbatim, W252 facts
live-registry-driven; leg0 extended with the W250->W251 chain-relation
anchors leg (+2,200/+2,200) and the no-skip-claim leg (W253/W254 inbox
vacancy -- seat numbering stays dense)."""''', 1)
# ---- receipt probe face -------------------------------------------------------
L('''receipt = {"probe": "W251 pre-seat probe (bm-c loop r1046 window, 2026-10-16 08:5x, queue-head supply lane: upstream W250 = bm-c OWN registered+FINALIZED complete chain (r1046 continuation finalize ledger 974,335 / K=547,920); NO in-flight seat upstream -- W251 FREEZE UNBLOCKED at seat time; seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + CEO fill-order standing + O-20261015-0025 full mobilization; universe = post-W250-REGISTERED 240 owner rows)", "legs": {}}''',
   '''receipt = {"probe": "W252 pre-seat probe (bm-c loop r1048 window, 2026-10-16 10:xx, queue-head supply lane: upstream W251 = bm-c OWN registered+FINALIZED complete chain (r1048 continuation finalize ledger 976,535 / K=550,120); NO in-flight seat upstream -- W252 FREEZE UNBLOCKED at seat time; seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + CEO fill-order standing + O-20261015-0025 full mobilization; universe = post-W251-REGISTERED 241 owner rows)", "legs": {}}''', 1)
# ---- leg0: registry shape + rows + finalize anchors ---------------------------
L('# --- leg 0: registry shape + W247..W250 landed faces + chain-relation anchors ---',
  '# --- leg 0: registry shape + W248..W251 landed faces + chain-relation anchors ---', 1)
L('w250_splice_landed = 250 in N1_BANDS\nassert w250_splice_landed, "leg0 failed: W250 splice not landed (registry row absent -- r1046 splice face broken)"',
  'w251_splice_landed = 251 in N1_BANDS\nassert w251_splice_landed, "leg0 failed: W251 splice not landed (registry row absent -- r1048 splice face broken)"', 1)
L('base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 251))',
  'base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 252))', 1)
L('assert 251 not in N1_BANDS, "leg0 failed: W251 ALREADY registered locally (upstream freeze landed mid-probe -- re-derive on the post-W251 universe honestly, do not seat on a stale universe)"',
  'assert 252 not in N1_BANDS, "leg0 failed: W252 ALREADY registered locally (upstream freeze landed mid-probe -- re-derive on the post-W252 universe honestly, do not seat on a stale universe)"', 1)
# keep W247..W250 row blocks verbatim; add W251 row block + roll relations
L('''assert W250_A[0] == W249_A[1] + 1, \\
    "leg0 failed: W250 A base != W249 A tail+1 (seed-gap A-continuation face drift)"
assert W250_B[0] == W249_B[1] + 1, \\
    "leg0 failed: W250 B base != W249 B tail+1 (clean arithmetic continuation face drift)"''',
   '''assert W250_A[0] == W249_A[1] + 1, \\
    "leg0 failed: W250 A base != W249 A tail+1 (seed-gap A-continuation face drift)"
assert W250_B[0] == W249_B[1] + 1, \\
    "leg0 failed: W250 B base != W249 B tail+1 (clean arithmetic continuation face drift)"

W251_A = tuple(N1_BANDS[251]["a"])
W251_B = tuple(N1_BANDS[251]["b_exit"])
assert W251_A == (567_501, 569_500) and W251_B == (569_501, 569_700) and \\
    N1_BANDS[251].get("engine_owner") == "bm-c", "leg0 failed: W251 registry row drift (bm-c r1048 splice face)"
assert W251_A[0] == W250_A[1] + 1, \\
    "leg0 failed: W251 A base != W250 A tail+1 (seed-gap A-continuation face drift)"
assert W251_B[0] == W251_A[1] + 1, \\
    "leg0 failed: W251 B base != W251 A tail+1 (above-own-A staircase face drift -- W251 13-hop walk landed base==own-A tail+1 EXACT)"''', 1)
L('for _w in (248, 249, 250):', 'for _w in (249, 250, 251):', 1)
L('''w250_results = os.path.join(ROOT, "results", "perpetual_faces", "n1_w250_results.json")
w250_out = json.load(open(w250_results, encoding="utf-8"))
w250_led = (w250_out.get("science_gates") or {}).get("ledger") or {}
w250_total = w250_led.get("total")
w250_merged_n = None''',
   '''w250_results = os.path.join(ROOT, "results", "perpetual_faces", "n1_w250_results.json")
w250_out = json.load(open(w250_results, encoding="utf-8"))
w250_led = (w250_out.get("science_gates") or {}).get("ledger") or {}
w250_total = w250_led.get("total")
w250_merged_n = None''', 1)  # anchor kept; W250 block reused as the chain tail-1 face
L('''assert w250_total == 974_335 and w250_merged_n == 547_920, \\
    f"leg0 failed: W250 finalize anchors drift: total={w250_total} merged={w250_merged_n} (expect 974,335 / 547,920)"
assert w250_total == w249_total + 2_200 and w250_merged_n == w249_merged_n + 2_200, \\
    "leg0 failed: W249->W250 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"
assert w250_klift is not None and abs(w250_klift) <= 0.02, \\
    f"leg0 failed: W250 K-lift out-of-band at seat time: {w250_klift} (expect |delta|<=0.02 per the frozen prereg key-4 band)"''',
   '''assert w250_total == 974_335 and w250_merged_n == 547_920, \\
    f"leg0 failed: W250 finalize anchors drift: total={w250_total} merged={w250_merged_n} (expect 974,335 / 547,920)"

w251_results = os.path.join(ROOT, "results", "perpetual_faces", "n1_w251_results.json")
w251_out = json.load(open(w251_results, encoding="utf-8"))
w251_led = (w251_out.get("science_gates") or {}).get("ledger") or {}
w251_total = w251_led.get("total")
w251_merged_n = None
w251_klift = None
try:
    w251_merged_n = w251_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
try:
    w251_klift = w251_out["skill_line_v2_k_lift"]["line_delta_k_lift"]
except Exception:
    pass
assert w251_total == 976_535 and w251_merged_n == 550_120, \\
    f"leg0 failed: W251 finalize anchors drift: total={w251_total} merged={w251_merged_n} (expect 976,535 / 550,120)"
assert w251_total == w250_total + 2_200 and w251_merged_n == w250_merged_n + 2_200, \\
    "leg0 failed: W250->W251 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"
assert w251_klift is not None and abs(w251_klift) <= 0.02, \\
    f"leg0 failed: W251 K-lift out-of-band at seat time: {w251_klift} (expect |delta|<=0.02 per the frozen prereg key-4 band)"''', 1)
# ---- ordinals ------------------------------------------------------------------
L('''assert owner_total == 240 and len(bmc_rows) == 70, \\
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 240/70 post-W250-splice, W251 unregistered)"''',
   '''assert owner_total == 241 and len(bmc_rows) == 71, \\
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 241/71 post-W251-splice, W252 unregistered)"''', 1)
L('assert ordinal == 241, f"leg0 ordinal derive: {ordinal} != 241"',
  'assert ordinal == 242, f"leg0 ordinal derive: {ordinal} != 242"', 1)
L('assert bmc_ordinal == 71, f"leg0 bmc ordinal derive: {bmc_ordinal} != 71"',
  'assert bmc_ordinal == 72, f"leg0 bmc ordinal derive: {bmc_ordinal} != 72"', 1)
# ---- leg0.5 + vacancy ----------------------------------------------------------
L('w251_seats_pre = [ln for ln in all_inbox if "w251" in ln.lower() and "seat" in ln.lower()]\nassert w251_seats_pre == [], f"leg0.5 failed: W251 seat already claimed on origin: {w251_seats_pre} (vacancy broken -- yield per fleet README sec.4)"',
   'w252_seats_pre = [ln for ln in all_inbox if "w252" in ln.lower() and "seat" in ln.lower()]\nassert w252_seats_pre == [], f"leg0.5 failed: W252 seat already claimed on origin: {w252_seats_pre} (vacancy broken -- yield per fleet README sec.4)"', 1)
L('skip_claims = [ln for ln in all_inbox if any(t in ln.lower() for t in ("w252", "w253")) and "seat" in ln.lower()]',
  'skip_claims = [ln for ln in all_inbox if any(t in ln.lower() for t in ("w253", "w254")) and "seat" in ln.lower()]', 1)
L('''receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W250-registered+FINALIZED (bm-c own-wave complete)",
    "w250_splice_landed": w250_splice_landed,
    "w250_bands": {"A": list(W250_A), "B": list(W250_B)},
    "w249_bands": {"A": list(W249_A), "B": list(W249_B)},
    "w250_finalize_landed": True,
    "w250_finalize_anchors": {"ledger_total": w250_total, "merged_n": w250_merged_n,
                               "skill_line_delta_k_lift": w250_klift},
    "chain_relation": {"w249_total": w249_total, "w250_total": w250_total,
                        "ledger_delta": w250_total - w249_total,
                        "k_delta": w250_merged_n - w249_merged_n},
    "inflight_upstream": False,''',
   '''receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W251-registered+FINALIZED (bm-c own-wave complete)",
    "w251_splice_landed": w251_splice_landed,
    "w251_bands": {"A": list(W251_A), "B": list(W251_B)},
    "w250_bands": {"A": list(W250_A), "B": list(W250_B)},
    "w251_finalize_landed": True,
    "w251_finalize_anchors": {"ledger_total": w251_total, "merged_n": w251_merged_n,
                               "skill_line_delta_k_lift": w251_klift},
    "chain_relation": {"w250_total": w250_total, "w251_total": w251_total,
                        "ledger_delta": w251_total - w250_total,
                        "k_delta": w251_merged_n - w250_merged_n},
    "inflight_upstream": False,''', 1)
L('"waits_upstream": "NONE (W250 complete: registered+FINALIZED; the W251 FREEZE is UNBLOCKED at seat time -- prereg derive = next window FIRST ACTION on the post-W250 universe)",',
   '"waits_upstream": "NONE (W251 complete: registered+FINALIZED; the W252 FREEZE is UNBLOCKED at seat time -- prereg derive = next window FIRST ACTION on the post-W251 universe)",', 1)
L('''"bmc_ordinal_note": ("bm-c 71st owned [W248, W249, W250, now W251 -- attempt-continuity: "
                          "live derive governs r359]; engine wave ordinal = "
                          "240 registry owner rows + this candidate = 241st"),''',
   '''"bmc_ordinal_note": ("bm-c 72nd owned [W248, W249, W250, W251, now W252 -- attempt-continuity: "
                          "live derive governs r359]; engine wave ordinal = "
                          "241 registry owner rows + this candidate = 242nd"),''', 1)
L('''    "anchor": ("W250 registered+FINALIZED own-wave (bm-c seat r1043-window origin cc06f1f4a + prereg "
               "4f7a130ff + r1046 splice 29930f489 (incl disclosed print-face heal rows 68->69) + "
               "engine self-burn 12/12 (ledger appends 486458150+77a4f529a) + r1046 continuation "
               "finalize: ledger 974,335 EXACT (972,135+2,200) / K=547,920 "
               "(545,720+2,200) / fivekeys ALL PASS results/_r1046bmc_w250_fivekeys.json / "
               "sixgate ALL PASS results/_r1046bmc_w250_sixgate.json PRE-FINALIZE phase, gate-1 "
               "anchored to landed git blob n1 22a957f851fd3adc / pf 40b0befe37ebbe2c) -- this W251 SEAT "
               "= queue-head supply per seat-first law O-20261010-2350 sec.2 (seats never queue "
               "behind freeze windows; standing CEO fill-order + O-20261013 22:1x CPU "
               "standing-open + O-20261015-0025 full mobilization + never-dry O-1819); the W251 "
               "FREEZE is UNBLOCKED (no in-flight seat upstream): the freezer proceeds prereg "
               "derive + five-face splice re-derived on the post-W250 universe")}''',
   '''    "anchor": ("W251 registered+FINALIZED own-wave (bm-c seat r1046-window origin bc3b2b693 + prereg "
               "9f5f106d6 + r1048 splice c813471cd (zero post-splice heal) + "
               "engine self-burn 12/12 (ledger appends c15c32afd+e46094052) + r1048 continuation "
               "finalize: ledger 976,535 EXACT (974,135+2,200) / K=550,120 "
               "(547,920+2,200) / fivekeys ALL PASS results/_r1048bmc_w251_fivekeys.json / "
               "sixgate ALL PASS results/_r1048bmc_w251_sixgate.json PRE-FINALIZE phase, gate-1 "
               "triple identity worktree==receipt==landed git blob n1 c9de218d7c362499 / pf d88cd951f44dfaf6) -- this W252 SEAT "
               "= queue-head supply per seat-first law O-20261010-2350 sec.2 (seats never queue "
               "behind freeze windows; standing CEO fill-order + O-20261013 22:1x CPU "
               "standing-open + O-20261015-0025 full mobilization + never-dry O-1819); the W252 "
               "FREEZE is UNBLOCKED (no in-flight seat upstream): the freezer proceeds prereg "
               "derive + five-face splice re-derived on the post-W251 universe")}''', 1)
L('print(f"leg0: {len(N1_BANDS)} rows tail=W250-registered+FINALIZED (bm-c own-wave complete, W251 unregistered), W250 face=registry A={W250_A} B={W250_B}, chain-relation W249->W250 ledger 972,135->974,335 (+2,200) K 545,720->547,920 (+2,200) OK, owner={owner_total} -> W251=241st wave candidate, bm-c 71st owned")',
   'print(f"leg0: {len(N1_BANDS)} rows tail=W251-registered+FINALIZED (bm-c own-wave complete, W252 unregistered), W251 face=registry A={W251_A} B={W251_B}, chain-relation W250->W251 ledger 974,135->976,535 (+2,200) K 547,920->550,120 (+2,200) OK, owner={owner_total} -> W252=242nd wave candidate, bm-c 72nd owned")', 1)
L('print("leg0.5: no W251 seat claim on origin (vacancy held) + zero skip-ahead W252/W253 seat claims (numbering density green) + waits-upstream=NONE (W251 freeze UNBLOCKED)")',
   'print("leg0.5: no W252 seat claim on origin (vacancy held) + zero skip-ahead W253/W254 seat claims (numbering density green) + waits-upstream=NONE (W252 freeze UNBLOCKED)")', 1)
L('# --- W251 own vacancy on origin -------------------------------------------------',
  '# --- W252 own vacancy on origin -------------------------------------------------', 1)
L('w251_seats = [ln for ln in all_inbox2 if "w251" in ln.lower() and "seat" in ln.lower()]\nassert w251_seats == [], f"vacancy failed: W251 seats already exist: {w251_seats}"',
   'w252_seats = [ln for ln in all_inbox2 if "w252" in ln.lower() and "seat" in ln.lower()]\nassert w252_seats == [], f"vacancy failed: W252 seats already exist: {w252_seats}"', 1)
L("assert '251: {\"a\": (' not in out_pf, \"vacancy failed: W251 row ALREADY on origin (r511 tail-lock)\"",
   "assert '252: {\"a\": (' not in out_pf, \"vacancy failed: W252 row ALREADY on origin (r511 tail-lock)\"", 1)
L("assert '\"PERPETUAL-N1-W251\"' not in outn1_vac, \"vacancy failed: W251 WAVE_CONFIGS ALREADY on origin\"",
   "assert '\"PERPETUAL-N1-W252\"' not in outn1_vac, \"vacancy failed: W252 WAVE_CONFIGS ALREADY on origin\"", 1)
L('outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",\n                                       "research/PERPETUAL_N1_W251_PREREG.md"], cwd=ROOT,',
   'outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",\n                                       "research/PERPETUAL_N1_W252_PREREG.md"], cwd=ROOT,', 1)
L('assert not outpre_vac, "vacancy failed: W251 per-wave prereg ALREADY on origin"',
   'assert not outpre_vac, "vacancy failed: W252 per-wave prereg ALREADY on origin"', 1)
L('print("vacancy: W251 origin vacancy held (no seat / row / configs / prereg)")',
   'print("vacancy: W252 origin vacancy held (no seat / row / configs / prereg)")', 1)
# ---- leg1: walk anchors ----------------------------------------------------------
L('# --- leg 1: honest forward walk from the W250 REGISTERED tails ------------------',
   '# --- leg 1: honest forward walk from the W251 REGISTERED tails ------------------', 1)
L('ARITH_A = (W250_A[1] + 1, W250_A[1] + WIDTH_A)\nARITH_B = (W250_B[1] + 1, W250_B[1] + WIDTH_B)',
   'ARITH_A = (W251_A[1] + 1, W251_A[1] + WIDTH_A)\nARITH_B = (W251_B[1] + 1, W251_B[1] + WIDTH_B)', 1)
L('''assert fc_a[0] == ARITH_A[0], ("leg1 A refused at naive start (W250 prereg sec.5 item5 + "
                                "W250 probe leg4 anticipated first-clean 567_501..569_500 hops=0 "
                                "on this universe; never transcribe r587 -- if this fires the "
                                "universe changed: re-read the live trace honestly)")''',
   '''assert fc_a[0] == ARITH_A[0], ("leg1 A refused at naive start (W251 prereg sec.5 item5 + "
                                "W251 probe leg4 anticipated first-clean 569_501..571_500 hops=0 "
                                "on this universe; never transcribe r587 -- if this fires the "
                                "universe changed: re-read the live trace honestly)")''', 1)
L('''assert not overlaps(fc_a, W249_A) and not overlaps(fc_a, W249_B), \\
    "leg1 failed: A overlaps prior-wave W249 registered bands"
assert not overlaps(fc_a, W250_A) and not overlaps(fc_a, W250_B), \\
    "leg1 failed: A overlaps prior-wave W250 registered bands"
assert fc_a[0] >= W250_B[1] + 1, \\
    "leg1 failed: A base must land at-or-after the registered prior-wave B tail+1 (mutual exclusion floor)"
# B honest face: naive start REFUSED (W250 prereg sec.5 item5 projection: seed 545_500 +
# W240..W249 A-ladder refusal face); the walk governs -- record the trace verbatim.
assert fc_b[0] > ARITH_B[0] or hops_b == 0, \\
    "leg1 B walk non-rotational/governance violation"
assert fc_b[0] > W250_B[1], \\
    "leg1 failed: B base must land above the registered prior-wave B tail (forward-monotone)"
assert not overlaps(fc_b, fc_a), "leg1 failed: B first-clean window lands inside the own-wave A window (B_hop lands-inside-A leg must be FALSE)"
assert not overlaps(fc_b, W249_A) and not overlaps(fc_b, W249_B), \\
    "leg1 failed: B overlaps prior-wave W249 registered bands"
assert not overlaps(fc_b, W250_A) and not overlaps(fc_b, W250_B), \\
    "leg1 failed: B overlaps prior-wave W250 registered bands"''',
   '''assert not overlaps(fc_a, W250_A) and not overlaps(fc_a, W250_B), \\
    "leg1 failed: A overlaps prior-wave W250 registered bands"
assert not overlaps(fc_a, W251_A) and not overlaps(fc_a, W251_B), \\
    "leg1 failed: A overlaps prior-wave W251 registered bands"
assert fc_a[0] >= W251_B[1] + 1, \\
    "leg1 failed: A base must land at-or-after the registered prior-wave B tail+1 (mutual exclusion floor)"
# B honest face: naive start 569_701..569_900 CLEAN at naive but lands INSIDE the own-wave
# W252 A window 569_501..571_500 (staircase re-emergence face, W251 prereg sec.5 item5
# projection); the own-A reservation walk governs -- record the trace verbatim.
assert fc_b[0] > ARITH_B[0] or hops_b == 0, \\
    "leg1 B walk non-rotational/governance violation"
assert fc_b[0] > W251_B[1], \\
    "leg1 failed: B base must land above the registered prior-wave B tail (forward-monotone)"
assert not overlaps(fc_b, fc_a), "leg1 failed: B first-clean window lands inside the own-wave A window (B_hop lands-inside-A leg must be FALSE)"
assert not overlaps(fc_b, W250_A) and not overlaps(fc_b, W250_B), \\
    "leg1 failed: B overlaps prior-wave W250 registered bands"
assert not overlaps(fc_b, W251_A) and not overlaps(fc_b, W251_B), \\
    "leg1 failed: B overlaps prior-wave W251 registered bands"''', 1)
L('''    "A_semantics": ("A arithmetic continuation from the REGISTERED W250 A tail "
                    "567_500+1 = 567_501..569_500 is CLEAN at naive start on the "
                    "post-W250-REGISTERED universe (fourteenth consecutive seed-gap "
                    "A-continuation face, anticipated by the W250 prereg sec.5 item5 + "
                    "W250 probe leg4 and confirmed live; never transcribe r587); A base = "
                    "first clean window, forward-monotone non-rotational r587 enforced "
                    "in-walk; A base >= registered prior-wave B tail+1 floor relation"),''',
   '''    "A_semantics": ("A arithmetic continuation from the REGISTERED W251 A tail "
                    "569_500+1 = 569_501..571_500 is CLEAN at naive start on the "
                    "post-W251-REGISTERED universe (fifteenth consecutive seed-gap "
                    "A-continuation face, anticipated by the W251 prereg sec.5 item5 + "
                    "W251 probe leg4 and confirmed live; never transcribe r587); A base = "
                    "first clean window, forward-monotone non-rotational r587 enforced "
                    "in-walk; A base >= registered prior-wave B tail+1 floor relation"),''', 1)
L('''    "B_semantics": ("B walk from the REGISTERED W250 B tail 545_300+1 = 545_301 is "
                    "REFUSED at naive start (SEED_REGISTRY seed 545_500 + the W240..W249 "
                    "A-ladder bands, per the W250 prereg sec.5 item5 projection) -- the "
                    "pre-W250 projected first-clean 565_501..565_700 is now INSIDE the "
                    "registered W250 A band 565_501..567_500, so the post-W250 walk hops "
                    "past it AND past the own-wave A window (own-A reservation standard "
                    "leg); B_hop lands-inside-A=false leg; live trace recorded verbatim"),''',
   '''    "B_semantics": ("B walk from the REGISTERED W251 B tail 569_700+1 = 569_701 is "
                    "CLEAN at naive start but the naive window 569_701..569_900 lands "
                    "INSIDE the own-wave W252 A window 569_501..571_500 (staircase "
                    "re-emergence face, per the W251 prereg sec.5 item5 projection) -- "
                    "the own-A reservation standard leg hops B past the own-wave A tail "
                    "571_500 to the staircase landing ~571_501..571_700 (B lands "
                    "above own-A, base==own-A tail+1 face re-emerges); "
                    "B_hop lands-inside-A=false leg; live trace recorded verbatim"),''', 1)
L('''    "relation_asserts": {"A_clean_at_naive_start": True,
                          "A_base_ge_priorB_tail_plus1": True,
                          "B_clean_at_naive_start": fc_b[0] == ARITH_B[0] and hops_b == 0,
                          "B_base_above_W250_tail": True,
                          "AB_mutual_exclusion": True,
                          "B_hop_lands_inside_A": False,
                          "W249_W250_bands_respected_A": True,
                          "W249_W250_bands_respected_B": True}}''',
   '''    "relation_asserts": {"A_clean_at_naive_start": True,
                          "A_base_ge_priorB_tail_plus1": True,
                          "B_clean_at_naive_start": fc_b[0] == ARITH_B[0] and hops_b == 0,
                          "B_base_above_W251_tail": True,
                          "AB_mutual_exclusion": True,
                          "B_hop_lands_inside_A": False,
                          "W250_W251_bands_respected_A": True,
                          "W250_W251_bands_respected_B": True}}''', 1)
# ---- leg2/leg3 labels ------------------------------------------------------------
L('# --- leg 2: seed_admit_gate rc0 ADMIT both bands (O-20261010-1945-bm-a convention) --',
   '# --- leg 2: seed_admit_gate rc0 ADMIT both bands (O-20261010-1945-bm-a convention) --', 1)
# ---- leg4: projection labels -----------------------------------------------------
L('# --- leg 4: W252+ naive projection (pre-W251 universe, honest forward face) ------',
   '# --- leg 4: W253+ naive projection (pre-W252 universe, honest forward face) ------', 1)
L('''receipt["legs"]["leg4"] = {
    "W252p_A_naive": f"{pA[0]}..{pA[1]}", "W252p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W252p_A_naive_refusers_seeds": pA_refusers,
    "W252p_B_naive": f"{pB[0]}..{pB[1]}", "W252p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W252p_B_lands_inside_W252p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W252+ projection on the pre-W251 universe (assuming the W251 seat bands "
             "declared here register verbatim). The W252 freezer MUST re-derive on the "
             "post-W251 universe AND reserve the own-wave A window when deriving B "
             "-- never transcribe r587; seed-gap face inherited from W239..W250: "
             "A/B decoupled, re-read the live trace, do NOT assume the staircase "
             "A-base==prior-B-tail+1 equality.")}''',
   '''receipt["legs"]["leg4"] = {
    "W253p_A_naive": f"{pA[0]}..{pA[1]}", "W253p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W253p_A_naive_refusers_seeds": pA_refusers,
    "W253p_B_naive": f"{pB[0]}..{pB[1]}", "W253p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W253p_B_lands_inside_W253p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W253+ projection on the pre-W252 universe (assuming the W252 seat bands "
             "declared here register verbatim). The W253 freezer MUST re-derive on the "
             "post-W252 universe AND reserve the own-wave A window when deriving B "
             "-- never transcribe r587; staircase face re-emergent since W251 "
             "(B lands above own-A): re-read the live trace, do NOT assume the "
             "A-base==prior-B-tail+1 or B-base==own-A-tail+1 equalities.")}''', 1)
L('print(f"leg4: W252+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")',
   'print(f"leg4: W253+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")', 1)
L('out_path = os.path.join(ROOT, "results", "_w251bmc_20261016_probe_receipt.json")',
   'out_path = os.path.join(ROOT, "results", "_w252bmc_20261016_probe_receipt.json")', 1)

if fails:
    print("DERIVE-FAIL %d legs:" % len(fails))
    for f in fails:
        print("  " + f)
    raise SystemExit(1)
# MUST_NOT stale faces
must_not = ['240 owner rows', 'W251 pre-seat probe (bm-c loop window r1046',
            '"W251 SEAT"', 'w250_klift is not None', 'range(16, 251)',
            '_w251bmc_20261016_probe_receipt.json']
for m in must_not:
    if m in t:
        print("MUST_NOT survived: %r" % m)
        raise SystemExit(1)
# MUST faces
must = ['W252 pre-seat probe', '241 owner rows', 'W252 candidate = 242nd wave',
        'W251 registry row drift', '976_535', '550_120', 'W253p_A_naive',
        'staircase re-emergence face', 'range(16, 252)',
        'assert 252 not in N1_BANDS', 'bmc_ordinal == 72',
        '_w252bmc_20261016_probe_receipt.json']
for m in must:
    if m not in t:
        print("MUST face missing: %r" % m)
        raise SystemExit(1)
io.open(DST, "w", encoding="utf-8", newline="").write(t)
py_compile.compile(DST, doraise=True)
print("DERIVE-OK bytes=%d" % len(t.encode("utf-8")))
