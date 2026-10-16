# -*- coding: utf-8 -*-
# 2026-10-17 04:4x bm-c r1060 freeze window (upstream W1..W256 ALL LANDED, clean
# precondition -- W256 finalize one-pass bm-c r1058 window closeout 04:0x,
# ledger head 987,535 / K=561,120 machine-read): W257 five-face freeze splice
# editor -- bm-c OWN-SEAT face (seat MSG-20261017-03xx-bmc-w257-seat
# published=reserved by bm-c itself @ origin 27ee6e95a r1058, pre-seat probe
# ADMIT receipt results/_w257bmc_20261017_probe_receipt.json same payload;
# the W257 seat was published AFTER the W256 five-face + finalize landing
# (queue-head supply -- W256 complete at publish, ZERO waits-upstream face;
# bm-c r1058 splice + r1058 finalize one-pass ledger 987,535 / K=561,120)); zero DRAFT marker; per-wave prereg
# PERPETUAL_N1_W257_PREREG.md derived by the bm-c r1059 window (machine-SUB from the frozen W256 template)
# (authored 04:1x, banned_direction_gate ADMIT rc0, committed+pushed same window c7fbc443c).
# Lineage: _w256bmc_freeze_edits.py template (proven live-fire freeze, bm-c
# r1058 splice window; engine self-burn 12/12 + finalize one-pass verified r1058)
# + r787 preflight law + r609 origin-verbatim base + r761 programmatic quote
# wrapping + r909 physical-byte anchors + r838 per-file EOL detection
# + family #6 LHS/RHS/comment ATOMIC TRIPLE (the new block's w<257>/
# range(16,257)/range(17,257)/below-257 quadruple is count-asserted
# atomically; the W256 block's own w<256> face is legitimate prior-wave
# boundary, not stale) + E63 heal lineage (arith_a257/arith_b257
# define+assert consistent; band-set variable aging face continues:
# w244_a holds wave-257 bands, disclosed).
# NEW FACE vs the W256 editor (honest disclosure, frozen W257 prereg sec.3
# mandate): BOTH bands take 1-HOP WALK faces -- staircase + cascade
# CONTINUE -- A = STAIRCASE-AFFECTS-A 1-hop walk, SIXTH consecutive A-hop
# (the naive continuation 580_501..582_500 is REFUSED at its own start --
# the registered W256 B band 580_501..580_700 sits INSIDE the naive A
# window = staircase re-emergence continues to affect A; the W256 prereg
# sec.5 item5 A-CLEAN-at-naive projection was a pre-W256-universe face,
# superseded live per r587, divergence disclosed; the walk hops past the
# W256 B tail 580_700 -> A first-clean 580_701..582_700, hops=1; A base ==
# registered prior-wave B tail+1 (580_700+1) floor relation EXACT this
# window; A_clean_at_naive_start=false; A_staircase_hop_past_W256_B=true);
# B = 1-HOP own-A RESERVATION CASCADE above own-A, SEVENTH consecutive
# above-own-A (the naive continuation 580_701..580_900 is REFUSED at its
# own start -- the naive window lands INSIDE the own-wave A first-clean
# window 580_701..582_700, own-A reservation cascade standard leg; the
# walk hops past the own-A tail 582_700 -> B landing 582_701..582_900,
# hops=1; B lands ABOVE own-A; B base == own-A tail+1 (582_700+1) EXACT;
# B_naive_refused_at_start=true; B_lands_above_own_A=true;
# B_hop_lands_inside_A=false; hops=1).
# PARITY STRUCTURAL CHOICE (frozen W257 prereg sec.3 mandate, verbatim):
# the parity estate (W138..W206 69-row full-span, r858 absorb generation)
# is extracted from the OWN W256 block physical bytes (structure known
# exactly, extraction self-asserts the 69-row range identity); the W256
# block's own W239..W255 legs (17 rows) do NOT enter the estate path;
# after extraction, fresh W239..W256 legs (18 rows) are added,
# machine-derived from the LIVE pf registry at freeze time -> W257 block
# parity = 115 rows (W138..W206 + W211..W256). Zero assumption zero risk.
# Zero hardcoded upstream band values: ALL W256 facts machine-derived from the
# LIVE pf import at freeze time (the registered W256 row -- bm-c own seat
# honored), cross-checked against the committed ADMIT receipt
# (results/_w257bmc_20261017_probe_receipt.json) which was derived on the
# post-W256-REGISTERED universe with the W257 candidate bands treated as
# reserved refusers (now REGISTERED verbatim -- values identical, disclosed).
# If the LIVE W256 bands differ from the declared face, the continuation
# asserts fail LOUD (fail-closed).
# Own bundle hashes (prereg/probe receipt) derived via pickaxe, never transcribed.
# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.
import json, hashlib, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PF = os.path.join(REPO, "scripts", "perpetual_faces.py")
N1 = os.path.join(REPO, "scripts", "perpetual_faces_n1.py")
RECEIPT_IN = os.path.join(REPO, "results", "_w257bmc_20261017_probe_receipt.json")
RECEIPT_OUT = os.path.join(REPO, "results", "_w257bmc_freeze_receipt.json")
SEAT_MSG = "MSG-20261017-03xx-bmc-w257-seat.md"
SEAT_ORIGIN = "27ee6e95a"
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

# ---------- gate 0.5: W256 five-face landed + W256 finalize product present ----------
# (chain-order precondition; belt-and-braces transitive window W244..W253 checked
# here + enforced by the block's cumulative-deps assert range(17, 257) at selftest time)
W256 = dict(pf_mod.N1_BANDS.get(256) or {})
assert W256.get("engine_owner") == "bm-c", \
    f"W256 row not landed as declared (bm-c seat owner expected): {W256} -- five-face freeze missing;" \
    " if an unexpected face exists the freeze window MUST re-derive this editor honestly"
w256_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w256_results.json")
assert os.path.exists(w256_out_path), "W256 finalize product missing (n1_w256_results.json) -- chain dep not met"
for _w in (253, 252, 251, 250, 249, 248, 247, 246, 245, 244):
    assert os.path.exists(os.path.join(REPO, "results", "perpetual_faces", f"n1_w{_w}_results.json")), \
        f"W{_w} finalize product missing (transitive chain dep) -- abort"
w256_out = json.load(open(w256_out_path, encoding="utf-8"))
w256_led = (w256_out.get("science_gates") or {}).get("ledger") or {}
w256_total = w256_led.get("total")
w256_merged_n = None
try:
    w256_merged_n = w256_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
assert w256_total == 987_535 and w256_merged_n == 561_120, \
    f"W256 finalize anchors drift at freeze time: total={w256_total} merged={w256_merged_n} (expect 987,535 / 561,120)"
# freeze shas machine-derived (pickaxe), never transcribed
r = git("log", "--format=%H", "-S", '256: {"a"', "--", "scripts/perpetual_faces.py")
w256_freeze_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W256_PREREG.md")
w256_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W257_PREREG.md")
w257_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
assert os.path.exists(os.path.join(REPO, "research", "PERPETUAL_N1_W257_PREREG.md")), \
    "W257 per-wave prereg missing on disk -- chain face incomplete, abort (r1035 derive landed pre-freeze expected)"
with open(os.path.join(REPO, "research", "PERPETUAL_N1_W257_PREREG.md"), encoding="utf-8") as _fh:
    _pre_head = _fh.read(2000)
assert "DRAFT-NOT-FROZEN" not in _pre_head, "W257 prereg still DRAFT -- abort (freeze commit pending face)"
# live ordinal derive (r359 law: gate machine output governs; the pre-seat probe
# receipt leg0 face owner_rows=246 / bmc_rows=76 / bmc_ordinal=77
# = seat-time PRE-W257-splice live faces (post-W256-REGISTERED universe,
# upstream complete -- queue-head supply); live derive at freeze time:
# W256 splice LANDED (finalize adds no registry rows) -> owner rows 246 + candidate = 247th EXACT; bm-c rows 76 +
# candidate = 77th EXACT -- bm-c own-seat continuity face (bm-c published the
# W257 seat itself r1058; queue-head supply -- W256 chain complete at publish, ZERO
# waits-upstream face (bm-c r1058 splice + r1058 finalize))
owner_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner")]
bma_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-a"]
bmc_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
assert len(owner_rows_live) == 246 and len(bma_rows_live) == 129 and len(bmc_rows_live) == 76, \
    f"leg0 ordinal drift at freeze time: owner={len(owner_rows_live)} bma={len(bma_rows_live)} bmc={len(bmc_rows_live)} (expect 246/129/76 PRE-splice post-W256 registration; this candidate = bm-c's 77th own wave per the same live-derive law, r587/r359)"
print(f"gate0.5 OK: W256 landed (freeze {w256_freeze_sha[:10]}, owner=bm-c seat honored (upstream W256), queue-head supply, ZERO waits-upstream face), "
      f"W257+W252..W243 finalize products present "
      f"(W256 ledger head {w256_total}, merged n={w256_merged_n}); owner rows {len(owner_rows_live)} + candidate, "
      f"bm-c rows {len(bmc_rows_live)} + candidate (77th own wave per live derive; "
      f"probe receipt leg0 bmc_ordinal=77 = seat-time pre-splice faces disclosed honest)")

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
assert (a_lo, a_hi) == (580_701, 582_700) and (b_lo, b_hi) == (582_701, 582_900), \
    f"W257 band drift vs probe ADMIT: {(a_lo, a_hi)} {(b_lo, b_hi)}"
w256_b_tail = W256["b_exit"][1]      # registered W256 row b_exit hi (pf import, live)
w256_a_tail = W256["a"][1]           # registered W256 row A hi (pf import, live)
# W257 FACE (probe receipt leg1 relation_asserts):
# A takes the 1-HOP STAIRCASE-AFFECTS-A walk face, SIXTH consecutive A-hop
# (naive continuation REFUSED at its own start -- A_clean_at_naive_start=false,
# A_staircase_hop_past_W256_B=true, hops=1, A_hop_chain verbatim in the
# receipt; the registered W256 B band sits INSIDE the naive A window =
# staircase re-emergence continues to affect A; the W256 prereg sec.5 item5
# A-CLEAN-at-naive projection superseded live r587, divergence disclosed;
# the walk hops past the W256 B tail -> A first-clean; A base == registered
# prior-wave B tail+1 EXACT -- SIXTH consecutive A-hop of the staircase
# era, the fourteen-wave seed-gap face ENDED at W252); B takes the 1-HOP
# own-A RESERVATION CASCADE face (naive continuation REFUSED at its own
# start -- B_naive_refused_at_start=true, hops=1, B_hop_chain verbatim in
# the receipt; the naive window lands INSIDE the own-wave A first-clean
# window, own-A reservation cascade standard leg; the walk hops past the
# own-A tail -> B lands ABOVE own-A, B_lands_above_own_A=true -- B base ==
# own-A tail+1 EXACT, SEVENTH consecutive above-own-A landing);
# machine-derived from the LIVE registered row, never transcribed.
assert w256_b_tail + 1 == a_lo, "A staircase-hop landing base relation (A base == registered prior-wave B tail+1 EXACT -- the 1-hop walk past the registered W256 B band; sixth consecutive A-hop of the staircase era; A_staircase_hop_past_W256_B=true)"
assert a_lo >= w256_b_tail + 1, "A staircase landing floor relation (A base >= registered prior-wave B tail+1; the fourteen-wave seed-gap face ENDED at W252 -- sixth consecutive A-hop of the staircase era, A base == prior-B tail+1 EXACT this window per the prereg floor-relation mandate)"
assert b_lo == a_hi + 1, "B base == own-A tail+1 EXACT (the 1-hop own-A reservation cascade lands ABOVE own-A -- seventh consecutive above-own-A; B_hop_lands_inside_A=false; B_lands_above_own_A=true)"
assert W256["b_exit"][0] == W256["a"][1] + 1, \
    "upstream W256 row above-own-A staircase relation broken (registered W256 B base == own W256 A tail+1 EXACT -- the above-own-A face inherited from the W256 freeze)"
assert leg1.get("hops_A") == 1, "A hop-count drift vs probe receipt leg1 (A band naive hops=1, staircase-affects-A walk face)"
assert leg1.get("hops_B") == 1, "B hop-count drift vs probe receipt leg1 (B band hops=1, own-A reservation walk face above own-A)"
assert len(leg1.get("A_hop_chain") or []) == 1 and (
    leg1.get("A_clean_at_naive_start") is False
    or (leg1.get("relation_asserts") or {}).get("A_clean_at_naive_start") is False
), \
    "A hop-chain face drift (hops=1 staircase-affects-A walk -- naive continuation REFUSED at own start, the registered W256 B band sits inside the naive A window; A_hop_chain verbatim in the probe receipt)"
assert len(leg1.get("B_hop_chain") or []) == 1 and leg1.get("B_naive_refused_at_start") is True, \
    "B hop-chain face drift (hops=1 own-A reservation walk -- naive continuation lands INSIDE the own-wave A window, B_naive_refused_at_start=true; B_hop_chain verbatim in the probe receipt)"
assert leg1.get("B_hop_lands_inside_A") is False, "B lands-inside-own-A drift vs probe receipt leg1 (B_hop_lands_inside_A must be False)"
assert leg1.get("B_lands_above_own_A") is True and leg1.get("B_naive") == [w256_b_tail + 1, w256_b_tail + 200], "B lands-above-own-A + naive-window drift vs probe receipt leg1 (B_lands_above_own_A=true; B base == own-A tail+1 EXACT; naive window == prior-B tail+1..+200)"
ra = leg1.get("relation_asserts") or {}
assert ra.get("A_clean_at_naive_start") is False and ra.get("A_staircase_hop_past_W256_B") \
    and ra.get("A_base_ge_priorB_tail_plus1") \
    and ra.get("B_clean_at_naive_start") is False and ra.get("B_base_above_W256_tail") \
    and ra.get("AB_mutual_exclusion") and ra.get("B_hop_lands_inside_A") is False \
    and ra.get("B_lands_above_own_A") and ra.get("W254_W255_W256_bands_respected_A") and ra.get("W254_W255_W256_bands_respected_B"), \
    f"probe receipt leg1 relation_asserts face drift: {ra}"
assert [w256_a_tail + 1, w256_a_tail + 2_000] == leg1["ARITH_A"], \
    f"A naive-arithmetic window start drift vs probe receipt leg1 ARITH_A: {[w256_a_tail + 1, w256_a_tail + 2_000]} != {leg1['ARITH_A']}"
assert [w256_b_tail + 1, w256_b_tail + 200] == leg1["ARITH_B"], \
    f"B naive continuation drift vs probe receipt leg1 ARITH_B: {[w256_b_tail + 1, w256_b_tail + 200]} != {leg1['ARITH_B']}"

# own bundle shas via pickaxe (self-referencing commit facts, zero transcription)
r = git("log", "--diff-filter=A", "--format=%H", "--", "results/_w257bmc_20261017_probe_receipt.json")
w257_receipt_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
# seat MSG honest location (inbox or processed; S7 archive law)
seat_found = None
for _p in ("fleet/inbox", "fleet/inbox/processed"):
    if os.path.exists(os.path.join(REPO, _p, SEAT_MSG)):
        seat_found = _p + "/" + SEAT_MSG
        break
assert seat_found, f"W257 seat MSG missing from both inbox paths: {SEAT_MSG}"

# ---------- re-run discipline gates at freeze window (banned + seed_admit) ----------
g = subprocess.run([PY, os.path.join(REPO, "Tools", "banned_direction_gate.py"),
                    "--prereg", "research/PERPETUAL_N1_W257_PREREG.md"],
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

def fmt(n):  # 580701 -> "580_701"
    return f"{n // 1000}_{n % 1000:03d}"

# ---------- extract parity estate + kept legs (physical bytes, never re-typed) ----------
# STRUCTURAL CHOICE (frozen W257 prereg sec.3 mandate): extract the 69-row
# estate (W138..W206 full-span 69 rows, r858 absorb generation) AND the
# W211..W238 legs (28) from the OWN W256 block physical bytes (bm-c r1058
# splice generation, committed -- structure known exactly); the W256
# block's own W239..W255 legs (17) are EXCLUDED from the estate path per the
# prereg mandate; the W257 block appends fresh W239..W256 legs (18,
# machine-derived from the LIVE pf registry at freeze time) -> 115 parity
# rows.
a22 = '    # --- W256 materializer face'
a_t141 = '    # --- T-141 s2 lane face'
w256_start = n1_t.find(a22); t141_pos = n1_t.find(a_t141)
assert w256_start > 0 and t141_pos > w256_start, \
    "W256 materializer block face not found (W256 freeze not landed? header-text drift -> honest re-derive required)"
blk = n1_t[w256_start:t141_pos]
m_first_row = re.search(r"assert pf\.N1_BANDS\[", blk)
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state", blk)
assert m_first_row and m_disj and m_disj.start() > m_first_row.start(), \
    "parity span markers not found in W256 block"
_row_ls = blk.rfind(EOL, 0, m_first_row.start()) + len(EOL)
par_full = blk[_row_ls:m_disj.start()]
m211 = re.search(r" *assert pf\.N1_BANDS\[211\] ==", par_full)
assert m211, "upstream W211 row leg not found inside W256 parity span (estate boundary: W138..W206 full-span 69 rows only, frozen W257 prereg sec.3 mandate)"
par_sec = par_full[:m211.start()]
legs_sec = par_full[m211.start():]
assert par_sec.endswith(EOL), "estate segment must end with EOL"
assert legs_sec.endswith(EOL), "legs segment must end with EOL"
_estate_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", par_sec)
assert par_sec.count("assert pf.N1_BANDS[") == 69 \
    and [int(w) for w in _estate_ws] == list(range(138, 207)), \
    f"estate segment not W138..W206 full-span 69 rows (frozen W257 prereg sec.3 estate-extraction mandate): n={par_sec.count('assert pf.N1_BANDS[')} range={(_estate_ws[:2], _estate_ws[-4:])}"
assert par_full.count("assert pf.N1_BANDS[") == 114, \
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 114 (69 estate + W211..W255 legs 45)"
_legs_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", legs_sec)
assert legs_sec.count("assert pf.N1_BANDS[") == 45 \
    and [int(w) for w in _legs_ws] == list(range(211, 256)), \
    f"legs segment not W211..W255 forty-five legs: n={legs_sec.count('assert pf.N1_BANDS[')} waves={_legs_ws}"
# prereg sec.3 mandate split: keep W211..W238 verbatim (28 legs); the W256
# block's own W239..W255 legs (17) are excluded from the estate path
m239 = re.search(r" *assert pf\.N1_BANDS\[239\] ==", legs_sec)
assert m239, "W239 leg boundary not found inside W257 legs segment (prereg sec.3 split face)"
legs_kept = legs_sec[:m239.start()]
legs_dropped = legs_sec[m239.start():]
assert legs_kept.endswith(EOL) and legs_dropped.endswith(EOL), "split segments must end with EOL"
_kept_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", legs_kept)
assert legs_kept.count("assert pf.N1_BANDS[") == 28 \
    and [int(w) for w in _kept_ws] == list(range(211, 239)), \
    f"kept segment not W211..W238 twenty-eight legs: n={legs_kept.count('assert pf.N1_BANDS[')} waves={_kept_ws}"
_dropped_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", legs_dropped)
assert legs_dropped.count("assert pf.N1_BANDS[") == 17 \
    and [int(w) for w in _dropped_ws] == list(range(239, 256)), \
    f"dropped segment not W239..W255 seventeen legs: n={legs_dropped.count('assert pf.N1_BANDS[')} waves={_dropped_ws}"

# ---------- fresh legs W239..W256 (machine-derived from the LIVE pf registry) ----------
fresh_leg_lines = []
for _w in range(239, 257):
    _row = dict(pf_mod.N1_BANDS[_w])
    _owner = _row["engine_owner"]
    if _w == 256:
        _msg = '"registered W256 row parity drift (r307; bm-c five-face freeze; own-seat face disclosed)"'
    else:
        _msg = f'"registered W{_w} row parity drift (r307; engine_owner={_owner}; W257 freeze fresh-derive from live registry)"'
    fresh_leg_lines += [
        f'        assert pf.N1_BANDS[{_w}] == {{"a": ({fmt(_row["a"][0])}, {fmt(_row["a"][1])}),',
        f'                                    "b_exit": ({fmt(_row["b_exit"][0])}, {fmt(_row["b_exit"][1])}),',
        f'                                    "engine_owner": "{_owner}"}}, \\',
        f'            {_msg}',
    ]
fresh_legs = EOL.join(fresh_leg_lines)
assert fresh_leg_lines[0].startswith('        assert pf.N1_BANDS[239] == {"a": (')

# ---------- indent extraction (physical, not assumed; per-file EOL) ----------
def line_indent(t, needle, eol):
    i = t.find(needle)
    assert i >= 0, f"indent needle not found: {needle[:40]}"
    ls = t.rfind(eol, 0, i) + len(eol)
    line = t[ls:t.find(eol, ls)]
    return line[:len(line) - len(line.lstrip(" "))]

CFG_I  = line_indent(n1_t, '256: {"batch"', EOL)
PRE_KEY_I = line_indent(n1_t, '"prereg": ("research/PERPETUAL_N1_W256_PREREG.md', EOL)
PRE_I  = line_indent(n1_t, '"pre-run; design = frozen v1 null calibration verbatim, "', EOL)
_c256 = n1_t.find('256: {"batch"')
assert _c256 > 0, "W256 cfg entry not found (W256 freeze not landed?)"
_mpos = n1_t.find('"a_seed_base"', _c256)
assert _mpos > 0 and n1_t.find('"shard_subdir"', _c256) > _mpos, "W256 cfg a_seed_base line not found"
MEM_I  = line_indent(n1_t, '"a_seed_base": ' + str(W256["a"][0]), EOL) \
    if n1_t.find('"a_seed_base": ' + str(W256["a"][0]), _c256) > 0 \
    else line_indent(n1_t, '"a_seed_base": ' + fmt(W256["a"][0]), EOL)
ROW_I  = line_indent(pf_t,  '256: {"a"', PF_EOL)

# ---------- W256 row owner line (physical bytes; comment text is own generation) ----------
w256_row_start = pf_t.find('    256: {"a"')
assert w256_row_start > 0, "W256 row literal not found in pf source"
_own_ls = pf_t.find(PF_EOL, w256_row_start) + len(PF_EOL)
_own_le = pf_t.find(PF_EOL, _own_ls)
w256_own_line = pf_t[_own_ls:_own_le]
assert '"engine_owner": "bm-c"' in w256_own_line, \
    f"W256 owner line unexpected bytes: {w256_own_line!r}"
ROWC_I = w256_own_line[:len(w256_own_line) - len(w256_own_line.lstrip(" "))]

# ---------- pf comment + row ----------
pf_comment = PF_EOL.join([
"    # W257 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat",
"    # MSG-20261017-03xx-bmc-w257-seat published=reserved by bm-c itself @",
"    # origin " + SEAT_ORIGIN + " (r1058, queue-head supply -- W256 complete -> freeze UNBLOCKED at publish, ZERO waits-upstream face; the W257 seat was published AFTER the W256 five-face + finalize landing (zero waits-upstream face) -- bm-c r1058 freeze + r1058 finalize one-pass ledger 987,535 / K=561,120); prereg + ADMIT probe",
"    # receipt frozen commit " + w257_prereg_sha[:10] + " (prereg research/PERPETUAL_N1_W257_PREREG.md",
"    # bm-c r1059 window machine-SUB derive landed pre-freeze, probe",
"    # results/_w257bmc_20261017_probe_receipt.json @ " + w257_receipt_sha[:10] + ");",
"    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10",
"    # ~23:1x; deletion-set EMPTY; delivery window = chain-order",
"    # splice AFTER the bm-c W256 five-face (freeze " + w256_freeze_sha[:10] + ") + W256",
"    # finalize product landed (n1_w256_results.json present, ledger",
"    # head " + str(w256_total) + " machine-read at freeze time); zero --no-verify;",
"    # the W257 seat MSG sits in " + seat_found + " at freeze",
"    # time, honest archived per S7 law);",
"    # band gate ADMIT results/_w257bmc_20261017_probe_receipt.json: A = 1-HOP",
"    # STAIRCASE-AFFECTS-A walk SIXTH consecutive A-hop (the naive continuation " + fmt(w256_a_tail + 1) + ".." + fmt(w256_a_tail + 2_000) + " is REFUSED",
"    # at naive start -- the registered W256 B band sits INSIDE the naive A window;",
"    # the walk hops past the W256 B tail -> A first-clean, hops=1 -- FIFTH",
"    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face",
"    # ENDED at W256;",
"    # A base == registered prior-wave B tail+1 (" + fmt(w256_b_tail) + "+1) machine-checkable; A_clean_at_naive_start=false;",
"    # A_staircase_hop_past_W256_B=true)",
"    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation",
"    # " + fmt(w256_b_tail + 1) + ".." + fmt(w256_b_tail + 200) + " lands INSIDE the own-wave A first-clean window --",
"    # own-A reservation cascade standard leg; hops=1,",
"    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A",
"    # tail -> B lands ABOVE own-A -- SEVENTH consecutive above-own-A;",
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
"    # W258+ projection (gate-derived pre-seat probe leg4, pre-W257",
"    # universe): A naive first-clean " + rec["legs"]["leg4"]["W258p_A_naive"] + " hops=" + str(rec["legs"]["leg4"]["hops_A"]) + " (this window's gate: CLEAN, zero live",
"    # seed refusers) / B naive " + rec["legs"]["leg4"]["W258p_B_naive"] + " hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " CLEAN at naive -- first-clean " + rec["legs"]["leg4"]["W258p_B_first_clean"] + " BUT lands INSIDE the projection A window,",
"    # (W258p_B_lands_inside_W258p_A_naive=true -- staircase re-emergence face: the W258 walk MUST hop past own-A reservation);",
"    # the W258 freezer MUST",
"    # re-derive on the post-W257 universe AND reserve the own-wave A window",
"    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1",
"    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.",
])
pf_row = (f'{ROW_I}257: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), '
          f'"b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'
          + PF_EOL + f'{ROWC_I}"engine_owner": "bm-c"}},' + PF_EOL)
# belt-and-braces: display form must equal the canonical W-family text
assert pf_row.split(PF_EOL)[0].strip() == \
    f'257: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), "b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'

old_pf = must(pf_t, (w256_own_line + PF_EOL + '}'
                     + PF_EOL + '# v1 + ext(wave-1) in-use bands'), 1, "pf_close")
new_pf = (w256_own_line + PF_EOL
          + pf_comment + PF_EOL + pf_row
          + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands')
pf_t2 = pf_t.replace(old_pf, new_pf, 1)

# ---------- n1 cfg entry (programmatic quote wrapping, r761 law) ----------
fin_face = (f"W1..W256 finalize ALL LANDED (W256 finalize product present at splice, "
            f"net chain head {w256_total} machine-read, merged pool K={w256_merged_n} "
            f"machine-read) -- ZERO in-flight upstream seats at splice time, clean precondition "
            f"(forty-fifth consecutive fully-clean freeze window); downstream W258 seat NOT YET "
            f"PUBLISHED at this freeze window (the next freezer must seat-first publish per "
            f"O-20261010-2350 sec.2 queue-depth supply; the W258 freezer MUST re-derive live on "
            f"the post-W257 universe + reserve the own-wave A window when deriving B per the "
            f"W257 seat leg4 mandate, never transcribe r587)")
cfg_lines = [
 f'{CFG_I}257: {{"batch": "PERPETUAL-N1-W257",',
 f'{PRE_KEY_I}"prereg": ("research/PERPETUAL_N1_W257_PREREG.md (wave-level frozen "',
]
PRE = [
 "pre-run; design = frozen v1 null calibration verbatim, ",
 "new seed bands only; TWO HUNDRED AND FIFTY-SEVENTH ENGINE-OWNED WAVE ",
 f"BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate), ",
 "own-series continuation per O-20260101-2355 sec.2 (first-free-",
 "number law after the REGISTERED W256 row five-face freeze (bm-c own seat executed at the bm-c r1058 splice window; engine self-burn 12/12; finalize one-pass bm-c r1058 closeout, ledger 987,535 / K=561,120 machine-read), ",
 f"{w256_freeze_sha[:10]} (prereg {w256_prereg_sha[:10]}), SINGLE STATE zero seat gap W2..W256 all ",
 "registered; " + fin_face + "; ",
 "seat published=reserved ",
 "MSG-20261017-03xx-bmc-w257-seat PUSHED to origin " + SEAT_ORIGIN + " ",
 "BEFORE this freeze per r565 early-visibility law (payload = ",
 "seat MSG + pre-seat probe script + probe receipt; per-wave prereg ",
 "bm-c r1059 window machine-SUB derive landed pre-freeze -- bm-c own-seat ",
 "continuity, ",
 f"prereg {w257_prereg_sha[:10]} @ receipt {w257_receipt_sha[:10]}) -- this freeze splice editor derived from the committed W256 editor template in this same freeze window; ",
 "deletion-set EMPTY; delivery window = chain-order splice ",
 "after the W256 five-face + W256 finalize product landed ",
 "(executed in the bm-c loop freeze window ",
 "under the CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED ",
 "2026-10-10 ~23:1x); zero merge at freeze delivery, zero ",
 "--no-verify; single-window derive -- r812 merged the gate ",
 "legs INTO the pre-seat probe; parity N/A honest), ",
 "engine_owner=bm-c (bm-c OWN-SEAT face -- bm-c's SEVENTY-SEVENTH owned claim per machine-derive (engine_owner==bm-c rows ",
 f"{len(bmc_rows_live)} + candidate; probe receipt leg0 bmc_ordinal=77 = seat-time pre-splice ",
 "live faces disclosed honest, live derive governs ",
 "r587/r359 -- attempt-continuity face: the superseded W245-bmc seat claim (quarantined 20261015T0924) left the 67 live bm-c rows intact), own-seat continuity)), ",
"wave 257: ",
 "A = 1-HOP STAIRCASE-AFFECTS-A walk SIXTH consecutive A-hop (the naive continuation ",
 f"{fmt(w256_a_tail + 1)}..{fmt(w256_a_tail + 2_000)} is REFUSED at its own start ",
 "-- hops=1, A_hop_chain verbatim in the probe receipt, A_clean_at_naive_start=false; ",
 "the registered W256 B band sits INSIDE the naive A window = staircase re-emergence continues to affect A; ",
 "the W256 prereg sec.5 item5 A-CLEAN-at-naive projection superseded live r587, divergence disclosed; the walk hops past the W256 B tail -> ",
 "A first-clean; A base == registered prior-wave B tail+1 (",
 f"{fmt(w256_b_tail)}+1) machine-checkable; SIXTH consecutive A-hop of the staircase era, ",
 "the fourteen-wave seed-gap face ENDED at W252; non-rotational r587 forward-monotone walk) ",
 "+ B = 1-HOP own-A RESERVATION CASCADE above own-A ",
 "(the naive continuation ",
 f"{fmt(w256_b_tail + 1)}..{fmt(w256_b_tail + 200)} is REFUSED at its own start ",
 "-- hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; the ",
 f"naive window lands INSIDE the own-wave A first-clean window (own-A reservation cascade standard leg); the walk hops past the own-wave A tail -> B lands ABOVE the ",
 f"own-A window {fmt(a_lo)}..{fmt(a_hi)} at tail+1 EXACT; SEVENTH consecutive above-own-A ",
 "landing; B base == own-A tail+1 (",
 f"{fmt(a_hi)}+1) machine-checkable; cross-window convergence with the W256 prereg sec.5 item5 + W256 probe leg4 + seat leg4 succession projection ",
 "notes -- all MANDATORY notes honored (post-W256 universe ",
 "re-derive + live-trace re-read, no staircase-equality assumption); ADMIT receipt ",
 "results/_w257bmc_20261017_probe_receipt.json + ",
 "seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a ",
 "ADMIT convention); W258+ projection per this window gate: ",
 f"A naive first-clean {rec['legs']['leg4']['W258p_A_naive']} CLEAN (hops=0, zero live seed refusers) / B naive ",
 f"{rec['legs']['leg4']['W258p_B_naive']} hops={rec['legs']['leg4']['hops_B']} CLEAN at naive -- first-clean {rec['legs']['leg4']['W258p_B_first_clean']} BUT lands INSIDE the W258 projection A window (W258p_B_lands_inside_W258p_A_naive=true staircase re-emergence face; seed-gap face ",
 "inherited); W258 freezer MUST re-derive on the post-W257 universe AND ",
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
 f'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W257 A: {fmt(a_lo)}..{fmt(a_hi)} (1-HOP STAIRCASE-AFFECTS-A walk SIXTH consecutive A-hop; naive {fmt(w256_a_tail + 1)}..{fmt(w256_a_tail + 2_000)} REFUSED at start -- hops=1, A_hop_chain verbatim in the probe receipt, A_clean_at_naive_start=false; registered W256 B band inside the naive A window; sixth consecutive A-hop of the staircase era -- seed-gap face ENDED at W252; A base == registered prior-wave B tail+1)',
 f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W257 B: {fmt(b_lo)}..{fmt(b_hi)} (1-HOP own-A RESERVATION CASCADE above own-A; naive {fmt(w256_b_tail + 1)}..{fmt(w256_b_tail + 200)} REFUSED at start -- hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; naive window lands inside the own-wave A first-clean window -> own-A reservation cascade; B lands ABOVE own-A at tail+1 EXACT -- seventh consecutive above-own-A; B base == own-A tail+1)',
 f'{MEM_I}"shard_subdir": "n1_w257", "out_name": "n1_w257_results.json",',
 f'{MEM_I}"engine_owner": "bm-c"}},',
]

cfg_block = EOL.join(cfg_lines)
old_cfg = must(n1_t, ('                       }' + EOL
                      + 'PREREG = WAVE_CONFIGS[2]["prereg"]'), 1, "n1_cfg_close")
new_cfg = (cfg_block + EOL
           + '                       }' + EOL
           + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
assert new_cfg.count('257: {"batch": "PERPETUAL-N1-W257"') == 1
n1_t2 = n1_t.replace(old_cfg, new_cfg, 1)

# ---------- n1 materializer block ----------
hdr = [
 "    # --- W257 materializer face (bm-c loop five-face freeze splice --",
 "    #     OWN-SEAT face under CEO fill-order standing 2026-10-08 ~23:5x",
 "    #     + RE-ISSUE 2026-10-10 ~23:1x + O-20260909-2334 local-full-use",
 "    #     + O-20260924-1730 claim-and-start same-round law):",
 "    #     bm-c's SEVENTY-SEVENTH owned per machine-derive (engine_owner==bm-c",
 f"    #     rows {len(bmc_rows_live)} + candidate; own-seat face: seat published=reserved by bm-c itself",
 "    #     (r1058 MSG-20261017-03xx-bmc-w257-seat @ origin " + SEAT_ORIGIN + "; probe leg0",
 "    #     bmc_ordinal=77 = seat-time pre-splice faces;",
 "    #     live derive at freeze governs);",
 "    #     wave 257 = first free number after the",
 "    #     REGISTERED W256 row (five-face freeze " + w256_freeze_sha[:10] + "; bm-c own seat executed at",
 "    #     the bm-c r1058 splice window; engine",
 "    #     self-burn 12/12 + finalize one-pass bm-c r1058 closeout ledger 987,535 / K=561,120",
 "    #     -- SINGLE STATE zero seat gap (W2..W256 all registered). Seat",
 "    #     published=reserved MSG-20261017-03xx-bmc-w257-seat pushed",
 "    #     to origin " + SEAT_ORIGIN + " BEFORE this freeze, r565 law (payload =",
 "    #     seat MSG + pre-seat probe script + probe receipt; per-wave prereg",
 f"    #     bm-c r1059 window derive landed pre-freeze commit {w257_prereg_sha[:10]}; this freeze splice editor",
 "    #     derived from the committed W256 editor template in this same freeze",
 "    #     window (E63 heal lineage: arith_a257/arith_b257 define+assert consistent;",
 "    #     band-set variable aging face w244_a holds wave-257 bands, disclosed);",
 "    #     deletion-set EMPTY; delivery window",
 "    #     = chain-order splice after the W256 five-face + W256 finalize",
 "    #     product landed; zero --no-verify; the W257 seat MSG sits in",
 "    #     " + seat_found + " at freeze time, honest archived",
 "    #     per S7 law).",
 "    #     TWO HUNDRED AND FIFTY-SEVENTH engine wave BY",
 f"    #     MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate; gate",
 "    #     leg0 machine output governs per r359 law).",
 f"    #     {fin_face}; the finalize merge loop",
 "    #     still derives the wave set from registry keys at run",
 "    #     time, FAIL-CLOSED r307 always on. ADMIT receipt",
 "    #     results/_w257bmc_20261017_probe_receipt.json;",
 "    #     seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a",
 f"    #     ADMIT convention upgrade): {gate_lines[0]}; {gate_lines[1]};",
 "    #     banned gate ADMIT 0 (re-run at freeze window);",
 "    #     not a re-pick (R257: W257 bands were never assigned).",
"    #     PARITY STRUCTURAL CHOICE (frozen W257 prereg sec.3 mandate):",
 "    #     estate 69 rows (W138..W206 full-span, r858 absorb generation) +",
 "    #     W211..W238 legs (28) extracted verbatim from the OWN W256 block",
 "    #     physical bytes; the W256 block's own W239..W255 legs (17) are",
 "    #     EXCLUDED from the estate path per the prereg mandate; fresh",
 "    #     W239..W256 legs (18) added, machine-derived from the live pf",
 "    #     registry at freeze time -> 115 parity rows (W138..W206+W211..W256).",
 "    _set_wave(257)",
 "    try:",
 '        assert WAVE_CONFIGS[256]["a_seed_base"] == pf.N1_BANDS[256]["a"][0], \\',
 '            "W257 upstream W256 mirror drift (a)"',
 "        assert WAVE_CONFIGS[256][\"b_exit_seed_base\"] == \\",
 '            pf.N1_BANDS[256]["b_exit"][0], "W257 upstream W256 mirror drift (b)"',
 "        assert WAVE_CONFIGS[256].get(\"engine_owner\") == \\",
 '            pf.N1_BANDS[256].get("engine_owner") == "bm-c", \\',
 '            "W257 upstream W256 engine_owner mirror drift (law-mirror parity; bm-c upstream seat face (own-seat upstream))"',
 "        w244_a = {A_SEED_BASE + j for j in range(A_N)}",
 "        w244_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
 '        assert not (w244_a & w244_b), "W257 A/B band overlap"',
 "        assert not (w244_a & reg_ints) and not (w244_b & reg_ints), \\",
 '            "W257 hits SEED_REGISTRY"',
 '        for nm, band in (("A", w244_a), ("B", w244_b)):',
 '            assert not (band & v1_a) and not (band & v1_b), f"W257 {nm} hits v1"',
 '            assert not (band & w1_a) and not (band & w1_b), f"W257 {nm} hits W1"',
 '            assert not (band & probes), f"W257 {nm} hits probe seeds"',
]
tail = [
 "        # prior-wave disjointness W2..W256 (single state: all",
 "        # registered, dynamic registry derive, r511 law)",
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 257):",
 '            assert not (w244_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
 "                                 for j in range(A_N)}), f\"W257 A hits W{wprev}\"",
 '            assert not (w244_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
 "                                  for j in range(B_N)}), f\"W257 B hits W{wprev}\"",
 "        n3r1_used245 = set(range(70_000, 70_006))",
 "        assert not (w244_a & n3r1_used245) and not (w244_b & n3r1_used245), \\",
 '            "W257 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
 "        assert not (w244_a & lfc_actual12) and not (w244_b & lfc_actual12), \\",
 '            "W257 bands must clear the lfc actual draw range"',
 "        assert not (w244_a & options_actual12) and \\",
 "            not (w244_b & options_actual12), \\",
 '            "W257 bands must clear the options_wave2 actual draw range"',
"        # band facts (law sec.4 W257 row): A = 1-HOP STAIRCASE-AFFECTS-A",
"        # walk SIXTH consecutive A-hop (the naive continuation",
f"        # {fmt(w256_a_tail + 1)}..{fmt(w256_a_tail + 2_000)} REFUSED at naive start -- the registered W256 B band",
f"        # {fmt(pf_mod.N1_BANDS[256]['b_exit'][0])}..{fmt(pf_mod.N1_BANDS[256]['b_exit'][1])} sits INSIDE the naive A window (staircase re-emergence",
"        # continues to affect A; the W256 prereg sec.5 item5 A-CLEAN-at-naive projection superseded live r587,",
"        # divergence disclosed); hops=1, A_hop_chain verbatim in the probe receipt,",
"        # A_clean_at_naive_start=false, A_staircase_hop_past_W256_B=true; the walk hops",
"        # past the W256 B tail -> A first-clean; A base ==",
f"        # registered prior-wave B tail+1 ({fmt(w256_b_tail)}+1) machine-checkable; SIXTH consecutive A-hop of the W239",
"        # staircase era -- the fourteen-wave seed-gap face ENDED at W252;",
"        # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation",
f"        # {fmt(w256_b_tail + 1)}..{fmt(w256_b_tail + 200)} REFUSED at naive start -- the naive window lands",
"        # INSIDE the own-wave A first-clean window (own-A reservation cascade standard leg); hops=1,",
"        # B_hop_chain verbatim in the probe receipt; the walk hops past the own-wave A tail",
f"        # -> B lands ABOVE the own-A window {fmt(a_lo)}..{fmt(a_hi)} at tail+1 EXACT -- SEVENTH consecutive",
"        # above-own-A landing;",
"        # B base == own-A tail+1 EXACT",
"        # machine-checkable; B_hop_lands_inside_A=false;",
"        # B_lands_above_own_A=true; cross-window convergence with",
"        # the W256 prereg sec.5 item5 + W256 probe leg4 + seat leg4 succession projection notes -- all",
"        # MANDATORY notes honored (post-W256 universe",
"        # re-derive + live-trace re-read, no staircase-equality assumption);",
f'        assert WAVE_CONFIGS[257]["a_seed_base"] == {a_lo} == {w256_b_tail} + 1, (',
'            "W257 A staircase-affects-A walk SIXTH consecutive A-hop: the naive "',
'            "continuation is REFUSED at its own start (the registered W256 B band sits INSIDE "',
'            "the naive A window -- staircase re-emergence continues; hops=1, A_hop_chain verbatim in the probe receipt, "',
'            "A_clean_at_naive_start=false, A_staircase_hop_past_W256_B=true; the walk hops past "',
'            "the W256 B tail -> A first-clean -- SIXTH consecutive A-hop of the staircase era, "',
'            "the fourteen-wave seed-gap face ENDED at W252; A base == registered prior-wave B "',
'            "tail+1 machine-checkable, floor relation honored)")',
f"        arith_a257 = set(range({a_lo}, {a_hi + 1}))",
"        assert not (arith_a257 & reg_ints), \\",
'            "W257 A window must be CLEAN (first-clean ADMIT face, staircase walk landing)"',
f'        assert WAVE_CONFIGS[257]["b_exit_seed_base"] == {b_lo} == {a_hi} + 1, (',
'            "W257 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "',
f'            "{fmt(w256_b_tail + 1)}..{fmt(w256_b_tail + 200)} is REFUSED at its own start "',
'            "(hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; "',
'            "the naive window lands INSIDE the own-wave A first-clean window -- own-A reservation hops B past the own-wave A tail) -- B base == own-A tail+1 "',
'            "EXACT (B_lands_above_own_A + B_base_above_W256_tail face relation asserts, "',
'            "probe receipt leg1 mirrored exactly; B_hop_lands_inside_A=false)")',
f"        assert {b_lo} > {w256_b_tail}, \\",
'            "W257 B walk base must sit above the prior-wave B tail"',
f"        arith_b257 = set(range({b_lo}, {b_hi + 1}))",
"        assert not (arith_b257 & reg_ints), \\",
'            "W257 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"',
"        assert not (arith_b257 & arith_a257), \\",
'            "W257 A/B same-freeze mutual exclusion (B lands ABOVE own-A at tail+1 EXACT -- seventh consecutive above-own-A; zero overlap)"',
"        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W257-SHARD-0\",",
 '                                          "n1w257-0of12"), "W257 entry identity"',
 '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W257-SHARD-11",',
 '                                           "n1w257-11of12")',
 "        assert SHARD_DIR.endswith(\"n1_w257\") and OUT.endswith(",
 '            "n1_w257_results.json"), "W257 path drift"',
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 257):",
 "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(",
 "                PATHS.results_dir, \"p2cal_ext\",",
 "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\",
 '                f"W257 shard dir collides with W{wprev}"',
 "        # W257 finalize cumulative deps: W17..W256 outputs ALL PRESENT",
 f"        # (landed net chain head {w256_total} machine-read at freeze time)",
 "        # -- ZERO in-flight upstream seats at splice, clean precondition",
 "        # freeze window; the finalize merge loop derives the wave",
 "        # set from registry keys at run time and stays",
 "        # FAIL-CLOSED, r307 two-state law).",
 "        for _depw in range(17, 257):",
 "            assert os.path.exists(os.path.join(",
 "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\",
 '                f"W257 finalize cumulative dep (W{_depw} output) missing"',
 "        # finalize wave-set derivation face (r511 derive law): every",
 "        # registered wave below 257 composes; wave 15 excluded by",
 "        # design; SINGLE STATE (W2..W256 all registered -- no",
 "        # two-state seat disclosure needed at this freeze).",
 "        assert sorted(w for w in WAVE_CONFIGS if w < 257) == \\",
 "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\",
 "            [w for w in range(16, 257)], \\",
 '            "W257 prior-wave set must derive from registry keys (no 15; " \\',
 '            "W2..W256 registered single state)"',
 "        assert os.path.exists(os.path.join(",
 '            PATHS.root, "research", "PERPETUAL_N1_W257_PREREG.md")), \\',
 '            "W257 per-wave prereg missing (materializer requirement)"',
 "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"",
 "    finally:",
 "        _set_wave(2)",
]
block = EOL.join(hdr) + EOL + par_sec + legs_kept + fresh_legs + EOL + EOL.join(tail) + EOL
# family #6 atomic triple gate (carried forward): the new
# block's LHS w<257> / RHS range(16,257)+range(17,257) / comment below-257 MUST move together.
assert block.count("if w < 257)") == 3, f"family-6 triple: w<257 count {block.count('if w < 257)')} != 3"
assert block.count("if w < 256)") == 0, "family-6 triple: stale w<256 leaked into the W257 block"
assert block.count("range(16, 257)") == 1 and block.count("range(17, 257)") == 1, "family-6 triple: RHS ranges wrong"
assert block.count("registered wave below 257 composes") == 1, "family-6 triple: comment face wrong"
old_blk_anchor = must(n1_t2, "    # --- T-141 s2 lane face", 1, "t141_marker")
n1_t3 = n1_t2.replace(old_blk_anchor, block + old_blk_anchor, 1)

# ---------- n1 print line ----------
pr = [
 '          "+ W257 materializer face [same guard set, dep=W17..W256 "',
 f'          "outputs ALL PRESENT (landed net chain head {w256_total} = W256 bm-c finalize one-pass, K={w256_merged_n} merged pool) -- ZERO "',
 '          "in-flight upstream seats at splice, clean precondition, TWO HUNDRED AND FIFTY-SEVENTH "',
 f'          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} "',
 '          "+ candidate) bm-c\'s SEVENTY-SEVENTH owned claim per "',
 '          "machine-derive (engine_owner==bm-c rows 76 + candidate; OWN-SEAT face: seat published by bm-c itself, "',
 '          "probe leg0 bmc_ordinal=77 = seat-time pre-splice faces disclosed honest, "',
 '          "live derive at freeze governs), "',
 '          "A=1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim, A_clean_at_naive_start=false, "',
 '          "registered W256 B band inside the naive A window, SIXTH consecutive A-hop of the staircase era, "',
 '          "the fourteen-wave seed-gap face ENDED at W252) "',
 '          "+ B=1-HOP own-A RESERVATION CASCADE above own-A (hops=1, B_naive_refused_at_start=true, "',
 '          "B_hop_chain verbatim, naive window lands inside the own-wave A window -> own-A reservation cascade, "',
 '          "B base == own-A tail+1 EXACT, B_lands_above_own_A=true, "',
 '          "SEVENTH consecutive above-own-A landing), chain-order splice from the "',
 '          "committed ADMIT receipt + seed_admit_gate rc0 both bands FREE "',
 '          "(O-20261010-1945-bm-a ADMIT convention), "',
 '          "ADMIT receipt "',
 '          "results/_w257bmc_20261017_probe_receipt.json, law sec.4 W257 row, "',
 '          "bm-c loop CEO fill-order RE-ISSUE 23:1x] "',
]

old_pr = must(n1_t3, '          "+ T-141 s2 ', 1, "print_t141")
n1_t4 = n1_t3.replace(old_pr, EOL.join(pr) + EOL + old_pr, 1)

# ---------- post-edit count gates ----------
assert n1_t4.count('"batch": "PERPETUAL-N1-W257"') == 1
assert n1_t4.count("# --- W257 materializer face") == 1     # block header
assert n1_t4.count('"+ W257 materializer face') == 1        # print fragment
assert n1_t4.count('257: {"batch": "PERPETUAL-N1-W257"') == 1
assert pf_t2.count(ROW_I + '257: {"a"') == 1
assert pf_t2.count('"engine_owner": "bm-c"},' + PF_EOL + '}') == 1
assert n1_t4.count('    # --- T-141 s2 lane face') == 1
assert n1_t4.count('"PERPETUAL-N1-W257-SHARD-0"') == 1
# leg count gates: leg W_k lives in blocks W_{k+1}..W257 -> (257 - k) occurrences
for _lw in range(239, 257):
    _first = (f'assert pf.N1_BANDS[{_lw}] == {{"a": '
              f'({fmt(pf_mod.N1_BANDS[_lw]["a"][0])}, {fmt(pf_mod.N1_BANDS[_lw]["a"][1])}),')
    _got = n1_t4.count(_first)
    assert _got == 257 - _lw, \
        f"W{_lw} leg count drift: {_got} != {257 - _lw} (first-line: {_first})"
for _b in range(209, 258):
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
  "machine": "bm-c", "wave": 257,
  "phase": "five-face freeze chain-order splice (bm-c own-seat freeze window, upstream ALL LANDED clean precondition)",
  "origin_base": omain,
  "pf_sha16_pre": hashlib.sha256(pf_b).hexdigest()[:16],
  "n1_sha16_pre": hashlib.sha256(n1_b).hexdigest()[:16],
  "pf_sha16_post": hashlib.sha256(pf_t2.encode("utf-8")).hexdigest()[:16],
  "n1_sha16_post": hashlib.sha256(n1_t4.encode("utf-8")).hexdigest()[:16],
  "bands": {"A": A, "B": B, "a_lo": a_lo, "a_hi": a_hi, "b_lo": b_lo, "b_hi": b_hi},
  "admit_receipt": "results/_w257bmc_20261017_probe_receipt.json",
  "seed_admit_gate": gate_lines,
  "banned_gate": "ADMIT rc0 (re-run at freeze window)",
  "band_semantics": {"A": "1-HOP STAIRCASE-AFFECTS-A walk SIXTH consecutive A-hop (hops=1, A_hop_chain verbatim in the probe receipt; the naive continuation 580_501..582_500 refused at start -- the registered W256 B band 580_501..580_700 sits INSIDE the naive A window (staircase re-emergence continues; the W256 prereg sec.5 item5 A-CLEAN-at-naive projection superseded live r587, divergence disclosed); the walk hops past the W256 B tail 580_700 -> A first-clean 580_701..582_700 -- SIXTH consecutive A-hop of the staircase era, the fourteen-wave seed-gap face ENDED at W252; A_clean_at_naive_start=false; A_staircase_hop_past_W256_B=true; A base == registered prior-wave B tail+1 (580_700+1) EXACT)",
                     "B": "1-HOP own-A RESERVATION CASCADE above own-A (hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; the naive continuation 580_701..580_900 is refused at start -- the naive window lands INSIDE the own-wave W257 A first-clean window 580_701..582_700 (own-A reservation cascade standard leg; the W256 prereg sec.5 item5 + probe leg4 projected landing superseded live -- the A face itself moved, divergence disclosed per r587); the walk hops past the own-A tail 582_700 -> B landing 582_701..582_900; B lands ABOVE own-A -- SEVENTH consecutive above-own-A landing; B_lands_above_own_A=true; B_hop_lands_inside_A=false; B base == own-A tail+1 (582_700+1) EXACT)"},
  "w256_upstream": {"freeze_sha": w256_freeze_sha, "prereg_sha": w256_prereg_sha,
                    "ledger_total": w256_total, "merged_n": w256_merged_n,
                    "engine_owner": "bm-c (upstream seat honored)",
                    "repair_chain_note": "W256 bm-c own-wave closeout r1058 (five-face splice " + w256_freeze_sha[:10] + " + engine self-burn 12/12 + finalize one-pass ledger 987,535 / K=561,120)"},
  "own_seat_face": {"seat_msg": SEAT_MSG, "seat_origin": SEAT_ORIGIN,
                    "inherited": False,
                    "note": "seat published=reserved by bm-c itself (MSG-20261017-03xx-bmc-w257-seat pushed to origin " + SEAT_ORIGIN + " r1058 BEFORE this freeze per r565 law, queue-head supply -- W256 complete -> freeze UNBLOCKED at publish, ZERO waits-upstream face; the W257 seat published post-W256-chain (queue-head supply, freeze-UNBLOCKED; the W256 five-face + finalize landed bm-c r1058 splice + r1058 finalize before publish) -- wave 257 engine_owner=bm-c, bm-c's 77th own wave per live derive (probe leg0 bmc_ordinal=77 = seat-time pre-splice faces disclosed honest, live derive governs r587/r359; freeze-time live face owner rows 246 + candidate = 247th EXACT; attempt-continuity face: the superseded W245-bmc seat claim (quarantined 20261015T0924) left the 67 live bm-c rows intact)"},
  "transitive_deps": {f"W{w}": f"results/perpetual_faces/n1_w{w}_results.json present (belt-and-braces gate)" for w in (253, 252, 251, 250, 249, 248, 247, 246, 245, 244)},
  "downstream_seat": "W258 = next free number, next freezer must seat-first publish per O-20261010-2350 sec.2 queue-depth supply; the W258 freezer MUST re-derive live on the post-W257 universe + reserve the own-wave A window when deriving B per the W257 seat leg4 mandate, never transcribe r587 -- W258p face per this window's probe leg4 (pre-W257 universe): A naive 582701..584700 CLEAN (hops=0, zero live refusers -- pre-W257-universe face) / B naive 582901..583100 hops=0 CLEAN at naive, first-clean 582901..583100 BUT lands INSIDE the W258 projection A window (W258p_B_lands_inside_W258p_A_naive=true staircase face continuation since W251: A hops over prior B, B lands above own-A; on the post-W257 universe the W258 naive A window start 582_701 lands INSIDE the registered W257 B band 582_701..582_900 -- staircase affects A inherited, the A first-clean and the B own-A reservation cascade landing both move up, live re-derive governs); re-read the live trace at W258 derive time, do NOT assume the staircase A-base==prior-B-tail+1 or B-base==own-A-tail+1 equalities",
  "seat": seat_found + " (origin " + SEAT_ORIGIN + ")",
  "prereg_bundle": {"prereg_sha": w257_prereg_sha, "probe_receipt_sha": w257_receipt_sha,
                    "note": "prereg derived by the bm-c r1059 window (authored 04:1x, banned gate ADMIT rc0 re-verified r1059, committed r1059; commit " + w257_prereg_sha[:10] + "; facts live-derived ledger 987,535 / K=561,120; freeze-time live derive bmc rows 76 + candidate 77th EXACT per r587/r359); splice editor derived from the committed W256 editor template by count-asserted ordered transform in this same freeze window (E63 heal lineage: arith_a257/arith_b257 define+assert consistent; band-set variable aging face w244_a holds wave-257 bands, disclosed); upstream W256 already landed (clean-precondition forty-fifth consecutive window); zero transcription"},
  "ordinal_faces": {"owner_rows_live": len(owner_rows_live), "bma_rows_live": len(bma_rows_live),
                    "bmc_rows_live": len(bmc_rows_live),
                    "engine_owned_ordinal": len(owner_rows_live) + 1,
                    "bmc_own_ordinal": len(bmc_rows_live) + 1,
                    "probe_receipt_bmc_ordinal_face": 77,
                    "note": "post-W256 registration: bm-c rows 76 + candidate = 77th owned (live derive at freeze time governs per r587/r359; probe leg0 bmc_ordinal=77 = seat-time faces -- bm-c own-seat continuity, queue-head supply -- W256 complete at publish, ZERO waits-upstream face)"},
  "parity_section": {"source": "OWN W256 block physical bytes (bm-c splice generation r1058 window, structure known exactly)",
                     "bytes": len(par_sec) + len(legs_kept),
                     "estate_row_asserts": par_sec.count("assert pf.N1_BANDS["),
                     "kept_legs_row_asserts": legs_kept.count("assert pf.N1_BANDS["),
                     "dropped_legs_row_asserts": legs_dropped.count("assert pf.N1_BANDS["),
                     "fresh_legs_row_asserts": 18,
                     "total_parity_rows": par_sec.count("assert pf.N1_BANDS[")
                                          + legs_kept.count("assert pf.N1_BANDS[") + 18,
                     "note": "estate W138..W206 (69 rows, r858 absorb generation) + W211..W238 legs (28) extracted verbatim per the frozen W257 prereg sec.3 mandate; the W256 block's own W239..W255 legs (17) EXCLUDED from the estate path per the same mandate; fresh W239..W256 legs (18) machine-derived from the live pf registry -> W257 block = 115 rows (W138..W206 + W211..W256); disclosed: (a) inherited W213 leg error-string face preserved verbatim per extraction law (r912 generation cosmetic slip, assert target [213] correct, zero functional impact); (b) band-set variable one-behind naming face (w244_a holds wave-257 bands) = lineage mechanical aging face, zero functional impact; (c) fresh-leg error strings are own-generation text (assert targets identical, first-line format identical, disclosed); (d) E63 9th-gen prevention this window: the W257 derive editor kept the P1-blanket-immune pass ordering and the extraction-restructure legs/kept/dropped wave-identity asserts fixed post-blanket (list(range(211,256))/list(range(211,239))/list(range(239,256)) live-structure exact) -- zero heal needed, zero splice executed pre-verify"},
  "family6_triple_gate": {"absorbed": True,
                          "note": "W256 editor family-6 gate carried forward: new block LHS w<257 x3 / RHS range(16,257)+range(17,257) / comment below-257 count-asserted ATOMICALLY before splice; W256 block's own w<256 face = legitimate prior-wave boundary (not stale); E63 heal lineage applied (arith define/assert consistent)"},
  "eol": {"n1_crlf": EOL == "\r\n", "pf_crlf": PF_EOL == "\r\n"},
  "liveness_anchors": {f"w{_b}_block_kept": 1 for _b in range(209, 258)},
}

open(RECEIPT_OUT, "w", encoding="utf-8").write(json.dumps(receipt, indent=1))
print(json.dumps({k: receipt[k] for k in
      ("phase", "origin_base", "pf_sha16_post", "n1_sha16_post", "bands",
       "w256_upstream", "own_seat_face")}, indent=1))
print("SPLICE OK -- py_compile both green; NEXT: selftest (default wave, r522 law) -> pathspec commit+push -> engine self-ignite W257 burn (12 shards) -> PRE-FINALIZE six-gate (standing law) -> finalize one-pass")
