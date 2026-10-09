import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
n1 = open(r"scripts\perpetual_faces_n1.py", encoding="utf-8",
          newline="").read().replace("\r\n", "\n")
pts = [
    ("W193 face", "    # --- W193 materializer face"),
    ("W199 face", "    # --- W199 materializer face"),
    ("W200 face", "    # --- W200 materializer face"),
    ("W201 face", "    # --- W201 materializer face"),
    ("claim W200", '          "+ W200 materializer face'),
    ("claim W201", '          "+ W201 materializer face'),
    ("claim T141", '          "+ T-141 s2 "'),
    ("T141 marker", "    # --- T-141 s2 lane face"),
    ("cfg W200", '    200: {"batch": "PERPETUAL-N1-W200",'),
    ("cfg W201", '    201: {"batch": "PERPETUAL-N1-W201",'),
]
for name, needle in pts:
    print("%-14s pos=%d count=%d" % (name, n1.find(needle), n1.count(needle)))
i = n1.find("    # --- W201 materializer face")
j = n1.find("    _set_wave(2)", i)
print("mat201 chunk len:", j + len("    _set_wave(2)") - i)
