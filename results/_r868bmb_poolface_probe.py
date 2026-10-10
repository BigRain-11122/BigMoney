"""r868 pool-face probe 3 (read-only): exact last-entry opening bytes."""
txt = open('results/runnable_pool.json', encoding='utf-8').read()
i = txt.rfind('"id": "THERMO-OVERLAY-P1-BURN"')
# walk back to the opening brace of this entry
j = txt.rfind('{', 0, i)
print('bytes before id line:', repr(txt[j - 20:j + 60]))
# how many entries open with 2sp vs 3sp
import re
opens2 = re.findall(r'\n  \{\n   "id":', txt)
opens3 = re.findall(r'\n   \{\n   "id":', txt)
opens_other = re.findall(r'\n( +)\{\n +?"id":', txt)
from collections import Counter
print('open-brace indent histogram:', Counter(len(m) for m in opens_other))
# separator between entries
k = txt.find('",\n  },\n   {', 0)
sep1 = re.findall(r'\n  \},\n   \{', txt)
sep2 = re.findall(r'\n  \},\n  \{', txt)
print('sep 2sp-close/3sp-open:', len(sep1), '| sep 2sp-close/2sp-open:', len(sep2))
