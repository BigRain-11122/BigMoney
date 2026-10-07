# _r855bma_handover_5x.py -- r855 5x HANDOVER entry (bm-a window r851-r855, append-only).
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
P = 'research/HANDOVER.md'
ENTRY = '''> bm-a round 855 五倍数核对（2026-10-08 02:0x·增量窗 r851-r855·逐轮权威=round_reports-bm-a.md 全行在册）：增量窗主线=**OSS 引进管线两连件收口（O-2245）+W180 全生命周期 finalize（r381 law）+E42/S0 rebase 停窗机制面续深**——r851..r853 state-heal 链（851->852->853 三态续接诚实·r852 push 后死）+r853 **OSS S3/S4/S5 补扫收口**（5 路准入链齐·三腿探针脚本·404 三例治愈=库全名 search 实证律·ledger section-6+S5-01 vibe-astock 排产 #1）+r854 **W180 finalize one-pass 同窗落地**（ledger 801,905 EXACT·K 393,920 EXACT·skill_line 1.1852·pf 9/9+n1 selftest·S6 38/38 dualrun streak 51·E42 writer-pause rebase 单 UU ts-newer take-local）+r855 **OSS S5-01 vibe-astock 准入探针 GO**（vibe-probe rc0 三面取证=meta 复验 667★Apache 隔日活跃+emotion_metrics.py 19.9KB 纯计算参考件存档+cycle_position 三轴门公式提取=(涨停家数+最高连板+1−炸板率)/3·10d minmax+晋级率/赚钱效应/连板溢价/梯队断档函数面全列；akshare 1.18.96 zt_pool_em/zbgc/dtgc 三端点本地全在位；反重复 PASS=theme_event_library L261 deferred 真缺口；ledger section-7 +13/-0；下一件=update_zt_pool.py 前向采集 gate 腿→准入回放 prereg）+r855 rebase-continue 假冲突拒进第四态坑新律（无关未暂存 daemon churn 触发·吸收进 continue commit 轻治愈·pit-git-resolver.md 30,089B 线内直写 r833 范式·main CODELY 30,606B 线 held 无 append）。
'''
with open(P, encoding='utf-8') as f:
    body = f.read()
assert ENTRY[:60] not in body, 'already appended'
with open(P, 'a', encoding='utf-8', newline='') as f:
    f.write('\n' + ENTRY)
print('HANDOVER 5x entry appended')
