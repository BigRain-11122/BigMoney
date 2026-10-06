import json, os, shutil, sys

# gamewin_cron_suspend.py - CEO 用机让路律 companion (fleet kit, resource-chain.md §六).
# suspend: backup scheduled_tasks.json then clear all durable cron jobs (the cron shifts
# auto-firing while the REPL is idle are the popup/resource noise source during CEO's
# game/work window). restore: merge backed-up jobs back by id (idempotent).
# status: report suspension state. Portable: all paths derive from this file's location.

BASE = os.path.dirname(os.path.abspath(__file__))
TASKS = os.path.join(BASE, 'scheduled_tasks.json')
BAK = TASKS + '.gamewin-bak'

def load(p):
    with open(p, encoding='utf-8-sig') as f:
        return json.load(f)

def dump(p, d):
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)

def find_jobs_key(d):
    if isinstance(d, dict):
        for k in ('tasks', 'jobs'):
            if isinstance(d.get(k), list):
                return k
        for k, v in d.items():
            if isinstance(v, list) and v and isinstance(v[0], dict) and 'id' in v[0]:
                return k
    return None

mode = sys.argv[1] if len(sys.argv) > 1 else 'status'

if mode == 'suspend':
    if not os.path.exists(TASKS):
        print('RESULT no_file')
    elif os.path.exists(BAK):
        bk = load(BAK); k = find_jobs_key(bk)
        print('RESULT already_suspended backup_jobs=%d' % len(bk.get(k, []) if k else []))
    else:
        shutil.copy2(TASKS, BAK)
        d = load(TASKS)
        k = find_jobs_key(d)
        n = len(d.get(k, [])) if k else 0
        if k:
            d[k] = []
        else:
            d = {}
        dump(TASKS, d)
        print('RESULT suspended_jobs=%d key=%s file_cleared=1' % (n, k))
elif mode == 'restore':
    if not os.path.exists(BAK):
        print('RESULT no_backup')
    else:
        bk = load(BAK); bkk = find_jobs_key(bk)
        bj = bk.get(bkk, []) if bkk else []
        cur = load(TASKS) if os.path.exists(TASKS) else {}
        curk = find_jobs_key(cur)
        if curk is None:
            curk = bkk or 'jobs'
            if not isinstance(cur.get(curk), list):
                cur[curk] = []
        curj = cur[curk]
        ids = set(j.get('id') for j in curj)
        added = 0
        for j in bj:
            if j.get('id') not in ids:
                curj.append(j); added += 1
        dump(TASKS, cur)
        os.remove(BAK)
        print('RESULT restored=%d total=%d' % (added, len(curj)))
else:
    if os.path.exists(BAK):
        bk = load(BAK); k = find_jobs_key(bk)
        print('RESULT suspended=%d' % len(bk.get(k, []) if k else []))
    elif os.path.exists(TASKS):
        d = load(TASKS); k = find_jobs_key(d)
        print('RESULT active=%d' % len(d.get(k, []) if k else []))
    else:
        print('RESULT none')
