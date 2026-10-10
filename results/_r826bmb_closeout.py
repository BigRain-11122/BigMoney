# r826 bm-b closeout: state.json + heartbeat bm-b.json + round report row.
# r818 law: load-modify-dump (orders_ack big list NEVER hand-retyped). ASCII stdout only.
import io, json, time, datetime

NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")
EPOCH = int(time.time())

# ---------- state.json ----------
sp = "state.json"
st = json.load(io.open(sp, encoding="utf-8"))
st["round_no"] = 826
st["round_no_label"] = "r826"
DID = ("r826: S0 dual-pick rebase collision rescue vs bm-a r948 (same-window E4 dual-dev + S6 storm): "
       "25 faces (21+4) canonical closeout via classifier 18 + manual 3 (attrition snapshot / AA probe yield / queue md merge) + daemon live-wins 4; "
       "AA scripts/omo_liquidity_probe.py yielded to origin land-order primary (bm-b findings preserved at results/omo_liquidity_probe.json + OMO_LIQUIDITY_DATA_FEASIBILITY.md, dual survey docs archived, explore.md E4 row dual-annotated + r825 yield record); "
       "snapshot family hardened deep-ts probe all-newer side (r100/R350; REPORT twins same-second tie->HEAD r140); compute_audit/regime_state ledger union zero-loss; "
       "both picks closed manually with author preservation + marker guard, push LANDED 12111ce5a..fd5a4e2b2; "
       "T-18 queue-head collision probe delivered (scripts/queue_head_collision_probe.py: advisory origin-blob heartbeat in_flight/declared_intent dual-tier + alnum word-boundary + 120/240min windows + origin queue-head STALE_LOCAL check; selftest 18/18 hermetic byte-identical double-run; "
       "live-fire: explore head E6 verdict=DECLARED_INTENT_RISK (bm-a heartbeat next 'r949: E6 P3 head' captured, matches manual read; 3rd event inside 24h after E3/E4); "
       "iteration_prompt.txt S3 pre-claim guard leg wired r931 anchor-surgery 49788->50199B leg x1 CRLF-preserved; tech queue 0->1->0 same-round seed+consume); "
       "E6 head yielded to bm-a per probe+heartbeat dual evidence; "
       "S6 41 legs rc0 (dualrun ZERO-DRIFT streak 11; zt_pool_crosscheck welded into chain rc0; Saturday no-new-bar legs legal skip); "
       "smoke 49/49; orders 60/60 both sweeps CLEAN; DEC/ORD hash MATCH both keys; attrition CLEAN; orphans=0")
st["did"] = DID
st["verdict"] = ("r826: engineering round - S0 same-window collision (bm-a r948) rescued zero-loss 25 faces + E4 dual-dev yield reconciled; "
                 "T-18 queue-head collision probe landed + wired (root-cause fix for E3/E4/E6 3-in-24h collision pattern); "
                 "smoke 49/49; S6 41 legs rc0 ZERO-DRIFT streak 11; watermark green (red=false, py_low_board_clear legal-idle whitelist); "
                 "orders 60/60 zero unacked; DEC/ORD MATCH; attrition CLEAN; orphans=0")
st["current_task"] = ("r827: first round with T-18 probe live in loop prompt (verify fleet adoption); E6 stays bm-a's (yielded); "
                      "watch W17-JUDGE drain (bm-c lane, 9 ready shards) -> W18 drafting window; Monday 2026-10-12 09:15 minute_feed first gated run backfills 10-08/10-09")
st["task"] = st["current_task"]
st["next"] = ("r827+: post-E6 queue head watch (E7 candidate once bm-a consumes E6 - claim only with T-18 probe CLEAR); "
              "W17-JUDGE drain -> W18 drafting window; Monday 2026-10-12 09:15 minute_feed gated backfill")
st["now_active"] = "r826: S0 collision rescue + E4 yield reconciliation + T-18 collision probe landed+wired + S6 41 legs (fleet integration steady)"
st["latest_artifact"] = ("r826: scripts/queue_head_collision_probe.py + Tools/iteration_prompt.txt S3 guard leg (49788->50199B) + "
                         "results/queue_head_collision_probe.json + resolver receipts results/_r826bmb_rebase_resolver.json + _r826bmb_rebase_resolver_p2.json, 2026-10-10 09:3x")
st["next_milestone"] = ("r827-r830: T-18 probe fleet-adoption verification + post-E6 queue consumption; "
                        "W17-JUDGE drain -> W18 drafting window (<=48h watch); Monday 2026-10-12 09:15 minute_feed first gated backfill 10-08/09")
st["last_action"] = ("r826: S0 25-face collision rescue zero-loss + E4 yield + T-18 probe landed/wired + S6 41 legs rc0 + S7 quartet green")
for k in ("last_round_at", "last_seen", "last_round_ts", "ts", "updated", "updated_at", "clock_read"):
    st[k] = TS
io.open(sp, "w", encoding="utf-8", newline="\n").write(json.dumps(st, ensure_ascii=False, indent=1) + "\n")

# ---------- heartbeat ----------
hp = "fleet/machines/bm-b.json"
hb = json.load(io.open(hp, encoding="utf-8"))
ack_before = len(hb.get("orders_ack", []))
hb["round_no"] = 826
hb["round"] = 825
hb["now_active"] = st["now_active"]
hb["current_task"] = st["current_task"]
hb["task"] = st["current_task"]
hb["latest_artifact"] = st["latest_artifact"]
hb["next_milestone"] = st["next_milestone"]
hb["verdict"] = st["verdict"]
hb["last_action"] = st["last_action"]
for k in ("last_round_at", "last_seen", "updated", "ts", "clock_read"):
    hb[k] = TS
hb["heartbeat_epoch_utc"] = EPOCH
hb["cpu_cores"] = 16
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
try:
    import psutil
    hb["free_ram_gb"] = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    hb["free_ram_gb"] = 10.5
hb["gpu_free_vram_mb"] = 3370
hb["gpu_free_vram_gb"] = 3.37
io.open(hp, "w", encoding="utf-8", newline="\n").write(json.dumps(hb, ensure_ascii=False, indent=1) + "\n")
assert isinstance(json.load(io.open(hp, encoding="utf-8"))["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
assert len(json.load(io.open(hp, encoding="utf-8"))["orders_ack"]) == ack_before, "orders_ack mutated"

# ---------- round report row ----------
ROW = ("{ts} | r826 bm-b | dept:工程（S0 同窗撞车抢救+E4 让路收口）+dept:工程（T-18 队头撞头探针） | "
       "WM-VERDICT: 绿（red=false；py_low_board_clear=合法闲置白名单〔板全闭环+bandit 0+本机可跑池批 0——池 9 ready 全 W17 bm-c 车道非本机候选〕）| "
       "CEO three-line: 当前活=r826 S0 双 pick 撞车 25 面 canonical 收口+E4 双开发让路+T-18 撞头探针落地接线；"
       "最近实物=scripts/queue_head_collision_probe.py+Tools/iteration_prompt.txt S3 前置腿（49788→50199B·leg x1）+results/queue_head_collision_probe.json, 2026-10-10 09:3x；"
       "下个里程碑=W17-JUDGE 排空→W18 起草窗（≤48h watch）+周一 10-12 09:15 minute_feed 门控首轮回补 | "
       "做了什么：①S0=lane-sync 吸收 commit 后 pull --rebase 撞 bm-a r948（同窗双开发 E4 撞头+S6 面风暴）双 pick 25 面 canonical 收口"
       "——分类器 18+手工定性 3：AA scripts/omo_liquidity_probe.py 按 land-order 让路取 origin 侧 384 行版"
       "（bm-b 641 行版发现保全于 results/omo_liquidity_probe.json+research/shortline/OMO_LIQUIDITY_DATA_FEASIBILITY.md 独立路径·双调研件并档·explore.md E4 行双注记+r825 让路记录 r947-E3 范式）；"
       "snapshot 族 hardened deep-ts 探针（r100 键归一+R350 墙钟值形）全取更新侧（bm-a 09:04-09:08>bm-b 08:57-09:00·REPORT 双胞胎同秒 tie→HEAD r140）；"
       "compute_audit/regime_state 双账 union 零丢失（receipt _r826bmb_rebase_resolver.json）·daemon 4 面 live-wins（jsonl 行 union 127·receipt _r826bmb_rebase_resolver_p2.json）；"
       "双 pick 手工落（r808 author-script 保真+marker 守卫零入库）·push LANDED 12111ce5a..fd5a4e2b2 fetch 自证；"
       "②T-18 队头撞头探针=scripts/queue_head_collision_probe.py（advisory·origin blob 新鲜读他机心跳 current_task/task=in_flight+next/now_active=declared_intent 双档声明匹配"
       "+alnum 词界防 E6/E60/E6x 误配+120/240min 新鲜窗分档+origin 队头对账 STALE_LOCAL_QUEUE=先 pull 再判；"
       "selftest 18/18 hermetic 双跑 stdout 字节恒等；live 实弹=探索头 E6 verdict=DECLARED_INTENT_RISK〔bm-a 心跳 next「r949: E6 P3 head」被探针捕获=与 r826 会话人工判读完全一致——E3/E4 双撞后 24h 内第三事件现场实证〕；"
       "iteration_prompt.txt S3 领队头前置腿 r931 anchor-surgery 49788→50199B leg x1 CRLF 保真·_r826bmb_prompt_wire.py 收据）；tech 队列 0→1→0 同轮建面同轮出列（种子=三连撞真实工具面缺口）；"
       "③E6 P3 头让路 bm-a（探针+心跳声明双证）；"
       "④S6 41 腿 rc0（dualrun ZERO-DRIFT streak 11·419 entries·zt_pool_crosscheck 焊入链 rc0〔r828 链位注记·软警 strong∩dtgc 已知良性〕·dualarm DUALARM-2026-09-30 index=BEAR·market_clock ORANGE_COOL sleeves=4 activated=0·周六无新 bar 合法跳过·lane 守卫族诚实 no-op）；"
       "⑤S7 四查绿（schtasks 4/4 OK 经 Invoke-SilentExe 零窗包装·双爪 IN-SYNC·孤儿面=0〔probe 16 py faces〕·attrition CLEAN 4 台账） | "
       "验证：smoke 49/49 PASS；post_review run 重derive 45Y/0N/5W；orders 双扫 60/60 CLEAN 零 unacked（orders_ack_scan 124 stale notes 软档非债）；"
       "DEC/ORD 双水位 MATCH（a3ea37bd/e286f842 canonical probe _r686bmb_d19_check.py）；探针 selftest 18/18+prompt 手术 leg x1 字节验证；S6 41 腿全 rc0 | "
       "下轮指针：r827=撞头探针接线后首轮（三机消费验证）+E6 归 bm-a 后队列下头候补观察〔领前必跑探针〕+W17-JUDGE 排空→W18 起草窗+周一 10-12 09:15 minute_feed 门控首轮回补 10-08/09 | "
       "孤儿面=0；本地未达 origin commit 数=0（push 后 fetch 自证）").format(ts=TS)
rp = "logs/iteration-loop/round_reports.md"
b = io.open(rp, "rb").read()
eol = b"\r\n" if b.endswith(b"\r\n") else b"\n"
if not b.endswith(b"\n"):
    b += b"\n"
io.open(rp, "wb").write(b + ROW.encode("utf-8") + eol)
print("CLOSEOUT OK: round_no=826 epoch=%d ack=%d ram=%.1f ts=%s" % (EPOCH, ack_before, hb["free_ram_gb"], TS))
