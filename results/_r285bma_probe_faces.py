"""R285 byte-face probe for results/post_review_criteria.json (r255 five-face law)."""
import json, re

PATH = "results/post_review_criteria.json"
raw = open(PATH, "rb").read()
print("BOM:", raw[:3] == b"\xef\xbb\xbf")
print("CRLF rows:", raw.count(b"\r\n"), "LF rows:", raw.count(b"\n"))
print("tail_newline:", raw.endswith(b"\n"))
print("len:", len(raw))
m = re.search(rb"\n(\s+)\"", raw)
print("first_indent:", m.group(1) if m else None)
print("has_ensure_ascii_escapes:", bool(re.search(rb"\\u", raw)))
d = json.loads(raw.decode("utf-8-sig"))
items = d.get("items", [])
print("items:", len(items), "ids_tail:", [it.get("id") for it in items[-3:]])
