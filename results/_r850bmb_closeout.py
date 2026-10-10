# -*- coding: utf-8 -*-
# r850 bm-b closeout: state.json + heartbeat update (driver file, GBK-safe)
import io
import json
import time
import datetime
import psutil

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# ---- machine resource readout ----
vm = psutil.virtual_memory()
ram_free_gb = round(vm.available / (1024**3), 1)
ram_free_pct = round(vm.available / vm.total * 100, 1)
try:
    import subprocess
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        capture_output=True, text=True,
    )
    vram_free_gb = round(float(out.stdout.strip().splitlines()[0]) / 1024, 2)
except Exception:
    vram_free_gb = None

NOTE = ("r850: C-20261010-01/02 双案 bm-b 侧异构补票窗内落地（HQ-FEEDBACK F-20261011-01·四判词全赞成·窗 10-11 13:00 前 ~12.5h 早到·D-20261011-01 承接=条件过会转全过会双机票齐） "
        "+ O-20261011-0012 CEO 机队CPU满用令承接（bm-b 条款4=重建完毕即认领池面+矩阵切片·审计面在役 py_cpu 15.1/4.9+队列深度 pool 0/fleet 0/matrix 9/10 bm-a·条款1 W17 并行=bm-a lane 单执行体让路·条款6 意义性律零为烧而烧） "
        "+ S0.5 D19 双 delta 消费（dec a20664ec→caca0c6e·ord 24e6066e→c9a4be3f·D-20261011-01~04 逐行·他司域零动作） "
        "+ S1 smoke 49/49 + S3 全活面 gated 诚实等待（astock 3670/5217 70% ETA ~02:08·T23 census=面板依赖·W207=上游 W205/W206 五面·W18=W17-JUDGE drain-gated·矩阵 P0=bm-a 活跃 lane 9/10 零撞面） "
        "+ S6 全链绿（dualrun streak 5·34 腿 rc0+alloc rc2 已知 510880+lane-io 守卫 bm-a fresh 诚实跳过·REPORT-2026-10-11+LIVE-2026-10-11 再生） "
        "+ S7 四任务活/双爪恒等/attrition CLEAN + idle --worked 清零")

VERDICT = ("GREEN: r850 (bm-b 补票 C-20261010-01/02 landed F-20261011-01 = 双机异构票齐·条件过会转全过会判据满足; O-20261011-0012 满用令承接审计面在役; "
           "astock rebuild in flight 3670/5217 70% ETA ~02:08; T23 census/W207 freeze gated honest; engine alive rc0 pool_empty_or_busy)")

TASK = ("r851 queue: astock completion verify (ETA ~02:08) -> spawn detached T23 census full burn -> census_holds readout -> N2 U3(1) prereg window / G2 fallback + S6 chain; "
        "O-20261011-0012 条款4 执行点=重建完毕即认领池面+矩阵切片（属主道自助）; "
        "W207 five-face freeze window (gated on W205 bm-a + W206 bm-c five faces landing on origin; anchor roll per r590 before freeze commit; selftest W207 face + M8-mirror watcher); "
        "W18 stays drain-gated (bm-a owns w17-judge)")

ARTIFACT = "r850: HQ-FEEDBACK.md F-20261011-01 补票行 (2026-10-11 00:26) + docs/daily_report/REPORT-2026-10-11.md + docs/live_usage/LIVE-2026-10-11.md (00:2x)"

MILESTONE = ("astock panel complete (~02:08) -> detached T23 census full burn -> holds verdict (window <=10-11 06:00) -> N2 U3(1) prereg window / G2 fallback; "
             "O-20261011-0012 条款4 pool+matrix claim at rebuild completion; W207 five-face freeze gated on W205/W206 five faces landing (anchor roll r590)")

# ---- state.json ----
sp = "state.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 850
st["round_no_label"] = "r851"
st["note"] = NOTE
st["did"] = NOTE
st["last_action"] = NOTE
st["verdict"] = VERDICT
st["current_task"] = TASK
st["task"] = TASK
st["next"] = TASK
st["now_active"] = "r850 closeout: bm-b 补票 C-20261010-01/02 landed (F-20261011-01); O-20261011-0012 acknowledged; astock rebuild in flight 3670/5217 70%"
st["latest_artifact"] = ARTIFACT
st["next_milestone"] = MILESTONE
st["last_round_at"] = now_iso
st["last_round_ts"] = now_iso
st["ts"] = now_iso
st["updated"] = now_iso
st["updated_at"] = now_iso
st["last_seen"] = now_iso
st["clock_read"] = now_iso
st["round"] = 850
st["last_decisions_sha"] = "caca0c6e08d3243f89c6d05dcabcd2a130f849a8"
st["last_decisions_at"] = now_iso
st["last_decisions_read_at"] = now_iso
st["last_orders_sha"] = "c9a4be3f59ea394e467c3fc3ebf1f3a1e89c0ccc"
st["last_orders_read_at"] = now_iso
st["last_orders_sha_note"] = "r850: dual delta consumed (dec caca0c6e, ord c9a4be3f); D-20261011-01~04 processed; C-20261010-01/02 bm-b 补票 landed"
with io.open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")

# ---- heartbeat fleet/machines/bm-b.json ----
hp = "fleet/machines/bm-b.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["round"] = 850
hb["round_no"] = 850
hb["now_active"] = st["now_active"]
hb["current_task"] = TASK
hb["task"] = TASK
hb["next"] = TASK
hb["did"] = NOTE
hb["last_action"] = NOTE
hb["latest_artifact"] = ARTIFACT
hb["next_milestone"] = MILESTONE
hb["verdict"] = VERDICT
hb["last_round_at"] = now_iso
hb["last_seen"] = now_iso
hb["updated"] = now_iso
hb["updated_at"] = now_iso
hb["ts"] = now_iso
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["cpu_cores"] = psutil.cpu_count(logical=True)
hb["free_ram_gb"] = ram_free_gb
hb["ram_free_gb"] = ram_free_gb
hb["ram_free_pct"] = ram_free_pct
if vram_free_gb is not None:
    hb["gpu_free_vram_gb"] = vram_free_gb
    hb["vram_free_gb"] = vram_free_gb
    hb["gpu_free_vram_mb"] = int(vram_free_gb * 1024)
oa = hb.get("orders_ack") or []
new_orders = ["O-20261011-0012-bm-a.md"]
for o in new_orders:
    if o not in oa:
        oa.append(o)
hb["orders_ack"] = oa
hb["orders_ack_count"] = len(oa)
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_faces"] = 0
hb["orphan_face_note"] = "round-zero probe 00:1x py_faces=13 orphans=0 (read-only)"
with io.open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")

# self-verify epoch int + clock T-separator
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must be T-separated ISO8601"
print("state+heartbeat written; epoch", chk["heartbeat_epoch_utc"], "clock", chk["clock_read"], "ram_free_gb", ram_free_gb, "vram", vram_free_gb, "orders_ack", len(oa))
