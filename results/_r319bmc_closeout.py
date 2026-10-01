# r319 bm-c closeout: state + heartbeat + round report + CODELY append
import json, time, os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = time.strftime("%Y-%m-%dT%H:%M:%S")
EPOCH = int(time.time())
CLOCK = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# ---- format probe helpers (r289/r509 law: probe before rewrite) ----
def probe_write(path, obj):
    raw = open(path, "rb").read() if os.path.exists(path) else b""
    eol = "\r\n" if b"\r\n" in raw[:2000] else "\n"
    text = json.dumps(obj, ensure_ascii=False, indent=1) + eol
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)

# ---- 1. state-bm-c.json ----
sp = os.path.join(ROOT, "state-bm-c.json")
st = json.load(open(sp, encoding="utf-8"))
st["machine_id"] = "bm-c"
st["round_no"] = 319
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["updated"] = NOW
try:
    import psutil
    st["cpu_pct"] = round(psutil.cpu_percent(interval=0.5), 1)
    vm = psutil.virtual_memory()
    st["idle_ram_gb"] = round(vm.available / 1024**3, 1)
except Exception:
    pass
st["verify"] = ("S1 smoke 47/47; T-141 s1 ENGINE LANDED (Tools/saturation_engine.py "
                "15/15 selftest, schtasks Bigmoney-SaturationEngine 1-min IgnoreNew "
                "resident, alive after psutil-priming patch restart); N1-W9 12/12 "
                "engine-burned (~90s/shard, 3 concurrent x8 workers) + finalize rc0 "
                "(K=19,920, ledger 380,039->382,239, skill_line_v2 1.1534->1.1474); "
                "S6 all legs rc0 (dualrun streak 5/3 MET, audit burning-healthy py "
                "85-100 with one transient cap_violation flag during S6+W9 burst "
                "overlap -- root cause psutil first-read-0.0 mis-sample, patched "
                "same round); D-19 753F99E8 MATCH-unchanged; O-1410 acked+executed; "
                "attrition CLEAN; T-131 alive")
st["did"] = ("r319: T-141 s1 saturation engine landed live + N1-W9 full wave "
             "engine-burned+finalized (ledger +2,200) + O-1410 ack/exec + S6 rc0")
st["current_task"] = ("T-141 s1 residual watch (engine resident, N1 queue empty "
                      "until W10+ prereg supply); T-131 backfill patrol (network-"
                      "bound); dualrun flip gate bm-c streak 5 MET awaiting fleet")
st["next"] = ("(r320) (a) T-141 s2 ledger-conversion + s3 CEO-face/round-zero "
              "wiring claims (unclaimed); (b) W10 prereg drafting (law sec.4 tail "
              "+ band gate -- engine queue supply); (c) T-131 patrol; (d) dualrun "
              "3-machine flip gate re-probe (bm-c 5/3 MET)")
st["heartbeat_epoch_utc"] = EPOCH
st["clock_read"] = NOW
st["note"] = ("r319: engine psutil first-read-0.0 pit found+fixed same round "
              "(prime + MACHINE_IGNITE_HOLD 88); engine burns ran during S6 chain "
              "-- transient audit cap_violation flag honestly reported, steady-"
              "state burn face = 3x8 workers under 26-cap; watchdog register "
              "access-denied line = benign re-register attempt on present task")
st["last_ts"] = NOW
st["last_round"] = ("2026-10-01 r319 bm-c: T-141 s1 saturation engine landed + "
                    "N1-W9 wave engine-burned+finalized (K=19,920 ledger 382,239) "
                    "+ O-1410 ack/exec + S6 rc0")
st["last_seen"] = NOW
probe_write(sp, st)

# ---- 2. heartbeat fleet/machines/bm-c.json ----
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
if "O-20261001-1410-bm-c.md" not in hb.get("orders_ack", []):
    hb["orders_ack"].append("O-20261001-1410-bm-c.md")
hb["round_no"] = 319
hb["updated_at"] = NOW
hb["last_seen"] = NOW
hb["last_seen_at"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
hb["health"] = "ok"
try:
    import psutil
    hb["cpu_pct"] = round(psutil.cpu_percent(interval=0.5), 1)
    hb["cpu_util_pct"] = hb["cpu_pct"]
    hb["cpu_idle_pct"] = round(100 - hb["cpu_pct"], 1)
    vm = psutil.virtual_memory()
    hb["free_ram_gb"] = round(vm.available / 1024**3, 1)
    hb["idle_ram_gb"] = hb["free_ram_gb"]
    hb["ram_free_gb"] = hb["free_ram_gb"]
except Exception:
    pass
hb["prod_lanes"] = ("r319: T-141 s1 saturation ENGINE LIVE (resident, 15/15 selftest, "
                    "N1-W9 12/12 burned+finalized K=19,920 ledger 382,239 skill_line 1.1474)")
hb["current_task"] = ("engine resident (queue empty -> W10 prereg supply next); "
                      "T-131 backfill patrol; T-141 s2/s3 unclaimed faces")
hb["verdict"] = ("saturation engine live; N1-W9 wave closed same-round (12/12 + "
                 "finalize); wm loaded_ok window avg 28.5 peak 85.4 (engine burn); "
                 "audit burning-healthy; one transient cap_violation flag (burst "
                 "overlap, root-cause patched same round)")
hb["activity_now"] = ("saturation engine resident alive (task 1-min IgnoreNew); "
                      "T-131 fund_history backfill network-bound in flight; "
                      "N1-W9 finalized")
hb["latest_artifact"] = ("Tools/saturation_engine.py + results/perpetual_faces/"
                         "n1_w9_results.json (K=19,920, finalize 14:26) + "
                         "results/p2cal_ext/n1_w9/ 12 shards (14:21-14:24)")
hb["next_milestone"] = ("T-141 s2+s3 build (ledger conversion + CEO py% live row + "
                        "round-zero wiring, window <=48h); W10 prereg supply "
                        "drafting (engine queue); acceptance face: 3 workdays "
                        "fleet py>=70% per law sec.6")
probe_write(hp, hb)

# ---- 3. round_reports-bm-c.md append ----
rp = os.path.join(ROOT, "round_reports-bm-c.md")
line = (
    NOW + "｜r319｜dept:工程（T-141 s1 饱和引擎）+dept:研究（N1-W9 测量波收官）｜"
    "watermark verdict=绿 red=false lane=healthy（引擎烧窗 py 85-100 burning-healthy·audit 旗=cap_violation 瞬态"
    "〔S6 链+W9 三连烧+T-131 同窗重叠·根因=psutil process_iter 首读 0.0 把满载读成空载→当轮双修："
    "启动预读 prime+MACHINE_IGNITE_HOLD 88 点火门〕）｜"
    "本轮主产出=①O-1410 签收+执行=T-141 s1 饱和引擎落地（Tools/saturation_engine.py·15/15 selftest·"
    "schtasks Bigmoney-SaturationEngine 1-min IgnoreNew 常驻宿主· InvisibleRunner.vbs 等待式宿主=死即下分重启·"
    "重启后活实证）②N1-W9 全波引擎烧毕+finalize（12/12 分片·引擎 3 并发×8 workers ~90s/片·全波 ~4min·"
    "finalize rc0：K=19,920·ledger 380,039→382,239·skill_line_v2 1.1534→1.1474·产物 results/perpetual_faces/"
    "n1_w9_results.json+12 分片件+12 claim 件）③S6 全腿 rc0（dualrun ZERO-DRIFT streak 5/3 MET·"
    "wm loaded_ok 窗均 28.5 峰 85.4·25 腿车道守卫 no-op 如实·daily_report 5 faces+ceo_live_usage 再生）｜"
    "验证证据=S1 smoke 47/47；attrition CLEAN（4 ledgers）；precommit claw IDENTICAL 重装幂等；"
    "schtasks 三任务在场（SaturationEngine 14:22 首 fire·IterLoop :05 针位符·Watchdog Ready 14:50——"
    "watchdog 重注册 access-denied 行=在场任务良性重试注记）；D-19 753F99E8 MATCH-unchanged（raw-blob python 法）；"
    "orders 轮首+S7 双扫差集={O-1410}→签收执行（T-141 s1 引擎即执行体·心跳 orders_ack 已更）；"
    "inbox 3 件均他机对帖（上下文读入=T-139 三族炉全判负里程碑〔REV 121/LOWAMP 144/MOM 16 全零幸存·诚实判负 "
    "REFINE_BENCH §3〕+LOWAMP-P2 18/18 done=T-140 verdict 面开闸〔bm-b/bm-a 主导〕）｜"
    "实况三行（CEO 过程可见面）：当前活=饱和引擎常驻在飞（N1 队列空·待 W10 prereg 供给）+T-131 回填（network-bound）｜"
    "最近实物=Tools/saturation_engine.py+Bigmoney-SaturationEngine 任务+n1_w9 12 分片+finalize 件（14:19-14:26）｜"
    "下个里程碑=T-141 s2/s3 建造（账本转换+CEO py% live 行+round-zero 接线·窗 ≤48h）+W10 prereg 供给起草｜"
    "产品分=2（可跑常驻引擎+真烧 W9 全波+finalize 科学件）｜本地未达 origin commit 数=POSTPUSH ｜"
    "next: (r320)(a) T-141 s2/s3 认领建造（lane-free 切片）；(b) W10 prereg 起草（法典 §4 尾+band gate 机验·引擎队列供给）；"
    "(c) T-131 回填巡检（progress/status/log 三面）；(d) dualrun flip 门三机面再探（bm-c streak 5 已 MET·候 bm-a/bm-b）"
)
with open(rp, "a", encoding="utf-8", newline="\n") as fh:
    fh.write("\n" + line + "\n")

# ---- 4. CODELY.md append (memory entry, four-question gate passed) ----
cp = os.path.join(ROOT, "CODELY.md")
centry = (
    "- [2026-10-01 14:3x r319 bm-c] psutil process_iter 首读 0.0 过载误判坑（T-141 s1 饱和引擎首窗实弹）："
    "process_iter([\"cpu_percent\"]) 对每进程首次调用恒返 0.0（无既往采样点）→新起常驻监督器首个周期把满载机器读成空载"
    "→过量点火（本窗：S6 链+T-131 在飞时引擎仍连点 12 分片·audit cap_violation 旗瞬态〔CEO 90 帽〕）；"
    "正解=启动时先空跑一次 _py_cpu_pct() 预读（丢弃结果·进程级计数器落锚）+点火双门（py<70 fill 线 + MACHINE_IGNITE_HOLD 88 机器面）；"
    "连带=psutil.cpu_percent(interval=None) 机器面同样需 prime。"
    "How to apply：一切 psutil 常驻采样器启动必 prime 双面（机器+进程）再进判定循环；首周期判定结果一律丢弃或走保守门。\n"
)
with open(cp, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(centry)

print("closeout files written; epoch=%d clock=%s" % (EPOCH, CLOCK))
