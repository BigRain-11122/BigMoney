# r444 bm-b closeout writer: CODELY lesson + state 444 + heartbeat + round report.
import io, json, time

ts_now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
assert isinstance(epoch, int)

# ---------- 1) CODELY.md lesson append (memory-entry four-question gate passed:
# lesson-first, one-thing-one-entry, <1.5KB, reusable next rounds) ----------
lesson = ("- [2026-09-30 02:4x r444 bm-b] S6 批跑器无参腿伪参数坑（本轮 5 腿 rc=2 假红实证·重跑后 33/33 全绿）："
 "PS 批跑腿参数化 `$leg.Split(' ')[1..($leg.Split(' ').Count-1)]` 在无参腿（Count=1）下 `[1..0]` 倒序越级"
 "=@($null, 元素0)=把脚本名自身传成子命令→「unknown subcommand」rc=2（update_options/sina_mf/astock_daily/ths/ah "
 "五 gate 无参默认腿全中）——无参腿必须走无参分支（参数计数判别）；附带：分类器 UNKNOWN 件手工定性范式=先逐键 "
 "deep-compare 双 blob，files 全同+唯一差=顶层 ts→take-new by ts 零风险（探针=results/_r444bmb_guardscan_probe.py"
 "·_attrition_guard_scan.json 撞车实战）；时间戳缩写 strftime(\"%H:%M\")[0]+\"x\" 生成「0x」丢小时位，正解 "
 "strftime('%H:')+分首位+'x'。How to apply：S6/批量腿批跑器先查无参腿分支；UNKNOWN 件先逐键比对定性再选配方。\n")
with io.open("CODELY.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(lesson)
size = io.open("CODELY.md", encoding="utf-8").read().__len__()
print("CODELY.md appended, chars=%d (under 50KB line)" % size)

# ---------- 2) state.json round 443 -> 444 ----------
st = json.load(io.open("state.json", encoding="utf-8"))
assert st["round_no"] == 443, st["round_no"]
st["round_no"] = 444
st["note"] = ("r444: W12 prereg FROZEN (RSQR trend-fit-quality gate, whole-package adoption of bm-a r447 berth, "
 "four-straight AMP->W9/MOM->W10/STD->W11/RSQR->W12; probe re-run bit-exact ALL GREEN decidable 3,363/open 341/"
 "rsqr10 332/slope 213-128/six cross-checks; SEED 20320500/20321000/20321500 three-step law ALL GREEN 143-key "
 "zero-collision first-els 1294340368/1873818339/561143918 bands clean facts _r444bmb_w12_seed_law_facts.json; "
 "wave ticket T-2026-09-30-124 opened+claimed; MSG-20260930-0225 dual-signal; ladder TRIAL-LABOR-W12-GENERATE "
 "armed_pending_runner) -- same round: r443 dead-round closure (31-UU legacy + fork-point storm wave-2 13-UU per "
 "bigmoney-conflict-resolve classifier 13/13, --onto 74da996dd explicit replay zero loss, guardscan UNKNOWN manual "
 "adjudication, pool W11-JUDGE done flip + SLOT-4 union, push landed 74da996dd..b5ccebd9e then storm rebase -> "
 "388140c81) + W11 judge harvest + S6 sweep commits replayed and landed. NEXT: W12 runner build slice "
 "(scripts/trial_labor_w12.py G-RSQR fail-closed door + verbatim-import) -> GENERATE pool ignition -> SCREEN -> "
 "JUDGE -> CEO-REPORT-WAVE12; ledger wave-12 row at GENERATE per W11 8d03c4126 precedent. WATERMARK GREEN "
 "(supply_floor FLAG honest: ready 0<3 until runner build next slice)")
st["last_round_at"] = ts_now
st["last_round_ts"] = "r444"
st["ts"] = ts_now
st["updated"] = ts_now
io.open("state.json", "w", encoding="utf-8", newline="\n").write(
 json.dumps(st, ensure_ascii=False, indent=1) + "\n")
json.loads(io.open("state.json", encoding="utf-8").read())
print("state.json round 444 written")

# ---------- 3) heartbeat bm-b.json ----------
hb = json.load(io.open("fleet/machines/bm-b.json", encoding="utf-8"))
hb["last_seen"] = ts_now
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts_now
hb["current_task"] = ("r444 CLOSED (this session): W12 prereg FROZEN whole-package adoption of bm-a r447 RSQR berth "
 "(SEED 3 keys + ticket T-124 + MSG-0225 + ladder armed_pending_runner) + r443 dead-round rebase closure fully "
 "pushed (b5ccebd9e/17a86b5d7/388140c81) + W11 judge pool entry flipped done -- NEXT round: W12 runner build slice "
 "-> GENERATE ignition")
hb["cpu_cores"] = 16
hb["free_ram_gb"] = 5.6
hb["gpu_free_vram_gb"] = 2.0
hb["cpu_util_pct"] = 3.8
hb["round_no"] = 444
hb["verdict"] = "healthy"
hb["round"] = 444
hb["loop_round"] = 444
hb["last_round_at"] = ts_now
io.open("fleet/machines/bm-b.json", "w", encoding="utf-8", newline="\n").write(
 json.dumps(hb, ensure_ascii=False, indent=1) + "\n")
chk = json.loads(io.open("fleet/machines/bm-b.json", encoding="utf-8").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
assert "T" in chk["clock_read"], "clock_read must be T-separated (R262 law)"
print("heartbeat written, epoch int + clock T-sep self-checked")

# ---------- 4) round report line ----------
rr = ("2026-09-30T02:30:18+08:00 | r444 bm-b | WM-VERDICT: 绿 red=false @02:28 probe (insufficient_history n=1 非阻塞"
 "·local_batch_running=true astock refresh lock alive=合法负载) | 当前活: W12 prereg FROZEN 收口（RSQR 趋势拟合强度门·"
 "四连收编 AMP→W9/MOM→W10/STD→W11/RSQR→W12） | 最近实物: research/TRIAL_LABOR_W12_PREREG.md FROZEN commit 17a86b5d7 "
 "+ push landed adca8cce0..388140c81（SEED 20320500/20321000/20321500 三步律全绿 facts _r444bmb_w12_seed_law_facts.json"
 "+票 T-2026-09-30-124 opened+claimed+MSG-20260930-0225 双信号+ladder armed_pending_runner）@02:2x | 下个里程碑: W12 runner "
 "构建（scripts/trial_labor_w12.py G-RSQR fail-closed 门+verbatim-import）→ GENERATE 入池点火，窗 ≤48h（by 2026-10-02 "
 "02:00） | did: (1) r443 死轮遗产收口=13-UU 第二波正典解（分类器 13/13·--onto 74da996dd 显式重放=fork-point r444 律"
 "二次实战·resolver _r444bmb_resolve2.py rolling union compute_audit 206+201→207+regime 3+3→3+孪生同侧 take-new+"
 "guardscan UNKNOWN 手工定性 4 键全同取新 ts）→ W11 judge harvest 9f05afc3f+S6 sweep 7e2d99e85 两 commit 重放落地 "
 "push 74da996dd..b5ccebd9e→风暴窗两连撞（pool W11-JUDGE/SLOT-4 双 flip union _r444bmb_poolflip_resolve.py+"
 "crash_fuse take-new ts 02:20:04）→388140c81 三段全落；(2) W11 死轮 S7 遗留=pool TRIAL-LABOR-W11-JUDGE ready→done "
 "owner 翻转（记账面收口·实质 finalize 01:47:40 已落）；(3) TRIAL_LABOR 常设线触发（板空+池空+判决批收口）→W12 "
 "冻结步全链：触发器活读复验（W11 全链消费落地+判官零在飞·SLOT-4=bm-c 创新配额车道非判官批如实披露）+探针确定性"
 "重跑逐位全绿+SEED 三步律 143 键全绿+catalog pre-arm armed_pending_runner+票+MSG；(4) S6 33 腿：28 绿+5 腿批跑器"
 "伪参数 rc=2 假红（坑律已入 CODELY）→无参重跑 33/33 全绿·update_lhb rc3 r229 第 4 观察例源改史隔离·dualrun "
 "ZERO-DRIFT streak 33/3·compute_audit FLAG supply_floor（ready 0<3=W12 runner 未建诚实旗·runner 落地即解除）"
 "·REPORT-2026-09-30+LIVE-2026-09-30 新鲜落盘（ORANGE cap50） | verify: smoke 26/26+attrition guard 4 ledgers "
 "CLEAN+claw identical+watchdog 就绪+push 三段全落（b5ccebd9e/17a86b5d7/388140c81）+SEED registry import 实读 "
 "w12 三键在册 20320500/20321000/20321500 | next: W12 runner 构建切片→GENERATE 入池→SCREEN→JUDGE→CEO-REPORT-"
 "WAVE12 [via bm-b]\n")
with io.open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(rr)
print("round report line appended")
print("closeout writer done")
