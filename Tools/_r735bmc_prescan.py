"""r735 bm-c prescan: measure candidate entry bytes in main CODELY.md for
mini-split (main 32,999B > 30,720B threshold per D-20261002-06).
Probes the 3 handoff-planned entries + additional candidates, reports exact
byte spans, and flags the merged-line boundary defect (r439 family)."""
import json

MAIN = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\CODELY.md"

with open(MAIN, encoding="utf-8") as fh:
    raw = fh.read()
main_bytes = len(raw.encode("utf-8"))

NEEDLES = {
    "r863_rebase_continue": "- [2026-10-08 05:5x r863 bm-a] **rebase --continue",
    "r863_buildgen_fresh": "- [2026-10-08 05:5x r863 bm-a] **buildgen FRESH token",
    "r734_prepush_claw": "- [2026-10-08 05:4x r734 bm-c] **pre-push",
    "r711_hex_case": "- [2026-10-08 01:0x r711 bm-c] **水位 hash hex 大小写归一坑",
    "r849_surgical_push": "- [2026-10-07 23:4x r849 bm-a] **外科推送双坑",
    "r847_bom_gbk": "- [2026-10-07 22:5x r847 bm-a] **跨机部署无 BOM",
    "r703_ollama_ptr": "- 域指针·r703 bm-c mini-split 批",
    "r731_ptr": "- 域指针·r731 bm-c（10-08）",
}

facts = {"main_bytes": main_bytes, "entries": {}}
for name, needle in NEEDLES.items():
    idx = raw.find(needle)
    if idx < 0:
        facts["entries"][name] = {"found": False}
        continue
    # entry ends at next "\n- " boundary (next list item) or EOF
    nxt = raw.find("\n- ", idx + 1)
    end = nxt + 1 if nxt >= 0 else len(raw)
    block = raw[idx:end]
    facts["entries"][name] = {
        "found": True,
        "start": idx,
        "end": end,
        "bytes": len(block.encode("utf-8")),
        "preview_tail": block[-40:].encode("utf-8", "replace").decode("utf-8"),
    }

# merged-line defect check: buildgen entry and r734 claw on same physical line?
b_idx = raw.find(NEEDLES["r863_buildgen_fresh"])
r_idx = raw.find(NEEDLES["r734_prepush_claw"])
nl_between = raw.find("\n", b_idx, r_idx) if (b_idx >= 0 and r_idx > b_idx) else -2
facts["merged_line_defect"] = bool(b_idx >= 0 and r_idx > b_idx and nl_between == -2)
facts["main_over"] = main_bytes - 30720

with open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r735bmc_prescan.json", "w", encoding="utf-8") as fh:
    json.dump(facts, fh, indent=1, ensure_ascii=False)
print(json.dumps(facts, indent=1, ensure_ascii=False))
