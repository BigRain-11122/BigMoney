"""r621 bm-b S7 bookkeeping: report line, heartbeat (epoch int + self-verify), MSG-1543 archive, CODELY append."""
import json, time, subprocess, io, sys, shutil
from datetime import datetime, timezone, timedelta

sys.stdout = io.open("results/_r621bmb_s7_bookkeeping.out", "w", encoding="utf-8")
now = datetime.now(timezone(timedelta(hours=8)))
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# 1) round report line
line = (
 "2026-10-03T15:<MIN>x+08:00 | r621 bm-b (dept:工程/舰队·S0多环集成收敛轮) | "
 "[watermark verdict: 绿 red=false; probe loaded_ok py 75.6% 三NULLS烧录在飞 burning-healthy; audit CLEAN; dualrun ZERO-DRIFT streak 11] | "
 "当前活: FUND 三族 NULLS 烧录在飞（daemon 续烧 ETA ~10-06）+moneyflow IC 参考批认领在飞·本机 N1 depth=0 | "
 "最近实物: ①S0 车队共享树解锁=上轮断头合并三环收敛治愈（环1 对陈旧MERGE_HEAD ab35cd73a 19UU正典解 commit 17fad4ba0→预推爪两拦=陈旧基座警报（删他机9件+池settle 15:16:03→14:54:07回退）→环2 追真tip 61a5b34afc 18UU方向翻转解 commit 4028932bd→环3 bm-c r421 addendum 零冲突合并 3f6430f62 推送落地 ls-remote 自证）②S6 产品面：日报+CEO一页纸再生（ORANGE/50%帽/COOL）+b_layer mask 5222码 gates 全过+market_clock CALL-09-30 ③MSG-1543 处理+澄清回执（修正「bm-b untested」陈旧表述=r620 已测可行） | "
 "下个里程碑: NULLS 烧毕（~10-06）→池翻面 finalize（烧毕后窗≤48h）；EM 车道 GM 裁决候票（窗≤48h） | "
 "本轮做了: S0.5 令扫 151/151 零未回执; S1 smoke 47/47; S6 34/34 rc0; S7 5/5（loop pin=2 no-op+watchdog 幂等+双爪装+attrition CLEAN+state 620→621）; MSG-1543→processed | "
 "验证证据: results/_r621bmb_merge_resolve.py+_r621bmb_merge2_resolve.py 断言全过（双环零丢失+CODELY 3热条目 pit 域件字节验证在案）+S6 34腿 rc=0+推送后 ls-remote origin/main==3f6430f62+guard scan CLEAN | "
 "下轮指针: ①烧录 harvest+池翻面判定②EM 裁决消费③本地未达 origin commit 数=0\n"
).replace("<MIN>", "%02d" % now.minute)
with open("logs/iteration-loop/round_reports.md", "rb") as f:
    f.seek(-600, 2)
    tailb = f.read()
if "r621 bm-b (dept" not in tailb.decode("utf-8", "replace"):
    with open("logs/iteration-loop/round_reports.md", "ab") as f:
        f.write(line.encode("utf-8"))
    print("report line appended")
else:
    print("report line already present (idempotent skip)")

# 2) heartbeat
import psutil
cpu = psutil.cpu_percent(interval=1)
ram = psutil.virtual_memory().available / (1024 ** 3)
gpu_free = None
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"], capture_output=True)
    gpu_free = round(int(r.stdout.decode().strip().split("\n")[0]) / 1024, 2)
except Exception:
    pass
hb = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
hb["last_seen"] = ts
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = ts
hb["round_no"] = 621
hb["round_no_label"] = "round 621 (bm-b)"
hb["current_task"] = ("r621 done: S0 fleet-unblock merge heal (3-ring convergence vs stale/true tips, 37 UU resolved per canon, claw double-catch honored, pushed 3f6430f62) + S6 faces regenerated; "
                      "FUND NULLS trio burns alive (ETA ~10-06); moneyflow option-A GM ruling awaited (bm-b probed viable r620 MSG-151x; bm-c refuted MSG-1543)")
hb["verdict"] = ("round 621: WM=loaded_ok green; smoke 47/47; S6 34/34 rc0 (dualrun streak 11, audit CLEAN burning-healthy); S7 5/5; orders 151/151 zero unacked; MSG-1543 processed+clarified; "
                 "DELIVERABLE: fleet shared-tree unblock (origin/main==3f6430f62) + daily report + CEO LIVE page (ORANGE/50%) + b_layer mask 5222; next: NULLS finish ~10-06 -> pool finalize <=48h; EM lane GM ruling <=48h")
hb["ts"] = ts
hb["updated"] = ts
hb["updated_at"] = ts
hb["cpu_cores"] = psutil.cpu_count(logical=True)
hb["cpu_util_pct"] = cpu
hb["free_ram_gb"] = round(ram, 2)
hb["idle_ram_gb"] = round(ram, 2)
hb["total_ram_gb"] = round(psutil.virtual_memory().total / (1024 ** 3), 2)
if gpu_free is not None:
    hb["gpu_idle_vram_gb"] = gpu_free
    hb["gpu_free_vram_gb"] = gpu_free
    hb["gpu_idle_vram_mb"] = int(gpu_free * 1024)
    hb["gpu_free_vram_mb"] = int(gpu_free * 1024)
    hb["gpu_vram_free"] = gpu_free
with open("fleet/machines/bm-b.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat updated: epoch=%r int-ok cpu=%.1f ram=%.2f gpu=%s" % (chk["heartbeat_epoch_utc"], cpu, ram, gpu_free))

# 3) MSG-1543 -> processed/
src = "fleet/inbox/MSG-2026-10-03-1543-bmc-all-moneyflow-option-a-refuted.md"
import os
dst = "fleet/inbox/processed/" + os.path.basename(src)
if os.path.exists(src):
    shutil.move(src, dst)
    print("MSG-1543 archived -> processed/")
else:
    print("MSG-1543 already archived (idempotent skip)")

# 4) CODELY.md append (one line, S4 memory gate: lesson-focused, no restating)
entry = ("- [2026-10-03 15:<MIN>x r621 bm-b] 多环陈旧tip合并收敛律（S0 push-race 实弹·r619/r620 姊妹面）：断头合并会话死后再入仓=先核 MERGE_HEAD vs ls-remote 真tip——陈旧基座（本窗 ab35cd73a vs 真tip 61a5b34af）直推=双害（删他机新件+池 settle 面 owner_since 回退），预推爪两拦=陈旧面警报器非障碍；正解=爪拦后 fetch 真tip 增量环合（环2/环3 常零冲突）→爪全过才推；snapshot 族方向随环翻（每环两侧 ts 重取证定 take-new），rolling-ledger 族恒 union 零丢失。How to apply：撞「deletion set non-self-owned」+「owner_since backward」双拦=勿 --no-verify 绕行，先查基座新旧。\n").replace("<MIN>", "%02d" % now.minute)
raw = open("CODELY.md", "rb").read()
assert not raw.rstrip(b"\n").endswith(entry.encode("utf-8")), "dup append"
if not raw.endswith(b"\n"):
    raw += b"\n"
open("CODELY.md", "wb").write(raw + entry.encode("utf-8"))
print("CODELY.md entry appended (%d bytes)" % len(entry.encode("utf-8")))
