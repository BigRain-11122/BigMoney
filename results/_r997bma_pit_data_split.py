"""r997 bm-a pit-data mini-split (D-20261002-06 authorized migration face,
r731/r816/r833 ceremony). Migrates the 2 oldest entries (r496/r503) verbatim
to research/pit-data-refresh.md, then appends the new r997 sina dual-face
publication-lag entry to the main file. Byte-identity assertions throughout.
"""
import json, os, datetime

MAIN = r"research/pit-data.md"
SUB = r"research/pit-data-refresh.md"
RECEIPT = r"results/_r997bma_pit_data_minisplit.json"

raw = open(MAIN, "rb").read()
orig_size = len(raw)
text = raw.decode("utf-8")
crlf = "\r\n" in text
NL = "\r\n" if crlf else "\n"
lines = text.split(NL)
# note: trailing element after final NL is "" (file ends with NL)

def entry_bytes(line):
    return (line + NL).encode("utf-8")

# locate r496 / r503 entry lines
i496 = i503 = None
for i, l in enumerate(lines):
    if l.lstrip().startswith("- [2026-10-01 07:0x r496 bm-b]"):
        i496 = i
    if l.lstrip().startswith("- [2026-10-01 12:2x r503 bm-b]"):
        i503 = i
assert i496 is not None and i503 is not None, (i496, i503)
assert i503 == i496 + 1, "expected r503 directly after r496, got %d/%d" % (i496, i503)

e496, e503 = lines[i496], lines[i503]
b496, b503 = entry_bytes(e496), entry_bytes(e503)
moved = b496 + b503

# --- sub-file (verbatim entries + provenance header) ---
stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
sub_header = (
    "# pit-data-refresh -- 数据域坑律子件（面板刷新/采集时序 facet）\r\n"
    "\r\n"
    "> 来源：pit-data.md mini-split 迁出（2026-10-14 %s·r997 bm-a·D-20261002-06 集团拆件令授权迁移面·r816 范式）。\r\n"
    "> 迁出 2 条（最旧面）：r496 panel-complete 活锁两-pass + r503 S6 日刷数据面×烧波中途钉，逐字节 verbatim（含 CRLF）。\r\n"
    "> 字节对账：迁出条目字节和 %d B == 主件净删减字节；receipt=results/_r997bma_pit_data_minisplit.json。\r\n"
    "> 执法面：面板 complete 停泊诊断/烧波中途数据面刷新撞钉/采集时序类动作前读本件（主件同域条目照旧在主件）。\r\n"
    "\r\n" % (stamp, len(moved))
)
sub_bytes = sub_header.encode("utf-8") + moved
assert b496 in sub_bytes and b503 in sub_bytes, "verbatim presence assert"
open(SUB, "wb").write(sub_bytes)

# --- rebuild main without the 2 lines ---
kept = lines[:i496] + lines[i503+1:]
main_body = NL.join(kept)

# byte-identity assert: original == rebuilt + moved (order: moved block sat between)
rebuilt_bytes = main_body.encode("utf-8")
assert orig_size == len(rebuilt_bytes) + len(moved), "size conservation"
# verbatim retained-face check: every remaining entry line must be in original
for l in kept:
    if l.lstrip().startswith(("- [2026", "[2026")):
        assert (l + NL).encode("utf-8") in raw or l == lines[-1], "retained face verbatim: " + l[:40]

# --- append new r997 entry at tail ---
new_entry = (
    "- [2026-10-14 19:4x r997 bm-a] **sina 日线双面发布差坑（update_daily 截止窗诊断·r997 双探针实证）**：同源同日双端点分叉——"
    "CN_MarketDataService.getKLineData（scale=240 jsonp 直连）收盘后即带当日 bar，而 akshare fund_etf_hist_sina（klc_kl.js face）"
    "惯例 21:00-23:00 才发布（10-13 bar=22:56 落/10-12≈次日 00:27/09-30=21:22）→ 19:0x-20:0x 轮 update_daily cutoff 停昨日="
    "正常源滞后非缺陷，后续轮自愈；禁在滞后窗判更新器坏或换端点硬拉（双面数值基准未对证，换面 append 会造 seam）。"
    "诊断序：①直探双端点定哪面缺②git log 该 bar 历史落地时刻③zero-row ambiguity 探针（T-08 腿）wrapper 已内建。"
    "How to apply：晚间轮见 cutoff 停昨日+failures=0+T-08 探针报 upstream 有 bar→判 klc 面正常滞后，下轮自愈勿动手。"
)
split_note = (
    "> mini-split 行（r997 bm-a·D-20261002-06 授权迁移·r816 范式）：最旧 2 条（r496/r503）verbatim 迁出→research/pit-data-refresh.md"
    "（%d B·字节恒等断言·receipt=results/_r997bma_pit_data_minisplit.json）；主件回线 ≤30KB；同窗入律 1 条（sina 日线双面发布差·r997 探针）。"
) % len(moved)

# insert split_note after the last header ">" line, append entry at end
out_lines = kept[:]
hdr_insert = None
for i, l in enumerate(out_lines):
    if l.startswith(">"):
        hdr_insert = i
out_lines.insert(hdr_insert + 1, split_note)
if out_lines[-1] == "":
    out_lines.insert(len(out_lines) - 1, new_entry)
else:
    out_lines.append(new_entry)
final = NL.join(out_lines).encode("utf-8")
open(MAIN, "wb").write(final)

# --- receipt ---
receipt = {
    "ts": datetime.datetime.now().isoformat(timespec="seconds"),
    "round": "r997", "machine": "bm-a",
    "op": "pit-data mini-split + new entry",
    "authorized_by": "D-20261002-06 group split order (prescan rc3 registry hit recorded, migration face)",
    "migrated_entries": ["r496 panel-complete 活锁 (1408B)", "r503 S6 日刷×烧波钉 (1388B)"],
    "migrated_bytes": len(moved),
    "sub_file": SUB, "sub_size": len(sub_bytes),
    "main_pre": orig_size, "main_post": len(final),
    "size_conservation_ok": orig_size == len(rebuilt_bytes) + len(moved),
    "verbatim_in_sub_ok": True,
    "main_under_cap": len(final) <= 30720,
    "sub_under_cap": len(sub_bytes) <= 30720,
    "new_entry": "sina 日线双面发布差 (r997)",
}
open(RECEIPT, "w", encoding="utf-8").write(json.dumps(receipt, ensure_ascii=False, indent=1))
print(json.dumps(receipt, ensure_ascii=False))
