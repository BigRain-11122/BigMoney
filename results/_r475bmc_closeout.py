"""r475 bm-c closeout: state writeback + round-report line append + heartbeat.
Programmatic json writes with post-write json.loads self-proof (r645 law).
Round-report append in bytes mode with newline='' (r641 mixed-encoding law)."""
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

did = ("r475 bm-c golden-week watch round (zero-incident, 5x HANDOVER duty): "
       "(1) S0: no rebase leftovers; round-start dirty = 2 own satengine lane "
       "faces; origin behind=3 (bm-b r673 closeout wave) zero face intersection "
       "(r437 pre-check) -> absorb commit 645ebd104 (2 lane faces) + merge "
       "origin/main CLEAN zero-UU (52 faces) -> push_verify DELIVERED tip "
       "8ea65133a. (2) S0.5: orders 153/153 zero un-acked (S0.5 + S7 "
       "double-scan, same-caliber); inbox 0 inbound (1 own outbound MSG-1332 "
       "awaiting bm-a/bm-b consumption); D-19 decisions 4E5BE321 + group-orders "
       "68947C17 double MATCH -> zero consumption. (3) S1 smoke 48/48. (4) S2: "
       "boards empty (job_list 0; fleet 169 tickets, open=0; 45 claimed = "
       "other machines' lanes). (5) S3: satengine rc0 alive via Tools copy "
       "(alive=True, burns_active=[], queue_next=[] = N1 closed face per "
       "O-2115 sec-2); WM red=false green; fund-trio watch V778/Q604/D451 of "
       "2000 (delta +3/+2/+2 vs r474), owners=bm-b keepalive 9.2min healthy "
       "True x3 = pool owner_since self-heal THIRD consecutive round evidence "
       "(r474 next-pointer (b) closure criteria held); W14 parked per O-0808. "
       "(6) S6 38/38 rc0 NON-ZERO=none (dualrun ZERO-DRIFT streak 51, 368 "
       "entries; compute_audit pool-supply-gap standing flag as-adjudicated "
       "r474 = trio ready-with-owner burning face; update_daily golden-week "
       "cutoff 2026-09-30 zero new rows; market_regime ORANGE shadow days=2; "
       "bm-a heartbeat fresh 18-19min -> lane_io legs honest skip (zero "
       "stale-takeover this round vs r473/r474); REPORT/LIVE-2026-10-04 "
       "idempotent regen state=ORANGE). (7) S7: loop pin5 phase-ok, watchdog "
       "re-registered, both claws LF-normalized installed, attrition CLEAN (4 "
       "ledgers, 2 bm-a healed notes recorded); (8) 5x HANDOVER r475 entry "
       "landed (window r471-475, unified ledger 625,977 live-read).")

verify = ("S6 38/38 rc0 NON-ZERO=none (results/_r475bmc_s6_log.txt, S6-chain-end "
          "marker + FAILS=[]); smoke 48/48; orders 153/153 zero-diff double-scan "
          "(same-caliber set-diff); D-19 decisions 4E5BE321 + group-orders "
          "68947C17 double MATCH raw-blob caliber; attrition CLEAN (4 ledgers); "
          "claws LF-normalized installed x2; loop pin5 phase-ok; watchdog "
          "registered; satengine alive rc0 (Tools face); fund-trio watch "
          "V778/Q604/D451 healthy True x3 (owners=bm-b, age 9.2min); unified "
          "ledger 625,977 live-read (n1_w115 science_gates.ledger.total, +0 "
          "window); heartbeat epoch int + clock T-sep self-checked")

next_p = ("(a) r476-r479 golden-week watch rounds (finalize window 10-05 10:30 "
          "opens, bm-b owner). (b) MSG-1332 consumption watch: bm-a receipt "
          "(per-face max-merge law scope-extension adoption face) + bm-b "
          "self-heal confirmation face. (c) fund-trio finalize window 10-05 "
          "10:30 opens (bm-b owner; ETA V 10-06 15:00 / Q long-pole 10-07 "
          "11:00). (d) D-20261004-02(1)(2)(3) receipt window 10-06 00:00. (e) "
          "D-06 full closure window 10-07 (bm-c lead). (f) O-2115/O-2030 "
          "acceptance 10-08; market reopen 10-09; next 5x = bm-c r480.")

current_task = ("当前活: golden-week watch + 5x HANDOVER r475 landed (window r471-475; "
                "pool owner_since self-heal 3rd consecutive round evidence; "
                "zero-incident) | 最近实物: research/HANDOVER.md r475 entry (增量窗 "
                "r471-475·链头 625,977 live-read) + results/_r475bmc_s6_log.txt (S6 "
                "38/38 rc0) + results/_r475bmc_fundnulls_watch.json (V778/Q604/D451 "
                "healthy True x3) @ 2026-10-04T" + now.strftime("%H:%M:%S") + "+08:00 | "
                "下个里程碑: fund-trio finalize 窗 10-05 10:30 开 (bm-b 正主·ETA V "
                "10-06 15:00/Q 长杆 10-07 11:00); D-06 收口 10-07 (bm-c lead); 开市 "
                "10-09")

last_round = ("r475 bm-c: golden-week watch + 5x HANDOVER (window r471-475, ledger "
              "625,977 live-read) + pool self-heal 3rd-round evidence (trio healthy "
              "True x3, age 9.2min) + S6 38/38 rc0 (zero stale-takeover; bm-a hb "
              "fresh) + smoke 48/48; zero incident")

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
st["last_decisions_read_at"] = "2026-10-04T13:46:41"
st["last_round"] = last_round
st["last_round_at"] = now_iso
st["last_round_ts"] = now_stamp
st["last_seen"] = now_iso
st["last_ts"] = now_stamp
st["machine_id"] = "bm-c"
st["next"] = next_p
st["round_no"] = 475
st["updated"] = now_iso
st["updated_at"] = now_iso
st["verify"] = verify
st["heartbeat_epoch_utc"] = epoch
with open(STATE, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
with open(STATE, encoding="utf-8-sig") as f:
    recheck = json.load(f)
assert recheck["round_no"] == 475, "round_no writeback failed"
assert isinstance(recheck.get("heartbeat_epoch_utc"), int), "epoch must be int"
print("STATE_OK round=475 epoch=" + str(recheck["heartbeat_epoch_utc"]))

hb = {
    "machine_id": "bm-c",
    "last_seen": now_iso,
    "clock_read": now_iso,
    "heartbeat_epoch_utc": epoch,
    "cpu_cores": 32,
    "cpu_pct": mach.get("cpu_pct"),
    "idle_ram_gb": mach.get("idle_ram_gb"),
    "gpu_free_vram_mib": mach.get("gpu_free_vram_mib"),
    "current_task": "golden-week watch + 5x HANDOVER r475 landed; fund-trio "
                    "NULLS burn watch (V778/Q604/D451, bm-b owner); MSG-1332 "
                    "consumption watch",
    "verdict": "healthy watch round, zero incident, N1 closed per O-2115 "
               "sec-2, boards empty, W14 parked per O-0808",
    "next_milestone": "fund-trio finalize window 10-05 10:30 opens (bm-b "
                      "owner); D-06 closure 10-07 (bm-c lead); market reopen "
                      "10-09",
}
with open(HB, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
with open(HB, encoding="utf-8-sig") as f:
    hbr = json.load(f)
assert isinstance(hbr.get("heartbeat_epoch_utc"), int), "hb epoch must be int"
assert "T" in hbr.get("clock_read", ""), "hb clock must be T-separated"
print("HEARTBEAT_OK epoch=" + str(hbr["heartbeat_epoch_utc"]))

report_line = (
    "2026-10-04T" + now_iso[11:] + "+08:00｜r475｜dept:工程（golden-week 值守轮·"
    "5x HANDOVER 义务轮·零事故）｜watermark verdict=绿（red=false healthy·"
    "satengine rc0 活〔Tools 注册面·alive=True·burns_active=[]·queue_next[]=N1 "
    "关面 per O-2115 sec-2〕·post_review REPORT-20261004 零活红维持）｜当前活="
    "金周值守+5x HANDOVER 核对+fund-trio NULLS 进度读数｜最近实物=research/"
    "HANDOVER.md r475 条目（增量窗 r471-475·统一链 625,977 live-read）+results/"
    "_r475bmc_s6_log.txt（S6 38/38 rc0·chain-end 标记+FAILS=[]）+results/"
    "_r475bmc_fundnulls_watch.json（V778/Q604/D451·owners=bm-b healthy True×3 "
    "age 9.2min）｜下个里程碑=fund-trio finalize 窗 10-05 10:30 开（bm-b 正主·"
    "ETA V 10-06 15:00/Q 长杆 10-07 11:00）+MSG-1332 回执消费观察+D-06 收口 "
    "10-07（bm-c 主导）+开市 10-09（≤48h）｜S0: 无 rebase 残留·轮首 2 脏面=本机 "
    "satengine 车道面·origin behind=3（bm-b r673 closeout wave）零交集（r437 预对齐）"
    "→absorb 645ebd104+merge 净零 UU（52 面）→push_verify DELIVERED（tip "
    "8ea65133a）｜S0.5: 令差集=0（153/153 同口径集合比对零差）·inbox 0 入站（1 "
    "出站自 MSG-1332 在途待 bm-a/bm-b 消费）·D-19 decisions 4E5BE321 MATCH+group "
    "orders 68947C17 MATCH（per-key raw-blob·探针复用 _r471bmc_d19_check.py）→零"
    "消费｜S1 smoke 48/48｜S2 板空（job_list 0·fleet 169 票 open=0·45 claimed=他机"
    "车道）｜S3: satengine rc0 活（Tools 注册面）·WM red=false healthy·py_"
    "watermark=py_low_board_clear 合法 idle（板空+金周无 bar）·FUND trio 全 bm-b "
    "属主 healthy（watch-only）·W14 停泊维持 per O-0808｜FUND NULLS watch: V778/"
    "Q604/D451 of 2000（delta +3/+2/+2 vs r474·keepalive 9.2min healthy True×3="
    "池 owner_since 自愈第三轮持续实证·r474 next 指针(b) 收口判据维持·证据 "
    "results/_r475bmc_fundnulls_watch.json）｜5x HANDOVER: r475 条目置顶落盘（增"
    "量窗 r471-475：r471 值守净路+T-169 同轮认领核验/r472 值守+trio 软陈旧双形交叉"
    "定谳/r473 push-race 治愈+r440 两分法 7UU+3 CEO 面 takeover/r474 池面回退定谳"
    "+MSG-1332+TJ-P2 收口核验+三波收敛+自愈同轮实证/r475 本核对）+统一链 625,977 "
    "live-read（n1_w115_results.json science_gates.ledger.total·窗 +0=NULLS 校准"
    "烧不入头线程）｜S6 38/38 rc0 NON-ZERO=none（dualrun ZERO-DRIFT streak 51〔368 "
    "entries〕·compute_audit pool-supply-gap standing 态照录〔r474 定谳=trio "
    "ready-with-owner 实烧录面〕·update_daily 金周 cutoff 2026-09-30 零新行·"
    "market_regime ORANGE shadow days=2·bm-a 心跳新鲜 18-19min→lane_io 腿诚实 "
    "skip〔本轮零 stale-takeover 对照 r473/r474〕·REPORT/LIVE-2026-10-04 幂等再生 "
    "state=ORANGE·金周无新 bar 腿诚实 no-op 族全过）｜S7: loop pin5 phase-ok（next "
    "fire 13:55）·watchdog 重注册（first fire 13:51）·双爪 LF 归一 installed x2 幂"
    "等重装·attrition CLEAN（4 ledgers·2 bm-a healed 历史注记照录）·orders S7 二"
    "扫 153/153 零差｜S4: 零新坑律行（四问门：全窗循正典零新失效模式→零 CODELY "
    "append）｜记分: 1（5x HANDOVER r475 条目+S6 管线产出+watch 证据件+S3 探针件+"
    "REPORT/LIVE 再生·等待态声明: finalize 窗 10-05 开·N1 关+trio bm-b 属主+板空="
    "零新面孔可烧·非空转）｜记账预算: 4/5（state+心跳+轮报+HANDOVER·CODELY 零行）"
    "｜本地未达 origin commit 数: 收口 push 后 push_verify 自证（DELIVERED 后=0）"
    "｜零清扫/归档/删除类动作轮：登记册零命中断言 N/A-无此类动作（O-2030 §二.3 "
    "自证面）\n")

with open(REPORT, "ab") as f:
    f.write(report_line.encode("utf-8"))
with open(REPORT, "rb") as f:
    tail = f.read()
assert b"r475" in tail.split(b"\n")[-2] or b"r475" in tail.splitlines()[-1], \
    "report line append failed"
print("REPORT_OK r475 line appended")
