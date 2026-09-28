"""r400 bm-a: compute_audit drift convergence per r389 canon (shared := face_view output, no hand-union)."""
import importlib.util
import json

spec = importlib.util.spec_from_file_location("mlv", "scripts/merge_lane_views.py")
mlv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mlv)

view = mlv.face_view("compute_audit")
base = open("results/compute_audit.json", "rb").read()
crlf = b"\r\n" in base
head = base[:400]
indent = 1 if b'\n "' in head else (2 if b'\n  "' in head else 0)
txt = json.dumps(view, ensure_ascii=False, indent=indent or None)
if crlf:
    txt = txt.replace("\n", "\r\n")
with open("results/compute_audit.json", "w", encoding="utf-8", newline="" if crlf else "\n") as f:
    f.write(txt)
print("written: crlf =", crlf, "indent =", indent, "bytes =", len(txt))
print("history rows in view:", len(view.get("history", [])))
