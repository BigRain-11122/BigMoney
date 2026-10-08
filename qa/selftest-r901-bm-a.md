# r901 bm-a W193 five-face freeze — QA evidence (takeover closeout)

- Round: r901 (bm-a, same-label takeover of the dead r901 session —
  prereg freeze landed+pushed 9c0c089b8 pre-death; this window landed
  the remaining five faces).
- Freeze tool: `results/_r901bma_w193_freeze_edits.py` (r787 bm-c
  direct-author machinery, count-asserted roll of the physical W192
  fragments; 91+34+24+9 replacements all count-asserted; first run
  FAIL-at-gates zero-writes x1 (sorted-needle count + CR/LF scan
  false-positive family), fixed gates, second run LIVE WRITES rc0).
- Receipt: `results/_r901bma_w193_freeze_receipt.json` (5/5 PASS
  prints; origin vacancy + seat sha 9df3078c5 ancestor + post-import
  guard rows 190->191, W193/W192/W191 byte-intact).
- Bands: A=439_404..441_403 / B=441_404..441_603, staircase FIFTY-THIRD
  (E36 card), hops 1/1, ADMIT receipt
  `results/_r900bma_w193_probe_receipt.json` machine-read.
- W192 upstream: bm-c five-face registered f8703842c, finalize IN
  FLIGHT — honest in-flight annotation per frozen prereg sec.0; W193
  finalize key-order precondition checks the W192 output at run time
  (FAIL-CLOSED r307 two-state law).
- pf selftest: 9/9 PASS
  (`perpetual_faces selftest: 9/9 PASS (registry/seed-bands+3c-W6+3d-W7-packing/pool/state/py-face/materializer-expansion/pool-format-probe+writer-roundtrip/skip-semantics-pin-D-20261002-05; 4b park_note + 4c ghost claimable legs)`).
- n1 selftest: PASS, full face chain W2..W193 incl the new W193
  materializer face (claim tail: "+ W193 materializer face [same guard
  set, dep=W17..W191 outputs ALL PRESENT (landed net chain head
  833,536 = W191 bm-a r895 one-pass, K=418,120 merged pool) + W192
  IN-FLIGHT upstream seat ... ONE HUNDRED-AND-NINETY-THIRD
  ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 182 +
  candidate) bm-a's one-hundred-eighth owned claim ... FIFTY-THIRD ...
  r901 bm-a]").
- Pre-existing red fixed this window (r874 precedent second instance,
  found by the five-face selftest): pf+n1 W137 adjudicated set
  extended {94_100} -> {94_100, 94_200} — the r899 F1-BULL-COND-P1
  seed registration (f1_bull_cond_p1_null_base=94_200, science_gates)
  landed inside the ALREADY-BURNED W137 B band 94_001..94_200 at
  j=199 (band tail); spawn-children-only consumption, W137 finalize
  stands un-reopened, F1 batch NOT re-registered; full disclosure in
  the pf-level ADJUDICATED EXCEPTION 3 comment + n1 mirror.
- Inherited-defect fix disclosed: the r787-lineage W192 face's
  arith_a190/arith_b190 CLEAN asserts referenced the PRIOR face's
  variables; the W193 face rolls them to its OWN arith_a192/arith_b192
  (the W191-face original correct pattern).
