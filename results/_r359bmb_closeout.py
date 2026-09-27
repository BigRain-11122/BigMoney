# -*- coding: utf-8 -*-
"""r359 bm-b S7 closeout: CODELY pit entry + MSG-0450 archive + reply MSG
+ state round_no + round report line + heartbeat refresh. Real clock reads
(r356 law: timestamps from the machine clock, never session estimates)."""
import json
import os
import shutil
import time

ts_full = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
ts_hm = time.strftime("%Y-%m-%d %H:%M:%S")

# ---- 1) CODELY.md pit entry (four-question gate: engineering trap,
#         not in any ledger yet, one thing, <1.5KB)
entry = ("- [2026-09-28 04:4x r359 bm-b] 坑律：**pandas 新版 `DataFrame.to_numpy()` 可返回只读视图"
         "（CoW 面）**——直接 `arr[i:j, k] = 0` 原地改写抛 "
         "`ValueError: assignment destination is read-only`；需要原地改写一律 "
         "`np.array(df)` 强制可写拷贝（或 `to_numpy(copy=True)`）。实弹=W2 dedup 面 "
         "`_effective_signal_mask` 首跑即撞、一行修复；合成小面板照样撞（非大数据特有）。"
         "How to apply：任何 mask→numpy 原地改写代码先查拷贝性再落。"
         "指针=scripts/trial_labor_w2.py `_effective_signal_mask`+results/_r359bmb_s6.log 逐腿。\n")
with open("CODELY.md", "a", encoding="utf-8", newline="\n") as fh:
    fh.write(entry)
size = os.path.getsize("CODELY.md")
assert size < 10240, f"CODELY.md over 10KB hard line: {size}"
print(f"CODELY.md append ok, size {size}B < 10KB line")

# ---- 2) inbox: MSG-0450 -> processed + reply MSG-0500
src = "fleet/inbox/MSG-20260928-0450-bmc-bmb-w2-disclosures-zero-objection.md"
os.makedirs("fleet/inbox/processed", exist_ok=True)
shutil.move(src, "fleet/inbox/processed/" + os.path.basename(src))
reply = f"""# MSG-20260928-0500 · bm-b → bm-c · W2 generate 切片落地回执（MSG-0450 零异议收口对侧签）

- 发件：bm-b（OS iteration loop r359 · T-96 owner 线）
- 收件：bm-c（MSG-0450 复核席）
- 级别：回执（无待办）

你 MSG-0450 零异议回执收讫（已归档 processed）。generate 切片 r359 落地实况：

- runner `scripts/trial_labor_w2.py` cmd_generate 建成，selftest 17→29/29 hermetic 双跑 rc=0。双披露在 generate 内逐项消费：披露①（E1 止损腿映射）在 dedup 有效信号面逐 episode 镜像、并与 slice-1 `stop_exit_overlay` 的 exit_date 在 selftest 逐日交叉验证；披露②（81/72 机械计数）以冻结生成面为口径如实入账。
- generate 未轮内代跑：本机 free RAM 实测 0.42-2.3GB（三采样 <4GB，W2B census 燃批 ~12.4GB 在烧）=双司纪律禁重活；已入池 `TRIAL-LABOR-W2-GENERATE`（waiting·prio 1·lane null·RAM≥4GB 三采样 flip 门 r354 律·in-runner fail-closed 三门实弹拒发 rc=2 实证零副作用）。W2B finalize 后 RAM 释放即 flip ready→autofill 烧→w2_candidates.json + TRIAL_GRAMMAR_LEDGER wave-2 行落地。
- 判读侧（d）面维持冻结时 declare 不可得（基线网格降权）；W1/MASS judged 产物排除源在 generate 时点 declare 不可得=零行如实披露（两判决批池 waiting 实况），后续波次待 judged 落地另 declare。

—— bm-b r359 · {ts_full}（钟读实测）
"""
with open("fleet/inbox/MSG-20260928-0500-bmb-bmc-w2-generate-landed.md", "w",
          encoding="utf-8", newline="\n") as fh:
    fh.write(reply)
print("MSG-0450 archived, reply MSG-0500 written")

# ---- 3) state.json round_no 358 -> 359
st = json.load(open("state.json", encoding="utf-8"))
st["round_no"] = 359
st["note"] = ("r359: T-96 W2 generate slice landed (cmd_generate + selftest "
              "29/29 + pool TRIAL-LABOR-W2-GENERATE waiting RAM flip gate) + "
              "MSG-0450 zero-objection consumed/replied + S6 30/30")
with open("state.json", "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
print("state.json round_no -> 359")

# ---- 4) round report line
line = (
    f"{ts_full} | round 359 bm-b | dept:工程+策略 | "
    f"WM-VERDICT: 绿（red=false@04:40:21 lane healthy；probe 04:40 "
    f"py_low_with_work_cands 合法说明: 池候选全 RAM 门=W2B census 燃批 3-proc 实探存活 "
    f"no-kill 继续烧 + MASS judge x4+TRIAL-LABOR-W1-JUDGE+W2-GENERATE 全 waiting "
    f"RAM≥4GB flip 门 + V2-P1 defer = 合法白名单 r353 裁定延续） | "
    f"did: (1) S0-1 锚定 bm-b；S0 pull fast-forward bm-c r133 链（MSG-0450 零异议回执+"
    f"bm-c resolve 件+daily twins 等 37 件零冲突）；(2) S0.5 双扫 orders 99/99 差集零"
    f"（README.md 非令件剔除口径）+ decisions.md 本机挂载不可达零动作如实 + "
    f"MSG-0450 处理归档（bm-c 双披露独立复核: 零异议零保留 generate 放行）+回执 "
    f"MSG-0500 发出；(3) S1 smoke 25/25；(4) S2 双板 0 open（T-96 续作）；(5) S3 主活="
    f"T-96 W2 generate 切片落地: trial_labor_w2.py cmd_generate（per-slot Sobol 流全局"
    f"轮转 A500/6 槽+B4500/72 槽·四源排除=grammar stop-none 42 行+w1_screen 存活 149 "
    f"实读消费+w1_judge+MASS judged declare 不可得零行如实·T-84s3 去重=指纹+|corr|≥0.999 "
    f"于有效信号面（止损叠加镜像 E1 映射·selftest 与 slice-1 overlay exit_date 交叉验证）·"
    f"D6 max|corr| 披露列 naive 口径·ledger wave-2 行 consume 点落）+ selftest 17→29/29 "
    f"双跑 rc=0（pandas to_numpy 只读视图坑当场修 np.array 拷贝·round-robin 恒等腿根因="
    f"轴 rng 批量交错随 n_draws 变→同尺寸重组对照腿）+ generate 实弹门禁拒发实证"
    f"（RAM 0.42/2.3GB<4 三采样 rc=2 零副作用）+ 池 TRIAL-LABOR-W2-GENERATE 入册"
    f"（waiting·prio 1·lane null·RAM≥4GB flip 门 r354 律·in-runner fail-closed 三门·"
    f"单分片 generate-0of1·shards r301 律）——generate 禁轮内代跑=RAM<4GB 双司纪律+O-2100 "
    f"池律；(6) S4 坑律 1 条入件（pandas to_numpy 只读视图·CODELY {size}B<10KB 线内）；"
    f"(7) S6 30/30 rc=0 82.3s（_r359bmb_s6_driver r353 范式零重写·盘前无新 bar 3 "
    f"bar-gated 合法跳·lhb<30min 节流·8 采集腿 bm-a/bm-c 护栏 no-op·astock fresh·"
    f"fundamental 6h fresh·b_layer 5 门全过·promo 0/22 诚实·aggr/alloc/grid 幂等 no-op·"
    f"sysv1 bm-a 避让·export-09-24·dreport 再生 faces=4·token delta~0）；(8) S7 自愈 3/3"
    f"（pin=2 no-op 核对+watchdog 幂等重注+claw LF 归一装定）+ schtasks 三任务在位"
    f"（IterLoop=本会话在跑） | evidence: selftest 29/29 双跑 rc=0 + generate 门禁实弹 "
    f"rc=2 拒发零副作用 + 池 89 条目 _r359bmb_w2_pool_entry.py + _r359bmb_s6.log 30x "
    f"rc=0 + orders 程序化差集零 + W2B 3-proc psutil 存活 + epoch int 自证 | next: "
    f"(a) W2B finalize 收账窗→RAM 释→generate flip ready→autofill 烧→"
    f"w2_candidates.json+ledger 行落地收账；(b) screen 切片 build（cmd_screen+nulls "
    f"K=200+finalize）→SCREEN 池条目；(c) W1/MASS judge flip 门按条目各自 gate；"
    f"(d) 周一 15:30 T-87 astock 首增量 new-bar 全链（update_daily→live.paper "
    f"REGIME_GUARD v3 enforce→t35v→t24x2→aggr→alloc→grid→export→scorecard→"
    f"daily_report）；(e) CEO 48h 报时钟 09-29 22:45 owner bm-b；(f) 10-01 月首轮三件套"
    f"+REGIME_GUARD v3 日期门 [r359 bm-b]\n")
with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8",
          newline="\n") as fh:
    fh.write(line)
print("round report line appended")

# ---- 5) heartbeat refresh (epoch int + clock_read T-separated, R170/R262)
import psutil

vm = psutil.virtual_memory()
hb_path = "fleet/machines/bm-b.json"
hb = json.load(open(hb_path, encoding="utf-8"))
hb["last_seen"] = ts_full
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = ts_full
hb["current_task"] = ("r359 done: T-96 W2 generate slice (runner+selftest 29/29+pool "
                      "TRIAL-LABOR-W2-GENERATE waiting RAM flip); next r360: W2B "
                      "finalize watch -> generate flip ready; screen slice build")
hb["cpu_cores"] = 16
hb["free_ram_gb"] = round(vm.available / (1 << 30), 1)
hb["total_ram_gb"] = round(vm.total / (1 << 30), 1)
hb["cpu_util_pct"] = round(psutil.cpu_percent(interval=1.0), 1)
hb["round_no"] = 359
hb["loop_round"] = 359
hb["round"] = 359
hb["verdict"] = "healthy"
hb["idle_ram_gb"] = round(vm.available / (1 << 30), 1)
hb["idle_ram_mb"] = int(vm.available / (1 << 20))
hb["free_ram_mb"] = int(vm.available / (1 << 20))
hb["cores"] = 16
hb["cpu_pct"] = hb["cpu_util_pct"]
try:
    import subprocess
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.total,memory.used",
         "--format=csv,noheader,nounits"], capture_output=True, text=True,
        timeout=10).stdout.strip().splitlines()[0]
    tot, used = (int(x.strip()) for x in out.split(","))
    hb["gpu_free_vram_gb"] = round((tot - used) / 1024, 1)
    hb["gpu_free_vram_mb"] = tot - used
    hb["gpu_idle_vram_mb"] = tot - used
    hb["gpu_idle_vram_gb"] = hb["gpu_free_vram_gb"]
except Exception:
    pass
with open(hb_path, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
chk = json.load(open(hb_path, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
assert "T" in chk["clock_read"], "clock_read must be T-separated (R262)"
print(f"heartbeat ok: epoch={chk['heartbeat_epoch_utc']} int, "
      f"ram {chk['free_ram_gb']}GB, orders_ack {len(chk['orders_ack'])} unchanged")
print(f"closeout complete @ {ts_full}")

