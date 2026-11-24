"""r2081 negative controls: can the new smoke leg actually go red?

Three mutations, each aimed at one way the check could be decorative:

  1. the page loses the sentence            -> red ("page does not quote...")
  2. the face's trim jumps above the band    -> the expected sentence flips, so the
     unchanged page no longer matches       -> red (proves the leg tracks the face,
     not a string somebody typed)
  3. the face is deleted from a temp dir     -> red (face missing)
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import smoke_test                                                    # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACE = os.path.join(ROOT, "results", "etf_book_cap_trim_toll.json")


def main():
    ok = 0
    with open(FACE, encoding="utf-8") as fh:
        face = json.load(fh)

    bad = smoke_test.cap_price_tag_problems(face=face)
    assert not bad, bad
    ok += 1
    print("[1] baseline: the shipped face and page agree")

    bad = smoke_test.cap_price_tag_problems(face=face, page="（页面没有这一句）")
    assert bad and "does not quote" in bad[0], bad
    ok += 1
    print("[2] page without the sentence -> red")

    big = copy.deepcopy(face)
    big["facts"]["trim_day_now_cny"] = float(big["facts"]["ruler_band_cny"]) * 2.0
    bad = smoke_test.cap_price_tag_problems(face=big, page=None)
    # the page still carries the OLD sentence, so the flipped expected text is absent
    assert bad and "does not quote" in bad[0], bad
    ok += 1
    print("[3] trim above the band flips the expected sentence -> red")

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        bad = smoke_test.cap_price_tag_problems(results_dir=td)
    assert bad and "face missing" in bad[0], bad
    ok += 1
    print("[4] missing face -> red")

    print("negative control %d/%d PASS" % (ok, ok))
    return 0


if __name__ == "__main__":
    sys.exit(main())
