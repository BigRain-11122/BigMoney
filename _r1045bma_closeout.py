# r1045 bm-a closeout writes: heartbeat (with orders_ack list rebuild from r1040 git face) + state
import json, os, subprocess, time, psutil

ROOT = os.path.dirname(os.path.abspath(__file__))
HB = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
STATE = os.path.join(ROOT, "state-bm-a.json")
NOW = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()) + "+08:00"
EPOCH = int(time.time())

# 1) rebuild orders_ack from r1040 pre-truncation face (8812bda52, 107 acks)
r = subprocess.run(["git", "show", "8812bda52:fleet/machines/bm-a.json"],
                   capture_output=True, cwd=ROOT)
old = json.loads(r.stdout.decode("utf-8"))
acks = list(old.get("orders_ack", []))
for add in ("O-20261017-2207-bm-c.md", "O-20261018-0137-bm-a.md",
            "O-20261018-0348-bm-a.md"):
    if add not in acks:
        acks.append(add)

vm = psutil.virtual_memory()
gpu_free = 7414  # idle_trigger face (llm-mode resident ~3G honest)

cur = ("r1045: S0 absorb+rebase (runtime faces; watermark_red UU r1028 newer-wins; behind-0) "
       "+ O-20261018-0348-bm-a receipted (r998 git-face closeout escalation order, @bm-b P0 first-action, "
       "MSG-0216 not yet on origin = O-0137 account stays open, bm-a watch1) "
       "+ D-19 orders delta CONSUMED (4 rows since e0dcbd80: V5.3-C01 deliver / O-2110 bookkeeping / "
       "bm-c resume receipt / @bm-c BM-repo unblock -- zero new BigMoney action; dec 1d4741e4 hold) "
       "+ watermark ADVANCED ord=eae5ac55 (d19 update --advance, read-back OK) "
       "+ D19 PROBE SILENT-RC0 DEFECT FIXED (cmd_probe pass-through child stdout swallowed on this "
       "Win/Py3.14 host -> loop read silence as hold and missed real delta r1044; fix=capture+relay "
       "_relay_child_streams; selftest 15->17/17 PASS; live probe now prints orders_changed=true) "
       "+ orders_ack LIST REGRESSION HEALED (r1041 incident rebuild dropped 107->1; rebuilt from "
       "r1040 git face +3 = 110; scanner unacked 99->0 expected) "
       "+ S6 42/42 rc0 (driver _r1045bma_s6chain.ps1) + smoke 49/49 + WM green healthy "
       "+ satengine ALIVE idle + loop pin=8 no-op + watchdog running (S4U flip access-denied = carried "
       "face C-20261016-04) + claws match x2 + idle --worked rc0 (9->0) + orphan face=0 (19 py faces)")

nxt = ("r1046: O-0137 taskaudit receipt verify (close after both bm-b MSG-0216 landing + bm-c receipt) "
       "+ W265 splice+finalize watch (bm-c first action) -> W266 owner naming per W265 sec.7 "
       "+ MF self-heal watch (day-5+, <=2026-10-19 retest window) + queue seeding scan")

hb = json.load(open(HB, encoding="utf-8"))
hb.update({
    "clock_read": NOW, "ts": NOW, "updated": NOW, "updated_at": NOW,
    "last_seen": NOW, "now_active": NOW, "last_round_at": NOW,
    "last_round_closed": NOW, "last_run": NOW, "last_action_at": NOW,
    "heartbeat_epoch_utc": EPOCH, "heartbeat_epoch_utc_type_int": True,
    "last_heartbeat_epoch_utc": hb.get("heartbeat_epoch_utc", 1792263096),
    "round": 1045, "loop_round": 1045, "last_round": "r1045",
    "last_round_label": "r1045", "round_no": 1046,
    "current": cur, "did": cur, "last_action": cur,
    "current_task": "r1045 closed (d19 probe relay fix + orders_ack rebuild + O-0137/0348 watch + S6 42-leg rc0)",
    "task": "r1045 D-19 intake defect fix + ack-list heal + incident watch",
    "next": nxt,
    "next_milestone": "O-0137 account close (both taskaudit receipts) + W266 window (owner named on W265 finalize sec.7)",
    "last_artifact": "scripts/d19_watermark.py (probe relay fix, selftest 17/17) + results/_r1045bma_s6chain_rc.log (42/42 rc0)",
    "recent_artifact": "scripts/d19_watermark.py (probe relay fix, selftest 17/17) + results/_r1045bma_s6chain_rc.log (42/42 rc0)",
    "latest_artifact": "scripts/d19_watermark.py (probe relay fix, selftest 17/17) + results/_r1045bma_s6chain_rc.log (42/42 rc0)",
    "orders_ack": acks,
    "orders_ack_note": ("r1045: O-20261018-0348-bm-a tracked (bm-a-issued escalation, @bm-b first-action, "
                        "watch1); ACK LIST REGRESSION HEALED: r1041 incident rebuild truncated 107->1, "
                        "rebuilt verbatim from r1040 git face 8812bda52 + 3 post-incident receipts = %d" % len(acks)),
    "orders_ack_last": acks[-1],
    "last_orders_sha": "eae5ac55af94d790a2ed9f040343fe7bf501f6df1a624afbebae682e24c935f4",
    "last_decisions_sha": "1d4741e4a0d6514519040442182b0679a423d58896a4105861e152108be441f1",
    "last_orders_seen": "r1045: ORD delta consumed (4 rows, zero BigMoney action) + advanced eae5ac55 (probe relay fix live)",
    "last_decisions_seen": "r1045: dec 1d4741e4 hold (opening scan; probe now prints verdict face post-fix)",
    "last_orders_at": NOW, "last_orders_read_at": NOW,
    "last_decisions_at": NOW, "last_decisions_read_at": NOW,
    "idle_rounds": 0, "agenda_starved": False,
    "orphan_face": 0, "orphan_faces": 0, "orphan_killed": 0,
    "free_ram_gb": round(vm.available / 1e9, 1),
    "ram_free_gb": round(vm.available / 1e9, 1),
    "idle_ram_gb": round(vm.available / 1e9, 1),
    "ram_free_mb": int(vm.available / 1e6),
    "idle_ram_mb": int(vm.available / 1e6),
    "free_ram_pct": round(100 * vm.available / vm.total, 1),
    "ram_free_pct": round(100 * vm.available / vm.total, 1),
    "ram_load_pct": round(100 - 100 * vm.available / vm.total, 1),
    "gpu_free_vram_mb": gpu_free,
    "gpu_source_note": "idle_trigger face 2026-10-18 (CEO weekend machine, llm-mode resident honest)",
    "verdict": ("green: r1045 = d19 probe silent-rc0 defect FIXED (capture+relay, selftest 17/17, live probe "
                "prints delta face) + orders delta consumed + watermark advanced eae5ac55 + orders_ack list "
                "regression healed 2->110 + O-0348 tracked (O-0137 account open, watch1) + S6 42/42 rc0 + "
                "smoke 49/49 + WM green + satengine ALIVE + orphan 0 + idle cleared"),
    "verify": ("results/_r1045bma_s6chain_rc.log 42/42 rc0 + smoke 49/49 + d19 selftest 17/17 + "
               "d19 update --advance read-back OK + verify structural_ok=true + orders_ack_scan rerun "
               "post-heal expected rc0 + claws match x2 + loop pin=8 no-op + watchdog Running + "
               "idle_trigger --worked rc=0"),
    "notes_r1045": ("r1045: (1) d19 intake defect: Win/Py3.14 host swallows pass-through subprocess child "
                    "stdout (parent prints land, child prints vanish even under > file; empirical "
                    "python -c subprocess test) -- cmd_probe relied on pass-through so loop read "
                    "silence+rc0 as zero-delta while real orders delta existed (r1044 'double-scan "
                    "zero-delta hold' was this miss, 4 group commits incl. 8ef6635 sat unconsumed "
                    "01:52-04:3x); fix = capture_output + _relay_child_streams reprint, selftest L16/L17; "
                    "(2) orders_ack list regression: r1041 incident-recovery state rebuild truncated "
                    "107->1 acks (b9cb641d8), scanner flagged 99 false P0 debt; healed verbatim from "
                    "r1040 git face 8812bda52 +3 post-incident receipts; (3) O-20261018-0348-bm-a = "
                    "bm-a-proxy 03:48 escalation order (r998 receipts stuck on bm-b disk); MSG-0216 "
                    "still absent on origin at 04:4x = bm-b first-action pending, O-0137 account open; "
                    "(4) W265 prereg LANDED (e57215a2c bm-c), splice+finalize = bm-c next window, W266 "
                    "owner naming rides W265 sec.7 backfill"),
})
hb["sync"] = {"ts": NOW, "origin_tip": None, "ahead_behind": "pending-closeout-push",
              "note": "r1045: pre-absorb rebased onto 3917a974e (5 origin commits: O-0348 order + "
                      "W265 PREREG FREEZE bm-c + r1078/1080/1081 estates); closeout push follows"}
hb["push_verified"] = {"ts": NOW, "origin_tip": None, "ahead_behind": "pending",
                       "note": "r1045 closeout push follows this write; fetch+ls-tree self-verify after push"}

with open(HB, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
assert isinstance(hb["heartbeat_epoch_utc"], int) and isinstance(EPOCH, int)

# 2) state-bm-a.json face update (round fields + r1045 pointers; keep notes history)
st = json.load(open(STATE, encoding="utf-8"))
st.update({
    "clock_read": NOW, "ts": NOW, "updated": NOW, "updated_at": NOW,
    "last_seen": NOW, "now_active": NOW, "last_round_at": NOW,
    "last_round_closed": NOW, "last_run": NOW, "last_round": "r1045",
    "last_round_label": "r1045", "round_no_label": "r1045",
    "round": 1045, "loop_round": 1045, "round_no": 1046,
    "current": cur, "did": cur, "last_action": cur,
    "current_task": hb["current_task"], "task": hb["task"],
    "next": nxt, "next_milestone": hb["next_milestone"],
    "last_artifact": hb["last_artifact"],
    "recent_artifact": hb["last_artifact"], "latest_artifact": hb["last_artifact"],
    "orders_ack": acks,
    "orders_ack_note": hb["orders_ack_note"],
    "last_orders_sha": hb["last_orders_sha"], "last_decisions_sha": hb["last_decisions_sha"],
    "last_orders_seen": hb["last_orders_seen"], "last_decisions_seen": hb["last_decisions_seen"],
    "last_orders_at": NOW, "last_orders_read_at": NOW,
    "last_decisions_at": NOW, "last_decisions_read_at": NOW,
    "idle_rounds": 0, "agenda_starved": False,
    "orphan_face": 0, "orphan_faces": 0,
    "heartbeat_epoch_utc": EPOCH, "heartbeat_epoch_utc_type_int": True,
    "last_heartbeat_epoch_utc": 1792263096,
    "free_ram_gb": hb["free_ram_gb"], "ram_free_gb": hb["ram_free_gb"],
    "idle_ram_gb": hb["idle_ram_gb"], "ram_free_pct": hb["ram_free_pct"],
    "verdict": hb["verdict"], "verify": hb["verify"],
    "notes_r1045": hb["notes_r1045"],
    "d19_watermark_guard": {"tool": "scripts/d19_watermark.py",
                            "probe": "results/_r686bmb_d19_check.py",
                            "probe_evidence": os.path.join(ROOT, "results", "_r686bmb_d19_check.json"),
                            "method_decisions": "sha256", "method_orders": "sha256",
                            "verbatim": True, "advance": True, "round_ref": 1045, "ts": NOW},
})
st["sync"] = hb["sync"]
with open(STATE, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

print("heartbeat+state written; acks=%d epoch_int=%s NOW=%s" % (len(acks), isinstance(EPOCH, int), NOW))
