# r824 bm-b closeout writer: state.json + heartbeat + round report + inbox move.
# r818 law: heartbeat big-list fields via script load-modify-save (orders_ack untouched).
import io, json, shutil, time

now = "2026-10-10T08:40:30+08:00"
epoch = int(time.time())

# ---------- state.json (bm-b lane file) ----------
sp = "state.json"
st = json.load(io.open(sp, encoding="utf-8"))
st["round_no"] = 824
st["round_no_label"] = "r824"
st["round"] = 823
st["note"] = ("r824: dying-session rebase legacy rescued (r813 sequence: classifier + dying-session resolver "
 "verification + ring-1 add/continue, 13 UU faces parse-verified, compute_audit history=210 union receipt-identical, "
 "jsonl unions 134/136 zero-loss) -> multi-ring pre-push claw race (2 blocks: stale base -> ring-2 rebase onto d2244da4b; "
 "bm-c per-minute tick moving target -> ring-3 tight cycle) -> push LANDED fa222465a..0d0028cdc; r823 northbound "
 "deliverables on origin; CODELY.md mini-split debt discharged (31767->30384B, r813x2->pit-git-resolver-rebase, "
 "r814->pit-protocol-d19, r824 claw-race lesson appended, receipt _r824bmb_codely_minisplit.json); S6 40 legs rc0 "
 "(ZERO-DRIFT streak 9; Saturday legs legit no-op); smoke 49/49; orders 60/184 zero unacked; DEC/ORD MATCH both keys; "
 "attrition CLEAN; orphans=0")
st["did"] = st["note"]
st["verdict"] = ("r824: engineering round - dying-session r823 rebase legacy fully rescued + pushed "
 "(fa222465a..0d0028cdc main landed, claw passed, r823 northbound probe/evidence/survey now on origin); CODELY.md "
 "over-cap debt discharged via mini-split (main 30384B<=30720B cap); smoke 49/49; S6 40 legs rc0 ZERO-DRIFT streak 9; "
 "watermark red=false healthy; orders both sweeps zero unacked (60/184); ORD/DEC hash MATCH both keys; attrition CLEAN; "
 "orphans=0")
st["now_active"] = "r824: dying-session rebase rescue + multi-ring claw-race push landed (fleet integration)"
st["latest_artifact"] = ("r824: pushed chain fa222465a..0d0028cdc (r823 northbound deliverables + rescue resolver "
 "receipts results/_r823bmb_rebase_resolve.json + results/_r824bmb_ring2_resolve.json + CODELY minisplit receipt "
 "results/_r824bmb_codely_minisplit.json), 2026-10-10 08:3x")
st["current_task"] = ("P3 explore E4 head ready for r825 full-round claim (central-bank OMO liquidity indicator face; "
 "check same-day new CEO orders before claiming); waiting: W17-JUDGE drain (bm-c lane) / Monday 10-12 09:15 "
 "minute_feed gated backfill")
st["task"] = st["current_task"]
st["next"] = ("r825: P3 explore E4 head (central-bank OMO liquidity indicator face: OMO net injection -> REPO rate "
 "linkage, REPO_PANEL consumer, survey-first, check same-day new CEO orders before claiming); waiting: W17-JUDGE "
 "drain (bm-c lane) / Monday 10-12 09:15 minute_feed first gated run backfills 10-08/10-09")
st["next_milestone"] = ("r825+: P3 explore E4 head (central-bank OMO liquidity indicator face, survey-first, <=48h) / "
 "Monday 2026-10-12 09:15 minute_feed first gated run backfills 10-08/10-09 / W18 wave drafting once W17-JUDGE drains")
st["last_action"] = ("r824: dying-session rebase rescue (r813 sequence, 3 rings, claw race won) + push landed + "
 "CODELY.md mini-split + S6 40 legs rc0 + S7 quartet green + attrition CLEAN + MSG-bma E5 declaration processed")
st["last_round_at"] = now
st["last_round_ts"] = now
st["ts"] = now
st["updated"] = now
st["updated_at"] = now
st["last_seen"] = now
st["clock_read"] = now
json.dump(st, io.open(sp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# ---------- heartbeat (r818: load-modify-save, orders_ack untouched) ----------
hp = "fleet/machines/bm-b.json"
hb = json.load(io.open(hp, encoding="utf-8"))
hb["round"] = 824
hb["round_no"] = 824
hb["now_active"] = st["now_active"]
hb["current_task"] = st["current_task"]
hb["task"] = st["current_task"]
hb["latest_artifact"] = st["latest_artifact"]
hb["next_milestone"] = st["next_milestone"]
hb["verdict"] = st["verdict"]
hb["last_action"] = st["last_action"]
hb["last_round_at"] = now
hb["last_seen"] = now
hb["updated"] = now
hb["ts"] = now
hb["clock_read"] = now
hb["heartbeat_epoch_utc"] = epoch
assert isinstance(hb["heartbeat_epoch_utc"], int)
hb["free_ram_gb"] = 11.3
hb["gpu_free_vram_mb"] = 3457
hb["gpu_free_vram_gb"] = 3.4
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_faces"] = 0
hb["orphan_face_note"] = "probe 16 py faces 0 orphans (r824)"
hb["sync"] = {"ahead": 0, "behind": 0, "last_push_ts": now,
              "note": "r824: 3-ring claw race won, push landed fa222465a..0d0028cdc; verify = post-push fetch+rev-list+ls-remote self-proof"}
json.dump(hb, io.open(hp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# ---------- round report append ----------
line = (now + " | r824 bm-b | dept:工程（濒死会话 rebase 遗产抢救·多环爪竞速推送闭环） | WM-VERDICT: 绿：red=false·lane healthy | "
 "孤儿面=0（probe 16 py faces 0 orphans） | ①S0-1 锚定 bm-b；S0 撞濒死会话 rebase 遗产（r823 会话 08:12:48 死于 pull --rebase "
 "冲突中途·4 pick 链·13 UU 面·非 porcelain git status 首行定谳）→r813 抢救序列：分类器 7 配方+6 docs 手工定性→dying 会话自家 "
 "resolver（results/_r823bmb_resolve.py+回执：11 快照 take-new+2 台账四源 union）核验过（13 件 parse-verify·compute_audit "
 "history=210=union 回执恒等）→add+continue 同秒律环1 完成（pick3/4 daemon 面 take-ours+jsonl union 134/136 行零丢失）；"
 "②push 爪双拦两连（爪读 push 协商真实远端 tip 非本地 ref：一拦=删集 bm-a r947 LHB 件+池 owner_since 08:16:05→08:05:30 回退"
 "〔陈旧基座信号〕→fetch 实核 origin 进 5→环2 rebase 7 UU〔6 S6 面 ts 取新+ledger union+explore.md 双机消耗行 union r823"
 "→r947 时序〕→二拦=origin 又进〔bm-c autofill keepalive 分钟 tick 08:29:06/08:30:05 移动目标〕→环3 紧凑三步单命令竞速="
 "live daemon 面 add -A 吸收 commit f397ca786→fetch→rebase 5/5 零冲突〔我方提交不触碰对端 tick 的 2 pool 文件=竞速零冲突条件〕"
 "→push 同命令连发=**fa222465a..0d0028cdc main 落地**（爪过快进收下）r823 北向全套交付物上 origin；③S0.5 双扫 orders "
 "60/184 unacked=0+D-19 正典探针 DEC a3ea37bd/ORD e286f842 双 MATCH 零新令零新决策；④S1 smoke 49/49；S2 job_list 0+fleet "
 "票 open=0；S3 水位红牌 false+饱和引擎活（heartbeat 47s·burns 0）+idle green_idle=false（VRAM 3.38GB<6GB 档）无义务；"
 "claimable_pool_lines=2=W17 族 bm-c lane-pinned 非本机可领→E4 explore 队头留 r825 全轮窗领做（本轮工程抢救占满工时·续作点="
 "state.next）；⑤S6 40 腿全 rc0（dualrun ZERO-DRIFT streak 9·排 compute_audit 前〔T-116 s3 顺序律〕；周六无新 bar quad 合法"
 "跳过；lane 守卫腿诚实 no-op；thermo+DUALARM-2026-09-30〔指数臂 BEAR〕+market_clock CALL-2026-09-30 ORANGE_COOL+REPORT/"
 "LIVE-2026-10-10 再生落 CEO 面；token delta=0）；⑥S7 四件套绿（loop pin=2 no-op·watchdog 首发 08:39·双爪重装）+attrition "
 "CLEAN；⑦CODELY.md 主件越帽债当窗清偿=mini-split（31,767→30,384B：r813 双行 verbatim→pit-git-resolver-rebase.md〔30,617B〕"
 "+r814 行→pit-protocol-d19.md〔25,650B〕+r824 爪竞速教训 853B 入主件·回执 _r824bmb_codely_minisplit.json·verbatim 断言全绿）；"
 "⑧inbox MSG-2026-10-10-0830-bma（bm-a E5 slice-2 在制声明）处理→processed/（回执：bm-b 无撞面——E5=bm-a 车道已判负收口 "
 "0/12·我 E4 车道正交·避让确认） | 等待态一行声明：W17-JUDGE drain=bm-c 道在跑（ETA ~22:45）；周一 10-12 09:15 minute_feed "
 "首 gated 轮回补 10-08/10-09 | 验证证据: push fa222465a..0d0028cdc+13 件 parse-verify+union 行数断言（210/134/136）+smoke "
 "49/49+S6 40 legs rc0 逐腿 exit 码核账 results/_r824bmb_s6_log.txt+dualrun ZERO-DRIFT streak 9+attrition CLEAN+双扫零未回执"
 "+心跳 epoch int 自证 | 记分: 2（机队集成抢救=能跑能推实物：4+1 commit 链上 origin+r823 交付物送达） | 记账预算: 4/5（state+心跳"
 "+轮报+CODELY mini-split·explore 队列本轮零触碰） | 宝藏捕获: 坑律 1 条（多环 push 爪竞速判例入 CODELY.md 主件·git 域回扫候选 "
 "pit-git-staged）；方法论资产卡零新方法 | unacked_orders=0 | 本地未达 origin commit 数：0（commit 后 push+fetch+rev-list "
 "自证） | 下轮指针: r825: ①P3 explore E4 队头（央行 OMO 流动性指标面：OMO 净投放→REPO 利率联动·调研先行·领队头前先查当日新 "
 "O 令面）②W17-JUDGE drain 观察→W18 起草窗③周一 10-12 09:15 minute_feed 首 gated 轮回补 10-08/10-09")
with io.open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8", newline="") as f:
    f.write(line + "\n")

# ---------- inbox MSG -> processed ----------
src = "fleet/inbox/MSG-2026-10-10-0830-bma.md"
dst = "fleet/inbox/processed/MSG-2026-10-10-0830-bma.md"
shutil.move(src, dst)

print("closeout written: state r824 + heartbeat epoch=%d + round report line (%dB) + MSG moved" % (epoch, len(line.encode('utf-8'))))
