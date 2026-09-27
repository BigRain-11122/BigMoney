# -*- coding: utf-8 -*-
"""r323 bm-b: S7 closing writes -- round report line (UTF-8 append), state.json, heartbeat.
All writes via io.open(..., encoding='utf-8') per r323 pitlaw (no bare open(), no PS Add-Content).
"""
import io, os, json, time, ctypes, subprocess, datetime

REPO = r"C:\Users\Administrator\Desktop\Bigmoney"
NOW = "2026-09-27 12:5x"
TS = "2026-09-27T12:51:30+08:00"

ROUND_LINE = (
    "2026-09-27T12:5x+08:00 | r323 bm-b | dept:舰队+工程 | "
    "水位=绿（red=false@12:30:14 lane healthy·probe 12:43 py_low_board_clear 合法 idle 白名单=板 0 open+bandit 0+池 77/77 done（T19-PHANTOM bm-c r80 已收割翻面）+主线全门控）| "
    "did: (1) S0 显式 stash 三步舞 FF pull 265c9cf1→fbef43da（bm-c r80 T19 stage-2c 收获批）零冲突·p1d_gates 保持 unstaged 设计态（r317 正典）"
    "(2) S0.5 双扫 orders 96/96 零未回执（轮首+S7 收尾一致）·decisions.md 候选路径不存在=零动作·post_review 2947 行 0 NO/X/WAIT "
    "(3) S1 smoke 25/25 "
    "(4) S3 主闭环=r320 GBK 污染残留根修：round_reports.md r320 行（L475·3381B 全 GBK）=r320 bm-a 只修冲突集件（HANDOVER）漏扫同窗生产者非冲突件·strict 读者轮首实撞 UnicodeDecodeError→正典修复=生产者两提交 54 件面全量 strict UTF-8 扫（孤例）+坏区 strict gbk 无损转码+全文件重验+邻行断言（r319/r321/r322 在场·行数 479 不变·零 GBK 残留）+双读者复核（进程内断言+PS 显式 UTF-8 面）·指针=results/_r323bmb_gbk_sweep.py "
    "(5) S4 坑律新条（污染修复扫描面=生产者写入面全量）+CODELY 水位律当窗整编 9609→7805B（十二批外迁 r317/r318/r319 共 2736B verbatim·multiset 零丢失 PASS）·指针=results/_r323bmb_codely_archive.py "
    "(6) S6 全链 29 腿跑全 rc=0（32 口径=29 跑+3 无新 bar 触发件依法跳 live.paper/t35_open_fill/t24_prospect_paper；audit CLEAN flags=0 py 1.6%·daily 0 新行 cutoff 09-24 中秋假日面·六他机车道诚实 no-op·本机 astock 面板新鲜 no-op·REV-OSC 幂等 no-op·promotion 0/22 NOT-ELIGIBLE 合法·纸盘四族幂等 no-op·token delta=23）"
    "(7) 迁移窗只读探针：v2.2 armed 编辑器门未开（12:46 precheck waiting）·窗至 09-29 12:00·零双 arm "
    "(8) S7 任务双源健康（IterationLoop 正在运行·Watchdog 就绪——schtasks 原始面复核，zh-CN 标签过滤失配教训非任务面问题） | "
    "验证证据：smoke 25/25·sweep verdict PASS（54 件扫·断言 9/9）·codely 整编 verdict PASS（7805B·multiset zero-loss）·S6 29 RC=0 全记账·orders 96/96 双扫 | "
    "下轮：sina 深面板 complete+N≥250 后 sina-construct prereg 起草（bm-a 判定窗）·GM 审 M-20260927-01·周一 09-28 09:15 T-91 s3 首队列入场+T-87 astock 15:30 首拉·10-01 月界三件套+REGIME_GUARD v3 日期门·R325 5x 核对"
)

def free_ram_gb():
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    ms = MS(); ms.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
    return round(ms.ullAvailPhys / (1024 ** 3), 2)

def gpu_free_mb():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                             capture_output=True).stdout.decode().strip()
        return int(float(out.splitlines()[0]))
    except Exception:
        return None

def main():
    # 1) round report append (UTF-8)
    rr = os.path.join(REPO, "logs", "iteration-loop", "round_reports.md")
    with io.open(rr, "a", encoding="utf-8", newline="") as f:
        f.write(ROUND_LINE + "\n")
    t = io.open(rr, encoding="utf-8").read()  # strict re-verify
    assert ROUND_LINE[:40] in t, "round line append failed"

    # 2) state.json update
    sp = os.path.join(REPO, "logs", "iteration-loop", "state.json")
    st = json.load(io.open(sp, encoding="utf-8"))
    st.update({
        "round_no": 323,
        "did": "r323: GBK-residue root fix (round_reports r320 line, producer-face full sweep canon) + S4 pitlaw + CODELY 12th-batch reorg 7805B + S6 29 legs rc=0",
        "verdict": "green",
        "next": "sina deep-panel prereg after complete (bm-a window) + Mon 09-28 09:15 T-91 s3 + astock 15:30 first pull + 10-01 month trio + R325 5x",
        "last_round_ts": TS,
        "last_result": "ok",
        "current_task": "r323 closed: GBK repair canon + maintenance round; next = sina-construct prereg gate + Monday T-91/T-87 chain",
        "updated_at": TS,
        "last_seen": TS,
        "ts": "2026-09-27 12:51:30",
    })
    with io.open(sp, "w", encoding="utf-8", newline="") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)

    # 3) heartbeat
    hp = os.path.join(REPO, "fleet", "machines", "bm-b.json")
    hb = json.load(io.open(hp, encoding="utf-8"))
    epoch = int(time.time())
    hb.update({
        "last_seen": TS,
        "verdict": "healthy",
        "loop_round": 323,
        "current_task": "r323 maintenance+GBK-repair round closed",
        "cpu_cores": 16,
        "free_ram_gb": free_ram_gb(),
        "gpu_free_vram_mb": gpu_free_mb(),
        "heartbeat_epoch_utc": epoch,
        "clock_read": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    })
    with io.open(hp, "w", encoding="utf-8", newline="") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)

    # self-verify: json parse + epoch int + clock T-sep + orders_ack intact
    hb2 = json.load(io.open(hp, encoding="utf-8"))
    assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
    assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"], "clock_read must be ISO with T"
    assert len(hb2.get("orders_ack", [])) == 96, "orders_ack must stay 96"
    print(json.dumps({"round_line": "ok", "state_round": st["round_no"],
                      "epoch": hb2["heartbeat_epoch_utc"], "clock": hb2["clock_read"],
                      "ram": hb2["free_ram_gb"], "gpu": hb2["gpu_free_vram_mb"],
                      "ack": len(hb2["orders_ack"])}, ensure_ascii=False))

if __name__ == "__main__":
    main()
