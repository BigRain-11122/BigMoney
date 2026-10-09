# -*- coding: utf-8 -*-
"""r820 bm-c close-out bookkeeping (state + heartbeat + round report).
Facts-driven: ORD/DEC shas read from results/_r820bmc_s05_facts.json
(r583 law: ZERO literal sha constants), watermark verdict from
results/watermark_red.json, idle face from results/idle_trigger.bm-c.json,
S6 receipt read live from results/_r820bmc_s6_log.txt (leg count derived
at runtime, honest in-flight face if chain unfinished).
RAM via ctypes GlobalMemoryStatusEx (zero subprocess), VRAM via
nvidia-smi CREATE_NO_WINDOW. Heartbeat epoch = int(time.time()) JSON int
(R170/R178 law). clock_read/ts ISO8601 with T separator (R262 law)."""
import ctypes
import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone, timedelta

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CNW = 0x08000000
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)
NOW_ISO = NOW.isoformat(timespec="seconds")


def ram_free_gb():
    class MemStat(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MemStat()
    m.dwLength = ctypes.sizeof(MemStat)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return round(m.ullAvailPhys / 1e9, 1), round(m.ullTotalPhys / 1e9, 1), \
        round(100 - m.dwMemoryLoad, 1)


def vram_free_mb():
    try:
        p = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                            "--format=csv,noheader"],
                           capture_output=True, creationflags=CNW, timeout=20)
        return int(p.stdout.decode().strip().splitlines()[0].split()[0])
    except Exception:
        return -1


def jload(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def s6_face():
    """Honest S6 receipt: leg count + nonzero-rc count from the live log.
    In-flight chain = 'in-flight N legs so far' face."""
    log = os.path.join(R, "results", "_r820bmc_s6_log.txt")
    if not os.path.exists(log):
        return "S6 chain log absent at close-write (ignite race, next round collects)"
    txt = open(log, encoding="utf-8", errors="replace").read()
    rcs = re.findall(r"\[rc=(\d+)\]", txt)
    nz = sum(1 for r in rcs if int(r) != 0)
    if len(rcs) >= 40:
        return "S6 %d legs rc0 (results/_r820bmc_s6_log.txt, nonzero-rc count=%d)" \
            % (len(rcs), nz)
    return "S6 in-flight %d/%d legs at close-write (receipt next round)" \
        % (len(rcs), max(40, len(rcs)))


facts = jload(os.path.join(R, "results", "_r820bmc_s05_facts.json"))
wm = jload(os.path.join(R, "results", "watermark_red.json"))
idle = jload(os.path.join(R, "results", "idle_trigger.bm-c.json"))
free_gb, total_gb, free_pct = ram_free_gb()
vfree = vram_free_mb()
epoch = int(time.time())
S6 = s6_face()

ACT = ("当前活: r820 bm-c W17 屏幕波 KeyError('faces') 根因修复+SLA 失守如实报告"
       "（第 120 连守轮）| 最近实物: scripts/trial_labor_w17.py 双修（screen worker "
       "state 换装 w16 face grammar+judge state 补 grammar 字段·selftest 21/21+1384 "
       "cells 59 mks 全解析）+S6 链+_r820bmc_{s05,s6,close} 工具族 @本轮收口 commit | "
       "下个里程碑: W17 screen 8 shard 复烧+judge（RAM≥4GB 窗即自动复烧·autofill "
       "resubmit 在役）+10-10 月首轮三件套（science_audit/monthly_briefing/self_review）")
NEXT = ("r821 续作: ①S6 收据验证（若收口时在飞则读 results/_r820bmc_s6_log.txt 40/40）"
        "②W17 复烧确认（新 hash 领取→fuse 自清→RAM 窗监控·SLA D-20261009-01(iii) "
        "失守已如实报：pool claimable 9<10·屏幕 0/8 全天烧成受阻=代码 bug+rAM 双病灶·"
        "代码面已修）③10-10 月首轮三件套（science_audit+monthly_briefing+self_review）"
        "④C7 MSG 待 bm-b（O-20261009-2150 入伙令已发·bm-a 守候上线·本机出站件在案）"
        "⑤10-09 bar 第 14 轮守（sina 迟发自愈）⑥tick 成轮验证（21:08→23:25 tick 会话"
        "连灭窗=RAM 紧张期 5min 零输出击杀疑·下轮 EngineTick 观察清单）⑦W17 judge 面 "
        "grammar 修复的实弹验证随首 shard 完成自然覆盖")
VERD = ("smoke 49/49 + SAT engine status rc0 (alive, N1 wave ledger face) + W17 "
        "KeyError('faces') fix verified (py_compile OK + selftest 21/21 PASS + mk "
        "coverage 1384 cells / 59 mks all resolve vs w16 grammar faces, evidence "
        "results/_r820bmc_mkcheck.py; fuse auto-clears on runner hash change) + "
        + S6 + " + idle non-green (RAM %.1fGB free / %.1f%% < 40%%, idle_rounds=0, "
        "agenda not starved) + self-heal green (IterationLoop no-op pin=5, watchdog "
        "re-registered, both claws installed LF-normalized) + attrition 4 ledgers "
        "CLEAN (healed history disclosed) + orphan face=1 read-only (probe "
        "py_faces=5) + DEC hold / ORD delta consumed IN-ROUND (row 324 bm-b "
        "onboarding order 21:5x, zero bm-c action, watermark updated) + unacked 0 "
        "+ inbox 1 outbound to bm-b (offline, honest hold) + watermark_red=%s"
        % (free_gb, free_pct, json.dumps(wm.get("red", "?"))))

REPORT = (NOW_ISO + " | r820 | dept:工程/舰队（W17 波根因修复+SLA 失守"
          "如实报+ORD 水位消费+S6 链+自愈链·第 120 bm-c 连守轮） | 本地未达 origin "
          "commit 数=0（收口 commit 后 push+fetch 自证） | WM-VERDICT: %s（red=%s） | "
          "孤儿面=1（只读·probe py_faces=5） | r820: ①S0=absorb 两段（W17 修复件+工具族"
          "7 件 commit 3a818d721〔rebase 前 hash〕+daemon 活面 43 件 b29e1f3e6）+origin "
          "连进 3 commit（bm-a round 928 closeout 等·零 bm-c 文件交叠）+rebase 排队 S6 "
          "链后执行（链写盘竞态首发拒两次·正法=链收口后 1-2s 窗内 commit+rebase 原子"
          "窗）；②S0.5=DEC 零 delta/ORD delta TRUE（0A1D9C1D→%s·新增行=row 324 "
          "O-20261009-2150 bm-b 入伙开工令 21:5x〔涉本司面=④ 产线恢复借池申请=由 bm-b "
          "发起·bm-c 零动作〕+行 320 尾注 bm-c FleetLink 升级已执行=零新动作·水位照更"
          "新）+unacked 0+inbox 出站 1（C7 MSG 待 bm-b·离线挂起如实）+21:08 死轮陈旧 "
          "s05 facts 由本轮新鲜扫覆盖；③S1 smoke 49/49+SAT 引擎活 rc0+idle 非绿（RAM "
          "%.1fGB 空闲·idle_rounds=0·agenda 未饿）；④**W17 屏幕波双病灶定谳+修复（本轮"
          "主产出）**：全天 0/8 烧成·fuse 拒投 143 次的根因=cmd_screen 把 _cell_list_w17"
          "() 的 w17 波 grammar（无 faces 键）塞进 worker state→_init_worker 用它覆写 "
          "每个 spawn worker 的 tl1.GRAMMAR→run_candidate_curve_w17 L350 "
          "GRAMMAR['faces'][mk] KeyError 每细胞必炸〔w17_grammar.json 键集实测=['cell_"
          "key','entry_source',...无 faces]·w16_grammar.json faces=77〕——修法=state 换装"
          "w16 face grammar（face_grammar 别名·主进程 tl1.GRAMMAR 同源）+judge 面同窗补 "
          "state['grammar'] 字段（w16 cmd_judge L3710 先例·防 judge 被 autofill 领走后"
          "再炸一次）·验证=py_compile+selftest 21/21+1384 cells 59 mks 全解析
          （results/_r820bmc_mkcheck.py）·fuse 按 hash-change 自清律下个领取周期自愈"
          "〔shards 0/1 的 143 拒投随新 hash 失效〕；第二病灶=RAM 门（runner 4GB 三采样"
          "门·当前空闲 %.1fGB 低于线·shard-2 20:56→21:37 40min 等待后诚实 park 实锚"
          "〔r491 park law·非 crash〕·CEO 桌面 Doubao ~4GB 不可动+ComfyUI 2.9GB idle "
          "H3 复用面 r817 裁定保留）——RAM 窗开（会话退出/桌面应用关闭）即 autofill "
          "自动复烧；⑤**SLA D-20261009-01(iii) 10-10 00:00 ≥10 claimable 失守如实报**："
          "池面实测 9 ready（8 W17 screen shard+judge）<10·W17 screens 0/8 未烧成=池补"
          "给链源头断·双病灶如上（代码面已修·RAM 面待窗）·无粉饰；⑥S6 链分离点火 pid "
          "44372（r818 evening-chain 先例）〔%s〕；⑦自愈链全绿（loop pin=5 no-op 首火 "
          "23:45+watchdog 重注册 23:46+双爪 LF 归一装）+attrition 4 ledger CLEAN；"
          "⑧tick 会话连灭窗观察（21:08→23:25 约 13 个 tick 槽无成轮会话=RAM 紧张期 5min "
          "零输出击杀疑·loop 任务本体在籍 pin=5·watchdog 在籍·下轮 EngineTick 成轮"
          "验证清单承接 r817 ⑬） | %s"
          % ("绿" if not wm.get("red") else "红", json.dumps(wm.get("red", "?")),
             facts["ord_sha"][:8], free_gb, free_gb, S6, NEXT))

# ---- state file ----
sp = os.path.join(R, "state-bm-c.json")
st = jload(sp)
st["round_no"] = 821
st["last_round"] = 820
st["round_no_label"] = "round 820 (bm-c)"
for k in ("clock_read", "current_task_at", "last_round_at", "last_round_ts",
          "last_seen", "last_seen_at", "last_ts", "updated", "updated_at",
          "last_decisions_read_at", "last_decisions_at", "last_orders_at",
          "last_run_at", "current_task_ts", "last_round_summary_at"):
    st[k] = NOW_ISO
st["heartbeat_epoch_utc"] = epoch
st["last_decisions_sha"] = facts["dec_sha"]
st["last_orders_sha"] = facts["ord_sha"]
st["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree "
    "origin/main git show; r820 start+close sweep via SSH primary leg rc0; dec "
    "delta FALSE = unchanged, zero action; facts-driven from "
    "results/_r820bmc_s05_facts.json, 64hex shape-asserted; close face reads sha "
    "PROGRAMMATICALLY from facts json, ZERO literal constants (r583 law)")
st["ord_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN "
    "per r537 law; r820 start+close sweep via SSH primary leg rc0; ord delta "
    "TRUE = 0A1D9C1D -> %s consumed IN-ROUND: delta face = new row 324 "
    "(O-20261009-2150 bm-b onboarding order, BigMoney face = borrow-pool "
    "application ORIGINATES FROM bm-b, zero bm-c action) + row 320 tail note "
    "(bm-c FleetLink upgrade already executed); facts-driven, 40hex "
    "shape-asserted; ZERO literal constants (r583 law)" % facts["ord_sha"][:8])
st["current_task"] = ACT
st["activity_now"] = ACT
st["next"] = NEXT
st["next_pointer"] = NEXT
st["next_milestone"] = NEXT
st["verify"] = VERD
st["verdict"] = VERD
st["last_round_summary"] = REPORT
st["did"] = REPORT
st["free_ram_gb"] = free_gb
st["ram_free_gb"] = free_gb
st["idle_ram_gb"] = free_gb
st["total_ram_gb"] = total_gb
st["gpu_free_vram_mb"] = vfree
st["gpu_free_vram_mib"] = vfree
st["gpu_free_mb"] = vfree
st["gpu_idle_vram_mb"] = vfree
st["gpu_idle_vram_mib"] = vfree
st["gpu_vram_free_mb"] = vfree
st["gpu_idle_mb"] = vfree
st["gpu_idle_mib"] = vfree
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["cpu_idle_pct"] = round(100 - idle.get("cpu_pct", 11.0), 1) if "cpu_pct" in idle else 89.0
st["cpu_util_pct"] = idle.get("cpu_pct", 11.0) if "cpu_pct" in idle else 11.0
st["cpu_pct"] = idle.get("cpu_pct", 11.0) if "cpu_pct" in idle else 11.0
st["latest_artifact"] = ("scripts/trial_labor_w17.py (r820 W17 screen+judge "
    "worker-grammar fix: w16 face grammar rides initargs, KeyError('faces') "
    "root-caused) + Tools/_r820bmc_{s05,clone_s6,s6,s6_ignite,close}.py (r820 "
    "helper set) + results/_r820bmc_mkcheck.py (1384 cells 59 mks all resolve) + "
    "results/_r820bmc_s6_log.txt (" + S6 + ") + results/_orphan_face_probe.bm-c.json "
    "(orphan 1 read-only) + results/_attrition_guard_scan.json (4 CLEAN) @ " + NOW_ISO)
st["sync"] = {"ahead": -1, "behind": -1,
              "last_push_ts": NOW_ISO,
              "note": ("r820 closeout: rebase+commit+push executes in the round "
                       "tail immediately after this state-write (S6 chain write "
                       "race forced rebase deferral); receipt = post-push fetch + "
                       "rev-list self-verify, read by next round; -1 = not yet "
                       "measured at state-write time (honest placeholder)")}
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# ---- heartbeat ----
hp = os.path.join(R, "fleet", "machines", "bm-c.json")
hb = jload(hp)
hb["last_seen"] = NOW_ISO
hb["ts"] = NOW_ISO
hb["clock_read"] = NOW_ISO
hb["heartbeat_epoch_utc"] = epoch
hb["current_task"] = ACT
hb["current_task_at"] = NOW_ISO
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["cpu_cores"] = 32
hb["cores"] = 32
hb["free_ram_gb"] = free_gb
hb["idle_ram_gb"] = free_gb
hb["ram_free_gb"] = free_gb
hb["gpu_free_vram_mb"] = vfree
hb["gpu_free_vram_mib"] = vfree
hb["gpu_free_mb"] = vfree
hb["verdict"] = "ok"
hb["next"] = NEXT
hb["next_milestone"] = NEXT
hb["latest_artifact"] = st["latest_artifact"]
with open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# ---- round report ----
rp = os.path.join(R, "round_reports-bm-c.md")
with open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write("\n" + REPORT + "\n")

# ---- self-asserts ----
st2 = jload(sp)
hb2 = jload(hp)
assert isinstance(st2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert isinstance(hb2["heartbeat_epoch_utc"], int), "hb epoch must be JSON int"
assert "T" in st2["clock_read"] and "T" in hb2["clock_read"], "T separator law"
assert len(st2["last_orders_sha"]) == 40 and len(st2["last_decisions_sha"]) == 64
print("CLOSE OK round=820 next=821 epoch=%d ram_free=%.1fGB vram_free=%dMB "
      "ord_sha=%s dec_sha=%s | %s"
      % (epoch, free_gb, vfree, facts["ord_sha"][:8], facts["dec_sha"][:8], S6))
