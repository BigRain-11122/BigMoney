import re
draft = open('results/_r464bma_w13_runner_draft.py', encoding='utf-8').read()
for m in re.finditer(r'add_argument\("([a-z_]+)"', draft):
    print('arg:', m.group(1))
i = draft.find('def main(')
print(draft[i:i+1500])
