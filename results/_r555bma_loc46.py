"""r555 helper: locate W46 WAVE_CONFIGS entry in scripts/perpetual_faces_n1.py."""
src = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = src.find('46: {"batch"')
print('W46 entry line:', src[:i].count('\n') + 1)
j = src.find('shard_subdir', i)
print(repr(src[j:j + 160]))
print('after-W46 window:')
print(repr(src[j:j + 700]))
print('CRLF:', src.count('\r\n'), 'of', src.count('\n'), 'newlines')
