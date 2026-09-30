import json, re
kit = open('results/_r463bma_w13_layer_kit.py', encoding='utf-8').read()
# run the kit's build_sumn_anchor to get actual keys? No - static scan for anchor key names
i = kit.find('def build_sumn_anchor')
seg = kit[i:kit.find('def ', i+10)]
keys = re.findall(r'"([a-z0-9_]+)":', seg)
print('anchor keys:', keys)
# check the r456 facts json for core48 spread
import glob
for p in glob.glob('results/_r456bma*'):
    print('r456 artifact:', p)
# probe facts file used by kit _load_facts
j = kit.find('def _load_facts')
print(kit[j:j+500])
