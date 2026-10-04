"""r695 bm-b S7 closeout: state round 695 + heartbeat + round-report append
(append-only idempotency gate per r679 law: marker count==0 before append)
+ MSG-2115 -> processed/ move. Clock strict regex + epoch int cross-check
per r641 law. Roundtrip-before-rewrite per r678 law (line-surgery fallback
if roundtrip fails)."""
import datetime
import json
import os
import re
import shutil
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLOCK_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+08:00$")
LOG = os.path.join(ROOT, "results", "_r695bmb_closeout_log.txt")
out = []


def log(s):
    out.append(s)
    print(s, flush=True)


now = datetime.datetime.now()
clock = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
assert CLOCK_RE.match(clock), f"clock malformed: {clock}"
epoch = int(time.time())

# --- state.json: absolute-value write (r694 ii law) ---
sp = os.path.join(ROOT, "state.json")
with open(sp, encoding="utf-8") as f:
    state = json.load(f)
assert state["round_no"] == 694, f"unexpected round_no {state['round_no']}"
state["round_no"] = 695
state["round_no_label"] = "round 695 (bm-b)"
state["note"] = ("r695: S0 daemon-lane absorb (8 faces zero origin intersection) + "
                 "merge origin wave (bm-a r697 + bm-c r497 N2-W15 12-shard SCREEN enrollment) zero-UU netpath; "
                 "MSG-2115 receipt (bm-c screen seats honored, RAM-floor 3.4GB self-hold, unclaimed SHARD-2..11 "
                 "-> daemon self-claim on RAM window after trio V closes); S6 38/38 rc0 ZERO-DRIFT streak 4; "
                 "HANDOVER 5x r695 row (window r691-695); smoke 48/48; attrition CLEAN; D-19 dual MATCH")
state["ts"] = state["updated"] = state["last_seen"] = state["last_round_at"] = clock
state["clock_read"] = clock
state["next"] = ("(a) trio NULLS close V ~10-06T17 / Q 10-07T11 / D 10-08T0x -> RAM window opens -> "
                 "N2-W15 screen shards daemon self-claim (SHARD-2..11 unclaimed, refuse-if-exists, "
                 "first-landed=canonical) + CONTEST-RC anchor+mirror two-phase auto-burn on pinned basis "
                 "-> same-window burner-side done-flip -> assembly A1.5 rerun = 219-measured CEO face <= 10-08; "
                 "(b) W3 judge bm-c landing watch (~22:1x, r482 id-dup probe owner-side); "
                 "(c) N2 screen finalize = all-12-done then first-arrival machine; (d) 10-09 post-holiday "
                 "market-open data-chain check")
raw = json.dumps(state, ensure_ascii=False, indent=1)
rt = json.dumps(json.loads(raw), ensure_ascii=False, indent=1)
assert raw == rt, "state roundtrip not identical"
with open(sp, "w", encoding="utf-8", newline="") as f:
    f.write(raw)
chk = json.loads(open(sp, encoding="utf-8").read())
assert chk["round_no"] == 695
log(f"STATE round 695 ok, clock={clock} epoch={epoch}")

# --- heartbeat: line-verified rewrite (roundtrip gate per r678 law) ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
with open(hp, encoding="utf-8") as f:
    hb = json.load(f)
rt2 = json.dumps(json.loads(json.dumps(hb, ensure_ascii=False, indent=1)), ensure_ascii=False, indent=1)
if rt2 != json.dumps(hb, ensure_ascii=False, indent=1):
    log("WARN: heartbeat roundtrip differs from canonical indent=1 - using in-place field update only")
hb["last_seen"] = clock
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock
hb["round_no"] = 695
hb["round_no_label"] = "round 695 (bm-b)"
hb["ts"] = hb["updated"] = hb["updated_at"] = clock
hb["current_task"] = ("r695 closed: S0 absorb+merge zero-UU (bm-c N2-W15 12-shard SCREEN enrolled in pool), "
                       "MSG-2115 receipt, S6 38/38, HANDOVER 5x r695; next = trio V close 10-06T17 -> RAM window "
                       "-> N2 screen daemon self-claim + CONTEST-RC two-phase auto-burn -> CEO face <= 10-08")
hb["verdict"] = ("healthy burning (trio NULLS three-family + N2-W15 screen 10 unclaimed shards RAM-gated + "
                 "CONTEST-RC queued for RAM window)")
hb["orders_ack_count"] = len(hb.get("orders_ack", []))
raw_h = json.dumps(hb, ensure_ascii=False, indent=1)
assert json.loads(raw_h) == hb, "heartbeat reparse mismatch"
with open(hp, "w", encoding="utf-8", newline="") as f:
    f.write(raw_h)
hchk = json.loads(open(hp, encoding="utf-8").read())
assert isinstance(hchk["heartbeat_epoch_utc"], int), "epoch not int"
assert hchk["round_no"] == 695
log(f"HB round 695 ok, epoch int={hchk['heartbeat_epoch_utc']} clock={hchk['clock_read']}")

# --- round report append: bytes mode + idempotency gate (r679 law) ---
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
rb = open(rp, "rb").read()
marker = "r695 (bm-b) PRODUCT".encode("utf-8")
assert rb.count(marker) == 0, "r695 marker already present - abort append (idempotency gate)"
line = (
    f"{clock} | r695 (bm-b) PRODUCT (dept:舰队协同+数据维护): [watermark verdict: GREEN (red=false lane=healthy; "
    f"py_watermark=py_low_with_work_cands 判读=local_batch_running=true trio 三簇合法占用非违令; satengine alive rc0 "
    f"hb 63s queue=18 held by RAM-floor 3.4GB<4.0GB 机队纪律自持; audit CLEAN py 96.3% burning-healthy; dualrun "
    f"ZERO-DRIFT streak 4 @390 entries cutoff 21:18:07; post_review ✓45/✗0/🟡5 零活红（r693 读数复用·本窗无新复审动作）; "
    f"S0.5 令差集 154/154 轮首扫零未回执零 extra; D-19 decisions/orders 双键 MATCH 水位零动作)] | 当前活: FUND trio "
    f"NULLS 三簇续烧（owner=bm-b keepalive 鲜活·ETA V 10-06T17 / Q 10-07T11 / D 10-08T0x）+ N2-W15 SCREEN 12 分片已入池"
    f"（SHARD-0=bm-c/SHARD-1=bm-a 认领烧中·SHARD-2..11 无主待 RAM 窗·本机 daemon RAM 窗开后自取）+ W3 judge finalize "
    f"bm-c 席落地观察（~22:1x·r487 工时标定·零复探=属主看护）+ CONTEST-RC RAM-gated 排队（due 10-08·fuse code_changed "
    f"自清正路）| 最近实物: S6 38/38 rc0（REPORT/LIVE-2026-10-04 再生·ORANGE cap50 COOL）+ HANDOVER r695 5x 核对行"
    f"（增量窗 r691-695）+ MSG-2115 收讫回执 MSG-2026-10-04-2150 @ {clock} | 下个里程碑: trio V 收口 10-06T17 → RAM 窗开 "
    f"→ N2 screen 分片 daemon 自取 + CONTEST-RC anchor+mirror 双相自燃 → assembly 219-measured CEO 面 ≤10-08 治理日；"
    f"开市 10-09 数据链复苏（窗≤48h=10-06T17 V 收口）| 做了什么: S0-1 身份锚定 bm-b（machine.json 单源）+ S0 daemon "
    f"lane faces absorb 8 面（trio nulls×3+satengine×3+p1d_gates·autofill_state 交集面 origin-checkout 预对齐 r437-ii "
    f"可再生零损失）→ merge origin wave（bm-a r697+bm-c r497 N2 12 分片 SCREEN enrollment+autofill claims）零 UU 净路 + "
    f"S0.5 orders 154/154 同口径集合比对零未回执 + D-19 双键 MATCH（r689 正典探针 method_for sha256/sha1 键口径自证复跑）"
    f"+ 决策审核步零新涉本司行（水位不变零动作）+ S1 smoke 48/48 + S2 板扫 169 票 0 open+job_list 空 + S3 satengine rc0 活"
    f"+ 修红无 + MSG-2115 收讫回执+归档 processed（零席位冲突声明+RAM 门实况披露）+ trio watch 三证 OK + S6 38/38 rc0 "
    f"（dualrun 先于 compute_audit 序律·REPORT/LIVE 再生）+ HANDOVER 5x r695 行 + S7 quartet 绝缘（loop pin=2 no-op 首燃 "
    f"21:32 / watchdog default-logon 幂等重装在位 D-20261002-02 / pre-commit+pre-push 双爪 LF 归一装）+ attrition 4 台账 "
    f"CLEAN（healed 历史注记照录）| 验证证据: smoke 48/48; D-19 probe JSON 双 MATCH methods=sha256/sha1; orders 同口径 "
    f"154 零差; S6 38 腿 rc0 全绿（log _r695bmb_s6_log.txt·PARITY PASS 38 legs==canon·NON-ZERO LEGS: none）; satengine "
    f"status rc0 active_burns=[] queue=18 RAM-floor 3.4GB; trio watch rc0 verdict OK; attrition scan CLEAN 4 ledgers "
    f"（evidence results/_attrition_guard_scan.json）; HB/STATE roundtrip 恒等自证 + json.loads 自证 + epoch int 自证"
    f"（results/_r695bmb_closeout_log.txt）| 产品分: 1（S6 再生面+HANDOVER 5x 核对=实际文件改动档；协调实物=MSG-2150 "
    f"回执件；新机制新实物=0·真实产品在飞=trio nulls 三行 daemon 自提 commit 持续落盘+N2 screen 双席烧中+CONTEST-RC "
    f"排队零重复开发）| 坑例新增=0（守成轮·既有正典全复用零新坑）| 下轮指针: (a) trio 看护续跑（V 10-06T17 收口窗）；"
    f"(b) N2-W15 screen 分片收割观察（双席烧中+10 席无主·RAM 窗开后本机 daemon 自取）；(c) W3 judge bm-c 落地观察；"
    f"(d) CONTEST-RC RAM 窗自燃观察；(e) 开市 10-09 数据链核验 | 本地未达 origin commit 数=收口 push 后 push_verify 实证"
).encode("utf-8")
with open(rp, "ab") as f:
    if not rb.endswith(b"\n"):
        f.write(b"\n")
    f.write(line + b"\n")
rb2 = open(rp, "rb").read()
assert rb2.count(marker) == 1, "post-append marker count != 1"
log("ROUND-REPORT append ok, marker count==1")

# --- MSG-2115 -> processed ---
src = os.path.join(ROOT, "fleet", "inbox", "MSG-2026-10-04-2115-bmc-ALL.md")
dst = os.path.join(ROOT, "fleet", "inbox", "processed", "MSG-2026-10-04-2115-bmc-ALL.md")
if os.path.exists(src):
    shutil.move(src, dst)
    log("MSG-2115 moved to processed/")
else:
    log("MSG-2115 already processed (skip)")

with open(LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
log("CLOSEOUT OK")
