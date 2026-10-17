# -*- coding: utf-8 -*-
# r1043 bm-a closeout patch: state-bm-a.json + heartbeat + round report line + W265 seat MSG yield-processing
import json, time, shutil, os, datetime

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def save(p, obj):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")

# --- fresh idle/RAM faces (idle_trigger 23:18 read + psutil cross-check) ---
trig = load(os.path.join(ROOT, "results", "idle_trigger.bm-a.json"))
vram_free_gb = float(trig.get("vram_free_gb", 7.24))
try:
    import psutil
    vm = psutil.virtual_memory()
    total_gb = round(vm.total / 1024**3, 1)
    free_gb = round(vm.available / 1024**3, 1)
    free_pct = round(vm.available * 100.0 / vm.total, 1)
except Exception:
    total_gb = 93.6
    free_pct = float(trig.get("ram_free_pct", 42.1))
    free_gb = round(total_gb * free_pct / 100.0, 1)

# --- honest S6 chain rc-line count from this round's log ---
log_path = os.path.join(ROOT, "results", "_r1043bma_s6chain_rc.log")
rc_lines = []
with open(log_path, "r", encoding="utf-8-sig", errors="replace") as f:
    for ln in f:
        if " rc=" in ln and ln.strip():
            rc_lines.append(ln.strip())
n_legs = len(rc_lines)
nonzero = [l for l in rc_lines if not l.endswith("rc=0")]
assert n_legs >= 40, "unexpected S6 log leg count: %d" % n_legs
assert not nonzero, "nonzero rc legs found: %r" % nonzero
print("S6_LOG_COUNT legs=%d all_rc0=True" % n_legs)

R = "r1043"
did = ("r1043: r1042 closeout commit pushed at S0 (range 7343e3650..35f6f63c2 behind-0) "
       "+ W265 seat MSG-2241 processed = YIELD (owner bm-c per chain-order law, W264 prereg sec.7 named window; "
       "r1042 own-seat expectation superseded BEFORE any claim; zero skip-claim, zero claims on origin) "
       "+ MF push2 re-probe adjudication CLOSED (8/8 fail incl ctrl-quote baseline flip = block WIDENED from clist-path "
       "to push2-family API-path level; day-4+ longest in r40/r46 family; receipt results/_r1043bma_mf_reprobe_adjudication.json; "
       "<=2026-10-19 deadline satisfied early; MF-IC-P1 stays legally waiting; conn-fuse+30min throttle self-heal armed) "
       "+ S6 chain %d legs rc0 bad=0 (_r1043bma_s6chain.ps1, r1042 face clone) + smoke 49/49 + "
       "D-19 opening+closing double-scan zero-delta + idle two_read_red consumed via --worked (product work)" % n_legs)
verdict = ("green: r1043 = r1042 closeout delivered + W265 seat YIELDED to bm-c (MSG-2241, zero skip-claim) "
           "+ MF adjudication closed (blockade widened day-4, receipt) + S6 %d-leg rc0 + smoke 49/49 + WM green (red=false healthy) "
           "+ satengine ALIVE idle + D-19 double-scan zero-delta + orphan face=0 + idle --worked cleared" % n_legs)
nxt = ("r1044: watch bm-c W265 prereg derive+freeze landing (their FIRST ACTION per seat MSG) -> W266 owner naming "
       "per W265 prereg sec.7; P2/P3 queue seeding scan (both boards drained, honest agenda face); MF self-heal watch (blockade day-4+)")
art = "results/_r1043bma_mf_reprobe_adjudication.json (MF blockade widened verdict, 23:2x)"

# --- state patch ---
sp = os.path.join(ROOT, "state-bm-a.json")
st = load(sp)
st["round"] = 1043
st["round_no"] = 1044
st["round_no_label"] = R
st["last_round"] = R
st["last_round_label"] = R
st["loop_round"] = 1043
for k in ("current", "did", "last_action"):
    st[k] = did
st["current_task"] = "r1043 closed (W265 yield + MF adjudication closed + S6 %d-leg rc0 + smoke 49/49)" % n_legs
st["task"] = "r1043 W265 seat yield + MF re-probe adjudication + S6 maintenance"
st["verdict"] = verdict
st["next"] = nxt
st["next_milestone"] = ("W266 bm-a window watch (owner named by W265 prereg sec.7 on bm-c freeze) "
                       "+ MF self-heal watch (blockade day-4+)")
for k in ("last_artifact", "latest_artifact", "recent_artifact"):
    st[k] = art
for k in ("last_round_at", "last_round_closed", "last_round_ts", "last_run", "last_seen",
          "last_action_at", "now_active", "ts", "updated", "updated_at"):
    st[k] = now_iso
st["last_heartbeat_epoch_utc"] = st.get("heartbeat_epoch_utc")
st["heartbeat_epoch_utc"] = epoch
st["heartbeat_epoch_utc_type_int"] = True
st["last_decisions_seen"] = "r1043: dec 1d4741e4 hold opening+closing scans (d19 probe rc0 silent x2, zero delta)"
st["last_decisions_at"] = now_iso
st["last_decisions_read_at"] = now_iso
st["last_orders_seen"] = ("r1043: ORD e0dcbd80 hold opening+closing scans (d19 probe rc0 silent x2, zero delta; "
                          "newest fleet/orders = O-20261017-2207-bm-c receipted r1041)")
st["last_orders_at"] = now_iso
st["last_orders_read_at"] = now_iso
st["orders_ack_note"] = ("r1043: opening+closing double-scan zero new orders; W265 seat MSG-20261017-2241 "
                         "processed = yield (owner bm-c), moved to inbox/processed")
st["orphan_face"] = 0
st["orphan_faces"] = 0
st["orphan_killed"] = 0
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["free_ram_gb"] = free_gb
st["ram_free_gb"] = free_gb
st["idle_ram_gb"] = free_gb
st["ram_free_pct"] = free_pct
st["free_ram_pct"] = free_pct
st["ram_load_pct"] = round(100 - free_pct, 1)
st["total_ram_gb"] = total_gb
st["gpu_free_vram_mb"] = int(round(vram_free_gb * 1024))
st["gpu_source_note"] = "idle_trigger face + psutil cross-check " + now_iso + " (CEO working machine, honest free face)"
st["notes_r1043"] = ("r1043: (1) W265 seat MSG-2241 (bm-c r1077 22:41) declares owner=bm-c per chain-order law "
                     "(W263 bm-a -> W264 bm-c -> W265 bm-c own-turn; W264 prereg sec.7 backfill named the window) -- "
                     "r1042 'W265 bm-a own-seat' plan expectation superseded BEFORE any claim (zero skip-claim both windows); "
                     "bm-a yields per fleet README sec.4 + seat-first law O-20261010-2350 sec.2; "
                     "(2) MF push2 8-leg diag rerun: all fail incl ctrl-quote (was OK at r1027 05:5x baseline) = block widened "
                     "clist-path -> push2-family API-path level (push2his root 404 = host alive, api paths reset); day-4+ duration "
                     "longest in r40/r46 blockade family; panel cutoff 2026-10-13 complete=false frozen; self-heal armed; "
                     "(3) S6 chain cloned to _r1043bma_s6chain.ps1 (r1042 face verbatim) - %d rc-lines all rc0 bad=0; "
                     "(4) P2/P3 queue boards drained (T5-T26 / E1-E15 all done-closed) - honest agenda face, next supply = "
                     "wave-chain W266 window + queue seeding scan" % n_legs)
st["sync"] = {"ts": now_iso, "origin_tip": None, "ahead_behind": "pending-closeout-push",
              "note": "r1043: S0 push delivered r1042 closeout (range 7343e3650..35f6f63c2 behind-0); r1043 closeout push follows"}
st["push_verified"] = ("r1042 closeout delivery push range 7343e3650..35f6f63c2 behind-0 readback same-round (S0); "
                       "r1043 closeout push follows")
st["d19_watermark_guard"]["round_ref"] = 1043
st["d19_watermark_guard"]["ts"] = now_iso
st["last_decisions_ts"] = st.get("last_decisions_ts", "2026-10-17T13:52:13+08:00")
save(sp, st)
print("STATE_PATCHED r1043 epoch_int=%s ram_free_gb=%s vram_free_mb=%s" % (epoch, free_gb, int(vram_free_gb * 1024)))

# --- heartbeat patch (fleet/machines/bm-a.json) ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
hb = load(hp)
hb["last_seen"] = now_iso
hb["ts"] = now_iso
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["current_task"] = st["current_task"]
hb["task"] = st["task"]
hb["verdict"] = "green: W265 yielded to bm-c + MF adjudication closed + S6 %d-leg rc0 + smoke 49/49" % n_legs
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["free_ram_gb"] = free_gb
hb["ram_free_gb"] = free_gb
hb["ram_free_pct"] = free_pct
hb["gpu_free_vram_mb"] = int(round(vram_free_gb * 1024))
save(hp, hb)
rl = json.loads(open(hp, "r", encoding="utf-8").read())
assert isinstance(rl["heartbeat_epoch_utc"], int), "heartbeat epoch must be JSON int"
assert "T" in rl["clock_read"], "clock_read must be T-separated"
print("HEARTBEAT_PATCHED epoch_type_int=True clock_T=True")

# --- round report line append ---
rr = os.path.join(ROOT, "round_reports-bm-a.md")
line = (
    "%s | r1043 bm-a (dept:\u7814\u7a76\u00b7W265\u5e2d\u4f4d\u8ba9\u8def+MF\u6e90\u5c01\u9501\u88c1\u51b3+S6\u7ef4\u62a4) | "
    "WM-VERDICT: \u7eff (red=false lane=healthy; satengine ALIVE queue0 idle; idle two_read_red consumed via --worked(0)) | "
    "\u5f53\u524d\u6d3b=r1043: S0\u63a8\u8d70r1042\u6536\u53e3commit(35f6f63c2 range 7343e3650..35f6f63c2 behind-0)"
    "+W265\u5e2d\u4f4dMSG-2241\u5904\u7406=\u8ba9\u8def(owner bm-c per chain-order\u6cd5\u00b7W264 prereg \u00a77\u70b9\u540d\u7a97"
    "\u00b7r1042\u9884\u671f\u5728claim\u524d\u88ab\u5426\u00b7zero skip-claim)+MF push2\u518d\u63a2\u88c1\u51b3\u95ed\u7a97:"
    "8/8\u706d\u542bctrl-quote\u57fa\u7ebf\u7ffb\u8f6c=\u5c01\u9501\u81eaclist\u8def\u5f84\u7ea7\u6269\u5bbd\u81f3push2\u5bb6\u65cf"
    "API\u8def\u5f84\u7ea7(day-4+\u00b7r40/r46\u65cf\u6700\u957f\u7a97)\u00b7\u56de\u6267 _r1043bma_mf_reprobe_adjudication.json"
    "\u00b7<=10-19\u6b7b\u7ebf\u63d0\u524d\u6ee1\u8db3\u00b7MF-IC-P1\u5408\u6cd5\u7b49\u5f85\u00b7fuse+30min\u8282\u6d41\u81ea\u6108\u5728\u4f4d | "
    "\u9a8c\u8bc1\u8bc1\u636e=smoke 49/49 + S6 chain rc-lines %d/%d rc0 bad=0 (log _r1043bma_s6chain_rc.log) + "
    "d19 probe rc0 silent x2 (opening+closing zero-delta) + orphan face=0 (25 py faces) + idle --worked rc=0 "
    "+ P2/P3 queue drained face (T5-T26/E1-E15 \u5168done/closed) | "
    "\u4e0b\u8f6e\u6307\u9488=r1044: watch bm-c W265 prereg derive+freeze landing (\u5176FIRST ACTION per\u5e2d\u4f4dMSG) -> "
    "W266 owner\u547d\u540d\u9762(W265 prereg \u00a77); P2/P3\u961f\u5217\u64ad\u79cd\u626b\u63cf(\u53cc\u677f\u8017\u5c3d\u00b7agenda\u9762\u8bda\u5b9e); "
    "MF\u81ea\u6108watch(blockade day-4+) | \u6700\u8fd1\u5b9e\u7269=results/_r1043bma_mf_reprobe_adjudication.json "
    "(MF\u5c01\u9501\u6269\u5bbd\u88c1\u51b3, 23:2x) | \u672c\u5730\u672a\u8fbe origin commit \u6570=0\uff08\u6536\u53e3\u63a8\u9001\u540e\u6838\u9a8c\uff09 | "
    "[r1043 bm-a w265-yield-mf-adjudication]\n" % (now_iso, n_legs, n_legs)
)
with open(rr, "a", encoding="utf-8", newline="") as f:
    f.write(line)
print("ROUND_REPORT_APPENDED r1043")

# --- W265 seat MSG processing: yield + move to processed ---
src = os.path.join(ROOT, "fleet", "inbox", "MSG-20261017-2241-bmc-w265-seat.md")
dst = os.path.join(ROOT, "fleet", "inbox", "processed", "MSG-20261017-2241-bmc-w265-seat.md")
assert os.path.exists(src), "seat MSG missing: %s" % src
os.makedirs(os.path.dirname(dst), exist_ok=True)
shutil.move(src, dst)
assert os.path.exists(dst) and not os.path.exists(src)
print("SEAT_MSG_MOVED MSG-20261017-2241 -> processed (yield, owner bm-c)")
print("PATCH_DONE OK")
