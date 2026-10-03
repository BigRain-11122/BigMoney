import io, re
c = io.open('town.html', encoding='utf-8').read()
out = io.open(r'C:\Users\Administrator\AppData\Local\Temp\town_struct.txt', 'w', encoding='utf-8')
pats = [r'class="[^"]*build[^"]*"', r'class="[^"]*dept[^"]*"', r'<section',
        r'building', r'楼', r'部门', r'<h[23][^>]*>', r'data-[a-z]+=', r'id="[^"]+"']
for pat in pats:
    out.write('PAT %s = %d\n' % (pat[:44], len(re.findall(pat, c))))
ids = re.findall(r'id="([^"]+)"', c)
out.write('ids: %s\n' % ids[:60])
# dump lines containing CJK building names or dept-ish markers
for i, l in enumerate(c.splitlines()):
    if re.search(r'(楼|部|研究院|中心|小组|委员会|实验室|大厦)', l) and len(l) < 300:
        out.write('%d | %s\n' % (i, l.strip()[:220]))
out.close()
print('ok')
