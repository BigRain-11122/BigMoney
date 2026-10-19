# -*- coding: utf-8 -*-
# r1118 bm-c: build W278 sixgate + fivekeys clones from the r1114 W277 canons
# by COUNT-ASSERTED ORDERED TRANSFORM (E63 lineage; zero transcription --
# every needle count measured on the source text at build time; splice sha +
# fivekeys key anchors machine-read live). Zero heals this generation: the
# W277 canon faces are current-generation-correct (no lagged label faces
# found; the r1118 editor chain landed needle-preflight FIRST-RUN
# ZERO-MISMATCH per the r1077 measured law, zero table-heals).
# CAB-count reconciliation disclosed: landed canon chain = W276 sixgate
# "9th consecutive" -> W277 sixgate "10th consecutive" -> W278 "11th"
# (W278 prereg L1 confirms the W277 splice = CLEAN-AT-BIRTH 10th gen); the
# r1118 splice-commit prose face "CLEAN-AT-BIRTH 10th gen" reads as the
# canon-template generation (_w277bmc_freeze_edits.py = the 10th-gen CAB
# product being cloned); the W278 sixgate carries 11th for the W278 splice
# per chain arithmetic. PART B anchors = W277 finalize actuals live-read
# from n1_w277_results.json this window, cross-checked against the landed
# _r1114bmc_w277_fivekeys.json receipt (mu -0.09277044 / sigma 0.24508694 /
# a_p95 0.3095 / line_merged 1.197 / se_mu 0.000314 / k_lift 0.0, ledger
# 1,033,735 / K=607,320).
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
SPLICE = subprocess.run(["git", "log", "--format=%H", "--grep=W278 FIVE-FACE FREEZE SPLICE LANDED", "-1"],
                        capture_output=True, text=True).stdout.strip()
assert SPLICE.startswith("b6f486af35"), SPLICE  # splice commit located by message (machine-read)
six_reps = [
 ("# r1114 bm-c: W277 PRE-FINALIZE six-gate receipt (standing law since W217", "# r1118 bm-c: W278 PRE-FINALIZE six-gate receipt (standing law since W217", 1, "hdr"),
 ("# debt; clone lineage _r1111bmc_w276_sixgate.py, 40th consecutive", "# debt; clone lineage _r1114bmc_w277_sixgate.py, 41st consecutive", 1, "lineage"),
 ("# mtime-watch auto-ignite post-W277 splice (splice commit 9e53371814 landed", "# mtime-watch auto-ignite post-W278 splice (splice commit b6f486af35 landed", 1, "burn-a"),
 ("# first-try behind=0 on origin_base 5b2b2950f1 with no mid-window race;", "# first-try behind=0 on origin_base d2667773da after the mid-window bm-b race", 1, "burn-b"),
 ("# engine appender shards self-commit per the W272 estate precedent", "# heal (gate0 fail-closed; discard-3 regenerable + ff per r609 gate0 law); engine", 1, "burn-c"),
 ("# (batches 0df07c846b six + 644b4f8459 six, both on origin; finalize not", "# appender shards self-commit per the W272 estate precedent (batches", 1, "burn-d"),
 ("# yet run).", "# 60e630918f six + b965e2ecf0 six, both on origin; finalize not yet run).", 1, "burn-e"),
 ("# CLEAN-AT-BIRTH FACE (10th consecutive) on ENGINE MECHANICS: the W277", "# CLEAN-AT-BIRTH FACE (11th consecutive) on ENGINE MECHANICS: the W278", 1, "cab-a"),
 ("# splice carried ZERO canon heals -- zero post-splice heals on pf/n1,", "# splice carried ZERO heals of any class -- zero post-splice heals on pf/n1,", 1, "cab-b"),
 ("# zero canon anomalies (2 disclosed pre-splice editor gate-region", "# zero pre-splice authoring heals (needle preflight FIRST-RUN ZERO-MISMATCH", 1, "cab-c"),
 ("# table-heals = expectation-table misreads, faces absent from canon; all", "# r1077 measured law = zero table-heals this generation; all count-asserted", 1, "cab-d"),
 ("# count-asserted editor reps first-try; phase4 zero-residual + phase5", "# editor reps first-try; phase4 zero-residual + phase5 presence gates ALL", 1, "cab-e"),
 ("# presence gates ALL PASS at editor time; setwave root-cure held at the", "# PASS at editor time; setwave root-cure held at the birth station", 1, "cab-f"),
 ("# birth station (_set_wave(276):1 / _set_wave(275):0 / _set_wave(274):0", "# (_set_wave(277):1 / _set_wave(276):0 / _set_wave(275):0", 1, "cab-g"),
 ("# (c) segment-scoped birth-station presence gates after the W276 block:", "# (c) segment-scoped birth-station presence gates after the W277 block:", 1, "g1c"),
 ("# _set_wave(277) present, _set_wave(276)/_set_wave(275) absent.", "# _set_wave(278) present, _set_wave(277)/_set_wave(276) absent.", 1, "g1d"),
 ("SPLICE = '9e533718149273cdaf9cc0238ec53741faac12fa'", "SPLICE = '" + SPLICE + "'", 1, "splice-const"),
 ("fr = json.load(io.open('results/_w277bmc_freeze_receipt.json', encoding='utf-8'))", "fr = json.load(io.open('results/_w278bmc_freeze_receipt.json', encoding='utf-8'))", 1, "receipt-path"),
 ("i = n1t.find('277: {\"batch\": \"PERPETUAL-N1-W277\"')", "i = n1t.find('278: {\"batch\": \"PERPETUAL-N1-W278\"')", 1, "row-find"),
 ("assert i >= 0, 'W277 wave row missing'", "assert i >= 0, 'W278 wave row missing'", 1, "row-msg"),
 ("if '278: {' in seg:", "if '279: {' in seg:", 1, "seg-next"),
 ("    seg = seg[:seg.find('278: {')]", "    seg = seg[:seg.find('279: {')]", 1, "seg-trim"),
 ("    'a_seed_base_624701': '624701' in seg,", "    'a_seed_base_626901': '626901' in seg,", 1, "rf-a"),
 ("    'b_exit_seed_base_626701': '626701' in seg,", "    'b_exit_seed_base_628901': '628901' in seg,", 1, "rf-b"),
 ("    'shard_subdir_n1_w277': 'n1_w277' in seg,", "    'shard_subdir_n1_w278': 'n1_w278' in seg,", 1, "rf-sd"),
 ("    'out_name_n1_w277_results': 'n1_w277_results.json' in seg,", "    'out_name_n1_w278_results': 'n1_w278_results.json' in seg,", 1, "rf-out"),
 ("f1 = 'base=624701 span=2000'", "f1 = 'base=626901 span=2000'", 1, "f1"),
 ("f2 = 'base=626701 span=200'", "f2 = 'base=628901 span=200'", 1, "f2"),
 ("# prior-wave W276 registry boundary faces kept", "# prior-wave W277 registry boundary faces kept", 1, "bnd-comment"),
 ("m276 = re.search(r'276: \\{\"batch\": \"PERPETUAL-N1-W276\"', n1t)", "m277 = re.search(r'277: \\{\"batch\": \"PERPETUAL-N1-W277\"', n1t)", 1, "m276"),
 ("w276_seg = n1t[m276.start():m276.start() + 9000] if m276 else ''", "w277_seg = n1t[m277.start():m277.start() + 9000] if m277 else ''", 1, "seg276"),
 ("if '277: {' in w276_seg:", "if '278: {' in w277_seg:", 1, "seg276-next"),
 ("    w276_seg = w276_seg[:w276_seg.find('277: {')]", "    w277_seg = w277_seg[:w277_seg.find('278: {')]", 1, "seg276-trim"),
 ("boundary = bool(m276) and '622501' in w276_seg and '624501' in w276_seg", "boundary = bool(m277) and '624701' in w277_seg and '626701' in w277_seg", 1, "boundary"),
 ("k276pos = n1t.rfind('_set_wave(276)')", "k277pos = n1t.rfind('_set_wave(277)')", 1, "kpos"),
 ("after276 = n1t[k276pos + len('_set_wave(276)'):", "after277 = n1t[k277pos + len('_set_wave(277)'):", 1, "afterpos"),
 ("    'w277_block_has_277': '_set_wave(277)' in after276,", "    'w278_block_has_278': '_set_wave(278)' in after277,", 1, "swp1"),
 ("    'w277_block_has_276': '_set_wave(276)' in after276,", "    'w278_block_has_277': '_set_wave(277)' in after277,", 1, "swp2"),
 ("    'w277_block_has_275': '_set_wave(275)' in after276,", "    'w278_block_has_276': '_set_wave(276)' in after277,", 1, "swp3"),
 ("    'whole_file_277_count': n1t.count('_set_wave(277)'),", "    'whole_file_278_count': n1t.count('_set_wave(278)'),", 1, "swc1"),
 ("    'whole_file_276_count': n1t.count('_set_wave(276)'),", "    'whole_file_277_count': n1t.count('_set_wave(277)'),", 1, "swc2"),
 ("    'whole_file_275_count': n1t.count('_set_wave(275)'),", "    'whole_file_276_count': n1t.count('_set_wave(276)'),", 1, "swc3"),
 ("setwave_ok = (setwave_presence['w277_block_has_277']", "setwave_ok = (setwave_presence['w278_block_has_278']", 1, "swo1"),
 ("              and not setwave_presence['w277_block_has_276']", "              and not setwave_presence['w278_block_has_277']", 1, "swo2"),
 ("              and not setwave_presence['w277_block_has_275']", "              and not setwave_presence['w278_block_has_276']", 1, "swo3"),
 ("              and setwave_presence['whole_file_277_count'] == 1", "              and setwave_presence['whole_file_278_count'] == 1", 1, "swo4"),
 ("              and setwave_presence['whole_file_276_count'] == 1", "              and setwave_presence['whole_file_277_count'] == 1", 1, "swo5"),
 ("              and setwave_presence['whole_file_275_count'] == 1)", "              and setwave_presence['whole_file_276_count'] == 1)", 1, "swo6"),
 ("sd = 'results/p2cal_ext/n1_w277'", "sd = 'results/p2cal_ext/n1_w278'", 1, "sharddir"),
 ("'--prereg', 'research/PERPETUAL_N1_W277_PREREG.md'],", "'--prereg', 'research/PERPETUAL_N1_W278_PREREG.md'],", 1, "prereg"),
 ("os.path.exists('results/_w277bmc_derive_editor.py')", "os.path.exists('results/_w278bmc_derive_editor.py')", 1, "ev-editor"),
 ("and os.path.exists('results/_r1114bmc_derive_editor_log.txt')", "and os.path.exists('results/_r1118bmc_derive_editor_log.txt')", 1, "ev-log"),
 ("and os.path.exists('results/_r1114bmc_needle_preflight.json'))", "and os.path.exists('results/_r1118bmc_needle_preflight.json'))", 1, "ev-preflight"),
 ("    'r1114 GATE-1 CLEAN-AT-BIRTH FACE (10th consecutive) on ENGINE MECHANICS: '", "    'r1118 GATE-1 CLEAN-AT-BIRTH FACE (11th consecutive) on ENGINE MECHANICS: '", 1, "note-1"),
 ("    'the W277 splice carried ZERO canon heals -- zero post-splice '", "    'the W278 splice carried ZERO heals of any class -- zero post-splice '", 1, "note-2"),
 ("    'heals on pf/n1, zero canon anomalies (2 disclosed pre-splice editor '", "    'heals on pf/n1, zero pre-splice authoring heals (preflight FIRST-RUN '", 1, "note-3"),
 ("    'gate-region table-heals = expectation-table misreads, faces absent from canon; '", "    'ZERO-MISMATCH r1077 measured law, zero table-heals; all count-asserted '", 1, "note-4"),
 ("    'all count-asserted editor reps first-try). Phase4 zero-residual + phase5 '", "    'editor reps first-try). Phase4 zero-residual + phase5 presence gates '", 1, "note-5"),
 ("    'presence gates ALL PASS at editor time. Gate asserts worktree sha16 == '", "    'ALL PASS at editor time. Gate asserts worktree sha16 == freeze-receipt '", 1, "note-6"),
 ("    'freeze-receipt post faces, CR-normalized worktree == CR-normalized '", "    'post faces, CR-normalized worktree == CR-normalized landed blob @ '", 1, "note-7"),
 ("    'landed blob @ splice commit 9e53371814 (landed = LF storage face, raw '", "    'splice commit b6f486af35 (landed = LF storage face, raw sha16 '", 1, "note-8"),
 ("    'sha16 recorded; splice landed first-try behind=0 on origin_base '", "    'recorded; splice landed first-try behind=0 on origin_base d2667773da '", 1, "note-9"),
 ("    '5b2b2950f1, no mid-window race; engine batches 0df07c846b + 644b4f8459 '", "    'after the bm-b race heal (gate0 fail-closed, discard-3 regenerable + ff '", 1, "note-10"),
 ("    'self-committed post-splice), segment-scoped birth-station '", "    'per r609 gate0 law; engine batches 60e630918f + b965e2ecf0 '", 1, "note-11"),
 ("    'presence gates green, editor/preflight/log evidence files present.'", "    'self-committed post-splice), segment-scoped birth-station presence gates green, editor/preflight/log evidence files present.'", 1, "note-12"),
 ("# ledger_pre: machine-read from W276 finalize product (r587 never-transcribe)", "# ledger_pre: machine-read from W277 finalize product (r587 never-transcribe)", 1, "ledger-comment"),
 ("w276 = json.load(io.open('results/perpetual_faces/n1_w276_results.json',", "w277 = json.load(io.open('results/perpetual_faces/n1_w277_results.json',", 1, "prior-load"),
 ("ledger_w276 = _find_ledger(w276)", "ledger_w277 = _find_ledger(w277)", 1, "ledger-var"),
 ("assert ledger_w276 is not None, 'W276 ledger face missing'", "assert ledger_w277 is not None, 'W277 ledger face missing'", 1, "ledger-assert"),
 ("prev_total = ledger_w276['total']", "prev_total = ledger_w277['total']", 1, "prev-total"),
 ("prev_k = w276['null_pool_cumulative']['merged']['n_values']", "prev_k = w277['null_pool_cumulative']['merged']['n_values']", 1, "prev-k"),
 ("up = fr['w276_upstream']", "up = fr['w277_upstream']", 1, "upstream-face"),
 ("w276_finalize_present = os.path.exists('results/perpetual_faces/n1_w276_results.json')", "w277_finalize_present = os.path.exists('results/perpetual_faces/n1_w277_results.json')", 1, "prior-present"),
 ('"wave": 277,', '"wave": 278,', 1, "wave-out"),
 (' "phase": "PRE-FINALIZE six-gate (r1114 bm-c own-seat window, 40th consecutive correct-phase target; standing law -- engine self-burn 12/12 landed post-W277 splice 9e53371814 clean-at-birth 10th generation on engine mechanics, finalize not yet run)",',
  ' "phase": "PRE-FINALIZE six-gate (r1118 bm-c own-seat window, 41st consecutive correct-phase target; standing law -- engine self-burn 12/12 landed post-W278 splice b6f486af35 clean-at-birth 11th generation on engine mechanics, finalize not yet run)",', 1, "phase-out"),
 ("      and w276_finalize_present", "      and w277_finalize_present", 1, "prior-present-ok"),
 ('  "w276_finalize_product_present": w276_finalize_present,', '  "w277_finalize_product_present": w277_finalize_present,', 1, "prior-out"),
 ('  "source": "W276 finalize actuals machine-read from n1_w276_results.json (r587 law)",', '  "source": "W277 finalize actuals machine-read from n1_w277_results.json (r587 law)",', 1, "source-out"),
 ('  "anchor": "W276 finalize (bm-c r1111 one-pass 1,031,535/K=605,120) honored per freeze receipt w276_upstream face",', '  "anchor": "W277 finalize (bm-c r1114-continuation one-pass 1,033,735/K=607,320) honored per freeze receipt w277_upstream face",', 1, "anchor-out"),
 ("and upstream_match and prev_total == 1031535 and prev_k == 605120)", "and upstream_match and prev_total == 1033735 and prev_k == 607320)", 1, "ledger-pre-assert"),
 ('  "prior_wave_276_boundary_kept": boundary,', '  "prior_wave_277_boundary_kept": boundary,', 1, "bnd-key"),
 ('   "note": "freeze-time FREE evidence consumed verbatim from _w277bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",', '   "note": "freeze-time FREE evidence consumed verbatim from _w278bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",', 1, "seed-note"),
 ('    "source": "freeze receipt post faces (zero canon heals this generation -- zero post-splice engine-mechanics heals, 2 disclosed pre-splice editor gate-region table-heals = expectation-table misreads on faces absent from canon, zero canon anomalies; setwave root cure held at the birth station)",',
  '    "source": "freeze receipt post faces (zero heals of any class this generation -- zero post-splice engine-mechanics heals, zero pre-splice authoring heals, needle preflight FIRST-RUN ZERO-MISMATCH r1077 measured law = zero table-heals; setwave root cure held at the birth station)",', 1, "cab-source"),
 ('   "a_seed_base": 624701, "b_exit_seed_base": 626701,', '   "a_seed_base": 626901, "b_exit_seed_base": 628901,', 1, "wcr-bases"),
 ('   "shard_subdir": "n1_w277", "out_name": "n1_w277_results.json",', '   "shard_subdir": "n1_w278", "out_name": "n1_w278_results.json",', 1, "wcr-subdir"),
 ("   \"seed_bases_match_freeze_bands\": fr['bands']['a_lo'] == 624701 and fr['bands']['b_lo'] == 626701,", "   \"seed_bases_match_freeze_bands\": fr['bands']['a_lo'] == 626901 and fr['bands']['b_lo'] == 628901,", 1, "wcr-match"),
 ("io.open('results/_r1114bmc_w277_sixgate.json', 'w', encoding='utf-8').write(", "io.open('results/_r1118bmc_w278_sixgate.json', 'w', encoding='utf-8').write(", 1, "out-path"),
]
log_a = build("results/_r1114bmc_w277_sixgate.py", "results/_r1118bmc_w278_sixgate.py", six_reps)
print("\n".join(log_a))

# ---------------- PART B: fivekeys ----------------
# machine-verify the W277 key anchors live from the finalize product (zero-transcription)
d7 = json.load(io.open("results/perpetual_faces/n1_w277_results.json", encoding="utf-8"))
p = d7["null_pool_cumulative"]; s = d7["skill_line_v2_k_lift"]; f = d7["families"]["A_random_engine_exit"]
ANCH = {
 "mu": p["merged"]["mu"], "sigma": p["merged"]["sigma"],
 "a_p95": f["full_sharpe_p95"], "line_merged": s["line_merged_607320"],
 "se_mu": p["se_mu_at_k607320"], "klift": s["line_delta_k_lift"],
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
assert ANCH["prev_total"] == 1033735 and ANCH["k"] == 607320, (ANCH["prev_total"], ANCH["k"])
assert abs(ANCH["mu"] - (-0.09277043683725218)) < 1e-12, ANCH["mu"]
assert abs(ANCH["sigma"] - 0.24508693698115214) < 1e-12, ANCH["sigma"]
assert ANCH["a_p95"] == 0.3095, ANCH["a_p95"]
assert ANCH["line_merged"] == 1.197, ANCH["line_merged"]
assert ANCH["se_mu"] == 0.000314, ANCH["se_mu"]
assert ANCH["klift"] == 0.0, ANCH["klift"]
print("W277 key anchors machine-verified:", {k: v for k, v in ANCH.items()})

fk_reps = [
 ('"""r1114 bm-c: W277 five-prediction-key machine assertion (prereg sec.5 vs finalize face).', '"""r1118 bm-c: W278 five-prediction-key machine assertion (prereg sec.5 vs finalize face).', 1, "fk-doc"),
 ("Read-only against results/perpetual_faces/n1_w277_results.json + frozen prereg keys.", "Read-only against results/perpetual_faces/n1_w278_results.json + frozen prereg keys.", 1, "fk-res-doc"),
 ("W277 prereg froze its sec.5 keys on W276 finalize actuals (live-chain-head basis;", "W278 prereg froze its sec.5 keys on W277 finalize actuals (live-chain-head basis;", 1, "fk-basis"),
 ("keys machine-read from n1_w276_results.json, r587 never-transcribe law --", "keys machine-read from n1_w277_results.json, r587 never-transcribe law --", 1, "fk-keys-doc"),
 ("constants below are cross-check anchors only, live-extracted from the W276", "constants below are cross-check anchors only, live-extracted from the W277", 1, "fk-anchors-doc1"),
 ("finalize product this window: mu -0.09278451 / sigma 0.24508562 / a_p95 0.305 /", "finalize product this window: mu -0.09277044 / sigma 0.24508694 / a_p95 0.3095 /", 1, "fk-anchors-doc2"),
 ("line_merged 1.1969 / se_mu 0.000315 / k_lift +0.0001 -- FULL-PRECISION machine-read", "line_merged 1.197 / se_mu 0.000314 / k_lift 0.0 -- FULL-PRECISION machine-read", 1, "fk-anchors-doc3"),
 ("Writes results/_r1114bmc_w277_fivekeys.json receipt. Ledger +0, marks +0.", "Writes results/_r1118bmc_w278_fivekeys.json receipt. Ledger +0, marks +0.", 1, "fk-out-doc"),
 ("Clone lineage: _r1111bmc_w276_fivekeys.py (canon, prior-wave keys variant).", "Clone lineage: _r1114bmc_w277_fivekeys.py (canon, prior-wave keys variant).", 1, "fk-lineage"),
 ('RES = "results/perpetual_faces/n1_w277_results.json"', 'RES = "results/perpetual_faces/n1_w278_results.json"', 1, "fk-res"),
 ('PRIOR = "results/perpetual_faces/n1_w276_results.json"', 'PRIOR = "results/perpetual_faces/n1_w277_results.json"', 1, "fk-prior"),
 ('OUT = "results/_r1114bmc_w277_fivekeys.json"', 'OUT = "results/_r1118bmc_w278_fivekeys.json"', 1, "fk-out"),
 ("# Frozen prediction keys = W276 finalize actuals (machine-read below; the", "# Frozen prediction keys = W277 finalize actuals (machine-read below; the", 1, "fk-frozen"),
 ("full-precision anchors machine-read from the W276 finalize product this", "full-precision anchors machine-read from the W277 finalize product this", 1, "fk-prec"),
 ("KEY_MU_MERGED_W276 = -0.09278451381544156   # W276 finalize merged mu, K=605,120", "KEY_MU_MERGED_W277 = %r   # W277 finalize merged mu, K=607,320" % ANCH["mu"], 1, "fk-kmu"),
 ("KEY_SIGMA_W276 = 0.2450856226849218", "KEY_SIGMA_W277 = %r" % ANCH["sigma"], 1, "fk-ksig"),
 ("KEY_A_P95_W276 = 0.305", "KEY_A_P95_W277 = %r" % ANCH["a_p95"], 1, "fk-kp95"),
 ("KEY_LINE_W276_MERGED = 1.1969", "KEY_LINE_W277_MERGED = %r" % ANCH["line_merged"], 1, "fk-kline"),
 ("KEY_SE_MU_W276 = 0.000315", "KEY_SE_MU_W277 = %r" % ANCH["se_mu"], 1, "fk-kse"),
 ("KEY_KLIFT_W276 = 0.0001", "KEY_KLIFT_W277 = %r" % ANCH["klift"], 1, "fk-kkl"),
 ('w276 = json.load(open(PRIOR, encoding="utf-8"))', 'w277 = json.load(open(PRIOR, encoding="utf-8"))', 1, "fk-load"),
 ('p1 = w276["null_pool_cumulative"]; s1 = w276["skill_line_v2_k_lift"]', 'p1 = w277["null_pool_cumulative"]; s1 = w277["skill_line_v2_k_lift"]', 1, "fk-p1"),
 ('f1 = w276["families"]["A_random_engine_exit"]', 'f1 = w277["families"]["A_random_engine_exit"]', 1, "fk-f1"),
 ('k_line_merged = s1["line_merged_605120"]', 'k_line_merged = s1["line_merged_607320"]', 1, "fk-kline-read"),
 ('k_se_mu = p1["se_mu_at_k605120"]', 'k_se_mu = p1["se_mu_at_k607320"]', 1, "fk-kse-read"),
 ("KEY_MU_MERGED_W276", "KEY_MU_MERGED_W277", 2, "fk-kmu-ref"),
 ("KEY_SIGMA_W276", "KEY_SIGMA_W277", 2, "fk-ksig-ref"),
 ("KEY_A_P95_W276", "KEY_A_P95_W277", 2, "fk-kp95-ref"),
 ("KEY_LINE_W276_MERGED", "KEY_LINE_W277_MERGED", 2, "fk-kline-ref"),
 ("KEY_SE_MU_W276", "KEY_SE_MU_W277", 2, "fk-kse-ref"),
 ("KEY_KLIFT_W276", "KEY_KLIFT_W277", 2, "fk-kkl-ref"),
 ('se_mu = pool["se_mu_at_k607320"]', 'se_mu = pool["se_mu_at_k609520"]', 1, "fk-semu-read"),
 ('line_pre = sl["line_pre_w277"]', 'line_pre = sl["line_pre_w278"]', 1, "fk-lpre-read"),
 ('line_merged = sl["line_merged_607320"]', 'line_merged = sl["line_merged_609520"]', 1, "fk-lm-read"),
 ('w277_mu = pool["w277_only"]["mu"]', 'w278_mu = pool["w278_only"]["mu"]', 1, "fk-wonly"),
 ('gap1 = abs(w277_mu - merged_mu)', 'gap1 = abs(w278_mu - merged_mu)', 1, "fk-wonly-gap1"),
 ("# key 1: W277-only mu vs merged mu gap", "# key 1: W278-only mu vs merged mu gap", 1, "fk-k1c"),
 ('checks.append(("key1_w277_vs_merged_mu_gap"', 'checks.append(("key1_w278_vs_merged_mu_gap"', 1, "fk-k1"),
 ("# key 1b: merged mu vs W276 frozen key (prereg keys = prior-wave actuals)", "# key 1b: merged mu vs W277 frozen key (prereg keys = prior-wave actuals)", 1, "fk-k1bc"),
 ('checks.append(("key1b_merged_vs_w276_key"', 'checks.append(("key1b_merged_vs_w277_key"', 1, "fk-k1b"),
 ("# key 2: sigma rel change vs W276 key", "# key 2: sigma rel change vs W277 key", 1, "fk-k2c"),
 ("# key 3: A-band p95 vs W276 key (double-direction band)", "# key 3: A-band p95 vs W277 key (double-direction band)", 1, "fk-k3c"),
 ("# key 5: se_mu narrowing vs W276 (se_mu chain face, sec.5 prose)", "# key 5: se_mu narrowing vs W277 (se_mu chain face, sec.5 prose)", 1, "fk-k5c"),
 ('"wave": 277,', '"wave": 278,', 1, "fk-wave"),
 ('"se_mu_k607320": se_mu', '"se_mu_k609520": se_mu', 1, "fk-semu-out"),
 ('"w277_only": {"mu": w277_mu, "sigma": pool["w277_only"]["sigma"]}', '"w278_only": {"mu": w278_mu, "sigma": pool["w278_only"]["sigma"]}', 1, "fk-wonly-out"),
 ('"line_pre_w277": line_pre,', '"line_pre_w278": line_pre,', 1, "fk-lpre-out"),
 ('"line_merged_607320": line_merged,', '"line_merged_609520": line_merged,', 1, "fk-lm-out"),
 ('"keys_anchor": ("W276 finalize actuals machine-read from n1_w276_results.json "', '"keys_anchor": ("W277 finalize actuals machine-read from n1_w277_results.json "', 1, "fk-anchor"),
 ("(r587 law) -- W277 prereg froze sec.5 keys on W276 actuals ", "(r587 law) -- W278 prereg froze sec.5 keys on W277 actuals ", 1, "fk-basis-out"),
 ('(live-chain-head basis; W276 finalize landed pre-draft r1111)")', '(live-chain-head basis; W277 finalize landed pre-draft r1116)")', 1, "fk-basis2"),
 ('"ledger_identity": {"prev_total": 1031535, "batch_trials": 2200,', '"ledger_identity": {"prev_total": 1033735, "batch_trials": 2200,', 1, "fk-led"),
 ('"total": 1033735,', '"total": 1035935,', 1, "fk-led-tot"),
 ('"exact": (1031535 + 2200) == 1033735},', '"exact": (1033735 + 2200) == 1035935},', 1, "fk-led-ex"),
 ('"merged_k_identity": {"prev_k": 605120, "batch": 2200, "merged_k": merged_k,', '"merged_k_identity": {"prev_k": 607320, "batch": 2200, "merged_k": merged_k,', 1, "fk-kid"),
 ('"exact": (605120 + 2200) == merged_k},', '"exact": (607320 + 2200) == merged_k},', 1, "fk-kid-ex"),
 ('"keys_source": "W276 finalize actuals machine-read from n1_w276_results.json (r587 law)",', '"keys_source": "W277 finalize actuals machine-read from n1_w277_results.json (r587 law)",', 1, "fk-ksrc"),
]
log_b = build("results/_r1114bmc_w277_fivekeys.py", "results/_r1118bmc_w278_fivekeys.py", fk_reps)
print("\n".join(log_b))
print("CLONES BUILT OK")
