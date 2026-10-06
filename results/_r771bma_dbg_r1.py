# -*- coding: utf-8 -*-
"""r771 bm-a debug: post-VM r1 delivery segment actual form."""
import io, json

RT = json.load(io.open(r"results/_r771bma_w155_runtime_strings.json", encoding="utf-8"))
VM = [
    ("r768", "r769"), ("r767", "r768"),
    ("W155", "W156"), ("W154", "W155"),
    ("w155", "w156"), ("w154", "w155"),
]
s = RT["r1"]
# minimal VM application (just waves+rounds as in the real pipeline order after full VM)
# instead re-apply the full pipeline phases relevant to the segment
s = s.replace("W156", "@PW@").replace("w156", "@Pw@")
for old, new in VM:
    s = s.replace(old, new)
s = s.replace("155", "156").replace("154", "155")
s = s.replace("@PW@", "W157").replace("@Pw@", "w157")
i = s.find("delivery window")
print(repr(s[max(0, i - 300):i + 400]))
