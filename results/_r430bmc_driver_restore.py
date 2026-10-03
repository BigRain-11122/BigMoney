"""_r430bmc_driver_restore.py -- r429-law trio step 3: restore S6 driver to
HEAD canonical state after r430 chain run, sha-equal verified (sha_pre from
the adapt receipt 4ee7773ee8bee2de... = pre-edit blob)."""
import hashlib
import subprocess

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\_r428bmc_s6.py"
HEAD = subprocess.run(["git", "show", "HEAD:Tools/_r428bmc_s6.py"],
                      capture_output=True, cwd=r"K:\Fluxgroup\FluxGroup\quant\bigmoney")
assert HEAD.returncode == 0, "git show failed"
blob = HEAD.stdout
# r372 EOL dual-space law: repo blob is LF, canonical Windows checkout is
# CRLF; restore must land in worktree space (CRLF) to byte-match pre-edit.
crlf = blob.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
open(P, "wb").write(crlf)
cur = open(P, "rb").read()
assert hashlib.sha256(cur).hexdigest().startswith("4ee7773ee8bee2de"), \
    "sha mismatch after restore"
assert cur.count(b"_r430bmc_s6_log.txt") == 0, "r430 residue in driver"
print("RESTORE_OK driver==HEAD sha=%s" % hashlib.sha256(cur).hexdigest()[:16])
