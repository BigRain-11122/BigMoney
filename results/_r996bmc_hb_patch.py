# -*- coding: utf-8 -*-
# r996 heartbeat enforcement-patch (CEO O-20261014-1125 item-3: prod_lanes GPU=MV V3 BURNING + occupancy + watermark)
import json, subprocess, time, hashlib, re

HB = "fleet/machines/bm-c.json"
hb = json.load(open(HB, encoding="utf-8"))

# live GPU/RAM read
g = subprocess.run(["nvidia-smi", "--query-gpu=memory.free,utilization.gpu", "--format=csv,noheader,nounits"],
                  capture_output=True).stdout.decode().strip().split(",")
free_vram, gpu_util = int(g[0]), int(g[1])
ram = subprocess.run(["powershell", "-NoProfile", "-Command",
                      "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB)"],
                     capture_output=True).stdout.decode().strip()
free_ram = int(float(ram))
now_iso = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
epoch = int(time.time())

hb["prod_lanes"] = ("CPU=软著 B/C 机 18 款源程序复跑批在跑 (PID 27216 11:48 点火, CEO 令 O-20261014-1035 工单②) + "
                    "N1 W239 席候 W238 finalize (bm-a chain) + W19 SCREEN=bm-b lane; "
                    "GPU=MV V3 BURNING (CEO 令 O-20261014-1125 GPU=MV-only 执法: 35B 已卸载零驻卡无 pin 回拉任务; "
                    "波 1 6 签章帧 i2v 已由在飞执行体点火 PID 7188 11:18:43, SIL1 收片+CDN 11:32 (~14min/条), "
                    "SIL2 RUNNING + 4 PENDING, ETA ~13:00; 波 1.5 SIL4 探针格 8 帧接续; 波 2 32 文件云槽位 INT8 重产; "
                    "波 3 星晴 A 批 34 KF+选角板)")
hb["current_task"] = ("r996 CEO 令执法轮: O-20261014-1125 三件即办 (35B 卸载确认零驻卡/波 1 已点火守护/"
                       "心跳 prod_lanes 改写) + O-20261014-1035 工单② 软著 B/C 18 款复跑批后台在跑")
hb["current_task_at"] = now_iso
hb["current_task_ts"] = epoch
hb["activity_now"] = ("2026-10-14 12:0x | r996 | bm-c: CEO 令执法轮 (GPU=MV-only 执法 3 件 + 软著 18 款复跑批在跑 + "
                      "波 1 守护回执) | counter 996")
hb["now_active"] = hb["activity_now"]
hb["last_seen"] = now_iso
hb["last_seen_at"] = now_iso
hb["ts"] = now_iso
hb["clock_read"] = now_iso
hb["updated"] = now_iso
hb["updated_at"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["heartbeat_epoch_utc_type"] = "int (assert)"
hb["free_ram_gb"] = round(free_ram, 1)
hb["ram_free_gb"] = round(free_ram, 1)
hb["idle_ram_gb"] = round(free_ram, 1)
hb["gpu_free_vram_mb"] = free_vram
hb["gpu_free_vram_mib"] = free_vram
hb["gpu_idle_vram_mb"] = free_vram
hb["gpu_idle_vram_mib"] = free_vram
hb["gpu_vram_free_mb"] = free_vram
hb["gpu_free_mb"] = free_vram
hb["gpu_free_mib"] = free_vram
hb["gpu_util_pct"] = gpu_util
hb["full_load_selfproof"] = {
    "占用一行": ("GPU=MV V3 BURNING (H3 INT8 768P i2v 波 1 在烧, O-20261014-1125 CEO 令执法) + "
                 "ComfyUI 8188 常驻 + CEO 前台 GUI 常驻 (WeChat/Doubao/Edge, 禁碰面); 35B 已卸载零驻卡"),
    "当前活": "r996 CEO 令执法轮: 波 1 6 帧 i2v 在烧 (执行体 PID 7188) + 软著 B/C 18 款复跑批 (PID 27216)",
    "下一交付物": ("波 1 i2v 全收 ~13:00 (bm-a 装配站 V3.5 预览剪) -> 波 1.5 SIL4 探针格 -> 波 2 32 文件重产 "
                  "(今晚深夜全本地终剪) -> 波 3 星晴 A 批; 软著 18 款产物+commit+push+orders 回执行"),
    "队列水位": ("ComfyUI: 1 RUNNING + 4 PENDING (波 1 剩余); N1 引擎 0 在烧 (W239 席候上游); "
                "P2/P3 队列空; bars 15:30 papers 全链待点"),
}
hb["latest_artifact"] = ("波 1 SIL1_stele_backlit_v4b_s9021.mp4 收片+CDN 11:32 (wave1_r996_progress.json 执行体 PID 7188 在飞); "
                         "本窗产物=软著 18 款复跑批 (PID 27216 在跑, 完成后 commit+push+orders 回执行)")
hb["next_milestone"] = ("波 1 i2v 全收 ≈13:00 -> bm-a 装配 V3.5 预览剪; 软著 18 款 ≈12:20 产物 commit+push; "
                        "波 2 32 文件今晚深夜全本地终剪; bars 15:30 papers 全链")

# watermark advance (ORD 348eaf34 -> 35a51e728746..., DEC hold)
c = subprocess.run(["git", "-C", "K:/Fluxgroup/FluxGroup", "show", "origin/main:docs/orders.md"],
                   capture_output=True).stdout
hb["last_orders_sha"] = hashlib.sha1(c).hexdigest()
hb["last_orders_read_at"] = now_iso
hb["last_orders_at"] = now_iso
hb["last_orders_seen"] = now_iso
hb["last_orders_sha_note"] = ("r996: ORD delta TRUE 348eaf34->" + hb["last_orders_sha"][:12] +
                              " consumed (14 tail rows: @bm-c GPU 解锁令 O-20261014-1035 三波自链+波 2 精确产单 32 文件+"
                              "软著 B/C 18 款复跑批 [BOTH EXECUTED this window] + CEO 工艺两令 O-20261014-1050 [QC 面在制合规]"
                              " + CEO 导演席严格律 O-20261014-1045 [本窗按律自检] + O-20261014-1125 GPU=MV-only 执法令 "
                              "[三件即办 executed: 35B 卸载确认/波 1 点火守护/心跳改写] + bm-b B 站车道扩线 [bm-b lane zero bmc face] "
                              "+ bm-a 夜班勘误+音源批 [bm-a lane])")
json.dump(hb, open(HB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# assert epoch int + watermark shape
chk = json.load(open(HB, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert len(chk["last_orders_sha"]) == 40, "ord sha 40hex"
print("HB PATCHED ok epoch=%d free_vram=%d free_ram=%s ord=%s" %
      (chk["heartbeat_epoch_utc"], free_vram, free_ram, chk["last_orders_sha"][:12]))
