"""Lane log progress digester (T-70 local-coding pilot task 09, the arm).

Detached-refresh lane logs (options/ah/mf) -> one progress line per lane
plus a VERDICT line. Read-only, zero network, ASCII output.

Modes:
    lane_log_digest.py                usage, exit 2
    lane_log_digest.py selftest       offline assertions, exit 0/1
    lane_log_digest.py [logs_dir]     live digest (default "logs"), exit 0/1
                                      (logs_dir missing/not a dir -> exit 2)
"""

import re
import sys

# ---------------------------------------------------------------- regexes

OPT_PROGRESS_RE = re.compile(
    r"\[opt\-refresh\] (\d+)/(\d+) appended=(\d+) fuse=(\d+)")
OPT_CENSUS_RE = re.compile(
    r"\[opt\-refresh\] enumerated=(\d+) disk=(\d+) extra_sweep=(\d+) "
    r"sweep_skip=(\d+) ckpt_done=(\d+) pending=(\d+)(?:\s|$)")
OPT_DONE_RE = re.compile(
    r"\[opt\-refresh\] done pass_ok=(True|False) appended=(\d+) "
    r"mismatches=(\[[^\]]*\]) fails=(\[[^\]]*\]) last_pass=(\S+)\s*$")
OPT_FUSE_PREFIX = "[opt-refresh] conn-fuse:"

AH_DONE_RE = re.compile(
    r"refresh done: pairs=(\d+) done=(\d+) quarantined=(\d+) "
    r"pulled_rows=(\d+) cutoff=(\S+) complete=(True|False) exit=(\d+)\s*$")
AH_EM_PREFIX = "EM mapping unavailable:"
AH_FUSE_PREFIX = "fuse stop at "

MF_DONE_RE = re.compile(
    r"refresh done: \+(\d+) rows, (\d+) failures, (\d+) mismatches, "
    r"complete=(True|False), panel cutoff=(\S+)\s*$")
MF_BLOCK_PREFIX = "source-level block suspected"
MF_RANKFAIL_PREFIX = "rank pass failed:"
MF_RANK_PREFIX = "rank pass "

OPT_LINE_FIELDS = ("state", "progress", "appended", "fuse", "pending",
                   "fuse_events", "done_pass", "done_appended",
                   "done_mismatches", "done_fails", "last_pass")
AH_LINE_FIELDS = ("state", "pairs", "done_pairs", "quarantined",
                  "pulled_rows", "cutoff", "complete", "exit",
                  "em_unavail", "fuse_stops")
MF_LINE_FIELDS = ("state", "rows", "failures", "mismatches", "complete",
                  "cutoff", "blocks", "rank_fails", "rank_pass_events")


def _lines(text):
    return [] if text is None else text.splitlines()


def _list_count(bracket_text):
    """Element count inside a bracket list: 0 if empty, else commas + 1."""
    inner = bracket_text.strip()[1:-1].strip()
    if not inner:
        return 0
    return inner.count(",") + 1


def _last_match(lines, regex, group_fn):
    hit = None
    for line in lines:
        m = regex.match(line)
        if m:
            hit = group_fn(m)
    return hit


def _parse_options(text):
    f = {k: None for k in OPT_LINE_FIELDS}
    lines = _lines(text)
    if text is None:
        f["state"] = "missing"
        return f
    non_blank = [ln for ln in lines if ln.strip()]
    if not non_blank:
        f["state"] = "empty"
        f["fuse_events"] = 0
        return f

    def prog(m):
        return ("{}/{}".format(m.group(1), m.group(2)),
                int(m.group(3)), int(m.group(4)))

    got = _last_match(non_blank, OPT_PROGRESS_RE, prog)
    if got:
        f["progress"], f["appended"], f["fuse"] = got
    got = _last_match(non_blank, OPT_CENSUS_RE, lambda m: int(m.group(6)))
    if got is not None:
        f["pending"] = got

    def done(m):
        return (m.group(1) == "True", int(m.group(2)),
                _list_count(m.group(3)), _list_count(m.group(4)),
                m.group(5))

    got = _last_match(non_blank, OPT_DONE_RE, done)
    if got:
        (f["done_pass"], f["done_appended"], f["done_mismatches"],
         f["done_fails"], f["last_pass"]) = got
    f["fuse_events"] = sum(1 for ln in non_blank
                           if ln.startswith(OPT_FUSE_PREFIX))
    f["state"] = "done" if f["done_pass"] is not None else "in_progress"
    return f


def _parse_ah(text):
    f = {k: None for k in AH_LINE_FIELDS}
    lines = _lines(text)
    if text is None:
        f["state"] = "missing"
        return f
    non_blank = [ln for ln in lines if ln.strip()]
    if not non_blank:
        f["state"] = "empty"
        f["em_unavail"] = 0
        f["fuse_stops"] = 0
        return f

    def done(m):
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)),
                int(m.group(4)), m.group(5), m.group(6) == "True",
                int(m.group(7)))

    got = _last_match(non_blank, AH_DONE_RE, done)
    if got:
        (f["pairs"], f["done_pairs"], f["quarantined"], f["pulled_rows"],
         f["cutoff"], f["complete"], f["exit"]) = got
    f["em_unavail"] = sum(1 for ln in non_blank
                          if ln.startswith(AH_EM_PREFIX))
    f["fuse_stops"] = sum(1 for ln in non_blank
                          if ln.startswith(AH_FUSE_PREFIX))
    f["state"] = "done" if f["pairs"] is not None else "in_progress"
    return f


def _parse_mf(text):
    f = {k: None for k in MF_LINE_FIELDS}
    lines = _lines(text)
    if text is None:
        f["state"] = "missing"
        return f
    non_blank = [ln for ln in lines if ln.strip()]
    if not non_blank:
        f["state"] = "empty"
        for k in ("blocks", "rank_fails", "rank_pass_events"):
            f[k] = 0
        return f

    def done(m):
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)),
                m.group(4) == "True", m.group(5))

    got = _last_match(non_blank, MF_DONE_RE, done)
    if got:
        f["rows"], f["failures"], f["mismatches"], f["complete"], \
            f["cutoff"] = got
    f["blocks"] = sum(1 for ln in non_blank
                      if ln.startswith(MF_BLOCK_PREFIX))
    f["rank_fails"] = sum(1 for ln in non_blank
                          if ln.startswith(MF_RANKFAIL_PREFIX))
    f["rank_pass_events"] = sum(
        1 for ln in non_blank
        if ln.startswith(MF_RANK_PREFIX)
        and not ln.startswith(MF_RANKFAIL_PREFIX))
    f["state"] = "done" if f["rows"] is not None else "in_progress"
    return f


def _lane_ok(lane, f):
    if lane == "options":
        return f["state"] == "done" and f["done_pass"] is True
    if lane == "ah":
        return (f["state"] == "done" and f["complete"] is True
                and f["exit"] == 0)
    return f["state"] == "done" and f["complete"] is True


def _render(f, fields):
    out = []
    for k in fields:
        v = f[k]
        if v is None:
            out.append(k + "=-")
        else:
            out.append(k + "=" + str(v))
    return " ".join(out)


def digest(options_text, ah_text, mf_text):
    """Pure face: three log texts (str) or None (missing) -> digest dict."""
    lanes = {
        "options": _parse_options(options_text),
        "ah": _parse_ah(ah_text),
        "mf": _parse_mf(mf_text),
    }
    ok = sum(1 for lane in ("options", "ah", "mf") if _lane_ok(lane, lanes[lane]))
    lines = [
        "LANE options " + _render(lanes["options"], OPT_LINE_FIELDS),
        "LANE ah " + _render(lanes["ah"], AH_LINE_FIELDS),
        "LANE mf " + _render(lanes["mf"], MF_LINE_FIELDS),
        "VERDICT ok={}/3".format(ok),
    ]
    return {"lanes": lanes, "ok": ok, "lines": lines}


# ---------------------------------------------------------------- live

def _read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return None


def _live(logs_dir):
    texts = tuple(
        _read_text(logs_dir + "/" + name) for name in
        ("options_refresh.log", "ah_refresh.log", "moneyflow_refresh.log"))
    res = digest(*texts)
    for line in res["lines"]:
        print(line)
    return 0 if res["ok"] == 3 else 1


# ---------------------------------------------------------------- selftest

def _selftest():
    checks = []

    def check(name, cond, detail=""):
        checks.append((name, bool(cond), detail))

    o1 = "\n".join([
        "[opt-refresh] pass target=2026-09-24 start 2026-09-26T01:00:00",
        "[opt-refresh] enumerated=142 disk=200 extra_sweep=58 sweep_skip=0 "
        "ckpt_done=0 pending=200 months={'510050': ['202610', '202612', "
        "'202703'], '510300': ['202610', '202612', '202703']}",
        "[opt-refresh] 25/200 appended=0 fuse=0",
        "[opt-refresh] 200/200 appended=0 fuse=0",
        "[opt-refresh] conn-fuse: 3 consecutive fails, stop",
        "[opt-refresh] done pass_ok=True appended=0 mismatches=[] "
        "fails=[] last_pass=2026-09-24",
    ])
    a1 = "\n".join([
        "EM mapping unavailable: em page 1: RemoteDisconnected: Remote end "
        "closed connection without response",
        "EM mapping unavailable: em page 1: RemoteDisconnected: Remote end "
        "closed connection without response",
        "refresh done: pairs=6 done=6 quarantined=0 pulled_rows=1200 "
        "cutoff=2026-09-24 complete=True exit=0",
    ])
    m1 = "\n".join([
        "rank pass failed: page 1: RemoteDisconnected -> exit 2 (nothing "
        "written)",
        "source-level block suspected (3 consecutive connection failures) "
        "-- stopping, checkpoint intact, gate retries after throttle window",
        "refresh done: +3600 rows, 3 failures, 0 mismatches, complete=True, "
        "panel cutoff=2026-09-24",
    ])

    # sample 1: all three lanes ok
    r = digest(o1, a1, m1)
    o, a, m = r["lanes"]["options"], r["lanes"]["ah"], r["lanes"]["mf"]
    check("s1 ok=3", r["ok"] == 3, "ok=%r" % r["ok"])
    check("s1 states", (o["state"], a["state"], m["state"])
          == ("done", "done", "done"))
    check("s1 options fields",
          (o["progress"], o["appended"], o["fuse"], o["pending"],
           o["fuse_events"], o["done_pass"], o["done_appended"],
           o["done_mismatches"], o["done_fails"], o["last_pass"])
          == ("200/200", 0, 0, 200, 1, True, 0, 0, 0, "2026-09-24"))
    check("s1 ah fields",
          (a["pairs"], a["done_pairs"], a["quarantined"], a["pulled_rows"],
           a["cutoff"], a["complete"], a["exit"], a["em_unavail"],
           a["fuse_stops"])
          == (6, 6, 0, 1200, "2026-09-24", True, 0, 2, 0))
    check("s1 mf fields",
          (m["rows"], m["failures"], m["mismatches"], m["complete"],
           m["cutoff"], m["blocks"], m["rank_fails"], m["rank_pass_events"])
          == (3600, 3, 0, True, "2026-09-24", 1, 1, 0))
    check("s1 line0", r["lines"][0] ==
          "LANE options state=done progress=200/200 appended=0 fuse=0 "
          "pending=200 fuse_events=1 done_pass=True done_appended=0 "
          "done_mismatches=0 done_fails=0 last_pass=2026-09-24",
          r["lines"][0])
    check("s1 line1", r["lines"][1] ==
          "LANE ah state=done pairs=6 done_pairs=6 quarantined=0 "
          "pulled_rows=1200 cutoff=2026-09-24 complete=True exit=0 "
          "em_unavail=2 fuse_stops=0", r["lines"][1])
    check("s1 line2", r["lines"][2] ==
          "LANE mf state=done rows=3600 failures=3 mismatches=0 "
          "complete=True cutoff=2026-09-24 blocks=1 rank_fails=1 "
          "rank_pass_events=0", r["lines"][2])
    check("s1 line3", r["lines"][3] == "VERDICT ok=3/3", r["lines"][3])

    # sample 2: options in flight
    o2 = "\n".join([
        "[opt-refresh] enumerated=142 disk=200 extra_sweep=58 sweep_skip=0 "
        "ckpt_done=0 pending=200 months={}",
        "[opt-refresh] 50/200 appended=0 fuse=0",
    ])
    r2 = digest(o2, a1, m1)
    o2f = r2["lanes"]["options"]
    check("s2 state", o2f["state"] == "in_progress", o2f["state"])
    check("s2 fields", (o2f["progress"], o2f["pending"], o2f["fuse_events"])
          == ("50/200", 200, 0))
    check("s2 done fields none",
          all(o2f[k] is None for k in ("done_pass", "done_appended",
                                       "done_mismatches", "done_fails",
                                       "last_pass")))
    check("s2 ok=2", r2["ok"] == 2, "ok=%r" % r2["ok"])
    check("s2 verdict byte", r2["lines"][3] == "VERDICT ok=2/3",
          r2["lines"][3])
    check("s2 line0 render", r2["lines"][0] ==
          "LANE options state=in_progress progress=50/200 appended=0 "
          "fuse=0 pending=200 fuse_events=0 done_pass=- done_appended=- "
          "done_mismatches=- done_fails=- last_pass=-", r2["lines"][0])

    # sample 3: mf blocked
    rank_ok = ("rank pass 2026-09-25T23:15:00: +3600 rows, 3 same-day "
               "skips, 2 not in rank face, 1 not in universe, 0 mismatches")
    m3 = "\n".join([
        rank_ok,
        "rank pass failed: page 1: x -> exit 2 (nothing written)",
        "rank pass failed: page 2: x -> exit 2 (nothing written)",
        "rank pass failed: page 3: x -> exit 2 (nothing written)",
        "source-level block suspected (3 consecutive connection failures) "
        "-- stopping",
        "source-level block suspected (3 consecutive connection failures) "
        "-- stopping",
        "refresh done: +120 rows, 3 failures, 0 mismatches, complete=False, "
        "panel cutoff=2026-09-23",
    ])
    r3 = digest(o1, a1, m3)
    m3f = r3["lanes"]["mf"]
    check("s3 state", m3f["state"] == "done", m3f["state"])
    check("s3 fields", (m3f["rows"], m3f["complete"], m3f["cutoff"],
                        m3f["blocks"], m3f["rank_fails"],
                        m3f["rank_pass_events"])
          == (120, False, "2026-09-23", 2, 3, 1))
    check("s3 mf not ok", not _lane_ok("mf", m3f))
    check("s3 ok=2", r3["ok"] == 2, "ok=%r" % r3["ok"])

    # sample 4: all missing
    r4 = digest(None, None, None)
    check("s4 states", all(r4["lanes"][k]["state"] == "missing"
                           for k in ("options", "ah", "mf")))
    check("s4 fields none",
          all(v is None for f in r4["lanes"].values()
              for k, v in f.items() if k != "state"))
    check("s4 ok=0", r4["ok"] == 0)
    check("s4 line0", r4["lines"][0] ==
          "LANE options state=missing progress=- appended=- fuse=- "
          "pending=- fuse_events=- done_pass=- done_appended=- "
          "done_mismatches=- done_fails=- last_pass=-", r4["lines"][0])
    check("s4 line3", r4["lines"][3] == "VERDICT ok=0/3", r4["lines"][3])

    # edge 1: list element counting
    e1 = ("[opt-refresh] done pass_ok=True appended=0 "
          "mismatches=['a', 'b'] fails=['c'] last_pass=2026-09-24")
    rf = digest(e1, None, None)["lanes"]["options"]
    check("e1 counts", (rf["done_mismatches"], rf["done_fails"]) == (2, 1),
          (rf["done_mismatches"], rf["done_fails"]))

    # edge 2: last_pass None token renders as-is
    e2 = ("[opt-refresh] done pass_ok=False appended=0 mismatches=[] "
          "fails=[] last_pass=None")
    rf = digest(e2, None, None)["lanes"]["options"]
    check("e2 last_pass", rf["last_pass"] == "None", rf["last_pass"])
    check("e2 not ok", not _lane_ok("options", rf))

    # edge 3: options only blank lines -> empty
    rf = digest("  \n\n \n", None, None)["lanes"]["options"]
    check("e3 state", rf["state"] == "empty", rf["state"])
    check("e3 fuse_events=0", rf["fuse_events"] == 0, rf["fuse_events"])
    check("e3 struct none", all(rf[k] is None for k in
                                ("progress", "appended", "fuse", "pending",
                                 "done_pass", "last_pass")))

    # edge 4: ah done complete=True exit=3 -> done but not ok
    e4 = ("refresh done: pairs=6 done=6 quarantined=0 pulled_rows=1 "
          "cutoff=2026-09-24 complete=True exit=3")
    af = digest(None, e4, None)["lanes"]["ah"]
    check("e4 state", af["state"] == "done", af["state"])
    check("e4 not ok", not _lane_ok("ah", af))

    # edge 5: ah only EM lines -> in_progress
    e5 = "\n".join(["EM mapping unavailable: em page 1: RemoteDisconnected"]
                   * 3)
    af = digest(None, e5, None)["lanes"]["ah"]
    check("e5 state", af["state"] == "in_progress", af["state"])
    check("e5 fields", (af["em_unavail"], af["fuse_stops"]) == (3, 0))
    check("e5 done none", all(af[k] is None for k in
                              ("pairs", "done_pairs", "quarantined",
                               "pulled_rows", "cutoff", "complete",
                               "exit")))

    # edge 6: two options done lines -> last wins
    e6 = "\n".join([
        "[opt-refresh] done pass_ok=False appended=1 mismatches=[] "
        "fails=[] last_pass=2026-09-23",
        "[opt-refresh] done pass_ok=True appended=2 mismatches=[] "
        "fails=[] last_pass=2026-09-24",
    ])
    rf = digest(e6, None, None)["lanes"]["options"]
    check("e6 last wins", (rf["done_pass"], rf["done_appended"],
                           rf["last_pass"]) == (True, 2, "2026-09-24"))

    # edge 7: two fuse lines -> fuse_events=2
    e7 = "\n".join([
        "[opt-refresh] conn-fuse: 3 consecutive fails, stop",
        "[opt-refresh] conn-fuse: 3 consecutive fails, stop",
    ])
    rf = digest(e7, None, None)["lanes"]["options"]
    check("e7 fuse_events=2", rf["fuse_events"] == 2, rf["fuse_events"])
    check("e7 state", rf["state"] == "in_progress", rf["state"])

    # edge 8: ah done complete=False -> not ok
    e8 = ("refresh done: pairs=6 done=5 quarantined=1 pulled_rows=10 "
          "cutoff=None complete=False exit=2")
    af = digest(None, e8, None)["lanes"]["ah"]
    check("e8 not ok", not _lane_ok("ah", af))
    check("e8 cutoff None", af["cutoff"] == "None", af["cutoff"])

    # edge 9: mf done panel cutoff=None
    e9 = ("refresh done: +50 rows, 0 failures, 0 mismatches, complete=True, "
          "panel cutoff=None")
    mf9 = digest(None, None, e9)["lanes"]["mf"]
    check("e9 cutoff", mf9["cutoff"] == "None", mf9["cutoff"])
    check("e9 ok", _lane_ok("mf", mf9))

    fails = [(n, d) for n, ok_, d in checks if not ok_]
    for n, d in fails:
        print("FAIL: {} | {}".format(n, d))
    print("selftest: {} assertions ALL PASS".format(len(checks))
          if not fails else
          "selftest: {} FAIL of {}".format(len(fails), len(checks)))
    return 0 if not fails else 1


def main(argv):
    if len(argv) < 2:
        print("usage: lane_log_digest.py [selftest | logs_dir]")
        return 2
    if argv[1] == "selftest":
        return _selftest()
    return _live(argv[1])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
