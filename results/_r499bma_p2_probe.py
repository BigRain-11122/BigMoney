# -*- coding: utf-8 -*-
"""r499 bm-a: P2 census pre-burn probe (read-only, prereg sec.2 completeness
gates evidence). M4 register-face count + M5 alpha_NNN method/DEMO_FACTORS
assertion. Zero writes outside stdout."""
import os
import re
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TS = os.path.abspath(os.path.join(ROOT, "..", "toolstack", "repos"))
M4_DIR = os.path.join(TS, "ml-quant-trading", "src", "mlquant", "features")
M5_FILE = os.path.join(TS, "Machine_Learning-Quant-Stock-Selection",
                       "multifactor_demo", "factors.py")

report = {"m4_dir_exists": os.path.isdir(M4_DIR),
          "m5_file_exists": os.path.isfile(M5_FILE)}

faces = []
if report["m4_dir_exists"]:
    files = sorted(f for f in os.listdir(M4_DIR) if f.endswith(".py"))
    report["m4_files"] = files
    dec = re.compile(r"@register_\w+\(\s*['\"]([\w]+)['\"]\s*\)")
    for fn in files:
        text = open(os.path.join(M4_DIR, fn), encoding="utf-8",
                    errors="replace").read()
        for m in dec.finditer(text):
            faces.append((fn, m.group(1)))
report["m4_face_count"] = len(faces)
fams = {}
for _, name in faces:
    pre = name.split("_")[0]
    fams[pre] = fams.get(pre, 0) + 1
report["m4_family_counts"] = fams
report["m4_face_names"] = [n for _, n in faces]

if report["m5_file_exists"]:
    text = open(M5_FILE, encoding="utf-8", errors="replace").read()
    tree = ast.parse(text)
    methods = []
    demo = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "AlphaFactorEngine":
            for sub in node.body:
                if isinstance(sub, ast.FunctionDef):
                    m = re.match(r"alpha_(\d+)$", sub.name)
                    if m:
                        methods.append(sub.name)
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "DEMO_FACTORS":
                    try:
                        demo = ast.literal_eval(node.value)
                    except (ValueError, SyntaxError):
                        demo = None
    report["m5_methods"] = methods
    report["m5_method_count"] = len(methods)
    report["m5_demo_factors"] = demo
    report["m5_demo_equals_methods"] = (demo is not None
                                        and sorted(demo) == sorted(methods))

import io
import json

with io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "_r499bma_p2_probe_out.json"), "w",
             encoding="utf-8", newline="\n") as fh:
    json.dump(report, fh, ensure_ascii=False, indent=1)
print("probe written; m4=%d m5=%s"
      % (report["m4_face_count"], report.get("m5_method_count")))
