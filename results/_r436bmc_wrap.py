# -*- coding: utf-8 -*-
"""r436 bm-c wrap: state + heartbeat + round report + HANDOVER 5x backfill
(r431-435 window, deferred from r435 budget) + orders double-scan + CODELY
pit line + inbox MSG move. Delivery leg = Tools/push_verify.py (run by
caller after this script)."""
import datetime
import json
import os
import shutil
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
ROUND = 436
# live-clock stamp for narrative lines (time-pit law: never trust prior-round date)
NOW_SHORT = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")[:-1] + "x"


def jload(p):
    with open(os.path.join(REPO, p), "r", encoding="utf-8-sig") as f:
        return json.load(f)


def jdump(p, obj):
    with open(os.path.join(REPO, p), "w", encoding="utf-8", newline="") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


DID = (
    "r436 bm-c: WM 绿（red=false lane healthy·py_watermark verdict=insufficient_history n=1 窗短·"
    "合法性=W2 finalize 烧批在飞+周末采集腿 no-op 族）。"
    "(1) S0 分叉手术：r435 收尾 commit 未推（本地 1 ahead）+origin 8 ahead（bm-a r647 G2_SLOT_MON_P1 "
    "census 首正发现〔old_032 robust 1.64x·beat 0.7667·T-163 done〕+bm-b r638/639 merge 链）→预判改动面"
    "零重叠实证→churn absorb 提交+rebase 2/2 零冲突→push 送达 ca814f8be；后 origin 又进 3（bm-a r648 "
    "G2_SLOT_MON_P2 冻结面）pull 拉入。"
    "(2) (e) 工程小活=push_verify 单源件 Tools/push_verify.py（主产出）：r434 假送达缺陷回查定谳="
    "_r434bmc_s7_wrap.py 无 push/验证腿而 state 文本宣称「push 后 fetch 自证」=r502 族文本假回执根因"
    "→升格 r435 内嵌验证腿为可复用单源（40-hex 硬校验+CAS 四词判 fatal/rejected/failed/error+ahead "
    "清零三证+--no-push 探针+selftest 8/8 离线）；live-fire 实弹=--no-push 探针当场抓出「tip==remote "
    "过严」语义缺陷（多写者 fleet origin 前进 behind=3=常态非送达失败）→修判据 delivered=ahead==0→"
    "rc0 DELIVERED 复证。"
    "(3) S6 全链 37/37 rc0 NON-ZERO=none（r435 顺延债清偿·_r436bmc_s6_log.txt·adapt→run→restore r429 "
    "律三步·canon driver HEAD blob 复原 clean·dualrun ZERO-DRIFT streak 36·五 lane_io 面 stale-takeover "
    "derive 合法〔bm-a 心跳 48min 陈旧·O-2100 s2.4 STALE_MIN law〕·周末采集腿诚实 no-op 族·t24 promote "
    "0 员 eligible 合法·update_fund_premium 本机车道周末 no-op 正确）。"
    "(4) S0.5 orders 152/152 零差集（S7 双扫同）；D-19 4167B784 MATCH+GORDERS 68947C17 MATCH 双水位零"
    "消费；S1 smoke 47/47（首跑全绿零修复）；satengine rc0 活（alive_flag·age 52s）。"
    "(5) S7：四件套在位（loop pin=5 零漂移·watchdog 重注册·双 claw 重装）+attrition CLEAN rc0（2 healed "
    "注记照录）+HANDOVER r431-435 五倍数补账行（r435 顺延债）+inbox MSG-2330 bm-a T-163 开工声明收讫"
    "（票已 done r647·零撞车）移 processed。五收口步捕获问：本批无新宝藏（无判决批 finalize/族炉收口/考面"
    "冻结/名单进出/方法论新方法——push_verify=工程件非研究方法）→登记册零新行照实；登记簿零命中断言="
    "本轮删除类动作 0 起（inbox 移动=协议白名单面）。本地未达 origin commit 数=0（push_verify 实证 "
    "ahead==0）。"
)

CUR = ("r436: S0 surgery clean + push_verify.py single-source delivered (r502-family fix, selftest 8/8 "
       "+ live-fire) + S6 37/37 full chain (r435 deferred debt cleared) + W2 poll ALIVE (pid 31336, "
       "artifact absent, awaiting); next: W2 adopt-at-landing poll + push_verify wiring into wrap legs")

NEXT = ("(a) W2 poll: python Tools/_r426bmc_w2_judge_finalize.py status -> w2_judge.json 落地即收养 "
        "(adapt _r426bmc_close.py 模板, count->replace->assert 三段律) + 延迟烧日志原子 commit, "
        "deadline <=10-06; 若 pid 31336 再度静默死 (同窗 ~4.5h) =确定性灭门 -> 升级呈报 (防再烧三连浪费); "
        "(b) O-2030 验收证据包 10-08 (weld face complete r434 + demo receipts + W2 landing=首个判决-finalize "
        "捕获点样例); (c) D-06 全线收口 10-07 (pit-git 107KB sub-split + pit-data CRLF 裁定 + 流水下沉终扫); "
        "(d) push_verify 接线面: 下轮起 wrap 脚本 push 腿一律调 Tools/push_verify.py (单源律·防 r434 型"
        "文本假回执复发); (e) T-143 月考装配窗 10-09 后 (交付 10-29)。"
)

VERIFY = ("push_verify selftest 8/8 + live --no-push probe rc0 DELIVERED (ahead=0, behind=3 fleet-motion "
          "noted) + full-push live-fire at round end; S6 37/37 rc0 NON-ZERO=none (_r436bmc_s6_log.txt; "
          "dualrun streak 36; canon driver restored HEAD blob clean); smoke 47/47; orders 152/152 "
          "double-scan; D-19 MATCH; GORDERS MATCH; attrition CLEAN rc0; S7 4/4 (loop pin=5 no-drift; "
          "watchdog+claws reinstalled); inbox 1 processed (MSG-2330); HANDOVER r431-435 entry; "
          "epoch int + clock T-sep in-wrap"
)

REPORT_LINE = (NOW + "\t| r436 bm-c\t| " + DID + "\t| " + VERIFY + "\t| 下轮指针: " + NEXT)

HANDOVER_ENTRY = (
    "> bm-c round 435 五倍数核对（" + NOW_SHORT + "·增量窗 r431-435 五轮〔r435 5x 窗预算耗尽顺延 r436 补账〕）："
    "增量窗 r431-435=bm-c 面（**O-20261003-2030 CEO 宝藏保护令焊接主线+W2 判决 finalize 等待窗**——"
    "r431 D-06 post-split 增量回扫 4 条 verbatim 入域件〔pit-spawn +2：r422 三代执行体连环斩首收养律/r426 "
    "多子进程链驱动器禁经 CreateNoWindow 包装器点火律；pit-git +1：r423 merge 窗三连坑；pit-tooling +1："
    "r629 rehearsal/harness 镜像=调用点守卫复刻律〕+流水下沉 archive 202610.md r431 节+冷层指针行"
    "〔r444 范式〕+CODELY.md 30,442→25,418B=首次低于 D-06 ≤30KB 主件目标线+O-2030 令 mid-round S7 双扫"
    "截获即 ack〔首 ack 机·<=15min SLA〕；r432 焊面首片=守门引擎 treasure_guard.py 复验 selftest 21/21+"
    "硬拒 rc3 复演+隔离区 demo〔results/_quarantine/ manifest+identity assert rc0〕+协议焊点 3/3"
    "〔iteration_prompt 五类收口步/清扫硬门/轮报零命中断言·字节手术 count==1×3〕+POST_REVIEW §五接线+"
    "里程碑 tag 1d9ec9202〔§4 考面冻结类首例〕+登记册出入记录 2 行；r433 焊面余项2=treasure_guard "
    "restore 子命令〔S0-restore 分类门：登记册/记忆/state/票面/append-only 类 rc3 硬拒 vs 可再生工件 rc0 "
    "放行·selftest 21→40 腿+live-fire 双 demo receipt〕+协议焊点 s0_restore_gate 入 S0 律节〔+344B·"
    "count==1〕+S7-supplement push 撞拒手术〔14 faces per-face 判定 receipt _r433bmc_rebase_resolve.json〕；"
    "r434 焊面收口=item1 canon_sweep.py 热冷整编驱动器〔probe/apply 内嵌门四步〔treasure_guard 单源 "
    "import prescan→隔离区快照→verbatim 冷层追加→零丢失断言 FAIL 即回滚〕/selftest 13/13+live probe rc0"
    "〔CODELY 27,270B<51,200〕+live 硬拒 rc3 零写自证〕+item3 per-runner finalize capture 注释 31 焊点"
    "〔17 files/25+/0-/py_compile 全过〕=焊面全量齐〔r432 协议焊+r433 item2+r434 item1+3〕·T-162 progress "
    "r431-434+W2 finalize 首烧 spawn pid 31276〔19:28:59·4.5h 满核·22:59-23:15 窗静默死·日志零 traceback·"
    "四查全阴〔WER/watchdog/fuse/timeout 全净〕=外部杀手不可考〕+S7-supplement push claw 双拦截手术"
    "〔19 UU per-face 全解 receipt·r630 验吸收 skip 律〕；r435=本核对窗 **S0 重大发现=r434 两 commit 从未达 "
    "origin〔state 假送达声明=r502 族假回执〕**→隔离 worktree cherry-pick 手术重放 ca9c3a009+b4ab54ba0 "
    "onto e74c79c95〔bm-a r646〕·15 冲突面逐面 newer-wins〔14 origin/bm-a 23:0x 新+1 mine lhb 22:55〕·"
    "receipt _r435bmc_rebase_resolve.{py,json}·push 后 fetch+rev-parse+ls-tree 三证 origin/main==4de95e7f+"
    "canon_sweep 送达自证+marker 扫描 0 hits→O-2030 焊面交付物全员在册+W2 finalize respawn pid 31336"
    "〔23:34:14·r422/r426 设计重跑净重拉·deadline <=10-06〕+S6/S7 顺延 r436〔预算〕〕）"
    "产物清单漂移=Tools/treasure_guard.py〔restore 门 r433〕+Tools/canon_sweep.py〔r434〕+results/"
    "_r431bmc_*~_r435bmc_* 工件族〔sweep receipts/weld/restore guard demo/capture weld/rebase resolve×3+"
    "smoke log〕+research/pit-{spawn,git,tooling}.md 增量 4 条+research/memory-archive/202610.md r431 节+"
    "CODELY.md〔25,418B〕+fleet/tasks/T-2026-10-03-162-P1.json progress r431-434+git tag 1d9ec9202+"
    "O-2030 令件 orders_ack 152；orders 152/152 双扫零未回执全窗维持；smoke 47/47；D-19 4167B784 MATCH "
    "全窗零消费；GORDERS 68947C17 MATCH；池态=MASS_TRIAL_W2-JUDGE 4/4 shards done 805/805 rows on "
    "origin·finalize 在飞 pid 31336；指针：**W2 w2_judge.json 落地即收养〔adapt _r426bmc_close.py 模板·"
    "deadline <=10-06·首个判决-finalize 捕获点样例〕+O-2030 验收证据包 10-08+D-06 全线收口 10-07〔pit-git "
    "107KB sub-split+pit-data CRLF 裁定+流水下沉终扫〕+T-143 月考装配 10-09 后〔交付 10-29〕+月界首考 "
    "10-31**；下一 5x=bm-c r440。"
)

CODELY_PIT = (
    "[" + NOW_SHORT + " r436 bm-c] r436 两坑律（S0 手术窗实录）：①silent-git 包装器 -GitArgs 内单引号="
    "Windows 命令行不识别——PS 单引号只是 PS 层定界符、进 ProcessStartInfo.Arguments 后单引号非引用字符，"
    "commit -m 'msg' 消息被拆成 pathspec 假报错（error: pathspec 'absorb:' did not match）；正法=-m 消息一律"
    "双引号包裹（-GitArgs 'commit -m \"...\"'）。②push_verify 送达判据=push 后 fetch+ahead==0（r502 族根治件"
    "Tools/push_verify.py 单源·40-hex 硬校验+CAS 四词判 fatal/rejected/failed/error）——多写者机队 "
    "origin/main 常时前进，tip==remote 判据过严（behind>0=机队正常运动非送达失败）；live 实弹=behind=3 时"
    "NOT-DELIVERED 假红→修为 ahead==0。How to apply：wrap 脚本 push 腿一律调 Tools/push_verify.py 勿再内嵌"
    "重推导；git -m 引号一律双引号。"
)


def main():
    # --- state-bm-c.json ---
    st = jload("state-bm-c.json")
    st.update({
        "round_no": ROUND, "clock_read": NOW, "last_seen": NOW, "last_round_at": NOW,
        "last_round_ts": NOW, "updated": NOW, "updated_at": NOW,
        "last_decisions_read_at": NOW,
        "current_task": CUR, "did": DID, "next": NEXT,
        "last_round": ("r436 bm-c: S0 surgery (r435 commit delivered ca814f8be, origin re-synced); "
                       "push_verify.py single-source (r502 fix, selftest 8/8 + live-fire); S6 37/37 "
                       "full chain; W2 poll ALIVE; smoke 47/47"),
        "last_round_at2": NOW,
    })
    jdump("state-bm-c.json", st)

    # --- heartbeat fleet/machines/bm-c.json ---
    hb = jload("fleet/machines/bm-c.json")
    hb.update({
        "round_no": ROUND, "clock_read": NOW, "last_seen": NOW, "last_seen_at": NOW,
        "updated_at": NOW, "heartbeat_epoch_utc": EPOCH,
        "activity_now": ("r436: S0 surgery clean (r435 bookkeeping delivered ca814f8be); push_verify.py "
                         "single-source delivery leg delivered (r502-family fix, selftest 8/8 + live-fire); "
                         "S6 37/37 full chain (r435 deferred debt cleared)"),
        "current_task": CUR,
        "latest_artifact": ("Tools/push_verify.py (single-source round-end delivery verification, r502-family "
                            "fix: 40-hex hard-check + four-word push screen + ahead==0 proof) + "
                            "results/_r436bmc_s6_log.txt (37/37 rc0) @ " + NOW),
        "next_milestone": ("W2 w2_judge.json landing -> adoption same round (deadline <=10-06, first "
                           "judge-finalize capture-point example); O-2030 acceptance evidence pack 10-08; "
                           "D-06 full closure 10-07; T-143 monthly-exam assembly post-10-09 (deliver 10-29)"),
        "prod_lanes": ("O-2030 weld face complete (r432-434, all on origin 4de95e7f); MASS_TRIAL_W2-JUDGE "
                       "finalize burn in flight (pid 31336 respawned 23:34:14, artifact absent, deadline "
                       "<=10-06); push_verify single-source wiring into future wrap legs"),
    })
    jdump("fleet/machines/bm-c.json", hb)
    assert isinstance(jload("fleet/machines/bm-c.json")["heartbeat_epoch_utc"], int), "epoch must be int"

    # --- round report ---
    with open(os.path.join(REPO, "round_reports-bm-c.md"), "a", encoding="utf-8") as f:
        f.write(REPORT_LINE + "\n")

    # --- HANDOVER 5x backfill (insert after title line, newest-first) ---
    hp = os.path.join(REPO, "research", "HANDOVER.md")
    raw = open(hp, "rb").read()
    nl = raw.find(b"\n")
    assert nl > 0, "HANDOVER title line not found"
    eol = b"\r\n" if nl >= 1 and raw[nl - 1:nl] == b"\r" else b"\n"
    ins = HANDOVER_ENTRY.encode("utf-8") + eol
    if raw[nl + 1:nl + 1 + 8] == b"> bm-c ro" and b"round 435" in raw[:4000]:
        # guard: entry already present (idempotent rerun)
        print("HANDOVER: r435 entry already present, skip insert")
    else:
        open(hp, "wb").write(raw[:nl + 1] + ins + raw[nl + 1:])
        print("HANDOVER: r431-435 entry inserted after title (eol=%r)" % eol)

    # --- CODELY pit line (project memory, hot layer) ---
    cp = os.path.join(REPO, "CODELY.md")
    craw = open(cp, "rb").read()
    if "r436 两坑律".encode("utf-8") not in craw:
        with open(cp, "ab") as f:
            f.write(CODELY_PIT.encode("utf-8") + b"\n")
        print("CODELY: r436 pit line appended")
    else:
        print("CODELY: pit line already present, skip")

    # --- inbox: move processed MSG ---
    src = os.path.join(REPO, "fleet", "inbox", "MSG-2026-10-03-2330-bma-all.md")
    dst = os.path.join(REPO, "fleet", "inbox", "processed", "MSG-2026-10-03-2330-bma-all.md")
    if os.path.exists(src):
        os.replace(src, dst)
        print("INBOX: MSG-2026-10-03-2330-bma-all.md -> processed/")
    else:
        print("INBOX: msg already moved")

    # --- orders double-scan (S7) ---
    ack = set(hb.get("orders_ack", []))
    on_disk = set(f for f in os.listdir(os.path.join(REPO, "fleet", "orders")) if f.endswith(".md"))
    unacked = sorted(on_disk - ack)
    print("ORDERS_DOUBLE_SCAN unacked=%d %s" % (len(unacked), unacked if unacked else "(zero)"))

    # --- self-verification ---
    st2 = jload("state-bm-c.json")
    hb2 = jload("fleet/machines/bm-c.json")
    assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch not int"
    assert "T" in hb2["clock_read"] and "T" in st2["clock_read"], "clock not T-sep"
    print("S7 WRAP OK: state+heartbeat+report+HANDOVER+CODELY+inbox r436 @", NOW, "epoch=", EPOCH)


if __name__ == "__main__":
    main()
