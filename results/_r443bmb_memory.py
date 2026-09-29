import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

path = "CODELY.md"
t = open(path, encoding="utf-8").read()

entry = (
    "- [2026-09-30 01:0x r443 bm-b] jsonl 追加写吞换行腐败坑+union 双侧同族修复律（x2_watch_log 实弹·死轮遗产收编窗）："
    "追加型 jsonl 生产者在并发/异常退出窗下 append 未带前置换行→两 JSON 对象同线拼接=逐行 json.loads 全断"
    "（本机死轮 23:5x 写入+origin bm-a 侧同族各 1 例=双侧腐败非单机面）；正典修复=JSONDecoder.raw_decode 循环"
    "拆拼接行零丢失（工具 results/_r443bmb_x2log_repair.py·修复后行数==对象数核验 1814）+rebase union 解后必对"
    "产物再跑同族拆分（r442 resolver 只验 raw-decode 可解不拆行=粘连行存活进 commit）。How to apply：凡 append-only "
    "jsonl 面收编/union 后，最终产物以「行数==对象数」为验收线；新追加写者一律带「ensure trailing newline before "
    "append」守卫。\n"
)

anchor = "### Project"
i = t.find(anchor)
assert i > 0, "Project anchor missing"
t2 = t[:i] + entry + t[i:]

with open(path, "w", encoding="utf-8", newline="") as f:
    f.write(t2)
print("CODELY.md appended, new size:", len(t2.encode("utf-8")), "bytes")
