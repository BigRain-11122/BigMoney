# -*- coding: utf-8 -*-
"""r1071 bm-a closeout: state + heartbeat + round-report line (S5/S7).
Single-writer faces (bm-a own files), fresh-measure, atomic writes."""
import io
import json
import os
import subprocess
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.now().astimezone()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())


def _ram_free_mb():
    try:
        import ctypes
        class MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong)]
        ms = MS()
        ms.dwLength = ctypes.sizeof(MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
        return int(ms.ullAvailPhys / 1024 / 1024), int(ms.dwMemoryLoad)
    except Exception:
        return None, None


def _gpu_vram_free():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                              "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=20).stdout.strip()
        return int(out.splitlines()[0])
    except Exception:
        return None


free_mb, load_pct = _ram_free_mb()
vram_free = _gpu_vram_free()
ram_free_gb = round(free_mb / 1024, 1) if free_mb else None

DID = ("r1071: (1) S0 pull window: fetch no-ref transient (promisor family) -> direct fetch rc0 -> "
       "rebase --autostash onto origin f7b18587e absorbed 13 commits (bm-c W274 full cycle CLOSED: prereg FREEZE 839441a547 CAS "
       "-> splice ec907d164 -> burn 12/12 b3c8a83c5c+b4c0271044 -> sixgate 37th -> finalize 1,027,135/600,720 EXACT -> fivekeys 6/6 -> "
       "sec78 -> closeout c4e752d682; W275 SEAT PUBLISHED bf4bbbde1 owner=bm-c 94th own wave; bm-b r1014 drama chain + r1070 postscript "
       "08610b6ed); autostash pop-UU watermark_red.json = r1028 family newer-wins (origin 03:49:04 vs stash 03:42:02, theirs), marker "
       "scan rc0, autostash dropped via python subprocess channel (PS single-quote literal-passthrough face, see notes_r1071); "
       "(2) round-zero orphan probe 0/20 py faces 1 resident server exempt; idle trigger green_idle=false (RAM 33.2pct) two_read_red=false "
       "idle_rounds=0; (3) S0.5 fleet board CLEAN 105/114/0 zero face divergence; D-19 dec HOLD 8706acd8 zero-delta, ord delta "
       "e695556b->04050fda consumed (10-19 02:18 V5.9 receipt row = BigStream domain, bm-a interactive window executed, zero "
       "BigMoney-loop obligation per r1057 precedent) -> d19 --advance read-back equality, mirrors synced 5; (4) S1 smoke 49/49; "
       "S3 satengine ALIVE rc0 queue0 idle (claimable_n=0, A1 crossface live); watermark red=false; (5) MAIN DELIVERABLE A2 G4 "
       "PnL-ATTRIBUTION DAILY LEDGER LANDED (deadline was <=10-23, landed early): daily_report.py + _series_tail_delta/_top_position/"
       "_paper6_attribution/_marks_family/_attribution_face + section 七、盈亏归因日账 rendered into REPORT-2026-10-19.md/.json twin "
       "(live-fire rc0: 40 accounts attributed, grand day PnL +37,017.40 CNY asof 10-16 [pre-15:30 Monday honest note], paper6 +7,156.27 "
       "/ AGGR 20-acct +15,274.05 / ALLOC 7-acct +6,549.55 / GRID 5-acct +3,311.85 / SYSV1 2-acct +4,725.68 with route legs "
       "rev_osc 30%/trend 10%/lowvol 10%/cash 50% + REV-OSC-STD pure-sleeve detection ret=series + w_eff face; zero missing, zero "
       "fabricated); selftest legs PASS (5 helper-delta assertions incl first_day/no_data/stored-daily_ret preference + 24 render "
       "markers); automation_line_audit.py additive evidence face pnl_attribution_streak_days=1 (E4 verdict semantics untouched, "
       "audit selftest PASS) -> acceptance V2 streak counter live; (6) MSG-021x canon-adopt-traps receipted with code-level "
       "verification: bm-a v2 immune to both traps by construction (idle_since age arithmetic = fromisoformat inside try/except "
       "age=-1 fallback, NOT bare float-str; satengine leg = scripts status rc + register+tick recipe = bm-b-corrected architecture) "
       "+ 20+ live fires 23:05->03:55 all rc-clean incl hop logic exercised; MSG-034x W275 seat informational (owner=bm-c, zero "
       "bm-a obligation); MSG-2355 slots census = hardware-seat informational; all three moved to processed/; (7) S6 chain 43 rc-lines "
       "(42 legs + live_paper) ALL rc0 bad=0 (r1070 face clone verbatim; MF leg rc0 = gate-level, standing-blocked face per r1070 "
       "adjudication day-14); quad green (loop pin=8 no-op next fire 04:18 + watchdog present + claws both reinstalled LF-normalized); "
       "(8) watchdog S4U XML flip access-denied = carried C-20261016-04 (elevation window pending)")

VERDICT = ("GREEN: r1071 product round -- A2 G4 PnL-attribution daily ledger LANDED early (deadline <=10-23): daily_report section 七 "
           "live-fire 40 accounts +37,017.40 CNY day ledger with sleeve/leg attribution + selftest legs + audit streak counter=1; "
           "S6 43/43 rc0; smoke 49/49; board CLEAN 105/114/0; D-19 ord consumed 04050fda dec hold; satengine alive; orphan 0/20; "
           "canon-traps MSG verified-immune receipted; product score = 2-point (runnable+visible attribution ledger)")

NEXT = ("r1072: (1) A3 G1+G2 runtime-side enforcement (plan sec.III A3, <=10-24): autofill.py CLOSED_FAMILIES hard-reject before ignite "
        "+ in-pool budget_cap runtime tick auto-DISABLE with exposure; two selftest assertions + one live-fire intercept evidence; "
        "(2) A2 streak watch (>=3 trading days by ~10-21; V2 acceptance 5 days by 10-31); (3) W275 chain watch on bm-c lane (zero "
        "bm-a obligation until a seat names bm-a); (4) BmaIdleGuard v2 scheduled fires observation continues; (5) council sec.6 first "
        "ruling table watch <=10-20 12:00; (6) E20 three-axis synthesis = GM/council signature reserved face; (7) construction-plan "
        "committee report <=10-25; (8) month-boundary first exam 10-31; (9) next 5x HANDOVER = bm-a r1075")

ARTIFACT = ("scripts/daily_report.py (G4 attribution ledger, live-fire rc0) + scripts/automation_line_audit.py (streak evidence face) + "
            "docs/daily_report/REPORT-2026-10-19.md/.json (section 七 + JSON twin) + results/_r1071bma_s6chain_rc.log 43 rc0")

VERIFY = ("results/_r1071bma_s6chain_rc.log 43 rc-lines all rc0 bad=0 + daily_report selftest PASS (attribution legs) + audit selftest "
          "PASS + REPORT-2026-10-19.md section 七 (40 accounts, grand +37,017.40, asof-note honest) + audit E4 evidence "
          "pnl_attribution_streak_days=1 + orders_ack_scan CLEAN 105/114/0 + D-19 advance read-back equality (ord 04050fda, mirrors 5) + "
          "smoke 49/49 + orphan probe 0/20 + guard v2 live fires 23:05->03:55 rc-clean")

NOTE = ("r1071: (1) NEW pit-nuance (state-notes face per CODELY 10KB budget law): Invoke-SilentExe -ArgString passes embedded "
        "single-quotes to git as LITERAL characters -- git stash drop 'stash@{0}' via wrapper = \"not a valid reference\"; correct "
        "channels = python subprocess argv (used) or wrapper with unquoted arg tokens; r1058 'always quote the stash ref' law "
        "holds for DIRECT PS invocation only, not through the wrapper ArgString; (2) S0 pull first attempt 'no such ref fetched' "
        "promisor-window transient (2026-10-15 family) -- direct git fetch rc0 then rebase --autostash = recovery recipe, zero "
        "manual index surgery; (3) summary-line rc=0 false-positive in crude log parse (regex ^name rc=digits excludes it) "
        "-- chain evidence face = LEG_RC_LINES count, not substring match")

# ---------------- state file ----------------
sp = os.path.join(ROOT, "state-bm-a.json")
st = json.load(io.open(sp, encoding="utf-8"))
st.update({
    "round_no": 1072, "round": 1071, "loop_round": 1071,
    "last_round": "r1071", "last_round_label": "r1071",
    "last_round_at": TS, "last_round_ts": TS, "last_round_closed": TS,
    "last_run": TS, "last_seen": TS, "ts": TS, "updated": TS, "updated_at": TS,
    "now_active": "bm-a loop r1071 closeout (A2 G4 PnL-attribution ledger product round)",
    "current": "r1071: A2 G4 PnL-attribution daily ledger product round -- landed early (deadline <=10-23)",
    "current_task": "r1071: A2 G4 attribution ledger + S6 chain + D-19 consumption product round",
    "task": "r1071: A2 G4 attribution ledger product round",
    "did": DID, "last_action": DID, "last_action_at": TS,
    "last_artifact": ARTIFACT, "latest_artifact": ARTIFACT, "recent_artifact": ARTIFACT,
    "next": NEXT, "next_milestone": ("A3 G1+G2 runtime-side enforcement <=10-24; A2 attribution streak >=3 trading days by ~10-21; "
                                      "construction-plan committee report <=10-25; month-boundary first exam 10-31"),
    "verdict": VERDICT, "verify": VERIFY,
    "heartbeat_epoch_utc": EPOCH, "last_heartbeat_epoch_utc": st.get("heartbeat_epoch_utc", EPOCH - 3600),
    "clock_read": TS,
    "idle_rounds": 0, "agenda_starved": False,
    "orphan_face": 0, "orphan_faces": 0, "orphan_killed": 0,
    "free_ram_gb": ram_free_gb, "ram_free_gb": ram_free_gb, "idle_ram_gb": ram_free_gb,
    "ram_free_mb": free_mb, "idle_ram_mb": free_mb,
    "ram_free_pct": round(100 - load_pct, 1) if load_pct else None,
    "ram_load_pct": load_pct,
    "gpu_free_vram_mb": vram_free,
    "last_orders_at": TS, "last_decisions_at": TS,
    "last_decisions_seen": "r1071: D-19 dec HOLD 8706acd8 (zero delta)",
    "last_orders_seen": ("r1071: D-19 ord delta consumed (e695556b -> 04050fda; 10-19 02:18 V5.9 receipt row = BigStream domain, "
                         "bm-a interactive executed, zero loop obligation; dec 8706acd8 hold); fleet board CLEAN 105/114/0; "
                         "canon-traps MSG verified-immune receipted; W275 seat informational; slots census informational"),
    "orders_ack_note": ("r1071: zero NEW fleet orders this window (board CLEAN 105/114/0); D-19 group ord delta consumed via --advance; "
                        "inbox 3 MSGs consumed (canon-traps receipt + W275 seat + slots census) -> processed/"),
    "d19_watermark_guard_round_ref": 1071,
})
st["notes_r1071"] = NOTE
with io.open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# ---------------- heartbeat ----------------
hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
hb = json.load(io.open(hp, encoding="utf-8"))
hb.update({
    "last_seen": TS, "ts": TS, "clock_read": TS,
    "heartbeat_epoch_utc": EPOCH, "heartbeat_epoch_utc_type_int": True,
    "current_task": "r1071: A2 G4 PnL-attribution ledger landed early; S6 43/43 rc0",
    "last_artifact": ARTIFACT,
    "cpu_cores": 32,
    "idle_ram_gb": ram_free_gb, "free_ram_gb": ram_free_gb,
    "gpu_free_vram_mb": vram_free,
    "verdict": VERDICT,
    "idle_rounds": 0, "agenda_starved": False,
})
with io.open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# ---------------- round report (S5) ----------------
rp = os.path.join(ROOT, "round_reports-bm-a.md")
line = ("{ts} | r1071 | 产品轮：A2 G4 盈亏归因日账面提前落地（死线 <=10-23）——daily_report 增 section 七归因节"
        "（40 账户·日 PnL 总计 +37,017.40 CNY·asof 10-16 诚实注记·六员/AGGR 20/ALLOC 7/GRID 5/SYSV1 路由腿全归因·零缺数据）"
        "+ selftest 腿 PASS + 审计面 streak 读数=1（E4 判据语义不动）；S0 吸收 13 commit（bm-c W274 全链收口+W275 席发布）；"
        "D-19 ord 增量消费（04050fda·V5.9 回执=他司域零义务）dec hold；canon 双坑 MSG 代码级复核=v2 构造性免疫回执；"
        "S6 43/43 rc0 bad=0；孤儿面 0/20 | 证据=results/_r1071bma_s6chain_rc.log 43 rc0 + daily_report selftest PASS + "
        "audit selftest PASS + REPORT-2026-10-19.md section 七 + audit E4 streak=1 + orders_ack CLEAN 105/114/0 + D-19 advance "
        "read-back equality + smoke 49/49 | 下轮=r1072：A3 G1+G2 运行侧执法（<=10-24·autofill CLOSED_FAMILIES 硬拒+budget_cap "
        "tick 自动停）；A2 streak 观察至 >=3 交易日；5x HANDOVER=r1075\n").format(ts=TS)
with io.open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write(line)

print("state+heartbeat+report written; epoch=%d type=%s ram_free_gb=%s vram=%s"
      % (EPOCH, isinstance(EPOCH, int), ram_free_gb, vram_free))
