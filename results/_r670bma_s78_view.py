# r670 bm-a: exact sec.7-8 bytes view (JSON-escaped for precise needle build)
import json
src = open("research/THEME_JUDGE_P1.md", encoding="utf-8").read()
i7 = src.find("## §7")
i8 = src.find("## §8")
seg = src[i7:]
with open("results/_r670bma_s78_exact.json", "w", encoding="utf-8") as fh:
    json.dump({"i7": i7, "i8": i8, "seg_len": len(seg), "seg": seg}, fh, ensure_ascii=False, indent=1)
print("i7:", i7, "i8:", i8, "seg chars:", len(seg))
