# -*- coding: utf-8 -*-
# _r1008bmc_pit_append.py -- r1008 pit direct-writes (r666/r943 exception: main CODELY.md at cap)
# +pit-ps.md: PS comma-list literal arg passing (no expansion)
# +pit-git-staged.md: CAS empty-commit silent push (r615 class 2nd) + r739 diagnosis correction
# +global user CODELY.md: MV wave2 CDN INDEX-SKIP stale-bytes delivery trap (Project section)
# Receipt with byte accounting + md5 per touched file.
import hashlib, io, json, os

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GLOBAL = r"C:\Users\Dasheng\.codely-cli\CODELY.md"

PIT_PS = os.path.join(ROOT, "research", "pit-ps.md")
PIT_GS = os.path.join(ROOT, "research", "pit-git-staged.md")

entry_ps = (
"- [2026-10-14 20:5x r1008 bm-c] **PS 5.1 原生实参位逗号表=整串字面量零展开坑（CAS cacheinfo 三连炸实弹·python argv 复现定谳）**："
"`git ... --cacheinfo $meta[0],$meta[2],$parts[1]` 在 PS 原生命令实参位传出的既非三参也非展开值，而是**含 $ 符号的整串字面量** "
"`'$meta[0],$meta[2],$parts[1]'`（python -c argv 复现铁证：ARGV=['--cacheinfo','$meta[0],$meta[2],$parts[1]']）——逗号表在 argument mode "
"不拆参不展开，变量引用原样穿透；消费端报错面随工具而异（git update-index 报「option 'cacheinfo' expects <mode>,<sha1>,<path>」x3）。"
"正法=实参位禁裸逗号表，先预拼单串 $ci=\"$($a),$($b),$($c)\"（子表达式 $() 强制求值）再传 $ci，或脚本面改 python subprocess list-argv。"
"How to apply：一切「多变量拼单实参」场景（git cacheinfo/format 串/路径串）必 $() 包裹或落盘脚本；见工具报「格式不符」先 argv-dump 复核勿怪工具语法。\n"
)
entry_gs = (
"- [2026-10-14 20:5x r1008 bm-c] **CAS 空树提交静默上链坑（r615 断言腿同类二犯·r739 旧诊勘误·git 2.55 双形态科学测）**："
"PS 逗号字面量坑（pit-ps r1008 条）致 update-index --cacheinfo x3 全 no-op -> write-tree 返回父树原样 -> "
"commit-tree+push **照常成功**（实弹：集团树 7b53d661 空提交已上 origin/main=零内容污染·无 force 不可摘·披露收场）——"
"CAS 链缺「tree-delta==payload」断言腿=r615「断言漏跑」同类二犯（导演席同病二犯律：当窗落闸=本条+模板断言级升格）。"
"**r739 勘误**：git 2.55.0.windows.2 实测 cacheinfo 双形态全 rc=0（空格三参+逗号单串）——r739「连等形态拒收=老版本语法面」诊断为 PS 字面量假象非 git 语法面，"
"其「正法=空格三参」结论保留但根因改判。正法=CAS 模板三必备腿升级四：①update-index 后必断言 write-tree != 父 tree（或 diff-tree --cached vs 父树 payload 计数==预期）"
"②argv-dump/单串预拼 ③防重复投递门（cat-file -e 前置）④push 前送达自证。\n"
)
entry_mv = (
"- [2026-10-14 20:5x] bm-c wave2 CDN 交付面坑（mv0001 V3 全本地重产·O-20261014-1855 收割链·41 曲量产波复用）："
"**INDEX-SKIP=陈旧字节静默陷阱**——bmc_night_factory.cdn_upload 按标签查 I2V-URL-INDEX.md 去重，槽位重烧覆盖 mp4 后标签已在索引->INDEX SKIP 返回 None->"
"跑者记 UPLOAD_FAIL_OR_SKIPPED->新字节永不上传；bm-a 装配站 curl 旧 URL=旧片进终剪（23/26 槽中招·HEAD Content-Length vs 本地字节探针当场揭穿）。"
"修法=裸 file_upload+PUT 重传当前字节+后缀新标签（<slot>_w2r1008）+HEAD 字节验证+独立修复回执（勿碰跑者 progress.json 防竞态）。"
"律=**重烧波收割前必跑字节级 URL-本地恒等验证**（HEAD 尺寸比对即揭·无验证=交付面静默腐烂）。产物=bmc/wave2_cdn_{verify,repair}_r1008.json（23/23 修+26/26 验）·集团仓 d0045b0 上链。\n"
)

def append_with_accounting(path, entry, tag):
    before = os.path.getsize(path)
    data = io.open(path, "r", encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in data[:2000] else "\n"
    with io.open(path, "a", encoding="utf-8", newline="") as f:
        f.write(entry.replace("\n", nl))
    blob = io.open(path, "rb").read()
    return {"file": path, "tag": tag, "appended_bytes": len(entry.encode("utf-8")),
            "before_bytes": before, "after_bytes": len(blob), "md5": hashlib.md5(blob).hexdigest(),
            "eol": "CRLF" if nl == "\r\n" else "LF"}

receipt = {"ts": "2026-10-14T20:5x", "round": "r1008", "machine": "bm-c",
           "law": "direct-write per r666/r873/r943 exception (main CODELY.md at 31,063B >= 30,720B cap)",
           "entries": []}
receipt["entries"].append(append_with_accounting(PIT_PS, entry_ps, "pit-ps r1008 PS comma-literal"))
receipt["entries"].append(append_with_accounting(PIT_GS, entry_gs, "pit-git-staged r1008 CAS empty-commit + r739 correction"))

# global user memory: insert into Project section (before '### Reference' header)
g = io.open(GLOBAL, "r", encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in g[:2000] else "\n"
anchor = "### Reference"
i = g.find(anchor)
assert i > 0, "global Reference anchor missing"
new = g[:i] + entry_mv.replace("\n", nl) + g[i:]
io.open(GLOBAL, "w", encoding="utf-8", newline="").write(new)
blob = io.open(GLOBAL, "rb").read()
receipt["entries"].append({"file": GLOBAL, "tag": "global-user CODELY.md Project wave2 CDN trap",
                           "appended_bytes": len(entry_mv.encode("utf-8")), "insert": "before ### Reference",
                           "after_bytes": len(blob), "md5": hashlib.md5(blob).hexdigest(), "eol": "CRLF" if nl == "\r\n" else "LF"})

out = os.path.join(ROOT, "results", "_r1008bmc_codely_pit_direct.json")
io.open(out, "w", encoding="utf-8").write(json.dumps(receipt, ensure_ascii=False, indent=1))
print("receipt ->", out)
for e in receipt["entries"]:
    print(e["tag"], "+%dB" % e["appended_bytes"], "md5", e["md5"][:10])
