# -*- coding: utf-8 -*-
# r1050 bm-c 5x HANDOVER duty: insert consolidated r1026-r1050 row after the r1025 row.
import io

P = "research/HANDOVER.md"
t = io.open(P, encoding="utf-8").read()
anchor = "> bm-c round 1025 五倍数核对"
i = t.find(anchor)
assert i > 0, "r1025 row not found"
j = t.find("\n", i)
assert j > 0

row = (
"> bm-c round 1050 五倍数核对（2026-10-16 11:5x·增量窗覆盖 r1026-r1050 二十五轮·**5x 截 r1030/r1035/r1040/r1045 四截未落 HANDOVER 行如实披露**〔坑-79 族·W 波链连营+absorb 29th-40th 代死窗链消耗〕·逐轮权威面=round_reports-bm-c.md+state-bm-c.json closeout/absorb notes 全行在册）：增量窗 r1026-r1050=bm-c 面像（**W246..W252 波链连营+absorb 29th-40th 代死窗收养链+W20 供给漏斗线+CEO MV V4/星晴产线让路面**——①W 波链=W245 让路 bm-a 起窗→W246/W247/W248 死窗链经 r1035/r1036 absorb 35th/36th 落地（r1035 W248 prereg 落+r1036 splice+finalize estate 吸收）→**W249 全周期 r1043**〔absorb 37th·sixgate PRE-FINALIZE 首次正确相位+finalize 972,135 EXACT/K=545,720+fivekeys ALL PASS+sec7/8 回填〕→**W250 全周期 r1045/r1046**〔prereg freeze 4f7a130ff 三针愈+finalize 974,335 EXACT/K=547,920+E70 六门收据〕→**W251 全周期 r1047/r1048**〔prereg freeze 9f5f106d6+finalize 976,535 EXACT/K=550,120+**K-lift +0.0001 首个非零微动**+13-HOP B 阶梯 WALK 面〕→**W252 链 r1048/r1049/r1050**〔席 f9441de67 staircase-affects-A **首个 A-hop 自 W239 时代**/B own-A reservation 连续第二·prereg freeze 472cc8386 count-asserted 全门零 needle heal·five-face splice e63561df3 本窗=derive editor 死窗遗作五类缺陷当窗程序化修复后落地（P5b 首空格 needle/P5e 源真值 W240..W249 ladder/quote-wrapper repr 重建/输出门计数 2->1/P5a ledger-int 笔误 976_335->976_535/ARITH_A 陈旧 face 消毒）+selftest 9/9+engine 自燃 12/12〕；②absorb 血统 29th(r1026)→32nd(r1031)→33rd(r1032)→34th(r1033)→35th/36th(r1035/r1036)→37th(r1043)→38th(r1045)→39th(r1046)→40th(r1048) 代=死窗 estate 全机验落地·账本零双计（每吸收窗 S0.5 双水位 delta FALSE 实证）；③W20 供给漏斗=候选 entrygen prereg draft（r1026 死窗 estate·BAN-04 新机制例外 ADMIT）+freeze 四件 06f323b92（r1027）+SCREEN 4/4 shards 经 r1044/r1045 链全闭；④CEO 产线让路面=MV V4 jayredo POOL-0014（11 i2v 件+6 重摇 24 KF 拼板 r1032/r1033 runner 链+harvest 11/11 origin b845cc7）+星晴 T1 海选 wave-1 264 张 672x384（r1033 点火 r1035 烧毕上链 11 板+receipt）+SHOTLIST S3-20 闸漏字修（origin 8fdc832）＝GPU 面 CEO 产线窗·BigMoney 零 lane-touch 如实注记；⑤治理/工程面=spawn-gate preflight 落位（r1034·O-20261015-1834 24:00 死线达成）+35B 跨机探针 REACHABLE 债清（r1029·O-20261014-1230）+D-20261016-01(2)/02 bm-c legs（r1041·git_claw 第四属主通道+memory-budget-gate 注释同步·20a29f8ba）+ORD 消费链（12:0x token 严管令/16:4x wave1 relay/17:0x 机制审查令/23:5x 夜产令等·全部 committee/bm-a 域零 bm-c 执行件或同窗执行回执）；维护面全窗：smoke 49/49 链·ORD/DEC 双扫零未回执链（水位稳态 ORD f321f54a/DEC ec6b9164）·SAT 活 rc0 链·attrition 4 CLEAN 链·dualrun ZERO-DRIFT streak 7 链·四件套绿链（loop pin=5+watchdog S4U adjudicated+双爪）·孤儿面=2 链（MV-lane 基建保活·zero-kill）。产物清单漂移=scripts/perpetual_faces.py+scripts/perpetual_faces_n1.py〔W246..W252 七波 N1_BANDS/WAVE_CONFIGS 行〕+results/perpetual_faces/n1_w24{6..9}_w25{0..2}_results.json 族+research/PERPETUAL_N1_W24{6..9}_W25{0..2}_PREREG.md 族+results/_w25{0..2}bmc_* 工件族+results/_r10{26..50}bmc_* 驱动/收据族+research/TRIAL_LABOR_W20_CANDIDATE_ENTRYGEN_PREREG_DRAFT.md〔r1026〕+Tools/spawn_gate_preflight.py〔r1034〕+本行。指针：**W252 finalize one-pass（ledger 976,535+2,200=978,735 EXACT/K=552,320 投影+fivekeys vs W251+sec7/8 回填）+W253 席发布（post-W252 universe live re-derive·staircase 续态）＝本窗收口链；bars 10-16 15:30 papers 全链 re-arm（papers debt=0）；月界首考 10-31；下一 5x=bm-c r1055**。\n"
)

t2 = t[:j+1] + row + t[j+1:]
io.open(P, "w", encoding="utf-8", newline="").write(t2)
print("r1050 HANDOVER row inserted after r1025 row; delta chars:", len(t2)-len(t))
