# -*- coding: utf-8 -*-
"""r819 bm-a adoption-closeout S7 writer: heartbeat + state + round report line.
Fresh read-modify-write per multi-writer law (python single-file, no replace-tool)."""
import json, time, io, sys, subprocess, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
now = datetime.datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S") + ("+%02d:00" % (now.utcoffset().total_seconds() // 3600))
epoch = int(time.time())

# fresh machine probe (single source: existing heartbeat conventions)
cpu = subprocess.run(["powershell", "-NoProfile", "-Command",
    "(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average"],
    capture_output=True, text=True).stdout.strip()
ram = subprocess.run(["powershell", "-NoProfile", "-Command",
    "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)"],
    capture_output=True, text=True).stdout.strip()
gpu = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
    capture_output=True, text=True).stdout.strip().splitlines()[0]

HB = r"fleet\machines\bm-a.json"
hb = json.load(open(HB, encoding="utf-8"))
hb["last_heartbeat_epoch_utc"] = hb["heartbeat_epoch_utc"]
hb["heartbeat_epoch_utc"] = epoch
assert isinstance(hb["heartbeat_epoch_utc"], int) and isinstance(hb["last_heartbeat_epoch_utc"], int)
hb["clock_read"] = iso
hb["ts"] = iso
hb["last_seen"] = now.strftime("%Y-%m-%d %H:%M:%S")
hb["cpu_pct"] = float(cpu); hb["cpu_util_pct"] = float(cpu); hb["cpu_load_pct"] = float(cpu)
hb["free_ram_gb"] = float(ram); hb["ram_free_gb"] = float(ram); hb["idle_ram_gb"] = float(ram)
gb = round(int(gpu) / 1024, 1)
for k in ("gpu0_free_vram_gb", "gpu_free_vram_gb", "gpu_idle_vram_gb", "idle_gpu_vram_gb"):
    hb[k] = gb
for k, v in (("gpu_free_vram_mb", int(gpu)), ("gpu_free_vram_mib", round(int(gpu) * 0.976)),
             ("gpu_idle_vram_mb", int(gpu)), ("gpu_idle_vram_mib", round(int(gpu) * 0.976))):
    hb[k] = v
hb["last_round"] = 818
hb["round"] = 819
hb["round_no"] = 819
hb["loop_round"] = 819
hb["last_action"] = "r819: W172 full-lifecycle closeout (adoption after 25min-wrapper behead; finalize ledger 783,812 EXACT)"
hb["task"] = "r820: W173 seat chain (post-W172 universe re-derive-MANDATORY per W172 prereg sec8)"
hb["current"] = "r820: W173 seat chain (probe -> seat MSG -> band gate)"
hb["current_task"] = "r819 W172 adoption closeout landed (finalize+sec7/8+S6); next=W173 seat chain"
hb["now_active"] = ("perpetual N1 line W1..W172 closed (ledger 783,812, K 376,320, zero in-flight seats); "
                    "W173 next line (re-derive-MANDATORY on post-W172 universe)")
hb["latest_artifact"] = ("results/perpetual_faces/n1_w172_results.json + research/PERPETUAL_N1_W172_PREREG.md sec7/sec8 "
                         "@" + iso)
hb["next_milestone"] = ("W173 seat chain (window<=48h) + 10-08 reopen data-chain re-arm; "
                        "D-06 CODELY main window 10-09 00:00 (met ~29.7KB, maintain)")
hb["verdict"] = ("green: smoke 48/48; W172 finalize one-pass rc0 ledger 783,812 EXACT proj hit / K 376,320; "
                 "sec5 four keys machine-judged ALL PASS; S6 37/37 rc0; watermark red=false; satengine alive queue0")
json.dump(hb, open(HB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(HB, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"
print("heartbeat updated:", chk["heartbeat_epoch_utc"], chk["clock_read"], "cpu", chk["cpu_pct"], "ram", chk["free_ram_gb"], "gpu", gb)

ST = r"state-bm-a.json"
st = json.load(open(ST, encoding="utf-8"))
st["round_no"] = 819
st["round"] = 819
st["last_round"] = 818
st["loop_round"] = 819
st["did"] = ("r819 adoption closeout: dead main window froze W172 (commit 59fde9319 10:50:07) + tick-ignited + "
             "beheaded by 25min wrapper at 10:53:02 pre-S7 (r799 precedent); this window: burn 12/12 landed "
             "(10:50:18->11:00:17) + finalize one-pass rc0 (ledger 781,612+2,200=783,812 EXACT / K 376,320 / "
             "skill_line 1.1843->1.1842) + sec7/sec8 mechanical backfill + seat MSG self-ack archived + S6 37/37 rc0 rerun")
st["current_task"] = "W173 seat chain next window (post-W172 universe re-derive-MANDATORY; proj A 395_204..397_203 / B 395_404..395_603)"
st["last_action"] = "r819 W172 adoption closeout (finalize ledger 783,812 / K 376,320 EXACT)"
st["next"] = ("W173 seat chain (probe -> seat MSG -> band gate; staircase 33rd + own-A mutual-exclusion leg2 "
              "anticipated per W172 prereg sec8; then freeze->ignite->finalize; proj ledger 786,012 / K 378,520 naive)")
st["heartbeat_epoch_utc"] = epoch
st["last_heartbeat_epoch_utc"] = hb["last_heartbeat_epoch_utc"]
st["last_round_at"] = iso
st["last_round_ts"] = iso
st["last_seen"] = iso
st["last_run"] = iso
st["updated"] = iso
st["ts"] = iso
st["clock_read"] = iso
st["latest_artifact"] = hb["latest_artifact"]
st["verify"] = ("smoke 48/48; finalize ledger EXACT projection identity; results keys machine-read zero-transcribe (r587); "
                "S6 37/37 rc0; attrition CLEAN; orders zero-unack dual-sweep; D-19 dual-hash match zero action")
json.dump(st, open(ST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state bumped: round_no", json.load(open(ST, encoding="utf-8"))["round_no"])

RPT = r"logs\iteration-loop\round_reports-bm-a.md"
line = (
    "2026-10-07T11:1x+08:00 | r819 bm-a \u63a5\u7ba1\u6536\u53e3\u00b7\u4e3b\u4f53\u7a97 25min wrapper \u65a9\u9996\u6536\u517b (dept:\u7814\u7a76+\u5de5\u7a0b) | "
    "watermark verdict: \u7eff (red=false; probe insufficient_history \u7a97\u9996\u6837\u672c\u5982\u5b9e\u00b7\u677f\u5168\u95ed\u73af+bandit \u7a9f+\u5f15\u64ce idle queue0=W172 12/12 \u70e7\u6bd5=\u5408\u6cd5 idle \u767d\u540d\u5355\u9762) | "
    "\u5f53\u524d\u6d3b: W172 \u5168\u751f\u547d\u5468\u671f\u6536\u53e3\u2014\u2014\u4e3b\u4f53\u7a97\u51bb\u7ed3 commit 59fde9319 10:50:07+tick \u81ea\u71c3\u70b9\u706b\u540e\u88ab 25min wrapper \u65a9\u9996\u4e8e S7 \u524d\uff0810:53:02\u00b7\u96f6 closeout\u00b7r799 \u6536\u517b\u5148\u4f8b\u540c\u5f8b\uff09\uff1b\u672c\u63a5\u7ba1\u7a97\uff1a\u70e7\u5f55 12/12 \u843d\u5730\uff0810:50:18\u219211:00:17\uff09\u2192 finalize one-pass rc0 \u2192 \u00a77/\u00a78 \u673a\u68b0\u56de\u586b \u2192 \u5e2d\u4f4d MSG self-ack \u6536\u6863 | "
    "\u6700\u8fd1\u5b9e\u7269: results/perpetual_faces/n1_w172_results.json + research/PERPETUAL_N1_W172_PREREG.md \u00a77/\u00a78 @2026-10-07T11:0x (ledger 781,612+2,200=783,812 \u6070=\u00a75 \u6295\u5f71\u6052\u7b49/K 376,320 EXACT/skill_line_v2 1.1843\u21921.1842 \u0394-0.0001/se_mu \u6536\u7a84\u94fe 0.000401\u21920.000400) | "
    "\u4e0b\u4e2a\u91cc\u7a0b\u7891: W173 \u5e2d\u4f4d\u94fe\uff08post-W172 \u5b87\u5b99 re-derive \u5f3a\u5236\u00b7\u9636\u68af\u7b2c\u4e09\u5341\u4e09\u4f8b+own-A \u4e92 斥 leg2 \u9884\u62ab\u9732\uff09+10-08 \u590d\u5e02\u6570\u636e\u94fe re-arm\u00b7\u7a97\u226448h | "
    "did: S0 \u8eab\u4efd\u951a bm-a+fetch behind 2\uff08bm-c r670 \u4e24\u4ef6\u00b7\u96f6\u51b2\u7a81\u57df\uff09+\u63a5\u7ba1\u5224\u5b9a\uff08round.lock pid=23804 \u672c\u7a97\u6301\u6709\u00b7\u4e3b\u4f53\u7a97\u4ea7\u7269 mtime 10:52-53 \u505c\u66f4+heartbeat 10:16 \u505c\u66f4=\u65a9\u9996\u5b9e\u8bc1\uff09\uff1bS0.5 \u4ee4\u5dee\u96c6\u96f6\u672a\u56de\u6267+D-19 \u53cc hash \u6052\u7b49\u96f6\u52a8\u4f5c\uff08dec 635c3024/ord e9fa5da4\uff09+inbox 2 MSG \u6536\u6863\uff08W172 seat self-ack+bm-b \u80fd\u529b\u76d8\u70b9\u56de\u6267 ALL \u77e5\u6089\uff09\uff1bS1 smoke 48/48\uff1bS3 \u4e3b\u7ebf=W172 finalize\uff08status 12/12 present\u2192perpetual_faces_n1.py finalize --wave 172 rc0\uff09+\u00a77/\u00a78 \u56de\u586b\uff08_r819bma_w172_sec78_backfill.py \u5168 assertion \u7535\u6c60 PASS\u00b7CRLF \u4fdd\u5f8b\u00b7\u5360\u4f4d\u96f6\u6b8b\u7559+\u9632\u5f62\u7a97\u626b\u63cf CLEAN\uff09\uff1bS6 37/37 rc0 \u5168\u7eff\u91cd\u8dd1\uff08\u4e3b\u4f53\u7a97\u4e2d\u65ad\u817f\u8bda\u5b9e\u8865\u8dd1\u00b7dualrun ZERO-DRIFT streak 51\u00b7golden-week no-op \u65cf\u5982\u5b9e\u00b7QA 5-item \u9762\u817f 4/5=\u672c\u7a97 S6 \u5b9e\u63641/3 \u56fe\u8868\u817f=bm-b \u8f66\u9053\u4eca\u65e5 r803 pack \u5728\u518c\u00b7bm-a env \u65e0 matplotlib \u5982\u5b9e\u6ce8\uff09\uff1bS7 \u56db\u4ef6\u5957\uff08loop pin=8 no-op+watchdog \u91cd\u6ce8\u518c+\u53cc\u722a CR \u5f52\u4e00 match\uff09+state 818\u2192819 \u9012\u8fdb+\u53cc\u6c34\u4f4d\u952e\u590d\u6838 | "
    "verify: finalize ledger EXACT \u6295\u5f71\u6052\u7b49\uff08783,812=783,812\uff09+results \u952e\u673a\u8bfb\u96f6\u8f6c\u5199\uff08r587\uff09+\u00a75 \u56db\u9884\u952e\u673a\u8bc1\u5168\u8fc7\uff08d1=0.0028/d2=-0.0051%/d3=-0.0181/d4=-0.0001\uff09+smoke 48/48+S6 37/37+attrition CLEAN | "
    "\u8ba1\u5206: 2\uff08\u80fd\u8dd1/\u80fd\u770b\u5b9e\u7269=W172 finalize \u5408\u5e76\u4ef6 n1_w172_results.json+prereg \u00a77/\u00a78 \u56de\u586b\u2014\u2014\u5f15\u64ce\u6cd5\u4f9b\u7ed9\u7ebf\u5b9e\u7269\u589e\u91cf\uff09 | "
    "\u627f\u63a5\u5224\u5b9a: \u672c\u6279\u96f6\u65b0\u65b9\u6cd5\u96f6\u65b0\u5b9d\u85cf\uff08nulls-deepening \u4f8b\u6ce2\u00b7\u8bbe\u8ba1 verbatim \u590d\u7528\u00b7r799 \u6536\u517b\u5148\u4f8b\u590d\u7528\u975e\u65b0\u65b9\u6cd5\u8bba\uff09\uff1bTREASURE/METHODOLOGY \u96f6 append | "
    "\u767b\u8bb0\u518c\u96f6\u547d\u4e2d\u65ad\u8a00: \u672c\u8f6e\u96f6\u6e05\u626b/\u5f52\u6863/\u5220\u9664/\u6062\u590d\u7c7b\u52a8\u4f5c\uff08treasure_guard \u672a\u89e6\u53d1\uff09 | "
    "\u4e0b\u8f6e\u6307\u9488: r820=W173 \u5e2d\u4f4d\u94fe\u534a\u7a97\uff08probe\u2192seat MSG\u2192\u5e26\u95f8\uff1bpost-W172 \u5b87\u5b99 re-derive \u5f3a\u5236\u00b7A 395_204..397_203 \u649e W172 B \u5e26 395_204..395_403 \u9884\u62d2=\u9636\u68af\u7b2c\u4e09\u5341\u4e09\u4f8b\u5f85\u673a\u8bc1\u00b7B \u843d A \u7a97\u5185=leg2 \u9884\u7559\uff09+10-08 \u590d\u5e02\u9996\u4ea4\u6613\u65e5\u6570\u636e\u94fe re-arm | "
    "\u672c\u5730\u672a\u8fbe origin commit \u6570=0\uff08\u6536\u53e3 commit \u540e push+fetch \u590d\u6838\uff09 | [r819 bm-a]"
)
with open(RPT, "a", encoding="utf-8", newline="") as f:
    f.write(line.replace("2026-10-07T11:1x", now.strftime("%Y-%m-%dT%H:%M")) + "\n")
print("round report line appended:", len(line), "chars")
