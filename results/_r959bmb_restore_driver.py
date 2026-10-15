# r959 bm-b per-file restore driver v4: single-file checkout = single-blob lazy fetch
# = small pack that passes even in GFW night window (evidence r959: 3/3 files restored
# 0.3-0.4s each, vs v3 50-file chunk packs stalling 230-283s then dying). Supersedes v3.
# Law lineage: r949 (verify spawn via log start line, never trust receipt alone), r953
# (Popen + tree-kill soft cap, never trust run(timeout) timely return), r954 (per-unit
# persistence = guaranteed convergence), r955 (lazy fetch = only server-accepted face).
# Passes: fresh ls-files -d snapshot each pass; per-file 90s cap; zero-progress pass ->
# sleep 300 + retry (max 12 passes); resumable/idempotent by construction.
# Receipt: results/_r959bmb_restore_receipt.json (progress face, r960 verify).
import datetime, json, subprocess, time, os

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = BM + r'\results\_r959bmb_restore_driver.log'
REC = BM + r'\results\_r959bmb_restore_receipt.json'
NO_WINDOW = 0x08000000

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + str(m) + '\n')

def save(**kw):
    d = {'driver': 'r959bmb restore v4 (per-file)',
         'ts': datetime.datetime.now().astimezone().isoformat(timespec='seconds')}
    d.update(kw)
    json.dump(d, open(REC, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def remaining():
    p = subprocess.run(['git', '-C', BM, 'ls-files', '-d', '-z'], capture_output=True,
                       timeout=120, creationflags=NO_WINDOW)
    return [x.decode('utf-8') for x in p.stdout.split(b'\0') if x]

def checkout_one(path, cap=90):
    p = subprocess.Popen(['git', '-C', BM, 'checkout', '--', path],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         creationflags=NO_WINDOW)
    try:
        p.communicate(timeout=cap)
        return p.returncode
    except subprocess.TimeoutExpired:
        subprocess.run('taskkill /T /F /PID %d' % p.pid, shell=True, capture_output=True)
        try:
            p.communicate(timeout=10)
        except Exception:
            pass
        return -99

def main():
    W('v4 driver start pid=%d' % os.getpid())
    save(status='RUNNING', pass_no=0, remaining=len(remaining()), restored_total=0,
         next='r960 verify face; ALL_RESTORED -> completion package')
    total_restored = 0
    for pass_no in range(1, 13):
        paths = remaining()
        if not paths:
            save(status='ALL_RESTORED', pass_no=pass_no, restored_total=total_restored,
                 remaining=0)
            W('ALL_RESTORED at pass %d start' % pass_no)
            return
        W('pass %d start remaining=%d' % (pass_no, len(paths)))
        ok = fails = 0
        for i, path in enumerate(paths, 1):
            rc = checkout_one(path)
            if rc == 0:
                ok += 1
                total_restored += 1
            else:
                fails += 1
                W('FAIL pass=%d rc=%s %s' % (pass_no, rc, path))
            if i % 25 == 0:
                save(status='RUNNING', pass_no=pass_no, done_in_pass=i, of=len(paths),
                     ok_in_pass=ok, fails_in_pass=fails,
                     restored_total=total_restored, remaining=len(paths) - ok)
        rem = len(remaining())
        save(status='RUNNING' if rem else 'ALL_RESTORED', pass_no=pass_no,
             restored_this_pass=ok, fails_this_pass=fails,
             restored_total=total_restored, remaining=rem)
        W('pass %d done ok=%d fails=%d remaining=%d' % (pass_no, ok, fails, rem))
        if rem == 0:
            save(status='ALL_RESTORED', pass_no=pass_no, restored_total=total_restored,
                 remaining=0)
            W('ALL_RESTORED after pass %d' % pass_no)
            return
        if ok == 0:
            W('zero-progress pass %d -> sleep 300' % pass_no)
            time.sleep(300)
    rem = len(remaining())
    save(status='PARTIAL_PASSES_EXHAUSTED' if rem else 'ALL_RESTORED', remaining=rem,
         restored_total=total_restored,
         next='r960: ALL_RESTORED -> completion package (smoke 49/49 + S6 + orders ack '
              'diff-scan + attrition + warm catch-up + side-branch merges); '
              'PARTIAL -> push peer bundle request MSG to origin main + relaunch v4')
    W('exit remaining=%d' % rem)

main()
