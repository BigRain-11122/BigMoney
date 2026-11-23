"""r2009 negative control: prove etf_book_nobond_ticket.check() actually refuses.

Each leg copies the REAL published face into a temp dir, breaks exactly one thing, and
calls the module's real check() with its globals pointed at the temp copies. A guard that
only ever re-derives its own rows would pass every one of these (E662 family); the legs
below are the proof it does not.
"""
import importlib.util
import io
import contextlib
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.join(ROOT, "scripts", "etf_book_nobond_ticket.py")
REAL_JSON = os.path.join(ROOT, "results", "etf_book_nobond_ticket.json")
REAL_MD = os.path.join(ROOT, "research", "ETF_BOOK_NOBOND_TICKET.md")
REAL_PARENT = os.path.join(ROOT, "results", "etf_nobond_vt.json")

fails = []


def load_mod():
    spec = importlib.util.spec_from_file_location("ebnt_neg", MOD)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def arm(m, d, parent_src=None):
    m.OUT_JSON = os.path.join(d, "face.json")
    m.OUT_MD = os.path.join(d, "face.md")
    m.PARENT = parent_src or os.path.join(d, "parent.json")


def fresh(d):
    os.makedirs(d, exist_ok=True)
    shutil.copy(REAL_JSON, os.path.join(d, "face.json"))
    shutil.copy(REAL_MD, os.path.join(d, "face.md"))
    if os.path.exists(REAL_PARENT):
        shutil.copy(REAL_PARENT, os.path.join(d, "parent.json"))


def edit(d, fn, name="face.json"):
    p = os.path.join(d, name)
    with open(p, encoding="utf-8") as f:
        obj = json.load(f)
    fn(obj)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def leg(label, want_rc, want_stale, d, mutate):
    m = load_mod()
    arm(m, d)
    mutate(d)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = m.check()
    out = buf.getvalue()
    has_stale = "STALE" in out
    ok = rc == want_rc
    if want_stale is not None:
        ok = ok and (has_stale == want_stale)
    print(("PASS" if ok else "FAIL"), label,
          "rc=%d (want %d) stale_word=%s (want %s)" % (rc, want_rc, has_stale, want_stale))
    if not ok:
        fails.append(label)
        print("  output:", out.strip().replace("\n", " | ")[:400])


def main():
    if not (os.path.exists(REAL_JSON) and os.path.exists(REAL_MD)):
        print("negative control FAIL: no published face to break")
        return 1

    # L1 untouched copy must pass -- otherwise every leg below is meaningless
    d = tempfile.mkdtemp(prefix="r2009_l1_")
    fresh(d)
    leg("L1 untouched face passes", 0, None, d, lambda dd: None)

    # L2 missing face = STALE, not a crash
    d = tempfile.mkdtemp(prefix="r2009_l2_")
    os.makedirs(d, exist_ok=True)
    leg("L2 missing face -> STALE", 3, True, d, lambda dd: None)

    # L3 a pick swapped = prices a different book than the parent published
    d = tempfile.mkdtemp(prefix="r2009_l3_")
    fresh(d)
    leg("L3 swapped pick -> contradiction", 1, False, d,
        lambda dd: edit(dd, lambda o: o["picks"][0].__setitem__("symbol", "000000")))

    # L4 cash weight nudged = weights + cash no longer 1
    d = tempfile.mkdtemp(prefix="r2009_l4_")
    fresh(d)
    leg("L4 cash weight nudged", 1, False, d,
        lambda dd: edit(dd, lambda o: o["sizing"].__setitem__(
            "cash_weight", o["sizing"]["cash_weight"] + 0.01)))

    # L5 one digit hand-edited on the page
    d = tempfile.mkdtemp(prefix="r2009_l5_")
    fresh(d)
    def bump(dd):
        p = os.path.join(dd, "face.md")
        with open(p, encoding="utf-8") as f:
            s = f.read()
        with open(p, "w", encoding="utf-8") as f:
            f.write(s.replace("0.7350", "0.7351", 1))
    leg("L5 hand-edited page digit", 1, False, d, bump)

    # L6 verdict flipped while the legs still say TRADABLE
    d = tempfile.mkdtemp(prefix="r2009_l6_")
    fresh(d)
    leg("L6 verdict flipped", 1, False, d,
        lambda dd: edit(dd, lambda o: o.__setitem__("verdict", "NOT_TRADABLE_AT_1M")))

    # L7 parent moved one session = this face is stale, not wrong
    d = tempfile.mkdtemp(prefix="r2009_l7_")
    fresh(d)
    edit(d, lambda o: o["live_picks"].__setitem__("as_of", "2026-11-19"), name="parent.json")
    leg("L7 parent as_of moved -> STALE", 3, True, d, lambda dd: None)

    # L8 a lot count no longer equals floor(budget / one_lot)
    d = tempfile.mkdtemp(prefix="r2009_l8_")
    fresh(d)
    def bump_lots(o):
        t = o["tickets"][-1]
        t["legs"][0]["lots"] += 1
        t["legs"][0]["shares"] = t["legs"][0]["lots"] * 100
    leg("L8 lot count off by one", 1, False, d, lambda dd: edit(dd, bump_lots))

    # L9 a one-lot price that does not follow from its own close
    d = tempfile.mkdtemp(prefix="r2009_l9_")
    fresh(d)
    leg("L9 one_lot detached from price", 1, False, d,
        lambda dd: edit(dd, lambda o: o["picks"][0].__setitem__(
            "one_lot_cny", o["picks"][0]["one_lot_cny"] + 1.0)))

    # L10 scale and legs disagree (the r1911 family: printed scale != used scale)
    d = tempfile.mkdtemp(prefix="r2009_l10_")
    fresh(d)
    leg("L10 scale vs weights disagree", 1, False, d,
        lambda dd: edit(dd, lambda o: o["sizing"].__setitem__("scale", 0.80)))

    total = 10
    if fails:
        print("negative control FAIL %d/%d -> %s" % (len(fails), total, ", ".join(fails)))
        return 1
    print("negative control PASS %d/%d" % (total, total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
