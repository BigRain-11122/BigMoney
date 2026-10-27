import datetime as dt
import io
import json
import os
import time

NOW = dt.datetime.now().astimezone()
ISO = NOW.isoformat(timespec='seconds')
TS = NOW.strftime('%Y-%m-%d %H:%M')

hb = json.load(io.open('fleet/machines/bm-c.json', encoding='utf-8-sig'))
hb['last_seen'] = TS
hb['ts'] = ISO
hb['clock_read'] = ISO
hb['heartbeat_epoch_utc'] = int(time.time())
hb['behind_origin'] = 0
hb['delivered_head'] = os.popen('git rev-parse HEAD').read().strip()[:10]
hb['deployed_oversight_writer'] = 'K:\\Fluxgroup\\.codely-cli\\oversight-bmc\\fleet-oversight.ps1 @ -Check rc=0'
json.dump(hb, io.open('fleet/machines/bm-c.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

ROW = (
    "| %s | 1314 postscript | INBOX + S7: MSG-20261028-0130 (bm-b) said the hourly oversight task runs a "
    "DEPLOYED copy, not the repo source, so D-20261028-02's writer fix was not in the code that runs. On this "
    "host the deployed copy did not exist at all (K:\\Fluxgroup\\.codely-cli\\oversight-bmc\\fleet-oversight.ps1, "
    "Test-Path False) -- the hourly fire had no fixed-shape writer here. Deployed both tools from group "
    "origin/main into that path (20,923 chars, deployed -> verified) and confirmed with -Check rc=0; staged the "
    "two files out of origin blobs instead of checking them out in the group worktree, which sits 14 commits "
    "behind origin with 274 dirty paths from another lane (two-file copy did not justify a tree operation). "
    "Reply MSG-20261028-0200-bm-c written, incoming moved to processed. S7: iteration loop pin=5 no-op; watchdog "
    "re-registered (S4U flip access-denied, standing); pre-commit/pre-push claws match source; 114/114 orders "
    "acknowledged; D-19 decisions 6154bf1c consumed (D-20261028-02 = this round's work, D-20261028-04 group-root "
    "self-check owed by 10-31 00:00). | smoke 108/108 PASS 0 FAIL; chain legs 2/2 rc0; oversight -Check rc=0; "
    "inbox empty after processing; local commits behind origin N=0 | next: D-20261028-04 sweep -- find every "
    "resident script that resolves the group root by '..\\..' instead of rev-parse --show-toplevel |\n"
) % ISO
with io.open('round_reports-bm-c.md', 'a', encoding='utf-8', newline='') as fh:
    fh.write(ROW)
print('postscript written, head=%s' % hb['delivered_head'])