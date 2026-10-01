import json, os, glob
st = json.load(open('state.json', encoding='utf-8'))
print('state round_no:', st.get('round_no'))
for p in ('results/science_audit.json', 'results/briefings', 'results/self_review'):
    if os.path.isdir(p):
        print(p, '->', sorted(os.listdir(p))[-3:])
    elif os.path.exists(p):
        d = json.load(open(p, encoding='utf-8'))
        h = d.get('history') or []
        print(p, '-> history tail month:', h[-1].get('month') if h else d.get('month'))
    else:
        print(p, 'ABSENT')
