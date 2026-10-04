# r699 bm-b addendum append (r679 idempotent gate)
import time
P = r'C:\Fluxgroup\FluxGroup\quant\bigmoney\logs\iteration-loop\round_reports.md'
raw = open(P, 'rb').read()
marker = 'round 699 addendum (bm-b)'.encode('utf-8')
assert raw.count(marker) == 0, 'addendum marker already present'
clock = time.strftime('%Y-%m-%dT%H:%M:%S+08:00', time.localtime())
line = (
 clock + ' | round 699 addendum (bm-b) | '
 'S7 收口 push-race 实录：首推被拒（origin 前移 7 commits=bm-a r700 N2 finalize 预演 GREEN_WAIT_SHARD2+bm-c r501 W3 值守+三 merge）→零 --no-verify→merge 31 UU（双 S6 再生族）→r697 血统 resolver 幂等单跑（regen 面 ours-fresh 23:0x>theirs 22:5x 全取我侧·token per-key union side_pick theirs=21（他机键归其主）+default 键三面字节恒等 delta=0 族实证（_r699bmb_token_default.py）+x2_watch 行 union 2893+6）→add 笔误 pathspec fail-fast 零 staging（B795①族自愈）→单次 add 整清单 31 面（r673 律）→UU=0 过门→merge commit d3b7dc2ec→push DELIVERED（push_verify tip==remote ahead=0 behind=0）。'
 '本窗验证探针三件入册（token 三面归属/default 键/dump 结构）。双爬零强推。本地未达 origin commit 数=0\n'
)
with open(P, 'ab') as f:
    f.write(line.encode('utf-8'))
raw2 = open(P, 'rb').read()
assert raw2.count(marker) == 1
print('addendum appended count=1')
