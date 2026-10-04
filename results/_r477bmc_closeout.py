"""r477 bm-c closeout: state writeback + round-report line append + heartbeat.
IN-PLACE heartbeat update (r475 field-loss incident lesson: never wholesale
replace the hb dict; keep orders_ack and all legacy fields intact).
Programmatic json writes with post-write json.loads self-proof (r645 law).
Round-report append in bytes mode (r641 mixed-encoding law)."""
import datetime
import json
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = os.path.join(ROOT, "state-bm-c.json")
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")

now = datetime.datetime.now()
now_iso = now.isoformat(timespec="seconds")
now_stamp = now.strftime("%Y-%m-%d %H:%M:%S")
epoch = int(now.timestamp())


def sample_machine():
    ev = {}
    try:
        import psutil
        ev["cpu_pct"] = round(psutil.cpu_percent(interval=1.0), 1)
        vm = psutil.virtual_memory()
        ev["idle_ram_gb"] = round(vm.available / (1024 ** 3), 1)
    except Exception as e:
        ev["cpu_pct"] = None
        ev["idle_ram_gb"] = None
        ev["psutil_err"] = str(e)[:80]
    try:
        p = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free",
             "--format=csv,noheader,nounits"],
            capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=15)
        ev["gpu_free_vram_mib"] = int(
            (p.stdout or b"").decode("utf-8", "replace").strip().splitlines()[0])
    except Exception:
        ev["gpu_free_vram_mib"] = None
    return ev


mach = sample_machine()

did = ("r477 bm-c golden-week watch round (zero-incident by-threshold, "
       "fleet-silence observation logged): (1) S0: no rebase leftovers; "
       "round-start dirty = 2 own satengine lane faces; origin behind=0 "
       "after fetch -> absorb commit f5940bfce (2 lane faces), push_verify "
       "DELIVERED tip f5940bfce. (2) S0.5: orders 153/153 zero un-acked "
       "(S0.5 + S7 double-scan, same-caliber same-form set-diff); ack-form "
       "caliber pit caught self (r646 variant, unacked=153 full false-alarm "
       "-> form-aligned recheck zero-diff; one CODELY line appended); inbox "
       "0 inbound (1 own outbound MSG-1332 awaiting bm-a/bm-b consumption); "
       "D-19 decisions 4E5BE321 + group-orders 68947C17 double MATCH -> "
       "zero consumption. (3) S1 smoke 48/48. (4) S2: boards empty (job_list "
       "0; fleet 169 tickets, open=0; 45 claimed = other machines' lanes). "
       "(5) S3: satengine rc0 alive via Tools copy; WM red=false healthy; "
       "fund-trio watch V782/Q609/D454 of 2000 ZERO-DELTA vs r476 (trio "
       "progress stalled at 13:52:37 bm-b r674 snapshot, 15min window at "
       "probe); keepalive owner_since static 13:38:12 age 29.6min healthy "
       "True x3 (claim intact, no pool touch per r626d-2); FLEET-SILENCE "
       "observation: bm-a hb stale 25min + origin silent since 13:50:32 "
       "(r679 close) -> S6 lane_io x4 stale-takeover derive by bm-c per "
       "O-2100 s2.4 (designed mechanism, not incident); bm-b hb stale 30min "
       "+ origin silent since 13:52:37 (r674 S0+merge landed, r674 close not "
       "yet visible); no machine/* fallback branches on origin; escalation "
       "criteria set for r478: keepalive unhealthy OR fleet silence past "
       "watchdog revival window (~14:22+) -> MSG to fleet. (6) S6 38/38 rc0 "
       "FAILS=[] (dualrun ZERO-DRIFT streak 51, 368 entries; compute_audit "
       "pool-supply-gap standing flag as-adjudicated r474; update_daily "
       "golden-week cutoff 2026-09-30 zero new rows; market_regime ORANGE "
       "shadow days=2; lhb 30min-guard no-op + fundamental fresh-skip; "
       "REPORT/LIVE-2026-10-04 idempotent regen state=ORANGE). (7) S7: loop "
       "pin5 phase-ok (next fire 14:15), watchdog re-registered (first fire "
       "14:14), both claws LF-normalized installed, attrition CLEAN (4 "
       "ledgers, 2 bm-a healed notes recorded); heartbeat written IN-PLACE "
       "(orders_ack 154 preserved, field-intact assertion).")

verify = ("S6 38/38 rc0 FAILS=[] (results/_r477bmc_s6_log.txt, S6-chain-end "
          "marker); smoke 48/48; orders 153/153 zero-diff double-scan "
          "(same-caliber same-form set-diff); D-19 decisions 4E5BE321 + "
          "group-orders 68947C17 double MATCH raw-blob caliber; attrition "
          "CLEAN (4 ledgers); claws LF-normalized installed x2; loop pin5 "
          "phase-ok; watchdog registered; satengine alive rc0 (Tools face); "
          "fund-trio watch V782/Q609/D454 healthy True x3 (owners=bm-b, age "
          "29.6min, zero-delta window 13:52:37->14:07:48 recorded); "
          "heartbeat epoch int + clock T-sep + in-place field-intact "
          "self-checked (orders_ack 154 intact)")

next_p = ("(a) r478 fleet-silence re-probe round: re-run fund-trio watch + "
          "bm-a/bm-b heartbeat/origin checks; escalation if keepalive "
          "flips unhealthy OR bm-a/bm-b origin silence persists past "
          "watchdog revival window (~14:22+) -> MSG to fleet inbox (evidence "
          "file pointers); pool owner line intact = keepalive self-heal "
          "expected, no third-party surgery (r626d-2). (b) MSG-1332 "
          "consumption watch: bm-a receipt (per-face max-merge law "
          "scope-extension adoption face) + bm-b self-heal confirmation "
          "face. (c) fund-trio finalize window 10-05 10:30 opens (bm-b "
          "owner; ETA V 10-06 15:00 / Q long-pole 10-07 11:00, slip watch "
          "if burn stall persists). (d) D-20261004-02(1)(2)(3) receipt "
          "window 10-06 00:00. (e) D-06 full closure window 10-07 (bm-c "
          "lead). (f) O-2115/O-2030 acceptance 10-08; market reopen 10-09; "
          "next 5x = bm-c r480.")

current_task = ("当前活: golden-week watch r477 (fund-trio NULLS zero-delta "
                "window + fleet-silence observation bm-a/bm-b; lane_io "
                "stale-takeover x4 per O-2100 s2.4 designed mechanism; "
                "zero-incident by-threshold) | 最近实物: results/"
                "_r477bmc_s6_log.txt (S6 38/38 rc0·chain-end+FAILS=[]) + "
                "results/_r477bmc_fundnulls_watch.json (V782/Q609/D454 "
                "healthy True x3·age 29.6min·zero-delta window recorded) @ "
                + now_iso + " | 下个里程碑: r478 fleet-silence re-probe "
                "(escalation check ~14:25 post-watchdog-window); fund-trio "
                "finalize 窗 10-05 10:30 开 (bm-b 正主); D-06 收口 10-07 "
                "(bm-c lead); 开市 10-09")

last_round = ("r477 bm-c: golden-week watch + fund-trio zero-delta window "
              "observation (V782/Q609/D454 static since 13:52:37 snapshot, "
              "keepalive healthy True x3, claim intact no-touch) + "
              "fleet-silence observation (bm-a/bm-b origin silence 16-22min, "
              "lane_io stale-takeover x4 by-design per O-2100 s2.4, "
              "escalation criteria set for r478) + S6 38/38 rc0 + smoke "
              "48/48; zero incident by-threshold")

with open(STATE, encoding="utf-8-sig") as f:
    st = json.load(f)
st["clock_read"] = now_iso
st["cpu_pct"] = mach.get("cpu_pct")
st["idle_ram_gb"] = mach.get("idle_ram_gb")
st["ram_free_gb"] = mach.get("idle_ram_gb")
st["free_ram_gb"] = mach.get("idle_ram_gb")
st["gpu_free_vram_mib"] = mach.get("gpu_free_vram_mib")
st["current_task"] = current_task
st["did"] = did
st["last_decisions_read_at"] = now_iso
st["last_round"] = last_round
st["last_round_at"] = now_iso
st["last_round_ts"] = now_stamp
st["last_seen"] = now_iso
st["last_ts"] = now_stamp
st["machine_id"] = "bm-c"
st["next"] = next_p
st["round_no"] = 477
st["updated"] = now_iso
st["updated_at"] = now_iso
st["verify"] = verify
st["heartbeat_epoch_utc"] = epoch
with open(STATE, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
with open(STATE, encoding="utf-8-sig") as f:
    recheck = json.load(f)
assert recheck["round_no"] == 477, "round_no writeback failed"
assert isinstance(recheck.get("heartbeat_epoch_utc"), int), "epoch must be int"
print("STATE_OK round=477 epoch=" + str(recheck["heartbeat_epoch_utc"]))

# --- heartbeat: IN-PLACE update (r475 field-loss incident lesson) ---
with open(HB, encoding="utf-8-sig") as f:
    hb = json.load(f)
prev_fields = set(hb.keys())
prev_ack = hb.get("orders_ack")
assert isinstance(prev_ack, list) and len(prev_ack) >= 150, \
    "orders_ack missing before write: " + repr(prev_ack)[:100]
hb["machine_id"] = "bm-c"
hb["last_seen"] = now_iso
hb["last_seen_at"] = now_iso
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["cpu_pct"] = mach.get("cpu_pct")
hb["cpu_cores"] = 32
hb["cores"] = 32
hb["idle_ram_gb"] = mach.get("idle_ram_gb")
hb["ram_free_gb"] = mach.get("idle_ram_gb")
hb["free_ram_gb"] = mach.get("idle_ram_gb")
hb["gpu_free_vram_mib"] = mach.get("gpu_free_vram_mib")
hb["round_no"] = 477
hb["round_no_label"] = "r477"
hb["updated"] = now_iso
hb["updated_at"] = now_iso
hb["ts"] = now_stamp
hb["activity_now"] = ("golden-week watch r477; fund-trio NULLS zero-delta "
                      "window + fleet-silence observation (bm-a/bm-b); "
                      "escalation check r478")
hb["current_task"] = (hb["activity_now"] + "; MSG-1332 consumption watch")
hb["latest_artifact"] = ("results/_r477bmc_s6_log.txt (S6 38/38 rc0) + "
                         "results/_r477bmc_fundnulls_watch.json (V782/Q609/"
                         "D454 healthy True x3, zero-delta window recorded)")
hb["next_milestone"] = ("r478 fleet-silence re-probe (escalation check "
                        "~14:25); fund-trio finalize window 10-05 10:30 "
                        "opens (bm-b owner); D-06 closure 10-07 (bm-c "
                        "lead); market reopen 10-09")
hb["health"] = "healthy"
hb["verdict"] = ("healthy watch round by-threshold; fleet-silence "
                 "observation logged (bm-a/bm-b), lane_io stale-takeover "
                 "x4 by-design per O-2100 s2.4; trio keepalive healthy, "
                 "claim intact no-touch; boards empty; W14 parked per "
                 "O-0808")
hb["prod_lanes"] = ("FUND trio NULLS bm-b in-flight (watch only, zero-delta "
                    "window 13:52->14:08 recorded, keepalive healthy True "
                    "x3, claim intact); lane_io stale-takeover x4 (bm-a hb "
                    "stale 25min) per O-2100 s2.4 designed mechanism; N1 "
                    "closed per O-2115 sec-2; boards empty; zero-incident "
                    "watch round with fleet-silence observation")
with open(HB, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
with open(HB, encoding="utf-8-sig") as f:
    hbr = json.load(f)
assert set(hbr.keys()) >= prev_fields, \
    "field loss after hb write: " + repr(prev_fields - set(hbr.keys()))
assert hbr["orders_ack"] == prev_ack, "orders_ack mutated"
assert isinstance(hbr.get("heartbeat_epoch_utc"), int), "hb epoch must be int"
assert "T" in hbr.get("clock_read", ""), "hb clock must be T-separated"
print("HEARTBEAT_OK fields=" + str(len(hbr)) + " orders_ack=" +
      str(len(hbr["orders_ack"])) + " epoch=" +
      str(hbr["heartbeat_epoch_utc"]))

report_line = (
    now_iso + "+08:00｜r477｜dept:工程（golden-week 值守轮·阈值内零事故·机队"
    "静默观察窗入册）｜watermark verdict=绿（red=false healthy·satengine rc0 活"
    "〔Tools 注册面·N1 关面 per O-2115 sec-2〕）｜当前活=金周值守+fund-trio "
    "NULLS 零增量窗观察+机队静默观察（bm-a/bm-b）+lane_io stale-takeover x4〔"
    "O-2100 s2.4 法定机制〕｜最近实物=results/_r477bmc_s6_log.txt（S6 38/38 "
    "rc0·chain-end+FAILS=[]）+results/_r477bmc_fundnulls_watch.json（V782/Q609/"
    "D454·owners=bm-b healthy True×3·age 29.6min·零增量窗 13:52:37→14:07:48 "
    "记录）｜下个里程碑=r478 机队静默复探测（升级判据=keepalive 转 unhealthy 或 "
    "bm-a/bm-b 静默越过 watchdog 复活窗 ~14:22+→fleet MSG；池 owner 行完好="
    "keepalive 自愈预期勿第三方手术〔r626d-②〕）+finalize 窗 10-05 10:30（bm-b "
    "正主·烧录停摆持续则 ETA 滑窗观察）+D-06 收口 10-07（bm-c 主导）+开市 "
    "10-09（≤48h）｜S0: 无 rebase 残留·轮首 2 脏面=本机 satengine 车道面·"
    "origin behind=0→absorb f5940bfce+push_verify DELIVERED（tip f5940bfce）"
    "｜S0.5: 令差集=0（153/153 同口径同形态集合比对零差·S0.5+S7 双扫）·ack 形态"
    "口径坑当场自纠（r646 变体·unacked=153 全量假警→形态对齐复检零差·CODELY 一"
    "行入册）·inbox 0 入站（1 出站自 MSG-1332 在途待 bm-a/bm-b 消费）·D-19 "
    "decisions 4E5BE321 MATCH+group orders 68947C17 MATCH（per-key raw-blob·"
    "探针 _r477bmc_d19_check.py 复用 r471 范式）→零消费｜S1 smoke 48/48｜S2 板"
    "空（job_list 0·fleet 169 票 open=0·45 claimed=他机车道）｜S3: satengine "
    "rc0 活（Tools 注册面）·WM red=false healthy·FUND trio 全 bm-b 属主 "
    "healthy（watch-only·claim 完好零触碰）·W14 停泊维持 per O-0808｜FUND "
    "NULLS watch: V782/Q609/D454 of 2000 零增量 vs r476（trio 进度停在 bm-b "
    "r674 13:52:37 快照·探针时窗 15min）·keepalive owner_since 静止 13:38:12 "
    "age 29.6min healthy True×3（阈内=观察相数据非事故·r641 律）·机队静默观察:"
    "bm-a 心跳 25min 陈旧+origin 静默自 13:50:32（r679 收口）→S6 lane_io×4 "
    "stale-takeover derive（O-2100 s2.4 法定机制·t35_verify/t35_export/"
    "daily_scorecard/build_status 四面）·bm-b 心跳 30min 陈旧+origin 静默自 "
    "13:52:37（r674 S0+merge 落·r674 close 未现）·origin 无 machine/* 备胎分"
    "支→非 push-拒 fallback 面｜S6 38/38 rc0 FAILS=[]（dualrun ZERO-DRIFT "
    "streak 51〔368 entries〕·compute_audit pool-supply-gap standing 态照录"
    "〔r474 定谳〕·update_daily 金周 cutoff 2026-09-30 零新行·market_regime "
    "ORANGE shadow days=2·lhb 30min 守卫 no-op+fundamental 快照新跳过·REPORT/"
    "LIVE-2026-10-04 幂等再生 state=ORANGE·金周无新 bar 腿诚实 no-op 族全过）"
    "｜S7: loop pin5 phase-ok（next fire 14:15）·watchdog 重注册（first fire "
    "14:14）·双爪 LF 归一 installed x2 幂等重装·attrition CLEAN（4 ledgers·2 "
    "bm-a healed 历史注记照录）·orders S7 二扫 153/153 零差｜心跳 IN-PLACE 写入"
    "执法（orders_ack 154 原样保全+字段恒等断言+epoch int+clock T-sep 自证）"
    "｜S4: 一行（orders_ack 条目形态口径坑=r646 变体·CODELY.md 入册·72.5KB 水位"
    "维持=r504 定谳结构性在役律面·阈值重锚归集团/GM 裁定·零字节驱动归档）｜记"
    "分: 1（S6 管线产出+watch 证据件×2+REPORT/LIVE 再生+stale-takeover 四面 "
    "derive·等待态声明: 板空+N1 关+trio bm-b 属主=零新面孔可烧·非空转）｜记账预"
    "算: 4/5（state+心跳+轮报+CODELY 一行）｜本地未达 origin commit 数: 收口 "
    "push 后 push_verify 自证（DELIVERED 后=0）｜零清扫/归档/删除类动作轮：登记"
    "册零命中断言 N/A-无此类动作（O-2030 §二.3 自证面）\n")

with open(REPORT, "ab") as f:
    f.write(report_line.encode("utf-8"))
with open(REPORT, "rb") as f:
    tail = f.read()
lines = [ln for ln in tail.split(b"\n") if ln.strip()]
assert b"r477" in lines[-1], "report line append failed"
print("REPORT_OK r477 line appended")
