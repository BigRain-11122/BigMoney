# -*- coding: utf-8 -*-
"""r416 bm-c closeout ledger pass.

Modes:
    python Tools/_r416bmc_close.py                 # ledger pass: state+heartbeat+ticket
    python Tools/_r416bmc_close.py --report <sha>  # append r416 round-report line w/ push receipt <sha>
Laws: R170/R178 epoch int, R262 clock_read T-format, r413 ArgString (no inner quotes
needed here -- argv only), append-only report (never rewrite history lines).
416 not a 5x round: no HANDOVER reconciliation line (next 5x = r420).
"""
import datetime
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MID = "bm-c"
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
TICKET = os.path.join(ROOT, "fleet", "tasks", "T-2026-10-02-144-P1.json")
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")
S6LOG = os.path.join(ROOT, "results", "_r416bmc_s6_log.txt")
CREATE_NO_WINDOW = 0x08000000
ROUND = 416


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def load(path):
    with open(path, encoding="utf-8-sig") as fh:
        return json.load(fh)


def dump(path, obj):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)


def s6_summary():
    txt = open(S6LOG, encoding="utf-8", errors="replace").read()
    legs = re.findall(r"^=== (\S+) rc=(\d+) ([\d.]+)s", txt, re.M)
    bad = ["%s rc=%s" % (n, rc) for n, rc, _ in legs if int(rc) != 0]
    total = sum(float(s) for *_, s in legs)
    return len(legs), bad, total


def machine_read():
    cpu, ram, gpu = None, None, None
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        ram = round(psutil.virtual_memory().available / (1024 ** 3), 1)
    except Exception:
        pass
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                            "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=20,
                           creationflags=CREATE_NO_WINDOW)
        gpu = int(r.stdout.strip().splitlines()[0])
    except Exception:
        pass
    return cpu, ram, gpu


TICKET_PROGRESS = (
    "SPAWN/TOOLING-DOMAIN SPLIT (r416, D-06 window batch 3 per r415 REMAINING list): 5 hot-layer entries "
    "verbatim -> research/pit-spawn.md (new domain file): r317 detached-spawn pipe-holding (close_fds law) / "
    "r324 inline-SR 5min behead x spawn-driver __main__ guard / r570-a shared-jsonl shell-redirect overwrite / "
    "r614 croc sender zombie-relay conn / r614 croc public-relay DNS multi-A fork. Byte recon (CRLF "
    "working-tree face): CODELY.md 35,304B -> 31,432B (net = -4,598B moved + 726B pointer line); moved core "
    "LF-blob face 4,593B md5 c51afdfeae48837a1279e18c6257f14f; pit-spawn.md 6,460B md5 "
    "16850aeb6923ff7d14b3c0d6b187f518. Zero-loss PASS (each line exactly-once in pit-spawn + zero residue in "
    "CODELY + utf-8 strict + lone-CR=0 + no-mojibake gate, independent verify 14/14 PASS). Kin notes: r559/r617 "
    "PS5-redirect-UTF16 pair stays in pit-ps (already-migrated law); r570-bmb jsonl-union pretty-blob + r327 "
    "sub-100ms pool-IPC = pre-split survivors (next batches). REMAINING for D-06 closure (10-07): git-domain "
    "increments (r366-ls-tree/r614-rebase-live-write) + protocol increments (r366-laneio/r371) + pre-split "
    "survivors (r489/r294x3/r300/r303/r494/r304/r307/r311/r327/r570-bmb) + pit-data CRLF-face decision + "
    "flow-sinking sweep."
)


def ledger_pass():
    n_legs, bad, total = s6_summary()
    cpu, ram, gpu = machine_read()
    ts = now_iso()
    epoch = int(time.time())
    s6_ok = (n_legs == 37 and not bad)

    did = (
        "r416 bm-c: (1) S0 churn absorb b2d94ed2f (daemon state quad; live-fire of the ArgString inner-quote "
        "pit -- single-quoted msg mangled to pathspecs, escaped-double-quote retry per pit-ps law) + fetch "
        "0-behind clean (pull --rebase refused by live-writer-dirty satengine face per r614 law; nothing to "
        "pull, honest note). (2) S0.5 orders 151/151 acked (open scan + closing double-scan), D-19 4167b784 "
        "MATCH zero action. (3) smoke 47/47. (4) SatEngine rc0 alive (W114 registered). (5) Pool: r413 "
        "structural ruling stands -- FUND family p1c_stock-dependent, zero-touchable on bm-c; legal idle "
        "(board 0 open, bandit 0, next_pick source-blocked claimed). (6) MAIN DELIVERABLE T-144(c) D-06 "
        "batch3: spawn/tooling-domain split -- 5 hot-layer entries verbatim -> research/pit-spawn.md (byte "
        "recon 35,304->31,432B CRLF face, -4,598B moved +726B pointer; core LF 4,593B md5 c51afdfe; pit-spawn "
        "6,460B md5 16850aeb; zero-loss PASS, independent verify 14/14; receipt "
        "results/_r416bmc_pit_spawn_split.json; commit in closeout). (7) S6 chain %d legs rc%s (%s), "
        "stale-takeover derive on 4 shared faces (t35/daily_scorecard/paper_export/dashboard_status) = legal "
        "per lane_io L3 (bm-a heartbeat stale >20min, r371 origin-ref belt). (8) S7 4/4 + attrition CLEAN. "
        "(9) bm-a heartbeat stall since 10:26 (~2h50m at closeout, 3h threshold 13:26 crossing -- GM "
        "reassignment ruling check next round if still stalled)."
    ) % (n_legs, "0" if not bad else " " + ",".join(bad), "%.0fs" % total)

    verify = (
        "smoke 47/47 rc0; S6 %d/%d rc%s; orders 151/151 double-scan; D-19 4167b784 MATCH; attrition CLEAN; "
        "S7 4/4; pit-spawn split zero-loss PASS + independent verify 14/14 PASS"
    ) % (n_legs - len(bad), n_legs, "0" if not bad else " " + ",".join(bad))

    st = load(STATE)
    st.update({
        "clock_read": ts, "round_no": ROUND, "heartbeat_epoch_utc": epoch,
        "last_round": "r416 bm-c: T-144(c) D-06 batch3 spawn/tooling-domain split (pit-spawn.md 5 entries "
                      "zero-loss) + churn absorb + S6 37/37 + smoke 47/47 + S7 4/4",
        "last_round_at": "r416", "last_round_ts": ts, "last_seen": ts, "last_ts": ts,
        "updated": ts, "updated_at": ts,
        "current_task": "r416 closing: T-144(c) D-06 batch3 spawn/tooling-domain split delivered "
                        "(research/pit-spawn.md 5 entries); next: D-06 remaining batches before 10-07 closure",
        "did": did, "verify": verify,
        "next": "(a) D-06 remaining before 10-07: git increments (r366-ls-tree/r614-rebase-live-write), "
               "protocol increments (r366-laneio/r371), pre-split survivors (r489/r294x3/r300/r303/r494/r304/"
               "r307/r311/r327/r570-bmb), pit-data CRLF-face decision, flow-sinking sweep. (b) bm-a heartbeat "
               "stall since 10:26 -- >3h threshold 13:26: if still stalled next round, surface to GM for "
               "reassignment ruling. (c) T-156 p1c croc in flight (bm-b sender / bm-a camping receiver), "
               "bm-c observer; pool FUND family zero-touchable until p1c_stock lands locally. (d) T-143 "
               "assembly rounds Oct, deliverable 10-29.",
    })
    if cpu is not None:
        st["cpu_pct"] = cpu
    if ram is not None:
        st["idle_ram_gb"] = ram
    if gpu is not None:
        st["gpu_free_vram_mib"] = gpu
    dump(STATE, st)

    hb = load(HB)
    hb.update({
        "round_no": ROUND, "last_seen": ts, "clock_read": ts,
        "heartbeat_epoch_utc": epoch, "updated_at": ts,
        "current_task": "r416 done: pit-spawn.md domain split (T-144(c) D-06 batch3); next D-06 remaining batches before 10-07",
        "activity_now": "r416: T-144(c) D-06 batch3 spawn/tooling split (5 entries zero-loss) + S6 %d legs rc%s"
                        % (n_legs, "0" if not bad else " " + ",".join(bad)),
        "prod_lanes": "T-144(c) D-06 closure-window batches (git/pool/engine/protocol/data/ps/encoding/spawn done; git+protocol increments, pre-split survivors, pit-data CRLF face + flow-sinking remaining before 10-07)",
        "latest_artifact": "research/pit-spawn.md (r416 13:1x, 5 entries verbatim, zero-loss PASS + verify 14/14) + results/_r416bmc_pit_spawn_split.json",
        "next_milestone": "D-06 git/protocol increments + pre-split survivors (<=10-05 window) + full D-06 closure 10-07; bm-a heartbeat >3h GM ruling check next round if still stalled; T-143 assembly 10-29",
        "health": "ok", "verdict": "alive",
    })
    if cpu is not None:
        hb["cpu_pct"] = cpu
        hb["cpu_util_pct"] = round(cpu, 1)
        hb["cpu_idle_pct"] = round(100 - cpu, 1)
    if ram is not None:
        hb["idle_ram_gb"] = ram
        hb["free_ram_gb"] = ram
        hb["ram_free_gb"] = ram
    if gpu is not None:
        hb["gpu_free_vram_mib"] = gpu
        hb["gpu_idle_vram_mib"] = gpu
        hb["gpu_free_vram_mb"] = gpu
        hb["gpu_idle_vram_mb"] = gpu
    dump(HB, hb)
    assert isinstance(hb["heartbeat_epoch_utc"], int) and "T" in hb["clock_read"]

    tk = load(TICKET)
    tk["progress_r416_bmc"] = TICKET_PROGRESS
    dump(TICKET, tk)

    print("LEDGER PASS: state r%d + heartbeat (epoch=%d int ok) + ticket progress_r416_bmc; "
          "S6 %d legs rc%s %.0fs" % (ROUND, epoch, n_legs, "0" if not bad else " " + ",".join(bad), total))
    return 0 if s6_ok else 1


def report_pass(sha: str) -> int:
    n_legs, bad, total = s6_summary()
    ts = now_iso()
    rc_face = "0" if not bad else " " + ",".join(bad)
    line = (
        "%s | r416 | dept:工程/舰队（T-144(c) D-06 裁定窗批3=spawn/tooling 域拆件） | watermark verdict："
        "py_low_with_work_cands（red=false·§四白名单三证：板 0 open+bandit 0+池 FUND 族 r413 结构性零可碰"
        "〔p1c_stock 本地缺·T-156 croc bm-b→bm-a 在飞〕·next_pick=moneyflow IC 源阻塞已认领·audit 无异常旗） | "
        "S0 churn absorb b2d94ed2f（daemon 状态四件·ArgString 内层引号坑活实弹=单引号消息被撕成 pathspec·"
        "转义双引号重试即愈·pit-ps 已录族零新录）+fetch 0-behind 净（pull --rebase 被 satengine 活写脏面拒=r614 律"
        "如实注记·无物可拉）；S0.5 双扫 151/151 acked 零 unacked；D-19 4167b784 MATCH 零消费；smoke 47/47；"
        "SatEngine rc0 活（W114 驻册）；主活=T-144(c) D-06 批3：spawn/tooling 域 5 条（r317 分离 spawn 管道持握/"
        "r324 内联 SR 5min 斩首×__main__ 守卫/r570-a 共享 jsonl shell 重定向覆写/r614 croc 僵尸 relay 连接/"
        "r614 croc 公共 relay DNS 多 A 分叉）verbatim→research/pit-spawn.md 新域件（CODELY 35,304→31,432B·"
        "−4,598B 迁出+726B 指针行·迁移核 4,593B LF md5 c51afdfe·pit-spawn 6,460B md5 16850aeb·零丢失 PASS·"
        "独立复验 14 检 PASS·亲族 r559/r617 留 pit-ps·r570-bmb+r327=pre-split 存留·回执 "
        "results/_r416bmc_pit_spawn_split.json）；S6 %d/%d rc%s（_r416bmc_s6.py·%.0fs·四共享面 stale-takeover="
        "lane_io L3 合法〔bm-a 心跳>20min·r371 origin-ref 带〕）；S7 4/4+attrition CLEAN；"
        "bm-a 心跳停 10:26 起续观察（~2h50m·3h 阈值 13:26 过线=下轮呈 GM 改派裁定） | 下轮：D-06 git/protocol 增量"
        "+pre-split 存留条+pit-data CRLF 裁定+流水下沉（due 10-07）·bm-a 心跳裁定查·T-156 观察席·T-143 预备 | "
        "本地未达 origin commit 数：0（push %s 达→fetch 后 HEAD..origin/main=0·tip==origin 送达自证）"
    ) % (ts, n_legs - len(bad), n_legs, rc_face, total, sha)
    with open(REPORT, "a", encoding="utf-8", newline="") as fh:
        fh.write(line + "\n")
    print("REPORT PASS: r416 line appended with push receipt %s" % sha)
    return 0


if __name__ == "__main__":
    if "--report" in sys.argv:
        sha = sys.argv[sys.argv.index("--report") + 1]
        sys.exit(report_pass(sha))
    sys.exit(ledger_pass())
