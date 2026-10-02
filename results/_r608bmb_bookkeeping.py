# r608 bm-b: round report line append (UTF-8 safe) + state.json bump + heartbeat refresh
import json, time, datetime

now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec='seconds')
epoch = int(time.time())

line = ("| " + iso + " | round 608 (bm-b) | 水位 verdict=绿（red=false·insufficient_history 非红诚实面——VALUE NULLS 烧录占 py ~50%）"
        "| S0 纯 FF no-op（local==origin 0/0 分歧零）；orders 150/150 双扫零未回执；"
        "D-19 诚实 skip（K: S4U 缺席先例 r597·水位 937A373D 不变；备用路径 MiniGame 仓 origin/master 无 docs/decisions.md 实证）；smoke 47/47 "
        "| S3 本轮主产出=**FUND-QUALITY-P1 judged cell QUALITY-ROE x2 DELIVERED to origin**"
        "（cells_QUALITY-ROE_x2.jsonl 401 行 pos-grid census bit-exact vs x1 + cont 面 sharpe_full 0.391·ret_full 2.292·n_days 6078；"
        "runner status 401/401 cont=Y；池 done-flip 07:26 已 origin 可见；commit 93fb399ed·push f49500b7d..93fb399ed）——"
        "x1+x2 双 anchor face 齐=anchor 网格判决面完备；VALUE NULLS 烧录在飞（pid 34396 fund_value_p1.py run --nulls·py ~50%）；"
        "QUALITY NULLS 2000+SENS 500 池 ready=daemon 点火域（finalize_ready=False missing=2498·r606 估 10-09 窗内）"
        "| CEO 三行面：当前活=VALUE NULLS 烧录看护+QUALITY NULLS/SENS 池候点（daemon 域）；"
        "最近实物=cells_QUALITY-ROE_x2.jsonl+cont_QUALITY-ROE_x2.json（07:4x 至 origin·commit 93fb399ed）；"
        "下个里程碑=FUND-QUALITY-P1 family finalize 判决面（NULLS 2000+SENS 500 烧完即达·10-09 开市窗内·VALUE ETA ~10-05 后接力）"
        "| S6 34/34 rc0；dualrun streak 13 drift=false；attrition CLEAN（4 files）；"
        "S7 自愈：loop pin=2 no-op+watchdog 活+satengine 任务活+双爪字节装 2/2；"
        "inbox 两件=bmb→bma 待 bm-a 收（非本机件）；token delta report +398/state +0/mandate +0·L1 零 API "
        "| 本地未达 origin commit 数=0（push 后 fetch+ls-tree 自证）"
        "| 下轮指针：NULLS/SENS 点火观察（VALUE 烧完 daemon 接力）+x2 后判决就绪度跟踪+MSG-0640/0725 候 bm-a 回执 | [via bm-b r608]")
with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(line + "\n")

s = json.load(open("state.json", encoding="utf-8"))
s["round_no"] = 608
s["note"] = ("r608: (1) MAIN PRODUCT: FUND-QUALITY-P1 judged cell QUALITY-ROE x2 DELIVERED to origin "
             "(cells_QUALITY-ROE_x2.jsonl 401 census rows pos-grid bit-exact vs x1 + cont face sharpe_full 0.391, "
             "commit 93fb399ed pushed). Anchor-grid dual-face (x1+x2) complete on origin. "
             "(2) VALUE NULLS burn healthy in-flight (pid 34396, py ~50%); QUALITY NULLS 2000 + SENS 500 pool-ready "
             "awaiting daemon claim (finalize_ready=False missing=2498; r606 estimate inside 10-09 window). "
             "(3) S0 pure-FF no-op (0/0 divergence); orders 150/150 double-scan zero unacked; D-19 honest skip "
             "(K: S4U absent, watermark 937A373D unchanged). S6 34/34 rc0; smoke 47/47; attrition CLEAN; "
             "dualrun streak 13; claws 2/2 + loop pin=2 + watchdog alive. "
             "Next: NULLS/SENS ignition watch -> family finalize on completion (10-09 window).")
s["last_round_at"] = 608
s["round_no_label"] = "round 608 (bm-b)"
for k in ("last_round_ts", "ts", "updated", "updated_at", "last_seen"):
    s[k] = iso
json.dump(s, open("state.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

h = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
h["last_seen"] = iso
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = iso
h["round_no"] = 608
h["round_no_label"] = "round 608 (bm-b)"
h["current_task"] = ("FUND-QUALITY-P1 burn phase: x2 DELIVERED (commit 93fb399ed); value NULLS in-flight (pid 34396, py ~50%); "
                     "QUALITY NULLS 2000 + SENS 500 pool-ready (daemon domain); family finalize after burn completion (10-09 window)")
h["verdict"] = ("round 608 done: MAIN PRODUCT = judged cell QUALITY-ROE x2 delivered to origin (cells 401 rows pos-grid bit-exact + "
                "cont face, commit 93fb399ed) = anchor-grid dual-face x1+x2 complete; S6 34/34 rc0; smoke 47/47; attrition CLEAN; "
                "dualrun streak 13; claws 2/2 + loop pin=2 + watchdog alive; orders 150/150 double-scan")
for k in ("ts", "updated", "updated_at"):
    h[k] = iso
h["cpu_util_pct"] = 58.5
h["free_ram_gb"] = 3.3
h["idle_ram_gb"] = 3.3
h["ram_free_gb"] = 3.3
h["ram_avail_gb"] = 3.3
h["gpu_idle_vram_gb"] = 2.28
h["gpu_idle_vram_mb"] = 2283
h["gpu_free_vram_gb"] = 2.28
h["gpu_free_vram_mb"] = 2283
h["gpu_vram_free"] = 2.28
json.dump(h, open("fleet/machines/bm-b.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# post-write self-verify: epoch must be JSON int (R170/R178 law)
chk = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must be ISO T-separated"
print("BOOKKEEPING OK epoch_int=True iso=", iso)
