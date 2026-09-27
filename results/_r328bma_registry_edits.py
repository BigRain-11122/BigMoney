# r328 bm-a: DOMAIN_AUDIT row-4 status flip + T-88 progress note append
import io, json

# --- DOMAIN_AUDIT.md row 4 ---
p = "research/DOMAIN_AUDIT.md"
b = open(p, "rb").read()
t = b.decode("utf-8")
crlf = "\r\n" if "\r\n" in t else "\n"
old = ("| 4 | 国债逆回购（GC001/R-001 期限梯） | **仓内零数据面**（data/ 无 repo 目录）——采集器待建"
       "（s3：sina/EM 日线面，现金腿真实收益率曲线=SPM 现金腿价值，轻算力周末合法） | n/a（利率面） | "
       "无摩擦（成交价=利率） | T+0 资金 T+1 可用 | **collector 先建**（s3 载体） |")
new = ("| 4 | 国债逆回购（GC001/R-001 期限梯） | **已采集在库（r328 bm-a T-88 s3）**：data/repo_daily/ 11 员"
       "（沪 GC001/003/004/007/014/028/091/182+深 R-001/R-003/R-007）39,360 行、最深 2006-11 起"
       "（GC001 2011-05 起）→2026-09-24，双面仲裁（newfqkline 主+fqkline 修复）2 坏行修复 0 隔离；"
       "gate=scripts/update_repo.py（S6 已接线·spec=research/shortline/REPO_PANEL.md）"
       " | n/a（利率面） | 无摩擦（成交价=利率） | T+0 资金 T+1 可用 | **已建**（r328；深市长端 R-014+ 探针未验按需扩展；"
       "MM-ETF 511880/511990/511660 仍缺=后续件） |")
assert t.count(old) == 1, "row-4 old text not unique/found"
t2 = t.replace(old, new)
with io.open(p, "w", encoding="utf-8", newline="") as f:
    f.write(t2)
print("DOMAIN_AUDIT row-4 flipped, size", len(b), "->", len(t2.encode("utf-8")))

# --- T-88 ticket progress ---
tp = "fleet/tasks/T-2026-09-26-88-P1.json"
d = json.load(io.open(tp, encoding="utf-8"))
assert "progress_r328_bma" not in d
d["progress_r328_bma"] = (
    "R328 bm-a s3 DELIVERED: scripts/update_repo.py repo term-ladder rate collector "
    "(11 terms SH GC001..GC182 + SZ R-001/R-003/R-007) + research/shortline/REPO_PANEL.md v1.1 spec "
    "(dual-face arbitration: newfqkline primary per-year windows + row-order guard + fqkline repair "
    "face; akshare tx bloodline REJECTED as transposition-prone -- live evidence GC001 2021-08-10 "
    "close served 2.850>high 2.750, true bar 2.085 via sibling-curve cross-validation GC003 2.115/"
    "GC007 2.23/R-003 1.89/R-007 2.06; Money0923 cache inherited same glitch = same blood not evidence) "
    "+ first pull LANDED data/repo_daily/ 39,360 rows (GC091 from 2006-11-01, GC001 from 2011-05-13, "
    "SZ from 2012-12-10; zero weekend rows; 2 repaired rows GC001 2021-08-10 + R-001 2021-12-30; "
    "0 quarantined; idempotent rerun +0) + rate band (0,200) evidence-locked (2015-02-10 GC001 "
    "close 53.44/high 65.00 = genuine pre-CNY squeeze, both faces + siblings concur) + selftest 10/10 "
    "+ S6 chain registered (iteration_prompt) + DOMAIN_AUDIT row-4 flipped to built. Data lane pure: "
    "zero engine runs, ledger N untouched. NEXT: s4 next-domain probes (REITs/LOF/QDII per audit) "
    "or MM-ETF cash-leg trio (511880/511990/511660) supply decision."
)
with io.open(tp, "w", encoding="utf-8", newline="") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
    f.write("\n")
json.load(io.open(tp, encoding="utf-8"))  # parse-verify
print("T-88 progress_r328_bma appended + parse-verified")
