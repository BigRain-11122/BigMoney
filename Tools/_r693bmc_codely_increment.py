# -*- coding: utf-8 -*-
"""r693 bm-c CODELY increment (direct-write pattern r429/r666/r673):
new pit = post_review red-check latest-row-per-item canon (naive all-row
verdict counts double-sided false read; append-only ledger keeps flipped
NO rows). Full entry -> research/pit-tooling.md tail; compact pointer
line -> CODELY.md main tail; receipt -> results/_r693bmc_codely_increment.json
with byte+sha16 accounting, main <=30720B and target <=30720B asserts,
zero-loss = appended bytes present verbatim in target."""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "CODELY.md")
TARGET = os.path.join(ROOT, "research", "pit-tooling.md")
RECEIPT = os.path.join(ROOT, "results", "_r693bmc_codely_increment.json")
LIMIT = 30720

PIT = (
    "- [2026-10-07 17:5x r693 bm-c] **post_review \u7ea2\u884c\u5224\u5b9a=\u6bcf id \u672b\u884c\u53e3\u5f84\u5751\uff08r693 \u5b9e\u5f39\u00b7\u5f53\u573a\u6b63\u5178\u5316\uff09**\uff1a"
    "append-only \u53f0\u8d26 results/post_review.jsonl \u4fdd\u7559\u5168\u90e8\u5386\u53f2 derive \u884c\u2014\u2014\u540c\u4e00 item \u7684 NO \u884c"
    "\uff08\u5982\u6bcf\u65e5 00:0x C9 \u626b\u63cf\u4e0e S6 \u5199\u8005\u7ade\u6001\u7684 json_field \u89e3\u6790\u9519\u6682\u6001\u7ea2\uff09\u4f1a\u88ab\u540e\u7eed derive \u884c\u7ffb\u7eff"
    "\uff08T-81 \u5b9e\u8bc1\uff1a00:16:19 NO\u00d73 \u2192 16:50:29 YES 8/8\uff09\u4f46\u884c\u672c\u8eab\u6c38\u4e0d\u5220\u9664\uff1bnaive \u5168\u884c verdict \u8ba1\u6570"
    "\uff08count(verdict==NO)=46\uff09\u6216\u300c0 fail\u300d\u5b57\u9762 grep=\u53cc\u5411\u5047\u8bfb\uff08\u524d\u8005\u5047\u7ea2\u00b7\u540e\u8005\u56e0\u5b9e\u73b0\u8bcd\u6c47 YES/WAIT/NO"
    "\u2260\u6cd5\u5178\u8349\u6848 pass/fail/pending \u800c\u5047\u7eff\uff09\u3002\u6b63\u6cd5=\u7ea2\u884c\u5224\u5b9a\u53d6\u6bcf id \u672b\u884c\uff08file \u5e8f=\u65f6\u95f4\u5e8f\u00b7\u672b\u884c=\u6700\u65b0 derive\uff09\uff0c"
    "\u6d3b\u7ea2=\u672b\u884c verdict==NO\uff1br693 \u5b9e\u6d4b 53 unique items=48 YES/5 WAIT/0 NO \u96f6\u6d3b\u7ea2\u3002"
    "How to apply\uff1a\u4e00\u5207\u300cpost_review \u7ea2\u884c=\u4e0b\u4e00\u8f6e P0\u300d\u6d88\u8d39\u9762\uff08iteration_prompt S3/\u590d\u5ba1\u7eaa\u5f8b/\u6218\u62a5\u590d\u5ba1\u5217\uff09"
    "\u5fc5\u7528\u672b\u884c\u53e3\u5f84\uff1b\u5bf9\u53f0\u8d26\u505a\u4efb\u4f55 verdict \u7edf\u8ba1\u5148\u6309 id \u5206\u7ec4\u53d6\u672b\u884c\uff0c\u7981\u5168\u884c\u8ba1\u6570\u3002\n"
)
POINTER = (
    "- \u57df\u6307\u9488\u00b7r693 bm-c\uff1apost_review \u7ea2\u884c\u5224\u5b9a=\u6bcf id \u672b\u884c\u53e3\u5f84\u5751"
    "\uff08\u5386\u53f2 NO \u884c\u7ffb\u7eff\u4e0d\u5220\u00b7\u5168\u884c\u8ba1\u6570\u5047\u8bfb\uff09\u76f4\u5199 pit-tooling.md"
    "\u00b7\u6536\u636e _r693bmc_codely_increment.json\n"
)


def eol_of(raw):
    return b"\r\n" if raw.count(b"\r\n") >= 10 else b"\n"


def main():
    receipt = {"round": 693, "machine": "bm-c",
               "action": "direct-write increment (r429/r666/r673 pattern)",
               "pit": "post_review red-check latest-row-per-item canon"}

    # -- pit entry -> domain file --
    raw_t = open(TARGET, "rb").read()
    receipt["target_bytes_pre"] = len(raw_t)
    eol_t = eol_of(raw_t)
    guard = b"post_review \u7ea2\u884c\u5224\u5b9a=\u6bcf id \u672b\u884c\u53e3\u5f84\u5751"
    assert raw_t.count(guard) == 0, "rerun guard: pit already in target"
    assert raw_t.endswith(eol_t), "target tail EOL gate"
    block = PIT.encode("utf-8")
    new_t = raw_t + block
    open(TARGET, "wb").write(new_t)
    post_t = open(TARGET, "wb") and open(TARGET, "rb").read()
    assert post_t.count(guard) == 1, "post-verify pit count==1"
    assert block in post_t, "zero-loss: appended block not verbatim in target"
    receipt["target_bytes_post"] = len(post_t)
    receipt["appended_sha16"] = hashlib.sha256(block).hexdigest()[:16]
    receipt["appended_bytes"] = len(block)
    receipt["target_under_line"] = len(post_t) <= LIMIT

    # -- compact pointer -> main --
    raw_m = open(MAIN, "rb").read()
    receipt["main_bytes_pre"] = len(raw_m)
    eol_m = eol_of(raw_m)
    guard_m = b"\u57df\u6307\u9488\u00b7r693 bm-c"
    assert raw_m.count(guard_m) == 0, "rerun guard: pointer already in main"
    assert raw_m.endswith(eol_m), "main tail EOL gate"
    pblock = POINTER.encode("utf-8")
    new_m = raw_m + pblock
    open(MAIN, "wb").write(new_m)
    post_m = open(MAIN, "rb").read()
    assert post_m.count(guard_m) == 1, "post-verify pointer count==1"
    receipt["main_bytes_post"] = len(post_m)
    receipt["main_pointer_bytes"] = len(pblock)
    receipt["main_under_line"] = len(post_m) <= LIMIT
    receipt["zero_loss"] = True

    assert receipt["main_under_line"], "MAIN OVER 30720B LINE"
    assert receipt["target_under_line"], "TARGET OVER 30720B LINE"

    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    print(json.dumps(receipt, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
