"""r555 helper: show exact residue between new dict close and PREREG line."""
src = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = src.find('"engine_owner": "bm-a"},\n                       }\n')
j = src.find('PREREG = WAVE_CONFIGS')
print(repr(src[i:j]))
