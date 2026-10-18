# r1054 postscript: inbox moves (r1032 shutil.move law) + state W267-splice-midround disclosure
import os, shutil, json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
msgs = ['MSG-20261018-0845-bmb-audition-redrop-mixsample.md',
        'MSG-20261018-1035-bmb-rootfix.md',
        'MSG-20261018-1137-bmb-canon-installed.md']
moved = []
for m in msgs:
    src = os.path.join(ROOT, 'fleet', 'inbox', m)
    dst = os.path.join(ROOT, 'fleet', 'inbox', 'processed', m)
    if os.path.exists(src):
        shutil.move(src, dst)
        assert os.path.exists(dst) and not os.path.exists(src)
        moved.append(m)
print('moved:', moved)

# state postscript: W267 splice+self-burn landed mid-closeout
sp = os.path.join(ROOT, 'state-bm-a.json')
st = json.load(open(sp, encoding='utf-8'))
st['notes_r1054'] = st.get('notes_r1054','') + ("(6) 收口窗中途门面更新（rebase 11:5x 检出）：bm-c r1088 落 W267 五面 splice（7b9e937737·bands A 602_701..604_700/B 604_701..604_900 注册入 pf+n1·setwave ROOT CURE 同窗）+ 自燃 12/12 分片（99166404f2+eb5c74dbf7 六片×2）→ W267 chain 仅余 finalize（bm-c 下窗）→ W268 门槛=finalize+席面点名；本轮报告行「splice 未落」=11:45 探针时点真值、11:5x 落地后按本 postscript 勘注（sequence-honest）；rebase 21 UU 全=运行时活面 newer-wins 本机 11:49-52 derive 胜。")
st['next_milestone'] = 'W268 波窗（候 bm-c W267 finalize·仅余一步·≤24h 观察面）+ MF 封锁周一裁决 <=10-19'
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.load(open(sp, encoding='utf-8'))
print('state postscript OK')
