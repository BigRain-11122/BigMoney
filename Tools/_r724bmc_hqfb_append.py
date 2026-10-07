"""r724 bm-c: append one HQ-FEEDBACK improvement line (F-20261008-02,
orphan-probe shared-filename rebase-UU tax -> per-machine suffix law).
Idempotent: skips if the line marker already exists. UTF-8 no BOM."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FB = os.path.join(ROOT, "HQ-FEEDBACK.md")

LINE = (
    "- F-20261008-02 [bm-c r724 2026-10-08 03:4x\u00b7S0 rebase \u5b9e\u5f39\u00b7\u591a\u673a daemon "
    "\u4ea7\u7269\u547d\u540d\u5f8b] **\u591a\u673a\u5171\u5199\u63a2\u9488/daemon \u4ea7\u7269\u6587\u4ef6"
    "\u65e0\u673a\u5668\u540e\u7f00=\u6bcf\u8f6e pull --rebase \u56fa\u5b9a UU \u51b2\u7a81\u7a0e\uff08\u5171\u4eab"
    "\u540d\u6574\u6587\u4ef6\u8986\u5199\u578b\uff09**\u2014\u2014\u73b0\u8c61\uff1aTools/orphan_face_probe.py "
    "\u62a5\u544a\u8def\u5f84 results/_orphan_face_probe.json \u4e3a\u65e0\u540e\u7f00\u5171\u4eab\u540d\uff0c"
    "\u4e09\u673a\u8f6e\u73ed\u6bcf\u8f6e\u5404\u8dd1\u63a2\u9488\u6574\u6587\u4ef6\u8986\u5199\uff0c\u51e1\u4e24"
    "\u673a\u540c\u7a97\u5404\u8dd1\u5373\u4ea7 UU \u9700\u4eba\u5de5\u89e3\uff08\u672c\u4f8b bm-c r724 \u649e "
    "1-UU\uff1bbm-a r859 \u540c\u7a97 17-UU \u98ce\u66b4\u4e2d\u542b\u540c\u578b\u4ef6\uff09\uff1b\u5bf9\u7167"
    "\u9762=\u5e26\u673a\u5668\u540e\u7f00\u65cf\uff08results/saturation_engine/face_bm-c.json\u3001"
    "*_state.bm-c.json\u3001idle_trigger.bm-c.json\uff09\u4ece\u4e0d\u51b2\u7a81\u3002\u8bc1\u636e=r724 "
    "\u5b9e\u5f39\u5168\u7a0b\uff1a\u672c\u673a 03:35:19 \u63a2\u9488 commit 05daaa412 rebase \u65f6 vs "
    "origin bm-a 03:08:12 \u63a2\u9488\u5bf9\u649e UU\u2192python Tools/treasure_guard.py restore rc0"
    "\uff08reproducible-artifact \u7c7b\u653e\u884c\uff09\u2192live-wins newer-ts take-theirs\u2192\u539f"
    "\u5b50 add+continue\u2192rebase rc0 86b7cb21f\uff08\u51b2\u7a81\u9762\u53cc\u4fa7 blob ts \u884c git "
    "show \u53ef\u9a8c\uff09\u3002\u5efa\u8bae\u65b9\u5411\uff08\u96c6\u56e2\u666e\u9002\u5f8b\uff09\uff1a"
    "\u2460orphan_face_probe.py \u62a5\u544a\u8def\u5f84\u6539 per-machine \u540e\u7f00 results/"
    "_orphan_face_probe.<machine_id>.json\uff08\u8bfb fleet/machine.json\u00b7\u4e0e face_<id>.json/"
    "_state.<id>.json \u540c\u8303\u5f0f\uff09\u2014\u2014\u5b64\u513f\u5224\u5b9a\u4e0e\u300c\u5b64\u513f"
    "\u9762=N\u300d\u8f6e\u62a5/\u5fc3\u8df3\u884c\u5747\u4ea7\u81ea\u672c\u673a\u63a2\u9488 stdout\uff0c"
    "\u65e0\u8de8\u673a\u8bfb\u8be5\u4ef6\u6d88\u8d39\u9762=\u96f6\u7834\u574f\uff1b\u2461\u63a8\u5e7f\u5f8b"
    "\uff1a\u591a\u673a\u4ed3\u5e93\u4e00\u5207 daemon/\u63a2\u9488\u65b0\u4ea7\u7269\u6587\u4ef6\u8bbe\u8ba1"
    "\u65f6\u5fc5\u987b\u5e26\u673a\u5668\u540e\u7f00\uff08\u65e2\u6709\u65e0\u540e\u7f00\u5171\u4eab\u540d"
    "\u4ef6\u5b58\u91cf\u968f\u89e6\u968f\u6539\uff09\u3002\u72b6\u6001=open\n"
)


def main():
    txt = io.open(FB, encoding="utf-8").read()
    if "F-20261008-02" in txt:
        print("HQ-FEEDBACK F-20261008-02 already present, skip")
        return 0
    if not txt.endswith("\n"):
        txt += "\n"
    txt += LINE
    io.open(FB, "w", encoding="utf-8", newline="").write(txt)
    print("HQ-FEEDBACK appended F-20261008-02, bytes now", os.path.getsize(FB))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
