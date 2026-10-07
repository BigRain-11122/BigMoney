import re, json

s = open('results/_orphan_face_probe.json', encoding='utf-8').read()
ours = re.search(r'<<<<<<<.*?\n(.*?)\n=======', s, re.S)
theirs = re.search(r'=======\n(.*?)\n>>>>>>>', s, re.S)

def face_ts(block, label):
    if not block:
        print(label, 'NO BLOCK')
        return
    txt = block.group(1)
    m = re.search(r'"ts"\s*:\s*"([^"]+)"', txt)
    print(label, 'ts=', m.group(1) if m else '?')

face_ts(ours, 'OURS(bm-c@2991aa338):')
face_ts(theirs, 'THEIRS(bm-a@c8a518186):')
