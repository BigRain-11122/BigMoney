import io

P = "CODELY.md"
raw = open(P, "rb").read()
assert raw[:3] != b"\xef\xbb\xbf" and b"\r\n" not in raw
entry = (
    "- [2026-09-26 16:2x] 坑律（bm-b r259·T-80 slice-4 容量面 runner 首跑·"
    "parallel_runner 合同面·E1 自检期+首跑双捕零外泄）：**run_cells_parallel "
    "双合同细节——job=(key,fn,args) 以 fn(*args) 解包调用（非单 tuple 直传）；"
    "返回 dict 携带 __workers__ int 附加键**——按键消费免疫（电池先例），"
    "遍历消费不过滤该键=「'int' object is not subscriptable」崩或 +1 误计数；"
    "正律=新批 runner 消费面按键取值或显式跳 __workers__、audit.workers 直接"
    "取该键、写腿先读 parallel_runner.py 头注合同勿只镜像旧调用形状。"
    "指针=scripts/aggr_capacity_probe.py 修正史（worker 签名/manifest 裸文件名/"
    "log 顺序三修全在首跑前零产物窗，冻结后工程修=合法无重跑面）\n"
)
with open(P, "ab") as fh:
    fh.write(entry.encode("utf-8"))
print("appended; size:", len(open(P, "rb").read()))
