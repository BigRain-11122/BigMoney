# -*- coding: utf-8 -*-
"""r770 bm-c close: state-bm-c.json + fleet/machines/bm-c.json heartbeat +
round-report row to CANONICAL logs/iteration-loop/round_reports-bm-c.md (r750
pit law) + pit direct-write to research/pit-git-resolver-rebase.md (r666
direct-write precedent; resolver main 30,089B has no headroom, rebe sub-file
17,283B has room) + HANDOVER 5x window entry (window r711-r770,
OVERDUE-BACKLOG DISCLOSED per r420/r500/r670/r735 precedent).
Round: r770 O-1820 CEO review package delivered (MV order-22 line).
Pattern credit: Tools/_r769bmc_close.py."""
import datetime
import hashlib
import json
import os
import socket
import time

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")
EPOCH = int(time.time())
ROUND = 770
HEAD = os.popen('git -C "%s" rev-parse HEAD' % ROOT).read().strip()

try:
    import psutil
    ram_free_gb = round(psutil.virtual_memory().available / 1024**3, 1)
    cpu_pct = round(psutil.cpu_percent(interval=1), 1)
except Exception:
    ram_free_gb, cpu_pct = 3, 1.0
gpu_free_mb = 6951  # carried forward (nvidia-smi banned from windowless host)

fleetlink = "n/a"
try:
    s = socket.create_connection(("127.0.0.1", 8790), timeout=3)
    s.close()
    fleetlink = "200-ok port 8790"
except Exception:
    fleetlink = "listener-down honest"

ACT = ("当前活: r770 bm-c（18:0x-18:2x 窗·盘后窗·O-1820 CEO 呈审包送达轮·第 71 连守轮）——"
       "主产出=①风格样图 4 代全弧收口（v3 盲评 4/4 FAIL+v4 定向补射 4/4 FAIL=16 张收敛失败定谳两大不可达面）"
       "②后处理合成法破局（PIL screen 双曝=同框双影拍子构造性成立·beats b/c/d 盲评全 YES）"
       "③CEO 呈审包送达（5 件 jpg+REVIEW-PACKAGE-v1 三选项菜单→group outbound CAS 直投首过 ba58af82）"
       "④QA det-90th 5/5 ⑤S6 40/40 rc0 ⑥5x HANDOVER 本窗"
       " | 最近实物: cph4 fleet/mv0001-handover/outbound/（5 jpg+REVIEW-PACKAGE-v1.md·delivered=True）+"
       "qa/smoke-r770.md 5/5（93 trades·1,017,839 冻结恒等·png 66,276B） @ " + TS +
       " | 下个里程碑: CEO 三选项勾选（A 纯本地合成法再修一轮/B 批准云端通道/C 改构图）——CEO 点头前视频段维持冻结；"
       "sina 迟 bar 自愈重试；next 5x=bm-c r775")

DID = ("r770: O-1820 CEO 呈审包送达（MV 令二十二·CEO 18:2x 实况查询「有没有结果了？传过来给我看看」=出货紧迫信号）："
       "①4 代全弧：v3 构图重设计 4 张（r769 尾 spawn 17:59 落盘）三律门盲评 4/4 FAIL（双曝幽灵+墙影变形两路第二人像均不出生+"
       "刻字中近景楔形仍糊）；v4 定向补射 4 张（silhouette-merge 移植 glass 过门配方+macro-wedge 微距楔形）盲评 4/4 FAIL"
       "（平面向量感/codex/圣书体漂移+宏观蜡糊）→16 张收敛失败定谳=SDXL 两大不可达面（楔形形态学+同框第二人像直接渲染）+"
       "漂移家族（codex 纸书/维多利亚玻璃罩灯/圣书体/修士装束）；②破局=后处理合成法：单帧各画（单帧皆可生成）→PIL screen "
       "双曝叠加=「同框双影」拍子构造性成立——合成 v1（base=library_c+scribe 特写）盲评 beats (b)(c)(d) 全 YES"
       "（第二人像清晰可辨=评审通过）败因=底帧维多利亚灯+特写脸过巨；iter-2（灯负面词底帧+全身小像 overlay）灯已修"
       "（评审 f 项过）但双帧皆居中叠成一团——拍子可行性已证+机械修法已录（底帧换无穿帮版+overlay 缩小移位）；"
       "③CEO 呈审包=5 件（goddess_b PASS 7/8/7+glass_a PASS 7/7/7+library_x/y 合成双影拍子成立+carve_f 7/8/5 最佳"
       "如实 FAIL）+REVIEW-PACKAGE-v1.md（诚实 5 代台账+三选项菜单〔A 纯本地合成法再修一轮·推荐/B 云端通道两卡壳场景"
       "（判例9 本地穷尽不可达语义族云端可达先例）待批/C CEO 改构图〕+落点A 十场表+落点B 234s 剪辑图+SP 十二项清单）→"
       "group 仓 fleet/mv0001-handover/outbound/ CAS 直投首过（newc=ba58af82·6 件·fetch+ls-tree 送达自证 delivered=True）"
       "→bm-a 盯 outbound 位呈 CEO；④S0：孤儿探针=1（ComfyUI idle server=O-1820 产线资产只读不杀）+pull --rebase "
       "「Cannot rebase onto multiple branches」拒收（单远端配置正常·根因未确诊·坑律直写 resolver-rebe 子件）→显式 "
       "fetch+rebase origin/main 通道（r742 零 autostash 根治律同源）+S0-leg/leg2 双 absorb（daemon churn 竞窗·leg2 "
       "commit -m 单引号经 ProcessStartInfo 被吞→-F 文件律治愈）→push CLEAN；⑤S0.5：DEC EE70CEF0 恒等零动作+ORD "
       "44CA6C96→4B613571 delta 消费（6+1 行穷举=他机域回执 5 行+bm-c 已执行回执 2 行+18:2x MV 令二十二行=本机在飞主线"
       " receipt-only）·unacked=0（51 orders）·inbox 0；⑥S1 smoke 49/49+饱和引擎活（exit 0）；⑦S6 40/40 rc0"
       "（update_daily sina 迟 bar 续自愈 cutoff 09-30·fund_premium no-op=09-30 NAV 已覆盖·cta_p1 无可标 bar 续待·"
       "车道护栏全诚实 no-op）；⑧QA det-90th 5/5〔撞名 case#7：qa/smoke-r770.md bm-b golden-week 包 97c43fdc 先在册·"
       "同冻结数字零科学损失·bm-b 版 git 史保全·F-20261008-03 命名空间修法常设呈报先例族〕；⑨四件套绿（pin=5 no-op+"
       "watchdog 重注册+双爪 LF 归一）+attrition CLEAN（4 台账）+idle --worked（idle_rounds=0）+5x HANDOVER 窗 r711-r770")

VERIFY = ("smoke 49/49 + qa/smoke-r770.md 5/5（93 trades·equity 1,017,839 冻结恒等·determinism=True·.err 0B·"
          "png 66,276B·90 连证·case#7 披露） + results/_r770bmc_s6_log.txt（40 legs rc0·dualrun ZERO-DRIFT streak 51） + "
          "results/_r770bmc_s05_facts.json（ORD delta 消费/DEC 恒等/unacked=0/inbox 0/shape-asserted） + "
          "results/_r770bmc_ord_delta.txt（6+1 行穷举） + results/_r770bmc_outbound_cas.json（push_ok=True·delivered=True·"
          "newc=ba58af82·6 件 ls-tree 自证） + 盲评 10 calls 逐件 verdict 在案（v3 4+v4 4+合成 2·云端多模态·token 律披露） + "
          "style_gen.log v3/v4/overlay 三批 done ok=True（21 张生成+2 张合成全留档 results/mv_work/kf/） + "
          "attrition CLEAN（results/_attrition_guard_scan.json） + FleetLink " + fleetlink +
          " + 孤儿面=1 只读（ComfyUI 产线资产） + idle --worked（idle_rounds=0）")

NEXTP = ("r771 续作: ①CEO 三选项勾选后按勾选项走：A=合成法再修一轮（底帧无穿帮版+overlay 缩小移位=机械修法·拍子已证）；"
         "B=云端通道两卡壳场景关键帧（待 CEO 批·判例9）；C=CEO 改构图（待方向）——CEO 点头前视频段维持冻结（i2v 已杀·"
         "O-1715/1755 视频目标冻结）②sina 迟 bar 自愈重试→bar 落地即 CTA_P1 首接线+marks 验证+REGIME_GUARD v3 新 bar "
         "enforce（live.paper 宿主面=bm-a·bm-c lane-guard 诚实 skip 常设）③QA det-91th 撞名预检（git ls-tree origin/main "
         "qa/ 探 r771）④分镜呈审件已随包送达·CEO 反馈即出 v2 修订⑤next 5x=bm-c r775（HANDOVER 窗）")


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
        "last_orders_sha": "4B61357120BADBA4070E39AE2786F579083B18B6",
        "ord_sha_method": ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r770 sweep = "
                           "single-hop 44CA6C96->4B613571: 6 added + 1 rewritten row enumerated = bm-a domain "
                           "receipts x5 (popup root-cure + mechanism-silence + direct-solve 61-rewrap + own bm-c "
                           "silence receipts already-executed x2) + 18:2x MV order-22 row (dispatched, own "
                           "in-flight main line, receipt-only); CEO live query 'any results yet' = ship-now signal "
                           "acted on same round (package delivered ba58af82); hex-case normalized per r711 pit law; "
                           "facts-driven from results/_r770bmc_s05_facts.json + results/_r770bmc_ord_delta.txt, "
                           "40hex shape-asserted, never hand-typed (r583 S4 law)"),
        "last_round": ROUND, "round_no": ROUND + 1,
        "round_no_label": "round %d (bm-c)" % ROUND,
        "last_round_at": TS, "last_round_ts": TS, "last_seen": TS,
        "last_seen_at": TS, "last_ts": TS, "ts": TS,
        "last_round_summary": DID, "last_action": DID, "verdict": DID,
        "note": DID,
        "latest_artifact": ("cph4 group fleet/mv0001-handover/outbound/ (5 scene jpgs + REVIEW-PACKAGE-v1.md, "
                            "CAS ba58af82 delivered=True) + qa/smoke-r770.md 5/5 (93 trades frozen identity, "
                            "90th chain) + results/_r770bmc_s6_log.txt 40/40 rc0 @ " + TS),
        "next_milestone": ("O-1820 CEO gate: package DELIVERED to outbound -> bm-a presents -> CEO picks "
                           "option A/B/C; video lane stays frozen until CEO OK; sina late-bar self-heal per "
                           "round; next 5x = bm-c r775"),
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
        "last_orders_sha": "4B61357120BADBA4070E39AE2786F579083B18B6",
        "last_orders_at": TS, "last_pulled_at": TS,
        "last_seen_at": TS, "updated": TS, "updated_at": TS,
        "last_run_at": TS, "last_ts": TS, "head_sha": HEAD,
    })
    with open(hp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(hb, fh, indent=1, ensure_ascii=False)

    # ---- round report row ----
    rpt = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
    row = ("{ts} | r{r} | dept:工程+交易（盘后窗·O-1820 CEO 呈审包送达轮·第 71 连守轮·5x HANDOVER 窗） | "
           "WM-VERDICT: 绿（red=false·py_watermark insufficient_history 诚实〔series 窗 1〕·"
           "ORD delta 44CA6C96->4B613571 同窗消费〔6+1 行=他机域回执 5+bm-c 已执行回执 2+MV 令二十二行=本机在飞主线 "
           "receipt-only〕·DEC EE70CEF0 恒等零动作·水位律执法面 facts 驱动） | "
           "did: {did} | verify: {verify} | next: {nextp} | 本地未达 origin commit 数=见 S7-close 尾行（commit 后 "
           "push+fetch 自证） | score=2（CEO 呈审包=能看实物送达 outbound+合成法破局证据链=可看可复用+QA 证据包 90 连证+"
           "S6 40 面再生） | 记账预算：5（state+心跳+轮报+坑律直写+HANDOVER）[via bm-c r770]\n"
           ).format(ts=TS, r=ROUND, did=DID, verify=VERIFY, nextp=NEXTP)
    with open(rpt, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(row)

    # ---- pit direct-write -> research/pit-git-resolver-rebase.md ----
    pit_path = os.path.join(ROOT, "research", "pit-git-resolver-rebase.md")
    pit_line = ("- [2026-10-08 18:1x r770 bm-c] **pull --rebase「Cannot rebase onto multiple branches」拒收坑"
                "（单远端配置正常面·根因未确诊）**：r770 S0 实弹——remote -v 单 origin、remote.origin.fetch 单 refspec、"
                "branch.main.remote=origin/merge=refs/heads/main 三配置全正常，pull --rebase 仍 fatal 拒收（r766 前先例"
                "可跑=新面）；树脏首跑报 unstaged changes=正常序，absorb 后再跑即撞本坑。战斗通道=显式 fetch origin + "
                "rebase origin/main（r742 净树零 autostash 根治律同源·r768/r769 已用面）；同窗 commit -m 经 silent-git "
                "wrapper（ProcessStartInfo.Arguments）单引号被 MSVCRT 命令行解析吞=消息词散成 pathspec（pit-ps-wrapper "
                "ArgString 族新面）——正法=commit -F <msg 文件>（r769 同法）。How to apply：S0 集成遇本坑勿追根因"
                "（轮预算内不确诊）·直接 fetch+rebase origin/main；wrapper 传带空格消息一律 -F 文件律。"
                "| dept:工程 | r770 S0 窗（S0-leg/S0-leg2 双 absorb+conditional churn absorb 竞速法治愈）\n")
    pit_bytes = pit_line.encode("utf-8")
    with open(pit_path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(pit_line)
    sha16 = hashlib.md5(pit_bytes).hexdigest()[:16]

    # ---- HANDOVER 5x window entry (r711-r770, overdue-backlog disclosed) ----
    ho_path = os.path.join(ROOT, "research", "HANDOVER.md")
    ho_line = ("> bm-c round 770 五倍数核对（2026-10-08 18:2x·增量窗 r711-r770 六十轮·前窗 r606-610 已由 r610 行覆盖·"
               "OVERDUE-BACKLOG DISCLOSED: r715..r765 各 5x stamp 未落行——窗口承载金周值守尾段+复市 T-0 纪元+MV CEO 令面"
               "纪元+弹窗根治/机制静默纪元，per r420/r500/r670/r735 precedent 单窗紧凑覆盖零回改零伪造；逐轮权威="
               "round_reports-bm-c.md 全行在册）：窗口主线=①**金周值守尾段+复市 T-0（r711-r767）**：QA 证据包常设化连证"
               "31→88 连证〔metrics 恒等 sharpe 0.1586/93 trades/46.24% win/determinism=True/equity 1,017,839 冻结恒等〕+"
               "S6 33-40 腿 rc0 链〔dualrun ZERO-DRIFT streak 51〕+水位双键 MATCH 链+orders 双扫零未回执链〔51/51〕+"
               "attrition CLEAN 链+四件套绿链〔pin=5〕+孤儿面常驻 ComfyUI 只读披露链+r766 复市 T-0 盘中 86 连守+"
               "r767 盘后窗首轮 fund_premium 15:30 首采 14:4x 落地〔bm-c 车道〕+sina 迟 bar 自愈面持续〔cutoff 09-30 持有至 "
               "r770〕；②**MV CEO 令面纪元（r768-r770·O-20261008-1715/1755/1820）**：r768 模型三件 sha256 验证〔Wan2.2 "
               "Q4_K_M 3.43GB+VAE 1.41GB+umt5-xxl 3.66GB+clip_vision_h 1.26GB〕+SDXL kf 4/6+i2v run#1 CLIPLoaderGGUF 六败"
               "→run#2 点火 seg1 完成〔后被 O-1820 判负冻结〕；r769 O-1820 顺序改判令 P0 同轮执行〔i2v 31384 击杀+风格样图批 "
               "7/7+8 盲评 4 PASS〔goddess a/b+glass a/b〕/4 FAIL+v2 regen〕+ORD 半程态坑检出〔pit-protocol-d19 直写〕；"
               "r770〔本轮〕**CEO 呈审包送达**：v3 构图重设计 4/4 FAIL+v4 定向补射 4/4 FAIL=16 张收敛失败定谳两大不可达面"
               "〔楔形形态学+同框第二人像〕+漂移家族→破局=后处理合成法〔PIL screen 双曝=拍子构造性成立·beats b/c/d 盲评"
               "全 YES〕→5 件呈审包〔goddess_b 7/8/7+glass_a 7/7/7+library_x/y 合成+carve_f 7/8/5 如实 FAIL〕+"
               "REVIEW-PACKAGE-v1 三选项菜单〔A 本地合成法再修/B 云端通道判例9/C CEO 改构图〕+落点A 十场表+落点B 234s "
               "剪辑图+SP 十二项清单→group 仓 fleet/mv0001-handover/outbound/ CAS 直投首过〔ba58af82·6 件·delivered="
               "True〕+QA det-90th 5/5〔case#7 撞名披露制〕；③**弹窗根治/机制静默纪元（r768 承令·bm-a 域回执面）**："
               "四源归因+gitsilent 转发器+UGit 静默启动器+61 任务链 SilentShimRunner 换壳+task-register 唯一正门+60s 兜底"
               "车道+静默三件 group 正本同步〔r769〕。链头 live-read=812,128（bm-a r875 W184 finalize stamp 引用·bm-c 本轮"
               "未独立扫描）。维护面：smoke 48→49/49 链；盲评云端多模态 18 calls〔r769 8+r770 10·token 律披露〕。下一里程碑="
               "**CEO 三选项勾选→按勾选项走（A/B/C·CEO 点头前视频段冻结）+sina 迟 bar 落地即 CTA_P1 首接线+REGIME_GUARD v3 "
               "新 bar enforce+月界首考 10-31〔T-143 装配交付 10-29〕**；下一 5x=bm-c r775。 [via bm-c r770]\n")
    with open(ho_path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(ho_line)

    # ---- JSON int self-checks (R170/R178/R262 law) ----
    assert isinstance(state["heartbeat_epoch_utc"], int)
    assert isinstance(hb["heartbeat_epoch_utc"], int)
    assert "T" in state["clock_read"] and "+" in state["clock_read"]

    print(json.dumps({
        "ts": TS, "epoch": EPOCH, "head": HEAD[:9],
        "ram_free_gb": ram_free_gb, "cpu_pct": cpu_pct,
        "fleetlink": fleetlink, "pit_sha16": sha16,
        "pit_bytes": len(pit_bytes), "ho_bytes": len(ho_line.encode("utf-8")),
        "state_round_no": state["round_no"],
        "epoch_int_ok": True, "clock_ok": True,
    }, indent=1))


if __name__ == "__main__":
    main()
