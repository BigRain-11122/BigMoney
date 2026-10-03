# r627 bm-a: inspect moneyflow collector endpoints/headers/fetch logic (source-block diagnosis, lane R63)
import re
src = open('scripts/update_moneyflow.py', encoding='utf-8').read()
print('len:', len(src))
for m in re.finditer(r'https?://[^\s\'\")]+', src):
    print('URL:', m.group(0))
for m in re.finditer(r'headers\s*=\s*\{[^}]{0,400}\}', src, re.S):
    print('HDR:', m.group(0)[:400])
# requests usage
for m in re.finditer(r'(requests\.(get|post)\([^\n]{0,200})', src):
    print('REQ:', m.group(1)[:200])
# sleep / retry logic
for m in re.finditer(r'(def [a-z_]+\()', src):
    print('DEF:', m.group(1))
