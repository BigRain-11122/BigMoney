# r895 bm-a leg: pit entry direct-write to pit-engine-finalize.md (r666 exception: main at cap 30,922B>30,720B)
P = 'research/pit-engine-finalize.md'
src = open(P, encoding='utf-8').read()
assert 'materializer 自动 finalize' not in src[-2500:], 'already appended'
entry = '''
- [2026-10-09 02:2x r895 bm-a] **引擎 materializer 自动 finalize 的完成判定=嵌套面读（W191 首例实弹·r752 三恒等门判读续篇）**：W191 12/12 烧完引擎 materializer 02:02 自动合成落账（ledger 块在 science_gates.ledger 嵌套面·r459 律）——「finalize 是否待跑」判定必须三面任一：status 子命令 / 嵌套 science_gates.ledger / sg.ledger_head()；禁只读顶层 trials_ledger 键断「未落账」（本窗实弹：顶层读出 NO ledger block 差点误判 finalize pending→盲跑 finalize；pit-95 守卫+finalize_already_landed r459 嵌套面读核（源码级核验）双拦零事故）。materializer=W191 五面冻结自带机制（n1 selftest 已验）——引擎波 session 侧 finalize=多余动作；恢复轮「finalize one-pass next round」指针在 materializer 机制下=已被自动兑现，收尾只余 §7/§8 回填+commit。How to apply：引擎波 12/12 后 finalize 判定先 status 后动手；死尾收编探针的 G4 output-absent 门要核嵌套面（死会话探针 01:5x 时点 G4=True 正确·02:02 materializer 落账后失效=时点敏感）。
'''
with open(P, 'a', encoding='utf-8', newline='') as f:
    f.write(entry)
new = open(P, encoding='utf-8').read().encode()
print('pit appended', len(entry.encode()), 'bytes; new size', len(new))
