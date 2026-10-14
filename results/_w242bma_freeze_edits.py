# -*- coding: utf-8 -*-
# 2026-10-14 20:3x bm-a r998 freeze window (upstream W1..W241 ALL LANDED, clean
# precondition -- W241 finalize one-pass bm-c r1005/r1006 estate window 19:5x,
# ledger head 954,535 / K=528,120 machine-read): W242 five-face freeze splice
# editor -- bm-a OWN-SEAT face (seat MSG-20261014-1814-bma-w242-seat
# published=reserved by bm-a itself @ origin 138a94745 r995, pre-seat probe
# ADMIT receipt results/_w242bma_20261014_probe_receipt.json same payload;
# the W242 freeze's waits-upstream on the W241 finalize is DISARMED by the W241
# finalize landing 19:5x -- zero takeover, zero DRAFT marker; per-wave prereg
# PERPETUAL_N1_W242_PREREG.md derived+landed by THIS r998 window commit
# 702db9b3e, machine-SUB from frozen W241 tpl a9ab3b51d).
# Lineage: _w241bmc_freeze_edits.py template (proven live-fire freeze, bm-c
# r1004 window; engine self-burn 12/12 + finalize one-pass verified bm-c
# r1005/r1006) + r787 preflight law + r609 origin-verbatim base + r761
# programmatic quote wrapping + r909 physical-byte anchors + r838 per-file
# EOL detection + family #6 LHS/RHS/comment ATOMIC TRIPLE (the new block's
# w<242>/range(16,242)/range(17,242)/below-242 quadruple is count-asserted
# atomically; the W241 block's own w<241 face is legitimate prior-wave
# boundary, not stale) + E63 heal lineage (arith_a242/arith_b242
# define+assert consistent).
# Zero hardcoded upstream band values: ALL W241 facts machine-derived from the
# LIVE pf import at freeze time (the registered W241 row -- bm-c seat honored),
# cross-checked against the committed ADMIT receipt
# (results/_w242bma_20261014_probe_receipt.json) which was derived on the
# post-W241-DECLARED universe. If the LIVE W241 bands differ from the declared
# face, the continuation asserts fail LOUD (fail-closed).
# STRUCTURAL CHOICE (vs the W241 editor): the parity estate (W138..W206
# full-span 69 rows, r858 absorb generation, + W211..W231 legs) is extracted
# from the OWN W241 block physical bytes -- structure known exactly (bm-c's
# splice generation, committed) -- the W241 block's own W232..W240 legs are
# excluded from the estate path and fresh W232..W241 legs are appended for the
# W242 block parity (100 rows: estate 90 ending W231 + W232 leg + W233 leg +
# W234 leg + W235 leg + W236 leg + W237 leg + W238 leg + W239 leg + W240 leg +
# W241 leg). Extraction self-asserts the 90-row cut regardless.
# Disclosed: (a) the inherited W213 leg inside the estate carries a cosmetic
# error-string face ("registered W212 row parity drift") from the r912 editor
# generation -- physical bytes preserved verbatim per extraction law, zero
# functional impact (assert target [213] is correct); (b) the band-set
# variable naming one-behind face (w241_a holds wave-242 bands) is the
# lineage's mechanical aging face -- the W242 block follows the same
# mechanical pattern as its ancestors, zero functional impact.
# Own bundle hashes (prereg/probe receipt) derived via pickaxe, never transcribed.
# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.
import json, hashlib, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PF = os.path.join(REPO, "scripts", "perpetual_faces.py")
N1 = os.path.join(REPO, "scripts", "perpetual_faces_n1.py")
RECEIPT_IN = os.path.join(REPO, "results", "_w242bma_20261014_probe_receipt.json")
RECEIPT_OUT = os.path.join(REPO, "results", "_w242bma_freeze_receipt.json")
SEAT_MSG = "MSG-20261014-1814-bma-w242-seat.md"
SEAT_ORIGIN = "138a94745"
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

# ---------- gate 0.5: W241 five-face landed + W241 finalize product present ----------
# (chain-order precondition; W240/W239/W238/W237/W236/W235/W234/W233/W232 finalize are
# transitive deps of the W242 freeze and are belt-and-braces checked here + enforced
# by the block's cumulative-deps assert range(17, 242) at selftest time)
W241 = dict(pf_mod.N1_BANDS.get(241) or {})
assert W241.get("engine_owner") == "bm-c", \
    f"W241 row not landed as declared (bm-c seat owner expected): {W241} -- five-face freeze missing;" \
    " if an unexpected face exists the freeze window MUST re-derive this editor honestly"
w241_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w241_results.json")
assert os.path.exists(w241_out_path), "W241 finalize product missing (n1_w241_results.json) -- chain dep not met"
for _w in (240, 239, 238, 237, 236, 235, 234, 233, 232):
    assert os.path.exists(os.path.join(REPO, "results", "perpetual_faces", f"n1_w{_w}_results.json")), \
        f"W{_w} finalize product missing (transitive chain dep) -- abort"
w241_out = json.load(open(w241_out_path, encoding="utf-8"))
w241_led = (w241_out.get("science_gates") or {}).get("ledger") or {}
w241_total = w241_led.get("total")
w241_merged_n = None
try:
    w241_merged_n = w241_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
assert w241_total == 954_535 and w241_merged_n == 528_120, \
    f"W241 finalize anchors drift at freeze time: total={w241_total} merged={w241_merged_n} (expect 954,535 / 528,120)"
# freeze shas machine-derived (pickaxe), never transcribed
r = git("log", "--format=%H", "-S", '241: {"a"', "--", "scripts/perpetual_faces.py")
w241_freeze_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W241_PREREG.md")
w241_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W242_PREREG.md")
w242_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
assert os.path.exists(os.path.join(REPO, "research", "PERPETUAL_N1_W242_PREREG.md")), \
    "W242 per-wave prereg missing on disk -- chain face incomplete, abort (r998 derive landed pre-freeze expected)"
with open(os.path.join(REPO, "research", "PERPETUAL_N1_W242_PREREG.md"), encoding="utf-8") as _fh:
    _pre_head = _fh.read(2000)
assert "DRAFT-NOT-FROZEN" not in _pre_head, "W242 prereg still DRAFT -- abort (freeze commit pending face)"
# live ordinal derive (r359 law: gate machine output governs; the pre-seat probe
# receipt leg0 face owner_rows=230 / bma_rows=123 / bma_ordinal=124
# = seat-time PRE-W241-splice live faces; live derive at freeze time:
# W241 splice LANDED (finalize adds no registry rows) -> owner rows 231 + candidate = 232nd EXACT; bm-a rows 123 +
# candidate = 124th EXACT -- bm-a own-seat continuity face, zero takeover)
owner_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner")]
bma_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-a"]
bmc_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
assert len(owner_rows_live) == 231 and len(bma_rows_live) == 123 and len(bmc_rows_live) == 67, \
    f"leg0 ordinal drift at freeze time: owner={len(owner_rows_live)} bma={len(bma_rows_live)} bmc={len(bmc_rows_live)} (expect 231/123/67 PRE-splice post-W241 registration; this candidate = bm-a's 124th own wave per the same live-derive law, r587/r359)"
print(f"gate0.5 OK: W241 landed (freeze {w241_freeze_sha[:10]}, owner=bm-c seat honored, zero takeover face), "
      f"W241+W240+W239+W238+W237+W236+W235+W234+W233+W232 finalize products present "
      f"(W241 ledger head {w241_total}, merged n={w241_merged_n}); owner rows {len(owner_rows_live)} + candidate, "
      f"bm-a rows {len(bma_rows_live)} + candidate (124th own wave per live derive; "
      f"probe receipt leg0 bma_ordinal=124 = seat-time pre-splice faces disclosed honest)")

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
assert (a_lo, a_hi) == (549_501, 551_500) and (b_lo, b_hi) == (541_204, 541_403), \
    f"W242 band drift vs probe ADMIT: {(a_lo, a_hi)} {(b_lo, b_hi)}"
w241_b_tail = W241["b_exit"][1]      # registered W241 row b_exit hi (pf import, live)
w241_a_tail = W241["a"][1]           # registered W241 row A hi (pf import, live)
# W242 FACE (seed-decoupled A-continuation, probe receipt leg1 relation_asserts):
# A keeps the A-continuation base (prior-wave A tail+1 EXACT -- the naive
# arithmetic continuation is CLEAN at its own start, hops=0, A_hop_chain
# empty, A_clean_at_naive_start=true -- third consecutive seed-gap face per
# the W241 seat leg4 anticipation confirmed live); B keeps the staircase
# base (prior-wave B tail+1 EXACT, hops=0, fourth consecutive decoupled face);
# A sits far above the B staircase (seed-decoupled A/B gap);
# machine-derived from the LIVE registered row, never transcribed.
assert w241_a_tail + 1 == a_lo, "A continuation base relation broken (A == prior-wave A tail+1 EXACT)"
assert w241_b_tail + 1 == b_lo, "B staircase base relation broken (B == prior-wave B tail+1 EXACT)"
assert a_lo > w241_b_tail + 1, "seed-decoupled A-continuation face violated: A base must sit ABOVE prior-B tail+1 (seed-gap)"
assert b_hi < a_lo, "seed-decoupled A/B gap face violated: B window must sit entirely below own-A"
assert W241["b_exit"][1] < W241["a"][0], \
    "upstream W241 row in-wave decoupled relation broken (registered W241 B window must sit below own W241 A window)"
assert leg1.get("hops_A") == 0 and leg1.get("hops_B") == 0, "hop-count drift vs probe receipt leg1 (both bands naive hops=0)"
assert leg1.get("A_hop_chain") == [] and (
    leg1.get("A_clean_at_naive_start") is True
    or (leg1.get("relation_asserts") or {}).get("A_clean_at_naive_start") is True
), \
    "A hop-chain face drift (fc_a == fc_a_naive, hops=0, A_clean_at_naive_start=true -- naive continuation CLEAN at own start)"
assert leg1.get("B_hop_chain") == [] and leg1.get("B_naive_hops") == 0, "B hop-chain face drift (fc_b == fc_b_naive, hops=0)"
ra = leg1.get("relation_asserts") or {}
assert ra.get("A_clean_at_naive_start") and ra.get("A_base_ge_priorB_tail_plus1") \
    and ra.get("B_base_eq_priorB_tail_plus1") and ra.get("AB_mutual_exclusion") \
    and ra.get("B_no_ownA_jump"), \
    f"probe receipt leg1 relation_asserts face drift: {ra}"
assert [w241_a_tail + 1, w241_a_tail + 2_000] == leg1["ARITH_A"], \
    f"A-continuation start drift vs probe receipt leg1 ARITH_A: {[w241_a_tail + 1, w241_a_tail + 2_000]} != {leg1['ARITH_A']}"
assert [w241_b_tail + 1, w241_b_tail + 200] == leg1["ARITH_B"], \
    f"B-continuation drift vs probe receipt leg1 ARITH_B: {[w241_b_tail + 1, w241_b_tail + 200]} != {leg1['ARITH_B']}"

# own bundle shas via pickaxe (self-referencing commit facts, zero transcription)
r = git("log", "--diff-filter=A", "--format=%H", "--", "results/_w242bma_20261014_probe_receipt.json")
w242_receipt_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
# seat MSG honest location (inbox or processed; S7 archive law)
seat_found = None
for _p in ("fleet/inbox", "fleet/inbox/processed"):
    if os.path.exists(os.path.join(REPO, _p, SEAT_MSG)):
        seat_found = _p + "/" + SEAT_MSG
        break
assert seat_found, f"W242 seat MSG missing from both inbox paths: {SEAT_MSG}"

# ---------- re-run discipline gates at freeze window (banned + seed_admit) ----------
g = subprocess.run([PY, os.path.join(REPO, "Tools", "banned_direction_gate.py"),
                    "--prereg", "research/PERPETUAL_N1_W242_PREREG.md"],
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
# STRUCTURAL CHOICE: extract the estate from the OWN W241 block (bytes known
# exactly: full-span estate W138..W206 69 rows + own W211..W231 legs = 90
# rows) -- the W241 block is bm-c's own splice generation (r1004 window
# editor), structure known. The W241 block span ends where the T-141
# s2 lane face marker begins.
a21 = '    # --- W241 materializer face'
a_t141 = '    # --- T-141 s2 lane face'
w241_start = n1_t.find(a21); t141_pos = n1_t.find(a_t141)
assert w241_start > 0 and t141_pos > w241_start, \
    "W241 materializer block face not found (W241 freeze not landed? header-text drift -> honest re-derive required)"
blk = n1_t[w241_start:t141_pos]
m_first_row = re.search(r"assert pf\.N1_BANDS\[", blk)
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state", blk)
assert m_first_row and m_disj and m_disj.start() > m_first_row.start(), \
    "parity span markers not found in W241 block"
_row_ls = blk.rfind(EOL, 0, m_first_row.start()) + len(EOL)
par_full = blk[_row_ls:m_disj.start()]
m232 = re.search(r" *assert pf\.N1_BANDS\[232\] ==", par_full)
assert m232, "upstream W232 row leg not found inside W241 parity span"
par_sec = par_full[:m232.start()]
assert par_sec.endswith(EOL), "estate segment must end with EOL"
_estate_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", par_sec)
assert par_sec.count("assert pf.N1_BANDS[") == 90 \
    and [int(w) for w in _estate_ws[:69]] == list(range(138, 207)) \
    and [int(_estate_ws[69 + i]) for i in range(11)] == [211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221] \
    and [int(_estate_ws[80 + i]) for i in range(9)] == [222, 223, 224, 225, 226, 227, 228, 229, 230] \
    and int(_estate_ws[89]) == 231, \
    f"estate segment not W138..W206 full-span 69 rows + W211..W230 legs + W231 leg: n={par_sec.count('assert pf.N1_BANDS[')} range={(_estate_ws[:2], _estate_ws[-4:])}"
assert par_full.count("assert pf.N1_BANDS[") == 99, \
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 99 (69 estate + W211..W230 legs + W231 leg + W232 leg + W233 leg + W234 leg + W235 leg + W236 leg + W237 leg + W238 leg + W239 leg + W240 leg)"

# ---------- indent extraction (physical, not assumed; per-file EOL) ----------
def line_indent(t, needle, eol):
    i = t.find(needle)
    assert i >= 0, f"indent needle not found: {needle[:40]}"
    ls = t.rfind(eol, 0, i) + len(eol)
    line = t[ls:t.find(eol, ls)]
    return line[:len(line) - len(line.lstrip(" "))]

CFG_I  = line_indent(n1_t, '241: {"batch"', EOL)
PRE_KEY_I = line_indent(n1_t, '"prereg": ("research/PERPETUAL_N1_W241_PREREG.md', EOL)
PRE_I  = line_indent(n1_t, '"pre-run; design = frozen v1 null calibration verbatim, "', EOL)
_c241 = n1_t.find('241: {"batch"')
assert _c241 > 0, "W241 cfg entry not found (W241 freeze not landed?)"
_mpos = n1_t.find('"a_seed_base"', _c241)
assert _mpos > 0 and n1_t.find('"shard_subdir"', _c241) > _mpos, "W241 cfg a_seed_base line not found"
MEM_I  = line_indent(n1_t, '"a_seed_base": ' + str(W241["a"][0]), EOL) \
    if n1_t.find('"a_seed_base": ' + str(W241["a"][0]), _c241) > 0 \
    else line_indent(n1_t, '"a_seed_base": ' + fmt(W241["a"][0]), EOL)
ROW_I  = line_indent(pf_t,  '241: {"a"', PF_EOL)

# ---------- W241 row owner line (physical bytes; comment text is own generation) ----------
w241_row_start = pf_t.find('    241: {"a"')
assert w241_row_start > 0, "W241 row literal not found in pf source"
_own_ls = pf_t.find(PF_EOL, w241_row_start) + len(PF_EOL)
_own_le = pf_t.find(PF_EOL, _own_ls)
w241_own_line = pf_t[_own_ls:_own_le]
assert '"engine_owner": "bm-c"' in w241_own_line, \
    f"W241 owner line unexpected bytes: {w241_own_line!r}"
ROWC_I = w241_own_line[:len(w241_own_line) - len(w241_own_line.lstrip(" "))]

# ---------- pf comment + row ----------
pf_comment = PF_EOL.join([
"    # W242 (bm-a loop five-face freeze splice -- OWN-SEAT face, seat",
"    # MSG-20261014-1814-bma-w242-seat published=reserved by bm-a itself @",
"    # origin " + SEAT_ORIGIN + " (r995, queue-depth supply depth-2 at publish, zero takeover); prereg + ADMIT probe",
"    # receipt frozen commit " + w242_prereg_sha[:10] + " (prereg research/PERPETUAL_N1_W242_PREREG.md",
"    # r998 same-window machine-SUB derive landed pre-freeze, probe",
"    # results/_w242bma_20261014_probe_receipt.json @ " + w242_receipt_sha[:10] + ");",
"    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10",
"    # ~23:1x; deletion-set EMPTY; delivery window = chain-order",
"    # splice AFTER the bm-c W241 five-face (freeze " + w241_freeze_sha[:10] + ") + W241",
"    # finalize product landed (n1_w241_results.json present, ledger",
"    # head " + str(w241_total) + " machine-read at freeze time); zero --no-verify;",
"    # the W242 seat MSG sits in " + seat_found + " at freeze",
"    # time, honest archived per S7 law);",
"    # band gate ADMIT results/_w242bma_20261014_probe_receipt.json: A = FIRST-CLEAN",
"    # arithmetic continuation of the prior-wave A tail (" + fmt(w241_a_tail + 1) + ".." + fmt(w241_a_tail + 2_000) + " CLEAN",
"    # at naive start on the registered universe, hops=0, A_hop_chain empty +",
"    # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,",
"    # third consecutive seed-gap face per the W241 seat leg4 anticipation",
"    # confirmed live; A base == prior-wave A tail+1 (" + fmt(w241_a_tail) + "+1) machine-checkable;",
"    # B = FIRST-CLEAN arithmetic continuation of the prior-wave B tail",
"    # (" + fmt(w241_b_tail + 1) + ".." + fmt(w241_b_tail + 200) + " CLEAN on the",
"    # registered universe, hops=0, B_hop_chain empty + B_no_ownA_jump=true -- B",
"    # lands OUTSIDE the own-A window " + fmt(a_lo) + ".." + fmt(a_hi) + ":",
"    # seed-decoupled A/B gap face fourth consecutive; B base == prior-wave B",
"    # tail+1 (" + fmt(w241_b_tail) + "+1) machine-checkable;",
"    # single-window derive (r812 merged the gate legs INTO the",
"    # pre-seat probe; dual-window parity N/A honest); scan face =",
"    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1",
"    # used-seed band + probe cluster 95_000..95_003 + cross-face",
"    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/",
"    # N2-W15 probe points.",
"    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):",
"    # " + gate_lines[0] + ";",
"    # " + gate_lines[1] + ".",
"    # W243+ projection (gate-derived pre-seat probe leg4, pre-W242",
"    # universe): A naive first-clean " + rec["legs"]["leg4"]["W243p_A_naive"] + " CLEAN (hops=0, zero live",
"    # seed refusers) / B naive first-clean " + rec["legs"]["leg4"]["W243p_B_naive"] + " hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " (live refusal",
"    # inside 541_404..541_500 -- SEED_REGISTRY point 541_500 perpetual_n2_w15_gen, honest forward walk first-clean",
"    # " + rec["legs"]["leg4"]["W243p_B_first_clean"] + " -- B lands OUTSIDE",
"    # the naive A window, seed-gap face inherited); W243 freezer MUST",
"    # re-derive on the post-W242 universe AND reserve the own-wave A window",
"    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1",
"    # equality -- W242 A/B stay decoupled); never transcribe r587.",
])
pf_row = (f'{ROW_I}242: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), '
          f'"b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'
          + PF_EOL + f'{ROWC_I}"engine_owner": "bm-a"}},' + PF_EOL)
# belt-and-braces: display form must equal the canonical W-family text
assert pf_row.split(PF_EOL)[0].strip() == \
    f'242: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), "b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'

old_pf = must(pf_t, (w241_own_line + PF_EOL + '}'
                     + PF_EOL + '# v1 + ext(wave-1) in-use bands'), 1, "pf_close")
new_pf = (w241_own_line + PF_EOL
          + pf_comment + PF_EOL + pf_row
          + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands')
pf_t2 = pf_t.replace(old_pf, new_pf, 1)

# ---------- n1 cfg entry (programmatic quote wrapping, r761 law) ----------
fin_face = (f"W1..W241 finalize ALL LANDED (W241 finalize product present at splice, "
            f"net chain head {w241_total} machine-read, merged pool K={w241_merged_n} "
            f"machine-read) -- ZERO in-flight upstream seats at splice time, clean precondition "
            f"(thirty-first consecutive fully-clean freeze window); downstream W243 seat NOT YET "
            f"PUBLISHED at this freeze window (the next freezer must seat-first publish per "
            f"O-20261010-2350 sec.2 queue-depth supply; the W243 freezer MUST re-derive live on "
            f"the post-W242 universe + reserve the own-wave A window when deriving B per the "
            f"W242 seat leg4 mandate, never transcribe r587)")
cfg_lines = [
 f'{CFG_I}242: {{"batch": "PERPETUAL-N1-W242",',
 f'{PRE_KEY_I}"prereg": ("research/PERPETUAL_N1_W242_PREREG.md (wave-level frozen "',
]
PRE = [
 "pre-run; design = frozen v1 null calibration verbatim, ",
 "new seed bands only; TWO HUNDRED AND FORTY-SECOND ENGINE-OWNED WAVE ",
 f"BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate), ",
 "own-series continuation per O-20260101-2355 sec.2 (first-free-",
 "number law after the REGISTERED W241 row five-face freeze (bm-c own seat executed at the bm-c r1004 window; engine self-burn 12/12; finalize one-pass, ledger 954,535 / K=528,120 machine-read), ",
 f"{w241_freeze_sha[:10]} (prereg {w241_prereg_sha[:10]}), SINGLE STATE zero seat gap W2..W241 all ",
 "registered; " + fin_face + "; ",
 "seat published=reserved ",
 "MSG-20261014-1814-bma-w242-seat PUSHED to origin " + SEAT_ORIGIN + " ",
 "BEFORE this freeze per r565 early-visibility law (payload = ",
 "seat MSG + pre-seat probe script + probe receipt; per-wave prereg ",
 "r998 same-window machine-SUB derive landed pre-freeze -- zero takeover face, bm-a own-seat ",
 "continuity, ",
 f"prereg {w242_prereg_sha[:10]} @ receipt {w242_receipt_sha[:10]}) -- this freeze splice editor derived from the committed W241 editor template in this same freeze window; ",
 "deletion-set EMPTY; delivery window = chain-order splice ",
 "after the W241 five-face + W241 finalize product landed ",
 "(executed in the bm-a loop freeze window ",
 "under the CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED ",
 "2026-10-10 ~23:1x); zero merge at freeze delivery, zero ",
 "--no-verify; single-window derive -- r812 merged the gate ",
 "legs INTO the pre-seat probe; parity N/A honest), ",
 "engine_owner=bm-a (bm-a OWN-SEAT face -- bm-a's ONE HUNDRED AND TWENTY-FOURTH owned claim per machine-derive (engine_owner==bm-a rows ",
 f"{len(bma_rows_live)} + candidate; probe receipt leg0 bma_ordinal=124 = seat-time pre-splice ",
 "live faces disclosed honest, live derive governs ",
 "r587/r359 -- zero takeover, own-seat continuity)), ",
 "wave 242: ",
 "A = FIRST-CLEAN arithmetic continuation of the prior-wave A tail (the continuation ",
 f"{fmt(w241_a_tail + 1)}..{fmt(w241_a_tail + 2_000)} is CLEAN at its own start ",
 "-- hops=0, A_hop_chain empty + A_clean_at_naive_start=true, seed-decoupled ",
 "A-continuation face, third consecutive seed-gap face exactly as the W241 seat leg4 ",
 "succession projection notes anticipated; A base == prior-wave A tail+1 (",
 f"{fmt(w241_a_tail)}+1) machine-checkable; ",
 "non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN arithmetic ",
 "continuation of the prior-wave B tail (the continuation ",
 f"{fmt(w241_b_tail + 1)}..{fmt(w241_b_tail + 200)} is CLEAN on the registered universe ",
 "hops=0, B_hop_chain empty + B_no_ownA_jump=true -- B lands OUTSIDE the ",
 f"own-A window {fmt(a_lo)}..{fmt(a_hi)}; seed-decoupled A/B gap ",
 "face fourth consecutive; B base == prior-wave B ",
 "tail+1 machine-checkable; cross-window convergence with the W241 seat leg4 succession projection ",
 "notes -- all MANDATORY notes honored (post-W241 universe ",
 "re-derive + live-trace re-read, no staircase-equality assumption); ADMIT receipt ",
 "results/_w242bma_20261014_probe_receipt.json + ",
 "seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a ",
 "ADMIT convention); W243+ projection per this window gate: ",
 f"A naive first-clean {rec['legs']['leg4']['W243p_A_naive']} CLEAN (hops=0, zero live seed refusers) / B naive first-clean ",
 f"{rec['legs']['leg4']['W243p_B_naive']} hops=1 (live refusal inside 541_404..541_500 -- SEED_REGISTRY point 541_500 perpetual_n2_w15_gen, first-clean {rec['legs']['leg4']['W243p_B_first_clean']} -- lands OUTSIDE the naive A window -- seed-gap face ",
 "inherited); W243 freezer MUST re-derive on the post-W242 universe AND ",
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
 f'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W242 A: {fmt(a_lo)}..{fmt(a_hi)} (FIRST-CLEAN arithmetic continuation of the prior-wave A tail; {fmt(w241_a_tail + 1)}..{fmt(w241_a_tail + 2_000)} CLEAN at naive start hops=0, A_hop_chain empty + A_clean_at_naive_start=true; seed-decoupled A-continuation face third consecutive seed-gap face; A base == prior-A tail+1)',
 f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W242 B: {fmt(b_lo)}..{fmt(b_hi)} (FIRST-CLEAN arithmetic continuation of the prior-wave B tail; {fmt(w241_b_tail + 1)}..{fmt(w241_b_tail + 200)} CLEAN hops=0, B_hop_chain empty + B_no_ownA_jump=true; B lands outside own-A; seed-decoupled A/B gap face fourth consecutive; B base == prior-B tail+1)',
 f'{MEM_I}"shard_subdir": "n1_w242", "out_name": "n1_w242_results.json",',
 f'{MEM_I}"engine_owner": "bm-a"}},',
]

cfg_block = EOL.join(cfg_lines)
old_cfg = must(n1_t, ('                       }' + EOL
                      + 'PREREG = WAVE_CONFIGS[2]["prereg"]'), 1, "n1_cfg_close")
new_cfg = (cfg_block + EOL
           + '                       }' + EOL
           + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
assert new_cfg.count('242: {"batch": "PERPETUAL-N1-W242"') == 1
n1_t2 = n1_t.replace(old_cfg, new_cfg, 1)

# ---------- n1 materializer block ----------
hdr = [
 "    # --- W242 materializer face (bm-a loop five-face freeze splice --",
 "    #     OWN-SEAT face under CEO fill-order standing 2026-10-08 ~23:5x",
 "    #     + RE-ISSUE 2026-10-10 ~23:1x + O-20260909-2334 local-full-use",
 "    #     + O-20260924-1730 claim-and-start same-round law):",
 "    #     bm-a's one hundred and twenty-fourth owned per machine-derive (engine_owner==bm-a",
 f"    #     rows {len(bma_rows_live)} + candidate; own-seat face: seat published=reserved by bm-a itself",
 "    #     (r995 MSG-20261014-1814-bma-w242-seat @ origin 138a94745; probe leg0",
 "    #     bma_ordinal=124 = seat-time pre-splice faces;",
 "    #     live derive at freeze governs);",
 "    #     wave 242 = first free number after the",
 "    #     REGISTERED W241 row (five-face freeze " + w241_freeze_sha[:10] + "; bm-c own seat executed at",
 "    #     the bm-c r1004 window; engine",
 "    #     self-burn 12/12 + finalize one-pass ledger 954,535 / K=528,120",
 "    #     -- SINGLE STATE zero seat gap (W2..W241 all registered). Seat",
 "    #     published=reserved MSG-20261014-1814-bma-w242-seat pushed",
 "    #     to origin " + SEAT_ORIGIN + " BEFORE this freeze, r565 law (payload =",
 "    #     seat MSG + pre-seat probe script + probe receipt; per-wave prereg",
 f"    #     r998 same-window derive landed pre-freeze commit {w242_prereg_sha[:10]}; this freeze splice editor",
 "    #     derived from the committed W241 editor template in this same freeze",
 "    #     window (E63 heal lineage: arith_a242/arith_b242 define+assert consistent);",
 "    #     deletion-set EMPTY; delivery window",
 "    #     = chain-order splice after the W241 five-face + W241 finalize",
 "    #     product landed; zero --no-verify; the W242 seat MSG sits in",
 "    #     " + seat_found + " at freeze time, honest archived",
 "    #     per S7 law).",
 "    #     TWO HUNDRED AND FORTY-SECOND engine wave BY",
 f"    #     MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate; gate",
 "    #     leg0 machine output governs per r359 law).",
 f"    #     {fin_face}; the finalize merge loop",
 "    #     still derives the wave set from registry keys at run",
 "    #     time, FAIL-CLOSED r307 always on. ADMIT receipt",
 "    #     results/_w242bma_20261014_probe_receipt.json;",
 "    #     seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a",
 f"    #     ADMIT convention upgrade): {gate_lines[0]}; {gate_lines[1]};",
 "    #     banned gate ADMIT 0 (re-run at freeze window);",
 "    #     not a re-pick (R250: W242 bands were never assigned).",
 "    _set_wave(242)",
 "    try:",
 '        assert WAVE_CONFIGS[241]["a_seed_base"] == pf.N1_BANDS[241]["a"][0], \\',
 '            "W242 upstream W241 mirror drift (a)"',
 "        assert WAVE_CONFIGS[241][\"b_exit_seed_base\"] == \\",
 '            pf.N1_BANDS[241]["b_exit"][0], "W242 upstream W241 mirror drift (b)"',
 "        assert WAVE_CONFIGS[241].get(\"engine_owner\") == \\",
 '            pf.N1_BANDS[241].get("engine_owner") == "bm-c", \\',
 '            "W242 upstream W241 engine_owner mirror drift (law-mirror parity; bm-c upstream seat face)"',
 "        w241_a = {A_SEED_BASE + j for j in range(A_N)}",
 "        w241_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
 '        assert not (w241_a & w241_b), "W242 A/B band overlap"',
 "        assert not (w241_a & reg_ints) and not (w241_b & reg_ints), \\",
 '            "W242 hits SEED_REGISTRY"',
 '        for nm, band in (("A", w241_a), ("B", w241_b)):',
 '            assert not (band & v1_a) and not (band & v1_b), f"W242 {nm} hits v1"',
 '            assert not (band & w1_a) and not (band & w1_b), f"W242 {nm} hits W1"',
 '            assert not (band & probes), f"W242 {nm} hits probe seeds"',
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
w241_leg = [
 f'        assert pf.N1_BANDS[241] == {{"a": ({fmt(pf_mod.N1_BANDS[241]["a"][0])}, {fmt(pf_mod.N1_BANDS[241]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[241]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[241]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\',
'            "registered W241 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]
tail = [
 "        # prior-wave disjointness W2..W241 (single state: all",
 "        # registered, dynamic registry derive, r511 law)",
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 242):",
 '            assert not (w241_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
 "                                 for j in range(A_N)}), f\"W242 A hits W{wprev}\"",
 '            assert not (w241_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
 "                                  for j in range(B_N)}), f\"W242 B hits W{wprev}\"",
 "        n3r1_used242 = set(range(70_000, 70_006))",
 "        assert not (w241_a & n3r1_used242) and not (w241_b & n3r1_used242), \\",
 '            "W242 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
 "        assert not (w241_a & lfc_actual12) and not (w241_b & lfc_actual12), \\",
 '            "W242 bands must clear the lfc actual draw range"',
 "        assert not (w241_a & options_actual12) and \\",
 "            not (w241_b & options_actual12), \\",
 '            "W242 bands must clear the options_wave2 actual draw range"',
  "        # band facts (law sec.4 W242 row): A = FIRST-CLEAN arithmetic",
  "        # continuation of the prior-wave A tail",
 f"        # ({fmt(w241_a_tail + 1)}..{fmt(w241_a_tail + 2_000)} CLEAN at naive start on the",
  "        # registered universe, hops=0, A_hop_chain empty +",
  "        # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,",
  "        # third consecutive seed-gap face, exactly as the W241 seat leg4",
  "        # succession projection notes anticipated; A base == prior-wave A",
 f"        # tail+1 ({fmt(w241_a_tail)}+1) machine-checkable;",
  "        # B = FIRST-CLEAN arithmetic continuation of the prior-wave B",
 f"        # tail ({fmt(w241_b_tail + 1)}..{fmt(w241_b_tail + 200)} CLEAN on the registered",
  "        # universe, hops=0, B_hop_chain empty + B_no_ownA_jump=true -- B",
  "        # lands OUTSIDE the own-A window",
 f"        # {fmt(a_lo)}..{fmt(a_hi)}; seed-decoupled A/B gap face fourth consecutive;",
  "        # B base == prior-wave B tail+1",
 f"        # ({fmt(w241_b_tail)}+1) machine-checkable; cross-window convergence with",
  "        # the W241 seat leg4 succession projection notes -- all",
  "        # MANDATORY notes honored (post-W241 universe re-derive +",
  "        # live-trace re-read, no staircase-equality assumption);",
 f'        assert WAVE_CONFIGS[242]["a_seed_base"] == {a_lo} == {w241_a_tail} + 1, (',
 '            "W242 A must be the first-clean arithmetic continuation of the "',
 '            "prior-wave A tail (hops=0, A_hop_chain empty + A_clean_at_naive_start=true -- "',
 '            "seed-decoupled A-continuation face, third consecutive seed-gap face, "',
 '            "exactly as the W241 seat leg4 succession projection notes "',
 '            "anticipated; A base == prior-wave A tail+1 machine-checkable)")',
 f"        arith_a242 = set(range({a_lo}, {a_hi + 1}))",
 "        assert not (arith_a242 & reg_ints), \\",
 '            "W242 A window must be CLEAN (first-clean ADMIT face, A-continuation)"',
 f'        assert WAVE_CONFIGS[242]["b_exit_seed_base"] == {b_lo} == {w241_b_tail} + 1, (',
 '            "W242 B keeps the staircase base (FIRST-CLEAN arithmetic "',
 '            "continuation of the prior-wave B tail, hops=0, B_hop_chain "',
 '            "empty + B_no_ownA_jump=true -- B lands outside the own-A "',
 '            "window; seed-decoupled A/B gap face fourth consecutive; "',
 '            "B base == prior-wave B tail+1 machine-checkable)")',
 f"        arith_b242 = set(range({b_lo}, {b_hi + 1}))",
 "        assert not (arith_b242 & reg_ints), \\",
 '            "W242 B window must be CLEAN (first-clean ADMIT face, staircase-base continuation)"',
 "        assert not (arith_b242 & arith_a242), \\",
 '            "W242 A/B same-freeze mutual exclusion (seed-decoupled gap face inherited: B below own A)"',
 "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W242-SHARD-0\",",
 '                                          "n1w242-0of12"), "W242 entry identity"',
 '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W242-SHARD-11",',
 '                                           "n1w242-11of12")',
 "        assert SHARD_DIR.endswith(\"n1_w242\") and OUT.endswith(",
 '            "n1_w242_results.json"), "W242 path drift"',
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 242):",
 "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(",
 "                PATHS.results_dir, \"p2cal_ext\",",
 "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\",
 '                f"W242 shard dir collides with W{wprev}"',
 "        # W242 finalize cumulative deps: W17..W241 outputs ALL PRESENT",
 f"        # (landed net chain head {w241_total} machine-read at freeze time)",
 "        # -- ZERO in-flight upstream seats at splice, clean precondition",
 "        # freeze window; the finalize merge loop derives the wave",
 "        # set from registry keys at run time and stays",
 "        # FAIL-CLOSED, r307 two-state law).",
 "        for _depw in range(17, 242):",
 "            assert os.path.exists(os.path.join(",
 "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\",
 '                f"W242 finalize cumulative dep (W{_depw} output) missing"',
 "        # finalize wave-set derivation face (r511 derive law): every",
 "        # registered wave below 242 composes; wave 15 excluded by",
 "        # design; SINGLE STATE (W2..W241 all registered -- no",
 "        # two-state seat disclosure needed at this freeze).",
 "        assert sorted(w for w in WAVE_CONFIGS if w < 242) == \\",
 "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\",
 "            [w for w in range(16, 242)], \\",
 '            "W242 prior-wave set must derive from registry keys (no 15; " \\',
 '            "W2..W241 registered single state)"',
 "        assert os.path.exists(os.path.join(",
 '            PATHS.root, "research", "PERPETUAL_N1_W242_PREREG.md")), \\',
 '            "W242 per-wave prereg missing (materializer requirement)"',
 "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"",
 "    finally:",
 "        _set_wave(2)",
]
block = EOL.join(hdr) + EOL + par_sec + EOL.join(w232_leg) + EOL + EOL.join(w233_leg) + EOL + EOL.join(w234_leg) + EOL + EOL.join(w235_leg) + EOL + EOL.join(w236_leg) + EOL + EOL.join(w237_leg) + EOL + EOL.join(w238_leg) + EOL + EOL.join(w239_leg) + EOL + EOL.join(w240_leg) + EOL + EOL.join(w241_leg) + EOL + EOL.join(tail) + EOL
# family #6 atomic triple gate (carried forward): the new
# block's LHS w<242> / RHS range(16,242)+range(17,242) / comment below-242 MUST move together.
assert block.count("if w < 242)") == 3, f"family-6 triple: w<242 count {block.count('if w < 242)')} != 3"
assert block.count("if w < 241)") == 0, "family-6 triple: stale w<241 leaked into the W242 block"
assert block.count("range(16, 242)") == 1 and block.count("range(17, 242)") == 1, "family-6 triple: RHS ranges wrong"
assert block.count("registered wave below 242 composes") == 1, "family-6 triple: comment face wrong"
old_blk_anchor = must(n1_t2, "    # --- T-141 s2 lane face", 1, "t141_marker")
n1_t3 = n1_t2.replace(old_blk_anchor, block + old_blk_anchor, 1)

# ---------- n1 print line ----------
pr = [
 '          "+ W242 materializer face [same guard set, dep=W17..W241 "',
 f'          "outputs ALL PRESENT (landed net chain head {w241_total} = W241 bm-c finalize one-pass, K={w241_merged_n} merged pool) -- ZERO "',
 '          "in-flight upstream seats at splice, clean precondition, TWO HUNDRED AND FORTY-SECOND "',
 f'          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} "',
 '          "+ candidate) bm-a\'s one hundred and twenty-fourth owned claim per "',
 '          "machine-derive (engine_owner==bm-a rows 123 + candidate; OWN-SEAT face: seat published by bm-a itself, "',
 '          "probe leg0 bma_ordinal=124 = seat-time pre-splice faces disclosed honest, "',
 '          "live derive at freeze governs), "',
 '          "A=FIRST-CLEAN arithmetic continuation of prior-wave A tail (A-continuation face, "',
 '          "hops=0, A_hop_chain empty + A_clean_at_naive_start=true, seed-decoupled third consecutive seed-gap face) "',
 '          "+ B=staircase-base continuation "',
 '          "(prior-B-tail+1 EXACT, hops=0, B_hop_chain empty + B_no_ownA_jump=true, seed-decoupled A/B gap face fourth consecutive), chain-order splice from the "',
 '          "committed ADMIT receipt + seed_admit_gate rc0 both bands FREE "',
 '          "(O-20261010-1945-bm-a ADMIT convention), "',
 '          "ADMIT receipt "',
 '          "results/_w242bma_20261014_probe_receipt.json, law sec.4 W242 row, "',
 '          "bm-a loop CEO fill-order RE-ISSUE 23:1x] "',
]

old_pr = must(n1_t3, '          "+ T-141 s2 ', 1, "print_t141")
n1_t4 = n1_t3.replace(old_pr, EOL.join(pr) + EOL + old_pr, 1)

# ---------- post-edit count gates ----------
assert n1_t4.count('"batch": "PERPETUAL-N1-W242"') == 1
assert n1_t4.count("# --- W242 materializer face") == 1     # block header
assert n1_t4.count('"+ W242 materializer face') == 1        # print fragment
assert n1_t4.count('242: {"batch": "PERPETUAL-N1-W242"') == 1
assert pf_t2.count(ROW_I + '242: {"a"') == 1
assert pf_t2.count('"engine_owner": "bm-a"},' + PF_EOL + '}') == 1
assert n1_t4.count('    # --- T-141 s2 lane face') == 1
assert n1_t4.count('"PERPETUAL-N1-W242-SHARD-0"') == 1
assert n1_t4.count(f'assert pf.N1_BANDS[241] == {{"a": ({fmt(pf_mod.N1_BANDS[241]["a"][0])}, {fmt(pf_mod.N1_BANDS[241]["a"][1])}),') == 1
# the W241 leg lives ONLY in the new W242 block (1); the W240 leg lives in the kept
# W241 block + the new W242 block (2); the W239 leg lives in kept W240 + W241 + new
# W242 (3); the W238 leg in kept W239+W240+W241+new (4); the W237 leg in kept
# W238..W241+new (5); the W236 leg in kept W237..W241+new (6); the W235 leg in
# kept W236..W241+new (7)
assert n1_t4.count(f'assert pf.N1_BANDS[240] == {{"a": ({fmt(pf_mod.N1_BANDS[240]["a"][0])}, {fmt(pf_mod.N1_BANDS[240]["a"][1])}),') == 2
assert n1_t4.count(f'assert pf.N1_BANDS[239] == {{"a": ({fmt(pf_mod.N1_BANDS[239]["a"][0])}, {fmt(pf_mod.N1_BANDS[239]["a"][1])}),') == 3
assert n1_t4.count(f'assert pf.N1_BANDS[238] == {{"a": ({fmt(pf_mod.N1_BANDS[238]["a"][0])}, {fmt(pf_mod.N1_BANDS[238]["a"][1])}),') == 4
assert n1_t4.count(f'assert pf.N1_BANDS[237] == {{"a": ({fmt(pf_mod.N1_BANDS[237]["a"][0])}, {fmt(pf_mod.N1_BANDS[237]["a"][1])}),') == 5
assert n1_t4.count(f'assert pf.N1_BANDS[236] == {{"a": ({fmt(pf_mod.N1_BANDS[236]["a"][0])}, {fmt(pf_mod.N1_BANDS[236]["a"][1])}),') == 6
assert n1_t4.count(f'assert pf.N1_BANDS[235] == {{"a": ({fmt(pf_mod.N1_BANDS[235]["a"][0])}, {fmt(pf_mod.N1_BANDS[235]["a"][1])}),') == 7
for _b in range(209, 243):
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
  "machine": "bm-a", "wave": 242,
  "phase": "five-face freeze chain-order splice (bm-a own-seat freeze window, upstream ALL LANDED clean precondition)",
  "origin_base": omain,
  "pf_sha16_pre": hashlib.sha256(pf_b).hexdigest()[:16],
  "n1_sha16_pre": hashlib.sha256(n1_b).hexdigest()[:16],
  "pf_sha16_post": hashlib.sha256(pf_t2.encode("utf-8")).hexdigest()[:16],
  "n1_sha16_post": hashlib.sha256(n1_t4.encode("utf-8")).hexdigest()[:16],
  "bands": {"A": A, "B": B, "a_lo": a_lo, "a_hi": a_hi, "b_lo": b_lo, "b_hi": b_hi},
  "admit_receipt": "results/_w242bma_20261014_probe_receipt.json",
  "seed_admit_gate": gate_lines,
  "banned_gate": "ADMIT rc0 (re-run at freeze window)",
  "band_semantics": {"A": "FIRST-CLEAN arithmetic continuation of prior-wave A tail (hops=0, A_hop_chain empty + A_clean_at_naive_start=true; seed-decoupled A-continuation face, third consecutive seed-gap face; A base == prior-A tail+1 EXACT)",
                     "B": "FIRST-CLEAN arithmetic continuation of prior-wave B tail (hops=0, B_hop_chain empty + B_no_ownA_jump=true; B base == prior-B tail+1 EXACT; seed-decoupled A/B gap face fourth consecutive)"},
  "w241_upstream": {"freeze_sha": w241_freeze_sha, "prereg_sha": w241_prereg_sha,
                    "ledger_total": w241_total, "merged_n": w241_merged_n,
                    "engine_owner": "bm-c (upstream seat honored)",
                    "repair_chain_note": "W241 bm-c own-wave closeout bm-c r1005/r1006 estate window (five-face splice 8e980ce3e + engine self-burn 12/12 + finalize one-pass ledger 954,535 / K=528,120)"},
  "own_seat_face": {"seat_msg": SEAT_MSG, "seat_origin": SEAT_ORIGIN,
                    "inherited": False,
                    "note": "seat published=reserved by bm-a itself (MSG-20261014-1814-bma-w242-seat pushed to origin 138a94745 r995 BEFORE this freeze per r565 law, queue-depth supply depth-2 at publish; the W242 freeze's waits-upstream on the W241 finalize DISARMED by the W241 finalize landing 19:5x); zero takeover -- wave 242 engine_owner=bm-a, bm-a's 124th own wave per live derive (probe leg0 bma_ordinal=124 = seat-time pre-splice faces disclosed honest, live derive governs r587/r359; freeze-time live face owner rows 231 + candidate = 232nd EXACT)"},
  "transitive_deps": {f"W{w}": f"results/perpetual_faces/n1_w{w}_results.json present (belt-and-braces gate)" for w in (240, 239, 238, 237, 236, 235, 234, 233, 232)},
  "downstream_seat": "W243 seat NOT YET PUBLISHED at this freeze window (next freezer must seat-first publish per O-20261010-2350 sec.2 queue-depth supply; the W243 freezer MUST re-derive live on the post-W242 universe + reserve the own-wave A window when deriving B per the W242 seat leg4 mandate, never transcribe r587 -- W243p face: A naive 551_501..553_500 CLEAN / B naive 541_404..541_603 hops=1 refused by SEED_REGISTRY 541_500, first-clean 541_501..541_700)",
  "seat": seat_found + " (origin " + SEAT_ORIGIN + ")",
  "prereg_bundle": {"prereg_sha": w242_prereg_sha, "probe_receipt_sha": w242_receipt_sha,
                    "note": "prereg derived+committed by THIS r998 window (machine-SUB from the frozen W241 tpl a9ab3b51d; facts live-derived ledger 954,535 / K=528,120; freeze-time live derive bma rows 123 + candidate 124th EXACT per r587/r359); splice editor derived from the committed W241 editor template by count-asserted ordered transform in this same freeze window (E63 heal lineage: arith_a242/arith_b242 define+assert consistent); upstream W241 already landed (clean-precondition thirty-first consecutive window); zero transcription"},
  "ordinal_faces": {"owner_rows_live": len(owner_rows_live), "bma_rows_live": len(bma_rows_live),
                    "bmc_rows_live": len(bmc_rows_live),
                    "engine_owned_ordinal": len(owner_rows_live) + 1,
                    "bma_own_ordinal": len(bma_rows_live) + 1,
                    "probe_receipt_bma_ordinal_face": 124,
                    "note": "post-W241 registration: bm-a rows 123 + candidate = 124th owned (live derive at freeze time governs per r587/r359; probe leg0 bma_ordinal=124 = seat-time faces -- zero takeover, own-seat continuity)"},
  "parity_section": {"source": "OWN W241 block physical bytes (bm-c splice generation r1004 window, structure known exactly)",
                    "bytes": len(par_sec),
                    "row_asserts": par_sec.count("assert pf.N1_BANDS["),
                    "note": "full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W231 legs -> W242 block = 100 rows ending at W241 (estate 90 + fresh W232 leg + W233 leg + W234 leg + W235 leg + W236 leg + W237 leg + W238 leg + W239 leg + W240 leg + W241 leg); disclosed: (a) inherited W213 leg error-string face (\"registered W212 row parity drift\") preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact); (b) W241 block's band-set variable one-behind naming face (w241_a holds wave-242 bands) = lineage mechanical aging face, zero functional impact"},
  "family6_triple_gate": {"absorbed": True,
                          "note": "W241 editor family-6 gate carried forward: new block LHS w<242 x3 / RHS range(16,242)+range(17,242) / comment below-242 count-asserted ATOMICALLY before splice; W241 block's own w<241 face = legitimate prior-wave boundary (not stale); E63 heal lineage applied (arith define/assert consistent)"},
  "eol": {"n1_crlf": EOL == "\r\n", "pf_crlf": PF_EOL == "\r\n"},
  "liveness_anchors": {f"w{_b}_block_kept": 1 for _b in range(209, 243)},
}

open(RECEIPT_OUT, "w", encoding="utf-8").write(json.dumps(receipt, indent=1))
print(json.dumps({k: receipt[k] for k in
      ("phase", "origin_base", "pf_sha16_post", "n1_sha16_post", "bands",
       "w241_upstream", "own_seat_face")}, indent=1))
print("SPLICE OK -- py_compile both green; NEXT: selftest (default wave, r522 law) -> pathspec commit+push -> engine self-ignite W242 burn (12 shards) -> PRE-FINALIZE six-gate (standing law) -> finalize one-pass")
