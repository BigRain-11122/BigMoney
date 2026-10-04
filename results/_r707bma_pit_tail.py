import io
b = io.open('research/pit-engine.md', 'rb').read()
print('size', len(b))
tail = b[-500:]
print(repr(tail))
