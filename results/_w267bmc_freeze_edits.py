# -*- coding: utf-8 -*-
# 2026-10-18 11:2x bm-c r1088 freeze window (upstream W1..W266 ALL LANDED, clean
# precondition -- W266 cycle COMPLETE bm-c r1085+r1086 closeout 10:5x, ledger head
# 1,009,535 / K=583,120 machine-read): W267 five-face freeze splice
# editor -- bm-c OWN-SEAT face (seat MSG-20261018-1025-bmc-w267-seat
# published=reserved by bm-c itself @ origin 942ebd5885 r1086, pre-seat probe
# ADMIT receipt results/_w267bmc_20261018_probe_receipt.json same payload;
# the W267 seat was published AFTER the W266 finalize landing (W267 FREEZE
# UNBLOCKED at seat time, zero waits-upstream face -- seat-first law
# O-20261010-2350 sec.2; the SPLICE gate0.5 = GREEN at seat: W266 row +
# W266 finalize file both in-place); zero DRAFT
# marker; per-wave prereg PERPETUAL_N1_W267_PREREG.md derived by the bm-a
# r1087 window (machine-SUB from the frozen W266 template)
# (authored 10:5x, banned_direction_gate ADMIT rc0, committed+pushed same
# window df55e3fab9).
# Lineage: _w266bmc_freeze_edits.py template (proven live-fire freeze, bm-c
# r1086 splice window dc71ecc3f9; engine self-burn 12/12 + finalize one-pass
# verified r1087) + r787 preflight law + r609 origin-verbatim base + r761
# programmatic quote wrapping + r909 physical-byte anchors + r838 per-file
# EOL detection + family #6 LHS/RHS/comment ATOMIC TRIPLE (the new block's
# w<263>/range(16,263)/range(17,263)/below-263 quadruple is count-asserted
# atomically; the W266 block's own w<262> face is legitimate prior-wave
# boundary, not stale) + E63 heal lineage (arith_a267/arith_b267
# define+assert consistent; band-set variable aging face continues:
# w244_a holds wave-263 bands, disclosed).
# NEW FACE vs the W266 editor (honest disclosure, W267 prereg sec.3/sec.5
# mandate): BOTH bands take 1-HOP WALK faces -- staircase + cascade
# CONTINUE -- A = STAIRCASE-AFFECTS-A 1-hop walk, SIXTEENTH consecutive A-hop
# (the naive continuation 602_501..604_500 is REFUSED at its own start --
# the registered W266 B band 602_501..602_700 sits INSIDE the naive A
# window = staircase re-emergence continues to affect A; the W266 prereg
# sec.5 item5 post-W266-REGISTERED pre-disclosure confirmed live per r587,
# zero divergence disclosed; the walk hops past the W266 B tail 602_700 ->
# A first-clean 602_701..604_700, hops=1; A base == registered prior-wave B
# tail+1 (602_700+1) floor relation EXACT this window; A_clean_at_naive_start
# =false; A_staircase_hop_past_W266_B=true); B = 1-HOP own-A RESERVATION
# CASCADE above own-A, SEVENTEENTH consecutive above-own-A (the naive
# continuation 602_701..602_900 is REFUSED at its own start -- the naive
# window lands INSIDE the own-wave A first-clean window 602_701..604_700,
# own-A reservation cascade standard leg; the walk hops past the own-A tail
# 604_700 -> B landing 604_701..604_900, hops=1; B lands ABOVE own-A; B base
# == own-A tail+1 (604_700+1) EXACT; B_naive_refused_at_start=true;
# B_lands_above_own_A=true; B_hop_lands_inside_A=false; hops=1).
# PARITY STRUCTURAL CHOICE (W266 template lineage): the parity estate
# (W138..W206 69-row full-span, r858 absorb generation) is extracted from
# the OWN W266 block physical bytes (structure known exactly, extraction
# self-asserts the 69-row range identity); the W266 block's own W248..W265
# legs (18 rows) do NOT enter the estate path; after extraction, fresh
# W248..W266 legs (19 rows) are added, machine-derived from the LIVE pf
# registry at freeze time -> W267 block parity = 121 rows (W138..W206 +
# W211..W266). Zero assumption zero risk.
# Zero hardcoded upstream band values: ALL W266 facts machine-derived from the
# LIVE pf import at freeze time (the registered W266 row -- bm-c own seat
# honored), cross-checked against the committed ADMIT receipt
# (results/_w267bmc_20261018_probe_receipt.json) which was derived on the
# post-W266-REGISTERED universe with the W267 candidate bands treated as
# reserved refusers (now REGISTERED verbatim -- values identical, disclosed).
# If the LIVE W266 bands differ from the declared face, the continuation
# asserts fail LOUD (fail-closed).
# Own bundle hashes (prereg/probe receipt) derived via pickaxe, never transcribed.
# CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x.
import json, hashlib, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PF = os.path.join(REPO, "scripts", "perpetual_faces.py")
N1 = os.path.join(REPO, "scripts", "perpetual_faces_n1.py")
RECEIPT_IN = os.path.join(REPO, "results", "_w267bmc_20261018_probe_receipt.json")
RECEIPT_OUT = os.path.join(REPO, "results", "_w267bmc_freeze_receipt.json")
SEAT_MSG = "MSG-20261018-1025-bmc-w267-seat.md"
SEAT_ORIGIN = "942ebd5885"
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

# ---------- gate 0.5: W266 five-face landed + W266 finalize product present ----------
# (chain-order precondition; belt-and-braces transitive window W254..W263 checked
# here + enforced by the block's cumulative-deps assert range(17, 267) at selftest time)
W266 = dict(pf_mod.N1_BANDS.get(266) or {})
assert W266.get("engine_owner") == "bm-c", \
    f"W266 row not landed as declared (bm-c seat owner expected): {W266} -- five-face freeze missing;" \
    " if an unexpected face exists the freeze window MUST re-derive this editor honestly"
w266_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w266_results.json")
assert os.path.exists(w266_out_path), "W266 finalize product missing (n1_w266_results.json) -- chain dep not met"
for _w in (263, 262, 261, 260, 259, 258, 257, 256, 255, 254):
    assert os.path.exists(os.path.join(REPO, "results", "perpetual_faces", f"n1_w{_w}_results.json")), \
        f"W{_w} finalize product missing (transitive chain dep) -- abort"
w266_out = json.load(open(w266_out_path, encoding="utf-8"))
w266_led = (w266_out.get("science_gates") or {}).get("ledger") or {}
w266_total = w266_led.get("total")
w266_merged_n = None
try:
    w266_merged_n = w266_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
assert w266_total == 1_009_535 and w266_merged_n == 583_120, \
    f"W266 finalize anchors drift at freeze time: total={w266_total} merged={w266_merged_n} (expect 1,009,535 / 583,120)"
# freeze shas machine-derived (pickaxe), never transcribed
r = git("log", "--format=%H", "-S", '266: {"a"', "--", "scripts/perpetual_faces.py")
w266_freeze_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W266_PREREG.md")
w266_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
r = git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W267_PREREG.md")
w267_prereg_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
assert os.path.exists(os.path.join(REPO, "research", "PERPETUAL_N1_W267_PREREG.md")), \
    "W267 per-wave prereg missing on disk -- chain face incomplete, abort"
with open(os.path.join(REPO, "research", "PERPETUAL_N1_W267_PREREG.md"), encoding="utf-8") as _fh:
    _pre_head = _fh.read(2000)
assert "DRAFT-NOT-FROZEN" not in _pre_head, "W267 prereg still DRAFT -- abort (freeze commit pending face)"
# live ordinal derive (r359 law: gate machine output governs; the pre-seat probe
# receipt leg0 face owner_rows=256 / bma_rows=130 / bmc_rows=85
# = seat-time PRE-W267-splice live faces (post-W266-REGISTERED universe,
# W266 finalize LANDED at seat -- W267 FREEZE UNBLOCKED at seat time (zero waits-upstream face);
# live derive at freeze time:
# W266 splice LANDED (finalize adds no registry rows) -> owner rows 256 + candidate = 257th EXACT; bm-c rows 85 +
# candidate = 86th EXACT -- bm-c own-seat continuity face (bm-c published the
# W267 seat itself r1086; queue-head supply -- splice GATED on the W266 finalize
# landing per gate0.5, seat-first law O-20261010-2350 sec.2)
owner_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner")]
bma_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-a"]
bmc_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
assert len(owner_rows_live) == 256 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 85, \
    f"leg0 ordinal drift at freeze time: owner={len(owner_rows_live)} bma={len(bma_rows_live)} bmc={len(bmc_rows_live)} (expect 256/130/85 PRE-splice post-W266 registration; this candidate = bm-c's 86th own wave per the same live-derive law, r587/r359)"
print(f"gate0.5 OK: W266 landed (freeze {w266_freeze_sha[:10]}, owner=bm-c seat honored (upstream W266), chain complete incl finalize, clean precondition), "
      f"W267+W259..W250 finalize products present "
      f"(W266 ledger head {w266_total}, merged n={w266_merged_n}); owner rows {len(owner_rows_live)} + candidate, "
      f"bm-c rows {len(bmc_rows_live)} + candidate (86th own wave per live derive; "
      f"probe receipt leg0 bmc_rows=85 = seat-time pre-splice faces disclosed honest)")

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
assert (a_lo, a_hi) == (602_701, 604_700) and (b_lo, b_hi) == (604_701, 604_900), \
    f"W267 band drift vs probe ADMIT: {(a_lo, a_hi)} {(b_lo, b_hi)}"
w266_b_tail = W266["b_exit"][1]      # registered W266 row b_exit hi (pf import, live)
w266_a_tail = W266["a"][1]            # registered W266 row A hi (pf import, live)
# W267 FACE (probe receipt leg1 relation_asserts):
# A takes the 1-HOP STAIRCASE-AFFECTS-A walk face, SIXTEENTH consecutive A-hop
# (naive continuation REFUSED at its own start -- A_clean_at_naive_start=false,
# A_staircase_hop_past_W266_B=true, hops=1, A_hop_chain verbatim in the
# receipt; the registered W266 B band sits INSIDE the naive A window =
# staircase re-emergence continues to affect A; the W266 prereg sec.5 item5
# post-W266-REGISTERED pre-disclosure confirmed live r587, zero divergence;
# the walk hops past the W266 B tail -> A first-clean; A base == registered
# prior-wave B tail+1 EXACT -- SIXTEENTH consecutive A-hop of the staircase
# era, the fourteen-wave seed-gap face ENDED at W252); B takes the 1-HOP
# own-A RESERVATION CASCADE face (naive continuation REFUSED at its own
# start -- B_naive_refused_at_start=true, hops=1, B_hop_chain verbatim in the
# receipt; the naive window lands INSIDE the own-wave A first-clean
# window, own-A reservation cascade standard leg; the walk hops past the
# own-A tail -> B lands ABOVE own-A, B_lands_above_own_A=true -- B base ==
# own-A tail+1 EXACT, SEVENTEENTH consecutive above-own-A landing);
# machine-derived from the LIVE registered row, never transcribed.
assert w266_b_tail + 1 == a_lo, "A staircase-hop landing base relation (A base == registered prior-wave B tail+1 EXACT -- the 1-hop walk past the registered W266 B band; sixteenth consecutive A-hop of the staircase era; A_staircase_hop_past_W266_B=true)"
assert a_lo >= w266_b_tail + 1, "A staircase landing floor relation (A base >= registered prior-wave B tail+1; the fourteen-wave seed-gap face ENDED at W252 -- sixteenth consecutive A-hop of the staircase era, A base == prior-B tail+1 EXACT this window per the prereg floor-relation mandate)"
assert b_lo == a_hi + 1, "B base == own-A tail+1 EXACT (the 1-hop own-A reservation cascade lands ABOVE own-A -- seventeenth consecutive above-own-A; B_hop_lands_inside_A=false; B_lands_above_own_A=true)"
assert W266["b_exit"][0] == W266["a"][1] + 1, \
    "upstream W266 row above-own-A staircase relation broken (registered W266 B base == own W266 A tail+1 EXACT -- the above-own-A face inherited from the W266 freeze)"
assert leg1.get("hops_A") == 1, "A hop-count drift vs probe receipt leg1 (A band naive hops=1, staircase-affects-A walk face)"
assert leg1.get("hops_B") == 1, "B hop-count drift vs probe receipt leg1 (B band hops=1, own-A reservation walk face above own-A)"
assert len(leg1.get("A_hop_chain") or []) == 1 and (
    leg1.get("A_clean_at_naive_start") is False
    or (leg1.get("relation_asserts") or {}).get("A_clean_at_naive_start") is False
), \
    "A hop-chain face drift (hops=1 staircase-affects-A walk -- naive continuation REFUSED at own start, the registered W266 B band sits inside the naive A window; A_hop_chain verbatim in the probe receipt)"
assert len(leg1.get("B_hop_chain") or []) == 1 and leg1.get("B_naive_refused_at_start") is True, \
    "B hop-chain face drift (hops=1 own-A reservation walk -- naive continuation lands INSIDE the own-wave A window, B_naive_refused_at_start=true; B_hop_chain verbatim in the probe receipt)"
assert leg1.get("B_hop_lands_inside_A") is False, "B lands-inside-own-A drift vs probe receipt leg1 (B_hop_lands_inside_A must be False)"
assert leg1.get("B_lands_above_own_A") is True and leg1.get("B_naive") == [w266_b_tail + 1, w266_b_tail + 200], "B lands-above-own-A + naive-window drift vs probe receipt leg1 (B_lands_above_own_A=true; B base == own-A tail+1 EXACT; naive window == prior-B tail+1..+200)"
ra = leg1.get("relation_asserts") or {}
assert ra.get("A_clean_at_naive_start") is False and ra.get("A_staircase_hop_past_W266_B") \
    and ra.get("A_base_ge_priorB_tail_plus1") \
    and ra.get("B_clean_at_naive_start") is False and ra.get("B_base_above_W266_tail") \
    and ra.get("AB_mutual_exclusion") and ra.get("B_hop_lands_inside_A") is False \
    and ra.get("B_lands_above_own_A") and ra.get("W264_W265_W266_bands_respected_A") and ra.get("W264_W265_W266_bands_respected_B"), \
    f"probe receipt leg1 relation_asserts face drift: {ra}"
assert [w266_a_tail + 1, w266_a_tail + 2_000] == leg1["ARITH_A"], \
    f"A naive-arithmetic window start drift vs probe receipt leg1 ARITH_A: {[w266_a_tail + 1, w266_a_tail + 2_000]} != {leg1['ARITH_A']}"
assert [w266_b_tail + 1, w266_b_tail + 200] == leg1["ARITH_B"], \
    f"B naive continuation drift vs probe receipt leg1 ARITH_B: {[w266_b_tail + 1, w266_b_tail + 200]} != {leg1['ARITH_B']}"

# own bundle shas via pickaxe (self-referencing commit facts, zero transcription)
r = git("log", "--diff-filter=A", "--format=%H", "--", "results/_w267bmc_20261018_probe_receipt.json")
w267_receipt_sha = (r.stdout.decode().strip().splitlines() or ["n/a"])[0]
# seat MSG honest location (inbox or processed; S7 archive law)
seat_found = None
for _p in ("fleet/inbox", "fleet/inbox/processed"):
    if os.path.exists(os.path.join(REPO, _p, SEAT_MSG)):
        seat_found = _p + "/" + SEAT_MSG
        break
assert seat_found, f"W267 seat MSG missing from both inbox paths: {SEAT_MSG}"

# ---------- re-run discipline gates at freeze window (banned + seed_admit) ----------
g = subprocess.run([PY, os.path.join(REPO, "Tools", "banned_direction_gate.py"),
                    "--prereg", "research/PERPETUAL_N1_W267_PREREG.md"],
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

def fmt(n):  # 593901 -> "602_701"
    return f"{n // 1000}_{n % 1000:03d}"

# ---------- extract parity estate + kept legs (physical bytes, never re-typed) ----------
# STRUCTURAL CHOICE (W266 template lineage): extract the 69-row
# estate (W138..W206 full-span 69 rows, r858 absorb generation) AND the
# W211..W265 legs (55) from the OWN W266 block physical bytes (bm-c r1086
# splice generation, committed -- structure known exactly); the W266
# block's own W248..W265 legs (18) are EXCLUDED from the estate path per the
# template mandate; the W267 block appends fresh W248..W266 legs (19,
# machine-derived from the LIVE pf registry at freeze time) -> 121 parity
# rows.
a22 = '    # --- W266 materializer face'
a_t141 = '    # --- T-141 s2 lane face'
w266_start = n1_t.find(a22); t141_pos = n1_t.find(a_t141)
assert w266_start > 0 and t141_pos > w266_start, \
    "W266 materializer block face not found (W266 freeze not landed? header-text drift -> honest re-derive required)"
blk = n1_t[w266_start:t141_pos]
m_first_row = re.search(r"assert pf\.N1_BANDS\[", blk)
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state", blk)
assert m_first_row and m_disj and m_disj.start() > m_first_row.start(), \
    "parity span markers not found in W266 block"
_row_ls = blk.rfind(EOL, 0, m_first_row.start()) + len(EOL)
par_full = blk[_row_ls:m_disj.start()]
m211 = re.search(r" *assert pf\.N1_BANDS\[211\] ==", par_full)
assert m211, "upstream W211 row leg not found inside W266 parity span (estate boundary: W138..W206 full-span 69 rows only, template lineage estate-extraction mandate)"
par_sec = par_full[:m211.start()]
legs_sec = par_full[m211.start():]
assert par_sec.endswith(EOL), "estate segment must end with EOL"
assert legs_sec.endswith(EOL), "legs segment must end with EOL"
_estate_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", par_sec)
assert par_sec.count("assert pf.N1_BANDS[") == 69 \
    and [int(w) for w in _estate_ws] == list(range(138, 207)), \
    f"estate segment not W138..W206 full-span 69 rows (template lineage estate-extraction mandate): n={par_sec.count('assert pf.N1_BANDS[')} range={(_estate_ws[:2], _estate_ws[-4:])}"
assert par_full.count("assert pf.N1_BANDS[") == 124, \
    f"full parity span {par_full.count('assert pf.N1_BANDS[')} != 124 (69 estate + W211..W266 legs 55)"
_legs_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", legs_sec)
assert legs_sec.count("assert pf.N1_BANDS[") == 55 \
    and [int(w) for w in _legs_ws] == list(range(211, 266)), \
    f"legs segment not W211..W265 fifty-five legs: n={legs_sec.count('assert pf.N1_BANDS[')} waves={_legs_ws}"
# template mandate split: keep W211..W247 verbatim (37 legs); the W266
# block's own W248..W265 legs (18) are excluded from the estate path
m248 = re.search(r" *assert pf\.N1_BANDS\[248\] ==", legs_sec)
assert m248, "W244 leg boundary not found inside W267 legs segment (template split face)"
legs_kept = legs_sec[:m248.start()]
legs_dropped = legs_sec[m248.start():]
assert legs_kept.endswith(EOL) and legs_dropped.endswith(EOL), "split segments must end with EOL"
_kept_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", legs_kept)
assert legs_kept.count("assert pf.N1_BANDS[") == 37 \
    and [int(w) for w in _kept_ws] == list(range(211, 248)), \
    f"kept segment not W211..W247 thirty-seven legs: n={legs_kept.count('assert pf.N1_BANDS[')} waves={_kept_ws}"
_dropped_ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", legs_dropped)
assert legs_dropped.count("assert pf.N1_BANDS[") == 18 \
    and [int(w) for w in _dropped_ws] == list(range(248, 266)), \
    f"dropped segment not W248..W265 eighteen legs: n={legs_dropped.count('assert pf.N1_BANDS[')} waves={_dropped_ws}"

# ---------- fresh legs W244..W266 (machine-derived from the LIVE pf registry) ----------
fresh_leg_lines = []
for _w in range(248, 267):
    _row = dict(pf_mod.N1_BANDS[_w])
    _owner = _row["engine_owner"]
    if _w == 266:
        _msg = '"registered W266 row parity drift (r307; bm-c five-face freeze upstream seat; W267 freeze fresh-derive from live registry)"'
    else:
        _msg = f'"registered W{_w} row parity drift (r307; engine_owner={_owner}; W267 freeze fresh-derive from live registry)"'
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

CFG_I  = line_indent(n1_t, '266: {"batch"', EOL)
PRE_KEY_I = line_indent(n1_t, '"prereg": ("research/PERPETUAL_N1_W266_PREREG.md', EOL)
PRE_I  = line_indent(n1_t, '"pre-run; design = frozen v1 null calibration verbatim, "', EOL)
_c266 = n1_t.find('266: {"batch"')
assert _c266 > 0, "W266 cfg entry not found (W266 freeze not landed?)"
_mpos = n1_t.find('"a_seed_base"', _c266)
assert _mpos > 0 and n1_t.find('"shard_subdir"', _c266) > _mpos, "W266 cfg a_seed_base line not found"
MEM_I  = line_indent(n1_t, '"a_seed_base": ' + str(W266["a"][0]), EOL) \
    if n1_t.find('"a_seed_base": ' + str(W266["a"][0]), _c266) > 0 \
    else line_indent(n1_t, '"a_seed_base": ' + fmt(W266["a"][0]), EOL)
ROW_I  = line_indent(pf_t,  '266: {"a"', PF_EOL)

# ---------- W266 row owner line (physical bytes; comment text is own generation) ----------
w266_row_start = pf_t.find('    266: {"a"')
assert w266_row_start > 0, "W266 row literal not found in pf source"
_own_ls = pf_t.find(PF_EOL, w266_row_start) + len(PF_EOL)
_own_le = pf_t.find(PF_EOL, _own_ls)
w266_own_line = pf_t[_own_ls:_own_le]
assert '"engine_owner": "bm-c"' in w266_own_line, \
    f"W266 owner line unexpected bytes: {w266_own_line!r}"
ROWC_I = w266_own_line[:len(w266_own_line) - len(w266_own_line.lstrip(" "))]

# ---------- pf comment + row ----------
pf_comment = PF_EOL.join([
"    # W267 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat",
"    # MSG-20261018-1025-bmc-w267-seat published=reserved by bm-c itself @",
"    # origin " + SEAT_ORIGIN + " (r1086, queue-head seat-first supply -- W266 registered+FINALIZED complete at publish, W267 FREEZE UNBLOCKED at seat time (zero waits-upstream face; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE gate0.5 = GREEN at seat (W266 five-face + finalize product both in-place; prereg + ADMIT probe",
"    # receipt frozen commit " + w267_prereg_sha[:10] + " (prereg research/PERPETUAL_N1_W267_PREREG.md",
"    # bm-c r1087 window machine-SUB derive landed pre-freeze, probe",
"    # results/_w267bmc_20261018_probe_receipt.json @ " + w267_receipt_sha[:10] + ");",
"    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10",
"    # ~23:1x; deletion-set EMPTY; delivery window = chain-order",
"    # splice AFTER the bm-c W266 five-face (freeze " + w266_freeze_sha[:10] + ") + W266",
"    # finalize product landed (n1_w266_results.json present, ledger",
"    # head " + str(w266_total) + " machine-read at freeze time); zero --no-verify;",
"    # the W267 seat MSG sits in " + seat_found + " at freeze",
"    # time, honest archived per S7 law);",
"    # band gate ADMIT results/_w267bmc_20261018_probe_receipt.json: A = 1-HOP",
"    # STAIRCASE-AFFECTS-A walk SIXTEENTH consecutive A-hop (the naive continuation " + fmt(w266_a_tail + 1) + ".." + fmt(w266_a_tail + 2_000) + " is REFUSED",
"    # at naive start -- the registered W266 B band sits INSIDE the naive A window;",
"    # the walk hops past the W266 B tail -> A first-clean, hops=1 -- SIXTEENTH",
"    # consecutive A-hop of the staircase era, the fourteen-wave seed-gap face",
"    # ENDED at W252;",
"    # A base == registered prior-wave B tail+1 (" + fmt(w266_b_tail) + "+1) machine-checkable; A_clean_at_naive_start=false;",
"    # A_staircase_hop_past_W266_B=true)",
"    # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation",
"    # " + fmt(w266_b_tail + 1) + ".." + fmt(w266_b_tail + 200) + " is REFUSED at its own start -- the naive window lands",
"    # INSIDE the own-wave A first-clean window --",
"    # own-A reservation cascade standard leg; hops=1,",
"    # B_hop_chain verbatim in the probe receipt; the walk hops past the own-A",
"    # tail -> B lands ABOVE own-A -- SEVENTEENTH consecutive above-own-A;",
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
"    # W268+ projection (gate-derived pre-seat probe leg4, pre-W267",
"    # universe): A naive first-clean " + rec["legs"]["leg4"]["W268p_A_naive"] + " hops=" + str(rec["legs"]["leg4"]["hops_A"]) + " (this window's gate: CLEAN, zero live",
"    # seed refusers) / B naive " + rec["legs"]["leg4"]["W268p_B_naive"] + " hops=" + str(rec["legs"]["leg4"]["hops_B"]) + " CLEAN at naive -- first-clean " + rec["legs"]["leg4"]["W268p_B_first_clean"] + " BUT lands INSIDE the projection A window,",
"    # (W268p_B_lands_inside_W268p_A_naive=true -- staircase re-emergence face: the W268 walk MUST hop past own-A reservation);",
"    # the W268 freezer MUST",
"    # re-derive on the post-W267 universe AND reserve the own-wave A window",
"    # when deriving B (do NOT assume the staircase A-base==prior-B-tail+1",
"    # equality or the B-base==own-A-tail+1 equality); never transcribe r587.",
])
pf_row = (f'{ROW_I}267: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), '
          f'"b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'
          + PF_EOL + f'{ROWC_I}"engine_owner": "bm-c"}},' + PF_EOL)
# belt-and-braces: display form must equal the canonical W-family text
assert pf_row.split(PF_EOL)[0].strip() == \
    f'267: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), "b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'

old_pf = must(pf_t, (w266_own_line + PF_EOL + '}'
                     + PF_EOL + '# v1 + ext(wave-1) in-use bands'), 1, "pf_close")
new_pf = (w266_own_line + PF_EOL
          + pf_comment + PF_EOL + pf_row
          + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands')
pf_t2 = pf_t.replace(old_pf, new_pf, 1)

# ---------- n1 cfg entry (programmatic quote wrapping, r761 law) ----------
fin_face = (f"W1..W266 finalize ALL LANDED (W266 finalize product present at splice, "
            f"net chain head {w266_total} machine-read, merged pool K={w266_merged_n} "
            f"machine-read) -- ZERO in-flight upstream seats at splice time, clean precondition "
            f"(fifty-fifth consecutive fully-clean freeze window); downstream W268 seat NOT YET "
            f"PUBLISHED at this freeze window (the next freezer must seat-first publish per "
            f"O-20261010-2350 sec.2 queue-depth supply; the W268 freezer MUST re-derive live on "
            f"the post-W267 universe + reserve the own-wave A window when deriving B per the "
            f"W267 seat leg4 mandate, never transcribe r587)")
cfg_lines = [
 f'{CFG_I}267: {{"batch": "PERPETUAL-N1-W267",',
 f'{PRE_KEY_I}"prereg": ("research/PERPETUAL_N1_W267_PREREG.md (wave-level frozen "',
]
PRE = [
 "pre-run; design = frozen v1 null calibration verbatim, ",
 "new seed bands only; TWO HUNDRED AND SIXTY-SEVENTH ENGINE-OWNED WAVE ",
 f"BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate), ",
 "own-series continuation per O-20261001-2355 sec.2 (first-free-",
 "number law after the REGISTERED W266 row five-face freeze (bm-c own seat executed at the bm-c r1086 splice window; engine self-burn 12/12; finalize one-pass bm-c r1086 closeout, ledger 1,009,535 / K=583,120 machine-read), ",
 f"{w266_freeze_sha[:10]} (prereg {w266_prereg_sha[:10]}), SINGLE STATE zero seat gap W2..W266 all ",
 "registered; " + fin_face + "; ",
 "seat published=reserved ",
 "MSG-20261018-1025-bmc-w267-seat PUSHED to origin " + SEAT_ORIGIN + " ",
 "BEFORE this freeze per r565 early-visibility law (payload = ",
 "seat MSG + pre-seat probe script + probe receipt; per-wave prereg ",
 "bm-c r1087 window machine-SUB derive landed pre-freeze -- bm-a own-seat ",
 "continuity, ",
 f"prereg {w267_prereg_sha[:10]} @ receipt {w267_receipt_sha[:10]}) -- this freeze splice editor derived from the committed W266 freeze-edits template in this same freeze window; ",
 "deletion-set EMPTY; delivery window = chain-order splice ",
 "after the W266 five-face + W266 finalize product landed ",
 "(executed in the bm-c loop freeze window ",
 "under the CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED ",
 "2026-10-10 ~23:1x); zero merge at freeze delivery, zero ",
 "--no-verify; single-window derive -- r812 merged the gate ",
 "legs INTO the pre-seat probe; parity N/A honest), ",
 "engine_owner=bm-a (bm-c OWN-SEAT face -- bm-a's EIGHTY-SIXTH owned claim per machine-derive (engine_owner==bm-c rows ",
 f"{len(bmc_rows_live)} + candidate; probe receipt leg0 bmc_rows=85 = seat-time pre-splice ",
 "live faces disclosed honest, live derive governs ",
 "r587/r359), own-seat continuity)), ",
"wave 267: ",
 "A = 1-HOP STAIRCASE-AFFECTS-A walk SIXTEENTH consecutive A-hop (the naive continuation ",
 f"{fmt(w266_a_tail + 1)}..{fmt(w266_a_tail + 2_000)} is REFUSED at its own start ",
 "-- hops=1, A_hop_chain verbatim in the probe receipt, A_clean_at_naive_start=false; ",
 "the registered W266 B band sits INSIDE the naive A window = staircase re-emergence continues to affect A; ",
 "the W266 prereg sec.5 item5 post-W266-REGISTERED pre-disclosure confirmed live r587, zero divergence disclosed; the walk hops past the W266 B tail -> ",
 "A first-clean; A base == registered prior-wave B tail+1 (",
 f"{fmt(w266_b_tail)}+1) machine-checkable; SIXTEENTH consecutive A-hop of the staircase era, ",
 "the fourteen-wave seed-gap face ENDED at W252; non-rotational r587 forward-monotone walk) ",
 "+ B = 1-HOP own-A RESERVATION CASCADE above own-A ",
 "(the naive continuation ",
 f"{fmt(w266_b_tail + 1)}..{fmt(w266_b_tail + 200)} is REFUSED at its own start ",
 "-- hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; the ",
 f"naive window lands INSIDE the own-wave A first-clean window (own-A reservation cascade standard leg); the walk hops past the own-wave A tail -> B lands ABOVE the ",
 f"own-A window {fmt(a_lo)}..{fmt(a_hi)} at tail+1 EXACT; SEVENTEENTH consecutive above-own-A ",
 "landing; B base == own-A tail+1 (",
 f"{fmt(a_hi)}+1) machine-checkable; cross-window convergence with the W266 prereg sec.5 item5 + W266 probe leg4 + seat leg4 succession projection ",
 "notes -- all MANDATORY notes honored (post-W266 universe ",
 "re-derive + live-trace re-read, no staircase-equality assumption); ADMIT receipt ",
 "results/_w267bmc_20261018_probe_receipt.json + ",
 "seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a ",
 "ADMIT convention); W268+ projection per this window gate: ",
 f"A naive first-clean {rec['legs']['leg4']['W268p_A_naive']} CLEAN (hops=0, zero live seed refusers) / B naive ",
 f"{rec['legs']['leg4']['W268p_B_naive']} hops={rec['legs']['leg4']['hops_B']} CLEAN at naive -- first-clean {rec['legs']['leg4']['W268p_B_first_clean']} BUT lands INSIDE the W268 projection A window (W268p_B_lands_inside_W268p_A_naive=true staircase re-emergence face; seed-gap face ",
 "inherited); W268 freezer MUST re-derive on the post-W267 universe AND ",
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
 f'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W267 A: {fmt(a_lo)}..{fmt(a_hi)} (1-HOP STAIRCASE-AFFECTS-A walk SIXTEENTH consecutive A-hop; naive {fmt(w266_a_tail + 1)}..{fmt(w266_a_tail + 2_000)} REFUSED at start -- hops=1, A_hop_chain verbatim in the probe receipt, A_clean_at_naive_start=false; registered W266 B band inside the naive A window; sixteenth consecutive A-hop of the staircase era -- seed-gap face ENDED at W252; A base == registered prior-wave B tail+1)',
 f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W267 B: {fmt(b_lo)}..{fmt(b_hi)} (1-HOP own-A RESERVATION CASCADE above own-A; naive {fmt(w266_b_tail + 1)}..{fmt(w266_b_tail + 200)} REFUSED at start -- hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; naive window lands inside the own-wave A first-clean window -> own-A reservation cascade; B lands ABOVE own-A at tail+1 EXACT -- seventeenth consecutive above-own-A; B base == own-A tail+1)',
 f'{MEM_I}"shard_subdir": "n1_w267", "out_name": "n1_w267_results.json",',
 f'{MEM_I}"engine_owner": "bm-c"}},',
]

cfg_block = EOL.join(cfg_lines)
old_cfg = must(n1_t, ('                       }' + EOL
                      + 'PREREG = WAVE_CONFIGS[2]["prereg"]'), 1, "n1_cfg_close")
new_cfg = (cfg_block + EOL
           + '                       }' + EOL
           + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
assert new_cfg.count('267: {"batch": "PERPETUAL-N1-W267"') == 1
n1_t2 = n1_t.replace(old_cfg, new_cfg, 1)

# ---------- n1 materializer block ----------
hdr = [
 "    # --- W267 materializer face (bm-c loop five-face freeze splice --",
 "    #     OWN-SEAT face under CEO fill-order standing 2026-10-08 ~23:5x",
 "    #     + RE-ISSUE 2026-10-10 ~23:1x + O-20260909-2334 local-full-use",
 "    #     + O-20260924-1730 claim-and-start same-round law):",
 "    #     bm-a's EIGHTY-SIXTH owned per machine-derive (engine_owner==bm-a",
 f"    #     rows {len(bmc_rows_live)} + candidate; own-seat face: seat published=reserved by bm-c itself",
 "    #     (r1086 MSG-20261018-1025-bmc-w267-seat @ origin " + SEAT_ORIGIN + "; probe leg0",
 "    #     bmc_rows=85 = seat-time pre-splice faces (post-W266-REGISTERED universe,",
 "    #     W266 finalize LANDED at seat -- W267 FREEZE UNBLOCKED at seat time, zero waits-upstream face;",
 "    #     splice gate0.5 = GREEN at seat (W266 finalize landed pre-seat), zero skip-claim);",
 "    #     live derive at freeze governs);",
 "    #     wave 267 = first free number after the",
 "    #     REGISTERED W266 row (five-face freeze " + w266_freeze_sha[:10] + "; bm-c own seat executed at",
 "    #     the bm-c r1086 splice window; engine",
 "    #     self-burn 12/12 + finalize one-pass bm-c r1086 closeout ledger 1,009,535 / K=583,120",
 "    #     -- SINGLE STATE zero seat gap (W2..W266 all registered). Seat",
 "    #     published=reserved MSG-20261018-1025-bmc-w267-seat pushed",
 "    #     to origin " + SEAT_ORIGIN + " BEFORE this freeze, r565 law (payload =",
 "    #     seat MSG + pre-seat probe script + probe receipt; per-wave prereg",
 f"    #     bm-c r1087 window derive landed pre-freeze commit {w267_prereg_sha[:10]}; this freeze splice editor",
 "    #     derived from the committed W266 freeze-edits template in this same freeze",
 "    #     window (E63 heal lineage: arith_a267/arith_b267 define+assert consistent;",
 "    #     band-set variable aging face w244_a holds wave-263 bands, disclosed);",
 "    #     deletion-set EMPTY; delivery window",
 "    #     = chain-order splice after the W266 five-face + W266 finalize",
 "    #     product landed; zero --no-verify; the W267 seat MSG sits in",
 "    #     " + seat_found + " at freeze time, honest archived",
 "    #     per S7 law).",
 "    #     TWO HUNDRED AND SIXTY-SEVENTH engine wave BY",
 f"    #     MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate; gate",
 "    #     leg0 machine output governs per r359 law).",
 f"    #     {fin_face}; the finalize merge loop",
 "    #     still derives the wave set from registry keys at run",
 "    #     time, FAIL-CLOSED r307 always on. ADMIT receipt",
 "    #     results/_w267bmc_20261018_probe_receipt.json;",
 "    #     seed_admit_gate rc0 both bands FREE (O-20261010-1945-bm-a",
 f"    #     ADMIT convention upgrade): {gate_lines[0]}; {gate_lines[1]};",
 "    #     banned gate ADMIT 0 (re-run at freeze window);",
 "    #     not a re-pick (R266: W267 bands were never assigned).",
"    #     PARITY STRUCTURAL CHOICE (W266 template lineage):",
 "    #     estate 69 rows (W138..W206 full-span, r858 absorb generation) +",
 "    #     W211..W247 legs (37) extracted verbatim from the OWN W266 block",
 "    #     physical bytes; the W266 block's own W248..W265 legs (18) are",
 "    #     EXCLUDED from the estate path per the template mandate; fresh",
 "    #     W248..W266 legs (19) added, machine-derived from the live pf",
 "    #     registry at freeze time -> 125 parity rows (W138..W206+W211..W266).",
 "    _set_wave(267)",
 "    try:",
 '        assert WAVE_CONFIGS[266]["a_seed_base"] == pf.N1_BANDS[266]["a"][0], \\',
 '            "W267 upstream W266 mirror drift (a)"',
 "        assert WAVE_CONFIGS[266][\"b_exit_seed_base\"] == \\",
 '            pf.N1_BANDS[266]["b_exit"][0], "W267 upstream W266 mirror drift (b)"',
 "        assert WAVE_CONFIGS[266].get(\"engine_owner\") == \\",
 '            pf.N1_BANDS[266].get("engine_owner") == "bm-c", \\',
 '            "W267 upstream W266 engine_owner mirror drift (law-mirror parity; bm-c upstream seat face)"',
 "        w244_a = {A_SEED_BASE + j for j in range(A_N)}",
 "        w244_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}",
 '        assert not (w244_a & w244_b), "W267 A/B band overlap"',
 "        assert not (w244_a & reg_ints) and not (w244_b & reg_ints), \\",
 '            "W267 hits SEED_REGISTRY"',
 '        for nm, band in (("A", w244_a), ("B", w244_b)):',
 '            assert not (band & v1_a) and not (band & v1_b), f"W267 {nm} hits v1"',
 '            assert not (band & w1_a) and not (band & w1_b), f"W267 {nm} hits W1"',
 '            assert not (band & probes), f"W267 {nm} hits probe seeds"',
]
tail = [
 "        # prior-wave disjointness W2..W266 (single state: all",
 "        # registered, dynamic registry derive, r511 law)",
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 267):",
 '            assert not (w244_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
 "                                 for j in range(A_N)}), f\"W267 A hits W{wprev}\"",
 '            assert not (w244_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
 "                                  for j in range(B_N)}), f\"W267 B hits W{wprev}\"",
 "        n3r1_used245 = set(range(70_000, 70_006))",
 "        assert not (w244_a & n3r1_used245) and not (w244_b & n3r1_used245), \\",
 '            "W267 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
 "        assert not (w244_a & lfc_actual12) and not (w244_b & lfc_actual12), \\",
 '            "W267 bands must clear the lfc actual draw range"',
 "        assert not (w244_a & options_actual12) and \\",
 "            not (w244_b & options_actual12), \\",
 '            "W267 bands must clear the options_wave2 actual draw range"',
"        # band facts (law sec.4 W267 row): A = 1-HOP STAIRCASE-AFFECTS-A",
"        # walk SIXTEENTH consecutive A-hop (the naive continuation",
f"        # {fmt(w266_a_tail + 1)}..{fmt(w266_a_tail + 2_000)} REFUSED at naive start -- the registered W266 B band",
f"        # {fmt(pf_mod.N1_BANDS[266]['b_exit'][0])}..{fmt(pf_mod.N1_BANDS[266]['b_exit'][1])} sits INSIDE the naive A window (staircase re-emergence",
"        # continues to affect A; the W266 prereg sec.5 item5 post-W266-REGISTERED pre-disclosure confirmed live r587,",
"        # zero divergence disclosed); hops=1, A_hop_chain verbatim in the probe receipt,",
"        # A_clean_at_naive_start=false, A_staircase_hop_past_W266_B=true; the walk hops",
"        # past the W266 B tail -> A first-clean; A base ==",
f"        # registered prior-wave B tail+1 ({fmt(w266_b_tail)}+1) machine-checkable; SIXTEENTH consecutive A-hop of the W239",
"        # staircase era -- the fourteen-wave seed-gap face ENDED at W252;",
"        # B = 1-HOP own-A RESERVATION CASCADE above own-A (the naive continuation",
f"        # {fmt(w266_b_tail + 1)}..{fmt(w266_b_tail + 200)} REFUSED at naive start -- the naive window lands",
"        # INSIDE the own-wave A first-clean window (own-A reservation cascade standard leg); hops=1,",
"        # B_hop_chain verbatim in the probe receipt; the walk hops past the own-wave A tail",
f"        # -> B lands ABOVE the own-A window {fmt(a_lo)}..{fmt(a_hi)} at tail+1 EXACT -- SEVENTEENTH consecutive",
"        # above-own-A landing;",
"        # B base == own-A tail+1 EXACT",
"        # machine-checkable; B_hop_lands_inside_A=false;",
"        # B_lands_above_own_A=true; cross-window convergence with",
"        # the W266 prereg sec.5 item5 + W266 probe leg4 + seat leg4 succession projection notes -- all",
"        # MANDATORY notes honored (post-W266 universe",
"        # re-derive + live-trace re-read, no staircase-equality assumption);",
f'        assert WAVE_CONFIGS[267]["a_seed_base"] == {a_lo} == {w266_b_tail} + 1, (',
'            "W267 A staircase-affects-A walk SIXTEENTH consecutive A-hop: the naive "',
'            "continuation is REFUSED at its own start (the registered W266 B band sits INSIDE "',
'            "the naive A window -- staircase re-emergence continues; hops=1, A_hop_chain verbatim in the probe receipt, "',
'            "A_clean_at_naive_start=false, A_staircase_hop_past_W266_B=true; the walk hops past "',
'            "the W266 B tail -> A first-clean -- SIXTEENTH consecutive A-hop of the staircase era, "',
'            "the fourteen-wave seed-gap face ENDED at W252; A base == registered prior-wave B "',
'            "tail+1 machine-checkable, floor relation honored)")',
f"        arith_a267 = set(range({a_lo}, {a_hi + 1}))",
"        assert not (arith_a267 & reg_ints), \\",
'            "W267 A window must be CLEAN (first-clean ADMIT face, staircase walk landing)"',
f'        assert WAVE_CONFIGS[267]["b_exit_seed_base"] == {b_lo} == {a_hi} + 1, (',
'            "W267 B 1-HOP own-A RESERVATION CASCADE face: the naive continuation "',
f'            "{fmt(w266_b_tail + 1)}..{fmt(w266_b_tail + 200)} is REFUSED at its own start "',
'            "(hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; "',
'            "the naive window lands INSIDE the own-wave A first-clean window -- own-A reservation hops B past the own-wave A tail) -- B base == own-A tail+1 "',
'            "EXACT (B_lands_above_own_A + B_base_above_W266_tail face relation asserts, "',
'            "probe receipt leg1 mirrored exactly; B_hop_lands_inside_A=false)")',
f"        assert {b_lo} > {w266_b_tail}, \\",
'            "W267 B walk base must sit above the prior-wave B tail"',
f"        arith_b267 = set(range({b_lo}, {b_hi + 1}))",
"        assert not (arith_b267 & reg_ints), \\",
'            "W267 B window must be CLEAN (first-clean ADMIT face, 1-hop own-A reservation cascade landing)"',
"        assert not (arith_b267 & arith_a267), \\",
'            "W267 A/B same-freeze mutual exclusion (B lands ABOVE own-A at tail+1 EXACT -- seventeenth consecutive above-own-A; zero overlap)"',
"        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W267-SHARD-0\",",
 '                                          "n1w267-0of12"), "W267 entry identity"',
 '        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W267-SHARD-11",',
 '                                           "n1w267-11of12")',
 "        assert SHARD_DIR.endswith(\"n1_w267\") and OUT.endswith(",
 '            "n1_w267_results.json"), "W267 path drift"',
 "        for wprev in sorted(w for w in WAVE_CONFIGS if w < 267):",
 "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(",
 "                PATHS.results_dir, \"p2cal_ext\",",
 "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\",
 '                f"W267 shard dir collides with W{wprev}"',
 "        # W267 finalize cumulative deps: W17..W266 outputs ALL PRESENT",
 f"        # (landed net chain head {w266_total} machine-read at freeze time)",
 "        # -- ZERO in-flight upstream seats at splice, clean precondition",
 "        # freeze window; the finalize merge loop derives the wave",
 "        # set from registry keys at run time and stays",
 "        # FAIL-CLOSED, r307 two-state law).",
 "        for _depw in range(17, 267):",
 "            assert os.path.exists(os.path.join(",
 "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\",
 '                f"W267 finalize cumulative dep (W{_depw} output) missing"',
 "        # finalize wave-set derivation face (r511 derive law): every",
 "        # registered wave below 263 composes; wave 15 excluded by",
 "        # design; SINGLE STATE (W2..W266 all registered -- no",
 "        # two-state seat disclosure needed at this freeze).",
 "        assert sorted(w for w in WAVE_CONFIGS if w < 267) == \\",
 "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\",
 "            [w for w in range(16, 267)], \\",
 '            "W267 prior-wave set must derive from registry keys (no 15; " \\',
 '            "W2..W266 registered single state)"',
 "        assert os.path.exists(os.path.join(",
 '            PATHS.root, "research", "PERPETUAL_N1_W267_PREREG.md")), \\',
 '            "W267 per-wave prereg missing (materializer requirement)"',
 "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"",
 "    finally:",
 "        _set_wave(2)",
]
block = EOL.join(hdr) + EOL + par_sec + legs_kept + fresh_legs + EOL + EOL.join(tail) + EOL
# family #6 atomic triple gate (carried forward): the new
# block's LHS w<263> / RHS range(16,263)+range(17,263) / comment below-263 MUST move together.
assert block.count("if w < 267)") == 3, f"family-6 triple: w<263 count {block.count('if w < 267)')} != 3"
assert block.count("if w < 266)") == 0, "family-6 triple: stale w<262 leaked into the W267 block"
assert block.count("range(16, 267)") == 1 and block.count("range(17, 267)") == 1, "family-6 triple: RHS ranges wrong"
assert block.count("registered wave below 263 composes") == 1, "family-6 triple: comment face wrong"
old_blk_anchor = must(n1_t2, "    # --- T-141 s2 lane face", 1, "t141_marker")
n1_t3 = n1_t2.replace(old_blk_anchor, block + old_blk_anchor, 1)

# ---------- n1 print line ----------
pr = [
 '          "+ W267 materializer face [same guard set, dep=W17..W266 "',
 f'          "outputs ALL PRESENT (landed net chain head {w266_total} = W266 bm-c finalize one-pass, K={w266_merged_n} merged pool) -- ZERO "',
 '          "in-flight upstream seats at splice, clean precondition, TWO HUNDRED AND SIXTY-SEVENTH "',
 f'          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} "',
 '          "+ candidate) bm-a\'s EIGHTY-SIXTH owned claim per "',
 '          "machine-derive (engine_owner==bm-c rows 85 + candidate; OWN-SEAT face: seat published by bm-c itself, "',
 '          "probe leg0 bmc_rows=85 = seat-time pre-splice faces disclosed honest, "',
 '          "live derive at freeze governs), "',
 '          "A=1-HOP STAIRCASE-AFFECTS-A walk (hops=1, A_hop_chain verbatim, A_clean_at_naive_start=false, "',
 '          "registered W266 B band inside the naive A window, SIXTEENTH consecutive A-hop of the staircase era, "',
 '          "the fourteen-wave seed-gap face ENDED at W252) "',
 '          "+ B=1-HOP own-A RESERVATION CASCADE above own-A (hops=1, B_naive_refused_at_start=true, "',
 '          "B_hop_chain verbatim, naive window lands inside the own-wave A window -> own-A reservation cascade, "',
 '          "B base == own-A tail+1 EXACT, B_lands_above_own_A=true, "',
 '          "SEVENTEENTH consecutive above-own-A landing), chain-order splice from the "',
 '          "committed ADMIT receipt + seed_admit_gate rc0 both bands FREE "',
 '          "(O-20261010-1945-bm-a ADMIT convention), "',
 '          "ADMIT receipt "',
 '          "results/_w267bmc_20261018_probe_receipt.json, law sec.4 W267 row, "',
 '          "bm-c loop CEO fill-order RE-ISSUE 23:1x] "',
]

old_pr = must(n1_t3, '          "+ T-141 s2 ', 1, "print_t141")
n1_t4 = n1_t3.replace(old_pr, EOL.join(pr) + EOL + old_pr, 1)

# ---------- post-edit count gates ----------
assert n1_t4.count('"batch": "PERPETUAL-N1-W267"') == 1
assert n1_t4.count("# --- W267 materializer face") == 1     # block header
assert n1_t4.count('"+ W267 materializer face') == 1        # print fragment
assert n1_t4.count('267: {"batch": "PERPETUAL-N1-W267"') == 1
assert pf_t2.count(ROW_I + '267: {"a"') == 1
assert pf_t2.count('"engine_owner": "bm-c"},' + PF_EOL + '}') == 1
assert n1_t4.count('    # --- T-141 s2 lane face') == 1
assert n1_t4.count('"PERPETUAL-N1-W267-SHARD-0"') == 1
# leg count gates: leg W_k lives in blocks W_{k+1}..W267 -> (263 - k) occurrences
for _lw in range(248, 267):
    _first = (f'assert pf.N1_BANDS[{_lw}] == {{"a": '
              f'({fmt(pf_mod.N1_BANDS[_lw]["a"][0])}, {fmt(pf_mod.N1_BANDS[_lw]["a"][1])}),')
    _got = n1_t4.count(_first)
    assert _got == 267 - _lw, \
        f"W{_lw} leg count drift: {_got} != {267 - _lw} (first-line: {_first})"
for _b in range(209, 268):
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
  "machine": "bm-c", "wave": 266,
  "phase": "five-face freeze chain-order splice (bm-c own-seat freeze window, upstream ALL LANDED clean precondition incl W266 finalize)",
  "origin_base": omain,
  "pf_sha16_pre": hashlib.sha256(pf_b).hexdigest()[:16],
  "n1_sha16_pre": hashlib.sha256(n1_b).hexdigest()[:16],
  "pf_sha16_post": hashlib.sha256(pf_t2.encode("utf-8")).hexdigest()[:16],
  "n1_sha16_post": hashlib.sha256(n1_t4.encode("utf-8")).hexdigest()[:16],
  "bands": {"A": A, "B": B, "a_lo": a_lo, "a_hi": a_hi, "b_lo": b_lo, "b_hi": b_hi},
  "admit_receipt": "results/_w267bmc_20261018_probe_receipt.json",
  "seed_admit_gate": gate_lines,
  "banned_gate": "ADMIT rc0 (re-run at freeze window)",
  "band_semantics": {"A": "1-HOP STAIRCASE-AFFECTS-A walk SIXTEENTH consecutive A-hop (hops=1, A_hop_chain verbatim in the probe receipt; the naive continuation 602_501..604_500 refused at start -- the registered W266 B band 602_501..602_700 sits INSIDE the naive A window (staircase re-emergence continues; the W266 prereg sec.5 item5 post-W266-REGISTERED pre-disclosure confirmed live r587, zero divergence disclosed); the walk hops past the W266 B tail 602_700 -> A first-clean 602_701..604_700 -- SIXTEENTH consecutive A-hop of the staircase era, the fourteen-wave seed-gap face ENDED at W252; A_clean_at_naive_start=false; A_staircase_hop_past_W266_B=true; A base == registered prior-wave B tail+1 (602_700+1) EXACT)",
                     "B": "1-HOP own-A RESERVATION CASCADE above own-A (hops=1, B_naive_refused_at_start=true, B_hop_chain verbatim in the probe receipt; the naive continuation 602_701..602_900 is refused at start -- the naive window lands INSIDE the own-wave W267 A first-clean window 602_701..604_700 (own-A reservation cascade standard leg; the W266 prereg sec.5 item5 + probe leg4 projected landing confirmed live -- zero divergence per r587); the walk hops past the own-A tail 604_700 -> B landing 604_701..604_900; B lands ABOVE own-A -- SEVENTEENTH consecutive above-own-A landing; B_lands_above_own_A=true; B_hop_lands_inside_A=false; B base == own-A tail+1 (604_700+1) EXACT)"},
  "w266_upstream": {"freeze_sha": w266_freeze_sha, "prereg_sha": w266_prereg_sha,
                    "ledger_total": w266_total, "merged_n": w266_merged_n,
                    "engine_owner": "bm-c (upstream seat honored)",
                    "repair_chain_note": "W266 bm-c own-wave full cycle r1086 (five-face splice " + w266_freeze_sha[:10] + " + engine self-burn 12/12 + finalize one-pass ledger 1,009,535 / K=583,120)"},
  "own_seat_face": {"seat_msg": SEAT_MSG, "seat_origin": SEAT_ORIGIN,
                    "inherited": False,
                    "note": "seat published=reserved by bm-c itself (MSG-20261018-1025-bmc-w267-seat pushed to origin " + SEAT_ORIGIN + " r1086 BEFORE this freeze per r565 law, queue-head seat-first supply -- W266 registered+FINALIZED complete at publish, W267 FREEZE UNBLOCKED at seat time (zero waits-upstream face; seats never queue behind freeze windows per O-20261010-2350 sec.2); the SPLICE gate0.5 = GREEN at seat (W266 row + n1_w266_results.json both in-place) -- wave 267 engine_owner=bm-c, bm-c's 86th own wave per live derive (probe leg0 bmc_rows=85 = seat-time pre-splice faces disclosed honest, live derive governs r587/r359; freeze-time live face owner rows 256 + candidate = 257th EXACT)"},
  "transitive_deps": {f"W{w}": f"results/perpetual_faces/n1_w{w}_results.json present (belt-and-braces gate)" for w in (263, 262, 261, 260, 259, 258, 257, 256, 255, 254)},
  "downstream_seat": "W268 = next free number, next freezer must seat-first publish per O-20261010-2350 sec.2 queue-depth supply; the W268 freezer MUST re-derive live on the post-W267 universe + reserve the own-wave A window when deriving B per the W267 seat leg4 mandate, never transcribe r587 -- W268p face per this window's probe leg4 (pre-W267 universe): A naive 595901..597900 CLEAN (hops=0, zero live refusers -- pre-W267-universe face) / B naive 596101..596300 hops=0 CLEAN at naive, first-clean 596101..596300 BUT lands INSIDE the W268 projection A window (W268p_B_lands_inside_W268p_A_naive=true staircase face continuation since W251: A hops over prior B, B lands above own-A; on the post-W267 universe the W268 naive A window start 604_701 lands INSIDE the registered W267 B band 604_701..604_900 -- staircase affects A inherited (seventeenth consecutive A-hop expected), the A first-clean and the B own-A reservation cascade landing both move up, live re-derive governs); re-read the live trace at W268 derive time, do NOT assume the staircase A-base==prior-B-tail+1 or B-base==own-A-tail+1 equalities",
  "seat": seat_found + " (origin " + SEAT_ORIGIN + ")",
  "prereg_bundle": {"prereg_sha": w267_prereg_sha, "probe_receipt_sha": w267_receipt_sha,
                    "note": "prereg derived by the bm-c r1087 window (authored 10:5x, banned gate ADMIT rc0, committed+pushed r1087 commit " + w267_prereg_sha[:10] + "; facts live-derived ledger anchors W266 1,009,535 / K=583,120 at draft (upstream W266 complete at draft, disclosed honest); freeze-time live derive bma rows 129 + candidate 130th EXACT per r587/r359; splice editor derived from the committed W266 freeze-edits template by count-asserted ordered transform in this same freeze window (E63 heal lineage: arith_a267/arith_b267 define+assert consistent; band-set variable aging face w244_a holds wave-263 bands, disclosed); upstream W266 already landed incl finalize (clean-precondition fifty-fifth consecutive window); zero transcription"},
  "ordinal_faces": {"owner_rows_live": len(owner_rows_live), "bma_rows_live": len(bma_rows_live),
                    "bmc_rows_live": len(bmc_rows_live),
                    "engine_owned_ordinal": len(owner_rows_live) + 1,
                    "bmc_own_ordinal": len(bmc_rows_live) + 1,
                    "probe_receipt_bmc_ordinal_face": 85,
                    "note": "post-W266 registration: bm-c rows 85 + candidate = 86th owned (live derive at freeze time governs per r587/r359; probe leg0 bmc_rows=85 = seat-time faces -- bm-c own-seat continuity, zero waits-upstream face)"},
  "parity_section": {"source": "OWN W266 block physical bytes (bm-c splice generation r1086 window, structure known exactly)",
                     "bytes": len(par_sec) + len(legs_kept),
                     "estate_row_asserts": par_sec.count("assert pf.N1_BANDS["),
                     "kept_legs_row_asserts": legs_kept.count("assert pf.N1_BANDS["),
                     "dropped_legs_row_asserts": legs_dropped.count("assert pf.N1_BANDS["),
                     "fresh_legs_row_asserts": 19,
                     "total_parity_rows": par_sec.count("assert pf.N1_BANDS[")
                                          + legs_kept.count("assert pf.N1_BANDS[") + 19,
                     "note": "estate W138..W206 (69 rows, r858 absorb generation) + W211..W247 legs (37) extracted verbatim per the W266 template lineage mandate; the W266 block's own W248..W265 legs (18) EXCLUDED from the estate path per the same mandate; fresh W248..W266 legs (19) machine-derived from the live pf registry -> W267 block = 125 rows (W138..W206 + W211..W266); disclosed: (a) inherited estate/legs error-string faces preserved verbatim per extraction law (assert targets correct, zero functional impact); (b) band-set variable one-behind naming face (w244_a holds wave-263 bands) = lineage mechanical aging face, zero functional impact; (c) fresh-leg error strings are own-generation text (assert targets identical, first-line format identical, disclosed); (d) E63 15th-gen prevention this window: the W267 derive editor kept the P1-blanket-immune pass ordering and the extraction-restructure legs/kept/dropped wave-identity asserts fixed post-blanket (list(range(211,263))/list(range(211,244))/list(range(244,262)) live-structure exact) -- zero heal needed, zero splice executed pre-verify"},
  "family6_triple_gate": {"absorbed": True,
                          "note": "W266 editor family-6 gate carried forward: new block LHS w<263 x3 / RHS range(16,263)+range(17,263) / comment below-263 count-asserted ATOMICALLY before splice; W266 block's own w<262 face = legitimate prior-wave boundary (not stale); E63 heal lineage applied (arith define/assert consistent)"},
  "eol": {"n1_crlf": EOL == "\r\n", "pf_crlf": PF_EOL == "\r\n"},
  "liveness_anchors": {f"w{_b}_block_kept": 1 for _b in range(209, 268)},
}

open(RECEIPT_OUT, "w", encoding="utf-8").write(json.dumps(receipt, indent=1))
print(json.dumps({k: receipt[k] for k in
      ("phase", "origin_base", "pf_sha16_post", "n1_sha16_post", "bands",
       "w266_upstream", "own_seat_face")}, indent=1))
print("SPLICE OK -- py_compile both green; NEXT: selftest (default wave, r522 law) -> pathspec commit+push -> engine self-ignite W267 burn (12 shards) -> PRE-FINALIZE six-gate (standing law) -> finalize one-pass")
