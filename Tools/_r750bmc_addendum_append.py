# -*- coding: utf-8 -*-
# r750 bm-c: append push-race addendum row to the CANONICAL round ledger
# (r748 addendum precedent; write-then-grep self-verify)
import datetime

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\logs\iteration-loop\round_reports-bm-c.md"
raw = open(P, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
row = open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r750bmc_addendum_row.txt",
           "rb").read().rstrip(b"\r\n")
row = row.replace(b"10:0x", datetime.datetime.now().strftime("%H:%M").encode())
assert b"r750 addendum" in row and b"--no-verify" in row
if not raw.endswith(eol):
    raw += eol
open(P, "wb").write(raw + row + eol)
back = open(P, "rb").read()
assert back.count(b"r750 addendum") == 1, "addendum not exactly-once"
assert b"r750 addendum" in back.split(eol)[-2], "addendum not in tail"
print("addendum appended bytes=%d" % len(row))
