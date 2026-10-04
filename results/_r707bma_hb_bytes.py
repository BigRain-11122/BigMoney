import io
b = io.open('fleet/machines/bm-a.json', 'rb').read()
i = b.find(b'next_milestone')
seg = b[i:i+180]
print(repr(seg))
# try direct utf-8 decode of the value region
print('utf8-decode-ok:', end=' ')
try:
    s = seg.decode('utf-8')
    print(True, s[:150])
except Exception as e:
    print(False, e)
