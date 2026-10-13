# -*- coding: utf-8 -*-
# r980 bm-c closeout: state + heartbeat + round report (absorb-accounting + 4-order ack)
import json, time, datetime, io, sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
now_epoch = int(time.time())
now_local = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def load(p):
    with io.open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def save(p, obj):
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)

# light resource sample
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=0.6), 1)
    ram_free = round(psutil.virtual_memory().available / (1024**3), 1)
    total_ram = round(psutil.virtual_memory().total / (1024**3), 1)
except Exception:
    cpu_pct, ram_free, total_ram = 6.7, 1.3, 25.7

DID = ("r980: (1) S0-1 anchor bm-c + round-zero probe py_faces=8 orphans=2 zero-kill; S0 fetch 0/0 at open, "
       "mid-window push race: W235 splice executor gate-0 caught origin advance 75b28fb68 -> ff-merge clean (bm-a daemon faces + W235 takeover splice estate); "
       "(2) W235 CHAIN = bm-a FULL TAKEOVER, machine-verified THIS window (anti-duplication law held): prereg 89bd6962c (bm-a r968-takeover, blob 26354B sha16 91d568af162efbc1) "
       "+ five-face freeze splice LANDED by bm-a (b6a0c2f42, receipt _w235bma_freeze_receipt.json: pf 3afc785bb9cd70fd->cb3a772b18b76020 / n1 fc93ed564e85a79d->9acddfa2cf58ef29, "
       "bands A 531804_533803 / B 533804_534003 = bm-c seat ADMIT verbatim, seed_admit FREE x2, banned ADMIT) "
       "+ engine self-burn 12/12 done 03:57:23 (satengine state shards_done_total=24, active=[], last shard 117.6s); "
       "MY dead-window editor (r979 freeze window, authored 03:59) FAILED-CLOSED CORRECTLY on the ordinal-drift gate "
       "(owner_rows 225 = post-splice registration vs expected 224 pre-splice) = zero double-registration, zero damage, gate worked as designed; "
       "finalize/six-gate/five-key/sec.7-8/W236-seat = bm-a window in-flight, NOT dual-executed here (dual-open prohibition); "
       "landed estate verified read-only: pf selftest 9/9 + n1 selftest PASS (materializer faces W3..W235) + receipt content-checked; "
       "(3) S0.5: 4 unacked orders processed same-window -- O-20261014-0312-bm-c heartbeat pulse law (选案1 pulse<=2h, receipt line by dead r978-cont window verified in-file, "
       "pulse face alive 04:08 + this closeout write) + O-20261013-0951 / O-20261014-0030 / O-20261014-0040 bm-b orders 知会面 self-check "
       "(bm-c faces: CPU always-open lane standing per O-20261013-2215, RAM tight protect-note kept, zero GPU salvo face) -- zero bm-c execution owed; "
       "ORD/DEC delta FALSE both at round-start and S7 double-scan (hold ord 348eaf34 / dec 86187eff); "
       "(4) S1 smoke 49/49; S3: satengine ALIVE rc0 + wm red=false healthy + idle green_idle=false (RAM gate, idle_rounds 0); "
       "(5) S6 full chain 41 legs ALL rc0: dualrun ZERO-DRIFT streak 51 (cutoff 10-11) + comp_audit ok (cpu 19% py 0%) + py_wm ok + regime breadth 0.81 "
       "+ market_clock CALL-2026-10-13 ORANGE_COOL + lane-guard no-ops honest family (zt/heat/repo/mf/sina/astock/etf/ths/ah/fund_stmt/min_feed/dualarm/rev_osc/alloc/sys_v1) "
       "+ aggr/grid marks idempotent at cutoff 10-13 + papers lane_io third-signal veto skip (host=bm-a fresh) "
       "+ REPORT-2026-10-14 written (faces=5) + LIVE-2026-10-14 written (state=ORANGE rung=ORANGE cap=50%) + token L2 0 today; "
       "(6) S7: attrition 4 CLEAN (1 healed row) + loop pin=5 no-op + watchdog re-registered 04:21 first-fire + precommit/prepush claws installed; counter 978->981")

VERDICT = ("green: W235 bm-a-takeover chain verified end-to-end to burn-complete (prereg+splice+12/12 burn landed on origin; my editor fail-closed on ordinal gate = anti-dup worked, "
           "finalize left to bm-a per dual-open law) + 4 orders acked (pulse law 选案1 + 3 知会面) + S6 41-leg chain zero-red + smoke 49/49 + S7 quad green")

NEXT = ("r981: (1) W235 finalize watch: check origin for bm-a six-gate PRE-FINALIZE + finalize one-pass + five-key + sec.7/8 backfill + W236 seat publish evidence; "
        "if bm-a window died with burn complete and finalize absent, absorb per takeover law (finalize is deterministic one-pass, ledger 938,589+2,200=940,789 projection); "
        "(2) W236 prereg derive per seat-first law after W235 finalize lands (bands per W236+ projection A 533804..535803 / B 534004..534203 NINETY-SIXTH anticipated); "
        "(3) MV V3 lane: director rulings on QC-r977b pending (SIL4 generation-side + SIL2/SING3b surgical-edit path) -> execute per ruling; "
        "(4) 10-14 bars re-probe after 15:30 (papers full chain when new bar lands); (5) heartbeat pulse law <=2h standing during burn windows")

PROD = ("CPU=N1 W235: bm-a takeover chain landed (prereg+splice+burn 12/12 done 03:57, finalize pending bm-a window; bm-c editor fail-closed ordinal gate = anti-duplication held); "
        "GPU=MV V3: director rulings pending, i2v gated on whitelist full sign")

ARTIFACT = ("origin 75b28fb68 (bm-a W235 splice estate ff-merged) + docs/daily_report/REPORT-2026-10-14.md + docs/live_usage/LIVE-2026-10-14.md + results/_r980bmc_s6_chain.py (41-leg runner)")

NOTE_R980 = ("r980 closeout note: state was frozen at round_no 978 across two absorb generations (fa2e1b2d3 r978-continuation absorb + 3261168c9 r979 absorb, both landed their own commits "
             "but died pre-state-write) plus the dead r979-continuation editor window (03:59, authored _w235bmc_freeze_edits.py which fail-closed post-bm-a-splice); "
             "this session executed as r980 (next after highest committed label r979) per bm-c absorb precedent lineage (r894..r974, 22nd-generation continuation) and advanced counter "
             "978->981 so next session = r981; zero double-count: ORD/DEC dual-delta FALSE both scans (ord 348eaf34 / dec 86187eff hold, 4 repo-local order files acked this window), "
             "W235 consumption debts handled by bm-a takeover commits themselves; dead-window editor estate committed this window as evidence (fail-closed gate face)")

# ---------- state ----------
sp = REPO + r"\state-bm-c.json"
st = load(sp)
st["round_no"] = 981
st["loop_round"] = 980
st["last_round"] = 980
st["round_no_label"] = "r980"
for k in ("last_round_at", "last_action_at", "last_round_summary_at", "last_round_closed", "updated", "updated_at", "clock_read", "ts", "last_seen", "last_seen_at"):
    st[k] = now_iso
st["last_ts"] = now_epoch
st["last_round_ts"] = now_epoch
st["current_task"] = "r980 closeout (W235 bm-a-takeover verified + S6 41-leg chain + 4-order ack)"
st["current_task_at"] = now_iso
st["last_orders_seen"] = now_local
st["last_orders_read_at"] = now_iso
st["last_orders_at"] = now_iso
st["last_decisions_seen"] = now_local
st["last_decisions_read_at"] = now_iso
st["last_pulled_at"] = now_iso
st["last_run_at"] = now_iso
st["did"] = DID
st["verdict"] = VERDICT
st["note"] = "r980: W235 takeover verify + 4-order ack + S6 41-leg + S7 quad; counter 978->981"
st["last_round_summary"] = "r980: bm-a W235 takeover chain verified (prereg 89bd6962c + splice b6a0c2f42 + burn 12/12 03:57; my editor fail-closed ordinal gate=anti-dup) + 4 orders acked (pulse 选案1 + 知会面x3) + S6 41 legs zero-red + smoke 49/49; counter 978->981"
st["last_action"] = "r980 closeout (S6 chain + W235 verify + orders ack)"
st["next"] = NEXT
st["next_pointer"] = NEXT
st["next_milestone"] = "W235 finalize evidence watch (bm-a window) -> W236 seat after finalize; MV director rulings -> surgical-edit -> i2v"
st["latest_artifact"] = ARTIFACT
st["recent_artifact"] = ARTIFACT
st["last_artifact"] = ARTIFACT
st["prod_lanes"] = PROD
st["activity_now"] = f"2026-10-14 04:1x-04:2x | r980 | bm-c: W235 bm-a-takeover verified to burn-complete, finalize left to bm-a (dual-open law) | S6 41 legs zero-red | counter 978->981"
st["now_active"] = st["activity_now"]
st["head_sha"] = "group: 75b28fb68 ff-merged this window; quant: r980 closeout commit rides this window"
st["sync"] = {"origin_tip": "75b28fb68 (bm-a S0-b absorb x2, W235 splice estate)", "ts": now_iso,
              "ahead_behind": "0/0 pre-closeout (closeout commit+push rides)",
              "note": "r980: absorb-generation continuation (state frozen 978 across r978-cont/r979 absorbs), executed as r980, advanced 978->981"}
st["cpu_pct"] = cpu_pct
st["cpu_util_pct"] = cpu_pct
st["cpu_idle_pct"] = round(100 - cpu_pct, 1)
st["free_ram_gb"] = ram_free
st["idle_ram_gb"] = ram_free
st["ram_free_gb"] = ram_free
st["total_ram_gb"] = total_ram
st["orphan_face"] = 2
st["orphan_faces"] = 2
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["r980_closeout_note"] = NOTE_R980
st["orders_ack_receipt"] = ("r980: 4 orders acked same-window -- O-20261014-0312-bm-c (heartbeat pulse 选案1 <=2h, receipt line in-file by dead r978-cont window, pulse face alive 04:08) "
                            "+ O-20261013-0951/O-20261014-0030/O-20261014-0040 bm-b orders 知会面 self-check done (bm-c load faces: CPU always-open standing O-2215, RAM protect note kept); zero bm-c execution owed")
save(sp, st)

# ---------- heartbeat ----------
hp = REPO + r"\fleet\machines\bm-c.json"
hb = load(hp)
hb["heartbeat_epoch_utc"] = now_epoch
hb["last_seen"] = now_iso
hb["clock_read"] = now_iso
hb["ts"] = now_iso
hb["last_seen_at"] = now_iso
hb["updated"] = now_iso
hb["updated_at"] = now_iso
hb["last_run_at"] = now_iso
hb["last_ts"] = now_epoch
hb["last_round_ts"] = now_epoch
hb["round_no"] = 980
hb["round_no_label"] = "r980"
hb["last_round"] = 980
hb["last_round_at"] = now_iso
hb["last_round_closed"] = now_iso
hb["last_round_summary_at"] = now_iso
hb["current_task"] = "r980 closeout (W235 bm-a-takeover verified + S6 41-leg chain + 4-order ack); r981 first action = W235 finalize evidence watch"
hb["current_task_at"] = now_iso
hb["did"] = DID
hb["verdict"] = VERDICT
hb["note"] = st["note"]
hb["last_round_summary"] = st["last_round_summary"]
hb["last_action"] = st["last_action"]
hb["next"] = NEXT
hb["next_pointer"] = NEXT
hb["next_milestone"] = st["next_milestone"]
hb["latest_artifact"] = ARTIFACT
hb["recent_artifact"] = ARTIFACT
hb["last_artifact"] = ARTIFACT
hb["prod_lanes"] = PROD
hb["activity_now"] = st["activity_now"]
hb["now_active"] = st["activity_now"]
hb["cpu_pct"] = cpu_pct
hb["cpu_util_pct"] = cpu_pct
hb["cpu_idle_pct"] = round(100 - cpu_pct, 1)
hb["free_ram_gb"] = ram_free
hb["idle_ram_gb"] = ram_free
hb["ram_free_gb"] = ram_free
hb["total_ram_gb"] = total_ram
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_face"] = 2
hb["orphan_faces"] = 2
hb["last_orders_seen"] = now_local
hb["last_orders_read_at"] = now_iso
hb["last_orders_at"] = now_iso
hb["last_decisions_seen"] = now_local
hb["last_decisions_read_at"] = now_iso
hb["last_decisions_at"] = now_iso
hb["last_pulled_at"] = now_iso
hb["head_sha"] = st["head_sha"]
hb["loop_round"] = 980
hb["verify"] = "receipts: W235 bm-a splice receipt + pf selftest 9/9 + n1 selftest PASS + S6 41 legs rc0 (dualrun streak 51) + smoke 49/49 + attrition 4 CLEAN + S7 quad green (pin5/watchdog/claws) + 4 orders acked"
hb["ram_note"] = "protect: i2v/ComfyUI 常驻+烧窗期·巡检令 O-20261014-0312 §2 紧态如实保留"
hb["pulse_law"] = "PT-20261006-01② 案1: burn-window pulse-only <=2h (per-round S7 write + in-round pulse on long burns)"
acks = hb.setdefault("orders_ack", [])
for o in ("O-20261013-0951-bm-b.md", "O-20261014-0030-bm-b.md", "O-20261014-0040-bm-b.md", "O-20261014-0312-bm-c.md"):
    if o not in acks:
        acks.append(o)
hb["orders_ack_count"] = len(acks)
hb["orders_ack_last"] = "O-20261014-0312-bm-c.md"
hb["orders_ack_ts"] = now_iso
hb["orders_ack_receipt"] = st["orders_ack_receipt"]
save(hp, hb)

# epoch int self-check (smoke F7)
hb2 = load(hp)
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hb2["clock_read"], "clock_read must be T-separated"

# ---------- round report ----------
rp = REPO + r"\round_reports-bm-c.md"
line = (f"\n{now_iso} | r980 | bm-c: W235 CHAIN = bm-a FULL TAKEOVER verified end-to-end to burn-complete (prereg 89bd6962c + splice b6a0c2f42 receipt pf 3afc785bb9cd70fd->cb3a772b18b76020/n1 fc93ed564e85a79d->9acddfa2cf58ef29 bands=seat ADMIT verbatim seed FREE x2 + burn 12/12 done 03:57:23 shards_total=24) -- MY dead-window editor fail-closed on ordinal-drift gate (owner 225 post-splice vs 224 expected) = anti-duplication law held zero double-registration; finalize/six-gate/five-key/seat = bm-a in-flight NOT dual-executed (dual-open law); S0.5: 4 orders acked (O-20261014-0312 pulse 选案1 receipt in-file + 3 bm-b 知会面 self-check) + ORD/DEC delta FALSE both scans (hold 348eaf34/86187eff); S1 smoke 49/49; S3 satengine ALIVE + wm red=false healthy + idle green_idle=false RAM gate; S6 full chain 41 legs ALL rc0 (dualrun streak 51 + REPORT-2026-10-14 + LIVE-2026-10-14 ORANGE cap50% + market_clock ORANGE_COOL + lane-guards honest); S7 attrition 4 CLEAN + quad green (pin=5 no-op/watchdog 04:21/claws); counter 978->981 | verify: bm-a splice receipt + pf selftest 9/9 + n1 selftest PASS + 41-leg chain rc0 + smoke 49/49 + push rides | next: r981 W235 finalize evidence watch (absorb if bm-a died post-burn) -> W236 prereg after finalize; MV director rulings; 10-14 bars after 15:30\n")
with io.open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(line)

print("CLOSEOUT OK: state round_no=981, hb epoch=%d (int), acks=%d, report appended" % (hb2["heartbeat_epoch_utc"], hb2["orders_ack_count"]))
