import io

P = r"research/HANDOVER.md"
txt = io.open(P, encoding="utf-8", newline="").read()
lines = txt.split("\n")
row = ("> bm-c round 1070 五倍数核对（2026-10-17 18:2x·增量窗覆盖 r986-r1070 八十五轮·**5x 截 r990/r995/r1000/r1005/r1010/r1015/r1020/r1025/r1030/r1035/r1040/r1045/r1050/r1055/r1060/r1065 十六截未落 HANDOVER 行如实披露**〔坑-79 族·死窗吸收连营 26th-58th 代+wait-state 连守窗+CEO MV V3 收割窗消耗〕·逐轮权威面=round_reports-bm-c.md 全行在册）：增量窗 r986-r1070=bm-c 面像（**W 波链 W237→W262 全生命周期连营（absorb 续承世代制成熟期）+wait-state 连守与上游让路治理+CEO/MV 侧收割支持+短视带禁停批**——①W 波链=absorb 世代制正典化运行：每波五件套=席位公示（seat-first 律）→prereg FREEZE（跑前冻结+needle probe+floor audit+banned_direction_gate ADMIT）→五面冻结拼接（editor canon-clone+machine-splice builder+disclosed needle heals）→引擎 mtime-watch 自燃 12/12（ledger append 自提交）→sixgate PRE-FINALIZE（20th-24th 连续 ALL PASS·gate-1 TRIPLE identity worktree==receipt==LANDED）→finalize one-pass EXACT（W237 945,189/K519,320〔r990〕→W240 952,335/K525,920〔r1002〕→W244 961,135/K534,720〔r1022 收割〕→W262 **1,000,735/K574,320 EXACT**〔r1068 五键 6/6+sec78 placeholders=0〕）——账本百万级里程碑=W262 落账 1,000,735；②absorb 世代=26th（r1008 wave2 CDN 交付面 INDEX-SKIP 修复 23/23）→48th-58th 代（r1057-r1069·死窗自标轮号+estate 机器验证后落地=血统律：六门复跑+banned re-run+needle 探针+冻结 tpl 字节恒等）零双计（每窗 S0.5 双水位 delta FALSE 实证）；③staircase 带面=W255-W262 A-hop 第四至十一连（naive 撞前波 B 拒起→跳位被迫性机证）+B above-own-A 第五至十三连（own-A reservation cascade）；④wait-state 连守窗族=r993-r995/r1015-r1022（一行声明律·W238/W244 bm-a 席上游在飞=诚实等待不重扫）；⑤CEO/MV 侧=wave2 CDN 字节级 URL-本地恒等验证根除陈旧交付面（r1008 判例律）+MV V3 GPU lane 本机让路窗（ComfyUI 8188 常驻 CEO 资产·只读披露）；⑥治理面=CEO O-20261015-0906 委员会案执行（r1023/r1024·U256 车道审计+S8 闲置自驱接线）+**O-20261017-1741 短视频车道禁停批同轮执行**（r1068：ShortVideoHotScan1/2/3+ShortVideoHotApiKeepAlive 四任务 disabled rc0×4+DailyHotApi :6688 节点停置 port-FREE+V2/V3 冻结零在飞·standing re-verified r1069/r1070）+**ORD 幻影水位治愈**（r1069：872d6bb9 blob 史无此值→d19 guard advance 313c8c0f read-back OK·r977 家族 post-PIN 首例 r1069 入 CODELY）+RAM 面诚实更新 ~11GB free+LLM 面 retired per O-20260929-0953（r1066）；⑦r1070=本核对轮〔**5x HANDOVER 义务（本行）+S6 43/43 全绿 fresh run（driver _r1070bmc_s6.py canon-clone r1069·dualrun ZERO-DRIFT streak 33·审计旗 pool_starvation/supply_floor=waits-upstream 结构面诚实照录〔池 ready=0=W263 bm-a 席在飞·非本机怠工〕+zt crosscheck 软警 7 日带照录+周末 bars 10-16 诚实 no-op 族+lane 守卫他机腿诚实跳）+waits-upstream 验证（origin tip aba6247ec=r1069 收口·W263 splice/burn/finalize 未落→next bm-c turn=W264 seat）+smoke 49/49+satengine ALIVE+双水位双 SAME（ORD 313c8c0f content-sha1 钉法/DEC 1d4741e4）+orders 差集=0+孤儿面=1 零杀（用户 Doubao pythonw 域外+ComfyUI 驻留豁免 T28 跨机验）**〕。维护面全窗：smoke 49/49 链·orders 双扫零未回执链·SAT 活 rc0 链·attrition CLEAN 链·四件套绿链·孤儿面连窗只读披露。指针：**r1071+＝盯 bm-a W263 链（splice→burn→finalize）→finalize 落地即本机发 W264 席位（live re-derive post-W263 universe·staircase forward face·never transcribe r587）；周一 10-19 15:30 bars papers 全链 re-arm；短视带 disabled standing per O-20261017-1741；下一 5x=bm-c r1075**。")
# find insertion point: after title line(s) at top (first line starting with '#')
idx = 0
for i, l in enumerate(lines[:5]):
    if l.startswith("#"):
        idx = i + 1
        break
lines.insert(idx, row)
out = "\n".join(lines)
io.open(P, "w", encoding="utf-8", newline="").write(out)
print("INSERTED at line", idx + 1, "size", len(out.encode('utf-8')))
