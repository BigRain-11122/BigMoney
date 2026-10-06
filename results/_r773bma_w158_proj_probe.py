# -*- coding: utf-8 -*-
"""r773 probe2: read the W156/W155 entries' next-wave projection prose verbatim
to pin the canonical form (is the malformed-window face an inherited pattern
or an r772 corruption needing a same-window heal?)."""
import io

src = io.open("scripts/perpetual_faces_n1.py", encoding="utf-8", newline="").read()
for w in (156, 155):
    k = src.find(f'{w}: {{"batch"')
    m = src.find('"engine_owner": "bm-a"},', k) + len('"engine_owner": "bm-a"},')
    e = src[k:m]
    tag = f"W{w+1}+ projection"
    i = e.find(tag)
    print(f"=== W{w} entry, '{tag}' prose ===")
    if i < 0:
        print("  (not found)")
        # try the alternative: 'W157+ projection' etc.
        import re
        for mm in re.finditer(r"W\d+\+ projection", e):
            print("  found alt:", mm.group(0))
            j = mm.start()
            print(e[j:j+380].replace("\\n", " | "))
            break
    else:
        print(e[i:i+380].replace("\\n", " | "))
    print()
# also check the W157 entry prose again verbatim
k = src.find('157: {"batch"')
m = src.find('"engine_owner": "bm-a"},', k) + len('"engine_owner": "bm-a"},')
e7 = src[k:m]
import re
for mm in re.finditer(r"W\d+\+ projection", e7):
    print("=== W157 entry:", mm.group(0))
    print(e7[mm.start():mm.start()+380].replace("\\n", " | "))
