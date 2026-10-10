# r825 bm-b: S7 closeout triple -- state.json + heartbeat + round report
# line. Discipline: load-modify-save (r818 no-retyping law, orders_ack list
# verbatim untouched); round report tail append in bytes mode (r641).
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
EPOCH = int(time.time())

DID = ("r825: P3-E4 OMO liquidity indicator survey negative-closed at data-"
       "source layer (probe scripts/omo_liquidity_probe.py selftest 16/16 "
       "+ evidence results/omo_liquidity_probe.json + survey research/"
       "shortline/OMO_LIQUIDITY_DATA_FEASIBILITY.md; akshare 1141 names x17 "
       "keywords zero OMO daily net-injection face; monthly stock faces "
       "alive [PBOC balance sheet 356 months]; daily price faces fresh "
       "[repo_rate_query FR007 747 rows 1d fresh]; FR007xGC007 same-day "
       "Pearson r=0.869 over 728 overlap days = descriptive linkage "
       "evidence for REPO_PANEL consumer); post_review T-81 stale-criteria "
       "pin P0 fix (r817 v1.1 addendum moved file sha16, criteria pin "
       "left behind -> false NO; canonical r638-family repair: candidate-"
       "blob 3-way anchor [fa0126893 matched old pin] + idempotent repoint "
       "shared+bm-b criteria + re-derive 45 YES/0 NO/5 WAIT all green + "
       "receipt results/_r825bmb_pr_pinfix.json); pit-ps direct-write +1 "
       "(PS 2>&1 stderr-merge pipeline false-fail face 1010B); S6 37 legs "
       "rc0 (Saturday quad legally skipped, panel cutoff 2026-10-09; "
       "dualrun ZERO-DRIFT streak 10); smoke 49/49; orders 60/60 both "
       "sweeps zero unacked; DEC/ORD both MATCH (one method self-correction"
       ": git blob sha vs raw-content sha1 false delta, canonical probe "
       "re-check healed); attrition CLEAN; orphans=0; 5x HANDOVER r821-825 "
       "row landed")

VERDICT = ("r825: research round - P3-E4 OMO liquidity face survey closed "
           "negative at source layer + positive descriptive side-product "
           "(FR007xGC007 r=0.869, 728 days); post_review stale pin P0 "
           "repaired to 45Y/0N/5W; smoke 49/49; S6 37 legs rc0 ZERO-DRIFT "
           "streak 10; watermark red=false healthy; orders 60/60 zero "
           "unacked both sweeps; DEC/ORD hash MATCH both keys; attrition "
           "CLEAN; orphans=0")

TASK = ("P3 explore E6 head ready for r826 claim (micro-cap quant factor "
        "external-source scan; check same-day new CEO orders before "
        "claiming); waiting: W17-JUDGE drain (bm-c lane) -> W18 drafting "
        "window / Monday 10-12 09:15 minute_feed first gated run backfills "
        "10-08/10-09")

NEXT = ("r826: P3 explore E6 head (micro-cap quant factor external-source "
        "scan, survey-first, check same-day new CEO orders before claiming)"
        "; waiting: W17-JUDGE drain (bm-c lane) -> W18 drafting window; "
        "Monday 2026-10-12 09:15 minute_feed first gated run backfills "
        "10-08/10-09")

NOW_ACTIVE = ("r825: P3-E4 OMO survey negative-closed + post_review pin P0 "
              "fix + S6 37 legs + 5x HANDOVER (fleet integration steady)")
LATEST_ARTIFACT = ("r825: scripts/omo_liquidity_probe.py + research/"
                   "shortline/OMO_LIQUIDITY_DATA_FEASIBILITY.md + results/"
                   "omo_liquidity_probe.json + pinfix receipt results/"
                   "_r825bmb_pr_pinfix.json, 2026-10-10 09:0x")
NEXT_MILESTONE = ("r826+: P3 E6 head (micro-cap factor external scan, "
                  "<=48h) / Monday 2026-10-12 09:15 minute_feed gated "
                  "backfill 10-08/09 / W18 drafting once W17-JUDGE drains")

REPORT_LINE = (
    "2026-10-10T09:05:30+08:00 | r825 bm-b | dept:研究（P3-E4 央行 OMO 流动"
    "性指标面调研·流量面判负收口+价格联动正向副产出）+dept:工程（post_review "
    "陈旧 pin P0 修复） | CEO three-line: 当前活=r825 E4 判负收口+post_review "
    "P0 修复+S6 37 腿；最近实物=scripts/omo_liquidity_probe.py+research/"
    "shortline/OMO_LIQUIDITY_DATA_FEASIBILITY.md+results/omo_liquidity_probe."
    "json（2026-10-10 09:0x）；下个里程碑=P3 E6 队头调研 ≤48h+周一 10-12 09:15 "
    "minute_feed 回补 | WM-VERDICT: 绿（red=false·lane healthy·probe verdict="
    "insufficient_history 观察态·周六值 pool0/board0/bandit0 全空=合法白名单；"
    "compute_audit flags=supply_gap+ignition_sla=W17 分片 bm-c 车道非本机违例如"
    "实披露） | 孤儿面=0（probe 7 py faces 0 orphans） | ①S0-1 锚定 bm-b；S0 本地="
    "origin tip 零 pull 需求（085a293f7==ls-remote 实证·脏面=own daemon+post-push "
    "心跳 8 件良性轮末吸收）；②S0.5 双扫 CLEAN（orders 60/184 acks unacked=[]+"
    "D-19 正典探针 DEC a3ea37bd/ORD e286f842 双 MATCH 零新令零新决策——方法面自"
    "纠一次：本人首查误用 git blob sha 比对水位=口径错配假 delta（5811bc40 vs "
    "a3ea37bd），正典探针〔原文 sha1〕复核双 MATCH 治愈零动作）；③S1 smoke "
    "49/49；S2 job_list 0+fleet 票 open=0+tech 队列 0（r946 收口后空置如实）→"
    "P3 队头 E4 认领（领队头前核当日新 O 令=零新令·域现行法核=O-20261009-1105 "
    "期权死令不涉 OMO 域·M1 资金面季节/在飞族零冲突对账）；饱和引擎活 rc0 idle；"
    "④P0 产品=**P3-E4 央行 OMO 流动性指标面调研**：探针 scripts/omo_liquidity_"
    "probe.py（45s 超时夹克+2.5s 限速+getattr 守卫+签名感知调用+ASCII \\u 转义律"
    "+inventory 全库清点+净投放列检测+GC007 价格联动读出+selftest 16/16〔三处自"
    "写新码缺陷当窗自纠：B2 预算哨 break/continue 极性坑·linkage pearson 表达式 "
    "bug·L15 测试数据恒基差 std=0 假败〕）+证据 results/omo_liquidity_probe.json"
    "（13 端点 8 可达 3 MISSING 2 FAIL）+判读件 research/shortline/"
    "OMO_LIQUIDITY_DATA_FEASIBILITY.md；测量结论=**akshare 1.18.96 无 OMO 日频"
    "净投放流量面**（1141 函数名×17 关键词全库清点零命中+三显式名 MISSING+8 可"
    "达面零净投放列→日频净投放车道 via akshare 不可立=E3 北向同族数据源层判负）；"
    "月度存量面可达（央行资产负债表 356 月 1993.3→2026.8·对其他存款性公司债权="
    "政策工具存量·滞后 ~6 周=慢速状态分类候选）；日频价格面新鲜可达（repo_rate_"
    "query FR001/007/014 定盘 747 行至 2026-10-09·shibor_all 2380 行·lpr 1576 行）"
    "；**FR007×GC007 同日 Pearson r=0.869（728 重叠日·基差 +0.0305pp·std "
    "0.2229pp）=银行间→交易所利率传导紧密描述性证据**（REPO_PANEL 消费面·零判据"
    "零 prereg 零面板写零引擎）；死面如实（repo_rate_hist 17 行死窗/"
    "macro_bank_china_interest_rate 止 2019/swap_rate 形状故障/rate_interbank "
    "CJK 参数不匹配=5 分钟级小活候选）；explore.md E4→done+消耗记录行（P3 9→8·"
    "E6 队头）；⑤post_review T-81 陈旧 pin P0 修复（r817 LANDING_HOOKS_P1 v1.1 "
    "增补〔2be696154·v1.0 三族判线零触碰〕后 criteria 钉值 150ce7a7c54cbc19 未"
    "随迁=每跑假 NO〔本窗 09:02 第 7 例 NO〕→r638 stale-criteria repair 同族正"
    "典修法：候选 blob 三连验锚〔fa0126893 命中旧 pin=冻结后合法回填态〕+幂等 "
    "repoint 双 criteria 件〔共享+bm-b·bm-a/c 属主文件不动〕+重 derive **45 YES/"
    "0 NO/5 WAIT 全绿**+回执 results/_r825bmb_pr_pinfix.json）；⑥pit-ps 域直写 "
    "1 条（PS 2>&1 stderr 合流管道假败面 1010B md5 f46e1e85517682f0bb35a1bc"
    "f64e1133·r817 管道截杀坑姊妹面·r666 直写范式·helper results/"
    "_r825bmb_pit_append.py）；⑦S6 37 腿全 rc0（part1 17+part2 20·逐腿 rc 落"
    "日志 _r825bmb_s6_log.txt〔part1 撞 r559 UTF-16 混编坑=字节 regex 提取治愈"
    "·如实披露〕+_r825bmb_s6p2_log.txt；周六 quad〔live.paper/t35_open_fill_"
    "verify/t24_prospect_paper/t24_prospect_promotion〕无新 bar 合法跳过〔面板 "
    "cutoff 2026-10-09 双 no-op 证据〕；dualrun ZERO-DRIFT streak 10；thermo+"
    "DUALARM-2026-09-30 再生；REPORT/LIVE-2026-10-10 再生落 CEO 面；token "
    "delta=0）；⑧S7 四件套绿（loop pin=2 no-op+watchdog 重注册 09:04+双爪重装 "
    "MATCH）+attrition 4 台账 CLEAN（3 healed 注记照录）+idle_trigger --worked"
    "（idle_rounds 0·agenda_starved false）+post_review 重 derive 全绿；⑨5x "
    "HANDOVER 义务兑现（r825=5 倍数：research/HANDOVER.md r821-r825 五轮增量窗"
    "行落账·E1-E4 四调研件+四探针产物清单漂移+维护面链+指针） | 等待态一行声明"
    "：W17-JUDGE drain=bm-c 车道在飞→W18 起草窗；周一 10-12 09:15 minute_feed "
    "首 gated 轮回补 10-08/10-09 | 验证证据: smoke 49/49+omo_probe selftest "
    "16/16+live 13 端点证据件+S6 37 legs rc0 逐腿核销+post_review 45Y/0N/5W 重 "
    "derive+pinfix 回执+dualrun streak 10+attrition CLEAN+双扫零未回执+心跳 "
    "epoch int 自证 | 记分: 2（E4=能跑〔探针+selftest〕能看〔判读件+证据 JSON〕"
    "能用〔explore 消耗+未来产线决策输入〕实物）| 记账预算: 5/5（state+心跳+轮"
    "报+explore 消耗行+HANDOVER 5x〔五轮摊销〕；pit-ps 直写=S4 知识件·criteria "
    "pinfix=工程修复面·如实分列）| 宝藏捕获: 零新方法零新宝藏（E4=cb_data_probe"
    " r821 范式复用非新法）| unacked_orders=0 | 本地未达 origin commit 数：0"
    "（commit 后 push+fetch+rev-list 自证）| 下轮指针: r826: ①P3 explore E6 队"
    "头（微盘股量化因子外源扫描·调研先行·领队头前查当日新 O 令面）②tech 队列空"
    "=如实空置③W17-JUDGE drain 观察→W18 起草窗④周一 2026-10-12 09:15 "
    "minute_feed 首 gated 轮回补 10-08/10-09\n")


def update_state():
    p = os.path.join(ROOT, "state.json")
    d = json.load(open(p, encoding="utf-8"))
    d["machine_id"] = "bm-b"
    d["round_no"] = 825
    d["round_no_label"] = "r825"
    d["did"] = DID
    d["verdict"] = VERDICT
    d["current_task"] = TASK
    d["task"] = TASK
    d["next"] = NEXT
    d["now_active"] = NOW_ACTIVE
    d["latest_artifact"] = LATEST_ARTIFACT
    d["next_milestone"] = NEXT_MILESTONE
    d["last_action"] = ("r825: E4 OMO survey negative-closed + FR007xGC007 "
                        "r=0.869 descriptive linkage + post_review pin P0 "
                        "fix (45Y/0N) + S6 37 legs rc0 + S7 quartet green + "
                        "5x HANDOVER landed + attrition CLEAN")
    for k in ("last_round_at", "ts", "updated", "last_seen", "updated_at",
              "last_round_ts", "clock_read"):
        d[k] = NOW
    d["last_decisions_read_at"] = NOW
    d["last_orders_read_at"] = NOW
    d["round"] = 824  # trailing legacy mirror of previous round, keep law
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False,
              indent=1)
    print("state.json round_no=%d epoch-checked" % d["round_no"])


def update_heartbeat():
    p = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d.get("machine_id") == "bm-b"
    ack_before = len(d.get("orders_ack", []))
    d["round_no"] = 825
    d["round"] = 824
    d["last_seen"] = NOW
    d["ts"] = NOW
    d["clock_read"] = NOW
    d["updated"] = NOW
    d["updated_at"] = NOW
    d["last_round_at"] = NOW
    d["heartbeat_epoch_utc"] = EPOCH
    d["verdict"] = VERDICT
    d["current_task"] = TASK
    d["task"] = TASK
    d["now_active"] = NOW_ACTIVE
    d["latest_artifact"] = LATEST_ARTIFACT
    d["next_milestone"] = NEXT_MILESTONE
    d["last_action"] = d["last_action"]  # keep, refreshed below
    d["last_action"] = ("r825: E4 OMO survey negative-closed (r=0.869 "
                        "descriptive linkage side-product) + post_review "
                        "pin P0 fix 45Y/0N + S6 37 legs rc0 streak 10 + "
                        "5x HANDOVER landed")
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["cpu_cores"] = 16
    d["free_ram_gb"] = 10.5
    d["gpu_free_vram_mb"] = 3459
    d["gpu_free_vram_gb"] = round(3459 / 1024.0, 2)
    d["orphan_faces"] = 0
    d["orphan_face_note"] = "r825: orphan probe 7 py faces, 0 orphans"
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False,
              indent=1)
    back = json.load(open(p, encoding="utf-8"))
    assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int"
    assert len(back.get("orders_ack", [])) == ack_before, "orders_ack drift!"
    print("heartbeat ok epoch=%d acks=%d untouched" %
          (back["heartbeat_epoch_utc"], ack_before))


def append_report():
    p = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
    b = open(p, "rb").read()
    if not b.endswith(b"\n"):
        b += b"\n"
    n = b.count(REPORT_LINE[:40].encode("utf-8"))
    assert n == 0, "report line already present"
    open(p, "wb").write(b + REPORT_LINE.encode("utf-8"))
    print("round report line appended (%d B)" % len(REPORT_LINE.encode()))


if __name__ == "__main__":
    update_state()
    update_heartbeat()
    append_report()
