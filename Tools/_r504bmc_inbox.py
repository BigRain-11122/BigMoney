"""r504 bm-c: inbox unread scan (unprocessed msgs to bm-c/ALL) + N2-W15
completion evidence capture (shard result faces)."""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    # inbox unread
    inbox = os.path.join(ROOT, "fleet", "inbox")
    proc = os.path.join(inbox, "processed")
    unread = [f for f in sorted(glob.glob(os.path.join(inbox, "*.md"))
                                + glob.glob(os.path.join(inbox, "*.json")))
              if os.path.isfile(f)]
    print("UNREAD-INBOX", len(unread))
    for f in unread:
        with open(f, encoding="utf-8", errors="replace") as fh:
            head = fh.read(400)
        print("---", os.path.basename(f))
        print(head)

    # N2-W15 shard result faces
    pats = ["*n2*w15*", "*N2*W15*"]
    seen = set()
    for pat in pats:
        for p in glob.glob(os.path.join(ROOT, "results", "**", pat),
                           recursive=True):
            if p in seen:
                continue
            seen.add(p)
            print("N2W15-FACE", os.path.relpath(p, ROOT),
                  os.path.getmtime(p), os.path.getsize(p))


if __name__ == "__main__":
    main()
