import io

COD = 'CODELY.md'
ARC = 'research/memory-archive/202609.md'

# --- read CODELY bytes, locate the two full lines by keywords ---
raw = open(COD, 'rb').read()
text = raw.decode('utf-8')
eol = '\r\n'
lines = text.split(eol)
assert text.endswith(eol)

kw1 = 'tick 自提交落点在 fire 后'
kw2 = 'PowerShell ConvertFrom-Json 会对合法'
idx1 = idx2 = None
for i, l in enumerate(lines):
    if kw1 in l and idx1 is None and l.strip().startswith('- ['):
        idx1 = i
    if kw2 in l and idx2 is None and l.strip().startswith('- ['):
        idx2 = i
assert idx1 is not None and idx2 is not None, (idx1, idx2)
full1, full2 = lines[idx1], lines[idx2]
print('full1 line', idx1, len(full1.encode('utf-8')), 'B | full2 line', idx2, len(full2.encode('utf-8')), 'B')

stub1 = '- [2026-09-27 16:1x r332 bm-b] 坑律（二十批外迁·指针）：autofill tick 自提交落点在 fire 后 ~2.5-3min（:X0:02 fire→:X2:5x 落 commit），轮首 :X1 读数到 :X5 行动已陈旧——丢弃类 git 动作前必现读 git log -1+status 与轮首读数比对，已变=弃手工丢弃改走 rebase 重放+union 收敛。全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十批』节。'
stub2 = '- [2026-09-27 16:2x r335 bm-a] 坑律（二十批外迁·指针）：PowerShell ConvertFrom-Json 会对合法 JSON 件假报 parse 失败——板面/多件扫描的权威解析一律用 python，PS 结果只作初筛。全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十批』节。'
lines[idx1] = stub1
lines[idx2] = stub2

new_entry = '- [2026-09-27 16:5x r338 bm-a] 坑律：**共享 JSON 面（runnable_pool/fleet 票板等）python 追加编辑必须先探原写者格式逐字节复刻——json.dump 默认 LF+自选 indent 会整件重写（r338 实弹：runnable_pool.json 原生 CRLF 被 LF 重写=5,474 行 churn；T-46 票面 indent1 被写 indent2=41 行 churn），最小 diff 破功+跨机 rebase 冲突面放大**。正典=①改前 git show HEAD:<path> 取 blob 定 EOL/indent 深度/尾换行有无；②CRLF 件=json.dumps(...,ensure_ascii=False,indent=N) 字符串 .replace(\'\\n\',\'\\r\\n\')+newline=\'\' 落盘+按 blob 尾态补/省尾换行；③写后 git diff --stat 核 churn 面（≈目标行数×3 以上=格式漂移立即重写）。指针=results/_r338bma_fmt_check.py+_r338bma_fmt_fix.py+commit r338。'
lines.append(new_entry)

out = eol.join(lines)
open(COD, 'wb').write(out.encode('utf-8'))
print('CODELY.md new size:', len(out.encode('utf-8')), 'B')

# --- archive: append 20th-batch section with verbatim fulls ---
araw = open(ARC, 'rb').read()
arc_eol = '\r\n' if araw.count(b'\r\n') > (araw.count(b'\n') - araw.count(b'\r\n')) else '\n'
section_title = '## 坑律归档 2026-09-27 二十批（r338 bm-a·水位律当窗整编：新坑律 append 后 ~10.1KB 触发·两全文行级零丢失外迁）'
block = arc_eol.join([section_title, full1, full2, ''])
if not araw.endswith((b'\n', b'\r')):
    araw += arc_eol.encode()
elif not araw.endswith(arc_eol.encode()):
    araw += arc_eol.encode()
araw += block.encode('utf-8') + arc_eol.encode()
open(ARC, 'wb').write(araw)
print('archive appended, new size:', len(araw), 'B, eol=', repr(arc_eol))

# --- zero-loss verification: full texts present verbatim in archive ---
atext = open(ARC, encoding='utf-8').read()
ok1 = full1 in atext
ok2 = full2 in atext
ctext = open(COD, encoding='utf-8').read()
ok3 = kw1 not in ctext.split('（二十批外迁·指针）')[1] if '（二十批外迁·指针）' in ctext else True
print('verbatim-in-archive full1:', ok1, '| full2:', ok2)
assert ok1 and ok2
print('DONE')
