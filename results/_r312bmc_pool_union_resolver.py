# r312 bm-c rebase resolver: results/runnable_pool.json tail-union.
# Both sides appended DISJOINT new entry sets at the end of the entries
# array (r294 conflict-region union law; id sets have zero overlap):
#   HEAD (origin)  = REFINE-REV-STOCK-CENSUS-SHARD-0..5 (bm-a T-139)
#                    + STOCKFURN-REV/LOWAMP/MOM-AKSHARE-* (bm-b T-139)
#   mine (e4f54ed64) = PERPETUAL-N1-W8-SHARD-0..11 (bm-c W8 supply)
# The shared `{` line opens HEAD's first entry; the shared `}` line
# closes mine's last -- so the union needs a `},` + `{` separator pair
# inserted between HEAD's content and mine. Format preserved: raw line
# surgery only (r509 law), CRLF kept, no re-serialization.
import json

P = 'results/runnable_pool.json'
raw = open(P, 'rb').read()
text = raw.decode('utf-8')
lines = text.split('\n')

START = None   # line with '<<<<<<< HEAD'
SEP = None    # '|||||||'
MID = None    # '======='
END = None    # '>>>>>>> e4f54ed64'
for i, l in enumerate(lines):
    ls = l.strip()
    if ls.startswith('<<<<<<<'):
        START = i
    elif ls.startswith('|||||||') and SEP is None and START is not None:
        SEP = i
    elif ls.startswith('=======') and MID is None and START is not None:
        MID = i
    elif ls.startswith('>>>>>>>') and START is not None:
        END = i
        break
assert None not in (START, SEP, MID, END), f'markers missing {(START, SEP, MID, END)}'

head_side = lines[START + 1: SEP]          # origin entries content
base_side = lines[SEP + 1: MID]            # expected empty
mine_side = lines[MID + 1: END]           # W8 entries content
assert base_side == [] or all(not s.strip() for s in base_side), \
    f'unexpected non-empty base side: {len(base_side)} lines'

assert head_side[0].lstrip().startswith('"id": "REFINE-REV-STOCK-CENSUS-SHARD-0"'), \
    'HEAD side shape drift (first line)'
assert head_side[-1].strip() == ']', 'HEAD side tail shape drift'
assert mine_side[0].lstrip().startswith('"id": "PERPETUAL-N1-W8-SHARD-0"'), \
    'mine side shape drift (first line)'

sep_pair = ['},\r', '{\r']                  # close HEAD's last entry, open mine's first
resolved = (lines[:START] + head_side + sep_pair + mine_side
            + lines[END + 1:])
out = '\n'.join(resolved)
open(P, 'wb').write(out.encode('utf-8'))

# parse-verify + id-family assertions
data = json.loads(out)
entries = data['entries']
ids = [e['id'] for e in entries]
assert 'REFINE-REV-STOCK-CENSUS-SHARD-0' in ids, 'census family lost'
assert 'STOCKFURN-REV-AKSHARE-SHARD-0' in ids, 'stockfurn family lost'
w8 = [i for i in ids if i.startswith('PERPETUAL-N1-W8-SHARD-')]
assert len(w8) == 12, f'W8 entries {len(w8)} != 12'
# duplicate-id guard (union must not double any entry)
assert len(ids) == len(set(ids)), 'duplicate entry ids after union'
# W7 shard-10 (the OTHER one, wave 7) must be done post-merge
w7s10 = [e for e in entries if e['id'] == 'PERPETUAL-N1-W7-SHARD-10'][0]
assert w7s10['status'] == 'done', 'W7 SHARD-10 flip lost in merge'
print(f'union resolved: {len(ids)} entries '
      f'(+{len(head_side) and len(mine_side)} lines both sides kept), '
      f'W8 12/{len(w8)}, W7-SHARD-10 done, zero markers')
