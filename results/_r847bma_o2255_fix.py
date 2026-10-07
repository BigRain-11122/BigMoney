import io
p = r'fleet\orders\O-20261007-2255-bm-c.md'
t = io.open(p, encoding='utf-8').read()
old = u'`hostname`=SJS20-DESKTOP'
new = u'`hostname`=DASHENG（实读 os.environ COMPUTERNAME）'
assert t.count(old) == 1, t.count(old)
io.open(p, 'w', encoding='utf-8').write(t.replace(old, new))
print('hostname receipt corrected to DASHENG')
