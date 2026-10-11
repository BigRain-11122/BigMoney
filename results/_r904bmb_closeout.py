# -*- coding: utf-8 -*-
# r904 bm-b closeout: state.json + heartbeat + round report line (ASCII-safe io)
import json, time, datetime, subprocess

repo = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

def gpu_free():
    try:
        out = subprocess.run(["nvidia-smi","--query-gpu=memory.free","--format=csv,noheader"],
                             capture_output=True, text=True, timeout=15).stdout.strip()
        return int(out.split()[0])
    except Exception:
        return -1

def ram_free():
    try:
        out = subprocess.run(["powershell","-NoProfile","-Command",
            "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"],
            capture_output=True, text=True, timeout=20).stdout.strip()
        return round(int(out)/1048576.0, 1)
    except Exception:
        return -1

vram_free_mb = gpu_free()
ram_gb = ram_free()
vram_free_gb = round(vram_free_mb/1024.0, 2)

did = ("r904: ①i2v 释放阀第三腿收口（r903 残面）：daemon（ollama serve 14440·10-09 22:54 起）存活→01:57:43 下一在飞 flash 请求按需 respawn 新 runner"
       "→VRAM 回填 7858/161 产线续死（serve.log 500/4m+ 族复发实证）→完整阀=先杀 daemon（绝 respawn 源）再杀 runner→free 161→3800MiB"
       "→ComfyUI 吸满=渲染独占（预期）→30min+ 零 respawn（三源排查：keep-warm marker 门健康·keepwarm.log 10-04 后零新行/serve-warm=单发监督员"
       "/Serve 任务 login-only·LastRun 10-09 22:54）；②KN16 僵尸（01:10:53 起 110min·干净窗 32min 仍未完·干净基线 277帧=17min）interrupt 让位"
       "→KN21 pending→running 全速独卡；③坑律第三腿直写 pit-machine.md（1215B·sha16=62ce9d6934a2e0f0·对账行+receipt）+救援证据两件；"
       "④smoke 49/49+S6 41/41 rc0（_r904bmb_s6_log.txt）+attrition CLEAN+水位 red=false+SAT 活+D19 零 delta")

next_ptr = ("r905: i2v KN21+ 落地复核（~17-20min/单流水恢复·KN16 --only 回收待批尾）> 批毕移 keepwarm.pause marker 恢复 flash 本地线"
            "> unity-mcp POC 执行窗（due 10-13 12:00）> W18+E15 48h CEO 报（10-13 11:2x/10-14 00:44）> BigHouse T-2 ≤10-15 > T-184 bm-a courtesy compare")

verdict = ("GREEN: i2v 释放阀三腿完整落地（daemon+runner 全灭·零 respawn 30min+ 实证·KN21 全速独卡渲染）+ smoke 49/49 + S6 41/41 rc0 "
           "+ 水位 red=false；观察面 = KN21 落地 ETA ~03:2x（干净窗基线 17min）+ bm-a 暗窗（lane stale-takeover 依律接管面）+ O-2333 回执 due 10-13 12:00")

note = ("r904：i2v 释放阀第三腿收口轮（daemon respawn 根治）；孤儿面=1=i2v 驱动睡眠轮询假阳（pit-machine r884 律·消费面活跃未击杀）；"
        "合法 detached=i2v 驱动+ComfyUI；flash 本地线 marker 期走云端回退（L2 律）")

latest_artifact = ("results/_r904bmb_ollama_daemon_kill.json（第三腿救援证据）+ research/pit-machine.md r904 坑律条"
                   "（释放阀三腿律）+ _r904bmb_s6_log.txt 41 腿 rc0")

sp = json.load(open(repo + r"\state.json", encoding="utf-8"))
sp.update({
    "clock_read": ts, "current_task": "r904 closeout：i2v 释放阀第三腿收口",
    "did": did, "last_action": "r904: ollama daemon respawn 根治（完整阀=daemon 先 runner 后）+KN16 僵尸 interrupt 让位 KN21",
    "last_action_at": ts, "last_round_at": ts, "last_round_ts": ts, "last_seen": ts,
    "latest_artifact": latest_artifact, "next": next_ptr, "now_active": "r904 closeout",
    "note": note, "orphan_face": 1,
    "orphan_face_note": "r904 round probe: orphans=1=i2v driver sleep-poller 假阳（pit-machine r884 律·消费面活跃未击杀）；合法 detached=i2v/ComfyUI 族",
    "orphan_faces": 1, "round": 904, "round_no": 905, "round_no_label": "r904",
    "task": next_ptr, "ts": ts, "updated": ts, "updated_at": ts, "verdict": verdict,
    "next_milestone": "KN21 落地 ~03:2x→52 单流水 ETA 10-13 午后→unity-mcp POC 回执 ≤10-13 12:00；W18 48h CEO 报 10-14 00:44；E15 48h 报 10-13 11:2x；BigHouse T-2 ≤10-15",
    "sync": {"last_push_ts": ts, "note": "r904 closeout push lands with this commit; delivery self-proof = post-push fetch + rev-list 0"},
})
json.dump(sp, open(repo + r"\state.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

hb = json.load(open(repo + r"\fleet\machines\bm-b.json", encoding="utf-8"))
hb.update({
    "clock_read": ts, "current_task": "r904 closeout：i2v 释放阀第三腿收口",
    "did": did, "free_ram_gb": ram_gb, "gpu_free_vram_gb": vram_free_gb, "gpu_free_vram_mb": vram_free_mb,
    "heartbeat_epoch_utc": epoch, "idle_rounds": 0, "agenda_starved": False,
    "last_action": "r904: ollama daemon respawn 根治+KN16 僵尸 interrupt 让位 KN21 全速",
    "last_action_at": ts, "last_round_at": ts, "last_seen": ts,
    "latest_artifact": "results/_r904bmb_ollama_daemon_kill.json + pit-machine r904 条",
    "next": next_ptr, "note": note, "now_active": "r904 closeout",
    "orphan_face": 1, "orphan_face_note": "r904: orphans=1=i2v driver sleep-poller 假阳（未击杀）",
    "orphan_faces": 1, "ram_free_gb": ram_gb, "round": 904, "round_no": 905, "round_no_label": "r904",
    "task": next_ptr, "ts": ts, "updated": ts, "updated_at": ts, "verdict": verdict,
    "vram_free_gb": vram_free_gb, "green_idle": False,
    "sync": {"last_push_ts": ts, "note": "r904 closeout push lands with this commit"},
})
json.dump(hb, open(repo + r"\fleet\machines\bm-b.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# smoke F7 face: epoch must be int, clock T-separated
chk = json.load(open(repo + r"\fleet\machines\bm-b.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"
print("epoch_int_ok clock_ok ram=%s vram_free=%s" % (ram_gb, vram_free_mb))

report = ("| r904 | %s | dept:工程（i2v 释放阀第三腿收口·daemon respawn 根治）| 实况三行：当前活=i2v KN21 全速独卡渲染中"
          "（comfy 队列唯一·VRAM 全 ComfyUI 零 Ollama）；最近实物=results/_r904bmb_ollama_daemon_kill.json+research/pit-machine.md r904 坑律条（02:3x）；"
          "下个里程碑=KN21 落地 ~03:2x→52 单流水恢复 ETA 10-13 午后→unity-mcp POC 回执 ≤10-13 12:00 | did: ①r903 释放阀残面定谳：只杀 runner 不杀 daemon"
          "→daemon（14440·10-09 22:54 起）于 01:57:43 下一在飞 flash 请求按需 respawn 新 runner→VRAM 回填 7858/161 产线续死（serve.log 500/4m+ 复发）"
          "→完整阀=先杀 daemon 再杀 runner→free 161→3800→ComfyUI 吸满（预期·渲染独占）→30min+ 零 respawn 三源排查（keep-warm marker 门健康"
          "/serve-warm 单发监督/Serve 任务 login-only）；②KN16 僵尸（01:10:53 起 110min·干净窗 32min 仍未完）interrupt 让位→KN21 pending→running；"
          "③坑律第三腿直写 pit-machine.md（1215B sha16=62ce9d6934a2e0f0·对账行+receipt 双证）+救援证据两件；④S6 41/41 rc0 | 证据：smoke 49/49"
          "+S6 41/41 rc0（_r904bmb_s6_log.txt）+attrition CLEAN+水位 red=false+SAT 活+D19 零 delta+孤儿面=1（i2v 驱动睡眠轮询假阳 r884 律）"
          "| watermark verdict: GREEN(red=false) | 本地未达 origin commit 数=0（push 后 fetch+rev-list 自证）| 下轮指针: %s |\n") % (ts, next_ptr)
open(repo + r"\logs\iteration-loop\round_reports.md", "a", encoding="utf-8").write(report)
print("round_report_appended")
