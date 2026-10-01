import io
t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = t.find('42: {"batch"')
print('W42 config entry found at char', i)
print(t[i:i+2400])
