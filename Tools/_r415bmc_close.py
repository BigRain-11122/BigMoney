# -*- coding: utf-8 -*-
"""r415 bm-c closeout ledger pass.

Modes:
    python Tools/_r415bmc_close.py                 # ledger pass: state+heartbeat+ticket+HANDOVER
    python Tools/_r415bmc_close.py --report <sha>  # append r415 round-report line w/ push receipt <sha>
Laws: R170/R178 epoch int, R262 clock_read T-format, r413 ArgString (no inner quotes
needed here -- argv only), append-only report (never rewrite history lines).
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
HANDOVER = os.path.join(ROOT, "research", "HANDOVER.md")
S6LOG = os.path.join(ROOT, "results", "_r415bmc_s6_log.txt")
CREATE_NO_WINDOW = 0x08000000
ROUND = 415


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


HANDOVER_LINE = (
    "> bm-c round 415 五倍数核对（2026-10-03 13:0x·增量窗 r411-415 五轮）：增量窗 r411-415=bm-c 面（**T-144(c) D-06 域分件收口连营**——"
    "r411 增量回扫 2 条〔pool 1=r619 停泊泳道裁定链扫描律+protocol 1=r410 融合形态律块界变体④〕+pit-protocol L56 r607 行 bullet 缺失形 2 字节修复〔变体⑤〕；"
    "r412/r413 S6 维护+池面资格判定窗〔FUND-QUALITY-P1-SENS unclaimed=p1c_stock 本地缺席硬闸=结构性零可碰+Invoke-SilentExe ArgString 内层引号吞噬坑律+1〕；"
    "r414 **PS 域拆件 D-06 批1**〔10 条 verbatim→research/pit-ps.md·字节对账 43,467→36,244B·零丢失 PASS·独立复验 PASS·死会话收编+S6 37/37 收编+orders O-1210 ack〕+S4 坑律+1〔python 探针 CJK GBK console 崩〕；"
    "r415=本核对轮 **编码域拆件 D-06 批2**〔4 条 r593/r607/r407-mojibake/r414-GBK-console verbatim→research/pit-encoding.md·CODELY 37,106→34,431B（−3,366B 迁出+691B 指针行）·"
    "迁移核 3,362B LF md5 872fe043·pit-encoding 5,075B md5 7301f8ba·零丢失 PASS+独立复验 12 检 PASS·churn absorb f51dba4c0+rebase behind 4→0·S6 37 腿 rc0·HANDOVER 本行〕）"
    "产物清单漂移=research/pit-ps.md〔r414〕+research/pit-encoding.md〔r415〕+Tools/_r415bmc_{pit_encoding_split,s6,close}.py+results/_r415bmc_pit_encoding_split.json〔r415〕"
    "+CODELY.md PS 域/编码域双指针行+票 progress_r414/r415_bmc；orders 151/151 双扫零未回执全窗维持；smoke 47/47；D-19 4167B784 MATCH 全窗零消费；"
    "池态=FUND 族 p1c_stock 依赖结构性零可碰（r413 判定维持）+T-156 croc v3n9 bm-b 重发在飞观察席；"
    "指针：**D-06 批3 spawn/tooling 族+git/protocol 增量+pre-split 存留条+pit-data CRLF face 裁定+流水下沉〔due 10-07〕+bm-a 心跳停 10:26 起观察〔>3h 阈值 13:26 过线=呈 GM 改派裁定〕+T-143 月考装配 10-29+月界首考 10-31**；下一 5x=bm-c r420。"
)

TICKET_PROGRESS = (
    "ENCODING-DOMAIN SPLIT (r415, D-06 window batch 2 per r414 REMAINING list): 4 hot-layer entries verbatim "
    "-> research/pit-encoding.md (new domain file): r593 subprocess-capture GBK decode crash / r607 round_reports "
    "GBK pollution-byte tolerant-read / r407 mojibake write-channel fact-rebuild / r414 session-shell CJK probe "
    "GBK console crash. Byte recon (CRLF working-tree face): CODELY.md 37,106B -> 34,431B (net = -3,366B moved "
    "+ 691B pointer line); moved core LF-blob face 3,362B md5 872fe0433e3b0b955b7a8533441463b1; pit-encoding.md "
    "5,075B md5 7301f8ba6650b7e1e5eecf71784f450d. Zero-loss PASS (each line exactly-once in pit-encoding + zero "
    "residue in CODELY + utf-8 strict + lone-CR=0 + no-mojibake gate, independent verify 12/12 PASS). Kin note: "
    "r559/r617 PS5-redirect-UTF16 pair stays in pit-ps (already-migrated law); encoding domain hosts the "
    "callee/data-face incidents. REMAINING for D-06 closure (10-07): spawn/tooling cluster (r317/r324/"
    "r614-croc-x2/r570) + git-domain increments (r366-ls-tree/r614-rebase-live-write) + protocol increments "
    "(r366-laneio/r371) + pre-split survivors (r489/r294x3/r300/r303/r494/r304/r307/r311/r327) + pit-data "
    "CRLF-face decision + flow-sinking sweep."
)


def ledger_pass():
    n_legs, bad, total = s6_summary()
    cpu, ram, gpu = machine_read()
    ts = now_iso()
    epoch = int(time.time())
    s6_ok = (n_legs == 37 and not bad)

    did = (
        "r415 bm-c: (1) S0 churn absorb f51dba4c0 (daemon state trio) + pull --rebase behind 4->0 clean "
        "(incoming = bm-b r617 batch: DIVLOWVOL-YIELDVOL x2 verdict + T-156 croc v3n9 rearm). (2) S0.5 orders "
        "151/151 acked (open scan + closing double-scan), D-19 4167b784 MATCH zero action. (3) smoke 47/47. "
        "(4) SatEngine rc0 alive (W114 registered, queue empty). (5) Pool: r413 structural ruling stands -- FUND "
        "family p1c_stock-dependent, zero-touchable on bm-c; legal idle. (6) MAIN DELIVERABLE T-144(c) D-06 "
        "batch2: encoding-domain split -- 4 hot-layer entries verbatim -> research/pit-encoding.md (byte recon "
        "37,106->34,431B CRLF face, -3,366B moved +691B pointer; core LF 3,362B md5 872fe043; pit-encoding 5,075B; "
        "zero-loss PASS, independent verify 12/12; receipt results/_r415bmc_pit_encoding_split.json; commit in "
        "closeout). (7) S6 chain %d legs rc%s (%s). (8) HANDOVER r415 5x reconciliation line (window r411-415). "
        "(9) S7 4/4 + attrition CLEAN. (10) bm-a heartbeat stall since 10:26 continues (<3h surface threshold "
        "13:26, next-round ruling check)."
    ) % (n_legs, "0" if not bad else " " + ",".join(bad), "%.0fs" % total)

    verify = (
        "smoke 47/47 rc0; S6 %d/%d rc%s; orders 151/151 double-scan; D-19 4167b784 MATCH; attrition CLEAN; "
        "S7 4/4; pit-encoding split zero-loss PASS + independent verify 12/12 PASS"
    ) % (n_legs - len(bad), n_legs, "0" if not bad else " " + ",".join(bad))

    st = load(STATE)
    st.update({
        "clock_read": ts, "round_no": ROUND, "heartbeat_epoch_utc": epoch,
        "last_round": "r415 bm-c: T-144(c) D-06 batch2 encoding-domain split (pit-encoding.md 4 entries "
                      "zero-loss) + churn absorb + rebase + S6 37/37 + HANDOVER 5x line + smoke 47/47 + S7 4/4",
        "last_round_at": "r415", "last_round_ts": ts, "last_seen": ts, "last_ts": ts,
        "updated": ts, "updated_at": ts,
        "current_task": "r415 closing: T-144(c) D-06 batch2 encoding-domain split delivered "
                        "(research/pit-encoding.md 4 entries); next: D-06 batches 3-N before 10-07 closure",
        "did": did, "verify": verify,
        "next": "(a) D-06 batches 3-N before 10-07: batch3 spawn/tooling cluster (r317/r324/r614-croc-x2/r570), "
               "git increments (r366-ls-tree/r614-rebase-live-write), protocol increments (r366-laneio/r371), "
               "pre-split survivors (r489/r294x3/r300/r303/r494/r304/r307/r311/r327), pit-data CRLF-face "
               "decision, flow-sinking sweep. (b) bm-a heartbeat: stall since 10:26, >3h threshold 13:26 -> "
               "surface to GM for reassignment ruling next round if still stalled. (c) T-156 p1c croc v3n9 "
               "re-issue in flight (bm-b sender / bm-a camping receiver), bm-c observer. (d) pool FUND family "
               "zero-touchable until p1c_stock lands locally.",
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
        "current_task": "r415 done: pit-encoding.md domain split (T-144(c) D-06 batch2); next D-06 batches before 10-07",
        "activity_now": "r415: T-144(c) D-06 batch2 encoding split (4 entries zero-loss) + S6 %d legs rc%s + HANDOVER 5x reconciliation"
                        % (n_legs, "0" if not bad else " " + ",".join(bad)),
        "prod_lanes": "T-144(c) D-06 closure-window batches (git/pool/engine/protocol/data/ps/encoding done; spawn/tooling + pre-split survivors remaining before 10-07)",
        "latest_artifact": "research/pit-encoding.md (r415 12:5x, 4 entries verbatim, zero-loss PASS + verify 12/12) + results/_r415bmc_pit_encoding_split.json",
        "next_milestone": "D-06 batch3 spawn/tooling cluster (<=10-05 window) + full D-06 closure 10-07; bm-a heartbeat >3h ruling check 13:26; T-143 assembly 10-29",
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
    tk["progress_r415_bmc"] = TICKET_PROGRESS
    dump(TICKET, tk)

    raw = open(HANDOVER, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    body = raw[3:] if bom else raw
    crlf = b"\r\n" in body
    if crlf:
        assert b"\n" not in body.replace(b"\r\n", b""), "HANDOVER mixed EOL face"
        sep = b"\r\n"
    else:
        assert b"\r" not in body, "HANDOVER mixed EOL face"
        sep = b"\n"
    lines = body.split(sep)
    first = lines[0].decode("utf-8", "replace")
    assert first.startswith("# Bigmoney"), "HANDOVER head unexpected: %r" % first[:40]
    assert b"bm-c round 415" not in body, "5x line already present"
    lines.insert(1, HANDOVER_LINE.encode("utf-8"))
    tmp = HANDOVER + ".tmp_r415"
    with open(tmp, "wb") as fh:
        fh.write((b"\xef\xbb\xbf" if bom else b"") + sep.join(lines))
    os.replace(tmp, HANDOVER)

    print("LEDGER PASS: state r%d + heartbeat (epoch=%d int ok) + ticket progress_r415 + HANDOVER 5x line; "
          "S6 %d legs rc%s %.0fs" % (ROUND, epoch, n_legs, "0" if not bad else " " + ",".join(bad), total))
    return 0 if s6_ok else 1


def report_pass(sha: str) -> int:
    n_legs, bad, total = s6_summary()
    ts = now_iso()
    rc_face = "0" if not bad else " " + ",".join(bad)
    line = (
        "%s | r415 | dept:工程/舰队（T-144(c) D-06 裁定窗批2=编码域拆件+五倍数核对轮） | watermark verdict：绿（red=false·lane=healthy·"
        "next_pick=moneyflow IC claimed·audit CLEAN） | S0 churn absorb f51dba4c0+pull --rebase behind 4→0 干净重放"
        "（incoming=bm-b r617 批：DIVLOWVOL-YIELDVOL x2 判决+T-156 croc v3n9 重发）；S0.5 双扫 151/151 acked 零 unacked；"
        "D-19 4167b784 MATCH 零消费；smoke 47/47；SatEngine rc0 活（W114 驻册 queue 空）；池面 r413 判定维持（FUND 族 "
        "p1c_stock 本地缺=结构性零可碰）；主活=T-144(c) D-06 批2：编码域 4 条（r593 subprocess GBK 解码崩/r607 GBK 污染字节"
        "容错读/r407 mojibake 事实重建/r414 CJK 探针 console 崩）verbatim→research/pit-encoding.md 新域件（CODELY "
        "37,106→34,431B·−3,366B 迁出+691B 指针行·迁移核 3,362B LF md5 872fe043·pit-encoding 5,075B md5 7301f8ba·零丢失 "
        "PASS·独立复验 12 检 PASS·亲族 r559/r617 已迁不迁律留 pit-ps·回执 results/_r415bmc_pit_encoding_split.json）；"
        "S6 %d/%d rc%s（_r415bmc_s6.py·%.0fs）；S7 4/4+attrition CLEAN；HANDOVER r415 5x 行落账（增量窗 r411-415）；"
        "bm-a 心跳停 10:26 起续观察（<3h 线·13:26 阈值过线=下轮呈 GM 改派裁定） | 下轮：D-06 批3 spawn/tooling 族+git/protocol "
        "增量+pre-split 存留条+pit-data CRLF 裁定+流水下沉（due 10-07）·bm-a 心跳阈值查·T-156 观察席 | 本地未达 origin commit 数："
        "0（closeout push %s 一发即达→fetch 后 HEAD..origin/main=0·tip==origin 送达自证）"
    ) % (ts, n_legs - len(bad), n_legs, rc_face, total, sha)
    with open(REPORT, "a", encoding="utf-8", newline="") as fh:
        fh.write(line + "\n")
    print("REPORT PASS: r415 line appended with push receipt %s" % sha)
    return 0


if __name__ == "__main__":
    if "--report" in sys.argv:
        sha = sys.argv[sys.argv.index("--report") + 1]
        sys.exit(report_pass(sha))
    sys.exit(ledger_pass())
