# _r293bma_closure_wrap.py -- R293 closure wrap: report lines + state + heartbeat + CODELY kenglu
import json, time, ctypes, datetime, os

NOW = "2026-09-27 05:0x"
TS = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
EPOCH = int(time.time())
CLOCK = datetime.datetime.now().astimezone().isoformat(timespec="seconds")  # T-separated with offset

# ---------- 1) round report: R293 posthumous line + closure line ----------
R293_LINE = (
    "2026-09-27 04:33 | R293 bm-a (dept:research+strategy+fleet) | "
    "WM first-line verdict: GREEN-side (watermark red=false lane=healthy; "
    "py 0.1-0.4% low BUT pool fed same round + burned 353s = legal "
    "supply-line closure; compute_audit CLEAN flags=[] pool_ready 1->0 "
    "post-burn) | "
    "S0 pull clean + S0.5 orders double-scan 91/91 zero unacked + group "
    "decisions D-20260927-04 (re-audit hot-copy ban: own R290 anchor "
    "migration = executed-maintained receipt) + D-05-ii (orders.md "
    "full-file scan face: own loop already in-prompt = compliant "
    "zero-action) + S1 smoke 25/25 | "
    "S3 MAIN CLOSURE (T-87 s2 q3, full R99 chain one round): "
    "CN_KLINE_PATTERN_P1 runner built scripts/cn_kline_pattern_p1.py "
    "(selftest 23/23 hermetic planted-MS/TWS/DCC/TBC + negative control; "
    "REAL-DATA GATE PASS 36.4s: universe re-derive 3106 + skip ledger "
    "{1705/163/5/243} + boards {2000/758/346/2} + census "
    "MS1342/TWS21518/DCC35270/TBC14 ZERO DRIFT vs frozen probe cbf6c93c) "
    "-> pool entry #55 ready (workers_plan+shards per O-2130 multi-core "
    "law) -> autofill claim (fill latency 5.4min <= 10min O-2100 target) "
    "-> BURN pid 56364 elapsed 353s -> JUDGED 7/7 NEGATIVE-HONEST per "
    "prereg s5-p1 (x2 Sharpe MS-FIX -0.7145/MS-STOP -0.6385/TWS-FIX "
    "-0.3811/TWS-STOP -0.4363/MS-BEAR +0.1218/TWS-BEAR +0.4000/COMBO "
    "+0.2768; own-null skill lines 1.9486/2.6603/3.5701-4.0655 ALL "
    "line_ok=False; bootstrap CI<=0; DSR<=0.015; family PBO 0.4429>0.25; "
    "batch cells_ok 7/7 False ann>0-and-OOS>0-and-maxDD>=-35pct "
    "triple-fail, maxDD -97 to -100pct; D6 max|corr|<=0.1295 zero reject "
    "= mechanism-distinct from ew6 canon; TBC 14 events "
    "insufficient-sample flag honest; entries face healthy ~1.3k/21.2k/"
    "22.5k filled) -> ledger 200,396 = 198,389(bm-b r295 corrected head, "
    "live-read) + 2,007 single-count PASS -> gate_attrition own row "
    "entries-list face r248 -> prereg s7/s8 filled once-final "
    "(5-prediction reconciliation: p1 CONFIRMED claim!=verify; p3 "
    "half-hit BEAR modifier bigger than +-20pct band honest) -> pool "
    "flipped done + result_ref | "
    "PUSH-REJECTION REBASE WINDOW: 3-commit replay onto bm-b fc746e7c, "
    "UU x28 canonical resolve (classifier GREEN single-batch; "
    "autofill_state rebuilt from CLEAN sources origin/main+own-commit "
    "after fe251ac7 marker-poison incident -- first resolver crashed on "
    "junk assert BEFORE write-back -> git add staged markers -> committed "
    "mid-rebase; lesson E1 kenglu appended: write-first-assert-after + "
    "staged-marker git-grep gate before continue + poisoned-ours "
    "rebuild-from-clean-sources; snapshots take-newer-by-ts 14 files all "
    "mine-04:2x vs bmb-04:1x; x2_watch_log union 432+432->438; dashboard "
    "js take-side; tree-wide marker scan CLEAN; tip pushed "
    "fc746e7c..28fe1254) | "
    "E1 kenglu #2: pool entry needs workers_plan+shards or picker skips "
    "silently (log line only) -- registered in autofill log + this "
    "report; CODELY.md hot-cold rebin SAME WINDOW (10844B > 10KB hard "
    "line -> 12 dated entries moved verbatim zero-loss to "
    "research/memory-archive/202609.md, CODELY 2671B; scripts "
    "results/_r293bma_resolve.py + _r293bma_codely_rebin.py) | "
    "S6 chain 22 gates rc=0 (daily cutoff 09-24 no-op Sunday; LHB "
    "refetch 5209 rows 0-beyond-cutoff honest; mf/sina/ths/ah "
    "throttled-or-fresh no-ops; astock=bm-b lane + fundprem=bm-c lane "
    "honest guards; paper legs 2-bars-since-09-23 OK 6 traders; prospect "
    "22/22 pass drift 0; promotion 0/22 eligible honest; t35 PASS "
    "0-breach; regime ORANGE shadow asof 09-24; clock ORANGE_COOL "
    "activated 0; export 09-24) + token delta 0 + dashboard refreshed | "
    "NEXT: P0 candidate = post_review criteria registration for "
    "CN_KLINE_PATTERN_P1 (anchors on prereg s7/s8 + stable product keys "
    "per r291 no-hot-file law) + SCHOOL_SUPPLY_S1 next candidate per "
    "R99 cadence + carried O-2030/O-2100 anchor-migration evaluation + "
    "smoke F7 heartbeat epoch-int/clock-T self-check on write | "
    "POSTHUMOUS-APPEND (closure session 04:57): R293 session crashed ~04:33 "
    "after writing this line's generator (results/_r293bma_report.py) but "
    "before append/state/heartbeat/wrap; line appended verbatim by recovery "
    "session; wrap tasks completed under R293-closure line below"
)
CLOSURE_LINE = (
    "2026-09-27 04:57 | R293-closure bm-a (dept:research+strategy+fleet) | "
    "WM first-line verdict: py_low_board_clear LEGAL (board 0 open, bandit 0, "
    "pool 0 ready post-burn, no in-flight batch, audit v2.3 CLEAN flags=[] with "
    "idle-starvation candidate span-null honest; supply face = R99 prereg cadence = "
    "next-session line: post_review registration P0 + T-23 consumption prereg + "
    "SCHOOL_SUPPLY_S1 next candidate -- session-work not CPU-pool work, no fake-batch "
    "filler per O-1137) | "
    "RECOVERY ROUND: R293 crashed ~04:33 post-burn pre-wrap (liveness discriminator: "
    "schtasks IgnoreNew instance exited + zero live bigmoney codely.exe in Win32_Process "
    "face + state stuck 292 + freshest artifact 04:32:59 = dead-not-paused) -> sole-executor "
    "resumed: stranded tree (CODELY rebin + prereg s7/s8 + archive + gate_attrition +858 + "
    "pool done-flip + autofill state + burn products p1_results/cells/nulls/cells_summary "
    "+ 2 R293 scripts) folded as attributed salvage commit + rebase onto bm-b ec3dad4b "
    "(origin advanced 986a88a2->ec3dad4b IN-ROUND while working = bm-b r297 same-window) "
    "UU x3 canonical resolve per skill recipes: CODELY take-upstream superset reorg 2379B "
    "(<=10KB hard line; local 11-entry removals subset of remote 12) + archive union "
    "byte-dedup (bm-b 12-entry batch-2 section + R293 window header kept + R293-unique "
    "resolver-E1 entry kept + dedup note; zero-loss asserted BOTH sides incl r289 "
    "full-prefix asserts) + autofill_state mixed-dict+ledger (launches union 50 cap ASC "
    "r245 + last_tick same-second tie 04:40:01->HEAD/upstream per r140+r292 -- resolver "
    "first draft took own-side on >= and was self-caught + patched, tie-law held + "
    "LF/no-trailing-newline mirror; resolver=results/_r293bma_resolve2.py write-first-"
    "assert-after per R293-E1 law, staged marker-gate CLEAN) -> r291 semantic re-verify "
    "pre-push ON DISK: pool CN-KLINE status=done done_at 04:32:15 shard done + "
    "p1_results.json present + CODELY 2379B -> push rc=0 ec3dad4b..c986f8c5 | "
    "S0.5 double-scan 91/91 zero unacked (round-start + wrap) + group orders.md 47 "
    "@BigMoney/quant lines all receipted (L45 CODELY<=10KB=executed R287; zero new "
    "post-0302) + decisions.md zero new post D-20260927-05 | S1 smoke 25/25 | "
    "S6: R293 in-window full chain 22/22 rc=0 stands (28fe1254); closure re-ran "
    "machine faces only: compute_audit + watermark probe + token delta=274 (L2 legs 0 "
    "today, crash-fuse refusals 1/1 sigs honest); shared regen faces fresh from bm-b "
    "r296/r297 same-window runs not re-churned | crash_counted=true on CN-KLINE launch "
    "record = normal landed-settle per autofill.py L287 comment 'landed -> never a "
    "crash' (NOT phantom; selftest S16 covers) | CODELY +1 kenglu (crash-recovery "
    "liveness discriminator + salvage protocol) | "
    "NEXT (R294): P0 post_review criteria registration CN_KLINE_PATTERN_P1 (stable "
    "prereg-s7/s8 anchors per r291 no-hot-file law) + T-23 judged consumption prereg + "
    "SCHOOL_SUPPLY_S1 next candidate per R99 cadence + carried O-2030/O-2100 "
    "json_field anchor-migration evaluation"
)
with open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8") as f:
    f.write(R293_LINE + "\n" + CLOSURE_LINE + "\n")
print("report: 2 lines appended")

# ---------- 2) state-bm-a.json ----------
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st_last = dict(st)
st["round_no"] = 293
st["did"] = ("R293 (closure by recovery session): CN_KLINE_PATTERN_P1 full R99 chain "
             "judged 7/7 negative-honest (runner selftest 23/23 -> pool -> burn 353s -> "
             "prereg s7/s8 one-time finalization, slot closed no-reopen) + session crashed "
             "~04:33 pre-wrap -> salvage commit c986f8c5 + rebase UU x3 canonical resolve "
             "(CODELY take-upstream 2379B / archive union byte-dedup / autofill tie->HEAD) "
             "+ push rc=0 + S0.5 91/91 + smoke 25/25 + audit CLEAN + WM py_low_board_clear")
st["verdict"] = "ok"
st["next"] = ("R294: P0 post_review registration CN_KLINE_PATTERN_P1 (s7/s8 stable anchors) "
              "+ T-23 judged consumption prereg + SCHOOL_SUPPLY_S1 next candidate (R99) + "
              "O-2030/O-2100 json_field anchor-migration eval")
st["ts"] = TS
st["last_round_ts"] = st_last.get("ts", "2026-09-27 04:01:57")
st["updated_at"] = TS
st["current_task"] = st["did"][:120]
st["last_run"] = TS
st["last_round_at"] = st["last_round_ts"]
st["last_round"] = 292
st["updated"] = TS
st["last_seen"] = TS
st["task"] = st["next"]
json.dump(st, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("state: round_no=293 ts=", TS)

# ---------- 3) heartbeat fleet/machines/bm-a.json ----------
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
mem = MEMORYSTATUSEX()
mem.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
free_gb = round(mem.ullAvailPhys / (1024 ** 3), 1)
gpu_free_mb = 5683  # nvidia face via compute_audit: 12282 total - 6599 used
hp = "fleet/machines/bm-a.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = TS
hb["current_task"] = "R293 closure done: CN_KLINE judged-negative salvage+rebase+push; next=R294 post_review registration + T-23 prereg + school queue"
hb["cpu_cores"] = 32
hb["cpu_pct"] = 14.0
hb["free_ram_gb"] = free_gb
hb["free_ram_mb"] = int(mem.ullAvailPhys / (1024 ** 2))
hb["idle_ram_gb"] = free_gb
hb["gpu_free_vram_gb"] = round(gpu_free_mb / 1024, 1)
hb["gpu_free_vram_mb"] = gpu_free_mb
hb["gpu_idle_vram_gb"] = round(gpu_free_mb / 1024, 1)
hb["gpu_idle_vram_mb"] = gpu_free_mb
hb["gpu0_free_vram_gb"] = round(gpu_free_mb / 1024, 1)
hb["gpu"] = {"present": True, "idle_vram_free_gb": round(gpu_free_mb / 1024, 1),
             "note": "compute_audit face: 12282 MiB total - 6599 used = 5683 free"}
hb["verdict"] = ("R293-closure ok: CN_KLINE judged 7/7 negative salvage landed (c986f8c5); "
                 "WM py_low_board_clear LEGAL post-burn; supply=R99 prereg cadence next-session")
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = CLOCK
hb["round_no"] = 293
hb["task"] = hb["current_task"]
hb["cores"] = 32
json.dump(hb, open(hp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (F7)"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be T-separated ISO (F7)"
print("heartbeat: epoch=%d (int verified) clock=%s free_ram=%sGB" % (chk["heartbeat_epoch_utc"], chk["clock_read"], free_gb))

# ---------- 4) CODELY.md kenglu (one entry, E1) ----------
kp = "CODELY.md"
k = open(kp, encoding="utf-8").read()
entry = (
    "\n- [2026-09-27 04:5x] 坑律（bm-a R293-closure·轮会话崩溃恢复判别与打捞协议实弹·E1）：**轮会话可中途回合内崩溃（R293 ~04:33 post-burn pre-wrap：S6 链已 commit+push 而 state/心跳/轮报告未写）——「极新改动→退避」律需要活性判别子：新鲜脏树+活进程=真在飞让路，新鲜脏树+死进程树=崩溃打捞；判别法=schtasks 实例态（IgnoreNew 下我方获发=前实例必已退）+Win32_Process 全扫本仓 prompt 面（零活 codely.exe=死非暂停）+state round_no 停更。**正律=①确认死后即独占续作：搁浅工作以归属明示 salvage commit 收编（禁无限退避养脏、禁 add -A 盲吞），rebase 冲突按 skill 正典配方解②打捞必带 r291 实读断言（pool done-flip 等共享态盘面核验）③轮号处置=崩溃轮由恢复会话补闭（state round_no=崩溃轮号+轮报告 POSTHUMOUS-APPEND 双行制），禁跳号养出双号轮。指针=results/_r293bma_resolve2.py+closure 轮报告+salvage commit c986f8c5\n"
)
if "崩溃恢复判别与打捞协议" not in k:
    open(kp, "a", encoding="utf-8").write(entry)
sz = os.path.getsize(kp)
print("codely: +1 kenglu entry, bytes=%d (<=10240 hard line: %s)" % (sz, sz <= 10240))
