# -*- coding: utf-8 -*-
"""r753 bm-c addendum append: push-race closeout record (r750/r751 addendum
precedent). Byte-exact EOL-matched append to the CANONICAL RPT face."""
import datetime
import io

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\logs\iteration-loop\round_reports-bm-c.md"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
TT = NOW[11:16]

ENTRY = (
    u"2026-10-08T{TT}+08:00 | r753 addendum | dept:\u5de5\u7a0b\uff08\u63a8\u9001\u7ade\u7a97\u6536\u53e3\u5b9e\u5f55\uff09 | "
    u"\u672c\u5730\u672a\u8fbe origin commit \u6570=0\uff08\u6536\u53e3\u540e push+fetch \u81ea\u8bc1 0/0\uff09 | "
    u"\u505a\u4e86=push \u9996\u8bd5 non-FF \u62d2\uff08origin bm-a r875 closeout 1002d0a6c \u5728\u9014\uff09\u2192\u51c0\u6811 rebase origin/main"
    u"\u219214 UU \u5171\u4eab S6 \u518d\u751f\u9762\uff08r742/r750 \u540c\u65cf\uff09\u2192_r753bmc_rebase_resolve.py\uff08r750 \u6b63\u5178\u8840\u7edf\u514b\u9686"
    u"\u00b7ts-duel 9 \u9762+union 2 \u9762\uff08compute_audit history by-ts+token_usage per-key max\u3001\u96f6\u4e22\u5931\uff09+\u65e0 ts \u9762 OURS\u9ed8\u8ba5 3 \u9762\uff09"
    u"\u2192E42 churn \u62e6 continue\uff08r863 \u5f8b\uff1asatengine \u6d3b\u5199\u9762 TEMP \u5907\u4efd results/_r753bmc_churn_backup/\u2192checkout \u6e05\u6811"
    u"\u2192continue \u5373\u8fc7\u2192live-wins \u56de\u79fb\u8986\u5199\uff09\u2192churn absorb dab9445a3\uff08+r753 \u4e3b\u62df\u5408 0c9dcbc6c\uff09"
    u"\u2192push \u9001\u8fbe 1002d0a6c..dab9445a3 rc0\u00b7BEHIND=0/AHEAD=0 \u53cc\u8bc1\u00b7STATUS_CLEAN\u3002"
    u"\u5751\u65b0\u5f8b=boot \u81ea\u514b\u9686\u5751\u5df2\u76f4\u5199 pit-lineage.md\uff08\u4e3b\u4ef6\u538b\u7ebf 30,684B\u00b7r666 \u76f4\u5199\u5148\u4f8b\uff09\u3002"
    u"| \u4e0b\u8f6e\u6307\u9488\u4e0d\u53d8\uff08r754 marks \u7eed\u5b88\u7b2c 3 \u7a97+\u4eca\u665a\u76d8\u540e re-arm \u9762\uff09\u3002[via bm-c r753]"
).replace("{TT}", TT)

raw = io.open(P, "rb").read()
before = len(raw)
eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
if not raw.endswith(eol):
    io.open(P, "wb").write(raw + eol)
    raw = io.open(P, "rb").read()
line = ENTRY.encode("utf-8")
io.open(P, "ab").write(line + eol)
back = io.open(P, "rb").read()
assert back.count(b"| r753 addendum |") == 1, "addendum row not exactly-once"
assert b"| r753 addendum |" in back.split(eol)[-2] + back.split(eol)[-3], "addendum not in tail"
assert back.count(b"| r753 |") == 1, "main row still exactly-once"
print("addendum ok bytes=%d before=%d after=%d eol=%r" % (len(line), before, len(back), eol))
