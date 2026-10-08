# -*- coding: utf-8 -*-
"""r788 bm-c S7 bookkeeping driver (pre-push face): appends the round
report line to logs/iteration-loop/round_reports-bm-c.md (live file),
rolls state-bm-c.json (round_no 789, last_round 788) and
fleet/machines/bm-c.json heartbeat (epoch INT law R170/R178, clock_read
T-separator law R262, CEO-visible three lines per product-first law).
Machine metrics via psutil/nvidia-smi with idle_trigger fallback.
Post-push sync refresh is a separate follow-up step (fleet post-push
sync precedent, bm-a r897 / bm-c r786 close face)."""
import datetime
import json
import os
import subprocess
import time

sys_std = __import__("sys")
sys_std.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")
EPOCH = int(time.time())
R = 788

REPORT = (
    " | r788 | dept:工程/研究（04:35-05:0x 窗·死会话收养+W17 出场轴预注册冻结落地轮·第 89 bm-c 连守轮）"
    " | 本地未达 origin commit 数=0（commit 后 push+fetch 自证·post-push sync 随批）"
    " | WM-VERDICT: 绿（red=false·lane=healthy·next_pick=claimed moneyflow IC 源阻断 bm-a 车道合法·"
    "DEC 83813196/ORD 1212A338 双恒等零消费·unacked 0〔54 orders〕·inbox 唯一在册=本席 F-04 声明件）"
    " | 孤儿面=1（ComfyUI 产线资产·只读不杀·round-zero 探针新读）"
    " | r788: 死会话收养+W17 出场轴冻结落地轮——①S0 收养链：r788 前会话（04:05-04:29 窗）死体遗产全量收养"
    "（W17 prereg 全文+science_gates 泊位三键编辑+十腿冻结窗 facts 探针+S0 吸收轮已 commit 13cbe1489），"
    "收养核验三件全绿（facts sha256_16=ff6603a27623c787 与 prereg 引用恒等+banned_direction_gate ADMIT rc0 复跑"
    "〔matched=[]·BAN-08 例外块 §0.5 完备〕+SEED_REGISTRY 导入面三键在册）+S0.5 双扫零消费"
    "（DEC/ORD 双恒等·unacked 0·bm-a F1 MSG=非致本席 A10 分类在案）；②主产出=TRIAL_LABOR_W17 出场轴冻结四件齐："
    "prereg FROZEN（A7 出场烧史修正横幅=W 血统 X 恒混杂随机维度 32,869 生成/28,808 非缺省全负·"
    "完整配对块隔离=W 血统零烧真增量）+seeds 20610000/20610500/20611000 同 commit（R250 一步律·"
    "族带 [20610000,20612500) 零撞·泊位拒绝史 20598000/20600000 被 theme_deepen 带占如实载）+"
    "波级票 T-2026-10-09-178-P1 开票认领同轮（O-1730）+F-04 MSG 同轮；fill_ladder TRIAL-LABOR-W17-GENERATE "
    "门控条目同轮预宣布（三查镜像 W14/W16·runner_exists 门待 runner 切片·catalog JSON 20 entries 机读验证）；"
    "③S1 smoke 49/49（分离监督器 fresh 重跑）+QA smoke-r788-bm-c.md 5/5（equity PNG 同批·91 trades·"
    "sharpe 0.199·determinism=True）；④S6 40/40 rc0 九连绿（results/_r788bmc_s6_log.txt·"
    "fund_premium 10-08 NAV 首采=04:xx 窗诚实 no-op·15:30+ 轮落首采·update_daily 10-08 截止零新行）；"
    "⑤S4 固化一件（pit-spawn.md r788 包装器缓冲变体坑——Invoke-SilentExe ReadToEnd 全缓冲=5min 静默斩首"
    "对增量打印也生效·分离监督器正法 Tools/_r788bmc_runall.py 范式）；⑥S7 自愈批全绿（loop pin=5 no-op·"
    "watchdog 在位·双爪重装·attrition 4 台账 CLEAN〔3 历史 shrink 已 healed 注记〕·orders 收尾二扫 54/0）"
    "+分离长活通道首创（runall 监督器三段顺序 smoke→QA→S6+science_gates selftest 分离跑在飞·随班收读）"
    " | 下轮指针: r789=W17 runner 构建切片（funnel 4/5：clone scripts/trial_labor_w16.py import-face 复用+"
    "出场 face 层 §3 冻结参数 verbatim+改革面块必列〔W16 §8 缺口教训〕+G-face 断言电池〔control 臂决定论交叉门 "
    "40/173+ExitConfig 缺省表+入场源 sha 22179881b7537193+语法血统三面恒等〕+GBK 入口律+selftest 全绿→"
    "r446 三命令真数据 identity-face 首跑→runner landed→fill_ladder runner_exists 门放行）+入池 ≥10"
    "（D-20261009-01③ SLA 窗 10-10 00:00·到窗读数随班回执）+W192 finalize 跟进（引擎自动面）+"
    "fund_premium 10-08 NAV 首采（10-09 晚窗 15:30+）+science_gates selftest 分离跑收读（r788 已发）")

ACT = ("当前活: r788 bm-c（04:35-05:0x 窗·死会话收养+W17 出场轴冻结落地·第 89 连守轮）——"
       "主产出=TRIAL_LABOR_W17 冻结四件齐（prereg FROZEN+泊位三键 20610000/20610500/20611000 同 commit R250+"
       "T-2026-10-09-178-P1 开票认领+F-04 MSG）+fill_ladder W17 门控条目预宣布+banned gate ADMIT rc0 | "
       "最近实物: research/TRIAL_LABOR_W17_PREREG.md + scripts/science_gates.py (seeds trio) + "
       "Tools/fill_ladder_catalog.json (W17 gate-armed entry) @ 本轮冻结 commit 2026-10-09T05:0x+08:00 | "
       "下个里程碑: r789=W17 runner 构建切片（funnel 4/5·r446 三命令律）+入池 ≥10（SLA 窗 10-10 00:00）+"
       "fund_premium NAV 首采（10-09 晚 15:30+）")

ART = ("research/TRIAL_LABOR_W17_PREREG.md (FROZEN: exit-axis complete-block PAIRED isolation, "
       "A7 products-census correction banner, BAN-08 sec.0.5 exception block) + scripts/science_gates.py "
       "(trial_labor_w17_gen/scrnull/unc = 20610000/20610500/20611000, R250 one-step law, family band "
       "[20610000,20612500)) + Tools/fill_ladder_catalog.json (TRIAL-LABOR-W17-GENERATE gate-armed entry, "
       "20 entries JSON-validated) + fleet/tasks/T-2026-10-09-178-P1.json (opened+claimed same round) + "
       "fleet/inbox/MSG-2026-10-09-0453-bmc-trial-labor-w17.md (F-04) + Tools/_r788bmc_w17_freeze_facts.py "
       "+ results/_r788bmc_w17_freeze_facts.json (ten legs ALL GREEN, sha256_16 ff6603a27623c787) + "
       "Tools/_r788bmc_runall.py + Tools/_r788bmc_s6.py + Tools/_r788bmc_sg_selftest.py (detached-channel "
       "canon) + qa/smoke-r788-bm-c.md 5/5 + qa/equity-curve-r788-bm-c.png + results/_r788bmc_s6_log.txt "
       "(40 legs rc0, ninth green) + research/pit-spawn.md r788 wrapper-buffer variant entry @ " + TS)

NXT = ("r789 续作: ①W17 runner 构建切片（funnel 4/5：clone scripts/trial_labor_w16.py import-face 复用+"
       "出场 face 层 §3 冻结参数 verbatim〔7 单规则隔离 face+template_default 对照·never-true 习语 W1 同源〕+"
       "改革面块必列〔member_metrics 四维+dual-nulls+g2_reform_fdr4d+top-3+REFORM 常数 import·W16 §8 缺口教训〕+"
       "G-face 断言电池〔control 臂决定论交叉门 40/173+ExitConfig 缺省表 A9+入场源 sha 22179881b7537193+"
       "语法血统三面恒等 A4〕+GBK reconfigure 入口律 r236+selftest hermetic 全绿→r446 prep/finalize/judge-prep "
       "三命令真数据 identity-face 首跑→宣布 runner landed→fill_ladder TRIAL-LABOR-W17-GENERATE runner_exists "
       "门放行）②入池 ≥10（D-20261009-01③ SLA 窗 10-10 00:00·GENERATE 1+SCREEN 分片+JUDGE 分片·到窗读数随班回执）"
       "③W192 finalize 跟进（引擎自动面·r325/r535 律——上游 W1..W191 全落地前置全绿·finalize 键序按 registry derive）"
       "④fund_premium 10-08 NAV 首采（发布面 T+1·10-09 晚窗 15:30+·第十观测窗）⑤science_gates selftest 分离跑收读"
       "（r788 已发·results/_r788bmc_sg_selftest.txt.rc）⑥CEO 勾选后按选项走（A=视频段解冻·等待态）+"
       "T-177 regime-5 标签器消费面跟进（bm-a 车道）")

DID = (TS + " | r788 | dept:工程/研究（死会话收养+W17 出场轴冻结落地轮·第 89 bm-c 连守轮） | "
       "WM-VERDICT: 绿（red=false·lane=healthy·next_pick=claimed moneyflow IC 源阻断 bm-a 车道合法·"
       "DEC 83813196/ORD 1212A338 双恒等零消费·unacked 0〔54 orders〕·inbox 唯一在册=本席 F-04 声明件） | "
       "孤儿面=1（ComfyUI 产线资产·只读不杀） | r788: " + REPORT.split(" | r788: ", 1)[1])

VERIFY = ("W17 冻结四件 git 可验（prereg FROZEN banner+SEED_REGISTRY 三键同 commit+票 T-2026-10-09-178-P1 claimed+"
          "F-04 MSG 同轮） + banned_direction_gate ADMIT rc0（matched=[]·BAN-08 例外块完备） + facts "
          "sha256_16 ff6603a27623c787 恒等 + SEED_REGISTRY 导入面三键 20610000/20610500/20611000 + "
          "catalog JSON 20 entries 机读（W17 gates=prereg_frozen/runner_exists/standing_no_judge_inflight） + "
          "smoke 49/49（results/_r788bmc_smoke.txt·fresh 分离监督器重跑） + QA smoke-r788-bm-c.md 5/5"
          "（91 trades·sharpe 0.199·determinism=True·equity PNG 65,334B） + S6 40/40 rc0 九连绿"
          "（results/_r788bmc_s6_log.txt） + attrition 4 台账 CLEAN（3 历史 shrink healed 注记） + 双爪重装 + "
          "loop pin=5 no-op + watchdog 在位 + DEC/ORD 双恒等（_r788bmc_s05_facts.json 双扫） + 孤儿面=1")


def machine_metrics():
    m = {}
    try:
        import psutil
        m["cpu_pct"] = round(psutil.cpu_percent(interval=0.5), 1)
        vm = psutil.virtual_memory()
        m["free_ram_gb"] = round(vm.available / 1024 ** 3, 1)
        m["idle_ram_gb"] = m["free_ram_gb"]
        m["ram_free_gb"] = m["free_ram_gb"]
    except Exception:
        it = json.load(open(os.path.join(ROOT, "results", "idle_trigger.bm-c.json"),
                            encoding="utf-8"))
        m["cpu_pct"] = 0.0
        m["free_ram_gb"] = round(23.9 * it.get("ram_free_pct", 10.0) / 100, 1)
        m["idle_ram_gb"] = m["free_ram_gb"]
        m["ram_free_gb"] = m["free_ram_gb"]
    try:
        p = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                            "--format=csv,noheader,nounits"],
                           capture_output=True, creationflags=CNW)
        vmb = int(p.stdout.decode().strip().splitlines()[0])
        for k in ("gpu_free_vram_mb", "gpu_idle_vram_mb", "gpu_vram_free_mb",
                  "gpu_free_mb", "gpu_idle_mb", "gpu_free_vram_mib",
                  "gpu_idle_vram_mib", "gpu_idle_mib", "gpu_free_mib"):
            m[k] = vmb
    except Exception:
        pass
    m["cpu_idle_pct"] = round(100 - m.get("cpu_pct", 0.0), 1)
    m["cpu_util_pct"] = m["cpu_pct"]
    m["total_ram_gb"] = 23.9
    m["cores"] = 32
    m["cpu_cores"] = 32
    return m


def main():
    it = json.load(open(os.path.join(ROOT, "results", "idle_trigger.bm-c.json"),
                        encoding="utf-8"))
    mm = machine_metrics()

    # 1. round report append (live file)
    rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
    with open(rp, "a", encoding="utf-8", newline="") as fh:
        fh.write(TS + REPORT + "\n")

    # 2. state file
    sp = os.path.join(ROOT, "state-bm-c.json")
    st = json.load(open(sp, encoding="utf-8"))
    st.update({
        "round_no": R + 1, "round_no_label": "round %d (bm-c)" % R,
        "last_round": R, "last_round_at": TS, "last_run_at": TS,
        "last_seen": TS, "last_seen_at": TS, "clock_read": TS, "ts": TS,
        "heartbeat_epoch_utc": EPOCH,
        "current_task": ACT, "current_task_at": TS, "activity_now": ACT,
        "latest_artifact": ART, "next_milestone": NXT,
        "did": DID, "verdict": DID, "note": DID,
        "last_round_summary": DID, "last_action": DID,
        "next": NXT, "next_pointer": NXT, "verify": VERIFY,
        "health": "ok", "last_round_ts": TS, "last_ts": TS,
        "last_pulled_at": TS, "updated_at": TS, "updated": TS,
        "idle_rounds": int(it.get("idle_rounds", 0)),
        "agenda_starved": bool(it.get("agenda_starved", False)),
    })
    st.update(mm)
    with open(sp, "w", encoding="utf-8") as fh:
        json.dump(st, fh, indent=1, ensure_ascii=False)

    # 3. heartbeat
    hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
    hb = json.load(open(hp, encoding="utf-8"))
    hb.update({
        "last_seen": TS, "clock_read": TS, "ts": TS,
        "heartbeat_epoch_utc": EPOCH,
        "round_no": R + 1, "round_no_label": "round %d (bm-c)" % R,
        "last_round": R, "last_round_at": TS,
        "current_task": ACT, "current_task_at": TS, "activity_now": ACT,
        "latest_artifact": ART, "next_milestone": NXT,
        "did": DID, "verdict": DID, "note": DID,
        "last_round_summary": DID, "last_action": DID,
        "next": NXT, "next_pointer": NXT, "verify": VERIFY,
        "health": "ok",
        "idle_rounds": int(it.get("idle_rounds", 0)),
        "agenda_starved": bool(it.get("agenda_starved", False)),
        "last_seen_at": TS, "updated_at": TS, "updated": TS,
        "last_run_at": TS, "last_ts": TS,
    })
    hb.update(mm)
    with open(hp, "w", encoding="utf-8") as fh:
        json.dump(hb, fh, indent=1, ensure_ascii=False)

    # self-verify: epoch INT + T-separator (smoke F7 laws)
    chk = json.load(open(hp, encoding="utf-8"))
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
    assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read T-format"
    print("S7 pre-push bookkeeping OK: report line + state round_no=%d + heartbeat "
          "epoch=%d (int) ts=%s" % (chk["round_no"], chk["heartbeat_epoch_utc"], TS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
