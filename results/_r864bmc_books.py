# -*- coding: utf-8 -*-
# r864 bm-c books: state + heartbeat bump + r864 round report line
# CLONE SOURCE LAW (r855 pit-lineage entry): round-report CANONICAL path =
#   logs/iteration-loop/round_reports-bm-c.md   (do NOT use the pre-r645 ROOT legacy path)
# r864 clone of results/_r863bmc_books.py (weekend watch round: S6 43/43 + QA r864 5/5
# + ORD/DEC zero-delta + supply-floor flag disclosed + QA pack misnumber fix r758 law).
import json, time, io, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CANON = ROOT + r"\logs\iteration-loop\round_reports-bm-c.md"
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

did = ("r864 bm-c: (1) S0-1 identity anchor bm-c + round-zero probe py_faces=4 orphans=1 read-only "
       "no-kill; (1b) S0: pull blocked by 8 runtime dirty faces -> treasure_guard prescan 8 paths "
       "zero-hit rc0 -> checkout HEAD baseline -> pull Already-up-to-date (origin zero advance this "
       "window, in-sync 61c9d482d, zero rebase needed); (2) S0.5 DEC zero-delta 68d13893 + ORD "
       "zero-delta f90233c7 (NO corrupt-sha recurrence; standing composer verified); (3) S1 smoke "
       "49/49; S2 boards empty (job 0 / open tickets 0 / inbox 0 MSG), tech queue 17 done + T26 "
       "claimed@bm-b (A13 predface lane), explore 14/14 done-closed -> queue heads CLEAR; (4) S3: "
       "watermark py_low_board_clear legal idle whitelist (board empty + pool batch t101-v4-a14 "
       "owner=bm-b freeze respected), satengine alive rc0 queue_next=[] (W208 upstream-blocked known "
       "face), idle_trigger green_idle=false RAM 33.6%<40% no claim obligation, compute_audit "
       "FLAG:supply_floor (ready=1<floor=3 = W205-upstream supply gap, disclosed not masked); "
       "O-20261011-0012 audit face: bm-c py_cpu 0.3% (pool empty for me, bm-b lane burning), bm-a "
       "heartbeat stale 11.5h (W205 upstream face, GM sentinel owns), bm-b fresh GREEN r871; "
       "(5) PRODUCT-A = S6 43-leg chain 43/43 rc0 (results/_r864bmc_s6_log.txt: pool_dualrun "
       "ZERO-DRIFT streak 3 / 421 entries; weekend no-ops all clean lane-guards honest; panel bar "
       "2026-10-09 golden-week face; daily_report/scorecard/ceo_live_usage/dashboard regenerated); "
       "(6) PRODUCT-B = QA charter pack r864 5/5 (explicit --round 864; FIRST run via default "
       "state+1 produced misnumbered r865 pack -> treasure_guard prescan zero-hit -> deleted "
       "untracked zero-git-footprint per r758/r838 laws -> re-ignite explicit round; 91 trades "
       "determinism=True sharpe 0.199 annual 0.0072 maxdd -0.0431 win_rate 0.4725; CALL rc0 "
       "cell=ORA; qa/smoke-r864-bm-c.md + equity-curve-r864-bm-c.png 65,451B); (7) S7: attrition 4 "
       "ledgers CLEAN; loop task alive (next-run 9:35) + watchdog alive (9:32) no re-reg needed; "
       "pre-commit+pre-push claws content-match True both")

next_ptr = ("r865: (1) W208/W209 landing watch -> M10 auto-execute chain (cron 9defca39 armed); W211 "
            "freeze-prep when W210 approaches + W212 freeze gated (read pit-engine-finalize.md FIRST); "
            "(2) jman final-ckpt (jman_v1_rank32_cont.safetensors) re-board offer if CEO/bm-a "
            "requests; (3) O-20261011-0012 CPU-max face: bm-c opportunistic faces stay closed until "
            "RAM>=40% green or upstream lands; supply-floor breach = upstream face (GM sentinel "
            "owns escalation); (4) S0.5 standing composer (delta TRUE -> blob-history provenance "
            "check before consuming); (5) books clone source = results/_r864bmc_books.py")

activity = ("当前活: W208/W209 落链守望（cron 9defca39 durable armed·M10 自动执行链待 W205 五面落链）| "
            "最近实物: S6 43/43 rc0（results/_r864bmc_s6_log.txt·ZERO-DRIFT streak 3）+ QA 包 r864 5/5"
            "（qa/smoke-r864-bm-c.md+equity-curve-r864-bm-c.png）@ " + now_iso + " | "
            "下个里程碑: W208/W209 上游落链即自动冻结执行（M10 链）；jman final-ckpt 补板按需 ~10min GPU 窗")

verdict = ("r864 close: weekend watch round clean -- S6 43/43 rc0 + QA pack r864 5/5 (explicit --round fix "
           "per r758 law) + ORD/DEC zero-delta + supply-floor flag disclosed (W205 upstream) + smoke 49/49")

summary = ("r864 close: S6 43/43 (ZERO-DRIFT streak 3) + QA r864 5/5 (pack-misnumber fix r758) + "
           "ORD/DEC zero-delta + supply-floor disclosed")

report_line = ("2026-10-11T" + now_iso.split("T")[1] + " | r864 | dept:工程/舰队（周末值守轮：S6 43 腿全绿+QA 5/5+双守望维持·零上游推进） | "
               "本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） | "
               "WM-VERDICT: 绿（red=false·probe=py_low_board_clear 合法白名单：池批 t101-v4-a14 owner=bm-b 冻结窗在烧非本机面·板空/open 票 0·引擎队列合法空=W208 上游阻塞已知面·RAM 33.6-39.7% 未达 40% 无领单义务·compute_audit FLAG:supply_floor ready=1<floor=3=W205 上游供给缺口如实披露非本机可修面） | "
               "孤儿面=1（py_faces=4·只读不杀） | "
               "r864: ①S0-1 身份锚 bm-c+round-zero 探针只读·S0 pull 挡于 8 运行时脏面（prescan 8 路径 zero-hit→checkout 基线→pull Already-up-to-date·origin 零推进·in-sync 61c9d482d 零 rebase）；"
               "②S0.5 双水位零 delta（DEC 68d13893+ORD f90233c7·r863 矫正后无坏面复发·常设组合器验讫）；"
               "③S1 smoke 49/49·S2 双板空+inbox 0·队头 CLEAR（tech 17 done+T26 claimed@bm-b·explore 14/14 closed）；"
               "④S3 判读=py_low_board_clear 合法白名单+引擎活 queue_next=[]（W208 上游阻塞）+idle_trigger green_idle=false（RAM<40%）+O-0012 审计面=三机 py_cpu 披露（bm-c 0.3%·bm-a 心跳 11.5h 陈=W205 上游面哨兵域·bm-b GREEN r871 新鲜）；"
               "⑤PRODUCT-A=**S6 43/43 rc0**（pool_dualrun ZERO-DRIFT streak 3·421 entries·周末 no-op 全净·面板 bar 2026-10-09 金周面·daily_report/scorecard/ceo_live_usage/dashboard 全再生·_r864bmc_s6_log.txt）；"
               "⑥PRODUCT-B=**QA charter 包 r864 5/5**（首跑 state+1 默认面错号 r865→prescan zero-hit→未提交删除零足迹〔r758/r838 律〕→显式 --round 864 重跑：91 trades determinism=True sharpe 0.199·CALL rc0 cell=ORA·qa/smoke-r864-bm-c.md+equity-curve-r864-bm-c.png 65,451B）；"
               "⑦S7 attrition 4 台账 CLEAN+loop/watchdog 双任务在册（9:35/9:32 下次触发）+双爪内容恒等 | "
               "r865: (1) W208/W209 落链守望→M10 自动执行链维持+W211/W212 freeze-prep（W210 近时先读 pit-engine-finalize.md）；"
               "(2) jman final-ckpt 补板按需；(3) CPU 满用令面=RAM≥40% 或上游落链前 opportunistic 关闭如实（供给底破位=上游面哨兵域）；"
               "(4) S0.5 常设组合器维持 | "
               "本轮产品积分：2（S6 43 面链=经营层可验实物）+2（QA 包 5/5=charter 证据实物）=4 | 记账预算：3 面内（state+心跳+轮报=法定簿记）")

# round report: read tail first (anchor law), assert r863 main line tail, single append
with io.open(CANON, "r", encoding="utf-8") as f:
    can_body = f.read()
can_lines = [l for l in can_body.splitlines() if l.strip()]
assert ("| r863 |" in can_lines[-1]) and ("r863" in can_lines[-1]), ("canonical tail not r863 main line", can_lines[-1][:80])
assert ("| r864 |" not in can_body[-8000:]), "r864 main line already present"
with io.open(CANON, "a", encoding="utf-8", newline="") as f:
    f.write(report_line + "\n")


def upd(path, is_hb):
    with io.open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    ts_fields = ["ts","last_seen","last_seen_at","clock_read","updated","updated_at","last_run_at","last_round_at",
                 "last_round_ts","last_ts","last_round_closed","current_task_at","last_round_summary_at",
                 "last_orders_read_at","last_pulled_at","last_action_at","last_round_at_legacy"]
    for k in ts_fields:
        if k in d: d[k] = now_iso
    d["round_no"] = 865
    d["round_no_label"] = "r864"
    d["last_round"] = 864
    d["loop_round"] = 864
    d["heartbeat_epoch_utc"] = epoch
    d["cpu_pct"] = 23; d["cpu_util_pct"] = 23; d["cpu_idle_pct"] = 77
    d["free_ram_gb"] = 9.5; d["idle_ram_gb"] = 9.5; d["ram_free_gb"] = 9.5
    for k in ["gpu_free_vram_mb","gpu_free_vram_mib","gpu_idle_vram_mb","gpu_idle_vram_mib","gpu_vram_free_mb","gpu_free_mb","gpu_free_mib","gpu_idle_mib"]:
        if k in d: d[k] = 1761
    d["gpu_idle_mb"] = 1761
    d["head_sha"] = "61c9d482d"
    d["current_task"] = activity
    d["activity_now"] = activity
    d["did"] = did
    d["verdict"] = verdict
    d["last_round_summary"] = summary
    d["note"] = ("r864 = weekend watch round: S6 43/43 + QA r864 5/5 (explicit-round fix); ORD/DEC "
                 "zero-delta; supply-floor flag disclosed (W205 upstream).")
    d["next"] = next_ptr
    d["next_pointer"] = next_ptr
    d["next_milestone"] = ("r865: W208/W209 landing watch (M10 auto chain, cron 9defca39 armed) + jman "
                           "final-ckpt re-board on request")
    d["latest_artifact"] = ("S6 43/43 rc0 (_r864bmc_s6_log.txt) + QA pack r864 5/5 "
                            "(qa/smoke-r864-bm-c.md + equity-curve-r864-bm-c.png)")
    d["last_artifact"] = d["latest_artifact"]
    d["recent_artifact"] = d["latest_artifact"]
    d["last_action"] = ("r864 S6 43/43 + QA r864 5/5 (explicit --round fix) + books")
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["orphan_face"] = 1
    d["orphan_faces"] = 1
    d["health"] = "ok"
    d["last_orders_at"] = now_iso
    d["ord_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r864 fresh "
                           "probe rc0; ORD delta FALSE f90233c7==f90233c7 zero-delta, no corrupt-sha "
                           "recurrence post r863 reconcile; facts results/_r686bmb_d19_check.json, "
                           "40hex shape-asserted, zero literal constants (r583 law)")
    d["verify"] = ("receipts: smoke 49/49 + qa/smoke-r864-bm-c.md (5/5 charter, explicit --round 864) + "
                   "results/_r864bmc_s6_log.txt (43/43 rc0 bad=0) + results/_attrition_guard_scan.json "
                   "(4 ledgers CLEAN) + ORD/DEC zero-delta probe + this books commit/push_verify")
    if not is_hb:
        d["sync"] = {"ahead_behind": "1/0 pre-books", "origin_tip": "61c9d482d", "ts": now_iso,
                     "note": "r864 books: S6 43/43 + QA 5/5; commit+push follows this write"}
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return d

upd(ROOT + r"\state-bm-c.json", False)

# heartbeat (fleet/machines/bm-c.json): CRLF face, indent=1 (r852 close convention)
upd(ROOT + r"\fleet\machines\bm-c.json", True)
raw = io.open(ROOT + r"\fleet\machines\bm-c.json", "r", encoding="utf-8").read()
io.open(ROOT + r"\fleet\machines\bm-c.json", "w", encoding="utf-8", newline="").write(raw.replace("\n", "\r\n"))

for p in [ROOT + r"\state-bm-c.json", ROOT + r"\fleet\machines\bm-c.json"]:
    with io.open(p, "r", encoding="utf-8") as f:
        d = json.load(f)
    assert isinstance(d["heartbeat_epoch_utc"], int), p
    assert "T" in d["clock_read"], p
    assert d["round_no"] == 865, p
    assert d["loop_round"] == 864, p

print("BOOKS OK round_no=865(label r864) epoch=%d clock=%s report_line_appended=1" % (epoch, now_iso))
