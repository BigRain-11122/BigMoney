# r358 bm-c S7 bookkeeping: state + heartbeat + round report, one pass.
# Format laws: r289/r500 (probe indent+EOL before rewrite), F7 heartbeat
# (epoch int type, clock_read T-separated), r296 probe-not-assume.
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
TZ = timezone(timedelta(hours=8))
now = datetime.now(TZ)
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
print("NOW=" + ts + " EPOCH=" + str(epoch))

# system snapshot (psutil, primed per r319 law)
import psutil
psutil.cpu_percent(interval=None)
time.sleep(1.2)
cpu_pct = round(psutil.cpu_percent(interval=None), 1)
vm = psutil.virtual_memory()
idle_ram_gb = round(vm.available / (1024 ** 3), 1)
gpu_free = None
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"], capture_output=True)
    if r.returncode == 0 and r.stdout.strip():
        gpu_free = int(r.stdout.strip().splitlines()[0])
except Exception as exc:
    print("GPU probe fail:", exc)
print("SYS cpu=%s idle_ram=%s gpu_free=%s" % (cpu_pct, idle_ram_gb, gpu_free))


def probe_fmt(path):
    raw = open(path, "rb").read()
    txt = raw.decode("utf-8")
    indent = 1
    for line in txt.splitlines()[1:6]:
        if line.startswith(" "):
            indent = len(line) - len(line.lstrip(" "))
            break
    eol = "\r\n" if "\r\n" in txt else "\n"
    return raw, indent, eol


# 1) state-bm-c.json
sp = os.path.join(ROOT, "state-bm-c.json")
raw, ind, eol = probe_fmt(sp)
st = json.loads(raw)
st["round_no"] = 358
st["last_round_at"] = "r358"
st["last_round_ts"] = ts
st["updated"] = ts
st["cpu_pct"] = cpu_pct
st["idle_ram_gb"] = idle_ram_gb
st["gpu_free_vram_mib"] = gpu_free if gpu_free is not None else st.get("gpu_free_vram_mib", 10074)
st["verify"] = ("r358: dead-session chain r355/r356/r357 forensics-adopted (state stuck 354, "
                "three self-labeled commits on origin, numbers burned per r529 law); S0 ride+rebase "
                "0/0, engine W63 9 shard appender strays delivered (double-burn face lifted, origin "
                "ls-tree 9/9); W63 three-hole quarantine CURE (2/5/8 crash x3 = historical indent-"
                "corruption window, py_compile 3-verified, kill+state-edit+task-reignite, 12/12 "
                "09:02:44) + FINALIZE one-pass K=136,520 == sec.0 bitwise, ledger 500,948+2,200 = "
                "503,148 CHAIN HEAD, S5 4/4 PASS, s7/s8 backfill, default-wave selftest W2..W64 "
                "PASS; W64 upstream seat cleared (bm-a W64 finalize unlocked); S6 32 legs rc0; "
                "smoke 47/47; orders diff EMPTY; D-19 MATCH-unchanged.")
st["did"] = ("r358: S0 dead-session adoption + W63 hole-cure + W63 finalize (K=136,520, ledger "
             "503,148) + S6 chain + inbox 3 receipts")
st["current_task"] = ("W63 full lifecycle closed same window (cure -> 12/12 -> finalize K=136,520 "
                      "ledger 503,148); chain W1..W63 all landed; T-131 fund_history backfill in "
                      "flight (~62%); engine idle (W64 = bm-a owned, cross-machine burn in progress)")
st["next"] = ("(r359)(a) W65 freeze decision (fetch-verify table tail: W64 owned by bm-a burning; "
              "own-series first-free after W64 per de-throttle law); (b) T-131 backfill watch to "
              "completion (r340 three-face law); (c) T-134 s2 p1e_synth conversion (r304 paradigm); "
              "(d) register_satengine S4U-first cleanup (D-20261002-02, window 10-04); (e) T-143 "
              "month-exam prep ticket claim decision (deliverable 10-29); (f) month-boundary first "
              "exam 10-31")
st["heartbeat_epoch_utc"] = epoch
st["clock_read"] = ts
st["note"] = ("r351 skipped dead r347-r350 numbering per r529 law; r358 skips dead r355-r357 "
              "(state stuck 354 + three self-labeled r357-window commits on origin, products "
              "W59/W60 finalize + W61/W62 closeout + W63 freeze all verified on origin, zero "
              "redone). W63 = three-hole quarantine cure precedent (engine memory-frozen "
              "quarantined set, kill-clean-reignite path).")
st["last_ts"] = ts
st["last_decisions_sha"] = "4FD50184453162A8B01C47D6CA79224B95869DB2487AA18E10D61479177F250C"
st["last_decisions_read_at"] = ts
st["last_round"] = ("2026-10-02 r358 bm-c: W63 three-hole cure + finalize (K=136,520, ledger "
                    "503,148 chain head) + dead-session r355-r357 adoption + S6 chain + inbox 3")
st["last_seen"] = ts
out = json.dumps(st, ensure_ascii=False, indent=ind)
open(sp, "wb").write(out.replace("\n", eol).encode("utf-8"))
chk = json.loads(open(sp, "rb").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (F7)"
print("STATE OK round=%s epoch_int=%s" % (chk["round_no"], isinstance(chk["heartbeat_epoch_utc"], int)))

# 2) heartbeat fleet/machines/bm-c.json
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
raw, ind, eol = probe_fmt(hp)
hb = json.loads(raw)
hb["round_no"] = 358
hb["cpu_pct"] = cpu_pct
hb["cpu_util_pct"] = cpu_pct
hb["cpu_idle_pct"] = round(100 - cpu_pct, 1)
hb["idle_ram_gb"] = idle_ram_gb
hb["ram_free_gb"] = idle_ram_gb
hb["free_ram_gb"] = idle_ram_gb
if gpu_free is not None:
    hb["gpu_free_vram_mb"] = gpu_free
    hb["gpu_free_vram_mib"] = gpu_free
    hb["gpu_idle_vram_mb"] = gpu_free
    hb["gpu_idle_vram_mib"] = gpu_free
    hb["gpu_vram_free_mb"] = gpu_free
hb["prod_lanes"] = ("r358: W63 FULL LIFECYCLE closed (three-hole quarantine cure 12/12 09:02:44 "
                    "-> finalize one-pass K=136,520, ledger 503,148 CHAIN HEAD, S5 4/4, s7/s8 "
                    "backfilled, selftest W2..W64); chain W1..W63 ALL LANDED; engine W63 9-stray "
                    "appender delivery done (r488 double-burn face lifted)")
hb["current_task"] = ("r358 done: W63 full lifecycle (cure + finalize K=136,520 ledger 503,148); "
                      "T-131 backfill in flight (~62%)")
hb["updated_at"] = ts
hb["last_seen"] = ts
hb["last_seen_at"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts
hb["health"] = "ok"
hb["verdict"] = ("healthy: W63 closed same-window (cure -> 12/12 -> finalize ledger 503,148); "
                 "chain W1..W63 caught up; engine idle (W64 = bm-a owned, cross-machine burn); "
                 "T-131 network collector in flight (~62%)")
hb["activity_now"] = ("r358: W63 three-hole quarantine cure + finalize one-pass (K=136,520, "
                      "ledger 503,148) + dead-session r355-r357 adoption (S0 ride/rebase 0/0, "
                      "9 stray shards delivered) + S6 32 legs rc0 + smoke 47/47 + orders EMPTY + "
                      "D-19 MATCH + inbox 3 receipts (W63 seat/bmb W64 HOLD/bma yield+B-"
                      "semantics disclosure)")
hb["latest_artifact"] = ("results/perpetual_faces/n1_w63_results.json (ledger 503,148 chain head, "
                         "K=136,520 == projection bitwise, S5 4/4 PASS) + "
                         "research/PERPETUAL_N1_W63_PREREG.md s7/s8 backfill (commit 4de45c3e0, "
                         "2026-10-02T09:1x+08:00)")
hb["next_milestone"] = ("W65 freeze decision next round (own-series after bm-a's W64; window "
                        "<=48h); T-131 completion (~hours); month-boundary first exam 10-31")
out = json.dumps(hb, ensure_ascii=False, indent=ind)
open(hp, "wb").write(out.replace("\n", eol).encode("utf-8"))
chk = json.loads(open(hp, "rb").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "hb epoch must be int (F7)"
assert "T" in chk["clock_read"], "clock_read must be T-separated (F7)"
print("HEARTBEAT OK round=%s epoch_int=%s" % (chk["round_no"], isinstance(chk["heartbeat_epoch_utc"], int)))

# 3) round report append (EOL probe, append-only)
rp = os.path.join(ROOT, "round_reports-bm-c.md")
raw = open(rp, "rb").read()
eol = "\r\n" if b"\r\n" in raw else "\n"
line = (
 "2026-10-02T09:1x+08:00｜r358｜dept:研究（W63 全生命周期收口：三缺片治愈+finalize）+dept:工程（S0 三连猝死收编+appender 9 片送达）｜"
 "watermark verdict=绿（red=false·lane healthy·S6 probe rc0）｜"
 "S0: r355/r356/r357 三连猝死会话取证收编（state 停 354+origin 自标 commit+无活会话=r529 律号位烧毁·r358 续系列；遗产三面定性=W62/W63 研究面+工具件已被其 origin commit 送达=本地 M/untracked 恒等残留零重做）"
 "→ride e7d5bf5c8+rebase（3 UU=W63 注册面子集验证全过取 origin 侧·resolver 逐件断言零 local-only）+push 0/0；"
 "本机引擎 W63 appender 9 片滞留送达（push 双拒 fetch first→mini-ride→rebase→push 双连发一次过·origin ls-tree 9/9 实证·r488 族他机重烧面解除）｜"
 "主产出=**W63 三缺片隔离治愈+finalize one-pass**：诊断（quarantined=[63,2/5/8]·crash×3·queue 空自洽=隔离面+W64 owner gate）→崩因定谳（IndentationError L7964=r357 编辑坏窗历史面·py_compile 三验过·同窗 9 片成功+63:0/1/11 崩 2 次自愈佐证）→治愈三步（杀常驻 13012 双扫零+state 文本定点清隔离面 json.loads 自证+1-min 任务自燃新实例）→09:02:44 三片一次烧成 12/12（产物增长律）"
 "→finalize K=136,520==§0 投影逐位·ledger 500,948+2,200=**503,148 链头**（voids LOWAMP-P1/P2）·S5 4/4 PASS（mu Δ0.0062<0.02/sigma −0.06%<10%/A p95 Δ−0.0021<0.05/K-lift −0.0005≤0.02·skill_line 1.1619→1.1614 @n_eff 500,948）·se_mu 0.000668→0.000662 收窄·§7/§8 机械回填+回填后缺省波 selftest PASS 全链 W2..W64（r307 两态闭环）·W64 上游席清零（bm-a W64 finalize 解锁）｜"
 "S6 链 32 腿 rc0（dualrun/audit/watermark 绿·车道守卫诚实 no-op·fund_premium bm-c 动作腿·b_layer gates·REPORT/LIVE-2026-10-02 再生·token delta=0）｜"
 "S0.5 令差集 EMPTY（143/143 机证）·D-19 水位 4FD50184 MATCH-unchanged（raw-blob 法）｜S1 smoke 47/47｜"
 "S7: attrition CLEAN·loop pin=5 no-op·watchdog ACL 拒=良性在位（r341 先例）·claw 在位·inbox 三件收执归档（0843 W63 席位公示/0849 bmb W64 HOLD/0851 bma 让路回执+B 跳位语义分歧披露=HQ-FEEDBACK 候选·正主收执零动作）｜"
 "CODELY.md 112.7KB 水位照报（r504 注记=GM/集团裁定面·bm-a r566 同例）+S4 坑律新条=quarantine 双面治愈律｜"
 "实况三行（CEO 过程可见面）：当前活=W63 已收官账本 503,148+引擎空闲（W64=bm-a owned 跨机烧录中）+T-131 采集在飞 ~62%｜"
 "最近实物=results/perpetual_faces/n1_w63_results.json（K=136,520·ledger 503,148·commit 4de45c3e0·09:1x）+PERPETUAL_N1_W63_PREREG.md §7/§8 回填｜"
 "下个里程碑=W65 冻结决策（bm-a W64 收口后自有系列续位·窗≤48h）+T-131 采集完收口+月界首考 10-31｜"
 "产品分=2（finalize 科学件+缺片治愈=能跑能看实物）｜坑律新增=1｜本地未达 origin commit 数=收尾 push 后 fetch 自证｜"
 "next: (r359)(a) W65 冻结决策（fetch 实核表尾·W64=bm-a owned 在烧）；(b) T-131 巡检至完（r340 三面律）；(c) T-134 s2 p1e_synth 转换（r304 范式）；(d) S4U 清理窗 10-04；(e) T-143 月考备战票认领决断；(f) 月界首考 10-31"
)
open(rp, "ab").write((eol + line + eol).encode("utf-8"))
print("REPORT appended, total lines now:", len(open(rp, "rb").read().splitlines()))
