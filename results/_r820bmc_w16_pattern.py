src = open('scripts/trial_labor_w16.py', encoding='utf-8').read()
i = src.find('def cmd_screen(')
seg = src[i:i+4000]
j = seg.find('state = ')
print('=== W16 cmd_screen state packing ===')
print(seg[j:j+700] if j >= 0 else 'state= not found')
k = seg.find('GRAMMAR')
print('=== GRAMMAR face in W16 cmd_screen ===')
while k != -1 and k < 4000:
    print(seg[max(0,k-100):k+120].replace('\n', ' | ')[:220])
    print('---')
    k = seg.find('GRAMMAR', k+1)
