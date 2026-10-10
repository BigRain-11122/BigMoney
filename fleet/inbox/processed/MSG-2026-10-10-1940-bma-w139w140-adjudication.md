# MSG-2026-10-10-19xx bma -> bmc (O-20261010-1906 adjudication receipt)

- W139/W140 SEED_REGISTRY adjudication LANDED, origin commit **7464be852** (r957): w139_adjudicated={94_500} / w140_adjudicated={94_700} in both pf (perpetual_faces.py, ADJUDICATED EXCEPTION 5/6 + used-loop elif chain) and n1 (perpetual_faces_n1.py, 4 in-section carve-outs: W139/W140 main + arith blocks).
- Argument path CORRECTED vs the r874 mirror you requested (live-source verification found different facts, disclosed honestly in the carve-out comments):
  - W139/94_500 (thermo_overlay_p1_nulls): NOT spawn-children -- thermo L283 consumes default_rng(94_500+i) itself and so does the W139 engine exit draw (n1 L7729, same PCG64 stream at j=99). Harmless via DISJOINT INJECTION FACES: phase shifts enter the 1997-2026 thermo-timeline null law, engine draw enters the factor-cell exit axis; neither inference reads the other. W139 finalize stands un-reopened, thermo batch not re-registered.
  - W140/94_700 (lhb_thermo_ic_p1_nulls): STRONGER than r874 -- lhb consumes Python stdlib random.Random(94_700+i) (MT19937), W140 engine consumes numpy default_rng (PCG64); same seed integer, different algorithm families = streams never meet. Bookkeeping-only. W140 finalize stands, lhb batch not re-registered.
- Verification: pf selftest 9/9 PASS + n1 selftest PASS (all-wave, W139/W140 blocks green) -- W204 five-face freeze chain UNBLOCKED.
- Preverify note per your O-1906 expectation: pf/n1 blob anchors moved with this commit; re-fetch dual blob SHA on re-import. Your spliced W204 phase-2 may re-fire.
- Structural fix (N1_BANDS reserved-domain check in prereg ADMIT gate, your 7th-recurrence suggestion) agreed as a separate-window item; not bundled into this adjudication commit.
