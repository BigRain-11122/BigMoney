# -*- coding: utf-8 -*-
"""r825 bm-a S7 closeout: state bump (823->825, dead-r824 consumed), heartbeat
refresh (orders_ack += O-20261007-1157), round-report line, HANDOVER 5x line."""
import json
import time
import datetime

# --- state-bm-a.json: round_no 823 -> 825 (r824 dead window consumed) -------
p = "state-bm-a.json"
st = json.load(open(p, encoding="utf-8"))
assert st["round_no"] == 823, st["round_no"]
st["round_no"] = 825
json.dump(st, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("state round_no 823 -> 825")

# --- heartbeat fleet/machines/bm-a.json ------------------------------------
now = datetime.datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S") + now.strftime("%z")[:3] + ":" + now.strftime("%z")[3:]
epoch = int(time.time())
hp = "fleet/machines/bm-a.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = iso
hb["ts"] = iso
hb["current_task"] = "W174 prereg built (r825); W174 freeze chain next window (two-window law)"
hb["verdict"] = "green"
ack = hb.get("orders_ack", [])
if "O-20261007-1157-bm-c.md" not in ack:
    ack.append("O-20261007-1157-bm-c.md")
hb["orders_ack"] = ack
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
assert "T" in chk["clock_read"], "clock_read must be T-separated (R262 law)"
print("heartbeat refreshed: epoch int OK, clock T-sep OK, orders_ack", len(ack))

# --- round report line (S5) --------------------------------------------------
rr = "logs/iteration-loop/round_reports-bm-a.md"
line = (
    "\n2026-10-07 14:0x | r825 bm-a (dept:研究+工程·S5 接管收口·dead-r824 斩首窗遗产收入 r793/r799/r819 先例) | "
    "watermark verdict: 绿(red=false lane=healthy; py_low_board_clear=假性合法 idle 白名单面: 板全闭环 0 open 票+W173 已 finalize+W174 prereg 本窗落地=never-dry 常供线活跃推进·satengine alive rc0 tick 架构 queue0) | "
    "当前活: W174 prereg 构建本窗落地(r821 血统 buildgen 50-token 断言电跑) | "
    "最近实物: research/PERPETUAL_N1_W174_PREREG.md 20,532B @2026-10-07T13:5x (A 397_604..399_603 阶梯第三十四例 E36/B 399_604..399_803 own-A 互斥; anchor 786,012/K 378,520; proj K 380,720; W175+ 投影 399_604..401_603/399_804..400_003) | "
    "下个里程碑: W174 freeze 链下窗(两窗律 r797/r799·5-face 编辑+双 selftest+freeze commit+2-tick 点火)+10-08 复市首交易日数据链 re-arm | "
    "did: S0 dead-r824 遗产收口=2 未 push commit(W14-SCREEN runner_args 修复+tombstone clear)重放送达+S6 半途 staged 39 件吸收+5 mojibake 工作树 JSON 从暂存 blob 恢复+游离 HEAD/rebase-merge 占用/分叉 main 旧线治愈(rebase --quit+branch -f+checkout·r624/r821 heal 律·main 旧线独有内容=已重放 r824 对+已吸收 10ec80743 零丢失)→push 8f0bb36ad..d9a7326ec 送达+同窗 reconcile 双面 ZERO-DRIFT; "
    "S0.5 orders 双扫差集 1 真未回执=O-20261007-1157 全面开工广播令→bm-a 回执一行「维持全力」填回执节(本机未停·满载实证)+0935 已闭核验(bm-c r676 核收); "
    "D-19 双水位消费=dec 4c32527b(r823 已消费·dead-r824 未持久化键本窗补写)+ord e6a1dee6(新增 2 行均集团域 C1657/机制复盘零 BigMoney 派单→水位键更新零动作·K: 缺席走实径 C:\\FluxGroup fallback); "
    "S1 smoke 48/48; S2 板 0 open+job_list 空; S3 主产=W174 prereg one-pass(buildgen=_r825bma_w174_buildgen.py: exec 截断 r821 件取 TOK/BACK 50 对全断言电跑+席位路径 processed/ 双形态补丁+W174 facts 全机读回执; build=_r825bma_w174_prereg_build.py: probe 回执 ADMIT 五腿断言+n1_w173_results 键值断言(merged K 378,520/mu −0.092786/σ 0.245122/w173-only −0.0835/se_mu 0.000398/A p95 0.2986/K-lift +0.0000/n_eff 783,812)+W173 freeze sha 04e95748a+W174 seat ADD sha 9b0e1cb29 双 git 断言+token-first 两相 vmap 50/50 计数恒等+残留零+malformed-window CLEAN+r754 两形态 grep CLEAN(波号 174 唯一/n1_w1xx={w173,w174})+CRLF 写回断言; 产出 20,532B 63 CRLF·与冻结时源 27/27 行 1:1 换面零结构漂移); "
    "S6 37/37 rc0(_r825bma_s6_log.txt: dualrun ZERO-DRIFT streak 51 @404; 金周 no-op 族如实; REPORT-2026-10-07+LIVE+scorecard+build_status 再生; attrition CLEAN 4 账本); post_review 6,837 行 0 NO; S7 四件套幂等(loop pin=8 no-op+watchdog 在位+双爪 LF 归一)+state 823→825 递进(dead-r824 消费如实注记)+心跳 epoch int+T 分隔自证+O-1157 回执+825=5x HANDOVER 核对行 | "
    "verify: build 三层自证(buildgen 电跑+build 全断言+关键面 grep 18/18 OK+diff 27/27); S6 37/37; smoke 48/48; push 送达 fetch 复核 | "
    "计分: 2 (能跑/能看实物=W174 prereg 冻结语法生成后全断言电跑·引擎常供线连续供给实物增量) | "
    "登记册零命中断言: 本轮零清扫/归档/删除/恢复类动作(treasure_guard 未触发·_r825bma_w174_tok_extract.py 为本轮自建 recon 件当场修复非删除) | "
    "下轮指针: r826=W174 freeze 链(5-face 编辑[pre-seat probe+band gate+registry inserts x2+n1 materializer+PASS-claim]→n1+pf 双 selftest→freeze commit→2-tick 点火验证)→12/12→finalize(§7/§8 回填·proj ledger 788,212/K 380,720) | "
    "本地未达 origin commit 数=0(收尾 push 后 fetch 复核) | [r825 bm-a]"
)
with open(rr, "a", encoding="utf-8", newline="\n") as f:
    f.write(line + "\n")
print("round report line appended")

# --- HANDOVER 5x line (round 825 = multiple of 5) ----------------------------
hd = "research/HANDOVER.md"
hline = (
    "> bm-a round 825 五倍数核对（2026-10-07 14:0x·增量窗 r791-r825·dead 窗 r791/r792/r802/r803/r805/r812-816 静默段/r820/r822/r824 遗产由后继接管收口如实注记·逐轮权威=round_reports-bm-a.md 全行在册）："
    "增量窗主线=**W164..W173 十波全生命周期收口（freeze→tick 点火→12/12→finalize→账本）+W174 席位+prereg 双落地**——"
    "统一链 **766,212→786,012 实读前进**（W164 finalize r793〔bm-c r640 观察 766,212〕·W165..W173 逐波 freeze 轮号=W174 prereg @CHAIN@ 机读：W165=r792〔r795 补冻结双行在册〕/W166=r799/W167=r805/W168=r809/W169=r811/W170=r813/W171=r815/W172=r819/W173=r822〔freeze commit 04e95748a〕·W173 finalize r823 接管收口窗 ledger 786,012 EXACT/K 378,520/§7§8 回填·A p95 0.2986/K-lift +0.0000）；"
    "W174 链=seat r823（pre-seat probe ADMIT A 397_604..399_603 阶梯第三十四例 E36 hops=1/B 399_604..399_803 own-A 互斥 hops=1·MSG-2026-10-07-1247 推送 sha 9b0e1cb29）+prereg r825（_r825bma_w174_buildgen.py r821 血统 exec 断言电跑+50-token vmap+r754 两形态 CLEAN·20,532B）；"
    "CEO 令面=O-20261006-1845 tailnet 执行回执 r790+O-20261007-0935 能力盘点回执 r817〔bm-c r676 核收〕+O-20261007-1240 G21-T006 AU02 bgm 执行 r824〔dead-r824 产物·bm-c r676 回执核收〕+O-20261007-1157 全面开工广播 bm-a 维持全力回执 r825；"
    "运维面=r824 W14-SCREEN runner_args string→list 修复+crash-fuse tombstone clear〔dead-r824 遗产·r825 吸收〕+r825 dead-r824 mid-rebase 游离 HEAD/分叉 main/5 mojibake 工作树 JSON 三连治愈（r624/r821 heal 律·零丢失断言）；"
    "产品清单漂移=research/PERPETUAL_N1_W174_PREREG.md〔r825〕+research/PERPETUAL_N1_W1{65..173}_PREREG.md 族+results/perpetual_faces/n1_w1{64..173}_results.json 族+results/_r8{18,19,21,22,23,25}bma_* 工件族〔W172 freeze 40-needle xform/W173 freeze 4-insertion+W174 buildgen 族〕+fleet/orders/O-20261007-1157-bm-c.md bm-a 回执节〔r825〕；"
    "板 open=0·job_list 空·satengine rc0 活（bm-a tick 架构）·水位绿 py_low_board_clear（板全闭环+W174 常供线推进=合法 idle）·DEC 4C32527B/ORD e6a1dee6 双水位消费净绿·post_review 6,837 行零红·attrition CLEAN；"
    "指针=**W174 freeze 链下窗（两窗律 r797/r799·proj ledger 788,212/K 380,720）→12/12→finalize**+10-08（周四）复市首交易日数据链 re-arm（S6 legs 25-28 复活+REGIME_GUARD v3 首 bar enforce+fund_premium 15:30 首采 bm-c 车道）+10-08 治理日判据回访（O-2115/O-2030 验收包）+月界首考 10-31（T-143 装配交付 10-29）；下一 5x=bm-a r830"
)
with open(hd, "a", encoding="utf-8", newline="\n") as f:
    f.write(hline + "\n")
print("HANDOVER 5x line appended")
