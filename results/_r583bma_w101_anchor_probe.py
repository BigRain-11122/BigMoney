# r583 bm-a: probe anchors for W101 freeze edits
import subprocess

def show(p):
    return subprocess.run(['git', 'show', 'HEAD:%s' % p], capture_output=True).stdout.decode('utf-8')

pf = show('scripts/perpetual_faces.py')
i = pf.find('99: {"a"')
print('--- pf W99 row context ---')
print(pf[i-120:i+400])
n1 = show('scripts/perpetual_faces_n1.py')
j = n1.find('"batch": "PERPETUAL-N1-W99"')
print('--- n1 W99 config entry ---')
print(n1[j-100:j+700])
canon = show('research/PERPETUAL_FACES.md')
k = canon.find('\u6bcf\u6ce2 finalize')
print('--- canon sec.5 anchor ---')
print(repr(canon[k-40:k+80]))
m = n1.find('W99 materializer face')
print('--- n1 W99 summary segment tail ---')
print(repr(n1[m-200:m+140]))
t = n1.find('T-141 s2 lane face')
print('--- T-141 anchor ---')
print(repr(n1[t-60:t+80]))
