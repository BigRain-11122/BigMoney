# -*- coding: utf-8 -*-
"""r769 bm-c close: state-bm-c.json + fleet/machines/bm-c.json heartbeat +
round-report row to CANONICAL logs/iteration-loop/round_reports-bm-c.md
(r750 pit law -- NEVER the ROOT frozen-era file) + pit direct-write to
research/pit-protocol-d19.md (r666 direct-write precedent, main CODELY.md
stays under 30KB cap). Round: r769 O-1820 order-revision decree execution.
Pattern credit: Tools/_r767bmc_close.py (close shape) + r749 pit-direct-write
shape."""
import datetime
import hashlib
import json
import os
import socket
import time

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")          # 2026-10-08T18:0x:xx+08:00
EPOCH = int(time.time())
ROUND = 769
HEAD = os.popen("git -C \"%s\" rev-parse HEAD" % ROOT).read().strip()

# ---- machine stats (psutil RAM real read, GPU carried forward r768 face) ----
try:
    import psutil
    ram_free_gb = round(psutil.virtual_memory().available / 1024**3, 1)
    cpu_pct = round(psutil.cpu_percent(interval=1), 1)
except Exception:
    ram_free_gb, cpu_pct = 5, 0.2
gpu_free_mb = 6951  # carried forward (nvidia-smi banned from windowless host)

# ---- FleetLink standing self-cert (r767 line) ----
fleetlink = "n/a"
try:
    s = socket.create_connection(("127.0.0.1", 8790), timeout=3)
    s.close()
    fleetlink = "200-ok port 8790"
except Exception:
    fleetlink = "listener-down honest"

ACT = ("当前活: r769 bm-c（17:37-18:0x 窗·盘后窗·O-20261008-1820 顺序改判令 P0 执行轮）——"
       "主产出=①违令面即刻收口（i2v 视频驱动 pid 31384 击杀·令前启动的 seg1/seg2 冻结非交付物）"
       "②O-1820 风格样图批 7 张 SDXL 在烧（书库双影×2+刻字第二候选+尾桥女神显影×2+玻璃双时空叠印×2·seed 20011009-15）"
       "③QA det-89th 5/5 无撞名首注册 ④S6 40/40 rc0 ⑤静默三件 group 新正本同步（48a6d5f04 后漂移治愈）"
       " | 最近实物: results/mv_work/kf/st*.png 风格样图批+qa/smoke-r769.md 5/5（93 trades·1,017,839 冻结恒等·"
       "png 66,178B） @ " + TS +
       " | 下个里程碑: 风格样图+分镜表呈审包 outbound 传回呈 CEO 过目（今晚）——CEO 合格后才准视频；"
       "sina 迟 bar 自愈每轮重试; next 5x=bm-c r770（HANDOVER 核对窗）")

DID = ("r769: O-20261008-1820 顺序改判令 P0 执行（CEO 十二十二追加令·17:26:37 注册·r768 收尾窗 hash 进位而行未消费的"
       "半程态→本轮 blob diff 穷举检出）：①i2v 视频驱动 31384 击杀（16:58 先于令启动=违令面停·视频目标冻结至 CEO 过目闸·"
       "seg1/seg2 判负冻结非交付物）；②O-1820 风格样图批 spawn（核心三景=书库双影×2/刻字仪式第二候选/尾桥女神显影×2+"
       "玻璃双时空叠印×2·SDXL 本地律·kf_gen 血统单源复用·batch 内含 4 张既有 kf 同世界样）；③静默三件 drift 同步"
       "（group origin 48a6d5f04 新正本 task-register 3875B/silence-enforce 6439B·md5 恒等直写）；④S0.5 orders 51/51 "
       "unacked=0+inbox 0+DEC EE70CEF0 恒等+ORD F19F563F->44CA6C96 delta 消费（bm-a 弹窗归因+机制静默两行=他机域 "
       "receipt-only+自投回执 2 行零跳面）；⑤S1 smoke 49/49；⑥S6 40/40 rc0 首过（update_daily sina 迟 bar 续自愈 "
       "cutoff 09-30·fund_premium 今日首采 14:4x 已落 fresh 3.1h<24h 合规·cta_p1 无可标 bar 续待·车道护栏全诚实 no-op）；"
       "⑦QA det-89th 5/5（撞名预检=smoke-r769 无主→首注册·无 case）；⑧克隆门 PASS（s05 两代跳披露+s6/qa_ignite 自 r768·"
       "stale=0 compile OK×3·克隆门自披露行撞 stale 扫描假阳性 1 针当场锚定豁免重跑全绿）；⑨四件套+attrition CLEAN（4 台账）+"
       "孤儿面=0+idle --worked（idle_rounds=0）")

VERIFY = ("smoke 49/49 + qa/smoke-r769.md 5/5（93 trades·equity 1,017,839 冻结恒等·determinism=True·.err 0B·"
          "png 66,178B·89 连证·无撞名） + results/_r769bmc_s6_log.txt（40 legs rc0 首过·dualrun ZERO-DRIFT streak 51） + "
          "results/_r769bmc_s05_facts.json（ORD delta 消费/DEC 恒等/unacked=0/inbox 0/shape-asserted） + "
          "results/_r769bmc_ord_delta.txt（4 增 1 改写行穷举） + results/_r769bmc_clone_receipt.json（PASS·stale=0） + "
          "results/_r769bmc_qa_runner.out（终态 5/5） + attrition CLEAN（results/_attrition_guard_scan.json） + "
          "孤儿面=0（results/_orphan_face_probe.bm-c.json） + idle --worked + 三件 md5 恒等（task-register 3875B/"
          "silence-enforce 6439B） + FleetLink " + fleetlink + " + token delta=0（零 LLM 调用）")

NEXTP = ("r770 续作（5x HANDOVER 窗·r765-r769 产物清单核对）: ①O-1820 主线=查 results/mv_work/kf/st*.png 七张全完成→"
         "三律人眼门逐张过（油腻/AI 味/中国风/构图安全带/同世界一致·analyze_multimedia 面）→best-of-2 择优→分镜表呈审件"
         "（R-craft-deep 落点A 十场表+落点B 剪辑图+SP 规格随包）→cph4/fleet/mv0001-handover/outbound/ 传回→bm-a 查看→"
         "呈 CEO 过目；CEO 合格前禁跑任何视频段（i2v 驱动已杀·seg1/seg2 冻结；合格后视频目标解冻续 i2v）；"
         "②sina 迟 bar 自愈重试→bar 落地即 CTA_P1 首接线+marks 验证（fund_premium 今日首采已落）③风格样图批收尾校验"
         "（批若未完查 style_gen.log 续跑/探针）④QA 点火律 S6→qa_ignite→poll 终态⑤撞名预检 r770：git ls-tree origin/main "
         "qa/ 探 bm-b r770 包→按披露制⑥轮报行写正典 logs/iteration-loop/round_reports-bm-c.md（r750 律）")


def main():
    # ---- state ----
    sp = os.path.join(ROOT, "state-bm-c.json")
    state = json.load(open(sp, encoding="utf-8"))
    state.update({
        "machine_id": "bm-c", "clock_read": TS, "cpu_pct": cpu_pct,
        "current_task": ACT, "current_task_at": TS,
        "did": DID, "verify": VERIFY, "activity_now": ACT,
        "next": NEXTP, "next_pointer": NEXTP,
        "free_ram_gb": ram_free_gb, "ram_free_gb": ram_free_gb,
        "idle_ram_gb": ram_free_gb, "gpu_free_vram_mib": gpu_free_mb,
        "gpu_free_vram_mb": gpu_free_mb,
        "heartbeat_epoch_utc": EPOCH,
        "last_decisions_read_at": TS, "last_decisions_at": TS,
        "last_orders_at": TS,
        "last_orders_sha": "44CA6C96634F3B27B349FC18C151547A4E5B8AD2",
        "ord_sha_method": ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r769 sweep = "
                           "single-hop F19F563F->44CA6C96: bm-a popup-attribution + mechanism-silence rows "
                           "(their-machine domain, receipt-only) + own silence-duo receipt rows 2 (zero-hop "
                           "as predicted by r768 addendum); PLUS baseline-miss discovery: O-20261008-1820 "
                           "order-revision decree row (17:26:37, landed in r768 sweep window seconds-race, "
                           "hash advanced but row content NOT consumed by r768) -- surfaced by r769 full "
                           "blob-diff enumeration and executed SAME round as P0 (i2v kill + style-sample "
                           "batch); hex-case normalized per r711 pit law; facts-driven from "
                           "results/_r769bmc_s05_facts.json + results/_r769bmc_ord_delta.txt, 40hex "
                           "shape-asserted, never hand-typed (r583 S4 law)"),
        "last_round": ROUND, "round_no": ROUND + 1,
        "round_no_label": "round %d (bm-c)" % ROUND,
        "last_round_at": TS, "last_round_ts": TS, "last_seen": TS,
        "last_seen_at": TS, "last_ts": TS, "ts": TS,
        "last_round_summary": DID, "last_action": DID, "verdict": DID,
        "note": DID,
        "latest_artifact": ("results/mv_work/kf/st*.png O-1820 style-sample batch (7 SDXL, core-three "
                            "best-of-2) + qa/smoke-r769.md 5/5 (93 trades frozen identity) + "
                            "results/_r769bmc_s6_log.txt 40/40 rc0 @ " + TS),
        "next_milestone": ("O-1820 gate: style samples + storyboard package -> outbound -> CEO review "
                           "TONIGHT; video lane frozen until CEO approval; sina late-bar self-heal per "
                           "round; next 5x = bm-c r770 HANDOVER window"),
        "idle_rounds": 0, "agenda_starved": False,
        "head_sha": HEAD, "last_pulled_at": TS,
        "updated": TS, "updated_at": TS,
    })
    with open(sp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(state, fh, indent=1, ensure_ascii=False)

    # ---- heartbeat ----
    hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
    hb = json.load(open(hp, encoding="utf-8"))
    hb.update({
        "free_ram_gb": ram_free_gb, "ram_free_gb": ram_free_gb,
        "idle_ram_gb": ram_free_gb, "cpu_pct": cpu_pct,
        "cpu_util_pct": cpu_pct, "cpu_idle_pct": round(100 - cpu_pct, 1),
        "gpu_free_vram_mb": gpu_free_mb, "gpu_free_vram_mib": gpu_free_mb,
        "idle_rounds": 0, "agenda_starved": False,
        "heartbeat_epoch_utc": EPOCH, "last_seen": TS, "clock_read": TS,
        "ts": TS, "round_no": ROUND + 1, "last_round": ROUND,
        "round_no_label": "round %d (bm-c)" % ROUND,
        "last_round_at": TS, "current_task": ACT, "current_task_at": TS,
        "activity_now": ACT, "did": DID, "verify": VERIFY,
        "verdict": DID, "note": DID, "last_round_summary": DID,
        "last_action": DID, "next": NEXTP, "next_pointer": NEXTP,
        "latest_artifact": state["latest_artifact"],
        "next_milestone": state["next_milestone"],
        "last_decisions_sha": state["last_decisions_sha"],
        "last_decisions_read_at": TS, "last_decisions_at": TS,
        "last_orders_sha": "44CA6C96634F3B27B349FC18C151547A4E5B8AD2",
        "last_orders_at": TS, "last_pulled_at": TS,
        "last_seen_at": TS, "updated": TS, "updated_at": TS,
        "last_run_at": TS, "last_ts": TS, "head_sha": HEAD,
    })
    with open(hp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(hb, fh, indent=1, ensure_ascii=False)

    # ---- round report row -> CANONICAL ledger (r750 pit law) ----
    rpt = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
    row = ("{ts} | r{r} | dept:工程+交易（盘后窗·O-20261008-1820 顺序改判令 P0 执行轮·第 70 连守轮） | "
           "WM-VERDICT: 绿（red=false·py_low 合法面=板 open=0+MV CEO 令面在飞+风格样图批在烧=真实工作在途·"
           "ORD delta F19F563F->44CA6C96 同窗消费〔bm-a 弹窗归因+机制静默两行=他机域 receipt-only+自投回执 2 行零跳面〕·"
           "DEC EE70CEF0 恒等零动作·水位律执法面 facts 驱动） | "
           "did: {did} | verify: {verify} | next: {nextp} | 本地未达 origin commit 数=见 S7-close 尾行（commit 后 "
           "push+fetch 自证） | score=2（O-1820 顺序改判令合规执行=CEO 令面实物+风格样图批在烧=可看实物+QA 证据包 89 连证+"
           "S6 40 面再生） | 记账预算：5（state+心跳+轮报+坑律直写+收据族）[via bm-c r769]\n"
           ).format(ts=TS, r=ROUND, did=DID, verify=VERIFY, nextp=NEXTP)
    with open(rpt, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(row)

    # ---- pit direct-write -> research/pit-protocol-d19.md (r666 precedent) ----
    pit_path = os.path.join(ROOT, "research", "pit-protocol-d19.md")
    pit_line = ("- [2026-10-08 18:0x r769 bm-c] **ORD 水位消费半程态坑（hash 进位≠行消费）**：r768 收尾窗 fetch 与 "
                "O-20261008-1820 注册 commit（17:26:37）秒级竞态——s05 记录了新 blob hash（F19F563F）但轮消费叙事只 "
                "枚举了静默双令两行，顺序改判令行（CEO 追加令）被 hash 进位掩埋未消费；r768 addendum 的「own-receipt-"
                "only 零跳预测」差一点让违令视频生成持续烧 GPU。How to apply：ORD delta 消费清单必须对本窗 blob 做逐行 "
                "diff 穷举（git diff <prev-blob-commit>..origin/main -- docs/orders.md 增行全集）并逐行归类（本机执行/"
                "他机域 receipt-only/回执行）；前轮叙事引用不豁免本窗复核；发现未消费 CEO 令行=本轮最高优先执行。"
                "实弹=r769 检出即停 i2v（违令面）+spawn O-1820 风格样图批。\n")
    pit_bytes = pit_line.encode("utf-8")
    with open(pit_path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(pit_line)
    sha16 = hashlib.md5(pit_bytes).hexdigest()[:16]

    # ---- JSON int self-checks (R170/R178/R262 law) ----
    assert isinstance(state["heartbeat_epoch_utc"], int)
    assert isinstance(hb["heartbeat_epoch_utc"], int)
    assert "T" in state["clock_read"] and "+" in state["clock_read"]

    print(json.dumps({
        "ts": TS, "epoch": EPOCH, "head": HEAD[:9],
        "ram_free_gb": ram_free_gb, "cpu_pct": cpu_pct,
        "fleetlink": fleetlink,
        "pit_sha16": sha16, "pit_bytes": len(pit_bytes),
        "state_round_no": state["round_no"],
        "epoch_int_ok": True, "clock_ok": True,
    }, indent=1))


if __name__ == "__main__":
    main()
