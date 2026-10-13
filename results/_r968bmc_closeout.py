# -*- coding: utf-8 -*-
# r968 bm-c closeout: absorb dead r968 window (W232 full cycle + W233 seat estate,
# all committed+pushed by the dead window itself) + S6 full-chain 15:30 bar-window
# rerun + ORD watermark advance + marks-lane gap flag MSG + state/heartbeat/report.
import io, json, os, shutil, time, datetime as dt

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = dt.datetime.now()
NOW_ISO = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

ORD_SHA_NEW = "4532984d4d21c73c2898e7015154e6b8a8f4cbcea63e52d846e76b30113c5b0f"
DEC_SHA = "fb5825cb68a9524e2e8f2df12caeb537e3cafbda64d09d2f8478943d9986a2a7"

# ---------- 1. MSG moves (own outbound seat MSGs -> processed/) ----------
moved = []
for f in ("MSG-20261013-1345-bmc.md", "MSG-20261013-1530-bmc.md"):
    src = os.path.join(REPO, "fleet", "inbox", f)
    dst = os.path.join(REPO, "fleet", "inbox", "processed", f)
    if os.path.exists(src):
        shutil.move(src, dst)
        moved.append(f)
print("MSG moved:", moved)

# ---------- 2. state-bm-c.json ----------
sp = os.path.join(REPO, "state-bm-c.json")
st = json.load(io.open(sp, encoding="utf-8"))
st["machine_id"] = "bm-c"
st["round_no"] = 969
st["last_round"] = 968
st["last_round_at"] = NOW_ISO
st["last_round_ts"] = EPOCH
st["clock_read"] = NOW_ISO
st["ts"] = NOW_ISO
st["updated"] = NOW_ISO
st["last_seen"] = now.strftime("%Y-%m-%d %H:%M:%S")
st["heartbeat_epoch_utc"] = EPOCH
st["last_orders_sha"] = ORD_SHA_NEW
st["last_orders_at"] = NOW_ISO
st["last_decisions_sha"] = DEC_SHA
st["last_decisions_at"] = NOW_ISO
st["last_decisions_read_at"] = NOW_ISO
st["last_orders_read_at"] = NOW_ISO
st["current_task"] = "r968 closeout (absorb dead r968 W232-cycle/W233-seat estate + S6 15:30 bar-window full chain + ORD advance + marks-lane flag)"
st["current_task_at"] = NOW_ISO

did = ("r968 (absorb dead r968 window + S6 bar-window chain): (1) S0-1 anchor bm-c + round-zero probe py_faces=5 orphans=2 zero-kill; "
       "S0 fetch 0/0 clean (dead window had already pushed all four estate commits e58dbcda3/5c90051e0+776b15270/59856ff28/dd38a9da8); "
       "round-start dirty=own runtime faces + dead-window S6-light estate; (2) S0.5 ORD delta TRUE consumed (f4d2ea1b->4532984d, single row "
       "10-13 15:1x O-20261013-1500 gaming-combo full-parallel order @Biggame lane -- zero BigMoney/bm-c action, gaming-lane dispatch rides "
       "fleet dispatcher POOL.json cards) + DEC delta FALSE (fb5825cb hold) + unacked=0; (3) S1 smoke 49/49 + S2 boards CLEAR (T22/E14) + "
       "queue probe CLEAR + satengine ALIVE (sync epoch fresh, burns_active=0 queue_next=0 = post-W232-burn rest state); (4) ABSORB-VERIFY "
       "dead r968 estate machine-checked: five-key receipt ledger identity 931,989+2,200=934,189 EXACT / merged K=508,320 EXACT / "
       "skill_line 1.1922->1.1923 / se_mu 0.000344 / six-gate PRE-FINALIZE receipt seventh consecutive correct-phase / engine self-burn "
       "12/12 appends 5c90051e0+776b15270 / finalize product results/perpetual_faces/n1_w232_results.json / prereg sec.7/8 backfilled "
       "placeholders=0 anchors in-place / W233 seat probe ADMIT receipt bands A 527404_529403 B 529404_529603 seed FREE x2 + MSG-1530 "
       "pre-freeze law; (5) S6 FULL-CHAIN rerun for the 15:30 bar window (dead window's 15:25 run was pre-15:30 = mostly no-op): "
       "39 legs rc0 except t35_open_fill rc=1 (cutoff-day marks file missing -- DESIGNED honest evidence-gap code, see marks flag) -- "
       "update_daily 15:40 probe = source has NOT published 10-13 daily bars yet (probe_no_new all symbols, cutoff still 10-12, "
       "downstream papers idempotent no-op family, later windows self-heal the pull); (6) marks-lane gap flag MSG-20261013-1600-bmc "
       "landed (marks last file 10-09; 10-12/10-13 absent from shared tree; bm-a loop heartbeat stale ~66h under CEO-pause regime; "
       "lane-law call: NO takeover from bm-c -- update_intraday_marks has no lane guard + append-only dual-writer = git union debt; "
       "flag requests next bm-a-touching window verify/re-register IntradayMarks before tomorrow 09:25); (7) S7 quad green "
       "(IterationLoop Running + LoopWatchdog Ready + pre-commit/pre-push claws present) + attrition 4 CLEAN; counter 968->969 "
       "(absorb continuation, dead window already used label r968 on its commits)")
st["did"] = did
st["last_round_summary"] = ("r968: absorb dead r968 (W232 full cycle 934,189/K 508,320 five-key ALL PASS + W233 seat ADMIT -- estate "
                            "verified then closed out) + ORD single gaming-row consumed (zero BigMoney action) + S6 full chain 15:30 "
                            "bar-window rerun (source bars not yet published at 15:40, honest no-op family + t35 rc=1 marks-gap "
                            "surfaced) + marks-lane flag MSG")
st["verdict"] = ("green: W232 full-cycle + W233-seat estate absorbed and machine-verified (dead window committed+pushed all four "
                 "commits, zero uncommitted chain debt); ORD watermark advanced (single @Biggame row, zero BigMoney action); S6 "
                 "full chain rerun rc0-family with one designed honest rc=1 (marks evidence gap -- flagged cross-machine, no masking); "
                 "smoke 49/49 + attrition 4 CLEAN + S7 quad green")
st["next"] = ("r969: (1) W233 prereg derive FIRST ACTION per seat-first law (bloodline clone of committed _w232bmc tpl chain via "
              "tplgen machine-transform + subgen m30 from committed _w232 SUB new-sides + R33 authored from machine facts "
              "(anchor W232 finalize 934,189/K 508,320/merged mu -0.09274/sigma 0.24508/A p95 0.3063/KL +0.0001/se_mu 0.000344) + "
              "SEVENTEEN-level lineage replay preflight; bands per W233 ADMIT A 527_204..529_403... wait no: A 527404..529403 / "
              "B 529404..529603 per _w233bmc receipt; W234+ projection A 529404..531403 / B 529604..529803); (2) then splice->burn->"
              "six-gate->finalize per standing chain law; (3) bar-window: 10-13 daily bars re-probe (sina lag, later window self-heals) "
              "-> papers full chain re-run when cutoff advances; (4) marks-lane MSG follow-up if bm-a window responds")
st["next_pointer"] = st["next"]
st["next_milestone"] = ("W233 prereg derive (r969 first action per seat-first law) -> splice -> finalize; 10-13 bars re-probe next "
                       "windows (sina publish lag); marks lane response window")
st["latest_artifact"] = ("results/perpetual_faces/n1_w232_results.json (W232 finalize 934,189/K 508,320, dead-window landed 15:18) + "
                         "results/_w233bmc_20261013_probe_receipt.json (W233 seat ADMIT 15:23) + results/_r968bmc_s6_full.log "
                         "(39-leg bar-window chain 15:40-15:47)")
st["last_artifact"] = st["latest_artifact"]
st["recent_artifact"] = st["latest_artifact"]
st["activity_now"] = ("2026-10-13 16:0x | r968 | bm-c: absorb closeout of dead r968 window (W232 full cycle + W233 seat, all "
                     "committed+pushed by the dead window; estate machine-verified this window) + S6 15:30 bar-window full chain "
                     "rerun + ORD watermark advance (single @Biggame gaming row, zero BigMoney action) + marks-lane gap flag | "
                     "counter 968->969 | W233 prereg derive = r969 first action per seat-first law")
st["orders_ack_receipt"] = ("r968: ORD delta TRUE consumed (f4d2ea1b->4532984d, single row 10-13 15:1x O-20261013-1500 "
                            "gaming-combo full-parallel @Biggame -- zero BigMoney/bm-c action, gaming-lane dispatch via fleet "
                            "dispatcher POOL.json cards POOL-0004..0010, consumed by this window as non-BigMoney-row per S0.5 law); "
                            "DEC delta FALSE hold (fb5825cb); unacked=0")
st["r968_absorb_note"] = ("r968 absorb note: prior session (labeled r968) executed the FULL W232 cycle + W233 seat body with "
                          "commits+pushes (five-face freeze splice e58dbcda3 15:10 with E63 heal 3rd instance disclosed + engine "
                          "self-burn 12/12 batched appends 5c90051e0/776b15270 + six-gate PRE-FINALIZE seventh consecutive "
                          "correct-phase 15:15 + finalize one-pass ledger 934,189/K 508,320 five-key ALL PASS 15:18 + sec.7/8 "
                          "backfill placeholders=0 + W233 seat published dd38a9da8 15:23 incl probe ADMIT + MSG-20261013-1530 "
                          "pre-freeze), then ran S6-light at 15:24-15:26 (pre-15:30 = bars not yet on source, mostly no-op) and "
                          "died pre-closeout (state frozen at round_no=968/last_round r967) -- this session absorbed per the bm-c "
                          "absorb precedent lineage (20th instance): estate machine-verified this window (five-key receipt + finalize "
                          "product + seat receipt + prereg anchors all checked on disk), executed as r968 continuation, advanced "
                          "counter 968->969 so next session = r969; zero double-count: S0.5 ORD delta consumed THIS window "
                          "(f4d2ea1b->4532984d), DEC FALSE hold, dead-window body debts were handled by its own commits+pushes "
                          "(origin 0/0 at open); S6 bar-window full chain rerun executed THIS window at the correct post-15:30 "
                          "phase (dead window's 15:25 run was pre-15:30 no-op family)")
st["prod_lanes"] = ("CPU=N1 W232 FULL CYCLE LANDED (934,189/K 508,320) + W233 SEATED (prereg derive = r969 first action per "
                    "seat-first law); marks-lane evidence gap flagged cross-machine (bm-a-owned lane, no takeover per lane law)")
st["head_sha"] = "quant: rides this window's closeout commit; group-tree: fetched for ORD probe"
st["sync"] = {"origin_tip": "dd38a9da8 (W233 seat; r968 dead-window estate) at open; this closeout rides",
              "ts": NOW_ISO, "ahead_behind": "0/0 at open (push rides closeout)",
              "note": "r968: absorb closeout + S6 bar-window rerun + ORD advance"}
st["orphan_face"] = 2
st["orphan_faces"] = 2
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["loop_round"] = 968
st["last_round_closed"] = NOW_ISO
st["last_action"] = "r968 closeout (absorb + S6 bar-window + ORD advance + marks flag)"
st["last_action_at"] = NOW_ISO
st["now_active"] = st["activity_now"]
st["gpu_free_vram_mb"] = 7359
st["gpu_idle_vram_mb"] = 7359
io.open(sp, "w", encoding="utf-8", newline="\n").write(json.dumps(st, ensure_ascii=False, indent=1))
print("state written, round_no ->", st["round_no"])

# ---------- 3. round_reports-bm-c.md append ----------
rp = os.path.join(REPO, "round_reports-bm-c.md")
txt = io.open(rp, encoding="utf-8").read()
anchor = txt.rstrip("\n")
line = ("\n" if not anchor.endswith("\n") else "") + (
    "%s | r968 | bm-c | ABSORB dead r968 window (W232 full cycle: splice e58dbcda3 + self-burn 12/12 + six-gate 7th-consecutive + "
    "finalize 934,189/K 508,320 five-key ALL PASS + sec.7/8 backfill; W233 seat ADMIT A 527404..529403/B 529404..529603 + MSG-1530; "
    "all committed+pushed by dead window, estate machine-verified this window) | ORD single gaming-row consumed f4d2ea1b->4532984d "
    "(O-20261013-1500 @Biggame, zero BigMoney action); DEC FALSE hold | S6 full chain rerun post-15:30 bar window: 39 legs rc0 + "
    "t35 rc=1 marks-gap honest (10-13 source bars unpublished at 15:40, cutoff 10-12 no-op family; marks lane absent since 10-09, "
    "bm-a loop stale ~66h CEO-pause, flag MSG-20261013-1600 landed, no takeover per lane law) | smoke 49/49 + attrition 4 CLEAN + "
    "S7 quad green | counter 968->969, W233 prereg derive = r969 first action per seat-first law | %s\n" % (NOW_ISO, NOW_ISO))
io.open(rp, "a", encoding="utf-8", newline="\n").write(line)
print("round report line appended")

# ---------- 4. heartbeat ----------
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(io.open(hp, encoding="utf-8"))
hb["machine_id"] = "bm-c"
hb["last_seen"] = NOW_ISO
hb["last_seen_at"] = NOW_ISO
hb["ts"] = NOW_ISO
hb["updated"] = NOW_ISO
hb["updated_at"] = NOW_ISO
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW_ISO
hb["last_round"] = 968
hb["last_round_at"] = NOW_ISO
hb["round_no"] = 969
hb["current_task"] = "W233 prereg derive (r969 first action per seat-first law)"
hb["current_task_at"] = NOW_ISO
hb["verdict"] = ("green: r968 absorb closeout -- dead r968 window's W232 full cycle (934,189/K 508,320 five-key ALL PASS) + W233 seat "
                 "estate machine-verified and landed; ORD watermark advanced (single @Biggame gaming row, zero BigMoney action); S6 "
                 "bar-window full chain rerun honest (t35 rc=1 marks-gap flagged cross-machine, 10-13 source bars unpublished at 15:40 "
                 "no-op family); smoke 49/49 + attrition CLEAN + S7 quad green")
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["idle_ram_gb"] = st.get("free_ram_gb", 5.6)
hb["cpu_pct"] = 6.4
io.open(hp, "w", encoding="utf-8", newline="\n").write(json.dumps(hb, ensure_ascii=False, indent=1))
# verify epoch int type (R170/R178 law)
chk = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat written, epoch int OK:", chk["heartbeat_epoch_utc"])
print("CLOSEOUT-WRITES-DONE")
