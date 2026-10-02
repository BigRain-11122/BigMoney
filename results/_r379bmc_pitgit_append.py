# r379 S7: CODELY origin-verbatim restore + pit-git.md domain append (r378 adopt + r379 lesson)
import subprocess, io, sys

# 1) CODELY.md: restore origin verbatim (my r378 entry migrates to pit-git.md per D-06 domain law)
rc = subprocess.run(["git", "checkout", "--", "CODELY.md"], capture_output=True)
print("CODELY checkout rc=%d" % rc.returncode)
b = open("CODELY.md", "rb").read()
print("CODELY restored: bytes=%d crlf=%d lf=%d" % (len(b), b.count(b"\r\n"), b.count(b"\n")))

# 2) pit-git.md append: r378 adopted entry + r379 new lesson (bytes-safe, LF per file tail convention)
P = "research/pit-git.md"
raw = open(P, "rb").read()
assert raw.endswith(b"\n"), "pit-git.md must end with newline for clean append"
e378 = open(r"K:\Fluxgroup\FluxGroup\quant\.codely-cli\scratch\r378_entry.txt", "rb").read().strip()
assert e378.startswith(b"- [2026-10-02 18:1x r378 bm-c]"), "r378 entry head mismatch"
L379 = ("- [2026-10-02 18:3x r379 bm-c] 猝死会话正典件整文件行尾翻面伪影收养法+silent-git 包装器单串参数坑"
        "（r378 会话收养实弹·r585/r586 族 bm-c 首例）：①仓 checkout 面不转行尾（blob LF 直落盘）·猝死会话写入把 CODELY 翻成纯 CRLF"
        "→对 HEAD blob 逐行全异=全文件 -/+ 伪影（+114/−113）——内容真差=尾部单条 append；正法=bytes 级提取新条目（行首标记定位）"
        "→checkout -- 还原正本杀翻面→按还原后面实测行尾字节级追加→git diff --stat 外科断言≈+1 行族；禁直接 commit 翻面版"
        "（整文件重写污染 blob 史）。②bm-c 侧 silent-git 包装器接口=单串 -GitArgs 显式命名参数——positional 多参错绑 Cwd"
        "（'status --porcelain' 两词直传=工作目录变 '--porcelain' 启动失败，非 git 故障）。"
        "How to apply：收养猝死会话整文件翻面遗物按提取-还原-再追加三步；包装器调用一律 -GitArgs 单串显式命名参数。").encode("utf-8")
add = b"- "  # placeholder
new = raw + e378 + b"\n" + L379 + b"\n"
with io.open(P, "wb") as f:
    f.write(new)
print("pit-git appended: %d + %d bytes -> %d" % (len(e378), len(L379), len(new)))
# 3) verify: diff stat for both files
for p in ("CODELY.md", "research/pit-git.md"):
    d = subprocess.run(["git", "diff", "--stat", "HEAD", "--", p], capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(p, "|", d.stdout.strip() or "CLEAN")
