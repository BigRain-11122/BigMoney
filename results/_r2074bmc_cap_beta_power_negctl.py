"""Negative control for scripts/etf_book_cap_beta_power.py (r2074, bm-c).

Every leg tampers one thing, runs the real `--check`, asserts the sentence it must print
(and the sentence it must NOT print), then restores the byte-exact original.  A face that
stays green after its own numbers are edited is not a check.

  python results/_r2074bmc_cap_beta_power_negctl.py
"""
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SCRIPT = os.path.join(REPO, "scripts", "etf_book_cap_beta_power.py")
OUT = os.path.join(REPO, "results", "etf_book_cap_beta_power.json")
PAGE = os.path.join(REPO, "research", "ETF_BOOK_CAP_BETA_POWER.md")

INPUTS = [
    os.path.join(REPO, "results", "etf_book_cap_beta_units.json"),
    os.path.join(REPO, "results", "etf_book_beta_paths.json"),
]

cases = []


def leg(name, fn):
    try:
        fn()
        cases.append((name, True, ""))
    except AssertionError as e:
        cases.append((name, False, str(e)))


def run_check():
    p = subprocess.run([sys.executable, SCRIPT, "--check"], capture_output=True, text=True,
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def snapshot():
    with io.open(OUT, "rb") as fh:
        out = fh.read()
    with io.open(PAGE, "rb") as fh:
        page = fh.read()
    return out, page


def restore(out_bytes, page_bytes):
    with io.open(OUT, "wb") as fh:
        fh.write(out_bytes)
    with io.open(PAGE, "wb") as fh:
        fh.write(page_bytes)


def with_restore(fn):
    out_b, page_b = snapshot()
    try:
        fn()
    finally:
        restore(out_b, page_b)


def write_facts(mutate):
    data = json.loads(io.open(OUT, "r", encoding="utf-8").read())
    mutate(data)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")


def sha(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def t_baseline_green():
    rc, txt = run_check()
    assert rc == 0, "baseline check not green: rc=%s %s" % (rc, txt.strip()[:400])
    assert "CHECK OK" in txt, txt[:200]


def t_tamper_number_is_check_failed():
    def body():
        write_facts(lambda d: d["facts"].__setitem__(
            "bars_needed", d["facts"]["bars_needed"] + 1))
        rc, txt = run_check()
        assert rc == 3, "a tampered bar count must go red, rc=%s" % rc
        assert "CHECK FAILED" in txt, txt[:300]
        assert "bars_needed" in txt, "the failure must name the field: %s" % txt[:300]
        assert "STALE" not in txt, "an arithmetic disagreement is not staleness: %s" % txt[:300]

    with_restore(body)


def t_tamper_verdict_is_check_failed():
    def body():
        write_facts(lambda d: d["facts"].__setitem__("verdict", "RESOLVABLE_WITH_MORE_DATA"))
        rc, txt = run_check()
        assert rc == 3 and "CHECK FAILED" in txt, txt[:300]
        assert "verdict" in txt, txt[:300]

    with_restore(body)


def t_moved_inputs_is_stale_not_failed():
    def body():
        write_facts(lambda d: d.__setitem__("inputs_digest", "0" * 64))
        rc, txt = run_check()
        assert rc == 3, rc
        assert "STALE" in txt, txt[:300]
        assert "CHECK FAILED" not in txt, "moved inputs must not read as arithmetic: %s" % txt[:300]

    with_restore(body)


def t_page_block_edit_is_named():
    def body():
        page = io.open(PAGE, "r", encoding="utf-8").read()
        needle = "| 判词 | **"
        idx = page.find(needle)
        assert idx > 0, "the verdict row must exist in the page before we tamper with it"
        end = page.find("** |", idx)
        assert end > idx, "the verdict row must close with a bold cell"
        tampered = page[:idx] + needle + "PLACEHOLDER** |" + page[end + len("** |"):]
        assert tampered != page, "the tamper must actually change the page"
        with io.open(PAGE, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(tampered)
        rc, txt = run_check()
        assert rc == 3 and "page block" in txt, txt[:300]

    with_restore(body)


def t_missing_block_is_red():
    def body():
        page = io.open(PAGE, "r", encoding="utf-8").read()
        with io.open(PAGE, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(page.replace("<!-- CAP-BETA-POWER-END -->", ""))
        rc, txt = run_check()
        assert rc == 3 and "page block unreadable" in txt, txt[:300]

    with_restore(body)


def t_missing_face_is_stale():
    def body():
        out_b, _ = snapshot()
        os.remove(OUT)
        rc, txt = run_check()
        assert rc == 3 and "STALE face missing" in txt, txt[:300]
        with io.open(OUT, "wb") as fh:
            fh.write(out_b)

    with_restore(body)


def t_restore_is_green_and_inputs_untouched():
    before = [sha(p) for p in INPUTS]
    rc, txt = run_check()
    assert rc == 0 and "CHECK OK" in txt, txt[:300]
    after = [sha(p) for p in INPUTS]
    assert before == after, "the negative control must not touch the producer faces"


for name, fn in [
    ("baseline is green", t_baseline_green),
    ("an edited bar count reads CHECK FAILED", t_tamper_number_is_check_failed),
    ("an edited verdict reads CHECK FAILED", t_tamper_verdict_is_check_failed),
    ("moved inputs read STALE, not arithmetic", t_moved_inputs_is_stale_not_failed),
    ("an edited page block is named", t_page_block_edit_is_named),
    ("a missing block is red", t_missing_block_is_red),
    ("a missing face is STALE", t_missing_face_is_stale),
    ("restore is green and leaves inputs byte-identical", t_restore_is_green_and_inputs_untouched),
]:
    leg(name, fn)

bad = [c for c in cases if not c[1]]
for name, ok, msg in cases:
    print("%s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else " -- " + msg))
print("%d/%d PASS" % (len(cases) - len(bad), len(cases)))
sys.exit(0 if not bad else 1)
