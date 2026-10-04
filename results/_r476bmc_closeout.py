"""r476 bm-c closeout: state writeback + round-report line append + heartbeat.
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

did = ("r476 bm-c golden-week watch round (zero-incident): "
       "(1) S0: no rebase leftovers; round-start dirty = 2 own satengine lane "
       "faces; origin behind=0 after fetch -> absorb commit 9d0c3ba45 (2 lane "
       "faces), merge already-up-to-date, push_verify DELIVERED tip 9d0c3ba45. "
       "(2) S0.5: orders 153/153 zero un-acked (S0.5 + S7 double-scan, "
       "same-caliber); inbox 0 inbound (1 own outbound MSG-1332 awaiting "
       "bm-a/bm-b consumption); D-19 decisions 4E5BE321 + group-orders "
       "68947C17 double MATCH -> zero consumption. (3) S1 smoke 48/48. (4) S2: "
       "boards empty (job_list 0; fleet 169 tickets, open=0; 45 claimed = "
       "other machines' lanes). (5) S3: satengine rc0 alive via Tools copy; "
       "WM red=false healthy; fund-trio watch V782/Q609/D454 of 2000 (delta "
       "+4/+5/+3 vs r475), owners=bm-b keepalive 18.8min healthy True x3 = "
       "pool owner_since self-heal FOURTH consecutive round evidence; W14 "
       "parked per O-0808. (6) S6 38/38 rc0 FAILS=[] (dualrun ZERO-DRIFT "
       "streak 51, 368 entries; compute_audit pool-supply-gap standing flag "
       "as-adjudicated r474; update_daily golden-week cutoff 2026-09-30 zero "
       "new rows; market_regime ORANGE shadow days=2; lhb 11-page refresh + "
       "fundamental eligibility refresh + b_layer mask regen 5222 codes; "
       "bm-a heartbeat fresh 13min -> lane_io legs honest skip (zero "
       "stale-takeover second consecutive round); REPORT/LIVE-2026-10-04 "
       "idempotent regen state=ORANGE). (7) S7: loop pin5 phase-ok (next "
       "fire 14:05), watchdog re-registered (first fire 14:02), both claws "
       "LF-normalized installed, attrition CLEAN (4 ledgers, 2 bm-a healed "
       "notes recorded); heartbeat written IN-PLACE (r475 field-loss lesson "
       "applied: orders_ack 154 preserved, 35-field intact assertion).")

verify = ("S6 38/38 rc0 FAILS=[] (results/_r476bmc_s6_log.txt, S6-chain-end "
          "marker); smoke 48/48; orders 153/153 zero-diff double-scan "
          "(same-caliber set-diff); D-19 decisions 4E5BE321 + group-orders "
          "68947C17 double MATCH raw-blob caliber; attrition CLEAN (4 "
          "ledgers); claws LF-normalized installed x2; loop pin5 phase-ok; "
          "watchdog registered; satengine alive rc0 (Tools face); fund-trio "
          "watch V782/Q609/D454 healthy True x3 (owners=bm-b, age 18.8min); "
          "heartbeat epoch int + clock T-sep + 35-field in-place self-checked "
          "(orders_ack 154 intact)")

next_p = ("(a) r477-r479 golden-week watch rounds (finalize window 10-05 "
          "10:30 opens, bm-b owner). (b) MSG-1332 consumption watch: bm-a "
          "receipt (per-face max-merge law scope-extension adoption face) + "
          "bm-b self-heal confirmation face. (c) fund-trio finalize window "
          "10-05 10:30 opens (bm-b owner; ETA V 10-06 15:00 / Q long-pole "
          "10-07 11:00). (d) D-20261004-02(1)(2)(3) receipt window 10-06 "
          "00:00. (e) D-06 full closure window 10-07 (bm-c lead). (f) "
          "O-2115/O-2030 acceptance 10-08; market reopen 10-09; next 5x = "
          "bm-c r480.")

current_task = ("当前活: golden-week watch r476 (fund-trio NULLS burn watch "
                "V782/Q609/D454; pool owner_since self-heal 4th consecutive "
                "round evidence; zero-incident) | 最近实物: results/"
                "_r476bmc_s6_log.txt (S6 38/38 rc0·chain-end+FAILS=[]) + "
                "results/_r476bmc_fundnulls_watch.json (V782/Q609/D454 "
                "healthy True x3·age 18.8min) @ " + now_iso + " | 下个里程碑: "
                "fund-trio finalize 窗 10-05 10:30 开 (bm-b 正主·ETA V 10-06 "
                "15:00/Q 长杆 10-07 11:00); D-06 收口 10-07 (bm-c lead); 开市 "
                "10-09")

last_round = ("r476 bm-c: golden-week watch + fund-trio NULLS burn watch "
              "(V782/Q609/D454 delta +4/+5/+3, self-heal 4th-round evidence, "
              "trio healthy True x3) + S6 38/38 rc0 (zero stale-takeover; "
              "lhb/fundamental refresh landed) + smoke 48/48; zero incident")

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
st["last_decisions_read_at"] = "2026-10-04T13:56:41"
st["last_round"] = last_round
st["last_round_at"] = now_iso
st["last_round_ts"] = now_stamp
st["last_seen"] = now_iso
st["last_ts"] = now_stamp
st["machine_id"] = "bm-c"
st["next"] = next_p
st["round_no"] = 476
st["updated"] = now_iso
st["updated_at"] = now_iso
st["verify"] = verify
st["heartbeat_epoch_utc"] = epoch
with open(STATE, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
with open(STATE, encoding="utf-8-sig") as f:
    recheck = json.load(f)
assert recheck["round_no"] == 476, "round_no writeback failed"
assert isinstance(recheck.get("heartbeat_epoch_utc"), int), "epoch must be int"
print("STATE_OK round=476 epoch=" + str(recheck["heartbeat_epoch_utc"]))

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
hb["round_no"] = 476
hb["round_no_label"] = "r476"
hb["updated"] = now_iso
hb["updated_at"] = now_iso
hb["ts"] = now_stamp
hb["activity_now"] = ("golden-week watch r476; fund-trio NULLS burn watch "
                      "(V782/Q609/D454, bm-b owner)")
hb["current_task"] = (hb["activity_now"] + "; MSG-1332 consumption watch")
hb["latest_artifact"] = ("results/_r476bmc_s6_log.txt (S6 38/38 rc0) + "
                         "results/_r476bmc_fundnulls_watch.json (V782/Q609/"
                         "D454 healthy True x3)")
hb["next_milestone"] = ("fund-trio finalize window 10-05 10:30 opens "
                        "(bm-b owner); D-06 closure 10-07 (bm-c lead); "
                        "market reopen 10-09")
hb["health"] = "healthy"
hb["verdict"] = ("healthy watch round, zero incident, N1 closed per "
                 "O-2115 sec-2, boards empty, W14 parked per O-0808")
hb["prod_lanes"] = ("FUND trio NULLS bm-b in-flight (watch only, V39.1%/"
                    "Q30.5%/D22.7% per ETA face); pool trio owner_since "
                    "self-heal 4th-round evidence (V782/Q609/D454, healthy "
                    "True x3); THEME-JUDGE-P2 closed DONE; N1 closed per "
                    "O-2115 sec-2; boards empty; zero-incident watch round")
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
    now_iso + "+08:00｜r476｜dept:工程（golden-week 值守轮·零事故）｜watermark "
    "verdict=绿（red=false healthy·satengine rc0 活〔Tools 注册面·N1 关面 per "
    "O-2115 sec-2〕·post_review REPORT-20261004 零活红维持）｜当前活=金周值守+"
    "fund-trio NULLS 进度读数+池自愈第 4 轮实证｜最近实物=results/"
    "_r476bmc_s6_log.txt（S6 38/38 rc0·chain-end 标记+FAILS=[]）+results/"
    "_r476bmc_fundnulls_watch.json（V782/Q609/D454·owners=bm-b healthy True×3 "
    "age 18.8min）｜下个里程碑=fund-trio finalize 窗 10-05 10:30 开（bm-b 正主·"
    "ETA V 10-06 15:00/Q 长杆 10-07 11:00）+MSG-1332 回执消费观察+D-06 收口 "
    "10-07（bm-c 主导）+开市 10-09（≤48h）｜S0: 无 rebase 残留·轮首 2 脏面=本机 "
    "satengine 车道面·origin behind=0（fetch 后同步态）零交集（r437 预对齐）"
    "→absorb 9d0c3ba45+merge already-up-to-date→push_verify DELIVERED（tip "
    "9d0c3ba45）｜S0.5: 令差集=0（153/153 同口径集合比对零差·S0.5+S7 双扫）"
    "·inbox 0 入站（1 出站自 MSG-1332 在途待 bm-a/bm-b 消费）·D-19 decisions "
    "4E5BE321 MATCH+group orders 68947C17 MATCH（per-key raw-blob·探针复用 "
    "_r471bmc_d19_check.py）→零消费｜S1 smoke 48/48｜S2 板空（job_list 0·"
    "fleet 169 票 open=0·45 claimed=他机车道）｜S3: satengine rc0 活（Tools "
    "注册面）·WM red=false healthy·py_watermark=py_low_board_clear 合法 idle"
    "（板空+金周无 bar）·FUND trio 全 bm-b 属主 healthy（watch-only）·W14 停泊"
    "维持 per O-0808｜FUND NULLS watch: V782/Q609/D454 of 2000（delta +4/+5/+3 "
    "vs r475·keepalive 18.8min healthy True×3=池 owner_since 自愈第四轮持续实证"
    "·证据 results/_r476bmc_fundnulls_watch.json）｜S6 38/38 rc0 FAILS=[]"
    "（dualrun ZERO-DRIFT streak 51〔368 entries〕·compute_audit pool-supply-gap "
    "standing 态照录〔r474 定谳=trio ready-with-owner 实烧录面〕·update_daily "
    "金周 cutoff 2026-09-30 零新行·market_regime ORANGE shadow days=2·lhb 11 页"
    "刷新+fundamental eligibility 刷新+b_layer mask 再生 5222 码·bm-a 心跳新鲜 "
    "13min→lane_io 腿诚实 skip〔连续第二轮零 stale-takeover〕·REPORT/LIVE-"
    "2026-10-04 幂等再生 state=ORANGE·金周无新 bar 腿诚实 no-op 族全过）｜S7: "
    "loop pin5 phase-ok（next fire 14:05）·watchdog 重注册（first fire 14:02）"
    "·双爪 LF 归一 installed x2 幂等重装·attrition CLEAN（4 ledgers·2 bm-a "
    "healed 历史注记照录）·orders S7 二扫 153/153 零差｜心跳 IN-PLACE 写入执法"
    "（r475 字段丢失事故教训落地：orders_ack 154 原样保全+35 字段恒等断言+epoch "
    "int+clock T-sep 自证）｜S4: 零新坑律行（四问门：全窗循正典零新失效模式→零 "
    "CODELY append）｜记分: 1（S6 管线产出+watch 证据件+S3 探针件+lhb/fundamental "
    "数据刷新落地+REPORT/LIVE 再生·等待态声明: finalize 窗 10-05 10:30 开·N1 关"
    "+trio bm-b 属主+板空=零新面孔可烧·非空转）｜记账预算: 4/5（state+心跳+轮报"
    "+S7 回执·CODELY 零行）｜本地未达 origin commit 数: 收口 push 后 push_verify "
    "自证（DELIVERED 后=0）｜零清扫/归档/删除类动作轮：登记册零命中断言 N/A-无此"
    "类动作（O-2030 §二.3 自证面）\n")

with open(REPORT, "ab") as f:
    f.write(report_line.encode("utf-8"))
with open(REPORT, "rb") as f:
    tail = f.read()
lines = [ln for ln in tail.split(b"\n") if ln.strip()]
assert b"r476" in lines[-1], "report line append failed"
print("REPORT_OK r476 line appended")
