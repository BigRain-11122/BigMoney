b = open('research/PERPETUAL_N1_W97_PREREG.md', 'rb').read()
i = b.find(b'\xa7\x37')  # section sign 7 utf-8 starts with 0xc2\xa7
s = b.decode('utf-8')
i7 = s.find('\u00a77')
i8 = s.find('\u00a78')
k = s.find('\u8dd1\u524d\u51bb\u7ed3')  # 跑前冻结
print('S7 block repr:')
print(repr(s[i7-3:k]))
print()
print('S8 block repr:')
print(repr(s[i8-3:i7-3+0] or s[i8-3:k]))
