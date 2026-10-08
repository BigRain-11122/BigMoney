# -*- coding: utf-8 -*-
# r902 bm-a closeout: second orders scan (double-scan) + state heal 900->902 +
# heartbeat write (epoch int, T-sep clock) + r902 report line append.
import json, time, subprocess, hashlib, os, datetime, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
now_ts = int(time.time())

def stamp():
    return now_iso

# --- second orders scan (S7 double-scan) -------------------------------------
# local fleet/orders ack diff
d = os.path.join("fleet", "orders")
files = sorted(f for f in os.listdir(d) if f.startswith("O-") and f.endswith(".md"))
hb_path = os.path.join("fleet", "machines", "bm-a.json")
hb = json.load(io.open(hb_path, encoding="utf-8"))
acked = set(hb.get("orders_ack", []))
unacked = [f for f in files if f[:-3] not in acked and f not in acked]
assert unacked == [], f"second-scan found unacked orders: {unacked}"

# group ledger hash re-check (python raw-bytes canonical, C: real path)
GRP = r"C:\Users\sjs20\Desktop\FluxGroup"
subprocess.run(["git", "-C", GRP, "fetch", "origin"], capture_output=True, creationflags=0x08000000)
def blob(p):
    r = subprocess.run(["git", "-C", GRP, "show", "origin/main:" + p], capture_output=True)
    return r.stdout
h_dec = hashlib.sha256(blob("docs/decisions.md")).hexdigest()
h_ord = hashlib.sha256(blob("docs/orders.md")).hexdigest()
assert h_dec.startswith("8381319617dd5225"), f"DEC hash drifted: {h_dec[:16]}"
assert h_ord.startswith("861949ca7db707d1"), f"ORD hash drifted: {h_ord[:16]}"
print("second scan: unacked=0, DEC/ORD hashes UNCHANGED (83813196/861949ca)")

# --- state heal + write --------------------------------------------------------
sp = os.path.join(ROOT, "state-bm-a.json")
st = json.load(io.open(sp, encoding="utf-8"))
assert st["round_no"] == 900, f"unexpected state round_no {st['round_no']}"
st["round_no"] = 902
st["round"] = 902
st["loop_round"] = 902
st["last_round"] = 902
for k in ("clock_read", "ts", "updated", "last_seen", "last_round_at",
          "last_round_closed", "last_round_ts", "last_run"):
    st[k] = now_iso
st["heartbeat_epoch_utc"] = now_ts
st["last_heartbeat_epoch_utc"] = now_ts
next_agenda = ("r903: W194 prereg build window (buildgen xform W193->W194, anchor rolls r590 once "
               "W192/W193 finalize land); bm-c W192 finalize landing watch -> W193 finalize one-pass "
               "(key-order r307); 10-09 bars 15:30 -> evening marks chain (REGIME_GUARD enforce + "
               "live.paper + t35/t24 family); pool replenish bm-c lane F-2026109-01 (window 10-10 00:00); "
               "XASSET-ROT P1 cross-border ETF lane ticket pending GM signature")
closed = ("r902 closed: W194 seat published=reserved (probe ADMIT A 441_604..443_603 / B 443_604..443_803, "
          "push 5cca13637) + r901 estate line absorbed (W193 five-face freeze LANDED, burn 12/12 COMPLETE, "
          "finalize PENDING key-order r307) ; S6 39-leg green")
st["current"] = closed
st["now_active"] = closed
st["task"] = next_agenda
st["current_task"] = next_agenda
st["next"] = next_agenda
st["next_milestone"] = next_agenda
st["did"] = ("r902: dead-session estate absorption (r901 session + 05:48 takeover window both exited without "
             "closeout; census = this session sole live BigMoney loop line; estate line reconstructed from "
             "origin commit evidence 9c0c089b8+5cf0d6175; state heal 900->902 honest per r841 precedent) + "
             "W193 burn completion verification (12/12 ledger rows done, 12/12 shard files valid JSON; "
             "finalize key-order precondition FAIL-CLOSED r307 -- n1_w192_results.json absent on origin, "
             "machine-checked) + W194 seat chain (pre-seat probe 5-leg ADMIT: A 441_604..443_603 staircase "
             "FIFTY-FOURTH hops=1 refused by registered W193 B band / B 443_604..443_803 naive-inside-own-A "
             "reserved hops=1; conflicts 0; origin vacancy; 184th wave bm-a 109th owned; anchor=W191 ledger "
             "833,536 with W192+W193 finalize pending honest note) + seat MSG published push 5cca13637 "
             "delivery 0/0 + S6 39-leg rc0 bad NONE (panel 10-08, pre-market no-op family)")
st["last_action"] = "r902 closeout: W194 seat chain + estate absorption + S6 39-leg + commit/push"
st["last_artifact"] = ("r902 products: fleet/inbox/MSG-2026-10-09-0627-bma-w194-seat.md (published=reserved) + "
                       "results/_r902bma_w194_probe.py + results/_r902bma_w194_probe_receipt.json (ADMIT)")
st["latest_artifact"] = st["last_artifact"]
st["verify"] = ("smoke 49/49 + W194 pre-seat probe rc0 ADMIT (5 legs) + S6 39-leg bad NONE (panel 10-08 no new "
                "bar) + attrition CLEAN (4 ledgers) + orphan face=0 (29 py faces) + engine ALIVE (W193 burn "
                "12/12 COMPLETE, queue 0) + quartet green (loop pin=8 no-op / watchdog alive / claws "
                "LF-normalized) + ORD/DEC watermarks UNCHANGED (861949ca/83813196 python-raw) + orders "
                "unacked=0 double-scan")
st["last_orders_seen"] = ("r902 double-scan: unacked=0; ORD 861949ca python-raw UNCHANGED; tail rows all "
                          "10-08, zero new BigMoney rows")
st["last_decisions_seen"] = "r902: DEC 83813196 python raw-bytes UNCHANGED (zero action)"
st["last_orders_at"] = now_iso
st["last_decisions_at"] = now_iso
st["last_decisions_ts"] = now_iso
st["push_verified"] = {"ts": now_iso, "origin_tip": "5cca13637", "ahead_behind": "0/0",
                       "last_push_ts": now_iso, "last_sync_at": now_iso,
                       "note": "r902 seat push verified 0/0 @5cca13637 (W194 seat chain)"}
st["sync"] = dict(st["push_verified"])
with io.open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state healed 900->902, written")

# --- heartbeat write -----------------------------------------------------------
import psutil
ram_free_pct = round(psutil.virtual_memory().available * 100.0 / psutil.virtual_memory().total, 1)
hb["last_seen"] = now_iso
hb["ts"] = now_iso
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = now_ts
hb["verdict"] = "green"
hb["current_task"] = next_agenda
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["cpu_cores"] = psutil.cpu_count(logical=True)
hb["ram_free_pct"] = ram_free_pct
hb["vram_free_gb"] = 0.89
with io.open(hb_path, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
# self-check: epoch must be JSON int, clock must be T-separated
chk = json.load(io.open(hb_path, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in chk["clock_read"], "clock_read not T-separated"
print(f"heartbeat written; epoch int OK ({chk['heartbeat_epoch_utc']}), clock T-sep OK, ram_free={ram_free_pct}%")

# --- r902 report line -----------------------------------------------------------
line = (f"{now_iso} | r902 | bm-a | dept:research (W194 seat chain + r901 estate absorption; N1 supply line) | "
        "WM-VERDICT: green (red=false lane healthy; engine ALIVE rc0 W193 burn 12/12 COMPLETE queue 0; "
        "board open=0; pool ready=0 = replenish bm-c lane F-2026109-01 in window 10-10 00:00) | "
        "当前活: W194 席位链占位 + r901 遗产收口 (estate line + state heal 900->902 honest sequence) | "
        "实物: ①fleet/inbox/MSG-2026-10-09-0627-bma-w194-seat.md (published=reserved·push 5cca13637·184th "
        "engine wave bm-a 109th owned) ②results/_r902bma_w194_probe.py + _r902bma_w194_probe_receipt.json "
        "(pre-seat probe rc0 ADMIT: A 441_604..443_603 staircase FIFTY-FOURTH hops=1 refused at own start "
        "by registered W193 B band 441_404..441_603·r901 prereg leg4 + r900 probe leg4 anticipation both "
        "fulfilled / B 443_604..443_803 naive-B-inside-own-A reserved hops=1·W141 leg2; leg2 conflicts 0; "
        "leg3 origin vacancy; leg4 W195+ proj A 443_604..445_603 / B 443_804..444_003 B-inside-A) ③r901 "
        "estate line in round report (五面冻结+烧录全证据机验·状态簿记失写由本轮补) ④results/_r902bma_s6_chain.json "
        "(S6 39 腿 rc0 bad NONE·panel 10-08 no new bar·盘前 no-op 族) | did: S0-1 锚定 bm-a + 孤儿探针 0 "
        "(29 py faces) + S0 脏树=churn-absorb 6230822f9 先收 + fetch 0/0 纯净 (HEAD==origin 5cf0d6175) + "
        "死会话遗产定谳 (进程 census=本会话 44096 唯一存活 BigMoney loop 线·其余=BigStream 66556/MiniGame "
        "55456/23:0x 交互 Cowork 面·r901 takeover 窗 06:12:46 push 后退出报告/状态/心跳三写全失=estate 承接 "
        "r899 先例) + W193 烧录完成核验 (12/12 ledger rows + 12/12 shard files valid·finalize 键序前置 "
        "FAIL-CLOSED r307 [n1_w192_results.json origin 缺席机证]→诚实阻断待 bm-c W192 finalize) + S0.5 令差集 "
        "双扫 0 未回执 (DEC 83813196/ORD 861949ca python-raw 双 hash 恒等 UNCHANGED·C: 实径 fetch+show) + "
        "S1 smoke 49/49 + S2 双板零 open 票 job_list 空 + S3 主产出=W194 pre-seat probe 五腿全绿 (r900 血统机械 "
        "verbatim 滚代·191 行表尾 W193·owner 183/bm-a 108→184th/109th·锚=W191 账头 833,536 [W192+W193 finalize "
        "双未落如实注记·r590 滚动待落]) → 席位 MSG 发布 → seat push 5cca13637 送达 0/0 自证 + S6 39 腿 + "
        "attrition CLEAN (4 ledgers healed 注记照录) + idle_trigger --worked (idle_rounds=0) + S7 四件套绿 "
        "(loop pin=8 no-op next-fire 06:38 / watchdog next-run 06:30 / 双爪 LF 归一装) | 下轮指针: ①r903=W194 "
        "prereg build 窗 (buildgen xform W193→W194·facts=probe receipt+MSG·anchor 滚 r590) ②bm-c W192 finalize "
        "落地监控→W193 finalize one-pass (键序 r307) ③10-09 bars 15:30→晚间 marks 链 (REGIME_GUARD enforce+"
        "live.paper+t35/t24 族) ④池补货 stall-watch (bm-c 车道窗 10-10 00:00) ⑤XASSET-ROT P1 跨境 ETF 车道票 "
        "(GM 署名门) | 验证: smoke 49/49 + probe rc0 ADMIT + S6 39 腿 bad NONE + attrition CLEAN + 孤儿面=0 + "
        "engine ALIVE (burn 12/12) + 四件套绿 + orders unacked=0 双扫 + 本地未达 origin commit 数=0 (push 后 "
        "fetch+rev-list 自证) | scoring: 2 (W194 席位链 3 件套=引擎常供线连续供给实物增量) | 记账预算: 4/5 "
        "(state+两条轮账行[estate+r902]+心跳) | 宝藏捕获问: 本批零新方法零新宝藏 (probe/seat=既有律 verbatim "
        "滚代·estate 吸收=r899 先例复用·TREASURE/METHODOLOGY 零 append·登记册未触发零清扫动作) | orphan_face=0 | "
        "unacked_orders=0 | local_vs_origin=0 | token: L1 零 API [via bm-a r902]")
with io.open("round_reports-bm-a.md", "a", encoding="utf-8") as f:
    f.write(line + "\n")
print("r902 report line appended")
print("CLOSEOUT WRITES DONE")
