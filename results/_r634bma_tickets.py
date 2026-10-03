import json, os, glob
for f in sorted(glob.glob('fleet/tasks/*.json')):
    try:
        j = json.load(open(f, encoding='utf-8'))
        st = j.get('status', '?')
        if st in ('open', 'claimed', 'in_progress'):
            t = j.get('title') or j.get('type') or '?'
            print(f"{os.path.basename(f)}: {st} :: {j.get('id','?')} :: {str(t)[:80]} :: claimed_by={j.get('claimed_by','-')}")
    except Exception as e:
        print(f"{os.path.basename(f)}: PARSE-FAIL {e}")
