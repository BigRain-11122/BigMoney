entry = "\n- [2026-10-01 20:0x r534 bm-a] finalize 型 CLI 无 --help 护栏坑（W2 误触实弹·1 行元数据重写当场治愈零提交）：perpetual_faces_n1.py argv 解析对未知 flag 不 fail-fast——`finalize --help` 未识别 --help 即以默认波真跑 finalize（默认=W2）→ n1_w2_results.json 元数据面 1 行重写（ledger/skill_line 块按当时活链头 408,548 derive=stale-ID 面；科学 payload 字节恒等=确定性律自保护）。Why：mutating 子命令把「未知参」当「无参」静默消化=探针变实弹。How to apply：①探询 mutating runner 接口先读源码 argv 段或用只读 status 子命令，禁以 --help 试参；②误触 healing=git status 单行 diff 即刻 checkout HEAD 正典，禁「顺手续用」误触产物；③一切 mutating CLI 加 unknown-arg fail-fast=工程改进候选（不本窗改）。\n"
with open(r'CODELY.md', 'a', encoding='utf-8') as f:
    f.write(entry)
with open(r'CODELY.md', encoding='utf-8') as f:
    lines = f.read().splitlines()
print('appended; total lines:', len(lines))
print('tail check:', lines[-1][:60])
