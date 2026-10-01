# r535 bm-a closeout bookkeeping (state + heartbeat + round report)
import json, time, datetime, psutil

now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# --- state-bm-a.json ---
p = "state-bm-a.json"
s = json.load(open(p, encoding="utf-8"))
s["round_no"] = 535
s["did"] = ("r535 bm-a: (1) W24 freeze = THIRTEENTH engine wave bm-a fourth-owned "
    "(rotation slot W24=bm-a per W23 row verbatim; table tail fetch-verified clean): "
    "A 90_001..92_000 / B 39_500..39_699 both arithmetic-clean ADMIT "
    "(_r535bma_w24_band_gate.py, 21-row pre-W24 scan + N3-R1 leg, no skip R250) "
    "+ prereg PERPETUAL_N1_W24_PREREG.md (anchor W22 finalize r519 addendum K=46,320, "
    "cumulative K=50,720; W23 bm-c burning coexists per r531 band-disjoint law) "
    "+ law sec.4 W24 row (W25+ warning = bm-b slot) + N1_BANDS[24]/WAVE_CONFIGS "
    "+ selftest W24 materializer leg + banned gate ADMIT; "
    "(2) push rejected (bm-c r332 closeout raced) -> r523 surgical path: zero file "
    "intersection pre-check + commit-tree -p origin/main (in-script rev-parse per r531) "
    "-> 5b9ffb27b fast-forward + reset --mixed re-anchor + 40 origin-owned checkout sync; "
    "(3) engine ignition verified by product growth (tick architecture reads working "
    "tree fresh each minute = no restart needed): shard-0 20:14 -> 7+/12 growing, "
    "done_total 43->46+; (4) S6 chain 34 legs all rc0 holiday honest no-ops "
    "(dualrun ZERO-DRIFT streak 11/3); (5) MSG-202x (own-lineage W21 finalize "
    "prev-face verification, addressed ALL) read + archived")
s["verify"] = ("smoke 47/47; band gate ADMIT both tails; banned gate ADMIT zero-hit; "
    "n1 selftest PASS (W24 materializer leg) + pf 8/8; pool_core_samples.jsonl "
    "rebase conflict resolved as 317-line union (r294 domain law) via r501 "
    "false-rejection net path; attrition guard CLEAN; S6 34/34 rc0; "
    "origin synced at 5b9ffb27b")
s["next"] = ("r536: verify W24 12/12 burn completion + push remaining shard products; "
    "W24 finalize AFTER bm-c W23 finalize lands (registry order FAIL-CLOSED) "
    "+ S5 four-prediction + S7/S8 backfill at finalize window; W25=bm-b slot watch")
s["last_round_at"] = now
s["current_task"] = "r535 closed: W24 THIRTEENTH wave frozen (ADMIT) + engine burning 7+/12; finalize gated on bm-c W23"
s["last_round"] = 534
s["last_round_ts"] = now
s["round"] = 535
json.dump(s, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# --- heartbeat fleet/machines/bm-a.json ---
p = "fleet/machines/bm-a.json"
h = json.load(open(p, encoding="utf-8"))
h["last_seen"] = now
h["current_task"] = "r535 W24 THIRTEENTH engine wave frozen (A 90_001..92_000/B 39_500..39_699 ADMIT) + engine burning 7+/12 shards"
h["cpu_cores"] = psutil.cpu_count()
h["cpu_pct"] = psutil.cpu_percent(interval=0.5)
h["free_ram_gb"] = round(psutil.virtual_memory().available / 2**30, 1)
h["verdict"] = ("healthy: W24 frozen same-round (surgical 5b9ffb27b) + burn in flight; "
    "W23 (bm-c) finalize pending = W24 finalize registry-gated; board clean, pool next_pick=claimed")
h["heartbeat_epoch_utc"] = epoch
assert isinstance(h["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
h["clock_read"] = now
h["task"] = h["current_task"]
json.dump(h, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
# post-write self-check
h2 = json.load(open(p, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int) and "T" in h2["clock_read"]
print("heartbeat ok: epoch", h2["heartbeat_epoch_utc"], "clock", h2["clock_read"])

# --- round report append (UTF-8, one line + product three-liner) ---
line = (
f"{now} | r535 | dept:研究/工程 | WM=loaded_ok（引擎烧录窗·red=False·py 实测低但板净=烧录分片短批脉冲面）| 当前活: W24 引擎波烧录在飞（第十三枚引擎波·bm-a 第四枚自有波·本机引擎 7+/12 分片增长中）| 最近实物: PERPETUAL-N1-W24 冻结件集落 origin 5b9ffb27b（prereg+法典 §4 行+N1_BANDS[24]+WAVE_CONFIGS+selftest W24 腿+ADMIT 回执 _r535bma_w24_band_gate.py）+ results/p2cal_ext/n1_w24/shard-*.json 烧录增长中 | 下个里程碑: W24 12/12 烧毕（~20:26）→finalize 待 bm-c W23 finalize 落账按注册序跑（FAIL-CLOSED 链）；10-03 RW-5 外审（窗≤48h） | did: (1) S0-1 锚定 bm-a+S0 脏树=daemon 车道件 ride commit 8fc715cef→rebase 撞 pool_core_samples.jsonl（append 型·316+305 行集 union=317·r294 域律）→r501 假拒绝（零 unmerged 实锤）净路=commit -C 手工落位+quit+update-ref→push 干净·0 落后；S0.5 双扫 orders 139/139 零未回执+D-19 决策水位 753F99E8 MATCH-unchanged 零动作 (2) **主产出 W24 冻结六件套**（轮值槽 W24=bm-a per W23 行 verbatim·表尾 fetch 实核净空·W21=bm-a 实锚 finalize r534+3 续行）: A 90_001..92_000/B 39_500..39_699 双算术尾 CLEAN ADMIT（21 行 pre-W24 扫描+N3-R1 腿 70_000..70_005·免跳 R250）+prereg PERPETUAL_N1_W24_PREREG.md（锚=W22 finalize r519 addendum K=46,320·累计 K=50,720·W23 bm-c r332 冻结在烧共存 per r531 异带共存律=带域机证不相交）+法典 §4 W24 行（W25+ 警示 A 92_001..94_000/B 39_700..39_899=bm-b 槽位）+N1_BANDS[24]/WAVE_CONFIGS[24]+selftest W24 materializer 腿（finalize deps W17..W22 在场钉死·W23 不钉=in-flight 运行时 FAIL-CLOSED·prior-wave set derive 律）+禁向闸 ADMIT 零命中+n1 selftest PASS+pf 8/8 (3) push 被拒（bm-c r332 closeout rides 同窗抢道）→r523 外科路:双向零文件交集预检（我 5 件 vs origin 段 40 件·零交集）+temp-index commit-tree -p origin/main（parent 脚本内 rev-parse 实取 r531 律）→**5b9ffb27b** 纯快进推送+reset --mixed 重锚+40 件 origin-owned checkout 同步（r524 律·本机 6 活写车道件不在 origin 段=零触碰） (4) 引擎点火实证（r325/r330 律=产物增长面非 state 面）:bm-a tick 架构每分钟新进程读活树=W24 登记即自燃免重启·shard-0 20:14 落盘→7/12 增长·done_total 43→46+·队列自推进~60s/片 (5) S6 链 34 腿全 rc0 假日诚实 no-op（dualrun ZERO-DRIFT streak 11/3·update_daily cutoff 09-30 国庆假日合法·车道守卫 no-op×6·scorecard/dscore/REPORT/LIVE/build_status host=bm-a 再生·promotion 0/22 诚实·token 0） (6) MSG-202x（本机 lineage W21 finalize prev-face 验证回执·致 ALL）读后归档 processed (7) S7 自愈三件在位（loop pin=8 no-op·watchdog Ready 正法命名参数复查·claw byte-identical）+attrition CLEAN+月度三件 9 月套在册免双跑 | 验证证据: smoke 47/47+band gate ADMIT 双尾+banned ADMIT+n1/pf selftest 绿+S6 34/34 rc0+attrition CLEAN+心跳 epoch int json.loads 自证 | 计分: 2 分（W24 冻结件集+引擎烧录分片=能跑能看实物）| 本地未达 origin commit 数=commit 后自证 | next: r536=W24 12/12 烧毕核验+分片产物全量上 origin；W24 finalize 待 bm-c W23 finalize 落账后注册序跑（FAIL-CLOSED）+§5 四项判定+§7/§8 同窗回填；W25=bm-b 槽位观察窗 | [via bm-a]\n")
with open("round_reports-bm-a.md", "a", encoding="utf-8") as f:
    f.write(line)
print("round report appended")
