# -*- coding: utf-8 -*-
# 2026-10-16 07:5x bm-c r1046 freeze window (upstream W1..W249 ALL LANDED, clean
# precondition -- W249 finalize one-pass bm-c r1043 window closeout 05:5x,
# ledger head 972,135 / K=545,720 machine-read): W250 five-face freeze splice
# editor -- bm-c OWN-SEAT face (seat MSG-20261016-055x-bmc-w250-seat
# published=reserved by bm-c itself @ origin cc06f1f4a r1043, pre-seat probe
# ADMIT receipt results/_w250bmc_20261016_probe_receipt.json same payload;
# the W250 seat was published AFTER the W249 five-face + finalize landing
# (queue-head supply -- W249 complete at publish, ZERO waits-upstream face;
# bm-c r1042 splice + r1043 finalize one-pass ledger 972,135 / K=545,720)); zero DRAFT marker; per-wave prereg
# PERPETUAL_N1_W250_PREREG.md derived by the bm-c r1045 window (machine-SUB from the frozen W249 template)
# (authored 07:2x, banned_direction_gate ADMIT rc0, committed+pushed same window 4f7a130ff).
# Lineage: _w249bmc_freeze_edits.py template (proven live-fire freeze, bm-c
# r1042 splice window; engine self-burn 12/12 + finalize one-pass verified r1043)
# + r787 preflight law + r609 origin-verbatim base + r761 programmatic quote
# wrapping + r909 physical-byte anchors + r838 per-file EOL detection
# + family #6 LHS/RHS/comment ATOMIC TRIPLE (the new block's w<250>/
# range(16,250)/range(17,250)/below-250 quadruple is count-asserted
# atomically; the W249 block's own w<249> face is legitimate prior-wave
# boundary, not stale) + E63 heal lineage (arith_a250/arith_b250
# define+assert consistent; band-set variable aging face continues:
# w244_a holds wave-250 bands, disclosed).
# NEW FACE vs the W249 editor (honest disclosure, frozen W250 prereg sec.3
# mandate): BOTH bands take the CLEAN-hops=0 face -- A = FIRST-CLEAN
# arithmetic continuation of the prior-wave A tail (565_501..567_500, naive
# start CLEAN on the post-W249-REGISTERED universe, hops=0, A_hop_chain
# empty + A_clean_at_naive_start=true, seed-decoupled A-continuation face,
# THIRTEENTH consecutive seed-gap face, anticipated by the W249 probe leg4 +
# seat leg4 and confirmed live); B = CLEAN arithmetic continuation of the
# prior-wave B tail (545_101..545_300, hops=0, B_naive_hops=0, B_hop_chain
# empty + B_clean_at_naive_start=true, past the W239 staircase band-hop
# landing -- the registered W239 A band 542_501..544_500 and the registered
# W247/W248/W249 B bands all sit below the walk start; B lands
# OUTSIDE the own-A window 565_501..567_500; B base == prior-wave B tail+1
# (545_100+1) EXACT; B_no_ownA_jump=true; B_hop_lands_inside_A=false).
# PARITY STRUCTURAL CHOICE (frozen W250 prereg sec.3 mandate, verbatim):
# the parity estate (W138..W206 69-row full-span, r858 absorb generation)
# is extracted from the OWN W249 block physical bytes (structure known
# exactly, extraction self-asserts the 69-row range identity); the W249
# block's own W238..W248 legs (11 rows) do NOT enter the estate path;
# after extraction, fresh W238..W249 legs (12 rows) are added,
# machine-derived from the LIVE pf registry at freeze time -> W250 block
# parity = 108 rows (W138..W206 + W211..W249). Zero assumption zero risk.
# Zero hardcoded upstream band values: ALL W249 facts machine-derived from the
# LIVE pf import at freeze time (the registered W249 row -- bm-c own seat
# honored), cross-checked against the committed ADMIT receipt
# (results/_w250bmc_20261016_probe_receipt.json) which was derived on the
# post-W249-REGISTERED universe with the W250 candidate bands treated as
# reserved refusers (now REGISTERED verbatim -- values identical, disclosed).
# If the LIVE W249 bands differ from the declared face, the continuation
# asserts fail LOUD (fail-closed).
# Own bundle hashes (prereg/probe receipt) derived via pickaxe, never transcribed.
# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.
import json, hashlib, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PF = os.path.join(REPO, "scripts", "perpetual_faces.py")
N1 = os.path.join(REPO, "scripts", "perpetual_faces_n1.py")
RECEIPT_IN = os.path.join(REPO, "results", "_w250bmc_20261016_probe_receipt.json")
RECEIPT_OUT = os.path.join(REPO, "results", "_w250bmc_freeze_receipt.json")
SEAT_MSG = "MSG-20261016-055x-bmc-w250-seat.md"
SEAT_ORIGIN = "cc06f1f4a"
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

# ---------- gate 0.5: W249 five-face landed + W249 finalize product present ----------
# (chain-order precondition; belt-and-braces transitive window W235..W244 checked
# here + enforced by the block's cumulative-deps assert range(17, 250) at selftest time)
W249 = dict(pf_mod.N1_BANDS.get(249) or {})
assert W249.get("engine_owner") == "bm-c", \
    f"W249 row not landed as declared (bm-c seat owner expected): {W249} -- five-face freeze missing;" \
    " if an unexpected face exists the freeze window MUST re-derive this editor honestly"
w249_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w249_results.json")
assert os.path.exists(w249_out_path), "W249 finalize product missing (n1_w249_results.json) -- chain dep not met"
for _w in (246, 245, 244, 243, 242, 241, 240, 239, 238, 237):
    assert os.path.exists(os.path.join(REPO, "results", "perpetual_faces", f"n1_w{_w}_results.json")), \
        f"W{_w} finalize product missing (transitive chain dep) -- abort"
w249_out = json.load(open(w249_out_path, encoding="utf-8"))
w249_led = (w249_out.get("science_gates") or {}).get("ledger") or {}
w249_total = w249_led.get("total")
w249_merged_n = None
try:
    w249_merged_n = w249_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
assert w249_total == 972_135 and w249_merged_n == 545_720, \
    f"W249 finalize anchors drift at freeze time: total={w249_total} merged={w249_merged_n} (expect 972,135 / 545,720)"
# freeze shas machine-derived (pickaxe), never transcribed
r = git("log", "--format=%H", "-S", '249: {"a"', "--", "scripts/perpetual_faces.py")
w249_freeze_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W249_PREREG.md")
w249_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W250_PREREG.md")
w250_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
assert os.path.exists(os.path.join(REPO, "research", "PERPETUAL_N1_W250_PREREG.md")), \
    "W250 per-wave prereg missing on disk -- chain face incomplete, abort (r1035 derive landed pre-freeze expected)"
with open(os.path.join(REPO, "research", "PERPETUAL_N1_W250_PREREG.md"), encoding="utf-8") as _fh:
    _pre_head = _fh.read(2000)
assert "DRAFT-NOT-FROZEN" not in _pre_head, "W250 prereg still DRAFT -- abort (freeze commit pending face)"
# live ordinal derive (r359 law: gate machine output governs; the pre-seat probe
# receipt leg0 face owner_rows=239 / bmc_rows=69 / bmc_ordinal=70
# = seat-time PRE-W250-splice live faces (post-W249-REGISTERED universe,
# upstream complete -- queue-head supply); live derive at freeze time:
# W249 splice LANDED (finalize adds no registry rows) -> owner rows 239 + candidate = 240th EXACT; bm-c rows 69 +
# candidate = 70th EXACT -- bm-c own-seat continuity face (bm-c published the
# W250 seat itself r1043; queue-head supply -- W249 chain complete at publish, ZERO
# waits-upstream face (bm-c r1042 splice + r1043 finalize))
owner_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner")]
bma_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-a"]
bmc_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
assert len(owner_rows_live) == 239 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 69, \
    f"leg0 ordinal drift at freeze time: owner={len(owner_rows_live)} bma={len(bma_rows_live)} bmc={len(bmc_rows_live)} (expect 239/129/69 PRE-splice post-W249 registration; this candidate = bm-c's 70th own wave per the same live-derive law, r587/r359)"
print(f"gate0.5 OK: W249 landed (freeze {w249_freeze_sha[:10]}, owner=bm-c seat honored (upstream W249), queue-head supply, ZERO waits-upstream face), "
      f"W249+W245..W236 finalize products present "
      f"(W249 ledger head {w249_total}, merged n={w249_merged_n}); owner rows {len(owner_rows_live)} + candidate, "
      f"bm-c rows {len(bmc_rows_live)} + candidate (70th own wave per live derive; "
      f"probe receipt leg0 bmc_ordinal=70 = seat-time pre-splice faces disclosed honest)")

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
assert (a_lo, a_hi) == (565_501, 567_500) and (b_lo, b_hi) == (545_101, 545_300), \
    f"W250 band drift vs probe ADMIT: {(a_lo, a_hi)} {(b_lo, b_hi)}"
w249_b_tail = W249["b_exit"][1]      # registered W249 row b_exit hi (pf import, live)
w249_a_tail = W249["a"][1]           # registered W249 row A hi (pf import, live)
# W250 FACE (probe receipt leg1 relation_asserts):
# A keeps the A-continuation base (prior-wave A tail+1 EXACT -- the naive
# arithmetic continuation is CLEAN at its own start, hops=0, A_hop_chain
# empty, A_clean_at_naive_start=true -- thirteenth consecutive seed-gap face per
# the W249 probe leg4 + seat leg4 anticipation confirmed live, frozen receipt
# A_semantics verbatim); B takes the CLEAN arithmetic continuation face
# (prior-wave B tail+1 EXACT, hops=0, B_naive_hops=0, B_hop_chain empty,
# B_clean_at_naive_start=true, past the W239 staircase band-hop landing; the
# registered W239 A band and the registered W247/W248/W249 B bands all sit below the
# walk start); A sits far above the B staircase (seed-decoupled A/B gap,
# thirteenth consecutive); machine-derived from the LIVE registered row, never
# transcribed.
assert w249_a_tail + 1 == a_lo, "A continuation base relation broken (A == prior-wave A tail+1 EXACT)"
assert a_lo > w249_b_tail + 1, "seed-decoupled A-continuation face violated: A base must sit ABOVE prior-B tail+1 (seed-gap)"
assert b_hi < a_lo, "seed-decoupled A/B gap face violated: B window must sit entirely below own-A"
assert W249["b_exit"][1] < W249["a"][0], \
    "upstream W249 row in-wave decoupled relation broken (registered W249 B window must sit below own W249 A window)"
assert leg1.get("hops_A") == 0, "A hop-count drift vs probe receipt leg1 (A band naive hops=0, A-continuation face)"
assert leg1.get("hops_B") == 0, "B hop-count drift vs probe receipt leg1 (B band hops=0, CLEAN arithmetic continuation face)"
assert leg1.get("A_hop_chain") == [] and (
    leg1.get("A_clean_at_naive_start") is True
    or (leg1.get("relation_asserts") or {}).get("A_clean_at_naive_start") is True
), \
    "A hop-chain face drift (fc_a == fc_a_naive, hops=0, A_clean_at_naive_start=true -- naive continuation CLEAN at own start)"
assert leg1.get("B_hop_chain") == [] and leg1.get("B_naive_hops") == 0, \
    "B hop-chain face drift (hops=0, CLEAN arithmetic continuation face -- no band-hop this wave)"
assert leg1.get("B_hop_lands_inside_A") is False, "B lands-inside-own-A drift vs probe receipt leg1 (B_hop_lands_inside_A must be False)"
assert leg1.get("B_naive_first_clean") == [b_lo, b_hi], "B naive first-clean drift vs probe receipt leg1"
ra = leg1.get("relation_asserts") or {}
assert ra.get("A_clean_at_naive_start") and ra.get("A_base_ge_priorB_tail_plus1") \
    and ra.get("B_clean_at_naive_start") and ra.get("B_base_above_W249_tail") \
    and ra.get("AB_mutual_exclusion") and ra.get("B_hop_lands_inside_A") is False \
    and ra.get("W248_W249_bands_respected_A") and ra.get("W248_W249_bands_respected_B"), \
    f"probe receipt leg1 relation_asserts face drift: {ra}"
assert [w249_a_tail + 1, w249_a_tail + 2_000] == leg1["ARITH_A"], \
    f"A-continuation start drift vs probe receipt leg1 ARITH_A: {[w249_a_tail + 1, w249_a_tail + 2_000]} != {leg1['ARITH_A']}"
assert [w249_b_tail + 1, w249_b_tail + 200] == leg1["ARITH_B"], \
    f"B naive continuation drift vs probe receipt leg1 ARITH_B: {[w249_b_tail + 1, w249_b_tail + 200]} != {leg1['ARITH_B']}"

# own bundle shas via pickaxe (self-referencing commit facts, zero transcription)
r = git("log", "--diff-filter=A", "--format=%H", "--", "results/_w250bmc_20261016_probe_receipt.json")
w250_receipt_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
# seat MSG honest location (inbox or processed; S7 archive law)
seat_found = None
for _p in ("fleet/inbox", "fleet/inbox/processed"):
    if os.path.exists(os.path.join(REPO, _p, SEAT_MSG)):
        seat_found = _p + "/" + SEAT_MSG
        break
assert seat_found, f"W250 seat MSG missing from both inbox paths: {SEAT_MSG}"

# ---------- re-run discipline gates at freeze window (banned + seed_admit) ----------
g = subprocess.run([PY, os.path.join(REPO, "Tools", "banned_direction_gate.py"),
                    "--prereg", "research/PERPETUAL_N1_W250_PREREG.md"],
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

def fmt(n):  # 565501 -> "565_501"
    return f"{n // 1000}_{n % 1000:03d}"

# ---------- extract parity estate + kept legs (physical bytes, never re-typed) ----------
# STRUCTURAL CHOICE (frozen W250 prereg sec.3 mandate): extract the 91-row
# estate (W138..W206 full-span 69 rows + W211..W232 legs) AND the W233..W237
# legs (5) from the OWN W249 block physical bytes (bm-c r1042 splice
# generation, committed -- structure known exactly); the W249 block's own
# W238..W248 legs (11) are EXCLUDED from the estate path per the prereg
# mandate; the W250 block appends fresh W238..W249 legs (12, machine-derived
# from the LIVE pf registry at freeze time) -> 108 parity rows.
a22 = '    # --- W249 materializer face'
a_t141 = '    # --- T-141 s2 lane face'
w249_start = n1_t.find(a22); t141_pos = n1_t.find(a_t141)
assert w249_start > 0 and t141_pos > w249_start, \
    "W249 materializer block face not found (W249 freeze not landed? header-text drift -> honest re-derive required)"
blk = n1_t[w249_start:t141_pos]
m_first_row = re.search(r"assert pf\.N1_BANDS\[", blk)
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state", blk)
assert m_first_row and m_disj and m_disj.start() > m_first_row.start(), \
    "parity span markers not found in W249 block"
_row_ls = blk.rfind(EOL, 0, m_first_row.start()) + len(EOL)
par_full = blk[_row_ls:m_disj.start()]
m233 = re.search(r" *assert pf\.N1_BANDS\[233\] ==", par_full)
assert m233, "upstream W233 row leg not found inside W249 parity span"
par_sec = par_full[:m233.start()]
legs_sec = par_full[m233.start():]
assert par_sec.endswith(EOL), "estate segment must end with EOL"
assert legs_sec.endswith(EOL), "legs segment must end with EOL"
_estate_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", par_sec)
assert par_sec.count("assert pf.N1_BANDS[") == 91 \
    and [int(w) for w in _estate_ws[:69]] == list(range(138, 207)) \
    and [int(_estate_ws[69 + i]) for i in range(11)] == [211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221] \
    and [int(_estate_ws[80 + i]) for i in range(9)] == [222, 223, 224, 225, 226, 227, 228, 229, 230] \
    and int(_estate_ws[89]) == 231 \
    and int(_estate_ws[90]) == 232, \
    f"estate segment not W138..W206 full-span 69 rows + W211..W231 legs + W232 leg: n={par_sec.count('assert pf.N1_BANDS[')} range={(_estate_ws[:2], _estate_ws[-4:])}"
assert par_full.count("assert pf.N1_BANDS[") == 107, \
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 107 (91 estate + W233..W248 legs 16)"
_legs_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", legs_sec)
assert legs_sec.count("assert pf.N1_BANDS[") == 16 \
    and [int(w) for w in _legs_ws] == list(range(233, 249)), \
    f"legs segment not W233..W248 sixteen legs: n={legs_sec.count('assert pf.N1_BANDS[')} waves={_legs_ws}"
# prereg sec.3 mandate split: keep W233..W237 verbatim (5 legs); the W249
# block's own W238..W248 legs (11) are excluded from the estate path
m238 = re.search(r" *assert pf\.N1_BANDS\[238\] ==", legs_sec)
assert m238, "W238 leg boundary not found inside W250 legs segment (prereg sec.3 split face)"
legs_kept = legs_sec[:m238.start()]
legs_dropped = legs_sec[m238.start():]
assert legs_kept.endswith(EOL) and legs_dropped.endswith(EOL), "split segments must end with EOL"
_kept_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", legs_kept)
assert legs_kept.count("assert pf.N1_BANDS[") == 5 \
    and [int(w) for w in _kept_ws] == [233, 234, 235, 236, 237], \
    f"kept segment not W233..W237 five legs: n={legs_kept.count('assert pf.N1_BANDS[')} waves={_kept_ws}"
_dropped_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", legs_dropped)
assert legs_dropped.count("assert pf.N1_BANDS[") == 11 \
    and [int(w) for w in _dropped_ws] == list(range(238, 249)), \
    f"dropped segment not W238..W248 eleven legs: n={legs_dropped.count('assert pf.N1_BANDS[')} waves={_dropped_ws}"

# ---------- fresh legs W236..W249 (machine-derived from the LIVE pf registry) ----------
fresh_leg_lines = []
for _w in range(238, 250):
    _row = dict(pf_mod.N1_BANDS[_w])
    _owner = _row["engine_owner"]
    if _w == 249:
        _msg = '"registered W249 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"'
    else:
        _msg = f'"registered W{_w} row parity drift (r307; engine_owner={_owner}; W250 freeze fresh-derive from live registry)"'
    fresh_leg_lines += [
        f'        assert pf.N1_BANDS[{_w}] == {{"a": ({fmt(_row["a"][0])}, {fmt(_row["a"][1])}),',
        f'                                    "b_exit": ({fmt(_row["b_exit"][0])}, {fmt(_row["b_exit"][1])}),',
        f'                                    "engine_owner": "{_owner}"}}, \\',
        f'            {_msg}',
    ]
fresh_legs = EOL.join(fresh_leg_lines)
assert fresh_leg_lines[0].startswith('        assert pf.N1_BANDS[238] == {"a": (')

# ---------- indent extraction (physical, not assumed; per-file EOL) ----------
def line_indent(t, needle, eol):
    i = t.find(needle)
    assert i >= 0, f"indent needle not found: {needle[:40]}"
    ls = t.rfind(eol, 0, i) + len(eol)
    line = t[ls:t.find(eol, ls)]
    return line[:len(line) - len(line.lstrip(" "))]

CFG_I  = line_indent(n1_t, '249: {"batch"', EOL)
PRE_KEY_I = line_indent(n1_t, '"prereg": ("research/PERPETUAL_N1_W249_PREREG.md', EOL)
PRE_I  = line_indent(n1_t, '"pre-run; design = frozen v1 null calibration verbatim, "', EOL)
_c249 = n1_t.find('249: {"batch"')
assert _c249 > 0, "W249 cfg entry not found (W249 freeze not landed?)"
_mpos = n1_t.find('"a_seed_base"', _c249)
assert _mpos > 0 and n1_t.find('"shard_subdir"', _c249) > _mpos, "W249 cfg a_seed_base line not found"
MEM_I  = line_indent(n1_t, '"a_seed_base": ' + str(W249["a"][0]), EOL) \
    if n1_t.find('"a_seed_base": ' + str(W249["a"][0]), _c249) > 0 \
    else line_indent(n1_t, '"a_seed_base": ' + fmt(W249["a"][0]), EOL)
ROW_I  = line_indent(pf_t,  '249: {"a"', PF_EOL)

# ---------- W249 row owner line (physical bytes; comment text is own generation) ----------
w249_row_start = pf_t.find('    249: {"a"')
assert w249_row_start > 0, "W249 row literal not found in pf source"
_own_ls = pf_t.find(PF_EOL, w249_row_start) + len(PF_EOL)
_own_le = pf_t.find(PF_EOL, _own_ls)
w249_own_line = pf_t[_own_ls:_own_le]
assert '"engine_owner": "bm-c"' in w249_own_line, \
    f"W249 owner line unexpected bytes: {w249_own_line!r}"
ROWC_I = w249_own_line[:len(w249_own_line) - len(w249_own_line.lstrip(" "))]

# ---------- pf comment + row ----------
pf_comment = PF_EOL.join([
"    # W250 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat",
"    # MSG-20261016-055x-bmc-w250-seat published=reserved by bm-c itself @",
"    # origin " + SEAT_ORIGIN + " (r1043, queue-head supply -- W249 complete -> freeze UNBLOCKED at publish, ZERO waits-upstream face; the W250 seat was published AFTER the W249 five-face + finalize landing (zero waits-upstream face) -- bm-c r1042 freeze + r1043 finalize one-pass ledger 972,135 / K=545,720); prereg + ADMIT probe",
"    # receipt frozen commit " + w250_prereg_sha[:10] + " (prereg research/PERPETUAL_N1_W250_PREREG.md",
"    # bm-c r1045 window machine-SUB derive landed pre-freeze, probe",
"    # results/_w250bmc_20261016_probe_receipt.json @ " + w250_receipt_sha[:10] + ");",
"    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10",
"    # ~23:1x; deletion-set EMPTY; delivery window = chain-order",
"    # splice AFTER the bm-c W249 five-face (freeze " + w249_freeze_sha[:10] + ") + W249",
"    # finalize product landed (n1_w249_results.json present, ledger",
"    # head " + str(w249_total) + " machine-read at freeze time); zero --no-verify;",
"    # the W250 seat MSG sits in " + seat_found + " at freeze",
"    # time, honest archived per S7 law);",
"    # band gate ADMIT results/_w250bmc_20261016_probe_receipt.json: A = FIRST-CLEAN",
"    # arithmetic continuation of the prior-wave A tail (" + fmt(w249_a_tail + 1) + ".." + fmt(w249_a_tail + 2_000) + " CLEAN",
"    # at naive start on the registered universe, hops=0, A_hop_chain empty +",
"    # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,",
"    # THIRTEENTH consecutive seed-gap face per the W249 probe leg4 + seat leg4",
"    # anticipation confirmed live; A base == prior-wave A tail+1 (" + fmt(w249_a_tail) + "+1) machine-checkable;",
"    # B = CLEAN arithmetic continuation of the prior-wave B tail",
"    # (" + fmt(w249_b_tail + 1) + ".." + fmt(w249_b_tail + 200) + ", hops=0, B_naive_hops=0, B_hop_chain empty +",
"    # B_clean_at_naive_start=true, past the W239 staircase band-hop landing; the",
"    # registered W239 A band " + fmt(pf_mod.N1_BANDS[239]["a"][0]) + ".." + fmt(pf_mod.N1_BANDS[239]["a"][1]) + " and the registered W247/W248/W249 B bands",
"    # " + fmt(W249["b_exit"][0]) + ".." + fmt(W249["b_exit"][1]) + " all sit below the walk start) -- B lands OUTSIDE",
"    # the own-A window " + fmt(a_lo) + ".." + fmt(a_hi) + ": seed-decoupled A/B gap face THIRTEENTH;",
"    # B base == prior-wave B tail+1 (" + fmt(w249_b_tail) + "+1) machine-checkable;",
"    # single-window derive (r812 merged the gate legs INTO the",
"    # pre-seat probe; dual-window parity N/A honest); scan face =",
"    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1",
"    # used-seed band + probe cluster 95_000..95_003 + cross-face",
"    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/",
"    # N2-W15 probe points.",
"    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):",
"    # " + gate_lines[0] + ";",
"    # " + gate_lines[1] + ".",
"    # W251+ projection (gate-derived pre-seat probe leg4, pre-W250",
"    # universe): A naive first-clean " + rec["legs"]["leg4"]["W251p_A_naive"] + " hops=" + str(rec["legs"]["leg4"]["hops_A"]) + " (this window's gate: CLEAN, zero live",
"    # seed refusers) / B naive " + rec["legs"]["leg4"]["W251p_B_naive"] + " hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " NOT clean at naive -- first-clean " + rec["legs"]["leg4"]["W251p_B_first_clean"] + ",",
"    # lands OUTSIDE the projection A window;",
"    # B_hop lands-inside-A=false leg present); W251 freezer MUST",
"    # re-derive on the post-W250 universe AND reserve the own-wave A window",
"    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1",
"    # equality); never transcribe r587.",
])
pf_row = (f'{ROW_I}250: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), '
          f'"b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'
          + PF_EOL + f'{ROWC_I}"engine_owner": "bm-c"}},' + PF_EOL)
# belt-and-braces: display form must equal the canonical W-family text
assert pf_row.split(PF_EOL)[0].strip() == \
    f'250: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), "b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'

old_pf = must(pf_t, (w249_own_line + PF_EOL + '}'
                     + PF_EOL + '# v1 + ext(wave-1) in-use bands'), 1, "pf_close")
new_pf = (w249_own_line + PF_EOL
          + pf_comment + PF_EOL + pf_row
          + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands')
pf_t2 = pf_t.replace(old_pf, new_pf, 1)

# ---------- n1 cfg entry (programmatic quote wrapping, r761 law) ----------
fin_face = (f"W1..W249 finalize ALL LANDED (W249 finalize product present at splice, "
            f"net chain head {w249_total} machine-read, merged pool K={w249_merged_n} "
            f"machine-read) -- ZERO in-flight upstream seats at splice time, clean precondition "
            f"(thirty-eighth consecutive fully-clean freeze window); downstream W251 seat NOT YET "
            f"PUBLISHED at this freeze window (the next freezer must seat-first publish per "
            f"O-20261010-2350 sec.2 queue-depth supply; the W251 freezer MUST re-derive live on "
            f"the post-W250 universe + reserve the own-wave A window when deriving B per the "
            f"W250 seat leg4 mandate, never transcribe r587)")
cfg_lines = [
 f'{CFG_I}250: {{"batch": "PERPETUAL-N1-W250",',
 f'{PRE_KEY_I}"prereg": ("research/PERPETUAL_N1_W250_PREREG.md (wave-level frozen "',
]
PRE = [
 "pre-run; design = frozen v1 null calibration verbatim, ",
 "new seed bands only; TWO HUNDRED AND FIFTIETH ENGINE-OWNED WAVE ",
 f"BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate), ",
 "own-series continuation per O-20260101-2355 sec.2 (first-free-",
 "number law after the REGISTERED W249 row five-face freeze (bm-c own seat executed at the bm-c r1042 splice window; engine self-burn 12/12; finalize one-pass bm-c r1043 closeout, ledger 972,135 / K=545,720 machine-read), ",
 f"{w249_freeze_sha[:10]} (prereg {w249_prereg_sha[:10]}), SINGLE STATE zero seat gap W2..W249 all ",
 "registered; " + fin_face + "; ",
 "seat published=reserved ",
 "MSG-20261016-055x-bmc-w250-seat PUSHED to origin " + SEAT_ORIGIN + " ",
 "BEFORE this freeze per r565 early-visibility law (payload = ",
 "seat MSG + pre-seat probe script + probe receipt; per-wave prereg ",
 "bm-c r1045 window machine-SUB derive landed pre-freeze -- bm-c own-seat ",
 "continuity, ",
 f"prereg {w250_prereg_sha[:10]} @ receipt {w250_receipt_sha[:10]}) -- this freeze splice editor derived from the committed W249 editor template in this same freeze window; ",
 "deletion-set EMPTY; delivery window = chain-order splice ",
 "after the W249 five-face + W249 finalize product landed ",
 "(executed in the bm-c loop freeze window ",
 "under the CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED ",
 "2026-10-10 ~23:1x); zero merge at freeze delivery, zero ",
 "--no-verify; single-window derive -- r812 merged the gate ",
 "legs INTO the pre-seat probe; parity N/A honest), ",
 "engine_owner=bm-c (bm-c OWN-SEAT face -- bm-c's SEVENTIETH owned claim per machine-derive (engine_owner==bm-c rows ",
 f"{len(bmc_rows_live)} + candidate; probe receipt leg0 bmc_ordinal=70 = seat-time pre-splice ",
 "live faces disclosed honest, live derive governs ",
 "r587/r359 -- attempt-continuity face: the superseded W245-bmc seat claim (quarantined 20261015T0924) left the 67 live bm-c rows intact), own-seat continuity)), ",
 "wave 250: ",
 "A = FIRST-CLEAN arithmetic continuation of the prior-wave A tail (the continuation ",
 f"{fmt(w249_a_tail + 1)}..{fmt(w249_a_tail + 2_000)} is CLEAN at its own start ",
 "-- hops=0, A_hop_chain empty + A_clean_at_naive_start=true, seed-decoupled ",
 "A-continuation face, THIRTEENTH consecutive seed-gap face exactly as the W249 probe leg4 + seat leg4 ",
 "succession projection notes anticipated; A base == prior-wave A tail+1 (",
 f"{fmt(w249_a_tail)}+1) machine-checkable; ",
 "non-rotational r587 forward-monotone walk) + B = CLEAN arithmetic ",
 "continuation of the prior-wave B tail (the continuation ",
 f"{fmt(w249_b_tail + 1)}..{fmt(w249_b_tail + 200)} is CLEAN at its own start ",
 "-- hops=0, B_naive_hops=0, B_hop_chain empty + B_clean_at_naive_start=true, past the W239 ",
 f"staircase band-hop landing (the registered W239 A band {fmt(pf_mod.N1_BANDS[239]['a'][0])}..{fmt(pf_mod.N1_BANDS[239]['a'][1])} and the registered W247/W248/W249 B bands all sit below the walk start); B lands OUTSIDE the ",
 f"own-A window {fmt(a_lo)}..{fmt(a_hi)}; seed-decoupled A/B gap ",
 "face THIRTEENTH consecutive; B base == prior-wave B tail+1 (",
 f"{fmt(w249_b_tail)}+1) machine-checkable; cross-window convergence with the W249 probe leg4 + seat leg4 succession projection ",
 "notes -- all MANDATORY notes honored (post-W249 universe ",
 "re-derive + live-trace re-read, no staircase-equality assumption); ADMIT receipt ",
 "results/_w250bmc_20261016_probe_receipt.json + ",
 "seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a ",
 "ADMIT convention); W251+ projection per this window gate: ",
 f"A naive first-clean {rec['legs']['leg4']['W251p_A_naive']} CLEAN (hops=0, zero live seed refusers) / B naive ",
 f"{rec['legs']['leg4']['W251p_B_naive']} hops={rec['legs']['leg4']['hops_B']} NOT clean at naive -- first-clean {rec['legs']['leg4']['W251p_B_first_clean']} (B_hop lands-inside-A=false leg present; seed-gap face ",
 "inherited); W251 freezer MUST re-derive on the post-W250 universe AND ",
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
 f'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W250 A: {fmt(a_lo)}..{fmt(a_hi)} (FIRST-CLEAN arithmetic continuation of the prior-wave A tail; {fmt(w249_a_tail + 1)}..{fmt(w249_a_tail + 2_000)} CLEAN at naive start hops=0, A_hop_chain empty + A_clean_at_naive_start=true; seed-decoupled A-continuation face THIRTEENTH consecutive seed-gap face; A base == prior-A tail+1)',
 f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W250 B: {fmt(b_lo)}..{fmt(b_hi)} (CLEAN arithmetic continuation of the prior-wave B tail; {fmt(w249_b_tail + 1)}..{fmt(w249_b_tail + 200)} CLEAN at naive start hops=0, B_naive_hops=0, B_hop_chain empty + B_clean_at_naive_start=true; past the W239 staircase band-hop landing; B lands outside own-A; seed-decoupled A/B gap face THIRTEENTH consecutive; B base == prior-B tail+1)',
 f'{MEM_I}"shard_subdir": "n1_w250", "out_name": "n1_w250_results.json",',
 f'{MEM_I}"engine_owner": "bm-c"}},',
]

cfg_block = EOL.join(cfg_lines)
old_cfg = must(n1_t, ('                       }' + EOL
                      + 'PREREG = WAVE_CONFIGS[2]["prereg"]'), 1, "n1_cfg_close")
new_cfg = (cfg_block + EOL
           + '                       }' + EOL
           + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
assert new_cfg.count('250: {"batch": "PERPETUAL-N1-W250"') == 1
n1_t2 = n1_t.replace(old_cfg, new_cfg, 1)

# ---------- n1 materializer block ----------
hdr = [
 "    # --- W250 materializer face (bm-c loop five-face freeze splice --",
 "    #     OWN-SEAT face under CEO fill-order standing 2026-10-08 ~23:5x",
 "    #     + RE-ISSUE 2026-10-10 ~23:1x + O-20260909-2334 local-full-use",
 "    #     + O-20260924-1730 claim-and-start same-round law):",
 "    #     bm-c's SEVENTIETH owned per machine-derive (engine_owner==bm-c",
 f"    #     rows {len(bmc_rows_live)} + candidate; own-seat face: seat published=reserved by bm-c itself",
 "    #     (r1043 MSG-20261016-055x-bmc-w250-seat @ origin " + SEAT_ORIGIN + "; probe leg0",
 "    #     bmc_ordinal=70 = seat-time pre-splice faces;",
 "    #     live derive at freeze governs);",
 "    #     wave 245 = first free number after the",
 "    #     REGISTERED W249 row (five-face freeze " + w249_freeze_sha[:10] + "; bm-c own seat executed at",
 "    #     the bm-c r1042 splice window; engine",
 "    #     self-burn 12/12 + finalize one-pass bm-c r1043 closeout ledger 972,135 / K=545,720",
 "    #     -- SINGLE STATE zero seat gap (W2..W249 all registered). Seat",
 "    #     published=reserved MSG-20261016-055x-bmc-w250-seat pushed",
 "    #     to origin " + SEAT_ORIGIN + " BEFORE this freeze, r565 law (payload =",
 "    #     seat MSG + pre-seat probe script + probe receipt; per-wave prereg",
 f"    #     bm-c r1045 window derive landed pre-freeze commit {w250_prereg_sha[:10]}; this freeze splice editor",
 "    #     derived from the committed W249 editor template in this same freeze",
 "    #     window (E63 heal lineage: arith_a250/arith_b250 define+assert consistent;",
 "    #     band-set variable aging face w244_a holds wave-250 bands, disclosed);",
 "    #     deletion-set EMPTY; delivery window",
 "    #     = chain-order splice after the W249 five-face + W249 finalize",
 "    #     product landed; zero --no-verify; the W250 seat MSG sits in",
 "    #     " + seat_found + " at freeze time, honest archived",
 "    #     per S7 law).",
 "    #     TWO HUNDRED AND FIFTIETH engine wave BY",
 f"    #     MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate; gate",
 "    #     leg0 machine output governs per r359 law).",
 f"    #     {fin_face}; the finalize merge loop",
 "    #     still derives the wave set from registry keys at run",
 "    #     time, FAIL-CLOSED r307 always on. ADMIT receipt",
 "    #     results/_w250bmc_20261016_probe_receipt.json;",
 "    #     seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a",
 f"    #     ADMIT convention upgrade): {gate_lines[0]}; {gate_lines[1]};",
 "    #     banned gate ADMIT 0 (re-run at freeze window);",
 "    #     not a re-pick (R250: W250 bands were never assigned).",
 "    #     PARITY STRUCTURAL CHOICE (frozen W250 prereg sec.3 mandate):",
 "    #     estate 91 rows (W138..W206 full-span 69 + W211..W232 legs) +",
 "    #     W233..W237 legs (5) extracted verbatim from the OWN W249 block",
 "    #     physical bytes; the W249 block's own W238..W248 legs (11) are",
 "    #     EXCLUDED from the estate path per the prereg mandate; fresh",
 "    #     W238..W249 legs (12) added, machine-derived from the live pf",
 "    #     registry at freeze time -> 108 parity rows (W138..W206+W211..W249).",
 "    _set_wave(250)",
 "    try:",
 '        assert WAVE_CONFIGS[249]["a_seed_base"] == pf.N1_BANDS[249]["a"][0], \\',
 '            "W250 upstream W249 mirror drift (a)"',
 "        assert WAVE_CONFIGS[249][\"b_exit_seed_base\"] == \\",
 '            pf.N1_BANDS[249]["b_exit"][0], "W250 upstream W249 mirror drift (b)"',
 "        assert WAVE_CONFIGS[249].get(\"engine_owner\") == \\",
 '            pf.N1_BANDS[249].get("engine_owner") == "bm-c", \\',
 '            "W250 upstream W249 engine_owner mirror drift (law-mirror parity; bm-c upstream seat face (own-seat upstream))"',
 "        w244_a = {A_SEED_BASE + j for j in range(A_N)}",
 "        w244_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
 '        assert not (w244_a & w244_b), "W250 A/B band overlap"',
 "        assert not (w244_a & reg_ints) and not (w244_b & reg_ints), \\",
 '            "W250 hits SEED_REGISTRY"',
 '        for nm, band in (("A", w244_a), ("B", w244_b)):',
 '            assert not (band & v1_a) and not (band & v1_b), f"W250 {nm} hits v1"',
 '            assert not (band & w1_a) and not (band & w1_b), f"W250 {nm} hits W1"',
 '            assert not (band & probes), f"W250 {nm} hits probe seeds"',
]
tail = [
 "        # prior-wave disjointness W2..W249 (single state: all",
 "        # registered, dynamic registry derive, r511 law)",
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 250):",
 '            assert not (w244_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
 "                                 for j in range(A_N)}), f\"W250 A hits W{wprev}\"",
 '            assert not (w244_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
 "                                  for j in range(B_N)}), f\"W250 B hits W{wprev}\"",
 "        n3r1_used245 = set(range(70_000, 70_006))",
 "        assert not (w244_a & n3r1_used245) and not (w244_b & n3r1_used245), \\",
 '            "W250 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
 "        assert not (w244_a & lfc_actual12) and not (w244_b & lfc_actual12), \\",
 '            "W250 bands must clear the lfc actual draw range"',
 "        assert not (w244_a & options_actual12) and \\",
 "            not (w244_b & options_actual12), \\",
 '            "W250 bands must clear the options_wave2 actual draw range"',
"        # band facts (law sec.4 W250 row): A = FIRST-CLEAN arithmetic",
"        # continuation of the prior-wave A tail",
f"        # ({fmt(w249_a_tail + 1)}..{fmt(w249_a_tail + 2_000)} CLEAN at naive start on the",
"        # registered universe, hops=0, A_hop_chain empty +",
"        # A_clean_at_naive_start=true -- seed-decoupled A-continuation face,",
"        # THIRTEENTH consecutive seed-gap face, exactly as the W249 probe leg4 +",
"        # seat leg4 succession projection notes anticipated; A base ==",
f"        # prior-wave A tail+1 ({fmt(w249_a_tail)}+1) machine-checkable;",
"        # B = CLEAN arithmetic continuation of the prior-wave B tail",
f"        # ({fmt(w249_b_tail + 1)}..{fmt(w249_b_tail + 200)} CLEAN at naive start, hops=0,",
"        # B_naive_hops=0, B_hop_chain empty + B_clean_at_naive_start=true,",
f"        # past the W239 staircase band-hop landing (the registered W239 A band {fmt(pf_mod.N1_BANDS[239]['a'][0])}..{fmt(pf_mod.N1_BANDS[239]['a'][1])}",
f"        # and the registered W247/W248/W249 B bands all sit below the walk start);",
"        # B lands OUTSIDE the own-A window",
f"        # {fmt(a_lo)}..{fmt(a_hi)}; seed-decoupled A/B gap face THIRTEENTH consecutive;",
"        # B base == prior-wave B tail+1 EXACT",
"        # machine-checkable; B_hop_lands_inside_A=false;",
"        # B_no_ownA_jump=true; cross-window convergence with",
"        # the W249 probe leg4 + seat leg4 succession projection notes -- all",
"        # MANDATORY notes honored (post-W249 universe",
"        # re-derive + live-trace re-read, no staircase-equality assumption);",
f'        assert WAVE_CONFIGS[250]["a_seed_base"] == {a_lo} == {w249_a_tail} + 1, (',
'            "W250 A must be the first-clean arithmetic continuation of the "',
'            "prior-wave A tail (hops=0, A_hop_chain empty + A_clean_at_naive_start=true -- "',
'            "seed-decoupled A-continuation face, THIRTEENTH consecutive seed-gap face, "',
'            "exactly as the W249 probe leg4 + seat leg4 succession projection notes "',
'            "anticipated; A base == prior-wave A tail+1 machine-checkable)")',
f"        arith_a250 = set(range({a_lo}, {a_hi + 1}))",
"        assert not (arith_a250 & reg_ints), \\",
'            "W250 A window must be CLEAN (first-clean ADMIT face, A-continuation)"',
f'        assert WAVE_CONFIGS[250]["b_exit_seed_base"] == {b_lo} == {w249_b_tail} + 1, (',
'            "W250 B CLEAN arithmetic continuation face: the naive continuation "',
f'            "{fmt(w249_b_tail + 1)}..{fmt(w249_b_tail + 200)} is CLEAN at its own start "',
'            "(hops=0, B_naive_hops=0, B_hop_chain empty + B_clean_at_naive_start=true, "',
'            "past the W239 staircase band-hop landing) -- B base == prior-wave B tail+1 "',
'            "EXACT (B_base_above_priorB_tail + B_no_ownA_jump face relation asserts, "',
'            "probe receipt leg1 mirrored exactly; B_hop_lands_inside_A=false)")',
f"        assert {b_lo} > {w249_b_tail}, \\",
'            "W250 B clean-continuation base must sit above the prior-wave B tail"',
f"        arith_b250 = set(range({b_lo}, {b_hi + 1}))",
"        assert not (arith_b250 & reg_ints), \\",
'            "W250 B window must be CLEAN (first-clean ADMIT face, clean arithmetic continuation)"',
"        assert not (arith_b250 & arith_a250), \\",
'            "W250 A/B same-freeze mutual exclusion (seed-decoupled gap face inherited: B below own A)"',
"        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W250-SHARD-0\",",
 '                                          "n1w250-0of12"), "W250 entry identity"',
 '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W250-SHARD-11",',
 '                                           "n1w250-11of12")',
 "        assert SHARD_DIR.endswith(\"n1_w250\") and OUT.endswith(",
 '            "n1_w250_results.json"), "W250 path drift"',
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 250):",
 "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(",
 "                PATHS.results_dir, \"p2cal_ext\",",
 "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\",
 '                f"W250 shard dir collides with W{wprev}"',
 "        # W250 finalize cumulative deps: W17..W249 outputs ALL PRESENT",
 f"        # (landed net chain head {w249_total} machine-read at freeze time)",
 "        # -- ZERO in-flight upstream seats at splice, clean precondition",
 "        # freeze window; the finalize merge loop derives the wave",
 "        # set from registry keys at run time and stays",
 "        # FAIL-CLOSED, r307 two-state law).",
 "        for _depw in range(17, 250):",
 "            assert os.path.exists(os.path.join(",
 "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\",
 '                f"W250 finalize cumulative dep (W{_depw} output) missing"',
 "        # finalize wave-set derivation face (r511 derive law): every",
 "        # registered wave below 250 composes; wave 15 excluded by",
 "        # design; SINGLE STATE (W2..W249 all registered -- no",
 "        # two-state seat disclosure needed at this freeze).",
 "        assert sorted(w for w in WAVE_CONFIGS if w < 250) == \\",
 "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\",
 "            [w for w in range(16, 250)], \\",
 '            "W250 prior-wave set must derive from registry keys (no 15; " \\',
 '            "W2..W249 registered single state)"',
 "        assert os.path.exists(os.path.join(",
 '            PATHS.root, "research", "PERPETUAL_N1_W250_PREREG.md")), \\',
 '            "W250 per-wave prereg missing (materializer requirement)"',
 "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"",
 "    finally:",
 "        _set_wave(2)",
]
block = EOL.join(hdr) + EOL + par_sec + legs_kept + fresh_legs + EOL + EOL.join(tail) + EOL
# family #6 atomic triple gate (carried forward): the new
# block's LHS w<250> / RHS range(16,250)+range(17,250) / comment below-250 MUST move together.
assert block.count("if w < 250)") == 3, f"family-6 triple: w<250 count {block.count('if w < 250)')} != 3"
assert block.count("if w < 249)") == 0, "family-6 triple: stale w<249 leaked into the W250 block"
assert block.count("range(16, 250)") == 1 and block.count("range(17, 250)") == 1, "family-6 triple: RHS ranges wrong"
assert block.count("registered wave below 250 composes") == 1, "family-6 triple: comment face wrong"
old_blk_anchor = must(n1_t2, "    # --- T-141 s2 lane face", 1, "t141_marker")
n1_t3 = n1_t2.replace(old_blk_anchor, block + old_blk_anchor, 1)

# ---------- n1 print line ----------
pr = [
 '          "+ W250 materializer face [same guard set, dep=W17..W249 "',
 f'          "outputs ALL PRESENT (landed net chain head {w249_total} = W249 bm-c finalize one-pass, K={w249_merged_n} merged pool) -- ZERO "',
 '          "in-flight upstream seats at splice, clean precondition, TWO HUNDRED AND FIFTIETH "',
 f'          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} "',
 '          "+ candidate) bm-c\'s SEVENTIETH owned claim per "',
 '          "machine-derive (engine_owner==bm-c rows 68 + candidate; OWN-SEAT face: seat published by bm-c itself, "',
 '          "probe leg0 bmc_ordinal=70 = seat-time pre-splice faces disclosed honest, "',
 '          "live derive at freeze governs), "',
 '          "A=FIRST-CLEAN arithmetic continuation of prior-wave A tail (A-continuation face, "',
 '          "hops=0, A_hop_chain empty + A_clean_at_naive_start=true, seed-decoupled THIRTEENTH consecutive seed-gap face) "',
 '          "+ B=CLEAN arithmetic continuation of prior-wave B tail (hops=0, B_naive_hops=0, "',
 '          "B_hop_chain empty + B_clean_at_naive_start=true, past the W239 staircase landing, "',
 '          "B base == prior-B tail+1 EXACT, B_no_ownA_jump=true, "',
 '          "seed-decoupled A/B gap face THIRTEENTH consecutive), chain-order splice from the "',
 '          "committed ADMIT receipt + seed_admit_gate rc0 both bands FREE "',
 '          "(O-20261010-1945-bm-a ADMIT convention), "',
 '          "ADMIT receipt "',
 '          "results/_w250bmc_20261016_probe_receipt.json, law sec.4 W250 row, "',
 '          "bm-c loop CEO fill-order RE-ISSUE 23:1x] "',
]

old_pr = must(n1_t3, '          "+ T-141 s2 ', 1, "print_t141")
n1_t4 = n1_t3.replace(old_pr, EOL.join(pr) + EOL + old_pr, 1)

# ---------- post-edit count gates ----------
assert n1_t4.count('"batch": "PERPETUAL-N1-W250"') == 1
assert n1_t4.count("# --- W250 materializer face") == 1     # block header
assert n1_t4.count('"+ W250 materializer face') == 1        # print fragment
assert n1_t4.count('250: {"batch": "PERPETUAL-N1-W250"') == 1
assert pf_t2.count(ROW_I + '250: {"a"') == 1
assert pf_t2.count('"engine_owner": "bm-c"},' + PF_EOL + '}') == 1
assert n1_t4.count('    # --- T-141 s2 lane face') == 1
assert n1_t4.count('"PERPETUAL-N1-W250-SHARD-0"') == 1
# leg count gates: leg W_k lives in blocks W_{k+1}..W250 -> (250 - k) occurrences
for _lw in range(238, 250):
    _first = (f'assert pf.N1_BANDS[{_lw}] == {{"a": '
              f'({fmt(pf_mod.N1_BANDS[_lw]["a"][0])}, {fmt(pf_mod.N1_BANDS[_lw]["a"][1])}),')
    _got = n1_t4.count(_first)
    assert _got == 250 - _lw, \
        f"W{_lw} leg count drift: {_got} != {250 - _lw} (first-line: {_first})"
for _b in range(209, 251):
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
  "machine": "bm-c", "wave": 250,
  "phase": "five-face freeze chain-order splice (bm-c own-seat freeze window, upstream ALL LANDED clean precondition)",
  "origin_base": omain,
  "pf_sha16_pre": hashlib.sha256(pf_b).hexdigest()[:16],
  "n1_sha16_pre": hashlib.sha256(n1_b).hexdigest()[:16],
  "pf_sha16_post": hashlib.sha256(pf_t2.encode("utf-8")).hexdigest()[:16],
  "n1_sha16_post": hashlib.sha256(n1_t4.encode("utf-8")).hexdigest()[:16],
  "bands": {"A": A, "B": B, "a_lo": a_lo, "a_hi": a_hi, "b_lo": b_lo, "b_hi": b_hi},
  "admit_receipt": "results/_w250bmc_20261016_probe_receipt.json",
  "seed_admit_gate": gate_lines,
  "banned_gate": "ADMIT rc0 (re-run at freeze window)",
  "band_semantics": {"A": "FIRST-CLEAN arithmetic continuation of prior-wave A tail (hops=0, A_hop_chain empty + A_clean_at_naive_start=true; seed-decoupled A-continuation face, THIRTEENTH consecutive seed-gap face; A base == prior-A tail+1 EXACT)",
                     "B": "CLEAN arithmetic continuation of prior-wave B tail (hops=0, B_naive_hops=0, B_hop_chain empty + B_clean_at_naive_start=true; past the W239 staircase band-hop landing -- the registered W239 A band 542_501..544_500 and the registered W247/W248/W249 B bands 544_501..544_700 + 544_701..544_900 + 544_901..545_100 all sit below the walk start; B_no_ownA_jump=true; B_hop_lands_inside_A=false; seed-decoupled A/B gap face THIRTEENTH consecutive; B base == prior-B tail+1 EXACT)"},
  "w249_upstream": {"freeze_sha": w249_freeze_sha, "prereg_sha": w249_prereg_sha,
                    "ledger_total": w249_total, "merged_n": w249_merged_n,
                    "engine_owner": "bm-c (upstream seat honored)",
                    "repair_chain_note": "W249 bm-c own-wave closeout r1043 (five-face splice " + w249_freeze_sha[:10] + " + engine self-burn 12/12 + finalize one-pass ledger 972,135 / K=545,720)"},
  "own_seat_face": {"seat_msg": SEAT_MSG, "seat_origin": SEAT_ORIGIN,
                    "inherited": False,
                    "note": "seat published=reserved by bm-c itself (MSG-20261016-055x-bmc-w250-seat pushed to origin " + SEAT_ORIGIN + " r1043 BEFORE this freeze per r565 law, queue-head supply -- W249 complete -> freeze UNBLOCKED at publish, ZERO waits-upstream face; the W250 seat published post-W249-chain (queue-head supply, freeze-UNBLOCKED; the W249 five-face + finalize landed bm-c r1042 splice + r1043 finalize before publish) -- wave 250 engine_owner=bm-c, bm-c's 70th own wave per live derive (probe leg0 bmc_ordinal=70 = seat-time pre-splice faces disclosed honest, live derive governs r587/r359; freeze-time live face owner rows 239 + candidate = 240th EXACT; attempt-continuity face: the superseded W245-bmc seat claim (quarantined 20261015T0924) left the 67 live bm-c rows intact)"},
  "transitive_deps": {f"W{w}": f"results/perpetual_faces/n1_w{w}_results.json present (belt-and-braces gate)" for w in (246, 245, 244, 243, 242, 241, 240, 239, 238, 237)},
  "downstream_seat": "W251 = next free number, next freezer must seat-first publish per O-20261010-2350 sec.2 queue-depth supply; the W251 freezer MUST re-derive live on the post-W250 universe + reserve the own-wave A window when deriving B per the W250 seat leg4 mandate, never transcribe r587 -- W251p face per this window's probe leg4: A naive 567501..569500 CLEAN (hops=0, zero live refusers) / B naive 545301..545500 hops=11 NOT clean at naive, first-clean 565501..565700 (B_hop lands-inside-A=false leg present); seed-gap face inherited: W250 A/B decoupled, re-read the live trace at W251 derive time, do NOT assume the staircase A-base==prior-B-tail+1 equality",
  "seat": seat_found + " (origin " + SEAT_ORIGIN + ")",
  "prereg_bundle": {"prereg_sha": w250_prereg_sha, "probe_receipt_sha": w250_receipt_sha,
                    "note": "prereg derived by the bm-c r1045 window (authored 07:2x, banned gate ADMIT rc0 re-verified r1045, committed r1045; commit " + w250_prereg_sha[:10] + "; facts live-derived ledger 972,135 / K=545,720; freeze-time live derive bmc rows 69 + candidate 70th EXACT per r587/r359); splice editor derived from the committed W249 editor template by count-asserted ordered transform in this same freeze window (E63 heal lineage: arith_a250/arith_b250 define+assert consistent; band-set variable aging face w244_a holds wave-250 bands, disclosed); upstream W249 already landed (clean-precondition thirty-eighth consecutive window); zero transcription"},
  "ordinal_faces": {"owner_rows_live": len(owner_rows_live), "bma_rows_live": len(bma_rows_live),
                    "bmc_rows_live": len(bmc_rows_live),
                    "engine_owned_ordinal": len(owner_rows_live) + 1,
                    "bmc_own_ordinal": len(bmc_rows_live) + 1,
                    "probe_receipt_bmc_ordinal_face": 70,
                    "note": "post-W249 registration: bm-c rows 69 + candidate = 70th owned (live derive at freeze time governs per r587/r359; probe leg0 bmc_ordinal=70 = seat-time faces -- bm-c own-seat continuity, queue-head supply -- W249 complete at publish, ZERO waits-upstream face)"},
  "parity_section": {"source": "OWN W249 block physical bytes (bm-c splice generation r1042 window, structure known exactly)",
                     "bytes": len(par_sec) + len(legs_kept),
                     "estate_row_asserts": par_sec.count("assert pf.N1_BANDS["),
                     "kept_legs_row_asserts": legs_kept.count("assert pf.N1_BANDS["),
                     "dropped_legs_row_asserts": legs_dropped.count("assert pf.N1_BANDS["),
                     "fresh_legs_row_asserts": 12,
                     "total_parity_rows": par_sec.count("assert pf.N1_BANDS[")
                                          + legs_kept.count("assert pf.N1_BANDS[") + 12,
                     "note": "estate W138..W206 (69 rows, r858 absorb generation) + W211..W232 legs (estate 91) + W233..W237 legs extracted verbatim (5) per the frozen W250 prereg sec.3 mandate; the W249 block's own W238..W248 legs (11) EXCLUDED from the estate path per the same mandate; fresh W238..W249 legs (12) machine-derived from the live pf registry -> W250 block = 108 rows (W138..W206 + W211..W249); disclosed: (a) inherited W213 leg error-string face preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact); (b) band-set variable one-behind naming face (w244_a holds wave-250 bands) = lineage mechanical aging face, zero functional impact; (c) fresh-leg error strings are own-generation text (assert targets identical, first-line format identical, disclosed); (d) E63 3rd-gen prevention this window: the W250 derive editor reordered passes so P1 structural outputs are blanket-immune and the legs/dropped wave-identity asserts are fixed post-blanket (range(233,249)/range(238,249) live-structure exact) -- zero heal needed, zero splice executed pre-verify"},
  "family6_triple_gate": {"absorbed": True,
                          "note": "W249 editor family-6 gate carried forward: new block LHS w<250 x3 / RHS range(16,250)+range(17,250) / comment below-250 count-asserted ATOMICALLY before splice; W249 block's own w<249 face = legitimate prior-wave boundary (not stale); E63 heal lineage applied (arith define/assert consistent)"},
  "eol": {"n1_crlf": EOL == "\r\n", "pf_crlf": PF_EOL == "\r\n"},
  "liveness_anchors": {f"w{_b}_block_kept": 1 for _b in range(209, 251)},
}

open(RECEIPT_OUT, "w", encoding="utf-8").write(json.dumps(receipt, indent=1))
print(json.dumps({k: receipt[k] for k in
      ("phase", "origin_base", "pf_sha16_post", "n1_sha16_post", "bands",
       "w249_upstream", "own_seat_face")}, indent=1))
print("SPLICE OK -- py_compile both green; NEXT: selftest (default wave, r522 law) -> pathspec commit+push -> engine self-ignite W250 burn (12 shards) -> PRE-FINALIZE six-gate (standing law) -> finalize one-pass")
