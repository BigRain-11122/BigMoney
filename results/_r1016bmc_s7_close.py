# -*- coding: utf-8 -*-
"""r1016 bm-c S7: round ledger line + state increment + heartbeat."""
import json
import time
import datetime
import psutil

now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%dT%H:%M:%S") + now.strftime("%z")[:3] + ":" + now.strftime("%z")[3:]
epoch = int(time.time())

RAM = psutil.virtual_memory()
ram_free_gb = round(RAM.available / (1024 ** 3), 1)
vram_free_gb = 14.61  # idle_trigger 05:55 reading (nvidia-smi face via tool)

verdict = ("green: r1016 = T27 git_claw filename-suffix owner-evidence leg "
           "(selftest 31/31 + realfire PASS both legs; pre-push hook inherited) "
           "+ interrupted-r1016 estate absorbed (XQ wave3 A-batch 29/29 + casting 16/16 "
           "deposit DEPOSITED+remote-verified r1015 receipts) + S0.5 orders diff 0 "
           "(89/89 acked) + smoke 49/49 + S6 light green (dualrun streak 51 / attrition CLEAN / "
           "py_low_board_clear legal idle; audit flag pool_starvation attributed = wave seat "
           "chain at bm-a, MV deathline legal let-up, W242/243 frozen awaiting bm-a engine, "
           "W244 prereg in-flight at bm-a 03:58) + S7 quad green (loop pin=5 / watchdog / "
           "pre-commit+pre-push claws / orphan probe report-only 2)")

# 1) round ledger line (round_reports-bm-c.md)
line = ("| %s | r1016 | T27 git_claw.py 文件名后缀属主证据回退（点夹心 .bm-<id>.ext=blob 零 machine "
        "字段件唯一属主事实源·自面放行/他面拦/无点名 fail-closed 不变·dash 形态不入通道）：selftest 28→31 全 PASS；"
        "实弹复现 r1011 场景=plumbing 临时 commit 双腿（删自面 compute_audit.bm-c.json〔零 machine 字段〕rc0 放行·"
        "删 bm-a face rc1 foreign 拦）；pre-push 钩/daemon 带单源继承 | 证据=results/_r1016bmc_t27_realfire.py 输出 "
        "REALFIRE PASS+state/queue/tech.md T27 done 行+git_claw.py diff | 下轮指针：MV XQ B批12帧候 bm-a 定脸解锁"
        "（A批对审中）·波烧=242/243 bm-a 席位候其引擎·audit pool_starvation 旗归因记录在案 |\n" % ts)
with open("round_reports-bm-c.md", "a", encoding="utf-8") as fh:
    fh.write(line)

# 2) state round increment
with open("state-bm-c.json", encoding="utf-8") as fh:
    st = json.load(fh)
st["round_no"] = 1017
st["last_seen"] = ts
st["verdict"] = verdict
with open("state-bm-c.json", "w", encoding="utf-8") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)

# 3) heartbeat
hb_path = "fleet/machines/bm-c.json"
with open(hb_path, encoding="utf-8") as fh:
    hb = json.load(fh)
hb.update({
    "last_seen": ts,
    "current_task": "idle: r1016 closed (T27 claw leg + estate absorb); awaiting bm-a director face-lock for XQ B-batch",
    "cpu_cores": psutil.cpu_count(),
    "idle_ram_gb": ram_free_gb,
    "gpu_free_vram_gb": vram_free_gb,
    "verdict": "green",
    "idle_rounds": 0,
    "agenda_starved": False,
    "heartbeat_epoch_utc": epoch,
    "clock_read": ts,
    "ts": ts,
})
with open(hb_path, "w", encoding="utf-8") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
assert isinstance(json.load(open(hb_path, encoding="utf-8"))["heartbeat_epoch_utc"], int)
print("state round_no -> 1017; heartbeat epoch=%d int-verified; ram_free=%.1fGB" % (epoch, ram_free_gb))
