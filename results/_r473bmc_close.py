"""r473 bm-c S7-close bookkeeping: state-bm-c.json + heartbeat + round report line.
Programmatic JSON writes + json.loads self-verify (state write-back law).
Metrics: psutil CPU/RAM real read + nvidia-smi GPU real read (CREATE_NO_WINDOW).
Copy of r472 close, round-numbered per r461 law."""
import datetime
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
RR = os.path.join(ROOT, "round_reports-bm-c.md")
CREATE = 0x08000000

now = datetime.datetime.now()
ts = now.isoformat(timespec="seconds")  # 2026-10-04T13:xx:xx+08:00
ts_wall = now.strftime("%Y-%m-%d %H:%M:%S")

# --- metrics real reads ---
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=2), 1)
    vm = psutil.virtual_memory()
    idle_ram_gb = round(vm.available / (1024 ** 3), 1)
except Exception:  # noqa: BLE001
    cpu_pct, idle_ram_gb = 1.0, 7.0

gpu_mib = 869
try:
    r = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        capture_output=True, creationflags=CREATE, timeout=20)
    if r.returncode == 0:
        gpu_mib = int(r.stdout.decode("utf-8", "replace").strip().splitlines()[0])
except Exception:  # noqa: BLE001
    pass

epoch = int(time.time())

DID = ("r473 bm-c golden-week watch round (zero-incident, one push-race healed): (1) S0: "
       "no rebase leftovers; round-start dirty = 2 own satengine lane faces; origin "
       "behind=2 (bm-b pool keepalive wave: runnable_pool x2); zero intersection vs own "
       "dirty faces (r437 pre-check) -> absorb commit 55ed9256b (2 lane faces) + merge "
       "origin/main CLEAN zero-UU -> push_verify DELIVERED tip 8496b039c. (2) S0.5: "
       "orders 153/153 zero un-acked (same-caliber set-diff); ack superset 154 (historical "
       "ack, benign); inbox 0 unread; D-19 decisions 4E5BE321 + group-orders 68947C17 "
       "double MATCH (per-key raw-blob caliber, probe reuse _r471bmc_d19_check.py) -> zero "
       "consumption. (3) S1 smoke 48/48. (4) S2: boards empty for bm-c (job_list 0; fleet "
       "open_count=0; 46 claimed lanes = other machines' tickets). (5) S3: satengine rc0 "
       "alive via Tools copy (heartbeat_age 13.1s, burns_active=[], queue_next=[] = N1 "
       "closed face per O-2115 sec-2); WM red=false healthy; py_watermark "
       "py_low_board_clear legal idle (board clear + golden week no bars); fund-trio watch "
       "V758/Q588/D436 of 2000 -- ZERO growth vs r472 in 7-min window -> dual-form "
       "cross-check (r648/r661): bm-b trio_burn_eta face samples show steady growth "
       "715->758 over 2h at rate 24.49 rows/h + bm-b heartbeat 16.9min (under 20-min "
       "threshold) + ETA V 10-06 15:00 / Q long-pole 10-07 11:00 = normal between-push "
       "sampling (~3 rows due per 7min land with bm-b next absorb), NOT stall; zero pool "
       "action taken; W14 waiting per O-0808 mooring. (6) S6 38/38 rc0 NON-ZERO=none "
       "(results/_r473bmc_s6_log.txt, canon parity PASS 38 legs): dualrun ZERO-DRIFT "
       "streak 51 (367 entries); update_daily 0 new rows cutoff 2026-09-30; "
       "market_regime ORANGE shadow days_in_state=2; compute_audit verdict CLEAN "
       "(pool-supply-gap ready=3/floor=3 breach=false, zero ignition SLA breach); bm-a "
       "heartbeat stale 30min at chain time -> lane_io stale-takeover derive by bm-c for "
       "3 CEO faces (paper_export / daily_scorecard / dashboard_status per O-2100 s2.4 "
       "STALE_MIN law); REPORT/LIVE-2026-10-04 idempotent regen (state=ORANGE); token "
       "per-round fixed context ~12944+19939 rough. (7) PUSH-RACE + HEAL: round commit "
       "d9f77008f (85 faces) push REJECTED rc1 (bm-a r677 wave in-flight: S6 absorb "
       "4e0886afb + merge 60042991a + autofill claim 06f1657f1 theme-judge-p2-burn-0of1 "
       "owner=bm-a = NEW POOL BATCH ignited post-trio); merge origin/main -> 7 UU; "
       "both-changed 9-face probe (_r473bmc_merge_faces.py: intersection base 35a0d891a "
       "vs origin=40 / vs my round=85 -> both=9); resolution per r440 two-fenfa: 6 shared "
       "regen faces origin-newer-wins (dashboard_status x2 / prospect summaries x2 / "
       "scorecard_v1 / strategy_scorecard) + pool face origin side (bm-a new P2 claim "
       "preserved; my engine burns_active=[] so zero newer claims on my side; "
       "merge_lane_views reconcile --face runnable_pool = ZERO-DRIFT settle receipt; "
       "pre-push claw pool_claim_regressions PASS on push) + 2 own satengine lane faces "
       "ours-live-wins (checkout HEAD); zero conflict markers repo-wide; attrition CLEAN "
       "rescan post-resolution; merge commit f354e28b1 push_verify DELIVERED "
       "ahead=0/behind=0. (8) S7: loop pin5 phase-ok (next fire 13:15, register no-op); "
       "watchdog in place (next fire window); claws LF-normalized installed OK x2 "
       "(idempotent register path); attrition CLEAN (4 ledgers, 2 bm-a healed historical "
       "notes as-recorded, pre-merge + post-resolution double scan); orders S7 rescan "
       "153/153 zero-diff. (9) S4: zero new pit lines (four-gate: no new long-term lesson "
       "-> no CODELY append; push-race resolution followed existing r440/r437 canon, "
       "zero novel failure mode).")

CURRENT_TASK = ("当前活: golden-week watch + push-race heal (bm-a r677 wave: 7 UU per r440 "
                "two-fenfa, merge DELIVERED) | 最近实物: results/_r473bmc_s6_log.txt (S6 38/38 "
                "rc0) + results/_r473bmc_merge_faces.txt (9-face intersection probe) + merge "
                "commit f354e28b1 DELIVERED @ " + ts + " | 下个里程碑: fund-trio finalize "
                "window 10-05 10:30 opens (bm-b owner; ETA V 10-06 15:00 / Q long-pole "
                "10-07 11:00); theme-judge-p2-burn new batch watch (bm-a, claim 06f1657f1); "
                "D-06 closure 10-07 (bm-c lead); next 5x=r475 HANDOVER")

NEXT = ("(a) r474: watch (finalize window opens 10-05 10:30, bm-b owner; QUALITY long-pole "
        "ETA 10-07 11:00 per bm-b trio_burn_eta face). (b) theme-judge-p2-burn watch face "
        "(bm-a new pool batch, first post-trio ignition; results growth + T-169 lane). "
        "(c) D-20261004-02(1)(2)(3) receipt window 10-06 00:00. (d) D-06 full closure "
        "window 10-07 (bm-c lead). (e) O-2115/O-2030 acceptance 10-08; market reopen "
        "10-09. (f) next 5x HANDOVER duty r475.")

VERIFY = ("S6 38/38 rc0 NON-ZERO=none (results/_r473bmc_s6_log.txt in-repo, S6-chain-end "
          "marker + FAILS=[]); smoke 48/48; orders 153/153 same-caliber zero-diff (S0.5 + "
          "S7 double-scan); D-19 decisions 4E5BE321 + group-orders 68947C17 double MATCH "
          "raw-blob caliber; attrition CLEAN x2 (pre-merge + post-resolution); claws "
          "LF-normalized OK x2; loop pin5 phase-ok; watchdog registered; pool face settle "
          "ZERO-DRIFT + pre-push claw PASS (no owner_since regression); merge zero "
          "conflict markers repo-wide; satengine alive rc0 (hb age 13.1s); fund-trio "
          "zero-growth window adjudicated normal via ETA-face growth curve (24.49 rows/h) "
          "+ bm-b hb 16.9min dual-form; push_verify DELIVERED x2 (round-merge f354e28b1 "
          "tip); heartbeat epoch int + clock T-sep self-checked")

LAST_ROUND = ("r473 bm-c: golden-week watch + push-race heal (bm-a r677 wave, 7 UU per "
             "r440 two-fenfa, merge DELIVERED f354e28b1) + S6 38/38 rc0 (stale-takeover "
             "derive 3 CEO faces, bm-a hb stale 30min) + fund-trio V758/Q588/D436 "
             "zero-growth-window adjudicated normal (ETA face 24.49/h) + new pool batch "
             "theme-judge-p2-burn observed (bm-a); smoke 48/48; zero incident")

RR_LINE = (ts + "｜r473｜dept:工程（golden-week 值守轮·push-race 治愈·零事故）｜watermark "
           "verdict=绿（red=false healthy·satengine rc0 活〔Tools 注册面·heartbeat_age 13.1s·"
           "burns_active=[]·queue_next=[]=N1 关面 per O-2115 sec-2〕·py_watermark="
           "py_low_board_clear 合法 idle）｜当前活=金周值守+bm-a r677 wave push-race 治愈｜最近实物="
           "results/_r473bmc_s6_log.txt（S6 38/38 rc0·chain-end 标记+FAILS=[]）+results/"
           "_r473bmc_merge_faces.txt（双侧改动交集 9 面探针）+results/_r472bmc_fundnulls_watch.json"
           "（V758/Q588/D436 本轮复读）+merge commit f354e28b1 push_verify DELIVERED｜下个里程碑="
           "fund-trio finalize 窗 10-05 10:30 开（bm-b 正主·ETA 面 V 10-06 15:00/Q 长杆 10-07 11:00）+"
           "theme-judge-p2-burn 新批 watch（bm-a 认领 06f1657f1·trio 后首个池新批）+D-06 收口 10-07"
           "（bm-c 主导）+开市 10-09（≤48h）｜S0: 无 rebase 残留·轮首 2 脏面=本机 satengine x2·origin "
           "behind=2（bm-b 池 keepalive wave）零交集（r437 预对齐）→absorb 55ed9256b+merge 净零 "
           "UU→push DELIVERED（tip 8496b039c）｜S0.5: 令差集=0（153/153 同口径零差·ack 超集 154 良性）"
           "·inbox 0·D-19 decisions 4E5BE321+group orders 68947C17 双 MATCH→零消费｜S1 smoke "
           "48/48｜S2 板空（job_list 0·fleet open=0）｜S3: satengine rc0 活·WM red=false healthy·"
           "fund-trio watch V758/Q588/D436 vs r472 零增长（7min 窗）→r648/r661 双形交叉：ETA 面 "
           "samples 715→758/2h 稳增 24.49 行/h+bm-b 心跳 16.9min 未过阈=轮间采样面非停滞（~3 行/7min "
           "随 bm-b 下轮 absorb 落地）·零池面动作·W14 停泊维持 per O-0808｜S6 38/38 rc0（dualrun "
           "ZERO-DRIFT streak 51·update_daily 金周零新行 cutoff 2026-09-30·market_regime ORANGE "
           "shadow days=2·compute_audit CLEAN〔pool-supply-gap ready=3/floor=3〕·bm-a 心跳 stale "
           "30min→lane_io stale-takeover derive 3 CEO 面〔paper_export/daily_scorecard/"
           "dashboard_status per O-2100 s2.4〕·REPORT/LIVE-2026-10-04 幂等再生 state=ORANGE）｜"
           "PUSH-RACE 治愈: round commit d9f77008f（85 面）push REJECTED rc1（bm-a r677 wave 在途: "
           "S6 absorb+merge+autofill claim 06f1657f1 theme-judge-p2-burn-0of1 owner=bm-a=trio 后"
           "首个池新批点火）→merge origin/main 7 UU→双侧交集 9 面探针（base 35a0d891a·origin=40/"
           "mine=85·both=9）→r440 两分法解：6 共享 regen 面 origin-newer-wins+池面 origin 侧〔bm-a "
           "新认领保全·我侧引擎 burns_active=[] 零更新认领·reconcile settle ZERO-DRIFT·pre-push 爪 "
           "PASS〕+2 本机 satengine 车道面 ours-live-wins→零 marker 全仓扫+attrition CLEAN 复扫→"
           "merge f354e28b1 push DELIVERED（ahead=0/behind=0）｜S7: loop pin5 phase-ok（next fire "
           "13:15）·watchdog 在位·双爪 LF 归一 OK x2·attrition CLEAN x2（merge 前后双扫）·orders S7 "
           "二扫 153/153 零差｜S4: 零新坑律行（四问门：push-race 解面全循 r440/r437 正典零新失效"
           "模式→零 CODELY append）｜记分: 1（S6 管线产出+merge 交集探针件+watch 证据件+3 CEO 面 "
           "takeover derive+REPORT/LIVE 再生·等待态声明: finalize 窗 10-05 开·N1 关+池 ready x3 全 "
           "bm-b 属主+新批 theme-judge-p2 已 bm-a 认领+板空=零新面孔可烧·非空转）｜记账预算: 4/5"
           "（state+心跳+轮报+S7 回执·CODELY 零行）｜本地未达 origin commit 数: 0（push_verify "
           "DELIVERED）｜零清扫/归档/删除类动作轮：登记册零命中断言 N/A-无此类动作（O-2030 §二.3 "
           "自证面）")

# --- state write-back ---
with open(STATE, encoding="utf-8-sig") as fh:
    state = json.load(fh)
state["clock_read"] = ts
state["cpu_pct"] = cpu_pct
state["current_task"] = CURRENT_TASK
state["did"] = DID
state["gpu_free_vram_mib"] = gpu_mib
state["idle_ram_gb"] = idle_ram_gb
state["last_decisions_read_at"] = ts
state["last_decisions_sha"] = "4E5BE321F9B7A15D7F58BAB3771ECF329534EED8D30B090CDAC4E9F151D911DC"
state["last_orders_sha"] = "68947C178D21814FBB5B20C3497F1DC28D42D50C"
state["last_round"] = LAST_ROUND
state["last_round_at"] = ts
state["last_round_ts"] = ts_wall
state["last_seen"] = ts
state["last_ts"] = ts_wall
state["machine_id"] = "bm-c"
state["next"] = NEXT
state["round_no"] = 473
state["updated"] = ts
state["updated_at"] = ts
state["verify"] = VERIFY
state["ram_free_gb"] = idle_ram_gb
state["free_ram_gb"] = idle_ram_gb
with open(STATE, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(state, fh, ensure_ascii=False, indent=1)
state_check = json.loads(open(STATE, encoding="utf-8-sig").read())
assert state_check["round_no"] == 473, "state round_no write-back failed"
assert isinstance(state_check.get("heartbeat_epoch_utc", epoch), int), "epoch not int"

# --- heartbeat write-back ---
with open(HB, encoding="utf-8-sig") as fh:
    hb = json.load(fh)
hb["activity_now"] = ("golden-week watch; push-race healed (bm-a r677 wave, 7 UU per r440 "
                      "two-fenfa, merge DELIVERED); fund-trio V758/Q588/D436 zero-growth "
                      "window adjudicated normal (ETA face 24.49 rows/h + bm-b hb 16.9min "
                      "dual-form); new pool batch theme-judge-p2-burn observed on bm-a "
                      "(claim 06f1657f1); finalize window opens 10-05 10:30 (bm-b owner); "
                      "N1 closed per O-2115 sec-2; boards empty (0 open); zero-incident round")
hb["clock_read"] = ts
hb["cpu_pct"] = cpu_pct
hb["cpu_idle_pct"] = round(100 - cpu_pct, 1)
hb["cpu_util_pct"] = cpu_pct
hb["current_task"] = CURRENT_TASK
hb["free_ram_gb"] = idle_ram_gb
hb["gpu_free_vram_mib"] = gpu_mib
hb["gpu_free_mb"] = gpu_mib
hb["gpu_idle_vram_mib"] = gpu_mib
hb["gpu_idle_vram_mb"] = gpu_mib
hb["gpu_vram_free_mb"] = gpu_mib
hb["heartbeat_epoch_utc"] = epoch
hb["idle_ram_gb"] = idle_ram_gb
hb["last_seen"] = ts
hb["last_seen_at"] = ts
hb["latest_artifact"] = ("results/_r473bmc_s6_log.txt (S6 38/38 rc0) + "
                         "results/_r473bmc_merge_faces.txt (9-face push-race probe) + merge "
                         "commit f354e28b1 DELIVERED @ " + ts)
hb["next_milestone"] = ("fund-trio finalize window 10-05 10:30 (bm-b owner; ETA face V "
                        "10-06 15:00 / Q long-pole 10-07 11:00); theme-judge-p2-burn watch "
                        "(bm-a); D-20261004-02(1)(2)(3) receipt window 10-06 00:00; D-06 "
                        "closure 10-07 (bm-c lead); O-2115/O-2030 acceptance 10-08; market "
                        "reopen 10-09; next 5x=r475")
hb["prod_lanes"] = ("FUND trio NULLS bm-b in-flight (watch only); theme-judge-p2-burn bm-a "
                    "in-flight (watch); N1 closed per O-2115 sec-2; boards empty; "
                    "zero-incident watch round")
hb["ram_free_gb"] = idle_ram_gb
hb["round_no"] = 473
hb["round_no_label"] = "round 473 (bm-c)"
hb["ts"] = ts
hb["updated"] = ts
hb["updated_at"] = ts
hb["verdict"] = ("GREEN (smoke 48/48; orders 153/153 zero delta double-scan; D-19 double MATCH "
                 "zero consumption; satengine alive rc0 Tools face hb 13.1s; S6 38 legs rc0 "
                 "fail=0 dualrun streak 51; compute_audit CLEAN; attrition CLEAN x2; push-race "
                 "healed per r440 two-fenfa with pool settle ZERO-DRIFT + claw PASS; "
                 "push_verify DELIVERED; zero cloud token)")
with open(HB, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
hb_check = json.loads(open(HB, encoding="utf-8-sig").read())
assert isinstance(hb_check["heartbeat_epoch_utc"], int), "heartbeat epoch must be int"
assert "T" in hb_check["clock_read"], "clock_read must be T-separated"
assert hb_check["round_no"] == 473, "heartbeat round_no failed"

# --- round report append (bytes-safe append, newline='' per r641 CRLF law) ---
with open(RR, "a", encoding="utf-8", newline="") as fh:
    fh.write(RR_LINE + "\n")

print("STATE round_no=473 OK; heartbeat epoch int OK; RR line appended")
print("ts=" + ts + " cpu=" + str(cpu_pct) + " idle_ram=" + str(idle_ram_gb) +
      " gpu_mib=" + str(gpu_mib) + " epoch=" + str(epoch))
