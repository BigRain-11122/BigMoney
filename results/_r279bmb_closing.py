# -*- coding: utf-8 -*-
"""r279 bm-b S7 closing: round report line + state.json + heartbeat + CODELY.md entries.
Byte-face probed per R255/R257 (five-face) before every JSON write; md files append-only."""
import json, time, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime.datetime.now().astimezone()
ISO = NOW.isoformat()            # T-separated (R262 law)
ISO_SP = NOW.strftime("%Y-%m-%d %H:%M:%S")
EPOCH = int(time.time())          # JSON int (R170/R178 law)
HHMM = NOW.strftime("%H:%M")

def probe_write_json(path, d):
    raw = open(path, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf"); crlf = b"\r\n" in raw; tail = raw.endswith(b"\n")
    lines = raw.decode("utf-8-sig").splitlines()
    indent = len(lines[1]) - len(lines[1].lstrip(" ")) if len(lines) > 1 else 1
    out = json.dumps(d, ensure_ascii=False, indent=indent)
    if tail: out += "\n"
    if crlf: out = out.replace("\n", "\r\n")
    b = ("\xef\xbb\xbf" + out.encode("utf-8")) if bom else out.encode("utf-8")
    open(path, "wb").write(b)
    return json.loads(open(path, "rb").read().decode("utf-8-sig"))

def append_line(path, line):
    raw = open(path, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    add = line.encode("utf-8")
    sep = b"" if raw.endswith(b"\n") or not raw else b"\n"
    open(path, "ab").write(sep + add)
    back = open(path, "rb").read().decode("utf-8-sig")
    assert line.strip()[:60] in back[-2000:], "append verify failed"

# ---------------- 1. round report line ----------------
RR = ROOT / "logs/iteration-loop/round_reports.md"
rr_line = (
    f"{ISO} | r279 (bm-b) | dept:研究/数据/工程 | 水位=绿（red=false·py_low_board_clear 合法闲置：open_tickets=0 四 CEO 票全 bm-a 在飞"
    "+池唯一 ready 批 FUSION-P1-NAV 单分片 owner=bm-a 活跃·claim_lost_yield 实录）| O-20260926-2330+O-2026-09-26-2335 双 CEO 令回执："
    "呈件令=超跌反弹 ETF 代理交叉验证已在档（淬炼炉 P1 -41.4%→+20.9% 胜率 26.9%→61.3%·机理=熊市闸第一杠杆+首阳反接刀胜率杠杆）+淬炼令"
    "=REFINE_BENCH_LAW v1.0 在册核验（见即淬炼禁排队采纳）→bm-b 执行面=T-87 A 股 akshare 采集器供给车道认领（O-2330 §三①通道·票面 "
    "progress_r279_bmb commit 即锁·step-0=日线端点验证 r280 开建·与 bm-a s2 prereg 面零撞）；T-88 认领竞速败 bm-a（§4 commit 序 "
    "0cd23254 23:18:36 < 7313592d 23:24:37·S0 fetch 窗不可见=善意竞速·r278 先例）→整票让路+我的 DOMAIN_AUDIT 重复首切弃置"
    "（bm-a 12 域正典）+实测五发现降格捐赠件 research/DOMAIN_AUDIT-r279bmb-measured-notes.md（货基 ETF 511880/511990/511660 缺口"
    "·ext_slots dzjy/gdhs/margin 未登记·futures 10 主连·eligibility 11,626 行·ah_panel 本机空）+PRODUCT_MATRIX v1.2 缺口清单刷新"
    "（增 4-5 行：A 股日线通道+现金腿真实收益）；rebase 撞车批按 skill 正典解（autofill_state 同秒 tie→HEAD 让 bm-a 面+launches 恒等 49 零丢失"
    "·T-86/87 双 UU 并集·审计 AA 让路）+pre co-commit 同秒让路成空笔被 rebase 合法丢弃+假消息笔 r266 律翻正（两笔并一 37fc6464）；"
    "S6 21 腿全 rc=0+纸盘族 8 腿 bar 门诚实 skip（周六无新 bar·clock ORANGE_COOL idempotent）+月度三件套/季度治理面正确跳过"
    f"（10-01 界/09-26 槽已 discharge）；orders_ack 87→89 | evidence: 两令 origin 原文+REFINE-BENCH-20260926-P1 消费+commit 37fc6464 实况"
    "+S6 summary 21rc=0（results/_r279bmb_s6_summary.json）+心跳 89/89 自证 | next: r280=T-87 采集器 step-0 端点验证+建器"
    "（家属制 update_* 范式：2.5s 限速/checkpoint/conn-fuse/分离后台/selftest）；T-86 s2 runner 落地即 workers_plan 入池参与；"
    "T-88 s3 现金腿若开分片即参与；每轮 S0 首探迁移根（executor PID 28696 编辑器门仍等待）"
)
append_line(RR, rr_line)
print("round_reports appended")

# ---------------- 2. state.json ----------------
ST = ROOT / "logs/iteration-loop/state.json"
d = json.loads(open(ST, "rb").read().decode("utf-8-sig"))
d["round_no"] = 279
d["did"] = ("r279: O-2330/2335 CEO double-order receipts (REV-OSC context consumed, REFINE_BENCH_LAW verified in-file, "
            "T-87 akshare A-share collector supply-lane claimed on ticket, opens r280) + T-88 claim race LOST to bm-a per s4 "
            "(0cd23254 23:18:36 < mine 23:24:37, S0-fetch-window invisible honest race) -> whole-ticket yield, my duplicate "
            "DOMAIN_AUDIT first-cut discarded (bm-a 12-domain canonical), measured five findings donated as addendum "
            "(MM-ETF gap/ext_slots/futures-10/eligibility/ah_panel) + PRODUCT_MATRIX v1.2 gap items 4-5; rebase collision batch "
            "resolved per skill (autofill same-second tie->HEAD bm-a face, T-86/87 union, audit yield, false-message commits "
            "rewritten per r266 into single honest 37fc6464); S6 21 legs rc=0 + 8 paper legs honest bar-gate skip; orders_ack 87->89")
d["verdict"] = "green"
d["next"] = ("r280: T-87 collector step-0 endpoint verify + build (family conventions); T-86 workers_plan pool entry when "
             "s2 runner lands; T-88 s3 shard participation if opened; every round S0 first-probe migration root (editor-gated); "
             "09-28 Monday new-bar chain + 10-01 month-first trio")
d["last_round_ts"] = ISO
d["last_result"] = "ok"
d["current_task"] = ("r279 done: O-2330/2335 receipts (T-87 collector lane claimed, opens r280); T-88 yielded to bm-a per s4 "
                     "with addendum donation; ack 89/89")
d["last_tick"] = NOW.strftime("%H:%M")
d["updated_at"] = ISO
d["last_seen"] = ISO
d["ts"] = ISO_SP[:16]
d["last_run"] = f"R279 {ISO}"
d["last_round_at"] = NOW.strftime("%H:%M")
d["updated"] = NOW.strftime("%H:%M")
back = probe_write_json(ST, d)
assert back["round_no"] == 279
print("state.json -> round 279")

# ---------------- 3. heartbeat ----------------
HB = ROOT / "fleet/machines/bm-b.json"
h = json.loads(open(HB, "rb").read().decode("utf-8-sig"))
try:
    import psutil
    ram = psutil.virtual_memory()
    free_ram_gb = round(ram.available / 1024**3, 1)
    cpu_pct = psutil.cpu_percent(interval=1)
except Exception:
    free_ram_gb, cpu_pct = h.get("free_ram_gb", 13.3), h.get("cpu_util_pct", 15)
h["last_seen"] = ISO
h["heartbeat_epoch_utc"] = EPOCH
h["clock_read"] = ISO
h["current_task"] = d["current_task"]
h["cpu_cores"] = 16
h["free_ram_gb"] = free_ram_gb
h["idle_ram_gb"] = free_ram_gb
h["idle_ram_mb"] = int(free_ram_gb * 1024)
h["cpu_util_pct"] = cpu_pct
h["cpu_pct"] = cpu_pct
h["round_no"] = 279
h["verdict"] = "py_low_board_clear"
h["orders_ack"] = h["orders_ack"].rstrip() + " O-20260926-2330-bm-a.md O-2026-09-26-2335-bm-a.md"
h["n_orders_ack"] = h.get("n_orders_ack", 87) + 2
back = probe_write_json(HB, h)
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178)"
assert "T" in back["clock_read"], "clock_read must be T-separated (R262)"
assert back["n_orders_ack"] == 89
print(f"heartbeat: epoch={back['heartbeat_epoch_utc']} (int ok) ack={back['n_orders_ack']} clock={back['clock_read']}")

# ---------------- 4. CODELY.md ----------------
CM = ROOT / "CODELY.md"
pitfall = (
    f"- [{ISO_SP}] 坑律（bm-b r279·T-88 认领竞速双烧·r278 让路族新参·E1 push 期自捕）：**认领开放票前必须先 fetch 再读票面——"
    "S0 拉取窗与在飞认领 commit 的时间差（bm-a 认领 0cd23254 23:18:36+push 23:20:29 vs 本机 S0 fetch ~23:20:45 只达 23:18:05 "
    "origin）使「票面 open」读数为陈旧面；按陈旧面认领+同轮交付 first-cut=整票重复劳动（DOMAIN_AUDIT 11 域 vs 12 域双烧，弃置我件）**；"
    "正律=①认领写票前一刷新 fetch（秒级成本）+票面 status 再读②让路后自产件显式降格（弃置/捐赠 addendum 勿静默丢）+commit 消息 r266 律翻正"
    "（两笔并一重写）③连带=rebase 中同秒 tie 让路（last_tick 整 dict 让 HEAD）会使 pre-commit 变空笔被合法丢弃=零变更正常现象勿追。"
    "指针=results/_r279bmb_t88_yield.py+37fc6464 实录+r279 轮报告行\n"
)
exec_line = (
    f"- [{ISO_SP}] 执行 O-20260926-2330+O-2026-09-26-2335（CEO 超跌反弹呈件+淬炼令·bm-b r279）：呈件交叉验证与淬炼炉 P1 已在档"
    "（-41.4%→+20.9%）；bm-b 面=T-87 A 股 akshare 采集器供给车道认领（r280 开建）；T-88 让路 bm-a 附实测五发现捐赠件；"
    "详录=round_reports.md r279 行（复述禁令：不在此重复）\n"
)
raw = open(CM, "rb").read()
bom = raw.startswith(b"\xef\xbb\xbf")
txt = raw.decode("utf-8-sig")
sep_needed = not txt.endswith("\n")
with open(CM, "ab") as f:
    if sep_needed:
        f.write(b"\n")
    f.write(pitfall.encode("utf-8"))
    f.write(exec_line.encode("utf-8"))
back = open(CM, "rb").read().decode("utf-8-sig")
assert "T-88 认领竞速双烧" in back[-1500:] and "O-20260926-2330" in back[-1500:]
print("CODELY.md: pitfall + exec line appended")
print("ALL CLOSING FILES DONE", HHMM)
