import json, hashlib
p = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r666bmc_codely_mojibake_heal.json"
with open(p, encoding="utf-8") as fh:
    r = json.load(fh)
r["fact_reconstruction_addendum"] = (
    "line-88 pointer carried r662-session hand-escape typo: recovered byte-faithful text had U+4C92 where entry anchor (pit-ps.md L53) reads \u5b57\u7b26\u4e32\u00d7 (string-x); "
    "diagnosis: author typed \\xe4\\xb2\\x92 instead of \\xe4\\xb8\\x82\\xc3\\x97 (dropped 2 bytes); corrected per r407 fact-reconstruction law using surviving verbatim anchor. "
    "line-85 pointer byte-faithful recovery matched entry (pit-ps.md L54) with no correction needed."
)
mb = open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\CODELY.md", "rb").read()
r["main_bytes_final_after_correction"] = len(mb)
r["main_final_md5_16"] = hashlib.md5(mb).hexdigest()[:16]
text = mb.decode("utf-8", errors="replace")
c1 = [i for i, l in enumerate(text.split("\n"), 1) if any(0x80 <= ord(c) <= 0x9F for c in l)]
r["post_correction_c1_residual"] = c1
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(r, fh, ensure_ascii=False, indent=1)
print("RECEIPT_UPDATED final=%d md5=%s c1=%s" % (len(mb), r["main_final_md5_16"], c1))
print("MAIN_LIMIT_CHECK %d <= 30720: %s" % (len(mb), len(mb) <= 30720))
