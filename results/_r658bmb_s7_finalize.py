import json, os, time
from datetime import datetime

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = time.time()
epoch = int(now)
clock = datetime.now().astimezone().isoformat(timespec="seconds")

# --- 1. round report append (bytes mode, mixed-encoding history file, r641 law) ---
rr = os.path.join(R, "logs", "iteration-loop", "round_reports.md")
line = (
    "%s | round 658 (bm-b) | dept:工程/舰队 全绿值守轮: 当前活=FUND trio NULLS烧(V661/D363/Q504 of 2000各,pids 34396/57116/30208活); 最近实物=finalize就绪探针三族门径全验证REFUSED rc3(nulls 661/363/504各of 2000,门径健康零写入)+r633②VALUE空被动窗崩点属主修已核在树(_passive_window None守卫+首非空月起窗+audit披露面); S0 churn-absorb 8车道daemon面(241b908c5,commit误标r668应r658如实记)+rebase净窗(origin bff4de40b=bm-a r665收口2 commit); S0.5令差集零(153/153); D-19双MATCH零消费(sparse-clone origin-blob原字节哈希,decisions/orders sha恒等); S1 48/48; S2板零open票(job_list空+fleet 46票全claimed); S3门序全绿(WM red=false、引擎alive rc0 idle、池3ready=trio本机烧中+1waiting=W14 GM停泊维持)→常设线不触发新批; S6 34腿rc0 fail=0(dualrun streak50、09-30国庆休市无新bar→live.paper条件腿不触发、REPORT/LIVE-2026-10-04幂等刷新); S7四件套自愈(loop pin=2 no-op+watchdog重注册+双爪installed)+attrition CLEAN; | 证据=S6链34rc0+finalize三族REFUSED探针+S6 evidence件+attrition CLEAN行 | 下轮指针: trio机械就绪即finalize+E1判决(窗10-05..10-09,按烧速ETA~10-05深夜..10-06); 下个里程碑=trio finalize+E1判决批(窗内≤48h) | 本地未达origin commit数=0(commit后push_verify自证) | token: L2本地2腿零云端\n" % clock
)
with open(rr, "ab") as f:
    f.write(line.encode("utf-8"))
print("round_report appended")

# --- 2. state.json update (programmatic write + self-verify, r645 law) ---
sp = os.path.join(R, "state.json")
st = json.loads(open(sp, "rb").read().decode("utf-8"))
st["round_no"] = 658
st["round_no_label"] = "round 658 (bm-b)"
st["note"] = ("r658: all-green watch round + finalize-readiness verification -- S0 churn-absorb 8 local daemon faces (commit 241b908c5, msg mislabeled r668 should-be r658, honest note) "
              "then clean rebase onto origin bff4de40b (bm-a r665 closeout); orders delta zero (153/153); D-19 double MATCH zero-consume (sparse-clone origin-blob raw-bytes sha, both equal); "
              "S1 48/48; S2 zero open tickets (job_list empty + fleet 46 all claimed); S3 gates green, WM red=false, engine alive rc0 idle, pool 3-ready=trio burning local + 1-waiting=W14 GM-parked -> no new trial batch; "
              "finalize readiness probes: all three REFUSED rc3 healthy (nulls V661/D363/Q504 of 2000 each), r633-b VALUE empty-passive-window owner fix verified in-tree (None guard + first-non-empty-month start + disclosure); "
              "S6 34 legs rc0 fail=0 (dualrun streak 50; expected bar 2026-09-30 holiday-closed no new bar -> live.paper conditional legs skipped; REPORT/LIVE-2026-10-04 idempotent refresh); "
              "trio pids 34396/57116/30208 alive; S7 loop pin=2 no-op + watchdog registered + both claws installed, attrition CLEAN")
st["last_round_at"] = clock
st["ts"] = clock
st["updated"] = clock
st["last_seen"] = clock
st["clock_read"] = clock
st["last_decisions_read_at"] = clock
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, indent=1, ensure_ascii=False)
print("state written")

# --- 3. heartbeat update (programmatic + int-epoch self-verify) ---
hp = os.path.join(R, "fleet", "machines", "bm-b.json")
hb = json.loads(open(hp, "rb").read().decode("utf-8"))
hb["last_seen"] = clock
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock
hb["round_no"] = 658
hb["round_no_label"] = "round 658 (bm-b)"
hb["current_task"] = ("当前活: FUND trio NULLS burn V661/D363/Q504 of 2000 each, pids 34396/57116/30208 alive | "
                      "最近实物: finalize readiness probes all-3 REFUSED rc3 healthy + r633-b owner fix verified in-tree + REPORT/LIVE-2026-10-04 refreshed | "
                      "下个里程碑: trio mechanical_ready -> finalize+E1 verdict batch, window 10-05..10-09, ETA ~10-05 late night..10-06 (within 48h)")
hb["verdict"] = ("GREEN (smoke 48/48; orders delta zero 153/153; D-19 double MATCH; WM red=false; engine alive rc0 idle; "
                 "S6 34 legs rc0 fail=0 dualrun streak 50; trio V661/D363/Q504 advancing pids alive, finalize gates verified REFUSED rc3 healthy; "
                 "attrition CLEAN; claws/pins self-healed; zero cloud token)")
hb["ts"] = clock
hb["updated"] = clock
try:
    import psutil
    hb["cpu_util_pct"] = round(psutil.cpu_percent(interval=1), 1)
    vm = psutil.virtual_memory()
    hb["free_ram_gb"] = round(vm.available / (1024 ** 3), 2)
    hb["idle_ram_gb"] = hb["free_ram_gb"]
    hb["ram_avail_gb"] = hb["free_ram_gb"]
    print("psutil sampled cpu=%.1f ram=%.2f" % (hb["cpu_util_pct"], hb["free_ram_gb"]))
except Exception as e:
    print("psutil unavailable, kept old resource fields:", e)
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, indent=1, ensure_ascii=False)
print("heartbeat written")

# --- 4. self-verify (json.loads + int epoch + T-separated clock, R170/R178/R262 laws) ---
for p, key in [(sp, None), (hp, "heartbeat_epoch_utc")]:
    d = json.loads(open(p, "rb").read().decode("utf-8"))
    if key:
        assert isinstance(d[key], int), "epoch not int"
    assert "T" in d["clock_read"] and " " not in d["clock_read"], "clock not T-separated"
print("SELF-VERIFY PASS: both files parse, epoch int, clock T-separated")
