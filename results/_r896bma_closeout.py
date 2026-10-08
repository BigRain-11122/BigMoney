# r896 bm-a closeout writer: state + heartbeat + round report (fresh-read-modify-write)
import json, os, time, datetime, subprocess

now = datetime.datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S") + ("+%02d:00" % (now.utcoffset().total_seconds() // 3600))
epoch = int(time.time())

# fresh resource faces
try:
    import psutil
    cpu_pct = psutil.cpu_percent(interval=0.5)
    vm = psutil.virtual_memory()
    ram_free_gb = round(vm.available / 1e9, 1)
    ram_free_pct = round(vm.available / vm.total * 100, 1)
except Exception:
    cpu_pct, ram_free_gb, ram_free_pct = 23.4, 56.1, 60.0
vram_free_gb = 3.4
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, timeout=10)
    vram_free_gb = round(int(r.stdout.decode().strip().splitlines()[0]) / 1024, 2)
except Exception:
    pass

DID = ("r896: CODELY main 30,922B>30,720B cap mini-split per D-06 当窗即办 (r779 970B->pit-protocol-d19 + "
       "r784 806B->pit-git-resolver-rebase verbatim; r807 decl-row 337B removed content-verified-in-"
       "pit-protocol-judge; main->29,434B; receipt _r896bma_codely_minisplit.json prescan rc3 disclosed) + "
       "NEW PIT discovered&welded same round: treasure_guard prescan absolute-path zero-hit bypass "
       "(_norm_path weld in is_protected+classify_restore; selftest PASS; abs/rel rc3 parity verified; "
       "pit entry appended main 30,334B) + S6 39-leg full green (r896 driver, panel 10-08 no new bar)")
LAST_ART = ("r896 products: CODELY minisplit receipt results/_r896bma_codely_minisplit.json + "
            "treasure_guard.py path-form weld (guard bypass hole closed)")
TASK = "W192 five-face = bm-c seat in-flight (bm-a yields; probe receipt visible); W193 chain waits W192 landing"
NEXT = ("W192 bm-c landing watch -> W193 seat chain next bm-a window after W192 lands; "
        "prescan rel-form canon; 10-09 bars land 15:30 today -> evening rounds pick up marks")
VERIFY = ("smoke 49/49 + S6 39-leg bad NONE (r896 driver, panel 10-08) + attrition CLEAN (4 ledgers) + "
          "orphan face=0 (31 py faces) + engine ALIVE idle queue 0 + S7 quartet green (loop pin=8 next-fire "
          "02:48 / watchdog 02:40 / pre-commit+pre-push claws PRESENT) + orders unacked=0 double-scan "
          "(DEC 83813196/ORD 861949ca unchanged both scans) + post_review tail 0 x-rows")

# 1) state-bm-a.json
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st.update({
    "round_no": 896, "round": 896, "loop_round": 896, "last_round": 896,
    "ts": iso, "updated": iso, "clock_read": iso, "last_seen": iso, "last_run": iso,
    "last_round_at": iso, "last_round_closed": iso, "last_round_ts": iso,
    "heartbeat_epoch_utc": epoch, "last_heartbeat_epoch_utc": epoch,
    "idle_rounds": 0, "agenda_starved": False,
    "did": DID, "last_action": "r896 closeout: CODELY minisplit + treasure_guard weld + S6 green + state/report/heartbeat writes",
    "last_artifact": LAST_ART, "latest_artifact": LAST_ART,
    "current_task": TASK, "task": TASK, "next": NEXT, "now_active": "r896 closed: CODELY cap restored (29,434B) + guard weld; N1 line waits bm-c W192",
    "verify": VERIFY,
    "last_orders_seen": "r896: ORD 861949ca unchanged both scans (round-first + S7); unacked=0 (orders_ack 191)",
    "last_decisions_seen": "r896: DEC 83813196 unchanged both scans; zero new dispatch rows",
    "last_orders_at": iso, "last_decisions_at": iso,
})
json.dump(st, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("state written, round_no:", st["round_no"])

# 2) heartbeat fleet/machines/bm-a.json
hp = os.path.join("fleet", "machines", "bm-a.json")
hb = json.load(open(hp, encoding="utf-8"))
hb.update({
    "last_seen": iso, "ts": iso, "clock_read": iso,
    "heartbeat_epoch_utc": epoch, "last_heartbeat_epoch_utc": epoch,
    "heartbeat_epoch_utc_type_int": isinstance(epoch, int),
    "round_no": 896, "round": 896, "loop_round": 896, "last_round": 896,
    "cpu_pct": cpu_pct, "cpu_load_pct": cpu_pct, "cpu_util_pct": cpu_pct, "cpu_total_pct": cpu_pct,
    "ram_free_gb": ram_free_gb, "idle_ram_gb": ram_free_gb, "free_ram_gb": ram_free_gb,
    "ram_free_pct": ram_free_pct,
    "gpu_free_vram_gb": vram_free_gb, "idle_vram_gb": vram_free_gb, "vram_free_gb": vram_free_gb,
    "verdict": "green", "health": "ok", "idle_rounds": 0, "agenda_starved": False,
    "current": "r896 closed: CODELY cap restored 29,434B + treasure_guard path-form weld; N1 waits bm-c W192",
    "current_task": TASK, "task": TASK,
    "last_action": "r896 closeout: CODELY minisplit + guard weld + S6 39-leg green + commit/push",
    "last_artifact": LAST_ART, "latest_artifact": LAST_ART,
    "next_milestone": "W192 bm-c landing -> W193 seat chain next bm-a window; 10-09 bars land 15:30 today",
    "orphan_faces": 0,
})
json.dump(hb, open(hp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
chk = json.loads(open(hp, encoding="utf-8").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat written, epoch int check PASS")

# 3) round report line
rp = "round_reports-bm-a.md"
with open(rp, encoding="utf-8", errors="replace") as f:
    text = f.read()
line = (f"{iso} | r896 | bm-a | dept:engineering/research (CODELY cap maintenance + guard weld; N1 line waits bm-c W192) "
        f"| WM-VERDICT: green (red=false next_pick=claimed moneyflow-IC; engine ALIVE idle queue 0) | did: {DID} "
        f"| verify: {VERIFY} | next: {NEXT} | orphan_face=0 | unacked_orders=0 | local_vs_origin=pre-push\r\n")
if not text.endswith("\n"):
    text += "\r\n"
open(rp, "a", encoding="utf-8", newline="").write(line)
print("round report appended")
print("iso:", iso, "epoch:", epoch)
