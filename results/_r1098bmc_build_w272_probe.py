# -*- coding: utf-8 -*-
"""r1098 builder: _w272bmc_20261018_probe.py canon-clone of _w271bmc_20261018_probe.py
per E63 age() machine-needle law (ordered exact needles, each count-asserted,
reverse-order wave rolls to avoid duplicate-target collisions; live faces
machine-verified pre-build this window: W271 registry A 611501-613500 /
B 613501-613700 bm-c, finalize ledger 1,020,535 / merged 594,120 / klift
+0.0001, owner 261 rows bmc 90 / bma 130 / bmb 41, keytail [269,270,271],
seat MSG-20261018-175x-bmc-w271-seat on origin)."""
import py_compile

SRC = "results/_w271bmc_20261018_probe.py"
DST = "results/_w272bmc_20261018_probe.py"

NEEDLES = [
# 1. docstring head+chain block
('''W271 pre-seat probe (bm-c loop window r1095, 2026-10-18 ~17:4x;
queue-head supply lane: upstream W270 = bm-c OWN WAVE complete chain
(seat MSG-20261018-1605-bmc-w270-seat origin 9f480646f4 -> prereg freeze
3bb8b9308e r1094 -> five-face splice CLEAN-AT-BIRTH 3rd gen 1c814343e r1095
(setwave birth-station presence gates _set_wave(270):1/(269):0/(268):0 held;
zero surgical heals; estate carries clean n1 per freeze receipt) + engine
self-burn 12/12 batched self-commits 6c1aee751d+ae98b97a10
-> sixgate PRE-FINALIZE ALL PASS 33rd consecutive r1095 + finalize one-pass
n1_w270_results.json r1095 ledger 1,018,335 EXACT (1,016,135+2,200) / merged
pool K=591,920 EXACT (589,720+2,200) + fivekeys 6/6 + sec.7/8 backfilled
r1095 estate e4b015cbb) -- NO in-flight seat upstream: the W271 FREEZE is
UNBLOCKED at seat time. Universe face = post-W270-REGISTERED (live registry,
260 owner rows: bm-a 130 / bm-b 41 / bm-c 89 incl W270; W271 candidate =
261st wave, bm-c 90th own wave).''',
'''W272 pre-seat probe (bm-c loop window r1098, 2026-10-18 ~19:0x;
queue-head supply lane: upstream W271 = bm-c OWN WAVE complete chain
(seat MSG-20261018-175x-bmc-w271-seat origin 87d2697cd -> prereg freeze
f75b18c862 r1096 -> five-face splice CLEAN-AT-BIRTH 4th gen 7dd091eef1 r1097
(setwave birth-station presence gates _set_wave(271):1/(270):0/(269):0 held;
zero surgical heals; estate carries clean n1 per freeze receipt) + engine
self-burn 12/12 batched self-commits a035552321+037445477b
-> sixgate PRE-FINALIZE ALL PASS 34th consecutive r1097 + finalize one-pass
n1_w271_results.json r1097 ledger 1,020,535 EXACT (1,018,335+2,200) / merged
pool K=594,120 EXACT (591,920+2,200) + fivekeys 6/6 + sec.7/8 backfilled
r1097 cycle estate e0a21b817d) -- NO in-flight seat upstream: the W272 FREEZE is
UNBLOCKED at seat time. Universe face = post-W271-REGISTERED (live registry,
261 owner rows: bm-a 130 / bm-b 41 / bm-c 90 incl W271; W272 candidate =
262nd wave, bm-c 91st own wave).''', 1),
# 2. staircase continuation paragraph
('''STAIRCASE CONTINUATION face (W270 probe receipt leg4 note named it; live
re-derive governs r587): naive W271 A continuation 611_301..613_300 is
REFUSED at the REGISTERED W270 B band 611_301..611_500 -> A hops past
611_500 to first-clean 611_501..613_500 (TWENTIETH consecutive A-hop
expected); B naive 611_501..611_700 is CLEAN vs registered BUT lands INSIDE
the own-wave A first-clean window -> own-A reservation hops B past 613_500
to first-clean 613_501..613_700 (TWENTY-FIRST consecutive above-own-A
expected; B base==own-A tail+1 floor).''',
'''STAIRCASE CONTINUATION face (W271 probe receipt leg4 note named it; live
re-derive governs r587): naive W272 A continuation 613_501..615_500 is
REFUSED at the REGISTERED W271 B band 613_501..613_700 -> A hops past
613_700 to first-clean 613_701..615_700 (TWENTY-FIRST consecutive A-hop
expected); B naive 613_701..613_900 is CLEAN vs registered BUT lands INSIDE
the own-wave A first-clean window -> own-A reservation hops B past 615_700
to first-clean 615_701..615_900 (TWENTY-SECOND consecutive above-own-A
expected; B base==own-A tail+1 floor).''', 1),
# 3. bloodline
('''Bloodline: _w270bmc_20261018_probe.py derive machinery verbatim
(walk/gates/constants), W271 facts live-registry-driven, compact re-authoring''',
'''Bloodline: _w271bmc_20261018_probe.py derive machinery verbatim
(walk/gates/constants), W272 facts live-registry-driven, compact re-authoring''', 1),
# 4. receipt probe head
('''receipt = {"probe": "W271 pre-seat probe (bm-c loop r1095 window, 2026-10-18 ~17:4x, queue-head supply lane: upstream W270 = bm-c OWN WAVE complete chain (finalize ledger 1,018,335 / K=591,920 landed r1095 chain); NO in-flight seat upstream -- W271 FREEZE UNBLOCKED at seat time; seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + CEO fill-order standing; universe = post-W270-REGISTERED 260 owner rows)", "legs": {}}''',
'''receipt = {"probe": "W272 pre-seat probe (bm-c loop r1098 window, 2026-10-18 ~19:0x, queue-head supply lane: upstream W271 = bm-c OWN WAVE complete chain (finalize ledger 1,020,535 / K=594,120 landed r1097 chain); NO in-flight seat upstream -- W272 FREEZE UNBLOCKED at seat time; seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + CEO fill-order standing; universe = post-W271-REGISTERED 261 owner rows)", "legs": {}}''', 1),
# 5. leg0 comment
('# --- leg 0: registry shape + W268..W270 landed faces + chain-relation anchors ---',
 '# --- leg 0: registry shape + W269..W271 landed faces + chain-relation anchors ---', 1),
# 6. splice landed
('''w270_splice_landed = 270 in N1_BANDS
assert w270_splice_landed, "leg0 failed: W270 splice not landed (registry row absent -- r1095 splice face broken)"''',
'''w271_splice_landed = 271 in N1_BANDS
assert w271_splice_landed, "leg0 failed: W271 splice not landed (registry row absent -- r1097 splice face broken)"''', 1),
# 7. base keys range
('list(range(16, 271))', 'list(range(16, 272))', 1),
# 8. not-registered assert
('''assert 271 not in N1_BANDS, "leg0 failed: W271 ALREADY registered locally (upstream freeze landed mid-probe -- re-derive on the post-W271 universe honestly, do not seat on a stale universe)"''',
'''assert 272 not in N1_BANDS, "leg0 failed: W272 ALREADY registered locally (upstream freeze landed mid-probe -- re-derive on the post-W272 universe honestly, do not seat on a stale universe)"''', 1),
# 9. W270 registry block -> W271 (REVERSE ORDER: run before W269->W270)
('''W270_A = tuple(N1_BANDS[270]["a"])
W270_B = tuple(N1_BANDS[270]["b_exit"])
assert W270_A == (609_301, 611_300) and W270_B == (611_301, 611_500) and \\
    N1_BANDS[270].get("engine_owner") == "bm-c", "leg0 failed: W270 registry row drift (bm-c r1095 clean-at-birth 3rd-gen splice 1c814343e face)"''',
'''W271_A = tuple(N1_BANDS[271]["a"])
W271_B = tuple(N1_BANDS[271]["b_exit"])
assert W271_A == (611_501, 613_500) and W271_B == (613_501, 613_700) and \\
    N1_BANDS[271].get("engine_owner") == "bm-c", "leg0 failed: W271 registry row drift (bm-c r1097 clean-at-birth 4th-gen splice 7dd091eef1 face)"''', 1),
# 10. W269 registry block -> W270
('''W269_A = tuple(N1_BANDS[269]["a"])
W269_B = tuple(N1_BANDS[269]["b_exit"])
assert W269_A == (607_101, 609_100) and W269_B == (609_101, 609_300) and \\
    N1_BANDS[269].get("engine_owner") == "bm-c", "leg0 failed: W269 registry row drift (bm-c r1093 clean-at-birth 2nd-gen splice 440b07c94b face)"''',
'''W270_A = tuple(N1_BANDS[270]["a"])
W270_B = tuple(N1_BANDS[270]["b_exit"])
assert W270_A == (609_301, 611_300) and W270_B == (611_301, 611_500) and \\
    N1_BANDS[270].get("engine_owner") == "bm-c", "leg0 failed: W270 registry row drift (bm-c r1095 clean-at-birth 3rd-gen splice 1c814343e face)"''', 1),
# 11. W268 registry block -> W269
('''W268_A = tuple(N1_BANDS[268]["a"])
W268_B = tuple(N1_BANDS[268]["b_exit"])
assert W268_A == (604_901, 606_900) and W268_B == (606_901, 607_100) and \\
    N1_BANDS[268].get("engine_owner") == "bm-c", "leg0 failed: W268 registry row drift (bm-c r1091 clean-at-birth splice 8bc7ac759e face)"''',
'''W269_A = tuple(N1_BANDS[269]["a"])
W269_B = tuple(N1_BANDS[269]["b_exit"])
assert W269_A == (607_101, 609_100) and W269_B == (609_101, 609_300) and \\
    N1_BANDS[269].get("engine_owner") == "bm-c", "leg0 failed: W269 registry row drift (bm-c r1093 clean-at-birth 2nd-gen splice 440b07c94b face)"''', 1),
# 12. staircase continuity asserts
('''assert W270_A[0] == W269_B[1] + 1, \\
    "leg0 failed: W270 A base != W269 B tail+1 (staircase-affects-A nineteenth consecutive hop face drift)"
assert W270_B[0] == W270_A[1] + 1, \\
    "leg0 failed: W270 B base != own-A tail+1 (above-own-A twentieth consecutive face drift)"''',
'''assert W271_A[0] == W270_B[1] + 1, \\
    "leg0 failed: W271 A base != W270 B tail+1 (staircase-affects-A twentieth consecutive hop face drift)"
assert W271_B[0] == W271_A[1] + 1, \\
    "leg0 failed: W271 B base != own-A tail+1 (above-own-A twenty-first consecutive face drift)"''', 1),
# 13. for-loop wave tuple
('for _w in (268, 269, 270):', 'for _w in (269, 270, 271):', 1),
# 14. w270_out block -> w271_out (REVERSE ORDER)
('''w270_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w270_results.json"), encoding="utf-8"))
w270_led = (w270_out.get("science_gates") or {}).get("ledger") or {}
w270_total = w270_led.get("total")
w270_merged_n = w270_out["null_pool_cumulative"]["merged"]["n_values"]
w270_klift = w270_out["skill_line_v2_k_lift"]["line_delta_k_lift"]''',
'''w271_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w271_results.json"), encoding="utf-8"))
w271_led = (w271_out.get("science_gates") or {}).get("ledger") or {}
w271_total = w271_led.get("total")
w271_merged_n = w271_out["null_pool_cumulative"]["merged"]["n_values"]
w271_klift = w271_out["skill_line_v2_k_lift"]["line_delta_k_lift"]''', 1),
# 15. w269_out block -> w270_out
('''w269_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w269_results.json"), encoding="utf-8"))
w269_led = (w269_out.get("science_gates") or {}).get("ledger") or {}
w269_total = w269_led.get("total")
w269_merged_n = w269_out["null_pool_cumulative"]["merged"]["n_values"]''',
'''w270_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w270_results.json"), encoding="utf-8"))
w270_led = (w270_out.get("science_gates") or {}).get("ledger") or {}
w270_total = w270_led.get("total")
w270_merged_n = w270_out["null_pool_cumulative"]["merged"]["n_values"]''', 1),
# 16. w268_out block -> w269_out
('''w268_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w268_results.json"), encoding="utf-8"))
w268_led = (w268_out.get("science_gates") or {}).get("ledger") or {}
w268_total = w268_led.get("total")
w268_merged_n = w268_out["null_pool_cumulative"]["merged"]["n_values"]''',
'''w269_out = json.load(open(os.path.join(ROOT, "results", "perpetual_faces", "n1_w269_results.json"), encoding="utf-8"))
w269_led = (w269_out.get("science_gates") or {}).get("ledger") or {}
w269_total = w269_led.get("total")
w269_merged_n = w269_out["null_pool_cumulative"]["merged"]["n_values"]''', 1),
# 17. W270 ledger assert -> W271 (REVERSE ORDER)
('''assert w270_total == 1_018_335 and w270_merged_n == 591_920, \\
    f"leg0 failed: W270 finalize anchors drift: total={w270_total} merged={w270_merged_n} (expect 1,018,335 / 591,920)"''',
'''assert w271_total == 1_020_535 and w271_merged_n == 594_120, \\
    f"leg0 failed: W271 finalize anchors drift: total={w271_total} merged={w271_merged_n} (expect 1,020,535 / 594,120)"''', 1),
# 18. W269 ledger assert -> W270
('''assert w269_total == 1_016_135 and w269_merged_n == 589_720, \\
    f"leg0 failed: W269 finalize anchors drift: total={w269_total} merged={w269_merged_n} (expect 1,016,135 / 589,720)"''',
'''assert w270_total == 1_018_335 and w270_merged_n == 591_920, \\
    f"leg0 failed: W270 finalize anchors drift: total={w270_total} merged={w270_merged_n} (expect 1,018,335 / 591,920)"''', 1),
# 19. W268 ledger assert -> W269
('''assert w268_total == 1_013_935 and w268_merged_n == 587_520, \\
    f"leg0 failed: W268 finalize anchors drift: total={w268_total} merged={w268_merged_n} (expect 1,013,935 / 587,520)"''',
'''assert w269_total == 1_016_135 and w269_merged_n == 589_720, \\
    f"leg0 failed: W269 finalize anchors drift: total={w269_total} merged={w269_merged_n} (expect 1,016,135 / 589,720)"''', 1),
# 20. W270->W269 chain assert -> W271->W270 (REVERSE ORDER)
('''assert w270_total == w269_total + 2_200 and w270_merged_n == w269_merged_n + 2_200, \\
    "leg0 failed: W269->W270 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"''',
'''assert w271_total == w270_total + 2_200 and w271_merged_n == w270_merged_n + 2_200, \\
    "leg0 failed: W270->W271 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"''', 1),
# 21. W269->W268 chain assert -> W270->W269
('''assert w269_total == w268_total + 2_200 and w269_merged_n == w268_merged_n + 2_200, \\
    "leg0 failed: W268->W269 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"''',
'''assert w270_total == w269_total + 2_200 and w270_merged_n == w269_merged_n + 2_200, \\
    "leg0 failed: W269->W270 chain-relation anchors broken (ledger/K continuity +2,200/+2,200)"''', 1),
# 22. klift assert
('''assert w270_klift is not None and abs(w270_klift) <= 0.02, \\
    f"leg0 failed: W270 K-lift out-of-band at seat time: {w270_klift} (expect |delta|<=0.02 per the frozen prereg key-4 band)"''',
'''assert w271_klift is not None and abs(w271_klift) <= 0.02, \\
    f"leg0 failed: W271 K-lift out-of-band at seat time: {w271_klift} (expect |delta|<=0.02 per the frozen prereg key-4 band)"''', 1),
# 23. owner counts + ordinal
('''assert owner_total == 260 and len(bmc_rows) == 89, \\
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 260/89 post-W270-splice, W271 unregistered)"
ordinal = owner_total + 1
assert ordinal == 261, f"leg0 ordinal derive: {ordinal} != 261"''',
'''assert owner_total == 261 and len(bmc_rows) == 90, \\
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 261/90 post-W271-splice, W272 unregistered)"
ordinal = owner_total + 1
assert ordinal == 262, f"leg0 ordinal derive: {ordinal} != 262"''', 1),
# 24. bma registration line
('f"leg0 bma ordinal drift: {len(bma_rows)} (expect 130 post-W270-registration)"',
 'f"leg0 bma ordinal drift: {len(bma_rows)} (expect 130 post-W271-registration)"', 1),
# 25. leg0 receipt dict
('''receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W270-registered+FINALIZED (bm-c own-wave complete r1095 chain)",
    "w270_bands": {"A": list(W270_A), "B": list(W270_B)},
    "w269_bands": {"A": list(W269_A), "B": list(W269_B)},
    "w270_finalize_landed": True,
    "w270_finalize_anchors": {"ledger_total": w270_total, "merged_n": w270_merged_n,
                                "skill_line_delta_k_lift": w270_klift},
    "chain_relation": {"w268_total": w268_total, "w269_total": w269_total,
                       "w270_total": w270_total,
                       "ledger_delta": w270_total - w269_total,
                       "k_delta": w270_merged_n - w269_merged_n},
    "inflight_upstream": False,
    "waits_upstream": "NONE (W270 complete: registered+FINALIZED r1095 chain; the W271 FREEZE is UNBLOCKED at seat time -- prereg derive = next window FIRST ACTION on the post-W270 universe)",
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": ordinal,
}''',
'''receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W271-registered+FINALIZED (bm-c own-wave complete r1097 chain)",
    "w271_bands": {"A": list(W271_A), "B": list(W271_B)},
    "w270_bands": {"A": list(W270_A), "B": list(W270_B)},
    "w271_finalize_landed": True,
    "w271_finalize_anchors": {"ledger_total": w271_total, "merged_n": w271_merged_n,
                                "skill_line_delta_k_lift": w271_klift},
    "chain_relation": {"w269_total": w269_total, "w270_total": w270_total,
                       "w271_total": w271_total,
                       "ledger_delta": w271_total - w270_total,
                       "k_delta": w271_merged_n - w270_merged_n},
    "inflight_upstream": False,
    "waits_upstream": "NONE (W271 complete: registered+FINALIZED r1097 chain; the W272 FREEZE is UNBLOCKED at seat time -- prereg derive = same-window/next-window FIRST ACTION on the post-W271 universe)",
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": ordinal,
}''', 1),
# 26. leg0 print
('''print(f"leg0: {len(N1_BANDS)} rows tail=W270-registered+FINALIZED (bm-c own-wave complete r1095 chain, W271 unregistered), W270 face=registry A={W270_A} B={W270_B}, chain-relation W268->W269->W270 ledger 1,013,935->1,016,135->1,018,335 (+2,200/+2,200) K 587,520->589,720->591,920 (+2,200/+2,200) OK, owner={owner_total} -> W271=261st wave candidate")''',
'''print(f"leg0: {len(N1_BANDS)} rows tail=W271-registered+FINALIZED (bm-c own-wave complete r1097 chain, W272 unregistered), W271 face=registry A={W271_A} B={W271_B}, chain-relation W269->W270->W271 ledger 1,016,135->1,018,335->1,020,535 (+2,200/+2,200) K 589,720->591,920->594,120 (+2,200/+2,200) OK, owner={owner_total} -> W272=262nd wave candidate")''', 1),
# 27. leg0.5 seats_pre
('w271_seats_pre = [ln for ln in all_inbox if "w271" in ln.lower() and "seat" in ln.lower()]',
 'w272_seats_pre = [ln for ln in all_inbox if "w272" in ln.lower() and "seat" in ln.lower()]', 1),
# 28. leg0.5 seats_pre assert
('''assert w271_seats_pre == [], f"leg0.5 failed: W271 seat already claimed on origin: {w271_seats_pre} (vacancy broken -- yield per fleet README sec.4)"''',
'''assert w272_seats_pre == [], f"leg0.5 failed: W272 seat already claimed on origin: {w272_seats_pre} (vacancy broken -- yield per fleet README sec.4)"''', 1),
# 29. skip-claims tuple
('skip_claims = [ln for ln in all_inbox if any(t in ln.lower() for t in ("w272", "w273")) and "seat" in ln.lower()]',
 'skip_claims = [ln for ln in all_inbox if any(t in ln.lower() for t in ("w273", "w274")) and "seat" in ln.lower()]', 1),
# 30. skip-claims message
('f"leg0.5 failed: skip-ahead seat claims exist (W272/W273 numbering density violated): {skip_claims}"',
 'f"leg0.5 failed: skip-ahead seat claims exist (W273/W274 numbering density violated): {skip_claims}"', 1),
# 31. leg0.5 print
('''print("leg0.5: no W271 seat claim on origin (vacancy held) + zero skip-ahead W272/W273 seat claims (numbering density green) + waits-upstream=NONE (W271 freeze UNBLOCKED)")''',
'''print("leg0.5: no W272 seat claim on origin (vacancy held) + zero skip-ahead W273/W274 seat claims (numbering density green) + waits-upstream=NONE (W272 freeze UNBLOCKED)")''', 1),
# 32. vacancy comment
('# --- W271 own vacancy on origin ',
 '# --- W272 own vacancy on origin ', 1),
# 33. vacancy seats
('''w271_seats = [ln for ln in all_inbox2 if "w271" in ln.lower() and "seat" in ln.lower()]
assert w271_seats == [], f"vacancy failed: W271 seats already exist: {w271_seats}"''',
'''w272_seats = [ln for ln in all_inbox2 if "w272" in ln.lower() and "seat" in ln.lower()]
assert w272_seats == [], f"vacancy failed: W272 seats already exist: {w272_seats}"''', 1),
# 34. vacancy row
('''assert '271: {"a": (' not in out_pf, "vacancy failed: W271 row ALREADY on origin (r511 tail-lock)"''',
'''assert '272: {"a": (' not in out_pf, "vacancy failed: W272 row ALREADY on origin (r511 tail-lock)"''', 1),
# 35. vacancy configs
('''assert '"PERPETUAL-N1-W271"' not in outn1_vac, "vacancy failed: W271 WAVE_CONFIGS ALREADY on origin"''',
'''assert '"PERPETUAL-N1-W272"' not in outn1_vac, "vacancy failed: W272 WAVE_CONFIGS ALREADY on origin"''', 1),
# 36. vacancy prereg
('''outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W271_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W271 per-wave prereg ALREADY on origin"''',
'''outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W272_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W272 per-wave prereg ALREADY on origin"''', 1),
# 37. vacancy print
('print("vacancy: W271 origin vacancy held (no seat / row / configs / prereg)")',
 'print("vacancy: W272 origin vacancy held (no seat / row / configs / prereg)")', 1),
# 38. leg1 ARITH
('''ARITH_A = (W270_A[1] + 1, W270_A[1] + WIDTH_A)
ARITH_B = (W270_B[1] + 1, W270_B[1] + WIDTH_B)''',
'''ARITH_A = (W271_A[1] + 1, W271_A[1] + WIDTH_A)
ARITH_B = (W271_B[1] + 1, W271_B[1] + WIDTH_B)''', 1),
# 39. leg1 A staircase assert
('''assert fc_a == (611_501, 613_500) and hops_a == 1, ("leg1 A staircase face: live walk refused "
                                "the naive start 611_301..613_300 at the REGISTERED W270 B band "
                                "611_301..611_500 (staircase-affects-A TWENTIETH consecutive hop; "
                                "the W270 probe receipt leg4 note projection confirmed live per r587 -- "
                                "live walk governs; if this fires the universe changed again: "
                                "re-read the live trace honestly)")''',
'''assert fc_a == (613_701, 615_700) and hops_a == 1, ("leg1 A staircase face: live walk refused "
                                "the naive start 613_501..615_500 at the REGISTERED W271 B band "
                                "613_501..613_700 (staircase-affects-A TWENTY-FIRST consecutive hop; "
                                "the W271 probe receipt leg4 note projection confirmed live per r587 -- "
                                "live walk governs; if this fires the universe changed again: "
                                "re-read the live trace honestly)")''', 1),
# 40. leg1 A overlap asserts
('''assert not overlaps(fc_a, W268_A) and not overlaps(fc_a, W268_B), \\
    "leg1 failed: A overlaps prior-wave W268 registered bands"
assert not overlaps(fc_a, W269_A) and not overlaps(fc_a, W269_B), \\
    "leg1 failed: A overlaps prior-wave W269 registered bands"
assert not overlaps(fc_a, W270_A) and not overlaps(fc_a, W270_B), \\
    "leg1 failed: A overlaps prior-wave W270 registered bands"
assert fc_a[0] >= W270_B[1] + 1, \\
    "leg1 failed: A base must land at-or-after the registered prior-wave B tail+1 (mutual exclusion floor)"''',
'''assert not overlaps(fc_a, W269_A) and not overlaps(fc_a, W269_B), \\
    "leg1 failed: A overlaps prior-wave W269 registered bands"
assert not overlaps(fc_a, W270_A) and not overlaps(fc_a, W270_B), \\
    "leg1 failed: A overlaps prior-wave W270 registered bands"
assert not overlaps(fc_a, W271_A) and not overlaps(fc_a, W271_B), \\
    "leg1 failed: A overlaps prior-wave W271 registered bands"
assert fc_a[0] >= W271_B[1] + 1, \\
    "leg1 failed: A base must land at-or-after the registered prior-wave B tail+1 (mutual exclusion floor)"''', 1),
# 41. B honest-face comment
('''# B honest face: naive start 611_501..611_700 CLEAN vs registered BUT lands INSIDE the own-wave
# W271 A first-clean window 611_501..613_500 (own-A reservation face, cascade per the W270
# probe receipt leg4 note projection, superseded live per r587); walk governs.''',
'''# B honest face: naive start 613_701..613_900 CLEAN vs registered BUT lands INSIDE the own-wave
# W272 A first-clean window 613_701..615_700 (own-A reservation face, cascade per the W271
# probe receipt leg4 note projection, superseded live per r587); walk governs.''', 1),
# 42. B asserts
('''assert fc_b[0] > W270_B[1], \\
    "leg1 failed: B base must land above the registered prior-wave B tail (forward-monotone)"
assert not overlaps(fc_b, fc_a), "leg1 failed: B first-clean window lands inside the own-wave A window (B_hop lands-inside-A leg must be FALSE)"
assert not overlaps(fc_b, W268_A) and not overlaps(fc_b, W268_B), \\
    "leg1 failed: B overlaps prior-wave W268 registered bands"
assert not overlaps(fc_b, W269_A) and not overlaps(fc_b, W269_B), \\
    "leg1 failed: B overlaps prior-wave W269 registered bands"
assert not overlaps(fc_b, W270_A) and not overlaps(fc_b, W270_B), \\
    "leg1 failed: B overlaps prior-wave W270 registered bands"''',
'''assert fc_b[0] > W271_B[1], \\
    "leg1 failed: B base must land above the registered prior-wave B tail (forward-monotone)"
assert not overlaps(fc_b, fc_a), "leg1 failed: B first-clean window lands inside the own-wave A window (B_hop lands-inside-A leg must be FALSE)"
assert not overlaps(fc_b, W269_A) and not overlaps(fc_b, W269_B), \\
    "leg1 failed: B overlaps prior-wave W269 registered bands"
assert not overlaps(fc_b, W270_A) and not overlaps(fc_b, W270_B), \\
    "leg1 failed: B overlaps prior-wave W270 registered bands"
assert not overlaps(fc_b, W271_A) and not overlaps(fc_b, W271_B), \\
    "leg1 failed: B overlaps prior-wave W271 registered bands"''', 1),
# 43. A_semantics
('''    "A_semantics": ("A arithmetic continuation from the REGISTERED W270 A tail "
                    "611_300+1 = 611_301..613_300 is REFUSED at naive start on the "
                    "post-W270-REGISTERED universe (the REGISTERED W270 B band "
                    "611_301..611_500 sits INSIDE the naive A window: staircase-"
                    "affects-A TWENTIETH consecutive A-hop, confirming the W270 "
                    "probe receipt leg4 note projection live per r587; live walk "
                    "governs); the walk hops past the W270 B tail 611_500 -> A "
                    "first-clean 611_501..613_500 (hops=1); forward-monotone "
                    "non-rotational r587 enforced in-walk; A base >= registered "
                    "prior-wave B tail+1 floor"),''',
'''    "A_semantics": ("A arithmetic continuation from the REGISTERED W271 A tail "
                    "613_500+1 = 613_501..615_500 is REFUSED at naive start on the "
                    "post-W271-REGISTERED universe (the REGISTERED W271 B band "
                    "613_501..613_700 sits INSIDE the naive A window: staircase-"
                    "affects-A TWENTY-FIRST consecutive A-hop, confirming the W271 "
                    "probe receipt leg4 note projection live per r587; live walk "
                    "governs); the walk hops past the W271 B tail 613_700 -> A "
                    "first-clean 613_701..615_700 (hops=1); forward-monotone "
                    "non-rotational r587 enforced in-walk; A base >= registered "
                    "prior-wave B tail+1 floor"),''', 1),
# 44. B_semantics
('''    "B_semantics": ("B walk from the REGISTERED W270 B tail 611_500+1 = 611_501 is "
                    "CLEAN at naive start vs the registered universe but the naive "
                    "window 611_501..611_700 lands INSIDE the own-wave W271 A "
                    "first-clean window 611_501..613_500 (own-A reservation cascade "
                    "face, per the W270 probe receipt leg4 note projection "
                    "confirmed live) -- the own-A reservation standard leg hops B "
                    "past the own-wave A tail 613_500 -> first-clean 613_501..613_700 "
                    "(B lands above own-A, base==own-A tail+1 face, TWENTY-FIRST "
                    "consecutive above-own-A); B_hop lands-inside-A=false leg; live "
                    "trace recorded verbatim"),''',
'''    "B_semantics": ("B walk from the REGISTERED W271 B tail 613_700+1 = 613_701 is "
                    "CLEAN at naive start vs the registered universe but the naive "
                    "window 613_701..613_900 lands INSIDE the own-wave W272 A "
                    "first-clean window 613_701..615_700 (own-A reservation cascade "
                    "face, per the W271 probe receipt leg4 note projection "
                    "confirmed live) -- the own-A reservation standard leg hops B "
                    "past the own-wave A tail 615_700 -> first-clean 615_701..615_900 "
                    "(B lands above own-A, base==own-A tail+1 face, TWENTY-SECOND "
                    "consecutive above-own-A); B_hop lands-inside-A=false leg; live "
                    "trace recorded verbatim"),''', 1),
# 45. relation_asserts keys
('"A_staircase_hop_past_W270_B": True,', '"A_staircase_hop_past_W271_B": True,', 1),
# 46
('"B_base_above_W270_tail": True,', '"B_base_above_W271_tail": True,', 1),
# 47. leg4 comment
('# --- leg 4: W272+ naive projection (pre-W271 universe, honest forward face) ------',
 '# --- leg 4: W273+ naive projection (pre-W272 universe, honest forward face) ------', 1),
# 48. leg4 dict + note
('''receipt["legs"]["leg4"] = {
    "W272p_A_naive": f"{pA[0]}..{pA[1]}", "W272p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W272p_A_naive_refusers_seeds": pA_refusers,
    "W272p_B_naive": f"{pB[0]}..{pB[1]}", "W272p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W272p_B_lands_inside_W272p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W272+ projection on the pre-W271 universe (assuming the W271 seat bands "
             "declared here register verbatim). ONCE W271 REGISTERS, the naive W272 A "
             "start 613_501 is REFUSED by the registered W271 B band 613_501..613_700 "
             "(staircase-affects-A TWENTY-FIRST consecutive A-hop expected) AND the W272 B "
             "naive start lands inside the own-A reservation face; the W272 freezer "
             "MUST re-derive on the post-W271 universe AND reserve the own-wave A "
             "window when deriving B -- never transcribe r587; staircase face "
             "continuing since W251 (A hops over prior B; B lands above own-A): "
             "re-read the live trace, do NOT assume the A-base==prior-B-tail+1 or "
             "B-base==own-A-tail+1 equalities.")}''',
'''receipt["legs"]["leg4"] = {
    "W273p_A_naive": f"{pA[0]}..{pA[1]}", "W273p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W273p_A_naive_refusers_seeds": pA_refusers,
    "W273p_B_naive": f"{pB[0]}..{pB[1]}", "W273p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W273p_B_lands_inside_W273p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W273+ projection on the pre-W272 universe (assuming the W272 seat bands "
             "declared here register verbatim). ONCE W272 REGISTERS, the naive W273 A "
             "start 615_701 is REFUSED by the registered W272 B band (live-derived at "
             "W272 seat time; expected 615_701..615_900) "
             "(staircase-affects-A TWENTY-SECOND consecutive A-hop expected) AND the W273 B "
             "naive start lands inside the own-A reservation face; the W273 freezer "
             "MUST re-derive on the post-W272 universe AND reserve the own-wave A "
             "window when deriving B -- never transcribe r587; staircase face "
             "continuing since W251 (A hops over prior B; B lands above own-A): "
             "re-read the live trace, do NOT assume the A-base==prior-B-tail+1 or "
             "B-base==own-A-tail+1 equalities.")}''', 1),
# 49. leg4 print
('print(f"leg4: W272+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")',
 'print(f"leg4: W273+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")', 1),
# 50. out_path
('"_w271bmc_20261018_probe_receipt.json"', '"_w272bmc_20261018_probe_receipt.json"', 1),
]

MUST_CONTAIN = [
    'W272 pre-seat probe (bm-c loop window r1098',
    'list(range(16, 272))',
    'assert 272 not in N1_BANDS',
    "assert '272: {\"a\": (' not in out_pf",
    "'\"PERPETUAL-N1-W272\"' not in outn1_vac",
    'research/PERPETUAL_N1_W272_PREREG.md',
    '_w272bmc_20261018_probe_receipt.json',
    'W271_A = tuple(N1_BANDS[271]["a"])',
    'assert W271_A == (611_501, 613_500) and W271_B == (613_501, 613_700)',
    'assert fc_a == (613_701, 615_700) and hops_a == 1',
    'ARITH_A = (W271_A[1] + 1, W271_A[1] + WIDTH_A)',
    'assert owner_total == 261 and len(bmc_rows) == 90',
    'assert ordinal == 262',
    'for _w in (269, 270, 271):',
    'n1_w271_results.json',
    'w271_klift',
    '"W273p_A_naive"',
    '("w273", "w274")',
    'assert w271_total == 1_020_535 and w271_merged_n == 594_120',
]
MUST_NOT_CONTAIN = [
    'W271 pre-seat', '_w271bmc_20261018_probe_receipt', 'range(16, 271)',
    '271 not in N1_BANDS', '(604_901', '1_013_935', '587_520',
    'post-W270-REGISTERED', 'W270 probe receipt', 'TWENTIETH',
    '611_301..611_500', '611_301..613_300', '611_501..613_500',
    'assert 260 and', 'W272/W273', 'MSG-20261018-1605', 'W272p_',
    'w270_klift', 'W268_A', 'W272p_A_naive',
]

raw = open(SRC, "rb").read()
crlf = b"\r\n" in raw
body = raw.decode("utf-8")
if crlf:
    body = body.replace("\r\n", "\n")

for i, (old, new, expect) in enumerate(NEEDLES, 1):
    n = body.count(old)
    assert n == expect, f"needle#{i} count={n} expect={expect} :: head={old[:80]!r}"
    body = body.replace(old, new)
    print(f"needle#{i:02d} OK ({expect}x) {old[:48]!r}")

for m in MUST_CONTAIN:
    assert m in body, f"MUST_CONTAIN missing: {m!r}"
for m in MUST_NOT_CONTAIN:
    assert m not in body, f"MUST_NOT_CONTAIN leaked: {m!r}"

if crlf:
    body = body.replace("\n", "\r\n")
with open(DST, "wb") as f:
    f.write(body.encode("utf-8"))
py_compile.compile(DST, doraise=True)
print("BUILD OK ->", DST, "| EOL=crlf" if crlf else "| EOL=lf",
      "| bytes", len(body.encode('utf-8')), "| needles", len(NEEDLES))
