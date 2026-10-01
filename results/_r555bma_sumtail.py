"""r555 helper: dump exact source of the summary tail region."""
src = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = src.find('pre-claim exempt face')
k = src.rfind('W46 materializer face', 0, i)
print(repr(src[k - 100:i + 60]))
