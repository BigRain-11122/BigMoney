import io, re
c = io.open('town.html', encoding='utf-8').read()
out = io.open(r'C:\Users\Administrator\AppData\Local\Temp\town_bldgs.txt', 'w', encoding='utf-8')
# building objects: { id:.., x:.., y:.., w:.., h:.., draw:.., label:.., dept:.., mandate:.., info:fn }
for m in re.finditer(r"\{ id:'([^']+)'[^{}]*?label:'([^']*)'(.{0,1200}?)\}\s*,?\s*\n", c, re.S):
    bid, label, rest = m.group(1), m.group(2), m.group(3)
    dept = re.search(r"dept:'([^']*)'", rest)
    mand = re.search(r"mandate:'([^']*)'", rest)
    out.write('=== %s | %s\n' % (bid, label))
    if dept:
        out.write('DEPT: %s\n' % dept.group(1))
    if mand:
        out.write('MAND: %s\n' % mand.group(1))
    # info blocks (function or string concat)
    im = re.search(r"info\s*[:=]\s*(.{0,900}?)(?:,\s*\}|\},?\s*\n\s*\{|\Z)", rest, re.S)
    if im:
        out.write('INFO-SNIPPET: %s\n' % im.group(1)[:600].replace('\n', ' | '))
    out.write('\n')
out.close()
print('done')
