# -*- coding: utf-8 -*-
# r1111 bm-c: build W276 sixgate + fivekeys clones from the r1108 W275 canons
# by COUNT-ASSERTED ORDERED TRANSFORM (E63 lineage; zero transcription --
# every needle count measured on the source text at build time; splice sha +
# fivekeys key anchors machine-read live).
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
SPLICE = subprocess.run(["git", "log", "--format=%H", "--grep=W276 five-face freeze splice LANDED", "-1"],
                       capture_output=True, text=True).stdout.strip()
assert SPLICE.startswith("354a645155"), SPLICE  # splice commit located by message (machine-read)
six_reps = [
 ("r1108 bm-c: W275 PRE-FINALIZE six-gate receipt", "r1111 bm-c: W276 PRE-FINALIZE six-gate receipt", 1, "hdr"),
 ("clone lineage _r1105bmc_w274_sixgate.py, 38th consecutive", "clone lineage _r1108bmc_w275_sixgate.py, 39th consecutive", 1, "lineage"),
 ("mtime-watch auto-ignite post-W275 splice (splice commit 018782314d landed", "mtime-watch auto-ignite post-W276 splice (splice commit 354a645155 landed", 1, "burnface"),
 ("via stash-bridge rebase over the mid-window bm-b r1072 chain d1330ca4e6+", "on the ff'd base 7a70aee504 after splice gate0 caught the mid-window bm-a", 1, "race1"),
 ("9c4ef60548, pushed 9c4ef60548..5089f02250 first-try after rebase; engine", "r1073 chain fail-closed zero-disk-pollution, re-ran clean; engine", 1, "race2"),
 ("CLEAN-AT-BIRTH FACE (8th consecutive) on ENGINE MECHANICS: the W275", "CLEAN-AT-BIRTH FACE (9th consecutive) on ENGINE MECHANICS: the W276", 1, "cab-hdr"),
 ("'r1108 GATE-1 CLEAN-AT-BIRTH FACE (8th consecutive)", "'r1111 GATE-1 CLEAN-AT-BIRTH FACE (9th consecutive)", 1, "cab-note"),
 ("the W274-generation date-roll rep was DROPPED count-0 per the", "the W275-generation date-roll rep was DROPPED count-0 per the", 1, "dateroll"),
 ("editor reps first-try; the date-roll rep was DROPPED count-0 per the '", "editor reps first-try; the W275-generation date-roll rep was DROPPED count-0 per the '", 1, "note-dr"),
 ("_set_wave(275) present, _set_wave(274)/_set_wave(273) absent", "_set_wave(276) present, _set_wave(275)/_set_wave(274) absent", 1, "setwave-hdr"),
 ("SPLICE = '018782314d5f9826a45985f533215ce076fbf22b'", "SPLICE = '" + SPLICE + "'", 1, "splice-const"),
 ("io.open('results/_w275bmc_freeze_receipt.json'", "io.open('results/_w276bmc_freeze_receipt.json'", 1, "receipt-path"),
 ("n1t.find('275: {\"batch\": \"PERPETUAL-N1-W275\"')", "n1t.find('276: {\"batch\": \"PERPETUAL-N1-W276\"')", 1, "row-find"),
 ("if '276: {' in seg:", "if '277: {' in seg:", 1, "seg-next"),
 ("seg = seg[:seg.find('276: {')]", "seg = seg[:seg.find('277: {')]", 1, "seg-trim"),
 ("'a_seed_base_620301': '620301' in seg,", "'a_seed_base_622501': '622501' in seg,", 1, "rf-a"),
 ("'b_exit_seed_base_622301': '622301' in seg,", "'b_exit_seed_base_624501': '624501' in seg,", 1, "rf-b"),
 ("'shard_subdir_n1_w275': 'n1_w275' in seg,", "'shard_subdir_n1_w276': 'n1_w276' in seg,", 1, "rf-sd"),
 ("'out_name_n1_w275_results': 'n1_w275_results.json' in seg,", "'out_name_n1_w276_results': 'n1_w276_results.json' in seg,", 1, "rf-out"),
 ("f1 = 'base=620301 span=2000'", "f1 = 'base=622501 span=2000'", 1, "f1"),
 ("f2 = 'base=622301 span=200'", "f2 = 'base=624501 span=200'", 1, "f2"),
 ("m274 = re.search(r'274: \\{\"batch\": \"PERPETUAL-N1-W274\"', n1t)", "m275 = re.search(r'275: \\{\"batch\": \"PERPETUAL-N1-W275\"', n1t)", 1, "m274"),
 ("w274_seg = n1t[m274.start():m274.start() + 9000] if m274 else ''", "w275_seg = n1t[m275.start():m275.start() + 9000] if m275 else ''", 1, "seg274"),
 ("if '275: {' in w274_seg:", "if '276: {' in w275_seg:", 1, "seg274-next"),
 ("w274_seg = w274_seg[:w274_seg.find('275: {')]", "w275_seg = w275_seg[:w275_seg.find('276: {')]", 1, "seg274-trim"),
 ("boundary = bool(m274) and '618101' in w274_seg and '620101' in w274_seg", "boundary = bool(m275) and '620301' in w275_seg and '622301' in w275_seg", 1, "boundary"),
 ("k274pos = n1t.rfind('_set_wave(274)')", "k275pos = n1t.rfind('_set_wave(275)')", 1, "kpos"),
 ("after274 = n1t[k274pos + len('_set_wave(274)'):", "after275 = n1t[k275pos + len('_set_wave(275)'):", 1, "afterpos"),
 ("'w275_block_has_275': '_set_wave(275)' in after274,", "'w276_block_has_276': '_set_wave(276)' in after275,", 1, "swp1"),
 ("'w275_block_has_274': '_set_wave(274)' in after274,", "'w276_block_has_275': '_set_wave(275)' in after275,", 1, "swp2"),
 ("'w275_block_has_273': '_set_wave(273)' in after274,", "'w276_block_has_274': '_set_wave(274)' in after275,", 1, "swp3"),
 ("'whole_file_275_count': n1t.count('_set_wave(275)'),", "'whole_file_276_count': n1t.count('_set_wave(276)'),", 1, "swc1"),
 ("'whole_file_274_count': n1t.count('_set_wave(274)'),", "'whole_file_275_count': n1t.count('_set_wave(275)'),", 1, "swc2"),
 ("'whole_file_273_count': n1t.count('_set_wave(273)'),", "'whole_file_274_count': n1t.count('_set_wave(274)'),", 1, "swc3"),
 ("setwave_ok = (setwave_presence['w275_block_has_275']", "setwave_ok = (setwave_presence['w276_block_has_276']", 1, "swo1"),
 ("and not setwave_presence['w275_block_has_274']", "and not setwave_presence['w276_block_has_275']", 1, "swo2"),
 ("and not setwave_presence['w275_block_has_273']", "and not setwave_presence['w276_block_has_274']", 1, "swo3"),
 ("and setwave_presence['whole_file_275_count'] == 1", "and setwave_presence['whole_file_276_count'] == 1", 1, "swo4"),
 ("and setwave_presence['whole_file_274_count'] == 1", "and setwave_presence['whole_file_275_count'] == 1", 1, "swo5"),
 ("and setwave_presence['whole_file_273_count'] == 1)", "and setwave_presence['whole_file_274_count'] == 1)", 1, "swo6"),
 ("sd = 'results/p2cal_ext/n1_w275'", "sd = 'results/p2cal_ext/n1_w276'", 1, "sharddir"),
 ("'research/PERPETUAL_N1_W275_PREREG.md'", "'research/PERPETUAL_N1_W276_PREREG.md'", 1, "prereg"),
 ("w274 = json.load(io.open('results/perpetual_faces/n1_w274_results.json',", "w275 = json.load(io.open('results/perpetual_faces/n1_w275_results.json',", 1, "prior-load"),
 ("ledger_w274 = _find_ledger(w274)", "ledger_w275 = _find_ledger(w275)", 1, "ledger-var"),
 ("assert ledger_w274 is not None, 'W274 ledger face missing'", "assert ledger_w275 is not None, 'W275 ledger face missing'", 1, "ledger-assert"),
 ("prev_total = ledger_w274['total']", "prev_total = ledger_w275['total']", 1, "prev-total"),
 ("prev_k = w274['null_pool_cumulative']['merged']['n_values']", "prev_k = w275['null_pool_cumulative']['merged']['n_values']", 1, "prev-k"),
 ("up = fr['w274_upstream']", "up = fr['w275_upstream']", 1, "upstream-face"),
 ("w274_finalize_present = os.path.exists('results/perpetual_faces/n1_w274_results.json')", "w275_finalize_present = os.path.exists('results/perpetual_faces/n1_w275_results.json')", 1, "prior-present"),
 ("and w274_finalize_present", "and w275_finalize_present", 1, "prior-present-ok"),
 ('"wave": 275,', '"wave": 276,', 1, "wave-out"),
 ('"phase": "PRE-FINALIZE six-gate (r1108 bm-c own-seat window, 38th consecutive correct-phase target; standing law -- engine self-burn 12/12 landed post-W275 splice 018782314d clean-at-birth 8th generation on engine mechanics, finalize not yet run)"',
  '"phase": "PRE-FINALIZE six-gate (r1111 bm-c own-seat window, 39th consecutive correct-phase target; standing law -- engine self-burn 12/12 landed post-W276 splice 354a645155 clean-at-birth 9th generation on engine mechanics, finalize not yet run)"', 1, "phase-out"),
 ('"w274_finalize_product_present": w274_finalize_present,', '"w275_finalize_product_present": w275_finalize_present,', 1, "prior-out"),
 ('"source": "W274 finalize actuals machine-read from n1_w274_results.json (r587 law)",', '"source": "W275 finalize actuals machine-read from n1_w275_results.json (r587 law)",', 1, "source-out"),
 ('"anchor": "W274 finalize (bm-c r1105 one-pass 1,027,135/K=600,720) honored per freeze receipt w274_upstream face",', '"anchor": "W275 finalize (bm-c r1108 one-pass 1,029,335/K=602,920) honored per freeze receipt w275_upstream face",', 1, "anchor-out"),
 ("and prev_total == 1027135 and prev_k == 600720)", "and prev_total == 1029335 and prev_k == 602920)", 1, "ledger-pre-assert"),
 ("'the W275 splice carried ZERO heals of any class -- zero post-splice '", "'the W276 splice carried ZERO heals of any class -- zero post-splice '", 1, "note-carried"),
 ("commit 018782314d (landed = LF storage face, raw sha16 recorded; '", "commit 354a645155 (landed = LF storage face, raw sha16 recorded; '", 1, "note-splice"),
 ("splice pushed via stash-bridge rebase over the mid-window bm-b r1072 '", "splice landed on the ff-base 7a70aee504 after gate0 caught the mid-window '", 1, "note-race1"),
 ("chain, landed 9c4ef60548..5089f02250), segment-scoped birth-station '", "bm-a r1073 chain fail-closed; engine batch1 df7dedfd07 rode the push), segment-scoped birth-station '", 1, "note-race2"),
 ("os.path.exists('results/_w275bmc_derive_editor.py')", "os.path.exists('results/_w276bmc_derive_editor.py')", 1, "ev-editor"),
 ("os.path.exists('results/_r1108bmc_derive_editor_log.txt')", "os.path.exists('results/_r1111bmc_derive_editor_log.txt')", 1, "ev-log"),
 ("os.path.exists('results/_r1108bmc_needle_preflight.json')", "os.path.exists('results/_r1111bmc_needle_preflight.json')", 1, "ev-preflight"),
 ("io.open('results/_r1108bmc_w275_sixgate.json', 'w', encoding='utf-8')", "io.open('results/_r1111bmc_w276_sixgate.json', 'w', encoding='utf-8')", 1, "out-path"),
]
log_a = build("results/_r1108bmc_w275_sixgate.py", "results/_r1111bmc_w276_sixgate.py", six_reps)
print("\n".join(log_a))

# ---------------- PART B: fivekeys ----------------
# machine-verify the W275 key anchors live from the finalize product (zero-transcription)
d5 = json.load(io.open("results/perpetual_faces/n1_w275_results.json", encoding="utf-8"))
p = d5["null_pool_cumulative"]; s = d5["skill_line_v2_k_lift"]; f = d5["families"]["A_random_engine_exit"]
ANCH = {
 "mu": p["merged"]["mu"], "sigma": p["merged"]["sigma"],
 "a_p95": f["full_sharpe_p95"], "line_merged": s["line_merged_602920"],
 "se_mu": p["se_mu_at_k602920"], "klift": s["line_delta_k_lift"],
 "prev_total": None, "k": p["merged"]["n_values"],
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
ANCH["prev_total"] = _fl(d5)["total"]
assert ANCH["prev_total"] == 1029335 and ANCH["k"] == 602920, (ANCH["prev_total"], ANCH["k"])
assert abs(ANCH["mu"] - (-0.09280540618987594)) < 1e-12, ANCH["mu"]
assert abs(ANCH["sigma"] - 0.24507988853984436) < 1e-12, ANCH["sigma"]
assert ANCH["a_p95"] == 0.3088, ANCH["a_p95"]
assert ANCH["line_merged"] == 1.1967, ANCH["line_merged"]
assert ANCH["se_mu"] == 0.000316, ANCH["se_mu"]
assert ANCH["klift"] == -0.0001, ANCH["klift"]
print("W275 key anchors machine-verified:", {k: v for k, v in ANCH.items()})

fk_reps = [
 ('"""r1108 bm-c: W275 five-prediction-key machine assertion', '"""r1111 bm-c: W276 five-prediction-key machine assertion', 1, "fk-doc"),
 ("Read-only against results/perpetual_faces/n1_w275_results.json + frozen prereg keys.", "Read-only against results/perpetual_faces/n1_w276_results.json + frozen prereg keys.", 1, "fk-res-doc"),
 ("W275 prereg froze its sec.5 keys on W274 finalize actuals (live-chain-head basis;", "W276 prereg froze its sec.5 keys on W275 finalize actuals (live-chain-head basis;", 1, "fk-basis"),
 ("keys machine-read from n1_w274_results.json, r587 never-transcribe law --", "keys machine-read from n1_w275_results.json, r587 never-transcribe law --", 1, "fk-keys-doc"),
 ("live-extracted from the W274", "live-extracted from the W275", 1, "fk-anchors-doc1"),
 ("finalize product this window: mu -0.09280110 / sigma 0.24508947 / a_p95 0.3009 /", "finalize product this window: mu -0.09280541 / sigma 0.24507989 / a_p95 0.3088 /", 1, "fk-anchors-doc2"),
 ("Writes results/_r1108bmc_w275_fivekeys.json receipt.", "Writes results/_r1111bmc_w276_fivekeys.json receipt.", 1, "fk-out-doc"),
 ("Clone lineage: _r1105bmc_w274_fivekeys.py (canon, prior-wave keys variant).", "Clone lineage: _r1108bmc_w275_fivekeys.py (canon, prior-wave keys variant).", 1, "fk-lineage"),
 ('RES = "results/perpetual_faces/n1_w275_results.json"', 'RES = "results/perpetual_faces/n1_w276_results.json"', 1, "fk-res"),
 ('PRIOR = "results/perpetual_faces/n1_w274_results.json"', 'PRIOR = "results/perpetual_faces/n1_w275_results.json"', 1, "fk-prior"),
 ('OUT = "results/_r1108bmc_w275_fivekeys.json"', 'OUT = "results/_r1111bmc_w276_fivekeys.json"', 1, "fk-out"),
 ("# Frozen prediction keys = W274 finalize actuals (machine-read below; the", "# Frozen prediction keys = W275 finalize actuals (machine-read below; the", 1, "fk-frozen"),
 ("full-precision anchors machine-read from the W274 finalize product this", "full-precision anchors machine-read from the W275 finalize product this", 1, "fk-prec"),
 ("KEY_MU_MERGED_W274 = -0.09280109518577706   # W274 finalize merged mu, K=600,720", "KEY_MU_MERGED_W275 = -0.09280540618987594   # W275 finalize merged mu, K=602,920", 1, "fk-kmu"),
 ("KEY_SIGMA_W274 = 0.24508946834133466", "KEY_SIGMA_W275 = 0.24507988853984436", 1, "fk-ksig"),
 ("KEY_A_P95_W274 = 0.3009", "KEY_A_P95_W275 = 0.3088", 1, "fk-kp95"),
 ("KEY_LINE_W274_MERGED = 1.1967", "KEY_LINE_W275_MERGED = 1.1967", 1, "fk-kline"),
 ("KEY_SE_MU_W274 = 0.000316", "KEY_SE_MU_W275 = 0.000316", 1, "fk-kse"),
 ("KEY_KLIFT_W274 = -0.0001", "KEY_KLIFT_W275 = -0.0001", 1, "fk-kkl"),
 ("w274 = json.load(open(PRIOR, encoding=\"utf-8\"))", "w275 = json.load(open(PRIOR, encoding=\"utf-8\"))", 1, "fk-load"),
 ('p1 = w274["null_pool_cumulative"]; s1 = w274["skill_line_v2_k_lift"]', 'p1 = w275["null_pool_cumulative"]; s1 = w275["skill_line_v2_k_lift"]', 1, "fk-p1"),
 ('f1 = w274["families"]["A_random_engine_exit"]', 'f1 = w275["families"]["A_random_engine_exit"]', 1, "fk-f1"),
 ('k_line_merged = s1["line_merged_600720"]', 'k_line_merged = s1["line_merged_602920"]', 1, "fk-kline-read"),
 ('k_se_mu = p1["se_mu_at_k600720"]', 'k_se_mu = p1["se_mu_at_k602920"]', 1, "fk-kse-read"),
 ("KEY_MU_MERGED_W274", "KEY_MU_MERGED_W275", 2, "fk-kmu-ref"),
 ("KEY_SIGMA_W274", "KEY_SIGMA_W275", 2, "fk-ksig-ref"),
 ("KEY_A_P95_W274", "KEY_A_P95_W275", 2, "fk-kp95-ref"),
 ("KEY_LINE_W274_MERGED", "KEY_LINE_W275_MERGED", 2, "fk-kline-ref"),
 ("KEY_SE_MU_W274", "KEY_SE_MU_W275", 2, "fk-kse-ref"),
 ("KEY_KLIFT_W274", "KEY_KLIFT_W275", 2, "fk-kkl-ref"),
 ('se_mu = pool["se_mu_at_k602920"]', 'se_mu = pool["se_mu_at_k605120"]', 1, "fk-semu-read"),
 ('line_pre = sl["line_pre_w275"]', 'line_pre = sl["line_pre_w276"]', 1, "fk-lpre-read"),
 ('line_merged = sl["line_merged_602920"]', 'line_merged = sl["line_merged_605120"]', 1, "fk-lm-read"),
 ('w275_mu = pool["w275_only"]["mu"]', 'w276_mu = pool["w276_only"]["mu"]', 1, "fk-wonly"),
 ('gap1 = abs(w275_mu - merged_mu)', 'gap1 = abs(w276_mu - merged_mu)', 1, "fk-wonly-gap1"),
 ("# key 1: W275-only mu vs merged mu gap", "# key 1: W276-only mu vs merged mu gap", 1, "fk-k1c"),
 ('checks.append(("key1_w275_vs_merged_mu_gap"', 'checks.append(("key1_w276_vs_merged_mu_gap"', 1, "fk-k1"),
 ('checks.append(("key1b_merged_vs_w274_key"', 'checks.append(("key1b_merged_vs_w275_key"', 1, "fk-k1b"),
 ("# key 2: sigma rel change vs W274 key", "# key 2: sigma rel change vs W275 key", 1, "fk-k2c"),
 ("# key 3: A-band p95 vs W274 key (double-direction band)", "# key 3: A-band p95 vs W275 key (double-direction band)", 1, "fk-k3c"),
 ("# key 5: se_mu narrowing vs W274 (se_mu chain face, sec.5 prose)", "# key 5: se_mu narrowing vs W275 (se_mu chain face, sec.5 prose)", 1, "fk-k5c"),
 ('"wave": 275,', '"wave": 276,', 1, "fk-wave"),
 ('"se_mu_k602920": se_mu', '"se_mu_k605120": se_mu', 1, "fk-semu-out"),
 ('"w275_only": {"mu": w275_mu, "sigma": pool["w275_only"]["sigma"]}', '"w276_only": {"mu": w276_mu, "sigma": pool["w276_only"]["sigma"]}', 1, "fk-wonly-out"),
 ('"line_pre_w275": line_pre,', '"line_pre_w276": line_pre,', 1, "fk-lpre-out"),
 ('"line_merged_602920": line_merged,', '"line_merged_605120": line_merged,', 1, "fk-lm-out"),
 ('"keys_anchor": ("W274 finalize actuals machine-read from n1_w274_results.json "', '"keys_anchor": ("W275 finalize actuals machine-read from n1_w275_results.json "', 1, "fk-anchor"),
 ("(r587 law) -- W275 prereg froze sec.5 keys on W274 actuals ", "(r587 law) -- W276 prereg froze sec.5 keys on W275 actuals ", 1, "fk-basis-out"),
 ("(live-chain-head basis; W274 finalize landed pre-draft r1105)\"),", "(live-chain-head basis; W275 finalize landed pre-draft r1108)\"),", 1, "fk-basis2"),
 ('"ledger_identity": {"prev_total": 1027135, "batch_trials": 2200,', '"ledger_identity": {"prev_total": 1029335, "batch_trials": 2200,', 1, "fk-led"),
 ('"total": 1029335,', '"total": 1031535,', 1, "fk-led-tot"),
 ('"exact": (1027135 + 2200) == 1029335},', '"exact": (1029335 + 2200) == 1031535},', 1, "fk-led-ex"),
 ('"merged_k_identity": {"prev_k": 600720, "batch": 2200, "merged_k": merged_k,', '"merged_k_identity": {"prev_k": 602920, "batch": 2200, "merged_k": merged_k,', 1, "fk-kid"),
 ('"exact": (600720 + 2200) == merged_k},', '"exact": (602920 + 2200) == merged_k},', 1, "fk-kid-ex"),
 ('"keys_source": "W274 finalize actuals machine-read from n1_w274_results.json (r587 law)",', '"keys_source": "W275 finalize actuals machine-read from n1_w275_results.json (r587 law)",', 1, "fk-ksrc"),
]
log_b = build("results/_r1108bmc_w275_fivekeys.py", "results/_r1111bmc_w276_fivekeys.py", fk_reps)
print("\n".join(log_b))
print("CLONES BUILT OK")
