# -*- coding: utf-8 -*-
# r1114 bm-c: build W277 sixgate + fivekeys clones from the r1111 W276 canons
# by COUNT-ASSERTED ORDERED TRANSFORM (E63 lineage; zero transcription --
# every needle count measured on the source text at build time; splice sha +
# fivekeys key anchors machine-read live). Same-window heals disclosed:
# lagged label faces (prior_wave_274 key -> prior_wave_276, assert message,
# wave_configs_row stale prior-wave values -> current-wave W277 values with
# match=True, seed_admit note receipt filename, ledger_pre comment, key-1b
# comment, setwave station comment) rolled to current-generation truth;
# W277 editor 2-disclosed-table-heals face recorded honestly.
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
SPLICE = subprocess.run(["git", "log", "--format=%H", "--grep=W277 FIVE-FACE FREEZE SPLICE LANDED", "-1"],
                       capture_output=True, text=True).stdout.strip()
assert SPLICE.startswith("9e53371814"), SPLICE  # splice commit located by message (machine-read)
six_reps = [
 ("# r1111 bm-c: W276 PRE-FINALIZE six-gate receipt (standing law since W217", "# r1114 bm-c: W277 PRE-FINALIZE six-gate receipt (standing law since W217", 1, "hdr"),
 ("# debt; clone lineage _r1108bmc_w275_sixgate.py, 39th consecutive", "# debt; clone lineage _r1111bmc_w276_sixgate.py, 40th consecutive", 1, "lineage"),
 ("# mtime-watch auto-ignite post-W276 splice (splice commit 354a645155 landed", "# mtime-watch auto-ignite post-W277 splice (splice commit 9e53371814 landed", 1, "burnface-a"),
 ("# on the ff'd base 7a70aee504 after splice gate0 caught the mid-window bm-a", "# first-try behind=0 on origin_base 5b2b2950f1 with no mid-window race;", 1, "burnface-b"),
 ("# r1073 chain fail-closed zero-disk-pollution, re-ran clean; engine", "# engine appender shards self-commit per the W272 estate precedent", 1, "burnface-c"),
 ("# appender shards self-commit per the W272 estate precedent; finalize not", "# (batches 0df07c846b six + 644b4f8459 six, both on origin; finalize not", 1, "burnface-d"),
 ("# CLEAN-AT-BIRTH FACE (9th consecutive) on ENGINE MECHANICS: the W276", "# CLEAN-AT-BIRTH FACE (10th consecutive) on ENGINE MECHANICS: the W277", 1, "cab-hdr"),
 ("# splice carried ZERO heals of any class -- zero post-splice heals on", "# splice carried ZERO canon heals -- zero post-splice heals on pf/n1,", 1, "cab-2"),
 ("# pf/n1, zero pre-splice authoring heals (all count-asserted editor reps", "# zero canon anomalies (2 disclosed pre-splice editor gate-region", 1, "cab-3"),
 ("# first-try; the W275-generation date-roll rep was DROPPED count-0 per the", "# table-heals = expectation-table misreads, faces absent from canon; all", 1, "cab-4"),
 ("# measured 20261019==20261019 same-date fact, disclosed in the editor", "# count-asserted editor reps first-try; phase4 zero-residual + phase5", 1, "cab-5"),
 ("# header); phase4 zero-residual + phase5 presence gates ALL PASS at editor", "# presence gates ALL PASS at editor time; setwave root-cure held at the", 1, "cab-6"),
 ("# time; setwave root-cure held at the birth station (_set_wave(275):1 /", "# birth station (_set_wave(276):1 / _set_wave(275):0 / _set_wave(274):0", 1, "cab-7"),
 ("# _set_wave(274):0 / _set_wave(273):0 whole-file).", "# whole-file).", 1, "cab-8"),
 ("# (c) segment-scoped birth-station presence gates after the W274 block:", "# (c) segment-scoped birth-station presence gates after the W276 block:", 1, "g1c"),
 ("# _set_wave(276) present, _set_wave(275)/_set_wave(274) absent.", "# _set_wave(277) present, _set_wave(276)/_set_wave(275) absent.", 1, "g1d"),
 ("SPLICE = '354a645155c8206a71635572534753b3c6c08c28'", "SPLICE = '" + SPLICE + "'", 1, "splice-const"),
 ("fr = json.load(io.open('results/_w276bmc_freeze_receipt.json', encoding='utf-8'))", "fr = json.load(io.open('results/_w277bmc_freeze_receipt.json', encoding='utf-8'))", 1, "receipt-path"),
 ("i = n1t.find('276: {\"batch\": \"PERPETUAL-N1-W276\"')", "i = n1t.find('277: {\"batch\": \"PERPETUAL-N1-W277\"')", 1, "row-find"),
 ("assert i >= 0, 'W275 wave row missing'", "assert i >= 0, 'W277 wave row missing'", 1, "row-msg"),
 ("if '277: {' in seg:", "if '278: {' in seg:", 1, "seg-next"),
 ("    seg = seg[:seg.find('277: {')]", "    seg = seg[:seg.find('278: {')]", 1, "seg-trim"),
 ("    'a_seed_base_622501': '622501' in seg,", "    'a_seed_base_624701': '624701' in seg,", 1, "rf-a"),
 ("    'b_exit_seed_base_624501': '624501' in seg,", "    'b_exit_seed_base_626701': '626701' in seg,", 1, "rf-b"),
 ("    'shard_subdir_n1_w276': 'n1_w276' in seg,", "    'shard_subdir_n1_w277': 'n1_w277' in seg,", 1, "rf-sd"),
 ("    'out_name_n1_w276_results': 'n1_w276_results.json' in seg,", "    'out_name_n1_w277_results': 'n1_w277_results.json' in seg,", 1, "rf-out"),
 ("f1 = 'base=622501 span=2000'", "f1 = 'base=624701 span=2000'", 1, "f1"),
 ("f2 = 'base=624501 span=200'", "f2 = 'base=626701 span=200'", 1, "f2"),
 ("# prior-wave W274 registry boundary faces kept", "# prior-wave W276 registry boundary faces kept", 1, "bnd-comment"),
 ("m275 = re.search(r'275: \\{\"batch\": \"PERPETUAL-N1-W275\"', n1t)", "m276 = re.search(r'276: \\{\"batch\": \"PERPETUAL-N1-W276\"', n1t)", 1, "m275"),
 ("w275_seg = n1t[m275.start():m275.start() + 9000] if m275 else ''", "w276_seg = n1t[m276.start():m276.start() + 9000] if m276 else ''", 1, "seg275"),
 ("if '276: {' in w275_seg:", "if '277: {' in w276_seg:", 1, "seg275-next"),
 ("    w275_seg = w275_seg[:w275_seg.find('276: {')]", "    w276_seg = w276_seg[:w276_seg.find('277: {')]", 1, "seg275-trim"),
 ("boundary = bool(m275) and '620301' in w275_seg and '622301' in w275_seg", "boundary = bool(m276) and '622501' in w276_seg and '624501' in w276_seg", 1, "boundary"),
 ("k275pos = n1t.rfind('_set_wave(275)')", "k276pos = n1t.rfind('_set_wave(276)')", 1, "kpos"),
 ("after275 = n1t[k275pos + len('_set_wave(275)'):", "after276 = n1t[k276pos + len('_set_wave(276)'):", 1, "afterpos"),
 ("    'w276_block_has_276': '_set_wave(276)' in after275,", "    'w277_block_has_277': '_set_wave(277)' in after276,", 1, "swp1"),
 ("    'w276_block_has_275': '_set_wave(275)' in after275,", "    'w277_block_has_276': '_set_wave(276)' in after276,", 1, "swp2"),
 ("    'w276_block_has_274': '_set_wave(274)' in after275,", "    'w277_block_has_275': '_set_wave(275)' in after276,", 1, "swp3"),
 ("    'whole_file_276_count': n1t.count('_set_wave(276)'),", "    'whole_file_277_count': n1t.count('_set_wave(277)'),", 1, "swc1"),
 ("    'whole_file_275_count': n1t.count('_set_wave(275)'),", "    'whole_file_276_count': n1t.count('_set_wave(276)'),", 1, "swc2"),
 ("    'whole_file_274_count': n1t.count('_set_wave(274)'),", "    'whole_file_275_count': n1t.count('_set_wave(275)'),", 1, "swc3"),
 ("setwave_ok = (setwave_presence['w276_block_has_276']", "setwave_ok = (setwave_presence['w277_block_has_277']", 1, "swo1"),
 ("              and not setwave_presence['w276_block_has_275']", "              and not setwave_presence['w277_block_has_276']", 1, "swo2"),
 ("              and not setwave_presence['w276_block_has_274']", "              and not setwave_presence['w277_block_has_275']", 1, "swo3"),
 ("              and setwave_presence['whole_file_276_count'] == 1", "              and setwave_presence['whole_file_277_count'] == 1", 1, "swo4"),
 ("              and setwave_presence['whole_file_275_count'] == 1", "              and setwave_presence['whole_file_276_count'] == 1", 1, "swo5"),
 ("              and setwave_presence['whole_file_274_count'] == 1)", "              and setwave_presence['whole_file_275_count'] == 1)", 1, "swo6"),
 ("sd = 'results/p2cal_ext/n1_w276'", "sd = 'results/p2cal_ext/n1_w277'", 1, "sharddir"),
 ("'--prereg', 'research/PERPETUAL_N1_W276_PREREG.md'],", "'--prereg', 'research/PERPETUAL_N1_W277_PREREG.md'],", 1, "prereg"),
 ("os.path.exists('results/_w276bmc_derive_editor.py')", "os.path.exists('results/_w277bmc_derive_editor.py')", 1, "ev-editor"),
 ("os.path.exists('results/_r1111bmc_derive_editor_log.txt')", "os.path.exists('results/_r1114bmc_derive_editor_log.txt')", 1, "ev-log"),
 ("os.path.exists('results/_r1111bmc_needle_preflight.json')", "os.path.exists('results/_r1114bmc_needle_preflight.json')", 1, "ev-preflight"),
 ("    'r1111 GATE-1 CLEAN-AT-BIRTH FACE (9th consecutive) on ENGINE MECHANICS: '", "    'r1114 GATE-1 CLEAN-AT-BIRTH FACE (10th consecutive) on ENGINE MECHANICS: '", 1, "note-hdr"),
 ("    'the W276 splice carried ZERO heals of any class -- zero post-splice '", "    'the W277 splice carried ZERO canon heals -- zero post-splice '", 1, "note-2"),
 ("    'heals on pf/n1, zero pre-splice authoring heals (all count-asserted '", "    'heals on pf/n1, zero canon anomalies (2 disclosed pre-splice editor '", 1, "note-3"),
 ("    'editor reps first-try; the W275-generation date-roll rep was DROPPED count-0 per the '", "    'gate-region table-heals = expectation-table misreads, faces absent from canon; '", 1, "note-4"),
 ("    'measured same-date 20261019==20261019 fact, disclosed in the editor '", "    'all count-asserted editor reps first-try). Phase4 zero-residual + phase5 '", 1, "note-5"),
 ("    'header). Phase4 zero-residual + phase5 presence gates ALL PASS at '", "    'presence gates ALL PASS at editor time. Gate asserts worktree sha16 == '", 1, "note-6"),
 ("    'editor time. Gate asserts worktree sha16 == freeze-receipt post '", "    'freeze-receipt post faces, CR-normalized worktree == CR-normalized '", 1, "note-7"),
 ("    'faces, CR-normalized worktree == CR-normalized landed blob @ splice '", "    'landed blob @ splice commit 9e53371814 (landed = LF storage face, raw '", 1, "note-8"),
 ("    'commit 354a645155 (landed = LF storage face, raw sha16 recorded; '", "    'sha16 recorded; splice landed first-try behind=0 on origin_base '", 1, "note-9"),
 ("    'splice landed on the ff-base 7a70aee504 after gate0 caught the mid-window '", "    '5b2b2950f1, no mid-window race; engine batches 0df07c846b + 644b4f8459 '", 1, "note-10"),
 ("    'bm-a r1073 chain fail-closed; engine batch1 df7dedfd07 rode the push), segment-scoped birth-station '", "    'self-committed post-splice), segment-scoped birth-station '", 1, "note-11"),
 ("# ledger_pre: machine-read from W274 finalize product (r587 never-transcribe)", "# ledger_pre: machine-read from W276 finalize product (r587 never-transcribe)", 1, "ledger-comment"),
 ("w275 = json.load(io.open('results/perpetual_faces/n1_w275_results.json',", "w276 = json.load(io.open('results/perpetual_faces/n1_w276_results.json',", 1, "prior-load"),
 ("ledger_w275 = _find_ledger(w275)", "ledger_w276 = _find_ledger(w276)", 1, "ledger-var"),
 ("assert ledger_w275 is not None, 'W275 ledger face missing'", "assert ledger_w276 is not None, 'W276 ledger face missing'", 1, "ledger-assert"),
 ("prev_total = ledger_w275['total']", "prev_total = ledger_w276['total']", 1, "prev-total"),
 ("prev_k = w275['null_pool_cumulative']['merged']['n_values']", "prev_k = w276['null_pool_cumulative']['merged']['n_values']", 1, "prev-k"),
 ("up = fr['w275_upstream']", "up = fr['w276_upstream']", 1, "upstream-face"),
 ("w275_finalize_present = os.path.exists('results/perpetual_faces/n1_w275_results.json')", "w276_finalize_present = os.path.exists('results/perpetual_faces/n1_w276_results.json')", 1, "prior-present"),
 ('"wave": 276,', '"wave": 277,', 1, "wave-out"),
 ('"phase": "PRE-FINALIZE six-gate (r1111 bm-c own-seat window, 39th consecutive correct-phase target; standing law -- engine self-burn 12/12 landed post-W276 splice 354a645155 clean-at-birth 9th generation on engine mechanics, finalize not yet run)",',
  '"phase": "PRE-FINALIZE six-gate (r1114 bm-c own-seat window, 40th consecutive correct-phase target; standing law -- engine self-burn 12/12 landed post-W277 splice 9e53371814 clean-at-birth 10th generation on engine mechanics, finalize not yet run)",', 1, "phase-out"),
 ("and w275_finalize_present", "and w276_finalize_present", 1, "prior-present-ok"),
 ('"w275_finalize_product_present": w275_finalize_present,', '"w276_finalize_product_present": w276_finalize_present,', 1, "prior-out"),
 ('"source": "W275 finalize actuals machine-read from n1_w275_results.json (r587 law)",', '"source": "W276 finalize actuals machine-read from n1_w276_results.json (r587 law)",', 1, "source-out"),
 ('"anchor": "W275 finalize (bm-c r1108 one-pass 1,029,335/K=602,920) honored per freeze receipt w275_upstream face",', '"anchor": "W276 finalize (bm-c r1111 one-pass 1,031,535/K=605,120) honored per freeze receipt w276_upstream face",', 1, "anchor-out"),
 ("and prev_total == 1029335 and prev_k == 602920)", "and prev_total == 1031535 and prev_k == 605120)", 1, "ledger-pre-assert"),
 ('"prior_wave_274_boundary_kept": boundary,', '"prior_wave_276_boundary_kept": boundary,', 1, "bnd-key"),
 ('"note": "freeze-time FREE evidence consumed verbatim from _w275bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",', '"note": "freeze-time FREE evidence consumed verbatim from _w277bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",', 1, "seed-note"),
 ('"source": "freeze receipt post faces (zero heals of any class this generation -- zero post-splice engine-mechanics heals, zero pre-splice authoring heals, date-roll rep count-0 drop disclosed; setwave root cure held at the birth station)",',
  '"source": "freeze receipt post faces (zero canon heals this generation -- zero post-splice engine-mechanics heals, 2 disclosed pre-splice editor gate-region table-heals = expectation-table misreads on faces absent from canon, zero canon anomalies; setwave root cure held at the birth station)",', 1, "cab-source"),
 ('   "a_seed_base": 620301, "b_exit_seed_base": 622301,', '   "a_seed_base": 624701, "b_exit_seed_base": 626701,', 1, "wcr-bases"),
 ('   "shard_subdir": "n1_w275", "out_name": "n1_w275_results.json",', '   "shard_subdir": "n1_w277", "out_name": "n1_w277_results.json",', 1, "wcr-subdir"),
 ("   \"seed_bases_match_freeze_bands\": fr['bands']['a_lo'] == 620301 and fr['bands']['b_lo'] == 622301,", "   \"seed_bases_match_freeze_bands\": fr['bands']['a_lo'] == 624701 and fr['bands']['b_lo'] == 626701,", 1, "wcr-match"),
 ("io.open('results/_r1111bmc_w276_sixgate.json', 'w', encoding='utf-8').write(", "io.open('results/_r1114bmc_w277_sixgate.json', 'w', encoding='utf-8').write(", 1, "out-path"),
]
log_a = build("results/_r1111bmc_w276_sixgate.py", "results/_r1114bmc_w277_sixgate.py", six_reps)
print("\n".join(log_a))

# ---------------- PART B: fivekeys ----------------
# machine-verify the W276 key anchors live from the finalize product (zero-transcription)
d6 = json.load(io.open("results/perpetual_faces/n1_w276_results.json", encoding="utf-8"))
p = d6["null_pool_cumulative"]; s = d6["skill_line_v2_k_lift"]; f = d6["families"]["A_random_engine_exit"]
ANCH = {
 "mu": p["merged"]["mu"], "sigma": p["merged"]["sigma"],
 "a_p95": f["full_sharpe_p95"], "line_merged": s["line_merged_605120"],
 "se_mu": p["se_mu_at_k605120"], "klift": s["line_delta_k_lift"],
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
ANCH["prev_total"] = _fl(d6)["total"]
assert ANCH["prev_total"] == 1031535 and ANCH["k"] == 605120, (ANCH["prev_total"], ANCH["k"])
assert abs(ANCH["mu"] - (-0.09278451381544156)) < 1e-12, ANCH["mu"]
assert abs(ANCH["sigma"] - 0.2450856226849218) < 1e-12, ANCH["sigma"]
assert ANCH["a_p95"] == 0.305, ANCH["a_p95"]
assert ANCH["line_merged"] == 1.1969, ANCH["line_merged"]
assert ANCH["se_mu"] == 0.000315, ANCH["se_mu"]
assert ANCH["klift"] == 0.0001, ANCH["klift"]
print("W276 key anchors machine-verified:", {k: v for k, v in ANCH.items()})

fk_reps = [
 ('"""r1111 bm-c: W276 five-prediction-key machine assertion (prereg sec.5 vs finalize face).', '"""r1114 bm-c: W277 five-prediction-key machine assertion (prereg sec.5 vs finalize face).', 1, "fk-doc"),
 ("Read-only against results/perpetual_faces/n1_w276_results.json + frozen prereg keys.", "Read-only against results/perpetual_faces/n1_w277_results.json + frozen prereg keys.", 1, "fk-res-doc"),
 ("W276 prereg froze its sec.5 keys on W275 finalize actuals (live-chain-head basis;", "W277 prereg froze its sec.5 keys on W276 finalize actuals (live-chain-head basis;", 1, "fk-basis"),
 ("keys machine-read from n1_w275_results.json, r587 never-transcribe law --", "keys machine-read from n1_w276_results.json, r587 never-transcribe law --", 1, "fk-keys-doc"),
 ("constants below are cross-check anchors only, live-extracted from the W275", "constants below are cross-check anchors only, live-extracted from the W276", 1, "fk-anchors-doc1"),
 ("finalize product this window: mu -0.09280541 / sigma 0.24507989 / a_p95 0.3088 /", "finalize product this window: mu -0.09278451 / sigma 0.24508562 / a_p95 0.305 /", 1, "fk-anchors-doc2"),
 ("line_merged 1.1967 / se_mu 0.000316 / k_lift -0.0001 -- FULL-PRECISION machine-read", "line_merged 1.1969 / se_mu 0.000315 / k_lift +0.0001 -- FULL-PRECISION machine-read", 1, "fk-anchors-doc3"),
 ("Writes results/_r1111bmc_w276_fivekeys.json receipt. Ledger +0, marks +0.", "Writes results/_r1114bmc_w277_fivekeys.json receipt. Ledger +0, marks +0.", 1, "fk-out-doc"),
 ("Clone lineage: _r1108bmc_w275_fivekeys.py (canon, prior-wave keys variant).", "Clone lineage: _r1111bmc_w276_fivekeys.py (canon, prior-wave keys variant).", 1, "fk-lineage"),
 ('RES = "results/perpetual_faces/n1_w276_results.json"', 'RES = "results/perpetual_faces/n1_w277_results.json"', 1, "fk-res"),
 ('PRIOR = "results/perpetual_faces/n1_w275_results.json"', 'PRIOR = "results/perpetual_faces/n1_w276_results.json"', 1, "fk-prior"),
 ('OUT = "results/_r1111bmc_w276_fivekeys.json"', 'OUT = "results/_r1114bmc_w277_fivekeys.json"', 1, "fk-out"),
 ("# Frozen prediction keys = W275 finalize actuals (machine-read below; the", "# Frozen prediction keys = W276 finalize actuals (machine-read below; the", 1, "fk-frozen"),
 ("full-precision anchors machine-read from the W275 finalize product this", "full-precision anchors machine-read from the W276 finalize product this", 1, "fk-prec"),
 ("KEY_MU_MERGED_W275 = -0.09280540618987594   # W275 finalize merged mu, K=602,920", "KEY_MU_MERGED_W276 = %r   # W276 finalize merged mu, K=605,120" % ANCH["mu"], 1, "fk-kmu"),
 ("KEY_SIGMA_W275 = 0.24507988853984436", "KEY_SIGMA_W276 = %r" % ANCH["sigma"], 1, "fk-ksig"),
 ("KEY_A_P95_W275 = 0.3088", "KEY_A_P95_W276 = %r" % ANCH["a_p95"], 1, "fk-kp95"),
 ("KEY_LINE_W275_MERGED = 1.1967", "KEY_LINE_W276_MERGED = %r" % ANCH["line_merged"], 1, "fk-kline"),
 ("KEY_SE_MU_W275 = 0.000316", "KEY_SE_MU_W276 = %r" % ANCH["se_mu"], 1, "fk-kse"),
 ("KEY_KLIFT_W275 = -0.0001", "KEY_KLIFT_W276 = %r" % ANCH["klift"], 1, "fk-kkl"),
 ("w275 = json.load(open(PRIOR, encoding=\"utf-8\"))", "w276 = json.load(open(PRIOR, encoding=\"utf-8\"))", 1, "fk-load"),
 ('p1 = w275["null_pool_cumulative"]; s1 = w275["skill_line_v2_k_lift"]', 'p1 = w276["null_pool_cumulative"]; s1 = w276["skill_line_v2_k_lift"]', 1, "fk-p1"),
 ('f1 = w275["families"]["A_random_engine_exit"]', 'f1 = w276["families"]["A_random_engine_exit"]', 1, "fk-f1"),
 ('k_line_merged = s1["line_merged_602920"]', 'k_line_merged = s1["line_merged_605120"]', 1, "fk-kline-read"),
 ('k_se_mu = p1["se_mu_at_k602920"]', 'k_se_mu = p1["se_mu_at_k605120"]', 1, "fk-kse-read"),
 ("KEY_MU_MERGED_W275", "KEY_MU_MERGED_W276", 2, "fk-kmu-ref"),
 ("KEY_SIGMA_W275", "KEY_SIGMA_W276", 2, "fk-ksig-ref"),
 ("KEY_A_P95_W275", "KEY_A_P95_W276", 2, "fk-kp95-ref"),
 ("KEY_LINE_W275_MERGED", "KEY_LINE_W276_MERGED", 2, "fk-kline-ref"),
 ("KEY_SE_MU_W275", "KEY_SE_MU_W276", 2, "fk-kse-ref"),
 ("KEY_KLIFT_W275", "KEY_KLIFT_W276", 2, "fk-kkl-ref"),
 ('se_mu = pool["se_mu_at_k605120"]', 'se_mu = pool["se_mu_at_k607320"]', 1, "fk-semu-read"),
 ('line_pre = sl["line_pre_w276"]', 'line_pre = sl["line_pre_w277"]', 1, "fk-lpre-read"),
 ('line_merged = sl["line_merged_605120"]', 'line_merged = sl["line_merged_607320"]', 1, "fk-lm-read"),
 ('w276_mu = pool["w276_only"]["mu"]', 'w277_mu = pool["w277_only"]["mu"]', 1, "fk-wonly"),
 ('gap1 = abs(w276_mu - merged_mu)', 'gap1 = abs(w277_mu - merged_mu)', 1, "fk-wonly-gap1"),
 ("# key 1: W276-only mu vs merged mu gap", "# key 1: W277-only mu vs merged mu gap", 1, "fk-k1c"),
 ('checks.append(("key1_w276_vs_merged_mu_gap"', 'checks.append(("key1_w277_vs_merged_mu_gap"', 1, "fk-k1"),
 ("# key 1b: merged mu vs W274 frozen key (prereg keys = prior-wave actuals)", "# key 1b: merged mu vs W276 frozen key (prereg keys = prior-wave actuals)", 1, "fk-k1bc"),
 ('checks.append(("key1b_merged_vs_w275_key"', 'checks.append(("key1b_merged_vs_w276_key"', 1, "fk-k1b"),
 ("# key 2: sigma rel change vs W275 key", "# key 2: sigma rel change vs W276 key", 1, "fk-k2c"),
 ("# key 3: A-band p95 vs W275 key (double-direction band)", "# key 3: A-band p95 vs W276 key (double-direction band)", 1, "fk-k3c"),
 ("# key 5: se_mu narrowing vs W275 (se_mu chain face, sec.5 prose)", "# key 5: se_mu narrowing vs W276 (se_mu chain face, sec.5 prose)", 1, "fk-k5c"),
 ('"wave": 276,', '"wave": 277,', 1, "fk-wave"),
 ('"se_mu_k605120": se_mu', '"se_mu_k607320": se_mu', 1, "fk-semu-out"),
 ('"w276_only": {"mu": w276_mu, "sigma": pool["w276_only"]["sigma"]}', '"w277_only": {"mu": w277_mu, "sigma": pool["w277_only"]["sigma"]}', 1, "fk-wonly-out"),
 ('"line_pre_w276": line_pre,', '"line_pre_w277": line_pre,', 1, "fk-lpre-out"),
 ('"line_merged_605120": line_merged,', '"line_merged_607320": line_merged,', 1, "fk-lm-out"),
 ('"keys_anchor": ("W275 finalize actuals machine-read from n1_w275_results.json "', '"keys_anchor": ("W276 finalize actuals machine-read from n1_w276_results.json "', 1, "fk-anchor"),
 ("(r587 law) -- W276 prereg froze sec.5 keys on W275 actuals ", "(r587 law) -- W277 prereg froze sec.5 keys on W276 actuals ", 1, "fk-basis-out"),
 ("(live-chain-head basis; W275 finalize landed pre-draft r1108)\")", "(live-chain-head basis; W276 finalize landed pre-draft r1111)\")", 1, "fk-basis2"),
 ('"ledger_identity": {"prev_total": 1029335, "batch_trials": 2200,', '"ledger_identity": {"prev_total": 1031535, "batch_trials": 2200,', 1, "fk-led"),
 ('"total": 1031535,', '"total": 1033735,', 1, "fk-led-tot"),
 ('"exact": (1029335 + 2200) == 1031535},', '"exact": (1031535 + 2200) == 1033735},', 1, "fk-led-ex"),
 ('"merged_k_identity": {"prev_k": 602920, "batch": 2200, "merged_k": merged_k,', '"merged_k_identity": {"prev_k": 605120, "batch": 2200, "merged_k": merged_k,', 1, "fk-kid"),
 ('"exact": (602920 + 2200) == merged_k},', '"exact": (605120 + 2200) == merged_k},', 1, "fk-kid-ex"),
 ('"keys_source": "W275 finalize actuals machine-read from n1_w275_results.json (r587 law)",', '"keys_source": "W276 finalize actuals machine-read from n1_w276_results.json (r587 law)",', 1, "fk-ksrc"),
]
log_b = build("results/_r1111bmc_w276_fivekeys.py", "results/_r1114bmc_w277_fivekeys.py", fk_reps)
print("\n".join(log_b))
print("CLONES BUILT OK")
