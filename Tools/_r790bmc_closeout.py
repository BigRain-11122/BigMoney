# -*- coding: utf-8 -*-
"""r790 bm-c closeout driver (dead-session adoption continuation):
round-report line append + state round_no bump + heartbeat full refresh.
Live metrics via psutil/nvidia-smi (CREATE_NO_WINDOW). Epoch = python int
(R170/R178 law). Facts printed for in-round verification."""
import json, time, subprocess, sys, os, datetime, io

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%dT%H:%M:%S") + ("+%02d:%02d" % (now.utcoffset().h // 3600 if hasattr(now.utcoffset(), 'h') else 8, 0) if False else now.strftime("%z")[:3] + ":" + now.strftime("%z")[3:])
# simpler robust ISO with +08:00 shape
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
    f"{ts} | r790 | dept:工程/研究（死会话收养+W17 生成腿落地+claim-collision 治理收口轮·第 91 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证·merge 单停收口随批） | "
    "WM-VERDICT: 绿（red=false·probe=insufficient_history 窗 n=1 诚实如实·W17 screen 烧录在飞=合法活批·regime ORANGE shadow·lane=healthy） | "
    "孤儿面=1（ComfyUI 产线资产·只读不杀·round-zero 探针新读） | "
    "r790: 死会话收养+W17 池烧跟进轮（07:07-07:53 前会话猝死于 S7 收口前+08:05 本会话收养续作同轮收口）——"
    "①前段主产出（收养核验后计入）：W17-GENERATE 烧录落地（autofill 常轨点火 07:00·173×8=1384 paired cells·"
    "w17_cells.json 217KB+ledger row sha16 09476ecc5beb2304·elapsed 2.5s 零引擎格烧）+screen-prep 1253 starts 五门 PASS"
    "（prep_state.json 07:15）+runner selftest 复跑 21/21（07:38）+claim-collision 治理（daemon git 无超时坑 12min fetch "
    "挂起→tick 240s 帽杀留 git 孙进程孤儿=dispatcher 单实例停摆→60s 硬超时焊入 autofill _git；未送达 commit 群 ahead=3 "
    "vs bm-a 07:20:38 GENERATE claim 竞窗→absorb a4a4390e3→merge 664c54a60 per-face max-merge〔409 done+9 ready·"
    "W16-GENERATE 同形〕+jsonl 双指针 ts 归并→push 后 daemon claim_lost_yield 自解锁复燃 screen-0 点火 07:48:47 实证）"
    "+S4 固化四件（E50 未送达 claim 撞车交付法卡+TREASURE 出入行+pit-spawn 直写行〔主件 386B 红线 r666/r747 直写范式〕"
    "+HANDOVER 五倍数核对 r771-r790 窗·三 stamp OVERDUE-BACKLOG 披露）；"
    "②S1 smoke 49/49（07:48 fresh·0 FAIL）+QA smoke-r790-bm-c.md 5/5（91 trades·sharpe 0.1994·determinism=True·"
    "equity PNG 同批·per-machine 后缀律）；"
    "③S6 40/40 rc0 十一连绿（results/_r790bmc_s6_log.txt·dualrun ZERO-DRIFT streak 51·compute_audit 旗=ignition_sla"
    "〔8 分片 ready 未点火=RAM 门 1.7GB<4GB 顺序烧诚实·supply_family_streak 593.5min 如实载〕·regime ORANGE shadow·"
    "fund_premium 15:30 前诚实 no-op·update_daily 10-08 截止零新行）；"
    "④收养收口段（本会话）：round-zero 孤儿探针（孤儿面=1 同判 ComfyUI 只读）+收养核验（smoke/QA/S6/内容四件 diff 全读面核）"
    "+收尾二扫（DEC 83813196/ORD 1212A338 双恒等零消费·unacked 0〔54 orders〕·inbox 0）+S7 自愈（loop pin=5 no-op·"
    "watchdog 重装首发 08:17·双爪 LF 归一重装·attrition 4 台账 CLEAN〔3 历史 shrink healed 注记照录〕）+"
    "merge origin/main 单停收口（bm-a r905 系 5 提交：W194 五面冻结 82670b0ba+引擎自燃 bafcafb04+双 round-zero 态面·"
    "resolver per-face max-merge 收口+merged-tree n1 selftest）→push 送达自证 0/0；"
    "⑤W17 池烧态读数：SCREEN-SHARD-0 07:47:31 点火在飞（pid 39968·keepalive 08:00:08）·SHARD-1..7+JUDGE ready 在池"
    "（RAM 门顺序烧·autofill last_tick 08:10:32 pool_empty_or_busy 诚实态）·SLA 窗 10-10 00:00 | "
    "下轮指针: r791=W17 screen 分片 1-7 顺序烧跟进+JUDGE（到窗读数随班回执）+T-2026-10-09-178-P1 判决链票跟进"
    "（judge verdict→s4 intake→48h CEO 呈报）+fund_premium 10-08 NAV 首采（15:30+·第十观测窗）+维护债=pit-pool-edit.md "
    "32,616B 超线让位窗 sub-split（下让位窗即办）+CEO 三选项勾选等待态（MV 面）"
)

CUR = ("当前活: r790 bm-c（07:0x-08:1x 双段合成·死会话收养+W17 生成腿落地+claim-collision 治理收口·第 91 连守轮）——"
       "主产出=W17-GENERATE 1384 paired cells 落地+w17_cells.json+claim-collision merge 治愈（409 done+9 ready）"
       "+autofill _git 60s 硬超时焊+E50 方法论卡")
ART = ("最近实物: results/trial_labor_w17/w17_cells.json (1384 paired cells·07:14) + results/trial_labor_w17/prep_state.json "
       "(1253 starts·07:15) + merge 664c54a60 (claim-collision per-face max-merge) + knowledge/METHODOLOGY_ASSETS.md (E50 卡) "
       "+ research/HANDOVER.md (r771-r790 五倍核) @ " + ts)
MILE = ("下个里程碑: r791=W17 screen 8 分片顺序烧跟进（SHARD-0 在飞 07:47 起·SHARD-1..7+JUDGE ready 在池·SLA 10-10 00:00）"
        "→JUDGE→s4 intake→48h CEO 呈报+fund_premium 10-08 NAV 首采（今日 15:30+）·窗 ≤48h")
NXT = ("r791 续作: ①W17 screen 分片 1-7 顺序烧跟进+JUDGE（到窗读数随班回执·RAM 门单发顺序烧设计内）"
       "②T-2026-10-09-178-P1 判决链票跟进（judge verdict→s4 intake→48h CEO 呈报·池烧完成前不关票）"
       "③fund_premium 10-08 NAV 首采（15:30+·第十观测窗）④维护债=pit-pool-edit.md 32,616B 超线让位窗 sub-split（下让位窗即办）"
       "⑤CEO 三选项勾选等待态（A=视频段解冻·MV 面）+T-177 regime-5 标签器消费面跟进（bm-a 车道）")
VERIFY = ("W17 generate+screen-prep+runner selftest 21/21 git 可验（w17_cells.json 1384 cells+prep_state.json 1253 starts+"
          "results/_r790bmc_w17_selftest_rerun.txt 21/21+results/_r790bmc_w17_generate_out.txt）+claim-collision 治理 git 可验"
          "（merge 664c54a60+resolver Tools/_r790bmc_merge_resolver.py+receipt results/_r790bmc_merge_resolver.json·"
          "409 done+9 ready·marker CLEAN）+smoke 49/49（results/_r790bmc_smoke_out.txt）+QA smoke-r790-bm-c.md 5/5"
          "（91 trades·sharpe 0.1994·determinism=True）+S6 40/40 rc0（results/_r790bmc_s6_log.txt·dualrun streak 51）+"
          "attrition 4 台账 CLEAN+双爪重装+loop pin=5+收尾二扫 DEC/ORD 双恒等零消费 unacked 0〔54 orders〕+孤儿面=1 只读"
          "（results/_orphan_face_probe.bm-c.json）+merge origin/main 单停收口（W194 冻结 82670b0ba 收入）+push 送达自证 0/0")

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
state["round_no"] = 791
state["last_round_at"] = ts
with open(sp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(state, fh, indent=1, ensure_ascii=False)
print("state round_no -> 791 @", ts)

# --- heartbeat full refresh ---
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["round_no"] = 791
hb["round_no_label"] = "round 790 (bm-c)"
hb["last_round"] = 790
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
hb["did"] = f"{ts} | r790 | " + ROUND_LINE.split(" | ", 2)[2]
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
hb["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r790 closing sweep = "
                        "NO delta 83813196->83813196 (group unchanged since r785 batch); facts-driven from "
                        "results/_r790bmc_s7_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law")
hb["last_decisions_sha_method"] = hb["dec_sha_method"]
hb["ord_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r790 closing sweep = NO delta "
                        "1212A338->1212A338; facts-driven from results/_r790bmc_s7_facts.json, 40hex shape-asserted, "
                        "never hand-typed (r583 S4 law")
hb["last_orders_sha_method"] = hb["ord_sha_method"]
with open(hp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, indent=1, ensure_ascii=False)

# --- self-verify (R170/R178 epoch-int law + T-separator law) ---
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be json int"
assert "T" in chk["clock_read"] and "T" in chk["ts"], "clock_read/ts must be ISO T-separated"
assert chk["round_no"] == 791 and chk["last_round"] == 790
print(json.dumps({"epoch": chk["heartbeat_epoch_utc"], "epoch_is_int": isinstance(chk["heartbeat_epoch_utc"], bool) is False and isinstance(chk["heartbeat_epoch_utc"], int), "clock_read": chk["clock_read"], "free_ram_gb": free_ram_gb, "cpu_pct": cpu_pct, "vram_free_mb": vram_free, "orders_ack_count": len(chk.get("orders_ack", [])), "keys": len(chk)}, indent=1))
print("closeout driver OK")
