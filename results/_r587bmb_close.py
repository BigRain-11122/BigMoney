# r587 bm-b closeout: state bump + heartbeat + round report line (dynamic-fields-only law r583)
import json, time, datetime, psutil

now_iso = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# 1. state.json (bm-b special: root state.json, S5 law)
sp = "state.json"
s = json.load(open(sp, encoding="utf-8"))
s["round_no"] = 587
s["note"] = ("r587: W109 FREEZE five-face delivered end-to-end (99th engine wave by machine-derive rows 98+candidate, "
             "bm-b 37th owned rows 36+candidate; seat MSG-20261002-1817-bmb rev.B pushed to origin 99e29877c per r565 "
             "law BEFORE the freeze -- rev.B = first-draft B projection 60_801..61_000 corrected PRE-PUSH after the "
             "origin advance caught by the pre-push claw (r374 fork artifact), bm-c W108 freeze 3a3c51b73 landed "
             "mid-window, refusal point SEED_REGISTRY wild_route_s1=61_000 own-probe confirmed + cross-verified vs "
             "bm-c W108 gate-tail disclosure, zero prior visibility; band gate ADMIT rc0 single state A 261_004..263_003 "
             "+ B 61_001..61_200 VALUE-COLLISION JUMP hops=1 per law sec.4 W5 precedent family, "
             "results/_r587bmb_w109_band_gate.py; banned gate ADMIT 0; per-wave prereg frozen with anchors rolled to "
             "W103 finalize landed values chain head 591,148 K=224,520 r576 anchor-roll law; five-face pure insertion "
             "+31/+194/+2 FIX-A/B/C + AST + n1 selftest PASS with W109 materializer leg live + pf 9/9; freeze commit "
             "f077ae11b pushed FF) + engine ignition within minutes (tick architecture r535 law: n1w109-1of12 pid active "
             "-- product-growth proof at r325 law pending shard files) + S6 33 legs rc0 (dualrun ZERO-DRIFT streak 31/3, "
             "REPORT/LIVE-2026-10-02 regenerated, host-guarded faces honest skip, paper block honestly skipped: Golden "
             "Week LAST_BAR=2026-09-30 no new bar) + S7 5/5 (loop pin=2 no-op, watchdog registered, both claws "
             "installed, attrition CLEAN 4-healed) + WM py_low_with_work_cands legal face (W109 burn in flight = the "
             "supply-step ignition itself; moneyflow IC next_pick claimed; W14/N2-W15 governance-parked per r483)")
s["last_round_at"] = epoch
s["last_round_ts"] = now_iso
s["ts"] = now_iso
s["updated"] = "r587 bm-b: W109 freeze delivered + engine ignited + S6/S7 green"
s["updated_at"] = now_iso
json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state.json -> 587")

# 2. heartbeat fleet/machines/bm-b.json (dynamic fields only, orders_ack carried)
hp = "fleet/machines/bm-b.json"
h = json.load(open(hp, encoding="utf-8"))
vm = psutil.virtual_memory()
h["last_seen"] = now_iso
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = now_iso
h["current_task"] = "W109 burning (engine tick self-saw the freeze; 12/12 shards expected this evening); finalize chain waits on W104 bm-a upstream (FAIL-CLOSED r307); next bm-b finalize duty = W106 after W104/W105 land"
h["cpu_cores"] = psutil.cpu_count(logical=True)
h["free_ram_gb"] = round(vm.available / 1e9, 1)
h["gpu_free_vram_gb"] = h.get("gpu_free_vram_gb", 2.1)
h["total_ram_gb"] = round(vm.total / 1e9, 1)
h["cpu_util_pct"] = psutil.cpu_percent(interval=0.5)
h["round_no"] = 587
h["verdict"] = "W109 freeze delivered + engine ignited (never-dry supply); py_low_with_work_cands legal face (W109 burn in flight, W14/N2-W15 parked r483)"
assert isinstance(h.get("orders_ack"), list) and len(h["orders_ack"]) == 143, "orders_ack carry broken: %s" % len(h.get("orders_ack") or [])
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
loaded = json.load(open(hp, encoding="utf-8"))
assert isinstance(loaded["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
print("heartbeat ok: epoch=%d orders_ack=%d" % (loaded["heartbeat_epoch_utc"], len(loaded["orders_ack"])))

# 3. round report line (utf-8 append, EOL detected from file tail)
rp = "logs/iteration-loop/round_reports.md"
raw = open(rp, "rb").read()
eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
line = ("{ts} | r587 | WM=py_low_with_work_cands(py 55.3%@18:26 probe·合法面非违令：W109 引擎烧录在飞=本日供给步点火实证"
        "(audit 面 py_cpu 77.3%·30 py procs)·moneyflow IC next_pick=claimed 在飞·W14/N2-W15 治理停泊 r483 合法持有·板 0 open="
        "无可开新批候选) | 当前活=W109 冻结五面已交付+引擎 tick 自见点火烧录在飞(n1w109-1of12) | "
        "最近实物=commit f077ae11b W109 FREEZE 五面+research/PERPETUAL_N1_W109_PREREG.md(锚滚至 W103 实测 K=224,520)+"
        "带闸回执 results/_r587bmb_w109_band_gate.py(18:2x·A 261_004..263_003/B 61_001..61_200) | "
        "下个里程碑=W109 12/12 烧毕+引擎台账交付(今夜窗·tick 自燃)+W104 bm-a finalize 落地后链序推进 W105/W106(≤48h 窗·多机并跑) | "
        "做了什么=S0-1 锚定 bm-b+orders 143/143 差集空(格式对齐 .md 后缀修正)+D-19 r481 特例诚实 skip+smoke 47/47+引擎活(30s 心跳)·"
        "**W109 供给步全链**(本机引擎队列清空=never-dry 律触发·r585 W106 全范式复用)=席位 MSG 首稿被 pre-push 爪拦=origin 前进分叉伪影 r374"
        "→amend 修正 B 投影(算术窗 60_801..61_000 撞 SEED_REGISTRY wild_route_s1=61_000·本机独立机验=bm-c W108 gate 尾披露交叉验证一致"
        "·首稿从未推送=零外见性·rev.B 唯一发布面)+外科推送席位 99e29877c(r523 律·单件 payload·18 面 checkout 同步)+带闸 ADMIT rc0(单态 W2..W108 全注册"
        "·A 算术续带 hops 0·B 撞值跳位首个净窗 hops 1·法典 §4 W5 先例族·99th/37th 序数机面 derive)+禁向闸 ADMIT 0+五面纯插入 +31/+194/+2"
        "(FIX-A/B/C+AST·n1 selftest W109 物化腿活体 PASS dep W17..W103 head 591,148·pf 9/9)+冻结 FF 直推 f077ae11b+引擎点火实证"
        "(saturation status active_burns=n1w109-1of12)+inbox 两枚他机席位 MSG(W107 bm-a/W108 bm-c)消费归档 processed | "
        "S6 33 legs rc0(pool_dualrun ZERO-DRIFT 31/3·REPORT/LIVE-2026-10-02 再生·金周 LAST_BAR=2026-09-30 无新 bar=paper 块诚实跳过"
        "·车道守卫面诚实 no-op) | S7 自愈 5/5(loop pin=2 no-op·watchdog 注册·pre-commit/pre-push 双爪装·attrition CLEAN 4-healed) | "
        "验证证据=带闸/编辑/自测回执件 _r587bmb_w109_*+_r587bmb_seat_push.py 送达自证(seat on origin=True·ls-tree W109 prereg 在场)+"
        "S6 回执 _r587bmb_s6_chain.json anomalies=NONE+推送后 fetch 复核 | 本地未达 origin commit 数=0(冻结推送后复核·"
        "bm-a W107 ledger append 254b9d3f0 在后=他机前进非本机未达) | 下轮指针=W109 烧毕验证(产物增长面 r325 律·引擎台账 commit 自随)·"
        "W104 bm-a finalize 落地后 W105/W106 finalize 链序推进(本机 W106 finalize 待前置)·W110 席位=他机轮转位·orders 双扫照常"
        ).format(ts=now_iso)
with open(rp, "ab") as f:
    f.write(line.encode("utf-8") + eol)
print("round report line appended (eol=%r)" % eol)
