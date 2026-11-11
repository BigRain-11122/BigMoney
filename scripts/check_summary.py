"""The one line a tail-only harness still shows (r1545).

`smoke_test.py` keeps the LAST line of a leg's output (`splitlines()[-1]`, clipped to
80 chars).  A check that prints `[check] N/M OK` last and its reasons above therefore
survives as a count with no noun: r1544c spent a whole round unable to say WHICH two
fields of `etf_book_cut_order_gap` had drifted, even though `--check` had printed
them -- the harness had thrown the reasons away.

So the summary line itself has to carry the names of the legs that failed, while
staying byte-identical (`[check] N/M OK`) when the face is green: other readers and
greps already match on that shape.
"""

MAX_NAMES = 3


def summary_line(fails, total, tag="check", limit=MAX_NAMES, word="OK"):
    """`[check] 6/8 OK` when clean; `[check] 6/8 OK | FAILED: a; b` otherwise.

    `fails` are short names (no values, no prose): the line has to fit in the
    harness's 80-char tail window before anything is clipped.
    """
    head = "[%s] %d/%d %s" % (tag, total - len(fails), total, word)
    if not fails:
        return head
    shown = list(fails[:limit])
    extra = "" if len(fails) <= limit else " (+%d more)" % (len(fails) - limit)
    return head + " | FAILED: " + "; ".join(shown) + extra


def selftest():
    fails = []

    def leg(ok, msg):
        if not ok:
            fails.append(msg)

    leg(summary_line([], 8) == "[check] 8/8 OK", "clean line changed shape")
    one = summary_line(["field verdict"], 8)
    leg(one == "[check] 7/8 OK | FAILED: field verdict", "one fail: %r" % one)
    two = summary_line(["field verdict", "consumer list"], 8)
    leg("field verdict" in two and "consumer list" in two, "two fails: %r" % two)
    leg(len(two) <= 80, "two fails overflow the 80-char tail window: %d" % len(two))
    many = summary_line(["a", "b", "c", "d", "e"], 8)
    leg(many.endswith("(+2 more)"), "cap: %r" % many)
    leg(summary_line(["x"], 6, tag="selftest").startswith("[selftest] 5/6 OK"),
        "tag not honoured")
    for f in fails:
        print("  FAIL " + f)
    print(summary_line(fails, 6, "selftest"))
    return 0 if not fails else 1


if __name__ == "__main__":
    import sys
    sys.exit(selftest())
