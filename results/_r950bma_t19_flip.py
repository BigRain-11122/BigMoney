# r950 bm-a helper: flip T19 tech.md row to done + append consumption record.
# Fresh read-modify-write (multi-writer file discipline); ASCII source law.
import io
import sys

p = "state/queue/tech.md"
txt = io.open(p, encoding="utf-8", newline="").read()
lines = txt.splitlines()
out, flipped = [], False
for ln in lines:
    if ln.startswith("| T19 ") and ln.rstrip().endswith("| open |"):
        ln = ln.rstrip()[: -len("open |")] + "done |"
        flipped = True
    out.append(ln)
assert flipped, "T19 open row not found"
rec = (
    "> r950 \u6d88\u8017\u8bb0\u5f55\uff08bm-a\uff09\uff1aT19 \u672c\u8f6e\u5b8c\u6210\u51fa\u5217\uff08**\u961f\u5217\u79cd\u5b50\u95ed\u5408\u65cf\u673a\u68c0\u95f8 `scripts/queue_seed_gate.py`\uff08T-19 \u5efa\u9762\u540c\u8f6e\u51fa\u5217\u3001\u5efa\u9762\u540c\u8f6e\u5b8c\u6210\u5148\u4f8b\uff09**\uff1a"
    "\u2460\u5355\u6e90\u5f8b=9 \u952e\u6ce8\u518c\u8868 import \u81ea science_gates.CLOSED_FAMILIES \u96f6\u91cd\u58f0\u660e+face \u8868\u2194\u6ce8\u518c\u8868\u4e00\u81f4\u6027 selftest \u817f\uff08set \u6052\u7b49+9 \u952e\u8ba1\u6570\uff09\uff1b"
    "\u2461\u53cc\u9762=\u767b\u8bb0\u65f6 check \u5355\u7b7d lint\uff08rc3=rejected\uff1awork \u6587\u672c\u547d\u4e2d\u95ed\u5408\u65cf\u8bcd\u9762\u2192\u7981\u5165\u961f\u9664\u975e\u58f0\u660e\u8be5\u65cf reopen \u901a\u9053 per O-20260925-1105\u3014microcap=CEO \u4e00\u53e5\u8bdd\u552f\u4e00\u3015\u00b7--reopen \u58f0\u660e=reopen_channel_declared rc0\uff09"
    "+scan \u5168\u961f\u5217\u6d3b\u884c\uff08open/unknown\uff09\u536b\u751f\u5ba1\u8ba1\uff08exit 0 \u5e72\u51c0/3 \u6d3b\u884c HARD \u78b0\u649e=\u5f53\u503c\u8f6e\u987b\u88c1\u5b9a\u51fa\u5217/2 \u673a\u5236\u6545\u969c\uff09\uff1b"
    "\u2462\u5047\u9633\u6027\u63a7\u5236=HARD \u53ea\u770b work \u5217\u00b7pointer \u5217\u547d\u4e2d=note \u4e0d\u963b\u65ad\uff08meta \u884c\u5408\u6cd5\u5f15\u7528\u95ed\u5408\u65cf digest\u2014\u2014T19 \u672c\u884c\u6307\u9488\u5e26 e6-microcap-closed-adjudication.md \u5b9e\u8bc1 note \u9762\uff09+done/closed \u5386\u53f2\u88c1\u5b9a\u884c\u6c38\u4e0d\u590d\u62a5\uff1b"
    "\u2463\u8bcd\u9762=\u65cf\u8eab\u4efd\u6807\u8bb0\u4fdd\u5b88\u9762\uff08bare \u671f\u8d27/\u60c5\u7eea\u975e face\u2014\u2014E8 \u8de8\u671f\u4ef7\u5dee CLEAR \u5b9e\u8bc1=\u975e CTA \u8d8b\u52bf\u65cf\uff09\uff1b"
    "\u2464selftest 17/17 hermetic \u53cc\u8dd1\u5b57\u8282\u6052\u7b49+live \u5b9e\u5f39=scan CLEAR\uff08tech 1 \u6d3b\u884c+explore 5 \u6d3b\u884c\u00b70 findings\u00b71 note\uff09+check \u4e09\u6001 live-fire\uff08E6 \u7b7d rejected rc3/\u5e26 reopen \u58f0\u660e rc0/\u5e72\u51c0\u7b7d open\uff09\uff1b"
    "\u2465\u63a5\u7ebf=Tools/iteration_prompt.txt S3 \u767b\u8bb0\u524d\u7f6e\u817f\uff08ASCII \u7eaf\u4f53\u00b7leg present once \u5b9e\u8bc1\uff09\uff1b\u8bc1\u636e=results/queue_seed_gate.json\uff1b"
    "\u6cbb\u7406\u6559\u8bad\u627f\u63a5=E6 \u5efa\u9762\u8f6e r804 \u672a\u6838\u95ed\u5408\u65cf\u7684\u6839\u6cbb\u9762\uff08\u7981\u6362\u76ae\u91cd\u5f00\u9884\u5907\u9762\u518d\u751f\uff09\u3002\u6280\u672f\u961f\u5217 1\u21920\u3002"
)
out.append(rec)
new = "\n".join(out) + "\n"
io.open(p, "w", encoding="utf-8", newline="").write(new)
chk = io.open(p, encoding="utf-8").read()
t19ln = [l for l in chk.splitlines() if l.startswith("| T19 ")]
assert len(t19ln) == 1 and t19ln[0].rstrip().endswith("| done |"), t19ln
assert rec[:30] in chk
print("T19 flipped to done; consumption record appended; lines", len(chk.splitlines()))
