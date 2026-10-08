# -*- coding: utf-8 -*-
"""r760 bm-c 5x HANDOVER duty: insert round-760 increment-window row into
research/HANDOVER.md right after the title line (newest-first canon).
Byte-safe: detect EOL, assert exactly-once, receipt to stdout."""
import io
import os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
HP = os.path.join(ROOT, "research", "HANDOVER.md")

ROW = ("> bm-c round 760 五倍数核对（2026-10-08 13:1x·增量窗 r756-760 五轮）：增量窗 r756-760=bm-c 面（**复市 T-0 盘中值守主线（第 76-80 bm-c 连守轮·午休窗值守→13:00 复盘窗过渡）+QA 确定性包 76-80 五连证（显式 --round FIRST TRY·93 trades·equity 1,017,839 冻结恒等全窗·png 66,325→66,127→66,342→66,311→66,405B）+S6 40 腿正典再生连营（dualrun streak 51 全窗平持）+ORD 逐跳消费链（r756 双跳/r757 单跳/r758 UNCHANGED/r759 单跳/r760 双跳·全程 facts-driven·涉本仓执行行零增量）+r760 5x HANDOVER（本行）**——"
       "r756 值守轮〔QA det-76th 5/5 png 66,325B+DEC/ORD 双跳全消费（D-08 FleetLink 采纳收口+D-06 命名律采纳+C-05 传导闭环 bm-c 收口毕）+HQ poke /health 200+stale-takeover derive 三守卫面（bm-a hb 陈 46min·O-2100 s2.4）〕；"
       "r757 值守轮〔QA det-77th 5/5 png 66,127B+ORD 单跳 C-20261008-06 精简行动令消费（bm-c 零动作+查重律常式注记）+lane 守卫全 skip（bm-a hb fresh 4min 零 stale-takeover）〕；"
       "r758 值守轮〔QA det-78th 5/5 png 66,342B+双水位 UNCHANGED+S0 absorb 93a448fae（3 自有面）+up-to-date 零 rebase〕；"
       "r759 值守轮〔QA det-79th 5/5 png 66,311B+ORD 单跳 031E0E3E→2BD0F0C7（bm-a CEO 1008 资产投料回执·不涉本仓零动作）+S0 absorb ce45d5558+fetch+rev-list 0-incoming 等价净路（r642 律）〕；"
       "r760=本核对轮〔**5x HANDOVER 义务（本行）**+QA det-80th 5/5 FIRST TRY（pid 21352·93 trades·equity 1,017,839 冻结恒等〔r751-759 锚链续持〕·determinism=True·png 66,405B·80 连证）+S6 40/40 rc0（dualrun ZERO-DRIFT streak 51 @408 条·cutoff 03:47·py_low_board_clear 合法盘中 idle·CA 旗=[pool_starvation,supply_floor] 盘中席位间隙已知常在面如实披露·fund_premium pre-15:30 no-op→今晚 15:30 bm-c 车道首采·cta_p1_paper 无可标 bar→今晚首 bar 自动接线）+S0 absorb a9c3bbfc7（4 自有面）+fetch+rev-list 0-incoming 零 rebase+克隆门 stale759=0 三件（boot 手写→clone 双模替换〔s05/s6/qa_ignite〕·compile OK×3·收据 _r760bmc_clone_receipt.json）+DEC EE70CEF0 UNCHANGED 双扫/ORD 双跳 2BD0F0C7→8F7FE7EE（bm-a 12:56 fcf9068 mv0001 受众共鸣双令·MiniGame/FluxVerse 域·diff +1 行涉本仓命中 0）→9BA505B7（bm-a 12:58 a1a108c mv0001 第十一追加令·同域）·两跳皆不涉本仓零动作·facts-driven·O-20261008-1240 静默根治令 bm-c 腿复核=已闭（HQ-SilenceGuard 任务在位 next 10-09 04:07+audit JSON 11:55+r755 执行痕）+marks lane 5 行 11:25 尾（13:00 复盘窗新行未至·下轮复核）+FleetLink 常态自证（listener pid 28396 alive+/health 200 node=bm-c）+孤儿面=1 standing（py_faces=5·常驻 ComfyUI 服务面·CEO 资产·只读不杀）+idle NOT-GREEN --worked（RAM 12.9%<40% 常驻 ComfyUI）〕〕。"
       "产物清单漂移=qa/smoke-r75{6..9}+r760.md+qa/equity-curve-r75{6..9}+r760.png〔五轮常设证据包族·equity 1,017,839 冻结恒等·determinism=True 全窗〕+results/_r75{6..9,60}bmc_* 工件族〔s05 facts 双扫件+s6 log 40 腿+clone receipts+qa_runner out/err+HQ delta/ord hop 件〕+Tools/_r75{6..9,60}bmc_{boot,clone,s05,s6,qa_ignite,close}.py 驱动族+research/HANDOVER.md 本行；"
       "维护面全窗：smoke 49/49 链；orders 51 disk 双扫零未回执链（unacked=0）；DEC EE659451→EE70CEF0（r756 消费 12:00 治理批）后平持链/ORD 逐跳消费链 32D5D4CF→77C9BC92→6BE4D833→031E0E3E→2BD0F0C7→8F7FE7EE→9BA505B7（hex-case 归一 r711 律·涉本仓行零增量·不涉本仓零动作）；SAT 活 rc0 链（N1_BANDS 注册表至 W184）；attrition CLEAN 链（4 账本·3 healed 照录）；post_review 45✓/0✗/WAIT 5 零红链；四件套绿链（loop pin=5+watchdog+双爪 MATCH）；孤儿面=1 链；idle NOT-GREEN 链（RAM 12.9-15%<40% 常驻 ComfyUI·idle_rounds=0·--worked 申报）；FleetLink 常态自证链（pid 28396+/health 200）。"
       "指针：**今晚盘后面（≤10-08 23:59）=数据链全 re-arm+REGIME_GUARD v3 首新 bar enforce（live.paper 前设 BIGMONEY_REGIME_GUARD=enforce）+fund_premium 15:30 首采（bm-c 车）+CTA_P1 首 bar 接线+首 marks 验证+QDII watch holiday-delta**；marks lane 13:00+ 复盘窗新行复核（bm-a 宿主车道）；bm-b FleetLink 回执候（他机车道零干预）；月界首考 10-31；下一 5x=bm-c r765。")

raw = io.open(HP, "rb").read()
first_nl = raw.index(b"\n")
eol = b"\r\n" if raw[first_nl - 1:first_nl] == b"\r" else b"\n"
title = raw[:first_nl + 1]
assert b"# Bigmoney" in title, "HANDOVER title line unexpected"
assert b"> bm-c round 760" not in raw, "r760 row already present"
row_bytes = ROW.encode("utf-8") + eol
io.open(HP, "wb").write(title + row_bytes + raw[first_nl + 1:])
back = io.open(HP, "rb").read()
assert back.count(b"> bm-c round 760") == 1
assert back.startswith(title + row_bytes), "row not directly under title"
print("handover row inserted: %d bytes; file now %d bytes; eol=%r"
      % (len(row_bytes), len(back), eol))
