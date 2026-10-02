import sys

path = 'Tools/iteration_prompt.txt'
with open(path, 'rb') as f:
    raw = f.read()
t = raw.decode('utf-8')

old = 'S0 集成/收口 reland 环律（MSG-2026-10-03-0612 实弹·bm-a r611 立法）：撤-FF-重落/外科重放环 payload 含共享池面（runnable_pool.json/crash_fuse.json/pool 车道镜像族）时禁整文件重放——重放前对该面 per-face max-merge vs origin blob（owner_since/cleared_ts 等时间戳 newer-wins），或重放后立刻 python scripts\\merge_lane_views.py sync_face 幂等补 settle（实弹：陈旧 settle 快照整文件重放致 NULLS owner_since 回退 20min 破接管门→假接管评估窗 7.6min·crash fuse 侥幸拦截零双烧）；'

new = 'S0 集成/收口 reland 环律（MSG-2026-10-03-0612 实弹·bm-a r611 立法+MSG-0640 face 级扩展·bm-a r612）：撤-FF-重落/外科重放环 payload 含共享池面（runnable_pool.json/crash_fuse.json/pool 车道镜像族）时禁整文件重放——重放前对该面 per-face max-merge vs origin blob（owner_since/cleared_ts 等时间戳 newer-wins），或重放后立刻 python scripts\\merge_lane_views.py sync_face 幂等补 settle（实弹：陈旧 settle 快照整文件重放致 NULLS owner_since 回退 20min 破接管门→假接管评估窗 7.6min·crash fuse 侥幸拦截零双烧）；他机属主面（含代码面）origin-verbatim 恢复=每面执行时点 git rev-parse origin/main 后 git show <执行时点sha>:<path> 实取（或恢复后立即与 origin tip blob 恒等断言）——禁用环早先 fetch 缓存基座上已重建的树面直接重 commit（多环序列环 2+ 即使基座 CAS 到新 tip，树面仍是环 1 时点重建的陈旧面=重放即 revert；实弹：r609 环重放陈旧 fund_quality_p1_probe.py 快照=对 bm-b r604 修正的精确镜像 revert·4min 窗·bm-b r606 治愈）；'

n = t.count(old)
assert n == 1, 'occurrence count != 1: %d' % n
t2 = t.replace(old, new)
assert t2.count('MSG-0640 face 级扩展') == 1
assert len(t2) > len(t)
with open(path, 'wb') as f:
    f.write(t2.encode('utf-8'))
print('OK old_len=%d new_len=%d file_bytes=%d' % (len(old), len(new), len(t2.encode('utf-8'))))
