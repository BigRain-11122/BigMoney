# r893 bm-b closeout: state.json + heartbeat + round report
import json, time, datetime, os

NOW_DT = datetime.datetime.now().astimezone()
CLOCK = NOW_DT.isoformat(timespec="seconds")
EPOCH = int(time.time())
R = "r893"
NEXTR = "r894"

DID = ("r893 水位红修复轮：WM red=pool-batch-runnable-idle-low-cpu 定谳=N2U3 leg-2 probe 完成烧后被 25min confirmer 误记 crash"
       "（r860 gap：trial-labor runner 无 pool_claims 握手件；probe_receipt 19:06:39 face=probe 256eps/8workers 完整在盘）→"
       "r860 三件套收口=tombstone 假崩 sig+worker-claim 件+harvest flip（autofill tick 19:26:04 自提交 8ba709d9c entry done）→"
       "池面 ready 清空=红 lane 根治；O-20261011-1917-bm-c 派单三任务 claimed 回执入节（G 系软著目录群定位/热点池 topics 定位/BigHouse 待定位）；"
       "smoke 49/49；W18 judge 池注册+S6 41 腿延 r894（红修复吃掉轮预算）")

NEXT = (NEXTR + ": O-1917 执行主轴（G 系 generate_copyright 对齐产出 > 热点池 POOL-SCORED-20261012 > BigHouse 首研究件）"
        " > W18 judge 池注册（47 blocks·入池前读 pit-pool/pit-pool-burn）> S6 41 腿全链 > 水位红牌复核"
        " > T-184 510880 transfer 10-12 15:30 > IntradayMarks Monday 10-12 09:25 watch > 48h CEO 报 due 10-13 11:2x")

ART = (R + ": results/_r893bmb_n2u3_closeout.py + results/pool_claims/N2U3-ALPHAGEN-RL-P1-LEG2-PROBE/n2u3-leg2-probe.bm-b.json "
       "+ crash_fuse tombstone + pool entry done flip 8ba709d9c（+O-1917 receipt 节 claimed 回执）")


def ram_sample():
    try:
        import psutil
        vm = psutil.virtual_memory()
        pct = round(100.0 * vm.available / vm.total, 1)
        gb = round(vm.available / (1024 ** 3), 1)
        return pct, gb
    except Exception:
        return None, None


RAM_PCT, RAM_GB = ram_sample()

# ---- state.json (bm-b uses state.json per fleet/README §6) ----
with open("state.json", encoding="utf-8") as fh:
    st = json.load(fh)
st.update({
    "clock_read": CLOCK, "ts": CLOCK, "updated": CLOCK, "updated_at": CLOCK,
    "last_round_at": CLOCK, "last_round_ts": CLOCK, "last_seen": CLOCK,
    "last_action_at": CLOCK, "last_action": DID, "did": DID, "now_active": R + " closeout",
    "task": NEXT, "current_task": NEXT, "next": NEXT,
    "next_milestone": "O-1917 G 系+热点池 deliverable 10-12 12:00; BigHouse 首研究件 10-12 18:00; W18 judge 池注册 r894; 48h CEO 报 10-13 11:2x",
    "latest_artifact": ART, "note": R + ": WM-red P0 consumed round budget (N2U3 false-crash three-piece closeout); O-1917 claimed receipts in order file",
    "round": 893, "round_no": 894, "round_no_label": R,
    "orphan_face": 0, "orphan_faces": 0,
    "orphan_face_note": R + " round probe: 0 orphans (probe report results/_orphan_face_probe.bm-b.json)",
    "verdict": "GREEN: " + R + " WM-red fixed (N2U3 false-crash tombstone + claim + harvest flip entry done; pool ready cleared); smoke 49/49; O-1917 three tasks claimed; W18 judge reg + S6 deferred r894",
})
with open("state.json", "w", encoding="utf-8") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)

# ---- heartbeat fleet/machines/bm-b.json ----
HP = os.path.join("fleet", "machines", "bm-b.json")
with open(HP, encoding="utf-8") as fh:
    hb = json.load(fh)
ack = hb.get("orders_ack", [])
NEW_ORDER = "O-20261011-1917-bm-c.md"
if NEW_ORDER not in ack:
    ack.append(NEW_ORDER)
hb.update({
    "clock_read": CLOCK, "ts": CLOCK, "updated": CLOCK, "updated_at": CLOCK,
    "last_seen": CLOCK, "last_round_at": CLOCK, "last_action_at": CLOCK,
    "last_action": DID, "did": DID, "now_active": R + " closeout",
    "task": NEXT, "current_task": NEXT, "next": NEXT,
    "next_milestone": "O-1917 G 系+热点池 10-12 12:00; BigHouse 首研究件 10-12 18:00; W18 judge 池注册 r894; 48h CEO 报 10-13 11:2x",
    "latest_artifact": ART, "note": R + ": WM-red P0 round; N2U3 three-piece closeout landed",
    "round": 893, "round_no": 894,
    "heartbeat_epoch_utc": EPOCH,
    "orders_ack": ack, "orders_ack_count": len(ack),
    "idle_rounds": 0, "agenda_starved": False,
    "orphan_face": 0, "orphan_faces": 0,
    "orphan_face_note": R + " round probe: 0 orphans",
    "verdict": "green",
})
if RAM_PCT is not None:
    hb["ram_free_pct"] = RAM_PCT
    hb["ram_free_gb"] = RAM_GB
    hb["free_ram_gb"] = RAM_GB
with open(HP, "w", encoding="utf-8") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)

# sanity: epoch must be int (R170/R178 law)
with open(HP, encoding="utf-8") as fh:
    check = json.load(fh)
assert isinstance(check["heartbeat_epoch_utc"], int), "epoch must be JSON int"
print("heartbeat ok: epoch int =", check["heartbeat_epoch_utc"], "ram", RAM_GB, "GB", RAM_PCT, "%")

# ---- round report (bm-b uses logs/iteration-loop/round_reports.md) ----
RP = os.path.join("logs", "iteration-loop", "round_reports.md")
line = (f"{CLOCK} | {R} | {DID} | 证据: pool entry N2U3-ALPHAGEN-RL-P1-LEG2-PROBE status=done done_at=19:26:04 (harvest flip commit 8ba709d9c); "
        f"fuse sigs alphagen keys=[] (tombstone→cleared); probe_receipt 19:06:39 256eps/8workers; smoke 49/49; O-1917 receipt 节 claimed 回执; "
        f"本地未达 origin commit 数=见 push 自证 | 下轮指针: {NEXT}\n")
with open(RP, "a", encoding="utf-8") as fh:
    fh.write(line)
print("round report appended")
print("CLOSEOUT OK", CLOCK)
