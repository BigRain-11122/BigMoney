# r825 bm-b: direct-write append of one new PS pit to research/pit-ps.md
# (post-split direct-write convention, r635/r639 precedent family).
# Bytes-safe: reads/writes pit-ps.md in binary; accounting line cites the
# md5/size of the ENTRY block only (r635 convention).
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIT = os.path.join(ROOT, "research", "pit-ps.md")

ENTRY = (
    "- [2026-10-10 08:5x r825 bm-b] **PS 2>&1 \u5408\u6d41 native stderr "
    "\u8fdb\u7ba1\u9053 \u2192 shell \u6574\u4f53 exit 1 \u5047\u8d25\u5751"
    "\uff08E4 \u63a2\u9488\u5b9e\u5f39\u00b7\u540c\u7a97\u5bf9\u7167\u4e09"
    "\u8fde\u5b9a\u8c34\uff09**: python \u63a2\u9488\u672c\u4f53 rc=0 \u4e14"
    "\u8bc1\u636e\u4ef6\u5df2\u539f\u5b50\u843d\u76d8\uff0c\u4f46 `python "
    "... 2>&1 | Select-Object -Last 14` \u7684\u5de5\u5177\u9762 Exit "
    "Code=1\u2014\u2014PS5.1 \u628a native stderr \u884c\u7ecf 2>&1 \u5408"
    "\u6d41\u5305\u88c5\u6210 ErrorRecord \u8fdb\u7ba1\u9053\u2192\u672b\u7ba1"
    "\u9053 $?=False\u2192powershell.exe -Command \u6574\u4f53\u9000\u51fa"
    "\u7801 1\uff08\u540c\u7a97\u5bf9\u7167\uff1a\u65e0 stderr \u8f93\u51fa"
    "\u7684\u547d\u4ee4\u540c\u5f0f 2>&1 \u7ba1\u9053 exit 0\uff1b\u88f8\u8dd1"
    " stderr \u76f4\u901a exit 0\uff1b`> $null` \u91cd\u5b9a\u5411\u5f0f "
    "exit 0\uff09\u2014\u2014rc \u81ea\u8bc1\u9762\u88ab shell \u5c42\u5047"
    "\u8d25\u6c61\u67d3\uff0c\u4e0e r817\uff08Select -First \u622a\u6740\u7559"
    "\u9648\u503c\uff09\u59ca\u59b9\u9762=\u5408\u6d41\u9762\u3002How to "
    "apply: \u9700\u8981\u538b\u8f93\u51fa\u7684 native \u8c03\u7528\u4e00"
    "\u5f8b `> \u6587\u4ef6` \u5168\u91cf\u843d\u76d8\u540e grep \u6d88\u8d39"
    "\uff08\u7981 2>&1 | \u7ba1\u9053\u5408\u6d41\uff09\uff1b\u5de5\u5177"
    "\u9762 Exit Code \u8bfb\u53d6\u524d\u5148\u533a\u5206\u300cshell \u7ba1"
    "\u9053\u5047\u8d25\u300d\u4e0e\u300cnative \u771f\u8d25\u300d\u2014\u2014"
    "\u6709 stderr \u4ea7\u566a\u7684\u547d\u4ee4\uff08tqdm \u8fdb\u5ea6\u6761"
    "\u65cf\uff09\u5c24\u751a\uff1brc \u5224\u5b9a\u6c38\u8fdc\u663e\u5f0f "
    "`echo rc=$LASTEXITCODE` \u7d27\u8ddf\u76ee\u6807\u547d\u4ee4\u3002\n"
)

with open(PIT, "rb") as f:
    blob = f.read()
if not blob.endswith(b"\n"):
    blob += b"\n"
entry_b = ENTRY.encode("utf-8")
size = len(entry_b)
md5 = hashlib.md5(entry_b).hexdigest()
acct = (
    "> Direct-write line (r825 bm-b, post-split convention direct-write): "
    "+1 new pit (PS 2>&1 stderr-merge pipeline false-fail face, explicit "
    "rc-echo law) - appended %d B - LF blob net - md5=%s - file-tail "
    "append - the in-file accounting line is authoritative.\n" % (size, md5)
)
with open(PIT, "wb") as f:
    f.write(blob + entry_b + acct.encode("utf-8"))
print("appended entry %d B md5=%s; pit-ps.md now %d B"
      % (size, md5, os.path.getsize(PIT)))
sys.exit(0)
