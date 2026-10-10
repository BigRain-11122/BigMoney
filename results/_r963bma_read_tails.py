import io
for name in ['results/_r963bma_dec_tail.txt', 'results/_r963bma_ord_tail.txt']:
    b = io.open(name, 'rb').read()
    print('=====', name, len(b), 'bytes')
    print(b.decode('utf-8', errors='replace'))
