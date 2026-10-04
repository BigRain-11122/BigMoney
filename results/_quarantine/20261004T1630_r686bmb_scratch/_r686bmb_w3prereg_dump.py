"""r686 bm-b: dump MASS_TRIAL_W3_PREREG sections to UTF-8 file for reading."""
import io

txt = open("research/MASS_TRIAL_W3_PREREG.md", encoding="utf-8").read()
i4 = txt.find("## ")
# find section boundaries by header pattern
import re
secs = [(m.start(), m.group(0)) for m in re.finditer(r"## [^\n]+", txt)]
bounds = [(secs[k][1], secs[k][0], secs[k + 1][0] if k + 1 < len(secs)
           else len(txt)) for k in range(len(secs))]
out = []
for h, a, b in bounds:
    out.append(txt[a:b])
open("results/_r686bmb_w3prereg_secs.txt", "w", encoding="utf-8").write(
    "\n\n".join(out))
print("sections:", len(out))
