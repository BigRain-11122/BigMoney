# r692 bm-a closeout addendum append (push-race record + delivery stamp)
line = (
    "2026-10-04T19:3x+08:00 | r692 (bm-a) addendum | \u6536\u53e3 push-race "
    "\u5b9e\u5f55: \u4e3b commit \u540e origin \u524d\u79fb 13 commits(bm-b r687/688 + bm-c r490/491 "
    "\u540c\u7a97 S6 \u6ce2+\u4fdd\u6301 keepalive)\u2192merge \u9075 20-UU \u5168\u91cf\u6e05\u70b9(r657-\u2460 "
    "\u94fa\u74e6\u5f8b: porcelain UU \u8ba1\u6570=20 \u975e\u7ba1\u9053\u5c3e\u7a97)\u2192per-face resolver "
    "(_r692bma_merge_resolve.py\u00b7\u4e8b\u5148\u63a2\u9488\u88c1\u5b9a: pool trio "
    "owner_since theirs 19:10:12>ours 18:58:12 \u4e14\u96f6 ours-unique "
    "\u6761\u76ee=\u6bcf\u6761 max-merge \u7b49\u4ef7\u53d6 theirs r474 \u5f8b\u00b7crash_fuse "
    "owner-semantics theirs r687/r690 \u5148\u4f8b\u00b7\u5176\u4f59 17 \u9762 ts-freshness "
    "ours15/theirs2\u00b7token per-key union side_pick=0\u2192\u6574\u9762 fallback ours "
    "r466 \u5f8b)\u2192marker \u884c\u9996\u626b\u63cf+json reparse 20/20 PASS\u2192\u5355\u6b21 "
    "git add \u5168\u6e05\u5355(r673 \u5f8b)\u2192merge commit bcefd4197\u2192push_verify "
    "DELIVERED(tip==remote bcefd4197\u00b7ahead0\u00b7behind0)\u00b7\u96f6 --no-verify\u00b7\u53cc\u722a "
    "\u96f6\u62e6\u622a | \u672c\u5730\u672a\u8fbe origin commit \u6570 0 (push_verify \u81ea\u8bc1 "
    "bcefd4197) | \u62a5\u544a\u4e3b\u884c __PUSH_STAMP__ \u4f4d=\u62a5\u544a\u5148\u4e8e push "
    "\u843d\u76d8\u7684\u5b9e\u5f55(\u672c\u884c\u5373\u9001\u8fbe\u6233\u5b9a\u4ef6)"
)
path = "round_reports-bm-a.md"
data = open(path, "rb").read()
marker = "| r692 (bm-a) addendum |"
assert data.count(marker.encode("utf-8")) == 0, "addendum already present"
if not data.endswith(b"\n"):
    data += b"\n"
data += line.encode("utf-8") + b"\n"
with open(path, "wb") as f:
    f.write(data)
chk = open(path, "rb").read()
assert chk.count(marker.encode("utf-8")) == 1
print("addendum appended; r692 addendum marker count == 1")
