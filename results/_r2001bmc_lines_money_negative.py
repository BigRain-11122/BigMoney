"""Negative control for verified_lines_money_year.check(): each leg starts from the
ORIGINAL bytes (r1999 lesson: legs must not inherit each other's mutation)."""
import hashlib
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACE = os.path.join(ROOT, "results", "verified_lines_money_year.json")
SCRIPT = os.path.join(ROOT, "scripts", "verified_lines_money_year.py")


def sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


def run_check():
    p = subprocess.run([sys.executable, SCRIPT, "check"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main():
    orig = io.open(FACE, "rb").read()
    legs = []

    def leg(name, mutate, want_rc, want_tokens, forbid_tokens=()):
        io.open(FACE, "wb").write(orig)  # every leg starts from the original bytes
        face = json.loads(orig.decode("utf-8"))
        mutate(face)
        io.open(FACE, "w", encoding="utf-8").write(json.dumps(face, ensure_ascii=False, indent=1))
        rc, out = run_check()
        io.open(FACE, "wb").write(orig)
        ok = (rc == want_rc) and all(t in out for t in want_tokens) and \
             all(t not in out for t in forbid_tokens)
        legs.append(ok)
        print("%s %-52s rc=%d" % ("PASS" if ok else "FAIL", name, rc))
        if not ok:
            print("   tail:", out.strip().splitlines()[-3:])

    def m1(f):  # change one line's rate: combined no longer equals the mean
        f["rows"][2]["lines"]["L1_etf_book"]["ret"] += 0.01
        f["rows"][2]["lines"]["L1_etf_book"]["ret_pct"] += 1.0

    def m2(f):  # n_lines lies
        f["rows"][1]["combined"]["n_lines"] = 9

    def m3(f):  # money does not match the rate it carries
        f["rows"][0]["combined"]["money_end_cny"] += 12345.0

    def m4(f):  # a negative year is claimed where there is none
        f["sign_agreement"]["years_all_negative"] = ["2026"]
        f["verdict"] = "THREE_LINES_LOST_TOGETHER_IN_2026"

    def m5(f):  # a caliber is dropped: the page can no longer be read
        f["lines"][2]["caliber"].pop("execution", None)

    def m6(f):  # the "cannot be added" sentence removed
        f["cannot_be_added"] = ""

    leg("L1 one line's rate moved -> combined must be named", m1, 1, ["2022"], )
    leg("L2 n_lines disagrees with priced lines", m2, 1, ["n_lines"])
    leg("L3 money does not match capital*(1+r)", m3, 1, ["money"])
    leg("L4 verdict claims an all-negative year that the rows deny", m4, 1, ["years_all_negative"],
        forbid_tokens=("STALE",))
    leg("L5 a missing caliber is refused", m5, 1, ["caliber missing execution"])
    leg("L6 the not-addable sentence is required", m6, 1, ["cannot be added"])

    after = sha(io.open(FACE, "rb").read())
    same = after == sha(orig)
    print("%s face restored byte-identical (sha %s)" % ("PASS" if same else "FAIL", after))
    print("\nnegative-control %d/%d" % (sum(legs) + int(same), len(legs) + 1))
    return 0 if all(legs) and same else 1


if __name__ == "__main__":
    raise SystemExit(main())
