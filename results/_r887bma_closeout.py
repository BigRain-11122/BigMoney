# -*- coding: utf-8 -*-
"""r887 bm-a closeout writes: round report line + state file + heartbeat.
Fresh read-modify-write per multi-writer law; utf-8 everywhere."""
import json, time, datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

REPORT_LINE = (
    f"{NOW} | r887 | bm-a | dept:research/engine (perpetual line) | "
    "WM-VERDICT: green (red=false; engine rc0 idle-after-burn: W187 12/12 complete engine-autonomous; "
    "queue 0; supply answered THIS round by W188 pre-seat probe ADMIT + seat published=reserved; "
    "next_pick=moneyflow IC claimed=advisory only panel-source-blocked; py_watermark rc0) | "
    "当前活: W187 finalize one-pass closed + W188 seat reserved | "
    "本轮: W187 burn completed 12/12 engine-autonomous (16:54-17:04) -> pre-finalize three-gate probe GREEN "
    "(r831 half-open: sumA=2000/sumB=200/sum_bt=2200 + perfect half-open tiling + seed sets exact "
    "A 426_204..428_203 / B 428_204..428_403 own-A reserved; receipt _r887bma_w187_prefinalize_probe.json) "
    "-> finalize one-pass EXACT (pre mu -0.0929 sigma 0.2451 K 407,120 + W187 mu -0.0825 sigma 0.2504 K 2,200 "
    "-> merged mu -0.0928 sigma 0.2451 K 409,320; skill_line @n_eff 1.1859->1.1861 K-lift +0.0002; "
    "ledger 816,528+2,200=818,728 chain-linear == published projection EXACT) -> post-verify n1 selftest PASS "
    "incl W187 materializer face + pf 9/9 -> commit d35f59ece pushed; "
    "W188 chain started same-round: pre-seat probe rc0 ADMIT (A 428_404..430_403 staircase FORTY-EIGHTH E36 "
    "hops=1 refused-by-W187-B / B 430_404..430_603 own-A reserved W141 leg2 hops=1; naive A 428_204..430_203 + "
    "naive B 428_404..428_603 refused on live post-W187 universe per MANDATORY re-derive; leg2 zero-conflict + "
    "leg3 origin-vacancy; W189+ proj A 430_404..432_403 / B 430_604..430_803 B-inside-A re-derive-MANDATORY; "
    "178th engine wave bm-a 104th owned claim) + seat MSG published=reserved 943967370; "
    "S6 40/40 rc0 (_r887bma_s6_chain.json; panel cutoff 09-30 -- 10-08 post-holiday bar sina still-not-posted "
    "honest re-probe, self-heal watch; dualrun ZERO-DRIFT streak 51) | "
    "验证: smoke 49/49 + n1/pf selftests PASS + attrition CLEAN + orphan face=0 (py_faces 36) + "
    "four-piece suite green (loop pin=8 no-op/watchdog/claws MATCH) + orders unacked=0 "
    "(ORD 49e9fcd2 / DEC ee70cef0 both UNCHANGED zero group action) | "
    "下轮: W188 buildgen + per-wave prereg freeze + freeze-edits module five-face insertion + tick ignite "
    "(r885/r886 chain machinery, seat reserved on origin); 10-08 sina late-bar absorb on landing "
    "(REGIME_GUARD v3 enforce + live.paper family + marks settle face) | orphan face=0 | dualrun streak 51"
)

# 1) round report append (repo ROOT canonical path per r844 law)
with open("round_reports-bm-a.md", "r", encoding="utf-8") as f:
    rep = f.read()
assert "r887 |" not in rep, "r887 line already present"
if not rep.endswith("\n"):
    rep += "\n"
rep += REPORT_LINE + "\n"
with open("round_reports-bm-a.md", "w", encoding="utf-8", newline="\n") as f:
    f.write(rep)

# 2) state file (bm-a single-writer, fresh read-modify-write)
with open("state-bm-a.json", "r", encoding="utf-8") as f:
    st = json.load(f)
st.update({
    "round_no": 887, "round": 887, "loop_round": 887, "last_round": 887,
    "ts": NOW, "clock_read": NOW, "updated": NOW, "last_seen": NOW,
    "last_run": NOW, "last_round_at": NOW, "last_round_ts": NOW,
    "last_round_closed": NOW,
    "heartbeat_epoch_utc": EPOCH, "last_heartbeat_epoch_utc": EPOCH,
    "current_task": ("W188 chain next (buildgen + per-wave prereg freeze + freeze-edits module "
                     "five-face insertion + tick ignite; seat reserved 943967370); 10-08 sina late-bar "
                     "self-heal watch continues (panel cutoff 09-30)"),
    "did": ("r887: W187 finalize one-pass (burn 12/12 engine-autonomous -> three-gate probe GREEN r831 "
            "half-open -> finalize EXACT ledger 816,528+2,200=818,728 K 409,320 skill_line 1.1859->1.1861 "
            "-> n1 selftest PASS + pf 9/9 -> commit d35f59ece) + W188 pre-seat probe ADMIT + seat "
            "published=reserved (A 428_404..430_403 / B 430_404..430_603; 943967370) + S1 smoke 49/49 + "
            "S6 40/40 rc0 (_r887bma_s6_chain.json; 10-08 sina late-bar still-not-posted honest re-probe "
            "panel cutoff 09-30; dualrun streak 51) + attrition CLEAN + orphan face=0 + "
            "ORD/DEC both UNCHANGED (49e9fcd2/ee70cef0) zero group action"),
    "last_action": "r887 closeout: W187 finalize + W188 seat + S6 chain + state/heartbeat/report writes",
    "last_artifact": ("results/perpetual_faces/n1_w187_results.json (17:10 finalize, ledger 818,728 "
                      "K 409,320) + W188 seat fleet/inbox/MSG-2026-10-08-1717-bma-w188-seat.md "
                      "(probe ADMIT A 428_404..430_403 / B 430_404..430_603)"),
    "latest_artifact": ("results/perpetual_faces/n1_w187_results.json (17:10 finalize, ledger 818,728 "
                        "K 409,320) + W188 seat fleet/inbox/MSG-2026-10-08-1717-bma-w188-seat.md "
                        "(probe ADMIT A 428_404..430_403 / B 430_404..430_603)"),
    "next": ("W188 buildgen + prereg freeze + freeze-edits five-face insertion + tick ignite (r885/r886 "
             "machinery; seat reserved; W189+ proj A 430_404..432_403 / B 430_604..430_803 B-inside-A "
             "re-derive-MANDATORY per W141 leg2) ; 10-08 sina late-bar self-heal watch (on landing = "
             "REGIME_GUARD v3 enforce + live.paper family + marks settle face)"),
    "now_active": ("r887 composite: W187 finalize LANDED (ledger 818,728, K 409,320, skill_line 1.1861) + "
                   "W188 seat published=reserved (943967370); engine queue 0 (W188 buildgen pending next "
                   "window)"),
    "verify": ("W187 three-gate probe GREEN + finalize EXACT (816,528+2,200=818,728 == projection; K "
               "409,320; skill_line +0.0002) + n1 selftest PASS + pf 9/9 + smoke 49/49 + S6 40/40 rc0 + "
               "dualrun streak 51 ZERO-DRIFT + attrition CLEAN + orphan face=0 + four-piece suite green "
               "(loop pin=8 no-op/watchdog/claws MATCH) + orders unacked=0"),
    "last_orders_at": NOW, "last_decisions_at": NOW,
    "last_orders_seen": ("r887: ORD 49e9fcd2 UNCHANGED vs r886; fleet/orders disk dual-scan unacked=0 "
                         "(51 orders all acked); zero new fleet order files since 16:00 window scan"),
    "last_decisions_seen": ("r887: DEC ee70cef0 UNCHANGED vs r886 consumed tip -- zero action; watermark "
                            "keys held (group C real-path fetch + git show raw-bytes canonical)"),
    "idle_rounds": 0, "agenda_starved": False,
})
with open("state-bm-a.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# 3) heartbeat (bm-a-owned file, fresh read-modify-write)
with open("fleet/machines/bm-a.json", "r", encoding="utf-8") as f:
    h = json.load(f)
h.update({
    "last_seen": NOW, "ts": NOW, "clock_read": NOW,
    "heartbeat_epoch_utc": EPOCH, "last_heartbeat_epoch_utc": EPOCH,
    "heartbeat_epoch_utc_type_int": isinstance(EPOCH, int),
    "round_no": 887, "round": 887, "loop_round": 887, "last_round": 887, "last_run": NOW,
    "current_task": ("W188 chain next (buildgen+freeze+ignite; seat reserved 943967370); "
                     "10-08 sina late-bar self-heal watch"),
    "task": ("W188 chain next (buildgen+freeze+ignite; seat reserved 943967370); "
             "10-08 sina late-bar self-heal watch"),
    "current": "W187 finalize LANDED + W188 seat reserved",
    "now_active": "W187 finalize LANDED (ledger 818,728) + W188 seat published=reserved; engine queue 0",
    "last_action": "r887 closeout: W187 finalize + W188 seat + S6 chain + state/heartbeat/report writes",
    "last_artifact": ("results/perpetual_faces/n1_w187_results.json (17:10 finalize, ledger 818,728 "
                      "K 409,320) + W188 seat MSG (probe ADMIT A 428_404..430_403 / B 430_404..430_603)"),
    "latest_artifact": ("results/perpetual_faces/n1_w187_results.json (17:10 finalize, ledger 818,728 "
                        "K 409,320) + W188 seat MSG (probe ADMIT A 428_404..430_403 / B 430_404..430_603)"),
    "next_milestone": ("W188 freeze+ignite (next bm-a window, <=48h; machinery r885/r886 ready); "
                       "10-08 late-bar absorb on sina landing"),
    "verdict": "green",
    "idle_rounds": 0, "agenda_starved": False,
    "orphan_faces": 0, "orphan_killed": 0,
})
with open("fleet/machines/bm-a.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)

# self-verify: epoch int + clock T-sep + report line landed
h2 = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in h2["clock_read"] and "+" in h2["clock_read"], "clock_read must be ISO8601 T-sep"
rep2 = open("round_reports-bm-a.md", encoding="utf-8").read()
assert "r887 | bm-a" in rep2, "report line missing"
st2 = json.load(open("state-bm-a.json", encoding="utf-8"))
assert st2["round_no"] == 887 and isinstance(st2["heartbeat_epoch_utc"], int)
print("CLOSEOUT OK: report r887 line + state round 887 + heartbeat epoch", EPOCH)
