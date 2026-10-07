# _r855bma_pit_append.py -- append r855 rebase-continue false-refusal variant to pit-git-resolver.md.
# Multi-writer-file law: python fresh-read-append; numstat self-check after.
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
P = 'research/pit-git-resolver.md'
ENTRY = '''
- [2026-10-08 01:5x r855 bm-a] **rebase --continue 假冲突拒进第四态=无关未暂存 daemon churn 触发（ls-files -u 恒空·吸收进 continue commit 即愈·r835 终局前轻治愈）**：单 UU（共享探针件 ts-newer --theirs 解+add）后 continue 连报「You must edit all merge conflicts」而 git ls-files -u=0、worktree 零标记——真根因=continue 前置走 `git diff-files --quiet` 校验，被**无关联的 3 件未暂存 daemon churn 面**（satengine face/state/history tick 写）判非零即拒（--quiet 出码吞 --diff-filter=U 过滤面）；正法=churn 吸收进 continue commit（git add <churn faces> + continue 原子连发→秒过 rc0，commit 面自然混入 churn absorb=r854 pre-rebase 范式合法）。择机表第四态：continue 假冲突拒进先 `git ls-files -u`（空）+`git status --porcelain`（有无 ` M` churn）二分——有 churn=本条轻治愈（add+continue）；无 churn 且重试仍拒=r835 三步终局；rebase 起点 unstaged 拒（cannot rebase）=r696 absorb 先行。How to apply：continue 拒进勿直跳 r835 重手术；churn add 前确认 churn 件为本机 daemon live-wins 属主面（他机属主面禁 add）。
'''
with open(P, encoding='utf-8') as f:
    body = f.read()
assert ENTRY.strip()[:60] not in body, 'already appended'
with open(P, 'a', encoding='utf-8') as f:
    f.write(ENTRY)
print('pit appended', len(ENTRY.encode('utf-8')), 'bytes')
