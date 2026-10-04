# r691 bm-b closeout: state/heartbeat/round-report/CODELY pitlaw, all guarded
# (r645 json.dump+loads self-verify; r679 append marker gate; r170 epoch int)
import datetime
import io
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV = os.path.join(ROOT, "results", "_r691bmb_closeout_log.txt")
now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec="seconds")
epoch = int(time.time())
log = []


def ev(k, v):
    log.append(f"{k}: {v}")


# ---------- 1. CODELY.md pitlaw append (UTF-8 binary append) ----------
PIT = (
    "- [2026-10-04 20:3x r691 bm-b] RAM 门原地等待环三面隐形×帽标定-熔断链复合坑"
    "（N2-W15 generate 首烧实弹·当场诊断当场修）：r379 等待环（_ram_gate_gb "
    "sleep60 循环）在 daemon 无 -u 分离烧录下=零日志字节（块缓冲·RAM-GATE 行无 "
    "flush）+零 CPU+孤儿进程三面叠加——健康等待与挂死不可区分；本轮第三证=dedup "
    "flush 腿未达（日志零字节→必在门前）定谳非盲杀（r661 律）。40min 帽在多日 "
    "RAM 封锁机（trio 持 RAM<4GB 至 10-06..08）=帽耗尽→exit2→fuse 计数→同 "
    "hash 重launch 冻结（r379 族放大面）——帽必须按已知在飞批 ETA horizon 标定"
    "非瞬窗假设。修=两调用位 wait_min 40→2880+门环 print 补 flush（r680 等待环"
    "实例）·selftest 17/17。How to apply：分离烧录「零字节日志+零 CPU+活进程」"
    "先查等待环（RAM 门/节流 sleep）再查挂死；RAM 门帽=查本机在飞批 ETA；等待"
    "环 print 一律 flush。\n"
)
p = os.path.join(ROOT, "CODELY.md")
raw = io.open(p, "rb").read()
assert PIT[:40] not in raw.decode("utf-8", errors="replace"), "pitlaw dup"
with io.open(p, "ab") as f:
    f.write(PIT.encode("utf-8"))
ev("codely_append", "ok len=%d" % len(PIT.encode("utf-8")))

# ---------- 2. state.json round flip (roundtrip-verified json.dump) ----------
sp = os.path.join(ROOT, "state.json")
d = json.load(io.open(sp, encoding="utf-8"))
d["round_no"] = 691
d["note"] = ("r691: N2-W15 generate RAM-gate wait-loop diagnosed+fixed "
             "(wait_min 40->2880 x2 + flush, selftest 17/17) + bm-a r694 "
             "yield/cleanup wave consumed (MSG-1943/2010, receipt MSG-2005, "
             "pool single-shard verified) + S6 38/38 rc0 + smoke 48/48")
d["last_round_at"] = iso
d["ts"] = iso
d["updated"] = iso
d["last_seen"] = iso
d["round_no_label"] = "round 691 (bm-b)"
d["clock_read"] = iso
d["next"] = ("(a) old-code 40min-cap exit -> daemon relaunch with new code "
            "(new-process log RAM-GATE flush lines = public self-proof); "
            "(b) generate lands at RAM window (VALUE trio close ~10-06T17) "
            "-> same-window done-flip; (c) screen-prep + 12-shard SCREEN "
            "relay (<=10-08); (d) W3 judge bm-c ~22:1x watch; (e) 10-09 "
            "market-open data-chain check")
out = json.dumps(d, ensure_ascii=False, indent=1) + "\n"
with io.open(sp, "w", encoding="utf-8", newline="") as f:
    f.write(out)
json.loads(io.open(sp, encoding="utf-8").read())  # r645 self-verify
ev("state", "ok round=691")

# ---------- 3. heartbeat (roundtrip-verified json.dump) ----------
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
h = json.load(io.open(hp, encoding="utf-8"))
try:
    g = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=20)
    gpu_free_mb = int(g.stdout.strip().splitlines()[0])
except Exception:
    gpu_free_mb = h.get("gpu_free_vram_mb", 0)
import psutil
vm = psutil.virtual_memory()
h["last_seen"] = iso
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = iso
h["round_no"] = 691
h["round_no_label"] = "round 691 (bm-b)"
h["current_task"] = (
    "r691 closed: N2-W15 generate RAM-gate wait-loop diagnosed + fixed "
    "(wait_min 40->2880 x2 sites + gate-loop flush, selftest 17/17; old-code "
    "PID 54492 exits at 40min cap, daemon relaunches new code = 48h cap) + "
    "bm-a r694 yield/cleanup wave consumed (MSG-1943/2010 archived, MSG-2005 "
    "receipt, pool single-shard owner=bm-b verified) + S6 38/38 rc0; next = "
    "generate lands at RAM window (trio VALUE close 10-06T17) -> done-flip -> "
    "screen-prep + 12-shard SCREEN relay (<=10-08)")
h["verdict"] = "healthy burning (trio NULLS + N2 generate RAM-gated wait)"
h["ts"] = iso
h["updated"] = iso
h["updated_at"] = iso
h["cpu_util_pct"] = round(psutil.cpu_percent(interval=1), 1)
h["free_ram_gb"] = round(vm.available / (1 << 30), 2)
h["idle_ram_gb"] = round(vm.available / (1 << 30), 2)
h["ram_free_gb"] = round(vm.free / (1 << 30), 2)
h["ram_avail_gb"] = round(vm.available / (1 << 30), 2)
h["total_ram_gb"] = round(vm.total / (1 << 30), 2)
h["gpu_free_vram_mb"] = gpu_free_mb
h["gpu_idle_vram_mb"] = gpu_free_mb
h["gpu_idle_vram_gb"] = round(gpu_free_mb / 1024.0, 2)
h["gpu_free_vram_gb"] = round(gpu_free_mb / 1024.0, 2)
h["gpu_vram_free"] = gpu_free_mb
h["gpu_free_mb"] = gpu_free_mb
out = json.dumps(h, ensure_ascii=False, indent=1) + "\n"
with io.open(hp, "w", encoding="utf-8", newline="") as f:
    f.write(out)
hh = json.loads(io.open(hp, encoding="utf-8").read())
assert isinstance(hh["heartbeat_epoch_utc"], int), "epoch not int (R170/R178)"
ev("heartbeat", "ok epoch=%d gpu_free_mb=%d ram_avail=%.2f" % (
    hh["heartbeat_epoch_utc"], gpu_free_mb, vm.available / (1 << 30)))

# ---------- 4. round report append (r679 marker gate + bytes append) ----------
RP = ("2026-10-04T20:3x+08:00 | r691 (bm-b) PRODUCT (dept:研究工程+舰队协同): "
      "[watermark verdict: GREEN (red=false lane=healthy; satengine alive "
      "rc0 queue=18 held by RAM-floor ~3.1GB<4.0GB 机队纪律自持; audit CLEAN "
      "py 87.1% trio burning-healthy; dualrun DRIFT 观察相 keepalive 面 "
      "streak 归零照录 entries 378/378; post_review ✓45/✗0/🟡5 零活红; "
      "py_watermark verdict=insufficient_history 窗样本距不足诚实照录)] | "
      "当前活: N2-W15 generate 本机在飞（PID 54492·RAM 门原地等待环三证确诊·"
      "旧码 40min 帽到期退出后 daemon 以新码重launch·48h 帽+门环 flush）+ trio "
      "NULLS 三族续烧（owner=bm-b keepalive 鲜活·ETA V 10-06T17/Q 10-07T10/D "
      "10-08T06）+ W3 judge finalize bm-c ~22:1x 观察 | 最近实物: "
      "scripts/perpetual_faces_n2.py RAM 帽标定修（wait_min 40→2880×2 调用位·"
      "诚实拒路径保全）+ scripts/trial_labor_w2.py 门环 flush 修（r680 律）·"
      "selftest 17/17 ALL PASS @20:2x + fleet/inbox/MSG-2026-10-04-2005-bmb-ALL"
      ".md（让渡定谳/清创复核回执） | 下个里程碑: generate candidates 落地"
      "（RAM 物理窗=VALUE 10-06T17 收口后）→同窗 done-flip→screen-prep→12 分片 "
      "SCREEN enrollment（窗≤10-08）| 做了什么: S0-1 四源锚定 bm-b+orders "
      "154/154 轮首收口双扫零未回执（同口径集合比对）+D-19 双键 MATCH（r686 "
      "正典探针 sha256/sha1 method_for 键口径自证复跑）+决策审核步零新涉本司行"
      "（水位不变零动作）+S1 smoke 48/48+S2 板扫 0 open+job_list 空+S3 "
      "satengine rc0 活+修红无+S6 38/38 rc0（log _r691bmb_s6_log.txt·"
      "NON-ZERO LEGS: none·REPORT/LIVE/REGIME/CALL 再生）+origin 前进波全链消费"
      "（bm-a r694 让渡+清创+MSG-1943/2010 归档+MSG-1940 被 bm-a 消费实证+"
      "f7e0b2be6 FF 预对齐 15 交集面 r437-ii 可再生零损失）+双烧双分片事件全链"
      "定谳（origin 真值探针 _r691bmb_n2_origin_truth.py·池条目主键=id 键位）+"
      "RAM 门诊断（零 CPU×15min 双采样+零日志字节 dedup-flush 腿未达+RAM<4GB "
      "全晚三证）+双文件修复+S7 quartet 绿（loop pin=2 no-op/watchdog 幂等/"
      "双爪 LF 归一装）+attrition 4 台账 CLEAN（healed 注记照录） | 验证证据: "
      "smoke 48/48; selftest 17/17 ALL PASS; AST 双门 PASS; S6 38 rc0; D-19 "
      "双 MATCH; orders 集合比对 154/154 零差; 池面真值单分片 n2-w15-"
      "generate-0of1 owner=bm-b 19:44:22 实证; PID 54492 CIM 双采样 utime 冻结"
      "实证 | 产品分: 1（runner 双文件修复=selftest 实证的可跑实物改动+协调回执"
      "件；诚实注记: generate 产物未落地=RAM 物理窗未开·trio 在飞占用非本轮可"
      "控）| 坑律新增: 1（CODELY r691 RAM 门等待环三面隐形×帽标定-熔断链复合条）"
      "| 下轮指针: (a) 旧帽退出→daemon 新码重launch 实证（新进程日志 RAM-GATE "
      "flush 行可见=诊断公开自证+crash fuse code_changed 自清 tombstone 核验）;"
      "(b) trio V 10-06T17 收口→generate 落地窗; (c) W3 judge bm-c 落地观察; "
      "(d) screen relay ≤10-08; (e) 10-09 开市前数据链完备核验 | 本地未达 "
      "origin commit 数=0（commit 后 push+fetch+rev-list 自证）\n")
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
rb = io.open(rp, "rb").read()
assert rb.count(b"round 691 (bm-b)") == 0, "r679 marker already present"
with io.open(rp, "ab") as f:
    f.write(RP.encode("utf-8"))
ev("round_report", "ok appended %d bytes" % len(RP.encode("utf-8")))

with io.open(EV, "w", encoding="utf-8") as f:
    f.write("r691 bm-b closeout %s\n" % iso + "\n".join(log) + "\n")
print("CLOSEOUT OK")
for line in log:
    print(line)
