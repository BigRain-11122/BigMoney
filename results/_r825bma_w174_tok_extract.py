# -*- coding: utf-8 -*-
"""r825 bm-a: exec the truncated r821 W173 build script (all asserts, zero
writes) to extract TOK173/BACK173/EXPECT pairs for the W174 buildgen."""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

src = io.open(r"results/_r821bma_w173_prereg_build.py", encoding="utf-8").read()
cut = src.find("out_t = src")
assert 0 < cut, "cut marker missing"
trunc = src[:cut]
# W173 seat MSG archived inbox->processed (cef586bd3) -- patch the two
# live re-assert path forms; the historical 9cd8af3af value is frozen in the
# W173 text.
n_path = trunc.count('"fleet/inbox/MSG-2026-10-07-1122-bma-w173-seat.md"')
assert n_path == 1, n_path
trunc = trunc.replace(
    '"fleet/inbox/MSG-2026-10-07-1122-bma-w173-seat.md"',
    '"fleet/inbox/processed/MSG-2026-10-07-1122-bma-w173-seat.md"')
n_show = trunc.count('"origin/main:fleet/inbox/MSG-2026-10-07-1122-bma-w173-seat.md"')
assert n_show == 1, n_show
trunc = trunc.replace(
    '"origin/main:fleet/inbox/MSG-2026-10-07-1122-bma-w173-seat.md"',
    '"origin/main:fleet/inbox/processed/MSG-2026-10-07-1122-bma-w173-seat.md"')
old_assert = 'assert SEAT_SHA == "9cd8af3af", SEAT_SHA'
assert old_assert in trunc
trunc = trunc.replace(
    old_assert,
    'assert SEAT_SHA in ("9cd8af3af", "cef586bd3"), SEAT_SHA\n'
    'SEAT_SHA = "9cd8af3af"  # r820-time historical value frozen in the W173 text')
ns = {}
exec(compile(trunc, "r821_trunc", "exec"), ns)
BACK173 = ns["BACK173"]
TOK173 = ns["TOK173"]
EXPECT = ns["EXPECT"]
print("r821 TOK entries:", len(TOK173), "BACK entries:", len(BACK173))
print("names:", [t for (t, _v) in BACK173])
bm = dict(BACK173)
for k in ("@CHAIN@", "@KLT@", "@SEMT@", "@S51@", "@S51B@", "@S52@", "@S53@",
          "@KLKEY@", "@POOL@", "@SCANFACE@", "@ANCHOR@", "@S5ANCH@"):
    print(k, "=>", repr(bm[k])[:260])
print("EXPECT sum:", sum(EXPECT.values()), "n_tokens:", len(EXPECT))
