# r985 closeout: round report rows (r984-addendum + r985) + CODELY pit row + state.json + heartbeat.
# LAW (this round's own pit): NEVER open target with 'wb' before full content is computed.
# Pattern: build full bytes in memory -> write temp -> os.replace (atomic).
import json, io, os, time, datetime

NOW = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
NOW_SHORT = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")

def atomic_write(path, data):
    assert isinstance(data, bytes)
    tmp = path + ".r985tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)

def append_line(path, line_text):
    b = open(path, "rb").read()
    eol = b"\r\n" if b"\r\n" in b[-400:] else b"\n"
    if b and not b.endswith(eol):
        b += eol
    atomic_write(path, b + line_text.encode("utf-8") + eol)

# ---------- 1) round report rows ----------
rec = json.load(open("results/_r984bmb_push_receipt.json", encoding="utf-8"))
addendum = (
    "%s | r984-addendum | C-r984 收口回执消费：PUSHED_VERIFIED %s（own-face 树手术 r982 v2 血统·base=%s·faces=%d·"
    "ls-remote 双验·receipt=results/_r984bmb_push_receipt.json）| CODELY.md 让路面（origin bm-c r1031 append 领先·"
    "payload 排除防镜像revert）→r985 union 治愈（差集 1/1→0/0·19,434B）| astock per-files churn 保持本地候完工包 | "
    "本地未达 origin commit 数=0 | r985 消费本回执"
) % (NOW_SHORT, rec["commit"], rec["base"][:10], rec["face"])

r985_row = (
    "%s | r985 | WM: insufficient_history 合法（py_watermark probe n=1 窗·open 0/bandit 0/pool 0·local_batch=astock 续拉面·"
    "red=false 延续 r984 面）| 主线=CODELY union+HANDOVER 5x+孤儿锁治愈+astock 收敛推进："
    "①S0 孤儿 index.lock 治愈（r984 17:27:18 收口后遗留·Get-CimInstance 零 git.exe committer 实证→09:16 判例法清锁·"
    "pull --rebase 不可行=脏树让路面维持→D-19 probe 直读 origin 面替代）；"
    "②S0.5 D-19 双 sha 零增量（decisions ab3f0cc9 / orders 63a39ce0 双恒等水位·r984 17:26 消费后零新令零新 MSG·"
    "results/_r686bmb_d19_check.json）+origin 新进 bm-a r1019 双发（W247 prereg 落地+死窗遗产吸收·其 ORD delta 全 MV 域零 bm-b 腿）；"
    "③S1 smoke 49/49；④astock refresh 收敛推进：worker 8380 17:19 死（334min 马拉松·fetched 5224/5229·9 fail·checkpoint 保全）→"
    "gate 17:38 续拉点火（todo=20/5229）→17:39 段退出（301569 复拉治愈 appended=1·per_files 5220→5221·8 只二连败候 3 败隔离律·"
    "4 只未触·conn_stopped=false·30min 节流窗设计面）→18:08 gate 窗后下轮自燃续拉·完工包候 complete=true 窗（~19:00 估·≤48h）；"
    "⑤CODELY.md union merge：bm-c r1031 stash-bridge 判例行吸收+本地 r983 行保全（origin 18,569B/本地 18,443B 差集 1/1→union 后 0/0·19,434B·"
    "防镜像回退闭环）；⑥HANDOVER 5x（r981-r985 窗）条目落册（pre-write origin 面字节恒等验证 1,098,061B 0/0 差集）"
    "+**wb-open 截断坑事故治愈（本轮主坑）**：首跑 io.open('wb') 先截断目标后 write 参数求值抛 AttributeError→HANDOVER 0B·"
    "二跑读残面追加=2,139B 假象→原子恢复（origin 面+条目=1,100,199B 零丢失·temp 全量保全+os.replace·坑律入册 CODELY）；"
    "⑦S8 --worked 声明 idle_rounds=0·agenda_starved=false（本地池 W001-W006 全闭·AGENDA-STARVED-FLAG 在旗候秘书处补货·"
    "禁造无意义活 per O-2026928-1820）；⑧S7 四件套绿（loop pin=2 no-op 首火 17:52/watchdog running 17:47/双爪 byte-identical）"
    "+sat engine rc0 queue idle 实测；⑨S6 面=r984 17:06-17:10 全链 40 标记绿（同数据窗 25min·NEWBAR 门关 cutoff 10-14 sina 迟 bar 面）"
    "+本轮增量腿 token 0/watermark probe/astock gate 续拉点火；⑩孤儿面=0（round-zero 探针 14 py faces）"
    "| 实况三行：当前活=astock refresh 收敛段（8 只隔离判定+4 只续拉·18:08 gate 窗）；最近实物=CODELY.md union 治愈面（19,434B）+"
    "HANDOVER 5x r981-r985 条目（1,100,199B·含截断坑零丢失恢复）+孤儿 index.lock 治愈；下个里程碑=astock 完工包推送（complete=true 后·~19:00 窗·≤48h）"
    "| 记账预算: 5/5（state+report+心跳+receipt+HANDOVER 5x due 件）| 产品积分: 1（CODELY union+HANDOVER 5x=文件改动面·astock 完工包未落地如实）"
    "| 验证证据：smoke 49/49 终端面+results/_r686bmb_d19_check.json（双恒等）+results/astock_daily_update_status.json（17:39:18 面）+"
    "CODELY 双面差集命令面回执+HANDOVER 1,100,199B 恢复断言+idle_trigger declared=worked+sat engine rc0+S7 四件套命令面回执+"
    "results/_orphan_face_probe.bm-b.json（14 faces 0 orphans）| 本地未达 origin commit 数=0（推送后 ls-remote 自证·见 push 回执）"
    "| 下轮指针：r986=①astock 完工判定（18:08 gate 窗·complete=true→数据 churn 完工包推送=首要·8 只隔离面如实披露）"
    "②D-19 双 sha 复探③CODELY 坑律域件回扫（r747 范式·记账预算内分批）④S7/S8⑤r985 addendum 行随 r986 面"
) % NOW_SHORT

append_line("logs/iteration-loop/round_reports.md", addendum)
append_line("logs/iteration-loop/round_reports.md", r985_row)
print("round report rows appended")

# ---------- 2) CODELY.md pit row ----------
pit_row = (
    "[2026-10-15 17:4x r985 bm-b] python 落盘截断坑·wb-open 先截断族（HANDOVER 1,098,061B 实弹）："
    "io.open(path,'wb') 的 open() 调用本身即截断目标——其后 write(b+expr) 的 expr 求值抛异常"
    "（本案=eol.encode() 对 bytes 再 encode）=目标留 0B 截断态；二跑读残 b'' 追加=仅剩新条目 2,139B 假象。"
    "法：读改写大件一律内存拼全量→写 temp→os.replace 原子换（恢复面=origin 字节恒等 pre-write 验证+temp 保全·"
    "1,100,199B 零丢失）；write 参数先算后开柄。姊妹面=pit-ps 重定向覆写族。"
)
append_line("CODELY.md", pit_row)
print("CODELY pit row appended")

# ---------- 3) state.json ----------
s = json.load(open("state.json", encoding="utf-8"))
did = (
    "r985: (a) 孤儿 index.lock 治愈（r984 17:27:18 收口后遗留·Get-CimInstance 零 git.exe committer 实证→09:16 判例法清锁）；"
    "(b) D-19 双 sha 探针零增量（decisions ab3f0cc9 / orders 63a39ce0 双恒等水位·r984 17:26 消费后零新令；"
    "origin 新进 bm-a r1019 双发=W247 prereg 落地+死窗遗产吸收·ORD delta 全 MV 域零 bm-b 腿）；(c) smoke 49/49；"
    "(d) astock refresh 收敛推进：worker 8380 17:19 死（334min·fetched 5224/5229·9 fail·checkpoint 保全）→gate 17:38 续拉点火"
    "（todo=20）→17:39 段退出（301569 复拉治愈·per_files 5220→5221·8 只二连败候 3 败隔离律·4 只未触）→18:08 gate 窗后下轮自燃续拉；"
    "(e) CODELY.md union merge（bm-c r1031 行吸收+本地 r983 行保全·差集 1/1→0/0·19,434B）；"
    "(f) HANDOVER 5x（r981-r985 窗）落册+wb-open 截断坑事故治愈（首跑 open('wb') 先截断后 write 参数抛 AttributeError→0B·"
    "二跑残面追加假象→原子恢复 1,100,199B 零丢失·坑律入册 CODELY）；(g) S8 --worked 声明 idle_rounds=0"
    "（本地池全闭·AGENDA-STARVED-FLAG 在旗候补货）；(h) S7 四件套绿+sat engine rc0 实测；"
    "(i) S6 面=r984 17:06-17:10 全链绿（同数据窗）+本轮增量腿 token 0/watermark probe insufficient_history 合法；(j) 孤儿面=0"
)
s["round_no"] = 985
s["round"] = 985
s["round_no_label"] = "r985"
s["clock_read"] = NOW
s["current_task"] = "r986: astock completion package watch (18:08 gate window) + closeout"
s["task"] = s["current_task"]
s["current"] = "r985: CODELY union + HANDOVER 5x + orphan-lock heal + astock convergence"
s["did"] = did
s["last_action"] = "r985: CODELY union merge + HANDOVER 5x (r981-r985) + orphan index.lock heal + astock refresh convergence + D-19 zero-delta + smoke 49/49"
s["last_action_at"] = NOW
s["last_round_at"] = NOW
s["last_round_ts"] = NOW
s["last_seen"] = NOW
s["ts"] = NOW
s["updated"] = NOW
s["updated_at"] = NOW
s["next"] = (
    "r986: 1) astock 完工判定（18:08 gate 窗自燃续拉·complete=true→数据 churn 完工包推送=首要·8 只隔离面如实披露）"
    " 2) D-19 双 sha 复探 3) CODELY 坑律域件回扫（r747 范式·记账预算内分批）"
    " 4) S7/S8 5) r985 addendum 行随 r986 面"
)
s["next_milestone"] = "astock data churn completion package tonight (complete=true window ~19:00, <=48h); pit-domain re-scan batched within budget"
s["now_active"] = (
    "r985: live faces = astock refresh convergence (8 isolation-pending + 4 retry stocks, next gate window 18:08); "
    "local pool EMPTY (W001-W006 all closed) awaiting secretariat restock; GPU keepwarm standing (qwen3.8:4b pinned); i2v line CLOSED 53/53"
)
s["verdict"] = (
    "GREEN-closeout: CODELY union healed (1/1->0/0) + HANDOVER 5x landed with zero-loss truncation recovery + "
    "orphan index.lock healed (zero-committer proof) + D-19 zero-delta + smoke 49/49 + astock convergence honest defer "
    "(package awaits complete=true, 18:08 gate window)"
)
s["orphan_face"] = 0
s["orphan_faces"] = 0
s["orphan_face_note"] = "r985 round-zero probe (17:2x): 14 py faces, 0 orphans"
s["last_orders_probe_at"] = NOW
s["last_decisions_probe_at"] = NOW
s["d19_probe_due"] = False
s["d19_probe_due_note"] = "r985 round-start probe consumed (dec ab3f0cc9 / ord 63a39ce0 both unchanged); next probe = r986 cadence"
s["orders_delta_pending"] = False
s["decisions_delta_pending"] = False
s["last_orders_at"] = NOW
s["last_orders_read_at"] = NOW
s["sat_engine"] = {
    "status": "alive (live-probed rc=0 this round: status exit 0, queue 0, verdict idle)",
    "checked_at": NOW,
}
atomic_write("state.json", json.dumps(s, ensure_ascii=False, indent=1).encode("utf-8") + b"\n")
print("state.json updated (round 985)")

# ---------- 4) heartbeat ----------
h = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
h["last_seen"] = NOW
h["task"] = "r985: CODELY union + HANDOVER 5x + orphan-lock heal + astock convergence watch"
h["did"] = (
    "r985: (a) orphan index.lock healed (r984 leftover, zero-committer proven, 09:16 law); (b) D-19 dual-sha zero-delta "
    "(dec ab3f0cc9 / ord 63a39ce0 both match watermarks; origin new = bm-a r1019 x2, ORD delta all MV-domain zero bm-b leg); "
    "(c) smoke 49/49; (d) astock convergence: worker 8380 died 17:19 (334min marathon, 9 fails, checkpoint preserved) -> "
    "gate resumed 17:38 (todo=20) -> segment exit 17:39 (301569 healed, per_files 5220->5221, 8 stocks at 2-fail pending "
    "3-fail isolation, 4 untouched, 30min throttle design) -> next gate window 18:08, package awaits complete=true; "
    "(e) CODELY.md union merge (bm-c r1031 row absorbed + local r983 row preserved, 1/1->0/0, 19,434B); "
    "(f) HANDOVER 5x (r981-r985) landed + wb-open truncation pit incident healed (open('wb') truncates before write-arg "
    "eval; AttributeError left 0B; second pass on residue = 2,139B illusion; atomic restore 1,100,199B zero-loss, pit "
    "row into CODELY.md); (g) S8 --worked declared idle_rounds=0 (local pool empty, AGENDA-STARVED-FLAG standing, restock watch); "
    "(h) S7 quad green (loop pin=2 no-op first fire 17:52 / watchdog running 17:47 / claws byte-identical) + sat engine rc0; "
    "(i) S6 face = r984 full chain green (same data window) + this round legs token 0 / watermark probe insufficient_history legal"
)
h["cpu_cores"] = 16
h["free_ram_gb"] = 10.1
h["gpu_free_vram_mb"] = 3950
h["verdict"] = s["verdict"]
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["heartbeat_epoch_utc"] = EPOCH
h["clock_read"] = NOW
h["ts"] = NOW
h["orders_ack"] = (
    "r985: D-19 dual-sha zero-delta probe (dec ab3f0cc9 / ord 63a39ce0 both == watermarks, no new orders/decisions since "
    "r984 17:26 consumption) + own orders O-20261015-0025/0906/0915/0952 + own MSGs standing on origin | r984: (see prior ack)"
)
h["note"] = (
    "r985: CODELY union healed + HANDOVER 5x landed (truncation pit zero-loss recovery) + orphan index.lock healed; "
    "astock completion package awaits complete=true (18:08 gate window, next round first priority); "
    "AGENDA-STARVED flag standing (local pool empty, awaiting secretariat restock); orphan face=0"
)
atomic_write("fleet/machines/bm-b.json", json.dumps(h, ensure_ascii=False, indent=1).encode("utf-8") + b"\n")
print("heartbeat updated (epoch int=%d, verified type %s)" % (EPOCH, isinstance(EPOCH, int)))
chk = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
chk2 = json.load(open("state.json", encoding="utf-8"))
assert chk2["round_no"] == 985
print("self-verify PASS: epoch int + round 985")
