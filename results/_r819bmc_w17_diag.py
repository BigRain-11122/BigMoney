import re, sys
src = open('scripts/trial_labor_w17.py', encoding='utf-8', errors='replace').read()
for m in re.finditer(r"add_parser\(['\"](\w+)", src):
    print('subcmd:', m.group(1))
for m in re.finditer(r'def (cmd_\w+|main\w*)\(', src):
    print('func:', m.group(1))
# find how autofill invokes it: look for argv hints / shard kwarg
i = src.find('--shard')
print('---shard arg context---')
print(src[i-200:i+300] if i > 0 else 'no --shard found')
