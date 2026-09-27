# -*- coding: utf-8 -*-
"""r359 bm-a fixer pass 3: final 99B shave to meet the 10,240B hard line.
(1) tighten my own 30th-batch summary row; (2) second-stage fold the
'（r353 当窗整编外迁）' tail annotation on the two bm-c 28th-batch pointer
rows (annotation is redundant: the batch attribution is already in the row
body; canon precedent = 27th-batch '指针行二次折叠·行级零丢失'). Fail-closed."""
import sys

CODELY = "CODELY.md"

OLD_SUM = ("- 三十批外迁（r359 bm-a·2026-09-27·10KB 硬线当窗整编·行级零丢失）："
           "r96/r345/r100/r350/r101/r340bmb/r351×2/r353/r355 十条全文行=二十九批 "
           "union 再 materialize 面，折叠回指针（verbatim 已在二十九批节）"
           "+r109bmc/r342bmb/r359bma 三行 verbatim 入三十批节；"
           "保留=User 元律+法行 2+批指针行族。")
NEW_SUM = ("- 三十批外迁（r359 bm-a·2026-09-27·硬线当窗整编·行级零丢失）："
           "十条二十九批 union 再 materialize 全文行折叠回指针（verbatim 已在二十九批节）"
           "+r109/r342/r359 三行 verbatim 入三十批节；保留=User 元律+法行 2+批指针行族。")
TRIM = "（r353 当窗整编外迁）"


def main():
    txt = open(CODELY, "rb").read().decode("utf-8")
    assert OLD_SUM in txt, "summary row not found verbatim"
    txt = txt.replace(OLD_SUM, NEW_SUM)
    n_trim = txt.count(TRIM)
    assert n_trim == 2, f"trim target count={n_trim} != 2"
    txt = txt.replace(TRIM + "。", "。")
    open(CODELY, "wb").write(txt.encode("utf-8"))

    size = len(open(CODELY, "rb").read())
    assert size <= 10240, f"still over hard line: {size}B"
    assert NEW_SUM in open(CODELY, "rb").read().decode("utf-8")
    print(f"fixer3 OK: summary row tightened (-{len(OLD_SUM)-len(NEW_SUM)}B), "
          f"2 redundant tail annotations folded; CODELY.md -> {size}B "
          f"<= 10,240B hard line")
    return 0


if __name__ == "__main__":
    sys.exit(main())
