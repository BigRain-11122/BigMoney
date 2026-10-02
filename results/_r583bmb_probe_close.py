d = open('scripts/perpetual_faces.py', 'rb').read()
i = d.find('99: {"a": (241_004'.encode())
k = d.find(b'engine_owner', i)
ke = d.find(b'\n', k) + 1
print('pf W99 close line:', repr(d[k:ke]))
d2 = open('scripts/perpetual_faces_n1.py', 'rb').read()
j = d2.find('"shard_subdir": "n1_w99"'.encode())
m = d2.find(b'engine_owner', j)
me = d2.find(b'\n', m) + 1
print('n1 W99 cfg close line:', repr(d2[m:me]))
# what follows each close (next 30 bytes)
print('pf after close:', repr(d[ke:ke+30]))
print('n1 after close:', repr(d2[me:me+30]))
