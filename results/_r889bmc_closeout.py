# _r889bmc_closeout.py -- r889 bm-c S7 closeout: state + heartbeat + round
# report line (one-shot writer; fields per iteration-prompt S7 + heartbeat
# epoch int law R170/R178 + clock_read T-separator law R262)
import json
import os
import subprocess
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
HEAD_SHA = "b77d4cbb5"   # r889 product delivery push range-tip (self-proof 0/0)

DID = (
    "r889 bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=4 orphans=1 "
    "zero-kill (ComfyUI idle standing face, MV-lane domain per MSG-2100); "
    "S0 push-battle vs bm-b r895 (7 commits): pre-push claw correctly "
    "blocked first attempt (s05_probe had rewritten bm-b-owned "
    "_r686bmb_d19_check.json) -> surgical amend dropped the file -> claw "
    "pass; daemon-churn race (autofill/dispatcher/saturation faces rewrite "
    "every few sec) -> autostash rebase exception (stash set = bm-c-owned "
    "only, file-overlap vs origin 7 commits = zero -> pop conflict "
    "structurally impossible); delivery b77d4cbb5 self-proof behind 0/ahead "
    "0; (2) S0.5 dual watermark delta FALSE both, unacked 0; (3) S1 smoke "
    "49/49; S2 boards CLEAR (jobs 0 / tickets 0 open / queue heads T22+E14 "
    "CLEAR via collision probe); satengine alive rc0 queue_next=[] (W211 "
    "upstream W210 bm-b pending, M11 row armed + backup watch cron "
    "847675d7); idle GREEN (RAM 51.3%) -> --worked cleared same round; "
    "(4) inbox: MSG-0940 addressed bm-a (T-184 non-party, left for "
    "addressee); MSG-2100 ALL self-observation consumed by bm-b r895 "
    "(processed/ move verified on origin); (5) PRODUCT = P0 matrix slice5 "
    "= P0 row lowamp defensive-ETF home-ground verify (O-1725 sec.2 "
    "zero-burn): scripts/regime_p0_slice5.py (selftest 11/11; v1 machinery "
    "+ batch runner load_axis/_cont_task consumed verbatim, zero "
    "reimplementation) + results/regime_style_matrix/"
    "P0-SLICE5-LOWAMP-ETL-20261011.json (16/16 cells identity-clean: "
    "returns arrays max|diff|=0 vs stored, sharpe/ret/max_dd/nav_last exact; "
    "panel calendars probe-verified legacy 1631d 2020-01-02.. + deep 3230d "
    "2013-06-17.., REGIME-5 label coverage 100% residue 0) + "
    "P0_MATRIX_SLICE_V1.md sec.7. Headlines: LOWAMP-P3 judged-negative "
    "carried honest (dual-axis beat 642/1380=46.5% fail; NOT a rescue "
    "claim); BEAR = real defensive home (deep-window 12m median "
    "+7.2~+7.8% pos_share 100% on all 8 cells; legacy +3.2~+4.7% pos 100%); "
    "CHOP beats deposit floor (+2.8~+3.6%, pos 79-92%); P0 six rows: all "
    "resolvable faces landed (six-member/SYSTEM-V1 forward-accumulation = "
    "only honest hold) -> P0 matrix v1 assembly-ready in the 10-13/14 "
    "window; (6) W18-JUDGE: bm-b r895 registered pool entry (47 blocks/188 "
    "cells single-shard W13/W17 precedent, claim w18-judge-0of1 owner "
    "bm-b) -> zero bm-c-claimable face, monitor only; (7) S6 38/38 rc0 + 7 "
    "honest skips (Sunday no new bar / monthly legs not month-first); "
    "queue_seed_gate scan CLEAR; (8) S7: attrition 4 ledgers CLEAN (1 "
    "healed note) + loop pin=5 no-op + watchdog re-registered + heartbeat "
    "epoch int verified"
)

VERDICT = (
    "green: real product round -- P0 slice5 landed identity-clean, P0 "
    "resolvable coverage closed, matrix v1 assembly-ready; W211 chain "
    "upstream-pending per design (W210 bm-b)"
)

ARTIFACT = (
    "results/regime_style_matrix/P0-SLICE5-LOWAMP-ETL-20261011.json "
    "(2026-10-11T21:0x, 16 adjudicated lowamp cells replayed "
    "identity-clean, BEAR home +7.2% pos 100%, judged-negative carried)"
)

NOW_ACTIVE = (
    "r889: P0 slice5 (lowamp defensive ETF) landed + push-battle claw "
    "surgery (bmb-owned probe face excluded, autostash rebase exception) "
    "+ S6 38/38 + closeout books"
)

NEXT_PTR = (
    "r890: (1) W210 (bm-b) landing watch -> M11/cron auto-exec W211 freeze "
    "-> n1_w211 burn -> finalize -> W212 seat (c1010 template); (2) "
    "W18-JUDGE single-shard burn watch (bm-b) -> judge verdict -> 48h CEO "
    "clock; (3) 10-13/14 P0 matrix v1 assembly (slices 1-5 all landed; "
    "REGIME-5 verify 10-14 -> label revision => v1.1 zero-burn re-slice "
    "one-shot); (4) T-184 transfer deadline watch (10-12 15:30 bm-a->bm-b, "
    "non-party); (5) watermark re-derive"
)

REPORT_LINE = (
    NOW + " | r889 | S0 锚定+孤儿面1零击杀+推送战（爪正拦 bmb 属主件→外科 amend 剔除+autostash rebase 例外=stash 集纯 bm-c 面零重叠·送达 b77d4cbb5 自证 0/0）+ S0.5 双水位零增量 + S1 smoke 49/49 + S2 板清（队头 T22/E14 CLEAR·引擎活队列空=W211 上游待）+ 产品=P0 切片五低波防御族 ETF 主场验证（LOWAMP-P3 已判 16 cells 零烧重放 16/16 身份门全过 returns 数组逐位恒等·BEAR 真主场 deep 窗 12 月中位 +7.2~+7.8% 正份额 100%·CHOP 过定存底线·judged-negative 判负面诚实携带非翻案·selftest 11/11+底料 §七）+ P0 六行可解面全部落地=矩阵 v1 组装就绪（10-13/14 窗）+ W18-JUDGE 池已注册单分片 bm-b 自持（本机零可领面）+ S6 38/38 rc0+7 诚实跳（周日无新 bar） | 验证: "
    "P0-SLICE5-LOWAMP-ETL-20261011.json + _r889bmc_s6_log.txt 38/38 + "
    "attrition 4 CLEAN + idle --worked + smoke 49/49 + push self-proof "
    "0/0 | r890 指针: W210→W211 冻结自动链 / W18-JUDGE 烧录守望 / P0 矩阵 v1 "
    "组装 10-13/14 / T-184 期限 10-12 15:30"
)


def sample_hw():
    hw = {}
    try:
        import psutil
        vm = psutil.virtual_memory()
        hw["free_ram_gb"] = round(vm.available / 1024 ** 3, 2)
        hw["ram_free_gb"] = hw["free_ram_gb"]
        hw["idle_ram_gb"] = hw["free_ram_gb"]
    except Exception:
        pass
    try:
        p = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=20,
            creationflags=0x08000000)
        mib = int(p.stdout.strip().splitlines()[0])
        hw["gpu_free_vram_mb"] = mib
        for k in ("gpu_free_vram_mib", "gpu_idle_vram_mb",
                  "gpu_idle_vram_mib", "gpu_vram_free_mb", "gpu_free_mb",
                  "gpu_idle_mb", "gpu_free_mib", "gpu_idle_mib"):
            hw[k] = mib
        hw["gpu_free_vram_gb"] = round(mib / 1024, 1)
    except Exception:
        pass
    return hw


def main():
    hw = sample_hw()
    stamp = {"ts": NOW, "clock_read": NOW, "last_seen": NOW,
             "last_seen_at": NOW, "updated": NOW, "updated_at": NOW,
             "heartbeat_epoch_utc": EPOCH}
    roundface = {"round_no": 889, "round_no_label": "r889",
                 "last_round": 889, "last_round_at": NOW,
                 "last_round_ts": NOW, "last_round_closed": NOW,
                 "loop_round": 889}
    book = {"did": DID, "verdict": VERDICT, "note": DID[:400],
            "latest_artifact": ARTIFACT, "last_artifact": ARTIFACT,
            "recent_artifact": ARTIFACT, "activity_now": NOW_ACTIVE,
            "now_active": NOW_ACTIVE, "current_task": NOW_ACTIVE,
            "current_task_at": NOW, "current_task_ts": NOW,
            "next_milestone": NEXT_PTR, "next": NEXT_PTR,
            "next_pointer": NEXT_PTR, "idle_rounds": 0,
            "agenda_starved": False, "health": "ok",
            "sync": {"ahead_behind": "0/0 delivered",
                     "origin_tip": HEAD_SHA, "ts": NOW,
                     "note": "r889 product delivery b77d4cbb5 self-proof "
                             "0/0; closeout bookkeeping commit rides next "
                             "push"},
            "head_sha": HEAD_SHA,
            "last_pulled_at": NOW,
            "verify": "receipts: smoke 49/49 + S6 38/38 rc0 "
                      "(results/_r889bmc_s6_log.txt) + slice5 selftest "
                      "11/11 + 16/16 identity gates + attrition 4 CLEAN "
                      "+ idle --worked + push self-proof 0/0",
            "last_round_summary": DID[:1200],
            "last_round_summary_at": NOW,
            "last_action": NOW_ACTIVE, "last_action_at": NOW}

    for rel in ("state-bm-c.json", os.path.join("fleet", "machines",
                                                "bm-c.json")):
        path = os.path.join(ROOT, rel)
        d = json.load(open(path, encoding="utf-8"))
        d.update(stamp)
        d.update(roundface)
        d.update(book)
        d.update(hw)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, path)
        # post-write self-check (smoke F7 contract)
        chk = json.load(open(path, encoding="utf-8"))
        assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
        assert "T" in chk["clock_read"], "clock_read not T-separated"
        print(rel, "written ok epoch=", chk["heartbeat_epoch_utc"])

    rpt = os.path.join(ROOT, "logs", "iteration-loop",
                       "round_reports-bm-c.md")
    with open(rpt, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(REPORT_LINE + "\n")
    print("round report appended")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
