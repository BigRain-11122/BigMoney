# -*- coding: utf-8 -*-
# r971 S7 closeout: state advance + round report + heartbeat (machine-verified writes)
import io, json, subprocess, time, datetime, os, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
clock = now.strftime("%Y-%m-%dT%H:%M:%S") + ("+08:00" if now.utcoffset().total_seconds() >= 0 else "")
epoch = int(time.time())

# fresh machine faces
import psutil
ram_avail = round(psutil.virtual_memory().available / 1e9, 1)
gpu = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu",
                      "--format=csv,noheader,nounits"], capture_output=True, text=True).stdout.strip()
gmem = [x.strip() for x in gpu.split(",")]
gpu_free_mib = int(gmem[1]) - int(gmem[0])
cpu_pct = psutil.cpu_percent(interval=1)

# inbox unprocessed check (bm-c or ALL addressed)
inbox = os.path.join(REPO, "fleet", "inbox")
proc = os.path.join(inbox, "processed")
unhandled = []
if os.path.isdir(inbox):
    for f in os.listdir(inbox):
        if f.endswith(".md") and os.path.isfile(os.path.join(inbox, f)):
            body = io.open(os.path.join(inbox, f), encoding="utf-8", errors="replace").read()
            if ("@bm-c" in body[:400] or "ALL" in body[:400]) and not os.path.exists(os.path.join(proc, f)):
                unhandled.append(f)
print("inbox unhandled:", unhandled or "none")

# ---- state update ----
SP = os.path.join(REPO, "state-bm-c.json")
st = json.load(io.open(SP, encoding="utf-8"))
assert st["round_no"] == 971, f"unexpected round_no {st['round_no']}"
st["round_no"] = 972
st["loop_round"] = 971
st["last_round"] = 971
st["clock_read"] = clock
st["ts"] = clock
st["updated"] = clock
st["updated_at"] = clock
st["last_seen"] = now.strftime("%Y-%m-%d %H:%M:%S")
st["last_seen_at"] = clock
st["last_round_at"] = clock
st["last_round_closed"] = clock
st["last_round_ts"] = epoch
st["last_ts"] = epoch
st["current_task"] = "r971 closeout (V3 harvest relay closed + W233 facts/subgen prep + S6 41-leg chain)"
st["current_task_at"] = clock
st["heartbeat_epoch_utc"] = epoch
st["cpu_pct"] = cpu_pct
st["cpu_util_pct"] = cpu_pct
st["cpu_idle_pct"] = round(100 - cpu_pct, 1)
st["free_ram_gb"] = ram_avail
st["ram_free_gb"] = ram_avail
st["idle_ram_gb"] = ram_avail
st["gpu_idle_mib"] = gpu_free_mib
st["gpu_free_mib"] = gpu_free_mib
st["gpu_idle_mb"] = gpu_free_mib
st["gpu_free_mb"] = gpu_free_mib
st["gpu_mem_used_mib"] = int(gmem[0])
st["gpu_mem_total_mib"] = int(gmem[1])
st["gpu_used_vram_mib"] = int(gmem[0])
st["gpu_vram_free_mb"] = gpu_free_mib
st["gpu_free_vram_mb"] = round(gpu_free_mib / 1.048576, 1)
st["gpu_free_vram_gb"] = round(gpu_free_mib / 1024, 1)

st["did"] = ("r971: (1) S0-1 anchor bm-c + round-zero probe py_faces=6 orphans=2 zero-kill + state-sync 40038cb91 + pull up-to-date; "
             "(2) S0.5 phantom-watermark 8th healed-by-evidence (probe ORD TRUE vs rev-parse ground truth ad15e509==watermark -> zero rows owed; dec fb5825cb sha256-verified hold); "
             "S7 double-scan ORD real-delta = own row (2e403fb tail, zero foreign rows) -> watermark self-advanced 90f4d26d; "
             "(3) smoke 49/49; satengine ALIVE rc0; wm red=False healthy; "
             "(4) CEO V3 chain harvest FULL CLOSED (S3 top): NEWKF 28/28 trial board + QC-r970/r971 group-tree origin ae8bcb6 "
             "+ R05_v4 downloaded CDN + multimodal QC 6.0 FAIL (soft-freeze-tail FIXED 9/10 / zero-dust 2-consecutive 2/10 / NEW wood-grain drift = i2v model face, source frame verified featureless) "
             "-> night frame-fix dispatch merged with C02 (bm-a GPU night: Krea2 source-frame regen, basalt anchor + frame-level dust motes); "
             "director relay 5-piece: board+QC on-chain + MSG-20261013-1730-bmc + ORD row 2e403fb + poke bm-a accepted 17:23:56; "
             "5 loose duplicate mp4s hash-verified identical -> moved into gitignored archive (zero-loss); "
             "(5) W233 prereg derive PREP LANDED (honest split per large-task law): facts machine-frozen results/_w233bmc_facts.json "
             "(W232 finalize ledger 934,189/K 508,320/mu -0.09274288/sigma 0.24508296/w232_only -0.10490950 diff 0.0122 in-band/A_p95 0.3063/KL +0.0001/se_mu 0.000344 "
             "+ W233 bands A 527404_529403/B 529404_529603 leg1 hops 1/1 + leg0 230 rows/bmc_ordinal 63 + freeze receipt 62nd owned "
             "+ base blob a3a7aa632 25,380B freeze-time verified + hygiene: zero foreign W233 seat claims, zero origin W233 rows/prereg) "
             "+ subgen m30 skeleton results/_w233bmc_subgen.py (SUB32 46-group extraction + 4-face resolution VERIFIED live, stops at R33 import as designed) "
             "-- R33 data authoring + derive clone = next window FIRST ACTION (full-budget clean pass); "
             "(6) S6 full chain 41 legs: 40 rc0 + t35_openfill rc=1 (2026-10-12 marks evidence gap disclosed honestly, marks lane upstream) "
             "-- dualrun streak 51 zero-drift / update_daily rc0 but 10-13 bars source still unpublished (cutoff 10-12, sina lag self-heal next windows) "
             "/ live_paper OK / papers idempotent at 10-12 / daily_report+ceo_usage+build_status faces written / token L2 0 today; "
             "(7) S7: attrition 4 CLEAN + loop Running + watchdog Ready + both claws OK")
st["last_round_summary"] = ("r971: V3 链收割全闭环 (NEWKF 28 板+QC 上链+接力五件+poke accepted) + R05_v4 6.0 FAIL 归因 (夜窗帧级修法并入 C02) "
                            "+ W233 事实冻结+subgen 骨架 (R33=下窗首动作) + S6 41 腿 40rc0 (t35_openfill rc1 marks 缺口如实报)")
st["last_action"] = "r971 closeout (V3 harvest relay + W233 prep + S6 chain)"
st["last_round_summary_at"] = clock
st["last_action_at"] = clock
st["verdict"] = ("green: CEO V3 harvest relay closed 5-piece (board/QC/MSG/ORD/poke) + R05_v4 QC verdict landed (frame-fix routed bm-a night) "
                 "+ W233 prereg prep landed (facts frozen + subgen verified) + S6 40/41 rc0 (t35_openfill marks-gap disclosed) + smoke 49/49 "
                 "+ S7 quad green; W233 R33 authoring = r972 first action (honest large-task split, RAM window open 2.7G)")
st["latest_artifact"] = "bmc/V3-NEWKF-TRIAL-BOARD_q88.jpg + QC-r971.json (group origin ae8bcb6) + results/_w233bmc_facts.json"
st["last_artifact"] = st["latest_artifact"]
st["recent_artifact"] = st["latest_artifact"]
st["next_milestone"] = ("W233 prereg derive full pass (r972: R33 authoring + subgen + derive clone + asserts + commit) -> splice/burn/finalize; "
                        "NEWKF director pick -> 1344x768 upgrade batch; C02/R05 remade frames -> re-i2v; 10-13 bars self-heal window")
st["prod_lanes"] = ("GPU=MV V3 链毕 (Krea2 驻留 15.0G/16G·NEWKF 圈选回执到达即升正档批+C02/R05 重制帧到达即重 i2v·夜窗批); "
                    "CPU=W233 prereg derive R33 编著 = r972 首动作 (facts 已冻结·subgen 已验)")
st["now_active"] = ("2026-10-13 17:5x | r971 | bm-c: V3 链收割闭环+W233 prep | counter 971->972 | r972 首动作=W233 R33+derive")
st["activity_now"] = st["now_active"]
st["last_orders_sha"] = "90f4d26d5468886588dcca97d66cbdf420690838"
st["last_orders_sha_method"] = ("sha1 rev-parse origin/main:docs/orders.md (r971: probe TRUE=phantom 8th healed by rev-parse evidence ad15e509==wm zero rows; "
                                "S7 double-scan real-delta = own row 2e403fb tail zero foreign -> self-advanced 90f4d26d)")
st["last_orders_at"] = clock
st["last_orders_read_at"] = clock
st["last_orders_seen"] = now.strftime("%Y-%m-%d %H:%M:%S")
st["last_orders_read_note"] = "r971: ORD delta = own row (bm-c 2e403fb V3 relay row, tail-verified); zero foreign rows; watermark self-advanced"
st["last_orders_sha_note"] = "r971: ad15e509 -> 90f4d26d (own-row advance, zero consumption owed)"
st["last_decisions_at"] = clock
st["last_decisions_read_at"] = clock
st["last_decisions_read_note"] = "r971: DEC delta FALSE hold (fb5825cb sha256 blob-verified at 17:1x and probe FALSE at 17:5x)"
st["orders_ack_ts"] = clock
st["orders_ack_receipt"] = ("r971: probe ORD TRUE = PHANTOM-WATERMARK 8th (rev-parse ground truth ad15e509==watermark at window open, zero rows 16:43-17:1x, zero consumption; "
                            "corrupt-face lineage r902/r963/r967/r970 8th instance healed-by-evidence; S7 double-scan ORD delta = own row 2e403fb -> watermark advanced 90f4d26d)")
st["sync"] = {"origin_tip": "bmq: rides this closeout commit; group-tree: ae8bcb6 (V3 board/QC) + 2e403fb (ORD relay row)",
              "ts": clock, "ahead_behind": "group-tree 0/0 at closeout; bmq ahead 1 (state-sync) riding this push",
              "note": "r971: CEO V3 harvest + relay + W233 prep + S6 41-leg chain"}
st["head_sha"] = "quant: rides this window's closeout commit; group-tree: 2e403fb (ORD row tail)"
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["orphan_face"] = 2
st["orphan_faces"] = 2
st["r971_closeout_note"] = st["did"]
st["r971_absorb_note"] = "clean continuation window (state round_no=971 at open, executed r971, advanced 971->972 so next=r972; zero absorb owed)"
st["last_decisions_seen"] = now.strftime("%Y-10-13 17:%02d" % now.minute) if False else now.strftime("%Y-%m-%d %H:%M:%S")
st.pop("last_decisions_seen", None)
st["last_decisions_seen"] = now.strftime("%Y-%m-%d %H:%M:%S")

io.open(SP, "w", encoding="utf-8", newline="\n").write(json.dumps(st, ensure_ascii=False, indent=1))
chk = json.load(io.open(SP, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"
print("state OK: round_no 972, epoch int:", chk["heartbeat_epoch_utc"])

# ---- round report line ----
RP = os.path.join(REPO, "round_reports-bm-c.md")
row = (clock + " | r971 | bm-c | CEO V3 链收割全闭环: NEWKF 28/28 试构图板+QC-r970/r971 上链 (group ae8bcb6) + 导演席接力五件 (MSG-20261013-1730-bmc + ORD 行 2e403fb + poke accepted 17:23:56) | "
       "R05_v4 CDN 下载+multimodal QC 6.0 FAIL 定谳 (软冻尾 FIXED 9/10「窄亮边下行至底」修法生效·零尘两连败 2/10 提示词两版零渲染·NEW 木纹材质漂移=源帧多模态核验无特征排除帧烘焙→定性 i2v 模型面→夜窗帧级修法并入 C02 批 bm-a Krea2 重制玄武岩锚+帧级尘粒) | "
       "W233 prereg derive 诚实拆步: 事实冻结 results/_w233bmc_facts.json 全机读 (账本 934,189/K 508,320/mu -0.09274288/sigma 0.24508296/w232_only -0.10490950 差 0.0122 在带/A_p95 0.3063/KL +0.0001/se_mu 0.000344/带 A 527404_529403 B 529404_529603/leg0 230 行 bmc_ordinal 63/62nd owned/基座 a3a7aa632 25,380B 冻结时态验/外机席位零命中) + subgen m30 骨架实测验腿 (SUB32 46 组提取+四面解析·止于 R33 缺位=设计) | "
       "S0.5 phantom 8th healed (rev-parse ad15e509==水位零新行) + S7 双扫 ORD 真 delta=自进 90f4d26d (我行尾零外机) | "
       "S6 全链 41 腿 40rc0 + t35_openfill rc1 (10-12 marks 证据缺口如实报) · dualrun streak 51 · 10-13 bars 源未发 cutoff 10-12 后窗自愈 | smoke 49/49 | attrition 4 CLEAN | S7 quad green (loop Running/watchdog Ready/双爪 OK) | 水位绿 next_pick claimed moneyflow IC | "
       "下轮指针: r972 首动作=W233 R33 数据件编著+derive 克隆全预算一遍 (facts 已冻结) → splice/burn; NEWKF 圈选回执即升正档批; C02/R05 重制帧即重 i2v; 10-13 bars re-probe\n")
io.open(RP, "a", encoding="utf-8", newline="").write(row)
print("round report appended")

# ---- heartbeat ----
HP = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(io.open(HP, encoding="utf-8")) if os.path.exists(HP) else {}
hb.update({
    "machine_id": "bm-c", "last_seen": now.strftime("%Y-%m-%d %H:%M:%S"), "last_seen_at": clock,
    "current_task": st["current_task"], "verdict": "green",
    "cores": 32, "cpu_pct": cpu_pct,
    "free_ram_gb": ram_avail, "idle_ram_gb": ram_avail,
    "gpu_free_vram_mib": gpu_free_mib, "gpu_idle_mb": gpu_free_mib,
    "idle_rounds": 0, "agenda_starved": False,
    "heartbeat_epoch_utc": epoch, "clock_read": clock, "ts": clock,
    "round_no": 972, "loop_round": 971,
    "note": "r971: V3 harvest relay closed + W233 prep + S6 41-leg",
})
io.open(HP, "w", encoding="utf-8", newline="\n").write(json.dumps(hb, ensure_ascii=False, indent=1))
chk2 = json.load(io.open(HP, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int) and "T" in chk2["clock_read"]
print("heartbeat OK")
print("RAM avail %.1fG | GPU free %s MiB | cpu %.1f%%" % (ram_avail, gpu_free_mib, cpu_pct))
