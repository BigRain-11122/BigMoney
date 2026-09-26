b = open('logs/iteration-loop/round_reports.md', 'rb').read()
t = b.decode('utf-8').splitlines()
for l in t[-2:]:
    print(l)
    print('---')
