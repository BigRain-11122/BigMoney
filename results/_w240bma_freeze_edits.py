# -*- coding: utf-8 -*-
# 2026-10-14 16:1x bm-a r991 freeze window (upstream W1..W239 ALL LANDED, clean
# precondition -- W239 finalize one-pass bm-c r996-continuation window, ledger
# head 950,135 / K=523,720 machine-read): W240 five-face freeze splice editor
# -- bm-a OWN-SEAT face (seat MSG-20261014-1325-bma-w240-seat published=
# reserved by bm-a itself @ origin 39a30b6a0 r986, pre-seat probe ADMIT receipt
# results/_w240bma_20261014_probe_receipt.json same payload; per-wave prereg
# PERPETUAL_N1_W240_PREREG.md derived+landed by the dead r989 session commit
# 3e44118e [estate absorbed by THIS r991 window per the bm-a absorb precedent
# lineage], zero takeover, zero DRAFT marker; preflight contributed by the
# dead r990-yield retreat window results/_w240bma_preflight.py ALL GREEN,
# estate absorbed in commit 2c0bf15b9).
# Lineage: _w239bmc_freeze_edits.py template (proven live-fire freeze, bm-c
# r996-continuation window; engine self-burn + finalize one-pass verified) +
# r787 preflight law + r609 origin-verbatim base + r761 programmatic quote
# wrapping + r909 physical-byte anchors + r838 per-file EOL detection +
# family #6 LHS/RHS/comment ATOMIC TRIPLE (the new block's w<240>/
# range(16,240)/range(17,240)/below-240 quadruple is count-asserted
# atomically; the W239 block's own w<239 face is legitimate prior-wave
# boundary, not stale) + E63 heal lineage (arith_a240/arith_b240 define+assert
# consistent).
# Zero hardcoded upstream band values: ALL W239 facts machine-derived from the
# LIVE pf import at freeze time (the registered W239 row -- bm-c seat honored),
# cross-checked against the committed ADMIT receipt
# (results/_w240bma_20261014_probe_receipt.json) which was derived on the
# post-W239-DECLARED universe. If the LIVE W239 bands differ from the declared
# face, the staircase asserts fail LOUD (fail-closed).
# STRUCTURAL CHOICE (vs the W239 editor): the parity estate (W138..W206
# full-span 69 rows, r858 absorb generation, + W211..W231 legs) is extracted
# from the OWN W239 block physical bytes -- structure known exactly (bm-c's
# splice generation, committed) -- the W239 block's own W232..W238 legs are
# excluded from the estate path and fresh W232..W239 legs are appended for the
# W240 block parity (98 rows: estate 90 ending W231 + W232 leg + W233 leg +
# W234 leg + W235 leg + W236 leg + W237 leg + W238 leg + W239 leg).
# Extraction self-asserts the 90-row cut regardless.
# Disclosed: (a) the inherited W213 leg inside the estate carries a cosmetic
# error-string face ("registered W212 row parity drift") from the r912 editor
# generation -- physical bytes preserved verbatim per extraction law, zero
# functional impact (assert target [213] is correct); (b) the band-set
# variable naming one-behind face (w239_a holds wave-240 bands) is the
# lineage's mechanical aging face -- the W240 block follows the same
# mechanical pattern as its ancestors, zero functional impact.
# Own bundle hashes (prereg/probe receipt) derived via pickaxe, never transcribed.
# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.
import json, hashlib, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PF = os.path.join(REPO, "scripts", "perpetual_faces.py")
N1 = os.path.join(REPO, "scripts", "perpetual_faces_n1.py")
RECEIPT_IN = os.path.join(REPO, "results", "_w240bma_20261014_probe_receipt.json")
RECEIPT_OUT = os.path.join(REPO, "results", "_w240bma_freeze_receipt.json")
SEAT_MSG = "MSG-20261014-1325-bma-w240-seat.md"
SEAT_ORIGIN = "39a30b6a0"
PY = sys.executable

def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True)

# ---------- gate 0: fresh origin, working == origin (r609 law) ----------
git("fetch", "origin")
r = git("rev-parse", "HEAD"); head = r.stdout.decode().strip()
ro = git("rev-parse", "origin/main"); omain = ro.stdout.decode().strip()
anc = git("merge-base", "--is-ancestor", "origin/main", "HEAD")
assert anc.returncode == 0, f"origin/main {omain} not contained in HEAD {head} -- rebase first (r609)"
for path in ("scripts/perpetual_faces.py", "scripts/perpetual_faces_n1.py"):
    b = git("show", f"origin/main:{path}")
    w = open(os.path.join(REPO, path), "rb").read()
    assert b.stdout.replace(b"\r\n", b"\n") == w.replace(b"\r\n", b"\n"), \
        f"working {path} != origin blob (content, EOL-normalized) -- stale base (r609 abort)"

sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "research"))
import perpetual_faces as pf_mod

# ---------- gate 0.5: W239 five-face landed + W239 finalize product present ----------
# (chain-order precondition; W238/W237/W236/W235/W234/W233/W232/W231 finalize are
# transitive deps of the W239 freeze and are belt-and-braces checked here + enforced
# by the block's cumulative-deps assert range(17, 240) at selftest time)
W239 = dict(pf_mod.N1_BANDS.get(239) or {})
assert W239.get("engine_owner") == "bm-c", \
    f"W239 row not landed as declared (bm-c seat owner expected): {W239} -- five-face freeze missing;" \
    " if an unexpected face exists the freeze window MUST re-derive this editor honestly"
w239_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w239_results.json")
assert os.path.exists(w239_out_path), "W239 finalize product missing (n1_w239_results.json) -- chain dep not met"
for _w in (238, 237, 236, 235, 234, 233, 232, 231):
    assert os.path.exists(os.path.join(REPO, "results", "perpetual_faces", f"n1_w{_w}_results.json")), \
        f"W{_w} finalize product missing (transitive chain dep) -- abort"
w239_out = json.load(open(w239_out_path, encoding="utf-8"))
w239_led = (w239_out.get("science_gates") or {}).get("ledger") or {}
w239_total = w239_led.get("total")
w239_merged_n = None
try:
    w239_merged_n = w239_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
assert w239_total == 950_135 and w239_merged_n == 523_720, \
    f"W239 finalize anchors drift at freeze time: total={w239_total} merged={w239_merged_n} (expect 950,135 / 523,720)"
# freeze shas machine-derived (pickaxe), never transcribed
r = git("log", "--format=%H", "-S", '239: {"a"', "--", "scripts/perpetual_faces.py")
w239_freeze_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W239_PREREG.md")
w239_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W240_PREREG.md")
w240_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
assert os.path.exists(os.path.join(REPO, "research", "PERPETUAL_N1_W240_PREREG.md")), \
    "W240 per-wave prereg missing on disk -- chain face incomplete, abort (r989 dead-session derive landed pre-freeze expected)"
with open(os.path.join(REPO, "research", "PERPETUAL_N1_W240_PREREG.md"), encoding="utf-8") as _fh:
    _pre_head = _fh.read(2000)
assert "DRAFT-NOT-FROZEN" not in _pre_head, "W240 prereg still DRAFT -- abort (freeze commit pending face)"
# live ordinal derive (r359 law: gate machine output governs; the pre-seat probe
# receipt leg0 face owner_rows=228 / bma_rows=122 / bma_ordinal=123
# = seat-time PRE-W239-splice live faces; live derive at freeze time:
# W239 splice LANDED -> owner rows 229 + candidate = 230th EXACT; bm-a rows 122 +
# candidate = 123rd EXACT -- bm-a own-seat continuity face, zero takeover)
owner_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner")]
bma_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-a"]
bmc_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
assert len(owner_rows_live) == 229 and len(bma_rows_live) == 122 and len(bmc_rows_live) == 66, \
    f"leg0 ordinal drift at freeze time: owner={len(owner_rows_live)} bma={len(bma_rows_live)} bmc={len(bmc_rows_live)} (expect 229/122/66 PRE-splice post-W239 registration; this candidate = bm-a's 123rd own wave per the same live-derive law, r587/r359)"
print(f"gate0.5 OK: W239 landed (freeze {w239_freeze_sha[:10]}, owner=bm-c seat honored, zero takeover face), "
      f"W239+W238+W237+W236+W235+W234+W233+W232+W231 finalize products present "
      f"(W239 ledger head {w239_total}, merged n={w239_merged_n}); owner rows {len(owner_rows_live)} + candidate, "
      f"bm-a rows {len(bma_rows_live)} + candidate (123rd own wave per live derive; "
      f"probe receipt leg0 bma_ordinal=123 = seat-time pre-splice faces disclosed honest)")

# ---------- band facts from the committed ADMIT receipt (never transcribed) ----------
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
assert (a_lo, a_hi) == (545_501, 547_500) and (b_lo, b_hi) == (540_804, 541_003), \
    f"W240 band drift vs probe ADMIT: {(a_lo, a_hi)} {(b_lo, b_hi)}"
w239_b_tail = W239["b_exit"][1]      # registered W239 row b_exit hi (pf import, live)
w239_a_tail = W239["a"][1]            # registered W239 row A hi (pf import, live)
# W240 FACE (seed-hop decoupled, probe receipt leg1 relation_asserts):
# B keeps the staircase base (prior-wave B tail+1 EXACT); A seed-hops past
# a live SEED_REGISTRY point far above it (first live-seed refusal -- the
# refuser is a SEED POINT, not a prior-wave band, W239 A/B decoupled) --
# A base >= prior-B tail+1 with a live-seed gap, NOT the equality face;
# machine-derived from the LIVE registered row, never transcribed.
assert w239_b_tail + 1 == b_lo, "B staircase base relation broken (B == prior-wave B tail+1 EXACT)"
assert a_lo > w239_b_tail + 1, "A seed-hop face violated: A base must sit ABOVE prior-B tail+1 (live-seed gap)"
assert b_hi < a_lo, "seed-decoupled A/B gap face violated: B window must sit entirely below own-A"
assert W239["b_exit"][1] < W239["a"][0], \
    "upstream W239 row in-wave decoupled relation broken (registered W239 B window must sit below own W239 A window)"
assert leg1.get("hops_A") == 1 and leg1.get("hops_B") == 0, "hop-count drift vs probe receipt leg1"
assert leg1.get("A_hop_chain") and leg1["A_hop_chain"][0]["jump_to"] == a_lo \
    and leg1["A_hop_chain"][0]["refuser_bands"] == [] \
    and leg1["A_hop_chain"][0]["refuser_pts"] == [545_500], \
    "A hop-chain refuser face drift: the refuser must be the live SEED_REGISTRY point 545_500, NOT a prior-wave band (W239 A/B decoupled)"
assert leg1.get("B_hop_chain") == [] and leg1.get("B_naive_hops") == 0, "B hop-chain face drift (fc_b == fc_b_naive, hops=0)"
ra = leg1.get("relation_asserts") or {}
assert ra.get("A_base_ge_priorB_tail_plus1") and ra.get("B_base_eq_priorB_tail_plus1") \
    and ra.get("AB_mutual_exclusion") and ra.get("B_no_ownA_jump"), \
    f"probe receipt leg1 relation_asserts face drift: {ra}"
assert [w239_a_tail + 1, w239_a_tail + 2_000] == leg1["ARITH_A"], \
    f"refused-continuation start drift vs probe receipt leg1 ARITH_A: {[w239_a_tail + 1, w239_a_tail + 2_000]} != {leg1['ARITH_A']}"
assert [w239_b_tail + 1, w239_b_tail + 200] == leg1["ARITH_B"], \
    f"B-continuation drift vs probe receipt leg1 ARITH_B: {[w239_b_tail + 1, w239_b_tail + 200]} != {leg1['ARITH_B']}"

# own bundle shas via pickaxe (self-referencing commit facts, zero transcription)
r = git("log", "--diff-filter=A", "--format=%H", "--", "results/_w240bma_20261014_probe_receipt.json")
w240_receipt_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
# seat MSG honest location (inbox or processed; S7 archive law)
seat_found = None
for _p in ("fleet/inbox", "fleet/inbox/processed"):
    if os.path.exists(os.path.join(REPO, _p, SEAT_MSG)):
        seat_found = _p + "/" + SEAT_MSG
        break
assert seat_found, f"W240 seat MSG missing from both inbox paths: {SEAT_MSG}"

# ---------- re-run discipline gates at freeze window (banned + seed_admit) ----------
g = subprocess.run([PY, os.path.join(REPO, "Tools", "banned_direction_gate.py"),
                    "--prereg", "research/PERPETUAL_N1_W240_PREREG.md"],
                   cwd=REPO, capture_output=True, text=True, encoding="utf-8",
                   errors="replace")
assert g.returncode == 0, f"banned gate FAIL: {g.stdout} {g.stderr}"
gate_lines = []
for base, span in ((a_lo, 2_000), (b_lo, 200)):
    g2 = subprocess.run([PY, os.path.join(REPO, "Tools", "seed_admit_gate.py"),
                         str(base), "--span", str(span)],
                        cwd=REPO, capture_output=True, text=True, encoding="utf-8",
                        errors="replace")
    assert g2.returncode == 0, f"seed_admit_gate FAIL base={base}: {g2.stdout} {g2.stderr}"
    gate_lines.append(g2.stdout.strip().splitlines()[-1] if g2.stdout.strip()
                      else f"rc0 base={base} span={span}")
print("gates OK:", " | ".join(gate_lines))

# ---------- read files, EOL (r838 law: runtime per-file detection) ----------
pf_b = open(PF, "rb").read(); pf_t = pf_b.decode("utf-8")
n1_b = open(N1, "rb").read(); n1_t = n1_b.decode("utf-8")

def detect_eol(t):
    """r838 law: per-file runtime EOL detection, never assume a single convention."""
    crlf = t.count("\r\n")
    lf = t.count("\n") - crlf
    return "\r\n" if crlf > lf else "\n"

EOL = detect_eol(n1_t); PF_EOL = detect_eol(pf_t)
assert pf_t.count(PF_EOL) > 0 and n1_t.count(EOL) > 0, \
    f"EOL detection degenerate: pf={PF_EOL!r} n1={EOL!r}"

def must(t, s, n, what):
    c = t.count(s)
    assert c == n, f"anchor {what}: count {c} != {n}"
    return s

def fmt(n):  # 501004 -> "501_004"
    return f"{n // 1000}_{n % 1000:03d}"

# ---------- extract parity section (physical bytes, never re-typed) ----------
# STRUCTURAL CHOICE: extract the estate from the OWN W239 block (bytes known
# exactly: full-span estate W138..W206 69 rows + own W211..W231 legs = 90
# rows) -- the W239 block is bm-c's own splice generation (r996-continuation
# window editor), structure known. The W239 block span ends where the T-141
# s2 lane face marker begins.
a19 = '    # --- W239 materializer face'
a_t141 = '    # --- T-141 s2 lane face'
w239_start = n1_t.find(a19); t141_pos = n1_t.find(a_t141)
assert w239_start > 0 and t141_pos > w239_start, \
    "W239 materializer block face not found (W239 freeze not landed? header-text drift -> honest re-derive required)"
blk = n1_t[w239_start:t141_pos]
m_first_row = re.search(r"assert pf\.N1_BANDS\[", blk)
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state", blk)
assert m_first_row and m_disj and m_disj.start() > m_first_row.start(), \
    "parity span markers not found in W239 block"
_row_ls = blk.rfind(EOL, 0, m_first_row.start()) + len(EOL)
par_full = blk[_row_ls:m_disj.start()]
m232 = re.search(r" *assert pf\.N1_BANDS\[232\] ==", par_full)
assert m232, "upstream W232 row leg not found inside W239 parity span"
par_sec = par_full[:m232.start()]
assert par_sec.endswith(EOL), "estate segment must end with EOL"
_estate_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", par_sec)
assert par_sec.count("assert pf.N1_BANDS[") == 90 \
    and [int(w) for w in _estate_ws[:69]] == list(range(138, 207)) \
    and [int(_estate_ws[69 + i]) for i in range(11)] == [211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221] \
    and [int(_estate_ws[80 + i]) for i in range(9)] == [222, 223, 224, 225, 226, 227, 228, 229, 230] \
    and int(_estate_ws[89]) == 231, \
    f"estate segment not W138..W206 full-span 69 rows + W211..W230 legs + W231 leg: n={par_sec.count('assert pf.N1_BANDS[')} range={(_estate_ws[:2], _estate_ws[-4:])}"
assert par_full.count("assert pf.N1_BANDS[") == 97, \
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 97 (69 estate + W211..W230 legs + W231 leg + W232 leg + W233 leg + W234 leg + W235 leg + W236 leg + W237 leg + W238 leg)"

# ---------- indent extraction (physical, not assumed; per-file EOL) ----------
def line_indent(t, needle, eol):
    i = t.find(needle)
    assert i >= 0, f"indent needle not found: {needle[:40]}"
    ls = t.rfind(eol, 0, i) + len(eol)
    line = t[ls:t.find(eol, ls)]
    return line[:len(line) - len(line.lstrip(" "))]

CFG_I  = line_indent(n1_t, '239: {"batch"', EOL)
PRE_KEY_I = line_indent(n1_t, '"prereg": ("research/PERPETUAL_N1_W239_PREREG.md', EOL)
PRE_I  = line_indent(n1_t, '"pre-run; design = frozen v1 null calibration verbatim, "', EOL)
# MEM_I derived INSIDE the W239 cfg entry span (own splice generation, value
# format known: plain int -- indent is all we take)
_c239 = n1_t.find('239: {"batch"')
assert _c239 > 0, "W239 cfg entry not found (W239 freeze not landed?)"
_mpos = n1_t.find('"a_seed_base"', _c239)
assert _mpos > 0 and n1_t.find('"shard_subdir"', _c239) > _mpos, "W239 cfg a_seed_base line not found"
MEM_I  = line_indent(n1_t, '"a_seed_base": ' + str(W239["a"][0]), EOL) \
    if n1_t.find('"a_seed_base": ' + str(W239["a"][0]), _c239) > 0 \
    else line_indent(n1_t, '"a_seed_base": ' + fmt(W239["a"][0]), EOL)
ROW_I  = line_indent(pf_t,  '239: {"a"', PF_EOL)

# ---------- W239 row owner line (physical bytes; comment text is own generation) ----------
w239_row_start = pf_t.find('    239: {"a"')
assert w239_row_start > 0, "W239 row literal not found in pf source"
_own_ls = pf_t.find(PF_EOL, w239_row_start) + len(PF_EOL)
_own_le = pf_t.find(PF_EOL, _own_ls)
w239_own_line = pf_t[_own_ls:_own_le]
assert '"engine_owner": "bm-c"' in w239_own_line, \
    f"W239 owner line unexpected bytes: {w239_own_line!r}"
ROWC_I = w239_own_line[:len(w239_own_line) - len(w239_own_line.lstrip(" "))]

# ---------- pf comment + row ----------
pf_comment = PF_EOL.join([
"    # W240 (bm-a loop five-face freeze splice -- OWN-SEAT face, seat",
"    # MSG-20261014-1325-bma-w240-seat published=reserved by bm-a itself @",
"    # origin " + SEAT_ORIGIN + " (r986, queue-depth supply depth-2, zero takeover); prereg + ADMIT probe",
"    # receipt frozen commit " + w240_prereg_sha[:10] + " (prereg research/PERPETUAL_N1_W240_PREREG.md",
"    # r989 dead-session derive landed pre-freeze [estate absorbed by the",
"    # r991 window], probe",
"    # results/_w240bma_20261014_probe_receipt.json @ " + w240_receipt_sha[:10] + ");",
"    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10",
"    # ~23:1x; deletion-set EMPTY; delivery window = chain-order",
"    # splice AFTER the bm-c W239 five-face (freeze " + w239_freeze_sha[:10] + ") + W239",
"    # finalize product landed (n1_w239_results.json present, ledger",
"    # head " + str(w239_total) + " machine-read at freeze time); zero --no-verify;",
"    # the W240 seat MSG sits in " + seat_found + " at freeze",
"    # time, honest archived per S7 law);",
"    # band gate ADMIT results/_w240bma_20261014_probe_receipt.json: A = FIRST-CLEAN",
"    # past the prior-wave B tail AND a live SEED_REGISTRY point -- the arithmetic",
"    # continuation " + fmt(w239_a_tail + 1) + ".." + fmt(w239_a_tail + 2_000) + " is REFUSED at its own start by the",
"    # live seed 545_500 (refuser = a SEED POINT, not a prior-wave band -- W239 A/B",
"    # decoupled, exactly as the W239 seat leg4 projection anticipated); honest",
"    # forward walk hop 1 -> first-clean " + fmt(a_lo) + ".." + fmt(a_hi) + ", hops=1,",
"    # non-rotational r587 forward-monotone walk; A base >= prior-wave B",
"    # tail+1 (" + fmt(w239_b_tail) + "+1) machine-checkable -- A-hops-prior-B",
"    # staircase GE face (E36 card, probe receipt leg1 A_semantics",
"    # machine-read, never transcribed);",
"    # B = FIRST-CLEAN arithmetic continuation of the prior-wave B tail",
"    # (" + fmt(w239_b_tail + 1) + ".." + fmt(w239_b_tail + 200) + " CLEAN on the",
"    # registered universe, hops=0, B_hop_chain empty + B_no_ownA_jump=true -- B",
"    # lands OUTSIDE the own-A seed-hopped window " + fmt(a_lo) + ".." + fmt(a_hi) + ":",
"    # seed-decoupled A/B gap face inherited from W239; B base == prior-wave B",
"    # tail+1 (" + fmt(w239_b_tail) + "+1) machine-checkable;",
"    # single-window derive (r812 merged the gate legs INTO the",
"    # pre-seat probe; dual-window parity N/A honest); scan face =",
"    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1",
"    # used-seed band + probe cluster 95_000..95_003 + cross-face",
"    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/",
"    # N2-W15 probe points.",
"    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):",
"    # " + gate_lines[0] + ";",
"    # " + gate_lines[1] + ".",
"    # W241+ projection (gate-derived pre-seat probe leg4, pre-W240",
"    # universe): A naive first-clean " + rec["legs"]["leg4"]["W241p_A_naive"] + " CLEAN (hops=0, zero live",
"    # seed refusers) / B naive first-clean " + rec["legs"]["leg4"]["W241p_B_naive"] + " CLEAN (hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " -- B lands OUTSIDE",
"    # the naive A window, seed-gap face inherited); W241 freezer MUST",
"    # re-derive on the post-W240 universe AND reserve the own-wave A window",
"    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1",
"    # equality -- W240 A/B stay decoupled); never transcribe r587.",
])
pf_row = (f'{ROW_I}240: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), '
          f'"b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'
          + PF_EOL + f'{ROWC_I}"engine_owner": "bm-a"}},' + PF_EOL)
# belt-and-braces: display form must equal the canonical W-family text
assert pf_row.split(PF_EOL)[0].strip() == \
    f'240: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), "b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'

old_pf = must(pf_t, (w239_own_line + PF_EOL + '}'
                     + PF_EOL + '# v1 + ext(wave-1) in-use bands'), 1, "pf_close")
new_pf = (w239_own_line + PF_EOL
          + pf_comment + PF_EOL + pf_row
          + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands')
pf_t2 = pf_t.replace(old_pf, new_pf, 1)

# ---------- n1 cfg entry (programmatic quote wrapping, r761 law) ----------
fin_face = (f"W1..W239 finalize ALL LANDED (W239 finalize product present at splice, "
            f"net chain head {w239_total} machine-read, merged pool K={w239_merged_n} "
            f"machine-read) -- ZERO in-flight upstream seats at splice time, clean precondition "
            f"(twenty-ninth consecutive fully-clean freeze window); downstream W241 seat NOT yet "
            f"published at this freeze window (never-dry queue-depth supply = next window standing "
            f"agenda: W241 pre-seat probe + seat publish per the W241+ projection pre-disclosed in the "
            f"W240 prereg sec.5 + probe receipt leg4)")
cfg_lines = [
 f'{CFG_I}240: {{"batch": "PERPETUAL-N1-W240",',
 f'{PRE_KEY_I}"prereg": ("research/PERPETUAL_N1_W240_PREREG.md (wave-level frozen "',
]
PRE = [
 "pre-run; design = frozen v1 null calibration verbatim, ",
 "new seed bands only; TWO HUNDRED AND FORTIETH ENGINE-OWNED WAVE ",
 f"BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate), ",
 "own-series continuation per O-20260101-2355 sec.2 (first-free-",
 "number law after the REGISTERED W239 row five-face freeze (bm-c own seat executed at the r996-continuation window; engine self-burn 12/12; finalize one-pass, ledger 950,135 / K=523,720 machine-read), ",
 f"{w239_freeze_sha[:10]} (prereg {w239_prereg_sha[:10]}), SINGLE STATE zero seat gap W2..W239 all ",
 "registered; " + fin_face + "; ",
 "seat published=reserved ",
 "MSG-20261014-1325-bma-w240-seat PUSHED to origin " + SEAT_ORIGIN + " ",
 "BEFORE this freeze per r565 early-visibility law (payload = ",
 "seat MSG + pre-seat probe script + probe receipt; per-wave prereg ",
 "r989 dead-session derive landed pre-freeze [estate absorbed by the r991 window] -- zero takeover face, bm-a own-seat ",
 "continuity, ",
 f"prereg {w240_prereg_sha[:10]} @ receipt {w240_receipt_sha[:10]}) -- this freeze splice editor derived from the committed W239 editor template in this same freeze window; ",
 "deletion-set EMPTY; delivery window = chain-order splice ",
 "after the W239 five-face + W239 finalize product landed ",
 "(executed in the bm-a loop freeze window ",
 "under the CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED ",
 "2026-10-10 ~23:1x); zero merge at freeze delivery, zero ",
 "--no-verify; single-window derive -- r812 merged the gate ",
 "legs INTO the pre-seat probe; parity N/A honest), ",
 "engine_owner=bm-a (bm-a OWN-SEAT face -- bm-a's ONE HUNDRED AND ",
 "TWENTY-THIRD owned claim per machine-derive (engine_owner==bm-a rows ",
 f"{len(bma_rows_live)} + candidate; probe receipt leg0 bma_ordinal=123 = seat-time pre-splice ",
 "live faces disclosed honest, live derive governs ",
 "r587/r359 -- zero takeover, own-seat continuity)), ",
 "wave 240: ",
 "A = FIRST-CLEAN past the prior-wave B tail AND a live SEED_REGISTRY ",
 "point (the arithmetic continuation ",
 f"{fmt(w239_a_tail + 1)}..{fmt(w239_a_tail + 2_000)} is REFUSED at its own start by the live seed 545_500 ",
 "-- refuser = a SEED POINT, not a prior-wave band (W239 A/B decoupled), ",
 "exactly as the W239 seat leg4 succession ",
 "projection notes anticipated; honest forward walk hop 1 -> ",
 f"{fmt(a_lo)}..{fmt(a_hi)} hops=1; A base >= prior-wave B tail+1 ",
 "machine-checkable = A-hops-prior-B staircase GE face, E36 card (probe ",
 "receipt leg1 machine-read relation_asserts); ",
 "non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN arithmetic ",
 "continuation of the prior-wave B tail (the continuation ",
 f"{fmt(w239_b_tail + 1)}..{fmt(w239_b_tail + 200)} is CLEAN on the registered universe ",
 "hops=0, B_hop_chain empty + B_no_ownA_jump=true -- B lands OUTSIDE the ",
 f"own-A seed-hopped window {fmt(a_lo)}..{fmt(a_hi)}; seed-decoupled A/B gap ",
 "face inherited from W239; B base == prior-wave B ",
 "tail+1 machine-checkable; cross-window convergence with the W239 seat leg4 succession projection ",
 "notes -- all MANDATORY notes honored (post-W239 universe ",
 "re-derive + live-trace re-read, no staircase-equality assumption); ADMIT receipt ",
 "results/_w240bma_20261014_probe_receipt.json + ",
 "seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a ",
 "ADMIT convention); W241+ projection per this window gate: ",
 f"A naive first-clean {rec['legs']['leg4']['W241p_A_naive']} CLEAN (hops=0, zero live seed refusers) / B naive first-clean ",
 f"{rec['legs']['leg4']['W241p_B_naive']} CLEAN (hops=0, lands OUTSIDE the naive A window -- seed-gap face ",
 "inherited); W241 freezer MUST re-derive on the post-W240 universe AND ",
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
 f'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W240 A: {fmt(a_lo)}..{fmt(a_hi)} (FIRST-CLEAN past prior-wave B tail AND live seed 545_500; arithmetic {fmt(w239_a_tail + 1)}..{fmt(w239_a_tail + 2_000)} REFUSED at own start by the live SEED_REGISTRY point 545_500 -- refuser = seed point not band, W239 A/B decoupled; hops=1; A-hops-prior-B staircase GE face, E36 card; relation machine-read per probe receipt)',
 f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W240 B: {fmt(b_lo)}..{fmt(b_hi)} (FIRST-CLEAN arithmetic continuation of the prior-wave B tail; {fmt(w239_b_tail + 1)}..{fmt(w239_b_tail + 200)} CLEAN hops=0, B_hop_chain empty + B_no_ownA_jump=true; B lands outside own-A; seed-decoupled A/B gap face inherited; B base == prior-B tail+1)',
 f'{MEM_I}"shard_subdir": "n1_w240", "out_name": "n1_w240_results.json",',
 f'{MEM_I}"engine_owner": "bm-a"}},',
]

cfg_block = EOL.join(cfg_lines)
old_cfg = must(n1_t, ('                       }' + EOL
                      + 'PREREG = WAVE_CONFIGS[2]["prereg"]'), 1, "n1_cfg_close")
new_cfg = (cfg_block + EOL
           + '                       }' + EOL
           + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
assert new_cfg.count('240: {"batch": "PERPETUAL-N1-W240"') == 1
n1_t2 = n1_t.replace(old_cfg, new_cfg, 1)

# ---------- n1 materializer block ----------
hdr = [
 "    # --- W240 materializer face (bm-a loop five-face freeze splice --",
 "    #     OWN-SEAT face under CEO fill-order standing 2026-10-08 ~23:5x",
 "    #     + RE-ISSUE 2026-10-10 ~23:1x + O-20260909-2334-bm-b sec.1-2",
 "    #     local-full-use + O-20260924-1730 claim-and-start same-round law):",
 "    #     bm-a's one hundred and twenty-third owned per machine-derive (engine_owner==bm-a",
 f"    #     rows {len(bma_rows_live)} + candidate; own-seat face: seat published=reserved by bm-a itself",
 "    #     (r986 MSG-20261014-1325-bma-w240-seat @ origin 39a30b6a0; probe leg0",
 "    #     bma_ordinal=123 = seat-time pre-splice faces;",
 "    #     live derive at freeze governs);",
 "    #     wave 240 = first free number after the",
 "    #     REGISTERED W239 row (five-face freeze " + w239_freeze_sha[:10] + "; bm-c own seat executed at",
 "    #     the r996-continuation window; engine",
 "    #     self-burn 12/12 + finalize one-pass ledger 950,135 / K=523,720",
 "    #     -- SINGLE STATE zero seat gap (W2..W239 all registered). Seat",
 "    #     published=reserved MSG-20261014-1325-bma-w240-seat pushed",
 "    #     to origin " + SEAT_ORIGIN + " BEFORE this freeze, r565 law (payload =",
 "    #     seat MSG + pre-seat probe script + probe receipt; per-wave prereg",
 f"    #     r989 dead-session derive landed pre-freeze commit {w240_prereg_sha[:10]} [estate absorbed by the",
 "    #     r991 window]; this freeze splice editor",
 "    #     derived from the committed W239 editor template in this same freeze",
 "    #     window (E63 heal lineage: arith_a240/arith_b240 define+assert consistent);",
 "    #     deletion-set EMPTY; delivery window",
 "    #     = chain-order splice after the W239 five-face + W239 finalize",
 "    #     product landed; zero --no-verify; the W240 seat MSG sits in",
 "    #     " + seat_found + " at freeze time, honest archived",
 "    #     per S7 law).",
 "    #     TWO HUNDRED AND FORTIETH engine wave BY",
 f"    #     MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate; gate",
 "    #     leg0 machine output governs per r359 law).",
 f"    #     {fin_face}; the finalize merge loop",
 "    #     still derives the wave set from registry keys at run",
 "    #     time, FAIL-CLOSED r307 always on. ADMIT receipt",
 "    #     results/_w240bma_20261014_probe_receipt.json;",
 "    #     seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a",
 f"    #     ADMIT convention upgrade): {gate_lines[0]}; {gate_lines[1]};",
 "    #     banned gate ADMIT 0 (re-run at freeze window);",
 "    #     not a re-pick (R250: W240 bands were never assigned).",
 "    _set_wave(240)",
 "    try:",
 '        assert WAVE_CONFIGS[239]["a_seed_base"] == pf.N1_BANDS[239]["a"][0], \\',
 '            "W240 upstream W239 mirror drift (a)"',
 "        assert WAVE_CONFIGS[239][\"b_exit_seed_base\"] == \\",
 '            pf.N1_BANDS[239]["b_exit"][0], "W240 upstream W239 mirror drift (b)"',
 "        assert WAVE_CONFIGS[239].get(\"engine_owner\") == \\",
 '            pf.N1_BANDS[239].get("engine_owner") == "bm-c", \\',
 '            "W240 upstream W239 engine_owner mirror drift (law-mirror parity; bm-c upstream seat face)"',
 "        w239_a = {A_SEED_BASE + j for j in range(A_N)}",
 "        w239_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
 '        assert not (w239_a & w239_b), "W240 A/B band overlap"',
 "        assert not (w239_a & reg_ints) and not (w239_b & reg_ints), \\",
 '            "W240 hits SEED_REGISTRY"',
 '        for nm, band in (("A", w239_a), ("B", w239_b)):',
 '            assert not (band & v1_a) and not (band & v1_b), f"W240 {nm} hits v1"',
 '            assert not (band & w1_a) and not (band & w1_b), f"W240 {nm} hits W1"',
 '            assert not (band & probes), f"W240 {nm} hits probe seeds"',
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
tail = [
 "        # prior-wave disjointness W2..W239 (single state: all",
 "        # registered, dynamic registry derive, r511 law)",
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 240):",
 '            assert not (w239_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
 "                                 for j in range(A_N)}), f\"W240 A hits W{wprev}\"",
 '            assert not (w239_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
 "                                  for j in range(B_N)}), f\"W240 B hits W{wprev}\"",
 "        n3r1_used240 = set(range(70_000, 70_006))",
 "        assert not (w239_a & n3r1_used240) and not (w239_b & n3r1_used240), \\",
 '            "W240 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
 "        assert not (w239_a & lfc_actual12) and not (w239_b & lfc_actual12), \\",
 '            "W240 bands must clear the lfc actual draw range"',
 "        assert not (w239_a & options_actual12) and \\",
 "            not (w239_b & options_actual12), \\",
 '            "W240 bands must clear the options_wave2 actual draw range"',
  "        # band facts (law sec.4 W240 row): A = FIRST-CLEAN past the",
  "        # prior-wave B tail AND a live SEED_REGISTRY point (the arithmetic",
 f"        # continuation {fmt(w239_a_tail + 1)}..{fmt(w239_a_tail + 2_000)} is REFUSED at its own",
  "        # start by the live seed 545_500 -- refuser = a SEED POINT, not a",
  "        # prior-wave band (W239 A/B decoupled), exactly as the W239 seat",
  "        # leg4 succession projection notes anticipated; honest forward walk",
 f"        # hop 1 -> {fmt(a_lo)}..{fmt(a_hi)} hops=1, non-rotational",
  "        # r587 forward-monotone walk; A base >= prior-wave B tail+1",
 f"        # ({fmt(w239_b_tail)}+1) machine-checkable -- A-hops-prior-B staircase",
  "        # GE face, E36 card);",
  "        # B = FIRST-CLEAN arithmetic continuation of the prior-wave B",
 f"        # tail ({fmt(w239_b_tail + 1)}..{fmt(w239_b_tail + 200)} CLEAN on the registered",
  "        # universe, hops=0, B_hop_chain empty + B_no_ownA_jump=true -- B",
  "        # lands OUTSIDE the own-A seed-hopped window",
 f"        # {fmt(a_lo)}..{fmt(a_hi)}; seed-decoupled A/B gap face inherited from W239;",
  "        # B base == prior-wave B tail+1",
 f"        # ({fmt(w239_b_tail)}+1) machine-checkable; cross-window convergence with",
  "        # the W239 seat leg4 succession projection notes -- all",
  "        # MANDATORY notes honored (post-W239 universe re-derive +",
  "        # live-trace re-read, no staircase-equality assumption);",
 f'        assert WAVE_CONFIGS[240]["a_seed_base"] == {a_lo} >= {w239_b_tail} + 1, (',
 '            "W240 A must be the first-clean window past the prior-wave B "',
 '            "tail AND the live seed point 545_500 (arithmetic continuation "',
 '            "REFUSED at its own start by the live SEED_REGISTRY point -- the "',
 '            "refuser is a seed point, NOT a prior-wave band, W239 A/B "',
 '            "decoupled, exactly as the W239 seat leg4 succession projection "',
 '            "notes anticipated; honest forward walk hops=1; A base >= "',
 '            "prior-wave B tail+1 machine-checkable = A-hops-prior-B "',
 '            "staircase GE face, E36 card")',
 f"        arith_a240 = set(range({a_lo}, {a_hi + 1}))",
 "        assert not (arith_a240 & reg_ints), \\",
 '            "W240 A window must be CLEAN (first-clean ADMIT face past prior-wave B + live seed)"',
 f'        assert WAVE_CONFIGS[240]["b_exit_seed_base"] == {b_lo} == {w239_b_tail} + 1, (',
 '            "W240 B keeps the staircase base (FIRST-CLEAN arithmetic "',
 '            "continuation of the prior-wave B tail, hops=0, B_hop_chain "',
 '            "empty + B_no_ownA_jump=true -- B lands outside the own-A "',
 '            "seed-hopped window; seed-decoupled A/B gap face inherited; "',
 '            "B base == prior-wave B tail+1 machine-checkable)")',
 f"        arith_b240 = set(range({b_lo}, {b_hi + 1}))",
 "        assert not (arith_b240 & reg_ints), \\",
 '            "W240 B window must be CLEAN (first-clean ADMIT face, staircase-base continuation)"',
 "        assert not (arith_b240 & arith_a240), \\",
 '            "W240 A/B same-freeze mutual exclusion (seed-decoupled gap face inherited: B below own A)"',
 "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W240-SHARD-0\",",
 '                                          "n1w240-0of12"), "W240 entry identity"',
 '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W240-SHARD-11",',
 '                                           "n1w240-11of12")',
 "        assert SHARD_DIR.endswith(\"n1_w240\") and OUT.endswith(",
 '            "n1_w240_results.json"), "W240 path drift"',
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 240):",
 "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(",
 "                PATHS.results_dir, \"p2cal_ext\",",
 "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\",
 '                f"W240 shard dir collides with W{wprev}"',
 "        # W240 finalize cumulative deps: W17..W239 outputs ALL PRESENT",
 f"        # (landed net chain head {w239_total} machine-read at freeze time)",
 "        # -- ZERO in-flight upstream seats at splice, clean precondition",
 "        # freeze window; the finalize merge loop derives the wave",
 "        # set from registry keys at run time and stays",
 "        # FAIL-CLOSED, r307 two-state law).",
 "        for _depw in range(17, 240):",
 "            assert os.path.exists(os.path.join(",
 "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\",
 '                f"W240 finalize cumulative dep (W{_depw} output) missing"',
 "        # finalize wave-set derivation face (r511 derive law): every",
 "        # registered wave below 240 composes; wave 15 excluded by",
 "        # design; SINGLE STATE (W2..W239 all registered -- no",
 "        # two-state seat disclosure needed at this freeze).",
 "        assert sorted(w for w in WAVE_CONFIGS if w < 240) == \\",
 "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\",
 "            [w for w in range(16, 240)], \\",
 '            "W240 prior-wave set must derive from registry keys (no 15; " \\',
 '            "W2..W239 registered single state)"',
 "        assert os.path.exists(os.path.join(",
 '            PATHS.root, "research", "PERPETUAL_N1_W240_PREREG.md")), \\',
 '            "W240 per-wave prereg missing (materializer requirement)"',
 "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"",
 "    finally:",
 "        _set_wave(2)",
]
block = EOL.join(hdr) + EOL + par_sec + EOL.join(w232_leg) + EOL + EOL.join(w233_leg) + EOL + EOL.join(w234_leg) + EOL + EOL.join(w235_leg) + EOL + EOL.join(w236_leg) + EOL + EOL.join(w237_leg) + EOL + EOL.join(w238_leg) + EOL + EOL.join(w239_leg) + EOL + EOL.join(tail) + EOL
# family #6 atomic triple gate (carried forward): the new
# block's LHS w<240> / RHS range(16,240)+range(17,240) / comment below-240 MUST move together.
assert block.count("if w < 240)") == 3, f"family-6 triple: w<240 count {block.count('if w < 240)')} != 3"
assert block.count("if w < 239)") == 0, "family-6 triple: stale w<239 leaked into the W240 block"
assert block.count("range(16, 240)") == 1 and block.count("range(17, 240)") == 1, "family-6 triple: RHS ranges wrong"
assert block.count("registered wave below 240 composes") == 1, "family-6 triple: comment face wrong"
old_blk_anchor = must(n1_t2, "    # --- T-141 s2 lane face", 1, "t141_marker")
n1_t3 = n1_t2.replace(old_blk_anchor, block + old_blk_anchor, 1)

# ---------- n1 print line ----------
pr = [
 '          "+ W240 materializer face [same guard set, dep=W17..W239 "',
 f'          "outputs ALL PRESENT (landed net chain head {w239_total} = W239 bm-c finalize one-pass, K={w239_merged_n} merged pool) -- ZERO "',
 '          "in-flight upstream seats at splice, clean precondition, TWO HUNDRED AND FORTIETH "',
 f'          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} "',
 '          "+ candidate) bm-a\'s one hundred and twenty-third owned claim per "',
 '          "machine-derive (engine_owner==bm-a rows 122 + candidate; OWN-SEAT face: seat published by bm-a itself, "',
 '          "probe leg0 bma_ordinal=123 = seat-time pre-splice faces disclosed honest, "',
 '          "live derive at freeze governs), "',
 '          "A=FIRST-CLEAN past prior-wave B tail AND live seed point (seed-hop face, "',
 '          "hops=1, refuser=live SEED_REGISTRY point 545_500 NOT a prior-wave band, W239 A/B decoupled, staircase GE face, E36 card) "',
 '          "+ B=staircase-base continuation "',
 '          "(prior-B-tail+1 EXACT, hops=0, B_hop_chain empty + B_no_ownA_jump=true, seed-decoupled A/B gap face inherited), chain-order splice from the "',
 '          "committed ADMIT receipt + seed_admit_gate rc0 both bands FREE "',
 '          "(O-20261010-1945-bm-a ADMIT convention), "',
 '          "ADMIT receipt "',
 '          "results/_w240bma_20261014_probe_receipt.json, law sec.4 W240 row, "',
 '          "bm-a loop CEO fill-order RE-ISSUE 23:1x] "',
]

old_pr = must(n1_t3, '          "+ T-141 s2 ', 1, "print_t141")
n1_t4 = n1_t3.replace(old_pr, EOL.join(pr) + EOL + old_pr, 1)

# ---------- post-edit count gates ----------
assert n1_t4.count('"batch": "PERPETUAL-N1-W240"') == 1
assert n1_t4.count("# --- W240 materializer face") == 1     # block header
assert n1_t4.count('"+ W240 materializer face') == 1        # print fragment
assert n1_t4.count('240: {"batch": "PERPETUAL-N1-W240"') == 1
assert pf_t2.count(ROW_I + '240: {"a"') == 1
assert pf_t2.count('"engine_owner": "bm-a"},' + PF_EOL + '}') == 1
assert n1_t4.count('    # --- T-141 s2 lane face') == 1
assert n1_t4.count('"PERPETUAL-N1-W240-SHARD-0"') == 1
assert n1_t4.count(f'assert pf.N1_BANDS[239] == {{"a": ({fmt(pf_mod.N1_BANDS[239]["a"][0])}, {fmt(pf_mod.N1_BANDS[239]["a"][1])}),') == 1
# the W239 leg lives ONLY in the new W240 block (1); the W238 leg lives in the
# kept W239 block + the new W240 block (2); the W237 leg lives in kept W238 +
# W239 + new W240 (3); the W236 leg in kept W237+W238+W239+new (4); the W235
# leg in kept W236+W237+W238+W239+new (5)
assert n1_t4.count(f'assert pf.N1_BANDS[238] == {{"a": ({fmt(pf_mod.N1_BANDS[238]["a"][0])}, {fmt(pf_mod.N1_BANDS[238]["a"][1])}),') == 2
assert n1_t4.count(f'assert pf.N1_BANDS[237] == {{"a": ({fmt(pf_mod.N1_BANDS[237]["a"][0])}, {fmt(pf_mod.N1_BANDS[237]["a"][1])}),') == 3
assert n1_t4.count(f'assert pf.N1_BANDS[236] == {{"a": ({fmt(pf_mod.N1_BANDS[236]["a"][0])}, {fmt(pf_mod.N1_BANDS[236]["a"][1])}),') == 4
assert n1_t4.count(f'assert pf.N1_BANDS[235] == {{"a": ({fmt(pf_mod.N1_BANDS[235]["a"][0])}, {fmt(pf_mod.N1_BANDS[235]["a"][1])}),') == 5
for _b in range(209, 241):
    assert n1_t4.count(f"    # --- W{_b} materializer face") == 1, f"W{_b} block kept-count drift"
# no start>end malformed windows in inserted prose (r773 law)
for seg in (pf_comment, cfg_block, block, EOL.join(pr)):
    for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", seg):
        lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
        assert lo <= hi, f"malformed window {m.group(0)} in inserted prose"

# ---------- write + AST gate ----------
open(PF, "wb").write(pf_t2.encode("utf-8"))
open(N1, "wb").write(n1_t4.encode("utf-8"))
import py_compile
py_compile.compile(PF, doraise=True)
py_compile.compile(N1, doraise=True)

# ---------- receipt ----------
receipt = {
  "machine": "bm-a", "wave": 240,
  "phase": "five-face freeze chain-order splice (bm-a own-seat freeze window, upstream ALL LANDED clean precondition)",
  "origin_base": omain,
  "pf_sha16_pre": hashlib.sha256(pf_b).hexdigest()[:16],
  "n1_sha16_pre": hashlib.sha256(n1_b).hexdigest()[:16],
  "pf_sha16_post": hashlib.sha256(pf_t2.encode("utf-8")).hexdigest()[:16],
  "n1_sha16_post": hashlib.sha256(n1_t4.encode("utf-8")).hexdigest()[:16],
  "bands": {"A": A, "B": B, "a_lo": a_lo, "a_hi": a_hi, "b_lo": b_lo, "b_hi": b_hi},
  "admit_receipt": "results/_w240bma_20261014_probe_receipt.json",
  "seed_admit_gate": gate_lines,
  "banned_gate": "ADMIT rc0 (re-run at freeze window)",
  "band_semantics": {"A": "FIRST-CLEAN past prior-wave B tail AND live SEED_REGISTRY point (hops=1 seed-hop face; refuser = seed point 545_500 NOT a prior-wave band, W239 A/B decoupled; staircase GE face)",
                     "B": "FIRST-CLEAN arithmetic continuation of prior-wave B tail (hops=0, B_hop_chain empty + B_no_ownA_jump=true; B base == prior-B tail+1 EXACT; seed-decoupled A/B gap face inherited)"},
  "w239_upstream": {"freeze_sha": w239_freeze_sha, "prereg_sha": w239_prereg_sha,
                    "ledger_total": w239_total, "merged_n": w239_merged_n,
                    "engine_owner": "bm-c (upstream seat honored)",
                    "repair_chain_note": "W239 bm-c own-wave closeout r996-continuation window (five-face splice c85e806c9 + engine self-burn 12/12 + finalize one-pass ledger 950,135 / K=523,720)"},
  "own_seat_face": {"seat_msg": SEAT_MSG, "seat_origin": SEAT_ORIGIN,
                    "inherited": False,
                    "note": "seat published=reserved by bm-a itself (MSG-20261014-1325-bma-w240-seat pushed to origin 39a30b6a0 r986 BEFORE this freeze per r565 law, queue-depth supply depth-2, freeze waited-upstream on the W239 finalize); zero takeover -- wave 240 engine_owner=bm-a, bm-a's 123rd own wave per live derive (probe leg0 bma_ordinal=123 = seat-time pre-splice faces disclosed honest, live derive governs r587/r359; freeze-time live face owner rows 229 + candidate = 230th EXACT)"},
  "transitive_deps": {f"W{w}": f"results/perpetual_faces/n1_w{w}_results.json present (belt-and-braces gate)" for w in (238, 237, 236, 235, 234, 233, 232, 231)},
  "downstream_seat": "W241 seat NOT yet published at this freeze window (never-dry queue-depth supply = next window standing agenda: W241 pre-seat probe + seat publish per the W241+ projection pre-disclosed in W240 prereg sec.5 + probe receipt leg4)",
  "seat": seat_found + " (origin " + SEAT_ORIGIN + ")",
  "prereg_bundle": {"prereg_sha": w240_prereg_sha, "probe_receipt_sha": w240_receipt_sha,
                    "note": "prereg derived+committed by the dead r989 session (48 SUB pairs from the frozen W239 tpl 97a7ff0e6; estate absorbed by THIS r991 window per the bm-a absorb precedent lineage; zero takeover; freeze-time live derive bma rows 122 + candidate 123rd EXACT per r587/r359); preflight contributed by the dead r990-yield retreat window (results/_w240bma_preflight.py ALL GREEN, estate absorbed in commit 2c0bf15b9); splice editor derived from the committed W239 editor template by count-asserted ordered transform in this same freeze window (E63 heal lineage: arith_a240/arith_b240 define+assert consistent); upstream W239 already landed (clean-precondition twenty-ninth consecutive window); zero transcription"},
  "ordinal_faces": {"owner_rows_live": len(owner_rows_live), "bma_rows_live": len(bma_rows_live),
                    "bmc_rows_live": len(bmc_rows_live),
                    "engine_owned_ordinal": len(owner_rows_live) + 1,
                    "bma_own_ordinal": len(bma_rows_live) + 1,
                    "probe_receipt_bma_ordinal_face": 123,
                    "note": "post-W239 registration: bm-a rows 122 + candidate = 123rd owned (live derive at freeze time governs per r587/r359; probe leg0 bma_ordinal=123 = seat-time faces -- zero takeover, own-seat continuity)"},
  "parity_section": {"source": "OWN W239 block physical bytes (bm-c splice generation r996-continuation window, structure known exactly)",
                    "bytes": len(par_sec),
                    "row_asserts": par_sec.count("assert pf.N1_BANDS["),
                    "note": "full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W231 legs -> W240 block = 98 rows ending at W239 (estate 90 + fresh W232 leg + W233 leg + W234 leg + W235 leg + W236 leg + W237 leg + W238 leg + W239 leg); disclosed: (a) inherited W213 leg error-string face (\"registered W212 row parity drift\") preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact); (b) band-set variable one-behind naming face (w239_a holds wave-240 bands) = lineage mechanical aging face, zero functional impact"},
  "family6_triple_gate": {"absorbed": True,
                          "note": "W239 editor family-6 gate carried forward: new block LHS w<240 x3 / RHS range(16,240)+range(17,240) / comment below-240 count-asserted ATOMICALLY before splice; W239 block's own w<239 face = legitimate prior-wave boundary (not stale); E63 heal lineage applied (arith define/assert consistent)"},
  "eol": {"n1_crlf": EOL == "\r\n", "pf_crlf": PF_EOL == "\r\n"},
  "liveness_anchors": {f"w{_b}_block_kept": 1 for _b in range(209, 241)},
}

open(RECEIPT_OUT, "w", encoding="utf-8").write(json.dumps(receipt, indent=1))
print(json.dumps({k: receipt[k] for k in
      ("phase", "origin_base", "pf_sha16_post", "n1_sha16_post", "bands",
       "w239_upstream", "own_seat_face")}, indent=1))
print("SPLICE OK -- py_compile both green; NEXT: selftest (default wave, r522 law) -> pathspec commit+push -> engine self-ignite W240 burn (12 shards) -> PRE-FINALIZE six-gate (standing law) -> finalize one-pass")
