# r328 bm-a: insert update_repo gate into Tools/iteration_prompt.txt S6 chain
import io

p = "Tools/iteration_prompt.txt"
b = open(p, "rb").read()
t = b.decode("utf-8")
entry = (
    r"→ python scripts\update_repo.py（国债逆回购期限梯利率日线·T-88 s3·r328 bm-a 接线："
    "11 员（沪 GC001/003/004/007/014/028/091/182+深 R-001/R-003/R-007）"
    "=newfqkline 主面逐年窗+行序守卫逐行把关+fqkline 修复面（守卫败行修复·不可修复隔离禁落地"
    "·spec=research/shortline/REPO_PANEL.md）+overlap 行级校验+15:30 no-op 门（本地 ETF 日历主源）"
    "+30min 节流+conn-fuse 3；利率带 0<close<200（2015-02-10 GC001 53.44=真春节前钱荒实证）；"
    "车道护栏=仅 bm-a 动作（R31 判例·T-88 认领线）他机 stdout-only 诚实 no-op；"
    "价格=年化%（close=当日收盘年化利率）·SPM 现金腿利率序列供给·纯采集零回测零引擎；"
    "exit 0=正常/no-op、2=源失败、3=overlap 失配原样上报勿掩盖；selftest 子命令=离线守卫测试）")
anchor = r"→ python scripts\update_options.py"
assert t.count(anchor) == 1, "anchor not unique"
t2 = t.replace(anchor, entry + anchor)
assert len(t2) == len(t) + len(entry)
n0 = t.count("\r\n")
with io.open(p, "w", encoding="utf-8", newline="") as f:
    f.write(t2)
b2 = open(p, "rb").read()
b2.decode("utf-8")
n1 = t2.count("\r\n")
print("written OK size:", len(b), "->", len(b2), "CRLF before/after:", n0, n1)
