import json

# strip the trailing newline I added (HEAD blobs have none for these two)
for path, eol in [('results/runnable_pool.json', '\r\n'), ('fleet/tasks/T-2026-09-25-46-P1.json', '\n')]:
    b = open(path, 'rb').read()
    if b.endswith(eol.encode()):
        open(path, 'rb+b').write() if False else open(path, 'wb').write(b[:-len(eol)])
    json.load(open(path, encoding='utf-8'))  # sanity
    print(path, 'trailing stripped, ends with', repr(open(path, 'rb').read()[-4:]))
