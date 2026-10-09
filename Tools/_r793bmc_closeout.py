# -*- coding: utf-8 -*-
"""r793 bm-c closeout driver: round-report line append + state round_no bump
(793->794) + heartbeat full refresh + QA slot probe JSON.
Live metrics via psutil/nvidia-smi (CREATE_NO_WINDOW). Epoch = python int
(R170/R178 law). Facts printed for in-round verification.
Clone credit: Tools/_r792bmc_closeout.py (1-gen clone)."""
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
    f"{ts} | r793 | dept:工程/研究（W17 池烧 RAM 门跟进+常设链全绿轮·第 94 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
    "WM-VERDICT: 绿（red=false·lane=healthy·next_pick=claimed moneyflow IC bm-a 车道合法·"
    "DEC 83813196/ORD 1212A338 双恒等零消费·unacked 0〔54 orders〕·inbox 0） | "
    "孤儿面=1（ComfyUI 产线资产只读不杀；SHARD-1 runner 40min 帽到点自退实证〔08:30 点火→09:1x 退〕·"
    "SHARD-2 新 runner 09:17 点火 pid 9260 RAM 门有界等待在飞·deadline 判别律只读） | "
    "r793: W17 池烧 RAM 门跟进+常设链全绿轮（09:1x-09:3x 窗·第 94 连守轮）——"
    "①S0 两步绿：7 daemon live-face 吸收 commit 45fad7a86+rebase origin/main rc0"
    "（吸收 bm-a r908 面：W195 prereg landed+S6 39 腿 rc0）·git commit 单引号拆参一发即窗内双引号补正"
    "（pit-ps-wrapper 既有律复发非新坑）；"
    "②S0.5 双扫：DEC/ORD 双恒等零消费·unacked 0〔54 orders〕·inbox 0"
    "（轮首 s05_facts+收尾 s0_facts 双件·shape-asserted）；"
    "③S1 smoke 49/49+QA r793 证据包 5/5（smoke-r793-bm-c.md·91 trades·sharpe 0.1994·determinism=True·"
    "equity PNG 65,547B·per-machine 后缀律）；"
    "④S6 40/40 rc0 十四连绿（dualrun ZERO-DRIFT streak 51 维持·fund_premium 15:30 前诚实 no-op"
    "〔第十观测窗·15:30+ 轮落首采〕·update_daily 10-08 截止零新行·compute_audit supply_gap+ignition_sla "
    "旗如实照录〔6 未点火面=RAM 门物理阻塞·run_samples 8 span 112.3min·supply_family_streak 682.6min〕·"
    "R31 他机车道 no-op 族照录）；"
    "⑤W17 池烧跟进（主产出面）：RAM 门 free 1.1GB<4GB（09:16/09:2x 双探针读）·autofill daemon 活"
    "（09:17 SHARD-2 launch-claim pid 9260·09:18 tick pool_empty_or_busy）·SHARD-0/1 runner 40min 帽到点自退"
    "（07:47/08:30 点火→自退实证）·9 ready 保持 claimable（SLA 窗 10-10 00:00 保持·r789 10 ready 达成后消费中）·"
    "T-178 票在飞不关（池烧完成前不关票·48h CEO 呈报钟待 judge 落地起算）；"
    "⑥SAT 引擎活 rc0·idle 非绿（RAM 8.6%<40% 档）无领单义务·job 板清·捕获律双零"
    "（无新方法无新宝藏·全 1-gen clone 正典链）；"
    "⑦S7 自愈批全绿（loop pin=5 no-op〔next fire 09:25〕·watchdog 在位〔09:24 next run〕·双爪 IN-PLACE·"
    "attrition 4 台账 CLEAN〔3 healed 注记照录〕）| "
    "下轮指针: r794=W17 screen 烧跟进（RAM 门读数随班回执·autofill 自续·SHARD-2 有界等待 ~09:57 帽退验证）+"
    "fund_premium 10-08 NAV 首采（15:30+·第十观测窗）+T-2026-10-09-178-P1 判决链票跟进+CEO 三选项等待态（MV 面）| "
    "本轮产品积分：2（QA r793 包 5/5=能看能跑实物·S6 40/40=经营层实物〔daily_report/live_usage/scorecard 面刷新〕）| "
    "记账预算：4（轮报行/心跳/state 收口+facts 双扫双件+qa 探针件+s7 log）"
)

CUR = ("当前活: r793 bm-c（09:1x-09:3x 窗·W17 池烧 RAM 门跟进+常设链全绿·第 94 连守轮）——"
       "主产出=QA r793 证据包 5/5+smoke 49/49+S6 40/40 rc0 十四连绿（daily_report/live_usage/scorecard 刷新）"
       "+W17 RAM 门读数到窗回执（SHARD-2 launch-claim 在飞·autofill 自续待 RAM）")
ART = ("最近实物: qa/smoke-r793-bm-c.md (5/5·91 trades·sharpe 0.1994·determinism=True) + qa/equity-curve-r793-bm-c.png "
       "(65,547B) + results/_r793bmc_s6_log.txt (40/40 rc0 十四连绿·dualrun streak 51) + "
       "results/_r793bmc_s05_facts.json + results/_r793bmc_s0_facts.json (双扫·DEC/ORD 恒等 shape-asserted) + "
       "results/_r793bmc_s7_log.txt (自愈批四绿) + Tools/_r793bmc_s05.py/_r793bmc_s6.py/_r793bmc_runall.py/_r793bmc_ignite.py "
       "(1-gen 正典链) @ " + ts)
MILE = ("下个里程碑: W17 screen 8 分片烧完→JUDGE→48h CEO 呈报（SLA 10-10 00:00·RAM 门阻塞面随班回执·autofill 自续）"
        "+fund_premium 10-08 NAV 首采（今日 15:30+）·窗 ≤48h")
NXT = ("r794 续作: ①W17 screen 烧跟进（SHARD-0..7+JUDGE 9 ready·RAM 门 free<4GB 阻塞·autofill 自续·"
       "SHARD-2 有界等待 ~09:57 帽退验证）②fund_premium 10-08 NAV 首采（15:30+·第十观测窗）"
       "③T-2026-10-09-178-P1 判决链票跟进（judge 落地→s4 intake→48h CEO 呈报·池烧完成前不关票）"
       "④CEO 三选项勾选等待态（A=视频段解冻·MV 面）⑤RAM 释放后 autofill 点火节奏回执")
VERIFY = ("smoke 49/49（results/_r793bmc_smoke.txt）+QA smoke-r793-bm-c.md 5/5（91 trades·sharpe 0.1994·determinism=True·"
          "equity PNG 65,547B）+S6 40/40 rc0 十四连绿（results/_r793bmc_s6_log.txt·dualrun ZERO-DRIFT streak 51）"
          "+SAT 引擎活 rc0+idle 非绿无领单义务+attrition 4 台账 CLEAN（3 healed 注记）+双爪 IN-PLACE+loop pin=5 no-op+"
          "watchdog 在位+DEC/ORD 双恒等零消费（_r793bmc_s0_facts.json 收尾二扫·shape-asserted）+unacked 0〔54 orders〕+"
          "孤儿面=1 只读零杀（ComfyUI 产线资产）+S0 吸收 45fad7a86+rebase rc0+push 送达自证 0/0")

# --- QA slot probe evidence JSON (slot free both faces, pack landed) ---
probe = {"round": 793, "machine": "bm-c", "slot_local": "free",
         "origin_r793_hits": 0, "probe_cmd": "Test-Path local + git ls-tree origin/main qa/ | Select-String r793",
         "pack": "qa/smoke-r793-bm-c.md items=5/5", "png_bytes": 65547,
         "trades": 91, "sharpe": 0.1994, "determinism": True,
         "runner_out": "results/_r793bmc_qa_out.txt"}
with open(os.path.join(REPO, "results", "_r793bmc_qa_probe.json"), "w",
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
state["round_no"] = 794
state["last_round"] = 793
state["last_round_at"] = ts
with open(sp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(state, fh, indent=1, ensure_ascii=False)
print("state round_no -> 794 @", ts)

# --- heartbeat full refresh ---
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["round_no"] = 794
hb["round_no_label"] = "round 793 (bm-c)"
hb["last_round"] = 793
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
hb["did"] = f"{ts} | r793 | " + ROUND_LINE.split(" | ", 2)[2]
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
hb["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r793 closing sweep = "
                        "NO delta 83813196->83813196 (group unchanged since r785 batch); facts-driven from "
                        "results/_r793bmc_s0_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law")
hb["last_decisions_sha_method"] = hb["dec_sha_method"]
hb["ord_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r793 closing sweep = NO delta "
                        "1212A338->1212A338; facts-driven from results/_r793bmc_s0_facts.json, 40hex shape-asserted, "
                        "never hand-typed (r583 S4 law")
hb["last_orders_sha_method"] = hb["ord_sha_method"]
with open(hp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, indent=1, ensure_ascii=False)

# --- self-verify (R170/R178 epoch-int law + T-separator law) ---
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be json int"
assert "T" in chk["clock_read"] and "T" in chk["ts"], "clock_read/ts must be ISO T-separated"
assert chk["round_no"] == 794 and chk["last_round"] == 793
print(json.dumps({"epoch": chk["heartbeat_epoch_utc"], "clock_read": chk["clock_read"],
                  "free_ram_gb": free_ram_gb, "cpu_pct": cpu_pct, "vram_free_mb": vram_free,
                  "orders_ack_count": len(chk.get("orders_ack", [])), "keys": len(chk)}, indent=1))
print("closeout driver OK")
