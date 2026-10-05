import io
src = io.open('results/_r741bmb_merge_resolve_w2.py', encoding='utf-8').read()
s2 = src.replace('_r741bmb_merge_resolve.w2.json', '_r740bma_merge_resolve.json')
s2 = s2.replace('r741 bm-b merge window (close-push claw-block behind-6 close-window daemon race)',
                'r740 bm-a merge window (dead r739 tail absorb + behind-9 integration)')
s2 = s2.replace('# r738 bm-b merge resolver', '# r741 bm-b merge resolver bloodline -> r740 bm-a')
assert s2 != src, 'no replacement applied'
assert s2.count('_r740bma_merge_resolve.json') == 1, 'receipt name count'
assert 'r740 bm-a merge window' in s2, 'round label missing'
io.open('results/_r740bma_merge_resolve.py', 'w', encoding='utf-8', newline='\n').write(s2)
print('written bytes:', len(s2.encode('utf-8')))
