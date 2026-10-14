# -*- coding: utf-8 -*-
# 2026-10-15 06:1x bm-a r1007 freeze window (upstream W1..W243 ALL LANDED, clean
# precondition -- W243 finalize one-pass bm-a r1003 own-wave closeout 01:4x,
# ledger head 958,935 / K=532,520 machine-read): W244 five-face freeze splice
# editor -- bm-a OWN-SEAT face (seat MSG-20261015-0206-bma-w244-seat
# published=reserved by bm-a itself @ origin 08df387e0 r1004, pre-seat probe
# ADMIT receipt results/_w244bma_20261015_probe_receipt.json same payload;
# the W244 freeze's waits-upstream on the W243 finalize is DISARMED by the W243
# finalize landing 01:4x -- zero takeover, zero DRAFT marker; per-wave prereg
# PERPETUAL_N1_W244_PREREG.md derived by the absorbed r1005 window
# and landed by the r1006 commit 260ffd3f8, machine-SUB from frozen W244 tpl 70141bc22).
# Lineage: _w243bma_freeze_edits.py template (proven live-fire freeze, bm-a
# r1002 window; engine self-burn 12/12 + finalize one-pass verified r1003) +
# r787 preflight law + r609 origin-verbatim base + r761 programmatic quote
# wrapping + r909 physical-byte anchors + r838 per-file EOL detection +
# family #6 LHS/RHS/comment ATOMIC TRIPLE (the new block's w<244>/
# range(16,244)/range(17,244)/below-244 quadruple is count-asserted
# atomically; the W243 block's own w<243 face is legitimate prior-wave
# boundary, not stale) + E63 heal lineage (arith_a244/arith_b244
# define+assert consistent).
# NEW FACE vs the W243 editor (honest disclosure): the W244 B band returns
# to the CLEAN staircase base (hops=0 -- the naive continuation
# 541_701..541_900 is CLEAN on the registered universe; the prior-wave
# live-seed refusal chain is behind us) -- B base == prior-B-tail+1 EXACT
# in this face; relation asserts mirror the probe receipt leg1
# relation_asserts exactly (B_clean_at_naive_start +
# B_base_above_priorB_tail), and the staircase base is machine-asserted
# (B base == prior-wave B tail+1).
# Zero hardcoded upstream band values: ALL W243 facts machine-derived from the
# LIVE pf import at freeze time (the registered W243 row -- bm-a own seat
# honored), cross-checked against the committed ADMIT receipt
# (results/_w244bma_20261015_probe_receipt.json) which was derived on the
# post-W243-REGISTERED universe. If the LIVE W243 bands differ from the
# declared face, the continuation asserts fail LOUD (fail-closed).
# STRUCTURAL CHOICE (vs the W243 editor): the parity estate + the W232..W242
# fresh legs are BOTH extracted from the OWN W243 block physical bytes
# (bm-a r1002 splice generation, committed -- structure known exactly); the
# W244 block appends ONE fresh W243 leg (machine-derived from the live
# registered row) -> 102 parity rows (estate 90 ending W231 + W232..W242
# legs 11 + W243 leg 1). Extraction self-asserts the 90-row estate cut and
# the 11-leg segment regardless.
# Own bundle hashes (prereg/probe receipt) derived via pickaxe, never transcribed.
# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.
import json, hashlib, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PF = os.path.join(REPO, "scripts", "perpetual_faces.py")
N1 = os.path.join(REPO, "scripts", "perpetual_faces_n1.py")
RECEIPT_IN = os.path.join(REPO, "results", "_w244bma_20261015_probe_receipt.json")
RECEIPT_OUT = os.path.join(REPO, "results", "_w244bma_freeze_receipt.json")
SEAT_MSG = "MSG-20261015-0206-bma-w244-seat.md"
SEAT_ORIGIN = "08df387e0"
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

# ---------- gate 0.5: W243 five-face landed + W243 finalize product present ----------
# (chain-order precondition; W243/W241/W240/W239/W238/W237/W236/W235/W234/W233 finalize are
# transitive deps of the W244 freeze and are belt-and-braces checked here + enforced
# by the block's cumulative-deps assert range(17, 244) at selftest time)
W243 = dict(pf_mod.N1_BANDS.get(243) or {})
assert W243.get("engine_owner") == "bm-a", \
    f"W243 row not landed as declared (bm-a seat owner expected): {W243} -- five-face freeze missing;" \
    " if an unexpected face exists the freeze window MUST re-derive this editor honestly"
w243_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w243_results.json")
assert os.path.exists(w243_out_path), "W243 finalize product missing (n1_w243_results.json) -- chain dep not met"
for _w in (242, 241, 240, 239, 238, 237, 236, 235, 234, 233):
    assert os.path.exists(os.path.join(REPO, "results", "perpetual_faces", f"n1_w{_w}_results.json")), \
        f"W{_w} finalize product missing (transitive chain dep) -- abort"
w243_out = json.load(open(w243_out_path, encoding="utf-8"))
w243_led = (w243_out.get("science_gates") or {}).get("ledger") or {}
w243_total = w243_led.get("total")
w243_merged_n = None
try:
    w243_merged_n = w243_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
assert w243_total == 958_935 and w243_merged_n == 532_520, \
    f"W243 finalize anchors drift at freeze time: total={w243_total} merged={w243_merged_n} (expect 958,935 / 532,520)"
# freeze shas machine-derived (pickaxe), never transcribed
r = git("log", "--format=%H", "-S", '243: {"a"', "--", "scripts/perpetual_faces.py")
w243_freeze_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W243_PREREG.md")
w243_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W244_PREREG.md")
w244_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
assert os.path.exists(os.path.join(REPO, "research", "PERPETUAL_N1_W244_PREREG.md")), \
    "W244 per-wave prereg missing on disk -- chain face incomplete, abort (r1005 derive landed pre-freeze expected)"
with open(os.path.join(REPO, "research", "PERPETUAL_N1_W244_PREREG.md"), encoding="utf-8") as _fh:
    _pre_head = _fh.read(2000)
assert "DRAFT-NOT-FROZEN" not in _pre_head, "W244 prereg still DRAFT -- abort (freeze commit pending face)"
# live ordinal derive (r359 law: gate machine output governs; the pre-seat probe
# receipt leg0 face owner_rows=233 / bma_rows=125 / bma_ordinal=126
# = seat-time PRE-W244-splice live faces; live derive at freeze time:
# W243 splice LANDED (finalize adds no registry rows) -> owner rows 233 + candidate = 234th EXACT; bm-a rows 124 +
# candidate = 126th EXACT -- bm-a own-seat continuity face, zero takeover)
owner_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner")]
bma_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-a"]
bmc_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
assert len(owner_rows_live) == 233 and len(bma_rows_live) == 125 and len(bmc_rows_live) == 67, \
    f"leg0 ordinal drift at freeze time: owner={len(owner_rows_live)} bma={len(bma_rows_live)} bmc={len(bmc_rows_live)} (expect 233/125/67 PRE-splice post-W243 registration; this candidate = bm-a's 126th own wave per the same live-derive law, r587/r359)"
print(f"gate0.5 OK: W243 landed (freeze {w243_freeze_sha[:10]}, owner=bm-a seat honored, zero takeover face), "
      f"W243+W241+W240+W239+W238+W237+W236+W235+W234+W233+W232 finalize products present "
      f"(W243 ledger head {w243_total}, merged n={w243_merged_n}); owner rows {len(owner_rows_live)} + candidate, "
      f"bm-a rows {len(bma_rows_live)} + candidate (126th own wave per live derive; "
      f"probe receipt leg0 bma_ordinal=126 = seat-time pre-splice faces disclosed honest)")

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
assert (a_lo, a_hi) == (553_501, 555_500) and (b_lo, b_hi) == (541_701, 541_900), \
    f"W244 band drift vs probe ADMIT: {(a_lo, a_hi)} {(b_lo, b_hi)}"
w243_b_tail = W243["b_exit"][1]      # registered W243 row b_exit hi (pf import, live)
w243_a_tail = W243["a"][1]           # registered W243 row A hi (pf import, live)
# W244 FACE (probe receipt leg1 relation_asserts):
# A keeps the A-continuation base (prior-wave A tail+1 EXACT -- the naive
# arithmetic continuation is CLEAN at its own start, hops=0, A_hop_chain
# empty, A_clean_at_naive_start=true -- fifth consecutive seed-gap face per
# the W243 seat leg4 anticipation confirmed live); B returns to the CLEAN
# staircase base (prior-wave B tail+1 EXACT, hops=0, B_hop_chain empty,
# B_clean_at_naive_start=true -- the prior-wave live-seed refusal chain is
# behind us; gap face sixth consecutive); A sits far above the B staircase
# (seed-decoupled A/B gap); machine-derived from the LIVE registered row,
# never transcribed.
assert w243_a_tail + 1 == a_lo, "A continuation base relation broken (A == prior-wave A tail+1 EXACT)"
assert w243_b_tail + 1 == b_lo, "B staircase base relation broken (B == prior-wave B tail+1 EXACT)"
assert a_lo > w243_b_tail + 1, "seed-decoupled A-continuation face violated: A base must sit ABOVE prior-B tail+1 (seed-gap)"
assert b_hi < a_lo, "seed-decoupled A/B gap face violated: B window must sit entirely below own-A"
assert W243["b_exit"][1] < W243["a"][0], \
    "upstream W243 row in-wave decoupled relation broken (registered W243 B window must sit below own W243 A window)"
assert leg1.get("hops_A") == 0 and leg1.get("hops_B") == 0, "hop-count drift vs probe receipt leg1 (both bands naive hops=0)"
assert leg1.get("A_hop_chain") == [] and (
    leg1.get("A_clean_at_naive_start") is True
    or (leg1.get("relation_asserts") or {}).get("A_clean_at_naive_start") is True
), \
    "A hop-chain face drift (fc_a == fc_a_naive, hops=0, A_clean_at_naive_start=true -- naive continuation CLEAN at own start)"
assert leg1.get("B_hop_chain") == [] and leg1.get("B_naive_hops") == 0, "B hop-chain face drift (fc_b == fc_b_naive, hops=0, B_clean_at_naive_start=true)"
assert leg1.get("B_naive_first_clean") == [b_lo, b_hi], "B naive first-clean drift vs probe receipt leg1"
ra = leg1.get("relation_asserts") or {}
assert ra.get("A_clean_at_naive_start") and ra.get("A_base_ge_priorB_tail_plus1") \
    and ra.get("B_clean_at_naive_start") and ra.get("B_base_above_priorB_tail") \
    and ra.get("AB_mutual_exclusion") and ra.get("B_no_ownA_jump"), \
    f"probe receipt leg1 relation_asserts face drift: {ra}"
assert [w243_a_tail + 1, w243_a_tail + 2_000] == leg1["ARITH_A"], \
    f"A-continuation start drift vs probe receipt leg1 ARITH_A: {[w243_a_tail + 1, w243_a_tail + 2_000]} != {leg1['ARITH_A']}"
assert [w243_b_tail + 1, w243_b_tail + 200] == leg1["ARITH_B"], \
    f"B naive continuation drift vs probe receipt leg1 ARITH_B: {[w243_b_tail + 1, w243_b_tail + 200]} != {leg1['ARITH_B']}"

# own bundle shas via pickaxe (self-referencing commit facts, zero transcription)
r = git("log", "--diff-filter=A", "--format=%H", "--", "results/_w244bma_20261015_probe_receipt.json")
w244_receipt_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
# seat MSG honest location (inbox or processed; S7 archive law)
seat_found = None
for _p in ("fleet/inbox", "fleet/inbox/processed"):
    if os.path.exists(os.path.join(REPO, _p, SEAT_MSG)):
        seat_found = _p + "/" + SEAT_MSG
        break
assert seat_found, f"W244 seat MSG missing from both inbox paths: {SEAT_MSG}"

# ---------- re-run discipline gates at freeze window (banned + seed_admit) ----------
g = subprocess.run([PY, os.path.join(REPO, "Tools", "banned_direction_gate.py"),
                    "--prereg", "research/PERPETUAL_N1_W244_PREREG.md"],
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

# ---------- extract parity estate + prior-wave legs (physical bytes, never re-typed) ----------
# STRUCTURAL CHOICE: extract BOTH the 90-row estate (W138..W206 full-span 69
# rows + W211..W231 legs) AND the W232..W242 fresh legs from the OWN W243
# block physical bytes (bm-a r1002 splice generation, committed -- structure
# known exactly); the W244 block appends ONE fresh W243 leg -> 101 rows.
a22 = '    # --- W243 materializer face'
a_t141 = '    # --- T-141 s2 lane face'
w243_start = n1_t.find(a22); t141_pos = n1_t.find(a_t141)
assert w243_start > 0 and t141_pos > w243_start, \
    "W243 materializer block face not found (W243 freeze not landed? header-text drift -> honest re-derive required)"
blk = n1_t[w243_start:t141_pos]
m_first_row = re.search(r"assert pf\.N1_BANDS\[", blk)
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state", blk)
assert m_first_row and m_disj and m_disj.start() > m_first_row.start(), \
    "parity span markers not found in W243 block"
_row_ls = blk.rfind(EOL, 0, m_first_row.start()) + len(EOL)
par_full = blk[_row_ls:m_disj.start()]
m232 = re.search(r" *assert pf\.N1_BANDS\[232\] ==", par_full)
assert m232, "upstream W232 row leg not found inside W243 parity span"
par_sec = par_full[:m232.start()]
legs_sec = par_full[m232.start():]
assert par_sec.endswith(EOL), "estate segment must end with EOL"
assert legs_sec.endswith(EOL), "legs segment must end with EOL"
_estate_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", par_sec)
assert par_sec.count("assert pf.N1_BANDS[") == 90 \
    and [int(w) for w in _estate_ws[:69]] == list(range(138, 207)) \
    and [int(_estate_ws[69 + i]) for i in range(11)] == [211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221] \
    and [int(_estate_ws[80 + i]) for i in range(9)] == [222, 223, 224, 225, 226, 227, 228, 229, 230] \
    and int(_estate_ws[89]) == 231, \
    f"estate segment not W138..W206 full-span 69 rows + W211..W230 legs + W231 leg: n={par_sec.count('assert pf.N1_BANDS[')} range={(_estate_ws[:2], _estate_ws[-4:])}"
assert par_full.count("assert pf.N1_BANDS[") == 101, \
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 101 (90 estate + W232..W242 legs 11)"
_legs_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", legs_sec)
assert legs_sec.count("assert pf.N1_BANDS[") == 11 \
    and [int(w) for w in _legs_ws] == list(range(232, 243)), \
    f"legs segment not W232..W242 eleven legs: n={legs_sec.count('assert pf.N1_BANDS[')} waves={_legs_ws}"

# ---------- indent extraction (physical, not assumed; per-file EOL) ----------
def line_indent(t, needle, eol):
    i = t.find(needle)
    assert i >= 0, f"indent needle not found: {needle[:40]}"
    ls = t.rfind(eol, 0, i) + len(eol)
    line = t[ls:t.find(eol, ls)]
    return line[:len(line) - len(line.lstrip(" "))]

CFG_I  = line_indent(n1_t, '243: {"batch"', EOL)
PRE_KEY_I = line_indent(n1_t, '"prereg": ("research/PERPETUAL_N1_W243_PREREG.md', EOL)
PRE_I  = line_indent(n1_t, '"pre-run; design = frozen v1 null calibration verbatim, "', EOL)
_c243 = n1_t.find('243: {"batch"')
assert _c243 > 0, "W243 cfg entry not found (W243 freeze not landed?)"
_mpos = n1_t.find('"a_seed_base"', _c243)
assert _mpos > 0 and n1_t.find('"shard_subdir"', _c243) > _mpos, "W243 cfg a_seed_base line not found"
MEM_I  = line_indent(n1_t, '"a_seed_base": ' + str(W243["a"][0]), EOL) \
    if n1_t.find('"a_seed_base": ' + str(W243["a"][0]), _c243) > 0 \
    else line_indent(n1_t, '"a_seed_base": ' + fmt(W243["a"][0]), EOL)
ROW_I  = line_indent(pf_t,  '243: {"a"', PF_EOL)

# ---------- W243 row owner line (physical bytes; comment text is own generation) ----------
w243_row_start = pf_t.find('    243: {"a"')
assert w243_row_start > 0, "W243 row literal not found in pf source"
_own_ls = pf_t.find(PF_EOL, w243_row_start) + len(PF_EOL)
_own_le = pf_t.find(PF_EOL, _own_ls)
w243_own_line = pf_t[_own_ls:_own_le]
assert '"engine_owner": "bm-a"' in w243_own_line, \
    f"W243 owner line unexpected bytes: {w243_own_line!r}"
ROWC_I = w243_own_line[:len(w243_own_line) - len(w243_own_line.lstrip(" "))]

# ---------- pf comment + row ----------
pf_comment = PF_EOL.join([
"    # W244 (bm-a loop five-face freeze splice -- OWN-SEAT face, seat",
"    # MSG-20261015-0206-bma-w244-seat published=reserved by bm-a itself @",
"    # origin " + SEAT_ORIGIN + " (r1004, queue-depth supply depth-1 at publish, zero takeover); prereg + ADMIT probe",
"    # receipt frozen commit " + w244_prereg_sha[:10] + " (prereg research/PERPETUAL_N1_W244_PREREG.md",
"    # r1005 absorbed-window machine-SUB derive landed pre-freeze, probe",
"    # results/_w244bma_20261015_probe_receipt.json @ " + w244_receipt_sha[:10] + ");",
"    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10",
"    # ~23:1x; deletion-set EMPTY; delivery window = chain-order",
"    # splice AFTER the bm-a W243 five-face (freeze " + w243_freeze_sha[:10] + ") + W243",
"    # finalize product landed (n1_w243_results.json present, ledger",
"    # head " + str(w243_total) + " machine-read at freeze time); zero --no-verify;",
"    # the W244 seat MSG sits in " + seat_found + " at freeze",
"    # time, honest archived per S7 law);",
"    # band gate ADMIT results/_w244bma_20261015_probe_receipt.json: A = FIRST-CLEAN",
"    # arithmetic continuation of the prior-wave A tail (" + fmt(w243_a_tail + 1) + ".." + fmt(w243_a_tail + 2_000) + " CLEAN",
"    # at naive start on the registered universe, hops=0, A_hop_chain empty +",
"    # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,",
"    # fifth consecutive seed-gap face per the W243 seat leg4 anticipation",
"    # confirmed live; A base == prior-wave A tail+1 (" + fmt(w243_a_tail) + "+1) machine-checkable;",
"    # B = FIRST-CLEAN arithmetic continuation of the prior-wave B tail",
"    # (" + fmt(w243_b_tail + 1) + ".." + fmt(w243_b_tail + 200) + " CLEAN on the",
"    # registered universe, hops=0, B_hop_chain empty + B_no_ownA_jump=true -- B",
"    # lands OUTSIDE the own-A window " + fmt(a_lo) + ".." + fmt(a_hi) + ":",
"    # seed-decoupled A/B gap face sixth",
"    # consecutive; B base == prior-wave B tail+1 (" + fmt(w243_b_tail) + "+1) machine-checkable;",
"    # single-window derive (r812 merged the gate legs INTO the",
"    # pre-seat probe; dual-window parity N/A honest); scan face =",
"    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1",
"    # used-seed band + probe cluster 95_000..95_003 + cross-face",
"    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/",
"    # N2-W15 probe points.",
"    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):",
"    # " + gate_lines[0] + ";",
"    # " + gate_lines[1] + ".",
"    # W245+ projection (gate-derived pre-seat probe leg4, pre-W244",
"    # universe): A naive first-clean " + rec["legs"]["leg4"]["W245p_A_naive"] + " CLEAN (hops=0, zero live",
"    # seed refusers) / B naive first-clean " + rec["legs"]["leg4"]["W245p_B_naive"] + " hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " (live refusal",
"    # inside the naive window -- honest forward walk first-clean",
"    # " + rec["legs"]["leg4"]["W245p_B_first_clean"] + " -- B lands OUTSIDE",
"    # the naive A window, seed-gap face inherited); W245 freezer MUST",
"    # re-derive on the post-W244 universe AND reserve the own-wave A window",
"    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1",
"    # equality); never transcribe r587.",
])
pf_row = (f'{ROW_I}244: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), '
          f'"b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'
          + PF_EOL + f'{ROWC_I}"engine_owner": "bm-a"}},' + PF_EOL)
# belt-and-braces: display form must equal the canonical W-family text
assert pf_row.split(PF_EOL)[0].strip() == \
    f'244: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), "b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'

old_pf = must(pf_t, (w243_own_line + PF_EOL + '}'
                     + PF_EOL + '# v1 + ext(wave-1) in-use bands'), 1, "pf_close")
new_pf = (w243_own_line + PF_EOL
          + pf_comment + PF_EOL + pf_row
          + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands')
pf_t2 = pf_t.replace(old_pf, new_pf, 1)

# ---------- n1 cfg entry (programmatic quote wrapping, r761 law) ----------
fin_face = (f"W1..W243 finalize ALL LANDED (W243 finalize product present at splice, "
            f"net chain head {w243_total} machine-read, merged pool K={w243_merged_n} "
            f"machine-read) -- ZERO in-flight upstream seats at splice time, clean precondition "
            f"(thirty-third consecutive fully-clean freeze window); downstream W245 seat NOT YET "
            f"PUBLISHED at this freeze window (the next freezer must seat-first publish per "
            f"O-20261010-2350 sec.2 queue-depth supply; the W245 freezer MUST re-derive live on "
            f"the post-W244 universe + reserve the own-wave A window when deriving B per the "
            f"W244 seat leg4 mandate, never transcribe r587)")
cfg_lines = [
 f'{CFG_I}244: {{"batch": "PERPETUAL-N1-W244",',
 f'{PRE_KEY_I}"prereg": ("research/PERPETUAL_N1_W244_PREREG.md (wave-level frozen "',
]
PRE = [
 "pre-run; design = frozen v1 null calibration verbatim, ",
 "new seed bands only; TWO HUNDRED AND FORTY-FOURTH ENGINE-OWNED WAVE ",
 f"BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate), ",
 "own-series continuation per O-20260101-2355 sec.2 (first-free-",
 "number law after the REGISTERED W243 row five-face freeze (bm-a own seat executed at the bm-a r1002 window; engine self-burn 12/12; finalize one-pass bm-a r1003 own-wave closeout, ledger 958,935 / K=532,520 machine-read), ",
 f"{w243_freeze_sha[:10]} (prereg {w243_prereg_sha[:10]}), SINGLE STATE zero seat gap W2..W243 all ",
 "registered; " + fin_face + "; ",
 "seat published=reserved ",
 "MSG-20261015-0206-bma-w244-seat PUSHED to origin " + SEAT_ORIGIN + " ",
 "BEFORE this freeze per r565 early-visibility law (payload = ",
 "seat MSG + pre-seat probe script + probe receipt; per-wave prereg ",
 "r1005 absorbed-window machine-SUB derive landed pre-freeze -- zero takeover face, bm-a own-seat ",
 "continuity, ",
 f"prereg {w244_prereg_sha[:10]} @ receipt {w244_receipt_sha[:10]}) -- this freeze splice editor derived from the committed W243 editor template in this same freeze window; ",
 "deletion-set EMPTY; delivery window = chain-order splice ",
 "after the W243 five-face + W243 finalize product landed ",
 "(executed in the bm-a loop freeze window ",
 "under the CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED ",
 "2026-10-10 ~23:1x); zero merge at freeze delivery, zero ",
 "--no-verify; single-window derive -- r812 merged the gate ",
 "legs INTO the pre-seat probe; parity N/A honest), ",
 "engine_owner=bm-a (bm-a OWN-SEAT face -- bm-a's ONE HUNDRED AND TWENTY-SIXTH owned claim per machine-derive (engine_owner==bm-a rows ",
 f"{len(bma_rows_live)} + candidate; probe receipt leg0 bma_ordinal=126 = seat-time pre-splice ",
 "live faces disclosed honest, live derive governs ",
 "r587/r359 -- zero takeover, own-seat continuity)), ",
 "wave 244: ",
 "A = FIRST-CLEAN arithmetic continuation of the prior-wave A tail (the continuation ",
 f"{fmt(w243_a_tail + 1)}..{fmt(w243_a_tail + 2_000)} is CLEAN at its own start ",
 "-- hops=0, A_hop_chain empty + A_clean_at_naive_start=true, seed-decoupled ",
 "A-continuation face, fifth consecutive seed-gap face exactly as the W243 seat leg4 ",
 "succession projection notes anticipated; A base == prior-wave A tail+1 (",
 f"{fmt(w243_a_tail)}+1) machine-checkable; ",
 "non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN arithmetic ",
 "continuation of the prior-wave B tail (the continuation ",
 f"{fmt(w243_b_tail + 1)}..{fmt(w243_b_tail + 200)} is CLEAN on the registered universe ",
 "hops=0, B_hop_chain empty + B_no_ownA_jump=true -- B lands OUTSIDE the ",
 f"own-A window {fmt(a_lo)}..{fmt(a_hi)}; seed-decoupled A/B gap ",
 "face fifth consecutive; B base == prior-wave B ",
 "tail+1 machine-checkable; cross-window convergence with the W243 seat leg4 succession projection ",
 "notes -- all MANDATORY notes honored (post-W243 universe ",
 "re-derive + live-trace re-read, no staircase-equality assumption); ADMIT receipt ",
 "results/_w244bma_20261015_probe_receipt.json + ",
 "seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a ",
 "ADMIT convention); W245+ projection per this window gate: ",
 f"A naive first-clean {rec['legs']['leg4']['W245p_A_naive']} CLEAN (hops=0, zero live seed refusers) / B naive first-clean ",
 f"{rec['legs']['leg4']['W245p_B_naive']} hops=1 (live refusal inside the naive window -- honest forward walk first-clean {rec['legs']['leg4']['W245p_B_first_clean']} -- lands OUTSIDE the naive A window -- seed-gap face ",
 "inherited); W245 freezer MUST re-derive on the post-W244 universe AND ",
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
 f'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W244 A: {fmt(a_lo)}..{fmt(a_hi)} (FIRST-CLEAN arithmetic continuation of the prior-wave A tail; {fmt(w243_a_tail + 1)}..{fmt(w243_a_tail + 2_000)} CLEAN at naive start hops=0, A_hop_chain empty + A_clean_at_naive_start=true; seed-decoupled A-continuation face fifth consecutive seed-gap face; A base == prior-A tail+1)',
 f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W244 B: {fmt(b_lo)}..{fmt(b_hi)} (FIRST-CLEAN arithmetic continuation of the prior-wave B tail: staircase {fmt(w243_b_tail + 1)}..{fmt(w243_b_tail + 200)} CLEAN on the registered universe, hops=0, B_hop_chain empty; B base == prior-B tail+1 EXACT in this face; B lands outside own-A; seed-decoupled A/B gap face sixth consecutive)',
 f'{MEM_I}"shard_subdir": "n1_w244", "out_name": "n1_w244_results.json",',
 f'{MEM_I}"engine_owner": "bm-a"}},',
]

cfg_block = EOL.join(cfg_lines)
old_cfg = must(n1_t, ('                       }' + EOL
                      + 'PREREG = WAVE_CONFIGS[2]["prereg"]'), 1, "n1_cfg_close")
new_cfg = (cfg_block + EOL
           + '                       }' + EOL
           + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
assert new_cfg.count('244: {"batch": "PERPETUAL-N1-W244"') == 1
n1_t2 = n1_t.replace(old_cfg, new_cfg, 1)

# ---------- n1 materializer block ----------
hdr = [
 "    # --- W244 materializer face (bm-a loop five-face freeze splice --",
 "    #     OWN-SEAT face under CEO fill-order standing 2026-10-08 ~23:5x",
 "    #     + RE-ISSUE 2026-10-10 ~23:1x + O-20260909-2334 local-full-use",
 "    #     + O-20260924-1730 claim-and-start same-round law):",
 "    #     bm-a's one hundred and twenty-sixth owned per machine-derive (engine_owner==bm-a",
 f"    #     rows {len(bma_rows_live)} + candidate; own-seat face: seat published=reserved by bm-a itself",
 "    #     (r1004 MSG-20261015-0206-bma-w244-seat @ origin " + SEAT_ORIGIN + "; probe leg0",
 "    #     bma_ordinal=126 = seat-time pre-splice faces;",
 "    #     live derive at freeze governs);",
 "    #     wave 244 = first free number after the",
 "    #     REGISTERED W243 row (five-face freeze " + w243_freeze_sha[:10] + "; bm-a own seat executed at",
 "    #     the bm-a r1002 window; engine",
 "    #     self-burn 12/12 + finalize one-pass bm-a r1003 own-wave closeout ledger 958,935 / K=532,520",
 "    #     -- SINGLE STATE zero seat gap (W2..W243 all registered). Seat",
 "    #     published=reserved MSG-20261015-0206-bma-w244-seat pushed",
 "    #     to origin " + SEAT_ORIGIN + " BEFORE this freeze, r565 law (payload =",
 "    #     seat MSG + pre-seat probe script + probe receipt; per-wave prereg",
 f"    #     r1005 absorbed-window derive landed pre-freeze commit {w244_prereg_sha[:10]}; this freeze splice editor",
 "    #     derived from the committed W243 editor template in this same freeze",
 "    #     window (E63 heal lineage: arith_a244/arith_b244 define+assert consistent);",
 "    #     deletion-set EMPTY; delivery window",
 "    #     = chain-order splice after the W243 five-face + W243 finalize",
 "    #     product landed; zero --no-verify; the W244 seat MSG sits in",
 "    #     " + seat_found + " at freeze time, honest archived",
 "    #     per S7 law).",
 "    #     TWO HUNDRED AND FORTY-FOURTH engine wave BY",
 f"    #     MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate; gate",
 "    #     leg0 machine output governs per r359 law).",
 f"    #     {fin_face}; the finalize merge loop",
 "    #     still derives the wave set from registry keys at run",
 "    #     time, FAIL-CLOSED r307 always on. ADMIT receipt",
 "    #     results/_w244bma_20261015_probe_receipt.json;",
 "    #     seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a",
 f"    #     ADMIT convention upgrade): {gate_lines[0]}; {gate_lines[1]};",
 "    #     banned gate ADMIT 0 (re-run at freeze window);",
 "    #     not a re-pick (R250: W244 bands were never assigned).",
 "    _set_wave(244)",
 "    try:",
 '        assert WAVE_CONFIGS[243]["a_seed_base"] == pf.N1_BANDS[243]["a"][0], \\',
 '            "W244 upstream W243 mirror drift (a)"',
 "        assert WAVE_CONFIGS[243][\"b_exit_seed_base\"] == \\",
 '            pf.N1_BANDS[243]["b_exit"][0], "W244 upstream W243 mirror drift (b)"',
 "        assert WAVE_CONFIGS[243].get(\"engine_owner\") == \\",
 '            pf.N1_BANDS[243].get("engine_owner") == "bm-a", \\',
 '            "W244 upstream W243 engine_owner mirror drift (law-mirror parity; bm-a upstream seat face)"',
 "        w243_a = {A_SEED_BASE + j for j in range(A_N)}",
 "        w243_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
 '        assert not (w243_a & w243_b), "W244 A/B band overlap"',
 "        assert not (w243_a & reg_ints) and not (w243_b & reg_ints), \\",
 '            "W244 hits SEED_REGISTRY"',
 '        for nm, band in (("A", w243_a), ("B", w243_b)):',
 '            assert not (band & v1_a) and not (band & v1_b), f"W244 {nm} hits v1"',
 '            assert not (band & w1_a) and not (band & w1_b), f"W244 {nm} hits W1"',
 '            assert not (band & probes), f"W244 {nm} hits probe seeds"',
]
w243_leg = [
 f'        assert pf.N1_BANDS[243] == {{"a": ({fmt(pf_mod.N1_BANDS[243]["a"][0])}, {fmt(pf_mod.N1_BANDS[243]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[243]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[243]["b_exit"][1])}),',
'                                    "engine_owner": "bm-a"}, \\',
'            "registered W243 row parity drift (r307; bm-a five-face freeze; own-seat face disclosed)"',
]
tail = [
 "        # prior-wave disjointness W2..W243 (single state: all",
 "        # registered, dynamic registry derive, r511 law)",
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 244):",
 '            assert not (w243_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
 "                                 for j in range(A_N)}), f\"W244 A hits W{wprev}\"",
 '            assert not (w243_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
 "                                  for j in range(B_N)}), f\"W244 B hits W{wprev}\"",
 "        n3r1_used244 = set(range(70_000, 70_006))",
 "        assert not (w243_a & n3r1_used244) and not (w243_b & n3r1_used244), \\",
 '            "W244 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
 "        assert not (w243_a & lfc_actual12) and not (w243_b & lfc_actual12), \\",
 '            "W244 bands must clear the lfc actual draw range"',
 "        assert not (w243_a & options_actual12) and \\",
 "            not (w243_b & options_actual12), \\",
 '            "W244 bands must clear the options_wave2 actual draw range"',
  "        # band facts (law sec.4 W244 row): A = FIRST-CLEAN arithmetic",
  "        # continuation of the prior-wave A tail",
 f"        # ({fmt(w243_a_tail + 1)}..{fmt(w243_a_tail + 2_000)} CLEAN at naive start on the",
  "        # registered universe, hops=0, A_hop_chain empty +",
  "        # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,",
  "        # fifth consecutive seed-gap face, exactly as the W243 seat leg4",
  "        # succession projection notes anticipated; A base == prior-wave A",
 f"        # tail+1 ({fmt(w243_a_tail)}+1) machine-checkable;",
  "        # B = FIRST-CLEAN arithmetic continuation of the prior-wave B",
 f"        # tail ({fmt(w243_b_tail + 1)}..{fmt(w243_b_tail + 200)} CLEAN on the registered",
  "        # universe, hops=0, B_hop_chain empty + B_no_ownA_jump=true -- B",
  "        # lands OUTSIDE the own-A window",
 f"        # {fmt(a_lo)}..{fmt(a_hi)}; seed-decoupled A/B gap face sixth consecutive;",
  "        # B base == prior-wave B tail+1",
 f"        # ({fmt(w243_b_tail)}+1) machine-checkable;",
  "        # B_no_ownA_jump=true (fc_b == fc_b_naive); cross-window convergence with",
  "        # the W243 seat leg4 succession projection notes -- all",
  "        # MANDATORY notes honored (post-W243 universe",
  "        # re-derive + live-trace re-read, no staircase-equality assumption);",
 f'        assert WAVE_CONFIGS[244]["a_seed_base"] == {a_lo} == {w243_a_tail} + 1, (',
 '            "W244 A must be the first-clean arithmetic continuation of the "',
 '            "prior-wave A tail (hops=0, A_hop_chain empty + A_clean_at_naive_start=true -- "',
 '            "seed-decoupled A-continuation face, fifth consecutive seed-gap face, "',
 '            "exactly as the W243 seat leg4 succession projection notes "',
 '            "anticipated; A base == prior-wave A tail+1 machine-checkable)")',
 f"        arith_a244 = set(range({a_lo}, {a_hi + 1}))",
 "        assert not (arith_a244 & reg_ints), \\",
 '            "W244 A window must be CLEAN (first-clean ADMIT face, A-continuation)"',
 f'        assert WAVE_CONFIGS[244]["b_exit_seed_base"] == {b_lo} == {w243_b_tail} + 1, (',
 '            "W244 B keeps the staircase base (FIRST-CLEAN arithmetic "',
 '            "continuation of the prior-wave B tail, hops=0, B_hop_chain "',
 '            "empty + B_no_ownA_jump=true -- B lands outside the own-A "',
 '            "window; seed-decoupled A/B gap face sixth consecutive; "',
 '            "B base == prior-wave B tail+1 machine-checkable)")',
 f"        arith_b244 = set(range({b_lo}, {b_hi + 1}))",
 "        assert not (arith_b244 & reg_ints), \\",
 '            "W244 B window must be CLEAN (first-clean ADMIT face, arithmetic continuation of the prior-wave B tail)"',
 "        assert not (arith_b244 & arith_a244), \\",
 '            "W244 A/B same-freeze mutual exclusion (seed-decoupled gap face inherited: B below own A)"',
 "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W244-SHARD-0\",",
 '                                          "n1w244-0of12"), "W244 entry identity"',
 '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W244-SHARD-11",',
 '                                           "n1w244-11of12")',
 "        assert SHARD_DIR.endswith(\"n1_w244\") and OUT.endswith(",
 '            "n1_w244_results.json"), "W244 path drift"',
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 244):",
 "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(",
 "                PATHS.results_dir, \"p2cal_ext\",",
 "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\",
 '                f"W244 shard dir collides with W{wprev}"',
 "        # W244 finalize cumulative deps: W17..W243 outputs ALL PRESENT",
 f"        # (landed net chain head {w243_total} machine-read at freeze time)",
 "        # -- ZERO in-flight upstream seats at splice, clean precondition",
 "        # freeze window; the finalize merge loop derives the wave",
 "        # set from registry keys at run time and stays",
 "        # FAIL-CLOSED, r307 two-state law).",
 "        for _depw in range(17, 244):",
 "            assert os.path.exists(os.path.join(",
 "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\",
 '                f"W244 finalize cumulative dep (W{_depw} output) missing"',
 "        # finalize wave-set derivation face (r511 derive law): every",
 "        # registered wave below 244 composes; wave 15 excluded by",
 "        # design; SINGLE STATE (W2..W243 all registered -- no",
 "        # two-state seat disclosure needed at this freeze).",
 "        assert sorted(w for w in WAVE_CONFIGS if w < 244) == \\",
 "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\",
 "            [w for w in range(16, 244)], \\",
 '            "W244 prior-wave set must derive from registry keys (no 15; " \\',
 '            "W2..W243 registered single state)"',
 "        assert os.path.exists(os.path.join(",
 '            PATHS.root, "research", "PERPETUAL_N1_W244_PREREG.md")), \\',
 '            "W244 per-wave prereg missing (materializer requirement)"',
 "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"",
 "    finally:",
 "        _set_wave(2)",
]
block = EOL.join(hdr) + EOL + par_sec + legs_sec + EOL.join(w243_leg) + EOL + EOL.join(tail) + EOL
# family #6 atomic triple gate (carried forward): the new
# block's LHS w<244> / RHS range(16,244)+range(17,244) / comment below-244 MUST move together.
assert block.count("if w < 244)") == 3, f"family-6 triple: w<244 count {block.count('if w < 244)')} != 3"
assert block.count("if w < 243)") == 0, "family-6 triple: stale w<243 leaked into the W244 block"
assert block.count("range(16, 244)") == 1 and block.count("range(17, 244)") == 1, "family-6 triple: RHS ranges wrong"
assert block.count("registered wave below 244 composes") == 1, "family-6 triple: comment face wrong"
old_blk_anchor = must(n1_t2, "    # --- T-141 s2 lane face", 1, "t141_marker")
n1_t3 = n1_t2.replace(old_blk_anchor, block + old_blk_anchor, 1)

# ---------- n1 print line ----------
pr = [
 '          "+ W244 materializer face [same guard set, dep=W17..W243 "',
 f'          "outputs ALL PRESENT (landed net chain head {w243_total} = W243 bm-a finalize one-pass, K={w243_merged_n} merged pool) -- ZERO "',
 '          "in-flight upstream seats at splice, clean precondition, TWO HUNDRED AND FORTY-FOURTH "',
 f'          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} "',
 '          "+ candidate) bm-a\'s one hundred and twenty-sixth owned claim per "',
 '          "machine-derive (engine_owner==bm-a rows 125 + candidate; OWN-SEAT face: seat published by bm-a itself, "',
 '          "probe leg0 bma_ordinal=126 = seat-time pre-splice faces disclosed honest, "',
 '          "live derive at freeze governs), "',
 '          "A=FIRST-CLEAN arithmetic continuation of prior-wave A tail (A-continuation face, "',
 '          "hops=0, A_hop_chain empty + A_clean_at_naive_start=true, seed-decoupled fifth consecutive seed-gap face) "',
 "+ B=FIRST-CLEAN arithmetic continuation of the prior-wave B tail (B-continuation face, ",
 "hops=0, B_hop_chain empty + B_clean_at_naive_start=true, B base == prior-B-tail+1 EXACT, ",
 '          "seed-decoupled A/B gap face sixth consecutive), chain-order splice from the "',
 '          "committed ADMIT receipt + seed_admit_gate rc0 both bands FREE "',
 '          "(O-20261010-1945-bm-a ADMIT convention), "',
 '          "ADMIT receipt "',
 '          "results/_w244bma_20261015_probe_receipt.json, law sec.4 W244 row, "',
 '          "bm-a loop CEO fill-order RE-ISSUE 23:1x] "',
]

old_pr = must(n1_t3, '          "+ T-141 s2 ', 1, "print_t141")
n1_t4 = n1_t3.replace(old_pr, EOL.join(pr) + EOL + old_pr, 1)

# ---------- post-edit count gates ----------
assert n1_t4.count('"batch": "PERPETUAL-N1-W244"') == 1
assert n1_t4.count("# --- W244 materializer face") == 1     # block header
assert n1_t4.count('"+ W244 materializer face') == 1        # print fragment
assert n1_t4.count('244: {"batch": "PERPETUAL-N1-W244"') == 1
assert pf_t2.count(ROW_I + '244: {"a"') == 1
assert pf_t2.count('"engine_owner": "bm-a"},' + PF_EOL + '}') == 1
assert n1_t4.count('    # --- T-141 s2 lane face') == 1
assert n1_t4.count('"PERPETUAL-N1-W244-SHARD-0"') == 1
assert n1_t4.count(f'assert pf.N1_BANDS[243] == {{"a": ({fmt(pf_mod.N1_BANDS[243]["a"][0])}, {fmt(pf_mod.N1_BANDS[243]["a"][1])}),') == 1
# the W243 leg lives ONLY in the new W244 block (1); the W241 leg lives in the kept
# W243 block + the new W244 block (2); the W240 leg lives in kept W241 + W243 + new
# W244 (3); the W239 leg in kept W240 + W241 + W243 + new (4); the W238 leg in
# kept W239..W243+new (5); the W237 leg in kept W238..W243+new (6); the W236 leg
# in kept W237..W243+new (7); the W235 leg in kept W236..W243+new (8)
assert n1_t4.count(f'assert pf.N1_BANDS[242] == {{"a": ({fmt(pf_mod.N1_BANDS[242]["a"][0])}, {fmt(pf_mod.N1_BANDS[242]["a"][1])}),') == 2
assert n1_t4.count(f'assert pf.N1_BANDS[241] == {{"a": ({fmt(pf_mod.N1_BANDS[241]["a"][0])}, {fmt(pf_mod.N1_BANDS[241]["a"][1])}),') == 3
assert n1_t4.count(f'assert pf.N1_BANDS[240] == {{"a": ({fmt(pf_mod.N1_BANDS[240]["a"][0])}, {fmt(pf_mod.N1_BANDS[240]["a"][1])}),') == 4
assert n1_t4.count(f'assert pf.N1_BANDS[239] == {{"a": ({fmt(pf_mod.N1_BANDS[239]["a"][0])}, {fmt(pf_mod.N1_BANDS[239]["a"][1])}),') == 5
assert n1_t4.count(f'assert pf.N1_BANDS[238] == {{"a": ({fmt(pf_mod.N1_BANDS[238]["a"][0])}, {fmt(pf_mod.N1_BANDS[238]["a"][1])}),') == 6
assert n1_t4.count(f'assert pf.N1_BANDS[237] == {{"a": ({fmt(pf_mod.N1_BANDS[237]["a"][0])}, {fmt(pf_mod.N1_BANDS[237]["a"][1])}),') == 7
assert n1_t4.count(f'assert pf.N1_BANDS[236] == {{"a": ({fmt(pf_mod.N1_BANDS[236]["a"][0])}, {fmt(pf_mod.N1_BANDS[236]["a"][1])}),') == 8
for _b in range(209, 245):
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
  "machine": "bm-a", "wave": 244,
  "phase": "five-face freeze chain-order splice (bm-a own-seat freeze window, upstream ALL LANDED clean precondition)",
  "origin_base": omain,
  "pf_sha16_pre": hashlib.sha256(pf_b).hexdigest()[:16],
  "n1_sha16_pre": hashlib.sha256(n1_b).hexdigest()[:16],
  "pf_sha16_post": hashlib.sha256(pf_t2.encode("utf-8")).hexdigest()[:16],
  "n1_sha16_post": hashlib.sha256(n1_t4.encode("utf-8")).hexdigest()[:16],
  "bands": {"A": A, "B": B, "a_lo": a_lo, "a_hi": a_hi, "b_lo": b_lo, "b_hi": b_hi},
  "admit_receipt": "results/_w244bma_20261015_probe_receipt.json",
  "seed_admit_gate": gate_lines,
  "banned_gate": "ADMIT rc0 (re-run at freeze window)",
  "band_semantics": {"A": "FIRST-CLEAN arithmetic continuation of prior-wave A tail (hops=0, A_hop_chain empty + A_clean_at_naive_start=true; seed-decoupled A-continuation face, fifth consecutive seed-gap face; A base == prior-A tail+1 EXACT)",
                     "B": "FIRST-CLEAN arithmetic continuation of the prior-wave B tail (B base == prior-B tail+1 EXACT, hops=0, B_hop_chain empty -- the prior-wave live-seed refusal chain is behind us; B_no_ownA_jump=true; seed-decoupled A/B gap face sixth consecutive)"},
  "w243_upstream": {"freeze_sha": w243_freeze_sha, "prereg_sha": w243_prereg_sha,
                    "ledger_total": w243_total, "merged_n": w243_merged_n,
                    "engine_owner": "bm-a (upstream seat honored)",
                    "repair_chain_note": "W243 bm-a own-wave closeout r1003 (five-face splice " + w243_freeze_sha[:10] + " + engine self-burn 12/12 + finalize one-pass ledger 958,935 / K=532,520)"},
  "own_seat_face": {"seat_msg": SEAT_MSG, "seat_origin": SEAT_ORIGIN,
                    "inherited": False,
                    "note": "seat published=reserved by bm-a itself (MSG-20261015-0206-bma-w244-seat pushed to origin " + SEAT_ORIGIN + " r1004 BEFORE this freeze per r565 law, queue-depth supply depth-1 at publish; the W244 freeze's waits-upstream on the W243 finalize DISARMED by the W243 finalize landing 01:4x); zero takeover -- wave 244 engine_owner=bm-a, bm-a's 126th own wave per live derive (probe leg0 bma_ordinal=126 = seat-time pre-splice faces disclosed honest, live derive governs r587/r359; freeze-time live face owner rows 233 + candidate = 234th EXACT)"},
  "transitive_deps": {f"W{w}": f"results/perpetual_faces/n1_w{w}_results.json present (belt-and-braces gate)" for w in (242, 241, 240, 239, 238, 237, 236, 235, 234, 233)},
  "downstream_seat": "W245 seat NOT YET PUBLISHED at this freeze window (next freezer must seat-first publish per O-20261010-2350 sec.2 queue-depth supply; the W245 freezer MUST re-derive live on the post-W244 universe + reserve the own-wave A window when deriving B per the W244 seat leg4 mandate, never transcribe r587 -- W245p face: A naive 555_501..557_500 CLEAN (hops=0) / B naive 541_901..542_100 hops=1, honest forward walk first-clean 542_001..542_200 (B lands OUTSIDE the naive A window; seed-gap face inherited))",
  "seat": seat_found + " (origin " + SEAT_ORIGIN + ")",
  "prereg_bundle": {"prereg_sha": w244_prereg_sha, "probe_receipt_sha": w244_receipt_sha,
                    "note": "prereg derived by the absorbed r1005 window and committed by r1006 (machine-SUB from the frozen W244 tpl 70141bc22; commit " + w244_prereg_sha[:10] + "; facts live-derived ledger 958,935 / K=532,520; freeze-time live derive bma rows 125 + candidate 126th EXACT per r587/r359); splice editor derived from the committed W243 editor template by count-asserted ordered transform in this same freeze window (E63 heal lineage: arith_a244/arith_b244 define+assert consistent); upstream W243 already landed (clean-precondition thirty-third consecutive window); zero transcription"},
  "ordinal_faces": {"owner_rows_live": len(owner_rows_live), "bma_rows_live": len(bma_rows_live),
                    "bmc_rows_live": len(bmc_rows_live),
                    "engine_owned_ordinal": len(owner_rows_live) + 1,
                    "bma_own_ordinal": len(bma_rows_live) + 1,
                    "probe_receipt_bma_ordinal_face": 125,
                    "note": "post-W243 registration: bm-a rows 125 + candidate = 126th owned (live derive at freeze time governs per r587/r359; probe leg0 bma_ordinal=126 = seat-time faces -- zero takeover, own-seat continuity)"},
  "parity_section": {"source": "OWN W243 block physical bytes (bm-a splice generation r1002 window, structure known exactly)",
                     "bytes": len(par_sec) + len(legs_sec),
                     "estate_row_asserts": par_sec.count("assert pf.N1_BANDS["),
                     "prior_legs_row_asserts": legs_sec.count("assert pf.N1_BANDS["),
                     "note": "full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W231 legs (estate 90) + W232..W242 legs extracted verbatim (11) -> W244 block = 102 rows ending at W243 (estate 90 + W232..W242 legs 11 + fresh W243 leg 1); disclosed: (a) inherited W213 leg error-string face preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact); (b) band-set variable one-behind naming face (w243_a holds wave-243 bands) = lineage mechanical aging face, zero functional impact"},
  "family6_triple_gate": {"absorbed": True,
                          "note": "W243 editor family-6 gate carried forward: new block LHS w<244 x3 / RHS range(16,244)+range(17,244) / comment below-244 count-asserted ATOMICALLY before splice; W243 block's own w<243 face = legitimate prior-wave boundary (not stale); E63 heal lineage applied (arith define/assert consistent)"},
  "eol": {"n1_crlf": EOL == "\r\n", "pf_crlf": PF_EOL == "\r\n"},
  "liveness_anchors": {f"w{_b}_block_kept": 1 for _b in range(209, 245)},
}

open(RECEIPT_OUT, "w", encoding="utf-8").write(json.dumps(receipt, indent=1))
print(json.dumps({k: receipt[k] for k in
      ("phase", "origin_base", "pf_sha16_post", "n1_sha16_post", "bands",
       "w243_upstream", "own_seat_face")}, indent=1))
print("SPLICE OK -- py_compile both green; NEXT: selftest (default wave, r522 law) -> pathspec commit+push -> engine self-ignite W244 burn (12 shards) -> PRE-FINALIZE six-gate (standing law) -> finalize one-pass")
