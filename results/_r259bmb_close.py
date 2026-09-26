import json
import time

# --- round report append (CRLF file, mirror one-line format) ---
RR = "logs/iteration-loop/round_reports.md"
raw = open(RR, "rb").read()
assert raw[:3] != b"\xef\xbb\xbf" and b"\r\n" in raw
line = (
    "2026-09-26 16:2x | r259 bm-b | dept:portfolio+research+engineering | "
    "WM-VERDICT: GREEN py_low_board_clear (probe 16:13 py 0.0% window n=2, "
    "board 0 open / pool 0 ready; red=false; audit FLAG:pool_starvation 61min "
    "span -- supply chain honest: capacity face DELIVERED this round + "
    "deep-axis face awaits T-82 transfer branch arrival) | did: S0 fetch "
    "up-to-date at round start (bm-a r255 close landed mid-round, rebase "
    "clean); S0.5 double-scan orders 82/82 zero un-acked + decisions.md "
    "absent at cph4 path zero-action; MAIN DELIVERY = T-80 slice-4 capacity "
    "face FULL ARC AGGR-CAPACITY-FACE-P1: F-04 MSG-1605 first, prereg frozen "
    "commit 70f71091 PRE-RUN (R99), runner scripts/aggr_capacity_probe.py "
    "(267 dedup units = frozen battery weights_representative verbatim, "
    "census gates 291/267 fail-closed, caliber manifest 29/29 sha R253 "
    "double door, selftest 8/8 incl tier-sum==num_entries identity + "
    "known-refusal matrix + determinism + scale boundary + core48 smoke), "
    "RUN 267/267 units 37.6s 12w labels 9 unconstrained / 11 constrained "
    "(ALL constrained = concentrated CE-sleeve weights: CONC-TOP2 24 caps "
    "2.72% .. TOP2-MON 3 caps 0.03%; dropped_zero_adv=0 missing_adv=0 all "
    "20, core48 shares calendar); structural location inference honestly "
    "labeled (counters have no date granularity): only 513520 2020-2022 "
    "cap1pct 37-64k below max CE demand 95k; products: p1_results.json "
    "evidence_cutoff 2026-09-24 top-level + attrition append-only row "
    "cells_ledger_delta=0 (ledger 186592 untouched, disclosure-leg precedent) "
    "+ battery product BYTE-FROZEN untouched + prereg s7/s8 backfilled "
    "(prediction 4/5 hit, missing-ADV overpredicted honest, zero fabricated "
    "busywork per O-1137); S7 push hit bm-a r255 close window = pull --rebase "
    "clean replay x2 + stash-pop watchdog race resolved take-ours R252 "
    "recipe zero loss; S6 28 legs exit 0 weekend no-ops (cutoff 09-24: "
    "live.paper/t35/t24pros bar-conditional legs legally skipped; regime "
    "ORANGE d2 shadow; clock ORANGE_COOL sleeves=4 activated=0; "
    "fundamental 19.1h fresh skip; b_layer green; scorecard 6 traders; "
    "daily_report faces=4 token=1; build_status refreshed; token L1 delta "
    "-48); smoke 25/25 | evidence: results/aggr_capacity_face/p1_results.json "
    "+ freeze commit 70f71091 + run commit fcee9267 + T-80 progress_r259 + "
    "gate_attrition AGGR-CAPACITY-FACE-P1 row + S6 28 exit-0 chain + state "
    "258->259 | next: T-82 transfer branch transfer/t80-deep-bcd-basis "
    "arrival = byte-verify + row-multiset semantic compare (bm-a accepted "
    "MSG-1556 offer, dD LF-normalize face R257 law); canon B_MAXDIV "
    "deep-axis member capacity = separate bm-a lane face; T-81 slice-4 "
    "hooks live; 09-28 Monday new bar full chain; 10-01 month boundary + "
    "REGIME_GUARD v3 activation window"
)
with open(RR, "ab") as fh:
    fh.write(line.encode("utf-8") + b"\r\n")
print("round report appended")

# --- state.json round_no 258 -> 259 (mirror field set, LF, no BOM) ---
SP = "logs/iteration-loop/state.json"
raw = open(SP, "rb").read()
assert raw[:3] != b"\xef\xbb\xbf" and b"\r\n" not in raw
d = json.loads(raw.decode("utf-8"))
assert d.get("round_no") == 258, d.get("round_no")
now = time.strftime("%Y-%m-%d %H:%M:%S")
short = now[:16]
d["round_no"] = 259
d["did"] = ("r259: T-80 slice-4 capacity face FULL ARC AGGR-CAPACITY-FACE-P1 "
            "(prereg frozen pre-run + runner selftest 8/8 + RUN 267/267 "
            "37.6s: 9 unconstrained / 11 constrained, all constrained = "
            "concentrated CE-sleeve weights; dropped/missing all zero; "
            "attrition row cells_ledger_delta=0; battery byte-frozen) + "
            "S6 28 legs exit 0 weekend no-ops + rebase-clean push")
d["verdict"] = "GREEN"
d["next"] = ("R260+: T-82 transfer branch arrival byte-verify + semantic "
             "compare (bm-a accepted) + canon B_MAXDIV deep-axis capacity = "
             "bm-a lane + T-81 slice-4 hooks live + 09-28 new-bar chain + "
             "10-01 month trio + REGIME_GUARD v3")
d["last_round_ts"] = int(time.time())
d["last_result"] = "ok"
d["ts"] = now
d["updated_at"] = short
d["last_round_at"] = now[:16]
with open(SP, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
print("state round_no ->", d["round_no"], "| last_round_ts int:",
      isinstance(d["last_round_ts"], int))
