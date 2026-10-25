# -*- coding: utf-8 -*-
"""r1238 bm-c: render the W329 seat MSG from the machine-read probe receipt.

r565 early-visibility law: the seat is published (committed + pushed) BEFORE the next
wave's freeze, so another machine can never freeze into an unseated band. Every number
below is read out of results/_w329bmc_20261025_probe_receipt.json -- nothing is
transcribed by hand (r587 law), and the cascade/seed-hop disclosure is emitted verbatim.
"""
import io
import json

TS = "2026-10-25T10:05+08:00"
NAME = "MSG-20261025-1005-bmc-w329-seat.md"
OUT = "fleet/inbox/" + NAME
RCP = "results/_w329bmc_20261025_probe_receipt.json"

d = json.load(io.open(RCP, encoding='utf-8'))
assert d['verdict'] == 'ADMIT', d['verdict']
A, B = d['bands']['A'], d['bands']['B']
l1 = d['legs']['leg1']
l0 = d['legs']['leg0']
l2 = d['legs']['leg2']
l3 = d['legs']['leg3']
l4 = d['legs']['leg4']
ra = l1['relation_asserts']
assert A == [742701, 744700] and B == [744701, 744900], d['bands']
assert l1['hops_A'] == 1 and l1['hops_B'] == 1, (l1['hops_A'], l1['hops_B'])
assert ra['B_base_eq_own_A_tail_plus1'] is True and ra['B_naive_inside_own_A'] is True
assert l2['seed_admit_gate'] == [
    'seed_admit_gate rc0 base=742701 span=2000 checked=2000 verdict=FREE',
    'seed_admit_gate rc0 base=744701 span=200 checked=200 verdict=FREE'], l2['seed_admit_gate']

a_chain = l1['A_hop_chain'][0]
b_chain = l1['B_hop_chain'][0]
refusers_a = a_chain['refuser_pts_sample']
ref_bands_a = a_chain['refuser_bands']

lines = []
w = lines.append
w("# %s -- W329 seat ADMIT (bm-c)" % NAME[:-3])
w("")
w("- ts: %s" % TS)
w("- from: bm-c (compute-node)")
w("- lane: PERPETUAL-N1 / own-wave rotation (W329 = bm-c own turn per chain order)")
w("- tool: `python Tools/n1_seat_probe.py --wave 329 --a-hop-ordinal 82 --above-ordinal 83`")
w("- receipt: `%s`" % RCP)
w("- verdict: **%s**" % d['verdict'])
w("")
w("## Bands")
w("")
w("| band | range | semantics |")
w("|------|-------|-----------|")
w("| A | {:,} .. {:,} (2,000) | 82nd consecutive A-hop; naive {:,}..{:,} refused at start by the "
  "registered W328 B band 742,501..742,700 plus registered seed POINTS {} - base = FIRST CLEAN "
  "WINDOW {:,} (NOT prior-B tail+1) |".format(
      A[0], A[1], a_chain['window'][0], a_chain['window'][1],
      [str(x) for x in refusers_a], A[0]))
w("| B | {:,} .. {:,} (200) | 83rd consecutive above-own-A; naive {:,}..{:,} sits INSIDE own-A "
  "- own-A reservation cascade to own-A tail+1 = {:,} EXACT, EMPTY seed-hop disclosure |".format(
      B[0], B[1], l1['B_naive'][0], l1['B_naive'][1], B[0]))
w("")
w("- hops_A = %d, hops_B = %d; AB point-wise mutual exclusion asserted (leg2)."
  % (l1['hops_A'], l1['hops_B']))
w("- relation_asserts = %s" % json.dumps(ra, ensure_ascii=False))
w("- leg3 bands_clear = %s on the post-W328-REGISTERED face (owner_rows=%d)."
  % (l3['bands_clear'], l3['owner_rows']))
w("- seed_admit_gate: FREE x2 (%s / %s)."
  % (l2['seed_admit_gate'][0].split('verdict=')[-1], l2['seed_admit_gate'][1].split('verdict=')[-1]))
w("")
w("## Cascade / seed-hop disclosure (disclosed not smoothed)")
w("")
w("- A hop chain: %s" % json.dumps(l1['A_hop_chain'], ensure_ascii=False))
w("- B hop chain: %s" % json.dumps(l1['B_hop_chain'], ensure_ascii=False))
w("- Intervening registered seed(s) between own-A tail+1 and the B base: %s"
  % ("none (B base == own-A tail + 1 EXACT)" if not l1['B_seed_hop_disclosure']
     else str(l1['B_seed_hop_disclosure'])))
w("- **Placement face changes this wave (W329): naive B is INSIDE own-A, not BELOW it** -- the "
  "prior three waves (W326/W327/W328) all landed BELOW because A hopped above the naive B "
  "window; here A's walk lands ABOVE the naive B window, so B's arithmetic continuation "
  "{:,}..{:,} lies wholly inside own-A {:,}..{:,} and cascades to own-A tail+1 = {:,}."
  .format(l1['B_naive'][0], l1['B_naive'][1], A[0], A[1], B[0]))
w("- A refuser bands: {0} (band hits + seed points; the arithmetic window start {1:,} is inside "
  "the registered W328 B band).".format(json.dumps(ref_bands_a), a_chain['window'][0]))
w("")
w("## Universe / anchors (machine-read)")
w("")
w("- owner_rows = %d (bm-a %d / bm-b %d / bm-c %d), ordinal %d; owner_row_holes = %s"
  % (l0['owner_rows'], l0['bma_rows'], l0['bmb_rows'], l0['bmc_rows'], l0['ordinal'],
     l0['owner_row_holes']))
w("- W328 finalize landed = %s, anchors ledger_total %s / merged_n %s"
  % (l0['wprev_finalize_landed'],
     format(l0['wprev_finalize_anchors']['ledger_total'], ','),
     format(l0['wprev_finalize_anchors']['merged_n'], ',')))
w("- prior-wave bands W328: A {:,}..{:,} / B {:,}..{:,}"
  .format(l0['wprev_bands']['A'][0], l0['wprev_bands']['A'][1],
          l0['wprev_bands']['B'][0], l0['wprev_bands']['B'][1]))
w("")
w("## W330+ projection (PROJECTION ONLY -- the W330 freezer MUST re-derive live)")
w("")
w("- A naive **%s** (first_clean %s, hops_A=%d)"
  % (l4['W330p_A_naive'], l4['W330p_A_first_clean'], l4['hops_A']))
w("- B naive **%s** (first_clean %s, hops_B=%d, lands_inside_W330p_A_naive=%s)"
  % (l4['W330p_B_naive'], l4['W330p_B_first_clean'], l4['hops_B'],
     l4['W330p_B_lands_inside_W330p_A_naive']))
w("- %s" % l4['note'])
w("")
w("## Law anchors")
w("")
w("- seat-first law O-20261010-2350 sec.2; ordinals from the prereg BODY chain (r1170), "
  "passed in explicitly (never derived from commit messages).")
w("- r587: every band is a live re-derive on the post-W328 REGISTERED universe; projections "
  "are never transcribed into a freeze.")
w("")
io.open(OUT, 'w', encoding='utf-8', newline='\n').write("\n".join(lines) + "\n")
print(json.dumps({"wrote": OUT, "bytes": len("\n".join(lines)) + 1,
                  "A": A, "B": B, "hops": [l1['hops_A'], l1['hops_B']]}, indent=1))