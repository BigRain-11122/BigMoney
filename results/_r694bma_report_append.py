"""r694 bm-a: round-report line + CODELY pit-law line append (r679 idempotent
gate: marker count==0 pre-check; UTF-8 append, newline='' per encoding law)."""
import io

RR = "round_reports-bm-a.md"
CODELY = "CODELY.md"

report = (
    "2026-10-04T19:5x+08:00 | r694 (bm-a) | watermark=green (red=false; "
    "satengine alive rc0 queue0 idle; py_watermark py_low_board_clear "
    "golden-week legal board-clear; compute_audit CLEAN v2.4.2 flags=None "
    "pool_ready=5; pool dualrun ZERO-DRIFT streak51 @cutoff 19:43:58) | "
    "当前活: N2-W15 supply 物化第一步落地——GENERATE 池条目入池（席位 "
    "MSG-1943 承接 MSG-1955 下游开放面·F-04 先行）| 最近实物: "
    "results/runnable_pool.json 新条目 PERPETUAL-N2-W15-GENERATE "
    "(377→378·r481 bm-c 入池正法复用=r678 行级手术+reparse+计数+difflib 断言·"
    "diff added=35 removed=2) + results/_r694bma_n2_gen_enroll.json + "
    "fleet/inbox/MSG-2026-10-04-1943-bma-all.md @ 19:4x | 下个里程碑: N2 "
    "generate daemon 烧录→harvest 翻面→screen-prep→12 分片 SCREEN 入池（窗 "
    "≤48h）; W3 judge 产物落地首查（今晚 ~22:3x·CEO 48h 钟）| DONE-1 S0: "
    "daemon lane churn absorb + merge origin 8 commits 零冲突零交集（r437 "
    "merge-over-rebase 律）| DONE-2 S0.5: orders 154/154 双扫零未回执（r477 "
    "全名同形态）+ D-19 MATCH 4e5be321（Tools/d19_check.py 正典实跑·源码律 "
    "已核 r682 后核验）+ inbox MSG-1955 消费归档 | DONE-3 (主产出·N2 GENERATE "
    "入池全链): 冻结态实核（SEED_REGISTRY 三带 import 实读 541500/542000/"
    "542500==冻结 commit 1ff613cbe）+ selftest 17/17 直跑复跑 + RAM 三采样 "
    "58GB 全绿 + candidates 缺席断言（一次性门安全）+ 入池后独立 reparse 复核 "
    "| DONE-4 S1+S6: smoke 48/48 + S6 38/38 rc0 110s（_r694bma_s6_log.txt·"
    "live.paper 黄金周无新 bar 诚实跳过 r660 先例·CEO 面 REPORT/LIVE-20261004 "
    "幂等再生 ORANGE·data gates 黄金周 no-op 族·CALL-2026-09-30 ORANGE_COOL "
    "sleeves4 activated0·token L2 12944+27635）| DONE-5 S7: 自愈 4/4（pin8 "
    "no-op+watchdog 重注册+双 claw LF 归一重装）+ attrition guard CLEAN 4 "
    "台账（healed 3 行照录）+ state 693→694 绝对值写+reparse 自证（首跑崩于 "
    "心跳步重跑双计 695→外科归正 694·fail-closed）+ 心跳 epoch int 1791114567 "
    "自证 clock T 格式 + orders 收尾复扫 154/154 | 记分: 2（可跑/能看实物="
    "GENERATE 池条目=daemon 可烧的活供给+入池证据链+席位 MSG；N2 常供线 "
    "supply_gap 修复·compute_audit 旗清）| 记账预算: 5/5（state+心跳+轮报+"
    "双扫+卫士扫描）| 本地未达 origin commit 数: __PUSH_STAMP__ | 承接判定: "
    "本批无新方法论（入池正法=r481 bm-c 既有配方复用·W2/W13 generate 先例族）"
    "| 宝藏捕获: 无（供给接线非五类收口步）| 坑例捕获: 2 条 CODELY（正则行级"
    "手术 repl 回补 eol 律·5 键连环吃 CRLF 实证；簿记脚本 increment 型重入双计"
    "坑·绝对值写正法）| 下轮指针: (1)W3 judge 产物落地首查 python "
    "results/_r693bma_w3_adopt_probe.py --live→ADOPTION_READY→收养 commit+CEO "
    "48h 钟 (2)N2 generate harvest 观察（daemon 烧录→r244 翻面→screen-prep→"
    "12 分片入池 r481 正法）(3)W117 finalize on W116 landing（预演 r684 armed）"
    "(4)trio NULLS finalize watch 10-05..09（bm-b canonical·keepalive 勿触 "
    "r626d-2）(5)bm-b slice-2 评审回执消费窗（MSG-1930 窗内）"
)

codely = (
    "\n- [2026-10-04 19:5x r694 bm-a] 正则行级手术 repl 回补行终结符律+簿记"
    "脚本重入双计坑（本窗实弹·两坑均 fail-closed 当场拦零盘伤）：①re.sub 行级"
    "手术模式整行吞（key 行含 eol），repl 替换串未回补 eol=每键吃一个 CRLF 把"
    "下一行静默并入本行——链式断行（本窗 5 键连环·后续键 '^\"key\"' 失配 "
    "count=0 断言当场炸·文件从未写过=零伤）；正法=repl 串末必须回补 eol+术后"
    "逐键计数断言。②increment 型簿记脚本（round_no=当前+1）中途崩于后续步、"
    "修 bug 重跑=前步已写面被再 +1（本窗 693→694 首跑已落·修后重跑 694→695）；"
    "正法=轮号一律绝对值写+重跑前先读现值比对期望幂等门。How to apply: 一切"
    "正则行级手术脚本 repl 层带 eol 回补；簿记轮号/水位类脚本重入一律绝对值写。"
)

for path, text, marker in ((RR, report, "r694 (bm-a)"),
                           (CODELY, codely, "r694 bm-a] 正则行级手术")):
    raw = io.open(path, encoding="utf-8", newline="").read()
    assert raw.count(marker) == 0, "marker already present (idempotent gate)"
    with io.open(path, "a", encoding="utf-8", newline="") as fh:
        if path == CODELY and not raw.endswith("\n"):
            fh.write("\n")
        fh.write(text + "\n")
    raw2 = io.open(path, encoding="utf-8", newline="").read()
    assert raw2.count(marker) == 1, "append not exactly once"
print("append OK: round report r694 line + CODELY pit line, both count==1")
