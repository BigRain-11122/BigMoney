# -*- coding: utf-8 -*-
"""r693 bm-c pit-tooling.md truncation heal (line-level union per
treasure_guard rc3 law): working copy truncated to 0B by a dead
`open(p,'wb')` boolean-chain (never wrote); guard FORBIDS origin-restore
for registry class -> legal path = line-level union. Current face = 0
lines, so union == HEAD blob lines verbatim. Zero-loss assert = every
HEAD line present in output; byte-equality with HEAD blob; then the
r693 pit block is re-appended CORRECTLY (str.encode guards, plain rb
re-read) + main CODELY pointer + receipt. Supersedes the broken
_r693bmc_codely_increment.py run (its target write already healed here;
receipt written only on full success)."""
import hashlib
import json
import os
import subprocess
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
    "\u5fc5\u7528\u672b\u884c\u53e3\u5f84\uff1b\u5bf9\u53f0\u8d26\u505a\u4efb\u4f55 verdict \u7edf\u8ba1\u5148\u6309 id \u5206\u7ec4\u53d6\u672b\u884c\uff0c\u7981\u5168\u884c\u8ba1\u6570\u3002"
    "\uff08\u540c\u7a97\u9644\u5f55\u5751\uff1a`open(p,'wb') and open(p,'rb').read()` \u5e03\u5c14\u94fe=\u6b7b\u622a\u65ad\u2014\u2014wb \u6253\u5f00\u5373\u6e05\u96f6\u3001\u672a\u5199\u5373\u5f03\uff0c"
    "r693 \u5b9e\u5f39\u5f53\u573a\u622a\u65ad pit-tooling.md\uff1b\u6b63\u6cd5=\u6052\u7528 open(p,'wb') \u540e\u5fc5\u7d27\u8ddf write+\u8bfb\u56de\u9a8c\u8bc1\uff0c\u7981\u4e00\u5207 'wb' \u6253\u5f00\u65e0\u5199\u8868\u8fbe\u5f0f\uff09\n"
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
               "action": "direct-write increment (r429/r666/r673 pattern) "
                         "+ truncation heal (line-level union per guard rc3)"}

    # -- STEP 1: line-level union heal of truncated target --
    cur = open(TARGET, "rb").read()
    p = subprocess.run(["git", "-C", ROOT, "show", "HEAD:research/pit-tooling.md"],
                       capture_output=True)
    assert p.returncode == 0, "git show HEAD blob fail"
    head = p.stdout
    cur_lines = cur.splitlines()
    head_lines = head.splitlines()
    # union: keep every current line that exists in HEAD (current is empty here),
    # then every HEAD line not already kept -> == HEAD when current empty
    head_set = set(head_lines)
    out_lines = [l for l in cur_lines if l in head_set]
    kept = set(out_lines)
    out_lines += [l for l in head_lines if l not in kept]
    eol_t = eol_of(head)
    rebuilt = (eol_t.join(out_lines) + eol_t) if out_lines else b""
    # zero-loss: every HEAD line present in rebuilt
    rb_lines = set(rebuilt.splitlines())
    missing = [l for l in head_lines if l not in rb_lines]
    assert not missing, "union zero-loss FAIL: %d HEAD lines missing" % len(missing)
    with open(TARGET, "wb") as fh:
        fh.write(rebuilt)
    post = open(TARGET, "rb").read()
    assert post == head or post == head.rstrip(b"\r\n") + eol_t, \
        "heal byte-equality FAIL (post=%d head=%d)" % (len(post), len(head))
    receipt["heal"] = {
        "truncated_bytes": len(cur), "head_bytes": len(head),
        "rebuilt_bytes": len(post), "zero_loss": True,
        "method": "line-level union (guard rc3 law, registry class)"}
    print("HEAL OK: pit-tooling.md %d -> %d bytes (HEAD blob union)" %
          (len(cur), len(post)))

    # -- STEP 2: pit entry append (fixed guards) --
    guard = "post_review \u7ea2\u884c\u5224\u5b9a=\u6bcf id \u672b\u884c\u53e3\u5f84\u5751".encode("utf-8")
    assert post.count(guard) == 0, "rerun guard: pit already in target"
    block = PIT.encode("utf-8")
    with open(TARGET, "ab") as fh:
        fh.write(block)
    post2 = open(TARGET, "rb").read()
    assert post2.count(guard) == 1, "post-verify pit count==1"
    assert block in post2, "zero-loss: appended block not verbatim"
    receipt["target_bytes_pre"] = len(post)
    receipt["target_bytes_post"] = len(post2)
    receipt["appended_bytes"] = len(block)
    receipt["appended_sha16"] = hashlib.sha256(block).hexdigest()[:16]
    receipt["target_under_line"] = len(post2) <= LIMIT

    # -- STEP 3: compact pointer -> main --
    raw_m = open(MAIN, "rb").read()
    receipt["main_bytes_pre"] = len(raw_m)
    eol_m = eol_of(raw_m)
    guard_m = "\u57df\u6307\u9488\u00b7r693 bm-c".encode("utf-8")
    assert raw_m.count(guard_m) == 0, "rerun guard: pointer already in main"
    assert raw_m.endswith(eol_m), "main tail EOL gate"
    pblock = POINTER.encode("utf-8")
    with open(MAIN, "ab") as fh:
        fh.write(pblock)
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
