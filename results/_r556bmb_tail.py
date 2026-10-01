b = open('research/PERPETUAL_FACES.md', 'rb').read().decode('utf-8')
i = b.find('N1 波47')
j = b.find('\n', i)
row = b[i:j]
print('W47 row tail 300 chars:')
print(repr(row[-300:]))
