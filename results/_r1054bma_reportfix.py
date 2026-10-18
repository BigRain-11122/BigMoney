# fix last report line to canonical format (dept + WM-VERDICT prefixes)
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
rp = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\round_reports-bm-a.md'
lines = open(rp, encoding='utf-8', errors='replace').read().splitlines()
assert lines[-1].startswith('2026-10-18T11:52:10'), 'unexpected tail: ' + lines[-1][:60]
lines[-1] = ("2026-10-18T11:52:10+08:00 | r1054 bm-a (dept:工程·解锁验证闭环+收件落位+委员会供证+S6维护收口) | "
             "WM-VERDICT: 绿 (red=false lane=healthy; satengine ALIVE queue0 idle; idle green_idle=true 达档 claimable=1=行14 bm-b 专属车道零领单→实际产品工 --worked 清零) | "
             "当前活=r1054: ①bm-b 解锁递送验证 CLOSED（r1053 next①·判据改法实锚=bm-b closeout push 落 origin 非 repo_heads==bm-a-sha：r1004/r1005 已落（9877424b4f+2722a044b5·estate dac9a725 lineage delivered 'r1054 criterion met'）+心跳新鲜 11:27:38+O-0948 ack+MSG-1035 rootfix 三腿全执行（13 TIMEOUT 清账+v2 采纳）→fast-path 死锁解锁全链闭环；rootfix 回执窗双机全闭（bm-c r1087 11:02:27 ack+432 清账+MiniGame 同修 df88bb98a）②MSG-0845 收件 8/8：Downloads 全扫捕获（tailscale file get CLI=静默 no-op=r1044 双面坑二次实录）+批1字节 4/4 恒等+WAV 头 44.1k/16bit/stereo+SHA256 拷贝对账 8/8+落位 CEO 看片通道 media\\drama-pilot-in\\audition-mix-20261018\\（8件+README）+回执 MSG-20261018-1145 ③全流程梳理令（组 orders 11:3x 行）本司 24h 补行同轮：council C-20261018-02 §六 BigMoney 司流程清单行 BM-1..BM-8+3 在册治理面供证·CAS 外科直投 origin edc8332778（40hex+tip/blob 双验·零树触碰）④D-19 ord a62af296→9a1771f3 advance（11:28 漫剧3D转向=非本司面零义务/11:3x 梳理=本司补行已执行）·dec 0ad85a30 hold ⑤W268 守门：W267=bm-c own seat（prereg df55e3fab9 ALL GATES PASS）但 splice/self-burn/finalize 未落→GATED 零抢跑维持（upstream waits 非空）⑥S6 43/43 rc0 bad=0（r1053 面 verbatim 克隆·MF day-11 数据点随链） | "
             "验证=Downloads 8 件字节/头/SHA256 对账 8/8 + CAS_PUSHED edc8332778（tip 恒等+blob 恒等）+ d19 advance 读回 full-string equality + origin ls-tree（W267 prereg 在/n1_w267 缺=zero skip-claim 证据）+ smoke 49/49 + orphan 0/24 + 双爪重装 + loop pin=8 no-op + idle --worked 回执 | "
             "下轮指针=r1055: (1)W268 守门候 bm-c W267 finalize（落地+席面点名 bm-a→live re-derive FIRST ACTION）(2)MF 封锁周一裁决 <=10-19（day-8/9/10/11 链 armed）(3)委员会 12:00 班对 §六 供证收取观察（首轮裁决表 <=10-20 12:00）(4)bm-b r1005 leftover MemoryBudgetGate first-fire 面（bm-b 自域观察）")
open(rp, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('report line fixed, tail ok:', open(rp, encoding='utf-8', errors='replace').read().splitlines()[-1][:80])
