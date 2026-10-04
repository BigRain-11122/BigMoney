"""r495 bm-c S7 state+hb update (RR row + MSG-2005 move already done in-round
via PS with marker==1 proof). Laws: r694 absolute round_no / r645
programmatic write + reparse / r641 strict clock regex + int epoch /
r694-2 absolute-value write idempotence."""
import json
import os
import re
import time
import datetime
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = os.path.join(REPO, "state-bm-c.json")
HB = os.path.join(REPO, "fleet", "machines", "bm-c.json")
CLOCK_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+08:00$")

NOW = datetime.datetime.now().astimezone()
CLOCK = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def gpu_free_mib():
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                            "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=20,
                           creationflags=CNW)
        return int(r.stdout.strip().splitlines()[0])
    except Exception:
        return None


def main():
    st = json.load(open(STATE, encoding="utf-8"))
    assert st["round_no"] == 494, f"unexpected prior round_no {st['round_no']}"
    st["round_no"] = 495
    st["clock_read"] = CLOCK
    st["last_round"] = ("r495 bm-c: W3-judge custody maintenance round + N2 dual-burn adjudication receipt + "
                        "HANDOVER 5x window entry (r441-r495) -- S0 zero-incoming verified then in-round bm-b "
                        "3-commit wave queued for S7 merge + S0.5 dual MATCH + MSG-2005 consumed + S1 48/48 + "
                        "satengine alive (wave116 burning) + post_review zero active red + N2 dual-shard "
                        "origin-truth probe (bm-a daemon bare-key re-claim = r694-i recurrence, adjudicated "
                        "bm-b r692 first-landed=canonical, MSG-2025 cleanup pending bm-a owner, bm-c zero-touch) "
                        "+ S6 38/38 rc0 + quartet 4/4 + attrition CLEAN")
    st["last_round_at"] = CLOCK
    st["last_round_ts"] = NOW.strftime("%Y-%m-%d %H:%M:%S")
    st["last_seen"] = CLOCK
    st["updated"] = CLOCK
    st["updated_at"] = CLOCK
    st["last_ts"] = NOW.strftime("%Y-%m-%d %H:%M:%S")
    st["did"] = ("r495 bm-c: (1) S0 20:25 zero-incoming check (origin==HEAD, daemon 4 lane faces dirty = "
                 "r437 treadmill normal, pull--rebase precheck refusal with intersection=0 zero action); "
                 "in-round bm-b wave (r692 N2 dual-burn adjudication + merge carrying r494 S6 faces + "
                 "addendum) lands via S7 merge. (2) S0.5 _r495bmc_s05_check dual-scan dual MATCH "
                 "(decisions 4E5BE321 + orders 68947C17), 0 unacked, inbox MSG-2005 (bm-b seat receipt, "
                 "zero bm-c obligation) consumed. (3) S1 48/48. (4) S3: satengine rc0 alive (Tools face, "
                 "wave116 6/12), watermark green, post_review official REPORT-20261004 45/0/5 zero active "
                 "red, W3 verify IN_FLIGHT (pid 33768 alive, cpu 9657.4s, age 162.9min, pool 4/4, ckpt 777 "
                 "union 0 dup), N2 candidates not landed (bm-b burn; bm-a daemon duplicate = adjudicated). "
                 "(5) S6 38/38 rc0 NON-ZERO=none (dualrun ZERO-DRIFT streak 51, 378 entries, REPORT/LIVE "
                 "regen, four lane stale-takeover derives legal per O-2100 s2.4). (6) S7 quartet 4/4 + "
                 "attrition CLEAN + HANDOVER 5x window row r441-r495 (ledger live anchor 646,799).")
    st["next"] = ("(a) W3 judge product lands ~22:1x -> python results/_r487bmc_w3_judge_verify.py -> "
                  "ADOPT_PASS -> treasure question + prereg sec.7/8 backfill + pool flip recheck (r668 law) "
                  "+ 48h CEO report clock (<=10-06 evening). (b) N2-W15 candidates land (bm-b canonical "
                  "burn; bm-a daemon duplicate product-first waiver) -> screen-prep + 12 SCREEN shard "
                  "enrollment seat opens (bm-c declared seat MSG-1955, fetch-verify + MSG declaration "
                  "window first per MSG-2010 lesson). (c) fund-trio finalize window 10-05 10:30..10-09 "
                  "(bm-b owner, watch only). (d) O-2115/O-2030 acceptance 10-08. (e) market reopen 10-09.")
    st["verify"] = ("r495: receipts _r495bmc_s05_check.py (dual MATCH, 0 unacked) + _r495bmc_s6_chain.py "
                   "(parity PASS 38 legs, NON-ZERO=none, log _r495bmc_s6_log.txt) + _r487bmc_w3_judge_verify.json "
                   "(IN_FLIGHT liveness 20:34) + _r495bmc_n2_entry.py (pool dual-shard origin truth, LOCAL==ORIGIN "
                   "True) + _r495bmc_pool_status.py (378 entries full-view) + smoke 48/48 + attrition CLEAN + "
                   "quartet 4/4 + RR row marker==1 + HANDOVER 5x row marker==1 + state/hb reparse self-proof")
    g = gpu_free_mib()
    if g is not None:
        st["gpu_free_vram_mib"] = g
    try:
        import psutil
        st["cpu_pct"] = round(psutil.cpu_percent(interval=0.3), 1)
        st["idle_ram_gb"] = round(psutil.virtual_memory().available / 1024 ** 3, 1)
        st["ram_free_gb"] = st["idle_ram_gb"]
        st["free_ram_gb"] = st["idle_ram_gb"]
        st["cpu_util_pct"] = st["cpu_pct"]
    except Exception as e:
        print("PSUTIL_SKIP", e)
    with open(STATE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    json.loads(open(STATE, encoding="utf-8").read())
    print("STATE_OK round_no=495")

    hb = json.load(open(HB, encoding="utf-8"))
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["clock_read"] = CLOCK
    hb["last_seen"] = CLOCK
    hb["current_task"] = ("当前活: W3 judge finalize --wave 3 看护（pid 33768·17:44:04 起·ETA ~22:1x·end-only writes）——r495=看护维护轮（S0 零入站核+S0.5 双 MATCH+S1 48/48+S6 38 面 rc0+N2 双烧裁定收讫+HANDOVER 5x）"
                          "| 最近实物: r495 S6 全链 38 面 rc0 再生（REPORT-2026-10-04+LIVE-2026-10-04 刷新+dualrun ZERO-DRIFT streak 51·378 entries）+HANDOVER 5x 窗口行（r441-r495）@ " + CLOCK +
                          " | 下个里程碑: w3_judge.json 判决产品落地（777 格·~22:1x）→ADOPT_PASS 收养→48h CEO 报告钟（≤10-06 晚）；N2 candidates 落地→screen-prep 开放承接；fund-trio 10-05 10:30（bm-b）；验收 10-08；开市 10-09")
    hb["current_task_at"] = CLOCK
    try:
        import psutil
        hb["cpu_pct"] = round(psutil.cpu_percent(interval=0.3), 1)
        hb["idle_ram_gb"] = round(psutil.virtual_memory().available / 1024 ** 3, 1)
        hb["ram_free_gb"] = hb["idle_ram_gb"]
        hb["free_ram_gb"] = hb["idle_ram_gb"]
        hb["cpu_util_pct"] = hb["cpu_pct"]
    except Exception as e:
        print("PSUTIL_SKIP", e)
    with open(HB, "w", encoding="utf-8", newline="\n") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)
    hb2 = json.loads(open(HB, encoding="utf-8").read())
    assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch not int (F7 law)"
    assert CLOCK_RE.match(hb2["clock_read"]), "clock not strict T-form (F7 law)"
    print("HB_OK epoch=", hb2["heartbeat_epoch_utc"], "clock=", hb2["clock_read"])
    print("S7_STATE_HB_DONE")


if __name__ == "__main__":
    main()
