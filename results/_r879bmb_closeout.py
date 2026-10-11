# -*- coding: utf-8 -*-
"""r879 bm-b closeout: state.json + heartbeat + round report append."""
import json, time, io, subprocess

TS = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# ---------- state.json (bm-b legacy name per fleet README S5) ----------
sp = "state.json"
s = json.load(open(sp, encoding="utf-8"))
s["round"] = 879
s["round_no"] = 880
s["round_no_label"] = "r879"
for k in ("last_round_at", "last_round_ts", "last_seen", "ts", "updated",
          "updated_at", "clock_read", "last_action_at"):
    s[k] = TS
s["current_task"] = ("r880: E16 shard-0 first-flush checkpoint verify (wiring-face real-fire proof, "
                      "ckpt rows >0 expected ~13:10) -> 12-shard burn completion watch -> finalize "
                      "when 12/12 (observing round) -> T-184 transfer receiver restore SAME round "
                      "origin/transfer/t184-510880 lands (deadline 2026-10-12 15:30, bm-a push "
                      "pending) -> W210 freeze anchor watch (W209 finalize bm-c side) -> E15 s4 "
                      "intake month-boundary face (2026-11-01) -> 48h CEO report due 2026-10-13 11:2x")
s["task"] = s["current_task"]
s["now_active"] = ("r879 closeout: E16 shard-0 relaunch verified alive (pid 20048 + 9 workers, fixed "
                   "runner sha 2761b762, ckpt append-open 12:52:26 zero crash; first flush ~13:10 = "
                   "r880 proof); T-184 receiver leg CLAIMED (bm-a push pending); CODELY r878 pitlaw "
                   "appended + r879 minisplit landed (main 29,067B)")
s["did"] = ("r879 first-action + watch round: S0 dirty-tree lane-state checkpoint commit (r642 "
            "clean-tree law, 11+3 tick faces) + rebase pull clean (origin 2d4ac1b0d->d771ea5b0 bm-c "
            "r872 S6 commits absorbed, 0 UU); S0.5 orders ack diff EMPTY (68/68 disk orders acked, "
            "count 193) + D19 dec 恒等 + ord delta consumed twice (629a7397->ba4f10ac 12:5x bm-a "
            "receipt row zero-BM-action; mid-round ba4f10ac->818bd43d 4 new rows ALL @BigStream MV "
            "domain bm-b=备援归 MV 车道非本司域 zero-BM-action) + watermark advance 818bd43d "
            "read-back OK; S1 smoke 49/49; FIRST ACTION (r878 deferred S4): with-block indent wiring "
            "pitlaw appended to CODELY.md + r879 minisplit ceremony (r822 655B verbatim->"
            "pit-protocol-d19 + r870 861B verbatim->pit-protocol-judge + r865 1359B main-file "
            "REMOVAL per r896/r807 in-domain precedent, evidence=pit-protocol-d19 r871 条+r672 "
            "raw-blob 律族 script-asserted; main 30,236->29,067B <=30,720B; receipt "
            "_r879bmb_codely_minisplit.json + TREASURE ledger line); P0 E16 shard-0 relaunch "
            "verified: autofill 12:32:01 launch pid 20048 fixed-runner sha 2761b762, tasklist "
            "alive + 9 child workers burning, ckpt append-open landed 12:52:26 zero crash (crashed "
            "run death point was FIRST FLUSH not open; flush due ~13:10 = r880 real-fire proof); "
            "S2 T-184 P1 ticket CLAIMED (receiver leg, physical dependency = bm-a push, branch "
            "absent from origin 12:5x ls-remote, alloc_paper stays rc=2 honest per spec); W209 not "
            "finalized (N1_BANDS tail W207), W210 pre-seat stands (ADMIT bands A 476804_478803 / "
            "B 478804_479003), freeze anchor watch continues; S6 40 legs 39 rc0 + alloc_paper "
            "rc=2 (T-184 dep honest, 4th consecutive round same face) + paper family no-new-bar "
            "lawful skip (Sunday); S7 hooks both match zero reinstall + attrition CLEAN (4 healed "
            "historical, 0 active) + loop task pin=2 no-op + watchdog re-registered + orphan probe "
            "0 (26 py faces)")
s["last_action"] = s["did"]
s["latest_artifact"] = ("r879: CODELY.md r878 pitlaw (with-block indent wiring bug + hermetic-"
                        "selftest wiring-face gap) + minisplit receipt results/_r879bmb_codely_"
                        "minisplit.json (main 29,067B) + T-2026-10-11-184-P1 claim (receiver leg)")
s["next"] = s["current_task"]
s["next_milestone"] = ("E16 12-shard burn complete + finalize <=2026-10-13 (first-flush proof r880 "
                       "~13:10); T-184 510880 restore before 2026-10-12 15:30 (bm-a push pending)")
s["orphan_face"] = 0
s["orphan_faces"] = 0
s["orphan_face_note"] = "r879 round probe: py_faces=26 alive, orphans=0"
s["verdict"] = ("GREEN: r879 COMPLETE (first-action pitlaw+minisplit landed; E16 shard-0 relaunch "
                "verified alive 9 workers, ckpt open zero crash, first flush = r880 proof; T-184 "
                "claimed w/ physical dep); smoke 49/49; S6 39rc0+alloc rc2 T-184 dep 4th round "
                "honest; WM red=true = burn ramp window (E16 in-flight py 48-65%, GM waiver "
                "O-1612 legal, expect green r880 as 15-min window fills)")
json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- heartbeat fleet/machines/bm-b.json ----------
hp = "fleet/machines/bm-b.json"
h = json.load(open(hp, encoding="utf-8"))
import psutil
ram = psutil.virtual_memory()
h["clock_read"] = TS
h["ts"] = TS
h["last_seen"] = TS
h["last_round_at"] = TS
h["heartbeat_epoch_utc"] = EPOCH
h["round"] = 879
h["round_no"] = 880
h["cpu_cores"] = psutil.cpu_count(logical=True)
h["ram_free_gb"] = round(ram.available / (1024 ** 3), 1)
h["free_ram_gb"] = h["ram_free_gb"]
h["ram_free_pct"] = round(ram.available * 100.0 / ram.total, 1)
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"], capture_output=True)
    vmb = int(r.stdout.decode("utf-8", errors="replace").strip().splitlines()[0])
    h["gpu_free_vram_gb"] = round(vmb / 1024.0, 1)
    h["vram_free_gb"] = h["gpu_free_vram_gb"]
    h["gpu_free_vram_mb"] = int(round(vmb))
except Exception:
    pass
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["current_task"] = s["current_task"]
h["task"] = s["current_task"]
h["now_active"] = s["now_active"]
h["did"] = s["did"]
h["last_action"] = s["did"]
h["last_action_at"] = TS
h["latest_artifact"] = s["latest_artifact"]
h["next"] = s["next"]
h["next_milestone"] = s["next_milestone"]
h["verdict"] = s["verdict"]
h["orphan_face"] = 0
h["orphan_faces"] = 0
h["orphan_face_note"] = s["orphan_face_note"]
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"

# ---------- round report append ----------
RR = ("{ts} | r879 bm-b | dept:工程（S0-S7 全链收口·CODELY r878 坑律+S4 欠账 mini-split 仪式首务）"
      "+dept:研究（E16 shard-0 relaunch 实证面·T-184 接收腿认领·W209/W210 候窗）| 孤儿面=0"
      "（round probe py_faces=26 orphans=0）| WM-VERDICT: red=true（lane=pool-batch-runnable-idle-"
      "low-cpu·E16 烧批爬坡窗=在飞合法〔GM waiver O-1612〕·py 48-65% 实测·15min 窗填满后 r880 预期转绿）"
      "| 实况三行：当前活=E16 shard-0 修复版烧批在飞（autofill 12:32:01 pid 20048·runner sha 2761b762"
      "·9 工在烧·ckpt 追加开脸 12:52:26 零崩·首 flush≈13:10=r880 接线面实弹证明）；最近实物="
      "CODELY.md r878 坑律入册+results/_r879bmb_codely_minisplit.json〔12:5x·主件 30,236→29,067B 回线"
      "·r822/r870 verbatim 迁 d19/judge 域+r865 按 r896/r807 先例域内实证摘除〕+T-2026-10-11-184-P1"
      " 认领〔接收腿·物理依赖留痕〕；下个里程碑=E16 12 分片烧完+finalize ≤2026-10-13（首 flush 证明 "
      "r880）+T-184 510880 恢复 deadline 2026-10-12 15:30（bm-a push pending·分支未达 origin）| did: "
      "S0 脏树车道活态 checkpoint 提交（r642 净树律）+rebase pull 干净零冲突（吸收 bm-c r872 S6 三提交）"
      "·S0.5 令差集空（68/68 acked）+D19 双 delta 双消费（12:5x bm-a 回执行+13:2x 前 4 新行全 @BigStream "
      "MV 域=bm-b 备援归 MV 车道零本司动作）+水位推进 818bd43d read-back OK·S1 smoke 49/49·首务=r878 "
      "with 内缩接线坑+封闭自检接线面盲区坑律入册+同窗 mini-split（receipt+TREASURE 台账行）·P0 E16 "
      "shard-0 relaunch 实证（进程活+9 工+ckpt 开面零崩）·T-184 认领（依赖留痕）·W209 未 finalize"
      "（注册表尾 W207）W210 席 probe 在位候窗·S6 40 腿 39 rc0+alloc_paper rc=2（T-184 dep 第 4 轮"
      "诚实面）·S7 双钩恒等零重装+attrition CLEAN+loop pin=2 no-op+watchdog 重注册 | next: r880 E16 "
      "首 flush ckpt 行>0 实证（~13:10）→12 分片完成 watch→12/12 finalize→T-184 分支落地同轮恢复"
      "（deadline 10-12 15:30）→W210 freeze 锚候窗（W209 bm-c）→48h CEO 报告 2026-10-13 11:2x | "
      "本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证）\n").format(ts=TS)
with io.open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8", newline="") as f:
    f.write(RR)

print(json.dumps({"state_round": 879, "round_no": 880, "epoch": chk["heartbeat_epoch_utc"],
                  "epoch_is_int": True, "ram_free_gb": h["ram_free_gb"],
                  "vram_free_gb": h.get("gpu_free_vram_gb"), "ts": TS, "rr_appended": True}))
