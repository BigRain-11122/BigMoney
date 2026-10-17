# -*- coding: utf-8 -*-
# r1044 bm-a closeout: round report + heartbeat + state (single-writer python, r985 full-rewrite law)
import io, json, time, re

NOW = "2026-10-18T02:52:30+08:00"
EPOCH = int(time.time())
REP = "round_reports-bm-a.md"
HB = "fleet/machines/bm-a.json"
ST = "state-bm-a.json"

did = ("r1044: S0 absorb+rebase (runtime faces + dead 00:0x post_review estate +50/REPORT-20261018.md; "
       "watermark_red UU newer-wins r1028 recipe; behind-0) + O-20261018-0137 机队误关事故恢复令 receipted "
       "(receipt watch state: bm-b revived heartbeat 02:26:54 r998 in-flight carrying O-0137 recovery receipt; "
       "bm-c revived 01:38 W265 prereg ARMED per dispatcher R14 02:3x evidence; bm-a takeover condition NOT met, "
       "zero skip-claim, watch-only, close account after both taskaudit receipts verified) + "
       "MSG-2356 drama redrop PROCESSED: 5-file taildrop pickup DONE — found via Downloads GUI two-face "
       "(CLI get silent-empty), moved to media\\drama-pilot-in\\, byte-verified vs manifest "
       "(PILOT-PREVIEW-3x20s.mp4 8224570/seg1 2019916/seg2 2099596/seg3 4106800/sea-review-level1.md 4111 = "
       "16454993B consistent with bm-b tx +18.6MB), reply MSG-20261018-0245 sent, MSG-2356 archived processed "
       "= CEO 看片通道 material in place + W265 gated watch (owner bm-c, prereg derive their FIRST ACTION, "
       "not landed; W266 naming gated on W265 prereg sec.7) + S6 43/43 rc0 (driver _r1044bma_s6chain.ps1 "
       "02:42-02:47) + smoke 49/49 + D-19 opening+closing double-scan zero-delta (dec 1d4741e4/ORD e0dcbd80 hold) "
       "+ loop pin=8 no-op + watchdog running + claws match x2 + idle --worked rc0 (product work) + orphan face=0 "
       "(23 py faces) + MF blockade day-5 watch (panel frozen complete=false, self-heal armed)")

report_line = (
    "2026-10-18T02:52:30+08:00 | r1044 bm-a (dept:舰队·drama取件收口+O-0137事故令守望+S6维护) | "
    "WM-VERDICT: 绿(red=false lane=healthy; satengine ALIVE queue0 idle; idle green_idle=true consumed via --worked(0)=drama取件产品活) | "
    "当前活=O-20261018-0137事故恢复令回执守望(bm-b心跳02:26:54推进r998在飞载O-0137 receipt+bm-c 01:38复活W265 prereg ARMED=两机回执在途·接管条件不成立·关账候两回执核验) + "
    "MSG-2356 drama五件取件完成(Downloads GUI双面落地判例·字节逐件对manifest全合·media\\drama-pilot-in\\ 5件=CEO看片通道材料就位·回执MSG-20261018-0245已发·r1037/r1041两轮假BLOCKED链终收口) + "
    "S0吸收收口(死窗00:0x post_review遗产+50行/REPORT-20261018.md+运行面·rebase UU watermark newer-wins r1028配方·behind-0) + "
    "W265 gated守watch(owner bm-c·prereg derive=其FIRST ACTION未落·zero skip-claim·W266命名候W265 §7) + "
    "S6 43/43 rc0(driver _r1044bma_s6chain.ps1·02:42-02:47·周日凌晨预期大半no-op) + S4坑固化(taildrop双面落地判例行入CODELY.md) | "
    "验证证据=chain log results/_r1044bma_s6chain_rc.log 43/43 rc0 + smoke 49/49 + d19 probe rc0 silent x2 (opening+closing zero-delta) + "
    "idle_trigger --worked rc=0 (idle_rounds=0) + drama-pilot-in dir 5-file byte listing vs MSG-2356 manifest 全合 + "
    "claws match x2 + loop pin=8 no-op (first fire 02:58) + watchdog Running | "
    "下轮指针=r1045: bm-b/bm-c taskaudit回执核验(O-0137 §3两回执齐后关账) + W265 prereg landing watch(落即推W266 owner命名) + "
    "P2/P3队列播种扫描(双板耗尽·agenda面诚实) + MF自愈watch(blockade day-5+·复测窗≤10-19) | "
    "最近实物=fleet/inbox/MSG-20261018-0245-bma-dramapickup-verified.md + C:\\Users\\sjs20\\Desktop\\FluxGroup\\media\\drama-pilot-in\\ 5件 (02:41) | "
    "本地未达 origin commit 数=0（收口 push 后自证）| [r1044 bm-a drama-pickup-incident-watch]\n"
)

with io.open(REP, "r", encoding="utf-8", errors="replace") as f:
    rep = f.read()
if "r1044 bm-a" not in rep:
    if not rep.endswith("\n"):
        rep += "\n"
    rep += report_line
    with io.open(REP, "w", encoding="utf-8", newline="") as f:
        f.write(rep)
    print("report appended")
else:
    print("report line already present, skip")

# ---- heartbeat ----
with io.open(HB, "r", encoding="utf-8", errors="replace") as f:
    hb = json.load(f)

import psutil
ram = psutil.virtual_memory()
try:
    import shutil
    tot, used, free = shutil.disk_usage("C:\\")
except Exception:
    free = 0
cpu = psutil.cpu_percent(interval=0.3)

hb.update({
    "ts": NOW, "last_seen": NOW, "now_active": NOW, "updated": NOW, "updated_at": NOW,
    "round": 1044, "loop_round": 1044, "round_no": 1045,
    "last_round": "r1044", "last_round_label": "r1044", "last_round_at": NOW, "last_round_closed": NOW,
    "current": did, "did": did, "last_action": did, "last_action_at": NOW,
    "current_task": "r1044 closed (drama pickup VERIFIED + O-0137 incident watch + S6 43-leg rc0)",
    "last_artifact": "fleet/inbox/MSG-20261018-0245-bma-dramapickup-verified.md + media/drama-pilot-in/ 5 files byte-verified (02:41)",
    "latest_artifact": "fleet/inbox/MSG-20261018-0245-bma-dramapickup-verified.md + media/drama-pilot-in/ 5 files byte-verified (02:41)",
    "recent_artifact": "fleet/inbox/MSG-20261018-0245-bma-dramapickup-verified.md + media/drama-pilot-in/ 5 files byte-verified (02:41)",
    "next": ("r1045: O-0137 taskaudit receipt verification (close incident account after both bm-b/bm-c receipts) + "
             "W265 prereg landing watch (bm-c first action) -> W266 owner naming per sec.7 + "
             "P2/P3 queue seeding scan + MF self-heal watch (day-5+, retest window <=2026-10-19)"),
    "next_milestone": "O-0137 incident account close (both taskaudit receipts verified, window in flight) + W266 window (owner named on W265 prereg freeze)",
    "verdict": ("green: r1044 = drama pilot 5-file taildrop pickup VERIFIED (byte-exact vs manifest, CEO 看片通道 material in place, MSG-0245 reply) "
                "+ O-0137 incident order receipted (both machines revived per dispatcher R14 evidence, receipts in flight, watch state) "
                "+ S6 43/43 rc0 + smoke 49/49 + WM green (red=false healthy) + satengine ALIVE idle + D-19 double-scan zero-delta "
                "+ orphan face=0 + idle --worked cleared"),
    "verify": ("chain log results/_r1044bma_s6chain_rc.log 43/43 rc0 + smoke 49/49 + d19 probe rc0 silent x2 + "
               "claws match x2 + loop pin=8 no-op (first fire 02:58) + watchdog Running + idle_trigger --worked rc=0 "
               "+ drama-pilot-in 5-file byte listing vs MSG-2356 manifest 全合"),
    "heartbeat_epoch_utc": EPOCH,
    "clock_read": NOW,
    "orders_ack": ["O-20261017-2207-bm-c.md", "O-20261018-0137-bm-a.md"],
    "orders_ack_note": ("r1044: O-20261018-0137 机队误关事故恢复令 receipted (watch state: @bm-b/@bm-c directives in flight, "
                        "bm-b r998 heartbeat advanced 02:26:54, bm-c revived 01:38 W265 ARMED; bm-a takeover condition NOT met); "
                        "MSG-2356 drama redrop processed = pickup VERIFIED (MSG-0245 reply, moved to processed)"),
    "idle_rounds": 0,
    "agenda_starved": False,
    "orphan_face": 0, "orphan_faces": 0, "orphan_killed": 0,
    "free_ram_gb": round(ram.available / (1024**3), 1),
    "ram_free_gb": round(ram.available / (1024**3), 1),
    "idle_ram_gb": round(ram.available / (1024**3), 1),
    "ram_free_pct": round(ram.available * 100.0 / ram.total, 1),
    "free_ram_pct": round(ram.available * 100.0 / ram.total, 1),
    "ram_load_pct": round(100.0 - ram.available * 100.0 / ram.total, 1),
    "cpu_pct": round(cpu, 1),
    "cpu_load_pct": round(cpu, 1),
    "cpu_util_pct": round(cpu, 1),
    "cpu_total_pct": round(cpu, 1),
    "gpu_source_note": "idle_trigger face + psutil cross-check 2026-10-18T02:52:30+08:00 (CEO weekend machine, honest free face)",
    "last_heartbeat_epoch_utc": hb.get("heartbeat_epoch_utc", EPOCH),
})
hb["notes_r1044"] = ("r1044: (1) taildrop two-face law: CLI file get silent-empty rc0 = pending inbox empty legal no-op; "
                     "Windows GUI layer auto-materializes Taildrop files into Downloads\\ — 'inbox empty' reads r1037/r1041 were two-face "
                     "confusion not transfer failure; pickup verify must include Downloads sweep leg (pit row appended CODELY.md); "
                     "(2) O-0137 incident: CEO 00:46 shutdown killed windows/sessions, scheduled tasks NOT disabled; wake pokes + worker v1.10 "
                     "self-heal revived both machines (bm-b heartbeat 02:26:54 r998 carrying O-0137 receipt, bm-c 01:38 revived W265 ARMED); "
                     "bm-a seat watch-only, incident account closes after both taskaudit receipts; (3) S0 rebase watermark UU = r1028 recipe "
                     "(newer-wins --theirs absorb side), zero loss; (4) dead 00:0x window estate absorbed (post_review +50 lines + REPORT-20261018.md)"
                     )
if "d19_watermark_guard" in hb:
    hb["d19_watermark_guard"]["round_ref"] = 1044
    hb["d19_watermark_guard"]["ts"] = NOW

with io.open(HB, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.load(io.open(HB, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat written, epoch int OK:", chk["heartbeat_epoch_utc"])

# ---- state ----
with io.open(ST, "r", encoding="utf-8", errors="replace") as f:
    st = json.load(f)
st.update({
    "round_no": 1045, "round": 1044, "loop_round": 1044,
    "last_round": "r1044", "last_round_label": "r1044",
    "last_round_at": NOW, "last_round_closed": NOW, "last_round_ts": NOW,
    "last_run": NOW, "last_seen": NOW, "now_active": NOW, "ts": NOW, "updated": NOW, "updated_at": NOW,
    "current": did, "current_task": "r1044 closed (drama pickup VERIFIED + O-0137 incident watch + S6 43-leg rc0)",
    "did": did, "last_action": did, "last_action_at": NOW,
    "last_artifact": "fleet/inbox/MSG-20261018-0245-bma-dramapickup-verified.md + media/drama-pilot-in/ 5 files (02:41)",
    "latest_artifact": "fleet/inbox/MSG-20261018-0245-bma-dramapickup-verified.md + media/drama-pilot-in/ 5 files (02:41)",
    "recent_artifact": "fleet/inbox/MSG-20261018-0245-bma-dramapickup-verified.md + media/drama-pilot-in/ 5 files (02:41)",
    "next": ("r1045: O-0137 taskaudit receipt verification (both machines) + W265 prereg landing watch -> W266 owner naming + "
             "P2/P3 queue seeding scan + MF self-heal watch (day-5+, <=2026-10-19)"),
    "next_milestone": "O-0137 incident account close (both receipts verified) + W266 bm-a window watch (owner named by W265 prereg sec.7)",
    "verdict": ("green: r1044 = drama pilot 5-file pickup VERIFIED (byte-exact, CEO 看片通道 material in place, MSG-0245) "
                "+ O-0137 incident order receipted (both machines revived, receipts in flight, watch state) "
                "+ S6 43/43 rc0 + smoke 49/49 + WM green + satengine ALIVE idle + D-19 double-scan zero-delta + orphan face=0 + idle --worked cleared"),
    "verify": ("chain log results/_r1044bma_s6chain_rc.log 43/43 rc0 + smoke 49/49 + d19 probe rc0 silent x2 + claws match x2 + "
               "loop pin=8 no-op + watchdog Running + idle_trigger --worked rc=0 + drama 5-file byte listing 全合"),
    "orders_ack": ["O-20261017-2207-bm-c.md", "O-20261018-0137-bm-a.md"],
    "orders_ack_note": ("r1044: O-20261018-0137 receipted (watch state, both machines revived, taskaudit receipts in flight); "
                        "MSG-2356 processed = pickup VERIFIED (MSG-0245), moved processed"),
    "idle_rounds": 0, "agenda_starved": False,
    "orphan_face": 0, "orphan_faces": 0, "orphan_killed": 0,
    "free_ram_gb": round(ram.available / (1024**3), 1),
    "cpu_pct": round(cpu, 1),
    "last_heartbeat_epoch_utc": EPOCH,
    "notes_r1044": ("r1044: (1) taildrop two-face pit (CLI get silent no-op vs GUI Downloads materialization) — r1037/r1041 BLOCKED "
                    "receipts were two-face confusion; law: pickup verify must sweep Downloads; (2) O-0137: CEO 00:46 shutdown killed "
                    "sessions not tasks; both machines self-revived (bm-b 02:26:54 r998 carrying receipt, bm-c 01:38 W265 ARMED); "
                    "bm-a watch-only, account closes on both taskaudit receipts; (3) S0 rebase watermark UU r1028 newer-wins; "
                    "(4) dead 00:0x estate absorbed (post_review +50 + REPORT-20261018.md)"),
})
st["sync"] = {"ts": NOW, "origin_tip": None, "ahead_behind": "pending-closeout-push",
              "note": "r1044: S0 pre-absorb 939619c0a rebased onto 0c49d5235 (O-0137 + bm-b r997); closeout push follows"}
st["d19_watermark_guard"]["round_ref"] = 1044
st["d19_watermark_guard"]["ts"] = NOW
st["push_verified"] = "r1044 closeout push follows this write"

with io.open(ST, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
chk2 = json.load(io.open(ST, encoding="utf-8"))
print("state written, round_no:", chk2["round_no"])
print("CLOSEOUT_WRITES_OK")
