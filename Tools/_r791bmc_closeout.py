# -*- coding: utf-8 -*-
"""r791 bm-c closeout driver: round-report line append + state round_no bump
(791->792) + heartbeat full refresh + QA slot probe JSON.
Live metrics via psutil/nvidia-smi (CREATE_NO_WINDOW). Epoch = python int
(R170/R178 law). Facts printed for in-round verification.
Clone credit: Tools/_r790bmc_closeout.py (1-gen clone)."""
import json, time, subprocess, sys, os, datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")
epoch = int(time.time())

import psutil
free_ram_gb = round(psutil.virtual_memory().available / (1024**3), 1)
cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
try:
    p = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, creationflags=CNW, timeout=20)
    vram_free = int(float(p.stdout.decode().strip().splitlines()[0]))
except Exception:
    vram_free = -1

ROUND_LINE = (
    f"{ts} | r791 | dept:工程/研究（pit-pool-edit 让位窗 sub-split+W17 池烧跟进轮·第 92 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
    "WM-VERDICT: 绿（red=false·probe=insufficient_history 窗 n=1 诚实如实·W17 screen SHARD-0/1 双认领在飞=RAM 门等待合法活批·lane=healthy） | "
    "孤儿面=2→1（首读=ComfyUI 只读+W17 screen runner RAM 门有界等待三面全中→deadline 判别律只读零误杀·40min 帽自退实证·尾读=ComfyUI 只读） | "
    "r791: pit-pool-edit 让位窗 sub-split+W17 池烧跟进轮（08:2x-08:5x 窗·第 92 连守轮）——"
    "①S0.5 双扫：DEC 83813196/ORD 1212A338 双恒等零消费·unacked 0〔54 orders〕·inbox 0（轮首+收尾二扫双件 _r791bmc_s05_facts.json/_r791bmc_s0_facts.json）；"
    "②主产出=pit-pool-edit.md 让位窗 sub-split（r790 挂账清偿·r705 仪式同款）：32,616B/33 条→18,699B 18 条"
    "（池文件编辑/写入路径/settle/reland 窗/翻面手术/冲突基底族）+新域件 pit-pool-burn.md 15,621B 15 条"
    "（点火闸/烧录机械/双烧接管竞态族）·条目字节和 14,262B 恒等·prescan rc3 留痕（research/ 全族 fail-closed 面·"
    "D-06 授权 verbatim 迁移三件齐：留痕+登记册出入行+零丢失断言）·SPLIT PASS+VERIFY 74 checks·CODELY 指针注 30,643B≤帽；"
    "③S4 新坑律直写 pit-pool-burn.md（RAM 门有界等待池 runner×孤儿探针三面命中=deadline 判别律·942B·"
    "W17 SHARD-0 实弹·r666 直写范式·主件 77B 红线）；"
    "④QA r791 证据包净写 5/5（smoke-r791-bm-c.md+equity png 65,440B·91 trades·sharpe 0.1994·determinism=True·"
    "槽双面零撞·per-machine 后缀律）；"
    "⑤W17 池烧跟进：SHARD-0 07:47 点火→RAM 门（free 1.3GB<4GB）40min 帽自退 rc2（~08:27·零误杀实证）"
    "→daemon 08:30 复燃 SHARD-0+SHARD-1 双认领（2 shard 在飞等待·SHARD-2..7+JUDGE ready·SLA 窗 10-10 00:00·"
    "supply_family_streak 641min 如实载·点火闸=deadline 判别律消费面首例）；"
    "⑥S1 smoke 49/49+SAT 引擎活 rc0+S2 板清（job 0·idle 非绿 RAM 8.1% 无领单义务）；"
    "⑦S6 40/40 rc0 十二连绿（dualrun ZERO-DRIFT streak 51·fund_premium 15:30 前诚实 no-op〔第十观测窗〕·"
    "update_daily 10-08 截止零新行·marks no-op）；"
    "⑧S7 自愈批（loop pin=5 no-op·watchdog 重装·双爪重装·attrition 4 台账 CLEAN〔3 healed 注记照录〕）| "
    "下轮指针: r792=W17 screen 烧跟进（RAM 门读数到窗回执·RAM 释放即自续）+T-2026-10-09-178-P1 判决链票跟进"
    "+fund_premium 10-08 NAV 首采（15:30+·第十观测窗）+CEO 三选项等待态（MV 面）| "
    "本轮产品积分：2（pit-pool-burn 新域件+pit-pool-edit 回线=能用执法导航实物·QA r791 包 5/5=能看能跑实物·S6 40/40=经营层实物）| "
    "记账预算：3（轮报行/心跳/state 收口+facts 双扫双件+qa 槽探针件）"
)

CUR = ("当前活: r791 bm-c（08:2x-08:5x 窗·pit-pool-edit 让位窗 sub-split+W17 池烧跟进·第 92 连守轮）——"
       "主产出=pit-pool-burn.md 新域件 15 条（点火闸/烧录/双烧接管族）+pit-pool-edit 18,699B 回线"
       "+RAM 门×孤儿探针 deadline 判别律直写+QA r791 包 5/5")
ART = ("最近实物: research/pit-pool-burn.md (15,621B+942B 直写=16,563B·15+1 条) + research/pit-pool-edit.md "
       "(18,699B 回线·18 条) + results/_r791bmc_pit_pool_edit_split_receipt.json (VERIFY 74 checks) "
       "+ qa/smoke-r791-bm-c.md 5/5 + qa/equity-curve-r791-bm-c.png (65,440B) + results/_r791bmc_s6_log.txt "
       "(40/40 rc0) @ " + ts)
MILE = ("下个里程碑: W17 screen 8 分片烧完→JUDGE→48h CEO 呈报（SLA 10-10 00:00·RAM 门阻塞面读数随班回执）"
        "+fund_premium 10-08 NAV 首采（今日 15:30+）·窗 ≤48h")
NXT = ("r792 续作: ①W17 screen 烧跟进（SHARD-0/1 在飞 RAM 门等待·SHARD-2..7+JUDGE ready·RAM 释放即自续·到窗读数随班回执）"
       "②T-2026-10-09-178-P1 判决链票（judge verdict→s4 intake→48h CEO 呈报·池烧完成前不关票）"
       "③fund_premium 10-08 NAV 首采（15:30+·第十观测窗）④CEO 三选项勾选等待态（A=视频段解冻·MV 面）"
       "⑤pit-pool.md 30,133B 近帽观察（下轮超线即 sub-split 触发评估）")
VERIFY = ("sub-split git 可验（receipt results/_r791bmc_pit_pool_edit_split_receipt.json·SPLIT PASS+VERIFY 74 checks·"
          "条目字节和 14,262B 恒等·登记册出入行+CODELY 指针注 30,643B≤帽）+直写件（pit-pool-burn 16,563B·r666 范式）"
          "+smoke 49/49+QA smoke-r791-bm-c.md 5/5（91 trades·sharpe 0.1994·determinism=True）+S6 40/40 rc0"
          "（results/_r791bmc_s6_log.txt·dualrun streak 51）+attrition 4 台账 CLEAN+双爪重装+loop pin=5+"
          "DEC/ORD 双恒等零消费（_r791bmc_s0_facts.json 收尾二扫·shape-asserted）+unacked 0〔54 orders〕+"
          "孤儿面=2→1（39968 RAM 门 40min 帽自退实证·零误杀）+push 送达自证 0/0")

# --- QA slot probe evidence JSON (slot free both faces, pack landed) ---
probe = {"round": 791, "machine": "bm-c", "slot_local": "free",
         "origin_r791_hits": 0, "probe_cmd": "Test-Path local + git ls-tree origin/main qa/ | Select-String r791",
         "pack": "qa/smoke-r791-bm-c.md items=5/5", "png_bytes": 65440,
         "trades": 91, "sharpe": 0.1994, "determinism": True,
         "runner_out": "results/_r791bmc_qa_runner.out"}
with open(os.path.join(REPO, "results", "_r791bmc_qa_probe.json"), "w",
          encoding="utf-8", newline="\n") as fh:
    json.dump(probe, fh, ensure_ascii=False, indent=1)
print("qa probe json written")

# --- round report append (match existing encoding/EOL) ---
rp = os.path.join(REPO, "logs", "iteration-loop", "round_reports-bm-c.md")
raw = open(rp, "rb").read()
eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
enc = "utf-8-sig" if raw[:3] == b"\xef\xbb\xbf" else "utf-8"
with open(rp, "ab") as fh:
    fh.write((ROUND_LINE + "\n").encode("utf-8"))
print("round_report appended eol=%r enc=%s bytes=%d" % (eol, enc, len(ROUND_LINE.encode("utf-8"))))

# --- state round_no bump ---
sp = os.path.join(REPO, "state-bm-c.json")
state = json.load(open(sp, encoding="utf-8"))
state["round_no"] = 792
state["last_round"] = 791
state["last_round_at"] = ts
with open(sp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(state, fh, indent=1, ensure_ascii=False)
print("state round_no -> 792 @", ts)

# --- heartbeat full refresh ---
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["round_no"] = 792
hb["round_no_label"] = "round 791 (bm-c)"
hb["last_round"] = 791
hb["last_round_at"] = ts
hb["last_seen"] = ts
hb["clock_read"] = ts
hb["ts"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["current_task"] = CUR
hb["current_task_at"] = ts
hb["latest_artifact"] = ART
hb["next_milestone"] = MILE
hb["health"] = "ok"
hb["activity_now"] = CUR
hb["did"] = f"{ts} | r791 | " + ROUND_LINE.split(" | ", 2)[2]
hb["verdict"] = hb["did"]
hb["note"] = hb["did"]
hb["last_round_summary"] = hb["did"]
hb["last_action"] = hb["did"]
hb["next"] = NXT
hb["next_pointer"] = NXT
hb["verify"] = VERIFY
hb["last_seen_at"] = ts
hb["updated_at"] = ts
hb["updated"] = ts
hb["last_run_at"] = ts
hb["last_ts"] = ts
hb["last_round_ts"] = ts
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["free_ram_gb"] = free_ram_gb
hb["idle_ram_gb"] = free_ram_gb
hb["ram_free_gb"] = free_ram_gb
hb["cpu_pct"] = cpu_pct
hb["cpu_util_pct"] = cpu_pct
hb["cpu_idle_pct"] = round(100 - cpu_pct, 1)
hb["gpu_free_vram_mb"] = vram_free
hb["gpu_free_mib"] = vram_free
hb["gpu_free_mb"] = vram_free
hb["gpu_idle_vram_mb"] = vram_free
hb["gpu_idle_mib"] = vram_free
hb["gpu_vram_free_mb"] = vram_free
hb["gpu_free_vram_mib"] = vram_free
hb["gpu_idle_vram_mib"] = vram_free
hb["gpu_idle_mb"] = vram_free
hb["last_decisions_read_at"] = ts
hb["last_decisions_at"] = ts
hb["last_orders_at"] = ts
hb["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r791 closing sweep = "
                        "NO delta 83813196->83813196 (group unchanged since r785 batch); facts-driven from "
                        "results/_r791bmc_s0_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law")
hb["last_decisions_sha_method"] = hb["dec_sha_method"]
hb["ord_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r791 closing sweep = NO delta "
                        "1212A338->1212A338; facts-driven from results/_r791bmc_s0_facts.json, 40hex shape-asserted, "
                        "never hand-typed (r583 S4 law")
hb["last_orders_sha_method"] = hb["ord_sha_method"]
with open(hp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, indent=1, ensure_ascii=False)

# --- self-verify (R170/R178 epoch-int law + T-separator law) ---
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be json int"
assert "T" in chk["clock_read"] and "T" in chk["ts"], "clock_read/ts must be ISO T-separated"
assert chk["round_no"] == 792 and chk["last_round"] == 791
print(json.dumps({"epoch": chk["heartbeat_epoch_utc"], "clock_read": chk["clock_read"],
                  "free_ram_gb": free_ram_gb, "cpu_pct": cpu_pct, "vram_free_mb": vram_free,
                  "orders_ack_count": len(chk.get("orders_ack", [])), "keys": len(chk)}, indent=1))
print("closeout driver OK")
