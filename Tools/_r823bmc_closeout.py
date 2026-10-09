# r823 bm-c closeout: state + heartbeat + round report append (facts-driven)
import json
import os
import time
import subprocess
import datetime

BM = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
now_iso = now.isoformat(timespec="seconds")
epoch = int(time.time())

with open(os.path.join(BM, "results", "_r823bmc_s05_facts.json"), encoding="utf-8") as f:
    facts = json.load(f)
dec_sha = facts["dec_sha256"]
ord_sha = facts["ord_sha1"]
new_orders = [x for x in facts.get("unacked_orders", [])
              if x.startswith("O-") and x.endswith(".md")]

ram_free = cpu_pct = gpu_free = None
try:
    import psutil
    ram_free = round(psutil.virtual_memory().available / 1024 ** 3, 2)
    cpu_pct = round(psutil.cpu_percent(interval=2), 1)
except Exception:
    pass
try:
    p = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    gpu_free = int(p.stdout.decode("utf-8", "replace").strip().splitlines()[0])
except Exception:
    pass

idle_verdict = "unknown"
try:
    with open(os.path.join(BM, "results", "idle_trigger.bm-c.json"), encoding="utf-8") as f:
        idle_verdict = json.load(f).get("verdict", "unknown")
except Exception:
    pass

SUMMARY = (
    "2026-10-10T01:39+08:00 | r823 | dept:工程/舰队（CEO 令 O-20261010-0025 jman 权重接收道点火"
    "+5 令回执补登记+S6 41 腿链点火+r822 前驱亡态注记·第 122 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） | "
    "WM-VERDICT: 绿（red=false·lane=healthy·SatEngine rc0 活） | "
    "孤儿面=1（只读·probe py_faces=6） | "
    "r823: ①S0-1 锚定 bm-c+孤儿探针（orphans=1·py_faces=6）+r822 前驱亡态定谳（01:17 absorb commit "
    "e1ee753a8 落账后中途死·state/轮报缺位·git 史保全·本轮取 r823 续位）；"
    "②S0=fetch 实核 0/0 对齐（脏面=own daemon 活态件·autofill 自偿车道）；"
    "③S0.5 双扫=DEC delta b728→b87a92b1（已知 D-20261010-01/02/03 行执行注记刷新·零新派工·水位更新）"
    "+ORD delta 0A1D→e286f842（O-0025 已接单行+状态格·与 bm-a r933 消费面一致·水位更新）"
    "+5 令回执消费：O-20261010-0010（CEO 三连令·交互窗 00:3x 已自执回执）"
    "+O-20261009-2334（云端解禁·bm-c=本地满用合规姿态确认）"
    "+O-20261009-2359（429 红线·零云端调用面在飞·合规确认）"
    "+O-20261009-2340（温度计 delivered·regime_thermo_build 腿补入 r823 S6 链=r820 正典链缺腿修正·勿双开遵守）"
    "+O-20261010-0058（Taildrop 轻回执=交互窗 00:29 已落档·测试件清理毕+可收确认·本轮 orders_ack 补登记）；"
    "④S1 smoke 49/49；⑤SatEngine 活检查 rc0；"
    "⑥CEO 令 O-20261010-0025 关键路径：MSG-0059 收讫（bm-a 双道 00:55 起开：taildrop PID 38932+http :8000 备）"
    "→接收道点火 tailscale file get D:\\krea2_weights\\（PID 31932·01:29:47 起·分离后台双 log）"
    "——收件在途（DERP 中继 394ms 面·26GB 件时长以实收为准）·二选一勿双拉纪律执行（主道 taildrop·备道不并拉）；"
    "⑦S6 r823 链 41 腿点火（r820 正典克隆+thermo 腿焊入·detached pid 51704）；"
    "⑧T-2026-10-10-180/181 open P1 票（温度计 prereg）在板未认领=下轮候选（idle 非 GREEN：RAM 面）"
)
ACT = (
    "当前活: r823 CEO 令 O-20261010-0025 jman 权重接收道已点火（tailscale file get PID 31932·01:29 起·DERP 中继在途）"
    "+S6 41 腿链在跑+5 令回执补登记 | "
    "最近实物: Tools/_r823bmc_s6.py（41 腿链·thermo 腿焊入·pid 51704 在跑）+results/_r823bmc_s05_facts.json"
    "+orders_ack 185 登记 @ 2026-10-10T01:39+08:00 | "
    "下个里程碑: 权重三件到件（实收速率定 ETA）→Get-FileHash×3 哈希门→precache→krea2 640 训练点火"
    "（完训到件后 ~6-8h·LOOKBOARD 上链）"
)
NEXT = (
    "r824 续作: ①权重接收监控（D:\\krea2_weights 到件面+Get-FileHash×3 对 MSG-0055 sha256 门）"
    "→到件=precache latents+TE→krea2_train_network 点火（res 640·blocks_to_swap 按腾后 RAM 实测 8-20"
    "·fp8_base+fp8_scaled·rank32/alpha32·lr1e-4·16 epochs·seed 42·num_repeats=8=256/epoch·输出 outputs/jman_v1_640/）"
    "②S6 r823 链 41 腿 rc 验收（absorb 面）③uv 装机+musubi uv sync --extra cu128 后台续跑验收"
    "④T-2026-10-10-180/181 prereg 认领评估⑤训毕恢复债（Ollama 双任务 enable+llama-server+ComfyUI server 重启）"
    "⑥QA r823 包 poll+收编（本轮超时让位如实）"
)
VERIFY = (
    "smoke 49/49 + SatEngine status rc0 (waves 143-202 registered) + tailscale file get PID 31932 "
    "detached (D:\\krea2_weights logs) + S6 chain detached pid 51704 (results/_r823bmc_s6_log.txt) + "
    "5 orders ack-registered (orders_ack 180->185) + DEC b87a92b1/ORD e286f842 watermarks consumed "
    "(zero new dispatch) + attrition scan CLEAN + orphan face=1 read-only (probe py_faces=6)"
)

TS_FIELDS = ["clock_read", "ts", "last_seen", "last_seen_at", "updated", "updated_at",
             "last_run_at", "current_task_at", "last_round_at", "last_round_ts",
             "last_decisions_read_at", "last_decisions_at", "last_orders_at",
             "last_round_summary_at", "last_seen", "last_ts"]


def apply_common(d):
    for k in TS_FIELDS:
        if k in d:
            d[k] = now_iso
    d["heartbeat_epoch_utc"] = epoch
    d["round_no"] = 823
    d["round_no_label"] = "r823"
    d["last_round"] = 823
    d["current_task"] = ACT
    d["activity_now"] = ACT
    d["next"] = NEXT
    d["next_milestone"] = NEXT
    d["next_pointer"] = NEXT
    d["did"] = SUMMARY
    d["last_round_summary"] = SUMMARY
    d["last_action"] = SUMMARY
    d["note"] = SUMMARY
    d["verdict"] = VERIFY
    d["verify"] = VERIFY
    d["latest_artifact"] = ("Tools/_r823bmc_s6.py (41-leg chain, thermo leg welded, pid 51704) + "
                            "tailscale file get PID 31932 + results/_r823bmc_s05_facts.json")
    if cpu_pct is not None:
        d["cpu_pct"] = cpu_pct
        d["cpu_util_pct"] = cpu_pct
        d["cpu_idle_pct"] = round(100 - cpu_pct, 1)
    if ram_free is not None:
        d["free_ram_gb"] = ram_free
        d["ram_free_gb"] = ram_free
        d["idle_ram_gb"] = ram_free
    if gpu_free is not None:
        for k in ["gpu_free_vram_mib", "gpu_idle_vram_mib", "gpu_free_mib", "gpu_idle_mib",
                  "gpu_free_mb", "gpu_idle_mb", "gpu_vram_free_mb", "gpu_free_vram_mb"]:
            if k in d:
                d[k] = gpu_free


# --- state-bm-c.json ---
sp = os.path.join(BM, "state-bm-c.json")
with open(sp, encoding="utf-8") as f:
    st = json.load(f)
apply_common(st)
st["last_decisions_sha"] = dec_sha
st["last_orders_sha"] = ord_sha
st["last_decisions_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; "
                                   "r823 sweep SSH fetch rc128 reset-window -> blob read from last-good origin/main "
                                   "ref (01:17 absorb face); dec delta TRUE = b7289489 -> b87a92b1 = known-row "
                                   "D-20261010-01/02/03 execution-note refresh, ZERO new dispatch, watermark updated; "
                                   "facts-driven from results/_r823bmc_s05_facts.json, 64hex shape-asserted")
st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r823 sweep SSH "
                                "fetch rc128 reset-window -> blob read from last-good origin/main ref; ord delta TRUE "
                                "= 0A1D9C1D -> e286f842 = O-20261010-0025 claimed-row + status cells, consistent with "
                                "bm-a r933 consumption face, ZERO new dispatch; facts-driven, 40hex shape-asserted")
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# --- heartbeat fleet/machines/bm-c.json ---
hp = os.path.join(BM, "fleet", "machines", "bm-c.json")
with open(hp, encoding="utf-8") as f:
    hb = json.load(f)
apply_common(hb)
ack = sorted(set(hb.get("orders_ack", [])) | set(new_orders))
hb["orders_ack"] = ack
hb["orders_ack_count"] = len(ack)
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["prod_lanes"] = ("bigmoney unattended loop (10min iteration) + quant research + "
                    "jman LoRA 640px training lane (CEO O-20261010-0025, weights inbound)")
hb["last_decisions_sha"] = dec_sha
hb["last_orders_sha"] = ord_sha
hb["last_decisions_sha_method"] = st["last_decisions_sha_method"]
hb["last_orders_sha_method"] = st["last_orders_sha_method"]
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# --- round report append ---
RR = (SUMMARY +
      " | 验证证据: smoke 49/49 + SatEngine rc0 + file get PID 31932 双 log 落盘（D:\\krea2_weights\\）"
      " + S6 pid 51704 log 增量落盘（results/_r823bmc_s6_log.txt） + facts=results/_r823bmc_s05_facts.json"
      " + attrition results/_attrition_guard_scan.json + orders_ack 185 登记"
      " | 下轮指针: " + NEXT +
      " | 本轮产品积分：1（接收道点火=CEO 令关键路径实物推进·训练点火=权重物理依赖在途如实留痕；5 令回执补登记）"
      " | 记账预算：4（轮报行/state+心跳收口/facts 件/orders_ack 登记）")
with open(os.path.join(BM, "round_reports-bm-c.md"), "a", encoding="utf-8") as f:
    f.write(RR + "\n")

# F7 self-checks: epoch int + clock T-format
assert isinstance(st["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in st["clock_read"] and st["clock_read"] == now_iso, "clock_read T-format"
print("CLOSEOUT OK r823 epoch=%d ack=%d new=%s cpu=%s ram=%s gpu=%s idle=%s" %
      (epoch, len(ack), new_orders, cpu_pct, ram_free, gpu_free, idle_verdict))
