import io
txt = open(r'results/_r936bmb_orders_face.md', encoding='utf-8').read()
lines = txt.splitlines()
out = io.open(r'results/_r936bmb_orders_new.txt', 'w', encoding='utf-8')
for l in lines[-60:]:
    out.write(l + '\n')
out.close()
print('total lines:', len(lines))
