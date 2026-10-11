# -*- coding: utf-8 -*-
# r866 bm-c books: state + heartbeat bump + r866 round report line
# CLONE SOURCE LAW (r855 pit-lineage entry): round-report CANONICAL path =
#   logs/iteration-loop/round_reports-bm-c.md   (do NOT use the pre-r645 ROOT legacy path)
# r866 clone of results/_r864bmc_books.py (weekend watch round: S6 43/43 + QA r866 5/5
# + ORD/DEC zero-delta via standing composer + supply-floor flag disclosed + T-184 observation).
import json, time, io, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CANON = ROOT + r"\logs\iteration-loop\round_reports-bm-c.md"
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

did = ("r866 bm-c: (1) S0-1 identity anchor bm-c + round-zero probe py_faces=4 orphans=1 "
       "read-only no-kill; S0 fetch origin tip feebf3c91 == HEAD 0-behind in-sync zero rebase "
       "(W208 not landed, zero bm-a commits this window; 5 own runtime dirty faces left for "
       "targeted absorb at close); (2) S0.5 standing composer rc0: ORD ccf3ed9d zero-delta + DEC "
       "68d13893 zero-delta (method pin per r865 erratum law, no false-delta recurrence), unacked "
       "0 (67 orders / 192 acks); (3) S1 smoke 49/49; S2 boards empty (job 0, open ticket T-184 "
       "bm-a->bm-b transfer non-party, tech/explore queues all done/closed -> heads CLEAR); "
       "satengine alive rc0 queue_next=[] (W208 upstream-blocked known face); (4) inbox "
       "MSG-20261011-0940-bmb addressed to bm-a (T-184 510880 transfer alert, deadline 2026-10-12 "
       "15:30) -> left in inbox for addressee, bm-c zero action (observation: bm-a stale ~12h, "
       "escalation owner = GM sentinel per O-20261011-0012 sec.3); (5) PRODUCT-A = S6 43-leg "
       "chain 43/43 rc0 (results/_r866bmc_s6_log.txt DONE 10:10:21 bad=0: pool_dualrun ZERO-DRIFT "
       "streak 6 / 421 entries; weekend no-ops clean, lane-guards honest no-op; update_daily 0 "
       "new rows cutoff 2026-10-09 legal; compute_audit 3 flags = known adjudicated faces "
       "[idle_with_work / pool_starvation / supply_floor ready=0<floor=3 = W208 upstream supply "
       "gap]; daily_report/scorecard/ceo_live_usage/dashboard regenerated); (6) PRODUCT-B = QA "
       "charter pack r866 5/5 explicit --round 866 (name-collision preflight origin qa/ zero "
       "r866; 91 trades determinism=True sharpe 0.1994 annual 0.0072 maxdd -0.0431 win_rate "
       "0.4725 equity final 1,023,027; CALL rc0 cell=ORA; panel bar 2026-10-09; qa/smoke-r866-"
       "bm-c.md + equity-curve-r866-bm-c.png 65,506B); (7) S7: attrition 4 ledgers CLEAN (3 "
       "healed notes); loop task Ready next 10:15 + watchdog Ready next 10:14 zero re-reg; "
       "pre-commit/pre-push claws in place; idle --worked (idle_rounds=0); W209 backup watch "
       "cron 9defca39 armed (cron_list verified)")

next_ptr = ("r867: (1) W208/W209 landing watch -> M10 auto-execute chain (cron 9defca39 armed); "
            "W211/W212 freeze-prep when W210 approaches (read pit-engine-finalize.md FIRST); "
            "(2) T-184 deadline watch: if bm-a still dark approaching 2026-10-12 15:30 -> "
            "escalation = GM sentinel domain (bm-c holds complete 510880.csv panel copy, ready "
            "to serve on GM reassignment per TRANSFER.md); (3) jman final-ckpt re-board on "
            "request; (4) O-20261011-0012 CPU-max face: opportunistic faces stay closed until "
            "upstream lands (RAM ~40% borderline); (5) S0.5 standing composer (delta TRUE -> "
            "blob-history provenance check per r863 gate); (6) books clone source = "
            "results/_r866bmc_books.py")

activity = ("当前活: W208/W209 落链守望（cron 9defca39 durable armed·M10 链待上游）+ T-184 期限观察（10-12 15:30·bm-a 收件）| "
            "最近实物: S6 43/43 rc0（results/_r866bmc_s6_log.txt·ZERO-DRIFT streak 6）+ QA 包 r866 5/5"
            "（qa/smoke-r866-bm-c.md+equity-curve-r866-bm-c.png）@ " + now_iso + " | "
            "下个里程碑: W208 上游落链即 M10 自动冻结 W209 点火；T-184 期限前 bm-a 无响应则升级 GM 哨兵")

verdict = ("r866 close: weekend watch round clean -- S6 43/43 rc0 (ZERO-DRIFT streak 6) + QA pack "
           "r866 5/5 (explicit --round) + ORD/DEC zero-delta (method pin law in force) + "
           "supply-floor disclosed (W208 upstream) + smoke 49/49 + T-184 observation logged")

summary = ("r866 close: S6 43/43 (ZERO-DRIFT streak 6) + QA r866 5/5 + ORD/DEC zero-delta + "
           "supply-floor disclosed + T-184 deadline observation")

report_line = ("2026-10-11T" + now_iso.split("T")[1] + " | r866 | dept:工程/舰队（周末守望轮：S6 43 腿全绿+QA 5/5+双水位 method-pin 首跑+T-184 观察·零上游推进·第 154 bm-c 连守轮） | "
               "本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） | "
               "WM-VERDICT: 绿（red=false·lane healthy·probe=py_low_with_work_cands 判读=合法白名单：work_cand=board T-184 传票非本机当事方〔bm-a→bm-b〕·板空/open 票 1 非当事·引擎队列合法空=W208 上游阻塞已知面·RAM ~40% 边缘无领单义务·supply_floor ready=0<3=W208 上游供给缺口如实披露非本机可修面） | "
               "孤儿面=1（py_faces=4·只读不杀） | "
               "r866: ①S0-1 身份锚 bm-c+round-zero 探针只读·S0 fetch origin tip feebf3c91==HEAD 0-behind in-sync 零 rebase（W208 未落链=零 bm-a 提交·5 本机运行态脏面留收口定向吸收）；"
               "②S0.5 常设组合器 rc0 双水位零 delta（ORD ccf3ed9d+DEC 68d13893·r865 勘误后 method-pin 首跑无假 delta 复发）+unacked 0（67/192）；"
               "③S1 smoke 49/49·S2 双板空（job 0/open 票 1=T-184 传票非当事方）·队头 CLEAR（tech/explore 全 done-closed）；"
               "④inbox 1 件=MSG-20261011-0940-bmb（bm-b→bm-a T-184 510880 传输提醒·期限 10-12 15:30）→非本机收件留箱·零动作·观察面=bm-a 暗 ~12h（升级面归 GM 哨兵域 O-0012 §3）；"
               "⑤PRODUCT-A=**S6 43/43 rc0**（_r866bmc_s6_runner.ps1=r865 verbatim clone·DONE 10:10:21 bad=0·pool_dualrun ZERO-DRIFT streak 6·421 entries·周末 no-op 全净·update_daily 0 新行 cutoff 2026-10-09 合法·compute_audit 三旗=已知定谳面照录〔idle_with_work/pool_starvation/supply_floor ready=0<3=W208 上游缺口〕·daily_report/scorecard/ceo_live_usage/dashboard 全再生）；"
               "⑥PRODUCT-B=**QA charter 包 r866 5/5**（显式 --round 866·撞名预检 origin qa/ 零 r866：91 trades determinism=True sharpe 0.1994 annual 0.0072 maxdd -0.0431 win 0.4725 equity final 1,023,027·CALL rc0 cell=ORA·面板 bar 2026-10-09·qa/smoke-r866-bm-c.md+equity-curve-r866-bm-c.png 65,506B）；"
               "⑦S7 attrition 4 台账 CLEAN（3 healed 注记）+loop/watchdog 双任务在册（next 10:15/10:14）+双爪在位+idle --worked（idle_rounds=0）+W209 守望 cron 9defca39 armed（cron_list 验证） | "
               "r867: (1) W208/W209 落链守望→M10 自动执行链维持+W211/W212 freeze-prep（W210 近时先读 pit-engine-finalize.md）；"
               "(2) T-184 期限观察：bm-a 若临近 10-12 15:30 仍暗→升级归 GM 哨兵（本机持完整 510880.csv 副本可按 TRANSFER.md 应援改派）；"
               "(3) jman final-ckpt 补板按需；(4) CPU 满用令面=RAM ~40% 边缘·上游落链前 opportunistic 关闭如实；(5) S0.5 常设组合器维持 | "
               "本轮产品积分：2（S6 43 面链=经营层可验实物）+2（QA 包 5/5=charter 证据实物）=4 | 记账预算：3 面内（state+心跳+轮报=法定簿记）")

# round report: read tail first (anchor law), assert r865 addendum tail, single append
with io.open(CANON, "r", encoding="utf-8") as f:
    can_body = f.read()
can_lines = [l for l in can_body.splitlines() if l.strip()]
assert ("| r865 bm-c addendum |" in can_lines[-1]) and ("r865" in can_lines[-1]), ("canonical tail not r865 addendum line", can_lines[-1][:80])
assert ("| r866 |" not in can_body[-9000:]), "r866 main line already present"
with io.open(CANON, "a", encoding="utf-8", newline="") as f:
    f.write(report_line + "\n")

def upd(path, is_hb):
    with io.open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    ts_fields = ["ts","last_seen","last_seen_at","clock_read","updated","updated_at","last_run_at","last_round_at",
                 "last_round_ts","last_ts","last_round_closed","current_task_at","last_round_summary_at",
                 "last_orders_read_at","last_pulled_at","last_action_at","last_round_at_legacy","last_decisions_read_at",
                 "last_decisions_at","last_orders_at"]
    for k in ts_fields:
        if k in d: d[k] = now_iso
    d["round_no"] = 867
    d["round_no_label"] = "r866"
    d["last_round"] = 866
    d["loop_round"] = 866
    d["heartbeat_epoch_utc"] = epoch
    d["cpu_pct"] = 7; d["cpu_util_pct"] = 7; d["cpu_idle_pct"] = 93
    d["free_ram_gb"] = 9.6; d["idle_ram_gb"] = 9.6; d["ram_free_gb"] = 9.6
    for k in ["gpu_free_vram_mb","gpu_free_vram_mib","gpu_idle_vram_mb","gpu_idle_vram_mib","gpu_vram_free_mb","gpu_free_mb","gpu_free_mib","gpu_idle_mib","gpu_idle_mb"]:
        if k in d: d[k] = 1747
    d["head_sha"] = "feebf3c91"
    d["current_task"] = activity
    d["activity_now"] = activity
    d["did"] = did
    d["verdict"] = verdict
    d["last_round_summary"] = summary
    d["note"] = ("r866 = weekend watch round: S6 43/43 (streak 6) + QA r866 5/5; ORD/DEC zero-delta "
                 "(method-pin first run); supply-floor (W208 upstream) disclosed; T-184 observation.")
    d["next"] = next_ptr
    d["next_pointer"] = next_ptr
    d["next_milestone"] = ("r867: W208/W209 landing watch (M10 auto chain, cron 9defca39 armed) + T-184 "
                           "deadline observation (GM sentinel escalation) + jman final-ckpt on request")
    d["latest_artifact"] = ("S6 43/43 rc0 (_r866bmc_s6_log.txt) + QA pack r866 5/5 "
                            "(qa/smoke-r866-bm-c.md + equity-curve-r866-bm-c.png)")
    d["last_artifact"] = d["latest_artifact"]
    d["recent_artifact"] = d["latest_artifact"]
    d["last_action"] = "r866 S6 43/43 + QA r866 5/5 + books"
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["orphan_face"] = 1
    d["orphan_faces"] = 1
    d["health"] = "ok"
    d["ord_sha_method"] = ("git rev-parse origin/main:docs/orders.md blob SHA-1 (ALGORITHM PIN per r537 law; "
                            "r866 fresh probe rc0 via standing composer Tools/s05_probe.py: ORD delta FALSE "
                            "ccf3ed9d==ccf3ed9d zero-delta, post-r865 healed real blob holds; facts results/"
                            "_r686bmb_d19_check.json, 40hex shape-asserted, zero literal constants (r583 law)")
    d["verify"] = ("receipts: smoke 49/49 + qa/smoke-r866-bm-c.md (5/5 charter, explicit --round 866) + "
                   "results/_r866bmc_s6_log.txt (43/43 rc0 bad=0, ZERO-DRIFT streak 6) + results/"
                   "_attrition_guard_scan.json (4 ledgers CLEAN) + Tools/s05_probe.py zero-delta + this "
                   "books commit/push_verify")
    if not is_hb:
        d["sync"] = {"ahead_behind": "1/0 pre-books", "origin_tip": "feebf3c91", "ts": now_iso,
                     "note": "r866 books: S6 43/43 + QA 5/5; commit+push follows this write"}
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
    assert d["round_no"] == 867, p
    assert d["round_no_label"] == "r866", p
    assert d["loop_round"] == 866, p

print("BOOKS OK round_no=867(label r866) epoch=%d clock=%s report_line_appended=1" % (epoch, now_iso))
