import re
log = open('results/_r1041bma_s6_log.txt', encoding='utf-8').read()

def seg(name):
    parts = log.split('===== %s =====' % name)
    if len(parts) < 2:
        return ''
    return parts[1].split('=====')[0]

m = re.search(r'"verdict":\s*"(\w+)"', seg('py_watermark'))
print('py_wm verdict =', m.group(1) if m else '?')

for line in seg('token_meter').splitlines():
    s = line.strip()
    if s and ('delta' in s or 'total' in s or 'usage' in s.lower()):
        print('token:', s[:130])

lp = [l for l in seg('live_paper').splitlines() if l.strip()]
print('live_paper tail:', lp[-1][:130] if lp else '(empty)')

dp = [l for l in seg('update_daily').splitlines() if l.strip()]
print('update_daily tail:', dp[-1][:130] if dp else '(empty)')

dr = [l for l in seg('daily_report').splitlines() if l.strip()]
print('daily_report tail:', dr[-1][:130] if dr else '(empty)')
