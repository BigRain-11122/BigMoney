# -*- coding: utf-8 -*-
# 2026-10-13 08:1x bm-c r959 freeze window (upstream W1..W227 ALL LANDED, clean precondition): W228 five-face freeze splice editor.
# Upstream chain ALL LANDED at this window: W1..W227 finalize products
# present (W227 finalize one-pass r956 06:5x dead-window body absorbed by
# r956-absorb 1e5ed3326, net chain head 923,189, merged pool K=497,320,
# n1_w227_results.json machine-read) -- ZERO in-flight upstream seats,
# clean precondition (seventeenth consecutive fully-clean freeze window).
# Upstream six-gate disclosure: the W227 cycle ran its six-gate PRE-FINALIZE
# correctly (W217-debt standing law held, W212-pattern zero recurrence); THIS
# W228 cycle runs PRE-FINALIZE likewise (standing law).
# Lineage: _w227bmc_freeze_edits.py pattern (proven live-fire freeze,
# r956 dead-window body, estate absorbed by r956-absorb 1e5ed3326) + r787 preflight law + r609
# origin-verbatim base + r761 programmatic quote wrapping + r909
# physical-byte anchors + r838 per-file EOL detection + family #6
# LHS/RHS/comment ATOMIC TRIPLE absorbed (the new block's w<228>/
# range(16,228)/below-228 triple is count-asserted atomically; the W227
# block's own w<227 face is legitimate prior-wave boundary, not stale).
# Zero hardcoded upstream band values: ALL W227 facts machine-derived from the
# LIVE pf import at freeze time (bm-c's own registered row), cross-checked against
# the committed ADMIT receipt (results/_w228bmc_20261013_probe_receipt.json)
# which was derived on the post-W227-REGISTERED universe. If the LIVE W227 bands
# differ from the declared face, the staircase asserts fail LOUD (fail-closed).
# STRUCTURAL CHOICE (vs the W226 editor): the parity estate (W138..W206
# full-span, 69 rows, r858 absorb generation) is extracted from the OWN W227
# block physical bytes -- structure known exactly (this machine's own splice
# generation) -- the W227 block's own W225 leg (1 row) is excluded from the
# estate path and fresh W225 + W226 + W227 legs are appended for the W228
# block parity (86 rows: estate 69 + W211..W224 legs + W225 leg + W226 leg +
# W227 leg). Extraction self-asserts the 83-row cut (69 estate + W211..W223 +
# W224) regardless. Disclosed: (a) the inherited W213 leg inside the estate
# carries a cosmetic error-string face ("registered W212 row parity drift")
# from the r912 editor generation -- physical bytes preserved verbatim per
# extraction law, zero functional impact (assert target [213] is correct);
# (b) the prereg block-30 prose face carries the lineage's one-wave-behind
# "块" reference (mechanical aging face, r927 fixB precedent family) while
# THIS editor extracts from the OWN W227 block -- parity list face is exact
# (ends at W227), zero functional impact.
# Own bundle hashes (prereg/probe receipt) derived via pickaxe, never transcribed.
# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.
import json, hashlib, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PF = os.path.join(REPO, "scripts", "perpetual_faces.py")
N1 = os.path.join(REPO, "scripts", "perpetual_faces_n1.py")
RECEIPT_IN = os.path.join(REPO, "results", "_w228bmc_20261013_probe_receipt.json")
RECEIPT_OUT = os.path.join(REPO, "results", "_w228bmc_freeze_receipt.json")
SEAT_MSG = "MSG-20261013-0720-bmc.md"
SEAT_ORIGIN = "4e30ddf69"
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

# ---------- gate 0.5: W227 five-face landed + W227 finalize product present ----------
# (chain-order precondition; W226/W225/W224/W223 finalize are transitive deps of the
# W228 freeze and are belt-and-braces checked here + enforced by the block's
# cumulative-deps assert range(17, 228) at selftest time)
W227 = dict(pf_mod.N1_BANDS.get(227) or {})
assert W227.get("engine_owner") == "bm-c", \
    f"W227 row not landed as declared (bm-c own seat owner expected, no takeover face): {W227} -- five-face freeze missing;" \
    " if an unexpected face exists the freeze window MUST re-derive this editor honestly"
w227_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w227_results.json")
assert os.path.exists(w227_out_path), "W227 finalize product missing (n1_w227_results.json) -- chain dep not met"
w225_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w225_results.json")
assert os.path.exists(w225_out_path), "W225 finalize product missing (transitive chain dep) -- abort"
w224_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w224_results.json")
assert os.path.exists(w224_out_path), "W224 finalize product missing (transitive chain dep) -- abort"
w223_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w223_results.json")
assert os.path.exists(w223_out_path), "W223 finalize product missing (transitive chain dep) -- abort"
w226_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w226_results.json")
assert os.path.exists(w226_out_path), "W226 finalize product missing (transitive chain dep) -- abort"
w227_out = json.load(open(w227_out_path, encoding="utf-8"))
w227_led = (w227_out.get("science_gates") or {}).get("ledger") or {}
w227_total = w227_led.get("total")
w227_merged_n = None
try:
    w227_merged_n = w227_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
assert w227_total == 923_189 and w227_merged_n == 497_320, \
    f"W227 finalize anchors drift at freeze time: total={w227_total} merged={w227_merged_n} (expect 923,189 / 497,320)"
# freeze shas machine-derived (pickaxe), never transcribed
r = git("log", "--format=%H", "-S", '227: {"a"', "--", "scripts/perpetual_faces.py")
w227_freeze_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W227_PREREG.md")
w227_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
assert os.path.exists(os.path.join(REPO, "research", "PERPETUAL_N1_W227_PREREG.md")), \
    "bm-c W227 per-wave prereg missing on disk -- chain face incomplete, abort"
# live ordinal derive (r359 law: gate machine output governs; the pre-seat probe
# receipt leg0 face bmc_ordinal=58 = seat-time live face; live derive at freeze
# time: bmc rows 57 + candidate = 58th EXACT)
owner_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner")]
bmc_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
assert len(owner_rows_live) == 217 and len(bmc_rows_live) == 57, \
    f"leg0 ordinal drift at freeze time: owner={len(owner_rows_live)} bmc={len(bmc_rows_live)} (expect 217/57 PRE-splice post-W227 registration; W227 precedent 216/56 pre-splice + W227 splice 217/57; this candidate = 58th own wave per the same live-derive law, r587/r359)"
print(f"gate0.5 OK: W227 landed (freeze {w227_freeze_sha[:10]}, owner=bm-c own seat), "
      f"W227+W226+W225+W224+W223 finalize products present "
      f"(W227 ledger head {w227_total}, merged n={w227_merged_n}); owner rows {len(owner_rows_live)} + candidate, "
      f"bm-c rows {len(bmc_rows_live)} + candidate (58th own wave per live derive r587/r359; "
      f"probe receipt leg0 bmc_ordinal=58 seat-time live face disclosed)")

# ---------- band facts from the committed ADMIT receipt (never transcribed) ----------
rec = json.load(open(RECEIPT_IN, encoding="utf-8"))
assert rec["verdict"] == "ADMIT"
A = rec["bands"]["A"]; B = rec["bands"]["B"]
a_lo, a_hi = (int(x) for x in A.split("_"))
b_lo, b_hi = (int(x) for x in B.split("_"))
leg1 = rec["legs"]["leg1"]
assert [a_lo, a_hi] == leg1["A"] and [b_lo, b_hi] == leg1["B"], "receipt band mismatch"
assert (a_lo, a_hi) == (516_404, 518_403) and (b_lo, b_hi) == (518_404, 518_603), \
    f"W228 band drift vs probe ADMIT: {(a_lo, a_hi)} {(b_lo, b_hi)}"
w227_b_tail = W227["b_exit"][1]      # registered W227 row b_exit hi (pf import, live)
w227_a_tail = W227["a"][1]           # registered W227 row A hi (pf import, live)
assert w227_b_tail + 1 == a_lo and a_hi + 1 == b_lo, "staircase base relations broken"
# the REFUSED arithmetic continuation starts at prior-wave A-tail+1 (== W227 B-base),
# machine-derived from the LIVE registered row, never transcribed.
assert w227_a_tail + 1 == W227["b_exit"][0], "W227 A-tail+1 != W227 B-base (registered row in-wave relation)"
assert [w227_a_tail + 1, w227_a_tail + 2_000] == leg1["ARITH_A"], \
    f"refused-continuation start drift vs probe receipt leg1 ARITH_A: {[w227_a_tail + 1, w227_a_tail + 2_000]} != {leg1['ARITH_A']}"

# own bundle shas via pickaxe (self-referencing commit facts, zero transcription)
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W228_PREREG.md")
w228_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "results/_w228bmc_20261013_probe_receipt.json")
w228_receipt_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
# seat MSG honest location (inbox or processed; S7 archive law)
seat_found = None
for _p in ("fleet/inbox", "fleet/inbox/processed"):
    if os.path.exists(os.path.join(REPO, _p, SEAT_MSG)):
        seat_found = _p + "/" + SEAT_MSG
        break
assert seat_found, f"W228 seat MSG missing from both inbox paths: {SEAT_MSG}"

# ---------- re-run discipline gates at freeze window (banned + seed_admit) ----------
g = subprocess.run([PY, os.path.join(REPO, "Tools", "banned_direction_gate.py"),
                    "--prereg", "research/PERPETUAL_N1_W228_PREREG.md"],
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
# STRUCTURAL CHOICE: extract the estate from the OWN W227 block (bytes known
# exactly: full-span estate W138..W206 69 rows + own W211 leg + ... + own W223 leg) -- the W227 block is this machine's own splice generation
# (r956 freeze-window editor, estate absorbed by r956-absorb 1e5ed3326), structure known. The W227 block span ends where the
# T-141 s2 lane face marker begins.
a15 = '    # --- W227 materializer face'
a_t141 = '    # --- T-141 s2 lane face'
w227_start = n1_t.find(a15); t141_pos = n1_t.find(a_t141)
assert w227_start > 0 and t141_pos > w227_start, \
    "W227 materializer block face not found (W227 freeze not landed? header-text drift -> honest re-derive required)"
blk = n1_t[w227_start:t141_pos]
m_first_row = re.search(r"assert pf\.N1_BANDS\[", blk)
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state", blk)
assert m_first_row and m_disj and m_disj.start() > m_first_row.start(), \
    "parity span markers not found in W227 block"
_row_ls = blk.rfind(EOL, 0, m_first_row.start()) + len(EOL)
par_full = blk[_row_ls:m_disj.start()]
m225 = re.search(r" *assert pf\.N1_BANDS\[225\] ==", par_full)
assert m225, "upstream W225 row leg not found inside W227 parity span"
par_sec = par_full[:m225.start()]
assert par_sec.endswith(EOL), "estate segment must end with EOL"
_estate_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", par_sec)
assert par_sec.count("assert pf.N1_BANDS[") == 83 \
    and [int(w) for w in _estate_ws[:69]] == list(range(138, 207)) \
    and [int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71]), int(_estate_ws[72]), int(_estate_ws[73]), int(_estate_ws[74]), int(_estate_ws[75]), int(_estate_ws[76]), int(_estate_ws[77]), int(_estate_ws[78]), int(_estate_ws[79])] == [211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221] \
    and int(_estate_ws[80]) == 222 \
    and int(_estate_ws[81]) == 223 \
    and int(_estate_ws[82]) == 224, \
    f"estate segment not W138..W206 full-span 69 rows + W211..W223 legs + W224 leg: n={par_sec.count('assert pf.N1_BANDS[')} range={(_estate_ws[:2], _estate_ws[-14:])}"
assert par_full.count("assert pf.N1_BANDS[") == 85, \
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 85 (69 estate + W211..W223 legs + W224 leg + W225 leg + W226 leg)"

# ---------- indent extraction (physical, not assumed; per-file EOL) ----------
def line_indent(t, needle, eol):
    i = t.find(needle)
    assert i >= 0, f"indent needle not found: {needle[:40]}"
    ls = t.rfind(eol, 0, i) + len(eol)
    line = t[ls:t.find(eol, ls)]
    return line[:len(line) - len(line.lstrip(" "))]

CFG_I  = line_indent(n1_t, '227: {"batch"', EOL)
PRE_KEY_I = line_indent(n1_t, '"prereg": ("research/PERPETUAL_N1_W227_PREREG.md', EOL)
PRE_I  = line_indent(n1_t, '"pre-run; design = frozen v1 null calibration verbatim, "', EOL)
# MEM_I derived INSIDE the W227 cfg entry span (own splice generation, value
# format known: plain int -- indent is all we take)
_c227 = n1_t.find('227: {"batch"')
assert _c227 > 0, "W227 cfg entry not found (W227 freeze not landed?)"
_mpos = n1_t.find('"a_seed_base"', _c227)
assert _mpos > 0 and n1_t.find('"shard_subdir"', _c227) > _mpos, "W227 cfg a_seed_base line not found"
MEM_I  = line_indent(n1_t, '"a_seed_base": ' + str(W227["a"][0]), EOL) \
    if n1_t.find('"a_seed_base": ' + str(W227["a"][0]), _c227) > 0 \
    else line_indent(n1_t, '"a_seed_base": ' + fmt(W227["a"][0]), EOL)
ROW_I  = line_indent(pf_t,  '227: {"a"', PF_EOL)

# ---------- W227 row owner line (physical bytes; comment text is own generation) ----------
w227_row_start = pf_t.find('    227: {"a"')
assert w227_row_start > 0, "W227 row literal not found in pf source"
_own_ls = pf_t.find(PF_EOL, w227_row_start) + len(PF_EOL)
_own_le = pf_t.find(PF_EOL, _own_ls)
w227_own_line = pf_t[_own_ls:_own_le]
assert '"engine_owner": "bm-c"' in w227_own_line, \
    f"W227 owner line unexpected bytes: {w227_own_line!r}"
ROWC_I = w227_own_line[:len(w227_own_line) - len(w227_own_line.lstrip(" "))]

# ---------- pf comment + row ----------
pf_comment = PF_EOL.join([
"    # W228 (bm-c loop five-face freeze splice, seat",
"    # MSG-20261013-0720-bmc pushed to origin " + SEAT_ORIGIN,
"    # pre-freeze r565 law; prereg + ADMIT probe receipt frozen",
"    # commit " + w228_prereg_sha[:10] + " (prereg research/PERPETUAL_N1_W228_PREREG.md",
"    # r958 prereg derived + landed pre-freeze, probe",
"    # results/_w228bmc_20261013_probe_receipt.json @ " + w228_receipt_sha[:10] + ");",
"    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10",
"    # ~23:1x; deletion-set EMPTY; delivery window = chain-order",
"    # splice AFTER the bm-c W227 five-face (freeze " + w227_freeze_sha[:10] + ") + W227",
"    # finalize product landed (n1_w227_results.json present, ledger",
"    # head " + str(w227_total) + " machine-read at freeze time); zero --no-verify;",
"    # the W228 seat MSG sits in " + seat_found + " at freeze",
"    # time, honest archived per S7 law);",
"    # band gate ADMIT results/_w228bmc_20261013_probe_receipt.json: A = FIRST-CLEAN",
"    # past the registered W227 B band (arithmetic continuation",
"    # " + fmt(w227_a_tail + 1) + ".." + fmt(w227_a_tail + 2_000) + " REFUSED at its own start by the W227 B band",
"    # " + fmt(W227["b_exit"][0]) + ".." + fmt(w227_b_tail) + ", exactly as the W227 seat leg4",
"    # projection anticipated);",
"    # honest forward walk hops=1 -> " + fmt(a_lo) + ".." + fmt(a_hi) + ", non-rotational",
"    # r587 forward-monotone walk; A base == prior-wave B tail+1",
"    # (" + fmt(w227_b_tail) + "+1) machine-checkable -- A-hops-prior-B staircase",
"    # EIGHTY-EIGHTH instance, E36 card (probe receipt leg1 A_semantics",
"    # machine-read ordinal, never transcribed);",
"    # B = FIRST-CLEAN past the own-wave A window (arithmetic",
"    # continuation " + fmt(a_lo) + ".." + fmt(a_lo + 199) + " CLEAN on the registered",
"    # universe but lands INSIDE the W228 A band window " + fmt(a_lo) + ".." + fmt(a_hi) + " --",
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
"    # W229+ projection (gate-derived pre-seat probe leg4, pre-W228",
"    # universe): A naive first-clean " + rec["legs"]["leg4"]["W228p_A"] + " CLEAN hops=" + str(rec["legs"]["leg4"]["hops_A"]) + " /",
"    # B naive first-clean " + rec["legs"]["leg4"]["W228p_B"] + " CLEAN hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " -- naive B lands",
"    # INSIDE the naive A window and the registered W228 B band",
"    # " + fmt(b_lo) + ".." + fmt(b_hi) + " will refuse the naive W229 A window; W229 freezer",
"    # MUST re-derive on the post-W228 universe AND reserve the",
"    # own-wave A window when deriving B (W141 precedent, leg2 law,",
"    # E36 staircase card, EIGHTY-NINTH instance anticipated; never transcribe r587).",
])
pf_row = (f'{ROW_I}228: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), '
          f'"b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'
          + PF_EOL + f'{ROWC_I}"engine_owner": "bm-c"}},' + PF_EOL)
# belt-and-braces: display form must equal the canonical W-family text
assert pf_row.split(PF_EOL)[0].strip() == \
    f'228: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), "b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'

old_pf = must(pf_t, (w227_own_line + PF_EOL + '}'
                     + PF_EOL + '# v1 + ext(wave-1) in-use bands'), 1, "pf_close")
new_pf = (w227_own_line + PF_EOL
          + pf_comment + PF_EOL + pf_row
          + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands')
pf_t2 = pf_t.replace(old_pf, new_pf, 1)

# ---------- n1 cfg entry (programmatic quote wrapping, r761 law) ----------
fin_face = (f"W1..W227 finalize ALL LANDED (W227 finalize product present at splice, "
            f"net chain head {w227_total} machine-read, merged pool K={w227_merged_n} "
            f"machine-read) -- ZERO in-flight upstream seats at splice time, clean precondition; "
            f"downstream W229 seat NOT yet published (queue-deepen seat-chain mandate "
            f"O-20261011-0012 sec.ii -- next seat publication follows per seat-first law)")
cfg_lines = [
 f'{CFG_I}228: {{"batch": "PERPETUAL-N1-W228",',
 f'{PRE_KEY_I}"prereg": ("research/PERPETUAL_N1_W228_PREREG.md (wave-level frozen "',
]
PRE = [
 "pre-run; design = frozen v1 null calibration verbatim, ",
 "new seed bands only; TWO HUNDRED AND TWENTY-EIGHTH ENGINE-OWNED WAVE ",
 f"BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate), ",
 "own-series continuation per O-20260101-2355 sec.2 (first-free-",
 "number law after the REGISTERED W227 row five-face freeze (own seat published MSG-20261013-0645-bmc, executed bm-c r956 dead window, estate absorbed by r956-absorb 1e5ed3326; engine self-burn 12/12; finalize one-pass r956 06:5x; six-gate PRE-FINALIZE correct phase standing law held), ",
 f"{w227_freeze_sha[:10]} (prereg {w227_prereg_sha[:10]}), SINGLE STATE zero seat gap W2..W227 all ",
 "registered; " + fin_face + "; ",
 "seat published=reserved ",
 "MSG-20261013-0720-bmc PUSHED to origin " + SEAT_ORIGIN + " ",
 "BEFORE this freeze per r565 early-visibility law (payload = ",
 "seat MSG + pre-seat probe script + probe receipt @ r957 window; per-wave prereg ",
 "r958 + freeze splice script landed in this r959 freeze-window bundle ",
 f"commit {w228_prereg_sha[:10]} @ receipt {w228_receipt_sha[:10]}); ",
 "deletion-set EMPTY; delivery window = chain-order splice ",
 "after the W227 five-face + W227 finalize product landed ",
 "(executed in the bm-c loop r959 freeze window ",
 "under the CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED ",
 "2026-10-10 ~23:1x); zero merge at freeze delivery, zero ",
 "--no-verify; single-window derive -- r812 merged the gate ",
 "legs INTO the pre-seat probe; parity N/A honest), ",
 "engine_owner=bm-c, wave 228: ",
 "A = FIRST-CLEAN past the registered W227 B band (the ",
 f"arithmetic continuation {fmt(w227_a_tail + 1)}..{fmt(w227_a_tail + 2_000)} is REFUSED at its ",
 f"own start by the W227 B band {fmt(W227['b_exit'][0])}..{fmt(w227_b_tail)}, exactly as ",
 "the W227 seat leg4 succession ",
 "projection notes anticipated; honest forward walk hops=1 -> ",
 f"{fmt(a_lo)}..{fmt(a_hi)}; A base == prior-wave B tail+1 ",
 "machine-checkable = A-hops-prior-B staircase EIGHTY-SEVENTH ",
 "instance, E36 card (probe receipt leg1 machine-read ordinal); ",
 "non-rotational r587 forward-monotone walk) + B = FIRST-CLEAN ",
 "past the own-wave A window (the arithmetic continuation ",
 f"{fmt(a_lo)}..{fmt(a_lo + 199)} is CLEAN on the registered universe but lands ",
 f"INSIDE the W228 A band window {fmt(a_lo)}..{fmt(a_hi)} -- same-freeze mutual ",
 "exclusion, W141 precedent, leg2 law -- the walk with the ",
 f"own-wave A window reserved jumps to {fmt(b_lo)}, first-clean ",
 f"{fmt(b_lo)}..{fmt(b_hi)} hops=1, non-rotational r587 forward-monotone walk; ",
 "B base == own-wave A tail+1 machine-checkable; cross-window ",
 "convergence with the W227 seat leg4 succession projection ",
 "notes -- all MANDATORY notes honored (post-W227 universe ",
 "re-derive + own-wave A reservation); ADMIT receipt ",
 "results/_w228bmc_20261013_probe_receipt.json + ",
 "seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a ",
 "ADMIT convention); W229+ projection per this window gate: ",
 f"A naive first-clean {rec['legs']['leg4']['W228p_A']} CLEAN / B naive first-clean ",
 f"{rec['legs']['leg4']['W228p_B']} CLEAN -- naive B lands INSIDE the naive A window and ",
 f"the registered W228 B band {fmt(b_lo)}..{fmt(b_hi)} will refuse the naive W229 A window; ",
 "W229+ freezer MUST re-derive on the post-W228 universe AND ",
 "reserve the own-wave A window when deriving B (W141 precedent, ",
 "leg2 law, E36 staircase card, EIGHTY-NINTH instance anticipated) -- ",
 "downstream W229 seat publication pending per seat-first law; " + fin_face + " -- the finalize ",
 "merge loop still derives the wave set from registry keys at ",
 "run time, FAIL-CLOSED r307 always on)",
]
for i, s in enumerate(PRE):
    if i == len(PRE) - 1:
        cfg_lines.append(f'{PRE_I}"{s}"),')
    else:
        cfg_lines.append(f'{PRE_I}"{s}"')
cfg_lines += [
 f'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W228 A: {fmt(a_lo)}..{fmt(a_hi)} (FIRST-CLEAN past the registered W227 B band; arithmetic {fmt(w227_a_tail + 1)}..{fmt(w227_a_tail + 2_000)} REFUSED at own start by the W227 B band {fmt(W227["b_exit"][0])}..{fmt(w227_b_tail)}; hops=1; A-hops-prior-B staircase EIGHTY-EIGHTH instance, E36 card; ordinal machine-read EIGHTY-SEVENTH per probe receipt)',
 f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W228 B: {fmt(b_lo)}..{fmt(b_hi)} (FIRST-CLEAN past the own-wave A window; arithmetic {fmt(a_lo)}..{fmt(a_lo + 199)} lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
 f'{MEM_I}"shard_subdir": "n1_w228", "out_name": "n1_w228_results.json",',
 f'{MEM_I}"engine_owner": "bm-c"}},',
]
cfg_block = EOL.join(cfg_lines)
old_cfg = must(n1_t, ('                       }' + EOL
                      + 'PREREG = WAVE_CONFIGS[2]["prereg"]'), 1, "n1_cfg_close")
new_cfg = (cfg_block + EOL
           + '                       }' + EOL
           + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
assert new_cfg.count('228: {"batch": "PERPETUAL-N1-W228"') == 1
n1_t2 = n1_t.replace(old_cfg, new_cfg, 1)

# ---------- n1 materializer block ----------
hdr = [
 "    # --- W228 materializer face (bm-c loop five-face freeze splice,",
 "    #     own-series law under CEO fill-order standing 2026-10-08 ~23:5x",
 "    #     + RE-ISSUE 2026-10-10 ~23:1x + O-20260909-2334-bm-b sec.1-2",
 "    #     local-full-use + O-20260924-1730 claim-and-start same-round law):",
 "    #     bm-c's fifty-eighth owned per machine-derive (engine_owner==bm-c",
 "    #     rows 57 + candidate; seat-time live face 58th = r957 probe leg0",
 "    #     live derive governs); wave 228 = first free number after the",
 "    #     REGISTERED W227 row (five-face freeze " + w227_freeze_sha[:10] + "; own seat published",
 "    #     MSG-20261013-0645-bmc, executed bm-c r956 dead window, estate absorbed",
 "    #     by r956-absorb 1e5ed3326; engine self-burn 12/12 + finalize one-pass r956 06:5x splice",
 "    #     estate + PRE-FINALIZE six-gate chain (standing law held, W212-pattern",
 "    #     zero recurrence -- THIS W228 cycle runs PRE-FINALIZE likewise), honest note)",
 "    #     -- SINGLE STATE zero seat gap (W2..W227 all registered). Seat",
 "    #     published=reserved MSG-20261013-0720-bmc pushed",
 "    #     to origin " + SEAT_ORIGIN + " BEFORE this freeze, r565 law (payload =",
 "    #     seat MSG + pre-seat probe script + probe receipt @ r957 window; per-wave prereg",
 "    #     r958 + freeze splice script landed in this r959 freeze-window bundle",
 "    #     commit " + w228_prereg_sha[:10] + "; deletion-set EMPTY; delivery window",
 "    #     = chain-order splice after the W227 five-face + W227 finalize",
 "    #     product landed; zero --no-verify; the W228 seat MSG sits in",
 "    #     " + seat_found + " at freeze time, honest archived",
 "    #     per S7 law).",
 "    #     TWO HUNDRED AND TWENTY-EIGHTH engine wave BY",
 "    #     MACHINE-DERIVE (engine_owner rows 217 + candidate; gate",
 "    #     leg0 machine output governs per r359 law).",
 f"    #     {fin_face}; the finalize merge loop",
 "    #     still derives the wave set from registry keys at run",
 "    #     time, FAIL-CLOSED r307 always on. ADMIT receipt",
 "    #     results/_w228bmc_20261013_probe_receipt.json;",
 "    #     seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a",
 f"    #     ADMIT convention upgrade): {gate_lines[0]}; {gate_lines[1]};",
 "    #     banned gate ADMIT 0 (re-run at freeze window);",
 "    #     not a re-pick (R250: W228 bands were never assigned).",
 "    _set_wave(228)",
 "    try:",
 '        assert WAVE_CONFIGS[227]["a_seed_base"] == pf.N1_BANDS[227]["a"][0], \\',
 '            "W228 upstream W227 mirror drift (a)"',
 "        assert WAVE_CONFIGS[227][\"b_exit_seed_base\"] == \\",
 '            pf.N1_BANDS[227]["b_exit"][0], "W228 upstream W227 mirror drift (b)"',
 "        assert WAVE_CONFIGS[227].get(\"engine_owner\") == \\",
 '            pf.N1_BANDS[227].get("engine_owner") == "bm-c", \\',
 '            "W228 upstream W227 engine_owner mirror drift (law-mirror parity; bm-c own-seat face)"',
 "        w227_a = {A_SEED_BASE + j for j in range(A_N)}",
 "        w227_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
 '        assert not (w227_a & w227_b), "W228 A/B band overlap"',
 "        assert not (w227_a & reg_ints) and not (w227_b & reg_ints), \\",
 '            "W228 hits SEED_REGISTRY"',
 '        for nm, band in (("A", w227_a), ("B", w227_b)):',
 '            assert not (band & v1_a) and not (band & v1_b), f"W228 {nm} hits v1"',
 '            assert not (band & w1_a) and not (band & w1_b), f"W228 {nm} hits W1"',
 '            assert not (band & probes), f"W228 {nm} hits probe seeds"',
]
w227_leg = [
 f'        assert pf.N1_BANDS[227] == {{"a": ({fmt(pf_mod.N1_BANDS[227]["a"][0])}, {fmt(pf_mod.N1_BANDS[227]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[227]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[227]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\',
'            "registered W227 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]
w225_leg = [
 f'        assert pf.N1_BANDS[225] == {{"a": ({fmt(pf_mod.N1_BANDS[225]["a"][0])}, {fmt(pf_mod.N1_BANDS[225]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[225]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[225]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\',
'            "registered W225 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]
w226_leg = [
 f'        assert pf.N1_BANDS[226] == {{"a": ({fmt(pf_mod.N1_BANDS[226]["a"][0])}, {fmt(pf_mod.N1_BANDS[226]["a"][1])}),',
 f'                                    "b_exit": ({fmt(pf_mod.N1_BANDS[226]["b_exit"][0])}, {fmt(pf_mod.N1_BANDS[226]["b_exit"][1])}),',
'                                    "engine_owner": "bm-c"}, \\',
'            "registered W226 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"',
]
tail = [
 "        # prior-wave disjointness W2..W227 (single state: all",
 "        # registered, dynamic registry derive, r511 law)",
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 228):",
 '            assert not (w227_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
 "                                 for j in range(A_N)}), f\"W228 A hits W{wprev}\"",
 '            assert not (w227_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
 "                                  for j in range(B_N)}), f\"W228 B hits W{wprev}\"",
 "        n3r1_used228 = set(range(70_000, 70_006))",
 "        assert not (w227_a & n3r1_used228) and not (w227_b & n3r1_used228), \\",
 '            "W228 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
 "        assert not (w227_a & lfc_actual12) and not (w227_b & lfc_actual12), \\",
 '            "W228 bands must clear the lfc actual draw range"',
 "        assert not (w227_a & options_actual12) and \\",
 "            not (w227_b & options_actual12), \\",
 '            "W228 bands must clear the options_wave2 actual draw range"',
 "        # band facts (law sec.4 W228 row): A = FIRST-CLEAN past",
 "        # the registered W227 B band (the arithmetic continuation",
 f"        # {fmt(w227_a_tail + 1)}..{fmt(w227_a_tail + 2_000)} is REFUSED at its own start by the W227 B band",
 f"        # {fmt(W227['b_exit'][0])}..{fmt(w227_b_tail)}, exactly as the W227 seat leg4",
 "        # succession projection notes anticipated; honest",
 f"        # forward walk hops=1 lands {fmt(a_lo)}..{fmt(a_hi)}; A base ==",
 f"        # prior-wave B tail+1 ({fmt(w227_b_tail)}+1) machine-checkable --",
 "        # A-hops-prior-B staircase EIGHTY-EIGHTH instance, E36 card;",
 "        # non-rotational r587 forward-monotone walk);",
 "        # B = FIRST-CLEAN past the own-wave A window (the",
 f"        # arithmetic continuation {fmt(a_lo)}..{fmt(a_lo + 199)} is CLEAN on the",
 f"        # registered universe but lands INSIDE the W228 A band window",
 f"        # {fmt(a_lo)}..{fmt(a_hi)} -- same-freeze mutual exclusion (W141 precedent,",
 "        # leg2 law) -- the walk with the own-wave A window reserved",
 f"        # jumps to {fmt(b_lo)} and lands {fmt(b_lo)}..{fmt(b_hi)}, hops=1,",
 "        # non-rotational r587 forward-monotone walk; B base ==",
 f"        # own-wave A tail+1 ({fmt(a_hi)}+1) machine-checkable;",
 "        # cross-window convergence with the W227 seat leg4",
 "        # succession projection notes -- all MANDATORY notes",
 "        # honored (post-W227 universe re-derive + own-wave A",
 "        # reservation when deriving B);",
 "        # seat MSG-1228 tail, re-derived).",
 f'        assert WAVE_CONFIGS[228]["a_seed_base"] == {a_lo} == {w227_b_tail} + 1, (',
 '            "W228 A must be the first-clean window past the registered "',
 '            "W227 B band tail (arithmetic continuation REFUSED at its own "',
 '            "start by the W227 B band, exactly as the W227 seat leg4 "',
 '            "succession projection notes anticipated; honest forward walk "',
 '            "hops=1; A base == prior-wave B tail+1 machine-checkable "',
 '            "= A-hops-prior-B staircase EIGHTY-EIGHTH instance, E36 card")',
 f"        arith_a228 = set(range({a_lo}, {a_hi + 1}))",
 "        assert not (arith_a228 & reg_ints), \\",
 '            "W228 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
 f'        assert WAVE_CONFIGS[228]["b_exit_seed_base"] == {b_lo} == {a_hi} + 1, (',
 '            "W228 B must be the first-clean window past the own-wave A "',
 '            "band tail (arithmetic continuation CLEAN on the registered "',
 '            "universe but lands INSIDE the W228 A band window; "',
 '            "same-freeze mutual exclusion (W141 precedent, leg2 law) -- "',
 '            "the walk with the own-wave A window reserved jumps, "',
 '            "first-clean hops=1, non-rotational r587 forward-monotone "',
 '            "walk; B base == own-wave A tail+1 machine-checkable)")',
 f"        arith_b228 = set(range({b_lo}, {b_hi + 1}))",
 "        assert not (arith_b228 & reg_ints), \\",
 '            "W228 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
 "        assert not (arith_b228 & arith_a228), \\",
 '            "W228 A/B same-freeze mutual exclusion (B hops past own A)"',
 "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W228-SHARD-0\",",
 '                                          "n1w228-0of12"), "W228 entry identity"',
 '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W228-SHARD-11",',
 '                                           "n1w228-11of12")',
 "        assert SHARD_DIR.endswith(\"n1_w228\") and OUT.endswith(",
 '            "n1_w228_results.json"), "W228 path drift"',
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 228):",
 "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(",
 "                PATHS.results_dir, \"p2cal_ext\",",
 "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\",
 '                f"W228 shard dir collides with W{wprev}"',
 "        # W228 finalize cumulative deps: W17..W227 outputs ALL PRESENT",
 f"        # (landed net chain head {w227_total} machine-read at freeze time)",
 "        # -- ZERO in-flight upstream seats at splice, clean precondition",
 "        # freeze window; the finalize merge loop derives the wave",
 "        # set from registry keys at run time and stays",
 "        # FAIL-CLOSED, r307 two-state law).",
 "        for _depw in range(17, 228):",
 "            assert os.path.exists(os.path.join(",
 "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\",
 '                f"W228 finalize cumulative dep (W{_depw} output) missing"',
 "        # finalize wave-set derivation face (r511 derive law): every",
 "        # registered wave below 228 composes; wave 15 excluded by",
 "        # design; SINGLE STATE (W2..W227 all registered -- no",
 "        # two-state seat disclosure needed at this freeze).",
 "        assert sorted(w for w in WAVE_CONFIGS if w < 228) == \\",
 "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\",
 "            [w for w in range(16, 228)], \\",
 '            "W228 prior-wave set must derive from registry keys (no 15; " \\',
 '            "W2..W227 registered single state)"',
 "        assert os.path.exists(os.path.join(",
 '            PATHS.root, "research", "PERPETUAL_N1_W228_PREREG.md")), \\',
 '            "W228 per-wave prereg missing (materializer requirement)"',
 "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"",
 "    finally:",
 "        _set_wave(2)",
]
block = EOL.join(hdr) + EOL + par_sec + EOL.join(w225_leg) + EOL + EOL.join(w226_leg) + EOL + EOL.join(w227_leg) + EOL + EOL.join(tail) + EOL
# family #6 atomic triple gate (carried forward): the new
# block's LHS w<227 / RHS range(16,227)/range(17,227) / comment below-227 MUST move together.
assert block.count("if w < 228)") == 3, f"family-6 triple: w<228 count {block.count('if w < 228)')} != 3"
assert block.count("if w < 227") == 0, "family-6 triple: stale w<227 leaked into the W228 block"
assert block.count("range(16, 228)") == 1 and block.count("range(17, 228)") == 1, "family-6 triple: RHS ranges wrong"
assert block.count("registered wave below 228 composes") == 1, "family-6 triple: comment face wrong"
old_blk_anchor = must(n1_t2, "    # --- T-141 s2 lane face", 1, "t141_marker")
n1_t3 = n1_t2.replace(old_blk_anchor, block + old_blk_anchor, 1)

# ---------- n1 print line ----------
pr = [
 '          "+ W228 materializer face [same guard set, dep=W17..W227 "',
 f'          "outputs ALL PRESENT (landed net chain head {w227_total} = W227 bm-c finalize one-pass, K={w227_merged_n} merged pool) -- ZERO "',
 '          "in-flight upstream seats at splice, clean precondition, TWO HUNDRED AND TWENTY-EIGHTH "',
 f'          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} "',
 '          "+ candidate) bm-c\'s fifty-eighth owned claim per "',
 '          "machine-derive (engine_owner==bm-c rows 57 + candidate; seat-time live face 58th disclosed, "',
 '          "live derive at freeze governs), "',
 '          "A=FIRST-CLEAN past the registered W227 B band (staircase "',
 '          "EIGHTY-EIGHTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
 '          "own-wave A window (W141 precedent, leg2 law, same-freeze "',
 '          "mutual exclusion, hops=1), chain-order splice from the "',
 '          "committed ADMIT receipt + seed_admit_gate rc0 both bands FREE "',
 '          "(O-20261010-1945-bm-a ADMIT convention), "',
 '          "ADMIT receipt "',
 '          "results/_w228bmc_20261013_probe_receipt.json, law sec.4 W228 row, "',
 '          "bm-c loop CEO fill-order RE-ISSUE 23:1x] "',
]
old_pr = must(n1_t3, '          "+ T-141 s2 ', 1, "print_t141")
n1_t4 = n1_t3.replace(old_pr, EOL.join(pr) + EOL + old_pr, 1)

# ---------- post-edit count gates ----------
assert n1_t4.count('"batch": "PERPETUAL-N1-W228"') == 1
assert n1_t4.count("# --- W228 materializer face") == 1     # block header
assert n1_t4.count('"+ W228 materializer face') == 1        # print fragment
assert n1_t4.count('228: {"batch": "PERPETUAL-N1-W228"') == 1
assert pf_t2.count(ROW_I + '228: {"a"') == 1
assert pf_t2.count('"engine_owner": "bm-c"},' + PF_EOL + '}') == 1
assert n1_t4.count('    # --- T-141 s2 lane face') == 1
assert n1_t4.count('"PERPETUAL-N1-W228-SHARD-0"') == 1
assert n1_t4.count(f'assert pf.N1_BANDS[227] == {{"a": ({fmt(pf_mod.N1_BANDS[227]["a"][0])}, {fmt(pf_mod.N1_BANDS[227]["a"][1])}),') == 1
assert n1_t4.count('    # --- W209 materializer face') == 1  # estate source block kept
assert n1_t4.count('    # --- W210 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W211 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W212 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W213 materializer face') == 1  # prior block kept
assert n1_t4.count('    # --- W214 materializer face') == 1  # prior block kept (W214 splice landed r910 window)
assert n1_t4.count('    # --- W215 materializer face') == 1  # prior block kept (W215 splice landed r912 window)
assert n1_t4.count('    # --- W216 materializer face') == 1  # prior block kept (W216 splice landed r914 window)
assert n1_t4.count('    # --- W217 materializer face') == 1  # prior block kept (W217 splice landed r916 window)
assert n1_t4.count('    # --- W218 materializer face') == 1  # prior block kept (W218 splice landed r918 window)
assert n1_t4.count('    # --- W219 materializer face') == 1  # prior block kept (W219 splice landed r920 window)
assert n1_t4.count('    # --- W220 materializer face') == 1  # prior block kept (W220 splice landed r923 window)
assert n1_t4.count('    # --- W221 materializer face') == 1  # prior block kept (W221 splice landed r927 window)
assert n1_t4.count('    # --- W222 materializer face') == 1  # prior block kept (W222 splice landed r931 window)
assert n1_t4.count('    # --- W223 materializer face') == 1  # prior block kept (W223 splice landed r934 window)
assert n1_t4.count('    # --- W224 materializer face') == 1  # prior block kept (W224 splice landed r937 dead window)
assert n1_t4.count('    # --- W225 materializer face') == 1  # prior block kept (W225 splice landed r939 freeze window)
assert n1_t4.count('    # --- W226 materializer face') == 1  # prior block kept (W226 splice landed r943 dead window, estate absorbed r945)
assert n1_t4.count('    # --- W227 materializer face') == 1  # prior block kept (W227 splice landed r956 dead window, estate absorbed by r956-absorb 1e5ed3326)
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
  "machine": "bm-c", "wave": 228,
  "phase": "five-face freeze chain-order splice (r959 freeze window, upstream ALL LANDED clean precondition)",
  "origin_base": omain,
  "pf_sha16_pre": hashlib.sha256(pf_b).hexdigest()[:16],
  "n1_sha16_pre": hashlib.sha256(n1_b).hexdigest()[:16],
  "pf_sha16_post": hashlib.sha256(pf_t2.encode("utf-8")).hexdigest()[:16],
  "n1_sha16_post": hashlib.sha256(n1_t4.encode("utf-8")).hexdigest()[:16],
  "bands": {"A": A, "B": B, "a_lo": a_lo, "a_hi": a_hi, "b_lo": b_lo, "b_hi": b_hi},
  "admit_receipt": "results/_w228bmc_20261013_probe_receipt.json",
  "seed_admit_gate": gate_lines,
  "banned_gate": "ADMIT rc0 (re-run at freeze window)",
  "w227_upstream": {"freeze_sha": w227_freeze_sha, "prereg_sha": w227_prereg_sha,
                    "ledger_total": w227_total, "merged_n": w227_merged_n,
                    "engine_owner": "bm-c (own seat honored, no takeover face)",
                    "repair_chain_note": "r956 splice (W227 freeze landed 48c321706 dead window, estate absorbed by r956-absorb 1e5ed3326) + engine self-burn 12/12 + r956 finalize one-pass 06:5x (six-gate PRE-FINALIZE correct phase -- standing law held)"},
  "w225_transitive": {"finalize_product": "results/perpetual_faces/n1_w225_results.json present (belt-and-braces gate; ledger 918,789 / K=492,920)"},
  "w224_transitive": {"finalize_product": "results/perpetual_faces/n1_w224_results.json present (belt-and-braces gate; ledger 916,589 / K=490,720)"},
  "w223_transitive": {"finalize_product": "results/perpetual_faces/n1_w223_results.json present (belt-and-braces gate; ledger 914,389 / K=488,520)"},
  "w226_transitive": {"finalize_product": "results/perpetual_faces/n1_w226_results.json present (belt-and-braces gate; ledger 920,989 / K=495,120)"},
  "seat": seat_found + " (origin " + SEAT_ORIGIN + ")",
  "prereg_bundle": {"prereg_sha": w228_prereg_sha, "probe_receipt_sha": w228_receipt_sha,
                    "note": "prereg derived+committed in the r958 window (e6c8441aa, TWELVE-level lineage replay chain, preflight 46/46); splice editor derived from the committed W227 editor template by count-asserted ordered transform (protect-restore regions, fail-closed pair law) in this same r959 freeze window; upstream W227 already landed (clean-precondition seventeenth consecutive window); zero transcription"},
  "ordinal_faces": {"owner_rows_live": len(owner_rows_live), "bmc_rows_live": len(bmc_rows_live),
                    "engine_owned_ordinal": len(owner_rows_live) + 1,
                    "bmc_own_ordinal": len(bmc_rows_live) + 1,
                    "probe_receipt_bmc_ordinal_face": 58,
                    "note": "post-W228 registration: bm-c rows 57 + candidate = 58th owned (live derive at freeze time governs per r587/r359; probe leg0 bmc_ordinal=58 = r957 seat-time live face -- disclosed honest)"},
  "parity_section": {"source": "OWN W227 block physical bytes (own splice generation, structure known exactly)",
                    "bytes": len(par_sec),
                    "row_asserts": par_sec.count("assert pf.N1_BANDS["),
                    "note": "full-span estate W138..W206 (69 rows, r858 absorb generation) + W211..W224 legs + W225 leg + W226 leg + W227 leg -> W228 block = 86 rows ending at W227; disclosed: (a) inherited W213 leg error-string face (\"registered W212 row parity drift\") preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact); (b) prereg block-30 prose carries the lineage one-wave-behind \"块\" face (mechanical aging, r927 fixB family) while this editor extracts from the OWN W227 block -- parity list face exact, zero functional impact"},
  "family6_triple_gate": {"absorbed": True,
                          "note": "W227 editor family-6 gate carried forward: new block LHS w<228 x3 / RHS range(16,228)+range(17,228) / comment below-228 count-asserted ATOMICALLY before splice; W227 block's own w<227 face = legitimate prior-wave boundary (not stale)"},
  "eol": {"n1_crlf": EOL == "\r\n", "pf_crlf": PF_EOL == "\r\n"},
  "liveness_anchors": {"t141_marker_kept": 1, "w209_block_kept": 1, "w210_block_kept": 1, "w211_block_kept": 1, "w212_block_kept": 1, "w213_block_kept": 1, "w214_block_kept": 1, "w215_block_kept": 1, "w216_block_kept": 1, "w217_block_kept": 1, "w218_block_kept": 1, "w219_block_kept": 1, "w220_block_kept": 1, "w221_block_kept": 1, "w222_block_kept": 1, "w223_block_kept": 1, "w224_block_kept": 1, "w225_block_kept": 1, "w226_block_kept": 1, "w227_block_kept": 1},
}
open(RECEIPT_OUT, "w", encoding="utf-8").write(json.dumps(receipt, indent=1))
print(json.dumps({k: receipt[k] for k in
      ("phase", "origin_base", "pf_sha16_post", "n1_sha16_post", "bands",
       "w227_upstream")}, indent=1))
print("SPLICE OK -- py_compile both green; NEXT: selftest (default wave, r522 law) -> pathspec commit+push -> PRE-FINALIZE six-gate (W212-pattern standing law) -> ignition verify (2-cycle n1_w228 growth)")
