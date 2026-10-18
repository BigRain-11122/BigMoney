# r1055 fixface: correct report line + sync notes (rc.log = blanket *.log gitignored local evidence, NOT an origin artifact)
import json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'

rp = ROOT + r'\round_reports-bm-a.md'
txt = open(rp, encoding='utf-8', errors='replace').read()
bad = '本地未达 origin commit=0（closeout push 7d515de7bc 后 fetch+ls-tree 自证·关键件 5/5 在 origin）'
good = '本地未达 origin commit=0（closeout push 7d515de7bc 后 fetch+ls-tree 自证·关键件 4/5 在 origin——第 5 件 results/_r1055bma_s6chain_rc.log=.gitignore L131 恒等 *.log 本地证据面·r1053/r1054 同款 rc.log 均未跟踪·rc 证据=会话控制台 43 行 rc0+本地 log 双面）'
assert bad in txt, 'report line anchor not found'
txt = txt.replace(bad, good)
open(rp, 'w', encoding='utf-8', newline='').write(txt)

for path in (ROOT + r'\state-bm-a.json', ROOT + r'\fleet\machines\bm-a.json'):
    d = json.load(open(path, encoding='utf-8'))
    if 'sync' in d:
        d['sync']['note'] = 'r1055 closeout push 7d515de7bc delivered; fetch+ls-tree self-verified (4/5 origin artifacts; 5th=results/_r1055bma_s6chain_rc.log blanket-*.log gitignored local evidence per r1053/r1054 face); report-line commit follows'
        d['push_verified']['note'] = 'r1055 closeout delivered (7d515de7bc); ls-tree 4/5 key origin artifacts; rc.log=gitignored local evidence (*.log rule); postscript report line + sync faces ride next push (next-round S0 re-verify)'
    json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('FIXFACE OK')
