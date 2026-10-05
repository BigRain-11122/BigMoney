# -*- coding: utf-8 -*-
"""r739: locate the first byte divergence between the old_parity needle and
the actual W133 face parity block (diagnostic for the insert needle)."""
import io
face = io.open(r".codely-cli\scratch_w133_face_source.txt", encoding="utf-8").read()
i = face.find("assert pf.N1_BANDS[129]")
needle = (
'assert pf.N1_BANDS[129] == {"a": (301_004, 303_003),\n'
'                                    "b_exit": (68_201, 68_400),\n'
'                                    "engine_owner": "bm-a"}, \\\n'
'            "registered W129 row parity drift (r307; bm-a r734)"\n'
'        assert pf.N1_BANDS[130] == {"a": (303_004, 305_003),\n'
'                                    "b_exit": (68_502, 68_701),\n'
'                                    "engine_owner": "bm-a"}, \\\n'
'            "registered W130 row parity drift (r307; bm-a r735)"\n'
'        assert pf.N1_BANDS[131] == {"a": (305_004, 307_003),\n'
'                                    "b_exit": (68_702, 68_901),\n'
'                                    "engine_owner": "bm-a"}, \\\n'
'            "registered W131 row parity drift (r307; bm-a r736)"\n'
'        assert pf.N1_BANDS[132] == {"a": (307_004, 309_003),\n'
'                                    "b_exit": (68_902, 69_101),\n'
'                                    "engine_owner": "bm-a"}, \\\n'
'            "registered W132 row parity drift (r307; bm-a r737)"'
)
actual = face[i:i + len(needle) + 50]
for j, (a, b) in enumerate(zip(needle, actual)):
    if a != b:
        print("diverge at needle char", j)
        print("NEEDLE:", repr(needle[max(0, j - 40):j + 40]))
        print("ACTUAL:", repr(actual[max(0, j - 40):j + 40]))
        break
else:
    print("no divergence in overlap; actual continues:", repr(actual[len(needle):len(needle) + 40]))
print("needle count in face:", face.count(needle))
