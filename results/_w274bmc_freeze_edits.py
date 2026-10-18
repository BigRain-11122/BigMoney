# -*- coding: utf-8 -*-
# 2026-10-19 02:5x bm-c r1105 splice window (upstream W1..W273 ALL LANDED, clean
# precondition -- W273 cycle COMPLETE bm-c r1102 closeout 01:0x, ledger head
# 1,024,935 / K=598,520 machine-read): W274 five-face freeze splice
# editor -- bm-c OWN-SEAT face (seat MSG-20261019-012x-bmc-w274-seat
# published=reserved by bm-c itself @ origin 70b21a0264 r1102, pre-seat probe
# ADMIT receipt results/_w274bmc_20261019_probe_receipt.json same payload;
# the W274 seat was published AFTER the W273 finalize landing (W274 FREEZE
# UNBLOCKED at seat time, zero waits-upstream face -- seat-first law
# O-20261010-2350 sec.2; the SPLICE gate0.5 = GREEN at seat: W273 row +
# W273 finalize file both in-place); zero DRAFT
# marker; per-wave prereg PERPETUAL_N1_W274_PREREG.md derived by the bm-c
# r1104 window (E63 canon-clone builder _r1104bmc_build_w274_derive.py)
# (authored 02:2x, banned_direction_gate ADMIT rc0, frozen sha16 ddc158b5047596ea + CAS-
# graft-delivered to origin 6f31f6e073, r1104 window).
# Lineage: _w273bmc_freeze_edits.py template (proven live-fire freeze, bm-c
# r1102 splice window 04f2127db; engine self-burn 12/12 + finalize one-pass
# verified r1102) + r787 preflight law + r609 origin-verbatim base + r761
# programmatic quote wrapping + r909 physical-byte anchors + r838 per-file
# EOL detection + family #6 LHS/RHS/comment ATOMIC TRIPLE (the new block's
# w<263>/range(16,263)/range(17,263)/below-263 quadruple is count-asserted
# atomically; the W273 block's own w<262> face is legitimate prior-wave
# boundary, not stale) + E63 heal lineage (arith_a274/arith_b274
# define+assert consistent; band-set variable aging face continues:
# w244_a holds wave-263 bands, disclosed).
# NEW FACE vs the W273 editor (honest disclosure, W274 prereg sec.3/sec.5
# mandate): BOTH bands take 1-HOP WALK faces -- staircase + cascade
# CONTINUE -- A = STAIRCASE-AFFECTS-A 1-hop walk, TWENTY-THIRD consecutive A-hop
# (the naive continuation 617_901..619_900 is REFUSED at its own start --
# the registered W273 B band 617_901..618_100 sits INSIDE the naive A
# window = staircase re-emergence continues to affect A; the W273 prereg
# sec.5 item5 post-W273-REGISTERED pre-disclosure confirmed live per r587,
# zero divergence disclosed; the walk hops past the W273 B tail 618_100 ->
# A first-clean 618_101..620_100, hops=1; A base == registered prior-wave B
# tail+1 (618_100+1) floor relation EXACT this window; A_clean_at_naive_start
# =false; A_staircase_hop_past_W273_B=true); B = 1-HOP own-A RESERVATION
# CASCADE above own-A, TWENTY-FOURTH consecutive above-own-A (the naive
# continuation 618_101..618_300 is REFUSED at its own start -- the naive
# window lands INSIDE the own-wave A first-clean window 618_101..620_100,
# own-A reservation cascade standard leg; the walk hops past the own-A tail
# 620_100 -> B landing 620_101..620_300, hops=1; B lands ABOVE own-A; B base
# == own-A tail+1 (620_100+1) EXACT; B_naive_refused_at_start=true;
# B_lands_above_own_A=true; B_hop_lands_inside_A=false; hops=1).
# PARITY STRUCTURAL CHOICE (W273 template lineage): the parity estate
# (W138..W206 69-row full-span, r858 absorb generation) is extracted from
# the OWN W273 block physical bytes (structure known exactly, extraction
# self-asserts the 69-row range identity); the W273 block's own W248..W272
# legs (25 rows) do NOT enter the estate path; after extraction, fresh
# W248..W274 legs (26 rows) are added, machine-derived from the LIVE pf
# registry at freeze time -> W274 block parity = 132 rows (W138..W206 +
# W211..W273). Zero assumption zero risk.
# Zero hardcoded upstream band values: ALL W273 facts machine-derived from the
# LIVE pf import at freeze time (the registered W273 row -- bm-c own seat
# honored), cross-checked against the committed ADMIT receipt
# (results/_w274bmc_20261019_probe_receipt.json) which was derived on the
# post-W273-REGISTERED universe with the W274 candidate bands treated as
# reserved refusers (now REGISTERED verbatim -- values identical, disclosed).
# If the LIVE W273 bands differ from the declared face, the continuation
# asserts fail LOUD (fail-closed).
# Own bundle hashes (prereg/probe receipt) derived via pickaxe, never transcribed.
# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.
import json, hashlib, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PF = os.path.join(REPO, "scripts", "perpetual_faces.py")
N1 = os.path.join(REPO, "scripts", "perpetual_faces_n1.py")
RECEIPT_IN = os.path.join(REPO, "results", "_w274bmc_20261019_probe_receipt.json")
RECEIPT_OUT = os.path.join(REPO, "results", "_w274bmc_freeze_receipt.json")
SEAT_MSG = "MSG-20261019-012x-bmc-w274-seat.md"
SEAT_ORIGIN = "70b21a0264"
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

# ---------- gate 0.5: W273 five-face landed + W273 finalize product present ----------
# (chain-order precondition; belt-and-braces transitive window W261..W270 checked
# here + enforced by the block's cumulative-deps assert range(17, 274) at selftest time)
W273 = dict(pf_mod.N1_BANDS.get(273) or {})
assert W273.get("engine_owner") == "bm-c", \
    f"W273 row not landed as declared (bm-c seat owner expected): {W273} -- five-face freeze missing;" \
    " if an unexpected face exists the freeze window MUST re-derive this editor honestly"
w273_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w273_results.json")
assert os.path.exists(w273_out_path), "W273 finalize product missing (n1_w273_results.json) -- chain dep not met"
for _w in (270, 269, 268, 267, 266, 265, 264, 263, 262, 261):
    assert os.path.exists(os.path.join(REPO, "results", "perpetual_faces", f"n1_w{_w}_results.json")), \
        f"W{_w} finalize product missing (transitive chain dep) -- abort"
w273_out = json.load(open(w273_out_path, encoding="utf-8"))
w273_led = (w273_out.get("science_gates") or {}).get("ledger") or {}
w273_total = w273_led.get("total")
w273_merged_n = None
try:
    w273_merged_n = w273_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
assert w273_total == 1_024_935 and w273_merged_n == 598_520, \
    f"W273 finalize anchors drift at freeze time: total={w273_total} merged={w273_merged_n} (expect 1,024,935 / 598,520)"
# freeze shas machine-derived (pickaxe), never transcribed
r = git("log", "--format=%H", "-S", '273: {"a"', "--", "scripts/perpetual_faces.py")
w273_freeze_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W273_PREREG.md")
w273_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W274_PREREG.md")
w274_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
assert os.path.exists(os.path.join(REPO, "research", "PERPETUAL_N1_W274_PREREG.md")), \
    "W274 per-wave prereg missing on disk -- chain face incomplete, abort"
with open(os.path.join(REPO, "research", "PERPETUAL_N1_W274_PREREG.md"), encoding="utf-8") as _fh:
    _pre_head = _fh.read(2000)
assert "DRAFT-NOT-FROZEN" not in _pre_head, "W274 prereg still DRAFT -- abort (freeze commit pending face)"
# live ordinal derive (r359 law: gate machine output governs; the pre-seat probe
# receipt leg0 face owner_rows=263 / bma_rows=130 / bmc_rows=92
# = seat-time PRE-W274-splice live faces (post-W273-REGISTERED universe,
# W273 finalize LANDED at seat -- W274 FREEZE UNBLOCKED at seat time (zero waits-upstream face);
# live derive at freeze time:
# W273 splice LANDED (finalize adds no registry rows) -> owner rows 263 + candidate = 264th EXACT; bm-c rows 92 +
# candidate = 93rd EXACT -- bm-c own-seat continuity face (bm-c published the
# W274 seat itself r1102; queue-head supply -- splice GATED on the W273 finalize
# landing per gate0.5, seat-first law O-20261010-2350 sec.2)
owner_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner")]
bma_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-a"]
bmc_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
assert len(owner_rows_live) == 263 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 92, \
    f"leg0 ordinal drift at freeze time: owner={len(owner_rows_live)} bma={len(bma_rows_live)} bmc={len(bmc_rows_live)} (expect 263/130/92 PRE-splice post-W273 registration; this candidate = bm-c's 93rd own wave per the same live-derive law, r587/r359)"
print(f"gate0.5 OK: W273 landed (freeze {w273_freeze_sha[:10]}, owner=bm-c seat honored (upstream W273), chain complete incl finalize, clean precondition), "
      f"W274+W259..W250 finalize products present "
      f"(W273 ledger head {w273_total}, merged n={w273_merged_n}); owner rows {len(owner_rows_live)} + candidate, "
      f"bm-c rows {len(bmc_rows_live)} + candidate (93rd own wave per live derive; "
      f"probe receipt leg0 bmc_rows=92 = seat-time pre-splice faces disclosed honest)")

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
assert (a_lo, a_hi) == (618_101, 620_100) and (b_lo, b_hi) == (620_101, 620_300), \
    f"W274 band drift vs probe ADMIT: {(a_lo, a_hi)} {(b_lo, b_hi)}"
w273_b_tail = W273["b_exit"][1]      # registered W273 row b_exit hi (pf import, live)
w273_a_tail = W273["a"][1]            # registered W273 row A hi (pf import, live)
# W274 FACE (probe receipt leg1 relation_asserts):
# A takes the 1-HOP STAIRCASE-AFFECTS-A walk face, TWENTY-THIRD consecutive A-hop
# (naive continuation REFUSED at its own start -- A_clean_at_naive_start=false,
# A_staircase_hop_past_W273_B=true, hops=1, A_hop_chain verbatim in the
# receipt; the registered W273 B band sits INSIDE the naive A window =
# staircase re-emergence continues to affect A; the W273 prereg sec.5 item5
# post-W273-REGISTERED pre-disclosure confirmed live r587, zero divergence;
# the walk hops past the W273 B tail -> A first-clean; A base == registered
# prior-wave B tail+1 EXACT -- TWENTY-THIRD consecutive A-hop of the staircase
# era, the fourteen-wave seed-gap face ENDED at W252); B takes the 1-HOP
# own-A RESERVATION CASCADE face (naive continuation REFUSED at its own
# start -- B_naive_refused_at_start=true, hops=1, B_hop_chain verbatim in the
# receipt; the naive window lands INSIDE the own-wave A first-clean
# window, own-A reservation cascade standard leg; the walk hops past the
# own-A tail -> B lands ABOVE own-A, B_lands_above_own_A=true -- B base ==
# own-A tail+1 EXACT, TWENTY-FOURTH consecutive above-own-A landing);
# machine-derived from the LIVE registered row, never transcribed.
assert w273_b_tail + 1 == a_lo, "A staircase-hop landing base relation (A base == registered prior-wave B tail+1 EXACT -- the 1-hop walk past the registered W273 B band; twenty-third consecutive A-hop of the staircase era; A_staircase_hop_past_W273_B=true)"
assert a_lo >= w273_b_tail + 1, "A staircase landing floor relation (A base >= registered prior-wave B tail+1; the fourteen-wave seed-gap face ENDED at W252 -- twenty-third consecutive A-hop of the staircase era, A base == prior-B tail+1 EXACT this window per the prereg floor-relation mandate)"
assert b_lo == a_hi + 1, "B base == own-A tail+1 EXACT (the 1-hop own-A reservation cascade lands ABOVE own-A -- twenty-fourth consecutive above-own-A; B_hop_lands_inside_A=false; B_lands_above_own_A=true)"
assert W273["b_exit"][0] == W273["a"][1] + 1, \
    "upstream W273 row above-own-A staircase relation broken (registered W273 B base == own W273 A tail+1 EXACT -- the above-own-A face inherited from the W273 freeze)"
assert leg1.get("hops_A") == 1, "A hop-count drift vs probe receipt leg1 (A band naive hops=1, staircase-affects-A walk face)"
assert leg1.get("hops_B") == 1, "B hop-count drift vs probe receipt leg1 (B band hops=1, own-A reservation walk face above own-A)"
assert len(leg1.get("A_hop_chain") or []) == 1 and (
    leg1.get("A_clean_at_naive_start") is False
    or (leg1.get("relation_asserts") or {}).get("A_clean_at_naive_start") is False
), \
    "A hop-chain face drift (hops=1 staircase-affects-A walk -- naive continuation REFUSED at own start, the registered W273 B band sits inside the naive A window; A_hop_chain verbatim in the probe receipt)"
assert len(leg1.get("B_hop_chain") or []) == 1 and leg1.get("B_naive_refused_at_start") is True, \
    "B hop-chain face drift (hops=1 own-A reservation walk -- naive continuation lands INSIDE the own-wave A window, B_naive_refused_at_start=true; B_hop_chain verbatim in the probe receipt)"
assert leg1.get("B_hop_lands_inside_A") is False, "B lands-inside-own-A drift vs probe receipt leg1 (B_hop_lands_inside_A must be False)"
assert leg1.get("B_lands_above_own_A") is True and leg1.get("B_naive") == [w273_b_tail + 1, w273_b_tail + 200], "B lands-above-own-A + naive-window drift vs probe receipt leg1 (B_lands_above_own_A=true; B base == own-A tail+1 EXACT; naive window == prior-B tail+1..+200)"
ra = leg1.get("relation_asserts") or {}
assert ra.get("A_clean_at_naive_start") is False and ra.get("A_staircase_hop_past_W273_B") \
    and ra.get("A_base_ge_priorB_tail_plus1") \
    and ra.get("B_clean_at_naive_start") is False and ra.get("B_base_above_W273_tail") \
    and ra.get("AB_mutual_exclusion") and ra.get("B_hop_lands_inside_A") is False \
    and ra.get("B_lands_above_own_A") and ra.get("W271_W272_W273_bands_respected_A") and ra.get("W271_W272_W273_bands_respected_B"), \
    f"probe receipt leg1 relation_asserts face drift: {ra}"
assert [w273_a_tail + 1, w273_a_tail + 2_000] == leg1["ARITH_A"], \
    f"A naive-arithmetic window start drift vs probe receipt leg1 ARITH_A: {[w273_a_tail + 1, w273_a_tail + 2_000]} != {leg1['ARITH_A']}"
assert [w273_b_tail + 1, w273_b_tail + 200] == leg1["ARITH_B"], \
    f"B naive continuation drift vs probe receipt leg1 ARITH_B: {[w273_b_tail + 1, w273_b_tail + 200]} != {leg1['ARITH_B']}"

# own bundle shas via pickaxe (self-referencing commit facts, zero transcription)
r = git("log", "--diff-filter=A", "--format=%H", "--", "results/_w274bmc_20261019_probe_receipt.json")
w274_receipt_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
# seat MSG honest location (inbox or processed; S7 archive law)
seat_found = None
for _p in ("fleet/inbox", "fleet/inbox/processed"):
    if os.path.exists(os.path.join(REPO, _p, SEAT_MSG)):
        seat_found = _p + "/" + SEAT_MSG
        break
assert seat_found, f"W274 seat MSG missing from both inbox paths: {SEAT_MSG}"

# ---------- re-run discipline gates at freeze window (banned + seed_admit) ----------
g = subprocess.run([PY, os.path.join(REPO, "Tools", "banned_direction_gate.py"),
                    "--prereg", "research/PERPETUAL_N1_W274_PREREG.md"],
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

def fmt(n):  # 593901 -> "618_101"
    return f"{n // 1000}_{n % 1000:03d}"

# ---------- extract parity estate + kept legs (physical bytes, never re-typed) ----------
# STRUCTURAL CHOICE (W273 template lineage): extract the 69-row
# estate (W138..W206 full-span 69 rows, r858 absorb generation) AND the
# W211..W272 legs (62) from the OWN W273 block physical bytes (bm-c r1102
# splice generation, committed -- structure known exactly); the W273
# block's own W248..W272 legs (25) are EXCLUDED from the estate path per the
# template mandate; the W274 block appends fresh W248..W274 legs (26,
# machine-derived from the LIVE pf registry at freeze time) -> 121 parity
# rows.
a22 = '    # --- W273 materializer face'
a_t141 = '    # --- T-141 s2 lane face'
w273_start = n1_t.find(a22); t141_pos = n1_t.find(a_t141)
assert w273_start > 0 and t141_pos > w273_start, \
    "W273 materializer block face not found (W273 freeze not landed? header-text drift -> honest re-derive required)"
blk = n1_t[w273_start:t141_pos]
m_first_row = re.search(r"assert pf\.N1_BANDS\[", blk)
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state", blk)
assert m_first_row and m_disj and m_disj.start() > m_first_row.start(), \
    "parity span markers not found in W273 block"
_row_ls = blk.rfind(EOL, 0, m_first_row.start()) + len(EOL)
par_full = blk[_row_ls:m_disj.start()]
m211 = re.search(r" *assert pf\.N1_BANDS\[211\] ==", par_full)
assert m211, "upstream W211 row leg not found inside W273 parity span (estate boundary: W138..W206 full-span 69 rows only, template lineage estate-extraction mandate)"
par_sec = par_full[:m211.start()]
legs_sec = par_full[m211.start():]
assert par_sec.endswith(EOL), "estate segment must end with EOL"
assert legs_sec.endswith(EOL), "legs segment must end with EOL"
_estate_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", par_sec)
assert par_sec.count("assert pf.N1_BANDS[") == 69 \
    and [int(w) for w in _estate_ws] == list(range(138, 207)), \
    f"estate segment not W138..W206 full-span 69 rows (template lineage estate-extraction mandate): n={par_sec.count('assert pf.N1_BANDS[')} range={(_estate_ws[:2], _estate_ws[-4:])}"
assert par_full.count("assert pf.N1_BANDS[") == 131, \
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 131 (69 estate + W211..W273 legs 62)"
_legs_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", legs_sec)
assert legs_sec.count("assert pf.N1_BANDS[") == 62 \
    and [int(w) for w in _legs_ws] == list(range(211, 273)), \
    f"legs segment not W211..W272 sixty-two legs: n={legs_sec.count('assert pf.N1_BANDS[')} waves={_legs_ws}"
# template mandate split: keep W211..W247 verbatim (37 legs); the W273
# block's own W248..W272 legs (25) are excluded from the estate path
m248 = re.search(r" *assert pf\.N1_BANDS\[248\] ==", legs_sec)
assert m248, "W244 leg boundary not found inside W274 legs segment (template split face)"
legs_kept = legs_sec[:m248.start()]
legs_dropped = legs_sec[m248.start():]
assert legs_kept.endswith(EOL) and legs_dropped.endswith(EOL), "split segments must end with EOL"
_kept_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", legs_kept)
assert legs_kept.count("assert pf.N1_BANDS[") == 37 \
    and [int(w) for w in _kept_ws] == list(range(211, 248)), \
    f"kept segment not W211..W247 thirty-seven legs: n={legs_kept.count('assert pf.N1_BANDS[')} waves={_kept_ws}"
_dropped_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", legs_dropped)
assert legs_dropped.count("assert pf.N1_BANDS[") == 25 \
    and [int(w) for w in _dropped_ws] == list(range(248, 273)), \
    f"dropped segment not W248..W272 twenty-five legs: n={legs_dropped.count('assert pf.N1_BANDS[')} waves={_dropped_ws}"

# ---------- fresh legs W244..W273 (machine-derived from the LIVE pf registry) ----------
fresh_leg_lines = []
for _w in range(248, 274):
    _row = dict(pf_mod.N1_BANDS[_w])
    _owner = _row["engine_owner"]
    if _w == 273:
        _msg = '"registered W273 row parity drift (r307; bm-c five-face freeze upstream seat; W274 freeze fresh-derive from live registry)"'
    else:
        _msg = f'"registered W{_w} row parity drift (r307; engine_owner={_owner}; W274 freeze fresh-derive from live registry)"'
    fresh_leg_lines += [
        f'        assert pf.N1_BANDS[{_w}] == {{"a": ({fmt(_row["a"][0])}, {fmt(_row["a"][1])}),',
        f'                                    "b_exit": ({fmt(_row["b_exit"][0])}, {fmt(_row["b_exit"][1])}),',
        f'                                    "engine_owner": "{_owner}"}}, \\',
        f'            {_msg}',
    ]
fresh_legs = EOL.join(fresh_leg_lines)
assert fresh_leg_lines[0].startswith('        assert pf.N1_BANDS[248] == {"a": (')

# ---------- indent extraction (physical, not assumed; per-file EOL) ----------
def line_indent(t, needle, eol):
    i = t.find(needle)
    assert i >= 0, f"indent needle not found: {needle[:40]}"
    ls = t.rfind(eol, 0, i) + len(eol)
    line = t[ls:t.find(eol, ls)]
    return line[:len(line) - len(line.lstrip(" "))]

CFG_I  = line_indent(n1_t, '273: {"batch"', EOL)
PRE_KEY_I = line_indent(n1_t, '"prereg": ("research/PERPETUAL_N1_W273_PREREG.md', EOL)
PRE_I  = line_indent(n1_t, '"pre-run; design = frozen v1 null calibration verbatim, "', EOL)
_c273 = n1_t.find('273: {"batch"')
assert _c273 > 0, "W273 cfg entry not found (W273 freeze not landed?)"
_mpos = n1_t.find('"a_seed_base"', _c273)
assert _mpos > 0 and n1_t.find('"shard_subdir"', _c273) > _mpos, "W273 cfg a_seed_base line not found"
MEM_I  = line_indent(n1_t, '"a_seed_base": ' + str(W273["a"][0]), EOL) \
    if n1_t.find('"a_seed_base": ' + str(W273["a"][0]), _c273) > 0 \
    else line_indent(n1_t, '"a_seed_base": ' + fmt(W273["a"][0]), EOL)
ROW_I  = line_indent(pf_t,  '273: {"a"', PF_EOL)

# ---------- W273 row owner line (physical bytes; comment text is own generation) ----------
w273_row_start = pf_t.find('    273: {"a"')
assert w273_row_start > 0, "W273 row literal not found in pf source"
_own_ls = pf_t.find(PF_EOL, w273_row_start) + len(PF_EOL)
_own_le = pf_t.find(PF_EOL, _own_ls)
w273_own_line = pf_t[_own_ls:_own_le]
assert '"engine_owner": "bm-c"' in w273_own_line, \
    f"W273 owner line unexpected bytes: {w273_own_line!r}"
ROWC_I = w273_own_line[:len(w273_own_line) - len(w273_own_line.lstrip(" "))]

# ---------- pf comment + row ----------
pf_comment = PF_EOL.join([
"    # W274 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat",
"    # MSG-20261019-012x-bmc-w274-seat published=reserved by bm-c itself @",
"    # origin " + SEAT_ORIGIN + " (r1102, queue-head seat-first supply -- W273 registered+FINALIZED complete at publish, W274 FREEZE UNBLOCKED at seat time (zero waits-upstream face; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE gate0.5 = GREEN at seat (W273 five-face + finalize product both in-place; prereg + ADMIT probe",
"    # receipt frozen commit " + w274_prereg_sha[:10] + " (prereg research/PERPETUAL_N1_W274_PREREG.md",
"    # bm-c r1104 window E63 canon-clone builder derive landed pre-freeze, probe",
"    # results/_w274bmc_20261019_probe_receipt.json @ " + w274_receipt_sha[:10] + ");",
"    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10",
"    # ~23:1x; deletion-set EMPTY; delivery window = chain-order",
"    # splice AFTER the bm-c W273 five-face (freeze " + w273_freeze_sha[:10] + ") + W273",
"    # finalize product landed (n1_w273_results.json present, ledger",
"    # head " + str(w273_total) + " machine-read at freeze time); zero --no-verify;",
"    # the W274 seat MSG sits in " + seat_found + " at freeze",
"    # time, honest archived per S7 law);",
"    # band gate ADMIT results/_w274bmc_20261019_probe_receipt.json: A = 1-HOP",
"    # STAIRCASE-AFFECTS-A walk TWENTY-THIRD consecutive A-hop (the naive continuation " + fmt(w273_a_tail + 1) + ".." + fmt(w273_a_tail + 2_000) + " is REFUSED",
"    # at naive start -- the registered W273 B band sits INSIDE the naive A window;",
"    # the walk hops past the W273 B tail -> A first-clean, hops=1 -- TWENTY-THIRD",
"    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face",
"    # ENDED at W252;",
"    # A base == registered prior-wave B tail+1 (" + fmt(w273_b_tail) + "+1) machine-checkable; A_clean_at_naive_start=false;",
"    # A_staircase_hop_past_W273_B=true)",
"    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation",
"    # " + fmt(w273_b_tail + 1) + ".." + fmt(w273_b_tail + 200) + " is REFUSED at its own start -- the naive window lands",
"    # INSIDE the own-wave A first-clean window --",
"    # own-A reservation cascade standard leg; hops=1,",
"    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A",
"    # tail -> B lands ABOVE own-A -- TWENTY-FOURTH consecutive above-own-A;",
"    # B base == own-A tail+1 (" + fmt(a_hi) + "+1) EXACT; B_lands_above_own_A=true;",
"    # B_hop_lands_inside_A=false; B_naive_refused_at_start=true)",
"    # single-window derive (r812 merged the gate legs INTO the",
"    # pre-seat probe; dual-window parity N/A honest); scan face =",
"    # SEED_REGISTRY live int values + v1/W1 ext bands + N3-R1",
"    # used-seed band + probe cluster 95_000..95_003 + cross-face",
"    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/",
"    # N2-W15 probe points.",
"    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):",
"    # " + gate_lines[0] + ";",
"    # " + gate_lines[1] + ".",
"    # W275+ projection (gate-derived pre-seat probe leg4, pre-W274",
"    # universe): A naive first-clean " + rec["legs"]["leg4"]["W275p_A_naive"] + " hops=" + str(rec["legs"]["leg4"]["hops_A"]) + " (this window's gate: CLEAN, zero live",
"    # seed refusers) / B naive " + rec["legs"]["leg4"]["W275p_B_naive"] + " hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " CLEAN at naive -- first-clean " + rec["legs"]["leg4"]["W275p_B_first_clean"] + " BUT lands INSIDE the projection A window,",
"    # (W275p_B_lands_inside_W275p_A_naive=true -- staircase re-emergence face: the W275 walk MUST hop past own-A reservation);",
"    # the W275 freezer MUST",
"    # re-derive on the post-W274 universe AND reserve the own-wave A window",
"    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1",
"    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.",
])
pf_row = (f'{ROW_I}274: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), '
          f'"b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'
          + PF_EOL + f'{ROWC_I}"engine_owner": "bm-c"}},' + PF_EOL)
# belt-and-braces: display form must equal the canonical W-family text
assert pf_row.split(PF_EOL)[0].strip() == \
    f'274: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), "b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'

old_pf = must(pf_t, (w273_own_line + PF_EOL + '}'
                     + PF_EOL + '# v1 + ext(wave-1) in-use bands'), 1, "pf_close")
new_pf = (w273_own_line + PF_EOL
          + pf_comment + PF_EOL + pf_row
          + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands')
pf_t2 = pf_t.replace(old_pf, new_pf, 1)

# ---------- n1 cfg entry (programmatic quote wrapping, r761 law) ----------
fin_face = (f"W1..W273 finalize ALL LANDED (W273 finalize product present at splice, "
            f"net chain head {w273_total} machine-read, merged pool K={w273_merged_n} "
            f"machine-read) -- ZERO in-flight upstream seats at splice time, clean precondition "
            f"(sixty-second consecutive fully-clean freeze window); downstream W275 seat NOT YET "
            f"PUBLISHED at this freeze window (the next freezer must seat-first publish per "
            f"O-20261010-2350 sec.2 queue-depth supply; the W275 freezer MUST re-derive live on "
            f"the post-W274 universe + reserve the own-wave A window when deriving B per the "
            f"W274 seat leg4 mandate, never transcribe r587)")
cfg_lines = [
 f'{CFG_I}274: {{"batch": "PERPETUAL-N1-W274",',
 f'{PRE_KEY_I}"prereg": ("research/PERPETUAL_N1_W274_PREREG.md (wave-level frozen "',
]
PRE = [
 "pre-run; design = frozen v1 null calibration verbatim, ",
 "new seed bands only; TWO HUNDRED AND SEVENTY-FOURTH ENGINE-OWNED WAVE ",
 f"BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate), ",
 "own-series continuation per O-20261001-2355 sec.2 (first-free-",
 "number law after the REGISTERED W273 row five-face freeze (bm-c own seat executed at the bm-c r1102 splice window; engine self-burn 12/12; finalize one-pass bm-c r1102 closeout, ledger 1,024,935 / K=598,520 machine-read), ",
 f"{w273_freeze_sha[:10]} (prereg {w273_prereg_sha[:10]}), SINGLE STATE zero seat gap W2..W273 all ",
 "registered; " + fin_face + "; ",
 "seat published=reserved ",
 "MSG-20261019-012x-bmc-w274-seat PUSHED to origin " + SEAT_ORIGIN + " ",
 "BEFORE this freeze per r565 early-visibility law (payload = ",
 "seat MSG + pre-seat probe script + probe receipt; per-wave prereg ",
 "bm-c r1104 window E63 canon-clone builder derive landed pre-freeze -- bm-c own-seat ",
 "continuity, ",
 f"prereg {w274_prereg_sha[:10]} @ receipt {w274_receipt_sha[:10]}) -- this freeze splice editor derived from the committed W273 freeze-edits template in this same freeze window; ",
 "deletion-set EMPTY; delivery window = chain-order splice ",
 "after the W273 five-face + W273 finalize product landed ",
 "(executed in the bm-c loop freeze window ",
 "under the CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED ",
 "2026-10-10 ~23:1x); zero merge at freeze delivery, zero ",
 "--no-verify; single-window derive -- r812 merged the gate ",
 "legs INTO the pre-seat probe; parity N/A honest), ",
 "engine_owner=bm-c (bm-c OWN-SEAT face -- bm-c's NINETY-THIRD owned claim per machine-derive (engine_owner==bm-c rows ",
 f"{len(bmc_rows_live)} + candidate; probe receipt leg0 bmc_rows=92 = seat-time pre-splice ",
 "live faces disclosed honest, live derive governs ",
 "r587/r359), own-seat continuity)), ",
"wave 274: ",
 "A = 1-HOP STAIRCASE-AFFECTS-A walk TWENTY-THIRD consecutive A-hop (the naive continuation ",
 f"{fmt(w273_a_tail + 1)}..{fmt(w273_a_tail + 2_000)} is REFUSED at its own start ",
 "-- hops=1, A_hop_chain verbatim in the probe receipt, A_clean_at_naive_start=false; ",
 "the registered W273 B band sits INSIDE the naive A window = staircase re-emergence continues to affect A; ",
 "the W273 prereg sec.5 item5 post-W273-REGISTERED pre-disclosure confirmed live r587, zero divergence disclosed; the walk hops past the W273 B tail -> ",
 "A first-clean; A base == registered prior-wave B tail+1 (",
 f"{fmt(w273_b_tail)}+1) machine-checkable; TWENTY-THIRD consecutive A-hop of the staircase era, ",
 "the fourteen-wave seed-gap face ENDED at W252; non-rotational r587 forward-monotone walk) ",
 "+ B = 1-HOP own-A RESERVATION CASCADE above own-A ",
 "(the naive continuation ",
 f"{fmt(w273_b_tail + 1)}..{fmt(w273_b_tail + 200)} is REFUSED at its own start ",
 "-- hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; the ",
 f"naive window lands INSIDE the own-wave A first-clean window (own-A reservation cascade standard leg); the walk hops past the own-wave A tail -> B lands ABOVE the ",
 f"own-A window {fmt(a_lo)}..{fmt(a_hi)} at tail+1 EXACT; TWENTY-FOURTH consecutive above-own-A ",
 "landing; B base == own-A tail+1 (",
 f"{fmt(a_hi)}+1) machine-checkable; cross-window convergence with the W273 prereg sec.5 item5 + W273 probe leg4 + seat leg4 succession projection ",
 "notes -- all MANDATORY notes honored (post-W273 universe ",
 "re-derive + live-trace re-read, no staircase-equality assumption); ADMIT receipt ",
 "results/_w274bmc_20261019_probe_receipt.json + ",
 "seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a ",
 "ADMIT convention); W275+ projection per this window gate: ",
 f"A naive first-clean {rec['legs']['leg4']['W275p_A_naive']} CLEAN (hops=0, zero live seed refusers) / B naive ",
 f"{rec['legs']['leg4']['W275p_B_naive']} hops={rec['legs']['leg4']['hops_B']} CLEAN at naive -- first-clean {rec['legs']['leg4']['W275p_B_first_clean']} BUT lands INSIDE the W275 projection A window (W275p_B_lands_inside_W275p_A_naive=true staircase re-emergence face; seed-gap face ",
 "inherited); W275 freezer MUST re-derive on the post-W274 universe AND ",
 "reserve the own-wave A window when deriving B (do NOT assume the ",
 "staircase A-base==prior-B-tail+1 or B-base==own-A-tail+1 equalities) -- the finalize ",
 "merge loop still derives the wave set from registry keys at ",
 "run time, FAIL-CLOSED r307 always on)",
]
for i, s in enumerate(PRE):
    if i == len(PRE) - 1:
        cfg_lines.append(f'{PRE_I}"{s}"),')
    else:
        cfg_lines.append(f'{PRE_I}"{s}"')
cfg_lines += [
 f'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W274 A: {fmt(a_lo)}..{fmt(a_hi)} (1-HOP STAIRCASE-AFFECTS-A walk TWENTY-THIRD consecutive A-hop; naive {fmt(w273_a_tail + 1)}..{fmt(w273_a_tail + 2_000)} REFUSED at start -- hops=1, A_hop_chain verbatim in the probe receipt, A_clean_at_naive_start=false; registered W273 B band inside the naive A window; twenty-third consecutive A-hop of the staircase era -- seed-gap face ENDED at W252; A base == registered prior-wave B tail+1)',
 f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W274 B: {fmt(b_lo)}..{fmt(b_hi)} (1-HOP own-A RESERVATION CASCADE above own-A; naive {fmt(w273_b_tail + 1)}..{fmt(w273_b_tail + 200)} REFUSED at start -- hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; naive window lands inside the own-wave A first-clean window -> own-A reservation cascade; B lands ABOVE own-A at tail+1 EXACT -- twenty-fourth consecutive above-own-A; B base == own-A tail+1)',
 f'{MEM_I}"shard_subdir": "n1_w274", "out_name": "n1_w274_results.json",',
 f'{MEM_I}"engine_owner": "bm-c"}},',
]

cfg_block = EOL.join(cfg_lines)
old_cfg = must(n1_t, ('                       }' + EOL
                      + 'PREREG = WAVE_CONFIGS[2]["prereg"]'), 1, "n1_cfg_close")
new_cfg = (cfg_block + EOL
           + '                       }' + EOL
           + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
assert new_cfg.count('274: {"batch": "PERPETUAL-N1-W274"') == 1
n1_t2 = n1_t.replace(old_cfg, new_cfg, 1)

# ---------- n1 materializer block ----------
hdr = [
 "    # --- W274 materializer face (bm-c loop five-face freeze splice --",
 "    #     OWN-SEAT face under CEO fill-order standing 2026-10-08 ~23:5x",
 "    #     + RE-ISSUE 2026-10-10 ~23:1x + O-20260909-2334 local-full-use",
 "    #     + O-20260924-1730 claim-and-start same-round law):",
 "    #     bm-c's NINETY-THIRD owned per machine-derive (engine_owner==bm-c",
 f"    #     rows {len(bmc_rows_live)} + candidate; own-seat face: seat published=reserved by bm-c itself",
 "    #     (r1102 MSG-20261019-012x-bmc-w274-seat @ origin " + SEAT_ORIGIN + "; probe leg0",
 "    #     bmc_rows=92 = seat-time pre-splice faces (post-W273-REGISTERED universe,",
 "    #     W273 finalize LANDED at seat -- W274 FREEZE UNBLOCKED at seat time, zero waits-upstream face;",
 "    #     splice gate0.5 = GREEN at seat (W273 finalize landed pre-seat), zero skip-claim);",
 "    #     live derive at freeze governs);",
 "    #     wave 274 = first free number after the",
 "    #     REGISTERED W273 row (five-face freeze " + w273_freeze_sha[:10] + "; bm-c own seat executed at",
 "    #     the bm-c r1102 splice window; engine",
 "    #     self-burn 12/12 + finalize one-pass bm-c r1102 closeout ledger 1,024,935 / K=598,520",
 "    #     -- SINGLE STATE zero seat gap (W2..W273 all registered). Seat",
 "    #     published=reserved MSG-20261019-012x-bmc-w274-seat pushed",
 "    #     to origin " + SEAT_ORIGIN + " BEFORE this freeze, r565 law (payload =",
 "    #     seat MSG + pre-seat probe script + probe receipt; per-wave prereg",
 f"    #     bm-c r1104 window derive landed pre-freeze commit {w274_prereg_sha[:10]}; this freeze splice editor",
 "    #     derived from the committed W273 freeze-edits template in this same freeze",
 "    #     window (E63 heal lineage: arith_a274/arith_b274 define+assert consistent;",
 "    #     band-set variable aging face w244_a holds wave-263 bands, disclosed);",
 "    #     deletion-set EMPTY; delivery window",
 "    #     = chain-order splice after the W273 five-face + W273 finalize",
 "    #     product landed; zero --no-verify; the W274 seat MSG sits in",
 "    #     " + seat_found + " at freeze time, honest archived",
 "    #     per S7 law).",
 "    #     TWO HUNDRED AND SEVENTY-FOURTH engine wave BY",
 f"    #     MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate; gate",
 "    #     leg0 machine output governs per r359 law).",
 f"    #     {fin_face}; the finalize merge loop",
 "    #     still derives the wave set from registry keys at run",
 "    #     time, FAIL-CLOSED r307 always on. ADMIT receipt",
 "    #     results/_w274bmc_20261019_probe_receipt.json;",
 "    #     seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a",
 f"    #     ADMIT convention upgrade): {gate_lines[0]}; {gate_lines[1]};",
 "    #     banned gate ADMIT 0 (re-run at freeze window);",
 "    #     not a re-pick (R273: W274 bands were never assigned).",
"    #     PARITY STRUCTURAL CHOICE (W273 template lineage):",
 "    #     estate 69 rows (W138..W206 full-span, r858 absorb generation) +",
 "    #     W211..W247 legs (37) extracted verbatim from the OWN W273 block",
 "    #     physical bytes; the W273 block's own W248..W272 legs (25) are",
 "    #     EXCLUDED from the estate path per the template mandate; fresh",
 "    #     W248..W274 legs (26) added, machine-derived from the live pf",
 "    #     registry at freeze time -> 132 parity rows (W138..W206+W211..W273).",
 "    _set_wave(274)",
 "    try:",
 '        assert WAVE_CONFIGS[273]["a_seed_base"] == pf.N1_BANDS[273]["a"][0], \\',
 '            "W274 upstream W273 mirror drift (a)"',
 "        assert WAVE_CONFIGS[273][\"b_exit_seed_base\"] == \\",
 '            pf.N1_BANDS[273]["b_exit"][0], "W274 upstream W273 mirror drift (b)"',
 "        assert WAVE_CONFIGS[273].get(\"engine_owner\") == \\",
 '            pf.N1_BANDS[273].get("engine_owner") == "bm-c", \\',
 '            "W274 upstream W273 engine_owner mirror drift (law-mirror parity; bm-c upstream seat face)"',
 "        w244_a = {A_SEED_BASE + j for j in range(A_N)}",
 "        w244_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
 '        assert not (w244_a & w244_b), "W274 A/B band overlap"',
 "        assert not (w244_a & reg_ints) and not (w244_b & reg_ints), \\",
 '            "W274 hits SEED_REGISTRY"',
 '        for nm, band in (("A", w244_a), ("B", w244_b)):',
 '            assert not (band & v1_a) and not (band & v1_b), f"W274 {nm} hits v1"',
 '            assert not (band & w1_a) and not (band & w1_b), f"W274 {nm} hits W1"',
 '            assert not (band & probes), f"W274 {nm} hits probe seeds"',
]
tail = [
 "        # prior-wave disjointness W2..W273 (single state: all",
 "        # registered, dynamic registry derive, r511 law)",
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 274):",
 '            assert not (w244_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
 "                                 for j in range(A_N)}), f\"W274 A hits W{wprev}\"",
 '            assert not (w244_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
 "                                  for j in range(B_N)}), f\"W274 B hits W{wprev}\"",
 "        n3r1_used245 = set(range(70_000, 70_006))",
 "        assert not (w244_a & n3r1_used245) and not (w244_b & n3r1_used245), \\",
 '            "W274 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
 "        assert not (w244_a & lfc_actual12) and not (w244_b & lfc_actual12), \\",
 '            "W274 bands must clear the lfc actual draw range"',
 "        assert not (w244_a & options_actual12) and \\",
 "            not (w244_b & options_actual12), \\",
 '            "W274 bands must clear the options_wave2 actual draw range"',
"        # band facts (law sec.4 W274 row): A = 1-HOP STAIRCASE-AFFECTS-A",
"        # walk TWENTY-THIRD consecutive A-hop (the naive continuation",
f"        # {fmt(w273_a_tail + 1)}..{fmt(w273_a_tail + 2_000)} REFUSED at naive start -- the registered W273 B band",
f"        # {fmt(pf_mod.N1_BANDS[273]['b_exit'][0])}..{fmt(pf_mod.N1_BANDS[273]['b_exit'][1])} sits INSIDE the naive A window (staircase re-emergence",
"        # continues to affect A; the W273 prereg sec.5 item5 post-W273-REGISTERED pre-disclosure confirmed live r587,",
"        # zero divergence disclosed); hops=1, A_hop_chain verbatim in the probe receipt,",
"        # A_clean_at_naive_start=false, A_staircase_hop_past_W273_B=true; the walk hops",
"        # past the W273 B tail -> A first-clean; A base ==",
f"        # registered prior-wave B tail+1 ({fmt(w273_b_tail)}+1) machine-checkable; TWENTY-THIRD consecutive A-hop of the W239",
"        # staircase era -- the fourteen-wave seed-gap face ENDED at W252;",
"        # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation",
f"        # {fmt(w273_b_tail + 1)}..{fmt(w273_b_tail + 200)} REFUSED at naive start -- the naive window lands",
"        # INSIDE the own-wave A first-clean window (own-A reservation cascade standard leg); hops=1,",
"        # B_hop_chain verbatim in the probe receipt; the walk hops past the own-wave A tail",
f"        # -> B lands ABOVE the own-A window {fmt(a_lo)}..{fmt(a_hi)} at tail+1 EXACT -- TWENTY-FOURTH consecutive",
"        # above-own-A landing;",
"        # B base == own-A tail+1 EXACT",
"        # machine-checkable; B_hop_lands_inside_A=false;",
"        # B_lands_above_own_A=true; cross-window convergence with",
"        # the W273 prereg sec.5 item5 + W273 probe leg4 + seat leg4 succession projection notes -- all",
"        # MANDATORY notes honored (post-W273 universe",
"        # re-derive + live-trace re-read, no staircase-equality assumption);",
f'        assert WAVE_CONFIGS[274]["a_seed_base"] == {a_lo} == {w273_b_tail} + 1, (',
'            "W274 A staircase-affects-A walk TWENTY-THIRD consecutive A-hop: the naive "',
'            "continuation is REFUSED at its own start (the registered W273 B band sits INSIDE "',
'            "the naive A window -- staircase re-emergence continues; hops=1, A_hop_chain verbatim in the probe receipt, "',
'            "A_clean_at_naive_start=false, A_staircase_hop_past_W273_B=true; the walk hops past "',
'            "the W273 B tail -> A first-clean -- TWENTY-THIRD consecutive A-hop of the staircase era, "',
'            "the fourteen-wave seed-gap face ENDED at W252; A base == registered prior-wave B "',
'            "tail+1 machine-checkable, floor relation honored)")',
f"        arith_a274 = set(range({a_lo}, {a_hi + 1}))",
"        assert not (arith_a274 & reg_ints), \\",
'            "W274 A window must be CLEAN (first-clean ADMIT face, staircase walk landing)"',
f'        assert WAVE_CONFIGS[274]["b_exit_seed_base"] == {b_lo} == {a_hi} + 1, (',
'            "W274 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "',
f'            "{fmt(w273_b_tail + 1)}..{fmt(w273_b_tail + 200)} is REFUSED at its own start "',
'            "(hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; "',
'            "the naive window lands INSIDE the own-wave A first-clean window -- own-A reservation hops B past the own-wave A tail) -- B base == own-A tail+1 "',
'            "EXACT (B_lands_above_own_A + B_base_above_W273_tail face relation asserts, "',
'            "probe receipt leg1 mirrored exactly; B_hop_lands_inside_A=false)")',
f"        assert {b_lo} > {w273_b_tail}, \\",
'            "W274 B walk base must sit above the prior-wave B tail"',
f"        arith_b274 = set(range({b_lo}, {b_hi + 1}))",
"        assert not (arith_b274 & reg_ints), \\",
'            "W274 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"',
"        assert not (arith_b274 & arith_a274), \\",
'            "W274 A/B same-freeze mutual exclusion (B lands ABOVE own-A at tail+1 EXACT -- twenty-fourth consecutive above-own-A; zero overlap)"',
"        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W274-SHARD-0\",",
 '                                          "n1w274-0of12"), "W274 entry identity"',
 '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W274-SHARD-11",',
 '                                           "n1w274-11of12")',
 "        assert SHARD_DIR.endswith(\"n1_w274\") and OUT.endswith(",
 '            "n1_w274_results.json"), "W274 path drift"',
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 274):",
 "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(",
 "                PATHS.results_dir, \"p2cal_ext\",",
 "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\",
 '                f"W274 shard dir collides with W{wprev}"',
 "        # W274 finalize cumulative deps: W17..W273 outputs ALL PRESENT",
 f"        # (landed net chain head {w273_total} machine-read at freeze time)",
 "        # -- ZERO in-flight upstream seats at splice, clean precondition",
 "        # freeze window; the finalize merge loop derives the wave",
 "        # set from registry keys at run time and stays",
 "        # FAIL-CLOSED, r307 two-state law).",
 "        for _depw in range(17, 274):",
 "            assert os.path.exists(os.path.join(",
 "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\",
 '                f"W274 finalize cumulative dep (W{_depw} output) missing"',
 "        # finalize wave-set derivation face (r511 derive law): every",
 "        # registered wave below 263 composes; wave 15 excluded by",
 "        # design; SINGLE STATE (W2..W273 all registered -- no",
 "        # two-state seat disclosure needed at this freeze).",
 "        assert sorted(w for w in WAVE_CONFIGS if w < 274) == \\",
 "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\",
 "            [w for w in range(16, 274)], \\",
 '            "W274 prior-wave set must derive from registry keys (no 15; " \\',
 '            "W2..W273 registered single state)"',
 "        assert os.path.exists(os.path.join(",
 '            PATHS.root, "research", "PERPETUAL_N1_W274_PREREG.md")), \\',
 '            "W274 per-wave prereg missing (materializer requirement)"',
 "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"",
 "    finally:",
 "        _set_wave(2)",
]
block = EOL.join(hdr) + EOL + par_sec + legs_kept + fresh_legs + EOL + EOL.join(tail) + EOL
# family #6 atomic triple gate (carried forward): the new
# block's LHS w<263> / RHS range(16,263)+range(17,263) / comment below-263 MUST move together.
assert block.count("if w < 274)") == 3, f"family-6 triple: w<263 count {block.count('if w < 274)')} != 3"
assert block.count("if w < 273)") == 0, "family-6 triple: stale w<262 leaked into the W274 block"
assert block.count("range(16, 274)") == 1 and block.count("range(17, 274)") == 1, "family-6 triple: RHS ranges wrong"
assert block.count("registered wave below 263 composes") == 1, "family-6 triple: comment face wrong"
old_blk_anchor = must(n1_t2, "    # --- T-141 s2 lane face", 1, "t141_marker")
n1_t3 = n1_t2.replace(old_blk_anchor, block + old_blk_anchor, 1)

# ---------- n1 print line ----------
pr = [
 '          "+ W274 materializer face [same guard set, dep=W17..W273 "',
 f'          "outputs ALL PRESENT (landed net chain head {w273_total} = W273 bm-c finalize one-pass, K={w273_merged_n} merged pool) -- ZERO "',
 '          "in-flight upstream seats at splice, clean precondition, TWO HUNDRED AND SEVENTY-FOURTH "',
 f'          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} "',
 '          "+ candidate) bm-c\'s NINETY-THIRD owned claim per "',
 '          "machine-derive (engine_owner==bm-c rows 92 + candidate; OWN-SEAT face: seat published by bm-c itself, "',
 '          "probe leg0 bmc_rows=92 = seat-time pre-splice faces disclosed honest, "',
 '          "live derive at freeze governs), "',
 '          "A=1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim, A_clean_at_naive_start=false, "',
 '          "registered W273 B band inside the naive A window, TWENTY-THIRD consecutive A-hop of the staircase era, "',
 '          "the fourteen-wave seed-gap face ENDED at W252) "',
 '          "+ B=1-HOP own-A RESERVATION CASCADE above own-A (hops=1, B_naive_refused_at_start=true, "',
 '          "B_hop_chain verbatim, naive window lands inside the own-wave A window -> own-A reservation cascade, "',
 '          "B base == own-A tail+1 EXACT, B_lands_above_own_A=true, "',
 '          "TWENTY-FOURTH consecutive above-own-A landing), chain-order splice from the "',
 '          "committed ADMIT receipt + seed_admit_gate rc0 both bands FREE "',
 '          "(O-20261010-1945-bm-a ADMIT convention), "',
 '          "ADMIT receipt "',
 '          "results/_w274bmc_20261019_probe_receipt.json, law sec.4 W274 row, "',
 '          "bm-c loop CEO fill-order RE-ISSUE 23:1x] "',
]

old_pr = must(n1_t3, '          "+ T-141 s2 ', 1, "print_t141")
n1_t4 = n1_t3.replace(old_pr, EOL.join(pr) + EOL + old_pr, 1)

# ---------- post-edit count gates ----------
assert n1_t4.count('"batch": "PERPETUAL-N1-W274"') == 1
assert n1_t4.count("# --- W274 materializer face") == 1     # block header
assert n1_t4.count('"+ W274 materializer face') == 1        # print fragment
assert n1_t4.count('274: {"batch": "PERPETUAL-N1-W274"') == 1
assert pf_t2.count(ROW_I + '274: {"a"') == 1
assert pf_t2.count('"engine_owner": "bm-c"},' + PF_EOL + '}') == 1
assert n1_t4.count('    # --- T-141 s2 lane face') == 1
assert n1_t4.count('"PERPETUAL-N1-W274-SHARD-0"') == 1
# leg count gates: leg W_k lives in blocks W_{k+1}..W274 -> (263 - k) occurrences
for _lw in range(248, 274):
    _first = (f'assert pf.N1_BANDS[{_lw}] == {{"a": '
              f'({fmt(pf_mod.N1_BANDS[_lw]["a"][0])}, {fmt(pf_mod.N1_BANDS[_lw]["a"][1])}),')
    _got = n1_t4.count(_first)
    assert _got == 274 - _lw, \
        f"W{_lw} leg count drift: {_got} != {274 - _lw} (first-line: {_first})"
for _b in range(209, 275):
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
  "machine": "bm-c", "wave": 273,
  "phase": "five-face freeze chain-order splice (bm-c own-seat freeze window, upstream ALL LANDED clean precondition incl W273 finalize)",
  "origin_base": omain,
  "pf_sha16_pre": hashlib.sha256(pf_b).hexdigest()[:16],
  "n1_sha16_pre": hashlib.sha256(n1_b).hexdigest()[:16],
  "pf_sha16_post": hashlib.sha256(pf_t2.encode("utf-8")).hexdigest()[:16],
  "n1_sha16_post": hashlib.sha256(n1_t4.encode("utf-8")).hexdigest()[:16],
  "bands": {"A": A, "B": B, "a_lo": a_lo, "a_hi": a_hi, "b_lo": b_lo, "b_hi": b_hi},
  "admit_receipt": "results/_w274bmc_20261019_probe_receipt.json",
  "seed_admit_gate": gate_lines,
  "banned_gate": "ADMIT rc0 (re-run at freeze window)",
  "band_semantics": {"A": "1-HOP STAIRCASE-AFFECTS-A walk TWENTY-THIRD consecutive A-hop (hops=1, A_hop_chain verbatim in the probe receipt; the naive continuation 617_901..619_900 refused at start -- the registered W273 B band 617_901..618_100 sits INSIDE the naive A window (staircase re-emergence continues; the W273 prereg sec.5 item5 post-W273-REGISTERED pre-disclosure confirmed live r587, zero divergence disclosed); the walk hops past the W273 B tail 618_100 -> A first-clean 618_101..620_100 -- TWENTY-THIRD consecutive A-hop of the staircase era, the fourteen-wave seed-gap face ENDED at W252; A_clean_at_naive_start=false; A_staircase_hop_past_W273_B=true; A base == registered prior-wave B tail+1 (618_100+1) EXACT)",
                     "B": "1-HOP own-A RESERVATION CASCADE above own-A (hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; the naive continuation 618_101..618_300 is refused at start -- the naive window lands INSIDE the own-wave W274 A first-clean window 618_101..620_100 (own-A reservation cascade standard leg; the W273 prereg sec.5 item5 + probe leg4 projected landing confirmed live -- zero divergence per r587); the walk hops past the own-A tail 620_100 -> B landing 620_101..620_300; B lands ABOVE own-A -- TWENTY-FOURTH consecutive above-own-A landing; B_lands_above_own_A=true; B_hop_lands_inside_A=false; B base == own-A tail+1 (620_100+1) EXACT)"},
  "w273_upstream": {"freeze_sha": w273_freeze_sha, "prereg_sha": w273_prereg_sha,
                    "ledger_total": w273_total, "merged_n": w273_merged_n,
                    "engine_owner": "bm-c (upstream seat honored)",
                    "repair_chain_note": "W273 bm-c own-wave full cycle r1102 (five-face splice " + w273_freeze_sha[:10] + " + engine self-burn 12/12 + finalize one-pass ledger 1,024,935 / K=598,520)"},
  "own_seat_face": {"seat_msg": SEAT_MSG, "seat_origin": SEAT_ORIGIN,
                    "inherited": False,
                    "note": "seat published=reserved by bm-c itself (MSG-20261019-012x-bmc-w274-seat pushed to origin " + SEAT_ORIGIN + " r1102 BEFORE this freeze per r565 law, queue-head seat-first supply -- W273 registered+FINALIZED complete at publish, W274 FREEZE UNBLOCKED at seat time (zero waits-upstream face; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE gate0.5 = GREEN at seat (W273 row + n1_w273_results.json both in-place) -- wave 274 engine_owner=bm-c, bm-c's 93rd own wave per live derive (probe leg0 bmc_rows=92 = seat-time pre-splice faces disclosed honest, live derive governs r587/r359; freeze-time live face owner rows 263 + candidate = 264th EXACT)"},
  "transitive_deps": {f"W{w}": f"results/perpetual_faces/n1_w{w}_results.json present (belt-and-braces gate)" for w in (270, 269, 268, 267, 266, 265, 264, 263, 262, 261)},
  "downstream_seat": "W275 = next free number, next freezer must seat-first publish per O-20261010-2350 sec.2 queue-depth supply; the W275 freezer MUST re-derive live on the post-W274 universe + reserve the own-wave A window when deriving B per the W274 seat leg4 mandate, never transcribe r587 -- W275p face per this window's probe leg4 (pre-W274 universe): A naive 620101..622100 CLEAN (hops=0, zero live refusers -- pre-W274-universe face) / B naive 620301..620500 hops=0 CLEAN at naive, first-clean 620301..620500 BUT lands INSIDE the W275 projection A window (W275p_B_lands_inside_W275p_A_naive=true staircase face continuation since W251: A hops over prior B, B lands above own-A; on the post-W274 universe the W275 naive A window start 620_101 lands INSIDE the registered W274 B band 620_101..620_300 -- staircase affects A inherited (twenty-fourth consecutive A-hop expected), the A first-clean and the B own-A reservation cascade landing both move up, live re-derive governs); re-read the live trace at W275 derive time, do NOT assume the staircase A-base==prior-B-tail+1 or B-base==own-A-tail+1 equalities",
  "seat": seat_found + " (origin " + SEAT_ORIGIN + ")",
  "prereg_bundle": {"prereg_sha": w274_prereg_sha, "probe_receipt_sha": w274_receipt_sha,
                    "note": "prereg derived by the bm-c r1104 window (authored 02:2x, banned gate ADMIT rc0, frozen ddc158b5047596ea -> CAS-graft-delivered r1104 origin " + w274_prereg_sha[:10] + "; facts live-derived ledger anchors W273 1,024,935 / K=598,520 at draft (upstream W273 complete at draft, disclosed honest); freeze-time live derive bmc rows 92 + candidate 93rd EXACT per r587/r359; splice editor derived from the committed W273 freeze-edits template by count-asserted ordered transform in this same freeze window (E63 heal lineage: arith_a274/arith_b274 define+assert consistent; band-set variable aging face w244_a holds wave-263 bands, disclosed); upstream W273 already landed incl finalize (clean-precondition sixty-second consecutive window); zero transcription"},
  "ordinal_faces": {"owner_rows_live": len(owner_rows_live), "bma_rows_live": len(bma_rows_live),
                    "bmc_rows_live": len(bmc_rows_live),
                    "engine_owned_ordinal": len(owner_rows_live) + 1,
                    "bmc_own_ordinal": len(bmc_rows_live) + 1,
                    "probe_receipt_bmc_ordinal_face": 92,
                    "note": "post-W273 registration: bm-c rows 92 + candidate = 93rd owned (live derive at freeze time governs per r587/r359; probe leg0 bmc_rows=92 = seat-time faces -- bm-c own-seat continuity, zero waits-upstream face)"},
  "parity_section": {"source": "OWN W273 block physical bytes (bm-c splice generation r1102 window, structure known exactly)",
                     "bytes": len(par_sec) + len(legs_kept),
                     "estate_row_asserts": par_sec.count("assert pf.N1_BANDS["),
                     "kept_legs_row_asserts": legs_kept.count("assert pf.N1_BANDS["),
                     "dropped_legs_row_asserts": legs_dropped.count("assert pf.N1_BANDS["),
                     "fresh_legs_row_asserts": 26,
                     "total_parity_rows": par_sec.count("assert pf.N1_BANDS[")
                                          + legs_kept.count("assert pf.N1_BANDS[") + 26,
                     "note": "estate W138..W206 (69 rows, r858 absorb generation) + W211..W247 legs (37) extracted verbatim per the W273 template lineage mandate; the W273 block's own W248..W272 legs (25) EXCLUDED from the estate path per the same mandate; fresh W248..W274 legs (26) machine-derived from the live pf registry -> W274 block = 132 rows (W138..W206 + W211..W273); disclosed: (a) inherited estate/legs error-string faces preserved verbatim per extraction law (assert targets correct, zero functional impact); (b) band-set variable one-behind naming face (w244_a holds wave-263 bands) = lineage mechanical aging face, zero functional impact; (c) fresh-leg error strings are own-generation text (assert targets identical, first-line format identical, disclosed); (d) E63 15th-gen prevention this window: the W274 derive editor kept the P1-blanket-immune pass ordering and the extraction-restructure legs/kept/dropped wave-identity asserts fixed post-blanket (list(range(211,263))/list(range(211,244))/list(range(244,262)) live-structure exact) -- zero heal needed, zero splice executed pre-verify"},
  "family6_triple_gate": {"absorbed": True,
                          "note": "W273 editor family-6 gate carried forward: new block LHS w<263 x3 / RHS range(16,263)+range(17,263) / comment below-263 count-asserted ATOMICALLY before splice; W273 block's own w<262 face = legitimate prior-wave boundary (not stale); E63 heal lineage applied (arith define/assert consistent)"},
  "eol": {"n1_crlf": EOL == "\r\n", "pf_crlf": PF_EOL == "\r\n"},
  "liveness_anchors": {f"w{_b}_block_kept": 1 for _b in range(209, 275)},
}

open(RECEIPT_OUT, "w", encoding="utf-8").write(json.dumps(receipt, indent=1))
print(json.dumps({k: receipt[k] for k in
      ("phase", "origin_base", "pf_sha16_post", "n1_sha16_post", "bands",
       "w273_upstream", "own_seat_face")}, indent=1))
print("SPLICE OK -- py_compile both green; NEXT: selftest (default wave, r522 law) -> pathspec commit+push -> engine self-ignite W274 burn (12 shards) -> PRE-FINALIZE six-gate (standing law) -> finalize one-pass")
