# -*- coding: utf-8 -*-
# r1014 bm-b: ST-001 group LEDGER backfill row (J-D0-1R) via CAS surgery push.
# Template = _r1070bma_group_bank_cas.py (fetch->read-tree temp idx->hash-object->
# update-index->write-tree->commit-tree->push sha:main, 40-hex hard checks, retry once).
# Target file: cph4/fleet/drama-dept-v1/LEDGER.md (drama-dept-v1 judgment-case ledger).
# Edit = insert ONE backfill row right after the J-D0-1 row; zero other bytes touched.
import subprocess, os, tempfile, re, sys

G = r"C:\Fluxgroup\FluxGroup"
PATH = "cph4/fleet/drama-dept-v1/LEDGER.md"
MSG = ("fleet: drama-dept-v1 LEDGER backfill row J-D0-1R (bm-b-side taildrop SLA "
       "root-cause self-cert, discharges J-D0-1 pending-backfill marker; product = "
       "bigmoney content/drama/outbox/J-D0-1-rootcause.md; ST-001 group face "
       "via CONTENT-LOOP v0.1) [via bm-b r1014]")

def git(*a, env=None):
    return subprocess.run(["git", "-C", G, *a], capture_output=True, env=env)

def sha40(s):
    return re.fullmatch(r"[0-9a-f]{40}", s or "") is not None

ROW = ("| J-D0-1R | 粗样交付 SLA 违例根因回灌（承 J-D0-1 待回灌位·bm-b 侧自证 ST-001） "
       "| rootcause 件=bigmoney `content/drama/outbox/J-D0-1-rootcause.md`（9 事实；三候补根因排序："
       "①尾件落在扫描面外〔r1044 必扫 Downloads 面〕②发件侧回执行未写而接收迟到③窗内对端离线） "
       "| 闸=交付哨合同三钉：扫描面清单钉死（Downloads+fleet inbox）＋发件回执行必写＋跨机物理交付合同带 "
       "fallback-to-git 条款（SLA 可证化）；执法面=CONTENT-LOOP v0.1 ST-001 收口（r1014 集团上链） | 10-19 |")

r = git("fetch", "origin")
assert r.returncode == 0, ("fetch", r.stderr[:300])
base = git("rev-parse", "origin/main").stdout.decode().strip()
assert sha40(base), ("base", base)

raw = git("show", base + ":" + PATH).stdout
try:
    text = raw.decode("utf-8")
except UnicodeDecodeError:
    sys.exit("FATAL: LEDGER blob not utf-8")
nl = "\r\n" if "\r\n" in text else "\n"
lines = text.split(nl)
jdx = [i for i, l in enumerate(lines) if l.startswith("| J-D0-1 |")]
assert len(jdx) == 1, ("J-D0-1 row not unique", jdx)
assert not any(l.startswith("| J-D0-1R") for l in lines), "backfill row already present"
lines.insert(jdx[0] + 1, ROW)
new_text = nl.join(lines)

tmpf = os.path.join(tempfile.gettempdir(), "r1014bmb_ledger.md")
with open(tmpf, "w", encoding="utf-8", newline="") as f:
    f.write(new_text)

msgf = os.path.join(tempfile.gettempdir(), "r1014bmb_ledger_msg.txt")
with open(msgf, "w", encoding="utf-8", newline="\n") as f:
    f.write(MSG + "\n")

idx = os.path.join(tempfile.gettempdir(), "r1014bmb_group_cas.idx")
if os.path.exists(idx):
    os.remove(idx)

r = git("hash-object", "-w", tmpf)
blob = r.stdout.decode().strip()
assert r.returncode == 0 and sha40(blob), ("blob", r.returncode, blob, r.stderr[:200])

delivered = None
for attempt in (1, 2):
    r = git("fetch", "origin")
    assert r.returncode == 0, ("fetch", r.stderr[:300])
    base = git("rev-parse", "origin/main").stdout.decode().strip()
    assert sha40(base), ("base", base)
    env = dict(os.environ, GIT_INDEX_FILE=idx)
    if os.path.exists(idx):
        os.remove(idx)
    r = git("read-tree", base, env=env)
    assert r.returncode == 0, ("read-tree", r.stderr[:300])
    r = git("update-index", "--add", "--cacheinfo", "100644,%s,%s" % (blob, PATH), env=env)
    assert r.returncode == 0, ("update-index", r.stderr[:300])
    r = git("write-tree", env=env)
    tree = r.stdout.decode().strip()
    assert r.returncode == 0 and sha40(tree), ("tree", tree)
    r = git("commit-tree", tree, "-p", base, "-F", msgf)
    newc = r.stdout.decode().strip()
    assert r.returncode == 0 and sha40(newc), ("commit-tree", newc, r.stderr[:300])
    r = subprocess.run(["git", "-C", G, "push", "origin", newc + ":refs/heads/main"],
                       capture_output=True)
    out = (r.stdout + r.stderr).decode(errors="replace")
    push_ok = r.returncode == 0 and not any(
        w in out for w in ("fatal", "rejected", "failed", "error"))
    if push_ok:
        delivered = (base, newc)
        break
    print("push attempt %d rejected (rc=%s): %s" % (attempt, r.returncode, out[:200]))

assert delivered, "CAS push failed both attempts"
r = git("fetch", "origin")
assert r.returncode == 0
tip = git("rev-parse", "origin/main").stdout.decode().strip()
blob_check = git("rev-parse", "origin/main:" + PATH).stdout.decode().strip()
assert blob_check == blob, ("blob mismatch", blob_check, blob)
verify = git("show", "origin/main:" + PATH).stdout.decode("utf-8")
assert ROW in verify and verify.count("| J-D0-1 |") == 1, "row-landing verify failed"
print('{"push": "ok", "base": "%s", "new": "%s", "tip": "%s", "row": "J-D0-1R", '
      '"blob_equality": "ok", "attempts": %d}' % (delivered[0][:10], delivered[1][:10],
                                                 tip[:10], attempt))
