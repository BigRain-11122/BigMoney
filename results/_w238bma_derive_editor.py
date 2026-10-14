# -*- coding: utf-8 -*-
# 2026-10-14 12:3x bm-a r984: W238 five-face freeze splice editor DERIVATION
# transform -- template results/_w237bmc_freeze_edits.py (committed, proven
# live-fire by the bm-c r990 window) -> results/_w238bma_freeze_edits.py.
# Lineage law: count-asserted ordered transform, zero transcription, fail-closed
# (any count mismatch = loud abort, the derived editor is NOT written).
# All W237 facts in the derived editor are machine-derived at ITS run time
# (live pf import + pickaxe); this transform only carries the generation shift.
import os, sys, py_compile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(REPO, "results", "_w237bmc_freeze_edits.py")
OUT = os.path.join(REPO, "results", "_w238bma_freeze_edits.py")

raw = open(TPL, "rb").read()
t = raw.decode("utf-8")
IS_CRLF = t.count("\r\n") > (t.count("\n") - t.count("\r\n"))
if IS_CRLF:
    t = t.replace("\r\n", "\n")

fails = []
def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        fails.append((old[:90].replace("\n", "\\n"), c, n))
        return
    t = t.replace(old, new)

def span(start_anchor, end_anchor, new_text, include_end=False):
    global t
    i = t.find(start_anchor)
    if i < 0:
        fails.append((("START-MISS " + start_anchor[:70]), -1, 1)); return
    j = t.find(end_anchor, i + len(start_anchor))
    if j < 0:
        fails.append((("END-MISS " + end_anchor[:70]), -1, 1)); return
    if include_end:
        j += len(end_anchor)
    t = t[:i] + new_text + t[j:]

# ================= 1. header span =================
NEW_HEADER = """# 2026-10-14 12:3x bm-a r984 freeze window (upstream W1..W237 ALL LANDED, clean
# precondition): W238 five-face freeze splice editor -- bm-a OWN-SEAT face (seat
# MSG-20261014-0745-bma-w238-seat published=reserved by bm-a itself @ origin
# 3e551d846 r976, pre-seat probe ADMIT receipt _w238bma_20261014_probe_receipt.json
# same payload; per-wave prereg PERPETUAL_N1_W238_PREREG.md derived+landed own-seat
# r983 commit 8049952c9, zero takeover, zero DRAFT marker). Upstream chain ALL
# LANDED at this window: W1..W237 finalize products present (W237 bm-c own-wave
# closeout r990: five-face splice e4a23cc7a + engine self-burn 12/12 + finalize
# one-pass; net chain head 945,189, merged pool K=519,320, n1_w237_results.json
# machine-read) -- ZERO in-flight upstream seats, clean precondition (twenty-
# seventh consecutive fully-clean freeze window). Upstream six-gate disclosure:
# the W237 cycle ran its PRE-FINALIZE correctly (standing law since the W217
# debt); THIS W238 cycle runs PRE-FINALIZE likewise (standing law).
# Lineage: _w237bmc_freeze_edits.py template (proven live-fire freeze, committed by
# the bm-c r990 window; engine self-burn + finalize verified r990) + r787
# preflight law + r609 origin-verbatim base + r761 programmatic quote wrapping +
# r909 physical-byte anchors + r838 per-file EOL detection + family #6
# LHS/RHS/comment ATOMIC TRIPLE (the new block's w<238>/range(16,238)/
# range(17,238)/below-238 quadruple is count-asserted atomically; the W237 block's
# own w<237 face is legitimate prior-wave boundary, not stale).
# Zero hardcoded upstream band values: ALL W237 facts machine-derived from the
# LIVE pf import at freeze time (the registered W237 row -- bm-c seat honored),
# cross-checked against the committed ADMIT receipt
# (results/_w238bma_20261014_probe_receipt.json) which was derived on the
# post-W237-declared universe. If the LIVE W237 bands differ from the declared
# face, the staircase asserts fail LOUD (fail-closed).
# STRUCTURAL CHOICE (vs the W237 editor): the parity estate (W138..W206 full-span
# 69 rows, r858 absorb generation, + W211..W231 legs) is extracted from the OWN
# W237 block physical bytes -- structure known exactly (bm-c's own splice
# generation, committed) -- the W237 block's own W232 + W233 + W234 + W235 + W236
# legs are excluded from the estate path and fresh W232 + W233 + W234 + W235 +
# W236 + W237 legs are appended for the W238 block parity (96 rows: estate 90
# ending W231 + W232 leg + W233 leg + W234 leg + W235 leg + W236 leg + W237 leg).
# Extraction self-asserts the 90-row cut regardless.
# Disclosed: (a) the inherited W213 leg inside the estate carries a cosmetic
# error-string face ("registered W212 row parity drift") from the r912 editor
# generation -- physical bytes preserved verbatim per extraction law, zero
# functional impact (assert target [213] is correct); (b) the W237 block's
# band-set variable naming one-behind face (w236_a holds wave-237 bands) is
# the lineage's mechanical aging face -- the W238 block follows the same
# mechanical pattern (w237_a holds wave-238 bands), zero functional impact.
# Own bundle hashes (prereg/probe receipt) derived via pickaxe, never transcribed.
# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.
"""
span("# 2026-10-14 08:3x bm-c r990 freeze window",
     "# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.\n",
     NEW_HEADER, include_end=True)

# ================= 2. constants =================
rep('RECEIPT_IN = os.path.join(REPO, "results", "_w237bmc_20261014_probe_receipt.json")',
    'RECEIPT_IN = os.path.join(REPO, "results", "_w238bma_20261014_probe_receipt.json")')
rep('RECEIPT_OUT = os.path.join(REPO, "results", "_w237bmc_freeze_receipt.json")',
    'RECEIPT_OUT = os.path.join(REPO, "results", "_w238bma_freeze_receipt.json")')
rep('SEAT_MSG = "MSG-20261014-0654-bmc-w237-seat.md"',
    'SEAT_MSG = "MSG-20261014-0745-bma-w238-seat.md"')
rep('SEAT_ORIGIN = "9312ef7ac"', 'SEAT_ORIGIN = "3e551d846"')

# ================= 3. gate 0.5 =================
rep("# ---------- gate 0.5: W236 five-face landed + W236 finalize product present ----------",
    "# ---------- gate 0.5: W237 five-face landed + W237 finalize product present ----------")
rep("# (chain-order precondition; W235/W234/W233/W232/W231/W230/W225/W224 finalize are",
    "# (chain-order precondition; W236/W235/W234/W233/W232/W231/W230/W225 finalize are")
rep("W236 = dict(pf_mod.N1_BANDS.get(236) or {})",
    "W237 = dict(pf_mod.N1_BANDS.get(237) or {})")
rep('assert W236.get("engine_owner") == "bm-a", \\',
    'assert W237.get("engine_owner") == "bm-c", \\')
rep('    f"W236 row not landed as declared (bm-a seat owner expected): {W236} -- five-face freeze missing;" \\',
    '    f"W237 row not landed as declared (bm-c seat owner expected): {W237} -- five-face freeze missing;" \\')
rep('w236_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w236_results.json")',
    'w237_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w237_results.json")')
rep('assert os.path.exists(w236_out_path), "W236 finalize product missing (n1_w236_results.json) -- chain dep not met"',
    'assert os.path.exists(w237_out_path), "W237 finalize product missing (n1_w237_results.json) -- chain dep not met"')
# w224 belt-and-braces slides out (8-deep window), w236 slides in as transitive
rep('w224_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w224_results.json")\nassert os.path.exists(w224_out_path), "W224 finalize product missing (transitive chain dep) -- abort"\n',
    '')
rep('assert os.path.exists(w237_out_path), "W237 finalize product missing (n1_w237_results.json) -- chain dep not met"\n',
    'assert os.path.exists(w237_out_path), "W237 finalize product missing (n1_w237_results.json) -- chain dep not met"\nw236_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w236_results.json")\nassert os.path.exists(w236_out_path), "W236 finalize product missing (transitive chain dep) -- abort"\n')
rep('w236_out = json.load(open(w236_out_path, encoding="utf-8"))',
    'w237_out = json.load(open(w237_out_path, encoding="utf-8"))')
rep('w236_led = (w236_out.get("science_gates") or {}).get("ledger") or {}',
    'w237_led = (w237_out.get("science_gates") or {}).get("ledger") or {}')
rep('w236_total = w236_led.get("total")', 'w237_total = w237_led.get("total")')
rep('w236_merged_n = None', 'w237_merged_n = None')
rep('    w236_merged_n = w236_out["null_pool_cumulative"]["merged"]["n_values"]',
    '    w237_merged_n = w237_out["null_pool_cumulative"]["merged"]["n_values"]')
rep('assert w236_total == 942_989 and w236_merged_n == 517_120, \\',
    'assert w237_total == 945_189 and w237_merged_n == 519_320, \\')
rep('    f"W236 finalize anchors drift at freeze time: total={w236_total} merged={w236_merged_n} (expect 942,989 / 517,120)"',
    '    f"W237 finalize anchors drift at freeze time: total={w237_total} merged={w237_merged_n} (expect 945,189 / 519,320)"')
rep('-S", \'236: {"a"\'', '-S", \'237: {"a"\'')
rep('w236_freeze_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]',
    'w237_freeze_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]')
# ORDER MATTERS (fail-closed trap): rename the higher-wave own-prereg pickaxe
# FIRST (W237->W238), else the W236->W237 rename below creates a duplicate.
rep('r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W237_PREREG.md")',
    'r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W238_PREREG.md")')
rep('w237_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]',
    'w238_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]')
rep('r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W236_PREREG.md")',
    'r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W237_PREREG.md")')
rep('w236_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]',
    'w237_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]')
rep('assert os.path.exists(os.path.join(REPO, "research", "PERPETUAL_N1_W237_PREREG.md")), \\',
    'assert os.path.exists(os.path.join(REPO, "research", "PERPETUAL_N1_W238_PREREG.md")), \\')
rep('    "W237 per-wave prereg missing on disk -- chain face incomplete, abort (r990 derive landed pre-freeze expected)"',
    '    "W238 per-wave prereg missing on disk -- chain face incomplete, abort (r983 derive landed pre-freeze expected)"')
rep('with open(os.path.join(REPO, "research", "PERPETUAL_N1_W237_PREREG.md"), encoding="utf-8") as _fh:',
    'with open(os.path.join(REPO, "research", "PERPETUAL_N1_W238_PREREG.md"), encoding="utf-8") as _fh:')
rep('assert "DRAFT-NOT-FROZEN" not in _pre_head, "W237 prereg still DRAFT -- abort (freeze commit pending face)"',
    'assert "DRAFT-NOT-FROZEN" not in _pre_head, "W238 prereg still DRAFT -- abort (freeze commit pending face)"')

# ================= 4. live ordinal derive =================
rep("# receipt leg0 face owner_rows=225 / bmc_rows=64 / ordinal=227 / bmc_ordinal=65",
    "# receipt leg0 face owner_rows=226 / bma_rows=121 / ordinal=228 / bma_ordinal=122")
rep("# = seat-time PRE-W236-splice live faces; live derive at freeze time:",
    "# = seat-time PRE-W237-splice live faces; live derive at freeze time:")
rep("# W236 splice LANDED -> owner rows 226 + candidate = 227th EXACT; bm-c rows 64 +",
    "# W237 splice LANDED -> owner rows 227 + candidate = 228th EXACT; bm-a rows 121 +")
rep("# candidate = 65th EXACT -- bm-c own-seat continuity face, zero takeover)",
    "# candidate = 122nd EXACT -- bm-a own-seat continuity face, zero takeover)")
rep("assert len(owner_rows_live) == 226 and len(bmc_rows_live) == 64, \\",
    "assert len(owner_rows_live) == 227 and len(bma_rows_live) == 121, \\")
rep('    f"leg0 ordinal drift at freeze time: owner={len(owner_rows_live)} bmc={len(bmc_rows_live)} (expect 226/64 PRE-splice post-W236 registration; this candidate = bm-c\'s 65th own wave per the same live-derive law, r587/r359)"',
    '    f"leg0 ordinal drift at freeze time: owner={len(owner_rows_live)} bma={len(bma_rows_live)} (expect 227/121 PRE-splice post-W237 registration; this candidate = bm-a\'s 122nd own wave per the same live-derive law, r587/r359)"')
rep('print(f"gate0.5 OK: W236 landed (freeze {w236_freeze_sha[:10]}, owner=bm-a seat honored, zero takeover face), "',
    'print(f"gate0.5 OK: W237 landed (freeze {w237_freeze_sha[:10]}, owner=bm-c seat honored, zero takeover face), "')
rep('      f"W236+W235+W234+W233+W232+W231+W230+W225+W224 finalize products present "',
    '      f"W237+W236+W235+W234+W233+W232+W231+W230+W225 finalize products present "')
rep('      f"(W236 ledger head {w236_total}, merged n={w236_merged_n}); owner rows {len(owner_rows_live)} + candidate, "',
    '      f"(W237 ledger head {w237_total}, merged n={w237_merged_n}); owner rows {len(owner_rows_live)} + candidate, "')
rep('      f"bm-c rows {len(bmc_rows_live)} + candidate (65th own wave per live derive; "',
    '      f"bm-a rows {len(bma_rows_live)} + candidate (122nd own wave per live derive; "')
rep('      f"probe receipt leg0 owner_rows=225 / bmc_ordinal=65 = seat-time pre-splice faces disclosed honest)")',
    '      f"probe receipt leg0 owner_rows=226 / bma_ordinal=122 = seat-time pre-splice faces disclosed honest)")')

# ================= 5. band facts =================
rep("# W237 probe receipt bands carry int-list faces + explicit lo/hi keys",
    "# W238 probe receipt bands carry int-list faces + explicit lo/hi keys")
rep("assert (a_lo, a_hi) == (536_204, 538_203) and (b_lo, b_hi) == (538_204, 538_403), \\",
    "assert (a_lo, a_hi) == (538_404, 540_403) and (b_lo, b_hi) == (540_404, 540_603), \\")
rep('    f"W237 band drift vs probe ADMIT: {(a_lo, a_hi)} {(b_lo, b_hi)}"',
    '    f"W238 band drift vs probe ADMIT: {(a_lo, a_hi)} {(b_lo, b_hi)}"')
rep('w236_b_tail = W236["b_exit"][1]      # registered W236 row b_exit hi (pf import, live)',
    'w237_b_tail = W237["b_exit"][1]      # registered W237 row b_exit hi (pf import, live)')
rep('w236_a_tail = W236["a"][1]            # registered W236 row A hi (pf import, live)',
    'w237_a_tail = W237["a"][1]            # registered W237 row A hi (pf import, live)')
rep('assert w236_b_tail + 1 == a_lo and a_hi + 1 == b_lo, "staircase base relations broken"',
    'assert w237_b_tail + 1 == a_lo and a_hi + 1 == b_lo, "staircase base relations broken"')
rep("# the REFUSED arithmetic continuation starts at prior-wave A-tail+1 (== W236 B-base),",
    "# the REFUSED arithmetic continuation starts at prior-wave A-tail+1 (== W237 B-base),")
rep('assert w236_a_tail + 1 == W236["b_exit"][0], "W236 A-tail+1 != W236 B-base (registered row in-wave relation)"',
    'assert w237_a_tail + 1 == W237["b_exit"][0], "W237 A-tail+1 != W237 B-base (registered row in-wave relation)"')
rep("assert [w236_a_tail + 1, w236_a_tail + 2_000] == leg1[\"ARITH_A\"], \\",
    "assert [w237_a_tail + 1, w237_a_tail + 2_000] == leg1[\"ARITH_A\"], \\")
rep("    f\"refused-continuation start drift vs probe receipt leg1 ARITH_A: {[w236_a_tail + 1, w236_a_tail + 2_000]} != {leg1['ARITH_A']}\"",
    "    f\"refused-continuation start drift vs probe receipt leg1 ARITH_A: {[w237_a_tail + 1, w237_a_tail + 2_000]} != {leg1['ARITH_A']}\"")

# ================= 6. own bundle shas + seat + banned gate =================
rep('r = git("log", "--diff-filter=A", "--format=%H", "--", "results/_w237bmc_20261014_probe_receipt.json")',
    'r = git("log", "--diff-filter=A", "--format=%H", "--", "results/_w238bma_20261014_probe_receipt.json")')
rep('w237_receipt_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]',
    'w238_receipt_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]')
rep('assert seat_found, f"W237 seat MSG missing from both inbox paths: {SEAT_MSG}"',
    'assert seat_found, f"W238 seat MSG missing from both inbox paths: {SEAT_MSG}"')
rep('                    "--prereg", "research/PERPETUAL_N1_W237_PREREG.md"],',
    '                    "--prereg", "research/PERPETUAL_N1_W238_PREREG.md"],')

# ================= 7. parity extraction =================
rep("# STRUCTURAL CHOICE: extract the estate from the OWN W236 block (bytes known",
    "# STRUCTURAL CHOICE: extract the estate from the OWN W237 block (bytes known")
rep("# leg = 90 rows) -- the W236 block is bm-a's own splice generation",
    "# leg = 90 rows) -- the W237 block is bm-c's own splice generation")
rep("# (r974/r975 window editor), structure known. The W236 block span ends",
    "# (r990 window editor), structure known. The W237 block span ends")
rep("a16 = '    # --- W236 materializer face'", "a17 = '    # --- W237 materializer face'")
rep("w236_start = n1_t.find(a16); t141_pos = n1_t.find(a_t141)",
    "w237_start = n1_t.find(a17); t141_pos = n1_t.find(a_t141)")
rep("assert w236_start > 0 and t141_pos > w236_start, \\",
    "assert w237_start > 0 and t141_pos > w237_start, \\")
rep('    "W236 materializer block face not found (W236 freeze not landed? header-text drift -> honest re-derive required)"',
    '    "W237 materializer block face not found (W237 freeze not landed? header-text drift -> honest re-derive required)"')
rep("blk = n1_t[w236_start:t141_pos]", "blk = n1_t[w237_start:t141_pos]")
rep('    "parity span markers not found in W236 block"',
    '    "parity span markers not found in W237 block"')
rep('assert m232, "upstream W232 row leg not found inside W236 parity span"',
    'assert m232, "upstream W232 row leg not found inside W237 parity span"')
rep('assert par_full.count("assert pf.N1_BANDS[") == 94, \\',
    'assert par_full.count("assert pf.N1_BANDS[") == 95, \\')
rep("    f\"full parity span {par_full.count('assert pf.N1_BANDS[')} != 94 (69 estate + W211..W230 legs + W231 leg + W232 leg + W233 leg + W234 leg + W235 leg)\"",
    "    f\"full parity span {par_full.count('assert pf.N1_BANDS[')} != 95 (69 estate + W211..W230 legs + W231 leg + W232 leg + W233 leg + W234 leg + W235 leg + W236 leg)\"")

# ================= 8. indent extraction + row owner line =================
rep('CFG_I  = line_indent(n1_t, \'236: {"batch"\', EOL)',
    'CFG_I  = line_indent(n1_t, \'237: {"batch"\', EOL)')
rep('PRE_KEY_I = line_indent(n1_t, \'"prereg": ("research/PERPETUAL_N1_W236_PREREG.md\', EOL)',
    'PRE_KEY_I = line_indent(n1_t, \'"prereg": ("research/PERPETUAL_N1_W237_PREREG.md\', EOL)')
rep("# MEM_I derived INSIDE the W236 cfg entry span (own splice generation, value",
    "# MEM_I derived INSIDE the W237 cfg entry span (own splice generation, value")
rep("_c236 = n1_t.find('236: {\"batch\"')", "_c237 = n1_t.find('237: {\"batch\"')")
rep('assert _c236 > 0, "W236 cfg entry not found (W236 freeze not landed?)"',
    'assert _c237 > 0, "W237 cfg entry not found (W237 freeze not landed?)"')
rep('_mpos = n1_t.find(\'"a_seed_base"\', _c236)', '_mpos = n1_t.find(\'"a_seed_base"\', _c237)')
rep('assert _mpos > 0 and n1_t.find(\'"shard_subdir"\', _c236) > _mpos, "W236 cfg a_seed_base line not found"',
    'assert _mpos > 0 and n1_t.find(\'"shard_subdir"\', _c237) > _mpos, "W237 cfg a_seed_base line not found"')
rep("MEM_I  = line_indent(n1_t, '\"a_seed_base\": ' + str(W236[\"a\"][0]), EOL) \\",
    "MEM_I  = line_indent(n1_t, '\"a_seed_base\": ' + str(W237[\"a\"][0]), EOL) \\")
rep("    if n1_t.find('\"a_seed_base\": ' + str(W236[\"a\"][0]), _c236) > 0 \\",
    "    if n1_t.find('\"a_seed_base\": ' + str(W237[\"a\"][0]), _c237) > 0 \\")
rep("    else line_indent(n1_t, '\"a_seed_base\": ' + fmt(W236[\"a\"][0]), EOL)",
    "    else line_indent(n1_t, '\"a_seed_base\": ' + fmt(W237[\"a\"][0]), EOL)")
rep("ROW_I  = line_indent(pf_t,  '236: {\"a\"', PF_EOL)",
    "ROW_I  = line_indent(pf_t,  '237: {\"a\"', PF_EOL)")
rep("# ---------- W236 row owner line (physical bytes; comment text is own generation) ----------",
    "# ---------- W237 row owner line (physical bytes; comment text is own generation) ----------")
rep("w236_row_start = pf_t.find('    236: {\"a\"')", "w237_row_start = pf_t.find('    237: {\"a\"')")
rep('assert w236_row_start > 0, "W236 row literal not found in pf source"',
    'assert w237_row_start > 0, "W237 row literal not found in pf source"')
rep("_own_ls = pf_t.find(PF_EOL, w236_row_start) + len(PF_EOL)",
    "_own_ls = pf_t.find(PF_EOL, w237_row_start) + len(PF_EOL)")
rep("w236_own_line = pf_t[_own_ls:_own_le]", "w237_own_line = pf_t[_own_ls:_own_le]")
rep("assert '\"engine_owner\": \"bm-a\"' in w236_own_line, \\",
    "assert '\"engine_owner\": \"bm-c\"' in w237_own_line, \\")
rep("    f\"W236 owner line unexpected bytes: {w236_own_line!r}\"",
    "    f\"W237 owner line unexpected bytes: {w237_own_line!r}\"")
rep("ROWC_I = w236_own_line[:len(w236_own_line) - len(w236_own_line.lstrip(\" \"))]",
    "ROWC_I = w237_own_line[:len(w237_own_line) - len(w237_own_line.lstrip(\" \"))]")

# ================= 9. pf_comment span =================
NEW_PF_COMMENT = '''pf_comment = PF_EOL.join([
"    # W238 (bm-a loop five-face freeze splice -- OWN-SEAT face, seat",
"    # MSG-20261014-0745-bma-w238-seat published=reserved by bm-a itself @",
"    # origin " + SEAT_ORIGIN + " (r976, zero takeover); prereg + ADMIT probe",
"    # receipt frozen commit " + w238_prereg_sha[:10] + " (prereg research/PERPETUAL_N1_W238_PREREG.md",
"    # r983 own-seat derive landed pre-freeze, probe",
"    # results/_w238bma_20261014_probe_receipt.json @ " + w238_receipt_sha[:10] + ");",
"    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10",
"    # ~23:1x; deletion-set EMPTY; delivery window = chain-order",
"    # splice AFTER the bm-c W237 five-face (freeze " + w237_freeze_sha[:10] + ") + W237",
"    # finalize product landed (n1_w237_results.json present, ledger",
"    # head " + str(w237_total) + " machine-read at freeze time); zero --no-verify;",
"    # the W238 seat MSG sits in " + seat_found + " at freeze",
"    # time, honest archived per S7 law);",
"    # band gate ADMIT results/_w238bma_20261014_probe_receipt.json: A = FIRST-CLEAN",
"    # past the registered W237 B band (arithmetic continuation",
"    # " + fmt(w237_a_tail + 1) + ".." + fmt(w237_a_tail + 2_000) + " REFUSED at its own start by the W237 B band",
"    # " + fmt(W237["b_exit"][0]) + ".." + fmt(w237_b_tail) + ", exactly as the W237 seat leg4",
"    # projection anticipated);",
"    # honest forward walk hops=1 -> " + fmt(a_lo) + ".." + fmt(a_hi) + ", non-rotational",
"    # r587 forward-monotone walk; A base == prior-wave B tail+1",
"    # (" + fmt(w237_b_tail) + "+1) machine-checkable -- A-hops-prior-B staircase",
"    # NINETY-EIGHTH instance, E36 card (probe receipt leg1 A_semantics",
"    # machine-read ordinal, never transcribed);",
"    # B = FIRST-CLEAN past the own-wave A window (arithmetic",
"    # continuation " + fmt(a_lo) + ".." + fmt(a_lo + 199) + " CLEAN on the registered",
"    # universe but lands INSIDE the W238 A band window " + fmt(a_lo) + ".." + fmt(a_hi) + " --",
"    # same-freeze mutual exclusion (W141 precedent, leg2 law) --",
"    # the walk with the own-wave A window reserved jumps to",
"    # " + fmt(b_lo) + " -> " + fmt(b_lo) + ".." + fmt(b_hi) + ", hops=1, non-rotational",
"    # r587 forward-monotone walk; B base == own-wave A tail+1",
"    # (" + fmt(a_hi) + "+1) machine-checkable);",
"    # single-window derive (r812 merged the gate legs INTO the",
"    # pre-seat probe; dual-window parity N/A honest); scan face =",
"    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1",
"    # used-seed band + probe cluster 95_000..95_003 + cross-face",
"    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/",
"    # N2-W15 probe points.",
"    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):",
"    # " + gate_lines[0] + ";",
"    # " + gate_lines[1] + ".",
"    # W239+ projection (gate-derived pre-seat probe leg4, pre-W238",
"    # universe): A naive first-clean " + rec["legs"]["leg4"]["W239p_A_naive"] + " REFUSED by live",
"    # SEED_REGISTRY points " + str(rec["legs"]["leg4"]["W239p_A_naive_refusers_seeds"]) + " (NEW FACE: first live-seed refusal",
"    # above the registered tail) -> honest walk first-clean",
"    # " + rec["legs"]["leg4"]["W239p_A_first_clean"] + " hops=" + str(rec["legs"]["leg4"]["hops_A"]) + " /",
"    # B naive first-clean " + rec["legs"]["leg4"]["W239p_B_naive"] + " CLEAN hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " -- naive B lands",
"    # INSIDE the naive A window and the registered W238 B band",
"    # " + fmt(b_lo) + ".." + fmt(b_hi) + " will refuse the naive W239 A window; W239 freezer",
"    # MUST re-derive on the post-W238 universe AND reserve the",
"    # own-wave A window when deriving B (W141 precedent, leg2 law,",
"    # E36 staircase card, NINETY-NINTH instance anticipated; never transcribe r587).",
])
'''
span("pf_comment = PF_EOL.join([\n", "\n])\n", NEW_PF_COMMENT, include_end=True)

# pf_row + old_pf/new_pf anchors
rep("pf_row = (f'{ROW_I}237: {{\"a\": ({fmt(a_lo)}, {fmt(a_hi)}), '",
    "pf_row = (f'{ROW_I}238: {{\"a\": ({fmt(a_lo)}, {fmt(a_hi)}), '")
rep("          + PF_EOL + f'{ROWC_I}\"engine_owner\": \"bm-c\"}},' + PF_EOL)",
    "          + PF_EOL + f'{ROWC_I}\"engine_owner\": \"bm-a\"}},' + PF_EOL)")
rep("    f'237: {{\"a\": ({fmt(a_lo)}, {fmt(a_hi)}), \"b_exit\": ({fmt(b_lo)}, {fmt(b_hi)}),'",
    "    f'238: {{\"a\": ({fmt(a_lo)}, {fmt(a_hi)}), \"b_exit\": ({fmt(b_lo)}, {fmt(b_hi)}),'")
rep("old_pf = must(pf_t, (w236_own_line + PF_EOL + '}'",
    "old_pf = must(pf_t, (w237_own_line + PF_EOL + '}'")
rep("new_pf = (w236_own_line + PF_EOL", "new_pf = (w237_own_line + PF_EOL")

# ================= 10. cfg section span (fin_face + cfg_lines + PRE + MEM) =================
NEW_CFG_SECTION = '''fin_face = (f"W1..W237 finalize ALL LANDED (W237 finalize product present at splice, "
            f"net chain head {w237_total} machine-read, merged pool K={w237_merged_n} "
            f"machine-read) -- ZERO in-flight upstream seats at splice time, clean precondition; "
            f"downstream W239 seat NOT yet published (queue-deepen seat-chain mandate "
            f"O-20261011-0012 sec.ii -- next seat publication follows per seat-first law)")
cfg_lines = [
 f'{CFG_I}238: {{"batch": "PERPETUAL-N1-W238",',
 f'{PRE_KEY_I}"prereg": ("research/PERPETUAL_N1_W238_PREREG.md (wave-level frozen "',
]
PRE = [
 "pre-run; design = frozen v1 null calibration verbatim, ",
 "new seed bands only; TWO HUNDRED AND THIRTY-EIGHTH ENGINE-OWNED WAVE ",
 f"BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate), ",
 "own-series continuation per O-20260101-2355 sec.2 (first-free-",
 "number law after the REGISTERED W237 row five-face freeze (bm-c own seat executed at the r990 window; engine self-burn 12/12; finalize one-pass r990 08:5x, ledger 942,989+2,200=945,189 / K=519,320 machine-read), ",
 f"{w237_freeze_sha[:10]} (prereg {w237_prereg_sha[:10]}), SINGLE STATE zero seat gap W2..W237 all ",
 "registered; " + fin_face + "; ",
 "seat published=reserved ",
 "MSG-20261014-0745-bma-w238-seat PUSHED to origin " + SEAT_ORIGIN + " ",
 "BEFORE this freeze per r565 early-visibility law (payload = ",
 "seat MSG + pre-seat probe script + probe receipt; per-wave prereg ",
 "r983 own-seat derive landed pre-freeze -- zero takeover face, bm-a own-seat ",
 "continuity, ",
 f"prereg {w238_prereg_sha[:10]} @ receipt {w238_receipt_sha[:10]}) -- this freeze splice editor derived from the committed W237 editor template in this same freeze window; ",
 "deletion-set EMPTY; delivery window = chain-order splice ",
 "after the W237 five-face + W237 finalize product landed ",
 "(executed in the bm-a loop freeze window ",
 "under the CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED ",
 "2026-10-10 ~23:1x); zero merge at freeze delivery, zero ",
 "--no-verify; single-window derive -- r812 merged the gate ",
 "legs INTO the pre-seat probe; parity N/A honest), ",
 "engine_owner=bm-a (bm-a OWN-SEAT face -- bm-a's ONE HUNDRED AND ",
 "TWENTY-SECOND owned claim per machine-derive (engine_owner==bm-a rows ",
 f"{len(bma_rows_live)} + candidate; probe receipt leg0 owner_rows=226 / bma_ordinal=122 = seat-time pre-splice ",
 "live faces disclosed honest, live derive governs ",
 "r587/r359 -- zero takeover, own-seat continuity)), ",
 "wave 238: ",
 "A = FIRST-CLEAN past the registered W237 B band (the ",
 f"arithmetic continuation {fmt(w237_a_tail + 1)}..{fmt(w237_a_tail + 2_000)} is REFUSED at its ",
 f"own start by the W237 B band {fmt(W237['b_exit'][0])}..{fmt(w237_b_tail)}, exactly as ",
 "the W237 seat leg4 succession ",
 "projection notes anticipated; honest forward walk hops=1 -> ",
 f"{fmt(a_lo)}..{fmt(a_hi)}; A base == prior-wave B tail+1 ",
 "machine-checkable = A-hops-prior-B staircase NINETY-EIGHTH ",
 "instance, E36 card (probe receipt leg1 machine-read ordinal); ",
 "non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN ",
 "past the own-wave A window (the arithmetic continuation ",
 f"{fmt(a_lo)}..{fmt(a_lo + 199)} is CLEAN on the registered universe but lands ",
 f"INSIDE the W238 A band window {fmt(a_lo)}..{fmt(a_hi)} -- same-freeze mutual ",
 "exclusion, W141 precedent, leg2 law -- the walk with the ",
 f"own-wave A window reserved jumps to {fmt(b_lo)}, first-clean ",
 f"{fmt(b_lo)}..{fmt(b_hi)} hops=1, non-rotational r587 forward-monotone walk; ",
 "B base == own-wave A tail+1 machine-checkable; cross-window ",
 "convergence with the W237 seat leg4 succession projection ",
 "notes -- all MANDATORY notes honored (post-W237 universe ",
 "re-derive + own-wave A reservation); ADMIT receipt ",
 "results/_w238bma_20261014_probe_receipt.json + ",
 "seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a ",
 "ADMIT convention); W239+ projection per this window gate: ",
 f"A naive first-clean {rec['legs']['leg4']['W239p_A_naive']} REFUSED by live SEED_REGISTRY points ",
 f"{rec['legs']['leg4']['W239p_A_naive_refusers_seeds']} -> honest walk first-clean ",
 f"{rec['legs']['leg4']['W239p_A_first_clean']} CLEAN; B naive first-clean ",
 f"{rec['legs']['leg4']['W239p_B_naive']} CLEAN -- naive B lands INSIDE the naive A window and ",
 f"the registered W238 B band {fmt(b_lo)}..{fmt(b_hi)} will refuse the naive W239 A window; ",
 "W239+ freezer MUST re-derive on the post-W238 universe AND ",
 "reserve the own-wave A window when deriving B (W141 precedent, ",
 "leg2 law, E36 staircase card, NINETY-NINTH instance anticipated) -- ",
 "downstream W239 seat publication pending per seat-first law; " + fin_face + " -- the finalize ",
 "merge loop still derives the wave set from registry keys at ",
 "run time, FAIL-CLOSED r307 always on)",
]
for i, s in enumerate(PRE):
    if i == len(PRE) - 1:
        cfg_lines.append(f'{PRE_I}"{s}"),')
    else:
        cfg_lines.append(f'{PRE_I}"{s}"')
cfg_lines += [
 f'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W238 A: {fmt(a_lo)}..{fmt(a_hi)} (FIRST-CLEAN past the registered W237 B band; arithmetic {fmt(w237_a_tail + 1)}..{fmt(w237_a_tail + 2_000)} REFUSED at own start by the W237 B band {fmt(W237["b_exit"][0])}..{fmt(w237_b_tail)}; hops=1; A-hops-prior-B staircase NINETY-EIGHTH instance, E36 card; ordinal machine-read NINETY-EIGHTH per probe receipt)',
 f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W238 B: {fmt(b_lo)}..{fmt(b_hi)} (FIRST-CLEAN past the own-wave A window; arithmetic {fmt(a_lo)}..{fmt(a_lo + 199)} lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
 f'{MEM_I}"shard_subdir": "n1_w238", "out_name": "n1_w238_results.json",',
 f'{MEM_I}"engine_owner": "bm-a"}},',
]
'''
span('fin_face = (f"W1..W236', "cfg_block = EOL.join(cfg_lines)", NEW_CFG_SECTION + "\n")
rep("assert new_cfg.count('237: {\"batch\": \"PERPETUAL-N1-W237\"') == 1",
    "assert new_cfg.count('238: {\"batch\": \"PERPETUAL-N1-W238\"') == 1")

# ================= 11. hdr span =================
NEW_HDR = '''hdr = [
 "    # --- W238 materializer face (bm-a loop five-face freeze splice --",
 "    #     OWN-SEAT face under CEO fill-order standing 2026-10-08 ~23:5x",
 "    #     + RE-ISSUE 2026-10-10 ~23:1x + O-20260909-2334-bm-b sec.1-2",
 "    #     local-full-use + O-20260924-1730 claim-and-start same-round law):",
 "    #     bm-a's one hundred and twenty-second owned per machine-derive (engine_owner==bm-a",
 f"    #     rows {len(bma_rows_live)} + candidate; own-seat face: seat published=reserved by bm-a itself",
 "    #     (r976 MSG-20261014-0745-bma-w238-seat @ origin 3e551d846; probe leg0",
 "    #     owner_rows=226 / bma_ordinal=122 = seat-time pre-splice faces;",
 "    #     live derive at freeze governs);",
 "    #     wave 238 = first free number after the",
 "    #     REGISTERED W237 row (five-face freeze " + w237_freeze_sha[:10] + "; bm-c own seat executed at",
 "    #     the r990 window; engine",
 "    #     self-burn 12/12 + finalize one-pass r990 08:5x",
 "    #     splice estate + PRE-FINALIZE six-gate chain (standing law held) honest note)",
 "    #     -- SINGLE STATE zero seat gap (W2..W237 all registered). Seat",
 "    #     published=reserved MSG-20261014-0745-bma-w238-seat pushed",
 "    #     to origin " + SEAT_ORIGIN + " BEFORE this freeze, r565 law (payload =",
 "    #     seat MSG + pre-seat probe script + probe receipt; per-wave prereg",
 f"    #     r983 own-seat derive landed pre-freeze commit {w238_prereg_sha[:10]}; this freeze splice editor",
 "    #     derived from the committed W237 editor template in this same freeze",
 "    #     window; deletion-set EMPTY; delivery window",
 "    #     = chain-order splice after the W237 five-face + W237 finalize",
 "    #     product landed; zero --no-verify; the W238 seat MSG sits in",
 "    #     " + seat_found + " at freeze time, honest archived",
 "    #     per S7 law).",
 "    #     TWO HUNDRED AND THIRTY-EIGHTH engine wave BY",
 f"    #     MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate; gate",
 "    #     leg0 machine output governs per r359 law).",
 f"    #     {fin_face}; the finalize merge loop",
 "    #     still derives the wave set from registry keys at run",
 "    #     time, FAIL-CLOSED r307 always on. ADMIT receipt",
 "    #     results/_w238bma_20261014_probe_receipt.json;",
 "    #     seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a",
 f"    #     ADMIT convention upgrade): {gate_lines[0]}; {gate_lines[1]};",
 "    #     banned gate ADMIT 0 (re-run at freeze window);",
 "    #     not a re-pick (R250: W238 bands were never assigned).",
 "    _set_wave(238)",
 "    try:",
 '        assert WAVE_CONFIGS[237]["a_seed_base"] == pf.N1_BANDS[237]["a"][0], \\\\',
 '            "W238 upstream W237 mirror drift (a)"',
 "        assert WAVE_CONFIGS[237][\\"b_exit_seed_base\\"] == \\\\",
 '            pf.N1_BANDS[237]["b_exit"][0], "W238 upstream W237 mirror drift (b)"',
 "        assert WAVE_CONFIGS[237].get(\\"engine_owner\\") == \\\\",
 '            pf.N1_BANDS[237].get("engine_owner") == "bm-c", \\\\',
 '            "W238 upstream W237 engine_owner mirror drift (law-mirror parity; bm-c upstream seat face)"',
 "        w237_a = {A_SEED_BASE + j for j in range(A_N)}",
 "        w237_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
 '        assert not (w237_a & w237_b), "W238 A/B band overlap"',
 "        assert not (w237_a & reg_ints) and not (w237_b & reg_ints), \\\\",
 '            "W238 hits SEED_REGISTRY"',
 '        for nm, band in (("A", w237_a), ("B", w237_b)):',
 '            assert not (band & v1_a) and not (band & v1_b), f"W238 {nm} hits v1"',
 '            assert not (band & w1_a) and not (band & w1_b), f"W238 {nm} hits W1"',
 '            assert not (band & probes), f"W238 {nm} hits probe seeds"',
]
'''
span("hdr = [\n", "\nw232_leg = [", NEW_HDR)

# ================= 12. w237_leg insertion + block assembly =================
rep('''            "registered W236 row parity drift (r307; bm-a five-face freeze; own-seat face disclosed)"',
]
''',
    '''            "registered W236 row parity drift (r307; bm-a five-face freeze; own-seat face disclosed)"',
]
w237_leg = [
 f'        assert pf.N1_BANDS[237] == {{"a": ({fmt(pf_mod.N1_BANDS[237]["a"][0])}, {fmt(pf_mod.N1_BANDS[237]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[237]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[237]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\\\',
'            "registered W237 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]
''')
rep("block = EOL.join(hdr) + EOL + par_sec + EOL.join(w232_leg) + EOL + EOL.join(w233_leg) + EOL + EOL.join(w234_leg) + EOL + EOL.join(w235_leg) + EOL + EOL.join(w236_leg) + EOL + EOL.join(tail) + EOL",
    "block = EOL.join(hdr) + EOL + par_sec + EOL.join(w232_leg) + EOL + EOL.join(w233_leg) + EOL + EOL.join(w234_leg) + EOL + EOL.join(w235_leg) + EOL + EOL.join(w236_leg) + EOL + EOL.join(w237_leg) + EOL + EOL.join(tail) + EOL")

# ================= 13. family-6 triple =================
rep('assert block.count("if w < 237)") == 3, f"family-6 triple: w<237 count {block.count(\'if w < 237)\')} != 3"',
    'assert block.count("if w < 238)") == 3, f"family-6 triple: w<238 count {block.count(\'if w < 238)\')} != 3"')
rep('assert block.count("if w < 236)") == 0, "family-6 triple: stale w<236 leaked into the W237 block"',
    'assert block.count("if w < 237)") == 0, "family-6 triple: stale w<237 leaked into the W238 block"')
rep('assert block.count("range(16, 237)") == 1 and block.count("range(17, 237)") == 1, "family-6 triple: RHS ranges wrong"',
    'assert block.count("range(16, 238)") == 1 and block.count("range(17, 238)") == 1, "family-6 triple: RHS ranges wrong"')
rep('assert block.count("registered wave below 237 composes") == 1, "family-6 triple: comment face wrong"',
    'assert block.count("registered wave below 238 composes") == 1, "family-6 triple: comment face wrong"')

# ================= 14. tail renames =================
rep('        # prior-wave disjointness W2..W236 (single state: all',
    '        # prior-wave disjointness W2..W237 (single state: all')
rep('        for wprev in sorted(w for w in WAVE_CONFIGS if w < 237):',
    '        for wprev in sorted(w for w in WAVE_CONFIGS if w < 238):', 2)
rep('            assert not (w236_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
    '            assert not (w237_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j')
rep('                                 for j in range(A_N)}), f\\"W237 A hits W{wprev}\\"',
    '                                 for j in range(A_N)}), f\\"W238 A hits W{wprev}\\"')
rep('            assert not (w236_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
    '            assert not (w237_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j')
rep('                                  for j in range(B_N)}), f\\"W237 B hits W{wprev}\\"',
    '                                  for j in range(B_N)}), f\\"W238 B hits W{wprev}\\"')
rep("        n3r1_used237 = set(range(70_000, 70_006))", "        n3r1_used238 = set(range(70_000, 70_006))")
rep('        assert not (w236_a & n3r1_used237) and not (w236_b & n3r1_used237), \\\\',
    '        assert not (w237_a & n3r1_used238) and not (w237_b & n3r1_used238), \\\\')
rep('            "W237 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
    '            "W238 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"')
rep('        assert not (w236_a & lfc_actual12) and not (w236_b & lfc_actual12), \\\\',
    '        assert not (w237_a & lfc_actual12) and not (w237_b & lfc_actual12), \\\\')
rep('            "W237 bands must clear the lfc actual draw range"',
    '            "W238 bands must clear the lfc actual draw range"')
rep('        assert not (w236_a & options_actual12) and \\\\',
    '        assert not (w237_a & options_actual12) and \\\\')
rep('            not (w236_b & options_actual12), \\\\',
    '            not (w237_b & options_actual12), \\\\')
rep('            "W237 bands must clear the options_wave2 actual draw range"',
    '            "W238 bands must clear the options_wave2 actual draw range"')
rep('        # band facts (law sec.4 W237 row): A = FIRST-CLEAN past',
    '        # band facts (law sec.4 W238 row): A = FIRST-CLEAN past')
rep('        # the registered W236 B band (the arithmetic continuation',
    '        # the registered W237 B band (the arithmetic continuation')
rep("        # {fmt(w236_a_tail + 1)}..{fmt(w236_a_tail + 2_000)} is REFUSED at its own start by the W236 B band",
    "        # {fmt(w237_a_tail + 1)}..{fmt(w237_a_tail + 2_000)} is REFUSED at its own start by the W237 B band")
rep("        # {fmt(W236['b_exit'][0])}..{fmt(w236_b_tail)}, exactly as the W236 seat leg4",
    "        # {fmt(W237['b_exit'][0])}..{fmt(w237_b_tail)}, exactly as the W237 seat leg4")
rep('        # prior-wave B tail+1 ({fmt(w236_b_tail)}+1) machine-checkable --',
    '        # prior-wave B tail+1 ({fmt(w237_b_tail)}+1) machine-checkable --')
rep('        # A-hops-prior-B staircase NINETY-SEVENTH instance, E36 card;',
    '        # A-hops-prior-B staircase NINETY-EIGHTH instance, E36 card;')
rep('        # registered universe but lands INSIDE the W237 A band window',
    '        # registered universe but lands INSIDE the W238 A band window')
rep('        # cross-window convergence with the W236 seat leg4',
    '        # cross-window convergence with the W237 seat leg4')
rep('        assert WAVE_CONFIGS[237]["a_seed_base"] == {a_lo} == {w236_b_tail} + 1, (',
    '        assert WAVE_CONFIGS[238]["a_seed_base"] == {a_lo} == {w237_b_tail} + 1, (')
rep('            "W237 A must be the first-clean window past the registered "',
    '            "W238 A must be the first-clean window past the registered "')
rep('            "W236 B band tail (arithmetic continuation REFUSED at its own "',
    '            "W237 B band tail (arithmetic continuation REFUSED at its own "')
rep('            "start by the W236 B band, exactly as the W236 seat leg4 "',
    '            "start by the W237 B band, exactly as the W237 seat leg4 "')
rep('            "= A-hops-prior-B staircase NINETY-SEVENTH instance, E36 card")\'',
    '            "= A-hops-prior-B staircase NINETY-EIGHTH instance, E36 card")\'')
rep('        arith_a237 = set(range({a_lo}, {a_hi + 1}))',
    '        arith_a238 = set(range({a_lo}, {a_hi + 1}))')
rep('            "W237 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"\'',
    '            "W238 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"\'')
rep('        assert WAVE_CONFIGS[237]["b_exit_seed_base"] == {b_lo} == {a_hi} + 1, (',
    '        assert WAVE_CONFIGS[238]["b_exit_seed_base"] == {b_lo} == {a_hi} + 1, (')
rep('            "W237 B must be the first-clean window past the own-wave A "',
    '            "W238 B must be the first-clean window past the own-wave A "')
rep('            "universe but lands INSIDE the W237 A band window; "',
    '            "universe but lands INSIDE the W238 A band window; "')
rep('        arith_b237 = set(range({b_lo}, {b_hi + 1}))',
    '        arith_b238 = set(range({b_lo}, {b_hi + 1}))')
rep('            "W237 B window must be CLEAN (first-clean ADMIT face past own-wave A)"\'',
    '            "W238 B window must be CLEAN (first-clean ADMIT face past own-wave A)"\'')
rep('        assert not (arith_b237 & arith_a237), \\\\',
    '        assert not (arith_b238 & arith_a238), \\\\')
rep('            "W237 A/B same-freeze mutual exclusion (B hops past own A)"',
    '            "W238 A/B same-freeze mutual exclusion (B hops past own A)"')
rep('        assert _entry_shard_of(0, 12) == (\\"PERPETUAL-N1-W237-SHARD-0\\",',
    '        assert _entry_shard_of(0, 12) == (\\"PERPETUAL-N1-W238-SHARD-0\\",')
rep('                                          "n1w237-0of12"), "W237 entry identity"\'',
    '                                          "n1w238-0of12"), "W238 entry identity"\'')
rep('        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W237-SHARD-11",',
    '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W238-SHARD-11",')
rep('                                           "n1w237-11of12")\'',
    '                                           "n1w238-11of12")\'')
rep('        assert SHARD_DIR.endswith(\\"n1_w237\\") and OUT.endswith(',
    '        assert SHARD_DIR.endswith(\\"n1_w238\\") and OUT.endswith(')
rep('            "n1_w237_results.json"), "W237 path drift"\'',
    '            "n1_w238_results.json"), "W238 path drift"\'')
rep('                f"W237 shard dir collides with W{wprev}"\'',
    '                f"W238 shard dir collides with W{wprev}"\'')
rep('        # W237 finalize cumulative deps: W17..W236 outputs ALL PRESENT',
    '        # W238 finalize cumulative deps: W17..W237 outputs ALL PRESENT')
rep('        # (landed net chain head {w236_total} machine-read at freeze time)',
    '        # (landed net chain head {w237_total} machine-read at freeze time)')
rep('        for _depw in range(17, 237):', '        for _depw in range(17, 238):')
rep('                f"W237 finalize cumulative dep (W{_depw} output) missing"\'',
    '                f"W238 finalize cumulative dep (W{_depw} output) missing"\'')
rep('        # registered wave below 237 composes; wave 15 excluded by',
    '        # registered wave below 238 composes; wave 15 excluded by')
rep('        # design; SINGLE STATE (W2..W236 all registered -- no',
    '        # design; SINGLE STATE (W2..W237 all registered -- no')
rep('        assert sorted(w for w in WAVE_CONFIGS if w < 237) == \\\\',
    '        assert sorted(w for w in WAVE_CONFIGS if w < 238) == \\\\')
rep('            [w for w in range(16, 237)], \\\\',
    '            [w for w in range(16, 238)], \\\\')
rep('            "W237 prior-wave set must derive from registry keys (no 15; " \\\\',
    '            "W238 prior-wave set must derive from registry keys (no 15; " \\\\')
rep('            "W2..W236 registered single state)"\',',
    '            "W2..W237 registered single state)"\',')
rep('            PATHS.root, "research", "PERPETUAL_N1_W237_PREREG.md")), \\\\',
    '            PATHS.root, "research", "PERPETUAL_N1_W238_PREREG.md")), \\\\')
rep('            "W237 per-wave prereg missing (materializer requirement)"\'',
    '            "W238 per-wave prereg missing (materializer requirement)"\'')

# ================= 15. pr span =================
NEW_PR = '''pr = [
 '          "+ W238 materializer face [same guard set, dep=W17..W237 "',
 f'          "outputs ALL PRESENT (landed net chain head {w237_total} = W237 bm-c finalize one-pass, K={w237_merged_n} merged pool) -- ZERO "',
 '          "in-flight upstream seats at splice, clean precondition, TWO HUNDRED AND THIRTY-EIGHTH "',
 f'          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} "',
 '          "+ candidate) bm-a\\'s one hundred and twenty-second owned claim per "',
 '          "machine-derive (engine_owner==bm-a rows 121 + candidate; OWN-SEAT face: seat published by bm-a itself, "',
 '          "probe leg0 owner_rows=226 / bma_ordinal=122 = seat-time pre-splice faces disclosed honest, "',
 '          "live derive at freeze governs), "',
 '          "A=FIRST-CLEAN past the registered W237 B band (staircase "',
 '          "NINETY-EIGHTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
 '          "own-wave A window (W141 precedent, leg2 law, same-freeze "',
 '          "mutual exclusion, hops=1), chain-order splice from the "',
 '          "committed ADMIT receipt + seed_admit_gate rc0 both bands FREE "',
 '          "(O-20261010-1945-bm-a ADMIT convention), "',
 '          "ADMIT receipt "',
 '          "results/_w238bma_20261014_probe_receipt.json, law sec.4 W238 row, "',
 '          "bm-a loop CEO fill-order RE-ISSUE 23:1x] "',
]
'''
span("pr = [\n", "\nold_pr = must(", NEW_PR)

# ================= 16. post-edit count gates =================
rep("assert n1_t4.count('\"batch\": \"PERPETUAL-N1-W237\"') == 1",
    "assert n1_t4.count('\"batch\": \"PERPETUAL-N1-W238\"') == 1")
rep('assert n1_t4.count("# --- W237 materializer face") == 1     # block header',
    'assert n1_t4.count("# --- W238 materializer face") == 1     # block header')
rep("assert n1_t4.count('\"+ W237 materializer face') == 1        # print fragment",
    "assert n1_t4.count('\"+ W238 materializer face') == 1        # print fragment")
rep("assert n1_t4.count('237: {\"batch\": \"PERPETUAL-N1-W237\"') == 1",
    "assert n1_t4.count('238: {\"batch\": \"PERPETUAL-N1-W238\"') == 1")
rep("assert pf_t2.count(ROW_I + '237: {\"a\"') == 1",
    "assert pf_t2.count(ROW_I + '238: {\"a\"') == 1")
rep("assert pf_t2.count('\"engine_owner\": \"bm-c\"},' + PF_EOL + '}') == 1",
    "assert pf_t2.count('\"engine_owner\": \"bm-a\"},' + PF_EOL + '}') == 1")
rep("assert n1_t4.count('\"PERPETUAL-N1-W237-SHARD-0\"') == 1",
    "assert n1_t4.count('\"PERPETUAL-N1-W238-SHARD-0\"') == 1")
rep("assert n1_t4.count(f'assert pf.N1_BANDS[236] == {{\"a\": ({fmt(pf_mod.N1_BANDS[236][\"a\"][0])}, {fmt(pf_mod.N1_BANDS[236][\"a\"][1])}),') == 1",
    "assert n1_t4.count(f'assert pf.N1_BANDS[237] == {{\"a\": ({fmt(pf_mod.N1_BANDS[237][\"a\"][0])}, {fmt(pf_mod.N1_BANDS[237][\"a\"][1])}),') == 1")
rep("# the W235 leg now lives in BOTH the kept W236 block and the new W237 block (2);\n# the W232/W233/W234 legs likewise exist in the kept W233..W236 blocks (multiple)",
    "# the W236 leg now lives in BOTH the kept W237 block and the new W238 block (2);\n# the W235 leg lives in the kept W236 + kept W237 + new W238 blocks (3); the\n# W232/W233/W234 legs likewise exist in multiple kept blocks")
rep("assert n1_t4.count(f'assert pf.N1_BANDS[235] == {{\"a\": ({fmt(pf_mod.N1_BANDS[235][\"a\"][0])}, {fmt(pf_mod.N1_BANDS[235][\"a\"][1])}),') == 2",
    "assert n1_t4.count(f'assert pf.N1_BANDS[236] == {{\"a\": ({fmt(pf_mod.N1_BANDS[236][\"a\"][0])}, {fmt(pf_mod.N1_BANDS[236][\"a\"][1])}),') == 2\nassert n1_t4.count(f'assert pf.N1_BANDS[235] == {{\"a\": ({fmt(pf_mod.N1_BANDS[235][\"a\"][0])}, {fmt(pf_mod.N1_BANDS[235][\"a\"][1])}),') == 3")
rep("assert n1_t4.count('    # --- W236 materializer face') == 1  # prior block kept (W236 splice landed bm-a r974/r975 window)",
    "assert n1_t4.count('    # --- W236 materializer face') == 1  # prior block kept (W236 splice landed bm-a r974/r975 window)\nassert n1_t4.count('    # --- W237 materializer face') == 1  # prior block kept (W237 splice landed bm-c r990 window)")

# ================= 17. receipt span =================
NEW_RECEIPT = '''receipt = {
  "machine": "bm-a", "wave": 238,
  "phase": "five-face freeze chain-order splice (bm-a own-seat freeze window, upstream ALL LANDED clean precondition)",
  "origin_base": omain,
  "pf_sha16_pre": hashlib.sha256(pf_b).hexdigest()[:16],
  "n1_sha16_pre": hashlib.sha256(n1_b).hexdigest()[:16],
  "pf_sha16_post": hashlib.sha256(pf_t2.encode("utf-8")).hexdigest()[:16],
  "n1_sha16_post": hashlib.sha256(n1_t4.encode("utf-8")).hexdigest()[:16],
  "bands": {"A": A, "B": B, "a_lo": a_lo, "a_hi": a_hi, "b_lo": b_lo, "b_hi": b_hi},
  "admit_receipt": "results/_w238bma_20261014_probe_receipt.json",
  "seed_admit_gate": gate_lines,
  "banned_gate": "ADMIT rc0 (re-run at freeze window)",
  "w237_upstream": {"freeze_sha": w237_freeze_sha, "prereg_sha": w237_prereg_sha,
                    "ledger_total": w237_total, "merged_n": w237_merged_n,
                    "engine_owner": "bm-c (upstream seat honored)",
                    "repair_chain_note": "W237 bm-c own-wave closeout r990 (five-face splice e4a23cc7a + engine self-burn 12/12 + finalize one-pass + five-key ALL PASS + sec78 backfill; six-gate PRE-FINALIZE correct phase -- standing law held)"},
  "own_seat_face": {"seat_msg": SEAT_MSG, "seat_origin": SEAT_ORIGIN,
                    "inherited": False,
                    "note": "seat published=reserved by bm-a itself (MSG-20261014-0745-bma-w238-seat pushed to origin 3e551d846 r976 BEFORE this freeze per r565 law); zero takeover -- wave 238 engine_owner=bm-a, bm-a's 122nd own wave per live derive (probe leg0 owner_rows=226 / bma_ordinal=122 = seat-time pre-splice faces disclosed honest, live derive governs r587/r359; freeze-time live face owner rows 227 + candidate = 228th EXACT)"},
  "w236_transitive": {"finalize_product": "results/perpetual_faces/n1_w236_results.json present (belt-and-braces gate; ledger 942,989 / K=517,120)"},
  "w235_transitive": {"finalize_product": "results/perpetual_faces/n1_w235_results.json present (belt-and-braces gate; ledger 940,789 / K=514,920)"},
  "w234_transitive": {"finalize_product": "results/perpetual_faces/n1_w234_results.json present (belt-and-braces gate; ledger 938,589 / K=512,720)"},
  "w233_transitive": {"finalize_product": "results/perpetual_faces/n1_w233_results.json present (belt-and-braces gate; ledger 936,389 / K=510,520)"},
  "w232_transitive": {"finalize_product": "results/perpetual_faces/n1_w232_results.json present (belt-and-braces gate; ledger 934,189 / K=508,320)"},
  "w231_transitive": {"finalize_product": "results/perpetual_faces/n1_w231_results.json present (belt-and-braces gate)"},
  "w230_transitive": {"finalize_product": "results/perpetual_faces/n1_w230_results.json present (belt-and-braces gate)"},
  "w225_transitive": {"finalize_product": "results/perpetual_faces/n1_w225_results.json present (belt-and-braces gate; ledger 918,789 / K=492,920)"},
  "seat": seat_found + " (origin " + SEAT_ORIGIN + ")",
  "prereg_bundle": {"prereg_sha": w238_prereg_sha, "probe_receipt_sha": w238_receipt_sha,
                    "note": "prereg derived+committed by the bm-a r983 window (own-seat derive landed pre-freeze, on origin via the r983 push; zero takeover; freeze-time live derive bma rows 121 + candidate 122nd EXACT per r587/r359); splice editor derived from the committed W237 editor template by count-asserted ordered transform in this same freeze window; upstream W237 already landed (clean-precondition twenty-seventh consecutive window); zero transcription"},
  "ordinal_faces": {"owner_rows_live": len(owner_rows_live), "bma_rows_live": len(bma_rows_live),
                    "bmc_rows_live": len(bmc_rows_live),
                    "engine_owned_ordinal": len(owner_rows_live) + 1,
                    "bma_own_ordinal": len(bma_rows_live) + 1,
                    "probe_receipt_bma_ordinal_face": 122,
                    "note": "post-W237 registration: bm-a rows 121 + candidate = 122nd owned (live derive at freeze time governs per r587/r359; probe leg0 owner_rows=226 / bma_ordinal=122 = seat-time pre-splice faces -- zero takeover, own-seat continuity)"},
  "parity_section": {"source": "OWN W237 block physical bytes (bm-c own splice generation, structure known exactly)",
                    "bytes": len(par_sec),
                    "row_asserts": par_sec.count("assert pf.N1_BANDS["),
                    "note": "full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W231 legs -> W238 block = 96 rows ending at W237 (estate 90 + fresh W232 leg + W233 leg + W234 leg + W235 leg + W236 leg + W237 leg); disclosed: (a) inherited W213 leg error-string face (\\"registered W212 row parity drift\\") preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact); (b) W237 block's band-set variable one-behind naming face (w236_a holds wave-237 bands) = lineage mechanical aging face -- W238 block follows the same pattern (w237_a holds wave-238 bands), zero functional impact"},
  "family6_triple_gate": {"absorbed": True,
                          "note": "W237 editor family-6 gate carried forward: new block LHS w<238 x3 / RHS range(16,238)+range(17,238) / comment below-238 count-asserted ATOMICALLY before splice; W237 block's own w<237 face = legitimate prior-wave boundary (not stale)"},
  "eol": {"n1_crlf": EOL == "\\r\\n", "pf_crlf": PF_EOL == "\\r\\n"},
  "liveness_anchors": {"t141_marker_kept": 1, "w209_block_kept": 1, "w210_block_kept": 1, "w211_block_kept": 1, "w212_block_kept": 1, "w213_block_kept": 1, "w214_block_kept": 1, "w215_block_kept": 1, "w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1, "w219_block_kept": 1, "w220_block_kept": 1, "w221_block_kept": 1, "w222_block_kept": 1, "w223_block_kept": 1, "w224_block_kept": 1, "w225_block_kept": 1, "w226_block_kept": 1, "w227_block_kept": 1, "w228_block_kept": 1, "w229_block_kept": 1, "w230_block_kept": 1, "w231_block_kept": 1, "w232_block_kept": 1, "w233_block_kept": 1, "w234_block_kept": 1, "w235_block_kept": 1, "w236_block_kept": 1, "w237_block_kept": 1},
}
'''
span("receipt = {\n", "\nopen(RECEIPT_OUT", NEW_RECEIPT)

# final prints
rep('"w236_upstream", "own_seat_face")', '"w237_upstream", "own_seat_face")')
rep("engine self-ignite W237 burn (12 shards)", "engine self-ignite W238 burn (12 shards)")

# ================= write + verify =================
if fails:
    print("DERIVE FAIL-CLOSED -- %d replacement(s) mismatched, editor NOT written:" % len(fails))
    for f in fails:
        print("  expected=%s got=%s :: %s" % (f[2], f[1], f[0]))
    sys.exit(1)

if IS_CRLF:
    t = t.replace("\n", "\r\n")
open(OUT, "wb").write(t.encode("utf-8"))
py_compile.compile(OUT, doraise=True)
print("DERIVE OK -- %s written and py_compile green (%d bytes)" % (OUT, len(t.encode("utf-8"))))
