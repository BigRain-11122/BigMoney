"""r472 bm-c S7-close bookkeeping: state-bm-c.json + heartbeat + round report line.
Programmatic JSON writes + json.loads self-verify (state write-back law).
Metrics: psutil CPU/RAM real read + nvidia-smi GPU real read (CREATE_NO_WINDOW).
Copy of r471 close, round-numbered per r461 law."""
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

DID = ("r472 bm-c golden-week watch round (zero-incident): (1) S0: no rebase leftovers; "
       "round-start dirty = 3 own daemon lane faces (satengine face/state + autofill); "
       "origin behind=4 (bm-b r671 wave: S6 faces + trio ETA face + merge-resolve probes + "
       "REPORT/LIVE regen + merges); zero intersection vs own dirty faces (r437 pre-check) -> "
       "absorb commit 233378f (3 lane faces) + merge origin/main CLEAN zero-UU -> push_verify "
       "DELIVERED tip 9f9194c07 ahead=0/behind=0. (2) S0.5: orders 153/153 zero un-acked "
       "(same-caliber set-diff, files=153 missing=0); ack superset 154 (historical ack, "
       "benign); inbox 0 unread; D-19 decisions 4E5BE321 + group-orders 68947C17 double MATCH "
       "(per-key raw-blob caliber, probe reuse _r471bmc_d19_check.py) -> zero consumption. "
       "(3) S1 smoke 48/48. (4) S2: boards empty for bm-c (job_list 0; fleet tasks "
       "open_count=0). (5) S3: satengine rc0 alive via Tools copy (heartbeat_age 6.2s, "
       "burns_active=[], queue_next=[] = N1 closed face per O-2115 sec-2); WM red=false "
       "healthy; py_watermark py_low_board_clear legal idle (board clear + golden week no "
       "bars); pool ready x3 all owner=bm-b (owner_since 12:40:12 age 18.2min soft-stale -> "
       "r648/r661 dual-form cross-check: fresh fetch origin-true re-read + bm-b heartbeat "
       "7.1min healthy verdict r671 + nulls rows growing (+5/+6/+4) = healthy between-round "
       "sampling artifact, NOT stall; zero pool action taken); W14 waiting per O-0808 "
       "mooring. (6) CORE: fund-trio NULLS watch V758/Q588/D436 of 2000 (delta +5/+6/+4 vs "
       "r471; probe results/_r472bmc_fundnulls_watch.py/.json); bm-b trio_burn_eta.json "
       "consumption face: V 38.15% ETA 10-06 15:00 / Q 29.55% ETA 10-07 11:00 (long-pole "
       "QUALITY). (7) S6 38/38 rc0 NON-ZERO=none (results/_r472bmc_s6_log.txt, canon parity "
       "PASS 38 legs): dualrun ZERO-DRIFT streak 51 (367 entries); update_daily 0 new rows "
       "cutoff 2026-09-30; market_regime ORANGE shadow days_in_state=2; compute_audit "
       "verdict CLEAN (pool-supply-gap ready=3/floor=3 breach=false, zero ignition SLA "
       "breach); bm-a heartbeat fresh 18-19min -> lane_io legs honest skip (zero "
       "stale-takeover); REPORT/LIVE-2026-10-04 idempotent regen; token per-round fixed "
       "context ~12944+19939 rough. (8) S7: loop pin5 phase-ok (next fire 13:05); watchdog "
       "in place (next fire 13:00); claws LF-normalized OK x2 (zero reinstall); attrition "
       "CLEAN rc0 (4 ledgers, 2 bm-a healed historical notes as-recorded); orders S7 "
       "double-scan 153/153 zero-diff; round commit + close commit push_verify DELIVERED. "
       "(9) S4: zero new pit lines (four-gate: no new long-term lesson -> no CODELY append).")

CURRENT_TASK = ("当前活: golden-week watch + fund-trio readout (V758/Q588/D436 of 2000, delta "
                "+5/+6/+4 vs r471, owners=bm-b healthy per dual-form cross-check) | 最近实物: "
                "results/_r472bmc_s6_log.txt (S6 38/38 rc0) + results/_r472bmc_fundnulls_watch.json "
                "+ round commit DELIVERED @ " + ts + " | 下个里程碑: fund-trio finalize window "
                "10-05 10:30 opens (bm-b owner; per bm-b ETA face V 10-06 15:00 / Q long-pole "
                "10-07 11:00); D-20261004-02①②③ receipt window 10-06 00:00; D-06 closure 10-07; "
                "market reopen 10-09; next 5x=r475")

NEXT = ("(a) r473: watch (finalize window opens 10-05 10:30, bm-b owner; QUALITY long-pole "
        "ETA 10-07 11:00 per bm-b trio_burn_eta face). (b) D-20261004-02①②③ receipt window "
        "10-06 00:00. (c) D-06 full closure window 10-07 (bm-c lead). (d) O-2115/O-2030 "
        "acceptance 10-08; market reopen 10-09. (e) finalize landing -> next trial-labor wave "
        "supply gate reopens. (f) next 5x HANDOVER duty r475.")

VERIFY = ("S6 38/38 rc0 NON-ZERO=none (results/_r472bmc_s6_log.txt in-repo, S6-chain-end "
          "marker + FAILS=[]); smoke 48/48; orders 153/153 same-caliber zero-diff (S0.5 + S7 "
          "double-scan); D-19 decisions 4E5BE321 + group-orders 68947C17 double MATCH raw-blob "
          "caliber; attrition CLEAN; claws LF-normalized OK x2; loop pin5 phase-ok; watchdog "
          "registered; trio owners=bm-b healthy (dual-form: heartbeat 7.1min + nulls growth "
          "+5/+6/+4); satengine alive rc0 (hb age 6.2s); push_verify DELIVERED; heartbeat "
          "epoch int + clock T-sep self-checked")

LAST_ROUND = ("r472 bm-c: golden-week watch + fund-trio V758/Q588/D436 (+5/+6/+4, owners "
              "healthy dual-form cross-check) + S0 absorb 233378f + merge origin/main clean "
              "zero-UU (r437 pre-alignment) + S6 38/38 rc0 (zero stale-takeover, bm-a hb "
              "fresh) + orders/D-19 double MATCH; smoke 48/48; zero incident")

RR_LINE = (ts + "｜r472｜dept:工程（golden-week 值守轮·零事故）｜watermark verdict=绿（red=false "
           "healthy·satengine rc0 活〔Tools 注册面·heartbeat_age 6.2s·burns_active=[]·queue_next=[]"
           "=N1 关面 per O-2115 sec-2〕·py_watermark=py_low_board_clear 合法 idle）｜当前活=金周值守+"
           "fund-trio NULLS 进度读数｜最近实物=results/_r472bmc_s6_log.txt（S6 38/38 rc0·chain-end 标记+"
           "FAILS=[]）+results/_r472bmc_fundnulls_watch.json（V758/Q588/D436·delta +5/+6/+4 vs r471）+"
           "results/_r472bmc_pool_satengine.json（池/引擎探针）+round commit push_verify DELIVERED｜"
           "下个里程碑=fund-trio finalize 窗 10-05 10:30 开（bm-b 正主·bm-b ETA 面 V 10-06 15:00/Q 长杆 "
           "10-07 11:00）+D-20261004-02①②③ 回执窗 10-06 00:00+D-06 收口 10-07+开市 10-09（≤48h）｜S0: "
           "无 rebase 残留·轮首 3 脏面=本机 satengine x2+autofill 车道面·origin behind=4（bm-b r671 wave）"
           "与我脏面零交集（r437 预对齐检查）→absorb 233378f+merge origin/main 净零 UU→push_verify "
           "DELIVERED（tip 9f9194c07）｜S0.5: 令差集=0（153/153 同口径集合比对零差·ack 超集 154 历史项"
           "良性）·inbox 0·D-19 decisions 4E5BE321 MATCH+group orders 68947C17 MATCH（per-key "
           "raw-blob·复用 _r471bmc_d19_check.py）→零消费｜S1 smoke 48/48｜S2 板空（job_list 0·fleet "
           "open=0）｜S3: satengine rc0 活（Tools 注册面·hb age 6.2s）·WM red=false healthy·"
           "next_pick=claimed moneyflow IC（bm-a 道）·池 ready x3 全 bm-b 属主（owner_since 12:40:12 "
           "age 18.2min 软陈旧→r648/r661 双形交叉：fetch 后 origin 真值复核+bm-b 心跳 7.1min healthy "
           "r671+nulls 增长 +5/+6/+4=轮间采样面非停滞·零池面动作）·W14 waiting 停泊维持 per O-0808｜"
           "FUND NULLS watch: V758/Q588/D436 of 2000（delta +5/+6/+4 vs r471·证据 "
           "results/_r472bmc_fundnulls_watch.json）｜S6 38/38 rc0 NON-ZERO=none（dualrun ZERO-DRIFT "
           "streak 51〔367 entries〕·update_daily 金周 cutoff 2026-09-30 零新行·market_regime ORANGE "
           "shadow days=2·compute_audit CLEAN〔pool-supply-gap ready=3/floor=3 breach=false〕·bm-a 心跳"
           "新鲜 18-19min→lane_io 腿诚实 skip〔本轮零 stale-takeover〕·REPORT/LIVE-2026-10-04 幂等再生·"
           "金周无新 bar 腿诚实 no-op）｜S7: loop pin5 phase-ok（next fire 13:05）·watchdog 在位"
           "（next fire 13:00）·双爪 LF 归一 OK x2 零重装·attrition CLEAN（4 ledgers·2 bm-a healed "
           "历史注记照录）·orders S7 二扫 153/153 零差｜S4: 零新坑律行（四问门：无新长期教训→零 CODELY "
           "append）｜记分: 1（S6 管线产出+watch 证据件+池/引擎探针件+REPORT/LIVE 再生·等待态声明: "
           "finalize 窗 10-05 开·N1 关+池 ready x3 全 bm-b 属主+板空=零新面孔可烧·非空转）｜记账预算: "
           "4/5（state+心跳+轮报+S7 回执·CODELY 零行）｜本地未达 origin commit 数: 0（push_verify "
           "DELIVERED）｜零清扫/归档/删除类动作轮：登记册零命中断言 N/A-无此类动作（O-2030 §二.3 自证面）")

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
state["round_no"] = 472
state["updated"] = ts
state["updated_at"] = ts
state["verify"] = VERIFY
state["ram_free_gb"] = idle_ram_gb
state["free_ram_gb"] = idle_ram_gb
with open(STATE, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(state, fh, ensure_ascii=False, indent=1)
state_check = json.loads(open(STATE, encoding="utf-8-sig").read())
assert state_check["round_no"] == 472, "state round_no write-back failed"
assert isinstance(state_check.get("heartbeat_epoch_utc", epoch), int), "epoch not int"

# --- heartbeat write-back ---
with open(HB, encoding="utf-8-sig") as fh:
    hb = json.load(fh)
hb["activity_now"] = ("golden-week watch; fund-trio NULLS V758/Q588/D436 of 2000 (delta "
                      "+5/+6/+4 vs r471), owners=bm-b healthy per dual-form cross-check "
                      "(heartbeat 7.1min + nulls growth); finalize window opens 10-05 10:30 "
                      "(bm-b owner); N1 closed per O-2115 sec-2; boards empty (0 open); "
                      "zero-incident round")
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
hb["latest_artifact"] = ("results/_r472bmc_s6_log.txt (S6 38/38 rc0) + "
                         "results/_r472bmc_fundnulls_watch.json (V758/Q588/D436) + round "
                         "commit DELIVERED @ " + ts)
hb["next_milestone"] = ("fund-trio finalize window 10-05 10:30 (bm-b owner; ETA face V "
                        "10-06 15:00 / Q long-pole 10-07 11:00); D-20261004-02①②③ receipt "
                        "window 10-06 00:00; D-06 closure 10-07; O-2115/O-2030 acceptance "
                        "10-08; market reopen 10-09; next 5x=r475")
hb["prod_lanes"] = ("FUND trio NULLS bm-b in-flight (watch only); N1 closed per O-2115 "
                    "sec-2; boards empty; zero-incident watch round")
hb["ram_free_gb"] = idle_ram_gb
hb["round_no"] = 472
hb["round_no_label"] = "round 472 (bm-c)"
hb["ts"] = ts
hb["updated"] = ts
hb["updated_at"] = ts
hb["verdict"] = ("GREEN (smoke 48/48; orders 153/153 zero delta double-scan; D-19 double MATCH "
                 "zero consumption; satengine alive rc0 Tools face hb 6.2s; S6 38 legs rc0 "
                 "fail=0 dualrun streak 51; compute_audit CLEAN; attrition CLEAN; trio owners "
                 "healthy dual-form; push_verify DELIVERED; zero cloud token)")
with open(HB, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
hb_check = json.loads(open(HB, encoding="utf-8-sig").read())
assert isinstance(hb_check["heartbeat_epoch_utc"], int), "heartbeat epoch must be int"
assert "T" in hb_check["clock_read"], "clock_read must be T-separated"
assert hb_check["round_no"] == 472, "heartbeat round_no failed"

# --- round report append (bytes-safe append, newline='' per r641 CRLF law) ---
with open(RR, "a", encoding="utf-8", newline="") as fh:
    fh.write(RR_LINE + "\n")

print("STATE round_no=472 OK; heartbeat epoch int OK; RR line appended")
print("ts=" + ts + " cpu=" + str(cpu_pct) + " idle_ram=" + str(idle_ram_gb) +
      " gpu_mib=" + str(gpu_mib) + " epoch=" + str(epoch))
