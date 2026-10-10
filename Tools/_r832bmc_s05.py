import subprocess, hashlib, json, os, glob

GT = r'K:\Fluxgroup\FluxGroup'
REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
facts = {}

def run(cmd, cwd=None):
    return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', cwd=cwd)

# fetch group tree (non-blocking on failure -> fall back to last-good ref)
fr = run(['git', '-C', GT, 'fetch', 'origin'], cwd=GT)
facts['gt_fetch_rc'] = fr.returncode

def blob_sha(repo, ref, path, algo):
    r = run(['git', '-C', repo, 'show', f'{ref}:{path}'], cwd=repo)
    if r.returncode != 0 or not r.stdout:
        return None
    b = r.stdout.encode('utf-8', errors='replace')
    return hashlib.sha256(b).hexdigest() if algo == 'sha256' else hashlib.sha1(b).hexdigest()

# DEC sha256 (state holds b87a92b1...)
facts['dec_sha'] = blob_sha(GT, 'origin/main', 'docs/decisions.md', 'sha256')
# ORD sha1 (state holds e286f842...)
facts['ord_sha'] = blob_sha(GT, 'origin/main', 'docs/orders.md', 'sha1')
facts['gt_head'] = run(['git', '-C', GT, 'rev-parse', 'origin/main'], cwd=GT).stdout.strip()

# fleet orders inventory (names only)
orders_dir = os.path.join(REPO, 'fleet', 'orders')
facts['order_files'] = sorted(os.path.basename(f) for f in glob.glob(os.path.join(orders_dir, 'O-*.md')))

# heartbeat orders_ack
hb_path = os.path.join(REPO, 'fleet', 'machines', 'bm-c.json')
acks = []
if os.path.exists(hb_path):
    hb = json.load(open(hb_path, encoding='utf-8'))
    acks = hb.get('orders_ack', [])
facts['orders_ack'] = acks
facts['orders_ack_n'] = len(acks) if isinstance(acks, list) else acks
unacked = [o for o in facts['order_files'] if o.replace('O-', '').replace('.md', '') not in [a.replace('O-', '').replace('.md', '') for a in (acks if isinstance(acks, list) else [])]]
facts['unacked'] = unacked

# inbox unread
inbox_dir = os.path.join(REPO, 'fleet', 'inbox')
inbox_files = [os.path.basename(f) for f in glob.glob(os.path.join(inbox_dir, '*')) if os.path.isfile(f)]
facts['inbox_unread'] = inbox_files

out = os.path.join(REPO, 'results', '_r832bmc_s05_facts.json')
json.dump(facts, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: facts[k] for k in ['gt_fetch_rc', 'dec_sha', 'ord_sha', 'gt_head', 'orders_ack_n', 'unacked', 'inbox_unread']}, ensure_ascii=False))

