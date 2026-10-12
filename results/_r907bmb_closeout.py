# -*- coding: utf-8 -*-
# r907 bm-b closeout: state.json + heartbeat + round report line
# Context: post-outage first round. 03:03 power loss killed loop+batch (r906 last round 03:00),
# 22:16:45 second loss during diagnostic session, reboot ~22:20. This round absorbed dead
# predecessors r907 (22:12, killed by outage) + r907b (22:43, killed by 25min watchdog),
# re-ignited ComfyUI (:8188, 23:32:21) + i2v driver (detached, 23:32:47) per README-RUN resume law.
import json, time, io, sys

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
now_iso = time.strftime("%Y-%m-%dTH:%M:%S+08:00")
epoch = int(time.time())

REPORT_LINE = (
    "| {ts} | r907 | dept:engineering (post-outage first round: 20h gap adjudicated + predecessors r907/r907b absorbed + i2v batch re-ignition) | "
    "currently-active: i2v batch re-burning (KN07 in-flight, batch 8/53, ComfyUI r907c :8188 + driver detached, VRAM 7.9GB loaded) | "
    "latest-artifact: KN_KN16.mp4 3.5MB @23:00:32 (r907b predecessor heritage, batch 8/53) + log-bmb-r907c.out.txt (KN07 SUBMITTED + 15s running = revival proof) | "
    "next-milestone: i2v 53/53 ETA 10-13 morning (45 units @ ~5-15min/unit under 180W cap) then remove keepwarm.pause marker; E15 48h report 10-13 11:2x; W18 48h report 10-14 00:44; unity-mcp POC due 10-13 12:00 | "
    "did: (1) 20h gap adjudicated: 03:03 outage (root cause 550W PSU, CEO-domain verdict 22:57 memory) killed loop+batch; 22:16:45 second outage during diagnostic session; reboot ~22:20; predecessors r907 (ignited ComfyUI 22:12, died in outage) + r907b (22:43 relaunch, KN16 landed 23:00:32, died at 25min watchdog) both absorbed per r898 precedent; "
    "(2) PRIMARY PRODUCT: smoke 49/49 + power cap 180W verified ACTIVE (nvidia-smi) + keepwarm.pause marker present -> ComfyUI soup ignited 23:32:21 + driver detached 23:32:47 (README-RUN resume law 're-run command after resume') -> KN07 re-submitted 15s running = batch revival live-proof (8/53 checkpoint, SKIP-resume law); "
    "(3) machine face: MODE=pause -> resumed 23:24:26 (flag read; resume actor = other-domain session, not this window); "
    "(4) DEFERRED to r908 (watchdog 25min window, ignition first): S6 41-leg chain (Monday 10-12 bar unfetched, honest) + orders scan (3 fetch timeouts tonight, GFW-night-type; origin face stays 8aa1dcf4f = r906 push self-proven) + IntradayMarks Monday 09:25 first-fire verify (machine was off 03:03-22:20, missed fire = honest accounting next round) | "
    "evidence: log-bmb-r907c.out.txt + comfy-r907c ignition faces + nvidia-smi 180W + _orphan_face_probe.bm-b.json (py_faces=5 orphans=0) | "
    "orphan-faces=0 | WM-VERDICT: deferred (watermark probe rides r908 S6 rerun; r906 baseline red=false stale-carry) | "
    "local-unreached-origin-commits=1 (commit lands after; push dispatched detached due to degraded night network; delivery self-proof next round) | "
    "next-pointer r908: S6 41-leg full chain (update_daily pulls 10-12 bar -> paper family) > orders scan (fetch network re-probe) > IntradayMarks missed-fire accounting > i2v batch watch > T-184 courtesy compare / unity-mcp POC window / W18+E15 report windows | [r907 bm-b]\n"
).format(ts=now_iso)

# --- state.json (bm-b face) ---
sp = ROOT + r"\state.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 908
st["round_no_label"] = "r907"
st["round"] = "907"
st["current_task"] = "r907 closeout: post-outage first round -- i2v batch re-ignited (8/53, KN07 in-flight)"
st["now_active"] = "i2v batch re-burning (KN07 in-flight, 8/53 done, ComfyUI r907c + driver detached)"
st["did"] = ("r907: (1) 20h gap adjudicated: 03:03 + 22:16:45 power losses (root cause 550W PSU, CEO-domain), reboot ~22:20; "
             "predecessors r907 (22:12, died in outage) + r907b (22:43, KN16 landed 23:00:32, died at 25min watchdog) absorbed; "
             "(2) PRIMARY: smoke 49/49 + 180W cap verified + marker present -> ComfyUI 23:32:21 + driver 23:32:47 detached -> "
             "KN07 re-submitted 15s running = batch revival proof (8/53, SKIP-resume); "
             "(3) machine resumed 23:24:26 (other-domain actor); "
             "(4) DEFERRED r908: S6 41 legs (Monday bar unfetched) + orders scan (3 fetch timeouts) + IntradayMarks 09:25 missed-fire verify")
st["last_action"] = "r907: i2v batch re-ignited post-double-outage (8/53, KN07 in-flight) + 20h gap adjudicated"
st["last_action_at"] = now_iso
st["last_round_at"] = now_iso
st["last_seen"] = now_iso
st["last_round_ts"] = now_iso
st["latest_artifact"] = "log-bmb-r907c.out.txt (KN07 SUBMITTED+15s running) + KN_KN16.mp4 @23:00:32 (batch 8/53)"
st["next"] = ("r908: S6 41-leg full chain (update_daily pulls 10-12 bar -> paper family) > orders scan (fetch re-probe) > "
              "IntradayMarks Monday missed-fire accounting > i2v batch watch (53/53 ETA 10-13 morning -> remove keepwarm.pause marker) > "
              "unity-mcp POC (due 10-13 12:00) > W18+E15 48h CEO reports (10-13 11:2x / 10-14 00:44) > BigHouse T-2 (<=10-15)")
st["next_milestone"] = ("i2v 53/53 ETA 10-13 morning (45 units under 180W cap); E15 48h report 10-13 11:2x; "
                        "W18 48h report 10-14 00:44; unity-mcp POC due 10-13 12:00; BigHouse T-2 <=10-15")
st["note"] = ("r907: post-outage first round; batch re-ignited per README-RUN resume law; S6/orders deferred to r908 "
              "(watchdog window + night-network degraded, 3 fetch timeouts); legal detached = ComfyUI + i2v driver; "
              "flash local line stays cloud-fallback while keepwarm.pause marker in place")
st["orphan_face"] = 0
st["orphan_faces"] = 0
st["orphan_face_note"] = "r907 round probe 23:12: py_faces=5 orphans=0; post-reboot clean; legal detached = ComfyUI + i2v driver (re-ignited 23:32)"
st["verdict"] = ("GREEN: i2v batch revived (8/53, KN07 in-flight, VRAM 7.9GB loaded, 180W cap active, CEO-approved keep-running posture) + "
                 "smoke 49/49; deferred faces = S6 chain + orders scan + IntradayMarks verify (r908); observe = night network degraded (3 fetch timeouts)")
st["ts"] = now_iso
st["updated"] = now_iso
st["updated_at"] = now_iso
st["clock_read"] = now_iso
st["sync"] = {
    "last_push_ts": now_iso,
    "note": "r907 closeout push dispatched detached (night network degraded: 3 fetch timeouts); delivery self-proof = r908 post-push fetch + rev-list",
}
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- heartbeat fleet/machines/bm-b.json ---
hp = ROOT + r"\fleet\machines\bm-b.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["current_task"] = st["current_task"]
hb["did"] = st["did"]
hb["last_action"] = st["last_action"]
hb["last_action_at"] = now_iso
hb["last_round_at"] = now_iso
hb["last_seen"] = now_iso
hb["latest_artifact"] = st["latest_artifact"]
hb["next"] = st["next"]
hb["note"] = ("r907: post-outage first round; i2v batch re-ignited 23:32 (ComfyUI + driver detached, KN07 in-flight, 8/53); "
              "S6/orders deferred r908; idle_rounds reset = real production work this round")
hb["now_active"] = st["now_active"]
hb["free_ram_gb"] = 1.1
hb["ram_free_gb"] = 1.1
hb["ram_free_pct"] = 4.6
hb["gpu_free_vram_gb"] = 0.29
hb["gpu_free_vram_mb"] = 297
hb["vram_free_gb"] = 0.29
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["green_idle"] = False
hb["round"] = 907
hb["round_no"] = 908
hb["round_no_label"] = "r907"
hb["orphan_face"] = 0
hb["orphan_faces"] = 0
hb["orphan_face_note"] = st["orphan_face_note"]
hb["ts"] = now_iso
hb["updated"] = now_iso
hb["updated_at"] = now_iso
hb["verdict"] = st["verdict"]
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- round report append ---
rp = ROOT + r"\logs\iteration-loop\round_reports.md"
with open(rp, "a", encoding="utf-8") as f:
    f.write(REPORT_LINE)

# self-proof
chk = json.load(open(sp, encoding="utf-8"))
hbk = json.load(open(hp, encoding="utf-8"))
assert isinstance(hbk["heartbeat_epoch_utc"], int), "epoch must be int"
assert chk["round_no"] == 908
print("CLOSEOUT_OK state.round_no=%d hb.epoch=%d hb.round_no=%d ts=%s" % (chk["round_no"], hbk["heartbeat_epoch_utc"], hbk["round_no"], now_iso))
