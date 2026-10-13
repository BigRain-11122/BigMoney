import json, os, glob

INBOX = r"fleet\inbox"
for p in sorted(glob.glob(os.path.join(INBOX, "*.json")) + glob.glob(os.path.join(INBOX, "*.md"))):
    name = os.path.basename(p)
    try:
        txt = open(p, encoding="utf-8", errors="replace").read()
    except Exception as e:
        print(name, "READ_ERR", e); continue
    d = {}
    try:
        d = json.loads(txt)
    except Exception:
        pass
    to = d.get("to") or d.get("recipient") or ""
    frm = d.get("from") or d.get("sender") or ""
    if ("bm-a" in str(to)) or ("ALL" in str(to)) or (not to and "bm-a" in txt[:200]):
        print(f"UNREAD? {name} | to={to} from={frm} | {txt[:150]!r}")
print("---")
processed = sorted(os.path.basename(p) for p in glob.glob(os.path.join(INBOX, "processed", "*")))
print(f"processed count: {len(processed)}")
# show the 5 most recent processed for context
for n in processed[-5:]:
    print("  processed:", n)
