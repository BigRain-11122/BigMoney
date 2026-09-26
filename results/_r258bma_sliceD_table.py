import json
d = json.load(open(r'results\t73_s2\factor_history.json', encoding='utf-8'))
print('face | is_mean | is_ir | oos_mean | oos_ir | gates(v1/v2/v3/a3)')
for k, f in d['faces'].items():
    i, o = f['blocks']['is'], f['blocks']['oos']
    g = f['gates']
    print(f"{k} | {i['ic_mean']:+.4f} | {i['ic_ir']:+.3f} | {o['ic_mean']:+.4f} | "
          f"{o['ic_ir']:+.3f} | {g['v1']}/{g['v2']}/{g['v3']}/{g['a3']}")
print()
print('prereg law_faces:', d['prereg']['law_faces'])
print('trials_N:', d['trials_N'])
print('panel:', d['panel'])
