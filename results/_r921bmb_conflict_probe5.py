import subprocess, json


def stage_blob(path, stage):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    return r.stdout.decode('utf-8')


META_KEYS = {'generated', 'generated_at', 'elapsed_sec', 'ts', 'updated', 'meta'}


def strip_meta(obj):
    if isinstance(obj, dict):
        return {k: strip_meta(v) for k, v in obj.items() if k not in META_KEYS}
    if isinstance(obj, list):
        return [strip_meta(x) for x in obj]
    return obj


faces = ['results/daily_scorecard.json', 'results/dashboard_status.json',
         'results/scorecard_v1.json', 'results/strategy_scorecard.json']
for p in faces:
    o = strip_meta(json.loads(stage_blob(p, 2)))
    t = strip_meta(json.loads(stage_blob(p, 3)))
    same = o == t
    print(p, '-> data-identical(after meta-strip):', same)
    if not same:
        # locate first difference path
        def walk(a, b, path=''):
            if type(a) != type(b):
                return path + f' (type {type(a).__name__} vs {type(b).__name__})'
            if isinstance(a, dict):
                for k in a.keys() | b.keys():
                    if k not in a:
                        return path + '/' + k + ' (missing in ours)'
                    if k not in b:
                        return path + '/' + k + ' (missing in theirs)'
                    r = walk(a[k], b[k], path + '/' + k)
                    if r:
                        return r
            elif isinstance(a, list):
                if len(a) != len(b):
                    return path + f' (list len {len(a)} vs {len(b)})'
                for i, (x, y) in enumerate(zip(a, b)):
                    r = walk(x, y, path + f'[{i}]')
                    if r:
                        return r
            elif a != b:
                return path + f' ({str(a)[:60]} vs {str(b)[:60]})'
            return None
        print('   first-diff:', walk(o, t))
