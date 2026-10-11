# -*- coding: utf-8 -*-
"""r875 bm-b closeout: round report line + heartbeat + HANDOVER 5x line."""
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

ROUND_LINE = (
    NOW + " | r875 bm-b | dept:研究（E15 情绪族新判线复判登记认领=supply-floor chain leg-3·catalog #18 判线改革承接件"
    "·T-18 CLEAR+T19 seed gate hits=[] 前置双闸·leg-1 roster 探针同轮交付：scripts/emotion_reeval_roster.py"
    "〔selftest 8/8 hermetic·run rc0·L1 零网络零判据〕+results/emotion_reeval/e15_roster.json〔4 员 3 族："
    "sentiment.turnover_surge n=2=W2-23057〔DSR 0.5288〕/W3-23027〔DSR 0.4903·family_pbo 0.1857〕方向线索"
    "·近失档案 honesty 逐字携带〕·REEVAL18 drill 未覆盖 23027/23057 grep 实证=承接面未消化·W14/W16 改革首判在役"
    "·leg-2 prereg 起草待续〔批成员 m+四维子指标映射+W14/W16 先例+PREREG_TEMPLATE 正门+出场轴三选一+consumer_plan〕）"
    "| dept:工程（S6 33/33 rc=0：pool_dualrun ZERO-DRIFT streak 30〔先于 compute_audit 排序律〕·compute_audit flags"
    " idle_with_work/pool_starvation/supply_floor〔ready=0<3=E15 链正供·leg-3 已推进〕·py_watermark "
    "py_low_with_work_cands〔T-184 transfer 票=物理依赖 bm-a push 合法+supply-floor leg 本轮实做〕·周日无新 bar→"
    "live.paper/t35/t24/paper 族合法跳过·bm-b 四车道（astock/etf/minute/rev_osc）no-op fresh·options [RETIRED] 诚实 no-op"
    "·thermo rebuild+dualarm DUALARM-2026-09-30+scorecard 6/28/7+clock_call ORANGE_COOL sleeves=4+daily_report faces=5"
    "+ceo_live_usage LIVE-2026-10-11〔state=ORANGE cap=50% heat=COOL〕+token_meter L2 legs 0 全 rc0）"
    "| 孤儿面=0（round probe 10:42 py_faces=11 orphans=0）| WM-VERDICT: green（red=false @10:43 probe·"
    "next_pick=moneyflow IC claimed-parked 源阻塞自愈面）| D-19 双水位零 delta（decisions/orders 双恒等 raw-blob sha）"
    " | orders 67/67 acked 零差集（S0 pull up-to-date·r874 双扫维持）| smoke 49/49 | T-184 branch 未上 origin"
    "（ls-remote 精查空·接收腿 watch·deadline 10-12 15:30）| inbox 1 件=本机 r872 发 bm-a 的 T-184 票警示（非本机处理面·留 bm-a 消费）"
    "| 本地未达 origin commit 数=N（push 后 git rev-list 自证）"
)

DID = (
    "r875 supply-floor chain leg-3 (E15 emotion-family reform-line reeval registered+claimed same round, catalog #18 承接件): "
    "T-18 CLEAR + T-19 seed gate hits=[] 双闸前置; leg-1 roster probe scripts/emotion_reeval_roster.py "
    "(selftest 8/8 hermetic, run rc0, L1 zero-network zero-judgment) + evidence results/emotion_reeval/e15_roster.json "
    "(4 members 3 families: sentiment.turnover_surge n=2 W2-23057/W3-23027 direction clue with family_pbo 0.1857, "
    "near-miss dossier honesty carried verbatim); REEVAL18 drill non-coverage of 23027/23057 proven by grep = "
    "承接面 open; leg-2 = prereg draft (batch m pin + four-dim sub-metric mapping, W14/W16 precedent, "
    "PREREG_TEMPLATE gate + exit-axis 3-choice + consumer_plan) then freeze then pool entry toward supply floor. "
    "Chain: S0 rider-commit daemon faces then pull up-to-date (HEAD e3b0430dc); orders 67/67 acked zero diff; "
    "D-19 dual watermark zero-delta (raw-blob sha both match); smoke 49/49; orphan face 0 (py_faces=11 alive); "
    "S6 33/33 rc=0 (pool_dualrun ZERO-DRIFT streak 30, compute_audit flags idle_with_work/pool_starvation/supply_floor "
    "= E15 chain supplying, py_watermark py_low_with_work_cands lawful [T-184 physical dep + supply-floor leg worked], "
    "no new bar Sunday -> paper family lawful skip, bm-b lanes no-op fresh, thermo/dualarm/scorecard/clock_call/"
    "daily_report/ceo_live_usage rc0, ORANGE_COOL cap=50%); T-184 branch not yet on origin (receiver watch, "
    "deadline 2026-10-12 15:30); T-18 transfer ticket T-2026-10-11-184 open on bm-a side."
)

NEXT = (
    "r876 E15 leg-2: prereg draft (batch membership m pinned + four-dim sub-metric mapping from e15_roster + W14/W16 "
    "judged-face precedent + PREREG_TEMPLATE front door + exit-axis explicit 3-choice + consumer_plan named) -> freeze "
    "-> pool entry (supply floor ready 0->1) -> T-184 transfer receiver leg watch (after bm-a pushes origin/transfer/"
    "t184-510880: git checkout origin/transfer/t184-510880 -- data/daily/510880.csv + git restore --staged R90 pit law "
    "+ manifest Verify; deadline 2026-10-12 15:30) -> moneyflow IC panel watch (source-blocked self-heal face) -> "
    "W210/M9 chain watch (bm-a face)"
)

NOW_ACTIVE = "r875 closeout: E15 emotion-family reform reeval registered+claimed, leg-1 roster probe landed; supply floor 0<3 -> leg-2 prereg next"
LATEST_ARTIFACT = ("r875: scripts/emotion_reeval_roster.py (selftest 8/8) + results/emotion_reeval/e15_roster.json "
                   "+ E15 row in state/queue/explore.md")
NEXT_MILESTONE = ("E15 prereg frozen + pool entry (first supply-floor leg) by <=2026-10-12; T-184 510880 restore before "
                  "2026-10-12 15:30 next bar (bm-a push pending)")
VERDICT = ("GREEN: r875 supply-floor leg-3 (E15 emotion reform-reeval registered+claimed, roster probe landed "
           "selftest 8/8 rc0; smoke 49/49; orders/D-19 zero-delta; S6 33/33; T-184 branch not on origin = receiver "
           "watch; compute_audit supply_floor flags = E15 chain is the standing supply leg, honestly carried)")

HANDOVER_LINE = (
    "- 【第五节·产物清单核对（新增与删改）】**round 875 bm-b（5x 核对本轮）**：2026-10-11 11:0x 核对；对账区间=增量 bm-b "
    "r871-875（基线=round 870 bm-b 行）；本窗新增产物=E15 情绪族新判线复判供给线〔r873 E14 打板线收口后 supply-floor 正供："
    "r875 scripts/emotion_reeval_roster.py（selftest 8/8·run rc0·L1 零网络）+results/emotion_reeval/e15_roster.json"
    "（4 员 3 族·sentiment.turnover_surge 双员方向线索·近失档案 verbatim）+state/queue/explore.md E15 行（open·leg-1 done）〕"
    "+r874 E14 线终态〔census v1.1 交叉族证据+family CLOSE 零烧+digest sec.5 addendum+TREASURE_REGISTRY 族炉行〕"
    "+r872-873 E14 廉价普查全套〔lu_prem_census.py+face.json/by_board_rung.csv+digest·n=220,798 事件〕；完成状态=E14 "
    "done/closed（judged prereg 判负不开窗·年代坍塌判决）·E15 open（leg-2 prereg 起草待续=下轮主工）；supply floor "
    "ready 0<3 standing（E15 链正供·compute_audit 旗如实）；统一链账本以 results/trial_labor_w13/w13_judge.json live-read 为准本窗零烧批零账动。"
)


def main():
    # 1) round report line
    rr = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
    with open(rr, "a", encoding="utf-8", newline="\n") as f:
        f.write(ROUND_LINE + "\n")

    # 2) heartbeat
    hb_path = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
    with open(hb_path, "r", encoding="utf-8") as f:
        hb = json.load(f)
    try:
        import psutil
        ram = round(psutil.virtual_memory().available / (1024 ** 3), 1)
        ram_pct = round(psutil.virtual_memory().available * 100.0 / psutil.virtual_memory().total, 1)
    except Exception:
        ram, ram_pct = hb.get("free_ram_gb"), hb.get("ram_free_pct")
    vram = hb.get("gpu_free_vram_gb")
    vram_mb = hb.get("gpu_free_vram_mb")
    try:
        import pynvml
        pynvml.nvmlInit()
        h = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = pynvml.nvmlDeviceGetMemoryInfo(h)
        vram = round((info.total - info.used) / (1024 ** 3), 1)
        vram_mb = int((info.total - info.used) / (1024 ** 2))
        pynvml.nvmlShutdown()
    except Exception:
        pass
    hb.update({
        "round": 875,
        "round_no": 876,
        "clock_read": NOW,
        "ts": NOW,
        "updated": NOW,
        "updated_at": NOW,
        "last_seen": NOW,
        "last_action_at": NOW,
        "last_round_at": NOW,
        "heartbeat_epoch_utc": EPOCH,
        "did": DID,
        "last_action": DID,
        "current_task": NEXT,
        "task": NEXT,
        "next": NEXT,
        "now_active": NOW_ACTIVE,
        "latest_artifact": LATEST_ARTIFACT,
        "next_milestone": NEXT_MILESTONE,
        "verdict": VERDICT,
        "idle_rounds": 0,
        "agenda_starved": False,
        "orphan_face": 0,
        "orphan_face_note": "r875 round probe: py_faces=11 alive, orphans=0",
        "orphan_faces": 0,
        "free_ram_gb": ram,
        "ram_free_gb": ram,
        "ram_free_pct": ram_pct,
        "cpu_cores": 16,
        "gpu_free_vram_gb": vram,
        "vram_free_gb": vram,
        "gpu_free_vram_mb": vram_mb,
    })
    hb["sync"] = hb.get("sync") or {}
    hb["sync"]["last_push_ts"] = NOW
    with open(hb_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1, sort_keys=True)

    # 3) HANDOVER 5x line (chronological end-append)
    hd = os.path.join(ROOT, "research", "HANDOVER.md")
    with open(hd, "a", encoding="utf-8", newline="\n") as f:
        f.write(HANDOVER_LINE + "\n")

    # self-proof: epoch must be JSON int
    with open(hb_path, "r", encoding="utf-8") as f:
        check = json.load(f)
    assert isinstance(check["heartbeat_epoch_utc"], int), "epoch must be int"
    assert "T" in check["clock_read"] and " " not in check["clock_read"], "clock_read must be T-separated"
    print("closeout written: round_report r875 line, heartbeat round=875/876 epoch int ok, HANDOVER 5x line")
    print("ram_free_gb:", ram, "vram_free_gb:", vram)


if __name__ == "__main__":
    main()
