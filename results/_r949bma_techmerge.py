"""r949 bm-a tech.md proper merge: base :2: (bm-b T18 + r826 record) + our
T19 row inserted after their T18 row. Byte-safe raw write, no BOM."""
import subprocess

GIT = r"C:\Program Files\Git\cmd\git.exe"
REL = "state/queue/tech.md"

base = subprocess.run([GIT, "show", ":2:" + REL], capture_output=True).stdout
assert base.startswith(b"#"), "base side unexpected"

T19 = ("| T19 | queue \u79cd\u5b50\u9762\u95ed\u5408\u65cf\u673a\u68c0\u95f8\uff08P2/P3 \u961f\u5217\u767b\u8bb0\u65f6\u79cd\u5b50\u6587\u672c vs science_gates.CLOSED_FAMILIES \u952e/\u5224\u8d1f\u8bcd\u9762\u673a\u68c0\u2014\u2014"
       "E6 \u649e\u95e8\u5b9e\u5f55 r949 bm-a\uff1a\u5efa\u9762\u8f6e r804 \u672a\u6838\u95ed\u5408\u65cf=\u9648\u65e7\u9762\u5165\u961f\u3010725fa437"
       "\u3011\uff1b\u95f8=\u767b\u8bb0\u5668\u5185\u7f6e lint \u6216\u767b\u8bb0\u8f6e\u5f3a\u5236\u6838\u9a8c\u6b65\uff0c\u9632\u6362\u76ae\u91cd\u5f00\u9884\u5907\u9762\u518d\u751f\u3002"
       "\u884c\u53f7 T19=\u672c\u884c\u3010\u539f\u62df T18 \u649e bm-b r826 \u961f\u5934\u649e\u5934\u63a2\u9488\u540c\u7a97\u540c\u53f7\u00b7\u540e\u5230\u8ba9\u53f7 per fleet README \u00a74\u00b7r949 \u6ce8\u8bb0\u3011 | "
       "scripts/science_gates.py+state/queue/explore.md+research/digests/DIGEST-20261010-e6-microcap-closed-adjudication.md | open |")

lines = base.split(b"\n")
out = []
inserted = False
for ln in lines:
    out.append(ln)
    if not inserted and ln.startswith(b"| T18 |"):
        out.append(T19.encode("utf-8"))
        inserted = True
assert inserted, "T18 row not found in base"
merged = b"\n".join(out)

n_t18 = sum(1 for l in merged.split(b"\n") if l.startswith(b"| T18 |"))
n_t19 = sum(1 for l in merged.split(b"\n") if l.startswith(b"| T19 |"))
assert n_t18 == 1 and n_t19 == 1, "row count wrong: T18=%d T19=%d" % (n_t18, n_t19)
assert "队头撞头探针".encode("utf-8") in merged, "bm-b T18 probe row lost"
assert "> r826 消耗记录".encode("utf-8") in merged, "r826 record lost"

open(REL.replace("/", "\\"), "wb").write(merged)
print("tech.md merged: T18(bm-b probe) + T19(ours) + r826 record; bytes=%d" % len(merged))
