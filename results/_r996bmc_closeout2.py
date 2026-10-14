# -*- coding: utf-8 -*-
# r996 continuation closeout (dead-session estate absorb + GPU hang recovery window)
# - heartbeat: prod_lanes recovery facts + bm-a 35B probe receipt + clocks/epoch
# - state: round 996->997, absorb note, ORD/DEC watermarks (live-derived, zero literals)
# - round report row: logs/iteration-loop/round_reports-bm-c.md
import json, subprocess, time, hashlib, io, os

GR = r"K:\Fluxgroup\FluxGroup"
NOW = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
EPOCH = int(time.time())

def gshow(path):
    r = subprocess.run(["git", "-C", GR, "show", "origin/main:" + path],
                       capture_output=True)
    return r.stdout  # raw bytes

def ram_free():
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB)"],
                       capture_output=True)
    return int(float(r.stdout.decode().strip()))

def vram_free():
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True)
    return int(r.stdout.decode().strip().split(",")[0])

ORD_B = gshow("docs/orders.md")
ORD_SHA1 = hashlib.sha1(ORD_B).hexdigest()
DEC_B = gshow("docs/decisions.md")
DEC_SHA256 = hashlib.sha256(DEC_B).hexdigest()
RAM = ram_free()
VRAM = vram_free()

# ---------- heartbeat ----------
HB = "fleet/machines/bm-c.json"
hb = json.load(io.open(HB, encoding="utf-8"))
hb["prod_lanes"] = ("CPU=软著 B/C 18 款复跑批 DONE 12:25 (C机8款全产+B机10款勘正待 bm-b 接力, 回执组仓 fc1b936 + orders 12:2x 行) "
                    "+ N1 W239 席候 W238 finalize (bm-a chain) + W19 SCREEN=bm-b lane; "
                    "GPU=MV V3 BURNING (O-20261014-1125 MV-only 执法窗: 12:0x 服务器 hang 中途卡死 [SING1 燃至 258s 无进展] → "
                    "根因链=ComfyUI 内核卡死 ghost + KeepWarm 自愈回拉 qwen3.8:27b 驻卡 13G [CEO 令违例拦截] → "
                    "ollama stop + 双 pin 任务 disable [MiniGameOllamaKeepWarm/Serve] + EmptyWorkingSet 收 11.7G 物理内存 + "
                    "raw TerminateProcess 击杀 ghost → 端口 8188 释放 VRAM 13343MiB → 服务器重启 PID 29432 20s ALIVE → "
                    "波 1 runner 续跑 PID 60856 12:56:46 [SIL1/SIL2/SIL3 SKIP+CDN 在册, SING1/SING2/SING3b 重提交在烧] "
                    "→ 波 1.5 SIL4 探针 8 帧接续; 波 2 32 文件云槽位重产; 波 3 星晴 A 批)")
hb["current_task"] = ("r996 续体收口: 死窗 estate 吸收 (波 1 点火+软著批+S6 light+组仓回执 fc1b936 均死窗已落) + "
                      "GPU hang 三步恢复 (pin 任务禁用/ghost 击杀/服务器重启) + 波 1 续跑守护 + "
                      "O-20261014-1230 @bm-c 跨机探测执行 {status:ok}")
hb["current_task_at"] = NOW
hb["current_task_ts"] = EPOCH
hb["activity_now"] = ("2026-10-14 13:0x | r996 | bm-c: GPU hang 恢复+波 1 续跑 (3/6 SAVED+CDN, SING1/SING2/SING3b 在烧) | "
                      "counter 996->997")
hb["now_active"] = hb["activity_now"]
for k in ("last_seen", "last_seen_at", "ts", "clock_read", "updated", "updated_at"):
    hb[k] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["heartbeat_epoch_utc_type"] = "int (assert)"
hb["free_ram_gb"] = round(RAM, 1)
hb["idle_ram_gb"] = round(RAM, 1)
hb["ram_free_gb"] = round(RAM, 1)
hb["gpu_free_vram_mib"] = VRAM
hb["gpu_free_vram_mb"] = VRAM
hb["did"] = ("r996 续体: (1) 死窗 estate 吸收——波 1 点火 11:18 (SIL1/SIL2/SIL3 SAVED+CDN 11:32-11:55)+软著批 PID 27216 "
             "12:25 正常完成 (C机8款源程序全产 G02 7425/G03 8376/G06 6260/G09Y 3666/G10 5252/G12 10347/G17 8439/G18 12007 行, "
             "B机10款源码不在 K 机勘正待 bm-b)+组仓回执 fc1b936 12:26 已推+S6 light 11:50 全绿——死窗组仓面已全落, bigmoney 面本窗收编; "
             "(2) GPU hang 恢复: 11:59 服务器 SING1 燃至 258s 卡死 (API timeout/0% util) → Stop-Process×2+taskkill 均 'no running instance' "
             "ghost (端口 8188+11.7G RAM 内核滞留) → 发现 KeepWarm 自愈回拉 qwen3.8:27b 13G 驻卡 (CEO O-1125 MV-only 违例) → "
             "ollama stop+双 pin schtasks disable+EmptyWorkingSet(psapi) 收 11.7G 物理+raw TerminateProcess 击杀 → ghost GONE 端口释放 "
             "VRAM 13343MiB → 服务器 PID 29432 重启 20s ALIVE → 波 1 runner PID 60856 12:56:46 续跑 (3 SKIP+3 重提交, SING1 在烧); "
             "(3) O-20261014-1230 @bm-c 跨机探测执行: curl http://100.110.185.62:8090/health = {\"status\":\"ok\"} bm-a 35B 可达; "
             "(4) S0.5 新行消费: O-20261014-1210 总调度代理席 [委员会面 zero bm-c 执行]+O-20261014-1235 科学巡视 v2 [协议面 ack]+"
             "O-20261014-1230 bm-a 35B [他机面]+@bm-c 探测腿 [本窗执行]——水位双推进 ORD/DEC")
hb["verdict"] = ("green: r996 续体收口——死窗 CEO 令执法 estate 全吸收 (波 1 三镜 SAVED+CDN/软著 C机 8 款全产 fc1b936) + "
                 "GPU hang 三步恢复 (ghost 击杀+服务器重启+波 1 续跑在飞) + @bm-c 探测腿 ok——smoke 49/49 [死窗] + S6 light 绿 [死窗] + 本窗 S7 quad")
io.open(HB, "w", encoding="utf-8").write(json.dumps(hb, ensure_ascii=False, indent=1))
json.loads(io.open(HB, encoding="utf-8").read())
assert isinstance(hb["heartbeat_epoch_utc"], int)

# ---------- state ----------
ST = "state-bm-c.json"
st = json.load(io.open(ST, encoding="utf-8"))
st["round_no"] = 997
st["round_no_label"] = "r996"
st["last_round"] = "r996"
st["last_round_at"] = NOW
st["last_seen"] = NOW
st["clock_read"] = NOW
st["ts"] = NOW
st["last_orders_sha"] = ORD_SHA1
st["last_orders_sha_method"] = ("content-bytes sha1 of git show origin/main:docs/orders.md (r977 pinned probe method; "
                                "r996 consumed through 12:3x rows incl O-20261014-1230 @bm-c probe leg)")
st["last_decisions_sha"] = DEC_SHA256
st["last_decisions_sha_method"] = "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; pinned)"
st["r996_absorb_note"] = ("r996 absorb note: prior session (labeled r996) executed the CEO GPU-unlock enforcement round: "
                          "wave-1 V3 i2v ignition 11:18 (SIL1/SIL2/SIL3 SAVED+CDN by 11:55) + 软著 B/C 18 款复跑批 PID 27216 "
                          "(completed 12:25, C机8款 full + B机10款 honest-skip) + S6 light 11:50 + heartbeat patch + "
                          "group-repo receipt fc1b936 12:26 pushed + orders 11:5x/12:2x rows landed, then died pre-bigmoney-closeout "
                          "AND its wave-1 chain hit a server hang at 11:59 (SING1 stuck at 258s, ComfyUI kernel-deadlock ghost) -- "
                          "this continuation absorbed the estate, executed the three-step GPU recovery (ollama pin-task disable + "
                          "EmptyWorkingSet + raw TerminateProcess), rebooted the server (PID 29432) and resumed the wave-1 runner "
                          "(PID 60856 12:56:46, 3 SKIP + SING1/SING2/SING3b resubmitted); counter 996->997 so next session = r997; "
                          "zero double-count: group-repo receipts/orders rows were handled by the dead session itself (fc1b936)")
st["r996_closeout_note"] = ("r996: continuation-absorb + GPU hang recovery window; products: wave-1 3/6 SAVED+CDN + resume in-flight, "
                            "软著 C机 8 款源程序 (fc1b936), O-20261014-1230 probe receipt {status:ok}; S6 light [dead-window 11:50] + "
                            "S7 quad this window")
st["did"] = hb["did"]
st["verdict"] = hb["verdict"]
st["current_task"] = hb["current_task"]
st["current_task_at"] = NOW
st["activity_now"] = hb["activity_now"]
st["last_round_summary"] = ("r996: 死窗 estate 吸收 + GPU hang 恢复 (ghost 击杀/服务器重启/波 1 续跑) + 软著 fc1b936 收编 + "
                            "@bm-c 探测 ok; counter 996->997")
st["next_pointer"] = ("r997: (1) 波 1 收片守护 (SING1/SING2/SING3b ETA ~13:10/13:24/13:38) → 收片即 CDN+回执; "
                      "(2) 波 1.5 SIL4 探针格 8 帧 (runner 自链); (3) 波 2 云槽位 32 文件 INT8 重产点火 (波 1.5 毕接续); "
                      "(4) 15:30 bars → papers 全链; (5) W238 finalize watch → W239 freeze-prep 同窗; (6) MF 面板复检; "
                      "(7) bm-b 软著 B机 10 款接力催办")
st["latest_artifact"] = ("r996: 波 1 三镜 SAVED+CDN (bmc/i2v/SIL1_stele_backlit_v4b_s9021.mp4 等 3 件 12:0x 前) + "
                        "软著 C机 8 款源程序 (fc1b936 12:26) + SING1/SING2/SING3b 在烧 12:56 续")
st["next_milestone"] = "13:10-13:40 波 1 收片 → 波 2 点火; 15:30 bars papers 链; W238 finalize → W239 同窗"
io.open(ST, "w", encoding="utf-8").write(json.dumps(st, ensure_ascii=False, indent=1))
json.loads(io.open(ST, encoding="utf-8").read())

# ---------- round report ----------
RP = "logs/iteration-loop/round_reports-bm-c.md"
row = ("%s | r996 | bm-c: 死窗 estate 吸收+GPU hang 恢复收口 (波1 3/6 SAVED+CDN · ghost 三步击杀+服务器重启 PID 29432+runner 续跑 PID 60856 12:56 · "
       "KeepWarm 回拉 qwen3.8:27b 拦截+双 pin 任务 disable · 软著 C机8款全产 fc1b936 · O-20261014-1230 探测 {status:ok} · S6 light [死窗 11:50 绿] · "
       "孤儿面=4 [轮首探针零杀]) | 验证: wave1_r996_progress.json 3 SAVED+CDN 三链+runner log SING1 running · 软著 _gen_r996.out.log 全绿 Done ×32 · "
       "fc1b936 origin 在册 · probe exit=0 | 下轮: 波 1 收片+波 1.5/2 自链守护 · bars 15:30 papers 链 · W239 候 W238\n") % NOW
io.open(RP, "a", encoding="utf-8").write(row)
print("CLOSEOUT OK | RAM=%.1fG VRAM=%dMiB | ORD %s | DEC %s..%s" % (RAM, VRAM, ORD_SHA1[:12], DEC_SHA256[:8], DEC_SHA256[-6:]))
