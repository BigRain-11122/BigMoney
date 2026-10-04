"""r488 bm-c delivery stamp: fill <PUSH_VERIFY> placeholder in
round_reports-bm-c.md with push_verify three-proof result. Bytes-mode,
needle count==1 assertions, append-only containment preserved (prefix
identical). Lineage: _r487bmc_stamp.py pattern."""
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RR = os.path.join(REPO, "round_reports-bm-c.md")
NEEDLE = "本地未达 origin commit 数=<PUSH_VERIFY>".encode("utf-8")
STAMP = (
    "本地未达 origin commit 数=0（DELIVERED：round commit 0cb4a0411 + "
    "merge origin/main bm-b keepalive wave（零 UU）→ tip 52e29f316·"
    "push_verify ahead=0/behind=0 tip==remote 三证）"
).encode("utf-8")


def main():
    raw = open(RR, "rb").read()
    assert raw.count(NEEDLE) == 1, f"needle count={raw.count(NEEDLE)} != 1"
    new = raw.replace(NEEDLE, STAMP)
    assert new.count(STAMP) == 1
    assert new[:raw.index(NEEDLE)] == raw[:raw.index(NEEDLE)]
    assert len(new) == len(raw) - len(NEEDLE) + len(STAMP)
    open(RR, "wb").write(new)
    chk = open(RR, "rb").read()
    assert chk == new and chk.count(NEEDLE) == 0 and chk.count(STAMP) == 1
    print("STAMP_OK", len(raw), "->", len(chk))


if __name__ == "__main__":
    main()
