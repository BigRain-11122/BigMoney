src = open('scripts/merge_lane_views.py', encoding='utf-8').read()
j = src.find('def _cmd_resolve')
seg = src[j:j+3200]
k = seg.find('blobs[key] = data')
print(seg[k:k+1400])
