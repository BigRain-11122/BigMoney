"""r815 bm-b closeout: state bump + heartbeat + round-report line + inbox move.

Pure bookkeeping per S5/S7 (fixed-field ledger line, heartbeat epoch as JSON
int per R170/R178, clock_read T-separated per R262). Encoding: all appends
UTF-8 (round_reports.md is UTF-8; PS-console mojibake is display-only).
"""
import ctypes
import glob
import json
import os
import shutil
import subprocess
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(REPO, "state.json")
HB = os.path.join(REPO, "fleet", "machines", "bm-b.json")
REPORT = os.path.join(REPO, "logs", "iteration-loop", "round_reports.md")
INBOX = os.path.join(REPO, "fleet", "inbox")


def now_iso():
    t = time.time() + 8 * 3600.0  # local tz is UTC+8 (Asia/Shanghai)
    return time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.gmtime(t))


def free_ram_gb():
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    ms = MS()
    ms.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
    return round(ms.ullAvailPhys / (1024 ** 3), 1)


def gpu_free_vram_gb():
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                            "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=15)
        return round(float(r.stdout.strip().splitlines()[0]) / 1024.0, 2)
    except Exception:
        return None


def main():
    ts = now_iso()
    ram = free_ram_gb()
    vram = gpu_free_vram_gb()

    now_active = ("r815: tech T7+T14 closed (watermark red-card two-state "
                  "bucket read: pool-batch vs board-work + automated "
                  "violation-naming facts) + S6 chain 42/42 rc0")
    current_task = ("r816: tech queue head T8 (minute_feed completeness "
                   "verifier) + waiting: astock refresh closeout / bm-c W17 "
                   "burn receipt / moneyflow panel unblock")
    task = ("tech queue T8 head; O-1105 remaining face law-blocked (12mo "
            "forward accumulation + collector unbuilt) = lawful wait")
    latest_artifact = ("r815: scripts/py_watermark.py + Tools/watchdog.ps1 + "
                       "Tools/watchdog_c7_selftest.ps1 (bucket facts face; "
                       "selftests 27+18 legs green, 04:2x)")
    next_milestone = ("r816: tech T8 minute_feed gap verifier (<=48h); "
                      "consume bm-c W17 burn closeout receipt; astock "
                      "refresh closeout")
    verdict = ("r815: T7+T14 closed (two-state bucket red read -- pool-batch "
               "only triggers RED, board-work false-red class fixed, legacy "
               "sample fallback kept for 3-machine roll); smoke 49/49; S6 "
               "chain 42/42 rc0; pool dualrun ZERO-DRIFT streak 51; watermark "
               "buckets pool0/board0/local=astock lawful in-flight; "
               "supply_gap/ignition_sla yielded to bm-c W17 in-flight; "
               "orders both sweeps zero unacked; attrition CLEAN")

    st = json.load(open(STATE, encoding="utf-8"))
    st["round_no"] = 815
    st["round"] = 815
    st["round_no_label"] = "r815"
    st["last_round_at"] = ts
    st["ts"] = ts
    st["updated"] = ts
    st["updated_at"] = ts
    st["last_seen"] = ts
    st["clock_read"] = ts
    st["now_active"] = now_active
    st["current_task"] = current_task
    st["task"] = task
    st["latest_artifact"] = latest_artifact
    st["next_milestone"] = next_milestone
    st["next"] = ("r816: tech queue head T8 + consume bm-c W17 burn closeout "
                  "receipt + waiting: astock refresh closeout / moneyflow "
                  "panel unblock / O-1105 collector build")
    st["did"] = ("r815: tech T7+T14 merged closeout (py_watermark bucket "
                 "facts face + watchdog C7 two-state red read + auto naming, "
                 "selftests 27/18 legs) + S6 full chain 42/42 rc0")
    st["verdict"] = verdict
    json.dump(st, open(STATE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    hb = json.load(open(HB, encoding="utf-8"))
    hb["round"] = 815
    hb["round_no"] = 815
    hb["now_active"] = now_active
    hb["current_task"] = current_task
    hb["task"] = task
    hb["latest_artifact"] = latest_artifact
    hb["next_milestone"] = next_milestone
    hb["verdict"] = verdict
    hb["last_action"] = ("r815: tech T7+T14 (py_watermark+watchdog two-state "
                         "bucket red read + auto naming) + S6 full chain "
                         "re-run 42 legs + ALL inbox msg ack (T-181 prereg "
                         "freeze declaration)")
    hb["last_round_at"] = ts
    hb["last_seen"] = ts
    hb["updated"] = ts
    hb["ts"] = ts
    hb["clock_read"] = ts
    hb["heartbeat_epoch_utc"] = int(time.time())
    hb["cpu_cores"] = 16
    hb["free_ram_gb"] = ram
    if vram is not None:
        hb["gpu_free_vram_mb"] = int(vram * 1024)
        hb["gpu_free_vram_gb"] = vram
    hb["idle_rounds"] = 0
    hb["agenda_starved"] = False
    hb["orphan_faces"] = 0
    hb["orphan_face_note"] = ("r815 probe 04:13: 11 lawful py faces 0 "
                              "orphans; astock refresh lock alive (T-87 bm-b "
                              "lane full-universe pull in-flight, lawful)")
    ack = hb.get("orders_ack", [])
    hb["orders_ack_count"] = len(ack)
    hb["sync"] = {"ahead": 0, "behind": 6, "last_push_ts": ts,
                  "note": "r815 closeout: commit+pull --rebase onto "
                          "520e190b1..d4d3a0aa7 (6 incoming) then push; "
                          "post-push rev-list+ls-remote self-verify in "
                          "round-report addendum"}
    json.dump(hb, open(HB, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # round-report ledger line (UTF-8, one physical line, fixed fields)
    line = (
        "{ts} | r815 dept:工程（tech T7+T14 同窗合并出列：水位红牌两态桶判读+违令点名自动化）"
        " | 孤儿面=0（11 合法 py 面·astock 刷新 lock alive）"
        " | watermark verdict=绿（watchdog red=false lane=healthy @04:13:12 槽位；"
        "probe=py_low_with_work_cands→新桶面机械合法 idle 证明〔pool_batch=0/board_open=0/"
        "board_inflight=0/local_batch=1=astock 网络型在飞 lock alive〕；T14 落地后红牌读法只认"
        "池批可跑——T-180/T-181 认领板工误红类根治+legacy 样本 fallback 保三机滚动零断档；"
        "同窗 compute_audit 旗 supply_gap/ignition_sla=bm-c W17 在飞既有裁决 §4 让路续）"
        " | 本轮主产出=①scripts/py_watermark.py 探针桶化事实面（_pool_ready_claimable 池批可跑"
        "+_board_inflight 在飞板工点名+record 四新键 pool_ready_ids/pool_ready_count/"
        "board_inflight_ids/work_cand_buckets；判面四态与 work_cands 输入字节不动=frozen face 纪律）"
        "②Tools/watchdog.ps1 C7 红牌两态读法（RED 触发面 open_tickets/bandit_open→freshest 样本 "
        "pool_ready_count>0；lane 文案 runnable-work→pool-batch-runnable；红文件加自动点名透传"
        "三键 work_cand_buckets/pool_ready_ids/board_inflight_ids）③Tools/watchdog_c7_selftest.ps1 "
        "12→18 腿（T9 板工-only 低载不红+桶事实随件/T10 池 ready 真红+pool_ready_ids 点名/T10b 满载"
        "不红；T1/T8b legacy 形继续压 fallback 路）④state/queue/tech.md 消耗行（T7+T14 出列 10→8·"
        "T8 队头）"
        " | 验证=smoke 49/49+S6 全链 42/42 rc0（results/_r815bmb_s6_log.txt）+py_watermark "
        "selftest 27 腿全绿+C7 selftest 18/18+attrition CLEAN（4 台账零活动损耗）+D-19 双水位 "
        "MATCH 零动作（_r686bmb_d19_check.json）+S7 自愈链全绿（loop 针位 2 符/watchdog 在/双爪在）"
        " | 等待面一行声明=O-1105 剩余面 CB 采集器未建+12 个月前向积累律禁 prereg（r814 定谳勿重扫）；"
        "moneyflow IC 参考批=面板 source-blocked（53/5222·conn_stopped·bm-a 车道 30min 自愈在案）；"
        "MSG-2026-10-10-0335-bma ALL 件回执（T-181 THERMO-OVERLAY-P1 冻结声明收悉·与本轮工作零交叠·"
        "移 processed）；MSG-20261010-040x T180-YIELD 件=本机 r813→bm-c 留置待 bm-c 消费"
        " | 本地未达 origin commit 数=收口段自证（addendum 行）"
        " | 下轮指针=r816：tech 队头 T8（minute_feed 数据完备性校验器）+等待面消费"
        "（astock 刷新收口/bm-c W17 烧录收口回执/moneyflow 面板恢复后 IC 批认领门）"
    ).format(ts=ts)
    with open(REPORT, "a", encoding="utf-8") as f:
        if os.path.getsize(REPORT) > 0:
            with open(REPORT, "rb") as rb:
                rb.seek(-1, os.SEEK_END)
                if rb.read(1) != b"\n":
                    f.write("\n")
        f.write(line + "\n")

    # inbox: ALL broadcast processed -> processed/
    src = os.path.join(INBOX, "MSG-2026-10-10-0335-bma.md")
    dst = os.path.join(INBOX, "processed", "MSG-2026-10-10-0335-bma.md")
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)

    # self-checks: heartbeat epoch is JSON int; clock_read T-separated
    hb2 = json.load(open(HB, encoding="utf-8"))
    assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
    assert "T" in hb2["clock_read"] and " " not in hb2["clock_read"].split("+")[0], \
        "clock_read must be T-separated"
    st2 = json.load(open(STATE, encoding="utf-8"))
    assert st2["round_no"] == 815
    print(json.dumps({"ts": ts, "round": 815, "ram_gb": ram,
                      "vram_gb": vram, "ack_n": len(ack),
                      "epoch_int": hb2["heartbeat_epoch_utc"],
                      "inbox_moved": os.path.exists(dst)}))


if __name__ == "__main__":
    main()
