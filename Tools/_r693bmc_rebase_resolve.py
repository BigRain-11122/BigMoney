# -*- coding: utf-8 -*-
"""r693 bm-c rebase closeout resolver (2-UU, r773/r522/r704 canon):
- compute_audit.json: history UNION via bm-b r806 bloodline
  (_r806bmb_ca_union.py form; :2:=onto bm-b 223 rows, :3:=mine 201 rows;
  union dict.values(), sorted by ts, latest=newer face, zero-loss count
  assert, reparse verify).
- lhb_update_status.json: stage-3 take (mine 17:39:26 > onto 17:31:04,
  plain newer-wins; python bytes face per r710 law A).
Then: GM advisory M-20261007-01 in-window honest addendum (bm-b ALIVE --
origin tip d20c52647/966a570a7 merge commits absorbed r692 + bm-a W176
during this window = long-round hb lag, NOT whole-machine stall) +
round-report addendum line + atomic git add of all four faces (r787).
Run from repo root. HEAD stays mid-rebase until --continue."""
import json
import os
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(REPO)


def blob(stage, path):
    p = subprocess.run(["git", "-C", REPO, "show", f":{stage}:{path}"],
                       capture_output=True)
    assert p.returncode == 0 and p.stdout, "stage blob read fail %s %s" % (stage, path)
    return p.stdout


def main():
    # ---- compute_audit.json union ----
    o_raw = blob(2, "results/compute_audit.json")
    t_raw = blob(3, "results/compute_audit.json")
    o = json.loads(o_raw.decode("utf-8"))
    t = json.loads(t_raw.decode("utf-8"))

    def rk(r):
        return json.dumps(r, sort_keys=True, ensure_ascii=False)

    o_rows = {rk(r): r for r in o["history"]}
    t_rows = {rk(r): r for r in t["history"]}
    union = dict(o_rows)
    union.update(t_rows)
    merged = sorted(union.values(), key=lambda r: r.get("ts", ""))
    expected = len(o_rows) + len(set(t_rows) - set(o_rows))
    assert len(merged) == expected, f"{len(merged)}!={expected}"
    for r in merged:
        assert isinstance(r, dict), "r522 type gate: union row must be dict"
    latest = o["latest"] if o["latest"].get("ts", "") >= t["latest"].get("ts", "") else t["latest"]
    doc = {"latest": latest, "history": merged}
    crlf = b"\r\n" in o_raw[:2000]
    body = json.dumps(doc, ensure_ascii=False, indent=1)
    if crlf:
        body = body.replace("\n", "\r\n")
    tail = "\r\n" if crlf else "\n"
    if not body.endswith(tail):
        body += tail
    enc = "utf-8-sig" if o_raw.startswith(b"\xef\xbb\xbf") else "utf-8"
    with open("results/compute_audit.json", "w", encoding=enc, newline="") as f:
        f.write(body)
    json.loads(open("results/compute_audit.json", "rb").read().decode(enc))
    print("compute_audit union: onto=%d mine=%d -> %d rows (zero-loss PASS), latest ts=%s"
          % (len(o["history"]), len(t["history"]), len(merged), latest.get("ts")))

    # ---- lhb_update_status.json: take stage 3 (mine newer) ----
    l3 = blob(3, "results/lhb_update_status.json")
    l2 = blob(2, "results/lhb_update_status.json")
    d3 = json.loads(l3.decode("utf-8"))
    d2 = json.loads(l2.decode("utf-8"))
    assert d3.get("updated", "") > d2.get("updated", ""), \
        "newer-wins gate: mine must be newer (l3=%s l2=%s)" % (d3.get("updated"), d2.get("updated"))
    with open("results/lhb_update_status.json", "wb") as f:
        f.write(l3)
    json.loads(open("results/lhb_update_status.json", "rb").read().decode("utf-8"))
    print("lhb_update_status: stage-3 take (updated=%s > %s) PASS" %
          (d3.get("updated"), d2.get("updated")))

    # ---- GM advisory in-window honest addendum ----
    MEMOS = "research/GM_REVIEW_MEMOS.md"
    raw = open(MEMOS, "rb").read()
    guard = "17:5x 本窗补记".encode("utf-8")
    assert raw.count(guard) == 0, "advisory addendum already present"
    assert b"M-20261007-01" in raw, "advisory section must exist"
    eol = b"\r\n" if raw.count(b"\r\n") >= 10 else b"\n"
    ADD = (
        "- **17:5x \u672c\u7a97\u8865\u8bb0\uff08\u8bda\u5b9e\u4fee\u6b63\uff09**\uff1a\u672c advisory \u843d\u7b14\u540e origin \u5b9e\u6d4b\u53cd\u8f6c\u2014\u2014"
        "bm-b r806 \u8f6e\u5728\u9014\u6d3b\u8dc3\uff08origin tip d20c52647/966a570a7 \u4e24 merge commit \u540c\u7a97\u843d origin\uff0c"
        "\u5438\u6536\u672c\u53f8 r692 \u4e0e bm-a W176 \u9762\uff09=\u3010bm-b \u975e\u6574\u673a\u505c\u6ede\u3011\uff0chb \u9648\u65e7\uff0814:37:54 \u8d77\uff09"
        "\u5b9a\u6027\u4fee\u6b63\u4e3a\u957f\u8f6e\u5fc3\u8df3\u817f\u6ede\u540e\uff1bNULLS \u5c3e\u6bb5\uff08\u7f3a 214\uff09\u6682\u505c\u89e3\u91ca\u4fee\u6b63\u4e3a"
        "\u300c\u957f\u8f6e\u7a97\u5185\u70e7\u5f55\u817f\u6682\u6b47\u00b7bm-b \u8f6e\u6536\u53e3\u540e\u65ad\u70b9\u7eed\u70e7\u300d\uff1b\u672c advisory \u964d\u7ea7\u4e3a"
        "\u300c\u957f\u8f6e\u5fc3\u8df3\u6ede\u540e+\u5c3e\u6bb5\u70e7\u5f55\u5b88\u671b\u300d\uff0cfuse \u89e3\u9664/TRANSFER \u4e24\u9009\u9879\u4fdd\u7559"
        "\uff08\u4ec5\u5f53 bm-b \u8f6e\u6536\u53e3\u540e\u4ecd\u4e0d\u7eed\u70e7\u65f6\u542f\u7528\uff09\u3002\n"
    ).encode("utf-8")
    with open(MEMOS, "ab") as f:
        f.write(ADD)
    post = open(MEMOS, "rb").read()
    assert post.count(guard) == 1, "advisory addendum count==1"
    print("GM advisory addendum appended (bm-b alive honest correction)")

    # ---- round report addendum line ----
    RP = "logs/iteration-loop/round_reports-bm-c.md"
    raw2 = open(RP, "rb").read()
    g2 = "r693 bm-c ADDENDUM".encode("utf-8")
    assert raw2.count(g2) == 0, "report addendum already present"
    eol2 = b"\r\n" if raw2.count(b"\r\n") >= 10 else b"\n"
    import datetime
    ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    LINE = (
        ts + " | r693 bm-c ADDENDUM\uff08push-race \u6536\u53e3\u56de\u6267+\u8bda\u5b9e\u4fee\u6b63\uff09 | "
        "push#1 \u88ab\u672c\u673a pre-push \u6240\u6709\u6743\u722a\u62e6\u622a\uff08\u5220\u9664\u96c6\u542b bm-b r806 \u5de5\u4f5c\u4ef6\u975e\u672c\u673a\u5c5e\u4e3b="
        "\u6b63\u786e\u6267\u6cd5\uff09\u2192pull --rebase \u649e 2-UU\uff08compute_audit\u6084\u5408+on 223\u884c vs \u672c\u53f8 201\u884c\u65b0\u81f3 17:38:19\uff09"
        "\u2192bm-b r806 \u8840\u7edf\u590d\u7528\u89e3\u6790\uff08union 224 \u884c\u96f6\u4e22\u5931+latest \u53d6\u65b0\uff09+lhb \u53d6\u65b0\uff0817:39:26>17:31:04\uff09"
        "\u2192\u540c\u7a97 origin \u53cd\u8f6c\u8bc1\u636e\uff1a**bm-b \u975e\u6574\u673a\u505c\u6ede**\uff08r806 \u957f\u8f6e\u5728\u9014\uff0c\u540c\u7a97\u4e24 merge commit "
        "d20c52647/966a570a7 \u5438\u6536\u672c\u53f8 r692+bm-a W176 \u9762\u843d origin\uff09\u2192GM advisory M-20261007-01 \u5df2\u8865\u8bb0\u964d\u7ea7"
        "\uff08\u957f\u8f6e\u5fc3\u8df3\u6ede\u540e+\u5c3e\u6bb5\u70e7\u5f55\u5b88\u671b\uff09\u2192r825 \u5f8b\u672c\u673a daemon \u9762\u65e0\u6807\u8bb0\u6c61\u67d3\uff08\u672c\u673a satengine "
        "\u975e\u672c\u8f6e\u51b2\u7a81\u96c6\uff09\u00b7\u5220\u9664\u96c6\u5df2\u81ea\u6108\uff08\u5de5\u4f5c\u6811\u73b0\u542b 39 \u4ef6 r806 \u9762\u96f6 D\uff09\n"
    ).encode("utf-8")
    with open(RP, "ab") as f:
        f.write(LINE)
    assert open(RP, "rb").read().count(g2) == 1
    print("round report addendum appended")

    # ---- atomic add (r787) ----
    for p in ("results/compute_audit.json", "results/lhb_update_status.json",
              "research/GM_REVIEW_MEMOS.md", "logs/iteration-loop/round_reports-bm-c.md",
              "Tools/_r693bmc_rebase_resolve.py"):
        r = subprocess.run(["git", "-C", REPO, "add", "--", p], capture_output=True)
        assert r.returncode == 0, "add fail %s: %s" % (p, r.stderr.decode("utf-8", "replace")[:200])
    # post-add gates: zero UU + no r806 deletions in staged diff
    r = subprocess.run(["git", "-C", REPO, "ls-files", "-u"], capture_output=True)
    assert not r.stdout.strip(), "UU must be empty after add"
    r = subprocess.run(["git", "-C", REPO, "diff", "--cached", "--name-status", "HEAD"],
                       capture_output=True)
    dels = [l for l in r.stdout.decode("utf-8", "replace").splitlines() if l.startswith("D")]
    print("staged deletions vs HEAD:", dels if dels else "NONE")
    assert not dels, "staged deletion set must be empty (claw gate)"
    print("ATOMIC ADD COMPLETE -- ready for rebase --continue")
    return 0


if __name__ == "__main__":
    sys.exit(main())
