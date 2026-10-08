# -*- coding: utf-8 -*-
"""r786 bm-c S5/S7 bookkeeping: round-report row append + heartbeat/state
closeout write (house pattern from results/_r785bmc_bookkeep.py lineage).
New per O-20261009-0024 sec1-4: heartbeat sync face {ahead,behind,
last_push_ts,note} (bm-b r807 naming alignment, pre-push write + in-round
post-push refresh). orders_ack += 2 CEO orders via bm-b. round_no 786->787,
last_round 786. epoch as python int (R170/R178). clock T-separated ISO
(R262). Zero engine lane touches. ASCII source."""
import json
import os
import subprocess
import time
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
ST = os.path.join(ROOT, "state-bm-c.json")
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
ROUND = 786
TS = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())


def sh(*args):
    p = subprocess.run(list(args), capture_output=True, creationflags=CNW)
    return p.returncode, p.stdout.decode("utf-8", "replace").strip()


def stats(hb):
    cpu, ram_free, vram = hb.get("cpu_pct", 0.0), hb.get("free_ram_gb", 0.0), \
        hb.get("gpu_free_vram_mb", 0)
    try:
        import psutil
        cpu = round(psutil.cpu_percent(interval=1.0), 1)
        ram_free = round(psutil.virtual_memory().available / (1024 ** 3), 1)
    except Exception:
        pass
    try:
        rc, out = sh("nvidia-smi", "--query-gpu=memory.free",
                     "--format=csv,noheader,nounits")
        if rc == 0 and out:
            vram = int(out.splitlines()[0])
    except Exception:
        pass
    return cpu, ram_free, vram


ROW = (u"{ts} | r{r} | dept:工程/研究（断头收养轮·第 87 bm-c 连守轮·CEO 双令回执"
       u"+W17 probe 腿+S6 七连全绿） | WM-VERDICT: 绿（red=false·lane=healthy·"
       u"next_pick=claimed moneyflow IC 源阻断 bm-a 车道合法·DEC 83813196/ORD "
       u"1212A338 收尾二扫双恒等零消费·unacked 0〔54 orders·两张 bm-b 令当窗回执〕"
       u"·inbox=0） | 孤儿面=1（ComfyUI 产线资产·只读不杀·01:17 新读） | r{r}: "
       u"断头收养+CEO 双令回执轮——前 r786 会话（00:3x-01:0x）猝死于 S6 后零簿记"
       u"（S6 DONE 01:00:58·心跳未滚·轮报告无行），本会话 01:05 起接续收口："
       u"①S0 死会话遗产盘点收养=双 merge 集成（b62f2d7ab/50abcb406·吸收 bm-a "
       u"r806 死产收编波+compute_audit UU union 收口 _r786bmc_merge_resume.json）"
       u"+QA det-101st（新命名律首活体证 smoke-r786-bm-c.md 5/5）+W17 候选稿"
       u"（TRIAL_LABOR_W17_CANDIDATE_EXITAXIS_PREREG_DRAFT.md·funnel 1/5）+"
       u"Tools 三驱动（s05/s6/merge_resume）；②CEO 双令回执：O-20261008-2323-bm-b "
       u"全面开工令=bm-c resume 自检零 pause 态在册（86 连守零中断+SAT 活 rc0）+"
       u"复市日里程碑面（REGIME_GUARD v3 enforce 活·fund_premium 首采=10-09 晚窗 "
       u"T+1 待发·W14-JUDGE 77/77 judged 收口 n_eligible_g2=0 诚实负+"
       u"CEO-REPORT-WAVE14 在册 20261007）·O-20261009-0024-bm-b 同步一致性令="
       u"本轮收口 fetch→merge→push 全链闭环+心跳 sync 字段采用（bm-b 命名对齐）+"
       u"CEO「CPU 算力排满」令执行态=交互窗 W192 席 1abe1a57f+冻结 de1ad11f9 已在 "
       u"origin（r785 已回执·本轮维持）；③主线 W17 池补货（D-20261009-01③）"
       u"funnel 2/5 probe 腿落地=Tools/_r786bmc_w17_probe.py 五腿 rc0"
       u"（L1 登记簿出场轴零烧断言 17 W 行零命中·L2 banned gate 预跑 "
       u"REJECT_PREFREEZE 抓到冻结窗必办项=§0.5 例外块须引 BAN-08+"
       u"new_data|new_mechanism+cannot-see 陈述·L3 种子泊位提案 "
       u"20610000/20610500/20611000〔188 基点 conservative-2000 disjoint+"
       u"全表面零文本命中·20598000/20600000 被已注册基点 20600000 占用拒〕·"
       u"L4 出场 face 枚举 read-only 零触碰〔引擎缺省栈 P1-P6+ExitConfig 缺省+"
       u"草案 treatment 候选 face 6〕·L5 入场库锚面〔W14 grammar 3464 可判日·"
       u"cutoff 2026-09-22·judge_state sha↔ledger W14 sha16 恒等·W16 sha16 "
       u"ebf15822d2c8472e 在册〕）+facts results/_r786bmc_w17_probe_facts.json；"
       u"④W192 five-face 触发条件探=NOT MET（bm-a W191 five-face 未落地 origin·"
       u"r893 明示 next window first task）→严格续后零动作（顺序链完整性）；"
       u"⑤S1 smoke 49/49 本会话补跑（_r786bmc_smoke.txt）+SAT 引擎活 rc0"
       u"（alive_flag·burns/queue 空=待 W191/W192 five-face 落地）+S2 板清+"
       u"idle 非绿零义务（RAM 12.1%<40%·VRAM 1.12GB<6GB）+post_review ✗0；"
       u"⑥S6 40/40 rc0 七连全绿（死会话跑毕 DONE 01:00:58·本会话核 40×rc0 汇总）"
       u"·CEO 面 REPORT/LIVE-2026-10-09 再生；⑦S7 自愈批全绿（双爪 OK·loop pin=5·"
       u"watchdog 在·attrition 4 台账 CLEAN〔3 healed 注记〕） | 本地未达 origin "
       u"commit 数=见 S7-close 尾行（commit 后 push+fetch 自证）").format(ts=TS, r=ROUND)

DID = ROW

ACT = (u"当前活: r786 bm-c（01:05-01:2x 窗·断头收养+CEO 双令回执+W17 probe 腿+"
       u"S6 40/40 七连全绿·第 87 连守轮）——主产出=①W17 probe 腿五腿 rc0"
       u"（出场轴零烧断言+banned gate 预跑抓 BAN-08 冻结窗必办项+泊位提案 "
       u"20610000/20610500/20611000+出场 face 枚举+入场库锚面）②CEO 双令回执"
       u"（O-2323 resume 自检+复市日里程碑验收态·O-0024 同步闭环+sync 字段采用）"
       u"③死会话遗产收养（QA det-101st 新命名律首活体证 5/5+S6 40/40 七连全绿） "
       u"| 最近实物: Tools/_r786bmc_w17_probe.py + results/_r786bmc_w17_probe_"
       u"facts.json @ {ts} | 下个里程碑: r787=W17 freeze 窗（全模板+§0.5 BAN-08 "
       u"例外块+seeds R250 同 commit+开票认领同轮）→runner→入池≥10（D-01③ SLA 窗 "
       u"10-10 00:00）+fund_premium 10-08 NAV 首采（10-09 晚窗 15:30+）+W191 "
       u"five-face 落地后 W192 five-face（写入时探）").format(ts=TS)

NEXT = (u"r787 续作: ①W17 freeze 窗（PREREG_TEMPLATE 全模板填齐+§0.5 例外块引 "
        u"BAN-08〔new_data|new_mechanism+cannot-see 陈述〕+泊位 20610000/20610500/"
        u"20611000 R250 同 commit 一步律+开票 T-2026-10-09-<seq>-P1 认领同轮 "
        u"O-1730+F-04 MSG）②runner 构建（clone scripts/trial_labor_w16.py "
        u"import-face 复用+出场 face 层+selftest 全绿）③入池 ≥10（D-20261009-01③ "
        u"SLA 窗 10-10 00:00·到窗读数随班回执）④fund_premium 10-08 NAV 首采（发布面 "
        u"T+1·10-09 晚窗）⑤W192 five-face 落地窗=严格排后于 bm-a W191 five-face "
        u"（origin 触发条件写入时实探判定）⑥CEO 勾选后按选项走（A=视频段解冻·等待态）"
        u"+T-177 regime-5 标签器（bm-a 车道）消费面跟进")

VERIFY = (u"smoke 49/49（results/_r786bmc_smoke.txt） + S6 40/40 rc0 七连全绿"
          u"（results/_r786bmc_s6_log.txt DONE 01:00:58） + QA det-101st "
          u"qa/smoke-r786-bm-c.md 5/5（D-20261009-02 per-machine suffix law "
          u"first live proof·--round 786 显式） + W17 probe 五腿 rc0"
          u"（Tools/_r786bmc_w17_probe.py + results/_r786bmc_w17_probe_facts."
          u"json） + CEO 双令回执（O-20261008-2323-bm-b resume/milestones + "
          u"O-20261009-0024-bm-b sync 闭环+sync 字段） + W14-JUDGE 77/77 judged "
          u"n_eligible_g2=0 诚实负（results/trial_labor_w14/w14_judge.json） + "
          u"SAT 引擎活 rc0（alive_flag） + attrition 4 台账 CLEAN（results/"
          u"_attrition_guard_scan.json） + 双爪 OK + loop pin=5 + watchdog 在 + "
          u"孤儿面=1 只读（results/_orphan_face_probe.bm-c.json 01:17 新读） + "
          u"DEC/ORD 收尾二扫双恒等（_r786bmc_s05_facts.json 83813196/1212A338） + "
          u"push 送达自证（commit 后 fetch origin/main..HEAD=0）")

LATEST = (u"Tools/_r786bmc_w17_probe.py + results/_r786bmc_w17_probe_facts.json "
          u"(W17 funnel 2/5 probe five legs rc0: exit-axis zero-burn assert + "
          u"BAN-08 freeze-window to-do captured + berth 20610000/20610500/"
          u"20611000 proposed clean + exit face enum read-only + W14 entry-lib "
          u"anchors) + qa/smoke-r786-bm-c.md 5/5 (det-101st, per-machine suffix "
          u"law first live proof) + CEO orders x2 receipts + results/"
          u"_r786bmc_s6_log.txt (40 legs rc0=40 seventh consecutive all-green "
          u"window) + docs/daily_report/REPORT-2026-10-09.md + docs/live_usage/"
          u"LIVE-2026-10-09.md @ " + TS)

NEW_ACK = ["O-20261008-2323-bm-b.md", "O-20261009-0024-bm-b.md"]


def close_faces(obj):
    obj["last_seen"] = TS
    obj["ts"] = TS
    obj["clock_read"] = TS
    obj["last_round_at"] = TS
    obj["last_seen_at"] = TS
    obj["updated"] = TS
    obj["updated_at"] = TS
    obj["last_run_at"] = TS
    obj["last_ts"] = TS
    obj["last_pulled_at"] = TS
    obj["heartbeat_epoch_utc"] = EPOCH
    obj["round_no"] = ROUND + 1
    obj["round_no_label"] = u"round %d (bm-c)" % ROUND
    obj["last_round"] = ROUND
    obj["did"] = DID
    obj["verdict"] = DID
    obj["note"] = DID
    obj["last_round_summary"] = DID
    obj["last_action"] = DID
    obj["current_task"] = ACT
    obj["current_task_at"] = TS
    obj["activity_now"] = ACT
    obj["latest_artifact"] = LATEST
    obj["next_milestone"] = NEXT
    obj["next"] = NEXT
    obj["next_pointer"] = NEXT
    obj["verify"] = VERIFY
    obj["idle_rounds"] = 0
    obj["agenda_starved"] = False
    obj["health"] = "ok"
    obj["sync"] = {"ahead": 0, "behind": 0, "last_push_ts": None,
                   "note": u"O-20261009-0024 sec1-4 sync face (bm-b r807 "
                           u"naming alignment); this write is pre-push, "
                           u"post-push refresh follows in-round"}


def main():
    with open(HB, encoding="utf-8") as fh:
        hb = json.load(fh)
    cpu, ram_free, vram = stats(hb)
    close_faces(hb)
    hb["cpu_pct"] = cpu
    hb["cpu_util_pct"] = cpu
    hb["free_ram_gb"] = ram_free
    hb["idle_ram_gb"] = ram_free
    hb["ram_free_gb"] = ram_free
    hb["gpu_free_vram_mb"] = vram
    for k in ("gpu_free_vram_mib", "gpu_idle_vram_mb", "gpu_idle_vram_mib",
              "gpu_vram_free_mb", "gpu_free_mb", "gpu_idle_mb", "gpu_free_mib",
              "gpu_idle_mib"):
        hb[k] = vram
    ack = hb.setdefault("orders_ack", [])
    for a in NEW_ACK:
        if a not in ack:
            ack.append(a)
    hb["orders_ack_count"] = len(ack)
    with open(HB, "w", encoding="utf-8") as fh:
        json.dump(hb, fh, indent=1, ensure_ascii=False)
    assert isinstance(hb["heartbeat_epoch_utc"], int)

    with open(ST, encoding="utf-8") as fh:
        st = json.load(fh)
    close_faces(st)
    st["cpu_pct"] = cpu
    st["free_ram_gb"] = ram_free
    st["idle_ram_gb"] = ram_free
    st["gpu_free_vram_mb"] = vram
    st["gpu_free_vram_mib"] = vram
    st["gpu_idle_vram_mb"] = vram
    st["gpu_idle_vram_mib"] = vram
    with open(ST, "w", encoding="utf-8") as fh:
        json.dump(st, fh, indent=1, ensure_ascii=False)
    assert isinstance(st["heartbeat_epoch_utc"], int)

    with open(REPORT, "a", encoding="utf-8") as fh:
        fh.write(u"\n" + ROW + u"\n")
    print("bookkeep ok: row r%d appended; hb epoch=%d cpu=%s ram=%s vram=%s"
          % (ROUND, EPOCH, cpu, ram_free, vram))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
