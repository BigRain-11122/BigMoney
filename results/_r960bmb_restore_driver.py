# r960 bm-b restore driver v5: rc255-half-success conversion law
# Empirical root cause (r960 05:18-05:21 probes): GFW RST kills the ssh child
# AFTER the lazy-fetch pack fully lands + indexes -> parent checkout exits 255
# but the blob IS local. Probes 3/3: sh562180/sh588270 (v4-"failed" 05:05/05:17)
# + sh588800 all re-checkout RC=0 instantly. v4's 136 consecutive "fails" =
# mostly landed blobs (pack files landing every ~6s in .git/objects/pack while
# driver logged FAIL). v5 = v4 per-file loop + immediate same-file retry once
# (instant materialization when blob landed; one more fetch attempt otherwise)
# + circuit breaker: 10 consecutive double-fails -> sleep 300s (probe cadence
# instead of 6s/file hammer). Law lineage: r949 (log start line verify), r953
# (Popen + tree-kill soft cap), r954 (per-unit persistence = convergence), r955
# (single-blob lazy fetch = only server-accepted face), r959 (v4 pass design).
# Receipt: results/_r960bmb_restore_receipt.json (r961 verify face).
import datetime, json, subprocess, time, os

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = BM + r'\results\_r960bmb_restore_driver.log'
REC = BM + r'\results\_r960bmb_restore_receipt.json'
NO_WINDOW = 0x08000000

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + str(m) + '\n')

def save(**kw):
    d = {'driver': 'r960bmb restore v5 (per-file + retry-once)',
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

def try_file(path):
    # First attempt; rc!=0 -> immediate same-file retry (v4 fails were
    # half-successes: blob landed, retry materializes instantly).
    rc = checkout_one(path)
    if rc == 0:
        return True, False
    rc2 = checkout_one(path)
    return rc2 == 0, True

def main():
    W('v5 driver start pid=%d' % os.getpid())
    rem0 = remaining()
    save(status='RUNNING', pass_no=0, remaining=len(rem0), restored_total=0,
         retried_ok=0,
         next='r961 verify face; ALL_RESTORED -> completion package (smoke+S6+orders ack diff+attrition+catch-up+merges)')
    total_restored = 0
    total_retried_ok = 0
    for pass_no in range(1, 13):
        paths = remaining()
        if not paths:
            save(status='ALL_RESTORED', pass_no=pass_no, restored_total=total_restored,
                 remaining=0)
            W('ALL_RESTORED at pass %d start' % pass_no)
            return
        W('pass %d start remaining=%d' % (pass_no, len(paths)))
        ok = fail = retried = 0
        consec_double_fail = 0
        for i, path in enumerate(paths, 1):
            got, retried_first = try_file(path)
            if got:
                ok += 1
                total_restored += 1
                consec_double_fail = 0
                if retried_first:
                    retried += 1
                    total_retried_ok += 1
            else:
                fail += 1
                consec_double_fail += 1
                W('FAIL(pass-both) %s' % path)
                if consec_double_fail >= 10:
                    save(status='RUNNING', pass_no=pass_no, done_in_pass=i, of=len(paths),
                         ok_in_pass=ok, fails_in_pass=fail, retried_ok_in_pass=retried,
                         restored_total=total_restored, remaining=len(paths) - ok,
                         circuit_breaker='sleep300_after_%d_double_fails' % consec_double_fail)
                    W('circuit breaker: %d consecutive double-fails -> sleep 300' % consec_double_fail)
                    time.sleep(300)
                    consec_double_fail = 0
            if i % 25 == 0:
                save(status='RUNNING', pass_no=pass_no, done_in_pass=i, of=len(paths),
                     ok_in_pass=ok, fails_in_pass=fail, retried_ok_in_pass=retried,
                     restored_total=total_restored, remaining=len(paths) - ok)
        rem = len(remaining())
        save(status='RUNNING' if rem else 'ALL_RESTORED', pass_no=pass_no,
             restored_this_pass=ok, fails_this_pass=fail, retried_ok_this_pass=retried,
             restored_total=total_restored, remaining=rem)
        W('pass %d done ok=%d fail=%d (retried_ok=%d) remaining=%d'
          % (pass_no, ok, fail, retried, rem))
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
         restored_total=total_restored, retried_ok=total_retried_ok,
         next='r961: ALL_RESTORED -> completion package; PARTIAL -> peer bundle request '
              'MSG on origin main + relaunch v5 (idempotent)')
    W('exit remaining=%d' % rem)

main()
