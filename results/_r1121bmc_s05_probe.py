# -*- coding: utf-8 -*-
# r1121 bm-c: D-19 opening dual-delta probe (pinned methods: ORD=content-bytes sha1 r977 / DEC=raw-blob sha256)
# + T0 stamp-face measurements for the W279 builder authoring (r1077 measured law). Read-only.
import io, json, hashlib, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
GRP = r"K:\Fluxgroup\FluxGroup"

def gshow(path):
    r = subprocess.run(["git", "-C", GRP, "show", "origin/main:" + path], capture_output=True)
    if r.returncode != 0:
        raise SystemExit("git show fail %s: %s" % (path, r.stderr[:200]))
    return r.stdout

subprocess.run(["git", "-C", GRP, "fetch", "origin"], capture_output=True)
ord_bytes = gshow("docs/orders.md")
dec_bytes = gshow("docs/decisions.md")
ord_sha = hashlib.sha1(ord_bytes).hexdigest()
dec_sha = hashlib.sha256(dec_bytes).hexdigest()
st = json.load(open("state-bm-c.json", encoding="utf-8"))
print("ORD content-sha1:", ord_sha)
print("ORD watermark  :", st.get("last_orders_sha"))
print("ORD delta      :", ord_sha != st.get("last_orders_sha"))
print("DEC raw-blob sha256:", dec_sha)
print("DEC watermark  :", st.get("last_decisions_sha"))
print("DEC delta      :", dec_sha != st.get("last_decisions_sha"))

# T0 stamp measurements on the frozen W278 face (LF-normalized)
t0 = io.open(r"results/_w279bmc_w278_frozen_face.txt", encoding="utf-8", newline="").read().replace("\r\n", "\n")
print("T0 bytes:", len(t0.encode("utf-8")))
for pat in ["10:3x", "09:5x", "09:0x", "15:1x", "13:5x", "15:0x", "07:2x", "07:4x", "08:1x",
            "05:3x", "05:2x", "05:5x", "11:4x", "12:5x", "13:0x", "16:0x"]:
    print("T0 count %-8r = %d" % (pat, t0.count(pat)))
# key faces for the W279 prereg (zero-floor audit: next-wave faces must be 0 on T0)
for pat in ["_w279bmc", "n1_w278", "W279p_", "W280p_", "629_101", "631_101", "631_301..631_500",
            "631_101..633_100", "611,720", "611720", "1,038,135", "1038135", "900c23fe7d",
            "df1aaba72a", "b6f486af35", "0a92fcc28f", "60e630918f", "b965e2ecf0",
            "MSG-20261019-145x", "W279 freezer", "W280 freezer", "第二十八次连续", "第二十九次连续",
            "第三十次连续", "第 269 波", "第 98 枚", "池第 277 枚", "连续二十七波", "连续二十八波"]:
    print("T0 count %-22r = %d" % (pat, t0.count(pat)))
