"""r719 bm-c close-out: state round_no bump, round-report line append,
heartbeat refresh (three-line face per P-2026-09-29-07 #5, epoch int
self-check per R170/R178, clock_read T-separator per R262).
Pattern credit: Tools/_r718bmc_close.py (canonical)."""
import datetime
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")  # T-separated, +08:00 offset


def fresh_metrics():
    m = {"cpu_pct": None, "ram_free_gb": None, "gpu_free_mb": None}
    try:
        import psutil
        m["cpu_pct"] = round(psutil.cpu_percent(interval=1.0), 1)
        vm = psutil.virtual_memory()
        m["ram_free_gb"] = round(vm.available / (1024 ** 3), 1)
    except Exception:
        pass
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                            "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=20)
        m["gpu_free_mb"] = int(r.stdout.strip().splitlines()[0])
    except Exception:
        pass
    return m


def main():
    m = fresh_metrics()

    # --- 1) state-bm-c.json round_no bump 719 -> 720
    sp = os.path.join(ROOT, "state-bm-c.json")
    st = json.load(open(sp, encoding="utf-8"))
    st["round_no"] = 720
    json.dump(st, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    # --- 2) round report line
    line_ts = TS
    rpt = (
        f"{line_ts} | r719 | dept:工程（复市 T-0 盘前值守轮·第 39 bm-c 连守轮·值守+QA 复验轮） | "
        "WM-VERDICT: 绿（red=false lane healthy·py_low_board_clear=板空+盘前无 bar 合法 idle 白名单"
        "〔板 0 open/176 ack/池 406 全 done〕·compute_audit 旗标 pool_starvation+supply_floor 照录"
        "=池 ready 0<floor 3·处置在册=引擎常供线 W181+ 投影+今晚盘后 bar 面天然候选供给"
        "+W16 波起草泊位 bm-a T-172〔never-dry 常设律·禁手工代烧〕） | "
        "当前活: r719 值守+QA 复验轮（盘前零盲动·无新产品线如实）——主产出="
        "①QA 39th 确定性包 qa/smoke-r719.md 5/5+qa/equity-curve-r719.png 66,249B"
        "（determinism=True·93 trades·equity 1,017,839 冻结恒等·market_clock rc0 cell=ORA"
        "·latest_panel_bar 2026-09-30 金周合法）"
        "②S6 40 腿链正典再生 Tools/_r719bmc_s6.py（r718 40 腿正典版克隆·40/40 rc0"
        "·dualrun ZERO-DRIFT streak 39·cta_p1_paper bar-门控诚实 no-op"
        "〔panel cutoff 2026-09-30<paper_start 2026-10-08→今晚首 bar 轮自动接线〕"
        "·fund_premium pre-15:30 no-op→今日 15:30 bm-c 车道首采·全 lane 守卫诚实 no-op） | "
        "S0=轮首脏 6=自家 daemon live faces→定向吸收 5927eff2d→净树 rebase up-to-date（behind=0）"
        "·origin/machine/bm-a-r857 新分支=bm-a 推送竞态代投面（其车道 S0-carry 自理·本机零触碰） | "
        "smoke 49/49 · S6 40/40 rc0 · QA 5/5（determinism=True 39th） · "
        "orders 双扫 unacked=0（51 disk/176 ack·S0.5 首扫零差+S7 收尾二扫同验） · "
        "DEC/ORD 双水位 UNCHANGED（EE659451/17accc40·算法对按 r716 钉〔DEC=SHA-256/ORD=SHA-1〕"
        "·hex-case 归一 r711 律·facts results/_r719bmc_s05_facts.json shape-asserted） · "
        "SAT 活 rc0（心跳 22.7s 新鲜·burns 0·队列空） · 板 0 open·job_list 0·"
        "backlog 2 可领=非本司域（游戏线）不领 · idle NOT-GREEN（RAM 17.6%<40% 常驻 ComfyUI"
        "·idle_rounds=0·--worked 申报） · post_review 零红（45✓/0✗/5🟡） · "
        "孤儿面=1（本机常驻 ComfyUI 服务面·CEO 私产·只读披露不击杀·既有处置维持） · "
        "attrition CLEAN（4 healed 注记照录） · "
        "自愈=loop pin=5 no-op+watchdog 重注册+双爪 IN-PLACE LF 归一 · "
        "token 面=L1 零 token 腿（token_meter rc0） · "
        "方法论捕获=无新方法（纯值守复用）·宝藏捕获=N/A（无五类收口批）"
        "·登记册零命中断言=N/A（无清扫/归档/恢复类动作） · "
        "**诚实注记：收尾 commit 1bdf6dbff 误复用 S0 absorb 消息文件=标签滑位"
        "（内容完备 75 面纯 bm-c 车道·git 史保全零手术·r701 判例）** · "
        "本地未达 origin commit 数=0（commit 后 push+fetch+rev-list 自证） | "
        "下轮 r720：(a) 5x=HANDOVER 产物清单核对更新（增量窗 r711-720） "
        "(b) 值守续（今日 09:15 复市首交易日·intraday marks 车道起活·盘前零盲动） "
        "(c) 今晚盘后面=数据链全门 re-arm+REGIME_GUARD v3 首新 bar enforce+fund_premium 15:30 首采"
        "（bm-c 车）+QDII watch 重跑长假差分+CTA_P1 首 bar 自动接线+首 marks 验证（≤10-08 23:59） "
        "(d) O-2215 ① 矩阵规格件+切换律 v1（≤10-16 12:00·待 bm-a REGIME-5 ≤10-14+bm-b 五态路由 spec 面） "
        "(e) O-2245 续作=首批 OSS- 落池件先过 Tools/oss_import_gate.py rc0 再 settle（bm-a ≤10-16） "
        "(f) cloudF 行收取窗 ≤10-14 常设 (g) 月界首考 10-31 | "
        "轮产品计分：2（QA 39th 确定性包=能跑能看实物+S6 40 腿再生面；值守窗零新产品线如实） | "
        "记账预算：3（state+心跳+轮报） [via bm-c r719]"
    )
    rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
    with open(rp, "a", encoding="utf-8", newline="") as f:
        f.write(rpt + "\n")

    # --- 3) heartbeat
    hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
    hb = json.load(open(hp, encoding="utf-8"))
    epoch = int(time.time())
    cpu = m["cpu_pct"] if m["cpu_pct"] is not None else hb.get("cpu_pct", 0.0)
    ram = m["ram_free_gb"] if m["ram_free_gb"] is not None else hb.get("free_ram_gb", 0.0)
    gpu = m["gpu_free_mb"] if m["gpu_free_mb"] is not None else hb.get("gpu_free_vram_mb", 0)
    current_task = (
        "当前活: r719 bm-c 值守+QA 复验轮（QA det-39th 5/5+S6 40 腿正典再生 streak 39·复市 T-0 盘前值守"
        "第 39 连守轮·盘前零盲动） | "
        f"最近实物: qa/smoke-r719.md 5/5（det 39th·93 trades·equity 1,017,839 冻结恒等）"
        f"+results/_r719bmc_s6_log.txt（40 legs rc0·dualrun streak 39）+Tools/_r719bmc_s6.py @ {TS} | "
        "下个里程碑: 今晚盘后（10-08 15:30+）数据链全门 re-arm+REGIME_GUARD v3 新 bar enforce"
        "+fund_premium 首采（bm-c 车）+QDII watch 长假差分重跑+CTA_P1 首 bar 自动接线+首 marks 验证"
        "（≤10-08 23:59）；09:15 起值守 intraday 面；r720=5x HANDOVER 核对面"
    )
    latest_artifact = (
        "qa/smoke-r719.md 5/5 + qa/equity-curve-r719.png 66,249B (determinism 39th, 93 trades, "
        "equity 1,017,839 frozen identity) + Tools/_r719bmc_s6.py + results/_r719bmc_s6_log.txt "
        "(40 legs rc0, dualrun ZERO-DRIFT streak 39) + results/_r719bmc_s05_facts.json (both "
        "watermarks unchanged) @ " + TS
    )
    verdict = (
        "r719 bm-c: watch + QA re-verify round (39th consecutive, 10-08 reopen T-0, 02:4x "
        "pre-open window, zero blind action). Product = QA 39th determinism pack (5/5, 93 "
        "trades, equity 1,017,839 frozen identity, png 66,249B, market_clock cell=ORA, "
        "latest_panel_bar 2026-09-30 golden-week expected) + S6 40-leg chain regen via Tools/"
        "_r719bmc_s6.py (clone of r718 canonical; 40/40 rc0; dualrun ZERO-DRIFT streak 39; "
        "cta_p1_paper bar-gated no-op auto-fires tonight first-bar; fund_premium pre-15:30 "
        "no-op -> today 15:30 bm-c-lane first snapshot). S0: round-start dirty 6 = own daemon "
        "faces -> targeted absorb 5927eff2d -> clean rebase up-to-date behind=0; origin/machine/"
        "bm-a-r857 new branch noted = bm-a push-race alternate-delivery face, their lane "
        "S0-carry, zero touch. Both watermarks UNCHANGED (EE659451/17accc40, algorithm pair "
        "per r716 pin, hex-case normalized per r711); orders unacked=0 both sweeps; SAT alive "
        "rc0 (hb 22.7s fresh, burns 0, queue empty); board 0 open; not green-idle (RAM "
        "resident ComfyUI), idle_rounds=0 worked-declared; post_review zero red (45/0/5); "
        "orphan face=1 (resident ComfyUI, no-kill standing disposition); attrition CLEAN (4 "
        "healed noted); self-heal = loop pin=5 no-op + watchdog re-registered + both claws "
        "IN-PLACE (LF-normalized); token L1 zero-token legs. Honest annotation: closeout "
        "commit 1bdf6dbff reused the S0 absorb message file = label slip (content complete "
        "75-face pure bm-c lane, git history preserved, zero surgery, r701 precedent)."
    )
    did = (
        "r719 bm-c: watch + QA 39th pack + S6 40-leg regen (10-08 reopen T-0, 39th consecutive "
        "watch round, 02:4x pre-open window). (1) S0: round-start dirty 6 = own daemon live "
        "faces -> targeted absorb 5927eff2d -> pull --rebase up-to-date (behind=0); "
        "origin/machine/bm-a-r857 new branch = bm-a push-race alternate delivery, their S0-"
        "carry lane, zero touch. (2) S0.5 sweeps 1+2: orders 51 disk/176 ack unacked=0 both; "
        "DEC EE659451 / ORD 17accc40 both UNCHANGED (SHA-256/SHA-1 pair per r716 pin, hex-case "
        "normalized per r711; facts results/_r719bmc_s05_facts.json, shape-asserted); inbox 0 "
        "unread. (3) S1 smoke 49/49. (4) S3: satengine rc0 alive (hb 22.7s, burns 0, queue "
        "empty); watermark green (py_low_board_clear legal idle whitelist); board 0 open; "
        "job_list 0; idle NOT-GREEN (RAM 17.6% resident), idle_rounds=0, --worked declared. "
        "(5) MAIN PRODUCT: QA 39th determinism pack 5/5 (93 trades, equity 1,017,839 frozen "
        "identity, png 66,249B) + S6 40-leg chain regen (Tools/_r719bmc_s6.py, r718 canonical "
        "clone; 40/40 rc0; dualrun ZERO-DRIFT streak 39; cta_p1_paper bar-gated honest no-op "
        "auto-fires tonight; fund_premium pre-15:30 no-op -> today 15:30 bm-c first snapshot; "
        "compute_audit flags pool_starvation+supply_floor recorded with standing disposition). "
        "(6) post_review zero red (45Y/0N/5WAIT); orphan face=1 no-kill documented; attrition "
        "CLEAN (4 healed noted); self-heal = loop pin=5 no-op + watchdog re-registered + both "
        "claws IN-PLACE LF-normalized; token L1 zero-token legs. (7) Product score 2 (QA "
        "evidence pack = runnable visible artifact + S6 regen face; honest zero new product "
        "lines in pre-open watch window). (8) Label slip honest annotation: closeout commit "
        "1bdf6dbff reused S0 absorb message file (r701 precedent, git history preserved)."
    )
    nxt = (
        "r720: (a) 5x HANDOVER product-list check/update (increment window r711-720); (b) watch "
        "continuation: today 09:15 reopen first trading day, intraday marks lane live, "
        "pre-open zero blind action until 09:15; (c) tonight post-close face (<=10-08 23:59): "
        "data-chain full re-arm + REGIME_GUARD v3 first-new-bar enforce + fund_premium 15:30 "
        "first snapshot (bm-c lane) + QDII watch rerun holiday-delta + CTA_P1 first-bar "
        "auto-wiring + first-marks verification (S6 cta_p1_paper leg; verify = marks 1 row + "
        "state trial-live + compounding identity); (d) O-2215 deliverable (1) matrix spec + "
        "switching law v1 (<=10-16 12:00; consumes bm-a REGIME-5 discriminator <=10-14 + bm-b "
        "five-state router spec); (e) O-2245 follow-ups: first OSS- enrollments (bm-a "
        "strategy-class adaptations <=10-16) must pass Tools/oss_import_gate.py rc0 before "
        "settle; (f) cloudF row collection window <=10-14 standing; (g) month-boundary first "
        "exam 10-31. [via bm-c r719]"
    )
    hb.update({
        "idle_rounds": 0, "agenda_starved": False,
        "heartbeat_epoch_utc": epoch,
        "last_seen": TS, "clock_read": TS, "ts": TS,
        "cpu_pct": cpu, "cpu_util_pct": cpu, "cpu_idle_pct": round(100 - cpu, 1) if cpu is not None else None,
        "free_ram_gb": ram, "idle_ram_gb": ram, "ram_free_gb": ram,
        "gpu_free_vram_mb": gpu, "gpu_idle_vram_mb": gpu, "gpu_vram_free_mb": gpu,
        "gpu_free_mb": gpu, "gpu_idle_mb": gpu, "gpu_free_mib": gpu,
        "gpu_idle_vram_mib": gpu, "gpu_idle_mib": gpu,
        "round_no": 720, "round_no_label": "round 719 (bm-c)",
        "last_round": 719, "last_round_at": TS,
        "current_task": current_task, "current_task_at": TS,
        "latest_artifact": latest_artifact,
        "next_milestone": (
            "今晚盘后: data-chain re-arm + REGIME_GUARD v3 first-new-bar enforce + fund_premium "
            "15:30 first snapshot (bm-c lane) + CTA_P1 first-bar auto-wiring + first-marks verify "
            "(<= 10-08 23:59); 09:15 起值守 intraday 面; r720=5x HANDOVER"
        ),
        "health": "ok",
        "activity_now": verdict, "did": did, "verdict": verdict,
        "note": ("r719: watch + QA det-39th 5/5 + S6 40-leg regen streak 39; both watermarks "
                 "unchanged; orders unacked=0; smoke 49/49; label-slip honest annotation."),
        "last_round_summary": ("r719: QA det-39th 5/5 + S6 40 rc0 streak 39; watermarks unchanged; "
                              "unacked=0; smoke 49/49; post_review zero red."),
        "last_action": ("r719: QA det-39th 5/5 + S6 40 rc0 streak 39; watermarks unchanged; "
                        "unacked=0; smoke 49/49; post_review zero red."),
        "next": nxt,
        "last_seen_at": TS, "updated_at": TS, "updated": TS,
        "last_run_at": TS, "last_ts": TS,
    })
    json.dump(hb, open(hp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    chk = json.load(open(hp, encoding="utf-8"))
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
    assert "T" in chk["clock_read"], "clock_read must be T-separated"
    print("close-out done:", TS, "| cpu", cpu, "| ram_free", ram, "| gpu_free", gpu,
          "| epoch int OK | state round_no -> 720 | report line appended | heartbeat written")


if __name__ == "__main__":
    main()
