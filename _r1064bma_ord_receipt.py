import io
p = 'fleet/orders/O-20261018-1810-bm-c.md'
raw = io.open(p, 'r', encoding='utf-8').read()
find = '- [ ] bm-a resume 确认（未暂停机=一行「维持全力」回执）：'
assert raw.count(find) == 1, 'receipt line not found or ambiguous: %d' % raw.count(find)
repl = ('- [x] bm-a resume 确认（未暂停机）：维持全力——bm-a 无暂停史（本轮无 pause 事件），常态满载运转中；'
        'BigMoney loop r1064 收讫 2026-10-18T18:45+08:00（bm-a 多窗并存：BigMoney 循环/记忆治理席/导演席）；'
        '§3 待办提醒收悉：S5-27 帧位重裁/S5-26 ESRGAN 补修/F5-33c 过闸=导演席（BigStream 线）在案候裁，'
        '非本 BigMoney 循环司义务（双公司分工律·r1057 MSG-1200 判读先例）')
raw2 = raw.replace(find, repl)
io.open(p, 'w', encoding='utf-8', newline='').write(raw2)
chk = io.open(p, 'r', encoding='utf-8').read()
assert '- [x] bm-a resume 确认' in chk and find not in chk
print('RECEIPT_OK')
