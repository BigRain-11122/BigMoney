# -*- coding: utf-8 -*-
"""r787 bm-c S7 bookkeeping driver (pre-push face): appends the round
report line to logs/iteration-loop/round_reports-bm-c.md (live file per
r786 evidence), rolls state-bm-c.json (round_no 788, last_round 787) and
fleet/machines/bm-c.json heartbeat (epoch INT law R170/R178, clock_read
T-separator law R262, CEO-visible three lines per product-first law).
Machine metrics via psutil/nvidia-smi with idle_trigger fallback.
Post-push sync refresh is a separate follow-up step (fleet post-push
sync precedent, bm-a r897)."""
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
R = 787

REPORT = (
    " | r787 | dept:工程/研究（03:35-04:2x 窗·死会话收养+W192 五面冻结落地轮·第 88 bm-c 连守轮）"
    " | 本地未达 origin commit 数=0（commit 后 push+fetch 自证·post-push sync 随批）"
    " | WM-VERDICT: 绿（red=false·lane=healthy·next_pick=claimed moneyflow IC 源阻断 bm-a 车道合法·"
    "DEC 83813196/ORD 1212A338 双恒等零消费·unacked 0〔54 orders〕·inbox=0）"
    " | 孤儿面=1（ComfyUI 产线资产·只读不杀·round-zero 探针新读）"
    " | r787: 死会话收养+W192 五面冻结落地轮——①S0 收养链：r787 前三死会话 S0 吸收轮 3-5 续接+"
    "本会话 round-6 吸收（daemon live-faces+W192 stage-3 冻结编辑器遗产 untracked 收养）+pull rebase"
    "（吸收 bm-a r897/898）+S0.5 双扫零消费（DEC/ORD 水位恒等·unacked 0·inbox 0·_r787bmc_s05_facts.json）；"
    "②主产出=W192 五面冻结全落地（f8703842c 上 origin·送达 0/0）：收养遗产冻结编辑器首活四坑修复"
    "（G2 owner 分桶 owned 181 排 None 桶/G5 n3r1_used 子串计数 3≠2 行计数假象/G8 边界三件=chunk 4 空格缩进"
    "+滚块尾换行+T-141 4 空格形计数 1/G11 subprocess JSON list 归一）+preflight 干跑法首创"
    "（Tools/_r787bmc_w192_countcheck.py 零写入全 G 链仿真·155 项表核一次过·唯一失配 mat-39 当场归正·"
    "E48 方法论卡）；五面=pf N1_BANDS[192] 行 a=437_204..439_203/b_exit=439_204..439_403 owner=bm-c+"
    "n1 WAVE_CONFIGS[192] 行+n1 W192 materializer face（断言区=selftest 体内在跑）+selftest W192 prose 腿"
    "（Tools/_r787bmc_w192_selftest_leg.py·11 项滚面·selftest 重跑 PASS 输出带 W192 腿）+prereg"
    "（de1ad11f9 前已在 origin）；A=阶梯第 52 例（A base==W191 B 尾+1）·B=同窗互斥第 141 律·"
    "第 182 引擎波·bm-c 第 35 枚自有波（probe receipt leg0 机读）；引擎 mtime-watch 自燃 12/12 分片"
    "（never-dry 供给线交付·r325 点火证据=产物增长面 12 件实读）；G11 写后假红=幂等件楔死态收口"
    "（Tools/_r787bmc_w192_receipt_complete.py 收口件法·收据 results/_r787bmc_w192_freeze_receipt.json+"
    "五段 PASS）；③S1 smoke 49/49+QA smoke-r787-bm-c.md 5/5（per-machine 后缀律·equity PNG 同批）；"
    "④S6 40/40 rc0 八连全绿（results/_r787bmc_s6_log.txt·fund_premium 10-08 NAV 首采=04:xx 窗诚实 no-op·"
    "15:30+ 轮落首采·update_daily 10-08 截止零新行）；⑤S4 固化三件（pit-engine-freeze-editor.md 四坑复合行+"
    "METHODOLOGY_ASSETS.md E48 卡+TREASURE_REGISTRY.md 登记行）；⑥S7 自愈批全绿（loop pin=5 no-op·"
    "watchdog 重装·双爪重装·attrition 4 台账 CLEAN·orders 收尾二扫 54/0）"
    " | 下轮指针: r788=W17 freeze 窗（TRIAL_LABOR_W17 候选稿+probe 五腿已在册 funnel 2/5·"
    "PREREG_TEMPLATE 全模板+§0.5 BAN-08 例外块+泊位 20610000/20610500/20611000 R250 同 commit 一步律+"
    "开票 T-2026-10-09-<seq>-P1 认领同轮 O-1730+F-04）+W192 finalize 跟进（引擎自动面·上游 W1..W191 全落地=前置全绿）"
    "+fund_premium 10-08 NAV 首采（10-09 晚窗 15:30+·第九观测窗 r786 指针）")

ACT = ("当前活: r787 bm-c（03:35-04:2x 窗·死会话收养+W192 五面冻结落地·第 88 连守轮）——"
       "主产出=W192 五面冻结 f8703842c 上 origin（182nd 引擎波 bm-c 第 35 枚·A=437_204..439_203 "
       "阶梯第 52 例/B=439_204..439_403 同窗互斥·五面全落+selftest 带 W192 腿·引擎自燃 12/12）"
       "+preflight 干跑法 E48 入库+四坑修复 | 最近实物: scripts/perpetual_faces.py + "
       "scripts/perpetual_faces_n1.py @ f8703842c 2026-10-09T04:0x+08:00 | 下个里程碑: r788=W17 "
       "freeze 窗（全模板+BAN-08 例外块+泊位三枚+开票认领同轮）+W192 finalize（引擎自动）+"
       "fund_premium NAV 首采（10-09 晚 15:30+）")

ART = ("scripts/perpetual_faces.py + scripts/perpetual_faces_n1.py (W192 five-face freeze "
       "f8703842c: pf N1_BANDS[192] + n1 WAVE_CONFIGS[192] + materializer face + selftest "
       "W192 leg; A=437_204..439_203 FIFTY-SECOND staircase, B=439_204..439_403 own-A mutual "
       "exclusion; engine self-burn 12/12) + Tools/_r787bmc_w192_countcheck.py (preflight "
       "dry-run, E48) + Tools/_r787bmc_w192_receipt_complete.py + Tools/_r787bmc_w192_selftest_leg.py "
       "+ results/_r787bmc_w192_freeze_receipt.json + results/_r787bmc_w192_selftest_leg_receipt.json "
       "+ qa/smoke-r787-bm-c.md 5/5 + results/_r787bmc_s6_log.txt (40 legs rc0, eighth green) "
       "+ METHODOLOGY_ASSETS.md E48 + pit-engine-freeze-editor.md r787 entry @ " + TS)

NXT = ("r788 续作: ①W17 freeze 窗（TRIAL_LABOR_W17_CANDIDATE_EXITAXIS_PREREG_DRAFT.md 候选稿已落 r786·"
       "probe 五腿 rc0 已落 r786——freeze=PREREG_TEMPLATE 全模板填齐+§0.5 例外块引 BAN-08〔new_data|"
       "new_mechanism+cannot-see 陈述〕+泊位 20610000/20610500/20611000 R250 同 commit 一步律+开票 "
       "T-2026-10-09-<seq>-P1 认领同轮 O-1730+F-04 MSG）②runner 构建（clone scripts/trial_labor_w16.py "
       "import-face 复用+出场 face 层+selftest 全绿）③入池 ≥10（D-20261009-01③ SLA 窗 10-10 00:00·"
       "到窗读数随班回执）④W192 finalize 跟进（引擎自动面·r325/r535 律——上游 W1..W191 全落地前置全绿·"
       "finalize 键序按 registry derive）⑤fund_premium 10-08 NAV 首采（发布面 T+1·10-09 晚窗 15:30+）"
       "⑥CEO 勾选后按选项走（A=视频段解冻·等待态）+T-177 regime-5 标签器消费面跟进（bm-a 车道）")

DID = (TS + " | r787 | dept:工程/研究（死会话收养+W192 五面冻结落地轮·第 88 bm-c 连守轮） | "
       "WM-VERDICT: 绿（red=false·lane=healthy·next_pick=claimed moneyflow IC 源阻断 bm-a 车道合法·"
       "DEC 83813196/ORD 1212A338 双恒等零消费·unacked 0〔54 orders〕·inbox=0） | 孤儿面=1（ComfyUI "
       "产线资产·只读不杀） | r787: " + REPORT.split(" | r787: ", 1)[1])

VERIFY = ("W192 五面冻结 f8703842c 上 origin 送达 0/0（fetch+rev-list 自证） + n1 selftest PASS "
          "（输出含 W192 materializer face 腿） + pf/n1 post-import 机读（rows=190·W192 行="
          "a(437204,439203) b_exit(439204,439403) owner=bm-c·W191 行 byte-intact） + preflight "
          "155 项表核 rc0 + freeze receipt 五段 PASS + selftest_leg receipt 三段 PASS + smoke "
          "49/49（results/_r787bmc_smoke.txt） + QA smoke-r787-bm-c.md 5/5 + S6 40/40 rc0 八连全绿"
          "（results/_r787bmc_s6_log.txt） + W192 引擎自燃 12/12 分片（results/p2cal_ext/n1_w192 实数）"
          " + attrition 4 台账 CLEAN + 双爪重装 + loop pin=5 + watchdog + DEC/ORD 双恒等"
          "（_r787bmc_s05_facts.json）")


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
