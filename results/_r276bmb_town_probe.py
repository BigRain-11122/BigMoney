import re
src = open('town.html', encoding='utf-8').read()
print('town.html len', len(src))
for pat, label in [
    (r'class="b-name"[^>]*>([^<]+)', 'b-name'),
    (r'data-name="([^"]+)"', 'data-name'),
    (r'<h3[^>]*>([^<]+)</h3>', 'h3'),
    (r'title="([^"]{2,20})"', 'title-attr'),
]:
    hits = re.findall(pat, src)
    print(label, ':', hits[:40])
oc = open('firm/org_chart.md', encoding='utf-8').read()
# department table rows
rows = re.findall(r'^\|.*$', oc, re.M)
print('\norg_chart table rows:', len(rows))
for r in rows[:40]:
    print(r[:160])
