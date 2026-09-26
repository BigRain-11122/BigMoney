# R236 bm-a: insert update_sina_mf gate leg into Tools/iteration_prompt.txt
# (T-72 s3 S6-chain wiring). Byte-precise single-line UTF-8 insert, no BOM,
# CRLF tail preserved. Idempotent guard: refuses double insert.
import io
import sys

P = "Tools/iteration_prompt.txt"
b = open(P, "rb").read()
t = b.decode("utf-8")
if "update_sina_mf" in t:
    print("already wired -- refusing double insert")
    sys.exit(0)

ANCHOR = ("refresh 分离进程 exit 0=全宇宙完成/2=未完成/3=完成但有 overlap_mismatch；"
          "selftest 子命令=离线守卫测试）→ python scripts\\update_ths_panel.py")
assert t.count(ANCHOR) == 1, f"anchor count {t.count(ANCHOR)}"

LEG = ("refresh 分离进程 exit 0=全宇宙完成/2=未完成/3=完成但有 overlap_mismatch；"
       "selftest 子命令=离线守卫测试）"
       "→ python scripts\\update_sina_mf.py（sina 个股四档资金流前向采集 gate·"
       "T-72 s3 接线·spec=research\\shortline\\SINA_MF_PREREG.md："
       "面板新鲜（complete 且 cutoff 未落后 20 交易日）=零网络 no-op；"
       "首拉/未完成=分离后台全宇宙拉取（2.5s 限速 checkpoint 断点续拉+锁+30min "
       "spawn 节流+连接级 3 连败熔断+逐股 3 次失败隔离）；"
       "过期（complete 面板 cutoff 落后 20td）=refresh-repull done-reset "
       "全宇宙复拉（R236 修正案）；终态 cutoff 从面板字节 derive"
       "（零符号轮禁 None 覆写真值）；车道归属护栏=仅 bm-a 动作（R31 判例）"
       "他机 stdout-only 诚实 no-op；exit 0=正常/no-op/已 spawn、2=机制故障"
       "原样上报勿掩盖；refresh 分离进程 exit 0=全宇宙完成/2=未完备 checkpoint "
       "保全/3=完成但有 overlap 失配；selftest 子命令=离线守卫测试）"
       "→ python scripts\\update_ths_panel.py")
t2 = t.replace(ANCHOR, LEG)
assert t2.count("update_sina_mf") == 1
open(P, "wb").write(t2.encode("utf-8"))

b2 = open(P, "rb").read()
print("inserted; chars:", len(t2), "| BOM:", b2[:3] == b"\xef\xbb\xbf",
      "| CRLF:", b2.count(b"\r\n"), "| LF:", b2.count(b"\n"))
