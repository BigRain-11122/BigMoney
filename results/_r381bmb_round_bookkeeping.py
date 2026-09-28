# r381 bm-b round bookkeeping: CODELY kenglu append + round report line
# + state.json 381 + heartbeat (byte-style-aware appends per r381 lesson).
import json
import time
import ctypes
import subprocess
import datetime

NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")


def detect_style(path):
    b = open(path, "rb").read()
    crlf = b.count(b"\r\n")
    lf = b.count(b"\n") - crlf
    eol = "crlf" if crlf > 0 and crlf >= lf else "lf"
    return eol, b.endswith(b"\n")


def append_line(path, text):
    eol, trail = detect_style(path)
    line = text.encode("utf-8") + (b"\r\n" if eol == "crlf" else b"\n")
    if not trail:
        sep = b"\r\n" if eol == "crlf" else b"\n"
        with open(path, "ab") as fh:
            fh.write(sep)
    with open(path, "ab") as fh:
        fh.write(line)
    print("appended", path, eol)


# ---- 1) CODELY.md kenglu (one entry, <=1.5KB, four-questions gate pass)
kenglu = ("- [2026-09-28 12:4 r381 bm-b] 坑律：**共享 JSON 台账（runnable_pool 等）"
          "禁裸 json.dump 重写——落笔前先保字节风格**：池文件原=CRLF+无尾换行，"
          "json.dump(indent=2)+newline='\\n' 全量重写=3,272 行全文件 diff"
          "（=跨机并发写者冲突面+审阅噪音，r367 \\r\\r\\n 族姊妹面）；"
          "修法=写前探原字节（CRLF 计数+尾字节），dump 后还原行尾与尾换行"
          "（out.replace('\\n','\\r\\n')、不加尾），验收=git diff --stat 仅内容行翻面。"
          "How to apply：任何 append/注记类池台账编辑先跑行尾探针再落笔；"
          "全文件翻面 diff=当场返工。指针=results/_r381bmb_pool_note.py、"
          "claim commit 5bdade34（churn 版）→ amend 后净 diff=1 行。")
append_line("CODELY.md", kenglu)

# ---- 2) round report line (house format)
report = (
    f"{TS} | round 381 bm-b | dept:策略+研究+工程+舰队 (fix-first 探针面律修复轮·W4 线内闭环) | "
    "WM-VERDICT: 绿 red=false@11:40:23·probe 12:16 py_low_with_work_cands=RAM 顶合法占用"
    "(census W2B memory-bound 慢尾 4workers+W4-GENERATE 单进程 dedup 在飞·free 1.77-2.09GB·"
    "判定族按 MASS sec.9.1 冻结序+RAM r354 门排队=非违令如实点名) | did: "
    "(1) S0-1 bm-b 锚定·轮首树净·pull --rebase up-to-date+轮中 push 拒收按律收口"
    "(co-close b6d859f4 活写面快照 5 件=census checkpoint 推进/autofill 保活/fuse 双账/p1d 门，"
    "rebase 零冲突两提交 bm-c r161 落地); "
    "(2) S0.5 orders 99/99 轮首+收尾双扫零未回执·decisions.md 本机缺位零动作(r177 律)·"
    "firm/DECISIONS.md 尾=r239 无新行·集团席3(C-02)意见已在册 F-20260928-01·inbox 零未读; "
    "(3) smoke 25/25; "
    "(4) S3 主闭环=W4-GENERATE 11:46:03 G-VOL 探针锚诚实拒绝→轮内 r138 式 crash-fix-relaunch 全闭环: "
    "根因=runner 错装 tl1.load_core() W1-floor 面(2020-01 起 1631 bar·calm594/wild518·med500 首有效 2022-02-25)"
    "≠prereg §2 冻结锚面=data/daily/sh510300.csv 全史 3,483 行(git 在册·r396 探针基)——"
    "raw 面本机复算锚字面吻合(3483/na519/first_valid_bar_idx 519=2014-07-17/calm 1523/wild 1441); "
    "med500 窗 519 bar>floor→earliest 试用信号日 ⇒ leg-L 面 2021-04~2022-02-24 信号日 med500=NaN "
    "错误 gate-closed ⇒ overlay 面分歧=真科学面修正(锚无错·prereg 零改·零产品烧毁单射守卫未触发); "
    "单写者认领 MSG-20260928-1215(W3 MSG-0839 先例)+池分片注记→13 处修: "
    "_vol_face_full/_vol_state_full raw 全史装载器(≤CUTOFF 截断+末行==cutoff 断言)+"
    "G-VOL 锚断言五调用点全迁 raw 面(generate/screen-prep/screen/judge-prep/judge)+"
    "leg-L/D 面降级结构律(任意面恒真)+GATE 面 W3 机械零动→py_compile rc0+live probe ANCHOR-PASS+"
    "leg-L STRUCT-PASS+selftest 84/84→commit 61f81785 push 落地; "
    "autofill 12:13:42 修复态重发(fuse 12:13:37 S16c pick-time sha 变更自动清=r379 律第二实弹证)→"
    "G-VOL 门过·raw 5000 抽零排除·dedup face 1750/5000 在飞(harvest=下轮 r244 律); "
    "(5) S6 30 腿 rc=0: audit CLEAN(py48.3%/GPU4%/零旗/pool_ready=2)/"
    "scorecard+daily_scorecard+build_status+promotion+t35_export=bma 静默 137-138min "
    "STALE_MIN stale-takeover derive 合法×5(scorecard 6traders S2A4 best VOLATILITY-CE-01 87.0)/"
    "update_daily 盘中 no-op cutoff 09-24(09-25 中秋休市面板无缺)/regime ORANGE shadow d1/"
    "clock CALL-0924 ORANGE_COOL sleeves4 act0/lhb 30min 节流 no-op/"
    "heat+futures+repo+options+moneyflow+sina_mf+ths+ah bm-a 宿主诚实 no-op×7/"
    "fund_premium bm-c 宿主 no-op/astock_daily+rev_osc 本机双车道 cutoff09-24 幂等 no-op/"
    "fundamental 2.5h fresh 跳过/b_layer 5222/3517/1705 all_pass/"
    "live.paper+t35_open_fill+t24_prospect_paper 无新 bar 诚实跳/aggr+alloc+grid 幂等 no-op/"
    "system_v1 bma 守卫/t35_export 0924 6traders 18pos equity 5996645/"
    "daily_report 0928 faces4 token1/token_meter delta0(L2 crash-fuse refusals 4/3sigs 披露); "
    "(6) S4 坑律 1 条入 CODELY(共享 JSON 台账字节风格律); "
    "(7) S7 自愈: loop pin=2 no-op+watchdog 在位 12:40 就绪+claw identical+state 381 | "
    "verified: smoke 25/25+selftest 84/84+锚探针 live PASS(3483/519/1523/1441)+py_compile rc0+"
    "S6 全腿逐项 rc=0+pool 净 diff 1 行(字节风格修正后)+心跳写后自证 epoch int+clock fromisoformat 断言 | "
    "next: (a) W4-GENERATE dedup 收尾→candidates 落地→harvest(entry+shard done r244 律)+"
    "screen slice build 认领(W2 r360 先例)→SCREEN 入池; (b) census W2B 慢尾 ETA 午后→RAM 窗→"
    "W1-JUDGE flip 评估(r357 defer 前件)+V2-P1 un-defer; (c) judge-prep W2/W3=本机物理域 RAM 门后; "
    "(d) 今日 15:30 新 bar 窗本机双车道+三件套; (e) bma 静默 15:35+ 按 MSG-1042 评估; "
    "marks/账本/SEED 全 +0")
append_line("logs/iteration-loop/round_reports.md", report)

# ---- 3) state.json round_no -> 381
sp = "state.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 381
st["note"] = ("r381: W4-GENERATE G-VOL 面律修复轮内闭环(11:46 拒→诊断 load_core 1631bar floor 面 "
              "vs 冻结锚面 sh510300.csv 3483 全史→MSG-1215 认领→13 修+selftest 84/84+锚 live PASS→"
              "61f81785→autofill 12:13:42 修复态重发 dedup 在飞→harvest 下轮)+S6 30 legs rc=0+"
              "S7 自愈三件套+坑律 1 条(池台账字节风格); next: W4 harvest+screen slice build 认领+"
              "census 尾→RAM 窗→judge flips 评估+W2/W3 judge-prep(本机物理域 RAM 门后)")
eol, trail = detect_style(sp)
out = json.dumps(st, ensure_ascii=False, indent=1)
if eol == "crlf":
    out = out.replace("\n", "\r\n")
with open(sp, "wb") as fh:
    fh.write(out.encode("utf-8") + ((b"\r\n" if eol == "crlf" else b"\n")
                                    if trail else b""))
print("state round_no ->", st["round_no"])

# ---- 4) heartbeat fleet/machines/bm-b.json
hp = "fleet/machines/bm-b.json"
hb = json.load(open(hp, encoding="utf-8"))


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
ram_gb = round(ms.ullAvailPhys / 1024 ** 3, 2)
tot_gb = round(ms.ullTotalPhys / 1024 ** 3, 2)
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
except Exception:
    cpu_pct = None
try:
    q = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=20)
    vram_mb = int(q.stdout.strip().splitlines()[0])
except Exception:
    vram_mb = None
vram_gb = round(vram_mb / 1024, 2) if vram_mb is not None else None
epoch = int(time.time())
hb["last_seen"] = TS
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = TS
hb["current_task"] = ("r381 done: W4-GENERATE G-VOL face-fix closed loop "
                      "(refusal 11:46 root-caused = probe/overlay wired to W1-floored "
                      "load_core face 1631 bars vs frozen anchor face sh510300.csv 3483 "
                      "full-history; anchors reproduced byte-exact live "
                      "3483/519/2014-07-17/1523/1441; claim MSG-20260928-1215 -> 13-edit "
                      "raw-face law fix selftest 84/84 commit 61f81785; autofill relaunched "
                      "fixed-sha 12:13:42, fuse S16c auto-cleared 12:13:37 r379-law 2nd live "
                      "proof; generate burning dedup 1750/5000, harvest next round; overlay "
                      "face divergence = real-science fix [2021-04..2022-02-24 signal days "
                      "med500 NaN on floored face], prereg zero-change zero products burned) "
                      "+ S6 30 legs rc=0 (bma stale-takeover derives x5 lawful) + WM GREEN; "
                      "next: W4 harvest -> screen slice build claim -> census tail -> RAM "
                      "window -> judge flips eval + W2/W3 judge-prep (bm-b physical domain)")
hb["cpu_cores"] = 16
hb["free_ram_gb"] = ram_gb
hb["total_ram_gb"] = tot_gb
if cpu_pct is not None:
    hb["cpu_util_pct"] = cpu_pct
    hb["cpu_pct"] = cpu_pct
hb["idle_ram_gb"] = ram_gb
hb["idle_ram_mb"] = int(round(ram_gb * 1024))
hb["free_ram_mb"] = int(round(ram_gb * 1024))
if vram_gb is not None:
    hb["gpu_free_vram_gb"] = vram_gb
    hb["gpu_idle_vram_gb"] = vram_gb
    hb["gpu_free_vram_mb"] = vram_mb
    hb["gpu_idle_vram_mb"] = vram_mb
hb["round_no"] = 381
hb["round"] = 381
hb["loop_round"] = 381
hb["verdict"] = ("healthy: smoke 25/25, S6 30 legs rc=0, orders 99/99 dual-scan clean; "
                 "W4-GENERATE G-VOL refusal fixed+relaunched in-round (r138 precedent, "
                 "anchors byte-exact on raw face, selftest 84/84, zero products burned, "
                 "burning dedup 1750/5000); census W2B slow-tail alive memory-bound no-kill; "
                 "judge family queued per MASS sec.9.1 + RAM r354 gate "
                 "(py_low_with_work_cands = lawful RAM-ceiling, not idle); bma silence "
                 "137min stale-takeover derives lawful; board 0 open all claimed; "
                 "pool 2 ready both owned+burning; migration executor armed precheck "
                 "waiting (Tuanjie editor), window to 09-29 12:00, zero interference")
eol, trail = detect_style(hp)
out = json.dumps(hb, ensure_ascii=False, indent=1)
if eol == "crlf":
    out = out.replace("\n", "\r\n")
with open(hp, "wb") as fh:
    fh.write(out.encode("utf-8") + ((b"\r\n" if eol == "crlf" else b"\n")
                                    if trail else b""))

# ---- 5) self-verification (smoke F7 laws: epoch int + clock exact format)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert datetime.datetime.fromisoformat(chk["clock_read"]), "clock must parse"
assert chk["clock_read"].endswith("+08:00") and "T" in chk["clock_read"]
chk2 = json.load(open(sp, encoding="utf-8"))
assert chk2["round_no"] == 381
print("heartbeat verified: epoch", chk["heartbeat_epoch_utc"],
      "clock", chk["clock_read"], "| ram", ram_gb, "gb | cpu", cpu_pct,
      "| vram", vram_gb, "gb")
