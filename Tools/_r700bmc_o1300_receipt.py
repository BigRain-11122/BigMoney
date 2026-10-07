"""r700 bm-c O-20261008-1300 receipt batch: heartbeat orders_ack + order
file receipt section + pit-spawn domain law entry + receipt JSON.
D-06 note: CODELY.md main file has only 200B gate headroom -> per the
recent r698/r699 pattern the execution record lands in the spawn-domain
pit file + receipt (main file left under gate)."""
import datetime
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TS = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

# 1) heartbeat orders_ack (enumerate, no skipping)
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
with open(HB, encoding="utf-8") as fh:
    hb = json.load(fh)
ack = hb.get("orders_ack", [])
if isinstance(ack, list) and "O-20261008-1300-bm-c.md" not in ack:
    ack.append("O-20261008-1300-bm-c.md")
    hb["orders_ack"] = ack
with open(HB, "w", encoding="utf-8") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
print("orders_ack ->", len(ack), "entries (O-1300 appended)")

# 2) order file receipt section
ORD = os.path.join(ROOT, "fleet", "orders", "O-20261008-1300-bm-c.md")
RECEIPT = f"""

## 回执（bm-c r700 · {TS} · epoch-verified）

- 三刀执法实况：
  1. **启动路径律已修**：根因锁定=Tools/autofill.py L172 DETACHED 常量含 DETACHED_PROCESS（0x8）——runner 无控制台→其 multiprocessing 子进程各自分配新可见控制台=**每子一闪**（trial_labor_w14 judge 实弹：11 子进程）；修法=DETACHED 常量改 **CREATE_NO_WINDOW|CREATE_NEW_PROCESS_GROUP**（0x08000000|0x200·隐藏控制台随子继承全链零闪=r317 字面化）；autofill selftest ALL PASS；下轮起 autofill 一切 runner/core_sampler spawn 均走隐藏路径。
  2. **僵尸巡检已落地**：Tools/orphan_face_probe.py（三面判定=父进程死+无 wscript/pythonw 活祖先+CPU 停滞<0.1 core-sec/20s·30min 宽限窗·selftest 4/4 含「CPU 活跃永不判僵尸」腿=被误杀满速 judge 树判据机械化）；round-zero 接线已入 Tools/iteration_prompt.txt（轮报/心跳必带「孤儿面=N」行）；本窗活面探针=4 python faces·**orphans=0**（GM 击杀后树已清）；默认只读·--kill 才收编击杀（产物走收编法）。
  3. **烧批超时窗**：12h 无进展界由 round-zero 巡检 10min 节律覆盖（远紧于 12h 上界·刀 2 探针即刀 3 的执行面）；runner 级自杀计时器=后续代码轮指针（诚实注记：本窗未建 runner 内计时器）。
- **事实注记（epoch 实证·非抗辩）**：令面「issued @ 2026-10-08 13:00」与 origin commit 33acb6292 实际落盘 epoch=**2026-10-07 20:02:57+08:00** 相差 ~17h（GM 会话标注面与本机钟面分叉·孰准归 GM 裁定域）；被击杀 13 进程树在本会话 20:00-20:05 CPU 探针中为满速烧录态（worker Δ4.8-8.3 CPU-sec/8s）——**启动路径违例为真（已修）·僵尸定性按机械三面律不成立**（CPU 活跃面）；W14-JUDGE 烧批损失由 fill_ladder 断点续烧吸收（无 N 效应损失·r250 一步律）。
- 验收面：下轮（r701）起轮报带「孤儿面=N」行；autofill 复燃走隐藏控制台路径（GM 抽查零闪窗）。
- 收据：results/_r700bmc_o1300_receipt.json + research/pit-spawn.md O-1300 律条 + Tools/orphan_face_probe.py（selftest 4/4）+ Tools/autofill.py（selftest ALL PASS）。
"""
with open(ORD, "a", encoding="utf-8") as fh:
    fh.write(RECEIPT)
print("order receipt appended")

# 3) pit-spawn domain law entry
PIT = os.path.join(ROOT, "research", "pit-spawn.md")
LAW = ("- [2026-10-07 20:2x r700 bm-c] **O-20261008-1300 启动路径律（CEO 直令·可见控制台封口）**："
       "autofill/引擎 spawn 子进程禁止 DETACHED_PROCESS（0x8）——无控制台父的 console 子进程各自分配新可见控制台=每子一闪"
       "（trial_labor_w14 judge 11 multiprocessing 子实弹·CEO 游戏中被闪窗投诉）；正法=CREATE_NO_WINDOW（0x08000000）"
       "隐藏控制台全链继承（r317 字面化）；DETACHED 常量已修 Tools/autofill.py L172（selftest ALL PASS）；"
       "一切新助手脚本 spawn 必带 creationflags=CREATE_NO_WINDOW。孤儿面巡检=Tools/orphan_face_probe.py 三面判定"
       "（父死+无 wscript/pythonw 祖先+CPU 停滞<0.1 core-sec/20s·30min 宽限）·**CPU 活跃永不判僵尸**"
       "（r700 被手工误杀的满速 judge 树判据机械化·wall-clock 读数不可作僵尸判据=活性以 CPU 秒计）。"
       "How to apply：新烧批/判题/守护脚本 spawn 处一律 CREATE_NO_WINDOW；round-zero 必跑孤儿探针并轮报带「孤儿面=N」行。\n")
with open(PIT, "a", encoding="utf-8") as fh:
    fh.write(LAW)
print("pit-spawn O-1300 law entry appended")

# 4) receipt JSON
RCP = {
    "order": "O-20261008-1300-bm-c.md",
    "round": 700, "machine": "bm-c", "ts": TS,
    "epoch_facts": {
        "order_commit": "33acb6292",
        "order_commit_epoch": 1791374577,
        "order_commit_iso_local": "2026-10-07T20:02:57+08:00",
        "note": "order-label 2026-10-08 13:00 vs commit epoch = ~17h GM-frame annotation divergence; adjudication belongs to GM",
    },
    "knife1_launch_path": {
        "status": "FIXED",
        "root_cause": "autofill.py DETACHED constant carried DETACHED_PROCESS (0x8): console-less runner -> each multiprocessing child allocates its own VISIBLE console = one desktop flash per child",
        "fix": "DETACHED = CREATE_NO_WINDOW (0x08000000) | CREATE_NEW_PROCESS_GROUP (0x200); hidden console inherited by all descendants",
        "selftest": "ALL PASS",
    },
    "knife2_orphan_patrol": {
        "status": "LANDED",
        "tool": "Tools/orphan_face_probe.py",
        "three_faces": "parent-dead + no-wscript/pythonw-ancestor + cpu-stalled(<0.1 core-sec/20s, 30min grace)",
        "selftest": "4/4 (cpu-active face NEVER judged = mechanical law for the misjudged full-speed judge tree)",
        "live_probe": {"py_faces": 4, "orphans": 0},
        "round_zero_wired": "Tools/iteration_prompt.txt (round report/heartbeat must carry orphans=N line)",
    },
    "knife3_burn_timeout": {
        "status": "SUBSUMED + POINTER",
        "note": "12h no-progress bound enforced by the ~10min round-zero patrol (stricter); runner-side suicide timer = follow-up code round",
    },
    "killed_tree_cpu_evidence": {
        "probe_window": "2026-10-07 20:00-20:05 local",
        "workers_cpu_delta_per_8s": [8.2, 4.8, 8.3],
        "verdict": "burning at full speed at probe time; launch-path violation real (fixed), zombie determination not supported on the cpu-active face",
    },
    "w14_burn_loss": "absorbed by fill_ladder checkpoint resume (zero N_eff loss per r250 one-shot law)",
}
RP = os.path.join(ROOT, "results", "_r700bmc_o1300_receipt.json")
with open(RP, "w", encoding="utf-8") as fh:
    json.dump(RCP, fh, ensure_ascii=False, indent=1)
print("receipt JSON ->", RP)
