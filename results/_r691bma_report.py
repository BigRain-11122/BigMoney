"""r691 bm-a: round report append (idempotent marker gate per r679 law)."""
import io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = "round_reports-bm-a.md"
b = open(p, "rb").read()
marker = "r691 (bm-a)"
assert b.decode("utf-8", "replace").count(marker) == 0, "r691 marker already present"

entry = """
2026-10-04T18:4x+08:00 | r691 (bm-a) | watermark=green (red=false; satengine alive rc0 queue0 idle·shards_done_total 474; py_watermark py_low_board_clear golden-week legal board-clear idle; compute_audit CLEAN; pool dualrun ZERO-DRIFT streak 51 @cutoff 17:55:45) | 当前活: 等待态值守——W3 judge verdict bm-c 在飞 (~22:1x 落地投影·r487 工时标定) + N2 slice-2 席位 ping 窗 round-1/2 (无回复·树面零 N2 新 commit·r690 MSG 实核) | 最近实物: S6 36/36 rc0 (_r691bma_s6_log.txt·CEO 面 REPORT/LIVE-20261004/scorecard/dashboard 幂等再生) + 首查探针 results/_r691bma_firstcheck.py (W3 产品 origin 缺席=bm-c 烧录在途确认·N2 零 commit 实证) + D-19 探针 results/_r691bma_d19_check.py (双键 MATCH·orders 键 sha256 口径自证) | 下个里程碑: ①W3 judge 产品落地→verify+收养 commit+CEO 48h 报告钟 (窗≤今晚 22:3x) ②N2 slice-2 席位决议窗 round-2/2 (无回复+零树进=方案 A 生效 bm-a 开工·tl14 四面拷贝适配·窗≤2 轮) ③trio NULLS finalize 10-05..09 (bm-b canonical) 窗≤10-09 | DONE-1 S0: fetch+FF merge origin 3 commits 零交集零 UU (bm-b autofill keepalive 波·r437 merge-over-rebase 律·本机脏面全 bm-a lane daemon 面) | DONE-2 S0.5: orders 154/154 双扫零未回执 (r477 全名同形态·收尾二扫同) + D-19 双键 MATCH (decisions 4e5be321 / orders 82a0cef9·K: 缺席=S4U fallback sparse-clone ssh-first r631/r677) + **r458 orders 键口径坑当场自犯自纠** (从零新写探针首版算 SHA-1 而水位 64-hex=SHA-256 恒假 CHANGED·按 r672 值长度自证修 method_for() 腿·r680「复用仓内探针禁从零新写」律重犯实录·已在 _r691bma_d19_check.py 落码) | DONE-3 S1: smoke 48/48 | DONE-4 S2/S3: 板 0 open 票 (text-scan 直扫防 ConvertFrom-Json 假阴性·r641 律) · 池勘=4 ready 全他机属主 (trio NULLS=bm-b keepalive 18:2x fresh·CONTEST-YTD-RC=bm-b 18:06:31·W14-GENERATE=治理 park per D-20260930-41 sec.1.2 禁单方解冻) · W3 首查=产品未落地 (bm-c pid 33768 本机 tasklist 不可见=他机进程·收养面走 origin·r487 ETA ~22:1x) · N2 零回复零树进 (窗 round-1/2 继续) | DONE-5 S6: 36/36 rc0 (金周 no-op 族诚实·dualrun streak51 ZERO-DRIFT·live.paper 无新 bar r660 判例跳过) | DONE-6 S7: 自愈 4/4 (loop pin=8 no-op+watchdog 重注册+双爪 LF 归一重装) + state 690→691 程序化写+reparse 自证 + 心跳 epoch 1791110808 int 自证 clock T 格式 + MSG-1830 达 origin 验证 (15 行) 后归档 processed + orders 收尾二扫 154/154 | 记分: 0 (等待态轮·判决产品在飞 bm-c 手·N2 窗未满·池全有主或治理冻结·S6 幂等再生非新实物·如实计零不粉饰 per r674 先例) | 记账预算: 5/5 (state+心跳+轮报+orders 双扫+守卫扫描) | 本地未达 origin commit 数: 0 (收口 commit 后 push_verify 自证) | 登记册零命中断言: 本轮零清扫/归档/删除/恢复类动作 (treasure_guard 未触发·probes read-only·MSG 归档=inbox 协议移动) | 承接判定: 本批无新方法论 (探针=正典 D-19 探针族范式·r458/r672 口径律执法非新法) | 宝藏捕获: 无 (判决批未落地) | 下轮指针: ①W3 judge 产品落地首查→收养 ②N2 席位窗 round-2/2 决议 (无回复=方案 A 开工 tl14 拷贝) ③W117 finalize on W116 landing ④trio finalize watch
"""
with open(p, "ab") as f:
    f.write(entry.encode("utf-8"))
chk = open(p, "rb").read()
assert chk.decode("utf-8", "replace").count(marker) == 1, "append count!=1"
print("round report appended, marker count=1 OK")
