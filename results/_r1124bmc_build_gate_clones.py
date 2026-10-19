# -*- coding: utf-8 -*-
# r1124 bm-c: build W279 sixgate + fivekeys clones from the r1118 W278 canons
# by COUNT-ASSERTED ORDERED TRANSFORM (E63 lineage; zero transcription --
# every needle count measured on the source text at build time; splice sha +
# fivekeys key anchors machine-read live). Splice landed face: the W279
# splice was authored 61a65dd55d and landed post-rebase as 3810f4a7ac
# (r1123 verify face; located by message grep per the r1123 next_pointer
# law -- never transcribe the pre-rebase sha). Engine burn batches
# 498d178d0b + 332e8e8656 (12/12 shards on origin, dir count 12 verified).
# CAB face this generation (12th consecutive): zero post-splice heals on
# pf/n1, zero pre-splice EDITOR heals (E63 23rd-gen editor CLEAN-AT-BIRTH);
# the r1123 needle preflight carried FIRST-RUN one disclosed table-heal
# (push-race- x2 = both delivery prose forms, expectation-table face only,
# zero canon anomalies) -- disclosed honestly in the cloned note prose.
# PART B anchors = W278 finalize actuals live-read from n1_w278_results.json
# this window, cross-checked against the r1123 next_pointer face (mu
# -0.09278575748129675 / sigma 0.24505493584785207 / a_p95 0.2844 /
# line_merged@609,520 1.1969 / se_mu 0.000314 / k_lift -0.0002 / ledger
# 1,035,935 / K=609,520 -- ALL verified equal this window).
import io, subprocess, json


def rep(t, old, new, expect, tag, log):
    n = t.count(old)
    assert n == expect, f"[{tag}] count {n} != {expect}: {old[:100]!r}"
    return t.replace(old, new), log + [f"{tag}: {n}x"]


def build(src, dst, reps):
    t = io.open(src, encoding="utf-8", newline="").read()
    log = []
    for old, new, expect, tag in reps:
        t, log = rep(t, old, new, expect, tag, log)
    io.open(dst, "w", encoding="utf-8", newline="").write(t)
    import py_compile
    py_compile.compile(dst, doraise=True)
    print(f"BUILD OK {dst} ({len(t.encode('utf-8'))}B)")
    return log


# ---------------- PART A: sixgate ----------------
SPLICE = subprocess.run(["git", "log", "--format=%H", "--grep=W279 FIVE-FACE FREEZE SPLICE", "-1"],
                        capture_output=True, text=True).stdout.strip()
assert SPLICE.startswith("3810f4a7ac"), SPLICE  # splice located by message; authored 61a65dd55d pre-rebase face
six_reps = [
 ("# r1118 bm-c: W278 PRE-FINALIZE six-gate receipt (standing law since W217", "# r1124 bm-c: W279 PRE-FINALIZE six-gate receipt (standing law since W217", 1, "hdr"),
 ("# debt; clone lineage _r1114bmc_w277_sixgate.py, 41st consecutive", "# debt; clone lineage _r1118bmc_w278_sixgate.py, 42nd consecutive", 1, "lineage"),
 ("# mtime-watch auto-ignite post-W278 splice (splice commit b6f486af35 landed", "# mtime-watch auto-ignite post-W279 splice (splice commit 3810f4a7ac landed", 1, "burn-a"),
 ("# first-try behind=0 on origin_base d2667773da after the mid-window bm-b race", "# behind=0 at push (authored 61a65dd55d, mid-window rebase per r1123 verify", 1, "burn-b"),
 ("# heal (gate0 fail-closed; discard-3 regenerable + ff per r609 gate0 law); engine", "# face); engine", 1, "burn-c"),
 ("# 60e630918f six + b965e2ecf0 six, both on origin; finalize not yet run).", "# 498d178d0b six + 332e8e8656 six, both on origin; finalize not yet run).", 1, "burn-d"),
 ("# CLEAN-AT-BIRTH FACE (11th consecutive) on ENGINE MECHANICS: the W278", "# CLEAN-AT-BIRTH FACE (12th consecutive) on ENGINE MECHANICS: the W279", 1, "cab-a"),
 ("# zero pre-splice authoring heals (needle preflight FIRST-RUN ZERO-MISMATCH", "# zero pre-splice editor heals (E63 23rd-gen editor CLEAN-AT-BIRTH; needle", 1, "cab-b"),
 ("# r1077 measured law = zero table-heals this generation; all count-asserted", "# preflight FIRST-RUN one disclosed table-heal = push-race- x2 delivery prose", 1, "cab-c"),
 ("# editor reps first-try; phase4 zero-residual + phase5 presence gates ALL", "# forms, expectation-table face only, zero canon anomalies; phase4", 1, "cab-d"),
 ("# PASS at editor time; setwave root-cure held at the birth station", "# zero-residual + phase5 presence gates ALL PASS; setwave root-cure held", 1, "cab-e"),
 ("# (_set_wave(277):1 / _set_wave(276):0 / _set_wave(275):0", "# at the birth station (_set_wave(278):1 / _set_wave(277):0 / _set_wave(276):0", 1, "cab-f"),
 ("# (c) segment-scoped birth-station presence gates after the W277 block:", "# (c) segment-scoped birth-station presence gates after the W278 block:", 1, "g1c"),
 ("# _set_wave(278) present, _set_wave(277)/_set_wave(276) absent.", "# _set_wave(279) present, _set_wave(278)/_set_wave(277) absent.", 1, "g1d"),
 ("SPLICE = 'b6f486af35fcfbffcc704613a4c3369356c831ea'", "SPLICE = '" + SPLICE + "'", 1, "splice-const"),
 ("fr = json.load(io.open('results/_w278bmc_freeze_receipt.json', encoding='utf-8'))", "fr = json.load(io.open('results/_w279bmc_freeze_receipt.json', encoding='utf-8'))", 1, "receipt-path"),
 ("i = n1t.find('278: {\"batch\": \"PERPETUAL-N1-W278\"')", "i = n1t.find('279: {\"batch\": \"PERPETUAL-N1-W279\"')", 1, "row-find"),
 ("assert i >= 0, 'W278 wave row missing'", "assert i >= 0, 'W279 wave row missing'", 1, "row-msg"),
 ("if '279: {' in seg:", "if '280: {' in seg:", 1, "seg-next"),
 ("    seg = seg[:seg.find('279: {')]", "    seg = seg[:seg.find('280: {')]", 1, "seg-trim"),
 ("    'a_seed_base_626901': '626901' in seg,", "    'a_seed_base_629101': '629101' in seg,", 1, "rf-a"),
 ("    'b_exit_seed_base_628901': '628901' in seg,", "    'b_exit_seed_base_631101': '631101' in seg,", 1, "rf-b"),
 ("    'shard_subdir_n1_w278': 'n1_w278' in seg,", "    'shard_subdir_n1_w279': 'n1_w279' in seg,", 1, "rf-sd"),
 ("    'out_name_n1_w278_results': 'n1_w278_results.json' in seg,", "    'out_name_n1_w279_results': 'n1_w279_results.json' in seg,", 1, "rf-out"),
 ("f1 = 'base=626901 span=2000'", "f1 = 'base=629101 span=2000'", 1, "f1"),
 ("f2 = 'base=628901 span=200'", "f2 = 'base=631101 span=200'", 1, "f2"),
 ("# prior-wave W277 registry boundary faces kept", "# prior-wave W278 registry boundary faces kept", 1, "bnd-comment"),
 ("m277 = re.search(r'277: \\{\"batch\": \"PERPETUAL-N1-W277\"', n1t)", "m278 = re.search(r'278: \\{\"batch\": \"PERPETUAL-N1-W278\"', n1t)", 1, "m277"),
 ("w277_seg = n1t[m277.start():m277.start() + 9000] if m277 else ''", "w278_seg = n1t[m278.start():m278.start() + 9000] if m278 else ''", 1, "seg277"),
 ("if '278: {' in w277_seg:", "if '279: {' in w278_seg:", 1, "seg277-next"),
 ("    w277_seg = w277_seg[:w277_seg.find('278: {')]", "    w278_seg = w278_seg[:w278_seg.find('279: {')]", 1, "seg277-trim"),
 ("boundary = bool(m277) and '624701' in w277_seg and '626701' in w277_seg", "boundary = bool(m278) and '626901' in w278_seg and '628901' in w278_seg", 1, "boundary"),
 ("k277pos = n1t.rfind('_set_wave(277)')", "k278pos = n1t.rfind('_set_wave(278)')", 1, "kpos"),
 ("after277 = n1t[k277pos + len('_set_wave(277)'):", "after278 = n1t[k278pos + len('_set_wave(278)'):", 1, "afterpos"),
 ("    'w278_block_has_278': '_set_wave(278)' in after277,", "    'w279_block_has_279': '_set_wave(279)' in after278,", 1, "swp1"),
 ("    'w278_block_has_277': '_set_wave(277)' in after277,", "    'w279_block_has_278': '_set_wave(278)' in after278,", 1, "swp2"),
 ("    'w278_block_has_276': '_set_wave(276)' in after277,", "    'w279_block_has_277': '_set_wave(277)' in after278,", 1, "swp3"),
 ("    'whole_file_278_count': n1t.count('_set_wave(278)'),", "    'whole_file_279_count': n1t.count('_set_wave(279)'),", 1, "swc1"),
 ("    'whole_file_277_count': n1t.count('_set_wave(277)'),", "    'whole_file_278_count': n1t.count('_set_wave(278)'),", 1, "swc2"),
 ("    'whole_file_276_count': n1t.count('_set_wave(276)'),", "    'whole_file_277_count': n1t.count('_set_wave(277)'),", 1, "swc3"),
 ("setwave_ok = (setwave_presence['w278_block_has_278']", "setwave_ok = (setwave_presence['w279_block_has_279']", 1, "swo1"),
 ("              and not setwave_presence['w278_block_has_277']", "              and not setwave_presence['w279_block_has_278']", 1, "swo2"),
 ("              and not setwave_presence['w278_block_has_276']", "              and not setwave_presence['w279_block_has_277']", 1, "swo3"),
 ("              and setwave_presence['whole_file_278_count'] == 1", "              and setwave_presence['whole_file_279_count'] == 1", 1, "swo4"),
 ("              and setwave_presence['whole_file_277_count'] == 1", "              and setwave_presence['whole_file_278_count'] == 1", 1, "swo5"),
 ("              and setwave_presence['whole_file_276_count'] == 1)", "              and setwave_presence['whole_file_277_count'] == 1)", 1, "swo6"),
 ("sd = 'results/p2cal_ext/n1_w278'", "sd = 'results/p2cal_ext/n1_w279'", 1, "sharddir"),
 ("'--prereg', 'research/PERPETUAL_N1_W278_PREREG.md'],", "'--prereg', 'research/PERPETUAL_N1_W279_PREREG.md'],", 1, "prereg"),
 ("os.path.exists('results/_w278bmc_derive_editor.py')", "os.path.exists('results/_w279bmc_derive_editor.py')", 1, "ev-editor"),
 ("and os.path.exists('results/_r1118bmc_derive_editor_log.txt')", "and os.path.exists('results/_r1123bmc_derive_editor_log.txt')", 1, "ev-log"),
 ("and os.path.exists('results/_r1118bmc_needle_preflight.json'))", "and os.path.exists('results/_r1123bmc_needle_preflight.json'))", 1, "ev-preflight"),
 ("    'r1118 GATE-1 CLEAN-AT-BIRTH FACE (11th consecutive) on ENGINE MECHANICS: '", "    'r1124 GATE-1 CLEAN-AT-BIRTH FACE (12th consecutive) on ENGINE MECHANICS: '", 1, "note-1"),
 ("    'the W278 splice carried ZERO heals of any class -- zero post-splice '", "    'the W279 splice carried ZERO heals of any class -- zero post-splice '", 1, "note-2"),
 ("    'heals on pf/n1, zero pre-splice authoring heals (preflight FIRST-RUN '", "    'heals on pf/n1, zero pre-splice editor heals (E63 23rd-gen editor '", 1, "note-3"),
 ("    'ZERO-MISMATCH r1077 measured law, zero table-heals; all count-asserted '", "    'CLEAN-AT-BIRTH; needle preflight FIRST-RUN one disclosed table-heal '", 1, "note-4"),
 ("    'editor reps first-try). Phase4 zero-residual + phase5 presence gates '", "    '= push-race- x2 delivery prose forms, expectation-table face only, '", 1, "note-5"),
 ("    'ALL PASS at editor time. Gate asserts worktree sha16 == freeze-receipt '", "    'zero canon anomalies). Phase4 zero-residual + phase5 presence gates '", 1, "note-6"),
 ("    'post faces, CR-normalized worktree == CR-normalized landed blob @ '", "    'ALL PASS at editor time. Gate asserts worktree sha16 == freeze-receipt '", 1, "note-7"),
 ("    'splice commit b6f486af35 (landed = LF storage face, raw sha16 '", "    'post faces, CR-normalized worktree == CR-normalized landed blob @ '", 1, "note-8"),
 ("    'recorded; splice landed first-try behind=0 on origin_base d2667773da '", "    'splice commit 3810f4a7ac (landed = LF storage face, raw sha16 '", 1, "note-9"),
 ("    'after the bm-b race heal (gate0 fail-closed, discard-3 regenerable + ff '", "    'recorded; engine batches 498d178d0b + 332e8e8656 self-committed '", 1, "note-10"),
 ("    'per r609 gate0 law; engine batches 60e630918f + b965e2ecf0 '", "    'post-splice), segment-scoped birth-station presence gates green, '", 1, "note-11"),
 ("    'self-committed post-splice), segment-scoped birth-station presence gates green, editor/preflight/log evidence files present.'", "    'editor/preflight/log evidence files present.'", 1, "note-12"),
 ("# ledger_pre: machine-read from W277 finalize product (r587 never-transcribe)", "# ledger_pre: machine-read from W278 finalize product (r587 never-transcribe)", 1, "ledger-comment"),
 ("w277 = json.load(io.open('results/perpetual_faces/n1_w277_results.json',", "w278 = json.load(io.open('results/perpetual_faces/n1_w278_results.json',", 1, "prior-load"),
 ("ledger_w277 = _find_ledger(w277)", "ledger_w278 = _find_ledger(w278)", 1, "ledger-var"),
 ("assert ledger_w277 is not None, 'W277 ledger face missing'", "assert ledger_w278 is not None, 'W278 ledger face missing'", 1, "ledger-assert"),
 ("prev_total = ledger_w277['total']", "prev_total = ledger_w278['total']", 1, "prev-total"),
 ("prev_k = w277['null_pool_cumulative']['merged']['n_values']", "prev_k = w278['null_pool_cumulative']['merged']['n_values']", 1, "prev-k"),
 ("up = fr['w277_upstream']", "up = fr['w278_upstream']", 1, "upstream-face"),
 ("w277_finalize_present = os.path.exists('results/perpetual_faces/n1_w277_results.json')", "w278_finalize_present = os.path.exists('results/perpetual_faces/n1_w278_results.json')", 1, "prior-present"),
 ('"wave": 278,', '"wave": 279,', 1, "wave-out"),
 (' "phase": "PRE-FINALIZE six-gate (r1118 bm-c own-seat window, 41st consecutive correct-phase target; standing law -- engine self-burn 12/12 landed post-W278 splice b6f486af35 clean-at-birth 11th generation on engine mechanics, finalize not yet run)",',
  ' "phase": "PRE-FINALIZE six-gate (r1124 bm-c own-seat window, 42nd consecutive correct-phase target; standing law -- engine self-burn 12/12 landed post-W279 splice 3810f4a7ac clean-at-birth 12th generation on engine mechanics, finalize not yet run)",', 1, "phase-out"),
 ("      and w277_finalize_present", "      and w278_finalize_present", 1, "prior-present-ok"),
 ('  "w277_finalize_product_present": w277_finalize_present,', '  "w278_finalize_product_present": w278_finalize_present,', 1, "prior-out"),
 ('  "source": "W277 finalize actuals machine-read from n1_w277_results.json (r587 law)",', '  "source": "W278 finalize actuals machine-read from n1_w278_results.json (r587 law)",', 1, "source-out"),
 ('  "anchor": "W277 finalize (bm-c r1114-continuation one-pass 1,033,735/K=607,320) honored per freeze receipt w277_upstream face",', '  "anchor": "W278 finalize (bm-c r1119 one-pass 1,035,935/K=609,520) honored per freeze receipt w278_upstream face",', 1, "anchor-out"),
 ("and upstream_match and prev_total == 1033735 and prev_k == 607320)", "and upstream_match and prev_total == 1035935 and prev_k == 609520)", 1, "ledger-pre-assert"),
 ('  "prior_wave_277_boundary_kept": boundary,', '  "prior_wave_278_boundary_kept": boundary,', 1, "bnd-key"),
 ('   "note": "freeze-time FREE evidence consumed verbatim from _w278bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",', '   "note": "freeze-time FREE evidence consumed verbatim from _w279bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",', 1, "seed-note"),
 ('    "source": "freeze receipt post faces (zero heals of any class this generation -- zero post-splice engine-mechanics heals, zero pre-splice authoring heals, needle preflight FIRST-RUN ZERO-MISMATCH r1077 measured law = zero table-heals; setwave root cure held at the birth station)",',
  '    "source": "freeze receipt post faces (zero heals of any class this generation -- zero post-splice engine-mechanics heals, zero pre-splice editor heals (E63 23rd-gen editor CLEAN-AT-BIRTH), needle preflight FIRST-RUN one disclosed table-heal = push-race- x2 delivery prose forms, expectation-table face only; setwave root cure held at the birth station)",', 1, "cab-source"),
 ('   "a_seed_base": 626901, "b_exit_seed_base": 628901,', '   "a_seed_base": 629101, "b_exit_seed_base": 631101,', 1, "wcr-bases"),
 ('   "shard_subdir": "n1_w278", "out_name": "n1_w278_results.json",', '   "shard_subdir": "n1_w279", "out_name": "n1_w279_results.json",', 1, "wcr-subdir"),
 ("   \"seed_bases_match_freeze_bands\": fr['bands']['a_lo'] == 626901 and fr['bands']['b_lo'] == 628901,", "   \"seed_bases_match_freeze_bands\": fr['bands']['a_lo'] == 629101 and fr['bands']['b_lo'] == 631101,", 1, "wcr-match"),
 ("io.open('results/_r1118bmc_w278_sixgate.json', 'w', encoding='utf-8').write(", "io.open('results/_r1124bmc_w279_sixgate.json', 'w', encoding='utf-8').write(", 1, "out-path"),
]
log_a = build("results/_r1118bmc_w278_sixgate.py", "results/_r1124bmc_w279_sixgate.py", six_reps)
print("\n".join(log_a))

# ---------------- PART B: fivekeys ----------------
# machine-verify the W278 key anchors live from the finalize product (zero-transcription)
d7 = json.load(io.open("results/perpetual_faces/n1_w278_results.json", encoding="utf-8"))
p = d7["null_pool_cumulative"]; s = d7["skill_line_v2_k_lift"]; f = d7["families"]["A_random_engine_exit"]
ANCH = {
 "mu": p["merged"]["mu"], "sigma": p["merged"]["sigma"],
 "a_p95": f["full_sharpe_p95"], "line_merged": s["line_merged_609520"],
 "se_mu": p["se_mu_at_k609520"], "klift": s["line_delta_k_lift"],
 "k": p["merged"]["n_values"],
}


def _fl(o):
    if isinstance(o, dict):
        if "ledger" in o and isinstance(o["ledger"], dict) and "total" in o["ledger"]:
            return o["ledger"]
        for v in o.values():
            r = _fl(v)
            if r: return r
    elif isinstance(o, list):
        for v in o:
            r = _fl(v)
            if r: return r
    return None


ANCH["prev_total"] = _fl(d7)["total"]
assert ANCH["prev_total"] == 1035935 and ANCH["k"] == 609520, (ANCH["prev_total"], ANCH["k"])
assert abs(ANCH["mu"] - (-0.09278575748129675)) < 1e-12, ANCH["mu"]
assert abs(ANCH["sigma"] - 0.24505493584785207) < 1e-12, ANCH["sigma"]
assert ANCH["a_p95"] == 0.2844, ANCH["a_p95"]
assert ANCH["line_merged"] == 1.1969, ANCH["line_merged"]
assert ANCH["se_mu"] == 0.000314, ANCH["se_mu"]
assert ANCH["klift"] == -0.0002, ANCH["klift"]
print("W278 key anchors machine-verified:", {k: v for k, v in ANCH.items()})

fk_reps = [
 ('"""r1118 bm-c: W278 five-prediction-key machine assertion (prereg sec.5 vs finalize face).', '"""r1124 bm-c: W279 five-prediction-key machine assertion (prereg sec.5 vs finalize face).', 1, "fk-doc"),
 ("Read-only against results/perpetual_faces/n1_w278_results.json + frozen prereg keys.", "Read-only against results/perpetual_faces/n1_w279_results.json + frozen prereg keys.", 1, "fk-res-doc"),
 ("W278 prereg froze its sec.5 keys on W277 finalize actuals (live-chain-head basis;", "W279 prereg froze its sec.5 keys on W278 finalize actuals (live-chain-head basis;", 1, "fk-basis"),
 ("keys machine-read from n1_w277_results.json, r587 never-transcribe law --", "keys machine-read from n1_w278_results.json, r587 never-transcribe law --", 1, "fk-keys-doc"),
 ("constants below are cross-check anchors only, live-extracted from the W277", "constants below are cross-check anchors only, live-extracted from the W278", 1, "fk-anchors-doc1"),
 ("finalize product this window: mu -0.09277044 / sigma 0.24508694 / a_p95 0.3095 /", "finalize product this window: mu -0.09278576 / sigma 0.24505494 / a_p95 0.2844 /", 1, "fk-anchors-doc2"),
 ("line_merged 1.197 / se_mu 0.000314 / k_lift 0.0 -- FULL-PRECISION machine-read", "line_merged 1.1969 / se_mu 0.000314 / k_lift -0.0002 -- FULL-PRECISION machine-read", 1, "fk-anchors-doc3"),
 ("Writes results/_r1118bmc_w278_fivekeys.json receipt. Ledger +0, marks +0.", "Writes results/_r1124bmc_w279_fivekeys.json receipt. Ledger +0, marks +0.", 1, "fk-out-doc"),
 ("Clone lineage: _r1114bmc_w277_fivekeys.py (canon, prior-wave keys variant).", "Clone lineage: _r1118bmc_w278_fivekeys.py (canon, prior-wave keys variant).", 1, "fk-lineage"),
 ('RES = "results/perpetual_faces/n1_w278_results.json"', 'RES = "results/perpetual_faces/n1_w279_results.json"', 1, "fk-res"),
 ('PRIOR = "results/perpetual_faces/n1_w277_results.json"', 'PRIOR = "results/perpetual_faces/n1_w278_results.json"', 1, "fk-prior"),
 ('OUT = "results/_r1118bmc_w278_fivekeys.json"', 'OUT = "results/_r1124bmc_w279_fivekeys.json"', 1, "fk-out"),
 ("# Frozen prediction keys = W277 finalize actuals (machine-read below; the", "# Frozen prediction keys = W278 finalize actuals (machine-read below; the", 1, "fk-frozen"),
 ("full-precision anchors machine-read from the W277 finalize product this", "full-precision anchors machine-read from the W278 finalize product this", 1, "fk-prec"),
 ("KEY_MU_MERGED_W277 = -0.09277043683725218   # W277 finalize merged mu, K=607,320", "KEY_MU_MERGED_W278 = %r   # W278 finalize merged mu, K=609,520" % ANCH["mu"], 1, "fk-kmu"),
 ("KEY_SIGMA_W277 = 0.24508693698115214", "KEY_SIGMA_W278 = %r" % ANCH["sigma"], 1, "fk-ksig"),
 ("KEY_A_P95_W277 = 0.3095", "KEY_A_P95_W278 = %r" % ANCH["a_p95"], 1, "fk-kp95"),
 ("KEY_LINE_W277_MERGED = 1.197", "KEY_LINE_W278_MERGED = %r" % ANCH["line_merged"], 1, "fk-kline"),
 ("KEY_SE_MU_W277 = 0.000314", "KEY_SE_MU_W278 = %r" % ANCH["se_mu"], 1, "fk-kse"),
 ("KEY_KLIFT_W277 = 0.0", "KEY_KLIFT_W278 = %r" % ANCH["klift"], 1, "fk-kkl"),
 ('w277 = json.load(open(PRIOR, encoding="utf-8"))', 'w278 = json.load(open(PRIOR, encoding="utf-8"))', 1, "fk-load"),
 ('p1 = w277["null_pool_cumulative"]; s1 = w277["skill_line_v2_k_lift"]', 'p1 = w278["null_pool_cumulative"]; s1 = w278["skill_line_v2_k_lift"]', 1, "fk-p1"),
 ('f1 = w277["families"]["A_random_engine_exit"]', 'f1 = w278["families"]["A_random_engine_exit"]', 1, "fk-f1"),
 ('k_line_merged = s1["line_merged_607320"]', 'k_line_merged = s1["line_merged_609520"]', 1, "fk-kline-read"),
 ('k_se_mu = p1["se_mu_at_k607320"]', 'k_se_mu = p1["se_mu_at_k609520"]', 1, "fk-kse-read"),
 ("KEY_MU_MERGED_W277", "KEY_MU_MERGED_W278", 2, "fk-kmu-ref"),
 ("KEY_SIGMA_W277", "KEY_SIGMA_W278", 2, "fk-ksig-ref"),
 ("KEY_A_P95_W277", "KEY_A_P95_W278", 2, "fk-kp95-ref"),
 ("KEY_LINE_W277_MERGED", "KEY_LINE_W278_MERGED", 2, "fk-kline-ref"),
 ("KEY_SE_MU_W277", "KEY_SE_MU_W278", 2, "fk-kse-ref"),
 ("KEY_KLIFT_W277", "KEY_KLIFT_W278", 2, "fk-kkl-ref"),
 ('se_mu = pool["se_mu_at_k609520"]', 'se_mu = pool["se_mu_at_k611720"]', 1, "fk-semu-read"),
 ('line_pre = sl["line_pre_w278"]', 'line_pre = sl["line_pre_w279"]', 1, "fk-lpre-read"),
 ('line_merged = sl["line_merged_609520"]', 'line_merged = sl["line_merged_611720"]', 1, "fk-lm-read"),
 ('w278_mu = pool["w278_only"]["mu"]', 'w279_mu = pool["w279_only"]["mu"]', 1, "fk-wonly"),
 ('gap1 = abs(w278_mu - merged_mu)', 'gap1 = abs(w279_mu - merged_mu)', 1, "fk-wonly-gap1"),
 ("# key 1: W278-only mu vs merged mu gap", "# key 1: W279-only mu vs merged mu gap", 1, "fk-k1c"),
 ('checks.append(("key1_w278_vs_merged_mu_gap"', 'checks.append(("key1_w279_vs_merged_mu_gap"', 1, "fk-k1"),
 ("# key 1b: merged mu vs W277 frozen key (prereg keys = prior-wave actuals)", "# key 1b: merged mu vs W278 frozen key (prereg keys = prior-wave actuals)", 1, "fk-k1bc"),
 ('checks.append(("key1b_merged_vs_w277_key"', 'checks.append(("key1b_merged_vs_w278_key"', 1, "fk-k1b"),
 ("# key 2: sigma rel change vs W277 key", "# key 2: sigma rel change vs W278 key", 1, "fk-k2c"),
 ("# key 3: A-band p95 vs W277 key (double-direction band)", "# key 3: A-band p95 vs W278 key (double-direction band)", 1, "fk-k3c"),
 ("# key 5: se_mu narrowing vs W277 (se_mu chain face, sec.5 prose)", "# key 5: se_mu narrowing vs W278 (se_mu chain face, sec.5 prose)", 1, "fk-k5c"),
 ('"wave": 278,', '"wave": 279,', 1, "fk-wave"),
 ('"se_mu_k609520": se_mu', '"se_mu_k611720": se_mu', 1, "fk-semu-out"),
 ('"w278_only": {"mu": w278_mu, "sigma": pool["w278_only"]["sigma"]}', '"w279_only": {"mu": w279_mu, "sigma": pool["w279_only"]["sigma"]}', 1, "fk-wonly-out"),
 ('"line_pre_w278": line_pre,', '"line_pre_w279": line_pre,', 1, "fk-lpre-out"),
 ('"line_merged_609520": line_merged,', '"line_merged_611720": line_merged,', 1, "fk-lm-out"),
 ('"keys_anchor": ("W277 finalize actuals machine-read from n1_w277_results.json "', '"keys_anchor": ("W278 finalize actuals machine-read from n1_w278_results.json "', 1, "fk-anchor"),
 ("(r587 law) -- W278 prereg froze sec.5 keys on W277 actuals ", "(r587 law) -- W279 prereg froze sec.5 keys on W278 actuals ", 1, "fk-basis-out"),
 ('(live-chain-head basis; W277 finalize landed pre-draft r1116)")', '(live-chain-head basis; W278 finalize landed pre-draft r1122)")', 1, "fk-basis2"),
 ('"ledger_identity": {"prev_total": 1033735, "batch_trials": 2200,', '"ledger_identity": {"prev_total": 1035935, "batch_trials": 2200,', 1, "fk-led"),
 ('"total": 1035935,', '"total": 1038135,', 1, "fk-led-tot"),
 ('"exact": (1033735 + 2200) == 1035935},', '"exact": (1035935 + 2200) == 1038135},', 1, "fk-led-ex"),
 ('"merged_k_identity": {"prev_k": 607320, "batch": 2200, "merged_k": merged_k,', '"merged_k_identity": {"prev_k": 609520, "batch": 2200, "merged_k": merged_k,', 1, "fk-kid"),
 ('"exact": (607320 + 2200) == merged_k},', '"exact": (609520 + 2200) == merged_k},', 1, "fk-kid-ex"),
 ('"keys_source": "W277 finalize actuals machine-read from n1_w277_results.json (r587 law)",', '"keys_source": "W278 finalize actuals machine-read from n1_w278_results.json (r587 law)",', 1, "fk-ksrc"),
]
log_b = build("results/_r1118bmc_w278_fivekeys.py", "results/_r1124bmc_w279_fivekeys.py", fk_reps)
print("\n".join(log_b))
print("CLONES BUILT OK")
