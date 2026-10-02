# r586 bm-b closeout: state bump + heartbeat + round report line (dynamic-fields-only law r583)
import json, time, datetime, psutil

now_iso = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# 1. state.json (bm-b special: root state.json, S5 law)
sp = "state.json"
s = json.load(open(sp, encoding="utf-8"))
s["round_no"] = 586
s["note"] = ("r586: W106 burn products 12/12 delivered to origin (2,200 backtests, workers=8, machine=bm-b, 96th engine wave; "
             "engine ledger 12 rows + faces ride) + S0 pure-FF surgical integration (e77cad0bb->e79dcf6b4: bm-c r377 wrap x2 + "
             "bm-a r587 wrap adopted; 55 shared/other-machine faces checkout-restored, bm-b live-writers kept; W106 seat MSG "
             "inbox/processed displacement artifact healed via blob-identity proof) + W14 governance face re-verified = PARKED "
             "per r483 verdict (RETAIL_QUANT_TRACK sec.1 W14 line: dual-draft confirmation-timing forbidden face + trial gate "
             "324/500; entry park honored r527 law, zero action, N2-W15 same-grammar hold) + S6 33 legs rc0 (dualrun "
             "ZERO-DRIFT 30/3, REPORT/LIVE-2026-10-02 regenerated, host-guarded faces honest skip) + WM py_low_board_clear "
             "(legal idle: board 0 open, bandit 0, pool sole entry = governance-parked W14; W107 = bm-a rotation berth; "
             "finalize chain W101 upstream FAIL-CLOSED honest wait) + S7 5/5 (loop pin=2 no-op, watchdog registered, "
             "pre-commit/pre-push claws verified, attrition CLEAN)")
s["last_round_at"] = epoch
s["last_round_ts"] = now_iso
s["ts"] = now_iso
s["updated"] = "r586 bm-b: W106 products delivered + S0 pure-FF + S6/S7 green"
s["updated_at"] = now_iso
json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state.json -> 586")

# 2. heartbeat fleet/machines/bm-b.json (dynamic fields only, orders_ack carried)
hp = "fleet/machines/bm-b.json"
h = json.load(open(hp, encoding="utf-8"))
vm = psutil.virtual_memory()
h["last_seen"] = now_iso
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = now_iso
h["current_task"] = "idle: W106 products delivered; finalize chain waits on W101 bm-a upstream (FAIL-CLOSED r307); next bm-b rotation wave = W109"
h["cpu_cores"] = psutil.cpu_count(logical=True)
h["free_ram_gb"] = round(vm.available / 1e9, 1)
h["gpu_free_vram_gb"] = h.get("gpu_free_vram_gb", 2.1)
h["total_ram_gb"] = round(vm.total / 1e9, 1)
h["cpu_util_pct"] = psutil.cpu_percent(interval=0.5)
h["round_no"] = 586
h["verdict"] = "W106 12/12 delivered; py_low_board_clear legal idle (board clear, bandit 0, W14 governance-parked); W107=bm-a rotation berth"
assert isinstance(h.get("orders_ack"), list) and len(h["orders_ack"]) == 143, "orders_ack carry broken: %s" % len(h.get("orders_ack") or [])
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
loaded = json.load(open(hp, encoding="utf-8"))
assert isinstance(loaded["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
print("heartbeat ok: epoch=%d orders_ack=%d" % (loaded["heartbeat_epoch_utc"], len(loaded["orders_ack"])))

# 3. round report line (utf-8 append, EOL detected from file tail)
rp = "logs/iteration-loop/round_reports.md"
raw = open(rp, "rb").read()
eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
line = ("{ts} | r586 | WM=py_low_board_clear(板 0 open/bandit 0/池唯一件=W14 治理停泊 r483 裁定泊位=合法 idle 白名单面；"
        "W107=轮转 bm-a 位+finalize 链 W101 上游 FAIL-CLOSED=诚实等待) | 当前活=W106 12/12 烧录产物交付 origin(本轮主产出) | "
        "最近实物=results/p2cal_ext/n1_w106/ 12 分片 2,200 回测(17:41-17:52 烧毕)+引擎台账 12 行 ride | "
        "下个里程碑=W101 bm-a finalize 落地后链序推进 W102/W103 finalize(~24h 窗)+W109 bm-b 轮转波位待 W107/W108 注册 | "
        "做了什么=S0 纯 FF 外科集成(e77cad0bb->e79dcf6b4 bm-c r377 wrap x2+bm-a r587 wrap 采纳;55 共享/他机面 checkout 取 origin;"
        "本机活写面保留;W106 seat MSG 位移伪影 blob 恒等治愈)+orders 143/143 差集空+D-19 诚实 skip(r481 特例)+smoke 47/47+"
        "W106 12/12 验核(audit 块逐件 n_backtests 总和=2,200·workers=8·machine=bm-b)+W14 治理面定谳=停泊非幽灵(r483 裁定+"
        "entry park honored r527 律=N2-W15 同语法连带自持=零动作)+S6 33 legs rc0(dualrun ZERO-DRIFT 30/3·REPORT/LIVE-2026-10-02 "
        "再生·host 守卫面诚实 skip)+S7 自愈 5/5(loop pin=2 no-op·watchdog 注册·双爪验证·attrition CLEAN 4-healed) | "
        "验证证据=分片 audit 块逐件核+S6 回执 _r586bmb_s6_chain.json anomalies=NONE+推送后 origin ls-tree n1_w106 复达+fetch 复核 | "
        "本地未达 origin commit 数=0(推送后复核) | 下轮指针=W107 bm-a 轮转位(bm-b 下一波=W109)·W101 落地后 W102/W103 链序 finalize·"
        "W14 泊位守 CEO §四闸解冻·S6 照常").format(ts=now_iso)
with open(rp, "ab") as f:
    f.write(line.encode("utf-8") + eol)
print("round report line appended (eol=%r)" % eol)
