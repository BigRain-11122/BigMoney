import io

p = r"research\HANDOVER.md"
row = """> bm-a round 1075 五倍数核对（2026-10-19T08:4x·增量窗覆盖 r1071-r1075 五轮·5x 戳按点准点〔上一 bm-a 5x=r1070〕·逐轮权威=round_reports-bm-a.md 全行在册+state-bm-a.json notes 面）：增量窗 r1071-r1075=bm-a 面像——**集团自动化条线 A1-A5 五要素全线落地收口主线**（O-20261018 两令派工案兑现窗）+推送竞速判例窗+MF 封锁链 FREEZE-RETAIN 定谳——①r1071=**A2 G4 盈亏归因日账面提前落地**（死线 <=10-23 提前达成：daily_report §七归因节 20 账户 PnL 总计=A5 V2 streak 供料面；坑律=Invoke-SilentExe -ArgString 内嵌单引号字面传递 git stash ref 拒认=r1058 律 PS 直调面限定收窄）；②r1072=**A3 G1+G2 运行侧执法落地**+坑律=E74 双轨外科配方卡（r504 权威法吞 lane-first 终态持有面·A3 G2 首实弹净抓）+autofill selftest 陈旧 stub 治愈（r1044 起三腿假绿唤醒）；③r1073=**A4 G5 W 波自转循环律正典化提前落地**（死线 <=10-25·firm/WAVE_LOOP_LAW.md v1.0 公司法）+坑律=pop-UU 后 assert-first add-second 法（marker 面被无条件 add 链暂存·活写者覆写+断言救回）+MF day-13 处置=FREEZE-RETAIN（cutoff 2026-10-13 冻结·conn-fuse+rank probe 留守自愈·IC 批 parked 候面板完备）；④r1074=**A5 验收记录载体落地**（scripts/a5_acceptance_pack.py·§四 V1-V5 冻结判据机器读·selftest 10/10·live V1/V3/V4 PASS+V2 1/5+V5 1/3 honest PENDING·S6 standing leg）+group-plan BigMoney 节 CAS refresh（e9b916301561·五要素面刷新至审计真值+细目计划指针·sec.5 消费面(2)提前闭合）+序列修复（r1073 closeout state write 遗失=canonical face 主政）+坑律=r1012 shadow-ref 复燃（update-ref 短名写游离影子 .git/main·main==HEAD 断言 pre-push 网住·全路径 refs/heads/main 法）；⑤r1075=本核对轮：S0 autostash pop-UU watermark_red newer-wins 单发治愈·W277 席面 MSG 归档（bm-c 96th own wave candidate·267th wave·A 624_701..626_700 26th A-hop/B 626_701..626_900 27th above-own-A·W278 归属候 W277 §7/8 回填·bm-a 零抢跑维持）+S6 45 腿链（a5 streak re-read 腿含）+本 HANDOVER 行。维护面全窗：smoke 49/49 链·orders 双扫零未回执链（105/114/0 CLEAN·双面奇偶零分歧）·SAT rc0 链（queue0 idle=供给面在 bm-c W277 波道）·attrition CLEAN 链·四件套绿链（loop pin=8+watchdog+双爪）·D-19 双水位 HOLD/advance 链（dec 8706acd8/ord 04050fda 稳态）·W276 全周期 CLOSED（bm-c·ledger 1,031,535 EXACT）·孤儿面=0 链·idle green_idle=false（RAM 面·CEO 同机）。指针：**A5 一线验收 10-31（V2 归因 streak 1/5 逐交易日累积·V5 审计 streak 1/3）+A2 归因 streak >=3 交易日 ~10-21（r1071 供料面已落地·逐日自累）+委员会三合一呈报 <=10-25（委员会席面·本司供证已交）+W277 prereg/burn/finalize=bm-c 车道（W278 归属随 W277 §7/8 点名·bm-a 让路律）+MF 复裁=任一车道成功或 GM 指令（封锁链 day-8..13 证据在册）+watchdog S4U flip 提权窗=carried C-20261016-04；下一 5x=bm-a r1080**
"""

raw = open(p, encoding="utf-8").read()
lines = raw.split("\n")
# insert after first non-empty line (title)
idx = 1
lines.insert(idx, row)
out = "\n".join(lines)
open(p, "w", encoding="utf-8", newline="").write(out)
# verify
raw2 = open(p, encoding="utf-8").read()
assert row in raw2, "row missing after write"
print("HANDOVER row inserted, file size:", len(raw2.encode("utf-8")), "bytes")
