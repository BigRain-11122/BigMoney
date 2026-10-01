"""r555 helper: dump the W46 materializer leg END region (for W47 leg insertion point)."""
src = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = src.find('--- W46 materializer face')
# find the end: the next '# ---' comment block or the finally after the leg
k = src.find('# --- T-141', i)
if k < 0:
    k = src.find('claim exempt', i)
print('next block at', k)
print(src[k - 1600:k + 100])
