import io

ENTRY = "- [2026-10-05 19:2x r740 bm-a] **0a 平移与 parity 块断言标签交互坑（r735 代码生成律新面·W135 冻结窗实弹·rep 断言 fail-closed 当场治愈零 origin 伤害）**：registry insert 血统的 0a 全量 W 序号平移（W134→W135/W133→W134/W132→W133）同样作用于提取 face 内 parity 块的**断言消息标签**（'W132 row parity drift'→'W133'、'W133'→'W134'）——old_parity 针若按原始 dump 标签（W130/W131/W132/W133）取形则 count==0 恒炸；正法=old_parity 针按 **0a 平移后标签形态**取形（本例 W130/W131/W133/W134——W130/W131 不在平移键集故原样），new_parity 写干净标签（W131..W134）；测量面（extract pass）跑在 0a 模拟后文本上故计数恒真。附：多段 insert 脚本（part1 face 变换+part2 n1 插入）必须严格串行——part2 在 part1 fail 后跑会把 WAVE_CONFIGS 插入只落内存（脚本尾部统一写盘=死在中间即零盘污），幂等重跑可收敛但时序上先 part1 后 part2 勿并行。"

P = 'CODELY.md'
raw = io.open(P, 'rb').read()
txt = raw.decode('utf-8')
assert ENTRY[:40] not in txt, 'entry already present'
if not txt.endswith('\n'):
    txt += '\n'
txt += ENTRY + '\n'
io.open(P, 'wb').write(txt.encode('utf-8'))
chk = io.open(P, 'rb').read().decode('utf-8')
assert ENTRY in chk
print('CODELY entry appended, new bytes:', len(chk.encode('utf-8')))
