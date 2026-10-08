# r749 bm-c: direct-write pit entry to research/pit-protocol-lane.md
# (r666 direct-write precedent; main CODELY.md 30,684B under 30,720B cap -> no append no split)
import hashlib

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\research\pit-protocol-lane.md"
ENTRY = (
    "- [2026-10-08 09:2x r749 bm-c] **QA \u5206\u79bb\u8dd1\u624b\u00d7S6 \u94fe\u540c\u7a97\u53cc\u8c03 market_clock \u7ade\u6001\u5751\uff08\u77ac\u6001 FACE_ERROR_HOT \u5047 cell\u00b7FAC \u622a\u65ad\u9762\uff09**\uff1a"
    "qa_ignite \u5206\u79bb\u8dd1\u624b item4 \u817f\u4e0e S6 \u94fe\u817f 5/7\uff08market_regime/market_clock\uff09\u540c\u7a97\u5404\u81ea\u8c03 scripts/market_clock_call.py run\u2014\u2014"
    "QA \u5b50\u8fdb\u7a0b\u8bfb results/regime_state.json \u649e S6 \u817f mid-rewrite \u7a97\u2192\u77ac\u6001 FACE_ERROR_HOT\uff08\u8bda\u5b9e fail-closed\u00b7rc0 \u975e\u5d29\uff09\uff0c"
    "\u88ab qa_smoke_run tail[-1][:100] \u622a\u65ad\u6210\u300ccell=FAC\u300d\uff08ORA=ORANGE_COOL \u540c\u673a\u5236\u622a\u65ad\u9762\uff09\uff1b"
    "\u6b63\u5178\u9762\u7531\u540e\u5199\u8005\u4fdd\u5168\uff08S6 \u817f 09:29:13 \u540e\u5199 CALL+call_latest=ORANGE_COOL\u00b7git clean\u00b7\u76d8\u4e0a\u4e3a\u51c6\uff09\u3002"
    "\u6b63\u6cd5=\u2460\u70b9\u706b\u5e8f\uff1aqa_ignite \u79fb\u5230 S6 \u94fe\u6536\u5c3e\u540e\uff08\u5206\u79bb\u8dd1\u624b DETACHED \u4e0d\u53d7 25min wrapper \u6740\u5f71\u54cd\u00b7r640 \u5f8b\uff09\u907f\u514d item4\u00d7\u817f 5/7 \u540c\u7a97\u53cc\u8c03\uff1b"
    "\u2461QA \u6355\u83b7\u9762 cell \u4e09\u5b57\u6bcd\u2260\u653f\u4f53\u683c\u771f\u503c\u2014\u2014FAC=FACE_ERROR_HOT/ORA=ORANGE_COOL \u7686 [:100] \u622a\u65ad\u9762\uff0c"
    "\u5224\u771f\u503c\u4ee5\u76d8\u4e0a CALL \u4ef6+call_latest.json \u4e3a\u51c6\uff08git clean=canonical\uff09\uff1b"
    "\u2462\u6355\u83b7\u9762\u51fa FACE_ERROR=\u7ade\u6001\u89c2\u5bdf\u7a97\u8bc1\u636e\u975e\u673a\u5236\u7ea2\uff0c\u5148\u6838\u6b63\u5178\u9762\u518d\u5b9a\u6027\u3002"
    "How to apply\uff1a\u503c\u5b88\u8f6e\u70b9\u706b\u5e8f=S6 \u5168\u94fe rc0 \u6536\u9f50\u2192qa_ignite\u2192qa_poll \u7ec8\u6001\u2192close \u8fdb\u4f4d\uff08r640 \u5e8f\u5f8b\u517c\u5bb9\uff09\uff1b"
    "\u8f6e\u62a5\u544a\u987b\u533a\u5206\u300c\u6355\u83b7\u9762\u77ac\u6001\u300d\u4e0e\u300c\u76d8\u4e0a\u6b63\u5178\u9762\u300d\u4e24\u6001\u3002"
)
raw = open(P, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
block = ENTRY.encode("utf-8")
sha16 = hashlib.sha256(block).hexdigest()[:16]
rec_line = ("- \u5bf9\u8d26\u884c r749 bm-c: entry bytes=%d sha16=%s verbatim-in-file (direct-write r666 precedent; "
            "main CODELY.md 30,684B under 30,720B cap untouched; zero-loss asserted)" % (len(block), sha16)).encode("utf-8")
if not raw.endswith(eol):
    raw += eol
with open(P, "wb") as f:
    f.write(raw + block + eol + rec_line + eol)
print("appended bytes=%d sha16=%s new_size=%d eol=%r" % (
    len(block), sha16, len(raw) + len(block) + 2 * len(eol) + len(rec_line), eol))
