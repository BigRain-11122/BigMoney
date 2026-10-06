# -*- coding: utf-8 -*-
"""r769 bm-a generator: W156 freeze-arc drivers from the r768 W155 templates.
Placeholder-safe ordered replacement (no cross-wave string collisions)."""
import py_compile

MAP = [
    # stage 1 -> tokens
    ("W154", "@PREV@"), ("W155", "@NEW@"), ("w155", "@new@"),
    ("r768", "@R@"), ("_r768bma", "@RDIR@"),
    ("fourteenth", "@ORDW@"), ("152", "@ROWS@"), ("144", "@OWN@"),
    ("70", "@BMA@"), ("145", "@ORD@"), ("71", "@BORD@"),
    ("N1_BANDS[154]", "@P154@"), ("N1_BANDS[153]", "@P153@"),
    ("(353_604, 355_603)", "@PA@"), ("(355_604, 355_803)", "@PB@"),
    ("(351_404, 353_403)", "@PPA@"), ("(353_404, 353_603)", "@PPB@"),
    ("range(16, 155)", "@RANGE@"),
    ("'155: {\"a\": ('", "@ROWCHK@"),
    ("PERPETUAL-N1-W155", "@BATCH@"), ("PERPETUAL_N1_W155_PREREG", "@PREREG@"),
    ("W156+", "@PROJ@"), ("W156p", "@PROJP@"), ("fc156", "@FCP@"),
    # stage 2 -> W156 values
    ("@PREV@", "W155"), ("@NEW@", "W156"), ("@new@", "w156"),
    ("@R@", "r769"), ("@RDIR@", "_r769bma"),
    ("@ORDW@", "fifteenth"),
    ("@ROWS@", "153"), ("@OWN@", "145"), ("@BMA@", "71"),
    ("@ORD@", "146"), ("@BORD@", "72"),
    ("@P154@", "N1_BANDS[155]"), ("@P153@", "N1_BANDS[154]"),
    ("@PA@", "(355_804, 357_803)"), ("@PB@", "(357_804, 358_003)"),
    ("@PPA@", "(353_604, 355_603)"), ("@PPB@", "(355_604, 355_803)"),
    ("@RANGE@", "range(16, 156)"),
    ("@ROWCHK@", "'156: {\"a\": ('"),
    ("@BATCH@", "PERPETUAL-N1-W156"), ("@PREREG@", "PERPETUAL_N1_W156_PREREG"),
    ("@PROJ@", "W157+"), ("@PROJP@", "W157p"), ("@FCP@", "fc157"),
]


def xform(src: str) -> str:
    out = src
    for a, b in MAP:
        out = out.replace(a, b)
    return out


def build(src_path: str, dst_path: str):
    src = open(src_path, encoding="utf-8").read()
    out = xform(src)
    open(dst_path, "w", encoding="utf-8", newline="\n").write(out)
    py_compile.compile(dst_path, doraise=True)
    print("built+compiled:", dst_path)


if __name__ == "__main__":
    build("results/_r768bma_w155_probe.py", "results/_r769bma_w156_probe.py")
    build("results/_r768bma_w155_band_gate.py", "results/_r769bma_w156_band_gate.py")
    print("generator done")
