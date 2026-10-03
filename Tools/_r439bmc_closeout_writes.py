# -*- coding: utf-8 -*-
"""r439 bm-c closeout writer: T-134 lineage, round report, state, heartbeat."""
import datetime
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())


def probe_cpu():
    try:
        import psutil
        return round(psutil.cpu_percent(interval=0.4), 1)
    except Exception:
        return None


def probe_ram():
    try:
        import psutil
        return round(psutil.virtual_memory().available / (1024 ** 3), 1)
    except Exception:
        return None


def probe_gpu():
    try:
        import subprocess
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10,
            creationflags=0x08000000)
        return int(r.stdout.strip().splitlines()[0])
    except Exception:
        return None


def main():
    # ---- 1. T-134 claim_note append ----
    tp = os.path.join(ROOT, "fleet", "tasks", "T-2026-09-30-134-P1.json")
    t = json.load(open(tp, encoding="utf-8"))
    assert t.get("claimed_by") == "bm-c", "ticket owner drift"
    add = (" | s2 PICK-9 RESCAN r439 bm-c (receipt results/_r439bmc_t134_pick9.json): "
           "bond_panel_puller (6 burns, most-burned remaining) ADJUDICATED EXEMPT "
           "(network-serial 2.5s/member; ProcessPool = parallel source pressure vs "
           "r175 fuse/cooldown discipline; S6 updater-gate pattern = correct future "
           "refresh route per census out_of_scope doctrine); decision_chain_v2 (2) "
           "DEPRIORITIZED (v3_tournament supersession r307); rev_osc_stock_p1/"
           "cn_kline_pattern_p1 conversion BLOCKED on bm-c (p1c_stock panel on bm-a "
           "host; D-20261004-02(1) data-locality gate refuses local verification "
           "burn) -- lands on a panel-host round; forward queue lines all "
           "multiprocess (p1e r334 + trial_labor_w1-14 + mass_trial_w1); no 9th "
           "conversion executed (honest waiting-state)")
    cn = t.get("claim_note") or ""
    assert "PICK-9 RESCAN r439" not in cn, "already appended"
    t["claim_note"] = cn + add
    with open(tp + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(t, fh, ensure_ascii=False, indent=1)
    os.replace(tp + ".tmp", tp)
    json.load(open(tp, encoding="utf-8"))
    print("T-134 claim_note appended")

    # ---- 2. round report line ----
    rp = os.path.join(ROOT, "round_reports-bm-c.md")
    src = open(rp, encoding="utf-8", newline="").read()
    line = (
        TS + "\t| r439 bm-c\t| r439 bm-c: WM 绿（red=false lane healthy·py_low_with_work_cands 合法白名单=W2 finalize 烧批在飞 pid 31336 CPU 10075s 实证累积+队列烧空+板空·黄金周周日零新 bar）。"
        "(1) 主产出=D-06 pit-git sub-split batch-1 DELIVERED：外科族 40 条 verbatim 迁出→research/pit-git-surgery.md（41,652B·件内字节对账+md5 行·零丢失断言·85 verify checks PASS）·pit-git.md 115,198B→75,666B（-34%）·拆件脚本 Tools/_r439bmc_pit_git_surgery_split.py（--verify 独立复检腿）·receipt results/_r439bmc_pit_git_surgery_split.json。"
        "(2) 前置治愈 DELIVERED：pit-protocol.md L14 行界合并缺陷（r509 行尾被拼接 r569 外科域条目全文·split 战役边界 bug 族 r419 kin）——sub-split already-migrated 门当场拦截发现·字节恒等预断言（无终结符 md5 c605cc4d…）后剔串录尾核 1429B 零信息损失（真本随批迁 pit-git-surgery.md）·Tools/_r439bmc_pit_protocol_heal.py+receipt；pit-protocol 38,280B→37,332B。"
        "(3) T-134 s2 pick-9 证据序重扫 receipt（results/_r439bmc_t134_pick9.json+claim_note 留痕）：bond_panel_puller（6 烧·最多）裁定豁免（网络串行·ProcessPool=源压力违 r175 熔断律）；decision_chain_v2 降优先（v3 supersession）；rev_osc_stock_p1/cn_kline_pattern_p1 转换在本机被数据本地性门阻（p1c_stock 面板在 bm-a 宿主）→panel-host 轮接手；前向队列线全 multiprocess→第 9 转换零执行=诚实等待态。"
        "(4) D-20261004-02(1)(2)(3) 回执=bm-b r640 已落（autofill data_deps 门+PREREG_TEMPLATE 探针种子选位律 L48+README 数据本地性行 L37·commit 9c38bd8ac·本机双扫核验在树）——反重复铁律零重做。"
        "(5) S6 37/37 rc0（results/_r439bmc_s6_log.txt·dualrun ZERO-DRIFT streak 41·scorecard/daily_scorecard/build_status 族 lane_io 单写者守卫跳过诚实）。"
        "(6) W2 poll 三次（CPU 7975→9146→10075s 活烧实证·w2_judge.json 未落·deadline 10-06 维持）。"
        "(7) S0.5 orders 153/153 轮首+S7 双扫零差+D-19 EB14B510 MATCH+GORDERS 68947C17 MATCH；S1 smoke 47/47；satengine rc0 活（queue_next 空=烧空如实）。"
        "本地未达 origin commit 数=0（push_verify 实证）；登记簿零命中断言=本轮删除/清扫/归档类动作 0 起（treasure_guard prescan 未触发=零删除面）。"
        "下轮指针=W2 落地即收养（adapt _r426bmc_close.py 三段律）/04:04 后静默死灭门线复核（pid 31336 CPU 停增+零 log 进展即呈报灭门升级）/D-06 sub-split batch-2（rebase 净路族+解析族裁定）10-07 收口/O-2030 证据包 10-08。\n"
    )
    assert "r439 bm-c\t| r439" not in src, "round line already present"
    with open(rp, "a", encoding="utf-8", newline="") as fh:
        fh.write(line)
    print("round report line appended")

    # ---- 3. state-bm-c.json ----
    sp = os.path.join(ROOT, "state-bm-c.json")
    st = json.load(open(sp, encoding="utf-8"))
    st.update({
        "round_no": 439,
        "clock_read": TS, "updated": TS, "updated_at": TS,
        "last_seen": TS, "last_ts": TS, "last_round_ts": TS,
        "last_round_at": TS,
        "heartbeat_epoch_utc": EPOCH,
        "cpu_pct": probe_cpu(),
        "idle_ram_gb": probe_ram(),
        "gpu_free_vram_mib": probe_gpu(),
        "last_decisions_read_at": TS,
        "current_task": ("r439 closeout done (D-06 pit-git sub-split batch-1 surgery "
                         "40 entries + pit-protocol L14 line-merge heal + T-134 pick9 "
                         "adjudications); next: W2 landing adoption (deadline <=10-06) "
                         "/ D-06 batch-2 10-07 / O-2030 evidence pack 10-08"),
        "did": ("r439 bm-c: (1) D-06 pit-git sub-split batch-1 DELIVERED -- surgery "
                "family 40 entries verbatim -> research/pit-git-surgery.md (41,652B, "
                "in-file byte reconciliation + md5 + zero-loss assertion, 85 verify "
                "checks PASS); pit-git.md 115,198B->75,666B (-34%); split tool "
                "Tools/_r439bmc_pit_git_surgery_split.py with --verify leg; receipt "
                "results/_r439bmc_pit_git_surgery_split.json. (2) PRE-HEAL DELIVERED -- "
                "pit-protocol.md L14 line-merge defect (r509 entry tail concatenated "
                "with full r569 surgery entry, split-campaign boundary bug family): "
                "caught live by the sub-split already-migrated law, byte-identity "
                "pre-asserted (md5 c605cc4d...), stray tail removed 1429B zero info "
                "loss (canonical copy rides batch-1 into pit-git-surgery.md); "
                "Tools/_r439bmc_pit_protocol_heal.py + receipt. (3) T-134 s2 pick-9 "
                "evidence-order rescan receipt + claim_note lineage: bond_panel_puller "
                "(most-burned, 6) adjudicated EXEMPT (network-serial, ProcessPool "
                "harmful vs r175 fuse discipline); decision_chain_v2 deprioritized "
                "(v3 supersession); rev_osc_stock_p1/cn_kline_pattern_p1 blocked on "
                "bm-c by data-locality (p1c_stock panel on bm-a host, D-20261004-02(1) "
                "gate) -- lands on panel-host round; forward queue lines all "
                "multiprocess; no 9th conversion executed (honest waiting-state). (4) "
                "D-20261004-02(1)(2)(3) = already landed by bm-b r640 (autofill "
                "data_deps gate + PREREG_TEMPLATE probe-seed law L48 + README "
                "data-locality line L37, commit 9c38bd8ac) -- zero duplicate action "
                "per anti-duplication law. (5) S6 37/37 rc0 (dualrun ZERO-DRIFT "
                "streak 41, same-day daily report + live usage faces regenerated "
                "idempotent). (6) W2 finalize poll x3: pid 31336 CPU 7975->9146->"
                "10075s genuine burn, artifact absent, deadline <=10-06 held. (7) "
                "S0 churn-absorb rebase clean (bm-a r652 integrated); orders 153/153 "
                "double-scan zero-diff; D-19 EB14B510 MATCH + GORDERS 68947C17 MATCH; "
                "smoke 47/47; satengine rc0 alive (queue exhausted honest)."),
        "verify": ("split SPLIT PASS + VERIFY 85 checks (pit-git 115198->75666B, -"
                   "40142B moved +610B ptr, core LF 40102B md5 c9d5f657..., "
                   "pit-git-surgery 41652B md5 20b3d2ba...); heal HEAL PASS + VERIFY "
                   "4 checks (pit-protocol 38280->37332B, -1429B stray +481B hdr, "
                   "tail md5 c605cc4d..., r509 intact); pick9 receipt "
                   "results/_r439bmc_t134_pick9.json; S6 37/37 rc0 "
                   "(_r439bmc_s6_log.txt, dualrun streak 41); smoke 47/47; orders "
                   "153/153 double-scan zero-diff; D-19 + GORDERS MATCH; W2 CPU "
                   "accumulating evidence x3; epoch int + clock T-sep in-wrap"),
        "next": ("(a) W2 poll: python Tools/_r426bmc_w2_judge_finalize.py status -> "
                 "w2_judge.json landing = same-round adoption (adapt "
                 "_r426bmc_close.py template, count->replace->assert + idempotent "
                 "no-op + burn-log atomic commit, deadline <=10-06); silent-death "
                 "window from 04:04 (zero log progress + CPU stopped) -> deterministic "
                 "kill escalation report; W2 landing = N1 supply reopen + first "
                 "judge-finalize capture-point sample for the 10-08 acceptance pack. "
                 "(b) D-06 sub-split batch-2 10-07: rebase/net-route family + "
                 "parse/wrapper family + staged family adjudication out of pit-git.md "
                 "(75,666B remaining); pit-data CRLF adjudication; flow down-migration "
                 "final sweep. (c) O-2030 acceptance evidence pack 10-08 (weld face "
                 "complete r432-434 + demo receipts + W2 landing sample). (d) T-134 "
                 "next conversion trigger = single_core runner actually queued for "
                 "pool re-registration or a panel-host round for rev_osc_stock_p1."),
        "last_round": ("r439 bm-c: D-06 pit-git sub-split batch-1 (surgery family 40 "
                       "entries -> pit-git-surgery.md, 85 checks) + pit-protocol L14 "
                       "line-merge heal (stray r569 dedup, byte-identity verified) + "
                       "T-134 pick-9 adjudications (bond exempt/dcv2 depri/stock "
                       "data-blocked); D-20261004-02 receipt=bm-b r640 zero-dup; S6 "
                       "37/37; W2 burn alive CPU 10075s; orders/D19/GORDERS MATCH; "
                       "smoke 47/47"),
        "last_round_at": TS,
    })
    with open(sp + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1)
    os.replace(sp + ".tmp", sp)
    chk = json.load(open(sp, encoding="utf-8"))
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
    print("state-bm-c.json updated, epoch int verified")

    # ---- 4. heartbeat fleet/machines/bm-c.json ----
    hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
    hb = json.load(open(hp, encoding="utf-8"))
    hb.update({
        "round_no": 439,
        "clock_read": TS, "last_seen": TS, "last_seen_at": TS,
        "updated_at": TS, "heartbeat_epoch_utc": EPOCH,
        "cpu_pct": probe_cpu(), "cpu_util_pct": probe_cpu(),
        "cpu_idle_pct": round(100 - (probe_cpu() or 0), 1),
        "free_ram_gb": probe_ram(), "idle_ram_gb": probe_ram(),
        "ram_free_gb": probe_ram(),
        "gpu_free_vram_mb": probe_gpu(), "gpu_idle_vram_mb": probe_gpu(),
        "gpu_free_vram_mib": probe_gpu(), "gpu_idle_vram_mib": probe_gpu(),
        "gpu_vram_free_mb": probe_gpu(),
        "activity_now": ("r439: D-06 pit-git sub-split batch-1 delivered (surgery "
                         "family -> pit-git-surgery.md) + pit-protocol line-merge "
                         "heal + T-134 pick-9 adjudications; W2 judge burn alive "
                         "(CPU 10075s, artifact pending)"),
        "current_task": ("r439 closeout done; W2 judge-finalize burn in flight (pid "
                         "31336 alive, CPU-accumulating, artifact absent, deadline "
                         "<=10-06); next: W2 adopt-at-landing + D-06 batch-2 + "
                         "O-2030 evidence pack"),
        "latest_artifact": ("research/pit-git-surgery.md (40 entries, 41,652B, 85 "
                            "verify checks) + pit-git.md slimmed to 75,666B + "
                            "results/_r439bmc_pit_git_surgery_split.json @ " + TS),
        "next_milestone": ("W2 w2_judge.json landing -> adoption same round (deadline "
                           "<=10-06); D-06 full closure 10-07 (sub-split batch-2 "
                           "rebase/parse/staged families + pit-data CRLF + flow "
                           "sink); O-2030 acceptance evidence pack 10-08; T-143 "
                           "monthly-exam assembly post-10-09 (deliver 10-29)"),
        "prod_lanes": ("D-06 sub-split batch-1 landed (pit-git-surgery.md new canon, "
                       "pit-git -34%); W2 judge-finalize burn in flight (pid 31336 "
                       "alive CPU-accumulating, deadline <=10-06); N1 local queue "
                       "exhausted (waves <=115 done) -- next-wave supply gated on W2 "
                       "landing"),
    })
    with open(hp + ".tmp", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(hb, fh, ensure_ascii=False, indent=1)
    os.replace(hp + ".tmp", hp)
    chk = json.load(open(hp, encoding="utf-8"))
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
    assert "T" in chk["clock_read"], "clock must be T-sep"
    print("heartbeat bm-c.json updated, epoch int + clock T-sep verified")
    print("CLOSEOUT WRITES DONE at", TS)


if __name__ == "__main__":
    main()
