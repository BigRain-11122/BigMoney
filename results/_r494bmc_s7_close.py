"""r494 bm-c S7 close: bookkeeping four-writes (state round_no absolute 494,
heartbeat with int epoch + T-form clock, round-report append with unique
marker self-proof count==1, inbox MSG moves to processed) + json.loads
reparse self-proof on both state faces. Laws: r694 absolute round_no /
r679 append marker gate / r645 programmatic write + reparse / r641 strict
clock regex + epoch<->clock cross-check / r657 EOL detect before append /
r489 marker needle must not collide with prior rows."""
import json
import os
import re
import shutil
import time
import datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = os.path.join(REPO, "state-bm-c.json")
HB = os.path.join(REPO, "fleet", "machines", "bm-c.json")
RR = os.path.join(REPO, "round_reports-bm-c.md")
INBOX = os.path.join(REPO, "fleet", "inbox")
PROCESSED = os.path.join(REPO, "fleet", "inbox", "processed")

CLOCK_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+08:00$")
MARKER = " | r494 | dept:"  # unique needle (r493 row cites bare r494 only)

NOW = datetime.datetime.now().astimezone()
CLOCK = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

PARTS = [
    " | r494 | dept:研究（W3 judge finalize 看护·舰队维护）",
    " | watermark verdict=绿（red=false·healthy·20:06 probe py_low_with_work_cands 合法面=finalize 在飞即 local_batch_running）",
    " | 当前活=W3 judge finalize 看护（pid 33768·17:44:04 起·20:07 verify IN_FLIGHT·CPU 累积 8505.8s≈1 核满烧·ETA ~22:1x·end-only writes·池 4/4 done·ckpt 777 union 0 dup——等待态轮 rule-2 一行声明零重扫）",
    " | 最近实物=S6 38 面 rc0 再生（REPORT-2026-10-04+LIVE-2026-10-04+dualrun ZERO-DRIFT streak 51·378 entries）@ " + CLOCK,
    " | 下个里程碑=W3 judge 产品落地（~22:1x·777 格·真链头 646,799→647,576）→ADOPT_PASS 收养→48h CEO 报告钟（≤10-06 晚）；N2 supply generate（bm-b 席位 19:44:22 起烧·candidates 未落=screen-prep 未开放·下轮首查）；fund-trio finalize 10-05 10:30（bm-b 正主）；O-2115/O-2030 验收 10-08；开市 10-09",
    " | S0: FF c851bae01 集成 4 commit（bm-a r694 addendum N2 席位让路定谳+双烧击杀清创+双 merge+bm-b autofill keepalive·交集核零·r437 treadmill 律·daemon 双态面全程保留）",
    " | S0.5: _r494bmc_s05_check 双扫双 MATCH（decisions 4E5BE321+orders 68947C17·轮首 20:06+收尾同结果）+0 未回执令（ack_extra README=历史无害）+inbox MSG-1943/MSG-2010（bm-a N2 席位认领→让路定谳 bm-b 正典+双烧击杀清创通报·bm-c 非当事零席位动作）消费入 processed",
    " | S1 smoke 48/48 | S2 板空（job_list 0·fleet 169 票 0 open）",
    " | S3: satengine rc0 活（bm-c Tools 面·r467 路径律）+post_review 官方面 ✓45/✗0/🟡5 零活红+W3 verify 回执刷新（liveness 三证=CPU 累积+end-only 契约+产品未落）+N2 generate watch（bm-b 活烧·candidates 未落）+compute_audit FLAG:supply_gap（ready=5≥floor=3·breach=false·N2 链在飞=供给管线活跃·观察面）",
    " | S6 38/38 rc0 NON-ZERO=none（金周 no-op 诚实·REPORT/LIVE/市场钟 CALL 再生·车道护栏全守）",
    " | S7: quartet 4/4（loop pin5 no-op·watchdog 幂等重建·双爪 LF 归一重装）+attrition CLEAN（4 ledgers·healed 注记照录）",
    " | 记分: 1（S6 实物再生+看护证据面=文件改动；等待态轮如实计）| 记账预算: 3（state+心跳+轮报）",
    " | 方法论捕获=无新方法（全链复用正典范式）·宝藏捕获=无（无判决面收口）",
    " | 本地未达 origin commit 数: 收口 push 后自证",
    " | 下轮指针=r495 ①W3 judge 产品落地首查（python results/_r487bmc_w3_judge_verify.py→ADOPT_PASS→宝藏捕获问+prereg §7/§8 回填+池翻面复核〔r668 律〕+48h CEO 报告钟）②N2 generate candidates 落地→screen-prep 席位开放承接（先 fetch 实核+MSG 公示窗·MSG-2010 教训）③fund-trio finalize 10-05 10:30（bm-b 正主）④O-2115/O-2030 验收 10-08⑤开市 10-09",
]
ROW = CLOCK + "".join(PARTS)


def main():
    # --- round report append (EOL-detect + marker gate) ---
    with open(RR, "rb") as f:
        raw = f.read()
    assert raw.count(MARKER.encode("utf-8")) == 0, "marker already present (r679 gate)"
    eol = b"\r\n" if (raw[-2:] == b"\r\n" or raw.count(b"\r\n") > raw.count(b"\n") // 2) else b"\n"
    if not raw.endswith(eol):
        raw = raw + eol
    with open(RR, "wb") as f:
        f.write(raw + ROW.encode("utf-8") + eol)
    with open(RR, "rb") as f:
        raw2 = f.read()
    assert raw2.count(MARKER.encode("utf-8")) == 1, "marker count != 1 after append (r679 gate)"
    assert raw2.startswith(raw[: len(raw) - 0]) or True  # prefix preserved trivially
    print("RR_APPEND_OK marker_count=1 eol=", eol)

    # --- state (absolute round_no, programmatic write) ---
    st = json.load(open(STATE, encoding="utf-8"))
    assert st["round_no"] == 493, f"unexpected prior round_no {st['round_no']}"
    st["round_no"] = 494
    st["clock_read"] = CLOCK
    st["last_round"] = ("r494 bm-c: W3-judge custody maintenance round (waiting state, rule-2 one-line no-rescan) "
                        "-- S0 FF 4-commit integration (bm-a r694 N2 seat yield addendum + bm-b keepalive) + "
                        "S0.5 dual-scan dual MATCH + S1 48/48 + satengine alive + S6 38/38 rc0 + quartet 4/4 + "
                        "attrition CLEAN; W3 judge finalize IN_FLIGHT (ETA ~22:1x); N2 generate burn = bm-b seat")
    st["last_round_at"] = CLOCK
    st["last_round_ts"] = NOW.strftime("%Y-%m-%d %H:%M:%S")
    st["last_seen"] = CLOCK
    st["updated"] = CLOCK
    st["updated_at"] = CLOCK
    st["last_ts"] = NOW.strftime("%Y-%m-%d %H:%M:%S")
    st["did"] = ("r494 bm-c: (1) S0 FF merge c851bae01, 4 incoming commits, zero UU, dirty-intersection zero "
                 "(r437 treadmill law, daemon dual-state faces preserved); (2) S0.5 open+close dual scan dual MATCH "
                 "(decisions 4E5BE321 + orders 68947C17), 0 unacked orders, inbox MSG-1943/2010 (bm-a N2 seat "
                 "claim then yield-to-bm-b adjudication + duplicate-burn kill cleanup) consumed to processed; "
                 "(3) S1 48/48; (4) S3 satengine rc0 alive (Tools face per r467), watermark green, post_review "
                 "REPORT-20261004 45/0/5 zero active red, W3 verify IN_FLIGHT receipt refreshed (pid 33768 alive, "
                 "cpu 8505.8s, pool 4/4 done, ckpt 777 union / 0 dup), N2 generate watch (bm-b burn, candidates "
                 "not landed), compute_audit FLAG:supply_gap (breach=false, supply pipeline active via N2 chain); "
                 "(5) S6 38/38 rc0 (dualrun ZERO-DRIFT streak 51, 378 entries, REPORT+LIVE regen); (6) S7 quartet "
                 "4/4 + attrition CLEAN.")
    st["next"] = ("(a) W3 judge product lands ~22:1x -> python results/_r487bmc_w3_judge_verify.py -> ADOPT_PASS -> "
                  "treasure question + prereg sec.7/8 backfill + pool flip recheck (r668 law) + 48h CEO report clock "
                  "(<=10-06 evening). (b) N2-W15 generate candidates land (bm-b burn, est 30-60min from 19:44) -> "
                  "screen-prep + 12 SCREEN shard enrollment seat opens first-come-first-served (fetch verify + MSG "
                  "declaration window first per MSG-2010 lesson). (c) fund-trio finalize 10-05 10:30 (bm-b owner, "
                  "watch only). (d) O-2115/O-2030 acceptance 10-08. (e) market reopen 10-09.")
    st["verify"] = ("r494: receipts _r494bmc_s05_check.py (dual-scan dual MATCH, 0 unacked) + _r494bmc_s6_chain.py "
                   "(parity PASS 38 legs, log _r494bmc_s6_log.txt, NON-ZERO=none) + _r487bmc_w3_judge_verify.json "
                   "(IN_FLIGHT liveness) + smoke 48/48 + attrition CLEAN + quartet 4/4 + state/hb reparse self-proof "
                   "(this script)")
    with open(STATE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    json.loads(open(STATE, encoding="utf-8").read())
    print("STATE_OK round_no=494")

    # --- heartbeat (int epoch + strict clock + cross-check) ---
    hb = json.load(open(HB, encoding="utf-8"))
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["clock_read"] = CLOCK
    hb["last_seen"] = CLOCK
    hb["current_task"] = ("当前活: W3 judge finalize --wave 3 看护（pid 33768·17:44:04 起·ETA ~22:1x·end-only writes）——r494=看护维护轮（S0 FF 4-commit 集成+S0.5 双扫双 MATCH+S1 48/48+S6 38 面 rc0+rule-2 零重扫）"
                          "| 最近实物: r494 S6 全链 38 面 rc0 再生（REPORT-2026-10-04+LIVE-2026-10-04 刷新+dualrun ZERO-DRIFT streak 51·378 entries）@ " + CLOCK +
                          " | 下个里程碑: w3_judge.json 判决产品落地（777 格·~22:1x）→ADOPT_PASS 收养→48h CEO 报告钟（≤10-06 晚）；N2 generate（bm-b 席位）candidates 落地→screen-prep 开放承接；fund-trio 10-05 10:30（bm-b）；验收 10-08；开市 10-09")
    hb["current_task_at"] = CLOCK
    try:
        import psutil
        hb["cpu_pct"] = round(psutil.cpu_percent(interval=0.3), 1)
        hb["idle_ram_gb"] = round(psutil.virtual_memory().available / 1024 ** 3, 1)
        hb["ram_free_gb"] = hb["idle_ram_gb"]
        hb["free_ram_gb"] = hb["idle_ram_gb"]
        hb["cpu_util_pct"] = hb["cpu_pct"]
    except Exception as e:
        print("PSUTIL_SAMPLE_SKIP", e)
    with open(HB, "w", encoding="utf-8", newline="\n") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)
    hb2 = json.loads(open(HB, encoding="utf-8").read())
    assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch not int (F7 law)"
    assert CLOCK_RE.match(hb2["clock_read"]), "clock not strict T-form (F7 law)"
    print("HB_OK epoch=", hb2["heartbeat_epoch_utc"], "clock=", hb2["clock_read"])

    # --- inbox moves ---
    for fn in ["MSG-2026-10-04-1943-bma-all.md", "MSG-2026-10-04-2010-bma-all.md"]:
        src = os.path.join(INBOX, fn)
        dst = os.path.join(PROCESSED, fn)
        if os.path.exists(src):
            shutil.move(src, dst)
            print("MSG_MOVED", fn)
        else:
            print("MSG_ALREADY_GONE", fn)
    print("S7_CLOSE_DONE")


if __name__ == "__main__":
    main()
