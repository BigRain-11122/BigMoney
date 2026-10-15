# -*- coding: utf-8 -*-
"""W248 pre-seat probe (bm-c loop window r1030, 2026-10-15 16:4x; queue-depth
supply depth-2 lane: the upstream W247 seat is IN-FLIGHT upstream (bm-a seat
MSG-20261015-1608-bma-w247-seat, freeze pending their next window) -- this
W248 seat publishes per the seat-first law O-20261010-2350-bm-c sec.2: seats
do NOT queue behind freeze windows; queue depth is the physical guarantee of
saturation. The W248 FREEZE carries waits-upstream ARMED: the freezer (bm-c)
must wait for the W247 five-face freeze splice + finalize landing before the
W248 prereg derive + freeze, and MUST re-derive on the post-W247-REGISTERED
universe at freeze time -- never transcribe r587.
Standing CEO fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x +
O-20261013 22:1x CPU standing-open + O-20260924-1730 claim-ignite same-round
law + never-dry supply line O-1819 + O-20261015-0025 full mobilization.
Universe face = post-W246-REGISTERED (live registry; W247 splice NOT landed
locally -- asserted) + the W247 CANDIDATE bands machine-read from the bm-a
W247 seat probe receipt on origin (results/_w247bma_20261015_probe_receipt.json
bands A 559_501..561_500 / B 544_501..544_700) treated as reserved refusers
via the extra_bands leg -- bands are binding seat reservations, the prereg
derives finds within them, so the W248 derivation treating them as refusers
is sound; if the W247 freeze lands with divergent bands the freeze-time
re-derive governs honestly (the honest-walk assert fires and is re-read).
Anticipated face (W247 probe leg4, honest forward face): naive W248 A
continuation 561_501..563_500 first-clean hops=0 / naive B 544_701..544_900
first-clean hops=0 -- live re-derive governs either way, non-rotational r587
forward-monotone enforced in-walk.
Bloodline: _w247bma_20261015_probe.py derive machinery verbatim, W248 facts
live-registry/receipt-driven; leg0 extended with the in-flight-upstream
candidate-reservation leg (waits-upstream ARMED face)."""
import subprocess
import sys, os, json
if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from perpetual_faces import N1_BANDS
import science_gates

CREAT = 0x08000000
WIDTH_A = 2_000
WIDTH_B = 200

N3R1_USED = (71_000, 71_005)
PROBE_SEEDS = (95_000, 95_001, 95_002, 95_003)
CROSSFACE_PROBE_POINTS = (95_004, 95_006)
LFC_ACTUAL = (30_000, 30_099)
OPTIONS_ACTUAL = (63_000, 63_049)
N24_PROBE_POINTS = (40_000, 40_001)
N2_W15_PROBE_POINTS = (31_000, 31_500, 32_000)
V1_IN_USE = [(10_000, 10_099), (20_000, 20_019)]
W1_EXT = [(10_100, 12_099), (20_100, 20_299)]
receipt = {"probe": "W248 pre-seat probe (bm-c loop r1030 window, 2026-10-15 16:4x, queue-depth supply depth-2 lane: upstream W247 seat IN-FLIGHT (bm-a seat MSG-20261015-1608, freeze pending their next window); waits-upstream ARMED -- the W248 freeze waits for the W247 freeze splice + finalize landing; seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + CEO fill-order standing; universe = post-W246-REGISTERED + W247 candidate bands machine-read from the origin seat probe receipt, treated as reserved refusers)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape + W241..W246 landed faces + W247 in-flight face ------
keys = sorted(N1_BANDS)
w246_splice_landed = 246 in N1_BANDS
assert w246_splice_landed, "leg0 failed: W246 splice not landed (registry row absent -- r1017 freeze face broken)"
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 247))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
assert 247 not in N1_BANDS, "leg0 failed: W247 ALREADY registered locally (upstream freeze landed mid-probe -- re-derive on the post-W247 universe honestly, do not seat on a stale universe)"
W241_A = tuple(N1_BANDS[241]["a"])
W241_B = tuple(N1_BANDS[241]["b_exit"])
assert W241_A == (547_501, 549_500) and W241_B == (541_004, 541_203) and \
    N1_BANDS[241].get("engine_owner") == "bm-c", "leg0 failed: W241 registry row drift"
W242_A = tuple(N1_BANDS[242]["a"])
W242_B = tuple(N1_BANDS[242]["b_exit"])
assert W242_A == (549_501, 551_500) and W242_B == (541_204, 541_403) and \
    N1_BANDS[242].get("engine_owner") == "bm-a", "leg0 failed: W242 registry row drift"
assert W242_B[0] == W241_B[1] + 1, "leg0 failed: W242 B base != W241 B tail+1 (registry face drift)"

W243_A = tuple(N1_BANDS[243]["a"])
W243_B = tuple(N1_BANDS[243]["b_exit"])
assert W243_A == (551_501, 553_500) and W243_B == (541_501, 541_700) and \
    N1_BANDS[243].get("engine_owner") == "bm-a", "leg0 failed: W243 registry row drift"

W244_A = tuple(N1_BANDS[244]["a"])
W244_B = tuple(N1_BANDS[244]["b_exit"])
assert W244_A == (553_501, 555_500) and W244_B == (541_701, 541_900) and \
    N1_BANDS[244].get("engine_owner") == "bm-a", "leg0 failed: W244 registry row drift"
assert W244_B[0] == W243_B[1] + 1, "leg0 failed: W244 B base != W243 B tail+1"

W245_A = tuple(N1_BANDS[245]["a"])
W245_B = tuple(N1_BANDS[245]["b_exit"])
assert W245_A == (555_501, 557_500) and W245_B == (542_001, 542_200) and \
    N1_BANDS[245].get("engine_owner") == "bm-a", "leg0 failed: W245 registry row drift"

W246_A = tuple(N1_BANDS[246]["a"])
W246_B = tuple(N1_BANDS[246]["b_exit"])
assert W246_A == (557_501, 559_500) and W246_B == (542_201, 542_400) and \
    N1_BANDS[246].get("engine_owner") == "bm-a", "leg0 failed: W246 registry row drift (bm-a r1017 splice + r1018 finalize face)"
assert W246_B[0] == W245_B[1] + 1, \
    "leg0 failed: W246 B base != W245 B tail+1 (registry face drift: double-clean arithmetic continuation)"

for _w in (243, 244, 245, 246):
    _p = os.path.join(ROOT, "results", "perpetual_faces", f"n1_w{_w}_results.json")
    assert os.path.exists(_p), f"leg0 failed: n1_w{_w}_results.json absent (W{_w} finalize not landed)"

w246_results = os.path.join(ROOT, "results", "perpetual_faces", "n1_w246_results.json")
w246_out = json.load(open(w246_results, encoding="utf-8"))
w246_led = (w246_out.get("science_gates") or {}).get("ledger") or {}
w246_total = w246_led.get("total")
w246_merged_n = None
w246_klift = None
try:
    w246_merged_n = w246_out["null_pool_cumulative"]["merged"]["n_values"]
except Exception:
    pass
try:
    w246_klift = w246_out["skill_line_v2_k_lift"]["line_delta_k_lift"]
except Exception:
    pass
assert w246_total == 965_535 and w246_merged_n == 539_120, \
    f"leg0 failed: W246 finalize anchors drift: total={w246_total} merged={w246_merged_n} (expect 965,535 / 539,120)"
assert w246_klift is not None and abs(w246_klift) <= 0.02, \
    f"leg0 failed: W246 K-lift out-of-band at seat time: {w246_klift} (expect |delta|<=0.02 per the frozen prereg key-4 band)"

owner_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner")]
bmc_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-c"]
bma_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-a"]
bmb_rows = [w for w, c in N1_BANDS.items() if c.get("engine_owner") == "bm-b"]
owner_total = len(owner_rows)
assert owner_total == 236 and len(bmc_rows) == 67, \
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 236/67 post-W246-splice, W247 unregistered)"
ordinal = owner_total + 2  # 236 registered + in-flight W247 seat (237th) + this candidate
assert ordinal == 238, f"leg0 ordinal derive: {ordinal} != 238"
assert len(bma_rows) == 128, f"leg0 bma ordinal drift: {len(bma_rows)} (expect 128 post-W246-registration)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"
bmc_ordinal = len(bmc_rows) + 1
assert bmc_ordinal == 68, f"leg0 bmc ordinal derive: {bmc_ordinal} != 68"

# --- leg 0.5: in-flight upstream W247 seat candidate reservation (origin face) --
out247_seat = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
    encoding="utf-8", errors="replace")
seat247_hits = [ln for ln in out247_seat.splitlines()
                if "w247" in ln.lower() and "seat" in ln.lower()]
assert seat247_hits, "leg0.5 failed: W247 seat MSG not found on origin (in-flight upstream face absent -- re-check the supply chain)"
w247_receipt_raw = subprocess.check_output(
    ["git", "show", "origin/main:results/_w247bma_20261015_probe_receipt.json"],
    cwd=ROOT, encoding="utf-8", errors="replace")
w247_receipt = json.loads(w247_receipt_raw)
W247c_A = tuple(w247_receipt["bands"]["A"])
W247c_B = tuple(w247_receipt["bands"]["B"])
assert W247c_A == (559_501, 561_500) and W247c_B == (544_501, 544_700), \
    f"leg0.5 failed: W247 candidate bands drift vs the published seat face: A={W247c_A} B={W247c_B} (re-read the live origin receipt honestly)"
assert w247_receipt.get("verdict") == "ADMIT", "leg0.5 failed: W247 seat probe receipt verdict != ADMIT"
receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W246-registered+FINALIZED",
    "w246_splice_landed": w246_splice_landed,
    "w246_face": "registry-row",
    "w246_bands": {"A": list(W246_A), "B": list(W246_B)},
    "w246_finalize_landed": True,
    "w246_finalize_anchors": {"ledger_total": w246_total, "merged_n": w246_merged_n,
                               "skill_line_delta_k_lift": w246_klift},
    "w247_inflight_upstream": True,
    "w247_seat_origin": seat247_hits,
    "w247_candidate_bands": {"A": list(W247c_A), "B": list(W247c_B)},
    "waits_upstream": "ARMED (W247 freeze+finalize pending; the W248 freeze must wait and re-derive on the post-W247-REGISTERED universe)",
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": ordinal, "bmc_ordinal": bmc_ordinal,
    "bmc_ordinal_note": ("bm-c 68th owned [attempt-continuity: the superseded W245-bmc seat claim "
                          "(quarantined 20261015T0924) left the 67 live bm-c rows intact; live derive "
                          "governs r359]; engine wave ordinal = 236 registry owner rows + the "
                          "in-flight W247 seat (237th, bm-a reserved) + this candidate = 238th"),
    "anchor": ("W246 registered+FINALIZED upstream-1 (bm-a r1018 closeout ledger 965,535 / K=539,120; "
               "n1_w246_results.json landed; five-key ALL PASS results/_r1017bma_w246_fivekeys.json); "
               "W247 seat IN-FLIGHT upstream (bm-a seat MSG-20261015-1608, freeze pending their next "
               "window) -- waits-upstream ARMED: this W248 SEAT = queue-depth supply depth-2 per "
               "seat-first law O-20261010-2350 sec.2 (seats never queue behind freeze windows; "
               "standing CEO fill-order + O-20261013 22:1x CPU standing-open + O-20261015-0025 "
               "full mobilization + never-dry O-1819); the W248 FREEZE is BLOCKED until the W247 "
               "freeze splice + finalize lands, and must re-derive on the post-W247 universe")}
print(f"leg0: {len(N1_BANDS)} rows tail=W246-registered+FINALIZED (W247 unregistered, in-flight seat upstream), W246 face=registry A={W246_A} B={W246_B}, owner={owner_total} + W247-seat(237th) -> W248=238th wave candidate, bm-c 68th owned")
print(f"leg0.5: W247 candidate bands machine-read from origin seat receipt: A={W247c_A} B={W247c_B} (treated as reserved refusers; waits-upstream ARMED)")

# --- W248 own vacancy on origin -------------------------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                        "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                       capture_output=True)
all_inbox = r_vac.stdout.decode("utf-8").splitlines()
w248_seats = [ln for ln in all_inbox if "w248" in ln.lower() and "seat" in ln.lower()]
assert w248_seats == [], f"vacancy failed: W248 seats already exist: {w248_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '248: {"a": (' not in out_pf, "vacancy failed: W248 row ALREADY on origin (r511 tail-lock"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W248"' not in outn1_vac, "vacancy failed: W248 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W248_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W248 per-wave prereg ALREADY on origin"
print("vacancy: W248 origin vacancy held (no seat / row / configs / prereg)")

points = {v for v in science_gates.SEED_REGISTRY.values() if isinstance(v, int)}
points |= set(N24_PROBE_POINTS) | set(N2_W15_PROBE_POINTS)
points |= set(CROSSFACE_PROBE_POINTS)
points |= set(range(N3R1_USED[0], N3R1_USED[1] + 1))
points |= set(PROBE_SEEDS)
bands = []
for wnum, cfg in N1_BANDS.items():
    for key in ("a", "b_exit"):
        bands.append(tuple(cfg[key]))
bands += V1_IN_USE + W1_EXT
actual = [LFC_ACTUAL, OPTIONS_ACTUAL]

# --- leg 1: honest forward walk from the W247 CANDIDATE tails (reserved) --------
ARITH_A = (W247c_A[1] + 1, W247c_A[1] + WIDTH_A)
ARITH_B = (W247c_B[1] + 1, W247c_B[1] + WIDTH_B)


def first_clean(lo, width, trace=None, extra_bands=()):
    hops = 0
    prev_lo = lo
    while True:
        hi = lo + width - 1
        bad_pts = [p for p in points if lo <= p <= hi]
        bad_bands = [b for b in list(bands) + list(extra_bands) + actual
                     if overlaps((lo, hi), b)]
        if not bad_pts and not bad_bands:
            return (lo, hi), hops
        jump = max([p + 1 for p in bad_pts] + [b[1] + 1 for b in bad_bands])
        assert jump > prev_lo, f"non-rotational violation: jump {jump} <= {prev_lo}"
        if trace is not None:
            trace.append({"hop": hops + 1, "window": [lo, hi], "jump_to": jump,
                          "refuser_pts": sorted(bad_pts),
                          "refuser_bands": [list(b) for b in bad_bands]})
        lo = jump
        prev_lo = lo
        hops += 1


a_trace = []
(fc_a, hops_a) = first_clean(ARITH_A[0], WIDTH_A, trace=a_trace,
                             extra_bands=(W247c_A, W247c_B))
# own-wave A reservation for B (standard leg): B walk reserves the own-A window
b_trace_own = []
(fc_b, hops_b) = first_clean(ARITH_B[0], WIDTH_B, trace=b_trace_own,
                             extra_bands=(W247c_A, W247c_B, fc_a))
assert fc_a[0] == ARITH_A[0], ("leg1 A refused at naive start (W247 probe leg4 anticipated "
                                "first-clean 561_501..563_500 hops=0 on this universe; never "
                                "transcribe r587 -- if this fires the universe changed: re-read "
                                "the live trace and the W247 candidate reservation honestly")
assert not overlaps(fc_a, W246_A) and not overlaps(fc_a, W246_B), \
    "leg1 failed: A overlaps prior-wave registered bands"
assert not overlaps(fc_a, W247c_A) and not overlaps(fc_a, W247c_B), \
    "leg1 failed: A overlaps the in-flight W247 candidate reservation"
assert fc_a[0] >= W246_B[1] + 1, \
    "leg1 failed: A base must land at-or-after the registered prior-wave B tail+1 (mutual exclusion floor)"
assert hops_b == 0 and fc_b == (544_701, 544_900), \
    f"leg1 B unexpected walk face (the W247 probe leg4 projected naive B 544_701..544_900 first-clean hops=0; if the universe changed the honest walk governs and this assert must be re-derived honestly): got hops={hops_b} fc_b={fc_b}"
assert fc_b[0] > W247c_B[1], \
    "leg1 failed: B base must land above the in-flight W247 candidate B tail (forward-monotone)"
assert not overlaps(fc_b, fc_a), "leg1 failed: B first-clean window lands inside the own-wave A window (B_hop lands-inside-A leg must be FALSE)"
assert not overlaps(fc_b, W246_A) and not overlaps(fc_b, W246_B), \
    "leg1 failed: B overlaps prior-wave registered bands"
assert not overlaps(fc_b, W247c_A) and not overlaps(fc_b, W247c_B), \
    "leg1 failed: B overlaps the in-flight W247 candidate reservation"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a, "A_hop_chain": a_trace,
    "B": list(fc_b), "hops_B": hops_b, "B_hop_chain": b_trace_own,
    "B_naive_first_clean": list(fc_b), "B_naive_hops": hops_b,
    "B_hop_lands_inside_A": bool(overlaps(fc_b, fc_a)),
    "A_semantics": ("A arithmetic continuation from the IN-FLIGHT W247-CANDIDATE A tail "
                    "561_500+1 = 561_501..563_500 is CLEAN at naive start on the "
                    "post-W246-REGISTERED universe + W247 candidate reservation "
                    "(tenth consecutive seed-gap A-continuation face, anticipated by the "
                    "W247 probe leg4 and confirmed live; never transcribe r587); A base = "
                    "first clean window, forward-monotone non-rotational r587 enforced "
                    "in-walk; A base >= registered prior-wave B tail+1 floor relation"),
    "B_semantics": ("B arithmetic continuation from the IN-FLIGHT W247-CANDIDATE B tail "
                    "544_700+1 = 544_701..544_900 is CLEAN at naive start (hops=0, "
                    "past the W239 staircase band-hop landing; the registered W239 A band "
                    "542_501..544_500 and the W247 candidate B band 544_501..544_700 both "
                    "sit below the walk start); B_hop lands-inside-A=false leg; "
                    "B_no_ownA_jump=true (the clean B window is below the own-A window)"),
    "relation_asserts": {"A_clean_at_naive_start": True,
                          "A_base_ge_priorB_tail_plus1": True,
                          "B_clean_at_naive_start": True,
                          "B_base_above_W247c_tail": True,
                          "AB_mutual_exclusion": True,
                          "B_hop_lands_inside_A": False,
                          "W247c_reservation_respected_A": True,
                          "W247c_reservation_respected_B": True}}
print(f"leg1: A {fc_a} hops={hops_a} (hop chain {[(t['window'], t['jump_to']) for t in a_trace]}) | B {fc_b} hops={hops_b} (refusal trace {[(t['window'], t['jump_to'], t['refuser_bands']) for t in b_trace_own]})")

# --- leg 2: seed_admit_gate rc0 ADMIT both bands (O-20261010-1945-bm-a convention) --
gate_lines = []
for base, span in ((fc_a[0], WIDTH_A), (fc_b[0], WIDTH_B)):
    r = subprocess.run([sys.executable, os.path.join(ROOT, "Tools", "seed_admit_gate.py"),
                         str(base), "--span", str(span)], cwd=ROOT, capture_output=True,
                        text=True, encoding="utf-8", errors="replace")
    out = (r.stdout or "").strip().splitlines()
    verdict = out[-1] if out else f"rc{r.returncode} empty"
    assert r.returncode == 0 and "verdict=FREE" in verdict, \
        f"leg2 failed: gate rc={r.returncode} base={base} span={span}: {verdict}"
    gate_lines.append(f"seed_admit_gate rc0 base={base} span={span} "
                      f"checked={span} verdict=FREE")
receipt["legs"]["leg2"] = {"conflicts": 0, "seed_admit_gate": gate_lines}
print("leg2: " + " | ".join(gate_lines))

receipt["legs"]["leg3"] = {"origin_vacancy": True}
print("leg3: origin vacancy TRUE (seat/row/configs/prereg four-check green)")

# --- leg 4: W249+ naive projection (pre-W248 universe, honest forward face) ------
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
pA_refusers = sorted(p for p in points if pA[0] <= p <= pA[1])
receipt["legs"]["leg4"] = {
    "W249p_A_naive": f"{pA[0]}..{pA[1]}", "W249p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W249p_A_naive_refusers_seeds": pA_refusers,
    "W249p_B_naive": f"{pB[0]}..{pB[1]}", "W249p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W249p_B_lands_inside_W249p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W249+ projection on the pre-W248 universe (assuming the W248 seat bands "
             "declared here register verbatim). W249 freezer MUST re-derive on the "
             "post-W248 universe AND reserve the own-wave A window when deriving B "
             "-- never transcribe r587; seed-gap face inherited from W239..W247: "
             "A/B decoupled, re-read the live trace, do NOT assume the staircase "
             "A-base==prior-B-tail+1 equality.")}
print(f"leg4: W249+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": list(fc_a), "B": list(fc_b),
                    "a_lo": fc_a[0], "a_hi": fc_a[1],
                    "b_lo": fc_b[0], "b_hi": fc_b[1]}
out_path = os.path.join(ROOT, "results", "_w248bmc_20261015_probe_receipt.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PROBE ADMIT receipt written:", out_path)
