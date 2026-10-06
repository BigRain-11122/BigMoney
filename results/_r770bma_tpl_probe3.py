# r770 bm-a probe 3: token counts for the corrected generator
import re

s = open("results/_r768bma_w155_freeze_edits.py", "rb").read().decode("utf-8")

for tok in ["w156", "W156", "156", "357_804..359_803", "358_004..358_203",
            "r768 freeze", "r768 bm-a freeze", "freeze, seat MSG",
            "seventy-first", "rows 70", "rows 144", "ONE HUNDRED-AND-FORTY-FIFTH",
            "fourteenth", "1fedffbe4", "MSG-2026-10-06-0943", "734,811",
            "336,720", "3095cb47e", "r767", "r768", "_r767bma", "_r768bma",
            "355_604..357_603", "355_804..356_003", "355_604..355_803",
            "range(355_804, 357_804)", "range(357_804, 358_004)",
            "(355_804, 357_803)", "(357_804, 358_003)", "355_803+1", "357_803+1",
            "355_804", "357_804", "153", "W155", "W154", "w155", "w154",
            "len(pf.N1_BANDS) == 153", "N1_BANDS 153 rows", "r768 gate",
            "r768 sec8", "n1_w154", "behind-2"]:
    print(f"{tok!r}: {s.count(tok)}")

print()
print("=== 'r768' contexts ===")
for m in re.finditer(r"r768", s):
    a, b = max(0, m.start() - 50), m.end() + 50
    print(repr(s[a:b]))
