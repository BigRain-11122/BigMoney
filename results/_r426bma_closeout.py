# r426 bm-a closeout: round report line + state bump + heartbeat (S5 + S7 bookkeeping)
import json, time, datetime
import psutil

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())
assert "T" in now_iso and " " not in now_iso

RR_LINE = (
    "2026-09-29 " + now_iso.split("T")[1] + "+08:00 | r426 bm-a (dept:工程·舰队 joint + 策略侧供给维护) | "
    "WM-VERDICT: green-legal-idle (red=false lane healthy @11:46 probe; py 0.5-3% low 无违令面=板 0 open+bandit next_pick claimed+池 ready 1 W7-JUDGE 在飞+W8 双泊位=常设线合法闲置·audit FLAG supply_gap/supply_floor standing answered by W7 chain in-flight) | "
    "did: S0-1 anchor bm-a; S0 STORM-6 队列构成诊断律首例（坑律一百零二批当窗立法）：pull --rebase 撞「Rebasing (1/1)」唯一件=陈旧 r425 原始件 f9890dfde（message 自述 da44b8b11 LANDED·merge-base --is-ancestor 验真在 origin/main）而未推 r426 merge 2f7b3e1a 会被线性 rebase 静默丢→0 件已解 abort 合法（r220 律只护已解工）→r419 单次 merge-back 6 UU 正典解（classify 6/6 全分类：5 ALL_FACES merge_lane_views resolve+1 append-log multiset union results/_r427bma_jsonl_union.py 审计留痕·base 3180+6+12=3198 行多重集验证）→54b2b5639 推拒→pit-93 两步第二次单 merge（bm-c r214 addendum 零 UU 自动合）→8198fe284 LANDED；同窗 reconcile 14 面 13 ZERO-DRIFT+1 autofill RETIRED-SHARED 合法态；注：54b2b5639 消息内「r427 S0」为笔误·实为本 r426 复活窗（前驱 11:20 限杀件 2f7b3e1a 由本会话收口落地）；"
    "S0.5 orders 122/122 双扫零差集+decisions 三新行：D-20260929-01 回执销账行零动作·D-20260929-02 BigMoney 切片认领 fetch-晋升律=已于今晨 r406 落地（F-20260929-01 closed·48h 窗提前；本窗在树验证 Tools/inbox_guard.py selftest 9/9 PASS+autofill submit/pool_worker 接线=git 可验）·D-20260929-03 BigDomain 非本仓零动作·C-20260929-01 token-economy attribution 接线窗 10-07 记指针；"
    "S1 smoke 26/26；S2 双板空（job 0/tasks 0 open/post_review 0 ✗）+pit-96 泊位核查 origin 零 W9 声明；S3 常设线合法闲置（W7-JUDGE ready 在飞·W8 TSTATE/AMP 双泊位 gate=W7 全链）；"
    "S4 坑律一百零二批入热层+水位当窗整编（10,168B 超 10,000B 线→一百批/百零一批 r211 两热条+八指针行 r173 范式合并 verbatim 迁 archive 202609.md『r426 bm-a 窗批』节·热层 6,456B 回线·10/10 行级零丢失）；"
    "S6 37 legs ALL rc=0（dualrun ZERO-DRIFT streak 6/3 cutoff 11:46；regime ORANGE d2 shadow；clock ORANGE_COOL sleeves4 act0；t35 09-28 PASS zero-pending；t24a 22/22 drift0+t24b 0/22 NOT-ELIGIBLE 诚实；moneyflow rank pass+ah refresh 分离 spawn；车道守卫诚实 no-op 族；export equity 5,988,732；daily_report faces=5；ceo_live ORANGE cap50 COOL；build_status 宿主执笔；token L2 0 today） | "
    "verify: origin/main=8198fe284 双 merge 落地（54b2b5639+8198fe284）；smoke 26/26；reconcile 13/14+RETIRED；热层 6,456B 零丢失；inbox_guard 9/9；S6 rc 全 0；S7 三件套绿（phase pin8 no-op+watchdog Ready+claw installed） | "
    "next: W7-JUDGE burn watch（autofill 面）→W8 窗（TSTATE bm-a+AMP bm-b·seeds 三步律重取）；48h CEO 钟 W6 judge 2026-10-01 08:14（bm-b）；10-01 月首轮三件套（science_audit+monthly_briefing+self_review）+REGIME_GUARD v3 日期门自动激活；MSG-1142 留 bm-b 消费窗（11:50:05+ retake）"
)

# --- round report append (CRLF) ---
rr = "logs/iteration-loop/round_reports-bm-a.md"
b = open(rr, "rb").read()
assert b.endswith(b"\r\n")
open(rr, "ab").write(RR_LINE.encode("utf-8") + b"\r\n")
print("round report: +1 line (r426)")

# --- state bump ---
sp = "state-bm-a.json"
s = json.load(open(sp, encoding="utf-8"))
assert s["round_no"] == 425, f"unexpected state round_no {s['round_no']}"
s["round_no"] = 426
s["did"] = ("r426: dead-predecessor merge-back revival conclude + S0 storm-6 queue-diagnosis first-fire (stale r425 replay aborted at 0-resolved, "
            "single merge-back 6-UU canon-resolved, two-step second merge, 8198fe284 LANDED; reconcile 13/14+RETIRED) + "
            "D-20260929-02 receipt verified in-tree (inbox_guard 9/9) + pit batch-102 + waterline 6,456B + S6 37 legs rc=0")
s["verify"] = "smoke 26/26; dualrun streak 6/3; regime ORANGE shadow; t35 PASS; t24 22/22 drift 0; export 5,988,732; token L2 0"
open(sp, "wb").write((json.dumps(s, ensure_ascii=False, indent=1) + "\r\n").encode("utf-8"))
print("state: 425 -> 426")

# --- heartbeat ---
hp = "fleet/machines/bm-a.json"
h = json.load(open(hp, encoding="utf-8"))
cpu = psutil.cpu_percent(interval=0.5)
vm = psutil.virtual_memory()
h["machine_id"] = "bm-a"
h["last_seen"] = now_iso
h["clock_read"] = now_iso
h["heartbeat_epoch_utc"] = epoch
h["round_no"] = 426
h["current_task"] = ("r426 closed: storm-6 merge-back landed 8198fe284 (queue-diagnosis law first-fire, 6-UU canon resolve); "
                     "D-20260929-02 receipt in-tree verified; standing-line legal-idle (W7-JUDGE in flight, W8 double-berth); next=W7 burn watch + 10-01 month-first triple")
h["cpu_cores"] = psutil.cpu_count(logical=True)
h["cpu_pct"] = cpu
h["cpu_util_pct"] = cpu
h["free_ram_gb"] = round(vm.available / 1024**3, 1)
h["idle_ram_gb"] = round(vm.available / 1024**3, 1)
h["cores"] = psutil.cpu_count(logical=True)
h["verdict"] = ("r426 green: smoke 26/26; storm-6 concluded (stale-replay abort + single-merge two-step landed, reconcile 13/14+RETIRED lawful); "
                "D-20260929-02 fetch-promotion law = already in-tree (inbox_guard selftest 9/9 this window); pit batch-102 legislated; "
                "hot CODELY 6,456B under line zero-loss; S6 37 legs rc=0; S7 trio green pin=8; state 426")
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

v = json.loads(open(hp, encoding="utf-8").read())
assert isinstance(v["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in v["clock_read"] and " " not in v["clock_read"], "clock_read must be T-separated"
print("heartbeat OK: epoch(int)=", v["heartbeat_epoch_utc"], "| clock=", v["clock_read"], "| round=", v["round_no"], "| cpu=", cpu)
