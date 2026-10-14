# -*- coding: utf-8 -*-
# _r997bmc_closeout.py -- r997 closeout: state+heartbeat+round-report append (canonical path)
import io, json, os, subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))
NOW = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
EPOCH = int(time.time())

# 1) state-bm-c.json
sp = "state-bm-c.json"
st = json.load(io.open(sp, encoding="utf-8"))
did = ("r997: (1) S0-1 anchor bm-c + round-zero probe py_faces=8 orphans=3 zero-kill "
       "(ComfyUI MV-lane + album_serve + Doubao user-file: service/user-domain, no adoption); "
       "(2) S0 bigmoney pull blocked by lane-live dirty tree (behind 0 = already synced); group-tree pull "
       "--autostash landed 6 but pop conflict exposed DEAD-WINDOW HALF-DONE staged deletion batch "
       "(mv-album anchors/lyrics cleanup face) -> reset --hard to origin-sync clean (live-wins law, "
       "stash@{0} kept as evidence, disclosed); (3) MV WAVE1.5 RUNNER REBUILT+IGNITED "
       "(bmc_v3_wave15_r997.py PID 38460 Popen-detach; first ignite via PS Start-Process died to quoting-pit "
       "'can't find __main__ in K:\\' -> .py Popen correct path; orphan server 12:55 dead-session form model-state "
       "unknown -> queue-empty check + reboot law; str04 SKIP exists, str05 cold-load burning, queue running=1); "
       "(4) WAVE2 MANIFEST FACT-FROZEN (wave2_manifest_r997.json: 46 burn slots machine-derived from "
       "mv_full_shots.NEW + assembly rows shape; GAPS 7 v2-bridge frames 3-dir confirmed ABSENT = "
       "director-seat/bm-a supply face; local-burnable=39; 13:2x three new shots INT1_desk_breath ABSENT / "
       "D01_carver_words OK / B02_far_home OK); (5) SOFT-COPYRIGHT 18-model VERIFIED ALREADY-LANDED: "
       "fc1b936 on origin/main (C-machine 8 full src-txt + B-machine 10 corrected to bm-b relay + orders receipt "
       "in batch) -- r996 pointer 'r997 todo' was stale, zero-action discharge; (6) S1 smoke 49/49; S3 satengine "
       "rc0 ALIVE + wm red=false py_low_board_clear legal (bars pre-15:30); (7) S6 light: dualrun ZERO-DRIFT "
       "streak 51 (456) + audit FLAG pool_starvation/supply_floor structural answered-by-chain (W239 landed + "
       "W240 bm-a seat + MV wave2 manifest frozen-to-burn) + update_daily no-op cutoff 10-13 + regime ORANGE "
       "breadth 0.81 + fund_premium no-op + token delta=0; (8) attrition 4 CLEAN (2 healed) + S7 loop 14:55 "
       "scheduled + watchdog 14:51 scheduled (zh-CN label pit avoided raw-output r963 law)")
st.update({"round_no": 998, "current_task": "r997 closeout (wave1.5 runner burning + wave2 manifest frozen + soft-copyright verified-landed); bars 15:30 next; W240=bm-a chain in flight",
           "current_task_at": NOW, "last_round": "r997", "last_round_at": NOW, "did": did,
           "heartbeat_epoch_utc": EPOCH, "clock_read": NOW, "ts": NOW, "last_seen": NOW})
io.open(sp, "w", encoding="utf-8").write(json.dumps(st, ensure_ascii=False, indent=1))
print("state: round 997->998 written")

# 2) heartbeat fleet/machines/bm-c.json
hp = "fleet/machines/bm-c.json"
hb = json.load(io.open(hp, encoding="utf-8"))
hb.update({"last_seen": NOW, "ts": NOW, "clock_read": NOW, "heartbeat_epoch_utc": EPOCH,
           "idle_rounds": 0, "agenda_starved": False,
           "verdict": ("green: r997 runner-rebuild ignited (wave1.5 probe burning PID 38460) + wave2 manifest frozen "
                       "(39 local-burnable slots, 7 v2-bridge frames = bm-a/director supply face) + soft-copyright 18 "
                       "verified already-landed fc1b936; r998 P0 = wave1.5 harvest -> H3 INT8 wave2 ignite (CEO idleness "
                       "law GPU never idle) + 15:30 bars papers chain + W240 finalize watch -> W241 seat (bm-c turn)")})
io.open(hp, "w", encoding="utf-8").write(json.dumps(hb, ensure_ascii=False, indent=1))
chk = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk.get("heartbeat_epoch_utc"), int), "epoch must be int"
print("heartbeat written; epoch int verified:", chk["heartbeat_epoch_utc"])

# 3) round report line -> CANONICAL path only (r750 law)
ROW = (NOW + " | r997 | bm-c | " + did +
       " | orphan-faces=3（ComfyUI MV-lane+album_serve+Doubao 用户件=服务/用户域评估不收编零杀）"
       " | 验证证据=smoke 49/49 + dualrun streak 51（456）+ attrition 4 CLEAN + wave2_manifest_r997.json 39 槽冻结 + "
       "runner log wave15_r997.out.log（str04 SKIP+str05 冷载在烧 queue running=1）+ fc1b936 origin 核验 + "
       "组树 reset --hard behind-0 净态 + schtasks loop 14:55/watchdog 14:51 raw 验证"
       " | 本地未达 origin commit 数=closeout push 骑本窗（fetch-verify 下轮开窗）"
       " | 下轮指针：r998=(1) 波 1.5 收割（8/8 板+断裂归因结论行）→杀 Krea2 boot H3 INT8→波 2 39 槽点火（7 v2 桥帧候供）；"
       "(2) 15:30 bars→papers 全链；(3) W240 finalize watch→W241 席（bm-c 轮到）；(4) MF-IC-P1 面板复查\n")
rp = "logs/iteration-loop/round_reports-bm-c.md"
with io.open(rp, "a", encoding="utf-8") as f:
    f.write(ROW)
print("round report appended to canonical:", rp)
