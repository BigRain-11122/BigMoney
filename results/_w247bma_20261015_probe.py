# -*- coding: utf-8 -*-
"""W247 pre-seat probe (bm-a loop window r1018, 2026-10-15 16:0x; own-seat
continuity lane: bm-a just landed the W246 finalize chain in this same
window -- sixgate ALL PASS + finalize one-pass (ledger 963,335+2,200=965,535
EXACT / merged pool K=539,120 / skill_line 1.1935->1.1935 K-lift +0.0000
in-band) + five-key ALL PASS + prereg sec7/8 backfill. Standing CEO
fill-order 2026-10-08 ~23:5x re-issued 2026-10-10 ~23:1x + O-20261013 22:1x
CPU standing-open order + O-20260924-1730 claim-ignite same-round law +
never-dry supply line O-1819 + O-20261010-2350-bm-c sec.2 seat-first law:
seats do NOT queue behind freeze windows -- queue depth is the physical
guarantee of saturation.
Upstream face = W246 registered+FINALIZED (bm-a r1018 same-window closeout:
seat MSG-20261015-1328-bma-w246-seat + prereg b2f893d14e6f763c (sec7/8
backfilled 34,724B) + five-face freeze splice 650953086 (pf a0f23ec2f7a38b7f
/ n1 c190658e307b8adc, sixgate splice-integrity green) + engine self-burn
12/12 done 15:44 + finalize one-pass ledger 965,535 EXACT / merged pool
K=539,120 machine-read (n1_w246_results.json: merged n=539,120 mu=-0.09282
sigma=0.24505 / w246_only n=2,200 mu=-0.09247 sigma=0.24802 / se_mu@539120
0.000334 narrowing chain continues / skill_line 1.1935->1.1935 K-lift
+0.0000 third-consecutive in-band micro-move) + five-key ALL PASS
results/_r1017bma_w246_fivekeys.json + product n1_w246_results.json
landed). ZERO in-flight upstream seats at this seat window -- the W247
FREEZE is UNBLOCKED immediately (waits-upstream DISARMED by the W246
finalize landing 16:0x); this W247 seat = the queue-depth supply depth-1.
Per the W246 prereg sec.8 downstream_seat mandate: re-derive live on the
post-W246-REGISTERED universe AND reserve the own-wave A window when
deriving B, W141 precedent, never transcribe r587; seed-gap face inherited:
W246 A/B are decoupled, do NOT assume the staircase A-base==prior-B-tail+1
equality. Anticipated face (W246 probe leg4 + W246 prereg sec.8, honest
forward face): naive W247 A continuation 559_501..561_500 first-clean
hops=0 (no live refusers) / naive B 542_401..542_600 REFUSED by the
registered W239 A band 542_501..544_500 -> first-clean 544_501..544_700
hops=1 staircase band-hop face first-materialized (B base == refuser
band end 544_500+1 EXACT; B_hop lands-inside-A=false leg present; W246 A
557_501..559_500 sits far above the B staircase) -- live re-derive
governs either way, non-rotational r587 forward-monotone enforced
in-walk.
Bloodline: _w246bma_20261015_probe.py derive machinery verbatim, W247
facts live-registry/receipt-driven; single-state leg0 (W246 splice
LANDED + W246 finalize LANDED same window)."""
import subprocess
import sys, os, json
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
receipt = {"probe": "W247 pre-seat probe (bm-a loop r1018 window, 2026-10-15 16:0x, own-seat continuity lane: bm-a landed the W246 finalize chain this same window; CEO fill-order standing + seat-first law O-20261010-2350 sec.2 + never-dry O-1819 + O-20261013 22:1x CPU standing-open; post-W246-REGISTERED universe, upstream W246 registered+FINALIZED (bm-a r1018 closeout ledger 965,535 / K=539,120); ZERO in-flight upstream seats -- W247 freeze UNBLOCKED at seat time, queue-depth supply depth-1)", "legs": {}}


def overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True,
               creationflags=CREAT)

# --- leg 0: registry shape + W241..W246 landed faces + W246 finalize face ---
keys = sorted(N1_BANDS)
w246_splice_landed = 246 in N1_BANDS
assert w246_splice_landed, "leg0 failed: W246 splice not landed (registry row absent -- r1017 freeze face broken)"
base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 247))
assert keys == base_keys, f"leg0 failed: unexpected registry keys tail {keys[-5:]}"
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

# W246 immediate-upstream bands: registry row face (splice LANDED r1017 freeze 650953086, r1018 finalize)
W246_A = tuple(N1_BANDS[246]["a"])
W246_B = tuple(N1_BANDS[246]["b_exit"])
assert W246_A == (557_501, 559_500) and W246_B == (542_201, 542_400) and \
    N1_BANDS[246].get("engine_owner") == "bm-a", "leg0 failed: W246 registry row drift (bm-a r1017 splice + r1018 finalize face)"
assert W246_B[0] == W245_B[1] + 1, \
    "leg0 failed: W246 B base != W245 B tail+1 (registry face drift: double-clean arithmetic continuation)"

# W243/W244/W245/W246 finalize landed faces (upstream transitive deps)
for _w in (243, 244, 245, 246):
    _p = os.path.join(ROOT, "results", "perpetual_faces", f"n1_w{_w}_results.json")
    assert os.path.exists(_p), f"leg0 failed: n1_w{_w}_results.json absent (W{_w} finalize not landed)"

# W246 finalize landed face (the immediate upstream anchor)
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
    f"leg0 ordinal drift: owner={owner_total} bmc={len(bmc_rows)} (expect 236/67 post-W246-splice)"
ordinal = owner_total + 1
assert ordinal == 237, f"leg0 ordinal derive: {ordinal} != 237"
assert len(bma_rows) == 128, f"leg0 bma ordinal drift: {len(bma_rows)} (expect 128 post-W246-registration)"
assert len(bma_rows) + len(bmb_rows) + len(bmc_rows) == owner_total, \
    f"leg0 owner bucket mismatch: {len(bma_rows)}+{len(bmb_rows)}+{len(bmc_rows)} != {owner_total}"
bma_ordinal = len(bma_rows) + 1
assert bma_ordinal == 129, f"leg0 bma ordinal derive: {bma_ordinal} != 129"

# W246 seat on origin (the prior closeout chain face)
outseat246 = subprocess.check_output(
    ["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
     "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
    encoding="utf-8", errors="replace")
seat_hits = [ln for ln in outseat246.splitlines()
             if "w246" in ln.lower() and "seat" in ln.lower()]
assert seat_hits, "leg0 failed: W246 seat MSG not found on origin (closeout chain face absent)"
receipt["legs"]["leg0"] = {
    "rows": len(N1_BANDS), "tail": "W246-registered+FINALIZED",
    "w246_splice_landed": w246_splice_landed,
    "w246_face": "registry-row",
    "w246_bands": {"A": list(W246_A), "B": list(W246_B)},
    "w246_finalize_landed": True,
    "w246_finalize_anchors": {"ledger_total": w246_total, "merged_n": w246_merged_n,
                               "skill_line_delta_k_lift": w246_klift},
    "owner_rows": owner_total, "bmc_rows": len(bmc_rows),
    "bma_rows": len(bma_rows), "bmb_rows": len(bmb_rows),
    "ordinal": ordinal, "bma_ordinal": bma_ordinal,
    "bma_ordinal_note": ("bm-a own-seat continuity: 128 live bm-a rows (tail=W246 registered+FINALIZED "
                          "bm-a r1018 same-window closeout: ledger 965,535 EXACT / merged pool K=539,120 / "
                          "skill_line 1.1935->1.1935 K-lift +0.0000 third-consecutive in-band micro-move) + this candidate = 129th owned; engine wave "
                          f"ordinal = {owner_total} registry owner rows + this candidate = 237th; live derive governs r359"),
    "anchor": ("W246 registered+FINALIZED upstream (bm-a r1018 closeout ledger 965,535 / K=539,120; "
               "n1_w246_results.json landed; five-key ALL PASS results/_r1017bma_w246_fivekeys.json); "
               "ZERO in-flight upstream seats at seat time -- the W247 FREEZE is UNBLOCKED immediately "
               "(waits-upstream DISARMED by the W246 finalize landing 16:0x); this W247 SEAT = "
               "queue-depth supply depth-1 (first seat of the new supply cycle) per seat-first law "
               "O-20261010-2350 sec.2 (seats never queue behind freeze windows; standing CEO fill-order "
               "2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x + O-20261013 22:1x CPU standing-open + never-dry O-1819)")}
print(f"leg0: {len(N1_BANDS)} rows tail=W246-registered+FINALIZED, W246 face=registry A={W246_A} B={W246_B}, owner={owner_total} -> 237th wave candidate, bm-a 129th owned (own-seat continuity)")

# --- W247 own vacancy on origin -------------------------------------------------
r_vac = subprocess.run(["git", "ls-tree", "--name-only", "-r", "origin/main", "--",
                        "fleet/inbox/", "fleet/inbox/processed/"], cwd=ROOT,
                       capture_output=True)
all_inbox = r_vac.stdout.decode("utf-8").splitlines()
w247_seats = [ln for ln in all_inbox if "w247" in ln.lower() and "seat" in ln.lower()]
assert w247_seats == [], f"vacancy failed: W247 seats already exist: {w247_seats}"
out_pf = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '247: {"a": (' not in out_pf, "vacancy failed: W247 row ALREADY on origin (r511 tail-lock"
outn1_vac = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
    cwd=ROOT, encoding="utf-8", errors="replace")
assert '"PERPETUAL-N1-W247"' not in outn1_vac, "vacancy failed: W247 WAVE_CONFIGS ALREADY on origin"
outpre_vac = subprocess.check_output(["git", "ls-tree", "--name-only", "origin/main", "--",
                                       "research/PERPETUAL_N1_W247_PREREG.md"], cwd=ROOT,
                                      encoding="utf-8", errors="replace").strip()
assert not outpre_vac, "vacancy failed: W247 per-wave prereg ALREADY on origin"
print("vacancy: W247 origin vacancy held (no seat / row / configs / prereg)")

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

# --- leg 1: honest forward walk from the W246 registered tails ------------------
ARITH_A = (W246_A[1] + 1, W246_A[1] + WIDTH_A)
ARITH_B = (W246_B[1] + 1, W246_B[1] + WIDTH_B)


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
(fc_a, hops_a) = first_clean(ARITH_A[0], WIDTH_A, trace=a_trace)
b_trace = []
(fc_b, hops_b) = first_clean(ARITH_B[0], WIDTH_B, trace=b_trace,
                             extra_bands=(fc_a,))
(fc_b_naive, hops_b_naive) = first_clean(ARITH_B[0], WIDTH_B)
assert fc_a[0] == ARITH_A[0], ("leg1 A refused at naive start (seed-decoupled clean continuation "
                                "anticipated by the W246 probe leg4 first-clean 559_501..561_500 "
                                "hops=0; never transcribe r587 -- re-read the live trace if this fires")
assert not overlaps(fc_a, W246_A) and not overlaps(fc_a, W246_B), \
    "leg1 failed: A overlaps prior-wave registered bands"
assert fc_a[0] >= W246_B[1] + 1, \
    "leg1 failed: A base must land at-or-after prior-wave B tail+1 (mutual exclusion floor)"
# B staircase band-hop face (W246 probe leg4 + W246 prereg sec.8 downstream_seat
# anticipation: naive B 542_401..542_600 REFUSED by the registered W239 A band
# 542_501..544_500 -> first-clean 544_501..544_700 hops=1). Live re-derive
# governs; if this assert fires the universe changed -- re-read honestly.
assert hops_b == 1 and fc_b == (544_501, 544_700), \
    f"leg1 B unexpected walk face (the W246 sec.8 downstream_seat projected hops=1 -> 544_501..544_700 staircase band-hop via the registered W239 A band 542_501..544_500 -- re-read the live trace; if the universe changed the honest walk governs and this assert must be re-derived honestly): got hops={hops_b} fc_b={fc_b}"
assert fc_b[0] > W246_B[1], \
    "leg1 failed: B base must land above the prior-wave B tail (forward-monotone)"
assert not overlaps(fc_b, fc_a), "leg1 failed: B first-clean window lands inside the own-wave A window (B_hop lands-inside-A leg must be FALSE per the W246 sec.8 projection)"
assert not overlaps(fc_b, W246_A) and not overlaps(fc_b, W246_B), \
    "leg1 failed: B overlaps prior-wave registered bands"
assert fc_b == fc_b_naive, "leg1 failed: B needed an own-A reservation jump (not expected on this universe: the hop refuser is the registered W239 A band, own-A sits far above the B staircase -- re-read trace if this fires)"
receipt["legs"]["leg1"] = {
    "ARITH_A": list(ARITH_A), "ARITH_B": list(ARITH_B),
    "A": list(fc_a), "hops_A": hops_a, "A_hop_chain": a_trace,
    "B": list(fc_b), "hops_B": hops_b, "B_hop_chain": b_trace,
    "B_naive_first_clean": list(fc_b_naive), "B_naive_hops": hops_b_naive,
    "B_hop_lands_inside_A": bool(overlaps(fc_b, fc_a)),
    "A_semantics": ("A arithmetic continuation from the W246-REGISTERED A tail "
                    "559_500+1 = 559_501..561_500 is CLEAN at naive start on the "
                    "post-W246-REGISTERED universe (ninth consecutive seed-gap "
                    "A-continuation face, anticipated by the W246 probe leg4 "
                    "and confirmed live; never transcribe r587); A base = first clean "
                    "window, forward-monotone non-rotational r587 enforced in-walk; "
                    "A base >= prior-wave B tail+1 floor machine-checkable relation"),
    "B_semantics": ("B arithmetic continuation from the W246-REGISTERED B tail "
                    "542_400+1 = 542_401..542_600 is REFUSED by the registered "
                    f"W239 A band 542_501..544_500 -> first-clean {fc_b[0]}..{fc_b[1]} "
                    f"(hops={hops_b}, staircase band-hop face FIRST-MATERIALIZED, "
                    "anticipated by the W246 probe leg4 + the W246 prereg sec.8 "
                    "downstream_seat projection and confirmed live; B base == "
                    "refuser band end 544_500+1 EXACT; the first-clean B window is NOT inside "
                    "the W247 own-wave A window 559_501..561_500 (B_hop "
                    "lands-inside-A=false leg); B_no_ownA_jump=true (fc_b == "
                    "fc_b_naive: the hop refuser is the registered W239 A band, "
                    "not the own-A reservation)"),
    "relation_asserts": {"A_clean_at_naive_start": True,
                          "A_base_ge_priorB_tail_plus1": True,
                          "B_band_hop_expected_face": True,
                          "B_base_above_priorB_tail": True,
                          "AB_mutual_exclusion": True,
                          "B_hop_lands_inside_A": False,
                          "B_no_ownA_jump": True}}
print(f"leg1: A {fc_a} hops={hops_a} (hop chain {[(t['window'], t['jump_to']) for t in a_trace]}) | B {fc_b} hops={hops_b} (refusal trace {[(t['window'], t['jump_to'], t['refuser_bands']) for t in b_trace]}) | naive B {fc_b_naive}")

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

# --- leg 4: W248+ naive projection (pre-W247 universe, honest forward face) ------
pA = (fc_a[1] + 1, fc_a[1] + WIDTH_A)
pB = (fc_b[1] + 1, fc_b[1] + WIDTH_B)
(pA_fc, pA_hops) = first_clean(pA[0], WIDTH_A)
(pB_fc, pB_hops) = first_clean(pB[0], WIDTH_B)
pA_refusers = sorted(p for p in points if pA[0] <= p <= pA[1])
receipt["legs"]["leg4"] = {
    "W248p_A_naive": f"{pA[0]}..{pA[1]}", "W248p_A_first_clean": f"{pA_fc[0]}..{pA_fc[1]}", "hops_A": pA_hops,
    "W248p_A_naive_refusers_seeds": pA_refusers,
    "W248p_B_naive": f"{pB[0]}..{pB[1]}", "W248p_B_first_clean": f"{pB_fc[0]}..{pB_fc[1]}", "hops_B": pB_hops,
    "W248p_B_lands_inside_W248p_A_naive": bool(overlaps(pB, pA)),
    "note": ("W248+ projection on the pre-W247 universe (assuming the W247 seat bands "
             "declared here register verbatim). W248 freezer MUST re-derive on the "
             "post-W247 universe AND reserve the own-wave A window when deriving B "
             "-- never transcribe r587; seed-gap face inherited from W239..W246: "
             "A/B decoupled, re-read the live trace, do NOT assume the staircase "
             "A-base==prior-B-tail+1 equality.")}
print(f"leg4: W248+ naive A {pA[0]}..{pA[1]} refusers {pA_refusers} -> first-clean {pA_fc[0]}..{pA_fc[1]} hops={pA_hops} / naive B {pB[0]}..{pB[1]} -> {pB_fc[0]}..{pB_fc[1]} hops={pB_hops}")

receipt["verdict"] = "ADMIT"
receipt["bands"] = {"A": list(fc_a), "B": list(fc_b),
                    "a_lo": fc_a[0], "a_hi": fc_a[1],
                    "b_lo": fc_b[0], "b_hi": fc_b[1]}
out_path = os.path.join(ROOT, "results", "_w247bma_20261015_probe_receipt.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("PROBE ADMIT receipt written:", out_path)
