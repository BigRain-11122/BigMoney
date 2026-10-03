# r646 bm-b addendum writer (push-race receipt + orders-count pit; append-only, bytes mode)
import os, datetime

ISO = datetime.datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S+08:00')

line = (f"{ISO} | round 646 addendum bm-b: S7 push-race receipt -- first push rc1 rejected by bm-c r443 wave; "
        "concurrent tick-session absorb 19add92fa + zero-intersection merge c7beb5443 (no UU) landed 04:24:34 per reflog "
        "[r643 live-overlap proven]; my follow-up absorb a7dc6fff3 + push_verify DELIVERED (tip==remote a7dc6fff3, ahead=0 behind=0). "
        "Orders double-scan zero-diff via same-filter ls-tree set-compare (Compare-Object count=0): the 153-vs-152 'new order' "
        "was a counting-artifact false alarm (ls-tree counts non-O-*.md files in fleet/orders/) disproven in-round per r641 law. "
        "No new orders, inbox 0; orders_ack 152/152 unchanged.\n")
p = 'logs/iteration-loop/round_reports.md'
with open(p, 'a', encoding='utf-8', newline='') as f:
    f.write(line)
print('addendum appended')

cp = 'CODELY.md'
cline = ('- [2026-10-04 04:3x r646 bm-b] orders 双扫计数口径坑：ls-tree 全目录计数（fleet/orders/ 含非 O-*.md 件=153）vs '
         'Get-ChildItem O-*.md 过滤计数（=152）——跨口径计数比对产出假「新令」警报；Compare-Object 双侧同口径 ls-tree 集合比对实证零差。'
         'How to apply：令差集判定一律双侧同口径集合比对（ls-tree vs ls-tree），禁跨口径计数比对；假警先证伪再上报（r641 律兑现面）。'
         '另（同窗观察）：S7 push-race 窗内并发 tick 会话同仓 absorb+merge（reflog 04:24:34 双 commit 实证 c7beb5443/19add92fa），'
         '后到会话 merge 报 Already up to date=前体已并——撞此形态先 reflog 核拓扑再定叙事，勿重复 absorb（本轮 a7dc6fff3 为无害幂等面）。\n')
craw = open(cp, 'rb').read()
if not craw.endswith(b'\n'):
    craw += b'\n'
open(cp, 'wb').write(craw + cline.encode('utf-8'))
print('CODELY pit line appended; new size =', os.path.getsize(cp))
