import re, os
src = open('scripts/lowamp_p2.py', encoding='utf-8').read()
print('len:', len(src))
print('cmd_ funcs:', sorted(set(re.findall(r'def (cmd_\w+)\(', src))))
print('add_parser:', sorted(set(re.findall(r"add_parser\('([\w-]+)'", src))))
print('e1 mentions:', [m.start() for m in re.finditer(r'[Ee]1', src)][:5])
d = 'results/lowamp_p2'
if os.path.isdir(d):
    for n in sorted(os.listdir(d)):
        p = os.path.join(d, n)
        print(' %s %dB %s' % (n, os.path.getsize(p), __import__('time').strftime('%m-%d %H:%M', __import__('time').localtime(os.path.getmtime(p)))))
