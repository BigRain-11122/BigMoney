# -*- coding: utf-8 -*-
"""r889 bm-a closeout: round report line + state + heartbeat writes.
Canonical paths per r844 law (report = repo ROOT round_reports-bm-a.md)."""
import json, time, datetime, hashlib, subprocess

NOW = datetime.datetime.now().astimezone()
ISO = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# --- final ORD watermark (re-verify + consume-zero-move assert) ---
repo_g = r'C:/Users/sjs20/Desktop/FluxGroup'
_r = subprocess.run(['git', '-C', repo_g, 'show', 'origin/main:docs/orders.md'],
                    capture_output=True)
ORD_SHA = hashlib.sha256(_r.stdout).hexdigest()
ORD_BYTES = len(_r.stdout)
assert ORD_SHA.startswith('2a5ec5a3975f6157'), 'ORD moved again: ' + ORD_SHA[:16]
DEC_SHA = 'ee70cef0f4a5e3b8db4c67936ce2a2aeee222fff8d03f33339b390eac814ac8c'

# --- 1) round report line (repo ROOT, append-only) ---
RPT = (
    "2026-10-08T" + NOW.strftime("%H:%M:%S") + "+08:00 | r889 | bm-a | "
    "dept:research/engine (perpetual line+MV viewing gate) | "
    "WM-VERDICT: green (red=false lane=healthy; engine rc0 idle-after-burn "
    "W188 12/12 complete 18:19 queue 0; idle_trigger vram 2.68GB < 6GB "
    "threshold not-green-idle honest note, real work done; next_pick="
    "moneyflow IC claimed=advisory only panel-source-blocked) | "
    "当前活: W188 finalize one-pass closed + MV outbound gate-check + "
    "CEO presentation | "
    "本轮: W188 burn 12/12 engine-autonomous (18:06-18:19) -> pre-finalize "
    "three-gate probe GREEN (r831 half-open: sumA=2000/sumB=200/sum_bt=2200 "
    "+ perfect half-open tiling + seed sets exact 428_404..430_403 A "
    "staircase FORTY-EIGHTH E36 / 430_404..430_603 B own-A reserved W141 "
    "leg2; receipt _r889bma_w188_prefinalize_probe.json) -> finalize "
    "one-pass EXACT (pre-W188 mu -0.0928 sigma 0.2451 K 409,320 + W188 mu "
    "-0.0986 sigma 0.2450 K 2,200 -> merged mu -0.0929 sigma 0.2451 K "
    "411,520; skill_line @n_eff 818,728 K-lift +0.0000; ledger "
    "818,728+2,200=820,928 chain-linear == published projection EXACT) -> "
    "post-verify n1 selftest PASS incl W188 materializer face + pf 9/9 -> "
    "commit 0061ab8c7 pushed (first push blocked by pre-push claw "
    "LIVE-REMOTE stale-base false-deletion Tools/_r770bmc_style_iter2.py "
    "r653 family vs bm-c r770 ae4f55eec mid-window origin advance -> "
    "checkout daemon-churned live-wins faces per r642 net-tree law -> "
    "fetch+rebase clean zero-UU -> push green) + ORD 2f765750->2a5ec5a3 "
    "delta consumed (rows 308-313: 308 bm-c silence-suite receipt-only / "
    "309+312 MV order-22/23 outbound DELIVERED by bm-c r770 18:2x -> bm-a "
    "frame-level multimodal gate-check 5/5 executed verdict 0/5 pass "
    "strict frame gate: goddess teal-robe vs 白衣 brief + sweet bloom + "
    "zero Babylon anchoring / glass center split-line diptych-not-overlay "
    "+ right figure reads male / carve atmosphere best-in-package but "
    "tablet text smudge honest FAIL confirm (in-video viable only 0.5-2s "
    "quick-cut+grain, no freeze close-up) / library x THREE Victorian "
    "lamps confirmed + second-era unreadable beat / library y ankh hard "
    "error + figure collision -> presented to CEO with full absolute "
    "paths + bm-c 3-option menu (A local composite iterate / B cloud "
    "channel / C CEO redirect); video stays frozen per O-1820 awaiting "
    "CEO pick) / 310 U060 direct-solve executed prior window receipt / "
    "311 software-copyright naming Biggame domain zero-BigMoney-action / "
    "313 U060-8 codely-burst WT containment executed prior window "
    "receipt-only) + DEC ee70cef0 unchanged zero group action | "
    "验证: smoke 49/49 + n1/pf selftests PASS + attrition CLEAN (4 ledger "
    "files) + orphan face=0 (py_faces 37) + four-piece suite green (loop "
    "pin=8 no-op / watchdog registered next 18:36 / claws in-use verified "
    "pre-commit+pre-push) + S6 39/39 rc0 (_r889bma_s6_chain.json; new_bar="
    "False sina late-bar watch panel cutoff 09-30; dualrun streak "
    "continued) + orders unacked=0 (local 51/51 acked) | "
    "下轮: W189 chain (prereg buildgen + freeze-edits five-face insertion "
    "+ tick ignite; seat 744de26ef on origin; A 430_604..432_603 / B "
    "432_604..432_803; W190+ re-derive-MANDATORY per W141 leg2) + sina "
    "late-bar absorb watch (panel cutoff 09-30) + CEO MV direction watch "
    "(A/B/C menu awaiting pick) [via bm-a r889]"
)
with open("round_reports-bm-a.md", "a", encoding="utf-8") as f:
    f.write("\n" + RPT + "\n")

# --- 2) state file ---
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st.update({
    "round_no": 889, "round": 889, "last_round": 889, "loop_round": 889,
    "clock_read": ISO, "ts": ISO, "updated": ISO, "last_run": ISO,
    "last_seen": ISO, "last_round_at": ISO, "last_round_ts": ISO,
    "last_round_closed": ISO, "last_round_at_": ISO,
    "heartbeat_epoch_utc": EPOCH, "last_heartbeat_epoch_utc": EPOCH,
    "idle_rounds": 0, "agenda_starved": False,
    "current": "r889 closeout: W188 finalize landed (0061ab8c7) + MV "
               "outbound gate-checked + CEO presented; engine idle queue 0",
    "now_active": "r889: W188 finalize one-pass EXACT landed (K 411,520 / "
                  "ledger 820,928 == projection) + MV outbound 5-image "
                  "frame-level gate-check -> CEO presented; engine idle "
                  "queue 0; W189 chain next",
    "task": "W189 chain (prereg buildgen + freeze-edits five-face "
            "insertion + tick ignite; seat 744de26ef; A 430_604..432_603 "
            "/ B 432_604..432_803; W190+ re-derive-MANDATORY per W141 "
            "leg2) + sina late-bar absorb watch + CEO MV direction watch",
    "current_task": "W189 chain next window (prereg buildgen + freeze-edits "
                    "+ tick ignite; proj ledger 820,928+2,200=823,128 / K "
                    "411,520+2,200=413,720); 10-08 sina late-bar self-heal "
                    "watch (panel cutoff 09-30); CEO MV A/B/C menu watch",
    "did": "r889: W188 burn 12/12 engine-autonomous complete (18:06-18:19) "
           "-> pre-finalize three-gate probe GREEN (r831 half-open, receipt "
           "_r889bma_w188_prefinalize_probe.json) -> finalize one-pass "
           "EXACT (merged mu -0.0929 sigma 0.2451 K 411,520; ledger "
           "818,728+2,200=820,928 == projection) -> n1 selftest PASS incl "
           "W188 materializer face + pf 9/9 -> commit 0061ab8c7 pushed "
           "(pre-push claw stale-base false-deletion vs bm-c r770 "
           "mid-window advance -> rebase clean -> green) + S6 39/39 rc0 "
           "(new_bar=False sina watch; _r889bma_s6_chain.json) + attrition "
           "CLEAN + orphan 0 + MV outbound (bm-c r770 delivery) "
           "frame-level multimodal gate-check 5/5: verdict 0/5 pass "
           "strict frame gate (teal robe / split-line diptych / tablet "
           "smudge / 3 Victorian lamps / ankh) -> CEO presented with "
           "paths + 3-option menu, video frozen per O-1820 + ORD "
           "2a5ec5a3 rows 308-313 consumed + DEC ee70cef0 unchanged",
    "last_action": "r889 closeout: W188 finalize + MV gate-check/present + "
                   "S6 chain + state/heartbeat/report writes",
    "last_artifact": "results/perpetual_faces/n1_w188_results.json (K "
                     "411,520, ledger 820,928) + "
                     "results/_r889bma_w188_prefinalize_probe.json + "
                     "results/_r889bma_s6_chain.json + CEO MV presentation "
                     "(C:/Users/sjs20/Desktop/FluxGroup/fleet/"
                     "mv0001-handover/outbound/ 5-image gate-check)",
    "latest_artifact": "results/perpetual_faces/n1_w188_results.json (K "
                       "411,520, ledger 820,928 == projection EXACT) + "
                       "MV outbound frame-level gate-check verdicts "
                       "presented to CEO",
    "next": "W189 chain (prereg buildgen + freeze-edits five-face insertion "
            "+ tick ignite; seat 744de26ef on origin; A 430_604..432_603 / "
            "B 432_604..432_803; W190+ proj A 432_604..434_603 / B "
            "432_804..433_003 re-derive-MANDATORY) + 10-08 sina late-bar "
            "absorb on landing (REGIME_GUARD v3 enforce + live.paper "
            "family + marks settle face) + CEO MV direction watch (A/B/C "
            "menu; video frozen until pick)",
    "verify": "W188 finalize EXACT (K 411,520 / ledger 820,928 == published "
              "projection) + n1 selftest PASS incl W188 materializer face "
              "+ pf 9/9 + smoke 49/49 + S6 39/39 rc0 (new_bar=False sina "
              "watch) + attrition CLEAN + orphan face=0 (py_faces 37) + "
              "four-piece suite green (loop pin=8 / watchdog / claws "
              "in-use) + ORD 2a5ec5a3 consumed rows 308-313 + DEC ee70cef0 "
              "unchanged + orders unacked=0",
    "last_orders_sha": ORD_SHA,
    "last_orders_at": ISO,
    "last_orders_seen": "r889: ORD 2f765750 -> 2a5ec5a3 delta consumed "
                        "(rows 308-313: 308 bm-c silence receipt-only; "
                        "309+312 MV order-22/23 outbound DELIVERED bm-c "
                        "r770 -> bm-a frame-level gate-check 0/5 strict + "
                        "CEO presented, video frozen; 310 U060 executed "
                        "receipt; 311 Biggame zero-action; 313 U060-8 WT "
                        "containment receipt-only)",
    "last_decisions_sha": DEC_SHA,
    "last_decisions_at": ISO,
    "last_decisions_seen": "r889: DEC ee70cef0 UNCHANGED vs r888 consumed "
                           "tip -- zero action; watermark keys held (group "
                           "C real-path fetch + git show raw-bytes canonical)",
    "last_decisions_src": "group origin/main via C: real-path fetch + git "
                          "show (C:/Users/sjs20/Desktop/FluxGroup; python "
                          "subprocess raw-bytes canonical path, zero PS pipe)",
    "last_decisions_ts": ISO,
})
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- 3) heartbeat ---
hp = "fleet/machines/bm-a.json"
hb = json.load(open(hp, encoding="utf-8"))
hb.update({
    "machine_id": "bm-a",
    "last_seen": ISO, "ts": ISO, "clock_read": ISO,
    "heartbeat_epoch_utc": EPOCH,
    "last_heartbeat_epoch_utc": EPOCH,
    "heartbeat_epoch_utc_type_int": isinstance(EPOCH, int),
    "idle_rounds": 0, "agenda_starved": False,
    "verdict": "green",
    "round_no": 889, "last_round": 889, "loop_round": 889,
    "last_run": ISO,
    "current": "r889: W188 finalize landed (0061ab8c7) + MV outbound "
               "gate-checked + CEO presented; engine idle queue 0",
    "current_task": "W189 chain next window (prereg buildgen + freeze-edits "
                    "+ tick ignite; proj ledger 823,128 / K 413,720); sina "
                    "late-bar watch; CEO MV A/B/C menu watch",
    "last_action": "r889 closeout: W188 finalize + MV gate-check/present + "
                   "S6 39/39 + state/heartbeat/report writes",
    "last_artifact": "results/perpetual_faces/n1_w188_results.json (K "
                     "411,520 ledger 820,928) + _r889bma_w188_prefinalize_"
                     "probe.json + _r889bma_s6_chain.json",
    "latest_artifact": "results/perpetual_faces/n1_w188_results.json",
    "next_milestone": "W189 chain freeze+ignite next bm-a window; 10-08 "
                      "sina late-bar absorb on landing; CEO MV A/B/C pick "
                      "gate (video frozen until pick)",
    "last_orders_sha": ORD_SHA,
    "last_decisions_sha": DEC_SHA,
    "orphan_faces": 0,
})
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# self-assert: epoch int + T-sep clock (R170/R178/R262 laws)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock not T-sep ISO"
print("closeout writes OK; epoch:", EPOCH, "clock:", ISO)
print("report line appended; ORD sha:", ORD_SHA[:16], ORD_BYTES, "bytes")
