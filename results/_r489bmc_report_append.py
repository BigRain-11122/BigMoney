# -*- coding: utf-8 -*-
"""r489 bm-c round report append + CODELY pit line (bytes-mode append per
r641 mixed-encoding file law; idempotence: marker count before append).
Lineage: _r690bma_report_append.py pattern (read per r461)."""
import datetime

REPORT = "round_reports-bm-c.md"
CODELY = "CODELY.md"
now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")          # T-separated, +08:00 suffix
hhmm = now.strftime("%H:%M")

marker = "| r489 |"
raw = open(REPORT, "rb").read()
assert raw.count(marker.encode("utf-8")) == 0, "r489 line already present (double-append)"

line = (
 ts + " | r489 | dept:策略/研究（W3 judge 看护轮·T-158 在册·rule-2 单线看护禁重扫） | "
 "watermark verdict=绿（red=false·healthy·18:39 probe=insufficient_history n=2 span12min·local_batch_running=true=judge-finalize pid 33768 活批合法面·板 0 open·bandit 0·pool ready=4 全=bm-b RAM-gated keepalive 车道 r487 判例禁手工代烧） | "
 "当前活=W3 judge finalize --wave 3 看护（pid 33768·17:44:04 起·end-only writes·ETA ~22:1x 按 w2 先例 4h44m 标定·18:39 复核 VERIFY_RC=0 IN_FLIGHT） | "
 "最近实物=r489 S6 38 面 rc0 再生（REPORT-2026-10-04+LIVE-2026-10-04 双面刷新+dualrun ZERO-DRIFT streak 51·377 entries）+D-19 双 MATCH 复核 @ " + ts + " | "
 "下个里程碑=w3_judge.json 判决产品落地（777 格·真链头 646,799→647,576）→ADOPT_PASS 一键收养链→48h CEO 报告钟起算（≤10-06 晚呈报）；fund-trio finalize 10-05 10:30（bm-b 正主）；O-2115/O-2030 验收 10-08；开市 10-09 | "
 "S0: fetch 后交集核零→merge FF ae68ffad5（bm-b r686+bm-a r690 waves·51 文件零 UU·daemon lane 双面保留） | "
 "S0.5: _r489bmc_s05_check 双 MATCH（decisions 4E5BE321+orders 68947C17·r458 per-key 口径 SHA-256/SHA-1）+令差集 0 未回执（ack_extra README=历史无害·r477 全名口径）+inbox 1=MSG-2026-10-04-1830（bm-a→bm-b N2 slice-2 席位 ping 42h 停滞·cc ALL·bm-c 非当事零席位动作·留存待 bm-b 处置） | "
 "S1 smoke 48/48 | S2 板空（job_list 0·fleet 169 票 0 open·45 claimed） | "
 "S3: satengine rc0 活（Tools 注册面 r467 律）·N2-W15 缺口=观察面（bm-b s2 正主 MSG-0016+bm-a 席位 ping 已发·两轮无回复默认方案 A 接管·bm-c 按 r479 让路律+零重复开发律不抢）·post_review 官方面 ✓45/✗0/🟡5 零活红 | "
 "S6 38/38 rc0 NON-ZERO=none（scorecard/build_status/paper 族=bm-a fresh 守卫跳过无接管·金周 no-op 族诚实） | "
 "S7: quartet 4/4（loop pin5 no-op 18:45 首发·watchdog 重注册 18:43·双爪 LF 归一重装）·attrition CLEAN（4 ledgers·healed 注记照录） | "
 "S4: 一条坑律行（包装器输出单串对象 Select-Object 不分行截断=rc 行淹没丢失·split 后截正法） | "
 "记分: 1（S6 38 面再生+探针件=实际文件改动·判决产品未落地=看护轮如实计） | 记账预算: 5/5（state+心跳+轮报+CODELY+自证） | "
 "方法论捕获=无新方法（全链复用正典范式）·宝藏捕获=无（无判决面收口） | "
 "本地未达 origin commit 数: 收口 push 后 push_verify 自证 | "
 "下轮指针=r490 ①产品 ~22:1x 落地首查（python results/_r487bmc_w3_judge_verify.py→ADOPT_PASS 收养链→宝藏捕获问+§7/§8 回填+48h CEO 钟）②MSG-1830 两轮回复窗观察③fund-trio 10-05 10:30（bm-b）④验收 10-08⑤开市 10-09"
)
with open(REPORT, "ab") as fh:
    fh.write(line.encode("utf-8"))
    fh.write(b"\n")
check = open(REPORT, "rb").read()
assert check.count(marker.encode("utf-8")) == 1, "post-append marker count != 1"
print("round report r489 appended, marker count 1 OK")

# ---- CODELY pit line (S4; entry-gate four questions passed) ----
cmarker = "r489 bm-c] 包装器输出单串对象"
craw = open(CODELY, "rb").read()
assert craw.count(cmarker.encode("utf-8")) == 0, "codely line already present"
cline = (
 "- [2026-10-04 " + hhmm + " r489 bm-c] silent-git/Invoke-SilentExe 包装器输出单串对象坑（两包装器 Write-Output $out.TrimEnd() 把整段 stdout 作为一个含换行的 PS 字符串对象返回——$o | Select-Object -Last N 按【对象数】截非按【行数】截=零截断：本窗 satengine status 大 JSON（N1_BANDS 全量）整段回流淹没会话壳输出+前段 SMOKE_RC/SATENG_RC 两行 rc 被工具端从头截断丢失〔首读即丢·split 后重跑恢复〕）。正法=($o -split \"\\r?\\n\") | Select-Object -Last N 先分行再截，或一律消费探针自写证据文件；rc 行/关键 verdict 放输出序尾。How to apply：包装器调用后一切「截短看输出」需求先 split 后 Select；见 rc 行丢失即按本律复跑勿凭空推断（r655 双 Format-Table 族姊妹面）。"
)
with open(CODELY, "ab") as fh:
    fh.write(cline.encode("utf-8"))
    fh.write(b"\n")
ccheck = open(CODELY, "rb").read()
assert ccheck.count(cmarker.encode("utf-8")) == 1, "codely post-append count != 1"
print("codely pit line appended, marker count 1 OK")
