# r403 bm-a close-out: state file, round report line, CODELY.md line, heartbeat.
# UTF-8 append-only for ledger files; heartbeat epoch MUST be JSON int (R170/R178 law).
import json, time, datetime as dt

NOW = dt.datetime.now().astimezone()
now_iso = NOW.strftime("%Y-%m-%dT%H:%M:%S") + NOW.strftime("%z")[:3] + ":" + NOW.strftime("%z")[3:]
now_plain = NOW.strftime("%Y-%m-%d %H:%M:%S")

ROUND = 403

DID = ("S0 pull-rebase collision resolved canonically (origin bm-c autofill main-ticks vs local bm-a judge-tick x2 replay UU runnable_pool.json -> "
       "merge_lane_views.py resolve x2 ALL_FACES union 104 entries done-absorb parse-verify -> rebase continue x2 -> reconcile ZERO-DRIFT r376 same-window law) "
       "+ 4h loop-gap diagnosis (18:09->22:13 zero bm-a rounds, both scheduled tasks alive Running/Ready pin=8, bm-b/bm-c stale-takeover of C-family single-writer faces lawful) "
       "+ S0.5 three order receipts acked (O-1925-bm-b/O-1925-bm-c = O-1755 toolchain execution receipts 33/33 skills in place; O-1930 fleet-consistency order issued via bm-a, both recipient RECEIPTs in-file) -> orders_ack 118->121 "
       "+ group ledger zero new rows (post D-06; two C rows council-pending votes already cast) "
       "+ smoke red fixed (sole red of the round): engine T+1 checker false-positive -- trades list carries EXIT records only, old opens-dict heuristic compared exit dates and hold_days<=1 misline; 09-28 bar made 159915 final exit hold_days=1 (legal 09-24 buy -> 09-28 sell, 09-25 mid-autumn holiday) trip it; fixed to hold_days<=0 signature (engine section-1 entry-day sell guard is the true gate) -> 26/26 (cross-machine benefit: bm-b/bm-c would hit the same false red on identical data) "
       "+ S6 36 legs rc=0: repo rates +11x 09-28 rows (GC001..R-007), options/moneyflow-rank/ths/ah four detached background refreshes spawned (checkpoint resumable), regime ORANGE d2, clock ORANGE_COOL sleeves4 activated0, paper chain idempotent post-bm-c-takeover (live.paper enforce honestly downgraded shadow pre-10-01), open-fill PASS zero-pending, prospect 22/22 drift0, promotion 0/22 honest, export 18 positions equity 5,988,732 CNY, live_usage cap50% state ORANGE, token delta=0")

VERIFY = ("smoke 26/26 PASS; S6 36/36 rc=0; reconcile zero-drift; register_loop pin=8 no-op; precommit claw OK; "
          "schtasks dual-alive (IterationLoop Running / Watchdog Ready); orders unacked 3->0; heartbeat epoch int self-verified")

NEXT = ("(1) trial-labor standing line: W4-JUDGE done (bm-b 19:13:28) + board empty + no in-flight verdict batch -> W5 wave prereg draft next round per T-97/T-98 lineage + W4 verdict-finalize watch (bm-b lane, 48h CEO clock); "
        "(2) T-109 s2 remaining bm-a faces: same-window corr card (REGIME-POLICY sims.npz in repo) + STEP-1 crisis-state scale grid freeze (T-106 detector bm-c in flight) + T-102 lane1/lane4 digests; "
        "(3) four background refreshes landing watch (options/moneyflow-rank/ths/ah -> next-round commit face); "
        "(4) 10-01 monthly first round live fire: science_audit + monthly_briefing + self_review incl SR6; "
        "(5) next 5x = r405 HANDOVER check")

STATE = {
    "round_no": ROUND,
    "did": DID,
    "verify": VERIFY,
    "next": NEXT,
    "last_round_at": now_iso,
    "current_task": ("round-closed R403 (S0 rebase collision resolved via canonical ALL_FACES recipe + smoke T+1 checker false-positive fixed 26/26 + "
                     "S6 36 legs green + 3 order receipts acked); active lanes T-102/T-109; next = trial-labor W5 prereg standing line"),
    "updated": now_plain,
    "round": ROUND,
    "loop_round": ROUND,
}

with open("state-bm-a.json", "w", encoding="utf-8") as f:
    json.dump(STATE, f, ensure_ascii=False, indent=1)

REPORT_LINE = (now_iso + " | R" + str(ROUND) + " bm-a (dept:工程+舰队·R403 空窗复活轮) | WM first-line verdict: 绿 (red=false; probe 22:32 insufficient_history n=1=4h 空窗后序列重建中; "
    "audit supply_floor ready1<3 诚实旗=T-107 bm-c 工程线在飞; 池 ready=1 INNOVATION-QUOTA-SLOT-2 bm-c autofill 在烧; W4-JUDGE 已收口 bm-b 19:13) | did: "
    "①S0 pull --rebase 撞车（origin bm-c autofill main-ticks vs 本地 bm-a judge-tick 两笔重放·UU=results/runnable_pool.json）正典解：classify_conflicts GREEN->merge_lane_views.py resolve ×2"
    "（ALL_FACES 面·三 stage 直读·union 104 entries·done 吸收·parse-verify·禁手写 union）-> rebase continue ×2 -> reconcile ZERO-DRIFT（r376 同窗律）"
    "②4h 轮空窗诊断：18:09->22:13 零 bm-a 轮·双计划任务存活（IterationLoop Running+Watchdog Ready·针位 8 无漂移）·期间 bm-b/bm-c 法定 stale-takeover 覆盖 C 族单写者面+heat 已采实证"
    "③S0.5 三令回执收口：O-1925-bm-b/O-1925-bm-c（O-1755 工具链执行回执·33/33 skills 全在位·yq 补齐面如实）+O-1930（机队一致性总括令·经 bm-a 签发·受令两机双 RECEIPT 在文 20:12/21:58）-> orders_ack +3=121/121"
    "④集团台账零新行（D-20260928-06 后无新增·C-20260927-01/02=council-pending 票已在册·C-20260928-02=O-1930 执行面）"
    "⑤修红（本轮唯一红项）：smoke engine T+1 检查器假阳——trades 列表只含出场记录（engine 单一 trades.append 面）·旧 opens-dict 启发式拿出场日互比+hold_days<=1 误线·09-28 bar 使 159915 末笔 hold_days=1 合法出场"
    "（09-24 买->09-28 卖·09-25 中秋休市实证）触发假阳；正解=hold_days<=0 出场签名（引擎 §1 入场日禁卖守卫=真门禁·同日往返结构不可能）；修复后 26/26（跨机受益面：bm-b/bm-c 同数据下轮必撞同假阳·拉本修复即免）"
    "⑥S6 36 腿全绿：repo 利率 +11×09-28 行（GC001 3738 行等）+options/moneyflow-rank/ths/ah 四分离后台刷新 spawn（checkpoint 断点续拉·本轮 commit 面排除 data/options 在写件）+regime ORANGE d2+clock ORANGE_COOL"
    "+live.paper enforce 诚实降级 shadow（10-01 日期门未开）+open-fill PASS 零 pending+prospect 22/22+promotion 0/22 诚实+export 18 仓 ¥5,988,732+live_usage cap50%+token delta=0+audit FLAG supply_floor 诚实（ready1<3·T-107 在飞）"
    " | verify: smoke 26/26；S6 36/36 rc=0；reconcile zero-drift；register_loop pin=8 no-op；precommit claw OK；orders 未回执 3->0 "
    " | next: (1)常设线 W5 波预注册起草（W4-JUDGE 收口->板空+无在飞判决批=T-97/T-98 谱系续作）+W4 verdict finalize 观察（bm-b lane·48h CEO 报钟）；(2)T-109 s2 剩余=同窗 corr 卡（REGIME-POLICY sims.npz）+STEP-1 危机态网格冻结（T-106 bm-c 在飞）+T-102 lane1/4 digests；(3)四后台刷新落地观察（下轮 commit 面）；(4)10-01 月首轮三件套实弹；(5)5x=r405 HANDOVER\n")

with open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8") as f:
    f.write(REPORT_LINE)

CODELY_LINE = ("- [2026-09-28 " + NOW.strftime("%H:%M") + "] r403 bm-a 执行记录：S0 rebase 撞车正典解（runnable_pool UU×2 重放腿=merge_lane_views resolve 联合 104+reconcile 零漂移）"
    "+smoke T+1 检查器假阳修复（坑：trades=纯出场记录面·旧 opens-dict 启发式误比出场日+hold_days<=1 误线·159915 合法 hold_days=1 末笔触发；正解=hold_days<=0 签名·引擎 §1 入场日禁卖守卫为真门禁）26/26 跨机受益"
    "+4h 空窗诊断（任务双活·他机法定接管）+三令回执（O-1925×2+O-1930）+S6 36 腿（repo 09-28 利率行+四后台刷新 spawn）。详情=round_reports-bm-a.md R403 行。\n")

with open("CODELY.md", "a", encoding="utf-8") as f:
    f.write(CODELY_LINE)

# heartbeat: live stats + epoch int + clock_read T-format + orders_ack +3
hb = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
hb["last_seen"] = now_iso
hb["current_task"] = STATE["current_task"]
hb["task"] = "round-closed"
try:
    import psutil
    hb["cpu_pct"] = round(psutil.cpu_percent(interval=1.0), 1)
    hb["free_ram_gb"] = round(psutil.virtual_memory().available / 1024**3, 1)
    hb["cpu_util_pct"] = hb["cpu_pct"]
    hb["idle_ram_gb"] = hb["free_ram_gb"]
except Exception as e:
    print("stat fallback (psutil):", e)
try:
    import subprocess
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                          capture_output=True, text=True, timeout=10).stdout.strip().splitlines()[0]
    gfree_mb = int(float(out))
    hb["gpu_free_vram_gb"] = round(gfree_mb / 1024, 1)
    hb["gpu_idle_vram_gb"] = hb["gpu_free_vram_gb"]
    hb["gpu_idle_vram_mb"] = gfree_mb
    hb["gpu0_free_vram_gb"] = hb["gpu_free_vram_gb"]
except Exception as e:
    print("stat fallback (nvidia-smi):", e)
hb["verdict"] = ("insufficient_history probe 22:32 window n=1 post-4h-gap (honest, resuming); audit FLAG supply_floor ready1<3 = T-107 bm-c engineering line in flight; "
                 "pool ready=1 INNOVATION-QUOTA-SLOT-2 burning bm-c autofill; W4-JUDGE done by bm-b 19:13 -> no in-flight verdict batch; "
                 "this-round carrier = S0 rebase-collision canonical resolution + smoke T+1 checker false-positive fix (26/26) + S6 36 legs; next = trial-labor W5 prereg standing line")
hb["round_no"] = ROUND
hb["round"] = ROUND
hb["loop_round"] = ROUND
for oid in ("O-20260928-1925-bm-b.md", "O-20260928-1925-bm-c.md", "O-20260928-1930-bm-a.md"):
    if oid not in hb["orders_ack"]:
        hb["orders_ack"].append(oid)
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = now_iso

with open("fleet/machines/bm-a.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# self-verify (R170/R178/R262 law): reload, epoch int, clock T-format, ack count
chk = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO8601 T-sep"
assert len(chk["orders_ack"]) == 121, "orders_ack must be 121"
json.load(open("state-bm-a.json", encoding="utf-8"))
print("close-out OK | epoch:", chk["heartbeat_epoch_utc"], "| clock:", chk["clock_read"], "| acks:", len(chk["orders_ack"]))
print("CODELY bytes:", __import__("os").path.getsize("CODELY.md"))
