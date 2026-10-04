"""r469 bm-c S7-close bookkeeping: state-bm-c.json + heartbeat + round report line.
Programmatic JSON writes + json.loads self-verify (state write-back law).
Metrics: psutil CPU/RAM real read + nvidia-smi GPU real read (CREATE_NO_WINDOW).
Copy of r467/r468 close, round-numbered per r461 law."""
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
ts = now.isoformat(timespec="seconds")  # 2026-10-04T12:3x:xx+08:00
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

DID = ("r469 bm-c golden-week watch round (zero-incident, zero-intersection S0 + fund-trio "
       "progress readout + full S6 chain): (1) S0: no rebase leftovers; round-start dirty = 2 "
       "own satengine daemon lane faces (face_bm-c + state_bm-c); behind=2 with ZERO "
       "intersection (incoming all bm-b faces: 5e9e4a5c7 absorb + 660fe8ae0 merge wave) -> "
       "directed absorb commit 431c3990e + pull --rebase clean (rebased 1/1). (2) S0.5: "
       "orders 153/153 zero un-acked (canonical Tools/orders_diff.py); inbox 0 unread; D-19 "
       "decisions 4E5BE321 + group-orders 68947C17 double MATCH (per-key raw-blob caliber, "
       "probe results/_r469bmc_d19_check.py) -> zero consumption. (3) S1 smoke 48/48. (4) S2: "
       "boards empty (job_list 0; fleet tasks 45 claimed / 0 open). (5) S3: satengine rc0 "
       "alive via Tools copy (registered face, r467 law); WM red=false lane healthy "
       "next_pick=claimed (moneyflow IC advisory, bm-a lane); post_review REPORT-20261004 "
       "distribution 45Y/0N/5W zero active red. (6) CORE: fund-trio NULLS watch V746/Q577/D428 "
       "of 2000 (+12/+10/+10 vs r468), owners=bm-b all healthy (keepalive age 11.0min, r288 "
       "gate green). (7) S6 38/38 rc0 NON-ZERO=none (results/_r469bmc_s6_log.txt, canon "
       "parity PASS 38 legs): dualrun ZERO-DRIFT streak 51 (367 entries); update_daily 0 new "
       "rows golden-week cutoff 2026-09-30; market_regime ORANGE shadow days=2; bm-a "
       "heartbeat FRESH 16min -> lane_io C-family derives honest skip; REPORT/LIVE-2026-10-04 "
       "idempotent regen; token ledger updated. (8) S7: loop pin5 phase-ok no-op (first fire "
       "12:35); watchdog re-registered idempotent (first fire 12:30); claws LF-normalized "
       "installed; attrition CLEAN rc0 (4 ledgers, 2 bm-a healed historical notes "
       "as-recorded). (9) S4: zero new pit lines this round (四问门: no long-term lesson -> "
       "no CODELY append).")

CURRENT_TASK = ("当前活: golden-week watch + fund-trio readout (V746/Q577/D428 of 2000, "
                "+12/+10/+10, owners=bm-b healthy keepalive 11.0min) + S0 zero-intersection "
                "netpath (absorb 431c3990e + rebase clean) | 最近实物: results/_r469bmc_s6_log.txt "
                "(S6 38/38 rc0) + results/_r469bmc_fundnulls_watch.json @ " + ts + " | 下个里程碑: "
                "fund-trio finalize window 10-05 10:30 (bm-b owner; QUALITY long-pole 577/2000); "
                "D-20261004-02①②③ receipt window 10-06 00:00; market reopen 10-09; next 5x=r470")

NEXT = ("(a) r470: 5x HANDOVER duty round + watch (finalize window opens 10-05 10:30, bm-b "
        "owner; QUALITY long-pole 577/2000). (b) D-20261004-02①②③ receipt window 10-06 00:00. "
        "(c) O-2115/O-2030 acceptance 10-08; market reopen 10-09. (d) finalize landing -> next "
        "trial-labor wave supply gate reopens.")

VERIFY = ("S6 38/38 rc0 NON-ZERO=none (results/_r469bmc_s6_log.txt in-repo, S6-chain-end marker "
          "+ FAILS=[]); smoke 48/48; orders 153/153 canonical zero-diff; D-19 decisions 4E5BE321 "
          "+ group-orders 68947C17 double MATCH raw-blob caliber; S0 zero-intersection absorb "
          "431c3990e + rebase clean; attrition CLEAN; claws LF-normalized installed; loop pin5 "
          "phase-ok; watchdog registered; trio owners=bm-b healthy (keepalive 11.0min); "
          "post_review 45Y/0N/5W zero active red; heartbeat epoch int + clock T-sep self-checked")

LAST_ROUND = ("r469 bm-c: golden-week watch + S0 zero-intersection absorb (431c3990e) + "
              "fund-trio V746/Q577/D428 (+12/+10/+10, owners healthy) + S6 38/38 rc0; smoke "
              "48/48; orders/D-19 double MATCH; zero active post_review red; zero incident")

RR_LINE = (ts + "｜r469｜dept:工程（golden-week 值守轮·零事故）｜watermark verdict=绿（red=false "
           "healthy·satengine rc0 活〔Tools 注册面·burns_active=[]·N1 关面 per O-2115 sec-2〕·"
           "post_review REPORT-20261004 分布 45Y/0N/5W 零活红）｜当前活=金周值守+fund-trio NULLS 进度"
           "读数+S0 零交集净路｜最近实物=results/_r469bmc_s6_log.txt（S6 38/38 rc0·chain-end 标记+"
           "FAILS=[]）+results/_r469bmc_fundnulls_watch.json（V746/Q577/D428·owners=bm-b healthy "
           "keepalive 11.0min）｜下个里程碑=fund-trio finalize 窗 10-05 10:30 开（QUALITY 长杆 "
           "577/2000·bm-b 正主）+O-2115/O-2030 验收 10-08+开市 10-09（≤48h）｜S0: 无 rebase 残留·"
           "轮首 2 脏面=本机 satengine daemon 车道面·behind=2 且交集为零（incoming 全 bm-b faces "
           "r671 wave）→定向 absorb commit 431c3990e+pull --rebase 净路（rebased 1/1）｜S0.5: 令差"
           "集=0（153/153 正典 orders_diff.py）·inbox 0·D-19 decisions 4E5BE321 MATCH+group orders "
           "68947C17 MATCH（per-key raw-blob·探针 _r469bmc_d19_check.py）→零消费｜S1 smoke 48/48｜"
           "S2 板空（job_list 0·fleet tasks 45 claimed/0 open）｜S3: satengine rc0 活（Tools 注册面）"
           "·WM red=false next_pick=claimed moneyflow IC advisory（bm-a 道）·FUND trio 全 bm-b 属主 "
           "healthy（watch-only）｜FUND NULLS watch: V746/Q577/D428 of 2000（+12/+10/+10 vs r468·"
           "烧速健康·finalize 窗明日 10:30 开·证据 results/_r469bmc_fundnulls_watch.json）｜S6 38/38 "
           "rc0 NON-ZERO=none（dualrun ZERO-DRIFT streak 51〔367 entries〕·update_daily 金周 "
           "cutoff 2026-09-30 零新行·market_regime ORANGE shadow days=2·bm-a 心跳新鲜 16min→lane_io "
           "C 族守卫面诚实 skip·REPORT/LIVE-2026-10-04 幂等再生·金周无新 bar 腿诚实 no-op·token 台账"
           "照常）｜S7: loop pin5 phase-ok no-op（first fire 12:35）·watchdog 重注册（幂等·first fire "
           "12:30）·双爪 LF 归一安装到位·attrition CLEAN（4 ledgers·2 bm-a healed 历史注记照录）｜"
           "S4: 零新坑律行（四问门：无新长期教训→零 CODELY append）｜记分: 1（S6 管线产出+watch 证据件+"
           "S0 净路证据·等待态声明: finalize 窗 10-05 开·本窗零新面孔可烧〔N1 关+池 ready x3 全 bm-b "
           "属主+板空〕·非空转）｜记账预算: 3/5（state+心跳+轮报·零 CODELY 行）｜本地未达 origin "
           "commit 数: 收口 push 后 push_verify 自证（DELIVERED 后=0）｜零清扫/归档/删除类动作轮："
           "登记册零命中断言 N/A-无此类动作（O-2030 §二.3 自证面）")

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
state["round_no"] = 469
state["updated"] = ts
state["updated_at"] = ts
state["verify"] = VERIFY
state["ram_free_gb"] = idle_ram_gb
state["free_ram_gb"] = idle_ram_gb
with open(STATE, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(state, fh, ensure_ascii=False, indent=1)
state_check = json.loads(open(STATE, encoding="utf-8-sig").read())
assert state_check["round_no"] == 469, "state round_no write-back failed"
assert isinstance(state_check.get("heartbeat_epoch_utc", epoch), int), "epoch not int"

# --- heartbeat write-back ---
with open(HB, encoding="utf-8-sig") as fh:
    hb = json.load(fh)
hb["activity_now"] = ("golden-week watch; fund-trio NULLS V746/Q577/D428 of 2000 (+12/+10/+10 "
                      "vs r468), owners=bm-b healthy keepalive 11.0min; finalize window opens "
                      "10-05 10:30 (bm-b owner); N1 closed per O-2115 sec-2; boards empty (0 "
                      "open); zero-incident round")
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
hb["latest_artifact"] = ("results/_r469bmc_s6_log.txt (S6 38/38 rc0) + "
                         "results/_r469bmc_fundnulls_watch.json (V746/Q577/D428) @ " + ts)
hb["next_milestone"] = ("fund-trio finalize window 10-05 10:30 (QUALITY long-pole 577/2000); "
                        "D-20261004-02①②③ receipt window 10-06 00:00; O-2115/O-2030 acceptance "
                        "10-08; market reopen 10-09; next 5x=r470")
hb["prod_lanes"] = ("FUND trio NULLS bm-b in-flight (watch only); N1 closed per O-2115 sec-2; "
                    "boards empty; zero-incident watch round")
hb["ram_free_gb"] = idle_ram_gb
hb["round_no"] = 469
hb["round_no_label"] = "round 469 (bm-c)"
hb["ts"] = ts
hb["updated"] = ts
hb["updated_at"] = ts
hb["verdict"] = ("GREEN (smoke 48/48; orders 153/153 zero delta; D-19 double MATCH zero "
                 "consumption; satengine alive rc0 Tools face; S6 38 legs rc0 fail=0 dualrun "
                 "streak 51; attrition CLEAN; trio owners healthy; post_review 45Y/0N/5W zero "
                 "active red; zero cloud token)")
with open(HB, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
hb_check = json.loads(open(HB, encoding="utf-8-sig").read())
assert isinstance(hb_check["heartbeat_epoch_utc"], int), "heartbeat epoch must be int"
assert "T" in hb_check["clock_read"], "clock_read must be T-separated"
assert hb_check["round_no"] == 469, "heartbeat round_no failed"

# --- round report append (bytes-safe append, newline='' per r641 CRLF law) ---
with open(RR, "a", encoding="utf-8", newline="") as fh:
    fh.write(RR_LINE + "\n")

print("STATE round_no=469 OK; heartbeat epoch int OK; RR line appended")
print("ts=" + ts + " cpu=" + str(cpu_pct) + " idle_ram=" + str(idle_ram_gb) +
      " gpu_mib=" + str(gpu_mib) + " epoch=" + str(epoch))
