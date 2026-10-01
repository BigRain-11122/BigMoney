"""r555 helper: find selftest PASS summary construction."""
src = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = src.find('T-141 s2 engine-lane claim exemption')
print('exemption text found at:', i)
# search for the summary print
j = src.find('selftest: PASS')
print('PASS print at:', j)
print(repr(src[j:j + 400]))
