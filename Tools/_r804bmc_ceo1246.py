# -*- coding: utf-8 -*-
"""r804 bm-c O-20261009-1246/1257 consumption probe.

CEO enforcement orders landed in GROUP docs/orders.md (ORD sha delta
4AA1A8F6 -> 31542B89, +2 rows): BigMoney named in the no-queue violation
list. Fix mandate (a): build state/queue/ three files (main >=5 /
tech >=10 / explore >=10) in the auditor-expected shape.

This probe FIRST reads the canon definitions before any file creation:
  - docs/self-drive.md v2.0 (sec 6 startup checklist item 2 definition)
  - Tools/subsidiary-load-audit.ps1 (the auditor itself -- its expected
    paths/count rules are the ONLY valid shape; building anything else
    would keep the violation flag red)
Usage: python Tools/_r804bmc_ceo1246.py probe
Writes UTF-8 byte-true copies to results/ and prints ASCII-only line
indexes (CJK-safe console contract per pit-encoding law); body is then
read via read_file.
Every subprocess passes CREATE_NO_WINDOW (zero-desktop-flash law)."""
import subprocess
import json
import re
import os
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP = r"K:\Fluxgroup\FluxGroup"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def git_blob(path):
    p = subprocess.run(["git", "-C", GROUP, "show", "origin/main:" + path],
                       capture_output=True, creationflags=CNW)
    return p.returncode, p.stdout


def ascii_index(name, text_bytes, out, patterns):
    """Write byte-true copy + print ASCII-only line-number index."""
    txt = text_bytes.decode("utf-8", "replace")
    lines = txt.splitlines()
    dst = os.path.join(REPO, "results", name)
    with open(dst, "wb") as fh:
        fh.write(text_bytes)
    idx = {"file": name, "n_lines": len(lines),
           "bytes": len(text_bytes), "hits": {}}
    for pat in patterns:
        hits = [i + 1 for i, l in enumerate(lines) if re.search(pat, l, re.I)]
        idx["hits"][pat] = hits[:60]
    out.append(idx)
    return lines


BK_REGEX = (r"chore|closeout|heartbeat|no-pullable|queue-empty|five-checks|"
            r"state tick|probes green|probes flat|absorb|declaration|fold|"
            r"ledger|snapshot|kanban|tick done|water-level|census-data-hygiene|"
            r"maintenance|bookkeeping|jie-lu|shou-|kai-|xin-|shou-ban|kuaizhao|"
            r"kanban|xintiao")


def verify():
    """Mirror Tools/subsidiary-load-audit.ps1 logic for the BigMoney row:
    queue counts (non-blank lines), prodAgeH from last-30 commits vs bkRegex,
    verdict deduction. ASCII-only output."""
    import datetime
    qdir = os.path.join(REPO, "state", "queue")
    counts = {}
    for f in ("main.md", "tech.md", "explore.md"):
        p = os.path.join(qdir, f)
        n = 0
        if os.path.exists(p):
            with open(p, "rb") as fh:
                for line in fh.read().decode("utf-8", "replace").splitlines():
                    if line.strip():
                        n += 1
        counts[f] = n
    m, t, e = counts["main.md"], counts["tech.md"], counts["explore.md"]
    q = "m%d/t%d/e%d" % (m, t, e)
    q += "/LOW" if (m < 5 or t < 10 or e < 10) else "/OK"
    p = subprocess.run(["git", "-C", REPO, "log", "-30",
                        "--pretty=format:%ad|%s",
                        "--date=format:%Y-%m-%d %H:%M:%S"],
                       capture_output=True, creationflags=CNW)
    now = datetime.datetime.now()
    prod_age_h, prod_count, idle_decl, last_subj = 999.0, 0, 0, ""
    for line in p.stdout.decode("utf-8", "replace").splitlines():
        if "|" not in line:
            continue
        ts_s, subj = line.split("|", 1)
        try:
            ts = datetime.datetime.strptime(ts_s, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
        age_h = (now - ts).total_seconds() / 3600.0
        if re.search(BK_REGEX, subj, re.I):
            idle_decl += 1
        else:
            prod_count += 1
            if age_h < prod_age_h:
                prod_age_h = round(age_h, 1)
                last_subj = subj
    verdict = "GREEN"
    if prod_age_h > 24:
        verdict = "RED"
    elif prod_age_h > 12 or "LOW" in q or "MISSING" in q or idle_decl >= 15:
        verdict = "AMBER"
    snip = last_subj[:40]
    result = {"queue": q, "prod_age_h": prod_age_h, "prod30": prod_count,
              "idle_decl30": idle_decl, "verdict": verdict,
              "last_prod_snip_ascii": snip.encode("ascii", "replace").decode()}
    print(json.dumps(result, indent=1))
    with open(os.path.join(REPO, "results",
                           "_r804bmc_ceo1246_verify.json"), "w",
              encoding="utf-8") as fh:
        json.dump(result, fh, indent=1)
    return 0 if verdict == "GREEN" else 1


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        return verify()
    out = []
    rc, sd = git_blob("docs/self-drive.md")
    out.append({"blob": "docs/self-drive.md", "rc": rc, "bytes": len(sd)})
    if rc == 0:
        ascii_index("_r804bmc_selfdrive.md", sd, out,
                    [r"queue", r"state", r"[§\u2460-\u2467]?6", r"\u542f\u52a8\u6e05\u5355",
                     r"main", r"tech", r"explore", r"\u4e09\u6587\u4ef6",
                     r"\u4e09\u6587\u4ef6|\u4e09\u4e2a\u6587\u4ef6"])
    rc, la = git_blob("Tools/subsidiary-load-audit.ps1")
    out.append({"blob": "Tools/subsidiary-load-audit.ps1", "rc": rc, "bytes": len(la)})
    if rc == 0:
        ascii_index("_r804bmc_loadaudit_tool.txt", la, out,
                    [r"BigMoney", r"bigmoney", r"queue", r"state", r"main",
                     r"tech", r"explore", r"Threshold|>=|ge "])
    dst = os.path.join(REPO, "results", "_r804bmc_ceo1246_probe.json")
    with open(dst, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=True)
    print(json.dumps(out, indent=1, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
