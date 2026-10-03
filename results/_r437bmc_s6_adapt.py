# -*- coding: utf-8 -*-
"""r437 bm-c S6 canon driver adapt/restore (r429 three-step law: count==1
replace LOG literal pair -> run -> restore HEAD byte-exact CRLF face).
Template: results/_r436bmc_s6_adapt.py.
Note: dead-predecessor hand-rolled driver (_r437bmc_s6_driver.py) omitted
BIGMONEY_REGIME_GUARD=enforce + PYTHONUTF8 -> guard-mode shadow downgrade +
mojibake log; superseded by this canon path (defect disclosed r437 report).
Usage: python results/_r437bmc_s6_adapt.py adapt|restore|check
"""
import subprocess
import sys

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
DRIVER = REPO + r'\Tools\_r428bmc_s6.py'
OLD = b'"results", "_r428bmc_s6_log.txt"'
NEW = b'"results", "_r437bmc_s6_log.txt"'
OLD_DOC = b'results/_r428bmc_s6_log.txt'
NEW_DOC = b'results/_r437bmc_s6_log.txt'
CREATE = 0x08000000


def git(*a):
    p = subprocess.run(['git'] + list(a), capture_output=True, creationflags=CREATE, cwd=REPO)
    return p.returncode, (p.stdout or b'') + (p.stderr or b'')


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'check'
    if mode == 'adapt':
        b = open(DRIVER, 'rb').read()
        assert b.count(OLD) == 1, 'LOG code literal count %d != 1' % b.count(OLD)
        assert b.count(OLD_DOC) == 1, 'LOG doc literal count %d != 1' % b.count(OLD_DOC)
        b2 = b.replace(OLD, NEW).replace(OLD_DOC, NEW_DOC)
        assert b2.count(NEW) == 1 and b2.count(NEW_DOC) == 1
        open(DRIVER, 'wb').write(b2)
        print('ADAPTED: LOG -> _r437bmc_s6_log.txt (code+doc, count==1 each, byte surgery)')
    elif mode == 'restore':
        rc, blob = git('show', 'HEAD:Tools/_r428bmc_s6.py')
        assert rc == 0 and blob, 'HEAD blob fetch failed'
        wt_crlf = blob.replace(b'\n', b'\r\n')  # r372 EOL dual-space law: blob=LF, worktree=CRLF
        open(DRIVER, 'wb').write(wt_crlf)
        rc, st = git('status', '--porcelain', '--', 'Tools/_r428bmc_s6.py')
        line = st.decode('utf-8', errors='replace').strip()
        assert line == '', 'canon driver still dirty after restore: %r' % line
        print('RESTORED: canon driver = HEAD blob (CRLF face), status clean')
    else:
        b = open(DRIVER, 'rb').read()
        print('check: code-literal=%d doc-literal=%d (canon expects 1/1, adapted expects 0/0)'
              % (b.count(OLD), b.count(OLD_DOC)))


if __name__ == '__main__':
    sys.exit(main())
