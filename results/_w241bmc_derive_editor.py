# -*- coding: utf-8 -*-
# 2026-10-14 18:4x bm-c r1004 freeze window: W241 five-face freeze splice editor
# DERIVATION transform -- template results/_w240bma_freeze_edits.py (committed,
# proven live-fire by the bm-a r991 window; engine self-burn + finalize
# verified bm-a r993 17:09:55) -> results/_w241bmc_freeze_edits.py.
# Lineage law: count-asserted ordered transform, zero transcription, fail-closed
# (any count mismatch = loud abort, the derived editor is NOT written).
# All W240 facts in the derived editor are machine-derived at ITS run time
# (live pf import + pickaxe); this transform only carries the generation shift.
# W241 band semantics (probe receipt leg1, committed r1002 origin 20782916a):
# A = 547_501..549_500 hops=0 naive arithmetic continuation of the W240-REGISTERED
# A tail 547_500+1, CLEAN at naive start (seed-decoupled A-continuation face,
# second consecutive seed-gap face per the W240 seat leg4 anticipation);
# B = 541_004..541_203 hops=0 keeps the staircase base (prior-wave B tail+1
# EXACT) -- third consecutive decoupled face. The A-relation assert face
# CHANGES this generation: A base == prior-wave A tail+1 EXACT (continuation),
# replacing W240's A-hops-prior-B staircase GE face.
# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.
import os, sys, py_compile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(REPO, "results", "_w240bma_freeze_edits.py")
OUT = os.path.join(REPO, "results", "_w241bmc_freeze_edits.py")

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
NEW_HEADER = r'''# 2026-10-14 18:4x bm-c r1004 freeze window (upstream W1..W240 ALL LANDED, clean
# precondition -- W240 finalize one-pass bm-a r993 window 17:09:55, ledger
# head 952,335 / K=525,920 machine-read): W241 five-face freeze splice editor
# -- bm-c OWN-SEAT face (seat MSG-20261014-1755-bmc-w241-seat published=
# reserved by bm-c itself @ origin 20782916a r1002, pre-seat probe ADMIT receipt
# results/_w241bmc_20261014_probe_receipt.json same payload; per-wave prereg
# PERPETUAL_N1_W241_PREREG.md derived+landed by the dead r1003 session
# [estate absorbed by THIS r1004 window per the bm-c absorb precedent
# lineage 25th instance, commit a9ab3b51d], zero takeover, zero DRAFT marker).
# Lineage: _w240bma_freeze_edits.py template (proven live-fire freeze, bm-a
# r991 window; engine self-burn + finalize one-pass verified bm-a r993) +
# r787 preflight law + r609 origin-verbatim base + r761 programmatic quote
# wrapping + r909 physical-byte anchors + r838 per-file EOL detection +
# family #6 LHS/RHS/comment ATOMIC TRIPLE (the new block's w<241>/
# range(16,241)/range(17,241)/below-241 quadruple is count-asserted
# atomically; the W240 block's own w<240 face is legitimate prior-wave
# boundary, not stale) + E63 heal lineage (arith_a241/arith_b241 define+assert
# consistent).
# Zero hardcoded upstream band values: ALL W240 facts machine-derived from the
# LIVE pf import at freeze time (the registered W240 row -- bm-a seat honored),
# cross-checked against the committed ADMIT receipt
# (results/_w241bmc_20261014_probe_receipt.json) which was derived on the
# post-W240-REGISTERED universe. If the LIVE W240 bands differ from the declared
# face, the continuation asserts fail LOUD (fail-closed).
# STRUCTURAL CHOICE (vs the W240 editor): the parity estate (W138..W206
# full-span 69 rows, r858 absorb generation, + W211..W231 legs) is extracted
# from the OWN W240 block physical bytes -- structure known exactly (bm-a's
# splice generation, committed) -- the W240 block's own W232..W239 legs are
# excluded from the estate path and fresh W232..W240 legs are appended for the
# W241 block parity (99 rows: estate 90 ending W231 + W232 leg + W233 leg +
# W234 leg + W235 leg + W236 leg + W237 leg + W238 leg + W239 leg + W240 leg).
# Extraction self-asserts the 90-row cut regardless.
# Disclosed: (a) the inherited W213 leg inside the estate carries a cosmetic
# error-string face ("registered W212 row parity drift") from the r912 editor
# generation -- physical bytes preserved verbatim per extraction law, zero
# functional impact (assert target [213] is correct); (b) the band-set
# variable naming one-behind face (w240_a holds wave-241 bands) is the
# lineage's mechanical aging face -- the W241 block follows the same
# mechanical pattern as its ancestors, zero functional impact.
# Own bundle hashes (prereg/probe receipt) derived via pickaxe, never transcribed.
# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.
import json, hashlib, os, re, subprocess, sys'''
span("# 2026-10-14 16:1x bm-a r991 freeze window", "import json, hashlib, os, re, subprocess, sys", NEW_HEADER, include_end=True)

# ================= 2. constants =================
rep('RECEIPT_IN = os.path.join(REPO, "results", "_w240bma_20261014_probe_receipt.json")',
    'RECEIPT_IN = os.path.join(REPO, "results", "_w241bmc_20261014_probe_receipt.json")')
rep('RECEIPT_OUT = os.path.join(REPO, "results", "_w240bma_freeze_receipt.json")',
    'RECEIPT_OUT = os.path.join(REPO, "results", "_w241bmc_freeze_receipt.json")')
rep('SEAT_MSG = "MSG-20261014-1325-bma-w240-seat.md"',
    'SEAT_MSG = "MSG-20261014-1755-bmc-w241-seat.md"')
rep('SEAT_ORIGIN = "39a30b6a0"', 'SEAT_ORIGIN = "20782916a"')

# ================= 3. gate 0.5 span =================
NEW_GATE05 = r'''# ---------- gate 0.5: W240 five-face landed + W240 finalize product present ----------
# (chain-order precondition; W239/W238/W237/W236/W235/W234/W233/W232 finalize are
# transitive deps of the W240 freeze and are belt-and-braces checked here + enforced
# by the block's cumulative-deps assert range(17, 241) at selftest time)
W240 = dict(pf_mod.N1_BANDS.get(240) or {})
assert W240.get("engine_owner") == "bm-a", \
    f"W240 row not landed as declared (bm-a seat owner expected): {W240} -- five-face freeze missing;" \
    " if an unexpected face exists the freeze window MUST re-derive this editor honestly"
w240_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w240_results.json")
assert os.path.exists(w240_out_path), "W240 finalize product missing (n1_w240_results.json) -- chain dep not met"
for _w in (239, 238, 237, 236, 235, 234, 233, 232):
    assert os.path.exists(os.path.join(REPO, "results", "perpetual_faces", f"n1_w{_w}_results.json")), \
        f"W{_w} finalize product missing (transitive chain dep) -- abort"
w240_out = json.load(open(w240_out_path, encoding="utf-8"))
w240_led = (w240_out.get("science_gates") or {}).get("ledger") or {}
w240_total = w240_led.get("total")
w240_merged_n = None
try:
    w240_merged_n = w240_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
assert w240_total == 952_335 and w240_merged_n == 525_920, \
    f"W240 finalize anchors drift at freeze time: total={w240_total} merged={w240_merged_n} (expect 952,335 / 525,920)"
# freeze shas machine-derived (pickaxe), never transcribed
r = git("log", "--format=%H", "-S", '240: {"a"', "--", "scripts/perpetual_faces.py")
w240_freeze_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W240_PREREG.md")
w240_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W241_PREREG.md")
w241_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
assert os.path.exists(os.path.join(REPO, "research", "PERPETUAL_N1_W241_PREREG.md")), \
    "W241 per-wave prereg missing on disk -- chain face incomplete, abort (r1003 dead-session derive landed pre-freeze expected)"
with open(os.path.join(REPO, "research", "PERPETUAL_N1_W241_PREREG.md"), encoding="utf-8") as _fh:
    _pre_head = _fh.read(2000)
assert "DRAFT-NOT-FROZEN" not in _pre_head, "W241 prereg still DRAFT -- abort (freeze commit pending face)"
# live ordinal derive (r359 law: gate machine output governs; the pre-seat probe
# receipt leg0 face owner_rows=230 / bmc_rows=66 / bmc_ordinal=67
# = seat-time PRE-splice live faces; live derive at freeze time:
# W240 splice LANDED (finalize adds no registry rows) -> owner rows 230 + candidate = 231st EXACT; bm-c rows 66 +
# candidate = 67th EXACT -- bm-c own-seat continuity face, zero takeover)
owner_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner")]
bma_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-a"]
bmc_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
assert len(owner_rows_live) == 230 and len(bma_rows_live) == 123 and len(bmc_rows_live) == 66, \
    f"leg0 ordinal drift at freeze time: owner={len(owner_rows_live)} bma={len(bma_rows_live)} bmc={len(bmc_rows_live)} (expect 230/123/66 PRE-splice post-W240 registration; this candidate = bm-c's 67th own wave per the same live-derive law, r587/r359)"
print(f"gate0.5 OK: W240 landed (freeze {w240_freeze_sha[:10]}, owner=bm-a seat honored, zero takeover face), "
      f"W240+W239+W238+W237+W236+W235+W234+W233+W232 finalize products present "
      f"(W240 ledger head {w240_total}, merged n={w240_merged_n}); owner rows {len(owner_rows_live)} + candidate, "
      f"bm-c rows {len(bmc_rows_live)} + candidate (67th own wave per live derive; "
      f"probe receipt leg0 bmc_ordinal=67 = seat-time pre-splice faces disclosed honest)")

'''
span("# ---------- gate 0.5: W239 five-face landed + W239 finalize product present ----------",
     "# ---------- band facts from the committed ADMIT receipt (never transcribed) ----------",
     NEW_GATE05)

# ================= 4. band facts span =================
NEW_BANDFACTS = r'''# ---------- band facts from the committed ADMIT receipt (never transcribed) ----------
rec = json.load(open(RECEIPT_IN, encoding="utf-8"))
assert rec["verdict"] == "ADMIT"
A = rec["bands"]["A"]; B = rec["bands"]["B"]
if isinstance(A, str):
    a_lo, a_hi = (int(x) for x in A.split("_"))
    b_lo, b_hi = (int(x) for x in B.split("_"))
else:
    a_lo, a_hi = int(A[0]), int(A[1])
    b_lo, b_hi = int(B[0]), int(B[1])
    a_lo = rec["bands"].get("a_lo", a_lo); a_hi = rec["bands"].get("a_hi", a_hi)
    b_lo = rec["bands"].get("b_lo", b_lo); b_hi = rec["bands"].get("b_hi", b_hi)
leg1 = rec["legs"]["leg1"]
assert [a_lo, a_hi] == leg1["A"] and [b_lo, b_hi] == leg1["B"], "receipt band mismatch"
assert (a_lo, a_hi) == (547_501, 549_500) and (b_lo, b_hi) == (541_004, 541_203), \
    f"W241 band drift vs probe ADMIT: {(a_lo, a_hi)} {(b_lo, b_hi)}"
w240_b_tail = W240["b_exit"][1]      # registered W240 row b_exit hi (pf import, live)
w240_a_tail = W240["a"][1]            # registered W240 row A hi (pf import, live)
# W241 FACE (seed-decoupled A-continuation, probe receipt leg1 relation_asserts):
# A keeps the A-continuation base (prior-wave A tail+1 EXACT -- the naive
# arithmetic continuation is CLEAN at its own start, hops=0, A_hop_chain
# empty, A_clean_at_naive_start=true -- second consecutive seed-gap face per
# the W240 seat leg4 anticipation confirmed live); B keeps the staircase
# base (prior-wave B tail+1 EXACT, hops=0, third consecutive decoupled face);
# A sits far above the B staircase (seed-decoupled A/B gap);
# machine-derived from the LIVE registered row, never transcribed.
assert w240_a_tail + 1 == a_lo, "A continuation base relation broken (A == prior-wave A tail+1 EXACT)"
assert w240_b_tail + 1 == b_lo, "B staircase base relation broken (B == prior-wave B tail+1 EXACT)"
assert a_lo > w240_b_tail + 1, "seed-decoupled A-continuation face violated: A base must sit ABOVE prior-B tail+1 (seed-gap)"
assert b_hi < a_lo, "seed-decoupled A/B gap face violated: B window must sit entirely below own-A"
assert W240["b_exit"][1] < W240["a"][0], \
    "upstream W240 row in-wave decoupled relation broken (registered W240 B window must sit below own W240 A window)"
assert leg1.get("hops_A") == 0 and leg1.get("hops_B") == 0, "hop-count drift vs probe receipt leg1 (both bands naive hops=0)"
assert leg1.get("A_hop_chain") == [] and leg1.get("A_clean_at_naive_start") is True, \
    "A hop-chain face drift (fc_a == fc_a_naive, hops=0, A_clean_at_naive_start=true -- naive continuation CLEAN at own start)"
assert leg1.get("B_hop_chain") == [] and leg1.get("B_naive_hops") == 0, "B hop-chain face drift (fc_b == fc_b_naive, hops=0)"
ra = leg1.get("relation_asserts") or {}
assert ra.get("A_clean_at_naive_start") and ra.get("A_base_ge_priorB_tail_plus1") \
    and ra.get("B_base_eq_priorB_tail_plus1") and ra.get("AB_mutual_exclusion") \
    and ra.get("B_no_ownA_jump"), \
    f"probe receipt leg1 relation_asserts face drift: {ra}"
assert [w240_a_tail + 1, w240_a_tail + 2_000] == leg1["ARITH_A"], \
    f"A-continuation start drift vs probe receipt leg1 ARITH_A: {[w240_a_tail + 1, w240_a_tail + 2_000]} != {leg1['ARITH_A']}"
assert [w240_b_tail + 1, w240_b_tail + 200] == leg1["ARITH_B"], \
    f"B-continuation drift vs probe receipt leg1 ARITH_B: {[w240_b_tail + 1, w240_b_tail + 200]} != {leg1['ARITH_B']}"

# own bundle shas via pickaxe (self-referencing commit facts, zero transcription)
r = git("log", "--diff-filter=A", "--format=%H", "--", "results/_w241bmc_20261014_probe_receipt.json")
w241_receipt_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
# seat MSG honest location (inbox or processed; S7 archive law)
seat_found = None
for _p in ("fleet/inbox", "fleet/inbox/processed"):
    if os.path.exists(os.path.join(REPO, _p, SEAT_MSG)):
        seat_found = _p + "/" + SEAT_MSG
        break
assert seat_found, f"W241 seat MSG missing from both inbox paths: {SEAT_MSG}"

'''
span("# ---------- band facts from the committed ADMIT receipt (never transcribed) ----------",
     "# ---------- re-run discipline gates at freeze window (banned + seed_admit) ----------",
     NEW_BANDFACTS)

# ================= 5. re-run gates: prereg path shift =================
rep('"--prereg", "research/PERPETUAL_N1_W240_PREREG.md"',
    '"--prereg", "research/PERPETUAL_N1_W241_PREREG.md"')

# ================= 6. parity extraction span =================
NEW_PARITY = r'''# ---------- extract parity section (physical bytes, never re-typed) ----------
# STRUCTURAL CHOICE: extract the estate from the OWN W240 block (bytes known
# exactly: full-span estate W138..W206 69 rows + own W211..W231 legs = 90
# rows) -- the W240 block is bm-a's own splice generation (r991 window
# editor), structure known. The W240 block span ends where the T-141
# s2 lane face marker begins.
a20 = '    # --- W240 materializer face'
a_t141 = '    # --- T-141 s2 lane face'
w240_start = n1_t.find(a20); t141_pos = n1_t.find(a_t141)
assert w240_start > 0 and t141_pos > w240_start, \
    "W240 materializer block face not found (W240 freeze not landed? header-text drift -> honest re-derive required)"
blk = n1_t[w240_start:t141_pos]
m_first_row = re.search(r"assert pf\.N1_BANDS\[", blk)
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state", blk)
assert m_first_row and m_disj and m_disj.start() > m_first_row.start(), \
    "parity span markers not found in W240 block"
_row_ls = blk.rfind(EOL, 0, m_first_row.start()) + len(EOL)
par_full = blk[_row_ls:m_disj.start()]
m232 = re.search(r" *assert pf\.N1_BANDS\[232\] ==", par_full)
assert m232, "upstream W232 row leg not found inside W240 parity span"
par_sec = par_full[:m232.start()]
assert par_sec.endswith(EOL), "estate segment must end with EOL"
_estate_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", par_sec)
assert par_sec.count("assert pf.N1_BANDS[") == 90 \
    and [int(w) for w in _estate_ws[:69]] == list(range(138, 207)) \
    and [int(_estate_ws[69 + i]) for i in range(11)] == [211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221] \
    and [int(_estate_ws[80 + i]) for i in range(9)] == [222, 223, 224, 225, 226, 227, 228, 229, 230] \
    and int(_estate_ws[89]) == 231, \
    f"estate segment not W138..W206 full-span 69 rows + W211..W230 legs + W231 leg: n={par_sec.count('assert pf.N1_BANDS[')} range={(_estate_ws[:2], _estate_ws[-4:])}"
assert par_full.count("assert pf.N1_BANDS[") == 98, \
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 98 (69 estate + W211..W230 legs + W231 leg + W232 leg + W233 leg + W234 leg + W235 leg + W236 leg + W237 leg + W238 leg + W239 leg)"

'''
span("# ---------- extract parity section (physical bytes, never re-typed) ----------",
     "# ---------- indent extraction (physical, not assumed; per-file EOL) ----------",
     NEW_PARITY)

# ================= 7. indent extraction span =================
NEW_INDENT = r'''# ---------- indent extraction (physical, not assumed; per-file EOL) ----------
def line_indent(t, needle, eol):
    i = t.find(needle)
    assert i >= 0, f"indent needle not found: {needle[:40]}"
    ls = t.rfind(eol, 0, i) + len(eol)
    line = t[ls:t.find(eol, ls)]
    return line[:len(line) - len(line.lstrip(" "))]

CFG_I  = line_indent(n1_t, '240: {"batch"', EOL)
PRE_KEY_I = line_indent(n1_t, '"prereg": ("research/PERPETUAL_N1_W240_PREREG.md', EOL)
PRE_I  = line_indent(n1_t, '"pre-run; design = frozen v1 null calibration verbatim, "', EOL)
# MEM_I derived INSIDE the W240 cfg entry span (own splice generation, value
# format known: plain int -- indent is all we take)
_c240 = n1_t.find('240: {"batch"')
assert _c240 > 0, "W240 cfg entry not found (W240 freeze not landed?)"
_mpos = n1_t.find('"a_seed_base"', _c240)
assert _mpos > 0 and n1_t.find('"shard_subdir"', _c240) > _mpos, "W240 cfg a_seed_base line not found"
MEM_I  = line_indent(n1_t, '"a_seed_base": ' + str(W240["a"][0]), EOL) \
    if n1_t.find('"a_seed_base": ' + str(W240["a"][0]), _c240) > 0 \
    else line_indent(n1_t, '"a_seed_base": ' + fmt(W240["a"][0]), EOL)
ROW_I  = line_indent(pf_t,  '240: {"a"', PF_EOL)

'''
span("# ---------- indent extraction (physical, not assumed; per-file EOL) ----------",
     "# ---------- W239 row owner line (physical bytes; comment text is own generation) ----------",
     NEW_INDENT)

# ================= 8. owner line span =================
NEW_OWNER = r'''# ---------- W240 row owner line (physical bytes; comment text is own generation) ----------
w240_row_start = pf_t.find('    240: {"a"')
assert w240_row_start > 0, "W240 row literal not found in pf source"
_own_ls = pf_t.find(PF_EOL, w240_row_start) + len(PF_EOL)
_own_le = pf_t.find(PF_EOL, _own_ls)
w240_own_line = pf_t[_own_ls:_own_le]
assert '"engine_owner": "bm-a"' in w240_own_line, \
    f"W240 owner line unexpected bytes: {w240_own_line!r}"
ROWC_I = w240_own_line[:len(w240_own_line) - len(w240_own_line.lstrip(" "))]

'''
span("# ---------- W239 row owner line (physical bytes; comment text is own generation) ----------",
     "# ---------- pf comment + row ----------",
     NEW_OWNER)

# ================= 9. pf comment + row span =================
NEW_PFROW = r'''# ---------- pf comment + row ----------
pf_comment = PF_EOL.join([
"    # W241 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat",
"    # MSG-20261014-1755-bmc-w241-seat published=reserved by bm-c itself @",
"    # origin " + SEAT_ORIGIN + " (r1002, queue-depth supply depth-2, zero takeover); prereg + ADMIT probe",
"    # receipt frozen commit " + w241_prereg_sha[:10] + " (prereg research/PERPETUAL_N1_W241_PREREG.md",
"    # r1003 dead-session derive landed pre-freeze [estate absorbed by the",
"    # r1004 window], probe",
"    # results/_w241bmc_20261014_probe_receipt.json @ " + w241_receipt_sha[:10] + ");",
"    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10",
"    # ~23:1x; deletion-set EMPTY; delivery window = chain-order",
"    # splice AFTER the bm-a W240 five-face (freeze " + w240_freeze_sha[:10] + ") + W240",
"    # finalize product landed (n1_w240_results.json present, ledger",
"    # head " + str(w240_total) + " machine-read at freeze time); zero --no-verify;",
"    # the W241 seat MSG sits in " + seat_found + " at freeze",
"    # time, honest archived per S7 law);",
"    # band gate ADMIT results/_w241bmc_20261014_probe_receipt.json: A = FIRST-CLEAN",
"    # arithmetic continuation of the prior-wave A tail (" + fmt(w240_a_tail + 1) + ".." + fmt(w240_a_tail + 2_000) + " CLEAN",
"    # at naive start on the registered universe, hops=0, A_hop_chain empty +",
"    # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,",
"    # second consecutive seed-gap face per the W240 seat leg4 anticipation",
"    # confirmed live; A base == prior-wave A tail+1 (" + fmt(w240_a_tail) + "+1) machine-checkable;",
"    # B = FIRST-CLEAN arithmetic continuation of the prior-wave B tail",
"    # (" + fmt(w240_b_tail + 1) + ".." + fmt(w240_b_tail + 200) + " CLEAN on the",
"    # registered universe, hops=0, B_hop_chain empty + B_no_ownA_jump=true -- B",
"    # lands OUTSIDE the own-A window " + fmt(a_lo) + ".." + fmt(a_hi) + ":",
"    # seed-decoupled A/B gap face third consecutive; B base == prior-wave B",
"    # tail+1 (" + fmt(w240_b_tail) + "+1) machine-checkable;",
"    # single-window derive (r812 merged the gate legs INTO the",
"    # pre-seat probe; dual-window parity N/A honest); scan face =",
"    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1",
"    # used-seed band + probe cluster 95_000..95_003 + cross-face",
"    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/",
"    # N2-W15 probe points.",
"    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):",
"    # " + gate_lines[0] + ";",
"    # " + gate_lines[1] + ".",
"    # W242+ projection (gate-derived pre-seat probe leg4, pre-W241",
"    # universe): A naive first-clean " + rec["legs"]["leg4"]["W242p_A_naive"] + " CLEAN (hops=0, zero live",
"    # seed refusers) / B naive first-clean " + rec["legs"]["leg4"]["W242p_B_naive"] + " CLEAN (hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " -- B lands OUTSIDE",
"    # the naive A window, seed-gap face inherited); W242 freezer MUST",
"    # re-derive on the post-W241 universe AND reserve the own-wave A window",
"    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1",
"    # equality -- W241 A/B stay decoupled); never transcribe r587.",
])
pf_row = (f'{ROW_I}241: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), '
          f'"b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'
          + PF_EOL + f'{ROWC_I}"engine_owner": "bm-c"}},' + PF_EOL)
# belt-and-braces: display form must equal the canonical W-family text
assert pf_row.split(PF_EOL)[0].strip() == \
    f'241: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), "b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'

old_pf = must(pf_t, (w240_own_line + PF_EOL + '}'
                     + PF_EOL + '# v1 + ext(wave-1) in-use bands'), 1, "pf_close")
new_pf = (w240_own_line + PF_EOL
          + pf_comment + PF_EOL + pf_row
          + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands')
pf_t2 = pf_t.replace(old_pf, new_pf, 1)

'''
span("# ---------- pf comment + row ----------",
     "# ---------- n1 cfg entry (programmatic quote wrapping, r761 law) ----------",
     NEW_PFROW)

# ================= 10. n1 cfg entry span =================
NEW_CFG = r'''# ---------- n1 cfg entry (programmatic quote wrapping, r761 law) ----------
fin_face = (f"W1..W240 finalize ALL LANDED (W240 finalize product present at splice, "
            f"net chain head {w240_total} machine-read, merged pool K={w240_merged_n} "
            f"machine-read) -- ZERO in-flight upstream seats at splice time, clean precondition "
            f"(thirtieth consecutive fully-clean freeze window); downstream W242 seat ALREADY "
            f"PUBLISHED by bm-a at this freeze window (MSG-20261014-1814-bma-w242-seat @ origin "
            f"138a94745, bm-a 124th owned = never-dry queue-depth supply depth-2; the W242 freezer "
            f"MUST re-derive live on the post-W241 universe + reserve the own-wave A window when "
            f"deriving B per the W241 seat leg4 mandate, never transcribe r587)")
cfg_lines = [
 f'{CFG_I}241: {{"batch": "PERPETUAL-N1-W241",',
 f'{PRE_KEY_I}"prereg": ("research/PERPETUAL_N1_W241_PREREG.md (wave-level frozen "',
]
PRE = [
 "pre-run; design = frozen v1 null calibration verbatim, ",
 "new seed bands only; TWO HUNDRED AND FORTY-FIRST ENGINE-OWNED WAVE ",
 f"BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate), ",
 "own-series continuation per O-20260101-2355 sec.2 (first-free-",
 "number law after the REGISTERED W240 row five-face freeze (bm-a own seat executed at the bm-a r991 window; engine self-burn 12/12; finalize one-pass, ledger 952,335 / K=525,920 machine-read), ",
 f"{w240_freeze_sha[:10]} (prereg {w240_prereg_sha[:10]}), SINGLE STATE zero seat gap W2..W240 all ",
 "registered; " + fin_face + "; ",
 "seat published=reserved ",
 "MSG-20261014-1755-bmc-w241-seat PUSHED to origin " + SEAT_ORIGIN + " ",
 "BEFORE this freeze per r565 early-visibility law (payload = ",
 "seat MSG + pre-seat probe script + probe receipt; per-wave prereg ",
 "r1003 dead-session derive landed pre-freeze [estate absorbed by the r1004 window] -- zero takeover face, bm-c own-seat ",
 "continuity, ",
 f"prereg {w241_prereg_sha[:10]} @ receipt {w241_receipt_sha[:10]}) -- this freeze splice editor derived from the committed W240 editor template in this same freeze window; ",
 "deletion-set EMPTY; delivery window = chain-order splice ",
 "after the W240 five-face + W240 finalize product landed ",
 "(executed in the bm-c loop freeze window ",
 "under the CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED ",
 "2026-10-10 ~23:1x); zero merge at freeze delivery, zero ",
 "--no-verify; single-window derive -- r812 merged the gate ",
 "legs INTO the pre-seat probe; parity N/A honest), ",
 "engine_owner=bm-c (bm-c OWN-SEAT face -- bm-c's SIXTY-SEVENTH owned claim per machine-derive (engine_owner==bm-c rows ",
 f"{len(bmc_rows_live)} + candidate; probe receipt leg0 bmc_ordinal=67 = seat-time pre-splice ",
 "live faces disclosed honest, live derive governs ",
 "r587/r359 -- zero takeover, own-seat continuity)), ",
 "wave 241: ",
 "A = FIRST-CLEAN arithmetic continuation of the prior-wave A tail (the continuation ",
 f"{fmt(w240_a_tail + 1)}..{fmt(w240_a_tail + 2_000)} is CLEAN at its own start ",
 "-- hops=0, A_hop_chain empty + A_clean_at_naive_start=true, seed-decoupled ",
 "A-continuation face, second consecutive seed-gap face exactly as the W240 seat leg4 ",
 "succession projection notes anticipated; A base == prior-wave A tail+1 (",
 f"{fmt(w240_a_tail)}+1) machine-checkable; ",
 "non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN arithmetic ",
 "continuation of the prior-wave B tail (the continuation ",
 f"{fmt(w240_b_tail + 1)}..{fmt(w240_b_tail + 200)} is CLEAN on the registered universe ",
 "hops=0, B_hop_chain empty + B_no_ownA_jump=true -- B lands OUTSIDE the ",
 f"own-A window {fmt(a_lo)}..{fmt(a_hi)}; seed-decoupled A/B gap ",
 "face third consecutive; B base == prior-wave B ",
 "tail+1 machine-checkable; cross-window convergence with the W240 seat leg4 succession projection ",
 "notes -- all MANDATORY notes honored (post-W240 universe ",
 "re-derive + live-trace re-read, no staircase-equality assumption); ADMIT receipt ",
 "results/_w241bmc_20261014_probe_receipt.json + ",
 "seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a ",
 "ADMIT convention); W242+ projection per this window gate: ",
 f"A naive first-clean {rec['legs']['leg4']['W242p_A_naive']} CLEAN (hops=0, zero live seed refusers) / B naive first-clean ",
 f"{rec['legs']['leg4']['W242p_B_naive']} CLEAN (hops=0, lands OUTSIDE the naive A window -- seed-gap face ",
 "inherited); W242 freezer MUST re-derive on the post-W241 universe AND ",
 "reserve the own-wave A window when deriving B (do NOT assume the ",
 "staircase A-base==prior-B-tail+1 equality) -- the finalize ",
 "merge loop still derives the wave set from registry keys at ",
 "run time, FAIL-CLOSED r307 always on)",
]
for i, s in enumerate(PRE):
    if i == len(PRE) - 1:
        cfg_lines.append(f'{PRE_I}"{s}"),')
    else:
        cfg_lines.append(f'{PRE_I}"{s}"')
cfg_lines += [
 f'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W241 A: {fmt(a_lo)}..{fmt(a_hi)} (FIRST-CLEAN arithmetic continuation of the prior-wave A tail; {fmt(w240_a_tail + 1)}..{fmt(w240_a_tail + 2_000)} CLEAN at naive start hops=0, A_hop_chain empty + A_clean_at_naive_start=true; seed-decoupled A-continuation face second consecutive seed-gap face; A base == prior-A tail+1)',
 f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W241 B: {fmt(b_lo)}..{fmt(b_hi)} (FIRST-CLEAN arithmetic continuation of the prior-wave B tail; {fmt(w240_b_tail + 1)}..{fmt(w240_b_tail + 200)} CLEAN hops=0, B_hop_chain empty + B_no_ownA_jump=true; B lands outside own-A; seed-decoupled A/B gap face third consecutive; B base == prior-B tail+1)',
 f'{MEM_I}"shard_subdir": "n1_w241", "out_name": "n1_w241_results.json",',
 f'{MEM_I}"engine_owner": "bm-c"}},',
]

cfg_block = EOL.join(cfg_lines)
old_cfg = must(n1_t, ('                       }' + EOL
                      + 'PREREG = WAVE_CONFIGS[2]["prereg"]'), 1, "n1_cfg_close")
new_cfg = (cfg_block + EOL
           + '                       }' + EOL
           + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
assert new_cfg.count('241: {"batch": "PERPETUAL-N1-W241"') == 1
n1_t2 = n1_t.replace(old_cfg, new_cfg, 1)

'''
span("# ---------- n1 cfg entry (programmatic quote wrapping, r761 law) ----------",
     "# ---------- n1 materializer block ----------",
     NEW_CFG)

# ================= 11. n1 materializer block span =================
NEW_MAT = r'''# ---------- n1 materializer block ----------
hdr = [
 "    # --- W241 materializer face (bm-c loop five-face freeze splice --",
 "    #     OWN-SEAT face under CEO fill-order standing 2026-10-08 ~23:5x",
 "    #     + RE-ISSUE 2026-10-10 ~23:1x + O-20260909-2334-bm-b sec.1-2",
 "    #     local-full-use + O-20260924-1730 claim-and-start same-round law):",
 "    #     bm-c's sixty-seventh owned per machine-derive (engine_owner==bm-c",
 f"    #     rows {len(bmc_rows_live)} + candidate; own-seat face: seat published=reserved by bm-c itself",
 "    #     (r1002 MSG-20261014-1755-bmc-w241-seat @ origin 20782916a; probe leg0",
 "    #     bmc_ordinal=67 = seat-time pre-splice faces;",
 "    #     live derive at freeze governs);",
 "    #     wave 241 = first free number after the",
 "    #     REGISTERED W240 row (five-face freeze " + w240_freeze_sha[:10] + "; bm-a own seat executed at",
 "    #     the bm-a r991 window; engine",
 "    #     self-burn 12/12 + finalize one-pass ledger 952,335 / K=525,920",
 "    #     -- SINGLE STATE zero seat gap (W2..W240 all registered). Seat",
 "    #     published=reserved MSG-20261014-1755-bmc-w241-seat pushed",
 "    #     to origin " + SEAT_ORIGIN + " BEFORE this freeze, r565 law (payload =",
 "    #     seat MSG + pre-seat probe script + probe receipt; per-wave prereg",
 f"    #     r1003 dead-session derive landed pre-freeze commit {w241_prereg_sha[:10]} [estate absorbed by the",
 "    #     r1004 window]; this freeze splice editor",
 "    #     derived from the committed W240 editor template in this same freeze",
 "    #     window (E63 heal lineage: arith_a241/arith_b241 define+assert consistent);",
 "    #     deletion-set EMPTY; delivery window",
 "    #     = chain-order splice after the W240 five-face + W240 finalize",
 "    #     product landed; zero --no-verify; the W241 seat MSG sits in",
 "    #     " + seat_found + " at freeze time, honest archived",
 "    #     per S7 law).",
 "    #     TWO HUNDRED AND FORTY-FIRST engine wave BY",
 f"    #     MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate; gate",
 "    #     leg0 machine output governs per r359 law).",
 f"    #     {fin_face}; the finalize merge loop",
 "    #     still derives the wave set from registry keys at run",
 "    #     time, FAIL-CLOSED r307 always on. ADMIT receipt",
 "    #     results/_w241bmc_20261014_probe_receipt.json;",
 "    #     seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a",
 f"    #     ADMIT convention upgrade): {gate_lines[0]}; {gate_lines[1]};",
 "    #     banned gate ADMIT 0 (re-run at freeze window);",
 "    #     not a re-pick (R250: W241 bands were never assigned).",
 "    _set_wave(241)",
 "    try:",
 '        assert WAVE_CONFIGS[240]["a_seed_base"] == pf.N1_BANDS[240]["a"][0], \\',
 '            "W241 upstream W240 mirror drift (a)"',
 "        assert WAVE_CONFIGS[240][\"b_exit_seed_base\"] == \\",
 '            pf.N1_BANDS[240]["b_exit"][0], "W241 upstream W240 mirror drift (b)"',
 "        assert WAVE_CONFIGS[240].get(\"engine_owner\") == \\",
 '            pf.N1_BANDS[240].get("engine_owner") == "bm-a", \\',
 '            "W241 upstream W240 engine_owner mirror drift (law-mirror parity; bm-a upstream seat face)"',
 "        w240_a = {A_SEED_BASE + j for j in range(A_N)}",
 "        w240_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
 '        assert not (w240_a & w240_b), "W241 A/B band overlap"',
 "        assert not (w240_a & reg_ints) and not (w240_b & reg_ints), \\",
 '            "W241 hits SEED_REGISTRY"',
 '        for nm, band in (("A", w240_a), ("B", w240_b)):',
 '            assert not (band & v1_a) and not (band & v1_b), f"W241 {nm} hits v1"',
 '            assert not (band & w1_a) and not (band & w1_b), f"W241 {nm} hits W1"',
 '            assert not (band & probes), f"W241 {nm} hits probe seeds"',
]

w232_leg = [
 f'        assert pf.N1_BANDS[232] == {{"a": ({fmt(pf_mod.N1_BANDS[232]["a"][0])}, {fmt(pf_mod.N1_BANDS[232]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[232]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[232]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\',
'            "registered W232 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]
w233_leg = [
 f'        assert pf.N1_BANDS[233] == {{"a": ({fmt(pf_mod.N1_BANDS[233]["a"][0])}, {fmt(pf_mod.N1_BANDS[233]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[233]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[233]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\',
'            "registered W233 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]
w234_leg = [
 f'        assert pf.N1_BANDS[234] == {{"a": ({fmt(pf_mod.N1_BANDS[234]["a"][0])}, {fmt(pf_mod.N1_BANDS[234]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[234]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[234]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\',
'            "registered W234 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]
w235_leg = [
 f'        assert pf.N1_BANDS[235] == {{"a": ({fmt(pf_mod.N1_BANDS[235]["a"][0])}, {fmt(pf_mod.N1_BANDS[235]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[235]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[235]["b_exit"][1])}),',
'                                    "engine_owner": "bm-a"}, \\',
'            "registered W235 row parity drift (r307; bm-a five-face freeze; takeover-window splice face disclosed)"',
]
w236_leg = [
 f'        assert pf.N1_BANDS[236] == {{"a": ({fmt(pf_mod.N1_BANDS[236]["a"][0])}, {fmt(pf_mod.N1_BANDS[236]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[236]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[236]["b_exit"][1])}),',
'                                    "engine_owner": "bm-a"}, \\',
'            "registered W236 row parity drift (r307; bm-a five-face freeze; own-seat face disclosed)"',
]
w237_leg = [
 f'        assert pf.N1_BANDS[237] == {{"a": ({fmt(pf_mod.N1_BANDS[237]["a"][0])}, {fmt(pf_mod.N1_BANDS[237]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[237]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[237]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\',
'            "registered W237 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]
w238_leg = [
 f'        assert pf.N1_BANDS[238] == {{"a": ({fmt(pf_mod.N1_BANDS[238]["a"][0])}, {fmt(pf_mod.N1_BANDS[238]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[238]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[238]["b_exit"][1])}),',
'                                    "engine_owner": "bm-a"}, \\',
'            "registered W238 row parity drift (r307; bm-a five-face freeze; own-seat face disclosed)"',
]
w239_leg = [
 f'        assert pf.N1_BANDS[239] == {{"a": ({fmt(pf_mod.N1_BANDS[239]["a"][0])}, {fmt(pf_mod.N1_BANDS[239]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[239]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[239]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\',
'            "registered W239 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]
w240_leg = [
 f'        assert pf.N1_BANDS[240] == {{"a": ({fmt(pf_mod.N1_BANDS[240]["a"][0])}, {fmt(pf_mod.N1_BANDS[240]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[240]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[240]["b_exit"][1])}),',
'                                    "engine_owner": "bm-a"}, \\',
'            "registered W240 row parity drift (r307; bm-a five-face freeze; own-seat face disclosed)"',
]
tail = [
 "        # prior-wave disjointness W2..W240 (single state: all",
 "        # registered, dynamic registry derive, r511 law)",
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 241):",
 '            assert not (w240_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
 "                                 for j in range(A_N)}), f\"W241 A hits W{wprev}\"",
 '            assert not (w240_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
 "                                  for j in range(B_N)}), f\"W241 B hits W{wprev}\"",
 "        n3r1_used241 = set(range(70_000, 70_006))",
 "        assert not (w240_a & n3r1_used241) and not (w240_b & n3r1_used241), \\",
 '            "W241 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
 "        assert not (w240_a & lfc_actual12) and not (w240_b & lfc_actual12), \\",
 '            "W241 bands must clear the lfc actual draw range"',
 "        assert not (w240_a & options_actual12) and \\",
 "            not (w240_b & options_actual12), \\",
 '            "W241 bands must clear the options_wave2 actual draw range"',
  "        # band facts (law sec.4 W241 row): A = FIRST-CLEAN arithmetic",
  "        # continuation of the prior-wave A tail",
 f"        # ({fmt(w240_a_tail + 1)}..{fmt(w240_a_tail + 2_000)} CLEAN at naive start on the",
  "        # registered universe, hops=0, A_hop_chain empty +",
  "        # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,",
  "        # second consecutive seed-gap face, exactly as the W240 seat leg4",
  "        # succession projection notes anticipated; A base == prior-wave A",
 f"        # tail+1 ({fmt(w240_a_tail)}+1) machine-checkable;",
  "        # B = FIRST-CLEAN arithmetic continuation of the prior-wave B",
 f"        # tail ({fmt(w240_b_tail + 1)}..{fmt(w240_b_tail + 200)} CLEAN on the registered",
  "        # universe, hops=0, B_hop_chain empty + B_no_ownA_jump=true -- B",
  "        # lands OUTSIDE the own-A window",
 f"        # {fmt(a_lo)}..{fmt(a_hi)}; seed-decoupled A/B gap face third consecutive;",
  "        # B base == prior-wave B tail+1",
 f"        # ({fmt(w240_b_tail)}+1) machine-checkable; cross-window convergence with",
  "        # the W240 seat leg4 succession projection notes -- all",
  "        # MANDATORY notes honored (post-W240 universe re-derive +",
  "        # live-trace re-read, no staircase-equality assumption);",
 f'        assert WAVE_CONFIGS[241]["a_seed_base"] == {a_lo} == {w240_a_tail} + 1, (',
 '            "W241 A must be the first-clean arithmetic continuation of the "',
 '            "prior-wave A tail (hops=0, A_hop_chain empty + A_clean_at_naive_start=true -- "',
 '            "seed-decoupled A-continuation face, second consecutive seed-gap face, "',
 '            "exactly as the W240 seat leg4 succession projection notes "',
 '            "anticipated; A base == prior-wave A tail+1 machine-checkable)")',
 f"        arith_a241 = set(range({a_lo}, {a_hi + 1}))",
 "        assert not (arith_a241 & reg_ints), \\",
 '            "W241 A window must be CLEAN (first-clean ADMIT face, A-continuation)"',
 f'        assert WAVE_CONFIGS[241]["b_exit_seed_base"] == {b_lo} == {w240_b_tail} + 1, (',
 '            "W241 B keeps the staircase base (FIRST-CLEAN arithmetic "',
 '            "continuation of the prior-wave B tail, hops=0, B_hop_chain "',
 '            "empty + B_no_ownA_jump=true -- B lands outside the own-A "',
 '            "window; seed-decoupled A/B gap face third consecutive; "',
 '            "B base == prior-wave B tail+1 machine-checkable)")',
 f"        arith_b241 = set(range({b_lo}, {b_hi + 1}))",
 "        assert not (arith_b241 & reg_ints), \\",
 '            "W241 B window must be CLEAN (first-clean ADMIT face, staircase-base continuation)"',
 "        assert not (arith_b241 & arith_a241), \\",
 '            "W241 A/B same-freeze mutual exclusion (seed-decoupled gap face inherited: B below own A)"',
 "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W241-SHARD-0\",",
 '                                          "n1w241-0of12"), "W241 entry identity"',
 '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W241-SHARD-11",',
 '                                           "n1w241-11of12")',
 "        assert SHARD_DIR.endswith(\"n1_w241\") and OUT.endswith(",
 '            "n1_w241_results.json"), "W241 path drift"',
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 241):",
 "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(",
 "                PATHS.results_dir, \"p2cal_ext\",",
 "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\",
 '                f"W241 shard dir collides with W{wprev}"',
 "        # W241 finalize cumulative deps: W17..W240 outputs ALL PRESENT",
 f"        # (landed net chain head {w240_total} machine-read at freeze time)",
 "        # -- ZERO in-flight upstream seats at splice, clean precondition",
 "        # freeze window; the finalize merge loop derives the wave",
 "        # set from registry keys at run time and stays",
 "        # FAIL-CLOSED, r307 two-state law).",
 "        for _depw in range(17, 241):",
 "            assert os.path.exists(os.path.join(",
 "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\",
 '                f"W241 finalize cumulative dep (W{_depw} output) missing"',
 "        # finalize wave-set derivation face (r511 derive law): every",
 "        # registered wave below 241 composes; wave 15 excluded by",
 "        # design; SINGLE STATE (W2..W240 all registered -- no",
 "        # two-state seat disclosure needed at this freeze).",
 "        assert sorted(w for w in WAVE_CONFIGS if w < 241) == \\",
 "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\",
 "            [w for w in range(16, 241)], \\",
 '            "W241 prior-wave set must derive from registry keys (no 15; " \\',
 '            "W2..W240 registered single state)"',
 "        assert os.path.exists(os.path.join(",
 '            PATHS.root, "research", "PERPETUAL_N1_W241_PREREG.md")), \\',
 '            "W241 per-wave prereg missing (materializer requirement)"',
 "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"",
 "    finally:",
 "        _set_wave(2)",
]
block = EOL.join(hdr) + EOL + par_sec + EOL.join(w232_leg) + EOL + EOL.join(w233_leg) + EOL + EOL.join(w234_leg) + EOL + EOL.join(w235_leg) + EOL + EOL.join(w236_leg) + EOL + EOL.join(w237_leg) + EOL + EOL.join(w238_leg) + EOL + EOL.join(w239_leg) + EOL + EOL.join(w240_leg) + EOL + EOL.join(tail) + EOL
# family #6 atomic triple gate (carried forward): the new
# block's LHS w<241> / RHS range(16,241)+range(17,241) / comment below-241 MUST move together.
assert block.count("if w < 241)") == 3, f"family-6 triple: w<241 count {block.count('if w < 241)')} != 3"
assert block.count("if w < 240)") == 0, "family-6 triple: stale w<240 leaked into the W241 block"
assert block.count("range(16, 241)") == 1 and block.count("range(17, 241)") == 1, "family-6 triple: RHS ranges wrong"
assert block.count("registered wave below 241 composes") == 1, "family-6 triple: comment face wrong"
old_blk_anchor = must(n1_t2, "    # --- T-141 s2 lane face", 1, "t141_marker")
n1_t3 = n1_t2.replace(old_blk_anchor, block + old_blk_anchor, 1)

'''
span("# ---------- n1 materializer block ----------",
     "# ---------- n1 print line ----------",
     NEW_MAT)

# ================= 12. n1 print line span =================
NEW_PRINT = r'''# ---------- n1 print line ----------
pr = [
 '          "+ W241 materializer face [same guard set, dep=W17..W240 "',
 f'          "outputs ALL PRESENT (landed net chain head {w240_total} = W240 bm-a finalize one-pass, K={w240_merged_n} merged pool) -- ZERO "',
 '          "in-flight upstream seats at splice, clean precondition, TWO HUNDRED AND FORTY-FIRST "',
 f'          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} "',
 '          "+ candidate) bm-c\'s sixty-seventh owned claim per "',
 '          "machine-derive (engine_owner==bm-c rows 66 + candidate; OWN-SEAT face: seat published by bm-c itself, "',
 '          "probe leg0 bmc_ordinal=67 = seat-time pre-splice faces disclosed honest, "',
 '          "live derive at freeze governs), "',
 '          "A=FIRST-CLEAN arithmetic continuation of prior-wave A tail (A-continuation face, "',
 '          "hops=0, A_hop_chain empty + A_clean_at_naive_start=true, seed-decoupled second consecutive seed-gap face) "',
 '          "+ B=staircase-base continuation "',
 '          "(prior-B-tail+1 EXACT, hops=0, B_hop_chain empty + B_no_ownA_jump=true, seed-decoupled A/B gap face third consecutive), chain-order splice from the "',
 '          "committed ADMIT receipt + seed_admit_gate rc0 both bands FREE "',
 '          "(O-20261010-1945-bm-a ADMIT convention), "',
 '          "ADMIT receipt "',
 '          "results/_w241bmc_20261014_probe_receipt.json, law sec.4 W241 row, "',
 '          "bm-c loop CEO fill-order RE-ISSUE 23:1x] "',
]

old_pr = must(n1_t3, '          "+ T-141 s2 ', 1, "print_t141")
n1_t4 = n1_t3.replace(old_pr, EOL.join(pr) + EOL + old_pr, 1)

'''
span("# ---------- n1 print line ----------",
     "# ---------- post-edit count gates ----------",
     NEW_PRINT)

# ================= 13. post-edit count gates span =================
NEW_POSTGATES = r'''# ---------- post-edit count gates ----------
assert n1_t4.count('"batch": "PERPETUAL-N1-W241"') == 1
assert n1_t4.count("# --- W241 materializer face") == 1     # block header
assert n1_t4.count('"+ W241 materializer face') == 1        # print fragment
assert n1_t4.count('241: {"batch": "PERPETUAL-N1-W241"') == 1
assert pf_t2.count(ROW_I + '241: {"a"') == 1
assert pf_t2.count('"engine_owner": "bm-c"},' + PF_EOL + '}') == 1
assert n1_t4.count('    # --- T-141 s2 lane face') == 1
assert n1_t4.count('"PERPETUAL-N1-W241-SHARD-0"') == 1
assert n1_t4.count(f'assert pf.N1_BANDS[240] == {{"a": ({fmt(pf_mod.N1_BANDS[240]["a"][0])}, {fmt(pf_mod.N1_BANDS[240]["a"][1])}),') == 1
# the W240 leg lives ONLY in the new W241 block (1); the W239 leg lives in the
# kept W240 block + the new W241 block (2); the W238 leg lives in kept W239 +
# W240 + new W241 (3); the W237 leg in kept W238+W239+W240+new (4); the W236
# leg in kept W237..W240+new (5); the W235 leg in kept W236..W240+new (6)
assert n1_t4.count(f'assert pf.N1_BANDS[239] == {{"a": ({fmt(pf_mod.N1_BANDS[239]["a"][0])}, {fmt(pf_mod.N1_BANDS[239]["a"][1])}),') == 2
assert n1_t4.count(f'assert pf.N1_BANDS[238] == {{"a": ({fmt(pf_mod.N1_BANDS[238]["a"][0])}, {fmt(pf_mod.N1_BANDS[238]["a"][1])}),') == 3
assert n1_t4.count(f'assert pf.N1_BANDS[237] == {{"a": ({fmt(pf_mod.N1_BANDS[237]["a"][0])}, {fmt(pf_mod.N1_BANDS[237]["a"][1])}),') == 4
assert n1_t4.count(f'assert pf.N1_BANDS[236] == {{"a": ({fmt(pf_mod.N1_BANDS[236]["a"][0])}, {fmt(pf_mod.N1_BANDS[236]["a"][1])}),') == 5
assert n1_t4.count(f'assert pf.N1_BANDS[235] == {{"a": ({fmt(pf_mod.N1_BANDS[235]["a"][0])}, {fmt(pf_mod.N1_BANDS[235]["a"][1])}),') == 6
for _b in range(209, 242):
    assert n1_t4.count(f"    # --- W{_b} materializer face") == 1, f"W{_b} block kept-count drift"
# no start>end malformed windows in inserted prose (r773 law)
for seg in (pf_comment, cfg_block, block, EOL.join(pr)):
    for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", seg):
        lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
        assert lo <= hi, f"malformed window {m.group(0)} in inserted prose"

'''
span("# ---------- post-edit count gates ----------",
     "# ---------- write + AST gate ----------",
     NEW_POSTGATES)

# ================= 14. receipt span (to EOF) =================
NEW_RECEIPT = r'''# ---------- receipt ----------
receipt = {
  "machine": "bm-c", "wave": 241,
  "phase": "five-face freeze chain-order splice (bm-c own-seat freeze window, upstream ALL LANDED clean precondition)",
  "origin_base": omain,
  "pf_sha16_pre": hashlib.sha256(pf_b).hexdigest()[:16],
  "n1_sha16_pre": hashlib.sha256(n1_b).hexdigest()[:16],
  "pf_sha16_post": hashlib.sha256(pf_t2.encode("utf-8")).hexdigest()[:16],
  "n1_sha16_post": hashlib.sha256(n1_t4.encode("utf-8")).hexdigest()[:16],
  "bands": {"A": A, "B": B, "a_lo": a_lo, "a_hi": a_hi, "b_lo": b_lo, "b_hi": b_hi},
  "admit_receipt": "results/_w241bmc_20261014_probe_receipt.json",
  "seed_admit_gate": gate_lines,
  "banned_gate": "ADMIT rc0 (re-run at freeze window)",
  "band_semantics": {"A": "FIRST-CLEAN arithmetic continuation of prior-wave A tail (hops=0, A_hop_chain empty + A_clean_at_naive_start=true; seed-decoupled A-continuation face, second consecutive seed-gap face; A base == prior-A tail+1 EXACT)",
                     "B": "FIRST-CLEAN arithmetic continuation of prior-wave B tail (hops=0, B_hop_chain empty + B_no_ownA_jump=true; B base == prior-B tail+1 EXACT; seed-decoupled A/B gap face third consecutive)"},
  "w240_upstream": {"freeze_sha": w240_freeze_sha, "prereg_sha": w240_prereg_sha,
                    "ledger_total": w240_total, "merged_n": w240_merged_n,
                    "engine_owner": "bm-a (upstream seat honored)",
                    "repair_chain_note": "W240 bm-a own-wave closeout bm-a r993 window (five-face splice dc27f5217 + engine self-burn 12/12 + finalize one-pass ledger 952,335 / K=525,920)"},
  "own_seat_face": {"seat_msg": SEAT_MSG, "seat_origin": SEAT_ORIGIN,
                    "inherited": False,
                    "note": "seat published=reserved by bm-c itself (MSG-20261014-1755-bmc-w241-seat pushed to origin 20782916a r1002 BEFORE this freeze per r565 law, queue-depth supply depth-2, freeze waited-upstream on the W240 finalize); zero takeover -- wave 241 engine_owner=bm-c, bm-c's 67th own wave per live derive (probe leg0 bmc_ordinal=67 = seat-time pre-splice faces disclosed honest, live derive governs r587/r359; freeze-time live face owner rows 230 + candidate = 231st EXACT)"},
  "transitive_deps": {f"W{w}": f"results/perpetual_faces/n1_w{w}_results.json present (belt-and-braces gate)" for w in (239, 238, 237, 236, 235, 234, 233, 232)},
  "downstream_seat": "W242 seat ALREADY PUBLISHED by bm-a at this freeze window (MSG-20261014-1814-bma-w242-seat @ origin 138a94745, bm-a 124th owned, 232nd engine wave = never-dry queue-depth supply depth-2; the W242 freezer MUST re-derive live on the post-W241 universe + reserve the own-wave A window when deriving B per the W241 seat leg4 mandate, never transcribe r587)",
  "seat": seat_found + " (origin " + SEAT_ORIGIN + ")",
  "prereg_bundle": {"prereg_sha": w241_prereg_sha, "probe_receipt_sha": w241_receipt_sha,
                    "note": "prereg derived+committed by the dead r1003 session (machine-SUB from the frozen W240 tpl 22c6c3374; estate absorbed by THIS r1004 window per the bm-c absorb precedent lineage 25th instance; zero takeover; freeze-time live derive bmc rows 66 + candidate 67th EXACT per r587/r359); splice editor derived from the committed W240 editor template by count-asserted ordered transform in this same freeze window (E63 heal lineage: arith_a241/arith_b241 define+assert consistent); upstream W240 already landed (clean-precondition thirtieth consecutive window); zero transcription"},
  "ordinal_faces": {"owner_rows_live": len(owner_rows_live), "bma_rows_live": len(bma_rows_live),
                    "bmc_rows_live": len(bmc_rows_live),
                    "engine_owned_ordinal": len(owner_rows_live) + 1,
                    "bmc_own_ordinal": len(bmc_rows_live) + 1,
                    "probe_receipt_bmc_ordinal_face": 67,
                    "note": "post-W240 registration: bm-c rows 66 + candidate = 67th owned (live derive at freeze time governs per r587/r359; probe leg0 bmc_ordinal=67 = seat-time faces -- zero takeover, own-seat continuity)"},
  "parity_section": {"source": "OWN W240 block physical bytes (bm-a splice generation r991 window, structure known exactly)",
                    "bytes": len(par_sec),
                    "row_asserts": par_sec.count("assert pf.N1_BANDS["),
                    "note": "full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W231 legs -> W241 block = 99 rows ending at W240 (estate 90 + fresh W232 leg + W233 leg + W234 leg + W235 leg + W236 leg + W237 leg + W238 leg + W239 leg + W240 leg); disclosed: (a) inherited W213 leg error-string face (\"registered W212 row parity drift\") preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact); (b) W240 block's band-set variable one-behind naming face (w240_a holds wave-241 bands) = lineage mechanical aging face, zero functional impact"},
  "family6_triple_gate": {"absorbed": True,
                          "note": "W240 editor family-6 gate carried forward: new block LHS w<241 x3 / RHS range(16,241)+range(17,241) / comment below-241 count-asserted ATOMICALLY before splice; W240 block's own w<240 face = legitimate prior-wave boundary (not stale); E63 heal lineage applied (arith define/assert consistent)"},
  "eol": {"n1_crlf": EOL == "\r\n", "pf_crlf": PF_EOL == "\r\n"},
  "liveness_anchors": {f"w{_b}_block_kept": 1 for _b in range(209, 242)},
}

open(RECEIPT_OUT, "w", encoding="utf-8").write(json.dumps(receipt, indent=1))
print(json.dumps({k: receipt[k] for k in
      ("phase", "origin_base", "pf_sha16_post", "n1_sha16_post", "bands",
       "w240_upstream", "own_seat_face")}, indent=1))
print("SPLICE OK -- py_compile both green; NEXT: selftest (default wave, r522 law) -> pathspec commit+push -> engine self-ignite W241 burn (12 shards) -> PRE-FINALIZE six-gate (standing law) -> finalize one-pass")'''
span("# ---------- receipt ----------",
     "finalize one-pass\")",
     NEW_RECEIPT, include_end=True)

# ================= write + verify =================
if fails:
    print("DERIVE FAIL-CLOSED -- %d replacement(s) mismatched, editor NOT written:" % len(fails))
    for f in fails:
        print("  expected=%s got=%s :: %s" % (f[2], f[1], f[0]))
    sys.exit(1)

# generation-shift residue sweep (fail-closed): zero W240-owner strings may remain
# in the derived editor's own-face positions
for stale in ('_w240bma_20261014_probe_receipt', '_w240bma_freeze_receipt',
              'MSG-20261014-1325-bma-w240-seat', 'SEAT_ORIGIN = "39a30b6a0"',
              'W239 five-face landed', '"engine_owner": "bm-a"}},' + "\n"):
    if stale in t:
        fails.append(("STALE-RESIDUE " + stale[:70], 1, 0))
if fails:
    print("DERIVE FAIL-CLOSED -- stale residue:")
    for f in fails:
        print("  :: %s" % (f[0],))
    sys.exit(1)

if IS_CRLF:
    t = t.replace("\n", "\r\n")
open(OUT, "wb").write(t.encode("utf-8"))
py_compile.compile(OUT, doraise=True)
print("DERIVE OK -- %s written and py_compile green (%d bytes)" % (OUT, len(t.encode("utf-8"))))
