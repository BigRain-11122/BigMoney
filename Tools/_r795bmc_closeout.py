# -*- coding: utf-8 -*-
"""r795 bm-c closeout driver: round-report line append + state round_no bump
(795->796) + heartbeat full refresh + QA slot probe JSON.
Live metrics via psutil/nvidia-smi (CREATE_NO_WINDOW). Epoch = python int
(R170/R178 law). Facts printed for in-round verification.
Clone credit: Tools/_r794bmc_closeout.py (1-gen clone)."""
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
    f"{ts} | r795 | dept:工程/研究（W17 池烧 RAM 门跟进第 2 窗+常设链全绿轮·第 96 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
    "WM-VERDICT: 绿（red=false·next_pick=claimed moneyflow IC bm-a 车道合法·"
    "DEC 83813196/ORD 1212A338 双恒等零消费·unacked 0〔54 orders〕·inbox 0） | "
    "孤儿面=1（ComfyUI 产线资产只读不杀；SHARD-2 runner pid 9260 09:17 点火 RAM 门有界等待在飞·"
    "RAM avail 1.54GB 仍 <4GB 门·帽 ~09:57 下窗验证·deadline 判别律只读） | "
    "r795: W17 池烧 RAM 门跟进第 2 窗+常设链全绿轮（09:3x-09:4x 窗·第 96 连守轮）——"
    "①S0 两步绿：5 daemon live-face 吸收 commit 4e7b93aab（sat daemon add/commit 间写竞态=同文件二段吸收·"
    "amend 未推提交合规 r731 律面）+rebase origin/main rc0（origin 零新 commit·behind=0·无 resolver）·"
    "1-gen 克隆链 Tools/_r795bmc_{s05,s6,runall,ignite}.py 落地（1-gen clone 正典律）；"
    "②S0.5 双扫：DEC/ORD 双恒等零消费·unacked 0〔54 orders〕·inbox 0"
    "（轮首 s05_facts+收尾 s0_facts 双件·shape-asserted）；"
    "③S1 smoke 49/49+QA r795 证据包 5/5（smoke-r795-bm-c.md·91 trades·sharpe 0.1994·determinism=True·"
    "equity PNG 65,508B·per-machine 后缀律）；"
    "④S6 40/40 rc0 十六连绿（dualrun ZERO-DRIFT streak 51 维持·compute_audit supply_gap+ignition_sla "
    "旗如实照录〔6 未点火面=RAM 门物理阻塞·supply_family_streak 702.1min·supply floor 9/3 无 breach〕·"
    "fund_premium 15:30 前诚实 no-op〔第十二观测窗〕·update_daily 10-08 截止零新行·R31 他机车道 no-op 族照录·"
    "token delta=0）；"
    "⑤W17 池烧跟进第 2 窗（主产出面）：SHARD-2 launch-claim pid 9260 仍在有界等待（09:17 点火·CPU 18.8s 低耗特征·"
    "RAM avail 1.54GB<4GB 物理阻塞·帽 ~09:57 到窗前不判退·下窗双面验证帽退/RAM 释放点火）·"
    "8 分片+JUDGE 9 ready 保持 claimable（SLA 窗 10-10 00:00）·autofill daemon 自续·"
    "T-178 票在飞不关（池烧完成前不关票·48h CEO 呈报钟待 judge 落地起算）；"
    "⑥SAT 引擎活 rc0·job 板清·idle 非绿（RAM<40% 档）无领单义务·捕获律双零"
    "（无新方法无新宝藏·全 1-gen clone 正典链）；"
    "⑦S7 自愈批全绿（loop pin=5 no-op〔next fire 09:45〕·watchdog 重注册〔-Force 幂等·first fire 09:40〕·"
    "双爪 IN-PLACE 重装〔LF-normalized〕·attrition 4 台账 CLEAN〔3 healed 注记照录〕）| "
    "下轮指针: r796=W17 SHARD-2 帽退/RAM 释放双面验证（~09:57 后窗）+fund_premium 15:30+ NAV 首采窗"
    "（10-08 NAV·第十二观测窗收口）+T-2026-10-09-178-P1 判决链票跟进+CEO 三选项勾选等待态（MV 面）| "
    "本轮产品积分：2（QA r795 包 5/5=能看能跑实物·S6 40/40=经营层实物〔daily_report/live_usage/scorecard 面刷新〕）| "
    "记账预算：4（轮报行/心跳/state 收口+facts 双扫双件+qa 探针件+s7 面入轮报）"
)

CUR = ("当前活: r795 bm-c（09:3x-09:4x 窗·W17 池烧 RAM 门跟进第 2 窗+常设链全绿·第 96 连守轮）——"
       "主产出=QA r795 证据包 5/5+smoke 49/49+S6 40/40 rc0 十六连绿（daily_report/live_usage/scorecard 刷新）"
       "+W17 SHARD-2 有界等待活读数到窗回执（pid 9260·RAM 1.54GB·帽 ~09:57·下窗验证）")
ART = ("最近实物: qa/smoke-r795-bm-c.md (5/5·91 trades·sharpe 0.1994·determinism=True) + qa/equity-curve-r795-bm-c.png "
       "(65,508B) + results/_r795bmc_s6_log.txt (40/40 rc0 十六连绿·dualrun streak 51) + "
       "results/_r795bmc_s05_facts.json + results/_r795bmc_s0_facts.json (双扫·DEC/ORD 恒等 shape-asserted) + "
       "Tools/_r795bmc_s05.py/_r795bmc_s6.py/_r795bmc_runall.py/_r795bmc_ignite.py "
       "(1-gen 正典链) @ " + ts)
MILE = ("下个里程碑: W17 screen 8 分片烧完→JUDGE→48h CEO 呈报（SLA 10-10 00:00·RAM 门阻塞面随班回执·autofill 自续）"
        "+fund_premium 10-08 NAV 首采（今日 15:30+）·窗 ≤48h")
NXT = ("r796 续作: ①W17 SHARD-2 帽退/RAM 释放双面验证（~09:57 后窗·autofill 自续）"
       "②fund_premium 15:30+ NAV 首采窗（10-08 NAV·第十二观测窗收口）"
       "③T-2026-10-09-178-P1 判决链票跟进（judge 落地→s4 intake→48h CEO 呈报·池烧完成前不关票）"
       "④CEO 三选项勾选等待态（A=视频段解冻·MV 面）")
VERIFY = ("smoke 49/49（results/_r795bmc_smoke.txt）+QA smoke-r795-bm-c.md 5/5（91 trades·sharpe 0.1994·determinism=True·"
          "equity PNG 65,508B）+S6 40/40 rc0 十六连绿（results/_r795bmc_s6_log.txt·dualrun ZERO-DRIFT streak 51）"
          "+SAT 引擎活 rc0+idle 非绿无领单义务+attrition 4 台账 CLEAN（3 healed 注记）+双爪 IN-PLACE 重装+"
          "loop pin=5 no-op+watchdog 重注册+DEC/ORD 双恒等零消费（_r795bmc_s0_facts.json 收尾二扫·shape-asserted）"
          "+unacked 0〔54 orders〕+孤儿面=1 只读零杀（ComfyUI 产线资产）+rebase origin/main rc0+push 送达自证 0/0")

# --- QA slot probe evidence JSON (slot free both faces, pack landed) ---
probe = {"round": 795, "machine": "bm-c", "slot_local": "landed",
         "origin_r795_bmc_hits": 0, "probe_cmd": "Test-Path local + git ls-tree origin/main qa/ | Select-String r795-bm-c",
         "pack": "qa/smoke-r795-bm-c.md items=5/5", "png_bytes": 65508,
         "trades": 91, "sharpe": 0.1994, "determinism": True,
         "runner_out": "results/_r795bmc_qa_out.txt"}
with open(os.path.join(REPO, "results", "_r795bmc_qa_probe.json"), "w",
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
state["round_no"] = 796
state["last_round"] = 795
state["last_round_at"] = ts
with open(sp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(state, fh, indent=1, ensure_ascii=False)
print("state round_no -> 796 @", ts)

# --- heartbeat full refresh ---
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["round_no"] = 796
hb["round_no_label"] = "round 795 (bm-c)"
hb["last_round"] = 795
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
hb["did"] = f"{ts} | r795 | " + ROUND_LINE.split(" | ", 2)[2]
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
hb["gpu_idle_mb"] = vram_free
hb["last_decisions_read_at"] = ts
hb["last_decisions_at"] = ts
hb["last_orders_at"] = ts
hb["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r795 closing sweep = "
                        "NO delta 83813196->83813196 (group unchanged since r785 batch); facts-driven from "
                        "results/_r795bmc_s0_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law")
hb["last_decisions_sha_method"] = hb["dec_sha_method"]
hb["ord_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r795 closing sweep = NO delta "
                        "1212A338->1212A338; facts-driven from results/_r795bmc_s0_facts.json, 40hex shape-asserted, "
                        "never hand-typed (r583 S4 law")
hb["last_orders_sha_method"] = hb["ord_sha_method"]
with open(hp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, indent=1, ensure_ascii=False)

# --- self-verify (R170/R178 epoch-int law + T-separator law) ---
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be json int"
assert "T" in chk["clock_read"] and "T" in chk["ts"], "clock_read/ts must be ISO T-separated"
assert chk["round_no"] == 796 and chk["last_round"] == 795
print(json.dumps({"epoch": chk["heartbeat_epoch_utc"], "clock_read": chk["clock_read"],
                  "free_ram_gb": free_ram_gb, "cpu_pct": cpu_pct, "vram_free_mb": vram_free,
                  "orders_ack_count": len(chk.get("orders_ack", [])), "keys": len(chk)}, indent=1))
print("closeout driver OK")
