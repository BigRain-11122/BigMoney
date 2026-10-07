# -*- coding: utf-8 -*-
"""r849 bm-a closeout writer: CODELY pit append + state bump + heartbeat
+ round report line. Multi-writer files -> python fresh-read-modify-write
(2026-10-06 pit law: no replace-tool appends on shared ledgers)."""
import io
import json
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---- fresh clock + machine metrics ----
now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
now_int = int(time.time())
free_gb = round(sum(int(l.split()[1]) for l in subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     "Get-CimInstance Win32_OperatingSystem | Select-Object -ExpandProperty FreePhysicalMemory"],
    capture_output=True, text=True).stdout.split()[:1]) / 1048576.0, 1) if False else None
_r = subprocess.run(["powershell", "-NoProfile", "-Command",
                     "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)"],
                    capture_output=True, text=True)
free_gb = float(_r.stdout.strip())
_g = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                     "--format=csv,noheader,nounits"], capture_output=True, text=True)
vram_free_mb = int(_g.stdout.strip().splitlines()[0])
_p = subprocess.run(["powershell", "-NoProfile", "-Command",
                     "Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average | Select-Object -ExpandProperty Average"],
                    capture_output=True, text=True)
cpu_pct = float(_p.stdout.strip())

# ---- 1. CODELY.md pit append (multi-writer file, python fresh write) ----
PIT = ("- [2026-10-07 23:4x r849 bm-a] **外科推送双坑：PS 重定向 commit -F 消息 NUL 字节炸 + git push 缺 repo 参数 sha 被当主机名（同窗实弹·均当场治愈零损失）**："
       "①PS 宿主 `git log --format=%B > msg.txt` 重定向默认 UTF-16LE 带 NUL 字节——git commit-tree -F 拒收（\"a NUL byte in commit log message not allowed\"）；"
       "正法=python subprocess 捕获 git stdout 后以 UTF-8 显式落盘再 -F 消费。"
       "②`git push \"<sha>:main\"` 缺 repository 位置参数=git 把 refspec 整串当远端名→\"ssh: Could not resolve hostname <sha>\" fatal（非竞态假象）；"
       "正法=永远写全 `git push origin <sha>:main`。How to apply：外科 commit-tree 推送窗模板必含三件——python 落消息件、显式 origin 参数、失败先读完整 stderr 再定性。\n")
c = io.open("CODELY.md", "r", encoding="utf-8", newline="").read()
assert "r849 bm-a] **外科推送双坑" not in c, "pit already present"
if not c.endswith("\n"):
    c += "\n"
c += PIT
io.open("CODELY.md", "w", encoding="utf-8", newline="").write(c)
print("CODELY.md pit appended, bytes:", len(c.encode("utf-8")))

# ---- 2. state-bm-a.json bump ----
st = json.load(io.open("state-bm-a.json", encoding="utf-8"))
st["round_no"] = 849
st["last_round"] = "r849"
st["last_round_at"] = now_iso
st["last_round_ts"] = now_iso
st["heartbeat_epoch_utc"] = now_int
st["last_heartbeat_epoch_utc"] = now_int
st["last_action"] = ("W179 prereg+FREEZE landed on origin (prereg 6f14c35d5 surgical push behind bm-c r706/707 race; "
                     "freeze ef540bf8f five-face S79f 173 pairs; tick ignition 2/12 shards growing)")
st["current_task"] = ("W179 burn in flight (engine queue 12 shards); finalize next round "
                      "(SS5 four pred keys + §7/§8 backfill); 10-08 market-reopen data chain re-arm")
st["did"] = ("r849: W179 supply_gap canonical response full chain: S0 fetch behind bm-c r706/707 wave + "
             "S0.5 double-sweep zero unacked + DEC hash unchanged (group-tree fallback path) + "
             "smoke 48/48 + S3 engine alive (queue0 -> supply): W179 prereg buildgen r845-bloodline "
             "(50 TOK pairs DRY 50/50 + stale-sweep CLEAN + banned gate ADMIT 0) -> surgical commit-tree "
             "push behind race (r523 law; PS NUL-byte redirect + sha-as-repo push-arg pits healed, CODELY appended) "
             "-> FREEZE buildgen S79f (173 pair old-sides dump-verified, DRY-RUN PASS then live, "
             "pf 9/9 + n1 selftest green incl W179 mat leg 169th wave/95th owned/39th staircase E36) "
             "-> freeze push ef540bf8f -> tick ignition product growth 2/12 shards; "
             "S6 38 legs rc0 (dualrun ZERO-DRIFT streak 51; golden-week no-op family honest; "
             "moneyflow+ah detached spawn); S7 quartet green (pin=8 no-op, watchdog registered, "
             "claws parity, attrition CLEAN); idle_trigger --worked; orphan face=1 (read-only)")
io.open("state-bm-a.json", "w", encoding="utf-8", newline="\n").write(
    json.dumps(st, ensure_ascii=False, indent=1))
print("state round_no -> 849")

# ---- 3. heartbeat fleet/machines/bm-a.json ----
hb = json.load(io.open("fleet/machines/bm-a.json", encoding="utf-8"))
hb["clock_read"] = now_iso
hb["ts"] = now_iso
hb["last_seen"] = now_iso
hb["heartbeat_epoch_utc"] = now_int
hb["last_round"] = "r849"
hb["round"] = 849
hb["round_no"] = 849
hb["loop_round"] = "r849"
hb["cpu_pct"] = cpu_pct
hb["cpu_util_pct"] = cpu_pct
hb["cpu_load_pct"] = cpu_pct
hb["free_ram_gb"] = free_gb
hb["ram_free_gb"] = free_gb
hb["idle_ram_gb"] = free_gb
hb["gpu_free_vram_gb"] = round(vram_free_mb / 1024.0, 1)
hb["gpu_idle_vram_gb"] = round(vram_free_mb / 1024.0, 1)
hb["gpu_free_vram_mb"] = vram_free_mb
hb["gpu_idle_vram_mb"] = vram_free_mb
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["last_action"] = ("W179 prereg (6f14c35d5 surgical push) + FREEZE (ef540bf8f, five-face S79f) "
                     "landed on origin; tick ignition 2/12 shards growing")
hb["last_run"] = ("smoke 48/48; pf 9/9 + n1 selftest green (W179 mat leg); S6 38 legs rc0; "
                  "quartet green; attrition CLEAN; dualrun streak 51")
hb["now_active"] = ("W179 burn in flight (engine queue, 12 shards); finalize next round; "
                    "10-08 market-reopen data chain re-arm queued")
hb["latest_artifact"] = ("scripts/perpetual_faces_n1.py (W179 row) + "
                         "results/perpetual_faces W179 chain receipts _r849bma_w179_*")
hb["next_milestone"] = ("W179 finalize next round (ledger 799,705 proj / K 391,720 proj / "
                        "SS5 four pred keys + §7/§8 backfill, window <=24h); 10-08 reopen data chain re-arm")
hb["current"] = "W179 burning (2/12+ at closeout); finalize next round"
hb["current_task"] = ("W179 burn in flight; finalize next round; 10-08 reopen re-arm; "
                      "CEO O-2215/2230/2245 execution files (due 10-10/10-12/10-14)")
hb["task"] = "W179 burn + finalize next round; 10-08 reopen data chain re-arm"
hb["verdict"] = ("green-idle=false (W179 burn active); product chain landed this round "
                 "(prereg+freeze+ignite)")
hb["last_artifact"] = ("scripts/perpetual_faces_n1.py W179 row @23:4x + "
                       "results/p2cal_ext/n1_w179/ shards")
json.dump(hb, io.open("fleet/machines/bm-a.json", "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)
chk = json.load(io.open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
print("heartbeat written, epoch int OK, free_ram", free_gb, "vram_free_mb", vram_free_mb)

# ---- 4. round report line ----
LINE = (now_iso + " | r849 bm-a (dept:research) | watermark verdict: green (red=false lane=healthy; "
        "supply_gap canonical response: W179 prereg 6f14c35d5 surgical-push behind bm-c r706/707 race + "
        "FREEZE ef540bf8f five-face S79f 173-pair dump-verified + dual selftest green incl W179 mat leg "
        "(169th wave / 95th bm-a owned / staircase 39th E36 / A 408_604..410_603 / B 410_604..410_803 / "
        "anchor W178 finalize r846 head 797,505 K 389,520 line 1.1849) + tick ignition product growth 2/12 "
        "shards | S6 38 legs rc0 (dualrun ZERO-DRIFT streak 51, golden-week no-op family honest, "
        "moneyflow+ah detached spawn, heat/lhb/futures/repo/options/sina_mf/ths/fund_stmt all no-op cutoff "
        "09-30); S7 quartet green (loop pin=8 no-op, watchdog registered, claws parity True, attrition "
        "CLEAN); orphan face=1 (read-only round-zero probe); idle_trigger --worked; local not-at-origin=0 "
        "| next: W179 burn 12/12 -> finalize next round (SS5 four pred keys, ledger proj 799,705 / K proj "
        "391,720, sec7/8 backfill); 10-08 market-reopen data chain re-arm\n")
rr = io.open("logs/iteration-loop/round_reports-bm-a.md", "r", encoding="utf-8", newline="").read()
if not rr.endswith("\n"):
    rr += "\n"
rr += LINE
io.open("logs/iteration-loop/round_reports-bm-a.md", "w", encoding="utf-8", newline="").write(rr)
print("round report line appended")
print("DONE closeout writes at", now_iso)
