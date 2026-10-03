import json, time, urllib.request

BASE = 'http://127.0.0.1:11434'
MODEL = 'qwen3-8b-ud:q4_k_xl'

def post(path, payload, timeout=300):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

# 1) load with keep_alive=-1 (resident) + measure tok/s
t0 = time.time()
r = post('/api/generate', {
    'model': MODEL,
    'prompt': 'Write a one-paragraph summary of what a quant trading firm does.',
    'stream': False,
    'think': False,
    'keep_alive': -1,
})
wall = time.time() - t0
ec = r.get('eval_count', 0)
ed = r.get('eval_duration', 0)
tok_s = (ec / (ed / 1e9)) if ed else 0
print('model:', MODEL)
print('load+gen wall: %.1fs' % wall)
print('prompt_eval: count=%s dur=%s' % (r.get('prompt_eval_count'), r.get('prompt_eval_duration')))
print('eval_count=%s eval_duration=%s -> %.1f tok/s' % (ec, ed, tok_s))
print('done_reason:', r.get('done_reason'))

# 2) resident state
ps = post('/api/ps', {}) if False else None
import urllib.request as u
with u.urlopen(BASE + '/api/ps', timeout=30) as resp:
    ps = json.loads(resp.read().decode())
print('ps:', json.dumps(ps, ensure_ascii=False))
